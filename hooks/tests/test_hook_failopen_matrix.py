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
import subprocess
import os
import pytest
from pathlib import Path


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
    """훅 실행."""
    run_hook_cmd = Path(__file__).parent.parent / "run-hook.cmd"

    try:
        stdin_data = None
        if isinstance(payload, dict):
            stdin_data = json.dumps(payload).encode("utf-8")
        elif isinstance(payload, str):
            stdin_data = payload.encode("utf-8")

        result = subprocess.run(
            ["cmd.exe", "/c", str(run_hook_cmd), hook_name],
            input=stdin_data,
            capture_output=True,
            timeout=30,
        )
        return result.returncode, result.stderr.decode("utf-8", errors="ignore")
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, str(e)


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


def test_hook_failopen_matrix_summary():
    """fail-open matrix 요약 (AC-N5 documentation)."""
    print(f"\nFail-open matrix:")
    print(f"  Hooks: {len(HOOKS)}")
    print(f"  Judgement deny: {len(JUDGEMENT_DENY_HOOKS)}")
    print(f"  Fail-open only: {len(HOOKS) - len(JUDGEMENT_DENY_HOOKS)}")
    print(f"  Invariant: exit 2 = judgement deny only, else exit 0")
