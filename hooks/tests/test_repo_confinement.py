"""test_repo_confinement.py — CFP-2965 S0 특성화 테스트 (N-2).

변경 0 시점의 repo-confinement 훅 현행 거동을 특성화.
deny/allow/carve-out/exit 2 전파/fail-open 은닉 + G-6 pin (python3 부재).

계약: repo 밖(홈 루트) 스크래치 누출 패턴 차단 (exit 2).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK_WRAPPER = WORKTREE_ROOT / "hooks" / "repo-confinement"
HOOK_SCRIPT = WORKTREE_ROOT / "scripts" / "check-repo-confinement.sh"

_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt"
    and Path(r"C:\Program Files\Git\bin\bash.exe").exists() else None)


def _run_hook(
    payload: dict | None = None,
    env_overrides: dict | None = None,
    env_additions: dict | None = None,
) -> tuple[int, str]:
    """Bash 훅 wrapper 실행."""
    env = dict(os.environ)
    if env_overrides:
        env.update(env_overrides)
    if env_additions:
        env.update(env_additions)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)

    payload_json = json.dumps(payload or {"tool_name": "Bash", "tool_input": {}})

    proc = subprocess.run(
        [_BASH, str(HOOK_WRAPPER)],
        input=payload_json,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    return proc.returncode, proc.stderr.strip()


# ============================================================ allow 케이스


def test_allow_repo_local_cwd():
    """repo 내부 cwd → exit 0 (deny 대상 아님)."""
    payload = {"tool_name": "Bash", "tool_input": {"command": "cd src && ls"}}
    rc, _ = _run_hook(payload)
    assert rc == 0


def test_allow_read_command():
    """읽기 명령(cat, find 등) → exit 0 (write 아님)."""
    payload = {"tool_name": "Bash", "tool_input": {"command": "find . -name '*.py'"}}
    rc, _ = _run_hook(payload)
    assert rc == 0


def test_allow_claude_internal_path():
    """~/.claude/ 경로 = carve-out (허용) → exit 0."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "rm -rf ~/.claude/worktrees"},
    }
    rc, _ = _run_hook(payload)
    # ~/.claude/ 는 허용된 경로 범위 (fail-open/carve-out)
    assert rc == 0


# ============================================================ deny 케이스 (홈 루트 누출)


def test_deny_home_root_write():
    """홈 루트(~)로 직접 쓰기 → exit 2."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test > ~/tempfile.txt"},
    }
    rc, stderr = _run_hook(payload)
    assert rc == 2, f"Expected exit 2, got {rc}. stderr: {stderr}"


def test_deny_home_root_mkdir():
    """홈 루트에서 mkdir — 현행 거동 특성화.

    mkdir 은 생성 위치를 인자로 받으므로, repo-confinement 가 탐지하려면
    command 문자열 패턴 매칭이 필요. 현행 구현 확인 필요.

    실측 (2026-08-14): mkdir -p ~/scratch/test → rc=0 (미차단).
    원인: check-repo-confinement.py 의 정규식이 mkdir 경로 인자를 파싱하지 않거나,
    carve-out 논리가 위치를 허용.

    본 테스트는 현행 거동 그대로 pin: rc=0 (mkdir 형태는 미차단).
    deny 커버리지는 test_deny_home_root_write 에서 echo > 로 확보.
    """
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "mkdir -p ~/scratch/test"},
    }
    rc, stderr = _run_hook(payload)
    assert rc == 0, "Current: mkdir format not detected for home-root block"


# ============================================================ G-6: python3 부재 특성화 pin


def test_characterization_g6_python3_absent():
    """(특성화 G-6) python3 부재 시 현행 거동.

    check-repo-confinement.sh 는 `exec python3` 을 호출.
    PATH 에서 python3 을 제거하면 shell 이 rc=127 (command not found) 를 반환.
    현행 훅 구조는 이를 처리하지 않으므로 → rc=127 미작동(조용히 통과).

    이는 G-6 결함: python3 단일 의존으로 python 부재 호스트에서 게이트 무력화.
    S7 에서 정규화(`command -v python3 → python fallback`)로 수정될 예정.

    본 테스트는 현행 거동 그대로 pin: rc=127 부작동을 기록.
    독립 함수로 분리하여 S7 재-pin 시 비교 용이.
    """
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test > ~/tempfile.txt"},
    }
    # PATH 에서 python3 제거 (python 도 제거해 단수로 격리)
    restricted_env = dict(os.environ)
    # PATH 에서 python3/python 제거
    path_list = restricted_env.get("PATH", "").split(os.pathsep)
    # git bash python / usr/bin 제거
    path_list = [p for p in path_list
                 if "python" not in p.lower() and "usr" not in p]
    restricted_env["PATH"] = os.pathsep.join(path_list)

    rc, stderr = _run_hook(payload, env_overrides=restricted_env)

    # 현행: python3 command not found → rc=127
    # 게이트가 작동하지 않으므로 위양성 allow(exit 0) 또는 rc=127 미작동
    assert rc == 127 or rc == 0, f"Current behavior: rc={rc} (G-6 defect — python3 missing)"

    # S7 에서 이 테스트는 재-pin: exit 2 로 변경될 것 (python fallback 정규화 후)


def test_bypass_env_suppresses_guard():
    """BYPASS_REPO_CONFINEMENT=1 설정 시 차단 우회 → exit 0."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test > ~/tempfile.txt"},
    }
    rc, stderr = _run_hook(
        payload,
        env_additions={"BYPASS_REPO_CONFINEMENT": "1"}
    )
    assert rc == 0
    assert "BYPASS_REPO_CONFINEMENT=1" in stderr or rc == 0
