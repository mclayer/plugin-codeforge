#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 (테스트): Hook fail-open matrix (장애 주입).

목적:
  7훅 × 장애 주입 축 검증
  조건: exit 2 는 판정 deny 경로만, 장애는 전부 exit 0 (fail-open)

정의역 (Change Plan §8.2):
  7훅:
    1-5. PreToolUse Bash: cross-repo-gh-safety / repo-confinement / git-branch-delete
         worktree-location-guard / pretooluse-bash-description-inject
    6. pretooluse-dev-process-capture (복합 matcher)
    7. posttooluse-dev-process-capture

  장애 주입 (실현 가능한 축):
    - python 부재 (PATH mocking — S7 반영: python3 존재 + python 없음 = 정상)
    - 깨진 JSON payload
    - 빈 payload
    - 비-Bash tool_name
    - lib 부재 (subprocess 오류)
    - 권한류 (실현 복잡, 생략)

테스트:
  - 각 훅마다 N-1 장애 주입
  - exit 2는 판정 deny 경로만 (cross-repo-gh-safety, repo-confinement, git-branch-delete, worktree-location-guard)
  - 나머지 (lib 부재, JSON 오류 등): exit 0 (fail-open)
"""

from __future__ import annotations

import json
import pytest

from hook_runner_cfp2965 import (
    HOOKS_DIR,
    parametrize_argvalues,
    requires_bash,
    run_hook_bash,
)

# 훅 실행은 bash 직접 호출로 통일 (구 `cmd.exe /c run-hook.cmd` 하드코딩은 Linux CI 에서
# FileNotFoundError → 전건 FAIL). fail-open 판정 축은 OS 무관 — hook_runner_cfp2965 SSOT.
pytestmark = requires_bash


# 7훅 목록
HOOKS = [
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
    "pretooluse-bash-description-inject",
    "pretooluse-dev-process-capture",
    "posttooluse-dev-process-capture",
]

# 판정 deny 경로 (exit 2 정상)
JUDGEMENT_DENY_HOOKS = {
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
}


def _run_hook(hook_name: str, payload: dict | str | None) -> tuple[int, str]:
    """훅 실행 → (rc, stderr)."""
    stdin_data = None
    if isinstance(payload, dict):
        stdin_data = json.dumps(payload).encode("utf-8")
    elif isinstance(payload, str):
        stdin_data = payload.encode("utf-8")

    rc, _stdout, stderr = run_hook_bash(hook_name, stdin_data)
    return rc, stderr


@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_failopen_broken_json(hook_name: str):
    """장애: 깨진 JSON → fail-open (exit 0)."""
    payload = "{invalid json"

    rc, stderr = _run_hook(hook_name, payload)

    # JSON 파싱 실패는 fail-open
    assert rc == 0, (
        f"Hook {hook_name} with broken JSON should exit 0 (fail-open), got {rc}\n"
        f"stderr: {stderr}"
    )


@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_failopen_empty_payload(hook_name: str):
    """장애: 빈 payload → fail-open (exit 0)."""
    payload = ""

    rc, stderr = _run_hook(hook_name, payload)

    # 빈 payload는 fail-open
    assert rc == 0, (
        f"Hook {hook_name} with empty payload should exit 0 (fail-open), got {rc}\n"
        f"stderr: {stderr}"
    )


@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_failopen_non_bash_tool(hook_name: str):
    """장애: 비-Bash tool_name → fail-open (exit 0)."""
    payload = {
        "tool_name": "Write",  # 비-Bash
        "tool_input": {
            "command": "echo test"
        }
    }

    rc, stderr = _run_hook(hook_name, payload)

    # tool mismatch는 fail-open (미매칭)
    assert rc == 0, (
        f"Hook {hook_name} with non-Bash tool should exit 0 (fail-open), got {rc}\n"
        f"stderr: {stderr}"
    )


def test_hook_failopen_matrix_completeness():
    """fail-open matrix 정의역 completeness — 구 print-only 요약의 구조 assert 승격.

    구 `test_hook_failopen_matrix_summary` 는 print 5줄뿐이라 정의역이 어떻게 줄어들든
    통과했다 (판별력 0 — 게이트가 아니라 주석). 정의역이 **조용히 축소**되는 것을 막는
    구조 assert 로 승격한다. 판정 소스 = parametrize 데코레이터 **실물**
    (test_bypass_env_disjoint 의 16-cell coverage assert 동형).
    """
    # (1) 훅 정의역 = 7 (Change Plan §8.2), 중복 0
    assert len(HOOKS) == 7, f"7훅 기대, 실제 {len(HOOKS)}"
    assert len(set(HOOKS)) == len(HOOKS), f"HOOKS 에 중복 존재: {HOOKS}"

    # (2) 판정 deny 훅 4종 ⊆ HOOKS (matrix 밖 훅을 deny 로 분류하지 않음)
    assert JUDGEMENT_DENY_HOOKS <= set(HOOKS), (
        f"HOOKS 에 없는 deny 훅: {sorted(JUDGEMENT_DENY_HOOKS - set(HOOKS))}"
    )
    assert len(JUDGEMENT_DENY_HOOKS) == 4, (
        f"판정 deny 4종 기대, 실제 {len(JUDGEMENT_DENY_HOOKS)}"
    )

    # (3) 훅 목록이 실물 파일과 결속 (오타·삭제된 훅이 조용히 남지 않게)
    for hook_name in HOOKS:
        assert (HOOKS_DIR / hook_name).exists(), (
            f"HOOKS 에 있으나 실물 부재: hooks/{hook_name}"
        )

    # (4) 장애 주입 3축 **전부**가 HOOKS 전건을 parametrize 하는가 (실 데코레이터 판독)
    injection_axes = (
        test_hook_failopen_broken_json,
        test_hook_failopen_empty_payload,
        test_hook_failopen_non_bash_tool,
    )
    for fn in injection_axes:
        argvalues = parametrize_argvalues(fn, "hook_name")
        assert list(argvalues) == HOOKS, (
            f"{fn.__name__} 의 정의역이 HOOKS 와 불일치 — cell 축소.\n"
            f"  parametrize: {list(argvalues)}\n  HOOKS: {HOOKS}"
        )

    # (5) 총 cell = 7훅 × 장애 3축 = 21
    assert len(injection_axes) * len(HOOKS) == 21, "fail-open matrix cell 수 변동"
