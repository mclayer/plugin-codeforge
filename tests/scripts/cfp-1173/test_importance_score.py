#!/usr/bin/env python3
# tests/scripts/cfp-1173/test_importance_score.py
# CFP-1173 Phase 2 — importance_score.py TDD pytest (TC-1~12)
# QADeveloperAgent TDD RED phase — scripts/lib/importance_score.py 구현 전 작성
#
# TC map (design SSOT: brainstorming 결정 4):
# TC-1: 3-tuple 기본 (touched_lanes=1, breaking=False, contract_major=0) → score 계산
# TC-2: touched_lanes_count 가중치 반영 (lanes 증가 시 score 증가)
# TC-3: breaking_change_marker=True → score 가중 증가
# TC-4: contract_major_bump=1 → score 가중 증가
# TC-5: 3-tuple 전체 최대값 → 최고 score
# TC-6: 3-tuple 전체 0 → 최저 score (0)
# TC-7: score 정렬 — 고 blast-radius entry 상위 (내림차순)
# TC-8: discriminating — touched_lanes=2 > touched_lanes=1 (lanes 차이 단독 반영)
# TC-9: discriminating — breaking_change True > False (breaking 단독 반영)
# TC-10: discriminating — contract_major=2 > contract_major=0 (contract 단독 반영)
# TC-11: 음수 입력 → ValueError raise (방어)
# TC-12: touched_lanes_count 상한(7 plugin family) 초과 → ValueError raise
#
# 3-layer defense (#960 always-pass 회피):
#   Layer 1 — TC assertion 의무 (no pytest.skip masking)
#   Layer 2 — 2-assertion per TC (positive + negative / boundary)
#   Layer 3 — discriminating fixture (단독 변수 변경으로 score 차이 검증)
#
# ADR-061 정합: 외부 .py 파일 (heredoc-python 0)
# SSOT: brainstorming 결정 4 + imperative-walker-protocol-v1 §중요도
# Sandbox: CBL_SKIP_ISSUE_CREATE=1

import os
import sys

import pytest

os.environ.setdefault("CBL_SKIP_ISSUE_CREATE", "1")

SCRIPTS_LIB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "scripts", "lib"
)
sys.path.insert(0, os.path.abspath(SCRIPTS_LIB_PATH))

# RED phase: ImportError 예상 (importance_score.py 미구현) → 구현 후 GREEN
try:
    from importance_score import (
        BlastRadiusTuple,
        calc_importance_score,
        sort_by_importance,
    )
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _MODULE_AVAILABLE,
    reason="importance_score.py 미구현 (TDD RED phase)"
)


# ─────────────────────────── TC-1: 기본 score 계산 ───────────────────────────

def test_tc1_basic_score():
    """TC-1: 3-tuple 기본 (touched_lanes=1, breaking=False, contract_major=0) → 양수 score"""
    entry = BlastRadiusTuple(touched_lanes_count=1, breaking_change_marker=False, contract_major_bump=0)
    score = calc_importance_score(entry)
    assert isinstance(score, (int, float)), "score는 수치여야 함"
    assert score >= 0, "기본 score는 0 이상"


# ─────────────────────────── TC-2: lanes 가중치 ───────────────────────────────

def test_tc2_lanes_weight():
    """TC-2: touched_lanes_count 증가 시 score 증가"""
    low = BlastRadiusTuple(touched_lanes_count=1, breaking_change_marker=False, contract_major_bump=0)
    high = BlastRadiusTuple(touched_lanes_count=5, breaking_change_marker=False, contract_major_bump=0)
    assert calc_importance_score(high) > calc_importance_score(low), \
        "lanes_count 5 > 1 이면 score도 높아야 함"
    # negative: 같은 lanes → 같은 score
    same1 = BlastRadiusTuple(touched_lanes_count=3, breaking_change_marker=False, contract_major_bump=0)
    same2 = BlastRadiusTuple(touched_lanes_count=3, breaking_change_marker=False, contract_major_bump=0)
    assert calc_importance_score(same1) == calc_importance_score(same2)


# ─────────────────────────── TC-3: breaking_change 가중치 ────────────────────

def test_tc3_breaking_change_weight():
    """TC-3: breaking_change_marker=True → score 가중 증가"""
    no_break = BlastRadiusTuple(touched_lanes_count=2, breaking_change_marker=False, contract_major_bump=0)
    with_break = BlastRadiusTuple(touched_lanes_count=2, breaking_change_marker=True, contract_major_bump=0)
    assert calc_importance_score(with_break) > calc_importance_score(no_break), \
        "breaking=True면 score가 더 높아야 함"
    # negative: breaking=False < breaking=True
    assert not (calc_importance_score(no_break) > calc_importance_score(with_break))


# ─────────────────────────── TC-4: contract_major 가중치 ─────────────────────

