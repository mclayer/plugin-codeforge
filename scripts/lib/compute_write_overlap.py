#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# compute_write_overlap.py — AC-14 쓰기 겹침 산출기 (P1 교대 + P2 구간 교집합)
#
# Carrier: CFP-2926 Phase 2 (구현) / Story NG-6
# SSOT: docs/adr/ADR-154-amendment-1.md §AC-14 (쓰기 겹침)
#
# 책임:
#   - dev-process-event 원장 읽기 → writer_key, artifact_key, first_write, last_write 필드
#   - 2중 겹침 술어 (둘 다 요구):
#     * P1 교대: 전역 쓰기 시각순 정렬 → 서로 다른 writer_key 가 A→B→A 재방문 횟수
#     * P2 구간 교집합: (writer_key, artifact_key) 별 [first_write, last_write) 반개구간
#       의 pairwise 교집합 > 0, 단 두 pair 의 artifact_key 가 서로 달라야 함
#   - 판정 = P1 > 0 ∧ P2 > 0 → PASS. 전건 미충족 → INCONCLUSIVE
#   - empty-target: 쓰기 0행 → INCONCLUSIVE
#   - unknown-input: unknown provenance → 입력 제외 + 카운트
#
# 불변식:
#   - read-only 원장 (IN-PLACE EDIT 절대 금지)
#   - 3-state: PASS / RED / INCONCLUSIVE
#   - stdout 단일 JSON 라인 + sys.exit(n)
#   - trace numeric (identity_probe echo)
#   - Python 3.9 + stdlib only + UTF-8
#
# 정직 천장 (docstring):
#   - "겹침 구간 > 0" 은 literal 동시 syscall 아니라 "서로 다른 주체의 쓰기가
#     시간상 동시 진행" 으로 pin 한다 (ADR-154-amendment-1 AC-14).
#
# 사용:
#   python3 compute_write_overlap.py [--ledger PATH]
#   python3 compute_write_overlap.py --self-test
#

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_DEFAULT_LEDGER_REL = Path(".claude") / "ledger" / "dev-process-event.jsonl"


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


def _has_intersection(interval_a, interval_b):
    """반개구간 [start, end) 교집합 판정.

    interval = (start, end) (반개구간).
    교집합이 있으면 True (단, 경계 접촉 제외).
    """
    start_a, end_a = interval_a
    start_b, end_b = interval_b
    # 교집합: max(start_a, start_b) < min(end_a, end_b)
    return max(start_a, start_b) < min(end_a, end_b)


