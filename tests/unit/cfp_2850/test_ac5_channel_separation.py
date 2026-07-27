"""AC-5 — 채널 분리 (measure ≠ outcome 재해석 금지).

Change Plan §8.1.1 RTM AC-5 (2 named test). phase1.
  - spawn-event.jsonl 단일 채널, escape 없이 (basename 고정).
  - measure field 를 outcome 의미로 재해석 금지 (별 field 축).

single_channel = 현행 basename 고정 → GREEN.
measure≠outcome = outcome 이 measure 와 별개 key (RED-until-landed: outcome field).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

_MEASURE_FIELDS = {
    "input_tokens", "output_tokens", "cache_creation_input_tokens",
    "cache_read_input_tokens", "cost_usd", "duration_ms", "tool_call_count",
    "total_tokens", "elapsed_seconds",
}


def test_ac5_single_channel_no_cross_write(tmp_path, run_append):
    """단일 채널 — storage_path override 해도 basename=spawn-event.jsonl 고정 (cross-write 방지).

    stop-event.jsonl 등 타 채널로 escape 없이 spawn-event.jsonl basename 으로만 기록.
    ledger-path 를 생략하고 storage-path 만 주면 basename 고정 규칙이 적용된다
    (contract §3 storage_path_override_rule).
    """
    parent = tmp_path / "custom_ledger_dir"
    res = run_append(
        None,  # ledger-path 생략 → storage-path + 고정 basename 경로 적용
        storage_path=str(parent),
        story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac5-chan", agent_id="agent-ac5-chan", spawn_seq="1",
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    # 측정 assertion: 기록 대상 basename = spawn-event.jsonl 고정 (단일 채널·escape 없음)
    assert (parent / "spawn-event.jsonl").exists(), (
        "storage-path override 시 basename 은 spawn-event.jsonl 로 고정 (단일 채널·cross-write 방지)"
    )
    # cross-write 방지: stop-event.jsonl 등 타 basename 미생성
    assert not (parent / "stop-event.jsonl").exists(), "타 채널 cross-write 금지"


def test_ac5_measure_field_not_reinterpreted_as_outcome(tmp_path, run_append, read_rows):
    """measure field 를 outcome 의미로 재해석 금지 — outcome 은 measure 와 별개 field 축.

    [RED-until-landed: outcome field — dev-core append_spawn_event.py]
    outcome 은 token/duration measure 로부터 파생/재해석되지 않는 독립 enum field.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac5-out", agent_id="agent-ac5-out", spawn_seq="1",
        attribution_confidence="attributed", total_tokens=139284, model="claude-opus-4",
        outcome="success", termination_cause="normal",
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: outcome 은 measure key 와 disjoint 한 독립 field
    assert "outcome" in row, "outcome 은 별개 field 로 존재해야 함 (measure 재해석 아님)"
    assert row["outcome"] not in _MEASURE_FIELDS, "outcome 값이 measure 의미로 재해석되면 안 됨"
    assert "outcome" not in _MEASURE_FIELDS, "outcome key 는 measure 축과 disjoint"
