#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-963 / ADR-081 Amendment 4 / ADR-060 Amendment 14
# pytest unit tests for check_codex_network_scope.py
#
# TDD RED → GREEN sequence (QADeveloperAgent, codeforge superpowers:test-driven-development):
#   RED:  these tests are written FIRST (implementation absent) — all fail.
#   GREEN: implementation written → all pass.
#
# Test coverage table (Story §8.5 / Change Plan §6 TestContractArch synthesis):
#   enum_value_offline_detected                 (1 case)
#   enum_value_repo_fetch_only_detected         (1 case)
#   enum_value_web_fetch_detected               (1 case)
#   enum_value_offline_substitution_declared_detected (1 case)
#   unknown_enum_value_advisory_warn            (1 case)
#   legacy_true_advisory                        (1 case)
#   legacy_false_advisory                       (1 case)
#   legacy_coexist_advisory                     (1 case)
#   field_absent_warning                        (1 case)
#   field_empty_warning                         (1 case)
#
# Invariants (Story §8.5 I-INV1 ~ I-INV4):
#   I-INV1: boolean legacy (sandbox_network_required:*) → always exit 0 (grace window)
#   I-INV2: unknown enum value → advisory warn, NOT hard-fail
#   I-INV3: network_scope field absent → warning tier (exit 1)
#   I-INV4: carrier_story self-exempt flag → skip enforcement (exit 0)
#
# SecurityArch §7.2 TH-2: no PAT/secret in lint output (set +x guard)
# ADR-061 §결정 1 정합: thin bash wrapper + Python SSOT (this file)
# ADR-081 §D5 declaration-only retain: lint = presence check only, NOT semantic validation

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Module loader helper — loads check_codex_network_scope.py from scripts/lib/
# ---------------------------------------------------------------------------
_HERE = Path(__file__).parent
_IMPL_PATH = _HERE / "check_codex_network_scope.py"


