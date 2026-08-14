#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AC-13 argv 경로형태 3-arm: 슬래시·백슬래시·bare filename 동일성.

목적:
  훅 스크립트를 가리키는 argv 경로가 3가지 형태로 표현되어도 훅의 관측 결과가
  동일함을 검증한다 (경로 형태를 전제한 코드가 훅에 스며드는 것을 차단).

정의역:
  대상 훅 = worktree-location-guard (deny 판정이 결정적이라 arm 간 대조가 선명하다)
  3-arm path form:
    (1) forward-slash 절대경로  — POSIX 정규형
    (2) backslash 절대경로      — Windows native (Windows 전용 arm, 아래 사유)
    (3) bare filename + cwd     — 경로 성분 없는 형태
  판정 triple = (rc, stdout, stderr 유무)

discriminating:
  "모두 같다"만 보면 모든 arm 이 똑같이 고장 나도 통과한다. 그래서
  (a) 각 arm 이 **기대 관측**(deny rc=2 + 게이트 식별자 stderr)에 도달했는지 개별 확인하고
  (b) 다른 훅을 같은 payload 로 실행하면 triple 이 **달라지는지**(rc=0) 확인해
  동일성 assert 가 항진이 아님을 실증한다.

이력: 구 버전은 세 arm 의 몸통이 전부 `pass` 였고, 동일성 테스트는 서로 다른 문자열
  리터럴 3개에 `len(set(...)) == 3` 을 걸어 항상 참이었다 (실행 0 · 관측 0).
  또한 docstring 이 AC-5/6 로 잘못 귀속돼 있었다 — 본 파일의 축은 AC-13 이다.
