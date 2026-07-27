"""AC-3 — opt-in OFF no-op + 데이터없음↔미작동 구분.

Change Plan §8.1.1 RTM AC-3 (2 named test). phase1.
  - telemetry.enabled ∨ channels.spawn_event 중 하나라도 false → no-op(row 0).
  - "데이터 없음"(wiring active·미emit) 과 "배선 미작동"(opt-in off) 구분.

현행 append_spawn_event.py _opt_in_enabled 기반 → GREEN.
"""

from __future__ import annotations


def test_ac3_opt_in_off_noop_zero_rows(tmp_path, run_append, read_rows):
    """opt-in flag 미지정 → no-op(row 0, exit 0). silent always-on 금지.

    mutation: silent always-on(off 인데 row 생성) 이면 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, opt_in=False,  # --telemetry-enabled/--spawn-event-enabled 미부착
        story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac3-off", agent_id="agent-ac3-off", spawn_seq="1",
    )
    # 측정 assertion (a): exit 0 (비차단)
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    # 측정 assertion (b): row 0 (파일 미생성 또는 빈 파일)
    assert read_rows(ledger) == [], "opt-in OFF 인데 row 생성됨 (silent always-on)"


def test_ac3_data_absent_vs_wiring_inactive_distinguish(tmp_path, run_append, read_rows):
    """"데이터 없음" ↔ "배선 미작동" 구분.

    - wiring inactive (opt-in OFF): ledger 파일 미생성 = 배선 자체가 no-op.
    - wiring active + emit: ledger 파일 생성 + row ≥1 = 배선 작동(데이터 존재).
    두 상태가 파일 존재/row 유무로 구분 가능해야 함 (혼동 시 "0 rows" 오진).
    """
    # wiring inactive (opt-in off) → 파일 미생성
    ledger_off = tmp_path / "off.jsonl"
    run_append(
        ledger_off, opt_in=False, story_key="CFP-2850", lane_label="구현",
        agent_type="DeveloperAgent", session_id="s-off", agent_id="a-off", spawn_seq="1",
    )
    wiring_inactive = not ledger_off.exists() or read_rows(ledger_off) == []

    # wiring active + emit → 파일 생성 + row 1
    ledger_on = tmp_path / "on.jsonl"
    run_append(
        ledger_on, opt_in=True, story_key="CFP-2850", lane_label="구현",
        agent_type="DeveloperAgent", session_id="s-on", agent_id="a-on", spawn_seq="1",
    )
    wiring_active_with_data = ledger_on.exists() and len(read_rows(ledger_on)) == 1

    # 측정 assertion: 두 상태가 구분 가능 (미작동 vs 데이터-존재)
    assert wiring_inactive, "opt-in OFF = 배선 미작동(파일 미생성)이어야 함"
    assert wiring_active_with_data, "opt-in ON emit = 배선 작동(row 존재)이어야 함"
