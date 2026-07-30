"""AC-3 (구현리뷰 FIX Iter2 F-CR-001 ④/⑤) — hooks/subagent-stop spawn-completion COUNTER opt-in gate.

Change Plan §8.1.1 RTM AC-3 확장 (counter 축) + AC-12 count-reconcile ON-regime pin.

기존 `test_ac3_opt_in.py` 는 **ledger row 만** 검사해 hook COUNTER 를 못 잡는
non-discriminating 상태였다 (F-CR-001 ④). 본 파일은 opt-in OFF 에서
`.claude/ledger/spawn-completion.count` 가 **미생성/무증가** 임을 실 hook 실행으로 gate 한다:
counter 가 opt-in gate **밖**에 있으면(현행 hook L222-226 opt-in-INDEPENDENT) RED.

  - OFF-1 (config 부재)          → counter 0            [production 의존: counter opt-in gate]
  - OFF-2 (enabled AND channel)  → channel false 면 0    [production 의존: AND semantics]
  - OFF-3 (config read 실패)     → fail-closed 0        [production 의존: fail-closed]
  - ON   (둘 다 true)            → 실행 1회당 +1        (positive control — OFF 단언이 vacuous 아님)
  - ⑤ ON-regime reconcile        → counter 2 vs recorded 1 → gap 1 gap_observed

production 로직 재구현 금지 — 실제 `hooks/subagent-stop` 을 bash 로 fork + 실
`reconcile_spawn_completion_count` (count 판독/대조) 직접 호출.

subprocess fork 진정성 (본 agent §distinct-marker 의무): exit code(hook 은 항상 0 —
never-block) 단독 판정 금지 → hook 고유 stderr sentinel `[codeforge-wrapper-subagent-stop]`
병행 assert. sentinel 부재 = fork 미발생/조기 종료 → OFF 단언이 vacuous 로 통과하는
false-negative 차단.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import reconcile_spawn_completion_count as recon  # 실 production reconcile 모듈

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK = REPO_ROOT / "hooks" / "subagent-stop"
COUNT_REL = Path(".claude") / "ledger" / "spawn-completion.count"
LEDGER_REL = Path(".claude") / "ledger" / "spawn-event.jsonl"

# hook 고유 stdout/stderr sentinel (one-channel rule marker — hooks/subagent-stop L32)
HOOK_MARKER = "[codeforge-wrapper-subagent-stop]"

# bash 인터프리터 (Linux/macOS/Windows Git Bash) — 기존 hook 테스트 패턴 mirror
_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe"
    if os.name == "nt" and Path(r"C:\Program Files\Git\bin\bash.exe").exists()
    else None
)

pytestmark = pytest.mark.skipif(_BASH is None, reason="bash interpreter 부재 (non-Git-Bash CI)")


def _hook_python_supports_yaml():
    """hook 이 쓰는 인터프리터(python3|python)가 PyYAML 을 import 할 수 있는지 실측 probe.

    config fixture 를 project.json(항상) + project.yaml(가능 시) 양쪽으로 깔기 위함 —
    production gate 가 yaml-우선 reader 든 json reader 든 동일하게 ON 을 관측하도록.
    (yaml 미가용인데 project.yaml 을 깔면 parse 실패 → fail-closed 로 오판될 수 있음.)
    """
    for name in ("python3", "python"):
        exe = shutil.which(name)
        if not exe:
            continue
        try:
            proc = subprocess.run([exe, "-c", "import yaml"], capture_output=True)
        except OSError:  # pragma: no cover — 인터프리터 실행 불가
            continue
        return proc.returncode == 0
    return False


_YAML_FOR_HOOK = _hook_python_supports_yaml()


def _write_telemetry_config(project_dir, telemetry_block):
    """project.json (+ 가능 시 project.yaml) 에 telemetry 블록 기록.

    JSON 텍스트는 YAML 의 valid subset 이므로 project.yaml 에도 동일 바이트를 쓴다
    (테스트 프로세스의 PyYAML 의존 0).
    """
    payload = json.dumps({"telemetry": telemetry_block}, ensure_ascii=False, indent=2)
    (project_dir / "project.json").write_text(payload, encoding="utf-8")
    if _YAML_FOR_HOOK:
        (project_dir / "project.yaml").write_text(payload, encoding="utf-8")


def _write_broken_config(project_dir):
    """config read/parse 실패 강제 (fail-closed 경로) — json/yaml 양쪽 모두 malformed."""
    broken = "{ this is not valid json/yaml : : ["
    (project_dir / "project.json").write_text(broken, encoding="utf-8")
    if _YAML_FOR_HOOK:
        (project_dir / "project.yaml").write_text(broken, encoding="utf-8")


def _make_project(tmp_path, name, telemetry_block=None, broken=False):
    project = tmp_path / name
    project.mkdir(parents=True, exist_ok=True)
    if broken:
        _write_broken_config(project)
    elif telemetry_block is not None:
        _write_telemetry_config(project, telemetry_block)
    return project


def _run_hook(project_dir, agent_id="agent-ac3-counter", session_id="sess-ac3-counter"):
    """실제 hooks/subagent-stop 을 bash 로 fork (production 재구현 금지).

    env: CLAUDE_PROJECT_DIR = tmp project (ledger·counter 전량 tmp 격리),
         CLAUDE_PLUGIN_ROOT = repo root (append_*.py 해결).
    BYPASS_CODEFORGE_SUBAGENT_STOP 는 제거 — bypass 로 인한 vacuous no-op 차단.
    """
    env = dict(os.environ)
    env.pop("BYPASS_CODEFORGE_SUBAGENT_STOP", None)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    env["CLAUDE_PLUGIN_ROOT"] = str(REPO_ROOT)
    env["CLAUDE_SESSION_ID"] = session_id
    payload = json.dumps(
        {"subagent_type": "DeveloperAgent", "agent_id": agent_id, "subagent_completed": True}
    )
    return subprocess.run(
        [_BASH, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        cwd=str(REPO_ROOT),
    )


def _assert_hook_forked_and_never_blocked(proc):
    """hook 실행 불변식 + fork 진정성 sentinel (exit code 단독 판정 금지).

    (a) exit 0 (ADR-115 §결정 2 never-block)
    (b) stdout 무출력 (block/permissionDecision 절대 미등장)
    (c) hook 고유 stderr sentinel — fork 가 실제 발생했음의 distinct-marker
    """
    assert proc.returncode == 0, f"hook 은 항상 exit 0 이어야 함, got {proc.returncode}: {proc.stderr}"
    assert proc.stdout.strip() == "", f"hook stdout 무출력 불변 위반: {proc.stdout!r}"
    assert HOOK_MARKER in proc.stderr, (
        f"hook fork 진정성 sentinel {HOOK_MARKER!r} 부재 — hook 이 실제 실행되지 않았을 수 있음"
        f"(exit-code-only 판정이었다면 vacuous 통과). stderr={proc.stderr!r}"
    )


def _counter(project_dir):
    """실 production counter 판독기로 완료 계수 산출 (미생성 → 0, 재구현 금지)."""
    return recon.count_hook_completions(str(project_dir / COUNT_REL))


# ─────────────────── ④ opt-in OFF → counter 미생성/무증가 (discriminating) ───────────────────


def test_ac3_hook_counter_no_op_when_opt_in_config_absent(tmp_path):
    """(disc) config 부재(opt-in default false) → spawn-completion.count 미생성/무증가.

    [RED-until-landed: hook COUNTER 를 _opt_in_enabled gate 뒤로 이동]
    현행 hook 은 counter 를 opt-in-INDEPENDENT 로 append → 본 test RED.
    mutation(counter 를 gate 밖으로 되돌림) 시 counter 1 → RED (discriminating).
    """
    project = _make_project(tmp_path, "proj-optin-absent")
    proc = _run_hook(project)
    _assert_hook_forked_and_never_blocked(proc)

    # 측정 assertion: opt-in OFF → hook 완료 계수 0 (counter 미생성/무증가)
    assert _counter(project) == 0, (
        "opt-in OFF(config 부재)인데 spawn-completion.count 가 증가함 — "
        "COUNTER 가 opt-in gate 밖에 있음(silent always-on telemetry)"
    )


def test_ac3_hook_counter_no_op_when_channel_flag_false(tmp_path):
    """(disc) telemetry.enabled=true ∧ channels.spawn_event=false → counter 무증가 (AND semantics).

    [RED-until-landed: counter opt-in gate = telemetry.enabled AND channels.spawn_event]
    mutation(OR 로 완화)이면 counter 1 → RED.
    """
    project = _make_project(
        tmp_path, "proj-channel-false",
        telemetry_block={"enabled": True, "channels": {"spawn_event": False}},
    )
    proc = _run_hook(project)
    _assert_hook_forked_and_never_blocked(proc)

    # 측정 assertion: channel flag false → counter 0 (AND 게이트)
    assert _counter(project) == 0, (
        "channels.spawn_event=false 인데 counter 증가 — opt-in AND semantics 위반"
    )


def test_ac3_hook_counter_fail_closed_on_unreadable_config(tmp_path):
    """(disc) config read/parse 실패 → fail-closed (counter 무증가).

    [RED-until-landed: config read 실패 = fail-closed]
    mutation(read 실패 시 fail-open 으로 counter append)이면 counter 1 → RED.
    """
    project = _make_project(tmp_path, "proj-broken-config", broken=True)
    proc = _run_hook(project)
    _assert_hook_forked_and_never_blocked(proc)

    # 측정 assertion: 읽기 실패 → counter 0 (fail-closed, 추정 opt-in 금지)
    assert _counter(project) == 0, (
        "config read 실패인데 counter 증가 — fail-closed 위반(불확실 시 telemetry OFF 여야 함)"
    )


def test_ac3_hook_counter_increments_when_opt_in_on(tmp_path):
    """(positive control) opt-in ON → 실행 1회당 counter +1 (OFF 단언이 vacuous 아님 실증).

    OFF test 들이 "hook 이 애초에 counter 를 못 만든다"로 통과하는 vacuous 를 배제한다:
    동일 fixture 배선에서 ON 이면 실제로 counter 가 증가함을 실측.
    """
    project = _make_project(
        tmp_path, "proj-optin-on",
        telemetry_block={"enabled": True, "channels": {"spawn_event": True}},
    )
    proc1 = _run_hook(project, agent_id="agent-on-1")
    _assert_hook_forked_and_never_blocked(proc1)
    # 측정 assertion (a): ON 1회 → counter 1
    assert _counter(project) == 1, (
        f"opt-in ON 1회 실행 → counter 1 이어야 함(배선 활성 실증), got {_counter(project)}"
    )

    proc2 = _run_hook(project, agent_id="agent-on-2")
    _assert_hook_forked_and_never_blocked(proc2)
    # (b): ON 2회 → counter 2 (monotonic append, 덮어쓰기 아님)
    assert _counter(project) == 2, (
        f"opt-in ON 2회 실행 → counter 2 이어야 함(누적 append), got {_counter(project)}"
    )


# ─────────────────── ⑤ AC-12 count-reconcile = opt-in ON fixture ───────────────────


def test_ac12_count_reconcile_under_opt_in_on_regime(tmp_path, run_append):
    """(⑤) AC-12 COUNT reconcile 은 opt-in **ON** regime 에서 성립 (counter 가 opt-in 종속).

    counter 가 opt-in gate 뒤로 이동하면 OFF regime 의 gap 은 정의상 0 (counter 자체가 0) →
    survivorship gap 관측은 ON regime 에서만 의미. 본 test 는 ON fixture 로:
      - 실 hook 2회 완료 → counter 2 (crash-safe 분모)
      - Orchestrator single-writer 가 동일 ledger 에 spawn-event row 1 (1건 누락 = survivorship)
      → reconcile gap 1 / status gap_observed 가 VISIBLE.
    부수 gate: 같은 ledger 에 hook 이 쓴 self-context-v1 row 가 섞여도 recorded_row_count 는
      spawn-event-v1 만 계수(record type isolation) — 오염 산입 시 gap 이 뒤집혀 RED.
    """
    project = _make_project(
        tmp_path, "proj-reconcile-on",
        telemetry_block={"enabled": True, "channels": {"spawn_event": True}},
    )
    # hook 완료 2건 (opt-in ON → counter 2)
    for i in range(2):
        proc = _run_hook(project, agent_id=f"agent-recon-{i}")
        _assert_hook_forked_and_never_blocked(proc)
    count_path = project / COUNT_REL
    ledger = project / LEDGER_REL
    assert recon.count_hook_completions(str(count_path)) == 2, (
        "opt-in ON regime 전제: hook 완료 2건이 counter 에 계수돼야 함 "
        "(counter 0 이면 본 reconcile 시나리오 자체가 vacuous)"
    )

    # Orchestrator single-writer: 완료 2건 中 1건만 recorded (1건 emit 실패 = survivorship)
    res = run_append(
        ledger, opt_in=True, story_key="CFP-2850", lane_label="구현",
        agent_type="DeveloperAgent", session_id="sess-recon-on",
        agent_id="agent-recon-0", spawn_seq="1",
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"

    result = recon.reconcile(str(count_path), str(ledger))
    # 측정 assertion: ON regime gap = 2 - 1 = 1 (VISIBLE), self-context row 미산입
    assert result["hook_completion_count"] == 2, f"ON regime counter 2 기대, got {result}"
    assert result["recorded_row_count"] == 1, (
        f"recorded 는 spawn-event-v1 row 만 계수해야 함(self-context-v1 오염 미산입), got {result}"
    )
    assert result["gap"] == 1 and result["status"] == "gap_observed", (
        f"ON regime survivorship gap 1 이 gap_observed 로 VISIBLE 해야 함, got {result}"
    )


def test_ac12_hook_writes_no_spawn_event_row_under_opt_in_on(tmp_path, read_rows):
    """(reg, behavioral) opt-in ON 에서도 hook 은 **spawn-event-v1 row 를 0개** 쓴다 (RETIRED).

    text-grep 프록시(식별자 부재)가 아니라 실 hook 실행 결과로 single-writer 를 확증한다:
      - ledger 파일에 도달은 함 (self-context-v1 row ≥1) → "아무것도 안 써서 0" vacuous 배제
      - 그러나 spawn-event-v1 row 는 0 (production reader `count_recorded_rows` 로 판정)
      - disjoint COUNTER 는 1 (retire 후에도 crash-safe 분모 보존)
    mutation: hook 에 spawn-event row append 를 되살리면 recorded 1 → RED.
    """
    project = _make_project(
        tmp_path, "proj-retire-on",
        telemetry_block={"enabled": True, "channels": {"spawn_event": True}},
    )
    proc = _run_hook(project, agent_id="agent-retire")
    _assert_hook_forked_and_never_blocked(proc)

    ledger = project / LEDGER_REL
    rows = read_rows(ledger)
    # 전제(비-vacuous): hook 이 실제로 공유 ledger 에 도달함 (self-context 채널은 잔존)
    self_ctx = [r for r in rows if r.get("schema_version") == "self-context-v1"]
    assert len(self_ctx) >= 1, (
        f"opt-in ON 인데 hook 이 ledger 에 아무것도 못 씀 — 'spawn row 0' 단언이 vacuous. rows={rows}"
    )
    # 측정 assertion (a): spawn-event-v1 row 0 (row-write RETIRED — single-writer 보존)
    assert recon.count_recorded_rows(str(ledger)) == 0, (
        f"hook 이 spawn-event-v1 row 를 append 함 — single-writer(Orchestrator) 위반, rows={rows}"
    )
    assert all(r.get("schema_version") != "spawn-event-v1" for r in rows)
    # (b): disjoint COUNTER 는 보존 (retire 가 counter 까지 지우지 않음)
    assert _counter(project) == 1, (
        f"retire 후에도 spawn-completion COUNTER 는 1 이어야 함(F-B 분모), got {_counter(project)}"
    )
