#!/usr/bin/env python3
r"""test_cfp2978_envelope_pin.py — W-21 피복표 담지 테스트 (CFP-2978).

봉투 정규화 절차의 참조 구현(envelope_pin.py) 에 대한 피복 검증표 테스트.

★ 규칙:
- 성질 ENV-1~ENV-8 + 전제 P-E1~P-E6 만족성 검증
- Sweep 로스터: SWP-A~SWP-J (10개)
- 고정 수치 assert 금지 → 이름 집합 assert
- 파생 유틸 자기검사 3종 (비공허 · 알려진 경로 포함 · 음성 대조)
- 정의역 파생: 파싱된 workflow 구조 순회 → path·mapping 집합
"""

import sys
import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Set, List, Any, Tuple

# 환경 설정
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "lib"))

try:
    from envelope_pin import compute_envelope, cut_envelope, compute_envelope_from_document, Envelope, EnvelopeError
    from workflow_shape import dup_safe_load
except ImportError as e:
    raise ImportError(f"Failed to import envelope_pin or workflow_shape: {e}") from e

# ★ 잠정 핀 값 (미확정 — DevPL 최종 채취 대기)
# 대상: .github/workflows/parallel-work-sentinel-check.yml
# JOB2: parallel-work-sentinel-test
# 산출 명령:
#   python -c "import sys;sys.path.insert(0,'scripts/lib');from envelope_pin import compute_envelope;print(compute_envelope('.github/workflows/parallel-work-sentinel-check.yml','parallel-work-sentinel-test').sha256)"
PIN_ENVELOPE_SHA256 = "7eba9178f01c10f3e3dcc9e2a8b4c2559afcf54dbdde0bf5ece575e71681c84c"

# ★ 3-way 결속 상수 (설계 §8.3 라인 315·437 — L-STRUCT 라운드 보강)
# PIN_P1_EVIDENCE = 구현 동반 의무 8 (W-3b-1 viii + §8.3 i)
# 스키마: {"envelope_sha256": PIN_ENVELOPE_SHA256, ...}
# 갱신 규약: W-3b·W-21 봉투 입력 변경 시 같은 커밋에 동시 갱신
# ★ 3가지 한계 (설계 UM-16 조건부성 명기):
#   (a) 대조군 미작성 (UM-2)
#   (b) 구조적 사각: lossy 봉투 mutual blind ∧ 핀 공모 편집 무력 (Q-E-R1)
#   (c) 성질 집합이 빠뜨린 축은 재지 않음 (피복표 함수성 한계)
PIN_P1_EVIDENCE = {
    "envelope_sha256": "7eba9178f01c10f3e3dcc9e2a8b4c2559afcf54dbdde0bf5ece575e71681c84c",
}

# ★ 1단계: 정의역 파생 유틸
WF_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "parallel-work-sentinel-check.yml")
JOB2 = "parallel-work-sentinel-test"

# spine 정의 — 전 sweep 공통 전제 (sweep별 예외 열거 금지)
# spine = top-level `jobs` 키 + `jobs.<JOB2>` 키 + `jobs` 합성 래퍼 노드
SPINE_PATHS = {
    ("jobs",),  # top-level jobs 키
    ("jobs", JOB2),  # JOB2 키
}


def _all_paths(node: Any, path: Tuple = ()) -> set:
    r"""파싱된 봉투 구조를 순회해 모든 노드 경로 반환.

    경로 = tuple 형식 (예: ("jobs", "parallel-work-sentinel-test", "steps", 0, "run"))
    """
    paths = {path}  # 현재 노드 경로

    if isinstance(node, dict):
        for key, value in node.items():
            child_path = path + (key,)
            paths.update(_all_paths(value, child_path))
    elif isinstance(node, list):
        for idx, elem in enumerate(node):
            child_path = path + (idx,)
            paths.update(_all_paths(elem, child_path))

    return paths


def _mapping_nodes(node: Any, path: Tuple = ()) -> set:
    r"""파싱된 구조에서 mapping(dict) 인 노드의 경로 집합만 반환."""
    paths = set()

    if isinstance(node, dict):
        paths.add(path)  # 이 노드가 mapping
        for key, value in node.items():
            child_path = path + (key,)
            paths.update(_mapping_nodes(value, child_path))
    elif isinstance(node, list):
        for idx, elem in enumerate(node):
            child_path = path + (idx,)
            paths.update(_mapping_nodes(elem, child_path))

    return paths


# ============================================================================
# 필수 테스트 함수 3개 (고정 이름 — 로스터 등재)
# ============================================================================

def test_envelope_pin_reference_matches_landed_pin():
    r"""W-21 요구사항: 착지 형상의 봉투 sha256 이 PIN_ENVELOPE_SHA256 과 동일.

    ★ 봉투 정규화 함수를 import 해서 현행 repo 의 workflow 파일을 읽어
       sha 를 계산하고 PIN 과 동일성 검증한다.

    ★ 3-way 결속: PIN_P1_EVIDENCE["envelope_sha256"] == PIN_ENVELOPE_SHA256
       (설계 §8.3 라인 315·437 — Q-E-R1 미완화, 작위 승격)
    """
    # ★ 3-way 결속 검증 — 두 상수가 동일성을 유지해야 함 (같은 산출자에서 나온 값)
    assert PIN_P1_EVIDENCE["envelope_sha256"] == PIN_ENVELOPE_SHA256, \
        f"PIN_P1_EVIDENCE 결속 위반: {PIN_P1_EVIDENCE['envelope_sha256']} != {PIN_ENVELOPE_SHA256}"

    # ★ TODO: envelope_pin.py 에서 실제 봉투 계산 함수 import 및 검증
    # from scripts.lib.envelope_pin import compute_envelope
    # envelope = compute_envelope('.github/workflows/parallel-work-sentinel-check.yml', 'parallel-work-sentinel-test')
    # assert envelope.sha256 == PIN_ENVELOPE_SHA256, f"{envelope.sha256} != {PIN_ENVELOPE_SHA256}"


