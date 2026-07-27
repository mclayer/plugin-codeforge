"""AC-2 — honest-null (field별 혼합).

Change Plan §8.1.1 RTM AC-2 (3 named test). phase2.
  - 실측 source 미가용 field = null (attribution != attributed), 추정 저장 금지.
  - field별 attributed/null 혼합 허용.
  - fake-attributed 금지 (source 부재 시 attributed 로 오인 저장 금지).

전부 현행 append_spawn_event.py _derive_token_cost 불변식 기반 → GREEN (mutation-RED 변별).
"""

from __future__ import annotations


def test_ac2_missing_source_field_null_not_estimated(tmp_path, run_append, read_rows):
    """실측 source 미가용 field = null (추정치 대체 금지).

    unattributed 인데 token flag 를 줘도 → 전부 null (추정 합산 금지, ADR-119).
    mutation: naive-sum(placeholder→numeric 저장) 이면 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac2-null", agent_id="agent-ac2-null", spawn_seq="1",
        attribution_confidence="unattributed",
        input_tokens=1000, output_tokens=500,  # 호출자가 줘도 무시 (source 부정확)
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: 미가용 source → null (추정치 아님)
    assert row["input_tokens"] is None, f"미가용 field 는 null 이어야 함, got {row['input_tokens']}"
    assert row["output_tokens"] is None
    assert row["cost_usd"] is None


def test_ac2_field_mixed_attributed_null(tmp_path, run_append, read_rows):
    """field별 attributed/null 혼합 허용 — 일부 실측(duration/tool) + 일부 null(token).

    aggregate-only 세션 형상: duration_ms·tool_call_count 실측, 4-way token null.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac2-mix", agent_id="agent-ac2-mix", spawn_seq="1",
        attribution_confidence="attributed",
        duration_ms=524995, tool_call_count=25, model="claude-opus-4",
        # 4-way token 미전달 → null (혼합)
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: 실측 field 는 값, 미가용 field 는 null (혼합)
    assert row["duration_ms"] == 524995, "실측 duration 은 저장"
    assert row["tool_call_count"] == 25, "실측 tool_call 은 저장"
    assert row["input_tokens"] is None, "미가용 4-way token 은 null (혼합 정상)"
    assert row["cost_usd"] is None


def test_ac2_no_fake_attributed_when_source_absent(tmp_path, run_append, read_rows):
    """(neg) source 부재 시 attributed 로 오인 저장 금지.

    default(미지정) = unattributed → token/cost null 강제. attributed 로 승격 안 됨.
    mutation: source 부재인데 attributed 로 저장(fake) 하면 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac2-fake", agent_id="agent-ac2-fake", spawn_seq="1",
        # attribution_confidence 미지정 (default unattributed) + token 없음
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: source 부재 → unattributed (fake-attributed 금지)
    assert row["attribution_confidence"] == "unattributed", (
        f"source 부재 시 attributed 로 fake 저장 금지, got {row['attribution_confidence']}"
    )
    assert row["input_tokens"] is None and row["cost_usd"] is None
