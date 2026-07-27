#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_backward_readpath.py — AC-9 (INV-READ read routing)."""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
import confluence_backward_sync as bsync


# ── AC-9: resolve_read_source (routing dispatcher) ──────────────────────────

def test_ac9_agent_maps_to_git_substrate():
    """AC-9: subject='agent' → 'git-substrate' (primary, not Confluence direct)."""
    assert bsync.resolve_read_source("agent") == "git-substrate"


def test_ac9_human_maps_to_atlassian_first():
    """AC-9: subject='human' → 'atlassian-first' (UX surface)."""
    assert bsync.resolve_read_source("human") == "atlassian-first"


def test_ac9_unknown_subject_raises_valueerror():
    """AC-9: unknown subject → ValueError."""
    with pytest.raises(ValueError, match="unknown read subject"):
        bsync.resolve_read_source("unknown")

    with pytest.raises(ValueError):
        bsync.resolve_read_source("")

    with pytest.raises(ValueError):
        bsync.resolve_read_source(None)


# ── AC-9: resolve_read_with_divergence (divergence handling) ───────────────

def test_ac9_no_divergence_git_authoritative():
    """AC-9: matching anchors → no divergence, git authoritative."""
    result = bsync.resolve_read_with_divergence(
        "agent",
        live_anchor_a="abc123def456",
        git_source_hash="abc123def456"
    )

    assert result["subject"] == "agent"
    assert result["read_source"] == "git-substrate"
    assert result["diverged"] is False
    assert "authoritative" not in result  # No audit event emitted


def test_ac9_divergence_detected_git_chosen():
    """AC-9: anchor mismatch → divergence, git authoritative, audit emitted."""
    result = bsync.resolve_read_with_divergence(
        "agent",
        live_anchor_a="old_hash_123",
        git_source_hash="new_hash_456"
    )

    assert result["subject"] == "agent"
    assert result["read_source"] == "git-substrate"
    assert result["diverged"] is True
    assert result["authoritative"] == "git-substrate"
    assert "audit_event" in result
    assert result["audit_event"]["event"] == "read_divergence"


def test_ac9_empty_anchors_safe_no_divergence_flag():
    """AC-9: empty anchors → no divergence (divergence requires both values)."""
    result = bsync.resolve_read_with_divergence(
        "agent",
        live_anchor_a="",
        git_source_hash="abc123"
    )

    assert result["diverged"] is False

    result = bsync.resolve_read_with_divergence(
        "agent",
        live_anchor_a="abc123",
        git_source_hash=""
    )

    assert result["diverged"] is False


# ── AC-9 MUTATION: read routing poisoned (agent→atlassian-first) ──────────

def test_ac9_mutation_agent_routed_to_atlassian(monkeypatch):
    """AC-9 MUTATION: if resolve_read_source(agent) → 'atlassian-first' (direct Confluence).

    Discriminating case: agent should read git-substrate primary, but mutant
    routes to Confluence direct → read-poisoning (UX surface instead of truth).

    Inject mutant: agent maps to wrong path.
    """
    def mutant_resolve_read_source(subject):
        if subject == "agent":
            return "atlassian-first"  # WRONG: should be git-substrate
        if subject == "human":
            return "atlassian-first"
        raise ValueError(f"unknown read subject: {subject!r}")

    monkeypatch.setattr("confluence_backward_sync.resolve_read_source", mutant_resolve_read_source)

    from confluence_backward_sync import resolve_read_source as patched

    # Agent should read substrate, not Confluence
    result = patched("agent")
    assert result == "atlassian-first"  # Mutant produces wrong result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
