"""AC-2a (T2 live A/B) — wallclock improvement (병렬 > 순차 + 2σ).

Change Plan §8 AC-2a RTM 명명 테스트 (T2 tier).

T2 = live A/B (수동 프로토콜, CI 미편입):
  - 동일 SHA, 동일 formation, 동일 tier
  - 순차 3회 σ 확정 후 병렬 개선폭 > 2σ

Carrier: CFP-2926 Phase 2 (구현) / Story NG-9

[Note: 실 T2 파일 없으면 skip]
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
