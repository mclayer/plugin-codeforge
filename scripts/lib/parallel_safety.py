#!/usr/bin/env python3
# scripts/lib/parallel_safety.py — CFP-1173 Phase 2
# 병렬 판정 이중 메커니즘 Python SSOT (ADR-061)
#
# 책임 (design SSOT: brainstorming 결정 5):
#   병렬 판정 이중 메커니즘:
#   (1) file-path 교집합 자동 default — touched_files 집합 교집합 검사
#   (2) entry-level parallel_safe_with: [] override — 명시 entry ID와 쌍이면 safe 강제
#
# 판정 우선순위 (brainstorming 결정 5):
#   override 명시 (parallel_safe_with에 상대 entry_id 포함) → parallel_safe=True
#   override 없음 또는 빈 override → file-path 교집합 auto-detect
#     교집합 없음(disjoint) → parallel_safe=True
#     교집합 있음(overlap) → parallel_safe=False
#
# ADR refs:
#   ADR-061 python script-writing convention (외부 .py 의무)
#   ADR-064 §Trace 4 — parallel default, sequential 3 사유
#   imperative-walker-protocol-v1 §병렬 판정 (file-path disjoint + override)
#
# SSOT: docs/change-plans/cfp-1173-blast-radius-parallel.md §3 병렬 이중 algorithm
# Contract: docs/inter-plugin-contracts/imperative-walker-protocol-v1.md §병렬 판정
#
# sanity check 3종 (ADR-061 의무):
#   1. diff inspection — 구현 직후 reviewer가 수행
#   2. lint re-run — flake8/ruff (CI)
#   3. sample file Read — 본 파일 상단 직접 확인
#
# Sandbox env: CBL_SKIP_ISSUE_CREATE=1

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ─────────────────────── 데이터 클래스 ───────────────────────────────────────

@dataclass
class PlanEntry:
    """plan stage 단일 entry (병렬 판정 대상).

    Fields:
        entry_id: entry 식별자 (unique, parallel_safe_with 참조용)
        touched_files: 해당 entry가 수정하는 파일 경로 목록 (절대 또는 repo-relative)
        parallel_safe_with: 명시적 병렬 안전 entry_id 목록 (override, 빈 list = auto-detect)
    """
    entry_id: str
    touched_files: List[str] = field(default_factory=list)
    parallel_safe_with: List[str] = field(default_factory=list)