"""

from __future__ import annotations

import json
import os
import subprocess

import pytest

from hook_runner_cfp2965 import BASH, HOOKS_DIR, requires_bash

pytestmark = requires_bash

HOOK_NAME = "worktree-location-guard"
GATE_MARKER = "check_worktree_location_guard"

# 표준 밖 worktree 생성 = deny 경로 (TIER=block 동반).
DENY_PAYLOAD = {
    "tool_name": "Bash",
    "tool_input": {"command": "git worktree add /tmp/test-wd"},
}


def _deny_env() -> dict:
    env = os.environ.copy()
    env["WORKTREE_LOCATION_GUARD_TIER"] = "block"
    return env


def _run_form(script_arg: str, cwd: str | None = None) -> tuple[int, str, bool]:
    """argv 경로형태 1종으로 훅 실행 → (rc, stdout, stderr 유무).

    conftest.run_hook_bash 는 훅 이름만 받으므로(경로형태 고정), 본 축은 경로형태
    자체가 검증 대상이라 여기서만 직접 argv 를 구성한다.
    """
    proc = subprocess.run(
        [BASH, script_arg],
        input=json.dumps(DENY_PAYLOAD).encode("utf-8"),
        capture_output=True,
        env=_deny_env(),
        cwd=cwd,
        timeout=60,
    )
    return (
        proc.returncode,
        proc.stdout.decode("utf-8", errors="replace"),
        bool(proc.stderr.decode("utf-8", errors="replace").strip()),
    )


def _forward_slash_arg() -> str:
    return str(HOOKS_DIR / HOOK_NAME).replace("\\", "/")


def _backslash_arg() -> str:
    return str(HOOKS_DIR / HOOK_NAME).replace("/", "\\")


def _assert_deny_observation(rc: int, stdout: str, has_stderr: bool, form: str) -> None:
    """각 arm 이 기대 관측(deny)에 도달했는지 — 동일성 이전의 전제."""
    assert rc == 2, f"{form}: deny payload 인데 rc={rc} (기대 2)"
    assert stdout == "", f"{form}: stdout 은 비어야 함 (실측 {stdout[:80]!r})"
    assert has_stderr, f"{form}: deny 진단 stderr 부재"


def test_argv_path_form_forward_slash():
    """3-arm (1): forward-slash 절대경로 — POSIX 정규형."""
    rc, out, err = _run_form(_forward_slash_arg())
    _assert_deny_observation(rc, out, err, "forward-slash")


@pytest.mark.skipif(
    os.name != "nt",
    reason="backslash 경로형태는 Windows 고유 — POSIX 에서 백슬래시는 경로 구분자가 "
           "아니라 파일명 문자라 같은 파일을 가리키지 않는다 (형태 자체가 부재)",
)
def test_argv_path_form_backslash():
    """3-arm (2): backslash 절대경로 — Windows native."""
    rc, out, err = _run_form(_backslash_arg())
    _assert_deny_observation(rc, out, err, "backslash")


def test_argv_path_form_bare_filename():
    """3-arm (3): 경로 성분 없는 bare filename (cwd = hooks/)."""
    rc, out, err = _run_form(HOOK_NAME, cwd=str(HOOKS_DIR))
    _assert_deny_observation(rc, out, err, "bare")


def test_argv_path_form_discriminating():
    """3-arm 동일성 + 항진 아님 실증.

    (a) 가용한 모든 arm 의 triple 이 서로 완전히 같아야 한다.
    (b) 같은 payload 를 **다른 훅**에 주면 triple 이 달라져야 한다 — 이게 성립해야
        (a) 의 동일성이 "무엇이든 같다"는 항진이 아님이 증명된다.
    """
    observed = {
        "forward-slash": _run_form(_forward_slash_arg()),
        "bare": _run_form(HOOK_NAME, cwd=str(HOOKS_DIR)),
    }
    if os.name == "nt":
        observed["backslash"] = _run_form(_backslash_arg())

    triples = set(observed.values())
    assert len(triples) == 1, (
        "argv 경로형태에 따라 훅 관측이 갈렸다 (경로형태 중립성 위반):\n"
        + "\n".join(f"  {form}: {t}" for form, t in observed.items())
    )

    # 전제: 그 하나의 triple 이 실제 deny 관측이어야 한다 (모두 같이 고장난 경우 배제).
    only = triples.pop()
    _assert_deny_observation(*only, form="all-forms")

    # (b) discriminating — 다른 훅은 달라야 한다.
    other = subprocess.run(
        [BASH, str(HOOKS_DIR / "cross-repo-gh-safety")],
        input=json.dumps(DENY_PAYLOAD).encode("utf-8"),
        capture_output=True,
        env=_deny_env(),
        timeout=60,
    )
    other_triple = (
        other.returncode,
        other.stdout.decode("utf-8", errors="replace"),
        bool(other.stderr.decode("utf-8", errors="replace").strip()),
    )
    assert other_triple != only, (
        "다른 훅인데 triple 이 같다 — 동일성 assert 가 무엇이든 통과시키는 항진일 수 있다 "
        f"(both {only})"
    )


def test_argv_path_form_gate_identity_in_stderr():
    """모든 arm 의 stderr 가 **같은 게이트**에서 나왔는지 (형태별 다른 훅 실행 방지).

    triple 은 stderr 유무만 보므로, 형태가 우연히 다른 스크립트를 물어도 rc 만 같으면
    통과할 수 있다. 게이트 식별자로 실행 주체를 고정한다.
    """
    args: list[tuple[str, str, str | None]] = [
        ("forward-slash", _forward_slash_arg(), None),
        ("bare", HOOK_NAME, str(HOOKS_DIR)),
    ]
    if os.name == "nt":
        args.append(("backslash", _backslash_arg(), None))

    for form, script_arg, cwd in args:
        proc = subprocess.run(
            [BASH, script_arg],
            input=json.dumps(DENY_PAYLOAD).encode("utf-8"),
            capture_output=True,
            env=_deny_env(),
            cwd=cwd,
            timeout=60,
        )
        stderr = proc.stderr.decode("utf-8", errors="replace")
        assert GATE_MARKER in stderr, (
            f"{form}: stderr 에 게이트 식별자({GATE_MARKER}) 부재 — 다른 스크립트가 "
            f"실행됐을 수 있다\n  stderr: {stderr[:200]!r}"
        )
