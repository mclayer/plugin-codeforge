"""AC-15 — captured-golden attributed row≥1 + honest-null + activation≠landing.

Change Plan §8.1.1 RTM AC-15 (3 named test). phase2 (P0-2 2층 실 데이터 bar).
  - source-available 세션: captured-golden 실측으로 attributed row ≥1.
  - 미가용 field 는 honest-null (추정 금지) — '3 field 전부 non-null' 단언 금지.
  - activation(배선 존재) ≠ landing(실 attributed 측정 착지) — 코드머지≠완료.

captured-golden fixture(tests/fixtures/cfp_2850/task_notification_usage_golden.py) 사용 —
합성-only 박제 아님(§8.7 CONDITIONAL-ACTIVE, 실 task-notification 수신 실측).
"""

from __future__ import annotations


def test_ac15_attributed_row_ge1_source_available_session(tmp_path, run_append, read_rows, golden):
    """captured-golden 실측 source → attributed row ≥1 (실세션 bar).

    golden.SESSION_CAPTURES = 실 task-notification 수신 삼중항(합성 아님). 각 capture 로
    attributed row 를 착지 → attributed row ≥1 + total_tokens = 실측 aggregate.
    mutation: attribution 미저장 or total_tokens 유실 시 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    captures = golden.SESSION_CAPTURES
    assert len(captures) >= 1, "captured-golden 실측 최소 1건 필요(source-available 세션)"

    for i, cap in enumerate(captures):
        run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
            session_id=f"sess-g{i}", agent_id=f"agent-g{i}", spawn_seq="1",
            attribution_confidence="attributed",
            total_tokens=cap["subagent_tokens"],
            tool_call_count=cap["tool_uses"],
            duration_ms=cap["duration_ms"],
            model="claude-opus-4",
        )
    rows = read_rows(ledger)
    attributed = [r for r in rows if r["attribution_confidence"] == "attributed"]
    # 측정 assertion (a): attributed row ≥1 (실세션 bar)
    assert len(attributed) >= 1, "source-available 세션에서 attributed row ≥1 이어야 함(P0-2 2층)"
    # (b): 첫 attributed row 의 total_tokens = 실측 aggregate (139284, 합성 아님)
    assert attributed[0]["total_tokens"] == captures[0]["subagent_tokens"] == 139284, (
        f"attributed row total_tokens 는 captured-golden 실측이어야 함, got {attributed[0]['total_tokens']}"
    )


def test_ac15_honest_null_for_unavailable_fields(tmp_path, run_append, read_rows, golden):
    """미가용 field = honest-null (추정 금지) — G2 crash 형상(usage block 부재).

    golden.CRASH_SHAPE: usage block 부재 → token=null(unattributed) + termination_cause
    ∈ {zero_output, error}. 미확보 field 는 null 단언(추정 저장 금지) — '전부 non-null' 단언 금지.
    mutation: 미가용인데 추정 숫자(0 or blended) 저장하면 RED.
    """
    shape = golden.CRASH_SHAPE
    assert shape["usage_block_present"] is False  # fixture 형상 확인 (crash = 블록 부재)
    ledger = tmp_path / "spawn-event.jsonl"
    run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-crash", agent_id="agent-crash", spawn_seq="1",
        attribution_confidence="unattributed",       # 블록 부재 → 실측 미확보
        termination_cause=shape["expected_termination_causes"][0],  # zero_output
    )
    row = read_rows(ledger)[0]
    # 측정 assertion (honest-null): 미확보 field 는 null (추정 금지) — 전부 non-null 단언 금지
    assert row["total_tokens"] is None, "미확보 total_tokens 는 honest-null(추정 금지)이어야 함"
    assert row["input_tokens"] is None and row["output_tokens"] is None, "미확보 4-way honest-null"
    assert row["cache_creation_input_tokens"] is None and row["cache_read_input_tokens"] is None
    assert row["cost_usd"] is None, "미확보 cost 는 honest-null(blended-rate 추정 금지)"
    # termination_cause 는 machine-observable → 저장(honest degrade 신호)
    assert row["termination_cause"] == "zero_output", "crash 형상 termination_cause 저장"


def test_ac15_activation_not_landing_bar(tmp_path, run_append, read_rows, golden):
    """activation(배선 존재) ≠ landing(실 attributed 측정 착지) — 코드머지≠완료.

    - 배선 activated(opt-in ON) 이나 실 source 미착지 → row 존재하되 total_tokens null +
      attribution != attributed = '활성화됐으나 미착지'.
    - 실 captured-golden source 착지 → attributed + total_tokens 실측 = 'landed'.
    두 상태가 구분 가능해야 함(bare 배선을 landing 으로 오판 금지 — activation≠landing).
    """
    # activated-but-not-landed: opt-in ON, 실 측정 source 미착지(unattributed default)
    ledger_act = tmp_path / "activated.jsonl"
    run_append(
        ledger_act, opt_in=True, story_key="CFP-2850", lane_label="구현",
        agent_type="DeveloperAgent", session_id="s-act", agent_id="a-act", spawn_seq="1",
    )
    act_rows = read_rows(ledger_act)
    assert len(act_rows) == 1, "opt-in ON = 배선 activated(row 존재)"
    activated_row = act_rows[0]
    # 측정 assertion (activation): 배선은 활성이나 실 측정 미착지 → total_tokens null
    assert activated_row["total_tokens"] is None, (
        "배선 activated 만으로는 landing 아님 — 실 source 미착지 시 total_tokens null(코드머지≠완료)"
    )
    assert activated_row["attribution_confidence"] != "attributed", (
        "실 source 미착지 row 를 attributed 로 오판하면 activation≠landing 위반"
    )

    # landed: captured-golden 실측 source 착지 → attributed + 실 total_tokens
    ledger_land = tmp_path / "landed.jsonl"
    cap = golden.SESSION_CAPTURES[0]
    run_append(
        ledger_land, opt_in=True, story_key="CFP-2850", lane_label="구현",
        agent_type="DeveloperAgent", session_id="s-land", agent_id="a-land", spawn_seq="1",
        attribution_confidence="attributed", total_tokens=cap["subagent_tokens"],
        model="claude-opus-4",
    )
    landed_row = read_rows(ledger_land)[0]
    # 측정 assertion (landing): 실 source 착지 → attributed + 실측 total_tokens (landed)
    assert landed_row["attribution_confidence"] == "attributed", "실 source 착지 = attributed"
    assert landed_row["total_tokens"] == 139284, "landed row 는 실측 total_tokens 보유"
    # 두 상태 구분 가능(activation ≠ landing)
    assert activated_row["total_tokens"] is None and landed_row["total_tokens"] is not None, (
        "activation(미착지 null) 과 landing(실측) 이 구분 가능해야 함"
    )