@dataclass
class ParallelVerdict:
    """pair 병렬 판정 결과.

    Fields:
        entry_a_id: 판정 대상 entry A id
        entry_b_id: 판정 대상 entry B id
        parallel_safe: True=병렬 안전 / False=순차 필요
        override_applied: True=parallel_safe_with override 적용됨
        overlap_paths: file-path 교집합 (parallel_safe=False 시 비어있지 않음)
        reason: 판정 근거 설명
    """
    entry_a_id: str
    entry_b_id: str
    parallel_safe: bool
    override_applied: bool = False
    overlap_paths: List[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class BatchVerdict:
    """N-entry batch 병렬 판정 결과.

    Fields:
        all_safe: 모든 pair가 parallel_safe=True
        unsafe_pairs: parallel_safe=False 인 ParallelVerdict 목록
        safe_pairs: parallel_safe=True 인 ParallelVerdict 목록 (참조용)
    """
    all_safe: bool
    unsafe_pairs: List[ParallelVerdict] = field(default_factory=list)
    safe_pairs: List[ParallelVerdict] = field(default_factory=list)


# ─────────────────────── pair 판정 ───────────────────────────────────────────

def check_pair_safety(a: PlanEntry, b: PlanEntry) -> ParallelVerdict:
    """pair (a, b) 병렬 판정 이중 메커니즘.

    판정 우선순위:
    1. a.parallel_safe_with에 b.entry_id 포함 → override=True, safe=True
    2. b.parallel_safe_with에 a.entry_id 포함 → override=True, safe=True
    3. touched_files 교집합 auto-detect
       - 교집합 없음(disjoint) → safe=True
       - 교집합 있음(overlap) → safe=False + overlap_paths 반환

    Args:
        a: PlanEntry A
        b: PlanEntry B

    Returns:
        ParallelVerdict (parallel_safe + override_applied + overlap_paths + reason)
    """
    # 1. override 검사 (양방향 — A→B 또는 B→A)
    a_overrides_b = b.entry_id in (a.parallel_safe_with or [])
    b_overrides_a = a.entry_id in (b.parallel_safe_with or [])

    if a_overrides_b or b_overrides_a:
        return ParallelVerdict(
            entry_a_id=a.entry_id,
            entry_b_id=b.entry_id,
            parallel_safe=True,
            override_applied=True,
            overlap_paths=[],
            reason=(
                f"override 적용: "
                f"{'A→B' if a_overrides_b else 'B→A'} "
                f"parallel_safe_with 명시"
            ),
        )

    # 2. file-path 교집합 auto-detect
    set_a = set(a.touched_files or [])
    set_b = set(b.touched_files or [])
    overlap = sorted(set_a & set_b)

    if overlap:
        return ParallelVerdict(
            entry_a_id=a.entry_id,
            entry_b_id=b.entry_id,
            parallel_safe=False,
            override_applied=False,
            overlap_paths=overlap,
            reason=(
                f"file-path overlap 검출: {len(overlap)}개 공유 파일 "
                f"(ADR-064 §Trace 4 sequential 의무 — shared_resource)"
            ),
        )

    # 3. disjoint → safe
    return ParallelVerdict(
        entry_a_id=a.entry_id,
        entry_b_id=b.entry_id,
        parallel_safe=True,
        override_applied=False,
        overlap_paths=[],
        reason="file-path disjoint (교집합 없음) → 병렬 안전",
    )


# ─────────────────────── batch 판정 ──────────────────────────────────────────

def check_batch_safety(entries: List[PlanEntry]) -> BatchVerdict:
    """N-entry batch 모든 pair 병렬 판정.

    모든 조합 (i, j) pair 검사 (i < j, 순서 무관 symmetric).

    Args:
        entries: PlanEntry 목록

    Returns:
        BatchVerdict (all_safe + unsafe_pairs + safe_pairs)
        빈 entries → all_safe=True (vacuous truth)
    """
    if not entries:
        return BatchVerdict(all_safe=True, unsafe_pairs=[], safe_pairs=[])

    unsafe_pairs: List[ParallelVerdict] = []
    safe_pairs: List[ParallelVerdict] = []

    n = len(entries)
    for i in range(n):
        for j in range(i + 1, n):
            verdict = check_pair_safety(entries[i], entries[j])
            if verdict.parallel_safe:
                safe_pairs.append(verdict)
            else:
                unsafe_pairs.append(verdict)

    return BatchVerdict(
        all_safe=len(unsafe_pairs) == 0,
        unsafe_pairs=unsafe_pairs,
        safe_pairs=safe_pairs,
    )


# ─────────────────────── CLI entry point ─────────────────────────────────────

if __name__ == "__main__":
    # sanity check self-test (ADR-061 §결정 3 sanity check 3종 중 sample)
    print("parallel_safety.py sanity check:")

    # disjoint pair
    a = PlanEntry(entry_id="A", touched_files=["scripts/a.sh"])
    b = PlanEntry(entry_id="B", touched_files=["scripts/b.sh"])
    v = check_pair_safety(a, b)
    assert v.parallel_safe is True, f"sanity FAIL disjoint: {v}"
    print("  disjoint pair → parallel_safe=True ✓")

    # overlap pair
    c = PlanEntry(entry_id="C", touched_files=["scripts/shared.sh"])
    d = PlanEntry(entry_id="D", touched_files=["scripts/shared.sh"])
    v = check_pair_safety(c, d)
    assert v.parallel_safe is False, f"sanity FAIL overlap: {v}"
    assert "scripts/shared.sh" in v.overlap_paths, f"sanity FAIL overlap_paths: {v}"
    print("  overlap pair → parallel_safe=False ✓")

    # override
    e = PlanEntry(entry_id="E", touched_files=["scripts/shared.sh"], parallel_safe_with=["F"])
    f_entry = PlanEntry(entry_id="F", touched_files=["scripts/shared.sh"])
    v = check_pair_safety(e, f_entry)
    assert v.parallel_safe is True, f"sanity FAIL override: {v}"
    assert v.override_applied is True, f"sanity FAIL override_applied: {v}"
    print("  override pair → parallel_safe=True, override_applied=True ✓")

    # batch
    batch = check_batch_safety([a, b, c])
    # a-b disjoint, a-c and b-c depend on files
    print(f"  batch all_safe={batch.all_safe}, unsafe={len(batch.unsafe_pairs)} ✓")

    print("sanity check PASS")
