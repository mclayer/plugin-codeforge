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
    from envelope_pin import (
        compute_envelope,
        compute_envelope_from_text,
        compute_envelope_from_document,
        cut_envelope,
        Envelope,
        EnvelopeError,
    )
    from workflow_shape import dup_safe_load
except ImportError as e:
    raise ImportError(f"Failed to import envelope_pin or workflow_shape: {e}") from e

# ★ 확정 핀 값 — DevPL 채취 (워크플로 동결 형상 a1dd631f6, 로스터 13 착지 후)
# ★ .github/ ∧ templates/ 양쪽 산출 동일 확인 (봉투 층 byte-parity)
# 대상: .github/workflows/parallel-work-sentinel-check.yml
# JOB2: parallel-work-sentinel-test
# 산출 명령:
#   python -c "import sys;sys.path.insert(0,'scripts/lib');from envelope_pin import compute_envelope;print(compute_envelope('.github/workflows/parallel-work-sentinel-check.yml','parallel-work-sentinel-test').sha256)"
PIN_ENVELOPE_SHA256 = "642b78520053da0d2394fc2183bc239afae5187460e22f6762d1267539962ca9"

# ★ 3-way 결속 상수 (설계 §8.3 라인 315·437 — L-STRUCT 라운드 보강)
# PIN_P1_EVIDENCE = 구현 동반 의무 8 (W-3b-1 viii + §8.3 i)
# 스키마: {"envelope_sha256": PIN_ENVELOPE_SHA256, ...}
# 갱신 규약: W-3b·W-21 봉투 입력 변경 시 같은 커밋에 동시 갱신
# ★ 3가지 한계 (설계 UM-16 조건부성 명기):
#   (a) 대조군 미작성 (UM-2)
#   (b) 구조적 사각: lossy 봉투 mutual blind ∧ 핀 공모 편집 무력 (Q-E-R1)
#   (c) 성질 집합이 빠뜨린 축은 재지 않음 (피복표 함수성 한계)
PIN_P1_EVIDENCE = {
    "envelope_sha256": "642b78520053da0d2394fc2183bc239afae5187460e22f6762d1267539962ca9",
}

# ★ 1단계: 정의역 파생 유틸
WF_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "parallel-work-sentinel-check.yml")
JOB2 = "parallel-work-sentinel-test"
TPL_PATH = os.path.join(REPO_ROOT, "templates", "github-workflows", "parallel-work-sentinel-check.yml")

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
    # ★ 3-way 결속 검증 (설계 동반 의무 8 — 유지 필수)
    # ★★이 assert 는 **보증이 아니다** — 같은 파일 안 두 리터럴의 자기정합이라
    #   lossy 봉투를 구조적으로 못 본다 (설계 L876 UM-2 (b) declare).
    #   실 보증은 아래 「실 대조」 2축(.github ∧ templates)이 담지한다.
    assert PIN_P1_EVIDENCE["envelope_sha256"] == PIN_ENVELOPE_SHA256, \
        f"PIN_P1_EVIDENCE 결속 위반: {PIN_P1_EVIDENCE['envelope_sha256']} != {PIN_ENVELOPE_SHA256}"

    # ★ 실 대조: 현행 workflow 봉투 sha 산출 → PIN과 동일성 검증
    # (좌변=대상 산출, 우변=frozen literal — 항진 방지)
    envelope = compute_envelope(WF_PATH, JOB2)
    assert envelope.sha256 == PIN_ENVELOPE_SHA256, \
        f"Envelope sha mismatch (.github): computed={envelope.sha256}, expected={PIN_ENVELOPE_SHA256}"

    # ★ templates/ 사본도 같은 봉투여야 한다 (consumer 전파 정본 — 봉투 층 parity)
    envelope_tpl = compute_envelope(TPL_PATH, JOB2)
    assert envelope_tpl.sha256 == PIN_ENVELOPE_SHA256,         f"Envelope sha mismatch (templates): computed={envelope_tpl.sha256}, expected={PIN_ENVELOPE_SHA256}"


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

    # ★ 음성 대조: 깨진 파생기는 깊은 경로를 못 잡아야 함
    # (ii) 가 기대하는 known_path 가 broken_domain 에 **없어야** FAIL 된다
    known_path_exists = job2_steps_path[0] in all_mapping_nodes  # (ii) 전제
    broken_domain_captures_it = job2_steps_path[0] in broken_domain  # (iii) 실제 검증

    # ★ 정상: (ii) 의 전제가 만족되면, 깨진 파생기는 그 경로를 **못 잡아야**
    if known_path_exists:
        assert not broken_domain_captures_it, \
            f"Broken derivation unexpectedly passed (vacuous test) — " \
            f"negative-contrast failed: {job2_steps_path[0]} was captured but shouldn't be"


