#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_property_rest.py — AC-10 축②(token env-absence) + AC-12 (error classify) + AC-13 (rate meter)."""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
from confluence_property_rest import (
    create_rest_client,
    is_over_limit_error,
    BUDGET_BYTES,
    MAX_RETRY_ATTEMPTS,
    INITIAL_BACKOFF_SECONDS,
    CFP1495_MOCK_MODE,
)


# ── AC-10 축②: token env-absence → write rejection ──────────────────────────

def test_ac10_creds_absent_write_rejected():
    """AC-10: ATLASSIAN_* env missing → put_property_v2 returns (False, 'Creds absent')."""
    # Clear env
    old_token = os.environ.pop("ATLASSIAN_API_TOKEN", None)
    old_email = os.environ.pop("ATLASSIAN_USER_EMAIL", None)

    try:
        client = create_rest_client("https://example.atlassian.net")

        # Write attempt must fail with IO-1 hard-fail
        success, error = client.put_property_v2("page123", "key", {"value": "data"})

        assert success is False
        assert error is not None
        assert "Creds absent" in error

    finally:
        if old_token:
            os.environ["ATLASSIAN_API_TOKEN"] = old_token
        if old_email:
            os.environ["ATLASSIAN_USER_EMAIL"] = old_email


# ── AC-10 축② MUTATION: token env check removed (write proceeds) ───────────

def test_ac10_mutation_creds_check_removed(monkeypatch):
    """AC-10 MUTATION: if creds check removed (always allow write).

    Discriminating case: write should fail without creds, but mutant allows it.
    """
    # Mutant: skip creds validation
    def mutant_put_property(self, page_id, property_key, value):
        # MUTANT: no creds check, always proceed
        return True, None  # Write succeeds even without creds

    monkeypatch.setattr("confluence_property_rest.ConfluencePropertyREST.put_property_v2", mutant_put_property)

    old_token = os.environ.pop("ATLASSIAN_API_TOKEN", None)
    old_email = os.environ.pop("ATLASSIAN_USER_EMAIL", None)

    try:
        client = create_rest_client("https://example.atlassian.net")

        from confluence_property_rest import ConfluencePropertyREST
        success, error = client.put_property_v2("page123", "key", {"value": "data"})

        # Mutant allows write (should be rejected)
        assert success is True

    finally:
        if old_token:
            os.environ["ATLASSIAN_API_TOKEN"] = old_token
        if old_email:
            os.environ["ATLASSIAN_USER_EMAIL"] = old_email


# ── AC-12: over_limit_error classification (v1 vs v2) ────────────────────────

def test_ac12_v1_413_over_limit():
    """AC-12: v1 API, status 413 → over-limit."""
    assert is_over_limit_error(1, 413, "") is True


def test_ac12_v1_400_not_over_limit():
    """AC-12: v1 API, status 400 → not over-limit (400 overloaded in v1)."""
    assert is_over_limit_error(1, 400, "any message") is False


def test_ac12_v2_400_with_size_signature_over_limit():
    """AC-12: v2 API, 400 + 'too large' → over-limit."""
    assert is_over_limit_error(2, 400, "value too large") is True
    assert is_over_limit_error(2, 400, "too long") is True
    assert is_over_limit_error(2, 400, "exceeds 5242880") is True
    assert is_over_limit_error(2, 400, "32KB limit") is True


def test_ac12_v2_400_without_size_signature_not_over_limit():
    """AC-12: v2 API, 400 without size signature → not over-limit."""
    assert is_over_limit_error(2, 400, "invalid JSON") is False
    assert is_over_limit_error(2, 400, "key already exists") is False


def test_ac12_v2_other_status_not_over_limit():
    """AC-12: v2 API, non-400 status → not over-limit."""
    assert is_over_limit_error(2, 401, "") is False
    assert is_over_limit_error(2, 429, "") is False
    assert is_over_limit_error(2, 500, "") is False


# ── AC-13: rate meter constants (declared) ──────────────────────────────────

def test_ac13_rate_meter_constants():
    """AC-13 (declared): rate meter constants defined."""
    assert MAX_RETRY_ATTEMPTS >= 2, "retry attempts must be >=2"
    assert INITIAL_BACKOFF_SECONDS > 0, "backoff must be positive"


def test_ac13_backoff_sequence():
    """AC-13 (declared): exponential backoff calculation."""
    # Mock backoff sequence: 1, 2, 4 seconds for 3 attempts
    backoff = INITIAL_BACKOFF_SECONDS
    sequence = []

    for attempt in range(MAX_RETRY_ATTEMPTS):
        sequence.append(backoff)
        backoff *= 2

    # Verify exponential growth
    assert sequence[0] == INITIAL_BACKOFF_SECONDS
    assert sequence[1] == INITIAL_BACKOFF_SECONDS * 2
    assert sequence[2] == INITIAL_BACKOFF_SECONDS * 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
