"""AC-13 — outcome vocab = stop-event REUSE, 3번째 divergent vocab 0.

Change Plan §8.1.1 RTM AC-13 (2 named test). phase1.
  - outcome enum 은 stop-event outcome vocab(success/failure/partial) 을 REUSE
    (+ inconclusive additive) — 별 vocab 신설 아님.
  - RESPAWN 은 outcome 으로 미저장(recovery_action REUSE 경로) → 3번째 divergent vocab 0.

production 로직 재구현 금지 — 실제 append_spawn_event._normalize_outcome + run_append CLI.
"""

from __future__ import annotations

import _expect

import append_spawn_event  # 실 production 모듈


def test_ac13_outcome_reuses_stop_event_vocab(tmp_path, run_append, read_rows):
    """outcome enum ⊇ stop-event outcome vocab (REUSE, remap 아님).

    stop-event {success, failure, partial} 3값이 그대로 재사용되고(값·의미 불변),
    inconclusive 만 additive → conflate 없는 harmonize.
    mutation: stop-event 값을 다른 문자열로 remap 하면(vocab 분기) RED.
    """
    # (a) enum superset 관계: stop-event vocab ⊆ outcome enum (REUSE)
    assert _expect.STOP_EVENT_OUTCOME <= _expect.OUTCOME_ENUM, (
        "outcome enum 은 stop-event vocab 을 REUSE 해야 함 (subset 관계 위반 = vocab 분기)"
    )
    # (b) production 정규화가 stop-event 값을 그대로 보존(remap 아님) — identity REUSE
    for v in sorted(_expect.STOP_EVENT_OUTCOME):
        assert append_spawn_event._normalize_outcome(v) == v, (
            f"stop-event outcome '{v}' 은 remap 없이 그대로 저장돼야 함(REUSE)"
        )
    # (c) 실 append 경로에서도 stop-event 값 구조화 저장
    ledger = tmp_path / "spawn-event.jsonl"
    run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-reuse", agent_id="agent-reuse", spawn_seq="1", outcome="partial",
    )
    # 측정 assertion: stop-event vocab 'partial' 이 그대로 저장(REUSE)
    assert read_rows(ledger)[0]["outcome"] == "partial", "stop-event 'partial' REUSE 저장 실패"


def test_ac13_no_third_divergent_vocab_respawn_via_recovery_action(tmp_path, run_append, read_rows):
    """(neg) RESPAWN 은 outcome 으로 미저장 — 3번째 divergent vocab 0.

    respawn = recovery_action REUSE 경로이지 outcome enum 확장이 아님 → outcome 으로 저장 금지.
    outcome enum = {success, inconclusive, failure, partial} 정확 4값(respawn/recovery 부재).
    mutation: respawn 을 outcome 으로 저장하거나 enum 에 추가하면 divergent 3rd vocab → RED.
    """
    # (a) enum closed-set = 정확 4값, respawn/recovery divergent 멤버 0
    assert _expect.OUTCOME_ENUM == {"success", "inconclusive", "failure", "partial"}, (
        f"outcome enum 은 정확 4값(reuse 3 + inconclusive)이어야 함, got {_expect.OUTCOME_ENUM}"
    )
    assert "respawn" not in _expect.OUTCOME_ENUM, "respawn 은 3번째 divergent outcome vocab 이면 안 됨"
    # (b) production 정규화: respawn → None (outcome enum membership reject)
    assert append_spawn_event._normalize_outcome("respawn") is None, (
        "respawn 은 outcome enum 밖 → null 이어야 함(recovery_action REUSE 경로, outcome 아님)"
    )
    # (c) 실 append: outcome=respawn 전달해도 row.outcome null (divergent vocab leak 차단)
    ledger = tmp_path / "spawn-event.jsonl"
    run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-respawn", agent_id="agent-respawn", spawn_seq="1", outcome="respawn",
    )
    # 측정 assertion: respawn 은 outcome 으로 미저장(null) — 3번째 vocab 0
    assert read_rows(ledger)[0]["outcome"] is None, (
        "respawn 이 outcome 으로 leak 저장됨 — 3번째 divergent vocab (AC-13 위반)"
    )