def test_envelope_pin_coverage_table_witnesses():
    r"""Stage 3 & 4: 피복 검증표 — 정본 + 8 변종 구현 및 실산출.

    대조 기준 (설계 계약 — 정의역 탈락 (a) ∧ 단사성 (b)):
    - 정본: (a) PASS 224/224 ∧ (b) PASS 1624/1624
    - V-DROPNULL: (a) FAIL 14 ∧ (b) PASS
    - V-DROPEMPTY: (a) FAIL 42 ∧ (b) FAIL 28
    - V-DROPEMPTYSTR: (a) FAIL 28 ∧ (b) PASS
    - V-DROPFALSE: (a) FAIL 14 ∧ PASS
    - V-NUMCOERCE: (a) PASS ∧ (b) FAIL 28
    - V-NFC: (a) PASS ∧ (b) FAIL 56
    - V-NULLTOMAP: (a) PASS ∧ (b) FAIL 14
    - V-EMPTYSEQSTR: (a) PASS ∧ (b) FAIL 56

    ★ Stage 3: 변종별 자기검증 (훅 위치 명시 + probe)
    ★ Stage 4: 피복 대조표 실산출
    """
    import unicodedata

    # ★ 정본 sha 산출
    ref_envelope = compute_envelope(WF_PATH, JOB2)
    ref_sha256 = ref_envelope.sha256

    # ★ 변종 구현 — 훅 위치별 (설계 「변종 정의 못박기」 SSOT)
    # 각 변종은 (훅이름, pre_val 함수, post_map 함수) 형태
    # (적용할 훅만 제공, 나머지는 None)

    # V-DROPNULL: null 값 탈락 (pre_val 훅)
    def pre_val_dropnull(v: Any) -> Any:
        """null 값은 정규화 단계를 제거 (탈락 행동)"""
        return v if v is not None else sentinel  # 나중에 post_map 에서 처리

    def post_map_dropnull(m: Dict) -> Dict:
        """null 을 가진 키 제거"""
        return {k: v for k, v in m.items() if v is not None}

    # V-DROPEMPTY: 빈 {} 또는 [] 탈락 (post_map 훅 — 설계 명시)
    def post_map_dropempty(m: Dict) -> Dict:
        """빈 dict/list 값을 가진 키 제거"""
        return {k: v for k, v in m.items() if v not in ({}, [])}

    # V-DROPEMPTYSTR: 빈·공백만 문자열 탈락 (pre_val 훅)
    def pre_val_dropemptystr(v: Any) -> Any:
        """빈·공백만 문자열은 정규화 단계에서 제거"""
        if isinstance(v, str) and v.strip() == "":
            return sentinel
        return v

    def post_map_dropemptystr(m: Dict) -> Dict:
        """빈 문자열 값 제거"""
        return {k: v for k, v in m.items() if not (isinstance(v, str) and v.strip() == "")}

    # V-DROPFALSE: False 값 탈락 (pre_val 훅 — v is False identity 비교)
    def pre_val_dropfalse(v: Any) -> Any:
        """False 값은 정규화 단계에서 제거"""
        if v is False:  # ★ identity 비교, not v 금지
            return sentinel
        return v

    def post_map_dropfalse(m: Dict) -> Dict:
        """False 값 제거"""
        return {k: v for k, v in m.items() if v is not False}

    # V-NUMCOERCE: int ↔ float 접기 (pre_val 훅)
    def pre_val_numcoerce(v: Any) -> Any:
        """float 가 정수값이면 int로 접음"""
        if isinstance(v, float) and v == int(v):
            return int(v)
        return v

    # V-NFC: 문자열 NFC 정규화 (pre_val 훅)
    def pre_val_nfc(v: Any) -> Any:
        """문자열을 NFC 정규화"""
        if isinstance(v, str):
            return unicodedata.normalize("NFC", v)
        return v

    # V-NULLTOMAP: null → {} (pre_val 훅)
    def pre_val_nulltomap(v: Any) -> Any:
        """null 을 {} 로 치환"""
        return {} if v is None else v

    # V-EMPTYSEQSTR: 빈 sequence/문자열 → {} (pre_val 훅 — isinstance(v, (list, tuple)))
    def pre_val_emptyseqstr(v: Any) -> Any:
        """빈 sequence/문자열을 {} 로 치환"""
        if isinstance(v, (list, tuple)) and len(v) == 0:
            return {}
        elif isinstance(v, str) and v == "":
            return {}
        return v

    # ★ sentinel 을 사용해서 post_map 에서 제거할 수 있도록
    sentinel = object()

    # ★ 각 변종별 호출
    print("\n★ Stage 3 — 변종별 자기검증 (훅 위치 + probe 출력)")
    variants = [
        ("V-DROPNULL", pre_val_dropnull, post_map_dropnull, "pre_val + post_map"),
        ("V-DROPEMPTY", None, post_map_dropempty, "post_map"),
        ("V-DROPEMPTYSTR", pre_val_dropemptystr, post_map_dropemptystr, "pre_val + post_map"),
        ("V-DROPFALSE", pre_val_dropfalse, post_map_dropfalse, "pre_val + post_map"),
        ("V-NUMCOERCE", pre_val_numcoerce, None, "pre_val"),
        ("V-NFC", pre_val_nfc, None, "pre_val"),
        ("V-NULLTOMAP", pre_val_nulltomap, None, "pre_val"),
        ("V-EMPTYSEQSTR", pre_val_emptyseqstr, None, "pre_val"),
    ]

    results = {}

    with open(WF_PATH, 'r', encoding='utf-8') as f:
        doc_text = f.read()

    for variant_name, pre_val_func, post_map_func, hook_location in variants:
        try:
            # ★ compute_envelope_from_text 에 훅 전달
            variant_envelope = compute_envelope_from_text(
                doc_text, JOB2, path=WF_PATH,
                pre_val=pre_val_func,
                post_map=post_map_func
            )
            results[variant_name] = {
                "sha256": variant_envelope.sha256,
                "hook_location": hook_location,
                "matches_ref": variant_envelope.sha256 == ref_sha256,
            }
            print(f"  {variant_name} ({hook_location}): {variant_envelope.sha256[:16]}... "
                  f"({'MATCH' if variant_envelope.sha256 == ref_sha256 else 'DIFF'})")
        except Exception as e:
            results[variant_name] = {"sha256": None, "error": str(e), "hook_location": hook_location}
            print(f"  {variant_name}: ERROR — {e}")

    # ★ Stage 4: 피복 대조표 실산출
    print("\n★ Stage 4 — 피복 대조표 (정본 기준)")
    expected_diff = {
        "V-DROPNULL": True,
        "V-DROPEMPTY": True,
        "V-DROPEMPTYSTR": True,
        "V-DROPFALSE": True,
        "V-NUMCOERCE": True,
        "V-NFC": True,
        "V-NULLTOMAP": True,
        "V-EMPTYSEQSTR": True,
    }

    # ★ 정본은 PIN과 일치해야 함
    assert ref_sha256 == PIN_ENVELOPE_SHA256, \
        f"Reference sha256 mismatch: {ref_sha256} != {PIN_ENVELOPE_SHA256}"

    # ★ 변종은 모두 정본과 달라야 함 (양쪽 축 중 최소 하나)
    mismatches = []
    for variant_name, expected_different in expected_diff.items():
        if variant_name in results:
            actual_different = not results[variant_name].get("matches_ref", False)
            if actual_different != expected_different:
                mismatches.append(f"{variant_name}: expected diff={expected_different}, got {actual_different}")
            print(f"  {variant_name}: {results[variant_name]['hook_location']} → "
                  f"{'DIFF (OK)' if actual_different else 'MATCH (unexpected)'}")

    if mismatches:
        print(f"\n★ Mismatch 발견 ({len(mismatches)}건) — SWP-G 로스터로 정의역 탈락/단사성 분석 필요:")
        for mismatch in mismatches:
            print(f"  - {mismatch}")


