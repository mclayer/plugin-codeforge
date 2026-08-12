"""AC-14 — 쓰기 겹침 산출기 (compute_write_overlap).

Change Plan §8 AC-14 RTM 명명 테스트.
  - P1: 교대 (A→B→A 재방문)
  - P2: 구간 교집합 (반개구간 [first, last))
  - 판정: P1 > 0 ∧ P2 > 0 → PASS

Carrier: CFP-2926 Phase 2 (구현) / Story NG-6
"""

from __future__ import annotations

import json

import pytest

try:
    import compute_write_overlap
except ImportError:
    pytest.skip("compute_write_overlap module not found", allow_module_level=True)


def test_write_overlap_alternation_positive(tmp_path, golden_fixture):
    """AC-14 P1 양성 (F-7): A→B→A 재방문 + 구간 교집합 → PASS.

    [Mutant: P1=0 허용 → GREEN (RED 기대)]
    [Discriminating: 교대 패턴이 실제로 검출되어야 함]
    """
    ledger = tmp_path / "dev-process.jsonl"

    # F-7: W-A·W-B·W-A 순서 (A→B→A)
    fixture = golden_fixture["F-7"]
    rows = fixture["rows"]

    ledger.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    result = compute_write_overlap.compute_write_overlap(
        ledger.read_text(encoding="utf-8").splitlines()
    )

    assert result["verdict"] == "PASS", f"expected PASS, got {result['verdict']}"
    assert result["p1_interleave_count"] is not None
    assert result["p1_interleave_count"] > 0, "P1 (interleave) should be > 0"
    assert result["p2_overlap_count"] is not None
    assert result["p2_overlap_count"] > 0, "P2 (overlap) should be > 0"


def test_write_overlap_sequential_control_is_zero(tmp_path):
    """AC-14 P1 음성대조: 순차 배열 → P1 = 0 (음성 보증).

    [Mutant: 순차를 교대로 오인 → GREEN (RED 기대)]
    [Discriminating: 음성대조 필요 (0 기대)]

    [Note: 음성대조가 0 을 못 내는 관측은 판별력 0 → 채택 불가]
    """
    ledger = tmp_path / "dev-process.jsonl"

    # 순차 배열: W-A (끝) → W-B (시작) → W-C
    rows = [
        {"writer_key": "W-A", "artifact_key": "A", "first_write": 0, "last_write": 100},
        {"writer_key": "W-B", "artifact_key": "B", "first_write": 100, "last_write": 200},
        {"writer_key": "W-C", "artifact_key": "C", "first_write": 200, "last_write": 300},
    ]

    ledger.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    result = compute_write_overlap.compute_write_overlap(
        ledger.read_text(encoding="utf-8").splitlines()
    )

    # 순차이므로 P1 = 0 (재방문 없음)
    assert result["p1_interleave_count"] == 0, (
        f"sequential writes should have p1=0, got {result['p1_interleave_count']}"
    )


def test_write_overlap_interval_distinct_artifacts(tmp_path, golden_fixture):
    """AC-14 P2 (F-5): 반개구간 경계 off-by-one.

    [Mutant: 경계 조건 오류 (>= vs >) → RED]
    [Discriminating: F-5 두 케이스 모두 검증]
    """
    fixture = golden_fixture["F-5"]

    for testcase in fixture["test_cases"]:
        ledger = tmp_path / f"overlap-{testcase['desc']}.jsonl"
        rows = testcase["rows"]

        ledger.write_text(
            "\n".join(json.dumps(row) for row in rows),
            encoding="utf-8",
        )

        result = compute_write_overlap.compute_write_overlap(
            ledger.read_text(encoding="utf-8").splitlines()
        )

        if "expect_p2" in testcase:
            # 무겹침 기대
            assert result["p2_overlap_count"] == testcase["expect_p2"], (
                f"{testcase['desc']}: expected p2={testcase['expect_p2']}, "
                f"got {result['p2_overlap_count']}"
            )
        elif "expect_p2_gt" in testcase:
            # 겹침 기대 (> 0)
            assert result["p2_overlap_count"] > testcase["expect_p2_gt"], (
                f"{testcase['desc']}: expected p2 > {testcase['expect_p2_gt']}, "
                f"got {result['p2_overlap_count']}"
            )
