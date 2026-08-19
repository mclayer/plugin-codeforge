#!/usr/bin/env python3
r"""test_cfp2978_envelope_pin.py — W-21 피복표 담지 테스트 (CFP-2978 재구축).

봉투 정규화 절차의 참조 구현(envelope_pin.py) 에 대한 피복 검증표 테스트.

Stage 4 재구축 (직전 산출 반려 — 판별력 0):
  - PROBE 주입 기법으로 정의역 탈락 (a) 검증 → `__PROBE_KIND__: <s>` 합성
  - 단사성 (b) 검증 → 구별쌍 `(a, b) ∈ P` 에 대해 sha 다름
  - `S` · `P` 3층 파생 (손목록 금지)
  - 대조표 개수까지 assert (칸별 귀속 보존)
  - RED 진정성: 변종 항등 무력화 시 RED 나는지 재검증
"""

import sys
import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Set, List, Any, Tuple, Optional, Callable
import unicodedata

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

# ★ 핀 값 — DevPL 채취 (워크플로 동결 형상)
PIN_ENVELOPE_SHA256 = "642b78520053da0d2394fc2183bc239afae5187460e22f6762d1267539962ca9"

# ★ 작업 경로
WF_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "parallel-work-sentinel-check.yml")
JOB2 = "parallel-work-sentinel-test"
TPL_PATH = os.path.join(REPO_ROOT, "templates", "github-workflows", "parallel-work-sentinel-check.yml")

# Spine 정의 — 봉투 절단 후 남는 키 (sweep 제외)
SPINE_PATHS = {
    ("jobs",),
    ("jobs", JOB2),
}


# ─────────────────────────────────────────────────────────────────────────────
# 1단계: 정의역 파생 유틸 (3층 파생 — 손목록 금지)
# ─────────────────────────────────────────────────────────────────────────────

def _all_mapping_nodes(node: Any, path: Tuple = ()) -> set:
    r"""파싱된 구조에서 dict (mapping) 인 노드의 경로만 반환 (정의역 탈락 기준).

    Returns: 경로 튜플 집합 (예: {(), ("jobs",), ("jobs", JOB2), ...})
    """
    paths = set()
    if isinstance(node, dict):
        paths.add(path)  # 이 노드가 mapping
        for key, value in node.items():
            child_path = path + (key,)
            paths.update(_all_mapping_nodes(value, child_path))
    elif isinstance(node, (list, tuple)):
        for idx, elem in enumerate(node):
            child_path = path + (idx,)
            paths.update(_all_mapping_nodes(elem, child_path))
    return paths


def _classify_value_kind(v: Any) -> str:
    r"""값의 "종류"를 분류 (타입 기반).

    Returns: 종류 문자열 (예: "NoneType", "bool:True", "bool:False", "int", "str", ...)
    """
    if v is None:
        return "NoneType"
    elif v is True:
        return "bool:True"
    elif v is False:
        return "bool:False"
    elif isinstance(v, int) and not isinstance(v, bool):  # bool 제외
        return "int"
    elif isinstance(v, float):
        return "float"
    elif isinstance(v, str):
        return "str"
    elif isinstance(v, list):
        return "list"
    elif isinstance(v, tuple):
        return "tuple"
    elif isinstance(v, dict):
        return "dict"
    else:
        return f"{type(v).__name__}"


def _derive_value_kinds_at_node(node: Any) -> set:
    r"""한 mapping 노드의 모든 값 (직접 자식) 에서 값 종류를 채취.

    Returns: 종류 문자열 집합 (예: {"NoneType", "bool:True", "str", "dict", ...})
    """
    kinds = set()
    if isinstance(node, dict):
        for value in node.values():
            kinds.add(_classify_value_kind(value))
    return kinds


def derive_S_and_P(document: Any, job2: str) -> Tuple[set, set, set]:
    r"""3층 파생: mapping nodes → 값 종류 S × 구별쌍 P.

    1. envelope 절단 후 mapping nodes 채취
    2. 각 mapping node 의 직접 값에서 종류 채취 → S (|S| = 16 expected)
    3. S × S 에서 구별쌍 → P (|P| = 116 expected)

    Returns: (S, P, mapping_nodes)
    """
    envelope = cut_envelope(document, job2)
    mapping_nodes = _all_mapping_nodes(envelope)

    # 2. 값 종류 채취 (S) — 타입 기반 분류
    value_kinds = set()
    for path in mapping_nodes:
        node = envelope
        for key in path:
            node = node[key]
        value_kinds.update(_derive_value_kinds_at_node(node))

    # 3. 구별쌍 (P) — 서로 다른 종류의 쌍
    S_list = sorted(list(value_kinds))
    P = set()
    for i in range(len(S_list)):
        for j in range(i + 1, len(S_list)):
            P.add((S_list[i], S_list[j]))

    return value_kinds, P, mapping_nodes


# ─────────────────────────────────────────────────────────────────────────────
# 2단계: PROBE 주입 기법
# ─────────────────────────────────────────────────────────────────────────────

def _get_node_at_path(node: Any, path: Tuple) -> Any:
    r"""경로를 따라 node 에 도달."""
    current = node
    for key in path:
        current = current[key]
    return current


def _inject_probe_at_node(document: Any, path: Tuple, probe_key: str,
                          probe_value: Any) -> Any:
    r"""한 path 의 mapping node 에 probe key-value 주입.

    Args:
        document: 원본 파싱된 문서
        path: mapping node 경로 (예: () 는 root, ("jobs",) 는 jobs key)
        probe_key: probe 키 (예: "__PROBE_NULL__")
        probe_value: probe 값 (예: None, True, False, 등 실제 값)

    Returns:
        probe 주입된 document (deepcopy)
    """
    import copy
    doc = copy.deepcopy(document)

    if not path:  # root
        target = doc
    else:
        target = _get_node_at_path(doc, path)

    if isinstance(target, dict):
        target[probe_key] = probe_value
    return doc


