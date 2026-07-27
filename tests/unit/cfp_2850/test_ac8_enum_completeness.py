"""AC-8 — enum 완결성 (§1 실사례류 포괄 + gap) + CREDIT=timeout sub-case.

Change Plan §8.1.1 RTM AC-8 (3 named test). phase1.
  - outcome covers success·inconclusive (completion-quality 축).
  - termination_cause covers timeout·zero_output·error·cancelled (+normal, mechanism 축).
  - credit-exhaustion = timeout sub-case (독립 top-level enum 아님).

[RED-until-landed] dev-core outcome/termination_cause field + closed-enum 정규화.
"""

from __future__ import annotations

import _expect


def test_ac8_outcome_covers_success_inconclusive(tmp_path, run_append, read_rows):
    """outcome closed-set 이 success·inconclusive 포괄 (completion-quality — §1 실사례류)."""
    for value in ("success", "inconclusive"):
        ledger = tmp_path / f"oc-{value}.jsonl"
        res = run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
            session_id=f"s-{value}", agent_id=f"a-{value}", spawn_seq="1", outcome=value,
        )
        assert res.returncode == 0, res.stderr
        # 측정 assertion: success·inconclusive 가 enum 멤버로 수용
        assert read_rows(ledger)[0]["outcome"] == value, f"outcome '{value}' 미포괄"


def test_ac8_termination_cause_covers_timeout_zero_output_error_cancelled(tmp_path, run_append, read_rows):
    """termination_cause closed-set 이 timeout·zero_output·error·cancelled 포괄 (gap 후보)."""
    for value in ("normal", "timeout", "zero_output", "error", "cancelled"):
        ledger = tmp_path / f"tc-{value}.jsonl"
        res = run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
            session_id=f"s-{value}", agent_id=f"a-{value}", spawn_seq="1",
            termination_cause=value,
        )
        assert res.returncode == 0, res.stderr
        # 측정 assertion: mechanism enum 멤버 전수 수용 (gap 후보 ERROR/CANCELLED 포함)
        assert read_rows(ledger)[0]["termination_cause"] == value, f"termination_cause '{value}' 미포괄"
    # enum set 정합
    assert _expect.TERMINATION_CAUSE_ENUM == {"normal", "timeout", "zero_output", "error", "cancelled"}


def test_ac8_credit_exhaustion_subcase_of_timeout(tmp_path, run_append, read_rows):
    """credit-exhaustion = timeout sub-case (독립 top-level termination_cause 아님).

    Change Plan §3.2 — CREDIT-EXHAUSTED 는 timeout 통합 상위의 하위 사유. 독립 enum 값 신설 금지
    (Analyst decision-packet-v2 quota_exhausted MAJOR-bump 제거 반례 존중).
    mutation: credit_exhausted 를 별도 top-level enum 값으로 저장하면 RED.
    """
    # credit_exhausted 는 enum 멤버가 아님 (별도 top-level 금지)
    assert "credit_exhausted" not in _expect.TERMINATION_CAUSE_ENUM, (
        "credit-exhaustion 은 독립 top-level enum 이 아니어야 함 (timeout sub-case)"
    )
    # timeout 은 정규 멤버 (credit 을 흡수하는 상위)
    assert "timeout" in _expect.TERMINATION_CAUSE_ENUM

    # CLI 행위: credit_exhausted 전달 → top-level enum 값으로 저장 안 됨 (null 또는 정규화)
    ledger = tmp_path / "credit.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="s-credit", agent_id="a-credit", spawn_seq="1",
        termination_cause="credit_exhausted",
    )
    assert res.returncode == 0, res.stderr
    stored = read_rows(ledger)[0].get("termination_cause")
    # 측정 assertion: credit_exhausted 가 별도 top-level 값으로 leak 저장 안 됨
    assert stored != "credit_exhausted", (
        "credit_exhausted 가 독립 top-level termination_cause 로 저장됨 (timeout sub-case 위반)"
    )
    assert stored in (None, *_expect.TERMINATION_CAUSE_ENUM), (
        f"termination_cause 는 closed-enum 값이거나 null, got {stored!r}"
    )
