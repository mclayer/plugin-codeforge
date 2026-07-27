"""AC-1 — P0-2 실측 source = task-notification usage block (field별 분해).

Change Plan §8.1.1 RTM AC-1 (5 named test). phase2.
  - token(subagent_tokens)·tool_uses 는 task-notification per-instance usage block 실측
    source 에서만 (SDK usage undercount·hook·추정 배제).
  - duration_ms 는 usage block OR Orchestrator wall-clock 중 하나의 실측값 (둘 다 실측).
  - aggregate-only(tier-2) 시 cost_usd=null (model 有에도) — P3 회귀방어 (discriminating).

production 의존(RED-until-landed): dev-core-2850 이 append_spawn_event.py 에
  --total-tokens flag + total_tokens row field (19→23) 를 착지시켜야 GREEN.
  discriminating cost-null 핀(spawn_event_pricing.cost_usd)은 현행에서 GREEN(mutation-RED 실증).
"""

from __future__ import annotations

import spawn_event_pricing  # 실 production 모듈 (tests/conftest.py 가 scripts/lib 주입)


def test_ac1_token_from_task_notification_usage_block(tmp_path, run_append, read_rows, golden):
    """token 값 = task-notification usage block 실측 aggregate(subagent_tokens) → total_tokens.

    [RED-until-landed: --total-tokens flag + total_tokens field — dev-core append_spawn_event.py]
    """
    ledger = tmp_path / "spawn-event.jsonl"
    cap = golden.SESSION_CAPTURES[0]  # {subagent_tokens:139284, tool_uses:25, duration_ms:524995}

    res = run_append(
        ledger,
        story_key="CFP-2850",
        lane_label="구현",
        agent_type="DeveloperAgent",
        session_id="sess-ac1-token",
        agent_id="agent-ac1-token",
        spawn_seq="1",
        attribution_confidence="attributed",
        total_tokens=cap["subagent_tokens"],
        model="claude-opus-4",
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    assert len(rows) == 1, "single row expected"
    # 측정 assertion: total_tokens == usage block subagent_tokens 실측 aggregate
    assert rows[0]["total_tokens"] == 139284, (
        f"total_tokens 는 usage block subagent_tokens 실측이어야 함, got {rows[0].get('total_tokens')}"
    )


def test_ac1_tool_uses_from_usage_block(tmp_path, run_append, read_rows, golden):
    """tool_uses 값 = task-notification usage block tool_uses → tool_call_count (clean)."""
    ledger = tmp_path / "spawn-event.jsonl"
    cap = golden.SESSION_CAPTURES[0]

    res = run_append(
        ledger,
        story_key="CFP-2850",
        lane_label="구현",
        agent_type="DeveloperAgent",
        session_id="sess-ac1-tools",
        agent_id="agent-ac1-tools",
        spawn_seq="1",
        tool_call_count=cap["tool_uses"],
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    # 측정 assertion: tool_call_count == usage block tool_uses 실측
    assert rows[0]["tool_call_count"] == 25, (
        f"tool_call_count 는 usage block tool_uses 실측이어야 함, got {rows[0]['tool_call_count']}"
    )


def test_ac1_duration_wallclock_or_usage_dual_source(tmp_path, run_append, read_rows, golden):
    """duration_ms = usage block OR Orchestrator wall-clock 중 하나의 실측값 (둘 다 실측).

    dual-source: (i) usage block duration_ms (ii) wall-clock elapsed — 둘 다 numeric 저장.
    """
    # leg (i): usage block duration
    ledger_a = tmp_path / "spawn-event-usage.jsonl"
    cap = golden.SESSION_CAPTURES[0]
    res_a = run_append(
        ledger_a, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-dur-a", agent_id="agent-dur-a", spawn_seq="1",
        duration_ms=cap["duration_ms"],
    )
    assert res_a.returncode == 0, res_a.stderr
    # 측정 assertion (i): usage block duration 실측 저장
    assert read_rows(ledger_a)[0]["duration_ms"] == 524995

    # leg (ii): Orchestrator wall-clock elapsed (spawn dispatch→notification 수신)
    ledger_b = tmp_path / "spawn-event-wallclock.jsonl"
    wallclock_ms = 61234  # Orchestrator 실 wall-clock 측정치 (추정 아님 — 실 elapsed)
    res_b = run_append(
        ledger_b, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-dur-b", agent_id="agent-dur-b", spawn_seq="1",
        duration_ms=wallclock_ms,
    )
    assert res_b.returncode == 0, res_b.stderr
    # 측정 assertion (ii): wall-clock 실측 저장 (dual-source 어느 쪽도 실측)
    assert read_rows(ledger_b)[0]["duration_ms"] == 61234


def test_ac1_sdk_usage_undercount_excluded(tmp_path, run_append, read_rows, golden):
    """(neg) SDK `usage`(subagent 제외 undercount)·hook·추정치로 대체 금지 — append 는
    Orchestrator 가 넘긴 task-notification 측정 aggregate 만 저장하고 자체 재파생 0.

    discriminating: append 가 SDK 값을 스스로 재계산(undercount)했다면 stored != 전달 aggregate → RED.
    부가 신호: 0-API(source 내부 Anthropic/SDK re-derive import 부재).
    [RED-until-landed: total_tokens field]
    """
    ledger = tmp_path / "spawn-event.jsonl"
    measured_aggregate = golden.SESSION_CAPTURES[1]["subagent_tokens"]  # 216489 (task-notification)
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-sdk-neg", agent_id="agent-sdk-neg", spawn_seq="1",
        attribution_confidence="attributed", total_tokens=measured_aggregate,
        model="claude-opus-4",
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: stored == 전달된 task-notification 측정 aggregate (SDK undercount 로 축소 안 됨)
    assert row["total_tokens"] == 216489, (
        "total_tokens 는 task-notification 측정 aggregate 여야 하며 SDK undercount 로 대체 금지"
    )
    # 0-API 부가 신호: append source 는 SDK/Anthropic re-derive import 0
    src = (spawn_event_pricing.__file__)  # noqa: F841 — import 존재만 확인 (0-API 로컬 상수)
    import pathlib
    append_src = pathlib.Path(spawn_event_pricing.__file__).parent / "append_spawn_event.py"
    text = append_src.read_text(encoding="utf-8")
    assert "import anthropic" not in text and "requests.get" not in text, (
        "append 경로는 0-API — SDK/외부 usage re-derive 금지 (task-notification 값만 저장)"
    )


def test_ac1_aggregate_only_cost_null_despite_model_present(tmp_path, run_append, read_rows):
    """(reg P3, discriminating) aggregate-only(tier-2) 시 cost_usd=null — model 有에도.

    핀: spawn_event_pricing.cost_usd 가 `any(t is None) → None` (L103-106) 이므로
    4-way(input/output/cache_creation/cache_read) 부재 시 model 이 있어도 cost=null (honest-null).
    blended-rate 로 단일 aggregate 에서 cost 를 추정 저장하면 RED.

    본 test 는 현행에서 GREEN + mutation-RED 실증 가능 (discriminating 성질):
      - (a) 순수 pricing 함수 핀 (4-way None → cost None)
      - (b) CLI tier-2 경로 (attributed + model, 4-way 부재 → row.cost_usd is None)
    """
    # (a) discriminating pricing-function 핀 (mutation: blended-rate → cost 반환하면 RED)
    for model in ("claude-opus-4", "claude-sonnet-4", "claude-haiku"):
        assert spawn_event_pricing.cost_usd(model, None, None, None, None) is None, (
            f"[P3] aggregate-only(4-way None) 시 cost=null 이어야 함 (model={model}) — "
            "blended-rate 추정 저장 금지 (ADR-119)"
        )
    # 대조: 4-way 완비 시엔 numeric (positive control — 핀이 vacuous 아님)
    assert isinstance(
        spawn_event_pricing.cost_usd("claude-opus-4", 1000, 500, 0, 0), (int, float)
    ), "4-way 완비 시엔 cost 파생돼야 함 (positive control)"

    # (b) CLI tier-2 경로: attributed + model, 4-way 미전달 → row.cost_usd is None
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-cost-null", agent_id="agent-cost-null", spawn_seq="1",
        attribution_confidence="attributed", model="claude-opus-4",
        # 4-way(input/output/cache) 미전달 = aggregate-only tier-2
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: model 有에도 aggregate-only → cost_usd null
    assert row["cost_usd"] is None, (
        f"[P3] aggregate-only(model 有, 4-way 부재) 시 cost_usd=null 이어야 함, got {row['cost_usd']}"
    )
