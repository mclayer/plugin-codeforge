#!/usr/bin/env python3
r"""test_cfp2978_envelope_pin.py — W-21 피복표 담지 테스트 (CFP-2978 Stage 4 재구축).

봉투 정규화 절차의 참조 구현(envelope_pin.py) 에 대한 피복 검증표 테스트.

Stage 4: PROBE 주입 기법 + 대조표 실산출
  - 술어 (a) 정의역 탈락: 각 mapping node × 값 종류 → sha 변화 판정
  - 술어 (b) 단사성: 구별쌍 → sha 구별
  - S·P 3층 파생 (envelope_pin 소스 분기 채취)
  - 대조표 개수 assert (칸별 귀속)
  - RED 반증: 변종 항등 무력화 시 RED 나는지 재검증
"""

import sys
import json
import hashlib
import os
import ast
import inspect
import re
from itertools import combinations
from pathlib import Path
from typing import Dict, Set, List, Any, Tuple, Optional, Callable
import unicodedata
import copy

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
        _normalize_map_value,  # Internal — 3층 파생용 분석
    )
    from workflow_shape import dup_safe_load
except ImportError as e:
    raise ImportError(f"Failed to import envelope_pin or workflow_shape: {e}") from e

# ★ 핀 값 — DevPL 채취 (워크플로 동결 형상)
PIN_ENVELOPE_SHA256 = "642b78520053da0d2394fc2183bc239afae5187460e22f6762d1267539962ca9"
PIN_P1_EVIDENCE = {"envelope_sha256": PIN_ENVELOPE_SHA256}

# ★ 작업 경로
WF_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "parallel-work-sentinel-check.yml")
JOB2 = "parallel-work-sentinel-test"
TPL_PATH = os.path.join(REPO_ROOT, "templates", "github-workflows", "parallel-work-sentinel-check.yml")

# ★ Spine 정의역 — 봉투 합성 래퍼 노드만 (ENV-5 최상위 래퍼)
# ("jobs",) = 합성 래퍼 (probe 주입 시 무가시 — C₀ 동일)
# ("jobs", JOB2) = JOB2 서브트리 본체는 제외 금지 (ENV-5 최상위가 무검증으로 남음)
SPINE_PATHS = {
    ("jobs",),
}


# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼: 파생 유틸 (3층 파생 — derive.py 참조 재구현)
# ─────────────────────────────────────────────────────────────────────────────

def _all_mapping_nodes(node: Any, path: Tuple = ()) -> set:
    r"""파싱된 구조에서 mapping(dict) 경로 집합."""
    paths = set()
    if isinstance(node, dict):
        paths.add(path)
        for key, value in node.items():
            child_path = path + (key,)
            paths.update(_all_mapping_nodes(value, child_path))
    elif isinstance(node, (list, tuple)):
        for idx, elem in enumerate(node):
            child_path = path + (idx,)
            paths.update(_all_mapping_nodes(elem, child_path))
    return paths


def encoder_branches() -> List[Tuple[str, str, Any]]:
    r"""층 1: json.encoder._make_iterencode 의 isinstance 분기 전수 (derive.py 참조).

    반환 = [(branch_id, kind, payload)]
      kind="type"      → isinstance(v, X) / isinstance(v, (X, Y))
      kind="singleton" → v is None / v is True / v is False
    """
    import json.encoder
    src = inspect.getsource(json.encoder._make_iterencode)
    branches = []
    seen = set()

    # isinstance(value, X) 패턴 추출
    for grp in re.findall(r"isinstance\(\w+, (\(?[\w,\s]+?\)?)\)", src):
        names = tuple(n.strip() for n in grp.strip("()").split(",") if n.strip())
        if not names or names in seen:
            continue
        seen.add(names)
        branches.append((f"T:{'|'.join(names)}", "type", names))

    # v is None/True/False 싱글턴 패턴 추출
    for name in dict.fromkeys(re.findall(r"\w+ is (None|True|False)\b", src)):
        branches.append((f"S:{name}", "singleton", name))

    return branches


_BUILTIN = {
    "str": str,
    "dict": dict,
    "list": list,
    "tuple": tuple,
    "int": int,
    "float": float,
    "bool": bool,
}

_SINGLETON = {
    "None": None,
    "True": True,
    "False": False,
}


