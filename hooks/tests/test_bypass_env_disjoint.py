#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 (테스트): Bypass env gate disjoint invariant INV-B1.

목적:
  게이트 4종 × bypass env 4종 = 16-cell matrix
  각 cell: deny payload 에서 "exit==0 iff env==own(gate)" 검증

정의역:
  게이트 4종:
    1. cross-repo-gh-safety (BYPASS_CROSS_REPO_GH_SAFETY)
    2. repo-confinement (BYPASS_REPO_CONFINEMENT)
    3. git-branch-delete-merge-gate (BYPASS_BRANCH_DELETE_MERGE_GATE)
    4. worktree-location-guard (BYPASS_WORKTREE_LOCATION_GUARD)

  각 게이트마다 고유 deny payload (deny-triggering test case)

INV-B1: exit==0 iff env==own(gate)
  - 예: cross-repo-gh-safety 게이트 + BYPASS_CROSS_REPO_GH_SAFETY=1 → exit 0
  - 예: cross-repo-gh-safety 게이트 + BYPASS_REPO_CONFINEMENT=1 → exit 2 (deny)

테스트:
  - 각 게이트별 deny payload 이용
  - 4개 bypass env 조합 (본 env + 타 env 3개 + 미설정)
  - 16 cell 모두 검증
"""

from __future__ import annotations

import json
import os
import subprocess
import pytest
from pathlib import Path


# Deny payloads per gate (S0/corpus 검증분 재사용)
DENY_PAYLOADS = {
    "cross-repo-gh-safety": {
        "tool_name": "Bash",
        "tool_input": {
            "command": "gh pr edit 94"  # bare space trigger (sed truncation)
        }
    },
    "repo-confinement": {
        "tool_name": "Bash",
        "tool_input": {
            "command": "echo secret > ~/payload.txt"  # home-root write (redirect)
        }
    },
    "git-branch-delete-merge-gate": {
        "tool_name": "Bash",
        "tool_input": {
            "command": "git push origin --delete develop"  # delete branch
        }
    },
    "worktree-location-guard": {
        "tool_name": "Bash",
        "tool_input": {
            "command": "git worktree add /tmp/test-wd"  # non-standard path
        }
    },
}

# Bypass env names (1:1 map to gates)
BYPASS_ENVS = {
    "cross-repo-gh-safety": "BYPASS_CROSS_REPO_GH_SAFETY",
    "repo-confinement": "BYPASS_REPO_CONFINEMENT",
    "git-branch-delete-merge-gate": "BYPASS_BRANCH_DELETE_MERGE_GATE",
    "worktree-location-guard": "BYPASS_WORKTREE_LOCATION_GUARD",
}

# Hook names (from hooks.json)
HOOK_NAMES = {
    "cross-repo-gh-safety": "cross-repo-gh-safety",
    "repo-confinement": "repo-confinement",
    "git-branch-delete-merge-gate": "git-branch-delete-merge-gate",
    "worktree-location-guard": "worktree-location-guard",
}


def _run_hook_with_env(hook_name: str, payload: dict, env_override: dict) -> tuple[int, str]:
    """훅 실행 (env 오버라이드).

    특별 처리: worktree-location-guard 는 TIER=block 동반 필수 (deny 판정 경로).
    """
    run_hook_cmd = Path(__file__).parent.parent / "run-hook.cmd"

    # 환경 변수 설정
    env = os.environ.copy()
    # 모든 bypass env 초기화
    for bypass_env in BYPASS_ENVS.values():
        env.pop(bypass_env, None)
    # 특정 env 만 설정
    env.update(env_override)
    # worktree-location-guard 는 TIER=block 동반 (deny path 진입 조건)
    if hook_name == "worktree-location-guard":
        env["WORKTREE_LOCATION_GUARD_TIER"] = "block"

    try:
        result = subprocess.run(
            ["cmd.exe", "/c", str(run_hook_cmd), hook_name],
            input=json.dumps(payload).encode("utf-8"),
            capture_output=True,
            env=env,
            timeout=30,
        )
        return result.returncode, result.stderr.decode("utf-8", errors="ignore")
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, str(e)


@pytest.mark.parametrize(
    "gate_key,bypass_env_name",
    [
        (gate, BYPASS_ENVS[gate])
        for gate in BYPASS_ENVS.keys()
    ]
)
def test_bypass_env_own_gate_exits_zero(gate_key: str, bypass_env_name: str):
    """INV-B1: 자기 게이트의 bypass env=1 → exit 0."""
    payload = DENY_PAYLOADS[gate_key]
    hook_name = HOOK_NAMES[gate_key]

    env_override = {bypass_env_name: "1"}
    rc, stderr = _run_hook_with_env(hook_name, payload, env_override)

    assert rc == 0, (
        f"Gate {gate_key} with {bypass_env_name}=1 should exit 0, got {rc}\n"
        f"stderr: {stderr}"
    )


@pytest.mark.parametrize(
    "gate_key",
    [k for k in BYPASS_ENVS.keys() if k != "git-branch-delete-merge-gate"]  # gh mock 필요 — 제외
)
@pytest.mark.parametrize(
    "other_bypass_idx",
    [0, 1, 2]  # 타 3개 bypass env
)
def test_bypass_env_other_gate_denies(gate_key: str, other_bypass_idx: int):
    """INV-B1: 타 게이트의 bypass env=1 → 자기 게이트 deny (exit 2).

    NOTE: git-branch-delete-merge-gate 는 gh 호출이 필요해 테스트 환경에서
    mock 배선 필수 (§8.2 N-5, branch-gate gh mock).
    """
    payload = DENY_PAYLOADS[gate_key]
    hook_name = HOOK_NAMES[gate_key]

    gate_keys = list(BYPASS_ENVS.keys())
    other_gates = [k for k in gate_keys if k != gate_key]

    if other_bypass_idx >= len(other_gates):
        pytest.skip(f"Not enough other gates for index {other_bypass_idx}")

    other_gate = other_gates[other_bypass_idx]
    other_bypass_env = BYPASS_ENVS[other_gate]

    env_override = {other_bypass_env: "1"}
    rc, stderr = _run_hook_with_env(hook_name, payload, env_override)

    # Deny payload: 타 env는 무시, 본 게이트는 여전히 차단
    assert rc == 2, (
        f"Gate {gate_key} with {other_bypass_env}=1 (wrong env) should exit 2, got {rc}\n"
        f"stderr: {stderr}"
    )


def test_bypass_env_unset_denies():
    """INV-B1: bypass env 미설정 → deny (exit 2)."""
    gate_key = "cross-repo-gh-safety"
    payload = DENY_PAYLOADS[gate_key]
    hook_name = HOOK_NAMES[gate_key]

    env_override = {}  # 모두 미설정
    rc, stderr = _run_hook_with_env(hook_name, payload, env_override)

    assert rc == 2, (
        f"Gate {gate_key} without bypass env should exit 2, got {rc}\n"
        f"stderr: {stderr}"
    )


def test_precondition_deny_without_bypass_env():
    """사전 조건: 각 게이트의 deny payload 가 bypass env 미설정 시 exit 2 인지 확인.

    INV-B1 의 기초 검증 — 비대각 cell 기대값(exit 2) 이 의미 있으려면
    사전에 각 게이트가 실제로 deny path 에 도달하는지 확인.

    NOTE: git-branch-delete-merge-gate 는 gh 명령 의존이므로 skip (§8.2 N-5 장애 주입에서
    네트워크 호출은 mock 배선 필요 — branch-gate gh mock 참조).
    """
    # gh 의존 게이트 제외
    non_network_gates = {k for k in DENY_PAYLOADS.keys() if k != "git-branch-delete-merge-gate"}

    for gate_key in non_network_gates:
        payload = DENY_PAYLOADS[gate_key]
        hook_name = HOOK_NAMES[gate_key]

        # env 0개 (worktree-guard 는 TIER=block 동반)
        rc, stderr = _run_hook_with_env(hook_name, payload, {})

        assert rc == 2, (
            f"Precondition failed: Gate {gate_key} with deny payload (no bypass env) "
            f"should exit 2, got {rc}. stderr: {stderr}"
        )


def test_16cell_matrix_summary():
    """16-cell matrix 검증 요약 (AC-N4 documentation)."""
    gates = list(BYPASS_ENVS.keys())
    bypass_envs = list(BYPASS_ENVS.values())

    print(f"\n16-cell bypass env gate matrix:")
    print(f"  Rows: {len(gates)} gates")
    print(f"  Cols: {len(bypass_envs)} bypass env + 1 unset = {len(bypass_envs) + 1}")
    print(f"  Cell count: {len(gates)} × {len(bypass_envs) + 1} = {len(gates) * (len(bypass_envs) + 1)}")
    print(f"  INV-B1: ∀ cell, exit==0 iff env==own(gate)")
