#!/usr/bin/env python3
# scripts/lib/importance_score.py — CFP-1173 Phase 2
# blast-radius importance_score 3-tuple weighted_sum Python SSOT (ADR-061)
#
# 책임 (design SSOT: brainstorming 결정 4):
#   blast-radius 3-tuple weighted_sum importance_score 계산
#   input: BlastRadiusTuple (touched_lanes_count + breaking_change_marker + contract_major_bump)
#   output: importance_score (정렬용 수치, 높을수록 영향도 높음)
#
# 가중치 설계 (brainstorming 결정 4 + imperative-walker-protocol-v1 §중요도):
#   touched_lanes_count:  lanes × WEIGHT_LANES    (0~7 range, 7 plugin family 상한)
#   breaking_change_marker: True → WEIGHT_BREAKING (binary: 0 or WEIGHT_BREAKING)
#   contract_major_bump:  bumps × WEIGHT_CONTRACT  (0~N range)
#
# 가중치 비율 (직관적 우선순위: breaking > contract_major > lanes):
#   WEIGHT_BREAKING  = 30  (binary flag, 가장 높은 단일 기여)
#   WEIGHT_CONTRACT  = 10  (per MAJOR bump)
#   WEIGHT_LANES     = 3   (per lane touched)
#
# ADR refs:
#   ADR-061 python script-writing convention (외부 .py 의무)
#   imperative-walker-protocol-v1 §중요도 순서 (blast-radius 3-tuple)
#
# SSOT: docs/change-plans/cfp-1173-blast-radius-parallel.md §3 importance_score 3-tuple
# Contract: docs/inter-plugin-contracts/imperative-walker-protocol-v1.md §중요도
#
# sanity check 3종 (ADR-061 의무):
#   1. diff inspection — 구현 직후 reviewer가 수행
#   2. lint re-run — flake8/ruff (CI)
#   3. sample file Read — 본 파일 상단 직접 확인
#
# Sandbox env: CBL_SKIP_ISSUE_CREATE=1

from __future__ import annotations

from dataclasses import dataclass
from typing import List

# ─────────────────────── 가중치 상수 ──────────────────────────────────────────

# 가중치 (brainstorming 결정 4 — 직관적 우선순위: breaking > contract_major > lanes)
WEIGHT_LANES: int = 3       # per lane touched (0~7 range)
WEIGHT_BREAKING: int = 30   # binary flag (breaking change = 가장 높은 단일 기여)
WEIGHT_CONTRACT: int = 10   # per MAJOR bump

# 7 plugin family 상한 (wrapper + 6 lane)
MAX_TOUCHED_LANES: int = 7


# ─────────────────────── BlastRadiusTuple ─────────────────────────────────────

@dataclass
class BlastRadiusTuple:
    """blast-radius 3-tuple (brainstorming 결정 4).

    Fields:
        touched_lanes_count: 영향받는 lane 수 (0~MAX_TOUCHED_LANES=7)
        breaking_change_marker: BREAKING CHANGE 포함 여부 (CHANGELOG ## [X.Y.Z] BREAKING 마커)
        contract_major_bump: inter-plugin contract MAJOR 버전 bump 수 (0~N)

    Raises:
        ValueError: touched_lanes_count < 0 또는 > MAX_TOUCHED_LANES
        TypeError: 타입 불일치
    """
    touched_lanes_count: int
    breaking_change_marker: bool
    contract_major_bump: int

    def __post_init__(self) -> None:
        """입력 검증 — abort-before-compute (잘못된 tuple 즉시 raise)."""
        if not isinstance(self.touched_lanes_count, int):
            raise TypeError(
                f"touched_lanes_count 는 int 이어야 함: {type(self.touched_lanes_count)}"
            )
        if not isinstance(self.contract_major_bump, int):
            raise TypeError(
                f"contract_major_bump 는 int 이어야 함: {type(self.contract_major_bump)}"
            )
        if self.touched_lanes_count < 0:
            raise ValueError(
                f"touched_lanes_count 는 0 이상이어야 함: {self.touched_lanes_count}"
            )
        if self.touched_lanes_count > MAX_TOUCHED_LANES:
            raise ValueError(
                f"touched_lanes_count 상한 초과: {self.touched_lanes_count} > {MAX_TOUCHED_LANES} "
                f"(7 plugin family 상한)"
            )
        if self.contract_major_bump < 0:
            raise ValueError(
                f"contract_major_bump 는 0 이상이어야 함: {self.contract_major_bump}"
            )