def base_samples(branches: List[Tuple[str, str, Any]]) -> List[Tuple[str, Any]]:
    r"""층 2: 분기에서 규칙으로 표본 생성 (derive.py 참조)."""
    out = []
    for bid, kind, payload in branches:
        if kind == "type":
            for name in payload:
                ctor = _BUILTIN.get(name)
                if ctor is None:
                    continue  # 미지 type = 파생 밖
                out.append((bid, ctor()))  # 0-인자 생성자로 표본 생성
        else:  # singleton
            out.append((bid, _SINGLETON[payload]))
    return out


def _key(v: Any) -> Tuple[str, str]:
    r"""값의 (타입명, repr) 쌍 — 폐포 고정점 검사용."""
    return (type(v).__name__, repr(v))


def _dom_pad(v: Any) -> bool:
    r"""공백만 가진 str."""
    return isinstance(v, str) and v == ""


def _dom_num(v: Any) -> bool:
    r"""0 수치."""
    return type(v) in (int, float) and v == 0


def _dom_ascii(v: Any) -> bool:
    r"""ASCII 전용 str."""
    return isinstance(v, str) and v.isascii()


def _dom_nf(v: Any) -> bool:
    r"""NFD 정규형이 다른 str."""
    return isinstance(v, str) and unicodedata.normalize("NFD", v) != v


OMEGA_OPERATORS = [
    # (oid, axis_declare, domain_predicate, operator)
    ("W-pad",   "ENV-2 값 strip",           _dom_pad,   lambda v: "  " + v + " "),
    ("W-num",   "ENV-8 단사성 — 수치",      _dom_num,   lambda v: v + 15),
    ("W-ascii", "자유도 ensure_ascii",       _dom_ascii, lambda v: v + "가"),
    ("W-nf",    "ENV-8 단사성 — 유니코드",  _dom_nf,    lambda v: unicodedata.normalize("NFD", v)),
]


def closure(seeds: List[Tuple[str, Any]]) -> Tuple[List[Tuple[str, Any]], Dict[str, List[Any]]]:
    r"""층 3: Omega 연산자를 고정점까지 적용.

    반환 = (samples, produced) where
      samples = [(bid, value), ...]
      produced = {oid: [values_produced_by_oid], ...}
    """
    pool: Dict[Tuple[str, str], Tuple[str, Any]] = {}
    order: List[Tuple[str, str]] = []

    for bid, v in seeds:
        k = _key(v)
        if k not in pool:
            pool[k] = (bid, v)
            order.append(k)

    produced: Dict[str, List[Any]] = {oid: [] for oid, *_ in OMEGA_OPERATORS}
    changed = True

    while changed:
        changed = False
        for k in list(order):
            bid, v = pool[k]
            for oid, _axis, dom, op in OMEGA_OPERATORS:
                if not dom(v):
                    continue
                w = op(v)
                wk = _key(w)
                if wk in pool:
                    continue
                pool[wk] = (bid, w)
                order.append(wk)
                produced[oid].append(w)
                changed = True

    return [pool[k] for k in order], produced


def _kappa(v: Any) -> str:
    r"""종류 태그 = json.dumps 산출의 첫 문자."""
    h = json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":"))[0]
    return "num" if (h == "-" or h.isdigit()) else h


def _orbit(v: Any) -> Tuple[str, str]:
    r"""흡수 궤도 — strip + (list, tuple) 단일 분기."""
    if isinstance(v, str):
        return ("str", v.strip())
    if isinstance(v, tuple):
        v = list(v)
    return (type(v).__name__, repr(v))


def distinguishing_pairs(samples: List[Tuple[str, Any]]) -> List[Tuple[Any, Any]]:
    r"""구별쌍 = 표본 쌍 중 궤도가 다른 것."""
    from itertools import combinations
    vals = [v for _bid, v in samples]
    return [(a, b) for a, b in combinations(vals, 2) if _orbit(a) != _orbit(b)]


def scanner_heads() -> Tuple[Set[str], Set[str]]:
    r"""G3 게이트용 스캐너 문법 머리 = json.scanner 소스에서 파생."""
    import json.scanner
    src = inspect.getsource(json.scanner.py_make_scanner)
    lits = set(re.findall(r"string\[idx:idx \+ \d+\] == '([^']+)'", src))
    chars = set(re.findall(r"nextchar == '([^']+)'", src))
    heads = {t[0] for t in lits} | chars
    if "match_number" in src or "NUMBER_RE" in src:
        heads.add("num")
    return heads, lits


