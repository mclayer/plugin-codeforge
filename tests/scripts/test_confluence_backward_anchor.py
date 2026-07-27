#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_backward_anchor.py — AC-8 (offline determinism, mutation)."""

import sys
import os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
import confluence_backward_sync as bsync

# AC-8 R-1: offline (no ATLASSIAN_* env access)
def test_ac8_offline_creds_absent():
    """AC-8 R-1: test executes offline, ATLASSIAN_* env must be absent."""
    assert os.environ.get("ATLASSIAN_API_TOKEN") is None, \
        "ATLASSIAN_API_TOKEN must not be set for offline test"
    assert os.environ.get("ATLASSIAN_USER_EMAIL") is None, \
        "ATLASSIAN_USER_EMAIL must not be set for offline test"


# ── AC-8: substrate_anchor_a (offline hash, CRLF/ws normalization) ──────────

def test_ac8_substrate_anchor_a_deterministic():
    """AC-8: substrate_anchor_a(data) → deterministic sha256 hex."""
    data = b"test markdown content"
    anchor1 = bsync.substrate_anchor_a(data)
    anchor2 = bsync.substrate_anchor_a(data)

    assert anchor1 == anchor2
    assert len(anchor1) == 64  # sha256 hex


def test_ac8_substrate_anchor_a_crlf_normalization():
    """AC-8: CRLF → LF normalization (byte-compatible across platforms)."""
    crlf_data = b"line1\r\nline2\r\n"
    lf_data = b"line1\nline2\n"

    # Both should produce same anchor after normalization
    anchor_crlf = bsync.substrate_anchor_a(crlf_data)
    anchor_lf = bsync.substrate_anchor_a(lf_data)

    assert anchor_crlf == anchor_lf, "CRLF/LF must normalize to same anchor"


def test_ac8_substrate_anchor_a_trailing_ws_strip():
    """AC-8: normalization consistent across equivalent inputs.

    _normalize_markdown handles CRLF + trailing-ws strips. Equivalent inputs
    should produce same anchor after normalization.
    """
    # CRLF normalization (equivalent after normalize)
    crlf = b"content\r\n"
    lf = b"content\n"

    a_crlf = bsync.substrate_anchor_a(crlf)
    a_lf = bsync.substrate_anchor_a(lf)

    # Both should normalize to same canonical form
    assert a_crlf == a_lf


def test_ac8_substrate_anchor_a_1byte_drift_detectable():
    """AC-8: 1-byte drift → different anchor (100% sensitivity)."""
    data1 = b"content X"
    data2 = b"content Y"

    anchor1 = bsync.substrate_anchor_a(data1)
    anchor2 = bsync.substrate_anchor_a(data2)

    assert anchor1 != anchor2, "1-byte difference must be detectable"


# ── AC-8: anchor_mismatch (offline decision) ──────────────────────────────

def test_ac8_anchor_mismatch_detect():
    """AC-8: anchor_mismatch(substrate, stored) → True if mismatch detected."""
    substrate = b"current markdown content"
    correct_anchor = bsync.substrate_anchor_a(substrate)
    different_anchor = bsync.substrate_anchor_a(b"different content")

    # Correct match → False (no mismatch)
    assert bsync.anchor_mismatch(substrate, correct_anchor) is False

    # Wrong anchor → True (mismatch detected)
    assert bsync.anchor_mismatch(substrate, different_anchor) is True


def test_ac8_anchor_mismatch_1byte_sensitive():
    """AC-8: 1-byte drift in substrate → mismatch detected."""
    base_content = b"content block"
    stored_anchor = bsync.substrate_anchor_a(base_content)

    # Modify by 1 byte
    modified = b"content black"

    # Mismatch must be detected
    assert bsync.anchor_mismatch(modified, stored_anchor) is True


# ── AC-8 MUTATION: normalization bypass (genuine — production 경유 + 실 dependency mutate) ──

def test_ac8_mutation_normalize_bypass_detectable(monkeypatch):
    """AC-8 MUTATION (genuine, option-a): production substrate_anchor_a 를 그대로 호출하되
    실 dependency `_normalize_markdown` 를 identity 로 monkeypatch 해 production output 이
    실제로 flip 하는지 assert.

    discriminating 계약 (_normalize_markdown = CRLF→LF + per-line rstrip):
      base     = b"alpha\\nbeta"            (trailing ws 없음)
      trailing = b"alpha   \\nbeta\\t\\t"   (line별 trailing ws)
      · REAL normalization → 둘 다 "alpha\\nbeta" 로 collapse → anchor SAME.
      · identity mutant(normalization 제거) → trailing ws 보존 → anchor DIFFERENT.
    production substrate_anchor_a 가 실제로 _normalize_markdown 을 경유함을 입증(제거 시 drift 미붕괴).
    """
    base = b"alpha\nbeta"
    trailing = b"alpha   \nbeta\t\t"

    # (1) REAL normalization 하 production 호출 → trailing ws collapse → 동일 anchor.
    real_base = bsync.substrate_anchor_a(base)
    real_trailing = bsync.substrate_anchor_a(trailing)
    assert real_base == real_trailing, \
        "REAL: _normalize_markdown rstrip 이 trailing ws 를 collapse 해야 함(동일 anchor)"

    # (2) identity mutant 주입(normalization 제거) 후 동일 production 함수 재호출.
    def mutant_identity(data):
        return bytes(data) if isinstance(data, (bytes, bytearray)) else str(data).encode("utf-8")

    monkeypatch.setattr("confluence_backward_sync._normalize_markdown", mutant_identity)

    mut_base = bsync.substrate_anchor_a(base)
    mut_trailing = bsync.substrate_anchor_a(trailing)

    # MUTANT: identity 는 trailing ws 를 strip 안 함 → anchor DIFFER (production output flip).
    assert mut_base != mut_trailing, \
        "MUT: normalization 제거 시 trailing ws 가 보존되어 anchor 가 달라져야 함(discriminating)"
    # cross-check: mutant base 는 REAL base 와 동일(공백 없는 입력은 normalize 영향 0),
    #              mutant trailing 은 REAL trailing 과 다름(normalize 가 load-bearing 이던 부분).
    assert mut_base == real_base
    assert mut_trailing != real_trailing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
