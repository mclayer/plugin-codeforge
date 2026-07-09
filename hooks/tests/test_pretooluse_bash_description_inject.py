"""test_pretooluse_bash_description_inject.py — CFP-2587 Phase 2 §8 (Bash inject hook, TDD).

계약 SSOT: Story CFP-2587 §7.10 / ADR-143 Amendment 1 표면②.
Subprocess-level (bash 로 hooks/pretooluse-bash-description-inject fork). 검증 초점:
  · subject source = payload TOP-LEVEL agent_type (self) — NOT tool_input.subagent_type (T-2/AC-8).
  · top-level Bash (agent_type 부재) = EXCLUDE (no stdout) — §7.7-3 dispatcher 명 미주입.
  · tool_name != Bash → no stdout.
  · fail-open: 어떤 실패도 exit 0.
bash 부재 환경(CI ubuntu 외)에서는 skip (precedent = test_pretooluse_inline_write_gate.py).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import check_spawn_description_prefix as csdp

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK = WORKTREE_ROOT / "hooks" / "pretooluse-bash-description-inject"
FIXTURES = WORKTREE_ROOT / "tests" / "spike" / "cfp-2587-updatedinput-honor" / "fixtures"

_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt"
    and Path(r"C:\Program Files\Git\bin\bash.exe").exists() else None)

pytestmark = pytest.mark.skipif(_BASH is None, reason="bash interpreter 부재 (Windows non-Git-Bash CI)")


def _run_hook(payload: dict) -> tuple[int, str]:
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)
    proc = subprocess.run([_BASH, str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8", env=env)
    return proc.returncode, proc.stdout.strip()


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_bash_in_subagent_injects_with_agent_type_subject():
    """T-2/AC-8: subagent 안 Bash → payload agent_type(self) 를 subject 로 주입."""
    payload = _load("bash-in-subagent.json")            # agent_type present
    orig_cmd = payload["tool_input"]["command"]
    rc, out = _run_hook(payload)
    assert rc == 0
    hso = json.loads(out)["hookSpecificOutput"]
    ui = hso["updatedInput"]
    assert ui["command"] == orig_cmd                    # whole-echo 보존
    at = csdp._sanitize_subject(payload["agent_type"])
    assert ui["description"].startswith("[%s] " % at)   # subject = agent_type
    assert csdp.RE_PREFIX.match(ui["description"]) is not None
    assert "permissionDecision" not in hso              # G4
    assert "additionalContext" not in hso               # Bash = reminder 비대상 (§7.3)


def test_top_level_bash_excluded_no_stdout():
    """§7.7-3: top-level Bash (agent_type 부재) → EXCLUDE (no stdout), exit 0."""
    payload = _load("bash-top-level.json")              # agent_type absent
    assert "agent_type" not in payload or not payload.get("agent_type")
    rc, out = _run_hook(payload)
    assert rc == 0
    assert out == ""                                    # dispatcher 명 절대 미주입


def test_subject_source_is_agent_type_not_subagent_type():
    """T-2 (§2.3 HIGH 경고): agent_type 와 tool_input.subagent_type 동시 존재 시
    Bash 표면 subject = agent_type (self), NOT subagent_type (헤더 소스)."""
    payload = {"tool_name": "Bash",
               "agent_id": "abc123",
               "agent_type": "ResearcherAgent",                    # self
               "tool_input": {"command": "ls",
                              "subagent_type": "ArchitectAgent",   # stray 헤더-source
                              "description": "list files"}}
    rc, out = _run_hook(payload)
    assert rc == 0
    desc = json.loads(out)["hookSpecificOutput"]["updatedInput"]["description"]
    assert desc.startswith("[ResearcherAgent] ")        # agent_type, NOT ArchitectAgent
    assert "ArchitectAgent" not in desc


def test_non_bash_tool_no_stdout():
    payload = {"tool_name": "Read", "agent_type": "X",
               "tool_input": {"file_path": "/x", "description": "read"}}
    rc, out = _run_hook(payload)
    assert rc == 0 and out == ""


def test_already_conformant_no_reinjection():
    """T-4 idempotency at hook level: 이미 conformant → no stdout (재주입 skip)."""
    payload = {"tool_name": "Bash", "agent_type": "X",
               "tool_input": {"command": "ls", "description": "[X] 07/09 19:30 - already"}}
    rc, out = _run_hook(payload)
    assert rc == 0 and out == ""


def test_malformed_payload_fail_open():
    """T-6: malformed JSON payload → exit 0, no stdout (원 tool 무차단)."""
    env = dict(os.environ); env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)
    proc = subprocess.run([_BASH, str(HOOK)], input="{not json",
                          capture_output=True, text=True, encoding="utf-8", env=env)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


def test_empty_payload_fail_open():
    rc, out = _run_hook({}) if False else (None, None)  # placeholder to keep parity
    env = dict(os.environ); env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)
    proc = subprocess.run([_BASH, str(HOOK)], input="", capture_output=True, text=True, encoding="utf-8", env=env)
    assert proc.returncode == 0 and proc.stdout.strip() == ""


def test_bypass_env_suppresses(monkeypatch):
    payload = _load("bash-in-subagent.json")
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)
    env["BYPASS_CODEFORGE_BASH_DESCRIPTION_INJECT"] = "1"
    proc = subprocess.run([_BASH, str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True, encoding="utf-8", env=env)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""                    # injection suppressed