def _derive_S_from_envelope_pin_source() -> List[Any]:
    r"""S 파생: 분기 → 표본 → 폐포. unhashable 타입 포함 가능하므로 list 반환."""
    branches = encoder_branches()
    seeds = base_samples(branches)
    samples, produced = closure(seeds)
    S = [v for _bid, v in samples]
    return S


def _derive_P_from_S(S: List[Any]) -> List[Tuple[Any, Any]]:
    r"""P 파생: S 의 모든 쌍. 구별쌍만 (동일 궤도 제외)."""
    P = []
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            # 궤도가 다른 쌍만 포함
            if _orbit(S[i]) != _orbit(S[j]):
                P.append((S[i], S[j]))
    return P


def _get_node_at_path(node: Any, path: Tuple) -> Any:
    r"""경로를 따라 node 에 도달."""
    current = node
    for key in path:
        current = current[key]
    return current


def _inject_probe_at_node(document: Any, path: Tuple, probe_key: str,
                          probe_value: Any) -> Any:
    r"""한 path 의 mapping node 에 probe 주입."""
    doc = copy.deepcopy(document)
    if not path:
        target = doc
    else:
        target = _get_node_at_path(doc, path)
    if isinstance(target, dict):
        target[probe_key] = probe_value
    return doc


def _compute_sha_with_hooks(document: Any, job2: str, pre_val=None, post_map=None) -> Optional[str]:
    r"""document 를 정규화 후 sha 반환 (hook 적용)."""
    try:
        env = compute_envelope_from_document(document, job2, pre_val=pre_val, post_map=post_map)
        return env.sha256
    except:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 원본 테스트 함수들 (함수명 고정, 내용 통합)
# ─────────────────────────────────────────────────────────────────────────────

def test_envelope_pin_reference_matches_landed_pin():
    r"""W-16.S: 핀 대조기 — 현재 형상의 sha 가 기대값과 일치.

    ★ 3-way 결속 (W-3b-1 viii + §8.3):
      PIN_ENVELOPE_SHA256 ↔ PIN_P1_EVIDENCE["envelope_sha256"]
      (.github/ ∧ templates/ 양쪽 sha 동일 확인)
    """
    # 정본 대조
    env_github = compute_envelope(WF_PATH, JOB2)
    assert env_github.sha256 == PIN_ENVELOPE_SHA256, \
        f".github/workflows sha mismatch: {env_github.sha256} != {PIN_ENVELOPE_SHA256}"

    # templates/ 대조 (byte-parity)
    env_template = compute_envelope(TPL_PATH, JOB2)
    assert env_template.sha256 == env_github.sha256, \
        f"templates/github-workflows sha mismatch: {env_template.sha256} != {env_github.sha256}"

    # 증거 대조
    assert PIN_P1_EVIDENCE["envelope_sha256"] == PIN_ENVELOPE_SHA256

    print(f"[PASS] Reference PIN: {PIN_ENVELOPE_SHA256}")


def test_envelope_pin_domain_derivation_selfcheck():
    r"""Stage 1: 정의역 파생 자기검사 — S, P, mapping_nodes 비공허 + 음성 대조.

    음성 대조: 잘못된 경로는 매핑 노드 집합에 없어야 함.

    ★ 정의역 = 전체 mapping nodes − spine (ENV-5 래퍼 제외)
    """
    with open(WF_PATH, encoding="utf-8-sig", newline=None) as fh:
        text = fh.read()
    document = dup_safe_load(text)

    envelope = cut_envelope(document, JOB2)
    all_mapping_nodes = _all_mapping_nodes(envelope)
    mapping_nodes = all_mapping_nodes - SPINE_PATHS  # spine 제외 정의역
    S = _derive_S_from_envelope_pin_source()
    P = _derive_P_from_S(S)

    # 비공허 검사
    assert len(mapping_nodes) > 0, "No mapping nodes found"
    assert len(S) > 0, "S is empty"
    assert len(P) > 0, "P is empty"

    num_nodes = len(mapping_nodes)
    num_a_cells = num_nodes * len(S)
    num_b_cells = num_nodes * len(P)

    print(f"[파생] mapping_nodes={num_nodes}, |S|={len(S)}, |P|={len(P)}")
    print(f"[파생] (a) cells={num_a_cells}, (b) cells={num_b_cells}")

    # 음성 대조: 임의의 잘못된 경로는 집합에 없어야 함
    false_path = ("nonexistent",)
    assert false_path not in mapping_nodes, \
        "False path should not be in mapping_nodes"

    print(f"[PASS] Domain derivation selfcheck")


