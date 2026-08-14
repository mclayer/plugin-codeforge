#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S9 (테스트): Dark-path worktree-location-guard block tier.

목적:
  WORKTREE_LOCATION_GUARD_TIER 환경 변수에 따른 동작 검증

정의역:
  WORKTREE_LOCATION_GUARD_TIER 값:
    - "block": 표준 밖 worktree add → exit 2 (deny)
    - "warn" (**default**): 표준 밖 worktree add → exit 0 (경고만, 통과)

  ★ default 정정 (CFP-2965 F5-4): 구 docstring·함수명은 default=block 이라고
    문서화했으나 실물은 warn 이다 —
    `scripts/lib/check_worktree_location_guard.py`: `os.environ.get(TIER_ENV) or "warn"`
    (실측 2026-08-14: TIER 미설정 + 표준 밖 payload → rc=0 + WARN 진단).
    구 테스트는 `assert rc in (0, 2)` 전-수용이라 이 어긋남을 검출할 수 없었다.
    도입기 warn → 승격기 block 은 CLAUDE.md / ADR-169 가 선언한 의도된 상태다.

테스트:
  - TIER=block + 표준 밖 path → exit 2 (discriminating)
  - TIER=warn + 표준 밖 path → exit 0 (discriminating vs block)
  - TIER 미설정 → warn 과 동치 (rc 0 + WARN 진단 고정)

Discriminating:
  - block-tier 와 warn-tier 의 exit code 분화 확인
  - stderr 게이트 식별자 존재 (block만)
"""

from __future__ import annotations

import json
import os
import subprocess

from hook_runner_cfp2965 import RUN_HOOK_CMD, requires_bash, requires_windows, run_hook_bash

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


def test_default_tier_is_warn():
    """TIER 미설정 → **warn** (실물 default, 도입기).

    구 `assert rc in (0, 2)` 는 가능한 두 값을 모두 수용하는 전-수용 assert 라
    default 가 어느 쪽이든 통과했다 — 문서(block)와 실물(warn)의 어긋남을
    원리적으로 검출할 수 없는 판정이었다. 실물 default 를 고정한다.
    """
    rc, stderr = _run_worktree_location_guard(None)

    assert rc == 0, (
        f"default tier 는 warn(통과) 여야 함 — got rc={rc}\n"
        f"(승격기 block 전환 시 이 테스트와 위 docstring 을 함께 갱신할 것)\n"
        f"stderr: {stderr}"
    )
    assert "WARN" in stderr, (
        f"default warn 은 경고 진단을 남겨야 한다 (조용한 통과 = 관측 소실)\n"
        f"stderr: {stderr}"
    )
    assert "BLOCKED" not in stderr, f"warn 인데 차단 진단이 나왔다\nstderr: {stderr}"
    assert "WORKTREE_LOCATION_GUARD_TIER=block" in stderr, (
        f"승격 경로 안내(block 승격 시 차단) 부재 — 도입기 warn 계약 미표기\n"
        f"stderr: {stderr}"
    )


def test_default_tier_equals_explicit_warn():
    """미설정 == TIER=warn 명시 (default 가 제3의 거동이 아님)."""
    rc_default, err_default = _run_worktree_location_guard(None)
    rc_warn, err_warn = _run_worktree_location_guard("warn")

    assert rc_default == rc_warn == 0, (
        f"미설정({rc_default}) 과 warn({rc_warn}) 이 갈렸다"
    )
    assert "WARN" in err_default and "WARN" in err_warn
    assert "BLOCKED" not in err_default and "BLOCKED" not in err_warn


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
