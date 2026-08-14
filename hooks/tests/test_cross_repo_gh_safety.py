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
    """(특성화 1) echo 명령에서 gh pr edit 문자가 매칭되는 사례.

    sed 절단 기전 (hooks/cross-repo-gh-safety:55): sed 's/".*//' 는
    JSON payload 의 첫 "(큰따옴표) 문자에서 절단.

    위양성 실재형: `echo gh pr edit 94` (따옴표 제거 — sed 절단 불가 → grep 공백후 gh 매칭 → exit 2).
    이는 echo 명령(write 아님)이지만 grep 정규식이 space-prefixed gh 를 매칭.

    현행 거동: bare space form 에서 grep 이 gh pr 를 찾음 → exit 2 (false-positive).
    본 테스트는 현행 거동 그대로 pin: exit 2 위양성 존재함을 기록.

    CP §5 S0 예시 literal (`echo "gh pr edit 94"`) 은 JSON quoting 미반영 —
    특성화 의도 보존 재구성 (PL 진단 2026-08-14).
    """
    rc, _ = _run_hook(_payload("echo gh pr edit 94"))
    # 현행: exit 2 (false-positive 위양성 — echo 는 쓰기 아님, grep space-suffix match)
    assert rc == 2, "Grep matches space-prefixed gh pattern"


def test_characterization_escaped_quotes_gh_pattern():
    """(특성화 2) gh 명령에 JSON-escaped 이중따옴표 포함.

    sed 절단 기전: sed 's/".*//' 는 JSON payload 안 첫 큰따옴표에서 절단.
    예: `gh pr edit 94 --body "this is \"escaped\""`
        첫 sed (command 추출): `gh pr edit 94 --body "this is \"escaped\""`
        두 번째 sed (따옴표 절단): `gh pr edit 94 --body ` (첫 `"` 다음 전부 절단)

    위음성 우회형: 큰따옴표 절단으로 gh write verb 가 누락되는 사례.

    현행 거동: escape 시 sed 절단 → command 불완전 → grep 매칭 실패(또는 성공).
    실제 재검증: `gh pr edit 94 --body "this is \"escaped\""` → rc=2 (매칭됨).

    본 테스트는 현행 거동 그대로 pin: exit 2 (절단 회피 — 여전히 차단됨).
    """
    rc, _ = _run_hook(_payload('gh pr edit 94 --body "this is \\"escaped\\""'))
    # 현행: exit 2 (sed 절단에도 불구하고 gh pr edit 매칭 성공 — 현행 동작)
    assert rc == 2, "Escaped quotes do not prevent grep match in this form"


def test_bypass_env_allows_write_verb():
    """BYPASS_CROSS_REPO_GH_SAFETY=1 설정 시 차단 우회 → exit 0."""
    rc, stderr = _run_hook(
        _payload("gh pr edit 94"),
        env_overrides={"BYPASS_CROSS_REPO_GH_SAFETY": "1"}
    )
    assert rc == 0
    assert "BYPASS_CROSS_REPO_GH_SAFETY=1" in stderr
