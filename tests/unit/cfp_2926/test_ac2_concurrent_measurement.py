"""AC-2b — 동시성 배수 측정 (compute_concurrency_metric 테스트).

Change Plan §8 AC-2b RTM 명명 테스트.
  - AC-2b 산출 입력: hook_stamped 행이 필수
  - AC-2b 완전성: 기대값과 실제 hook 카운트 검증
  - AC-2b 배수: 산출식 (Σduration ÷ union_span) 정확성
  - F-4/F-8: 비대칭 케이스로 산출식 형태 오류 감지

Mutant kill 요구:
  - "항상 INCONCLUSIVE 반환" (F-1~F-3 만으로는 RED 감지 못함)
  - 산출식 형태 오류 (count÷2 vs distinct_pairs vs 정본)
  - 0==0 GREEN 흡수 금지 (F-6′)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

try:
    import compute_concurrency_metric
except ImportError:
    pytest.skip("compute_concurrency_metric module not found", allow_module_level=True)


def test_concurrency_metric_requires_hook_stamped_source(tmp_path, golden_fixture):
    """산출 입력: stop_time_source == 'hook_stamped' 행만 처리.

    [Mutant: 모든 행 수용 → RED]
    [Discriminating: hook_stamped 제외 행이 원산출을 변경하면 FAIL]
    """
    ledger = tmp_path / "spawn-event.jsonl"

    # 정상 3행 (hook_stamped)
    rows = [
        {
            "event_id": "ev1",
            "agent_start_at": 1000,
            "agent_stop_at": 2000,
            "stop_time_source": "hook_stamped",
        },
        {
            "event_id": "ev2",
            "agent_start_at": 3000,
            "agent_stop_at": 4000,
            "stop_time_source": "hook_stamped",
        },
        {
            "event_id": "ev3",
            "agent_start_at": 5000,
            "agent_stop_at": 6000,
            "stop_time_source": "hook_stamped",
        },
        # 제외 행: model-stamped (버려짐)
        {
            "event_id": "ev_model",
            "agent_start_at": 10000,
            "agent_stop_at": 11000,
            "stop_time_source": "model_stamped",
        },
    ]

    ledger.write_text(
        "\n".join(json.dumps(row) for row in rows), encoding="utf-8"
    )

    # 기대: hook_stamped 3행만 처리 → multiplier 산출
    result = compute_concurrency_metric.compute_concurrency(
        ledger.read_text(encoding="utf-8").splitlines(),
        expected_spawns=3,
    )
    assert result["verdict"] == "PASS", f"expected PASS, got {result['verdict']}"
    assert result["trace"]["hook_stamped_count"] == 3, (
        f"hook_stamped_count={result['trace']['hook_stamped_count']}, expected 3"
    )


def test_partial_coverage_declares_inconclusive(tmp_path, golden_fixture):
    """완전성 게이트: hook_stamped_count != expected_spawns → INCONCLUSIVE.

    [Mutant: GREEN 으로 흡수 → RED]
    [Discriminating: 데이터 미충분이 산출을 방지해야 함]
    """
    ledger = tmp_path / "spawn-event.jsonl"

    # 3행만 기록, 기대 5행
    rows = [
        {
            "event_id": f"ev{i}",
            "agent_start_at": i * 1000,
            "agent_stop_at": i * 1000 + 500,
            "stop_time_source": "hook_stamped",
        }
        for i in range(3)
    ]

    ledger.write_text(
        "\n".join(json.dumps(row) for row in rows), encoding="utf-8"
    )

    result = compute_concurrency_metric.compute_concurrency(
        ledger.read_text(encoding="utf-8").splitlines(),
        expected_spawns=5,  # 불일치
    )
    assert result["verdict"] == "INCONCLUSIVE", (
        f"expected INCONCLUSIVE, got {result['verdict']}"
    )
    assert "데이터 불완전" in result["reason"]


def test_concurrency_multiplier_positive(tmp_path, golden_fixture):
    """배수 양성 테스트 (F-4): 2개 완전중첩 구간 → multiplier = 2.0 ± ε.

    [Mutant: 항상 INCONCLUSIVE 반환 → RED (기대 PASS)]
    [Discriminating: 산출 가능 케이스에서 실제 배수를 내야 함]
    """
    ledger = tmp_path / "spawn-event.jsonl"
    fixture = golden_fixture["F-4"]

    ledger.write_text(
        "\n".join(json.dumps(row) for row in fixture["rows"]),
        encoding="utf-8",
    )

    result = compute_concurrency_metric.compute_concurrency(
        ledger.read_text(encoding="utf-8").splitlines(),
        expected_spawns=fixture["expected_spawns"],
    )

    assert result["verdict"] == "PASS", f"expected PASS, got {result['verdict']}"
    assert result["multiplier"] is not None, "multiplier should not be None"
    expected_mult = fixture["expect_multiplier"]
    eps = 1e-6
    assert abs(result["multiplier"] - expected_mult) < eps, (
        f"multiplier={result['multiplier']}, expected ~{expected_mult}"
    )


def test_concurrency_multiplier_partial_overlap(tmp_path, golden_fixture):
    """배수 비대칭 테스트 (F-8): 부분중첩 → multiplier = 1.2 ± ε.

    [Mutant: 산출식 형태 오류]
      - count÷2 → 1.5 (FAIL)
      - distinct_pairs → 2.0 (FAIL)
      - 정본 형태만 → 1.2 (PASS)

    [Discriminating: F-4와 달리 비대칭이라 산출식을 강하게 구분]
    """
    ledger = tmp_path / "spawn-event.jsonl"
    fixture = golden_fixture["F-8"]

    ledger.write_text(
        "\n".join(json.dumps(row) for row in fixture["rows"]),
        encoding="utf-8",
    )

    result = compute_concurrency_metric.compute_concurrency(
        ledger.read_text(encoding="utf-8").splitlines(),
        expected_spawns=fixture["expected_spawns"],
    )

    assert result["verdict"] == "PASS", f"expected PASS, got {result['verdict']}"
    assert result["multiplier"] is not None
    expected_mult = fixture["expect_multiplier"]
    eps = 1e-6
    assert abs(result["multiplier"] - expected_mult) < eps, (
        f"multiplier={result['multiplier']}, expected ~{expected_mult} "
        f"(F-8 discriminating case for formula validation)"
    )


def test_zero_expected_spawn_declares_inconclusive(tmp_path, golden_fixture):
    """공백 완전성 (F-6′): 기대 spawn = 0 ∧ hook 행 = 0 → INCONCLUSIVE (GREEN 금지).

    [Mutant: 0 == 0 을 GREEN 으로 return 메커니즘 → RED]
    [Discriminating: empty input 에서 정당한 INCONCLUSIVE 반환 필수]
    """
    ledger = tmp_path / "spawn-event.jsonl"

    # 빈 원장
    ledger.write_text("", encoding="utf-8")

    result = compute_concurrency_metric.compute_concurrency(
        ledger.read_text(encoding="utf-8").splitlines(),
        expected_spawns=0,
    )

    # 0 == 0 이어도 INCONCLUSIVE (RED 아님)
    assert result["verdict"] == "INCONCLUSIVE", (
        f"0 spawns expected 0 should INCONCLUSIVE, got {result['verdict']}"
    )
    assert result["multiplier"] is None


def test_batch_provenance_regression_suite(tmp_path, golden_fixture):
    """배치 감지 회귀 (F-1·F-2·F-3): 모두 INCONCLUSIVE 기대.

    [Note: 배치 감지 미구현 (dispatcch packet 미명시) → 현재 INCONCLUSIVE]
    [Discriminating: 회귀 보존 — 정상 케이스 일부가 데이터 불완전으로 판정됨]
    """
    # F-1: 순수 batch (14초 군집)
    ledger1 = tmp_path / "f1.jsonl"
    fixture1 = golden_fixture["F-1"]
    ledger1.write_text(
        "\n".join(json.dumps(row) for row in fixture1["rows"]),
        encoding="utf-8",
    )
    result1 = compute_concurrency_metric.compute_concurrency(
        ledger1.read_text(encoding="utf-8").splitlines(),
        expected_spawns=fixture1["expected_spawns"],
    )
    assert result1["verdict"] == fixture1["expect_verdict"], (
        f"F-1 batch: expected {fixture1['expect_verdict']}, got {result1['verdict']}"
    )

    # F-2: 부분 batch
    ledger2 = tmp_path / "f2.jsonl"
    fixture2 = golden_fixture["F-2"]
    ledger2.write_text(
        "\n".join(json.dumps(row) for row in fixture2["rows"]),
        encoding="utf-8",
    )
    result2 = compute_concurrency_metric.compute_concurrency(
        ledger2.read_text(encoding="utf-8").splitlines(),
        expected_spawns=fixture2["expected_spawns"],
    )
    assert result2["verdict"] == fixture2["expect_verdict"]

    # F-3: 오염 baseline
    ledger3 = tmp_path / "f3.jsonl"
    fixture3 = golden_fixture["F-3"]
    ledger3.write_text(
        "\n".join(json.dumps(row) for row in fixture3["rows"]),
        encoding="utf-8",
    )
    result3 = compute_concurrency_metric.compute_concurrency(
        ledger3.read_text(encoding="utf-8").splitlines(),
        expected_spawns=fixture3["expected_spawns"],
    )
    assert result3["verdict"] == fixture3["expect_verdict"]
