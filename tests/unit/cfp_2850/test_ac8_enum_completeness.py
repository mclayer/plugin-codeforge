"""AC-8 — enum 완결성 (§1 실사례류 포괄 + gap) + CREDIT=timeout sub-case.

Change Plan §8.1.1 RTM AC-8 (5 named test). phase1.
  - outcome covers success·inconclusive (completion-quality 축).
  - termination_cause covers timeout·zero_output·error·cancelled (+normal, mechanism 축).
  - credit-exhaustion = timeout sub-case (독립 top-level enum 아님).
  - ★F-CR-005: production 상수 ↔ 기대 enum **양방향 일치** (초과/누락 0) — 아래 참조.

[RED-until-landed] dev-core outcome/termination_cause field + closed-enum 정규화.
"""

from __future__ import annotations

import _expect

import aggregate_spawn_event  # 실 production aggregate 모듈 (비성공 closed-set SSOT)
import append_spawn_event  # 실 production 모듈 (enum 상수 SSOT — 테스트 내 재선언 금지)


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


# ─────────── ★F-CR-005 — production 상수 ↔ 기대 enum 양방향 일치 (drift 봉인) ───────────


def test_ac8_production_enum_constants_bidirectional_match():
    """(disc) production `_TERMINATION_CAUSES` / `_OUTCOMES` == 기대 enum (양방향, 초과·누락 0).

    구 assert 는 "기대 값이 저장되는가"(단방향 subset)만 봤기에 production 이 **enum 값을
    추가**해도(예: credit_exhausted 독립 top-level 부활, respawn 추가) 통과했다.
    본 test 는 production 상수를 **직접 대조**한다 (테스트 내 enum 재선언 금지 — _expect 가
    계약 §2/§3 mirror SSOT).
    mutation: production enum 에 1값 추가/삭제 → set 불일치로 RED (양방향 discriminating).
    """
    # 측정 assertion (a): termination_cause 양방향 일치
    assert append_spawn_event._TERMINATION_CAUSES == _expect.TERMINATION_CAUSE_ENUM, (
        f"termination_cause enum drift:\n"
        f"  production 초과: {append_spawn_event._TERMINATION_CAUSES - _expect.TERMINATION_CAUSE_ENUM}\n"
        f"  production 누락: {_expect.TERMINATION_CAUSE_ENUM - append_spawn_event._TERMINATION_CAUSES}"
    )
    # (b): outcome 동형 양방향 일치
    assert append_spawn_event._OUTCOMES == _expect.OUTCOME_ENUM, (
        f"outcome enum drift:\n"
        f"  production 초과: {append_spawn_event._OUTCOMES - _expect.OUTCOME_ENUM}\n"
        f"  production 누락: {_expect.OUTCOME_ENUM - append_spawn_event._OUTCOMES}"
    )


def test_ac8_aggregate_nonsuccess_set_derived_from_production_outcomes():
    """(disc) aggregate 비성공 closed-set == production outcome enum − {success} (양방향).

    실패율 numerator / 낭비집계 대상 = 비성공 outcome. append 측 enum 이 확장됐는데
    aggregate 측 closed-set 이 안 따라오면 신규 outcome 이 조용히 '성공' 취급된다
    (silent 누락 — AC-9/AC-10 오집계). 두 production 상수를 직접 대조해 봉인한다.
    mutation: 한쪽만 확장하면 RED.
    """
    expected_nonsuccess = set(append_spawn_event._OUTCOMES) - {"success"}
    actual = set(aggregate_spawn_event._NONSUCCESS_OUTCOMES)
    # 측정 assertion: 양방향 일치 (초과 = 미지 값 산입 / 누락 = 신규 outcome 이 성공 취급)
    assert actual == expected_nonsuccess, (
        f"aggregate 비성공 set drift:\n  초과: {actual - expected_nonsuccess}\n"
        f"  누락(성공으로 오취급): {expected_nonsuccess - actual}"
    )