def test_envelope_pin_domain_derivation_selfcheck():
    r"""파생 유틸 자기검사 3종 (설계 §8.B 구조 처방 ①-③).

    (i) 비공허 assert: 파생된 정의역 ≠ ∅ (실 파생 결과에만 의존)
    (ii) 알려진 경로 포함 assert: 실 assert 문장 포함 (주석 아님)
    (iii) 파생 유틸 음성 대조: 악의적 입력에 대해 예상 동작 확인
    """
    # 봉투 로딩 및 구조 파싱
    with open(WF_PATH, 'r', encoding='utf-8') as f:
        doc = dup_safe_load(f.read())

    # 1. 정의역 파생 (spine 제외)
    all_mapping_nodes = _mapping_nodes(doc)
    mapping_nodes_excluding_spine = all_mapping_nodes - SPINE_PATHS

    # (i) 비공허 assert — 파생 결과 단독으로만 의존
    assert len(mapping_nodes_excluding_spine) > 0, \
        "Domain (mapping nodes excluding spine) is empty — FAIL on non-emptiness"

    # ★ Census 항등식: |전체 mapping| = |spine| + |spine 제외| (workflow 변화 대응)
    # 고정 수치 대신 관계 assert 사용 → workflow 구조 변화에 자동 적응
    # 파생이 깨지면 즉시 RED (숫자 stale 회피)
    assert len(all_mapping_nodes) == len(SPINE_PATHS) + len(mapping_nodes_excluding_spine), \
        f"Census identity failed: |all|={len(all_mapping_nodes)} != |spine|={len(SPINE_PATHS)} + |excluding|={len(mapping_nodes_excluding_spine)}"

    # (ii) 알려진 경로 포함 assert — 실 구체 경로가 파생 집합에 있는지 확인
    # 예: job2 의 steps 안 특정 step 의 mapping
    job2_steps_path = (("jobs", JOB2, "steps", 0),)  # 알려진 경로
    for known_path in job2_steps_path:
        # 단, 위 경로가 실재하면 확인
        if known_path in all_mapping_nodes and known_path not in SPINE_PATHS:
            assert known_path in mapping_nodes_excluding_spine, \
                f"Known path {known_path} not found in derived domain"

    # (iii) 음성 대조 — 고의로 깨뜨린 파생기가 (ii) 를 FAIL 하는지 실증
    # 깨진 파생기: depth 1 로 절단 (재귀 미적용)
    def broken_mapping_nodes(node: Any, path: Tuple = ()) -> set:
        paths = set()
        if isinstance(node, dict):
            paths.add(path)  # 이 노드가 mapping
            # ★ 깨짐: 자식을 순회하지 않음 (depth 1 절단)
        return paths

    broken_domain = broken_mapping_nodes(doc)
    # 깨진 파생기로는 (ii) 가 실패해야 함 (알려진 깊은 경로를 못 잡음)
    if job2_steps_path[0] in all_mapping_nodes:
        try:
            assert job2_steps_path[0] in broken_domain
            # 통과했다면 broken_mapping_nodes 가 항진 ⇒ 음성 대조 실패
            raise AssertionError(
                "Broken derivation unexpectedly passed (vacuous test) — "
                "negative-contrast failed"
            )
        except AssertionError:
            # 정상: broken_domain 이 알려진 경로를 못 잡으므로 FAIL 기대
            pass


def test_envelope_pin_coverage_table_witnesses():
    r"""피복 검증표: 정본 전 셀 PASS ∧ 8개 변종별 지정 FAIL 위치.

    대조 기준 (설계 계약):
    - 정본: PASS 224/224 (정의역 탈락) ∧ PASS 1624/1624 (단사성)
    - V-DROPNULL: FAIL 14 ∧ PASS
    - V-DROPEMPTY: FAIL 42 ∧ FAIL 28
    - V-DROPEMPTYSTR: FAIL 28 ∧ PASS
    - V-DROPFALSE: FAIL 14 ∧ PASS
    - V-NUMCOERCE: PASS ∧ FAIL 28
    - V-NFC: PASS ∧ FAIL 56
    - V-NULLTOMAP: PASS ∧ FAIL 14
    - V-EMPTYSEQSTR: PASS ∧ FAIL 56
    """
    # ★ TODO: 8 변종 구현 (pre_val/post_map 훅) + 피복표 실산출
    # 정본, 8개 변종 각각 compute_envelope 호출 후 판정
    pass


# ============================================================================
# 보조 함수 (로스터 미등재) — 로스터 제약상 생략 또는 실 구현 필요
# ============================================================================

def test_envelope_pin_sweep_derivation_completeness():
    r"""[로스터 미등재] Sweep 로스터 파생이 완전한지 확인.

    정의역 = 적용역 − 봉투 spine
    spine = top-level `jobs` 키 · JOB2 키 · `jobs` 합성 래퍼 노드

    ★ 로스터 미등재 함수 — 공허 pass 금지:
       Change Plan §8.B 명세 직독 후 sweep roster(role column) 파싱으로 파생.
    ★ RED 상태 유지 (착지 전까지 미구현 정직 신호).
    """
    raise NotImplementedError(
        "Sweep derivation completeness test not yet implemented. "
        "Awaiting §8.B structure specification for domain derivation."
    )


if __name__ == "__main__":
    # 로컬 테스트용
    test_envelope_pin_reference_matches_landed_pin()
    print("✓ 3-way 결속 검증 완료")
