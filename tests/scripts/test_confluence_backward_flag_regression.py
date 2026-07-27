#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_backward_flag_regression.py — AC-3 (flag OFF 회귀 검증)."""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
from confluence_backward_sync import backward_sync_enabled, FLAG_ENV


# ── AC-3: flag OFF 기본값 검증 (backward 전면 skip) ─────────────────────────

def test_ac3_flag_default_off():
    """AC-3: 기본값(unset/무조건) = flag OFF → backward 전면 skip."""
    old_flag = os.environ.pop(FLAG_ENV, None)

    try:
        # Flag 미설정 = OFF (default)
        result = backward_sync_enabled()
        assert result is False, f"Default should be OFF (flag unset), got {result}"

    finally:
        if old_flag:
            os.environ[FLAG_ENV] = old_flag


def test_ac3_flag_set_zero_is_off():
    """AC-3: CFP2829_BACKWARD_SYNC_ENABLED='0' = OFF."""
    old_flag = os.environ.get(FLAG_ENV)

    try:
        os.environ[FLAG_ENV] = "0"
        result = backward_sync_enabled()
        assert result is False, "Flag='0' should be OFF"

    finally:
        if old_flag:
            os.environ[FLAG_ENV] = old_flag
        else:
            os.environ.pop(FLAG_ENV, None)


def test_ac3_flag_set_empty_is_off():
    """AC-3: CFP2829_BACKWARD_SYNC_ENABLED='' (empty) = OFF."""
    old_flag = os.environ.get(FLAG_ENV)

    try:
        os.environ[FLAG_ENV] = ""
        result = backward_sync_enabled()
        assert result is False, "Flag='' (empty) should be OFF"

    finally:
        if old_flag:
            os.environ[FLAG_ENV] = old_flag
        else:
            os.environ.pop(FLAG_ENV, None)


def test_ac3_flag_set_one_is_on():
    """AC-3: CFP2829_BACKWARD_SYNC_ENABLED='1' = ON."""
    old_flag = os.environ.get(FLAG_ENV)

    try:
        os.environ[FLAG_ENV] = "1"
        result = backward_sync_enabled()
        assert result is True, "Flag='1' should be ON"

    finally:
        if old_flag:
            os.environ[FLAG_ENV] = old_flag
        else:
            os.environ.pop(FLAG_ENV, None)


def test_ac3_flag_set_any_non_zero_is_on():
    """AC-3: CFP2829_BACKWARD_SYNC_ENABLED='true'/'yes'/etc = ON (any non-zero string)."""
    old_flag = os.environ.get(FLAG_ENV)

    try:
        os.environ[FLAG_ENV] = "true"
        result = backward_sync_enabled()
        assert result is True, "Flag='true' should be ON"

        os.environ[FLAG_ENV] = "yes"
        result = backward_sync_enabled()
        assert result is True, "Flag='yes' should be ON"

        os.environ[FLAG_ENV] = "enabled"
        result = backward_sync_enabled()
        assert result is True, "Flag='enabled' should be ON"

    finally:
        if old_flag:
            os.environ[FLAG_ENV] = old_flag
        else:
            os.environ.pop(FLAG_ENV, None)


# ── AC-3: interface-freeze (forward_sync 무파괴) ──────────────────────────

def test_ac3_backward_disabled_no_forward_impact():
    """AC-3: backward OFF 시 forward 무파괴 — module import 가능해야 함."""
    # confluence_forward_sync 는 leg B 에 의해 hard import 되지 않음 (lazy import)
    # backward OFF 해도 forward 는 normal operation
    import confluence_forward_sync

    # Module import success = no impact
    assert hasattr(confluence_forward_sync, "load_manifest"), "forward_sync.load_manifest must exist"


# ── AC-3 source-mutation kill (production-through discriminating tests) ─────
#
# backward_sync_enabled 는 env 를 직접 읽는 terminal predicate 라 주입 가능한 sub-dependency
# 가 없다. 위 positive/negative 테스트가 production 을 직접 호출해 양방향으로 discriminating 하다:
#   · test_ac3_flag_default_off / _set_zero_is_off / _set_empty_is_off  → "always-ON" mutant kill
#   · test_ac3_flag_set_one_is_on / _set_any_non_zero_is_on             → "always-OFF" mutant kill
#
# source-mutation kill 실증 (neuter→run→RED→restore, DevPL firsthand):
#   always-ON  : confluence_backward_sync.py backward_sync_enabled 본문을 `return True` 로 치환
#                → test_ac3_flag_default_off RED.
#   always-OFF : 본문을 `return False` 로 치환
#                → test_ac3_flag_set_one_is_on RED.
#   명령: python -m pytest tests/scripts/test_confluence_backward_flag_regression.py::test_ac3_flag_default_off
#         python -m pytest tests/scripts/test_confluence_backward_flag_regression.py::test_ac3_flag_set_one_is_on
#   기대: 각 neuter 시 대응 테스트 FAILED / restore 시 PASSED.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