# ─────────────────────── 계산 함수 ───────────────────────────────────────────

def calc_importance_score(entry: BlastRadiusTuple) -> int:
    """blast-radius 3-tuple weighted_sum importance_score 계산.

    Formula (brainstorming 결정 4):
        score = (touched_lanes_count × WEIGHT_LANES)
              + (WEIGHT_BREAKING if breaking_change_marker else 0)
              + (contract_major_bump × WEIGHT_CONTRACT)

    Args:
        entry: BlastRadiusTuple (3-tuple)

    Returns:
        importance_score (int, 0 이상 — 높을수록 blast radius 높음)

    Examples:
        >>> calc_importance_score(BlastRadiusTuple(1, False, 0))
        3
        >>> calc_importance_score(BlastRadiusTuple(0, False, 0))
        0
        >>> calc_importance_score(BlastRadiusTuple(7, True, 3))
        21 + 30 + 30 = 81
    """
    lanes_score = entry.touched_lanes_count * WEIGHT_LANES
    breaking_score = WEIGHT_BREAKING if entry.breaking_change_marker else 0
    contract_score = entry.contract_major_bump * WEIGHT_CONTRACT

    return lanes_score + breaking_score + contract_score


def sort_by_importance(entries: List[BlastRadiusTuple]) -> List[BlastRadiusTuple]:
    """importance_score 기준 내림차순 정렬.

    고 blast-radius entry 를 상위에 배치 (적용 계획 우선순위 반영).

    Args:
        entries: BlastRadiusTuple 목록

    Returns:
        importance_score 내림차순 정렬된 새 list (원본 불변)
    """
    return sorted(entries, key=calc_importance_score, reverse=True)


# ─────────────────────── CLI entry point ─────────────────────────────────────

if __name__ == "__main__":
    # sanity check self-test (ADR-061 §결정 3 sanity check 3종 중 sample)
    print("importance_score.py sanity check:")
    print(f"  WEIGHT_LANES={WEIGHT_LANES}, WEIGHT_BREAKING={WEIGHT_BREAKING}, WEIGHT_CONTRACT={WEIGHT_CONTRACT}")
    print(f"  MAX_TOUCHED_LANES={MAX_TOUCHED_LANES}")

    # zero entry
    zero = BlastRadiusTuple(0, False, 0)
    assert calc_importance_score(zero) == 0, f"sanity FAIL: {calc_importance_score(zero)}"
    print("  BlastRadiusTuple(0, False, 0) → 0 ✓")

    # basic entry
    basic = BlastRadiusTuple(1, False, 0)
    assert calc_importance_score(basic) == WEIGHT_LANES, f"sanity FAIL: {calc_importance_score(basic)}"
    print(f"  BlastRadiusTuple(1, False, 0) → {WEIGHT_LANES} ✓")

    # breaking entry
    breaking = BlastRadiusTuple(2, True, 0)
    expected = 2 * WEIGHT_LANES + WEIGHT_BREAKING
    assert calc_importance_score(breaking) == expected, f"sanity FAIL: {calc_importance_score(breaking)}"
    print(f"  BlastRadiusTuple(2, True, 0) → {expected} ✓")

    # max entry
    max_entry = BlastRadiusTuple(7, True, 3)
    expected_max = 7 * WEIGHT_LANES + WEIGHT_BREAKING + 3 * WEIGHT_CONTRACT
    assert calc_importance_score(max_entry) == expected_max, f"sanity FAIL: {calc_importance_score(max_entry)}"
    print(f"  BlastRadiusTuple(7, True, 3) → {expected_max} ✓")

    # sort check
    entries = [
        BlastRadiusTuple(1, False, 0),
        BlastRadiusTuple(7, True, 3),
        BlastRadiusTuple(3, True, 0),
    ]
    sorted_entries = sort_by_importance(entries)
    scores = [calc_importance_score(e) for e in sorted_entries]
    assert scores == sorted(scores, reverse=True), f"sanity FAIL sort: {scores}"
    print(f"  sort_by_importance 내림차순: {scores} ✓")

    print("sanity check PASS")
