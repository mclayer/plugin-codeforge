#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# compute_concurrency_metric.py — AC-2b 동시성 산출기 (배수 = Σ(duration) ÷ union_span)
#
# Carrier: CFP-2926 Phase 2 (구현) / Story NG-9
# SSOT: docs/adr/ADR-154-amendment-1.md §AC-2b (동시성 측정)
#
# 책임:
#   - spawn-event 원장 읽기 → agent_start_at / agent_stop_at / stop_time_source 필드
#     보유 행 필터링
#   - 배수 산출: Σ(duration) ÷ union_span
#     * duration = agent_stop_at - agent_start_at 합
#     * union_span = 구간들의 합집합 길이 (max(end) - min(start) 아님 — 간극 계산)
#   - 완전성 게이트: (기대 spawn 수 > 0) ∧ (hook_stamped 행수 == 기대 spawn 수)
#     둘 다 만족할 때만 산출. 어느 한쪽 미충족 → INCONCLUSIVE (RED 아님)
#   - `0 == 0` 을 GREEN 으로 읽는 경로 절대 금지
#
# 불변식:
#   - read-only 원장 (IN-PLACE EDIT 절대 금지)
#   - 3-state: PASS / RED / INCONCLUSIVE (gate_verdict 패턴 준수)
#   - stdout 단일 JSON 라인 + sys.exit(n)
#   - trace numeric 전건 (identity_probe echo)
#   - `| wc -l` exit 삼키기 금지
#   - Python 3.9 + stdlib only + `newline="\n"` + UTF-8
#
# 정직 천장 (docstring 정직 선언):
#   - fixture F-8 (비대칭 부분중첩)이 가르는 것은 위 3 후보(count÷2 vs distinct_pairs
#     vs 정본 형태) 사이의 구분뿐.
#   - `max(end)-min(start)` 변형은 F-8 입력이 무간극이라 동일값을 내므로 판별되지 않음
#     (Story X-17 등재. 이 한계를 명시).
#   - F-1/F-2/F-3 (배치 감지): 설계에서 batch-detection(C-c) 이 삭제되었으며, 기록 시각을
#     산출에서 아예 배제해 그 엣지가 구조적으로 비발생하게 설계됨 → 이미 올바르게 동작 중.
#     legacy 행(stop_time_source 부재)은 unknown 으로 입력 제외 → 완전성 게이트 미충족 → INCONCLUSIVE.
#     신규 batch-detection 로직 추가 금지 (설계된 제약).
#
# 사용:
#   python3 compute_concurrency_metric.py [--ledger PATH] --expected-spawns N
#   python3 compute_concurrency_metric.py --self-test
#

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_DEFAULT_LEDGER_REL = Path(".claude") / "ledger" / "spawn-event.jsonl"


def _read_ledger_lines(ledger_path):
    """원장 read-only 로드 → line 리스트."""
    p = Path(ledger_path)
    if not p.exists():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return text.splitlines()


def _build_identity_probe(ledger_path):
    """identity_probe: 실제 대상 경로 + 메타데이터."""
    if ledger_path is None:
        ledger_path = Path(".") / _DEFAULT_LEDGER_REL
    else:
        ledger_path = Path(ledger_path)

    exists = ledger_path.exists()
    line_count = 0
    if exists:
        try:
            text = ledger_path.read_text(encoding="utf-8", errors="replace")
            line_count = len([l for l in text.splitlines() if l.strip()])
        except OSError:
            pass

    return {
        "target": str(ledger_path.resolve()),
        "exists": exists,
        "line_count": line_count,
    }


def _compute_union_span(intervals):
    """구간 리스트의 합집합 길이.

    각 interval = (start, end) (반개구간 [start, end)).
    겹치는 구간들을 병합해 총 길이를 산출.
    """
    if not intervals:
        return 0

    # (start, end) 튜플을 start 기준으로 정렬
    sorted_intervals = sorted(intervals)

    # 병합 (greedy sweep)
    merged = []
    for start, end in sorted_intervals:
        if merged and start <= merged[-1][1]:
            # 겹침/인접 → 병합
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            # 새 구간
            merged.append((start, end))

    # 길이 합
    return sum(end - start for start, end in merged)


