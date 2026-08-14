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

import io
import json
import os
import stat
import subprocess
import sys
from collections import namedtuple
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
        # encoding 명시 (Windows 기본 cp949 디코딩 → UnicodeDecodeError 스레드 예외 회피).
        # errors="replace": gh 부재 case 에서 **OS 로케일(cp949) 에러 메시지**가 stderr 로
        # 새어 들어와 UTF-8 로 디코딩 불가한 바이트가 섞인다 — 본 test 는 exit code 와
        # ASCII marker 만 판정하므로 치환 디코딩으로 충분(디코딩 예외로 죽지 않게).
        text=True, encoding="utf-8", errors="replace",
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


# ============================================================ gh 총예산 거동 (CFP-2965 F4 / P1-4)
#
# 검증 축 2 (실물 = git-branch-delete-merge-gate.py 의 GH_TOTAL_BUDGET_SEC 배선):
#   (a) 총예산 소진 → 잔여 branch 검사 skip + 진단 stderr + rc 0 (fail-open)
#         — "죽어서 통과"(hooks.json timeout kill, 흔적 0) 대신 "돌아서 통과"(흔적 有).
#   (b) 경계 직전 발사되는 call 의 in-flight deadline == min(_GH_TIMEOUT_SEC, 잔여)
#         — 누적 사전검사만으로는 경계 직전 call 이 (49.9 + 10) 로 총예산을 관통한다.
#
# 네트워크 0 · 실 gh 프로세스 기동 0: seam 은 프로세스 경계 **바로 안쪽**(subprocess.run)
#   1곳뿐이고, 그 위의 `_open_prs_for_branch` / `main()` / 파서는 전부 실물이다.
#   전역 모듈(time / subprocess) 은 건드리지 않는다 — gate 모듈이 들고 있는 **참조만**
#   교체하므로 pytest 내부·타 테스트로 누수되지 않는다.
#
# ADR-171 mock-seam 동반 assertion (seam 을 깔았으면 "실제로 물렸다"를 증명할 것):
#   모든 케이스가 (1) seam 호출 기록 비어있지 않음 (2) 기록된 argv 가 실 gh 조회 형태
#   (`gh pr list --head <b> --state open --json number,title`, shell=False) 와 일치함을
#   assert 한다. seam 이 안 물리면 기록이 비어 **FAIL** 한다 (조용한 거짓 PASS 불가).
#
# 판별력 실증 (mutation kill, 2026-08-14 firsthand):
#   M1 `call_timeout = min(_GH_TIMEOUT_SEC, budget_remaining_sec)` → `= _GH_TIMEOUT_SEC`
#      ⇒ test_per_call_deadline_clamped_to_remaining_budget FAIL (5.0 기대 vs 10).
#   M2 `if remaining <= 0:` → `if False:` (소진 분기 무력화)
#      ⇒ test_gh_total_budget_exhaustion_skips_rest_and_fails_open FAIL (b3 까지 조회).
#   둘 다 원복 확인.

_Call = namedtuple("_Call", "argv timeout shell at")


class _FakeClock:
    """monotonic 대체 — 명시 advance 로만 흐른다 (벽시계·부하 비의존 = 결정적)."""

    def __init__(self, start: float = 1000.0):
        self.start = float(start)
        self.now = float(start)

    def __call__(self) -> float:
        return self.now

    def advance(self, sec: float) -> None:
        self.now += float(sec)


class _ModuleShim:
    """gate 가 들고 있는 모듈 참조만 갈아끼우는 최소 shim (전역 모듈 무접촉)."""

    def __init__(self, **attrs):
        self.__dict__.update(attrs)


class _GhSeam:
    """subprocess.run seam — gh argv 를 가로채 canned 응답 + 소요시간 시뮬레이션."""

    def __init__(self, clock: _FakeClock, elapsed_per_call: float, stdout: str = "[]"):
        self.clock = clock
        self.elapsed_per_call = float(elapsed_per_call)
        self.stdout = stdout
        self.calls: list[_Call] = []

    def __call__(self, argv, **kwargs):
        self.calls.append(
            _Call(list(argv), kwargs.get("timeout"), kwargs.get("shell"), self.clock.now)
        )
        self.clock.advance(self.elapsed_per_call)
        return subprocess.CompletedProcess(argv, 0, self.stdout, "")


def _install_gh_seam(monkeypatch, command: str, elapsed_per_call: float, stdout: str = "[]"):
    """gate 의 time/subprocess 참조 + stdin 을 교체하고 seam 반환."""
    clock = _FakeClock()
    seam = _GhSeam(clock, elapsed_per_call, stdout)
    monkeypatch.setattr(gate, "time", _ModuleShim(monotonic=clock))
    monkeypatch.setattr(gate, "subprocess", _ModuleShim(run=seam))
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    return seam


def _assert_seam_engaged(seam: _GhSeam) -> None:
    """ADR-171 동반 assertion — seam 이 실제로 물렸고, 실 gh 조회 형태인가."""
    assert seam.calls, (
        "gh seam 미사용 — subprocess.run 이 가로채지지 않았다. "
        "관측 대상이 실물 gh 경로가 아니므로 이 테스트의 통과는 무효다."
    )
    for c in seam.calls:
        assert c.argv[:3] == ["gh", "pr", "list"], f"gh 조회 argv 아님: {c.argv}"
        assert "--head" in c.argv, f"--head 부재: {c.argv}"
        assert c.argv[c.argv.index("--state") + 1] == "open", f"열린 PR 조회 아님: {c.argv}"
        assert c.argv[c.argv.index("--json") + 1] == "number,title", f"json 필드 불일치: {c.argv}"
        assert c.shell is False, f"shell=False 아님: {c.shell}"


