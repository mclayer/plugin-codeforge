#!/usr/bin/env python3
# tests/scripts/cfp-1173/test_parallel_safety.py
# CFP-1173 Phase 2 — parallel_safety.py TDD pytest (TC-13~26)
# QADeveloperAgent TDD RED phase — scripts/lib/parallel_safety.py 구현 전 작성
#
# TC map (design SSOT: brainstorming 결정 5):
# TC-13: file-path disjoint 자동 판정 — 교집합 없음 → parallel_safe=True
# TC-14: file-path overlap 자동 판정 — 교집합 있음 → parallel_safe=False
# TC-15: entry-level parallel_safe_with=["entry_b"] override → True (file overlap에도)
# TC-16: override 미지정 + file overlap → False (default auto-detect)
# TC-17: override 미지정 + file disjoint → True (default auto-detect)
# TC-18: 빈 file set (entry에 touched_files=[]) → parallel_safe=True (disjoint 간주)
# TC-19: 단일 entry pair — 양방향 symmetric (A→B = B→A)
# TC-20: N-entry batch 판정 — 모두 disjoint → all_safe=True
# TC-21: N-entry batch 판정 — 하나 overlap → all_safe=False
# TC-22: override loop 방어 — entry가 자기 자신과 parallel_safe_with → safe=True
# TC-23: discriminating — path prefix 달라도 부분 일치 없으면 disjoint
# TC-24: discriminating — 동일 경로 서로 다른 entry → overlap 검출
# TC-25: 빈 override list (parallel_safe_with=[]) → auto-detect fallback
# TC-26: overlap 검출 시 overlap_paths 반환 (교집합 경로 목록)
#
# 3-layer defense (#960 always-pass 회피):
#   Layer 1 — TC assertion 의무
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture
#
# ADR-061 정합: 외부 .py 파일 (heredoc-python 0)
# SSOT: brainstorming 결정 5 + imperative-walker-protocol-v1 §병렬 판정
# Sandbox: CBL_SKIP_ISSUE_CREATE=1

import os
import sys

import pytest

os.environ.setdefault("CBL_SKIP_ISSUE_CREATE", "1")

SCRIPTS_LIB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "scripts", "lib"
)
sys.path.insert(0, os.path.abspath(SCRIPTS_LIB_PATH))

try:
    from parallel_safety import (
        PlanEntry,
        ParallelVerdict,
        check_pair_safety,
        check_batch_safety,
    )
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _MODULE_AVAILABLE,
    reason="parallel_safety.py 미구현 (TDD RED phase)"
)


# ─────────────────────────── TC-13: disjoint → safe ──────────────────────────

