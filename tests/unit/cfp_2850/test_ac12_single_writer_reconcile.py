"""AC-12 — single-writer topology + within-path event_id dedup + COUNT reconcile(F-B).

Change Plan §8.1.1 RTM AC-12 (4 named test). phase2.
  - hooks/subagent-stop 의 spawn-event row-write RETIRED (single-writer = Orchestrator).
  - deterministic event_id → within-path 이중 append dedup(read-time).
  - retire 후 hook∥Orchestrator 이중계산 0.
  - **F-B (discriminating)**: hook spawn-completion COUNTER > recorded row COUNT →
    survivorship gap 가시(gap 은닉 시 RED).

production 로직 재구현 금지 — 실제 hooks/subagent-stop 텍스트 +
  scripts/lib/reconcile_spawn_completion_count.py (import + CLI) + append_spawn_event
  _compute_event_id 직접 호출.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import append_spawn_event  # 실 production 모듈 (tests/conftest.py 가 scripts/lib 주입)
import reconcile_spawn_completion_count as recon  # 실 production reconcile 모듈

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK = REPO_ROOT / "hooks" / "subagent-stop"
RECONCILE_SCRIPT = REPO_ROOT / "scripts" / "lib" / "reconcile_spawn_completion_count.py"


def _run_reconcile_cli(count_path, ledger_path):
    """실제 reconcile CLI 를 subprocess 로 fork (production 재구현 금지).

    reconcile 은 record-only → exit 0 무조건. 따라서 **exit code 단독 판정 금지** —
    도메인 sentinel(status/gap) 을 stdout JSON 으로 병행 assert (distinct-marker 의무,
    본 agent §외부 script subprocess fork 규율). Returns (returncode, parsed_json|None).
    """
    cmd = [
        sys.executable, str(RECONCILE_SCRIPT), "check",
        "--count-path", str(count_path),
        "--ledger-path", str(ledger_path),
        "--json",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    parsed = None
    try:
        parsed = json.loads(proc.stdout.strip())
    except (json.JSONDecodeError, AttributeError):
        parsed = None
    return proc.returncode, parsed


def test_ac12_single_writer_hook_spawn_append_retired():
    """(reg) hooks/subagent-stop 의 spawn-event row-write RETIRED — single-writer 보존.

    mutation: hook 이 append_spawn_event 재호출(spawn-event row-write 부활)하면 이중 writer
      → event_id cross-path 불일치로 이중계수(AC-12 위반) → 이 reg 가 RED.
    """
    text = HOOK.read_text(encoding="utf-8")
    # 측정 assertion (a): hook 은 spawn-event row-writer(append_spawn_event) 를 호출 안 함(retired)
    assert "append_spawn_event" not in text, (
        "hooks/subagent-stop 가 spawn-event row-write 를 부활시킴 — single-writer(Orchestrator) 위반"
    )
    # (b): retire 명문 marker 존재
    assert "RETIRED" in text, "spawn-event row-write RETIRE marker 부재 (single-writer 근거 소실)"
    # (c): 경량 disjoint COUNTER 는 보존(crash-safe 분모) — spawn-completion.count append
    assert "spawn-completion.count" in text, (
        "retire 후 경량 spawn-completion COUNTER(disjoint 채널) 가 보존돼야 함(F-B reconcile 분모)"
    )


def test_ac12_deterministic_event_id_within_path_dedup(tmp_path, run_append, read_rows):
    """deterministic event_id → within-path 재append dedup(read-time first-wins).

    동일 (session_id, agent_id, spawn_seq) → 동일 event_id → 재시도/이중 append 여도
    recorded COUNT(read-time dedup)는 1 로 collapse(at-least-once idempotent, §11.6).
    """
    # (a) 순수 함수 결정성 핀: 동일 입력 → 동일 event_id (random UUID 금지)
    e1 = append_spawn_event._compute_event_id("sh", "ah", "1")
    e2 = append_spawn_event._compute_event_id("sh", "ah", "1")
    e_diff = append_spawn_event._compute_event_id("sh", "ah", "2")
    # 측정 assertion: 동일 입력 event_id 동일, spawn_seq 다르면 상이
    assert e1 == e2, "동일 (session,agent,seq) → 동일 event_id (deterministic, InfraOpArch §11.6)"
    assert e1 != e_diff, "spawn_seq 다르면 event_id 상이 (within-path 구분)"

    # (b) within-path dedup: 동일 identity 2회 + distinct 1회 → 물리 3행, recorded 2
    ledger = tmp_path / "spawn-event.jsonl"
    for _ in range(2):  # 동일 identity 재append (dup event_id)
        run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
            session_id="sess-dup", agent_id="agent-dup", spawn_seq="7",
        )
    run_append(  # distinct identity (별 event_id)
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-dup", agent_id="agent-distinct", spawn_seq="8",
    )
    physical = read_rows(ledger)
    assert len(physical) == 3, f"물리 append 3행 기대(dedup 前), got {len(physical)}"
    # 측정 assertion: production read-time dedup → recorded 2 (dup event_id collapse)
    recorded = recon.count_recorded_rows(str(ledger))
    assert recorded == 2, (
        f"deterministic event_id read-time dedup → recorded 2 이어야 함(3 물리행 中 dup 1 collapse), "
        f"got {recorded}"
    )


def test_ac12_no_double_count_after_retire(tmp_path, run_append):
    """(reg) retire 후 hook∥Orchestrator 이중계산 0.

    완료 1건: Orchestrator single-writer 가 spawn-event row 1 append + hook 이 disjoint
    COUNTER 1 line append. hook 은 spawn-event row 를 더 이상 안 쓰므로 recorded=1(2 아님).
    mutation: hook 이 spawn-event row 도 쓰면 recorded=2 → gap!=0 → 이 reg RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    count_path = tmp_path / "spawn-completion.count"
    # Orchestrator single-writer: 완료 1건 → spawn-event row 1
    run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-nodouble", agent_id="agent-nodouble", spawn_seq="1",
    )
    # hook disjoint COUNTER: 동일 완료 1건 → count line 1 (retired hook 의 경량 tally 형상)
    count_path.write_text("2026-07-28T01:00:00Z\n", encoding="utf-8")

    result = recon.reconcile(str(count_path), str(ledger))
    # 측정 assertion: recorded=1 (hook 이 spawn-event row 이중 append 안 함 — retire)
    assert result["recorded_row_count"] == 1, (
        f"완료 1건 → recorded 1 이어야 함(hook 이중 write 부활 시 2 → RED), got {result['recorded_row_count']}"
    )
    assert result["hook_completion_count"] == 1
    # gap 0(aligned) — 이중계산 0
    assert result["gap"] == 0 and result["status"] == "aligned", (
        f"retire 후 이중계산 0(gap 0 aligned)이어야 함, got {result}"
    )