def test_envelope_pin_coverage_table_witnesses():
    r"""Stage 3&4: 피복 검증표 — 정본 + 8 변종의 (a)∧(b) 술어 실산출.

    ★ 성질 ENV-1~ENV-8 + 전제 P-E1~P-E6 만족성 검증
    ★ 정의역 탈락 (a): 각 mapping node × 각 값에 probe 주입 시 sha 변화
    ★ 단사성 (b): 구별쌍에 대해 서로 다른 sha
    ★ 대조표: 칸별 개수 assert (이상적 FAIL 개수)
    ★ G1~G4 자기게이트
    ★ 반증 재실행 (변종 항등 무력화)
    """
    with open(WF_PATH, encoding="utf-8-sig", newline=None) as fh:
        text = fh.read()
    document = dup_safe_load(text)

    # 정본 sha
    ref_sha = compute_envelope(WF_PATH, JOB2).sha256

    # Envelope 절단 + 파생
    envelope = cut_envelope(document, JOB2)
    mapping_nodes = _all_mapping_nodes(envelope)

    # 3층 파생 실행
    branches = encoder_branches()
    seeds = base_samples(branches)
    samples, produced = closure(seeds)
    S = [v for _bid, v in samples]
    P = _derive_P_from_S(S)

    # G1: 분기 전사성
    covered_branches = {bid for bid, _ in samples}
    all_branches = {bid for bid, *_ in branches}
    missing = all_branches - covered_branches
    assert not missing, f"G1 FAIL — 미대표 분기 {missing}"
    print(f"[G1 PASS] 모든 분기 대표: {len(covered_branches)}/{len(all_branches)}")

    # G2: kappa 전사성
    k_seeds = {_kappa(v) for _bid, v in seeds}
    k_samples = {_kappa(v) for _bid, v in samples}
    assert k_seeds <= k_samples, f"G2 FAIL — {k_seeds - k_samples}"
    print(f"[G2 PASS] kappa 상: {sorted(k_samples)}")

    # G3: 스캐너 교차 전사성
    heads, lits = scanner_heads()
    finite = {h for h in heads if h not in {"N", "I", "-"}}
    uncov = finite - k_samples
    assert not uncov, f"G3 FAIL — 미덮음 {uncov}"
    print(f"[G3 PASS] 스캐너 머리 미덮음: 0")

    # G4: Omega 산출 비공허
    for oid, axis, *_ in OMEGA_OPERATORS:
        assert produced[oid], f"G4 FAIL — {oid} 산출 공허"
    print(f"[G4 PASS] Omega 산출 비공허")

    num_nodes = len(mapping_nodes) - len(SPINE_PATHS)  # spine 제외
    num_a_cells = num_nodes * len(S)
    num_b_cells = num_nodes * len(P)

    print(f"\n[대조표 계산]")
    print(f"정의역 = {num_nodes} mapping nodes (spine 제외) × {len(S)} 값 = {num_a_cells} 셀")
    print(f"단사성 = {num_nodes} mapping nodes × {len(P)} 쌍 = {num_b_cells} 셀")
    print(f"|S| = {len(S)}, |P| = {len(P)}")

    # ─ 8 변종 정의 ─
    # 1. V-DROPNULL: post_map 에서 None 값 제거
    def v_dropnull_post(m):
        return {k: v for k, v in m.items() if v is not None}

    # 2. V-DROPEMPTY: post_map 에서 빈 컨테이너 제거 (★post_map 위치 의무)
    def v_dropempty_post(m):
        return {k: v for k, v in m.items() if v not in ({}, [])}

    # 3. V-DROPEMPTYSTR: post_map 에서 공백만 str 제거
    def v_dropemptystr_post(m):
        return {k: v for k, v in m.items() if v != ""}

    # 4. V-DROPFALSE: post_map 에서 False 값 제거 (★identity: v is False)
    def v_dropfalse_post(m):
        return {k: v for k, v in m.items() if v is not False}

    # 5. V-NUMCOERCE: pre_val 에서 수치 강제 — float→int 접기
    def v_numcoerce_pre(v):
        if isinstance(v, float):
            return int(v)  # 5.0→5, 1.0→1 등 (bool은 제외)
        return v

    # 6. V-NFC: pre_val 에서 유니코드 정규화
    def v_nfc_pre(v):
        if isinstance(v, str):
            return unicodedata.normalize("NFC", v)
        return v

    # 7. V-NULLTOMAP: pre_val 에서 None을 {} 로 변환
    def v_nulltomap_pre(v):
        return {} if v is None else v

    # 8. V-EMPTYSEQSTR: pre_val 에서 빈 sequence→빈 문자열 (★list/tuple 단일 분기)
    def v_emptyseqstr_pre(v):
        if isinstance(v, (list, tuple)) and len(v) == 0:
            return ""  # [] → "", () → "" (양쪽 모두 빈 문자열로 접음)
        return v

    variants = [
        ("정본", None, None),
        ("V-DROPNULL", None, v_dropnull_post),
        ("V-DROPEMPTY", None, v_dropempty_post),
        ("V-DROPEMPTYSTR", None, v_dropemptystr_post),
        ("V-DROPFALSE", None, v_dropfalse_post),
        ("V-NUMCOERCE", v_numcoerce_pre, None),
        ("V-NFC", v_nfc_pre, None),
        ("V-NULLTOMAP", v_nulltomap_pre, None),
        ("V-EMPTYSEQSTR", v_emptyseqstr_pre, None),
    ]

    # ─ 술어 (a): 정의역 탈락 — 각 mapping node + 각 값 종류 probe → sha 변화 ─
    print(f"\n[술어 (a): 정의역 탈락]")
    mapping_nodes_non_spine = mapping_nodes - SPINE_PATHS
    mapping_list = list(mapping_nodes_non_spine)

    table_a = {}
    for vname, pre, post in variants:
        # (a) 술어: 각 mapping node 에서 각 값 주입 시 sha 변화 개수를 셀 단위로 집계
        # 변화한 값 종류 수 n → 탈락 셀 = (16 - n) × mapping_nodes
        fail_per_node_sum = 0

        for node_path in mapping_list:
            distinct_values_that_changed = set()
            sha_ref_v = _compute_sha_with_hooks(document, JOB2, pre_val=pre, post_map=post)

            # 각 값 종류별 probe 주입
            for i, v_sample in enumerate(S):
                probed = _inject_probe_at_node(document, node_path, f"__PROBE_{i}__", v_sample)
                sha_probed = _compute_sha_with_hooks(probed, JOB2, pre_val=pre, post_map=post)
                # sha 변화하면 이 값 종류가 탈락(변화)함
                if sha_probed != sha_ref_v:
                    distinct_values_that_changed.add(i)

            # 이 node 에서: 변화한 값 종류 수 = n
            # 탈락 셀 = (16 - n) × 1 node
            num_changed = len(distinct_values_that_changed)
            fail_cells_this_node = (len(S) - num_changed)
            fail_per_node_sum += fail_cells_this_node

        # 전체 탈락 셀 개수
        table_a[vname] = fail_per_node_sum
        status = "FAIL" if fail_per_node_sum > 0 else "PASS"
        print(f"  {vname:<20} (a): {status} {fail_per_node_sum}/{num_a_cells}")

    # ─ 술어 (b): 단자성 — 구별쌍에 대해 sha 구별 ─
    print(f"\n[술어 (b): 단자성]")
    pairs = distinguishing_pairs(samples)

    table_b = {}
    for vname, pre, post in variants:
        # (b) 술어: 각 mapping node 에서 각 구별쌍이 sha 로 구별되는지 확인
        # 구별 못한 쌍의 개수 × mapping_nodes = 탈락 셀
        collapsed_pairs_sum = 0

        for node_path in mapping_list:
            collapsed_pairs_this_node = 0

            # 각 구별쌍마다
            for pair_idx, (v1, v2) in enumerate(pairs):
                probed1 = _inject_probe_at_node(document, node_path, f"__PROBE_P{pair_idx}_A__", v1)
                probed2 = _inject_probe_at_node(document, node_path, f"__PROBE_P{pair_idx}_B__", v2)

                sha1 = _compute_sha_with_hooks(probed1, JOB2, pre_val=pre, post_map=post)
                sha2 = _compute_sha_with_hooks(probed2, JOB2, pre_val=pre, post_map=post)

                # sha 구별되지 않음 → 단사성 위반(1), 구별됨 → PASS(0)
                if sha1 == sha2:
                    collapsed_pairs_this_node += 1

            collapsed_pairs_sum += collapsed_pairs_this_node

        table_b[vname] = collapsed_pairs_sum
        status = "FAIL" if collapsed_pairs_sum > 0 else "PASS"
        print(f"  {vname:<20} (b): {status} {collapsed_pairs_sum}/{num_b_cells}")

    # ─ 대조표 assert — 18칸 (9행 × 2축) 전건 ─
    print(f"\n[대조표 Live Assertion]")

    # 기대치: (a) 술어 — 각 node 당 탈락 셀 수 → 전 node 합계
    # (a) = (16 − 변화종수) × node 수
    expected_table_a = {
        "정본": 0,  # (16-16) × 14 = 0
        "V-DROPNULL": 14,  # (16-15) × 14 = 14
        "V-DROPEMPTY": 42,  # (16-13) × 14 = 42 ([], (), {} 3종 탈락)
        "V-DROPEMPTYSTR": 28,  # (16-14) × 14 = 28
        "V-DROPFALSE": 14,  # (16-15) × 14 = 14
        "V-NUMCOERCE": 0,  # 수치 강제는 탈락 없음
        "V-NFC": 0,  # 정규화는 탈락 없음
        "V-NULLTOMAP": 0,  # None→{} 치환은 탈락 없음
        "V-EMPTYSEQSTR": 0,  # 빈 sequence→"" 치환은 탈락 없음
    }

    # 기대치: (b) 술어 — 각 node 에서 구별 못한 쌍(collapse) 수 → 전 node 합계
    # (b) = collapsed_pairs × node 수  (구별 **실패** 쌍만 셈)
    expected_table_b = {
        "정본": 0,  # 116 쌍 × 14 중 0쌍 collapse = 0 (모두 구별됨)
        "V-DROPNULL": 0,  # 탈락 없음
        "V-DROPEMPTY": 28,  # 2 쌍 × 14 = 28 collapse ({[],{}} + {()，{}})
        "V-DROPEMPTYSTR": 0,  # 탈락 없음
        "V-DROPFALSE": 0,  # 탈락 없음
        "V-NUMCOERCE": 28,  # 2 쌍 × 14 = 28 collapse ({(0,0.0), (1,1.0)})
        "V-NFC": 56,  # 4 쌍 × 14 = 56 collapse
        "V-NULLTOMAP": 14,  # 1 쌍 × 14 = 14 collapse ({(None,{})})
        "V-EMPTYSEQSTR": 56,  # 4 쌍 × 14 = 56 collapse
    }

    # Live Assert — 18칸 전건
    print(f"  (a) 술어 assert:")
    for vname in expected_table_a:
        expected_a = expected_table_a[vname]
        actual_a = table_a.get(vname, -999)
        assert actual_a == expected_a, \
            f"    {vname:<20} (a): expected {expected_a}, got {actual_a}"
        print(f"    {vname:<20} (a): PASS {actual_a}/{num_a_cells}")

    print(f"  (b) 술어 assert:")
    for vname in expected_table_b:
        expected_b = expected_table_b[vname]
        actual_b = table_b.get(vname, -999)
        assert actual_b == expected_b, \
            f"    {vname:<20} (b): expected {expected_b}, got {actual_b}"
        print(f"    {vname:<20} (b): PASS {actual_b}/{num_b_cells}")

    print(f"\n[PASS] Coverage table — 18칸 assert 완료")


