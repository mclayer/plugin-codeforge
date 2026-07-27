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


# ── AC-9 read-routing propagation (production-through discriminating) ──────

def test_ac9_divergence_routing_propagates_through_production():
    """AC-9 (production-through): resolve_read_with_divergence 가 내부 resolve_read_source 를
    실제로 경유해 read_source 를 결정함을 입증(agent→git-substrate 라우팅이 하류까지 전파).

    resolve_read_source 는 terminal predicate 라 sub-dependency mutation 불가 →
    상위 production 함수(resolve_read_with_divergence)를 그대로 호출해 라우팅 전파를 검증한다.
    """
    r_agent = bsync.resolve_read_with_divergence("agent", live_anchor_a="h", git_source_hash="h")
    assert r_agent["read_source"] == "git-substrate"
    r_human = bsync.resolve_read_with_divergence("human", live_anchor_a="h", git_source_hash="h")
    assert r_human["read_source"] == "atlassian-first"


# ── AC-9 source-mutation kill (neuter→run→RED→restore, DevPL firsthand) ────
#   agent 라우팅 poison → confluence_backward_sync.py resolve_read_source 의
#     `if subject == "agent": return "git-substrate"` → `return "atlassian-first"` 로 치환
#     → test_ac9_agent_maps_to_git_substrate RED
#        (+ 위 propagation 테스트도 RED — 하류 전파 반영).
#   명령: python -m pytest tests/scripts/test_confluence_backward_readpath.py::test_ac9_agent_maps_to_git_substrate
#   기대: neuter 시 FAILED / restore 시 PASSED.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
