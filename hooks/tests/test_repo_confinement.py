"""test_repo_confinement.py — CFP-2965 S0 특성화 테스트 (N-2).

변경 0 시점의 repo-confinement 훅 현행 거동을 특성화.
deny/allow/carve-out/exit 2 전파/fail-open 은닉 + G-6 pin (인터프리터 부재 — S7 재-pin 반영).

계약: repo 밖(홈 루트) 스크래치 누출 패턴 차단 (exit 2).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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


# ============================================================ G-6: 인터프리터 정규화 재-pin (S7)
#
# 재-pin 선언 (의도 변경 — Change Plan §3.1 판정 2 / SecArch R-19):
#   구 pin = "python3 부재 → rc=127 미작동" 특성화. S7 이 check-repo-confinement.sh 의
#   `exec python3` 단일 의존을 sibling 패턴(command -v python3 → python → exit 0)으로 정규화
#   → 같은 커밋에서 의도 변경으로 재-pin.
#     ① 정의역 분리 — python3 존재 호스트 delta 0 / 부재+python 존재 = inactive→active (강화 방향)
#     ② §1 보존 대상 = deny·fail-open 방향 — 바뀌는 것은 종료 코드 127→0 이지 방향 아님
#     ③ rc=127 은 선언된 계약(hook exit ∈ {0,2}) 부재 — AC-13 충족
#     ④ 커밋 위생 = 성능 hunk 와 분리된 독립 커밋


def _bash_bin_dirs() -> list[str]:
    """Git-Bash 실행에 필요한 최소 PATH 구성 (python 계열 디렉터리 제외)."""
    bash_dir = Path(_BASH).parent                       # .../Git/bin
    return [str(bash_dir), str(bash_dir.parent / "usr" / "bin")]


def _probe_interpreters(path_value: str) -> tuple[bool, bool]:
    """주어진 PATH 하 (python3 존재, python 존재) 실측 — mock seam 자체를 검증 (ADR-171).

    seam 이 실제로 원하는 상태를 만들었는지 확인하지 않으면 "게이트가 작동해서 통과"와
    "seam 이 안 걸려서 통과"가 구별되지 않는다.
    """
    proc = subprocess.run(
        [_BASH, "-c",
         "command -v python3 >/dev/null 2>&1 && echo Y || echo N; "
         "command -v python >/dev/null 2>&1 && echo Y || echo N"],
        capture_output=True, text=True, env={**os.environ, "PATH": path_value},
    )
    lines = proc.stdout.split()
    assert len(lines) == 2, f"probe 실패: {proc.stdout!r} {proc.stderr!r}"
    return lines[0] == "Y", lines[1] == "Y"


def test_repin_g6_python3_absent_python_present_gate_active(tmp_path):
    """(재-pin G-6) python3 부재 + python 존재 → 게이트 **정상 작동** (exit 2).

    구 거동은 `exec python3` 단일 의존이라 rc=127 (게이트 무력화 + transcript error notice).
    정규화 후에는 python fallback 으로 판정이 살아난다 (inactive → active 강화).
    """
    shim = tmp_path / "python"
    shim.write_text('#!/bin/sh\nexec "%s" "$@"\n' % sys.executable.replace("\\", "/"),
                    encoding="utf-8", newline="\n")
    shim.chmod(0o755)

    path_value = os.pathsep.join([str(tmp_path)] + _bash_bin_dirs())
    has_py3, has_py = _probe_interpreters(path_value)
    assert not has_py3, "seam 무효 — python3 가 여전히 PATH 에 있음"
    assert has_py, "seam 무효 — python shim 이 PATH 에서 안 잡힘"

    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test > ~/tempfile.txt"},
    }
    rc, stderr = _run_hook(payload, env_overrides={"PATH": path_value})

    assert rc == 2, f"python fallback 미작동 — rc={rc} (기대 2). stderr: {stderr[:200]}"
    assert "BLOCKED" in stderr, f"deny 메시지 부재: {stderr[:200]}"


def test_repin_g6_both_interpreters_absent_fail_open(tmp_path):
    """(재-pin G-6) python3·python 둘 다 부재 → fail-open **exit 0** (127 아님).

    hook 계약 정의역 {0, 2} 밖 종료 코드(127)를 내지 않는 것이 본 재-pin 의 핵심.
    게이트 미작동 자체는 현행과 동일 (델타 = 종료 코드 정규화 · ModuleArch 이의 2 잔존 declare).
    """
    path_value = os.pathsep.join(_bash_bin_dirs())
    has_py3, has_py = _probe_interpreters(path_value)
    assert not has_py3 and not has_py, f"seam 무효 — python3={has_py3}, python={has_py}"

    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "echo test > ~/tempfile.txt"},
    }
    rc, stderr = _run_hook(payload, env_overrides={"PATH": path_value})

    assert rc == 0, f"인터프리터 부재 fail-open 위반 — rc={rc} (기대 0, 특히 127 금지)"
    assert rc != 127, "rc=127 = hook 계약 정의역 밖 (transcript error notice 가시)"


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