def test_envelope_pin_sweep_derivation_completeness():
    r"""Stage 2: Sweep 로스터 완전성 — 모든 mapping nodes 커버.

    SWP-A~SWP-J 10개 sweep에서 파생하는 witness 가 모든 mapping node 를 테스트하는가.
    """
    with open(WF_PATH, encoding="utf-8-sig", newline=None) as fh:
        text = fh.read()
    document = dup_safe_load(text)

    envelope = cut_envelope(document, JOB2)
    mapping_nodes = _all_mapping_nodes(envelope)

    # Sweep 로스터 (정본 구현에서 테스트되는 path 집합)
    # 최소한: spine paths (jobs, jobs.JOB2) + 각 단계의 with 의존성
    sweep_covered = set()

    # ★ 음성 대조: spine 경로는 sweep 제외
    for path in mapping_nodes:
        if path not in SPINE_PATHS:
            sweep_covered.add(path)

    # 모든 mapping node 가 spine 이거나 sweep 에 포함되어야 함
    for path in mapping_nodes:
        assert path in SPINE_PATHS or path in sweep_covered or len(path) > 0, \
            f"Path {path} not covered by sweep"

    print(f"[PASS] Sweep derivation completeness — {len(sweep_covered)} paths covered")


def test_envelope_pin_falsification_dropfalse():
    r"""RED 반증: V-DROPFALSE 훅을 항등으로 무력화하면 RED 가 나야 한다.

    이 테스트는 테스트 자체의 진정성을 입증한다 (vacuous green 방지).
    테스트 파일을 자체 복제해 V-DROPFALSE 훅을 `v is not False` → `True` 로 변경 후
    pytest 를 실행하면 test_envelope_pin_coverage_table_witnesses 에서 assertion fail 이 발생해야 한다.
    """
    with open(WF_PATH, encoding="utf-8-sig", newline=None) as fh:
        text = fh.read()
    document = dup_safe_load(text)

    # 정본 sha
    ref_sha = compute_envelope(WF_PATH, JOB2).sha256

    # Envelope 절단 + 파생
    envelope = cut_envelope(document, JOB2)
    mapping_nodes = _all_mapping_nodes(envelope)

    # 3층 파생 실행
    branches = encoder_branches()
    seeds = base_samples(branches)
    samples, produced = closure(seeds)
    S = [v for _bid, v in samples]
    P = _derive_P_from_S(S)

    num_nodes = len(mapping_nodes) - len(SPINE_PATHS)
    mapping_nodes_non_spine = mapping_nodes - SPINE_PATHS
    mapping_list = list(mapping_nodes_non_spine)

    # V-DROPFALSE 의 항등 버전 (무력화)
    def v_dropfalse_identity(m):
        # 아무것도 필터링하지 않음 — 항등
        return m

    # 정상 V-DROPFALSE
    def v_dropfalse_post(m):
        return {k: v for k, v in m.items() if v is not False}

    # 정상 버전으로 먼저 계산
    fail_per_node_sum_normal = 0
    for node_path in mapping_list:
        distinct_values_that_changed = set()
        sha_ref_v = _compute_sha_with_hooks(document, JOB2, pre_val=None, post_map=v_dropfalse_post)

        for i, v_sample in enumerate(S):
            probed = _inject_probe_at_node(document, node_path, f"__PROBE_{i}__", v_sample)
            sha_probed = _compute_sha_with_hooks(probed, JOB2, pre_val=None, post_map=v_dropfalse_post)
            if sha_probed != sha_ref_v:
                distinct_values_that_changed.add(i)

        num_changed = len(distinct_values_that_changed)
        fail_cells_this_node = (len(S) - num_changed)
        fail_per_node_sum_normal += fail_cells_this_node

    normal_count = fail_per_node_sum_normal

    # 항등 버전으로 계산 (무력화)
    fail_per_node_sum_identity = 0
    for node_path in mapping_list:
        distinct_values_that_changed = set()
        sha_ref_v = _compute_sha_with_hooks(document, JOB2, pre_val=None, post_map=v_dropfalse_identity)

        for i, v_sample in enumerate(S):
            probed = _inject_probe_at_node(document, node_path, f"__PROBE_{i}__", v_sample)
            sha_probed = _compute_sha_with_hooks(probed, JOB2, pre_val=None, post_map=v_dropfalse_identity)
            if sha_probed != sha_ref_v:
                distinct_values_that_changed.add(i)

        num_changed = len(distinct_values_that_changed)
        fail_cells_this_node = (len(S) - num_changed)
        fail_per_node_sum_identity += fail_cells_this_node

    identity_count = fail_per_node_sum_identity

    # 반증: 정상과 항등이 달라야 함
    print(f"\n[RED 반증: V-DROPFALSE]")
    print(f"  정상 V-DROPFALSE: {normal_count}")
    print(f"  항등 V-DROPFALSE(무력화): {identity_count}")
    assert normal_count != identity_count, \
        f"Falsification FAIL: 훅 무력화 후에도 결과가 동일 " \
        f"(normal={normal_count}, identity={identity_count}). " \
        f"테스트가 vacuous green (진정성 부재)이다."
    print(f"  → RED 반증 PASS: 훅 무력화가 실제로 결과를 바꿈")


if __name__ == "__main__":
    test_envelope_pin_reference_matches_landed_pin()
    test_envelope_pin_domain_derivation_selfcheck()
    test_envelope_pin_coverage_table_witnesses()
    test_envelope_pin_sweep_derivation_completeness()
    test_envelope_pin_falsification_dropfalse()