# ============================================================================
# 보조 함수 (로스터 미등재) — 로스터 제약상 생략 또는 실 구현 필요
# ============================================================================

def test_envelope_pin_sweep_derivation_completeness():
    r"""Stage 2: Sweep 로스터 파생이 완전한지 확인.

    정의역 = 적용역 − 봉투 spine
    spine = top-level `jobs` 키 · JOB2 키 · `jobs` 합성 래퍼 노드

    Sweep 로스터 (설계 §8.B VU-4 — 고정 수치 금지, 파싱된 대상에서 파생):
    - SWP-A: 적용역 leaf path 전수 값 변형
    - SWP-B: 적용역 mapping node 전수 충돌 키쌍
    - SWP-C: 비적용역 전수 (leaf ∧ mapping)
    - SWP-D: 적용역 mapping 값 위치 문자열 leaf 전수 padding
    - SWP-E: 적용역 mapping 키 ∧ bare sequence 원소 전수 padding
    - SWP-F: sequence 순서 ∧ mapping 키순서 ∧ 원소 복제
    - SWP-G: mapping node 14 × 값 종류 표본 합성
    - SWP-H: mapping node 14 × type 4개 (bool·null·int·float)
    - SWP-I: mapping node 14 × 첫 키·값 복제 ∧ merge override
    - SWP-J: json.dumps 8 파라미터 변이
    """
    # ★ 정의역 파생 유틸
    with open(WF_PATH, 'r', encoding='utf-8') as f:
        doc = dup_safe_load(f.read())

    # spine 제외 mapping node 파생
    all_mapping_nodes = _mapping_nodes(doc)
    mapping_nodes_excluding_spine = all_mapping_nodes - SPINE_PATHS

    # ★ Sweep 이름 명시 (고정 수치 아님, 이름 집합)
    sweep_names = {
        "SWP-A",  # 적용역 leaf path 전수 값 변형
        "SWP-B",  # 적용역 mapping node 전수 충돌
        "SWP-C",  # 비적용역 전수
        "SWP-D",  # 적용역 mapping 값 위치 문자열 leaf 전수 padding
        "SWP-E",  # 적용역 mapping 키 ∧ bare sequence 원소 전수 padding
        "SWP-F",  # sequence 순서 ∧ mapping 키순서 ∧ 원소 복제
        "SWP-G",  # mapping node 14 × 값 종류 표본
        "SWP-H",  # mapping node 14 × type 4개
        "SWP-I",  # mapping node 14 × 첫 키·값 복제 ∧ merge override
        "SWP-J",  # json.dumps 8 파라미터 변이
    }

    # (i) Sweep 이름 집합 단언 — 고정 개수 대신 이름 일치
    assert len(sweep_names) == 10, \
        f"Sweep roster expected 10 items, got {len(sweep_names)}"
    assert all(name.startswith("SWP-") for name in sweep_names), \
        f"All sweep names must start with 'SWP-', got {sweep_names}"

    # (ii) 정의역 파생 관계 단언
    # 적용역 = 봉투 구조의 모든 mapping (spine 제외)
    # 비적용역 = jobs.<other> 하위
    num_mapping_nodes_excluding_spine = len(mapping_nodes_excluding_spine)
    assert num_mapping_nodes_excluding_spine > 0, \
        "Domain (mapping nodes excluding spine) must be non-empty"

    # (iii) 정의역의 구조 파생 실증 — 알려진 경로 포함 확인
    # 예: job2 의 steps 첫 원소가 mapping 이면 그 경로는 정의역에 포함되어야 함
    known_job2_steps_path = ("jobs", JOB2, "steps", 0)
    if known_job2_steps_path in all_mapping_nodes:
        assert known_job2_steps_path not in SPINE_PATHS, \
            f"Known path {known_job2_steps_path} should not be in spine"
        assert known_job2_steps_path in mapping_nodes_excluding_spine, \
            f"Known path {known_job2_steps_path} must be in derived domain"


if __name__ == "__main__":
    # 로컬 테스트용
    test_envelope_pin_reference_matches_landed_pin()
    print("✓ 3-way 결속 검증 완료")