def test_ac12_count_reconcile_hook_counter_vs_recorded_gap_visible(tmp_path, run_append):
    """(disc — F-B) hook COUNTER > recorded row COUNT → survivorship gap 가시.

    counter 3 completions, recorded 1 → gap 2 가 reconcile 출력에 VISIBLE(gap_observed).
    discriminating: gap 을 은닉(recorded==counter 로 위장)하면 status aligned 로 뒤집혀 RED.

    subprocess fork — exit code(record-only exit 0) 단독 판정 금지 → stdout JSON
    sentinel(status/gap) 병행 assert (distinct-marker 규율).
    """
    ledger = tmp_path / "spawn-event.jsonl"
    count_path = tmp_path / "spawn-completion.count"
    # hook COUNTER = 3 completions (crash·notification-loss 포함 platform-trigger 계수)
    count_path.write_text("t1\nt2\nt3\n", encoding="utf-8")
    # recorded = 1 spawn-event row (Orchestrator single-writer 가 2건 놓침 = survivorship)
    run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-gap", agent_id="agent-gap", spawn_seq="1",
    )

    returncode, parsed = _run_reconcile_cli(count_path, ledger)
    # distinct-marker: 도메인 sentinel(status/gap) 병행 assert — exit code 단독 판정 금지
    assert parsed is not None, "reconcile --json stdout 파싱 실패 (fork 미발생 or 형상 붕괴)"
    # 측정 assertion (primary sentinel): gap 2 가 VISIBLE + status gap_observed
    assert parsed["status"] == "gap_observed", (
        f"counter(3) > recorded(1) → gap_observed 여야 함(gap 은닉 시 aligned 로 뒤집혀 RED), "
        f"got status={parsed.get('status')!r}"
    )
    assert parsed["gap"] == 2, (
        f"survivorship gap = 3-1 = 2 가 VISIBLE 이어야 함, got gap={parsed.get('gap')!r}"
    )
    assert parsed["hook_completion_count"] == 3 and parsed["recorded_row_count"] == 1
    # secondary: record-only → exit 0 (gate 아님, INV-5). gap 은 관측치이지 실패 판정 아님.
    assert returncode == 0, f"reconcile 은 record-only exit 0(gate 아님)이어야 함, got {returncode}"
