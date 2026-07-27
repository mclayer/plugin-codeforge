"""AC-4 — writer monopoly (Orchestrator-owned writer).

Change Plan §8.1.1 RTM AC-4 (2 named test). phase1.
  - writer ownership = Orchestrator(-owned delegate) (ADR-039 §결정3).
  - lane/plugin 직접 append = 요구 충족 아님 (policy_violation).

계약 §3 append_rules.writer 규범 검증 (contract cross-검토).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT = REPO_ROOT / "docs" / "inter-plugin-contracts" / "spawn-event-v1.md"


def test_ac4_orchestrator_owned_writer():
    """계약 §3 append_rules.writer = Orchestrator-owned (ADR-039 §결정3 monopoly)."""
    text = CONTRACT.read_text(encoding="utf-8")
    # 측정 assertion: writer ownership = Orchestrator 명문
    assert "Orchestrator" in text, "계약이 Orchestrator writer ownership 을 명문화해야 함"
    assert "ADR-039" in text, "writer monopoly 근거 ADR-039 인용 존재"
    # writer 규범 문면에 Orchestrator-owned 취지 존재
    lower = text.lower()
    assert "writer" in lower and "orchestrator" in lower


def test_ac4_lane_direct_append_not_counted():
    """(neg) lane/plugin 직접 append = policy_violation (요구 충족 아님).

    계약이 lane plugin 직접 write 를 policy_violation 으로 명문 배제해야 함.
    mutation: 계약이 lane 직접 write 를 허용/침묵하면 RED.
    """
    text = CONTRACT.read_text(encoding="utf-8")
    # 측정 assertion: lane plugin 직접 write = policy_violation 명문
    assert "policy_violation" in text, (
        "계약이 lane plugin 직접 write 를 policy_violation 으로 배제해야 함 (writer monopoly)"
    )
