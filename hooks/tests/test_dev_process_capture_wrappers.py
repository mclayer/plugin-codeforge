"""test_dev_process_capture_wrappers.py — CFP-2965 S0 특성화 테스트 (N-3).

변경 0 시점의 dev-process-capture wrapper 훅 현행 거동을 특성화.
pre/post capture wrapper 전 경로 exit 0 ∧ stdout == b"".

계약: record-only 훅 → 모든 경로 exit 0, stdout 미방출(>/dev/null).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
PRETOOLUSE_CAPTURE = WORKTREE_ROOT / "hooks" / "pretooluse-dev-process-capture"
POSTTOOLUSE_CAPTURE = WORKTREE_ROOT / "hooks" / "posttooluse-dev-process-capture"

_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt"
    and Path(r"C:\Program Files\Git\bin\bash.exe").exists() else None)


def _run_capture_hook(
    hook_path: Path,
    payload: dict | None = None,
    env_overrides: dict | None = None,
) -> tuple[int, bytes, bytes]:
    """Capture 훅 실행 (stdout/stderr 원본 반환)."""
    env = dict(os.environ)
    if env_overrides:
        env.update(env_overrides)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)

    payload_json = json.dumps(payload or {
        "tool_name": "Bash",
        "tool_input": {"command": "ls"},
        "event_name": "PreToolUse" if "pretooluse" in hook_path.name else "PostToolUse",
    })

    proc = subprocess.run(
        [_BASH, str(hook_path)],
        input=payload_json.encode("utf-8"),
        capture_output=True,
        env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr


# ============================================================ pretooluse-dev-process-capture


def test_pretooluse_capture_exit_0_normal():
    """정상 payload → exit 0."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
        "event_name": "PreToolUse",
    }
    rc, stdout, stderr = _run_capture_hook(PRETOOLUSE_CAPTURE, payload)
    assert rc == 0


def test_pretooluse_capture_no_stdout():
    """stdout 미방출 (>/dev/null) → stdout == b''."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
        "event_name": "PreToolUse",
    }
    rc, stdout, stderr = _run_capture_hook(PRETOOLUSE_CAPTURE, payload)
    assert stdout == b"" or stdout.strip() == b"", f"Expected empty stdout, got {stdout}"


def test_pretooluse_capture_fail_open():
    """python 부재 등 오류 → 여전히 exit 0 (fail-open)."""
    # python 을 PATH 에서 제거
    env = dict(os.environ)
    path_list = env.get("PATH", "").split(os.pathsep)
    path_list = [p for p in path_list if "python" not in p.lower()]
    env["PATH"] = os.pathsep.join(path_list)

    payload = {"tool_name": "Bash", "tool_input": {"command": "ls"}}
    rc, _, _ = _run_capture_hook(
        PRETOOLUSE_CAPTURE,
        payload,
        env_overrides=env
    )
    # fail-open: python 부재해도 exit 0 (record-only 훅은 tool call block 금지)
    assert rc == 0


# ============================================================ posttooluse-dev-process-capture


def test_posttooluse_capture_exit_0_normal():
    """정상 payload → exit 0."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test"},
        "event_name": "PostToolUse",
    }
    rc, stdout, stderr = _run_capture_hook(POSTTOOLUSE_CAPTURE, payload)
    assert rc == 0


def test_posttooluse_capture_no_stdout():
    """stdout 미방출 → stdout == b''."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test"},
        "event_name": "PostToolUse",
    }
    rc, stdout, stderr = _run_capture_hook(POSTTOOLUSE_CAPTURE, payload)
    assert stdout == b"" or stdout.strip() == b""


def test_posttooluse_capture_fail_open():
    """python 부재 → exit 0 fail-open."""
    env = dict(os.environ)
    path_list = env.get("PATH", "").split(os.pathsep)
    path_list = [p for p in path_list if "python" not in p.lower()]
    env["PATH"] = os.pathsep.join(path_list)

    payload = {"tool_name": "Bash", "tool_input": {"command": "echo done"}}
    rc, _, _ = _run_capture_hook(
        POSTTOOLUSE_CAPTURE,
        payload,
        env_overrides=env
    )
    assert rc == 0


# ============================================================ 동형 구조


def test_both_capture_hooks_same_exit_pattern():
    """Pre/Post capture 훅 모두 동일 exit 0 패턴."""
    payload = {"tool_name": "Bash", "tool_input": {"command": "pwd"}}

    rc_pre, stdout_pre, _ = _run_capture_hook(PRETOOLUSE_CAPTURE, payload)
    rc_post, stdout_post, _ = _run_capture_hook(POSTTOOLUSE_CAPTURE, payload)

    # 둘 다 exit 0
    assert rc_pre == 0 and rc_post == 0
    # 둘 다 stdout 미방출
    assert stdout_pre == b"" and stdout_post == b""