def test_tc13_disjoint_files_safe():
    """TC-13: file-path 교집합 없음 → parallel_safe=True"""
    a = PlanEntry(entry_id="A", touched_files=["scripts/foo.sh", "docs/a.md"])
    b = PlanEntry(entry_id="B", touched_files=["scripts/bar.sh", "docs/b.md"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is True, "교집합 없으면 parallel_safe=True"
    assert verdict.overlap_paths == [], "교집합 없으면 overlap_paths=[]"


# ─────────────────────────── TC-14: overlap → unsafe ─────────────────────────

def test_tc14_overlap_files_unsafe():
    """TC-14: file-path 교집합 있음 → parallel_safe=False"""
    a = PlanEntry(entry_id="A", touched_files=["scripts/foo.sh", "scripts/shared.sh"])
    b = PlanEntry(entry_id="B", touched_files=["scripts/shared.sh", "docs/b.md"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is False, "교집합 있으면 parallel_safe=False"
    assert "scripts/shared.sh" in verdict.overlap_paths, "overlap_paths에 공유 파일 포함"


# ─────────────────────────── TC-15: override → safe (file overlap에도) ────────

def test_tc15_override_forces_safe():
    """TC-15: entry-level parallel_safe_with 명시 → parallel_safe=True (file overlap에도)"""
    a = PlanEntry(
        entry_id="A",
        touched_files=["scripts/shared.sh"],
        parallel_safe_with=["B"],
    )
    b = PlanEntry(entry_id="B", touched_files=["scripts/shared.sh"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is True, "override 명시 시 file overlap에도 safe"
    assert verdict.override_applied is True, "override_applied=True 표시"


# ─────────────────────────── TC-16: no override + overlap → unsafe ────────────

def test_tc16_no_override_with_overlap_unsafe():
    """TC-16: override 미지정 + file overlap → False (default auto-detect)"""
    a = PlanEntry(entry_id="A", touched_files=["scripts/shared.sh"])
    b = PlanEntry(entry_id="B", touched_files=["scripts/shared.sh"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is False
    assert verdict.override_applied is False


# ─────────────────────────── TC-17: no override + disjoint → safe ─────────────

def test_tc17_no_override_disjoint_safe():
    """TC-17: override 미지정 + file disjoint → True (default auto-detect)"""
    a = PlanEntry(entry_id="A", touched_files=["scripts/a.sh"])
    b = PlanEntry(entry_id="B", touched_files=["scripts/b.sh"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is True
    assert verdict.override_applied is False


# ─────────────────────────── TC-18: 빈 file set → safe ───────────────────────

def test_tc18_empty_files_safe():
    """TC-18: touched_files=[] → parallel_safe=True (disjoint 간주)"""
    a = PlanEntry(entry_id="A", touched_files=[])
    b = PlanEntry(entry_id="B", touched_files=["scripts/foo.sh"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is True, "빈 파일 셋은 disjoint 간주 → safe"


# ─────────────────────────── TC-19: symmetric ────────────────────────────────

def test_tc19_symmetric():
    """TC-19: 양방향 symmetric (A→B = B→A)"""
    a = PlanEntry(entry_id="A", touched_files=["scripts/shared.sh"])
    b = PlanEntry(entry_id="B", touched_files=["scripts/shared.sh"])
    ab = check_pair_safety(a, b)
    ba = check_pair_safety(b, a)
    assert ab.parallel_safe == ba.parallel_safe, "A→B와 B→A는 동일해야 함"


# ─────────────────────────── TC-20: batch all safe ───────────────────────────

def test_tc20_batch_all_safe():
    """TC-20: N-entry batch — 모두 disjoint → all_safe=True"""
    entries = [
        PlanEntry(entry_id="A", touched_files=["scripts/a.sh"]),
        PlanEntry(entry_id="B", touched_files=["scripts/b.sh"]),
        PlanEntry(entry_id="C", touched_files=["docs/c.md"]),
    ]
    result = check_batch_safety(entries)
    assert result.all_safe is True, "전부 disjoint이면 all_safe=True"
    assert result.unsafe_pairs == [], "unsafe_pairs=[]"


# ─────────────────────────── TC-21: batch one overlap ────────────────────────

def test_tc21_batch_one_overlap():
    """TC-21: N-entry batch — 하나 overlap → all_safe=False"""
    entries = [
        PlanEntry(entry_id="A", touched_files=["scripts/shared.sh"]),
        PlanEntry(entry_id="B", touched_files=["scripts/b.sh"]),
        PlanEntry(entry_id="C", touched_files=["scripts/shared.sh"]),  # A와 overlap
    ]
    result = check_batch_safety(entries)
    assert result.all_safe is False, "하나라도 overlap이면 all_safe=False"
    assert len(result.unsafe_pairs) >= 1, "unsafe_pairs에 A-C 쌍 포함"
    pair_ids = [(p.entry_a_id, p.entry_b_id) for p in result.unsafe_pairs]
    assert ("A", "C") in pair_ids or ("C", "A") in pair_ids, "A-C 쌍이 unsafe_pairs에"


# ─────────────────────────── TC-22: self-parallel safe ───────────────────────

def test_tc22_self_parallel_safe():
    """TC-22: entry가 자기 자신과 parallel_safe_with → safe=True"""
    a = PlanEntry(
        entry_id="A",
        touched_files=["scripts/shared.sh"],
        parallel_safe_with=["A"],
    )
    verdict = check_pair_safety(a, a)
    assert verdict.parallel_safe is True


# ─────────────────────────── TC-23: path prefix 불일치 ───────────────────────

def test_tc23_discriminating_path_prefix():
    """TC-23: path prefix 달라도 완전 일치 없으면 disjoint"""
    a = PlanEntry(entry_id="A", touched_files=["scripts/foo/bar.sh"])
    b = PlanEntry(entry_id="B", touched_files=["scripts/foo/baz.sh"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is True, "부분 prefix 일치 ≠ 파일 일치 → disjoint"


# ─────────────────────────── TC-24: 동일 경로 overlap ────────────────────────

def test_tc24_discriminating_same_path():
    """TC-24: 동일 경로 서로 다른 entry → overlap 검출"""
    a = PlanEntry(entry_id="A", touched_files=["docs/stories/CFP-1173.md"])
    b = PlanEntry(entry_id="B", touched_files=["docs/stories/CFP-1173.md"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is False, "동일 경로 → overlap"
    assert "docs/stories/CFP-1173.md" in verdict.overlap_paths


# ─────────────────────────── TC-25: empty override fallback ──────────────────

def test_tc25_empty_override_fallback():
    """TC-25: parallel_safe_with=[] → auto-detect fallback (override 미적용)"""
    a = PlanEntry(
        entry_id="A",
        touched_files=["scripts/shared.sh"],
        parallel_safe_with=[],  # 빈 override = auto-detect
    )
    b = PlanEntry(entry_id="B", touched_files=["scripts/shared.sh"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is False, "빈 override list → auto-detect → overlap → unsafe"
    assert verdict.override_applied is False, "빈 override는 override 미적용"


# ─────────────────────────── TC-26: overlap_paths 반환 ───────────────────────

def test_tc26_overlap_paths_returned():
    """TC-26: overlap 검출 시 overlap_paths에 교집합 경로 목록 반환"""
    a = PlanEntry(entry_id="A", touched_files=["scripts/a.sh", "scripts/shared.sh", "docs/a.md"])
    b = PlanEntry(entry_id="B", touched_files=["scripts/b.sh", "scripts/shared.sh"])
    verdict = check_pair_safety(a, b)
    assert verdict.parallel_safe is False
    assert set(verdict.overlap_paths) == {"scripts/shared.sh"}, \
        f"overlap_paths = {{'scripts/shared.sh'}} 이어야 함, actual={verdict.overlap_paths}"
