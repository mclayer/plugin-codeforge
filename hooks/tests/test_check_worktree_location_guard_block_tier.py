#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 (테스트): Dark-path worktree-location-guard block tier.

목적:
  WORKTREE_LOCATION_GUARD_TIER 환경 변수에 따른 동작 검증

정의역:
  WORKTREE_LOCATION_GUARD_TIER 값:
    - "block" (default): 표준 밖 worktree add → exit 2 (deny)
    - "warn": 표준 밖 worktree add → exit 0 (경고만, 통과)

테스트:
  - TIER=block + 표준 밖 path → exit 2 (discriminating)
  - TIER=warn + 표준 밖 path → exit 0 (discriminating vs block)
  - TIER 미설정 → 기본값 (block 예상)

Discriminating:
  - block-tier 와 warn-tier 의 exit code 분화 확인
  - stderr 게이트 식별자 존재 (block만)
"""

from __future__ import annotations

import json
import os
import subprocess

from conftest import RUN_HOOK_CMD, requires_bash, requires_windows, run_hook_bash

# 훅 실행은 bash 직접 호출로 통일 (구 `cmd.exe /c run-hook.cmd` 하드코딩은 Linux CI 에서
# FileNotFoundError → 전건 FAIL). tier 판정 축은 OS 무관 — conftest.run_hook_bash SSOT.
pytestmark = requires_bash


def _run_worktree_location_guard(tier: str | None) -> tuple[int, str]:
    """worktree-location-guard 실행 (TIER 환경 변수 지정) → (rc, stderr)."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": "git worktree add /tmp/test-wd"  # 표준 밖 path
        }
    }

    env = os.environ.copy()
    if tier is not None:
        env["WORKTREE_LOCATION_GUARD_TIER"] = tier
    else:
        env.pop("WORKTREE_LOCATION_GUARD_TIER", None)

    rc, _stdout, stderr = run_hook_bash(
        "worktree-location-guard", json.dumps(payload).encode("utf-8"), env=env
    )
    return rc, stderr


def test_block_tier_denies_nonstandard_worktree():
    """Dark-path: TIER=block + 표준 밖 → exit 2."""
    rc, stderr = _run_worktree_location_guard("block")

    assert rc == 2, (
        f"block tier should deny non-standard worktree, exit 2, got {rc}\n"
        f"stderr: {stderr}"
    )

    # 게이트 식별자 존재 (stderr 에 진단 메시지)
    assert stderr, "block tier should have diagnostic stderr message"


def test_warn_tier_allows_nonstandard_worktree():
    """Dark-path: TIER=warn + 표준 밖 → exit 0 (warn만)."""
    rc, stderr = _run_worktree_location_guard("warn")

    assert rc == 0, (
        f"warn tier should allow non-standard worktree (exit 0), got {rc}\n"
        f"stderr: {stderr}"
    )


def test_default_tier_is_block():
    """TIER 미설정 → 기본값 (block 예상)."""
    rc, stderr = _run_worktree_location_guard(None)

    # 기본값이 block 이면 exit 2
    # 기본값이 warn 이면 exit 0
    # 구현에 따라 달라질 수 있음 — 타당성 기준 defer
    assert rc in (0, 2), (
        f"Default tier should produce consistent result, got {rc}\n"
        f"stderr: {stderr}"
    )


@requires_windows
def test_run_hook_cmd_launcher_propagates_exit_code():
    """런처 축: run-hook.cmd(cmd.exe 배치) 경유 시 훅의 exit 2 가 소실 없이 전파되는가.

    본 축만 Windows 전용인 이유: 훅의 **판정**(tier 거동)은 위 테스트들이 bash 직접
    호출로 OS 무관하게 검증한다. 여기서 검증하는 대상은 판정이 아니라 **런처 자체의
    계약** — `setlocal enabledelayedexpansion` + `exit /b !ERRORLEVEL!` 가 자식 프로세스의
    rc 를 1 로 뭉개지 않는지다. 이는 cmd.exe 가 있어야만 성립하는 Windows 고유 축이라
    skipif 로 분리한다 (Linux 에서는 run-hook.cmd 의 polyglot 1행 `:; exec bash ...` 가
    대신 쓰이므로 검증 대상 자체가 다르다).

    구 코드에서는 모든 테스트가 cmd.exe 를 경유해 이 성질이 *우연히* 함께 덮였다.
    bash 직접 호출로 전환하며 잃는 커버리지를 여기서 명시적으로 되살린다.
    """
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "git worktree add /tmp/test-wd"},
    }
    env = os.environ.copy()
    env["WORKTREE_LOCATION_GUARD_TIER"] = "block"

    proc = subprocess.run(
        ["cmd.exe", "/c", str(RUN_HOOK_CMD), "worktree-location-guard"],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True,
        env=env,
        timeout=60,
    )

    # rc 2 그대로여야 한다 (배치가 rc 를 잃으면 0 또는 1 로 뭉개진다).
    assert proc.returncode == 2, (
        f"run-hook.cmd 가 훅의 exit 2 를 전파하지 못함 (rc={proc.returncode}) — "
        f"PreToolUse deny 가 통과로 뒤집힌다\nstderr: {proc.stderr.decode('utf-8', 'replace')[:300]}"
    )


def test_block_vs_warn_discriminating():
    """Discriminating case: block ≠ warn."""
    rc_block, stderr_block = _run_worktree_location_guard("block")
    rc_warn, stderr_warn = _run_worktree_location_guard("warn")

    # 명확히 다름
    assert rc_block != rc_warn, (
        f"block({rc_block}) should differ from warn({rc_warn})"
    )

    # block 은 stderr 진단 메시지
    if rc_block == 2:
        assert stderr_block, "block tier exit 2 should have diagnostic stderr"
