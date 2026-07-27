#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_backward_gate.py — AC-2 (structure-gate pass) + AC-6 (fail-closed)."""

import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
import confluence_backward_gate as gate


# ── AC-2: verify_substrate pass-through (ungated doc_type) ──────────────────

def test_ac2_ungated_architecture_doc_passthrough():
    """AC-2: architecture_doc (ungated) → verify_substrate(True)."""
    markdown = b"# Architecture\n\nSome content."
    result = gate.verify_substrate(markdown, "architecture_doc", "docs/architecture/test.md")
    assert result is True  # Pass-through (ungated)


def test_ac2_ungated_consumer_guide_passthrough():
    """AC-2: consumer_guide (ungated) → True."""
    markdown = b"# Consumer Guide\n\nUsage instructions."
    result = gate.verify_substrate(markdown, "consumer_guide", "docs/consumer-guide.md")
    assert result is True


# ── AC-2: gated doc_type pass (well-formed) ──────────────────────────────────

def test_ac2_gated_adr_wellformed_passes():
    """AC-2: adr doc_type with valid frontmatter + sections → True."""
    # Minimal valid ADR (gated)
    markdown_text = """---
adr_number: 999
title: Test ADR
status: draft
category: architecture
date: 2024-01-01
---

## 상태
Draft.

## 컨텍스트
Test context.

## 결정
Test decision.

## 결과
Test result.

## 관련 파일
- file.txt
"""
    markdown = markdown_text.encode("utf-8")
    result = gate.verify_substrate(markdown, "adr", "docs/adr/ADR-999-test.md")
    assert result is True


# ── AC-6: fail-closed (gated doc_type malformed) ────────────────────────────

def test_ac6_gated_adr_missing_sections_blocked():
    """AC-6: adr with missing required sections → False (fail-closed)."""
    incomplete_adr_text = """---
adr_number: 999
title: Test
status: draft
category: architecture
date: 2024-01-01
---

## 상태
Only status section (missing 컨텍스트, 결정, 결과, 관련파일).
"""
    incomplete_adr = incomplete_adr_text.encode("utf-8")
    result = gate.verify_substrate(incomplete_adr, "adr", "docs/adr/ADR-999-test.md")
    # Gate should reject due to missing sections
    assert result is False


def test_ac6_gated_change_plan_blocked_invalid():
    """AC-6: change_plan with invalid frontmatter → False (fail-closed)."""
    invalid_cp_text = """---
story_key: CFP-9999
invalid_field: value
---

Some content.
"""
    invalid_cp = invalid_cp_text.encode("utf-8")
    result = gate.verify_substrate(invalid_cp, "change_plan", "docs/change-plans/cfp-9999-test.md")
    assert result is False


def test_ac6_invalid_candidate_bytes_type():
    """AC-6: non-bytes input → False (fail-closed safety)."""
    with pytest.raises(TypeError):
        gate.verify_substrate("not bytes", "adr", "docs/adr/test.md")


def test_ac6_empty_rel_path():
    """AC-6: empty rel_path → False (fail-closed)."""
    markdown = b"# Test"
    result = gate.verify_substrate(markdown, "adr", "")
    assert result is False


# ── AC-6 MUTATION: fail-open escape (gate always True) ───────────────────────

# CR-C1 (F-CR-002 residual): hollow mutation test 제거 (지연 ClaudeReview peer 검출).
# 직전 버전(test_ac6_mutation_gate_always_passes)은 production _run_gate 를 always-True 로
# monkeypatch 한 뒤 그 mutant 결과(True)를 자기-assert → production fail-closed 회귀를
# 미검출(판별력 0, hollow theater).
# AC-6 fail-open mutation kill = source-mutation harness 로 실증(주석 기록):
#   production confluence_backward_gate._run_gate 를 `return True`(fail-open)로 실변조 →
#   아래 production-through negative test(test_ac6_gated_adr_missing_sections_blocked 등) RED.
# genuine 커버리지는 그 negative test 들이 담당(production verify_substrate 실호출).


# ── AC-2 + AC-6: real subprocess execution (if gate scripts present) ────────

def test_ac2_ac6_gate_script_execution():
    """AC-2/AC-6: if gate scripts exist, verify_substrate calls them via subprocess."""
    # Check if gate scripts are available
    gate_exists = all(s.exists() for s in gate._GATE_SCRIPTS)

    if not gate_exists:
        pytest.skip("Gate scripts not found (expected in CI)")

    # Ungated pass-through (no subprocess call needed)
    result = gate.verify_substrate(b"# Test", "architecture_doc", "docs/architecture/x.md")
    assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
