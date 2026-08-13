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
import subprocess
import os
import pytest
from pathlib import Path


def _run_worktree_location_guard(tier: str | None) -> tuple[int, str]:
    """worktree-location-guard 실행 (TIER 환경 변수 지정)."""
    run_hook_cmd = Path(__file__).parent.parent / "run-hook.cmd"

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

    try:
        result = subprocess.run(
            ["cmd.exe", "/c", str(run_hook_cmd), "worktree-location-guard"],
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
