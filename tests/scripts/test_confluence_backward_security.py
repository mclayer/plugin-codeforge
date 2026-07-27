#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_backward_security.py — 보안테스트 FIX 회귀 (F-SEC-01 path-traversal / F-SEC-02 ADF-DoS).

각 test = 보안테스트 lane finding 의 reproducer 를 fix 후 회귀 GREEN 으로 봉인.
production 경유(monkeypatch 자기-assert theater 아님).
"""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest

import confluence_backward_sync as bsync
import confluence_backward_gate as gate
from path_safety import safe_rel_path, contained_target


# ── F-SEC-01: path-traversal (write + gate staging) ─────────────────────────

def test_fsec01_safe_rel_path_rejects_traversal_and_absolute():
    """`..`/절대경로/드라이브/빈 경로 거부, 정상 rel 통과."""
    for bad in ["../x.md", "docs/../../x.md", "/etc/passwd", "C:/win.md", "", ".", "\\\\srv\\x"]:
        with pytest.raises(ValueError):
            safe_rel_path(bad)
    assert safe_rel_path("docs/adr/ADR-001-x.md") == "docs/adr/ADR-001-x.md"
    assert safe_rel_path("/docs/x.md".lstrip("/")) == "docs/x.md"  # 정상(선행 슬래시 없는)


def test_fsec01_contained_target_blocks_escape(tmp_path):
    """contained_target 이 base 밖 이탈을 ValueError 로 차단."""
    ok = contained_target(tmp_path, "docs/change-plans/foo.md")
    assert str(ok).startswith(str(tmp_path.resolve()))
    with pytest.raises(ValueError):
        contained_target(tmp_path, "../CFP2829_PWNED.md")


def test_fsec01_write_substrate_rejects_traversal(tmp_path):
    """write_substrate_working_tree(`../`) → InvariantViolation + repo 밖 파일 생성 0."""
    outside = tmp_path.parent / "CFP2829_PWNED.md"
    if outside.exists():
        outside.unlink()
    with pytest.raises(bsync.InvariantViolation):
        bsync.write_substrate_working_tree(str(tmp_path), "../CFP2829_PWNED.md", b"pwned")
    assert not outside.exists(), "path-traversal write 가 repo 밖에 파일을 생성했다(F-SEC-01 회귀)"


def test_fsec01_write_substrate_normal_path_ok(tmp_path):
    """정상 rel_path 는 repo 하위에 정상 write(회귀 방지)."""
    written = bsync.write_substrate_working_tree(str(tmp_path), "docs/adr/ADR-001-x.md", b"# ok\n")
    assert (tmp_path / "docs/adr/ADR-001-x.md").exists()
    assert str(written).startswith(str(tmp_path.resolve()))


def test_fsec01_gate_rejects_traversal_no_vacuous_pass():
    """verify_substrate(`../`) → False(fail-closed) — staging escape 로 인한 vacuous-pass 봉인."""
    assert gate.verify_substrate(b"# anything\n", "adr", "../evil.md") is False
    assert gate.verify_substrate(b"# anything\n", "adr", "docs/../../evil.md") is False


# ── F-SEC-02: ADF unbounded recursion DoS ───────────────────────────────────

def test_fsec02_adf_deep_nesting_bounded_no_recursionerror():
    """9000-deep blockquote → RecursionError 없이 depth-exceeded lossy-accept 절단."""
    node = {"type": "text", "text": "x"}
    for _ in range(9000):
        node = {"type": "blockquote", "content": [node]}
    doc = {"type": "doc", "content": [node]}
    # 수정 전: RecursionError. 수정 후: bounded (crash 0).
    md, dropped = bsync.adf_to_markdown(doc)
    assert "depth-exceeded" in dropped, "depth cap 이 작동하지 않음(F-SEC-02 회귀)"


def test_fsec02_adf_shallow_still_converts():
    """얕은 정상 ADF 는 depth cap 무관하게 정상 변환(회귀 방지)."""
    doc = {"type": "doc", "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "hello"}]},
    ]}
    md, dropped = bsync.adf_to_markdown(doc)
    assert "hello" in md
    assert "depth-exceeded" not in dropped
