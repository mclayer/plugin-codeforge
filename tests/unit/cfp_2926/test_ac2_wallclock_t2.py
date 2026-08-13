"""AC-2a (T2 live A/B) — wallclock improvement (병렬 > 순차 + 2σ).

Change Plan §8 AC-2a RTM 명명 테스트 (T2 tier).

T2 = live A/B (수동 프로토콜, CI 미편입):
  - 동일 SHA, 동일 formation, 동일 tier
  - 순차 3회 σ 확정 후 병렬 개선폭 > 2σ

Carrier: CFP-2926 Phase 2 (구현) / Story NG-9

★정직 declare — 본 파일의 CI 검증력 = 0 (F-CR-009)★

  Story 간판 성능 주장(AC-2a wall-clock: "병렬이 순차보다 2σ 이상 빠르다")을 이름으로
  달고 있으나, **CI 에서 이 단언이 검사되는 일은 구조적으로 없다**:

  - 판정 입력 = ``.t2-wallclock-improvement-result.jsonl`` (수동 live A/B 프로토콜 산출물).
  - 이 파일은 **repo 에 커밋되지 않고 CI 러너에도 생성되지 않는다** (동일 SHA·동일 tier
    조건의 수동 3+3 회 실측이 필요 — CI job 이 만들 수 있는 물건이 아니다).
  - ⇒ CI 에서 이 테스트는 **항상 skip** 이고, skip 은 pytest 에서 **green** 이다.
    즉 ``phase2-unit-tests`` job 의 통과는 AC-2a 에 대해 **아무것도 말하지 않는다**.

  ★"상시 skip = 상시 green" 을 검증으로 오독하지 말 것★. 이 파일이 보증하는 것은
  "T2 산출물이 **주어졌을 때** 판정 규칙이 무엇인가" 뿐이며(판정 로직의 실행 가능성),
  "그 판정이 실제로 내려졌는가" 는 보증하지 않는다.

  해소 경로 = ① 수동 T2 프로토콜 실행 후 산출물을 게이트 입력으로 배선하거나
  ② AC-2a 를 CI 로 검증 가능한 대리 지표로 재정의 — 둘 다 본 파일 소관 밖(설계 축).
  그때까지 이 테스트는 **검증면이 아니라 규칙 기록면**이다.

[Note: 실 T2 파일 없으면 skip — 위 정직 declare 참조]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# T2 result 파일 경로 규약
T2_RESULT_PATTERN = ".t2-wallclock-improvement-result.jsonl"


def test_wallclock_improvement_exceeds_2sigma(tmp_path):
    """AC-2a T2: 병렬 구현이 순차 대비 > 2σ 개선.

    T2 result 파일 규약:
      {
        "experiment_id": "...",
        "baseline_sha": "<git-sha>",
        "formation": "sequential" or "parallel",
        "wall_clock_ms": <float>,
        "tier": "<tier>",
        "run_n": <int>,
      }

    [Discriminating: 실 A/B 실측치에서만 판정 가능 (stub 불가)]

    [T2 조건]:
      - 동일 SHA (baseline_sha identical)
      - 동일 formation (sequential 3회 σ 확정 후 parallel 3회 σ 확정)
      - 동일 tier
      - parallel_mean - sequential_mean > 2 * sequential_σ
    """
    # T2 result 파일 조회
    cwd = Path.cwd()
    t2_file = cwd / T2_RESULT_PATTERN

    if not t2_file.exists():
        pytest.skip(
            reason=(
                f"T2 result file not found ({T2_RESULT_PATTERN}). "
                "★이 skip 은 PASS 가 아니다 — CI 러너에 이 산출물이 구조적으로 부재하므로 "
                "CI 에서 AC-2a wall-clock 주장의 검증력은 0 이다 (모듈 docstring 정직 declare 참조).★ "
                "AC-2a T2 requires live A/B protocol — "
                "identical SHA / identical tier / sequential 3-run σ + parallel 3-run σ. "
                "Result path: ~/.t2-results/<exp-id>.jsonl or CI output. "
                "Pass condition: parallel_mean > sequential_mean + 2 * sequential_σ"
            )
        )

    # 파일 존재 → 파싱 및 검증
    lines = t2_file.read_text(encoding="utf-8").splitlines()

    seq_results = []
    par_results = []

    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue

        formation = row.get("formation")
        wall_clock = row.get("wall_clock_ms")

        if formation == "sequential":
            seq_results.append(wall_clock)
        elif formation == "parallel":
            par_results.append(wall_clock)

    # 최소 3개씩 확정되었는가
    if len(seq_results) < 3:
        pytest.skip(
            reason=f"sequential baseline insufficient: {len(seq_results)} runs (need 3)"
        )
    if len(par_results) < 3:
        pytest.skip(
            reason=f"parallel runs insufficient: {len(par_results)} runs (need 3)"
        )

    # σ 계산
    import statistics

    seq_mean = statistics.mean(seq_results[:3])
    seq_stdev = statistics.stdev(seq_results[:3]) if len(seq_results[:3]) > 1 else 0

    par_mean = statistics.mean(par_results[:3])

    # 판정: parallel_mean < sequential_mean - 2*σ (개선)
    # (음수 = 감소 = 개선)
    improvement_threshold = seq_mean - 2 * seq_stdev

    assert par_mean < improvement_threshold, (
        f"AC-2a T2 improvement not exceeded: "
        f"parallel={par_mean:.2f}ms > threshold={improvement_threshold:.2f}ms "
        f"(sequential={seq_mean:.2f}ms ± {seq_stdev:.2f}ms, need > 2σ improvement)"
    )
