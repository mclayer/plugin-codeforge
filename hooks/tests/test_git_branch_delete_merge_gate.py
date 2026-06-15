"""test_git_branch_delete_merge_gate.py — CFP-2282 계약 검증.

미머지 PR branch 삭제 하드차단 PreToolUse hook 의 단위(파서) + 통합(subprocess) 테스트.

CI: lint.yml hook-unit-tests job (ubuntu-latest) 에서 실행. fake `gh` 스텁을
    PATH 앞에 둬 gh 조회를 결정적으로 모킹한다 (POSIX sh 스텁 — ubuntu 충분).

불변식:
  - 모든 경로 exit 0 (fail-open) except "열린 PR 확인" (그 때만 exit 2 block).
  - 비-Bash / 비-delete / 삭제대상 없음 / gh 오류·부재 / BYPASS = 전부 exit 0.
  - tag 삭제(`--delete tag` / `:refs/tags/...`) = scope 외 (fail-open 통과).
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

import git_branch_delete_merge_gate as gate


HOOK_PY = (
    Path(__file__).resolve().parent.parent / "git-branch-delete-merge-gate.py"
)


# ============================================================ _parse_delete_branches (단위)


@pytest.mark.parametrize(
    "command,expected",
    [
        # 비-delete
        ("git status", []),
        ("git push origin main", []),
        ("git push", []),
        ("ls -la", []),
        ("git branch -d foo", []),  # local branch 삭제 — remote push 아님
        # --delete / -d
        ("git push origin --delete foo", ["foo"]),
        ("git push origin -d foo", ["foo"]),
        ("git push origin --delete foo bar", ["foo", "bar"]),
        ("git push --force origin --delete foo", ["foo"]),
        ("git push origin --delete refs/heads/foo", ["foo"]),  # prefix 제거
        # colon refspec deletion
        ("git push origin :foo", ["foo"]),
        ("git push origin :refs/heads/foo", ["foo"]),
        ("git push origin src:dst", []),  # src 비지 않음 → 삭제 아님
        # tag 삭제 — scope 외 (fail-open)
        ("git push origin --delete tag v1.0", []),
        ("git push origin :refs/tags/v1.0", []),
        # env prefix / 경로형 git
        ("GIT_SSH=x git push origin --delete foo", ["foo"]),
        ("/usr/bin/git push origin --delete foo", ["foo"]),
        # 중복 제거
        ("git push origin --delete foo foo", ["foo"]),
    ],
)
def test_parse_delete_branches(command, expected):
    assert gate._parse_delete_branches(command) == expected


def test_parse_delete_branches_shlex_failure_fail_open():
    """shlex 파싱 실패(미닫힌 quote) → [] (fail-open)."""
    assert gate._parse_delete_branches('git push origin --delete "unterminated') == []


# ============================================================ _extract_command (단위)


def test_extract_command_non_bash():
    assert gate._extract_command({"tool_name": "Edit", "tool_input": {}}) == ""


def test_extract_command_bash_ok():
    payload = {"tool_name": "Bash", "tool_input": {"command": "git status"}}
    assert gate._extract_command(payload) == "git status"


def test_extract_command_missing_input():
    assert gate._extract_command({"tool_name": "Bash"}) == ""


# ============================================================ fake gh 스텁 + subprocess 통합

# Windows Python 의 subprocess(['gh',...], shell=False) 는 extensionless POSIX sh
# 스텁의 shebang 을 해석하지 못하고(.cmd 도 PATHEXT 비해석), gh 가 silent 빈 stdout
# 으로 떨어져 fail-open(exit 0) 로 수렴 → 거짓 PASS 위험. lint.yml hook-unit-tests 는
# ubuntu-latest 라 shebang 정상 동작. fail-open 진위 보장을 위해 stub 의존 테스트는
# POSIX 한정으로 명시 skip (parser 단위 + 비-stub 경로는 전 플랫폼 유지).
_requires_posix_gh_stub = pytest.mark.skipif(
    os.name == "nt",
    reason="gh sh-stub 은 POSIX shebang 의존 — Windows subprocess 미해석 (CI=ubuntu 에서 실행)",
)


def _write_gh_stub(tmp_path: Path, stdout: str, exitcode: int = 0) -> Path:
    """임시 dir 에 fake `gh` POSIX sh 실행스크립트 작성 후 dir 경로 반환.

    인자 무관하게 정해진 stdout 방출 + 지정 exit code. ubuntu CI 에서 실행.
    """
    bindir = tmp_path / "fakebin"
    bindir.mkdir()
    gh = bindir / "gh"
    gh.write_text(
        "#!/bin/sh\n"
        f"cat <<'GHEOF'\n{stdout}\nGHEOF\n"
        f"exit {exitcode}\n"
    )
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return bindir


def _run_hook(command: str | None, env_extra: dict, tool_name: str = "Bash"):
    """git-branch-delete-merge-gate.py 를 subprocess 로 실행 → (returncode, stderr)."""
    if command is None:
        payload = {"tool_name": tool_name, "tool_input": {}}
    else:
        payload = {"tool_name": tool_name, "tool_input": {"command": command}}
    env = dict(os.environ)
    env.update(env_extra)
    result = subprocess.run(
        [sys.executable, str(HOOK_PY)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stderr


def _path_with(bindir: Path) -> dict:
    """fake bindir 를 PATH 앞에 둔 env dict."""
    return {"PATH": f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}"}


# --- TC1: 비-Bash tool → exit 0
def test_tc1_non_bash_exit_zero(tmp_path):
    rc, _ = _run_hook("git push origin --delete foo", {}, tool_name="Edit")
    assert rc == 0


# --- TC2: 비-delete 명령 → exit 0
@pytest.mark.parametrize("cmd", ["git status", "git push origin main"])
def test_tc2_non_delete_exit_zero(cmd):
    rc, _ = _run_hook(cmd, {})
    assert rc == 0


# --- TC3: --delete + gh 가 열린 PR 반환 → exit 2
@_requires_posix_gh_stub
def test_tc3_delete_with_open_pr_blocks(tmp_path):
    bindir = _write_gh_stub(
        tmp_path, json.dumps([{"number": 42, "title": "WIP feature"}])
    )
    rc, stderr = _run_hook("git push origin --delete foo", _path_with(bindir))
    assert rc == 2
    assert "BLOCKED" in stderr
    assert "#42" in stderr
    assert "BYPASS_BRANCH_DELETE_MERGE_GATE=1" in stderr


# --- TC4: --delete + gh 가 빈 배열 → exit 0
@_requires_posix_gh_stub
def test_tc4_delete_no_open_pr_passes(tmp_path):
    bindir = _write_gh_stub(tmp_path, "[]")
    rc, _ = _run_hook("git push origin --delete foo", _path_with(bindir))
    assert rc == 0


# --- TC5: colon refspec + 열린 PR → exit 2
@_requires_posix_gh_stub
def test_tc5_colon_refspec_with_open_pr_blocks(tmp_path):
    bindir = _write_gh_stub(
        tmp_path, json.dumps([{"number": 7, "title": "colon branch"}])
    )
    rc, stderr = _run_hook("git push origin :foo", _path_with(bindir))
    assert rc == 2
    assert "#7" in stderr


# --- TC6: BYPASS=1 → exit 0 (gh 호출 안 해도 통과)
def test_tc6_bypass_exit_zero(tmp_path):
    # gh 스텁이 열린 PR 을 반환하더라도 bypass 면 exit 0.
    bindir = _write_gh_stub(
        tmp_path, json.dumps([{"number": 99, "title": "should be bypassed"}])
    )
    env = _path_with(bindir)
    env["BYPASS_BRANCH_DELETE_MERGE_GATE"] = "1"
    rc, stderr = _run_hook("git push origin --delete foo", env)
    assert rc == 0
    assert "BYPASS" in stderr


# --- TC7a: gh 가 비정상 종료(exit 1) → exit 0 (fail-open)
@_requires_posix_gh_stub
def test_tc7a_gh_nonzero_fail_open(tmp_path):
    bindir = _write_gh_stub(tmp_path, "error: not authenticated", exitcode=1)
    rc, _ = _run_hook("git push origin --delete foo", _path_with(bindir))
    assert rc == 0


# --- TC7b: gh 부재(PATH 에 gh 없음) → exit 0 (fail-open)
def test_tc7b_gh_absent_fail_open(tmp_path):
    # gh 가 절대 없는 격리 PATH (빈 dir 만)
    emptydir = tmp_path / "emptybin"
    emptydir.mkdir()
    rc, _ = _run_hook("git push origin --delete foo", {"PATH": str(emptydir)})
    assert rc == 0


# --- TC7c: gh 가 깨진 JSON → exit 0 (fail-open)
@_requires_posix_gh_stub
def test_tc7c_gh_bad_json_fail_open(tmp_path):
    bindir = _write_gh_stub(tmp_path, "{not valid json")
    rc, _ = _run_hook("git push origin --delete foo", _path_with(bindir))
    assert rc == 0


# --- TC8: tag 삭제 → exit 0 (gh 호출 없이 통과, scope 외)
def test_tc8_tag_delete_scope_out(tmp_path):
    # gh 스텁이 열린 PR 반환해도 tag 삭제는 파서가 [] 라 gh 호출 자체 없음.
    bindir = _write_gh_stub(
        tmp_path, json.dumps([{"number": 1, "title": "x"}])
    )
    rc, _ = _run_hook("git push origin --delete tag v1.0", _path_with(bindir))
    assert rc == 0


# --- TC9: 미머지 PR 메시지에 incident #2280 박제 포함
@_requires_posix_gh_stub
def test_tc9_block_message_carries_incident(tmp_path):
    bindir = _write_gh_stub(
        tmp_path, json.dumps([{"number": 5, "title": "t"}])
    )
    rc, stderr = _run_hook("git push origin --delete foo", _path_with(bindir))
    assert rc == 2
    assert "#2280" in stderr
    assert "mergedAt" in stderr


# ============================================================ INV


def test_inv_non_block_paths_exit_zero():
    """INV (전 플랫폼): 비-삭제 / tag 삭제 = gh 미호출 경로 → 전부 exit 0."""
    cases = [
        "git status",
        "git push origin main",
        "git push origin --delete tag v1",  # tag — 파서 [] (gh 미호출)
        "git branch -D foo",  # local 삭제 — scope 외
    ]
    for cmd in cases:
        rc, _ = _run_hook(cmd, {})
        assert rc == 0, f"'{cmd}' 는 exit 0 이어야 함 (got {rc})"


@_requires_posix_gh_stub
def test_inv_delete_no_open_pr_exit_zero(tmp_path):
    """INV (POSIX): 삭제 대상이지만 열린 PR 없음 → exit 0 (유일 차단경로 = 열린 PR)."""
    empty = _write_gh_stub(tmp_path, "[]")
    rc, _ = _run_hook("git push origin --delete foo", _path_with(empty))
    assert rc == 0
