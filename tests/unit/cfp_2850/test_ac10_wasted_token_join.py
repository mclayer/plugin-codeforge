"""AC-10 — 낭비토큰 outcome-conditioned join.

Change Plan §8.1.1 RTM AC-10 (2 named test). phase2.
  - outcome × 실측 token join 가능 (낭비집계는 outcome 분류에 인과 후행).
  - 추정 token 으로 낭비량 계산 금지 (neg — attributed non-null token 만).

aggregate gate (DeveloperPL 회부 ①): 낭비집계 = 실 aggregate_spawn_event.wasted_tokens /
  wasted_tokens_by_group 모듈 호출로 검증 (inline 재계산 금지 — discriminating).
  낭비 numerator = 비성공 closed-set {failure, inconclusive, partial} 의 실측 total_tokens 합.
"""

from __future__ import annotations

import aggregate_spawn_event  # 실 production aggregate 모듈 (read-only, conftest sys.path 주입)


def test_ac10_wasted_token_outcome_conditioned_join(tmp_path, run_append, read_rows):
    """비성공 outcome × 실측 total_tokens join → 낭비토큰 = 실 aggregate 모듈 산출.

    4 row: (Dev,opus,failure,100000) (Dev,opus,inconclusive,50000)
           (Dev,opus,success,999999) (Arch,sonnet,partial,30000)
      → wasted_total = 100000+50000+30000 = 180000 (success 제외, 비성공 실측 합).
      → by_group[(Dev,opus)] = 150000, [(Arch,sonnet)] = 30000.
    mutation(aggregate 가 success token 산입 or 비성공 set 오판)이면 총합 달라져 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    specs = [
        ("DeveloperAgent", "claude-opus-4", "failure", 100000, "s1", "a1"),
        ("DeveloperAgent", "claude-opus-4", "inconclusive", 50000, "s2", "a2"),
        ("DeveloperAgent", "claude-opus-4", "success", 999999, "s3", "a3"),  # 제외 대상
        ("ArchitectAgent", "claude-sonnet-4", "partial", 30000, "s4", "a4"),
    ]
    for role, model, outcome, tokens, sess, aid in specs:
        res = run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type=role,
            session_id=sess, agent_id=aid, spawn_seq="1",
            attribution_confidence="attributed", model=model,
            outcome=outcome, total_tokens=tokens,
        )
        assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    assert len(read_rows(ledger)) == 4

    # 실 aggregate 모듈 호출 (inline 재계산 아님)
    rows = aggregate_spawn_event.load_rows(str(ledger), story_key="CFP-2850")
    # 측정 assertion (a): 낭비 총합 = 비성공 실측 token 합 (success 999999 제외)
    assert aggregate_spawn_event.wasted_tokens(rows) == 180000, (
        f"wasted_tokens = 비성공(failure+inconclusive+partial) 실측 합 180000 이어야 함 "
        f"(success 제외), got {aggregate_spawn_event.wasted_tokens(rows)}"
    )
    # (b): 역할·모델별 낭비 join
    by_group = aggregate_spawn_event.wasted_tokens_by_group(rows)
    assert by_group[("DeveloperAgent", "claude-opus-4")] == 150000, "Dev/opus 낭비 = 100000+50000"
    assert by_group[("ArchitectAgent", "claude-sonnet-4")] == 30000, "Arch/sonnet 낭비 = 30000"


def test_ac10_no_estimated_token_in_waste_calc(tmp_path, run_append, read_rows):
    """(neg) 추정 token 낭비산입 금지 — null token(비attributed) row 는 aggregate 가 정직 제외.

    비성공(failure) row 2건: attributed(70000) + unattributed(token=null).
    aggregate.wasted_tokens 는 null-token row 를 추정치로 메꾸지 않고 제외 → 70000.
    mutation(aggregate 가 null 을 추정치·0 아닌 값으로 산입)이면 70000 ≠ 결과 → RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    run_append(  # 비성공 + attributed 실측 → 산입
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="s-attr", agent_id="a-attr", spawn_seq="1",
        attribution_confidence="attributed", model="claude-opus-4",
        outcome="failure", total_tokens=70000,
    )
    run_append(  # 비성공 + unattributed → total_tokens null → 제외 (추정 금지)
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="s-unattr", agent_id="a-unattr", spawn_seq="1",
        attribution_confidence="unattributed", outcome="failure", total_tokens=999999,
    )
    rows = aggregate_spawn_event.load_rows(str(ledger), story_key="CFP-2850")

    # honest-null 확인: unattributed failure row 의 total_tokens 는 null (추정 미대체)
    null_failure_present = any(
        r.get("outcome") == "failure" and r.get("total_tokens") is None for r in rows
    )
    assert null_failure_present, "unattributed failure row 의 token 은 null 이어야 함(추정 미대체)"
    # 측정 assertion: aggregate 가 null-token row 제외 → 실측 70000 만 (추정 산입 금지)
    assert aggregate_spawn_event.wasted_tokens(rows) == 70000, (
        f"aggregate 는 null-token row 를 추정치로 산입하면 안 됨(honest-null), "
        f"실측 70000 만이어야 함, got {aggregate_spawn_event.wasted_tokens(rows)}"
    )