def _heads(seam: _GhSeam) -> list[str]:
    """seam 기록에서 실제 조회된 branch 이름 순서 추출."""
    return [c.argv[c.argv.index("--head") + 1] for c in seam.calls]


def test_gh_total_budget_exhaustion_skips_rest_and_fails_open(monkeypatch, capsys):
    """(a) 총예산 소진 → 잔여 branch 미검사 + 진단 1줄 + rc 0.

    branch 3건 × call 당 30s → b1(0→30) b2(30→60) 검사 후 잔여 -10s → b3 skip.
    """
    seam = _install_gh_seam(
        monkeypatch, "git push origin --delete b1 b2 b3", elapsed_per_call=30.0
    )

    rc = gate.main()
    err = capsys.readouterr().err

    _assert_seam_engaged(seam)
    assert rc == 0, f"예산 소진은 fail-open(0) 이어야 함 (got {rc})"
    assert _heads(seam) == ["b1", "b2"], (
        f"예산 소진 이후 branch 가 계속 조회됐다: {_heads(seam)}"
    )
    assert f"총예산 {gate.GH_TOTAL_BUDGET_SEC}s 소진" in err, f"소진 진단 부재: {err!r}"
    assert "잔여 branch 1건 미검사" in err, f"미검사 건수 진단 부재: {err!r}"
    assert "fail-open" in err, f"fail-open 표기 부재: {err!r}"


def test_gh_budget_exhaustion_does_not_swallow_earlier_block(monkeypatch, capsys):
    """(a-대조군): 예산이 남아 있는 동안 열린 PR 을 만나면 여전히 exit 2.

    소진 경로(rc 0)가 차단 경로를 삼키지 않음을 고정한다 — 이게 없으면 (a) 는
    "언제나 0" 과 구별되지 않는다.
    """
    seam = _install_gh_seam(
        monkeypatch,
        "git push origin --delete b1 b2 b3",
        elapsed_per_call=30.0,
        stdout=json.dumps([{"number": 42, "title": "WIP"}]),
    )

    rc = gate.main()
    err = capsys.readouterr().err

    _assert_seam_engaged(seam)
    assert rc == 2, f"열린 PR 확인 = 유일 차단 경로 (got {rc})"
    assert _heads(seam) == ["b1"], f"첫 차단 후 조회가 계속됐다: {_heads(seam)}"
    assert "BLOCKED" in err and "#42" in err


def test_per_call_deadline_clamped_to_remaining_budget(monkeypatch, capsys):
    """(b) 각 call 의 in-flight deadline == min(_GH_TIMEOUT_SEC, 발사시점 잔여).

    b1 이 45s 소비 → b2 발사 시점 잔여 5s < _GH_TIMEOUT_SEC(10) → b2 deadline = 5.
    clamp 가 없으면 b2 는 10s 를 받아 최악 wall 55s 로 총예산 50s 를 관통한다.
    """
    seam = _install_gh_seam(
        monkeypatch, "git push origin --delete b1 b2", elapsed_per_call=45.0
    )

    rc = gate.main()
    capsys.readouterr()

    _assert_seam_engaged(seam)
    assert rc == 0
    assert _heads(seam) == ["b1", "b2"], f"두 branch 모두 조회돼야 함: {_heads(seam)}"

    timeouts = [c.timeout for c in seam.calls]
    assert timeouts[0] == gate._GH_TIMEOUT_SEC, (
        f"잔여 충분(50s) 시 per-call 상한 = _GH_TIMEOUT_SEC 여야 함: {timeouts[0]}"
    )
    assert timeouts[1] == pytest.approx(5.0), (
        f"경계 직전 call 은 잔여(5s)로 조여져야 함 (clamp 부재 시 10): {timeouts[1]}"
    )

    # 총예산 미관통 invariant: 발사시점 경과 + 그 call 의 deadline ≤ 총예산.
    for c in seam.calls:
        elapsed = c.at - seam.clock.start
        remaining = gate.GH_TOTAL_BUDGET_SEC - elapsed
        assert c.timeout == pytest.approx(min(gate._GH_TIMEOUT_SEC, remaining)), (
            f"deadline != min(_GH_TIMEOUT_SEC, 잔여): timeout={c.timeout}, 잔여={remaining}"
        )
        assert elapsed + c.timeout <= gate.GH_TOTAL_BUDGET_SEC + 1e-9, (
            f"최악 wall 이 총예산 관통: 경과={elapsed} + deadline={c.timeout} "
            f"> {gate.GH_TOTAL_BUDGET_SEC}"
        )


def test_open_prs_default_budget_is_per_call_timeout(monkeypatch):
    """단독 호출(budget 인자 생략) = 기존 거동 그대로 (_GH_TIMEOUT_SEC).

    docstring 이 선언한 default 를 실측으로 고정 — 기본값이 바뀌면 여기서 깨진다.
    """
    clock = _FakeClock()
    seam = _GhSeam(clock, elapsed_per_call=0.0)
    monkeypatch.setattr(gate, "subprocess", _ModuleShim(run=seam))

    assert gate._open_prs_for_branch("foo") == []

    _assert_seam_engaged(seam)
    assert seam.calls[0].timeout == gate._GH_TIMEOUT_SEC
    assert _heads(seam) == ["foo"]