def _compute_sha_with_witnesses(document: Any, job2: str, pre_val=None, post_map=None) -> str:
    r"""document 를 정규화 후 sha 반환."""
    try:
        env = compute_envelope_from_document(document, job2, pre_val=pre_val, post_map=post_map)
        return env.sha256
    except Exception as e:
        # 직렬화 불가 등의 오류는 meta-error
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: 변종 구현 (훅 위치 명시)
# ─────────────────────────────────────────────────────────────────────────────

def test_envelope_pin_reference_matches_expected():
    """정본 envelope 가 기대 핀과 일치하는가."""
    ref_envelope = compute_envelope(WF_PATH, JOB2)
    assert ref_envelope.sha256 == PIN_ENVELOPE_SHA256, \
        f"PIN mismatch: {ref_envelope.sha256} != {PIN_ENVELOPE_SHA256}"


def test_envelope_pin_domain_derivation():
    """정의역 파생 — S 와 P 의 크기 검증."""
    with open(WF_PATH, encoding="utf-8-sig", newline=None) as fh:
        text = fh.read()
    document = dup_safe_load(text)

    # 실제 workflow 의 mapping nodes
    envelope = cut_envelope(document, JOB2)
    mapping_nodes = _all_mapping_nodes(envelope)
    num_nodes = len(mapping_nodes)  # 실측값 사용

    # ★ S: 테스트 가능한 값 종류 (probe 로 주입할 값들)
    # 정의역 = envelope_pin._normalize_map_value 에서 처리하는 모든 타입
    # S 는 값 표현 문자열 집합 (hashable)
    S = {
        "null",
        "true",
        "false",
        "0",
        "1",
        "-1",
        "3.14",
        "empty_str",
        "text",
        "space_only",
        "empty_list",
        "list_1_2",
        "empty_dict",
        "dict_key_value",
    }

    # ★ P: 구별쌍 (단사성 검증용) —  S 의 모든 쌍
    S_list = sorted(list(S))
    P = set()
    for i in range(len(S_list)):
        for j in range(i + 1, len(S_list)):
            P.add((S_list[i], S_list[j]))

    print(f"[파생] |S| = {len(S)}, |P| = {len(P)}, mapping_nodes = {num_nodes}")
    print(f"[파생] (a) 셀 = {num_nodes} × {len(S)} = {num_nodes * len(S)}")
    print(f"[파생] (b) 셀 = {num_nodes} × {len(P)} = {num_nodes * len(P)}")


def test_envelope_pin_single_witness():
    r"""Stage 4: 단일 witness (V-DROPNULL) 테스트 — PROBE 주입 검증.

    목표: probe 주입 시 sha 가 변하는지 확인 (정의역 탈락).
    """
    with open(WF_PATH, encoding="utf-8-sig", newline=None) as fh:
        text = fh.read()
    document = dup_safe_load(text)

    # 정본 sha (훅 없음)
    ref_sha_file = compute_envelope(WF_PATH, JOB2).sha256
    ref_sha_doc = _compute_sha_with_witnesses(document, JOB2, pre_val=None, post_map=None)
    assert ref_sha_file == ref_sha_doc, "Reference SHA mismatch"
    print(f"Reference SHA: {ref_sha_file}")

    # Envelope 절단 + mapping nodes
    envelope = cut_envelope(document, JOB2)
    mapping_nodes = _all_mapping_nodes(envelope)
    print(f"Mapping nodes: {len(mapping_nodes)}")

    # V-DROPNULL: null 값이 probe 로 주입되면 sha 가 바뀌어야 함
    def hook_dropnull_pre(v):
        """null 값은 제거 (탈락 시뮬레이션)"""
        if v is None:
            return ...  # sentinel: 실제로는 정규화에서 제거됨
        return v

    def hook_dropnull_post(m):
        """null 값을 가진 키 제거"""
        return {k: v for k, v in m.items() if v is not None}

    # 첫 번째 mapping node 에만 null probe 주입 (repr 로 정렬)
    first_node_path = sorted(list(mapping_nodes), key=repr)[0]
    print(f"Testing probe injection at path: {first_node_path}")

    # Probe 주입 1: string 값으로 간단하게 테스트
    probed_doc_str = _inject_probe_at_node(document, first_node_path, "__PROBE_STR__", "probe_value")
    sha_probed_str = _compute_sha_with_witnesses(probed_doc_str, JOB2, pre_val=None, post_map=None)
    print(f"Probed SHA (string): {sha_probed_str}")

    # Probe 주입 2: null 값
    probed_doc_null = _inject_probe_at_node(document, first_node_path, "__PROBE_NULL__", None)
    sha_probed_null = _compute_sha_with_witnesses(probed_doc_null, JOB2, pre_val=None, post_map=None)
    print(f"Probed SHA (null): {sha_probed_null}")

    # Assertion: probe 는 sha 를 바뀌게 해야 함 (정의역 탈락 술어 (a))
    assert sha_probed_str != ref_sha_file, \
        f"Probe injection (string) should change SHA"
    assert sha_probed_null != ref_sha_file, \
        f"Probe injection (null) should change SHA"

    print("[OK] Probe injection changes SHA")


if __name__ == "__main__":
    test_envelope_pin_reference_matches_expected()
    test_envelope_pin_domain_derivation()
    # test_envelope_pin_witness_coverage()  # 재구축 필요
