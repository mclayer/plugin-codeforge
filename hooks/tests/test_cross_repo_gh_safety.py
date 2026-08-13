"""test_cross_repo_gh_safety.py — CFP-2965 S0 특성화 테스트 (N-1).

변경 0 시점의 cross-repo-gh-safety 훅 현행 거동을 특성화.
deny/allow 12+ 케이스 + 특성화 2행 (위양성·위음성 pin).

계약: write verb 매칭 시 --repo / -R / GH_REPO 확인 → 부재 시 exit 2 (block).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK = WORKTREE_ROOT / "hooks" / "cross-repo-gh-safety"

_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt"
    and Path(r"C:\Program Files\Git\bin\bash.exe").exists() else None)


def _run_hook(payload: dict, env_overrides: dict | None = None) -> tuple[int, str]:
    """Bash 훅 실행 및 반환값·stderr 캡처."""
    env = dict(os.environ)
    if env_overrides:
        env.update(env_overrides)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)

    proc = subprocess.run(
        [_BASH, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    return proc.returncode, proc.stderr.strip()


def _payload(command: str) -> dict:
    """최소 PreToolUse 페이로드 생성."""
    return {
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }


# ============================================================ deny 케이스


def test_deny_write_verb_no_repo_flag():
    """write verb 매칭되는데 --repo 없음 → exit 2."""
    rc, stderr = _run_hook(_payload("gh pr edit 94"))
    assert rc == 2, f"Expected exit 2, got {rc}. stderr: {stderr}"
    assert "BLOCKED" in stderr or "--repo" in stderr


def test_deny_issue_comment_no_repo_flag():
    """gh issue comment 에도 동일 차단 적용."""
    rc, stderr = _run_hook(_payload("gh issue comment 42 --body 'fix'"))
    assert rc == 2


def test_deny_gh_pr_merge():
    """gh pr merge 도 write verb."""
    rc, stderr = _run_hook(_payload("gh pr merge 5 --squash"))
    assert rc == 2


def test_deny_gh_pr_create():
    """gh pr create 도 write verb."""
    rc, stderr = _run_hook(_payload("gh pr create --title test"))
    assert rc == 2


# ============================================================ allow 케이스


def test_allow_with_repo_flag_short():
    """-R 플래그로 repo 명시 → exit 0."""
    rc, _ = _run_hook(_payload("gh pr edit 94 -R owner/repo"))
    assert rc == 0


def test_allow_with_repo_flag_long():
    """--repo 플래그로 repo 명시 → exit 0."""
    rc, _ = _run_hook(_payload("gh pr edit 94 --repo owner/repo"))
    assert rc == 0


def test_allow_with_gh_repo_env():
    """GH_REPO env 설정 → exit 0."""
    rc, _ = _run_hook(_payload("gh pr edit 94"), env_overrides={"GH_REPO": "owner/repo"})
    assert rc == 0


def test_allow_with_inline_gh_repo():
    """명령 인라인 GH_REPO=... prefix → exit 0."""
    rc, _ = _run_hook(_payload("GH_REPO=owner/repo gh pr edit 94"))
    assert rc == 0


def test_allow_readonly_verb():
    """gh pr view / list 등 read-only verb → exit 0 (write 아님)."""
    rc, _ = _run_hook(_payload("gh pr view 94"))
    assert rc == 0


def test_allow_non_bash_tool():
    """tool_name != Bash → exit 0 (scope 외)."""
    payload = {"tool_name": "Edit", "tool_input": {"command": "gh pr edit 94"}}
    rc, _ = _run_hook(payload)
    assert rc == 0


def test_allow_no_payload():
    """빈 payload → exit 0 (fail-open)."""
    rc, _ = _run_hook({})
    assert rc == 0


# ============================================================ 특성화 2행


def test_characterization_echo_command_with_gh_pattern():
    """(특성화 1) echo 명령에 gh pr edit 문자열 포함.

    현행 거동: sed 정규식이 "gh pr edit" 을 매칭 → false-positive deny(exit 2).
    이는 echo 명령이지만 grep 정규식이 문자열 패턴만 보므로 차단됨.

    의도: echo 는 write 아니므로 실제로는 차단할 이유 없지만,
    현행 훅의 정규식 기반 단순 매칭은 거짓 양성을 생성.

    본 테스트는 현행 거동 그대로 pin: exit 2 위양성 존재함을 기록.
    """
    rc, _ = _run_hook(_payload('echo "gh pr edit 94"'))
    # 현행: exit 2 (false-positive 위양성)
    assert rc == 2, "S1 이후 재검증 시 exit 0 으로 변경될 예정"


def test_characterization_escaped_quotes_gh_pattern():
    """(특성화 2) gh 명령에 이스케이프된 따옴표.

    현행 거동: gh pr edit 구조가 있어도 \\" 로 이스케이프되면
    sed 캡처가 깨져 매칭 실패 → exit 0 위음성.

    의도: 이스케이프가 제대로 handling 되면 여전히 block 해야 하지만,
    현행 sed 정규식은 단순하여 우회 가능.

    본 테스트는 현행 거동 그대로 pin: exit 0 위음성 존재함을 기록.
    """
    rc, _ = _run_hook(_payload('gh pr edit 94 --body "this is \\"escaped\\""'))
    # 현행: exit 0 (false-negative 위음성 — 본래는 block 해야 함)
    assert rc == 0, "S1 이후 재검증 시 exit 2 로 변경될 가능성"


def test_bypass_env_allows_write_verb():
    """BYPASS_CROSS_REPO_GH_SAFETY=1 설정 시 차단 우회 → exit 0."""
    rc, stderr = _run_hook(
        _payload("gh pr edit 94"),
        env_overrides={"BYPASS_CROSS_REPO_GH_SAFETY": "1"}
    )
    assert rc == 0
    assert "BYPASS_CROSS_REPO_GH_SAFETY=1" in stderr