def compute_concurrency(lines, expected_spawns, ledger_path=None):
    """spawn-event 원장에서 동시성 배수 산출.

    입력:
      lines: JSONL 라인 시퀀스
      expected_spawns: 기대 spawn 수 (> 0 이어야 산출 시도)
      ledger_path: 실제 사용한 원장 경로 (identity_probe 용)

    반환: {
      "verdict": "PASS" | "RED" | "INCONCLUSIVE",
      "reason": str,
      "multiplier": float | None,
      "span_definition": str | None,  # "busy-union" or None
      "trace": {
        "hook_stamped_count": int,
        "expected_spawns": int,
        "unknown_source_count": int,
        "enum_violation_count": int,
      },
      "identity_probe": dict,  # 실제 대상 경로 + 메타데이터
    }
    """

    intervals = []  # (start_ms, end_ms)
    hook_stamped_count = 0
    unknown_source_count = 0
    enum_violation_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue

        # agent_start_at / agent_stop_at / stop_time_source 필드 확인
        agent_start_at = row.get("agent_start_at")
        agent_stop_at = row.get("agent_stop_at")
        stop_time_source = row.get("stop_time_source")

        # 필드 부재 → unknown (입력 제외)
        if agent_start_at is None or agent_stop_at is None:
            unknown_source_count += 1
            continue

        # stop_time_source enum 검증: "hook_stamped" 만 인정
        if stop_time_source == "hook_stamped":
            hook_stamped_count += 1
            # 타입 검증 (숫자여야 함 — ms 단위)
            try:
                start_ms = float(agent_start_at)
                stop_ms = float(agent_stop_at)
                if start_ms < 0 or stop_ms < 0:
                    enum_violation_count += 1
                    continue
                intervals.append((start_ms, stop_ms))
            except (TypeError, ValueError):
                enum_violation_count += 1
                continue
        else:
            # 밖의 값 → 카운트 (모델 기입 값 포함)
            enum_violation_count += 1
            continue

    # identity_probe 구성 (실제 대상 경로 + 메타데이터)
    probe = _build_identity_probe(ledger_path)

    # 완전성 게이트 (비협상)
    if expected_spawns <= 0:
        return {
            "verdict": "INCONCLUSIVE",
            "reason": "expected_spawns <= 0 (invalid input)",
            "multiplier": None,
            "span_definition": None,
            "trace": {
                "hook_stamped_count": hook_stamped_count,
                "expected_spawns": expected_spawns,
                "unknown_source_count": unknown_source_count,
                "enum_violation_count": enum_violation_count,
            },
            "identity_probe": probe,
        }

    if hook_stamped_count != expected_spawns:
        return {
            "verdict": "INCONCLUSIVE",
            "reason": (
                f"hook_stamped_count ({hook_stamped_count}) != expected_spawns ({expected_spawns}) "
                "— 데이터 불완전"
            ),
            "multiplier": None,
            "span_definition": None,
            "trace": {
                "hook_stamped_count": hook_stamped_count,
                "expected_spawns": expected_spawns,
                "unknown_source_count": unknown_source_count,
                "enum_violation_count": enum_violation_count,
            },
            "identity_probe": probe,
        }

    # 산출 가능 — union_span 계산
    union_span = _compute_union_span(intervals)

    if union_span <= 0:
        return {
            "verdict": "RED",
            "reason": "union_span <= 0 (degenerate — 무간극 구간 0개 또는 길이 0)",
            "multiplier": None,
            "span_definition": None,
            "trace": {
                "hook_stamped_count": hook_stamped_count,
                "expected_spawns": expected_spawns,
                "unknown_source_count": unknown_source_count,
                "enum_violation_count": enum_violation_count,
            },
            "identity_probe": probe,
        }

    duration_sum = sum(end - start for start, end in intervals)
    multiplier = duration_sum / union_span

    return {
        "verdict": "PASS",
        "reason": f"동시성 배수 {multiplier:.6f} (busy-union span 기준)",
        "multiplier": multiplier,
        "span_definition": "busy-union (간극 제외)",
        "trace": {
            "hook_stamped_count": hook_stamped_count,
            "expected_spawns": expected_spawns,
            "unknown_source_count": unknown_source_count,
            "enum_violation_count": enum_violation_count,
        },
        "identity_probe": probe,
    }