def compute_write_overlap(lines, ledger_path=None):
    """dev-process-event 원장에서 쓰기 겹침 판정.

    입력:
      lines: JSONL 라인 시퀀스
      ledger_path: 실제 사용한 원장 경로 (identity_probe 용)

    반환: {
      "verdict": "PASS" | "RED" | "INCONCLUSIVE",
      "reason": str,
      "p1_interleave_count": int | None,  # A→B→A 재방문 횟수
      "p2_overlap_count": int | None,     # 구간 교집합 쌍 수
      "trace": {
        "total_writes": int,
        "unknown_writes": int,
        "distinct_writer_keys": int,
        "distinct_artifact_keys": int,
      },
      "identity_probe": dict,
    }
    """

    writes = []  # (timestamp, writer_key, artifact_key, (first_write, last_write))
    unknown_writes = 0
    writer_keys = set()
    artifact_keys = set()

    # ────────────────────── 데이터 로드 ──────────────────────
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

        writer_key = row.get("writer_key")
        artifact_key = row.get("artifact_key")
        first_write = row.get("first_write")
        last_write = row.get("last_write")

        # 필드 부재 또는 unknown → 입력 제외 + 카운트
        if (writer_key is None or artifact_key is None or
            first_write is None or last_write is None):
            unknown_writes += 1
            continue

        # 타입 검증
        try:
            fw = float(first_write)
            lw = float(last_write)
            if fw < 0 or lw < 0 or fw > lw:
                unknown_writes += 1
                continue
        except (TypeError, ValueError):
            unknown_writes += 1
            continue

        writes.append((fw, writer_key, artifact_key, (fw, lw)))
        writer_keys.add(writer_key)
        artifact_keys.add(artifact_key)

    # identity_probe 구성 (실제 대상 경로 + 메타데이터)
    probe = _build_identity_probe(ledger_path)

    # empty-target
    if not writes:
        return {
            "verdict": "INCONCLUSIVE",
            "reason": "쓰기 0행 (empty-target)",
            "p1_interleave_count": None,
            "p2_overlap_count": None,
            "trace": {
                "total_writes": len(writes),
                "unknown_writes": unknown_writes,
                "distinct_writer_keys": len(writer_keys),
                "distinct_artifact_keys": len(artifact_keys),
            },
            "identity_probe": probe,
        }

    # ────────────────────── P1: 교대 계산 ──────────────────────
    # 시각순 정렬
    writes_sorted = sorted(writes, key=lambda x: x[0])

    # writer_key 추출 순서
    writer_sequence = [w[1] for w in writes_sorted]

    # A→B→A 패턴 카운트
    interleave_count = 0
    for i in range(len(writer_sequence)):
        for j in range(i + 1, len(writer_sequence)):
            if writer_sequence[i] != writer_sequence[j]:
                # i 와 j 가 다른 writer
                # j 이후로 i 가 다시 나타나는가?
                for k in range(j + 1, len(writer_sequence)):
                    if writer_sequence[k] == writer_sequence[i]:
                        interleave_count += 1
                        break

    # ────────────────────── P2: 구간 교집합 계산 ──────────────────────
    # (writer_key, artifact_key) → 구간 (첫 쓰기 ~ 마지막 쓰기)
    write_spans = {}  # (writer_key, artifact_key) → (first_write, last_write)

    for fw, writer_key, artifact_key, interval in writes:
        key = (writer_key, artifact_key)
        if key not in write_spans:
            write_spans[key] = interval
        else:
            old_fw, old_lw = write_spans[key]
            # 구간 확장
            write_spans[key] = (min(old_fw, fw), max(old_lw, interval[1]))

    # pairwise 교집합 (artifact_key 상이 조건)
    overlap_count = 0
    keys = list(write_spans.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            (w1, a1) = keys[i]
            (w2, a2) = keys[j]

            # artifact_key 가 같으면 스킵
            if a1 == a2:
                continue

            # 구간 교집합 체크
            interval_i = write_spans[keys[i]]
            interval_j = write_spans[keys[j]]

            if _has_intersection(interval_i, interval_j):
                overlap_count += 1

    # ────────────────────── 판정 ──────────────────────
    p1_pass = interleave_count > 0
    p2_pass = overlap_count > 0

    if p1_pass and p2_pass:
        verdict = "PASS"
        reason = f"P1(교대)={interleave_count} > 0 ∧ P2(구간교집합)={overlap_count} > 0"
    else:
        verdict = "INCONCLUSIVE"
        reason = f"P1(교대)={interleave_count} | P2(구간교집합)={overlap_count} (전건 미충족)"

    return {
        "verdict": verdict,
        "reason": reason,
        "p1_interleave_count": interleave_count,
        "p2_overlap_count": overlap_count,
        "trace": {
            "total_writes": len(writes),
            "unknown_writes": unknown_writes,
            "distinct_writer_keys": len(writer_keys),
            "distinct_artifact_keys": len(artifact_keys),
        },
        "identity_probe": probe,
    }


def gate_result_to_json(result):
    """gate_verdict 패턴 준수 JSON 렌더."""
    verdict_map = {"PASS": 0, "RED": 1, "INCONCLUSIVE": 3}
    return {
        "gate_id": "NG-6",
        "verdict": result["verdict"],
        "exit_code": verdict_map.get(result["verdict"], 3),
        "reason": result["reason"],
        "p1_interleave_count": result["p1_interleave_count"],
        "p2_overlap_count": result["p2_overlap_count"],
        "trace": result["trace"],
        "identity_probe": result["identity_probe"],
    }


def _self_test():
    """fixture 기반 자가검증."""
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    # ────────────────────── F-5: 경계 (반개구간 규약) ──────────────────────
    # A.stop == B.start (A=[0,10), B=[10,20)) → P2 = 0 (교집합 없음)
    lines_f5a = [
        json.dumps({
            "writer_key": "w1", "artifact_key": "a1",
            "first_write": 0, "last_write": 10,
        }),
        json.dumps({
            "writer_key": "w2", "artifact_key": "a2",
            "first_write": 10, "last_write": 20,
        }),
    ]
    res_f5a = compute_write_overlap(lines_f5a)
    check(res_f5a["p2_overlap_count"] == 0,
          f"[F-5a] P2={res_f5a['p2_overlap_count']} != 0 (경계 접촉 제외)")

    # A.stop == B.start + 1ms → P2 > 0
    lines_f5b = [
        json.dumps({
            "writer_key": "w1", "artifact_key": "a1",
            "first_write": 0, "last_write": 10.001,
        }),
        json.dumps({
            "writer_key": "w2", "artifact_key": "a2",
            "first_write": 10, "last_write": 20,
        }),
    ]
    res_f5b = compute_write_overlap(lines_f5b)
    check(res_f5b["p2_overlap_count"] > 0,
          f"[F-5b] P2={res_f5b['p2_overlap_count']} <= 0 (1ms 차이 교집합 감지 실패)")

    # ────────────────────── F-7: 양성 (P1 + P2) ──────────────────────
    # A→B→A 재방문 + 구간 교집합 (artifact 상이)
    lines_f7 = [
        json.dumps({
            "writer_key": "writer_1", "artifact_key": "file_x",
            "first_write": 100, "last_write": 200,
        }),
        json.dumps({
            "writer_key": "writer_2", "artifact_key": "file_y",
            "first_write": 150, "last_write": 250,
        }),
        json.dumps({
            "writer_key": "writer_1", "artifact_key": "file_z",
            "first_write": 180, "last_write": 280,
        }),
    ]
    res_f7 = compute_write_overlap(lines_f7)
    check(res_f7["verdict"] == "PASS",
          f"[F-7] verdict {res_f7['verdict']} != PASS")
    check(res_f7["p1_interleave_count"] > 0,
          f"[F-7] P1={res_f7['p1_interleave_count']} <= 0")
    check(res_f7["p2_overlap_count"] > 0,
          f"[F-7] P2={res_f7['p2_overlap_count']} <= 0")

    # ────────────────────── 음성대조: 순차 배열 → P1 = 0 ──────────────────────
    # A→A→B 패턴 (A가 먼저 두 번, 그다음 B) → 시각 정렬 후에도 A→B→A 패턴 없음
    lines_f7_seq = [
        json.dumps({
            "writer_key": "writer_1", "artifact_key": "file_x",
            "first_write": 100, "last_write": 200,
        }),
        json.dumps({
            "writer_key": "writer_1", "artifact_key": "file_z",
            "first_write": 150, "last_write": 250,
        }),
        json.dumps({
            "writer_key": "writer_2", "artifact_key": "file_y",
            "first_write": 180, "last_write": 280,
        }),
    ]
    res_f7_seq = compute_write_overlap(lines_f7_seq)
    check(res_f7_seq["p1_interleave_count"] == 0,
          f"[음성] P1={res_f7_seq['p1_interleave_count']} != 0 (순차 배열)")

    if failures:
        print("[compute_write_overlap --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1

    print(
        "[compute_write_overlap --self-test] PASS "
        "(F-5a=0 OK; F-5b>0 OK; F-7 P1>0∧P2>0 OK; 음성대조 P1=0 OK)"
    )
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description="AC-14 쓰기 겹침 산출기 (P1 교대 + P2 구간 교집합)"
    )
    p.add_argument("--ledger", default=None, help="dev-process-event.jsonl 경로")
    p.add_argument("--self-test", action="store_true", help="fixture 기반 자가검증")

    args = p.parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.ledger is None:
        proj_dir = "."
        ledger_path = Path(proj_dir) / _DEFAULT_LEDGER_REL
    else:
        ledger_path = Path(args.ledger)

    lines = _read_ledger_lines(ledger_path)
    result = compute_write_overlap(lines, ledger_path=str(ledger_path))

    json_out = gate_result_to_json(result)
    print(json.dumps(json_out, ensure_ascii=False), file=sys.stdout)

    return json_out["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