def _load_module():
    """Load the implementation module (absent in RED phase = ImportError → test fail)."""
    if not _IMPL_PATH.exists():
        pytest.fail(
            f"Implementation absent (TDD RED expected): {_IMPL_PATH}\n"
            "GREEN: write scripts/lib/check_codex_network_scope.py to make tests pass."
        )
    spec = importlib.util.spec_from_file_location("check_codex_network_scope", _IMPL_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
FIXTURE_DIR = Path(__file__).parent.parent.parent / "tests" / "fixtures"


@pytest.fixture
def impl():
    """Return the loaded implementation module."""
    return _load_module()


@pytest.fixture
def fixture_with_network_scope():
    """Fixture file WITH network_scope field (PASS expected)."""
    p = FIXTURE_DIR / "codex_spawn_prompt_with_network_scope.txt"
    assert p.exists(), f"Fixture missing: {p}"
    return p


@pytest.fixture
def fixture_without_network_scope():
    """Fixture file WITHOUT network_scope field (WARN expected)."""
    p = FIXTURE_DIR / "codex_spawn_prompt_without_network_scope.txt"
    assert p.exists(), f"Fixture missing: {p}"
    return p


# ---------------------------------------------------------------------------
# TC-1: enum_value_offline_detected
# ---------------------------------------------------------------------------
def test_enum_value_offline_detected(impl, tmp_path):
    """network_scope: offline → PASS (exit 0, valid enum)."""
    f = tmp_path / "prompt.txt"
    f.write_text("network_scope: offline\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0
    assert result.get("enum_value") == "offline"


# ---------------------------------------------------------------------------
# TC-2: enum_value_repo_fetch_only_detected
# ---------------------------------------------------------------------------
def test_enum_value_repo_fetch_only_detected(impl, tmp_path):
    """network_scope: repo-fetch-only → PASS (exit 0, valid enum)."""
    f = tmp_path / "prompt.txt"
    f.write_text("network_scope: repo-fetch-only\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0
    assert result.get("enum_value") == "repo-fetch-only"


# ---------------------------------------------------------------------------
# TC-3: enum_value_web_fetch_detected
# ---------------------------------------------------------------------------
def test_enum_value_web_fetch_detected(impl, tmp_path):
    """network_scope: web-fetch → PASS (exit 0, valid enum)."""
    f = tmp_path / "prompt.txt"
    f.write_text("network_scope: web-fetch\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0
    assert result.get("enum_value") == "web-fetch"


# ---------------------------------------------------------------------------
# TC-4: enum_value_offline_substitution_declared_detected
# ---------------------------------------------------------------------------
def test_enum_value_offline_substitution_declared_detected(impl, tmp_path):
    """network_scope: offline_substitution_declared → PASS (exit 0, valid enum)."""
    f = tmp_path / "prompt.txt"
    f.write_text("network_scope: offline_substitution_declared\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0
    assert result.get("enum_value") == "offline_substitution_declared"


# ---------------------------------------------------------------------------
# TC-5: unknown_enum_value_advisory_warn (I-INV2)
# ADR-068 I-3 unconditional guard: unknown value = advisory only (exit 0, NOT exit 1)
# ---------------------------------------------------------------------------
def test_unknown_enum_value_advisory_warn(impl, tmp_path):
    """network_scope: <unknown> → advisory warn, exit 0 (unconditional guard, ADR-068 I-3)."""
    f = tmp_path / "prompt.txt"
    f.write_text("network_scope: totally-unknown-value\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    # Must NOT hard-fail — advisory only (I-INV2)
    assert result["exit_code"] == 0
    # Must emit advisory marker
    assert "[unknown-enum-value-advisory]" in result.get("advisory_markers", []) or \
           "unknown" in result.get("message", "").lower()


# ---------------------------------------------------------------------------
# TC-6: legacy_true_advisory (I-INV1)
# sandbox_network_required: true → [legacy-boolean-detected] advisory, exit 0 (grace window)
# ---------------------------------------------------------------------------
def test_legacy_true_advisory(impl, tmp_path):
    """sandbox_network_required: true → exit 0, [legacy-boolean-detected] advisory."""
    f = tmp_path / "prompt.txt"
    f.write_text("sandbox_network_required: true\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    assert result["exit_code"] == 0  # I-INV1: always exit 0 for boolean legacy
    markers = result.get("advisory_markers", [])
    assert any("legacy-boolean-detected" in m for m in markers) or \
           "legacy" in result.get("message", "").lower()


# ---------------------------------------------------------------------------
# TC-7: legacy_false_advisory (I-INV1)
# ---------------------------------------------------------------------------
def test_legacy_false_advisory(impl, tmp_path):
    """sandbox_network_required: false → exit 0, [legacy-boolean-detected] advisory."""
    f = tmp_path / "prompt.txt"
    f.write_text("sandbox_network_required: false\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    assert result["exit_code"] == 0  # I-INV1


# ---------------------------------------------------------------------------
# TC-8: legacy_coexist_advisory (I-INV1)
# Both boolean legacy AND network_scope present → enum wins, boolean advisory still emitted
# ---------------------------------------------------------------------------
def test_legacy_coexist_advisory(impl, tmp_path):
    """Both fields present → enum PASS + boolean legacy advisory (coexist graceful)."""
    f = tmp_path / "prompt.txt"
    f.write_text(
        "network_scope: offline\nsandbox_network_required: false\n", encoding="utf-8"
    )
    result = impl.check_network_scope_presence(str(f))
    # Enum PASS takes precedence
    assert result["status"] == "PASS"
    assert result["exit_code"] == 0
    # Boolean advisory still emitted (coexist)
    markers = result.get("advisory_markers", [])
    assert any("legacy" in m for m in markers) or \
           "legacy" in result.get("message", "").lower()


# ---------------------------------------------------------------------------
# TC-9: field_absent_warning (I-INV3)
# ---------------------------------------------------------------------------
def test_field_absent_warning(impl, tmp_path):
    """No network_scope field → WARNING (exit 1), advisory comment emitted."""
    f = tmp_path / "prompt.txt"
    f.write_text(
        "## Task\nDo something without declaring network scope.\n", encoding="utf-8"
    )
    result = impl.check_network_scope_presence(str(f))
    assert result["exit_code"] == 1
    assert result["status"] in ("WARN", "WARNING")


# ---------------------------------------------------------------------------
# TC-10: field_empty_warning
# network_scope: (empty value) → warning
# ---------------------------------------------------------------------------
def test_field_empty_warning(impl, tmp_path):
    """network_scope: (empty) → WARNING (exit 1), not a valid enum value."""
    f = tmp_path / "prompt.txt"
    f.write_text("network_scope: \n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    # Empty value = no enum — warning tier
    assert result["exit_code"] == 1
    assert result["status"] in ("WARN", "WARNING")


# ---------------------------------------------------------------------------
# TC-11: fixture_pair_discriminator_with_field (CX-963-3 P2 boundary mandate)
# ---------------------------------------------------------------------------
def test_fixture_pair_with_field_pass(impl, fixture_with_network_scope):
    """Fixture WITH network_scope field → PASS (discriminating fixture)."""
    result = impl.check_network_scope_presence(str(fixture_with_network_scope))
    assert result["exit_code"] == 0
    assert result["status"] == "PASS"


# ---------------------------------------------------------------------------
# TC-12: fixture_pair_discriminator_without_field (CX-963-3 P2 boundary mandate)
# ---------------------------------------------------------------------------
def test_fixture_pair_without_field_warn(impl, fixture_without_network_scope):
    """Fixture WITHOUT network_scope field → WARN (discriminating fixture)."""
    result = impl.check_network_scope_presence(str(fixture_without_network_scope))
    assert result["exit_code"] == 1
    assert result["status"] in ("WARN", "WARNING")


# ---------------------------------------------------------------------------
# TC-13: carrier_story self-exempt (I-INV4)
# If carrier_story=CFP-963 → skip enforcement (exit 0)
# ---------------------------------------------------------------------------
def test_carrier_story_self_exempt(impl, tmp_path):
    """carrier_story=CFP-963 → lint skip (self-exempt, exit 0)."""
    f = tmp_path / "prompt.txt"
    f.write_text("## No network_scope here\ncarrier_story: CFP-963\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f), carrier_story="CFP-963")
    assert result["exit_code"] == 0
    assert "exempt" in result.get("message", "").lower() or \
           result.get("status") == "PASS"


# ---------------------------------------------------------------------------
# TC-14: no_secret_in_output (SecurityArch TH-2 guard)
# PAT / token keywords must NOT appear in lint output
# ---------------------------------------------------------------------------
def test_no_secret_in_output(impl, tmp_path):
    """Lint output must not contain PAT/token/secret keywords (TH-2 guard)."""
    f = tmp_path / "prompt.txt"
    f.write_text("network_scope: offline\n", encoding="utf-8")
    result = impl.check_network_scope_presence(str(f))
    output_str = str(result)
    # SecurityArch TH-2: no sensitive tokens in output
    for forbidden in ("CODEFORGE_CROSS_REPO_PAT", "ghp_", "github_pat_"):
        assert forbidden not in output_str, \
            f"Secret keyword '{forbidden}' found in lint output (TH-2 violation)"