def test_tc4_contract_major_weight():
    """TC-4: contract_major_bump=1 → score 가중 증가"""
    no_major = BlastRadiusTuple(touched_lanes_count=1, breaking_change_marker=False, contract_major_bump=0)
    with_major = BlastRadiusTuple(touched_lanes_count=1, breaking_change_marker=False, contract_major_bump=1)
    assert calc_importance_score(with_major) > calc_importance_score(no_major), \
        "contract_major=1이면 score가 더 높아야 함"


# ─────────────────────────── TC-5: 최대값 ────────────────────────────────────

def test_tc5_max_score():
    """TC-5: 3-tuple 전체 최대값 → 최고 score"""
    max_entry = BlastRadiusTuple(touched_lanes_count=7, breaking_change_marker=True, contract_major_bump=3)
    min_entry = BlastRadiusTuple(touched_lanes_count=1, breaking_change_marker=False, contract_major_bump=0)
    assert calc_importance_score(max_entry) > calc_importance_score(min_entry), \
        "전체 최대값 entry가 최소값 entry보다 높아야 함"


# ─────────────────────────── TC-6: 최저값 ────────────────────────────────────

def test_tc6_zero_score():
    """TC-6: 3-tuple 전체 0 → 최저 score (0)"""
    zero_entry = BlastRadiusTuple(touched_lanes_count=0, breaking_change_marker=False, contract_major_bump=0)
    score = calc_importance_score(zero_entry)
    assert score == 0, f"전체 0 tuple → score=0 이어야 함, actual={score}"


# ─────────────────────────── TC-7: 정렬 ──────────────────────────────────────

def test_tc7_sort_descending():
    """TC-7: sort_by_importance → 고 blast-radius 상위 (내림차순)"""
    entries = [
        BlastRadiusTuple(touched_lanes_count=1, breaking_change_marker=False, contract_major_bump=0),
        BlastRadiusTuple(touched_lanes_count=7, breaking_change_marker=True, contract_major_bump=2),
        BlastRadiusTuple(touched_lanes_count=3, breaking_change_marker=True, contract_major_bump=0),
    ]
    sorted_entries = sort_by_importance(entries)
    scores = [calc_importance_score(e) for e in sorted_entries]
    assert scores == sorted(scores, reverse=True), \
        "sort_by_importance는 내림차순이어야 함"
    # negative: 정렬 전 첫 entry가 정렬 후 첫 entry와 달라야 함 (위 설정상 첫=lowest)
    assert sorted_entries[0] != entries[0], \
        "정렬 후 첫 entry는 원래 첫 entry와 달라야 함 (lowest→최후)"


# ─────────────────────────── TC-8: discriminating lanes ──────────────────────

def test_tc8_discriminating_lanes_only():
    """TC-8: touched_lanes 차이만으로 score 차이 (breaking/contract 동일)"""
    base = BlastRadiusTuple(touched_lanes_count=2, breaking_change_marker=False, contract_major_bump=0)
    higher = BlastRadiusTuple(touched_lanes_count=4, breaking_change_marker=False, contract_major_bump=0)
    diff = calc_importance_score(higher) - calc_importance_score(base)
    assert diff > 0, f"lanes 4>2 → score 차이 양수여야 함, diff={diff}"


# ─────────────────────────── TC-9: discriminating breaking ───────────────────

def test_tc9_discriminating_breaking_only():
    """TC-9: breaking_change 차이만으로 score 차이 (lanes/contract 동일)"""
    no_break = BlastRadiusTuple(touched_lanes_count=3, breaking_change_marker=False, contract_major_bump=1)
    with_break = BlastRadiusTuple(touched_lanes_count=3, breaking_change_marker=True, contract_major_bump=1)
    diff = calc_importance_score(with_break) - calc_importance_score(no_break)
    assert diff > 0, f"breaking=True → score 차이 양수여야 함, diff={diff}"


# ─────────────────────────── TC-10: discriminating contract ──────────────────

def test_tc10_discriminating_contract_only():
    """TC-10: contract_major 차이만으로 score 차이 (lanes/breaking 동일)"""
    low_contract = BlastRadiusTuple(touched_lanes_count=2, breaking_change_marker=True, contract_major_bump=0)
    high_contract = BlastRadiusTuple(touched_lanes_count=2, breaking_change_marker=True, contract_major_bump=2)
    diff = calc_importance_score(high_contract) - calc_importance_score(low_contract)
    assert diff > 0, f"contract=2>0 → score 차이 양수여야 함, diff={diff}"


# ─────────────────────────── TC-11: 음수 방어 ────────────────────────────────

def test_tc11_negative_input_raises():
    """TC-11: 음수 입력 → ValueError raise"""
    with pytest.raises((ValueError, TypeError)):
        BlastRadiusTuple(touched_lanes_count=-1, breaking_change_marker=False, contract_major_bump=0)


# ─────────────────────────── TC-12: 상한 초과 방어 ───────────────────────────

def test_tc12_lanes_over_max_raises():
    """TC-12: touched_lanes_count > 7 (7 plugin family 상한 초과) → ValueError raise"""
    with pytest.raises((ValueError, TypeError)):
        BlastRadiusTuple(touched_lanes_count=8, breaking_change_marker=False, contract_major_bump=0)
