"""AC-7 — outcome closed enum 단일 분류.

Change Plan §8.1.1 RTM AC-7 (2 named test). phase2.
  - 각 기록은 closed enum 의 구조화 분류 (자유 텍스트 대체 금지).
  - free-form reason 배제 (neg).

[RED-until-landed] dev-core append_spawn_event.py --outcome flag + outcome field +
  closed-enum 정규화 (free-form → null/reject).
"""

from __future__ import annotations

import _expect


def test_ac7_outcome_closed_enum_values(tmp_path, run_append, read_rows):
    """valid closed-enum outcome 값 → 그대로 구조화 저장 (자유텍스트 아님).

    [RED-until-landed: --outcome flag + outcome field]
    """
    for value in sorted(_expect.OUTCOME_ENUM):
        ledger = tmp_path / f"spawn-event-{value}.jsonl"
        res = run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
            session_id=f"sess-out-{value}", agent_id=f"agent-out-{value}", spawn_seq="1",
            outcome=value,
        )
        assert res.returncode == 0, f"exit {res.returncode} for outcome={value}: {res.stderr}"
        row = read_rows(ledger)[0]
        # 측정 assertion: closed-enum 값이 구조화 저장됨
        assert row["outcome"] == value, f"outcome closed-enum '{value}' 저장 실패, got {row.get('outcome')}"


def test_ac7_free_form_reason_rejected(tmp_path, run_append, read_rows):
    """(neg) 자유 텍스트·비구조화 사유는 outcome 으로 저장 안 됨 (closed-enum only).

    [RED-until-landed: outcome 정규화 — free-form → null (enum membership reject)]
    mutation: free-form 을 그대로 저장하면 (T-INFO-8 free-form leak) RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    free_form = "아무 자유 텍스트 사유 free-form reason"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-freeform", agent_id="agent-freeform", spawn_seq="1",
        outcome=free_form,
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: free-form 은 outcome 으로 저장 안 됨 (null 또는 enum 아님)
    assert row.get("outcome") != free_form, "free-form reason 이 outcome 으로 leak 저장됨 (T-INFO-8 위반)"
    assert row.get("outcome") in (None, *_expect.OUTCOME_ENUM), (
        f"outcome 은 closed-enum 값이거나 null 이어야 함, got {row.get('outcome')!r}"
    )
