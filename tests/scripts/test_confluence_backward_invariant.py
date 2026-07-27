#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_backward_invariant.py — AC-5 (INV-A PR-only) + AC-4 (flag) + AC-3 (dark-path)."""

import sys
import os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
import confluence_backward_sync as bsync


# ── AC-5: assert_pr_only (INV-A — no auto-merge, no direct base-write) ──────

def test_ac5_pr_only_good_proposal_passes():
    """AC-5: well-formed PR proposal (auto_merge=False, direct_push=False) → pass."""
    proposal = {
        "branch": "cfp2829-backward-feature",
        "base": "main",
        "auto_merge": False,
        "direct_push_to_base": False,
    }

    # Must not raise
    bsync.assert_pr_only(proposal)


def test_ac5_auto_merge_true_fails():
    """AC-5: auto_merge=True → InvariantViolation."""
    proposal = {
        "branch": "cfp2829-backward-feature",
        "base": "main",
        "auto_merge": True,  # VIOLATION
        "direct_push_to_base": False,
    }

    with pytest.raises(bsync.InvariantViolation, match="auto_merge"):
        bsync.assert_pr_only(proposal)


def test_ac5_direct_push_to_base_fails():
    """AC-5: direct_push_to_base=True → InvariantViolation."""
    proposal = {
        "branch": "cfp2829-backward-feature",
        "base": "main",
        "auto_merge": False,
        "direct_push_to_base": True,  # VIOLATION
    }

    with pytest.raises(bsync.InvariantViolation, match="direct_push_to_base"):
        bsync.assert_pr_only(proposal)


def test_ac5_branch_equals_base_fails():
    """AC-5: feature branch == base → InvariantViolation."""
    proposal = {
        "branch": "main",  # Same as base
        "base": "main",
        "auto_merge": False,
        "direct_push_to_base": False,
    }

    with pytest.raises(bsync.InvariantViolation, match="feature branch"):
        bsync.assert_pr_only(proposal)


def test_ac5_branch_missing_fails():
    """AC-5: branch absent → InvariantViolation."""
    proposal = {
        "base": "main",
        "auto_merge": False,
        "direct_push_to_base": False,
    }

    with pytest.raises(bsync.InvariantViolation, match="feature branch"):
        bsync.assert_pr_only(proposal)


# ── AC-5 MUTATION: auto_merge check removed (always-pass mutant) ───────────

def test_ac5_mutation_auto_merge_check_removed(monkeypatch):
    """AC-5 MUTATION: if auto_merge check is commented out (always-pass).

    Discriminating case: auto_merge=True should raise, but mutant doesn't check.
    """
    def mutant_assert_pr_only(proposal):
        # MUTANT: auto_merge check removed
        if proposal.get("direct_push_to_base"):
            raise bsync.InvariantViolation("INV-A 위반: direct_push_to_base=True")
        branch = proposal.get("branch")
        base = proposal.get("base")
        if not branch or branch == base:
            raise bsync.InvariantViolation(f"INV-A 위반: feature branch 부재/base 동일")

    monkeypatch.setattr("confluence_backward_sync.assert_pr_only", mutant_assert_pr_only)

    from confluence_backward_sync import assert_pr_only as patched

    proposal = {
        "branch": "feature",
        "base": "main",
        "auto_merge": True,  # Should fail, but mutant ignores
        "direct_push_to_base": False,
    }

    # Mutant does NOT raise (because check is removed)
    patched(proposal)  # No exception


# ── AC-3: cutover flag (backward_sync_enabled) ──────────────────────────────

def test_ac3_flag_default_off():
    """AC-3: CFP2829_BACKWARD_SYNC_ENABLED unset → OFF (backward_sync_enabled = False)."""
    # Ensure env is clear
    old_env = os.environ.pop(bsync.FLAG_ENV, None)
    try:
        assert bsync.backward_sync_enabled() is False
    finally:
        if old_env is not None:
            os.environ[bsync.FLAG_ENV] = old_env


def test_ac3_flag_explicit_0_off():
    """AC-3: CFP2829_BACKWARD_SYNC_ENABLED='0' → OFF."""
    old_env = os.environ.get(bsync.FLAG_ENV)
    try:
        os.environ[bsync.FLAG_ENV] = "0"
        assert bsync.backward_sync_enabled() is False
    finally:
        if old_env is not None:
            os.environ[bsync.FLAG_ENV] = old_env
        else:
            os.environ.pop(bsync.FLAG_ENV, None)


def test_ac3_flag_explicit_1_on():
    """AC-3: CFP2829_BACKWARD_SYNC_ENABLED='1' → ON."""
    old_env = os.environ.get(bsync.FLAG_ENV)
    try:
        os.environ[bsync.FLAG_ENV] = "1"
        assert bsync.backward_sync_enabled() is True
    finally:
        if old_env is not None:
            os.environ[bsync.FLAG_ENV] = old_env
        else:
            os.environ.pop(bsync.FLAG_ENV, None)


# ── AC-4: dark-path (ADF → substrate → PR) ──────────────────────────────────

def test_ac4_derive_substrate_dark_path():
    """AC-4: ADF → derive_substrate → gate_passed ∧ chunk_properties ∧ commit_metadata."""
    adf = {
        "type": "doc",
        "content": [
            {
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": "Title"}]
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Body content."}]
            }
        ]
    }

    result = bsync.derive_substrate(
        adf,
        "docs/architecture/test.md",
        "architecture_doc",
        source_page_url="https://example.atlassian.net/l/page123",
        editor="test@example.com",
        timestamp="2024-01-01T00:00:00Z"
    )

    # Dark-path assertions
    assert result["gate_passed"] is True
    assert result["anchor_a"] is not None
    assert len(result["anchor_a"]) == 64  # sha256 hex
    assert result["chunk_properties"] is not None
    assert "__manifest" in result["chunk_properties"]
    assert result["commit_metadata"] is not None
    assert result["commit_metadata"]["editor"] == "test@example.com"


# ── AC-3/AC-4 integration: flag controls backward entry ────────────────────

def test_ac34_main_flag_off_early_exit():
    """AC-3/AC-4 integration: main(--detect) with flag OFF → early exit code 0."""
    old_env = os.environ.get(bsync.FLAG_ENV)
    try:
        os.environ[bsync.FLAG_ENV] = "0"

        # main() should exit early if flag OFF
        rc = bsync.main(["--detect", "--input", "-"])
        assert rc == 0  # Early exit (AC-3 skip)

    finally:
        if old_env is not None:
            os.environ[bsync.FLAG_ENV] = old_env
        else:
            os.environ.pop(bsync.FLAG_ENV, None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
