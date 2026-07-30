"""§8.10 dark-path — opt-in default-false 뒤 product 코드 경로 활성 검증.

Change Plan §8.10 (ACTIVATED). spawn-event = opt-in default false(INV-7) 뒤 product 코드 존재
→ default-off flag 뒤 경로가 실제로 활성화되는지(dead code 아님) 검증 의무.
  - opt-in ON 세션: 배선 활성 → attributed row append(captured-golden 실측 source).
  - opt-in OFF(default): 경로 dark 유지(row 0) — flag 가 실제로 gate 함 실증.

wrapper dogfood opt-in ON = dark-path 검증 대상(§8.10). consumer opt-in = §5.6 non-goal.
production 로직 재구현 금지 — 실제 append_spawn_event CLI(run_append) 호출.
"""

from __future__ import annotations


def test_darkpath_opt_in_on_attributed_path(tmp_path, run_append, read_rows, golden):
    """opt-in ON → default-off flag 뒤 경로 활성 + attributed row append(dark-path 실행 실증).

    default-off flag 뒤 코드가 opt-in ON 에서 실제 실행(dead code 아님) → attributed row 착지.
    대조군(opt-in OFF)에서 경로 dark(row 0) = flag 가 실제로 gate 함(활성화 실증의 대조 축).
    mutation: flag 뒤 경로가 no-op(dark 유지)이면 ON 에서도 row 0 → RED.
    """
    cap = golden.SESSION_CAPTURES[0]  # 실측 source (attributed 착지 재료)

    # ── dark-path ACTIVATED: opt-in ON → 경로 활성 + attributed row ──
    ledger_on = tmp_path / "on.jsonl"
    res_on = run_append(
        ledger_on, opt_in=True, story_key="CFP-2850", lane_label="구현",
        agent_type="DeveloperAgent", session_id="s-dark-on", agent_id="a-dark-on", spawn_seq="1",
        attribution_confidence="attributed", total_tokens=cap["subagent_tokens"],
        model="claude-opus-4",
    )
    assert res_on.returncode == 0, f"exit {res_on.returncode}: {res_on.stderr}"
    on_rows = read_rows(ledger_on)
    # 측정 assertion (a): opt-in ON → 경로 활성(row ≥1) — default-off 뒤 코드 실행 실증
    assert len(on_rows) >= 1, "opt-in ON 인데 row 0 — default-off flag 뒤 경로가 dead(미활성)"
    # (b): attributed path 실행 — attributed + 실측 total_tokens 착지
    assert on_rows[0]["attribution_confidence"] == "attributed", "dark-path attributed 경로 활성"
    assert on_rows[0]["total_tokens"] == cap["subagent_tokens"] == 139284, (
        "attributed path 가 실측 total_tokens 착지시켜야 함"
    )

    # ── 대조: opt-in OFF(default) → 경로 dark 유지(row 0), flag 가 실제 gate ──
    ledger_off = tmp_path / "off.jsonl"
    run_append(
        ledger_off, opt_in=False, story_key="CFP-2850", lane_label="구현",
        agent_type="DeveloperAgent", session_id="s-dark-off", agent_id="a-dark-off", spawn_seq="1",
        attribution_confidence="attributed", total_tokens=cap["subagent_tokens"],
        model="claude-opus-4",
    )
    # 측정 assertion (c): opt-in OFF → row 0 (경로 dark, flag 가 실제로 gate — 활성화 대조 축)
    assert read_rows(ledger_off) == [], (
        "opt-in OFF(default) 인데 row 생성 — default-off gate 실패(silent always-on)"
    )