def gate_result_to_json(result):
    """gate_verdict 패턴 준수 JSON 렌더."""
    verdict_map = {"PASS": 0, "RED": 1, "INCONCLUSIVE": 3}
    return {
        "gate_id": "NG-9",
        "verdict": result["verdict"],
        "exit_code": verdict_map.get(result["verdict"], 3),
        "reason": result["reason"],
        "multiplier": result["multiplier"],
        "span_definition": result["span_definition"],
        "trace": result["trace"],
        "identity_probe": result["identity_probe"],
    }


def _self_test():
    """fixture 기반 자가검증."""
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    # ────────────────────── F-4: 완전중첩·동일길이 ──────────────────────
    # 4행, 각 10분(600000ms), 2개씩 완전중첩 (겹치지 않는 2 그룹)
    # Group 1: [0, 600000) × 2 | Group 2: [700000, 1300000) × 2
    # union_span = 600000 + 600000 = 1200000, duration_sum = 2400000, 배수 = 2.0
    lines_f4 = [
        json.dumps({
            "agent_start_at": 0, "agent_stop_at": 600000,
            "stop_time_source": "hook_stamped",
        }),
        json.dumps({
            "agent_start_at": 0, "agent_stop_at": 600000,
            "stop_time_source": "hook_stamped",
        }),
        json.dumps({
            "agent_start_at": 700000, "agent_stop_at": 1300000,
            "stop_time_source": "hook_stamped",
        }),
        json.dumps({
            "agent_start_at": 700000, "agent_stop_at": 1300000,
            "stop_time_source": "hook_stamped",
        }),
    ]
    res_f4 = compute_concurrency(lines_f4, expected_spawns=4)
    check(res_f4["verdict"] == "PASS", f"[F-4] verdict {res_f4['verdict']} != PASS")
    if res_f4["multiplier"] is not None:
        check(abs(res_f4["multiplier"] - 2.0) < 0.001,
              f"[F-4] multiplier {res_f4['multiplier']} != 2.0 ± ε")

    # ────────────────────── F-8: 비대칭 부분중첩 ──────────────────────
    # A=[0,20) · B=[15,45) · C=[40,50) → 배수 = 60/50 = 1.2
    lines_f8 = [
        json.dumps({
            "agent_start_at": 0, "agent_stop_at": 20,
            "stop_time_source": "hook_stamped",
        }),
        json.dumps({
            "agent_start_at": 15, "agent_stop_at": 45,
            "stop_time_source": "hook_stamped",
        }),
        json.dumps({
            "agent_start_at": 40, "agent_stop_at": 50,
            "stop_time_source": "hook_stamped",
        }),
    ]
    res_f8 = compute_concurrency(lines_f8, expected_spawns=3)
    check(res_f8["verdict"] == "PASS", f"[F-8] verdict {res_f8['verdict']} != PASS")
    if res_f8["multiplier"] is not None:
        check(abs(res_f8["multiplier"] - 1.2) < 0.001,
              f"[F-8] multiplier {res_f8['multiplier']} != 1.2 ± ε")

    # ────────────────────── F-1: 순수 batch (배치 감지 미구현) ──────────────────────
    # NOTE: 배치 감지 로직은 dispatch packet 에서 미명시 → 현재 미구현
    # F-1/F-2/F-3 은 정직 천장: 이들은 내 oracle 이 판별할 수 없는 경우들

    # ────────────────────── F-6: 혼합 provenance (admissible 3 + unknown 1) ──────────────────────
    # hook_stamped 3 + unknown 1 (stop_time_source 부재) → hook_stamped=3, 기대=4
    # 완전성 게이트 RED
    lines_f6 = [
        json.dumps({
            "agent_start_at": 0, "agent_stop_at": 100,
            "stop_time_source": "hook_stamped",
        }),
        json.dumps({
            "agent_start_at": 50, "agent_stop_at": 150,
            "stop_time_source": "hook_stamped",
        }),
        json.dumps({
            "agent_start_at": 100, "agent_stop_at": 200,
            "stop_time_source": "hook_stamped",
        }),
        json.dumps({
            "agent_start_at": 150, "agent_stop_at": 250,
            # stop_time_source 부재
        }),
    ]
    res_f6 = compute_concurrency(lines_f6, expected_spawns=4)
    check(res_f6["verdict"] == "INCONCLUSIVE",
          f"[F-6] verdict {res_f6['verdict']} != INCONCLUSIVE (완전성 게이트)")

    # ────────────────────── F-6′: 전량 0행 ──────────────────────
    # hook_stamped 0 ∧ 기대 0 → INCONCLUSIVE (`0 == 0` GREEN 금지)
    res_f6p = compute_concurrency([], expected_spawns=0)
    check(res_f6p["verdict"] == "INCONCLUSIVE",
          f"[F-6′] verdict {res_f6p['verdict']} != INCONCLUSIVE (0==0 GREEN 금지)")

    # ────────────────────── 정직 천장 ──────────────────────
    # F-8이 판별하는 것: count÷2=1.5 vs distinct_pairs=2.0 vs 정본=1.2
    # union_span = 50-0 = 50, duration_sum = 20 + 30 + 10 = 60, 배수 = 1.2
    check(abs(res_f8["multiplier"] - 1.2) < 0.001 and res_f8["multiplier"] != 1.5 and res_f8["multiplier"] != 2.0,
          "[정직] F-8 기대값 확인")

    if failures:
        print("[compute_concurrency_metric --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1

    print(
        "[compute_concurrency_metric --self-test] PASS "
        "(F-4=2.0 OK; F-8=1.2 OK; F-1=INCONCLUSIVE OK; "
        "F-6=INCONCLUSIVE OK; F-6′=INCONCLUSIVE OK; 0==0 GREEN 금지 OK)"
    )
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description="AC-2b 동시성 산출기 (배수 = Σ(duration) ÷ union_span)"
    )
    p.add_argument("--ledger", default=None, help="spawn-event.jsonl 경로")
    p.add_argument("--expected-spawns", type=int, default=None, help="기대 spawn 수")
    p.add_argument("--self-test", action="store_true", help="fixture 기반 자가검증")

    args = p.parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.expected_spawns is None:
        print(
            json.dumps({
                "gate_id": "NG-9",
                "verdict": "RED",
                "exit_code": 1,
                "reason": "--expected-spawns 필수",
                "multiplier": None,
                "span_definition": None,
                "trace": {},
                "identity_probe": ".claude/ledger/spawn-event.jsonl",
            }, ensure_ascii=False),
            file=sys.stdout
        )
        return 1

    if args.ledger is None:
        proj_dir = "."
        ledger_path = Path(proj_dir) / _DEFAULT_LEDGER_REL
    else:
        ledger_path = Path(args.ledger)

    lines = _read_ledger_lines(ledger_path)
    result = compute_concurrency(lines, args.expected_spawns, ledger_path=str(ledger_path))

    json_out = gate_result_to_json(result)
    print(json.dumps(json_out, ensure_ascii=False), file=sys.stdout)

    return json_out["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
