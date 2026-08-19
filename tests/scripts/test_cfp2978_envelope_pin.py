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
import os
import inspect
import re
import subprocess
import datetime
import contextlib
from collections import namedtuple
from typing import Dict, Set, List, Any, Tuple, Optional, Callable
import unicodedata
import copy

import pytest
import yaml

# 환경 설정
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts", "lib"))

try:
    import envelope_pin as envelope_pin_module  # ★ SWP-J 표기 파라미터 치환용 (모듈 객체)
    from envelope_pin import (
        compute_envelope,
        compute_envelope_from_text,
        compute_envelope_from_document,
        cut_envelope,
        EnvelopeError,
        ENVELOPE_ERROR_KINDS,
    )
    from workflow_shape import dup_safe_load
except ImportError as e:
    raise ImportError(f"Failed to import envelope_pin or workflow_shape: {e}") from e

# ★ 핀 값 — DevPL 채취 (워크플로 동결 형상)
PIN_ENVELOPE_SHA256 = "88aefea6410325bd5570f25b2e36d0334ca14d56d0818fc71722d1dc958cbeed"

# ★★ `PIN_P1_EVIDENCE` 는 **독립 리터럴**이다 — `PIN_ENVELOPE_SHA256` 을 참조해 파생하면
#    아래 3-way 결속의 세 번째 변이 `X == X` 가 되어 **항진**하고, §8.3 이 요구하는
#    「두 거처를 같은 커밋에서 함께 갱신한다」는 규율이 **구조적으로 반증 불가**가 된다.
#    (핀 재채취 시 이 줄과 위 줄을 **둘 다** 고쳐야 한다 — 그것이 검사 대상인 규율이다.)
PIN_P1_EVIDENCE = {
    "envelope_sha256": "88aefea6410325bd5570f25b2e36d0334ca14d56d0818fc71722d1dc958cbeed",
}

# ★ 작업 경로
WF_PATH = os.path.join(REPO_ROOT, ".github", "workflows", "parallel-work-sentinel-check.yml")
JOB2 = "parallel-work-sentinel-test"
TPL_PATH = os.path.join(REPO_ROOT, "templates", "github-workflows", "parallel-work-sentinel-check.yml")
ENVELOPE_PIN_SCRIPT = os.path.join(REPO_ROOT, "scripts", "lib", "envelope_pin.py")

# ★ Spine 정의역 — 봉투 합성 래퍼 노드만 (ENV-5 최상위 래퍼)
# ("jobs",) = 합성 래퍼 (probe 주입 시 무가시 — C₀ 동일)
# ("jobs", JOB2) = JOB2 서브트리 본체는 제외 금지 (ENV-5 최상위가 무검증으로 남음)
SPINE_PATHS = {
    ("jobs",),
}

# ★ Spine **키** 위치 (§8.B 「봉투 spine declare」 (i)·(ii)) — 봉투 구성이 *선택자로 소비*하는
#   구조 키 2종. 이 둘의 rename 은 내용 축이 아니라 전제 축에서 `exit 2` 가 되므로
#   키 정의역(`SWP-E`)에서 제외한다. (제외하지 않으면 정본이 FAIL 2/36 = born-RED)
SPINE_KEY_POSITIONS = {
    ((), "jobs"),
    (("jobs",), JOB2),
}

# ★ verdict 3값 (§8.B — `exit 0`/`exit 1`/`exit 2` 의 in-process 동형 라벨)
VERDICT_GREEN = "GREEN"
VERDICT_RED = "RED"
VERDICT_EXIT2 = "exit 2"


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


def _all_leaf_paths(node: Any, path: Tuple = ()) -> set:
    r"""scalar leaf 경로 전수 — mapping 값 위치 ∧ sequence 직접 원소 **양쪽** (`SWP-A` 정의역)."""
    paths = set()
    if isinstance(node, dict):
        for key, value in node.items():
            paths |= _all_leaf_paths(value, path + (key,))
    elif isinstance(node, (list, tuple)):
        for idx, elem in enumerate(node):
            paths |= _all_leaf_paths(elem, path + (idx,))
    else:
        paths.add(path)
    return paths


def _all_sequence_paths(node: Any, path: Tuple = ()) -> set:
    r"""sequence(list/tuple) 경로 전수 (`SWP-F` 정의역)."""
    paths = set()
    if isinstance(node, dict):
        for key, value in node.items():
            paths |= _all_sequence_paths(value, path + (key,))
    elif isinstance(node, (list, tuple)):
        paths.add(path)
        for idx, elem in enumerate(node):
            paths |= _all_sequence_paths(elem, path + (idx,))
    return paths


def _all_map_value_string_leaves(node: Any, path: Tuple = ()) -> set:
    r"""**mapping 값 위치**의 문자열 leaf 전수 (`SWP-D` 정의역 — `ENV-2` **적용역**).

    ★ sequence 의 **직접** 원소는 제외한다(독법 `A` 의 비적용역 — 그쪽은 `SWP-E` 소관).
    """
    paths = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str):
                paths.add(path + (key,))
            else:
                paths |= _all_map_value_string_leaves(value, path + (key,))
    elif isinstance(node, (list, tuple)):
        for idx, elem in enumerate(node):
            if not isinstance(elem, str):
                paths |= _all_map_value_string_leaves(elem, path + (idx,))
    return paths


def _all_key_positions(node: Any, path: Tuple = ()) -> set:
    r"""`(그 키를 보유한 mapping 의 경로, 키)` 전수 (`SWP-E` 키 반쪽 정의역 — `ENV-2` 비적용역)."""
    positions = set()
    if isinstance(node, dict):
        for key, value in node.items():
            positions.add((path, key))
            positions |= _all_key_positions(value, path + (key,))
    elif isinstance(node, (list, tuple)):
        for idx, elem in enumerate(node):
            positions |= _all_key_positions(elem, path + (idx,))
    return positions


def _bare_sequence_string_elements(node: Any, path: Tuple = ()) -> set:
    r"""`(sequence 경로, 인덱스)` — 직접 원소가 str 인 자리 전수 (`SWP-E` bare 반쪽).

    ★ 이 정의역이 `ENV-2` **비적용역**의 활성화 축(`on.pull_request.types`)을 담는다.
    """
    positions = set()
    if isinstance(node, dict):
        for key, value in node.items():
            positions |= _bare_sequence_string_elements(value, path + (key,))
    elif isinstance(node, (list, tuple)):
        for idx, elem in enumerate(node):
            if isinstance(elem, str):
                positions.add((path, idx))
            else:
                positions |= _bare_sequence_string_elements(elem, path + (idx,))
    return positions


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
    r"""한 path 의 노드에 probe 주입 — mapping 은 **키**, ★sequence 는 **원소**.

    ★★ 구 판본은 `isinstance(target, dict)` 일 때만 주입하고 그 외에는 **원본을 그대로**
       돌려줬다. 그 조용한 no-op 때문에 sequence 원소 위치(`ENV-2` **비적용역**)가 통째로
       사각이 됐다 — 주입이 일어나지 않았는데 「sha 무변화」가 「흡수」로 **오독**된다.
    ⇒ (i) sequence 확장 (ii) 미지원 노드는 **조용히 통과시키지 않고 raise**
       (하네스 사망을 verdict 로 위장하지 않는다 — 「RED 를 검출로 읽기 전에 사유 확인」).
    """
    doc = copy.deepcopy(document)
    target = doc if not path else _get_node_at_path(doc, path)
    if isinstance(target, dict):
        target[probe_key] = probe_value
    elif isinstance(target, list):
        target.append(probe_value)
    else:
        raise TypeError(
            f"probe 주입 불가 노드 {path!r}: {type(target).__name__} "
            f"(mapping/sequence 아님 — 정의역 파생이 잘못됐다)"
        )
    return doc


# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼: verdict 산출 (§8.B verdict 3값 — CLI `main()` 번역 규칙의 in-process 동형)
# ─────────────────────────────────────────────────────────────────────────────

def _envelope_outcome(document: Any, job2: str, *, pre_val=None,
                      post_map=None) -> Tuple[Optional[str], str]:
    r"""참조 구현 호출 1회의 산출 — `(sha_or_None, detail)`.

    ★★ bare `except:` **금지**. CLI `main()` 이 *전 예외* 를 `exit 2` 로 번역하는 것은 맞지만,
       그 번역을 재현하면서 **예외 정체를 버리면** 「`exit 2` 인가」와 「하네스가 죽었나」가
       구별 불가가 된다 — `SWP-B`/`SWP-H`/`SWP-I` 는 `exit 2` 를 **기대** verdict 로 삼으므로
       그 순간 sweep 자신이 항진 위험을 진다. ⇒ **detail 에 예외 정체를 보존**한다.
    ★ `try` 블록은 참조 구현 호출 **한 줄만** 감싼다 — 문서 변형·probe 주입은 블록 **밖**
      (하네스 자신의 버그가 `exit 2` 로 위장되지 않는다).
    """
    try:
        env = compute_envelope_from_document(document, job2, pre_val=pre_val, post_map=post_map)
    except EnvelopeError as exc:  # P-E1~P-E3
        return (None, f"EnvelopeError:{exc.error_kind}: {exc}")
    except Exception as exc:  # noqa: BLE001 — P-E4 (접힘·직렬화 불가·전 구간 미포착)
        return (None, f"{type(exc).__name__}: {exc}")
    return (env.sha256, "")


def _verdict(document: Any, ref_sha: str, *, pre_val=None,
             post_map=None) -> Tuple[str, str]:
    r"""문서 1건의 verdict — `(GREEN|RED|exit 2, detail)`."""
    sha, detail = _envelope_outcome(document, JOB2, pre_val=pre_val, post_map=post_map)
    if sha is None:
        return (VERDICT_EXIT2, detail)
    return (VERDICT_GREEN if sha == ref_sha else VERDICT_RED, "")


def _verdict_from_text(text: str, ref_sha: str) -> Tuple[str, str]:
    r"""**텍스트 층** verdict (`SWP-I` 전용 — 파싱 이전 사건은 구조 변형으로 탐침 불가)."""
    try:
        env = compute_envelope_from_text(text, JOB2)
    except EnvelopeError as exc:
        return (VERDICT_EXIT2, f"EnvelopeError:{exc.error_kind}: {exc}")
    except Exception as exc:  # noqa: BLE001
        return (VERDICT_EXIT2, f"{type(exc).__name__}: {exc}")
    return (VERDICT_GREEN if env.sha256 == ref_sha else VERDICT_RED, "")


def _compute_sha_with_hooks(document: Any, job2: str, pre_val=None, post_map=None) -> Optional[str]:
    r"""document 를 정규화 후 sha 반환 (hook 적용). `exit 2` 는 `None` (구 시그니처 보존)."""
    return _envelope_outcome(document, job2, pre_val=pre_val, post_map=post_map)[0]


def _load_target() -> Tuple[str, Any, str]:
    r"""대상 워크플로 → `(원문 텍스트, 파싱된 문서, 정본 sha)`."""
    with open(WF_PATH, encoding="utf-8-sig", newline=None) as fh:
        text = fh.read()
    document = dup_safe_load(text)
    return text, document, compute_envelope(WF_PATH, JOB2).sha256


# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼: 변형 연산자 (§8.B — 「전문 고정」. 이름이 구현을 결정하지 못하면 수치가 재현되지 않는다)
# ─────────────────────────────────────────────────────────────────────────────

def _mutate_leaf(value: Any) -> Any:
    r"""`SWP-A`/`SWP-C` 변형 연산자 **전문 고정**:
    str ⇒ 위치 1 에 토큰 `MUT` 삽입 / bool ⇒ 반전 / int ⇒ `+1` / 그 외 ⇒ `"MUT"` 치환.

    ★ bool 검사가 int 검사보다 **먼저**여야 한다 (`bool` 은 `int` 의 서브클래스).
    """
    if isinstance(value, str):
        return value[:1] + "MUT" + value[1:]
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    return "MUT"


def _pad(value: str) -> str:
    r"""`SWP-D`/`SWP-E` padding 연산자 **전문 고정** = 양끝 2칸."""
    return "  " + value + "  "


def _set_at_path(document: Any, path: Tuple, value: Any) -> Any:
    r"""경로 끝 원소를 치환한 **사본** 반환 (mapping 키 · sequence 인덱스 공용)."""
    doc = copy.deepcopy(document)
    parent = doc if len(path) == 1 else _get_node_at_path(doc, path[:-1])
    parent[path[-1]] = value
    return doc


def _rename_key(document: Any, map_path: Tuple, key: Any, new_key: Any) -> Any:
    r"""mapping 의 키를 rename 한 **사본** 반환 (원 삽입 순서 보존 — 키순서 축과 교락 금지)."""
    doc = copy.deepcopy(document)
    node = doc if not map_path else _get_node_at_path(doc, map_path)
    items = list(node.items())
    for k, _v in items:
        del node[k]
    for k, v in items:
        node[new_key if k == key else k] = v
    return doc


def _inject_collision_pair(document: Any, map_path: Tuple, raw_key: Any) -> Any:
    r"""`SWP-B`/`SWP-H` probe **전문 고정** — `{raw_key: "COLL"}` ∧ `{json 렌더(raw_key): "COLL"}`
    동시 주입. 두 키는 파싱 층에서 **서로 다른 키**지만 키 렌더 후 **같은 문자열로 접힌다**
    ⇒ `ENV-3` fail-closed 가 발동해야 한다(`exit 2`).
    """
    doc = copy.deepcopy(document)
    node = doc if not map_path else _get_node_at_path(doc, map_path)
    node[raw_key] = "COLL"
    node[json.dumps(raw_key, ensure_ascii=False)] = "COLL"
    return doc


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


def _sweep_domains(envelope: Any) -> Dict[str, Any]:
    r"""전 sweep 공통 정의역 — **「적용역 − 봉투 spine」에서 기계 파생** (§8.B spine declare).

    ★ 손목록·1점 하드코딩 0. 반환 키가 곧 sweep 정의역 이름이다.
    """
    key_positions = _all_key_positions(envelope) - SPINE_KEY_POSITIONS
    return {
        "mapping_nodes": _all_mapping_nodes(envelope) - SPINE_PATHS,
        "leaves": _all_leaf_paths(envelope),
        "sequences": _all_sequence_paths(envelope),
        "map_value_string_leaves": _all_map_value_string_leaves(envelope),
        "string_keys": {(p, k) for p, k in key_positions if isinstance(k, str)},
        "nonstring_keys": {(p, k) for p, k in key_positions if not isinstance(k, str)},
        "bare_sequence_string_elements": _bare_sequence_string_elements(envelope),
    }


# ★ 자기검사 (b) — **알려진 경로 포함** assert 의 앵커. 대상 워크플로에서 실재를 실측 확인했다
#   (`steps[3]` = "Collect pytest tests" 의 `run` · `steps[1]` = "Set up Python" 의 `with`).
KNOWN_LEAF_PATH = ("jobs", JOB2, "steps", 3, "run")
KNOWN_MAPPING_PATH = ("jobs", JOB2, "steps", 1, "with")


def _assert_derivation_selfcheck(domains: Dict[str, Any]) -> None:
    r"""★ **파생 유틸 자기검사 (a)+(b)** — 모든 sweep 이 **실행 이전에** 호출한다.

    §8.B 「파생 유틸 자기검사 의무」: sweep 의 기대 산출은 **정의상 균일**(`27/27`·`14/14` …)
    이라 *"산출 열이 균일하면 판별이 아니라 **하네스 사망**을 먼저 의심하라"* 규율의 적용
    대상이 정확히 sweep 자신이다. 파생 유틸이 **빈 집합**을 돌려주면 *"전건 기대 verdict"* 가
    **공허 참**이 되어 sweep 이 통과한다.
    """
    # (a) 비공허 — 전 정의역
    for name, dom in domains.items():
        assert len(dom) > 0, f"자기검사 (a) FAIL — 파생 정의역 {name!r} 이 공허 (하네스 사망 의심)"
    # (b) 알려진 경로 포함 — 비공허만으로는 `DERIVE-TOPONLY`(1) 를 못 잡는다
    assert KNOWN_LEAF_PATH in domains["leaves"], \
        f"자기검사 (b) FAIL — 알려진 leaf {KNOWN_LEAF_PATH} 가 파생 집합에 부재"
    assert KNOWN_MAPPING_PATH in domains["mapping_nodes"], \
        f"자기검사 (b) FAIL — 알려진 mapping {KNOWN_MAPPING_PATH} 가 파생 집합에 부재"


def test_envelope_pin_domain_derivation_selfcheck():
    r"""★ 파생 유틸 자기검사 (a) 비공허 ∧ (b) **알려진 경로 포함** (§8.B 자기검사 의무).

    (c) 음성 대조는 형제 테스트(`..._derivation_negative_control`)가 낸다 — 그쪽이
    **퇴화 유틸을 실제로 주입해** *"검출은 정의역에서 온다"* 를 실증한다.
    ★ 구 판본의 *"`('nonexistent',)` 가 집합에 없다"* 는 (c) 가 아니었다 — 어떤 퇴화 유틸도
      그 assert 를 통과하므로 **판별력 0**.
    """
    _text, document, _ref = _load_target()
    envelope = cut_envelope(document, JOB2)
    domains = _sweep_domains(envelope)

    _assert_derivation_selfcheck(domains)

    S = _derive_S_from_envelope_pin_source()
    P = _derive_P_from_S(S)
    assert len(S) > 0, "S is empty"
    assert len(P) > 0, "P is empty"

    for name in sorted(domains):
        print(f"[파생] {name:32} = {len(domains[name])}")
    print(f"[파생] |S|={len(S)}, |P|={len(P)}")
    print(f"[자기검사 (b)] {KNOWN_LEAF_PATH} ∈ leaves ∧ {KNOWN_MAPPING_PATH} ∈ mapping_nodes")

    # ★ `P-E5`(blocking) — `|jobs| ≥ 2`. 미충족이면 `SWP-C` 정의역이 0 이 되어
    #   「전건 GREEN」이 **공허 참**이 된다 (오라클 사망 ⇒ blocking).
    assert len(document["jobs"]) >= 2, \
        f"P-E5 위반 — |jobs| = {len(document['jobs'])} < 2 (SWP-C 정의역 공허)"

    # ★ `P-E6`-a(blocking) — 길이 ≥ 2 sequence ≥ 2 (`SWP-F` 순서·다중도 반쪽의 비공허 전제)
    long_seqs = [p for p in domains["sequences"] if len(_get_node_at_path(envelope, p)) >= 2]
    assert len(long_seqs) >= 2, f"P-E6-a 위반 — 길이 ≥ 2 sequence {len(long_seqs)} < 2"

    # ★ `P-E6`-b(declare 전용 — `exit 2` 로 내지 않는다). 미충족 시 **전칭 축소 마커**만 산출하고
    #   verdict 는 불변. 정의역이 0 이 아니라 **1** 이라 오라클은 살아 있고 주장 범위만 좁다.
    bare_carriers = {seq for seq, _idx in domains["bare_sequence_string_elements"]}
    if len(bare_carriers) < 2:
        print("[universal-narrowed: SWP-E.bare = observed-single-sequence]"
              f" — bare 담지 distinct sequence = {len(bare_carriers)}")

    print("[PASS] Domain derivation selfcheck (a)+(b) ∧ P-E5 ∧ P-E6-a")
# ─────────────────────────────────────────────────────────────────────────────
# 정의역 파생 보조 (sweep 반쪽이 공유)
# ─────────────────────────────────────────────────────────────────────────────

def _non_applicable_domains(document: Any) -> Tuple[set, set]:
    r"""`ENV-5` **비적용역** = `jobs.<other>` 단독 (여집합 자기 가드) — `SWP-C` 정의역."""
    others = [j for j in document["jobs"] if j != JOB2]
    leaves, mappings = set(), set()
    for job in others:
        sub = document["jobs"][job]
        base = ("jobs", job)
        leaves |= {base + p for p in _all_leaf_paths(sub)}
        mappings |= {base + p for p in _all_mapping_nodes(sub)}
    return leaves, mappings


def _distinguishing_pair_indices(S: List[Any]) -> List[Tuple[int, int]]:
    r"""구별쌍을 **인덱스**로 — 값 대신 인덱스를 쓰면 node 별 sha 를 재사용할 수 있다
    (`(b)` 를 `14×|P|×2` 회 계산 → `14×|S|` 회로 축약. 판정 내용은 동일)."""
    return [(i, j) for i in range(len(S)) for j in range(i + 1, len(S))
            if _orbit(S[i]) != _orbit(S[j])]


def _parser_derived_nonstring_scalar_samples() -> List[Tuple[str, Any]]:
    r"""`SWP-H` type 축 — **PyYAML `SafeLoader.yaml_implicit_resolvers` 에서 기계 파생**.

    후보 tag 는 resolver 표에서 얻고, 각 tag 의 표본 리터럴은 §8.B 「표본 전문 고정」을 따른다
    (`bool` = **`False`** · `null` = `None` · `int` = `2` · `float` = `3.25`).
    ★ `bool` 표본이 `True` 가 아닌 이유: `True` 는 대상 봉투 root 에 **이미 키로 존재**하므로
      (`on:` 이 YAML 1.1 에서 `True` 로 파싱) 주입이 **치환**이 되어 충돌쌍이 성립하지 않는다.
    ★ 「JSON 직렬화 가능」 여부는 **선언이 아니라 실행으로 판정**한다 — `timestamp` 는 그 판정에서
      기계적으로 탈락한다(4종이 손목록이 아니라 산출임을 보증).
    """
    resolver_tags = set()
    for _ch, rules in yaml.SafeLoader.yaml_implicit_resolvers.items():
        for tag, _regex in rules:
            resolver_tags.add(tag)

    # 값 스칼라 tag 후보 ↔ 표본 리터럴 (구조 지시어 tag `merge`/`value`/`yaml` 은 값이 아니다)
    literals = {
        "tag:yaml.org,2002:bool": "false",
        "tag:yaml.org,2002:null": "null",
        "tag:yaml.org,2002:int": "2",
        "tag:yaml.org,2002:float": "3.25",
        "tag:yaml.org,2002:timestamp": "2026-08-19",
    }
    out = []
    for tag in sorted(literals):
        assert tag in resolver_tags, f"resolver 표에 없는 tag: {tag}"
        value = yaml.safe_load(literals[tag])
        assert not isinstance(value, str), f"{tag} 표본이 문자열이다"
        try:
            json.dumps(value)
        except TypeError:
            continue  # ★ JSON 직렬화 불가 ⇒ 기계적으로 탈락 (timestamp)
        out.append((tag, value))
    return out


def _composed_region_mapping_nodes(text: str) -> List[Tuple[Tuple, Any]]:
    r"""**텍스트 층** mapping node 전수 — `yaml.compose()` 노드 트리에서 파생 (`SWP-I` 정의역).

    ★ 구조 층(`_all_mapping_nodes`)과 **독립 파생**이며, 두 산출의 일치가 곧 교차 검증이다.
    ★ spine 래퍼(`jobs` mapping 노드) 제외 ∧ `jobs.<other>` 는 비적용역이라 제외.
    """
    root = yaml.compose(text)

    def key_of(key_node):
        r"""composed 키 노드 → **파싱된 문서와 같은 키 값**.

        ★ `key_node.value` 를 그대로 쓰면 `on:` 이 `'on'`(str) 이 되어 구조 층의 `True`(YAML 1.1
          bool) 와 어긋난다 — 두 파생이 **같은 정의역을 낸다**는 교차 검증이 그 순간 깨진다.
          ⇒ resolver 가 붙인 **tag 로 구성**한다(따옴표 인용 키의 오해석도 함께 막힌다).
        """
        loader = yaml.SafeLoader("")
        try:
            return loader.construct_object(key_node, deep=True)
        finally:
            loader.dispose()

    def walk(node, in_region, path):
        out = []
        if isinstance(node, yaml.MappingNode):
            if in_region:
                out.append((path, node))
            for key_node, value_node in node.value:
                name = key_of(key_node) if isinstance(key_node, yaml.ScalarNode) else None
                if path == () and name == "jobs":
                    for k2, v2 in value_node.value:  # `jobs` 래퍼 = spine (자신 제외)
                        n2 = k2.value if isinstance(k2, yaml.ScalarNode) else None
                        out += walk(v2, n2 == JOB2, path + ("jobs", n2))
                else:
                    out += walk(value_node, in_region, path + (name,))
        elif isinstance(node, yaml.SequenceNode):
            for idx, elem in enumerate(node.value):
                out += walk(elem, in_region, path + (idx,))
        return out

    return walk(root, True, ())


def _first_single_line_pair(node: Any):
    r"""그 mapping 의 **첫 「단일 행을 차지하는」 키·값 쌍** — 없으면 `None`.

    ★ 블록 mapping/sequence/블록 스칼라 값은 끝 줄이 달라 자연히 제외된다
      (대상의 `on:` 노드가 정확히 그 이유로 (i) 정의역 밖 = 13).
    """
    for key_node, value_node in node.value:
        if key_node.start_mark.line == value_node.end_mark.line:
            return key_node, value_node
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Sweep 로스터 `SWP-A` ~ `SWP-J` (§8.B 「sweep 로스터」)
#
# ★ 정의역은 전건 **「적용역 − 봉투 spine」에서 기계 파생** (손목록·1점 하드코딩 0).
# ★ 각 sweep 은 실행 **이전에** `_assert_derivation_selfcheck` 를 통과한다
#   (기대 산출이 정의상 균일하므로, 그 균일이 판별인지 **하네스 사망**인지 먼저 가른다).
# ★ 한 sweep 은 1+ 개의 **반쪽(half)** 으로 이뤄진다 — 연언 성질(`ENV-4`)·양 술어(`ENV-8`)는
#   반쪽 하나만 재면 나머지가 「장식」으로 **오라벨**된다.
# ★★ 반쪽 정의는 `_sweep_halves()` **단일 출처**다 — sweep 테스트와 음성 대조가 **같은 정의**를
#   쓴다. 두 벌로 두면 이 Story 의 지배 결함(*"검사 정의역이 주장 범위와 어긋남"*)이 정확히
#   그 틈에서 재발한다.
# ─────────────────────────────────────────────────────────────────────────────

_Half = namedtuple("_Half", "sweep half domain cell ok expect")


def _elem_path(elem: Any) -> Tuple:
    r"""반쪽 원소에서 **경로 성분**을 뽑는다 (퇴화 정의역 필터의 depth 기준).

    원소 형태는 반쪽마다 다르다 — 경로 단독 `(k, ...)` · 합성 `((경로), 키/인덱스/tag/표본)`.
    합성은 **첫 성분이 tuple** 이라는 사실로 판별한다.
    """
    if isinstance(elem, tuple) and elem and isinstance(elem[0], tuple):
        return elem[0]
    return elem


def _sweep_halves(document: Any, text: str) -> List[_Half]:
    r"""`SWP-A`~`SWP-I` 의 **반쪽 전수** 를 구성한다 (정의역 ∧ 셀 ∧ 기대).

    ★ `SWP-J` 는 정의역이 대상 구조가 아니라 **직렬화기 시그니처**에 살아서 형태가 다르다
      — 별 테스트가 담지하고 본 목록에는 없다(로스터 테스트가 그 사실을 명시 assert 한다).
    """
    envelope = cut_envelope(document, JOB2)
    domains = _sweep_domains(envelope)
    _assert_derivation_selfcheck(domains)          # ★ sweep 실행 **이전** 자기검사 (a)+(b)
    ref = _envelope_outcome(document, JOB2)[0]

    def is_red(r):
        return r[0] == VERDICT_RED

    def is_green(r):
        return r[0] == VERDICT_GREEN

    def is_exit2(r):
        return r[0] == VERDICT_EXIT2

    halves: List[_Half] = []

    # ── `SWP-A` — `ENV-5` 적용역 leaf 전수 변형 ⇒ 전건 RED
    def cell_a(path):
        return _verdict(
            _set_at_path(document, path, _mutate_leaf(_get_node_at_path(document, path))), ref)

    halves.append(_Half("SWP-A", "적용역 leaf 변형", domains["leaves"], cell_a, is_red, VERDICT_RED))

    # ── `SWP-B` — `ENV-3` 적용역 mapping 전수 충돌 ⇒ 전건 exit 2
    def cell_b(path):
        return _verdict(_inject_collision_pair(document, path, 2), ref)

    halves.append(_Half("SWP-B", "적용역 mapping 충돌", domains["mapping_nodes"],
                        cell_b, is_exit2, VERDICT_EXIT2))

    # ── `SWP-C` — `ENV-5` 비적용역(`jobs.<other>` 단독) ⇒ 전건 GREEN
    other_leaves, other_maps = _non_applicable_domains(document)
    halves.append(_Half("SWP-C", "비적용역 leaf 변형", other_leaves, cell_a, is_green, VERDICT_GREEN))
    halves.append(_Half("SWP-C", "비적용역 충돌(순서 계약)", other_maps, cell_b, is_green, VERDICT_GREEN))

    # ── `SWP-D` — `ENV-2` 적용역 값 문자열 leaf padding ⇒ 전건 GREEN (흡수)
    def cell_d(path):
        return _verdict(_set_at_path(document, path, _pad(_get_node_at_path(document, path))), ref)

    halves.append(_Half("SWP-D", "적용역 값 padding", domains["map_value_string_leaves"],
                        cell_d, is_green, VERDICT_GREEN))

    # ── `SWP-E` — `ENV-2` 비적용역(키 ∧ bare sequence 원소) padding ⇒ 전건 RED
    def cell_e_key(elem):
        map_path, key = elem
        return _verdict(_rename_key(document, map_path, key, _pad(key)), ref)

    def cell_e_bare(elem):
        seq_path, idx = elem
        return _verdict(_set_at_path(document, seq_path + (idx,),
                                     _pad(_get_node_at_path(document, seq_path)[idx])), ref)

    halves.append(_Half("SWP-E", "적용역 문자열 키 padding", domains["string_keys"],
                        cell_e_key, is_red, VERDICT_RED))
    halves.append(_Half("SWP-E", "bare sequence 원소 padding",
                        domains["bare_sequence_string_elements"], cell_e_bare, is_red, VERDICT_RED))

    # ── `SWP-F` — `ENV-4`(연언 2 conjunct) ∧ `ENV-7`(다중도). 세 반쪽 전부 필수
    long_seqs = {p for p in domains["sequences"] if len(_get_node_at_path(envelope, p)) >= 2}
    multi_key_maps = {p for p in domains["mapping_nodes"] if len(_get_node_at_path(envelope, p)) >= 2}

    def cell_f_order(path):
        return _verdict(
            _set_at_path(document, path, list(reversed(_get_node_at_path(document, path)))), ref)

    def cell_f_keyorder(path):
        doc2 = copy.deepcopy(document)
        target = doc2 if not path else _get_node_at_path(doc2, path)
        items = list(target.items())
        for k, _v in items:
            del target[k]
        for k, v in reversed(items):
            target[k] = v
        return _verdict(doc2, ref)

    def cell_f_dup(path):
        node = _get_node_at_path(document, path)
        return _verdict(_set_at_path(document, path, [node[0]] + list(node)), ref)

    halves.append(_Half("SWP-F", "sequence 순서 역전", long_seqs, cell_f_order, is_red, VERDICT_RED))
    halves.append(_Half("SWP-F", "mapping 키순서 역전", multi_key_maps,
                        cell_f_keyorder, is_green, VERDICT_GREEN))
    halves.append(_Half("SWP-F", "sequence 원소 복제(다중도)", domains["sequences"],
                        cell_f_dup, is_red, VERDICT_RED))

    # ── `SWP-G` — `ENV-8` 값 표현 충실도. (a) 탈락 ∧ (b) 단사성 (★슬롯 고정)
    S = _derive_S_from_envelope_pin_source()
    pair_idx = _distinguishing_pair_indices(S)
    _probe_sha: Dict[Tuple, Optional[str]] = {}

    def probe_sha(path, i):
        key = (path, i)
        if key not in _probe_sha:
            probed = _inject_probe_at_node(document, path, "__PROBE_KIND__", S[i])
            _probe_sha[key] = _envelope_outcome(probed, JOB2)[0]
        return _probe_sha[key]

    def cell_g_a(elem):
        path, i = elem
        sha = probe_sha(path, i)
        if sha is None:
            return (VERDICT_EXIT2, f"주입 값 {S[i]!r} 이 exit 2")
        return (VERDICT_RED if sha != ref else VERDICT_GREEN, "")

    def cell_g_b(elem):
        path, i, j = elem
        if probe_sha(path, i) == probe_sha(path, j):
            return ("붕괴", f"{S[i]!r} ~ {S[j]!r} 이 같은 봉투로 접혔다")
        return ("구별", "")

    dom_g_a = {(p, i) for p in domains["mapping_nodes"] for i in range(len(S))}
    dom_g_b = {(p, i, j) for p in domains["mapping_nodes"] for i, j in pair_idx}
    halves.append(_Half("SWP-G", "(a) 정의역 탈락", dom_g_a, cell_g_a, is_red, VERDICT_RED))
    halves.append(_Half("SWP-G", "(b) 단사성", dom_g_b, cell_g_b, lambda r: r[0] == "구별", "구별"))

    # ── `SWP-H` — `ENV-6` 적용역 키 type 전칭 (파서 파생 비-문자열 스칼라 type)
    type_samples = dict(_parser_derived_nonstring_scalar_samples())

    def cell_h(elem):
        path, tag = elem
        return _verdict(_inject_collision_pair(document, path, type_samples[tag]), ref)

    dom_h = {(p, tag) for p in domains["mapping_nodes"] for tag in type_samples}
    halves.append(_Half("SWP-H", "키 type 충돌쌍", dom_h, cell_h, is_exit2, VERDICT_EXIT2))

    # ── `SWP-I` — `ENV-1` 파싱 층 전칭 (**텍스트 층** 주입)
    composed = dict(_composed_region_mapping_nodes(text))
    lines = text.split("\n")
    dup_domain = {p for p, node in composed.items() if _first_single_line_pair(node) is not None}

    def cell_i_dup(path):
        key_node, value_node = _first_single_line_pair(composed[path])
        fragment = text[key_node.start_mark.index:value_node.end_mark.index]
        injected = " " * key_node.start_mark.column + fragment
        at = value_node.end_mark.line
        return _verdict_from_text("\n".join(lines[:at + 1] + [injected] + lines[at + 1:]), ref)

    def cell_i_merge(path):
        node = composed[path]
        key_node, value_node = _first_single_line_pair(node) or node.value[0]
        col = key_node.start_mark.column
        at = value_node.end_mark.line
        injected = [" " * col + "<<: *cfp2978probe", " " * col + "zzz_probe_key: B"]
        anchor = "_cfp2978_merge_probe: &cfp2978probe\n  zzz_probe_key: A\n"
        return _verdict_from_text(
            anchor + "\n".join(lines[:at + 1] + injected + lines[at + 1:]), ref)

    halves.append(_Half("SWP-I", "(i) 리터럴 중복 키", dup_domain, cell_i_dup, is_exit2, VERDICT_EXIT2))
    halves.append(_Half("SWP-I", "(ii) merge override", set(composed), cell_i_merge,
                        lambda r: r[0] != VERDICT_EXIT2, "≠ exit 2"))

    return halves


def _run_half(half: _Half, domain: Optional[set] = None) -> Tuple[Dict[Any, Tuple[str, str]], set]:
    r"""반쪽 1개 실행 — `(셀별 산출, 기대 미달 원소 집합)`."""
    dom = half.domain if domain is None else domain
    results = {elem: half.cell(elem) for elem in sorted(dom, key=str)}
    return results, {e for e, r in results.items() if not half.ok(r)}


def _print_half(half: _Half, results: Dict[Any, Tuple[str, str]], failures: set) -> None:
    r"""산출 보고 — 실패는 **이름(원소)으로 지목**한다(카디널리티 형 단독 assert 금지)."""
    dist: Dict[str, int] = {}
    for verdict, _d in results.values():
        dist[verdict] = dist.get(verdict, 0) + 1
    print(f"  [{half.sweep} {half.half}] 정의역={len(results)} 기대={half.expect} 산출={dist}")
    for elem in sorted(failures, key=str)[:6]:
        print(f"      FAIL {elem} -> {results[elem][0]} {results[elem][1][:100]}")


def _assert_sweep(sweep_id: str) -> Dict[str, Dict[Any, Tuple[str, str]]]:
    r"""한 sweep 의 **반쪽 전건** 을 정본 정의역 위에서 실행하고 기대 미달 0 을 단언한다."""
    text, document, _pin = _load_target()
    halves = [h for h in _sweep_halves(document, text) if h.sweep == sweep_id]
    assert halves, f"{sweep_id} 반쪽이 로스터에 등록되지 않았다"

    out, all_fail = {}, set()
    for half in halves:
        results, failures = _run_half(half)
        _print_half(half, results, failures)
        assert results, f"{sweep_id} {half.half} 정의역 **공허** — 「전건 기대 verdict」가 공허 참"
        out[half.half] = results
        all_fail |= {(half.half, e) for e in failures}
    assert not all_fail, f"{sweep_id} 기대 미달: {sorted(all_fail, key=str)[:8]}"
    return out


def test_envelope_pin_swp_a_applicable_leaf_universal():
    r"""**`SWP-A`** — `ENV-5` 적용역 **leaf 전수** 변형 ⇒ **전건 RED** (census #9).

    변형 연산자 **전문 고정** = str ⇒ 위치 1 에 `MUT` 삽입 / bool ⇒ 반전 / int ⇒ `+1` /
    그 외 ⇒ `"MUT"` 치환.
    ablation target = `V-PARTIAL`(step 키를 부분만 봉투에 담는 구현) — 기존 16 셀을 전건 통과한다.
    ★ 부수 조건(census #6) — `ENV-3` **비적용**(값 위치): 전건 RED ∧ **`exit 2` 0**.
    """
    out = _assert_sweep("SWP-A")
    exit2 = {e for e, r in out["적용역 leaf 변형"].items() if r[0] == VERDICT_EXIT2}
    assert not exit2, f"census #6 위반 — 값 위치가 충돌 경로를 발동시켰다: {sorted(exit2, key=str)}"


def test_envelope_pin_swp_b_applicable_mapping_collision_universal():
    r"""**`SWP-B`** — `ENV-3` 적용역 **mapping node 전수**(임의 depth) 충돌 ⇒ **전건 `exit 2`**.

    probe **전문 고정** = `2: "COLL"` ∧ `"2": "COLL"` 동시 주입 (구 probe `True`/`"true"` 는
    봉투 root 에서 「주입」이 아니라 **「치환」**이었다 — `on:` 이 YAML 1.1 bool `True` 키).
    ablation target = `V-TOPCOL`(충돌검사 top-level 한정).
    ★ `exit 2` 를 **사유까지** 확인한다 — 아무 예외나 세면 하네스 사망이 검출로 위장된다.
    """
    out = _assert_sweep("SWP-B")
    wrong = {e: r[1] for e, r in out["적용역 mapping 충돌"].items() if "collision" not in r[1]}
    assert not wrong, f"exit 2 사유가 접힘이 아니다 (하네스 사망 의심): {list(wrong.items())[:4]}"


def test_envelope_pin_swp_c_nonapplicable_jobs_other_universal():
    r"""**`SWP-C`** — `ENV-5` **비적용역**(`jobs.<other>` 단독) 전수 변형 ∧ 충돌 ⇒ **전건 GREEN**.

    ablation target = `V-ALLJOBS`(봉투 scope 를 문서 전문으로 확대) ∧
    ★`V-NORMFIRST`(**정규화를 봉투 절단보다 먼저**) ⇒ 충돌 축이 `exit 2` 로 샌다.
    ⇒ 「절단이 먼저」라는 **순서 계약**의 유일 판별자가 이 sweep 의 충돌 반쪽이다.
    ★ 정의역 비공허는 전제 `P-E5`(`|jobs| ≥ 2`) — 미충족이면 「전건 GREEN」이 공허 참이 된다.
    """
    _assert_sweep("SWP-C")


def test_envelope_pin_swp_d_value_padding_absorbed_universal():
    r"""**`SWP-D`** — `ENV-2` 적용역 **mapping 값 문자열 leaf 전수** padding ⇒ **전건 GREEN**.

    ablation target = `V-NOSTRIP`(값 strip 제거). 구 3점 담지로는 여집합이 남았다.
    """
    _assert_sweep("SWP-D")


def test_envelope_pin_swp_e_nonabsorbed_padding_universal():
    r"""**`SWP-E`** — `ENV-2` **비적용역** 전칭: **mapping 문자열 키 전수** ∧ ★**bare sequence
    문자열 원소 전수** padding(양끝 2칸) ⇒ **전건 RED**.

    ablation target = `V-KEYSTRIP-DEEP`(키 strip 을 depth ≥ 1 에만) — `C₀` 가 정본과 **동일**하고
    top-level 키 1점 셀을 **통과**한다.
    ★★ **bare 반쪽이 독법 `A0`(sequence 직접 원소까지 strip)의 유일 판별자**다 —
       `A0` 구현은 `C₀` 동일이라 **핀 대조로는 원리적으로 못 잡는다**.
    ★ spine 키 2종(top-level `jobs` · JOB2)은 정의역 밖 — 포함하면 정본이 FAIL 2/36(born-RED).
    """
    _assert_sweep("SWP-E")
    _text, document, _pin = _load_target()
    domains = _sweep_domains(cut_envelope(document, JOB2))
    # ★ 전칭 축소 declare (`P-E6`-b, non-blocking) — verdict 불변
    carriers = {seq for seq, _idx in domains["bare_sequence_string_elements"]}
    if len(carriers) < 2:
        print("  [universal-narrowed: SWP-E.bare = observed-single-sequence]"
              f" carriers={sorted(carriers, key=str)}")


def test_envelope_pin_swp_f_datastructure_universal():
    r"""**`SWP-F`** — `ENV-4`·`ENV-7` 적용역 전칭 (**세 반쪽 전부 필수**).

      (1) sequence(길이 >= 2) 전수 **순서 역전** ⇒ **RED**   … `ENV-4` sequence conjunct
      (2) mapping(키 >= 2) 전수 **키 순서 역전**  ⇒ **GREEN** … `ENV-4` mapping conjunct
      (3) sequence 전수 **원소 1개 복제**(선두 원소를 앞에 삽입) ⇒ **RED** … `ENV-7` 다중도

    ★★ `ENV-4` 는 **연언**이고 두 conjunct 의 **판별자가 다르다** — (1) ablation `V-SORTSCALARSEQ`,
       (2) ablation `sort_keys=False`(`V-NOSORTKEYS`). 한쪽만 재면 다른 쪽이 「장식」으로 오라벨된다.
    ★ (3) ablation = `V-SEQDEDUP`(**equality 기반** — hashable-only 구현은 *다른 함수*다).
    """
    out = _assert_sweep("SWP-F")
    # ★ 이름 집합 assert — 다중도 정의역이 두 sequence 를 **둘 다** 담는다 (카디널리티 형 금지)
    assert set(out["sequence 원소 복제(다중도)"]) == {
        (True, "pull_request", "types"), ("jobs", JOB2, "steps")}, \
        f"다중도 정의역 이름 집합 불일치: {sorted(out['sequence 원소 복제(다중도)'], key=str)}"
    assert len(out["mapping 키순서 역전"]) >= 2, "mapping 키순서 반쪽 정의역이 1점 이하 — 전칭 미달"


def test_envelope_pin_swp_g_value_kind_fidelity_universal():
    r"""**`SWP-G`** — `ENV-8` 값 표현 충실도 전칭 (**2 술어**, 정의역은 **3층 기계 파생**).

      **(a) 탈락** — ∀ mapping node × ∀ 값 종류 표본 `s ∈ S`: `__PROBE_KIND__: <s>` ⇒ **RED**
      **(b) 단사성** — ∀ mapping node × ∀ 구별쌍 `(a,b) ∈ P`: `sha(a) != sha(b)`
        (★**슬롯 고정** — 같은 키에 두 값을 넣는다. 값과 함께 키를 바꾸면 원리적 미검출)

    ★★ `|S|`·`|P|` 는 **수치 리터럴이 아니라 3층 파생 산출**이다.
    ★★ **두 술어는 서로의 맹점을 덮는다** — 접힘형 4종(`V-NUMCOERCE`·`V-NFC`·`V-NULLTOMAP`·
       `V-EMPTYSEQSTR`)은 (a) 를 통과하고, 탈락형 3종(`V-DROPNULL`·`V-DROPEMPTYSTR`·
       `V-DROPFALSE`)은 (b) 를 통과한다 ⇒ **한쪽만 구현하면 8 witness 중 절반이 원리적 미검출**.
    """
    S = _derive_S_from_envelope_pin_source()
    assert len(_distinguishing_pair_indices(S)) == len(_derive_P_from_S(S)), \
        "구별쌍 인덱스 파생이 값 파생과 어긋난다"
    _assert_sweep("SWP-G")


def test_envelope_pin_swp_h_key_type_universal():
    r"""**`SWP-H`** — `ENV-6` 적용역 **키 type** 전칭: (mapping node 전수) ×
    (파서 파생 비-문자열 스칼라 type) 충돌쌍 주입 ⇒ **전건 `exit 2`**.

    ablation target = `V-STRBOOL`(bool 만 특수 처리 — `bool`→`json.dumps(k)` · 그 외 비-문자열
    →`str(k)`) ∧ `V-STRKEY`(전 비-문자열 키를 `str()` 렌더).
    ★ `V-STRBOOL` 은 `SWP-B` 를 **통과**하므로 본 sweep 이 **유일 담지자**다.
    """
    samples = _parser_derived_nonstring_scalar_samples()
    assert {t for t, _v in samples} == {
        "tag:yaml.org,2002:bool", "tag:yaml.org,2002:null",
        "tag:yaml.org,2002:int", "tag:yaml.org,2002:float",
    }, f"파서 파생 type 집합 불일치: {[t for t, _ in samples]}"
    out = _assert_sweep("SWP-H")
    wrong = {e: r[1] for e, r in out["키 type 충돌쌍"].items() if "collision" not in r[1]}
    assert not wrong, f"exit 2 사유가 접힘이 아니다: {list(wrong.items())[:4]}"


def test_envelope_pin_swp_i_text_layer_universal():
    r"""**`SWP-I`** — `ENV-1` 파싱 층 전칭 (**텍스트 층** 주입 — 파싱 이전 사건은 구조 변형으로
    원리적으로 탐침되지 않는다).

      **(i)** ∀ mapping node: **첫 단일행 키·값 쌍 `verbatim` 복제 주입** ⇒ **`exit 2`**
      **(ii)** ∀ mapping node: **merge 참조 + 명시 override 주입** ⇒ **≠ `exit 2`**

    ★ 삽입 위치는 `yaml.compose()` 의 `start_mark`/`end_mark` 에서 파생 — 열 = 그 **키의 열**
      (원 줄을 그대로 복사하면 `- ` dash 가 딸려와 *새 list 원소*가 되어 중복 키가 성립하지 않는다),
      행 = 그 쌍의 **끝 줄 다음**.
    ablation target = `V-DUPDEPTH`(중복 검출 top-level 한정, ★**노드 동일성** 구성) ∧
    `V-MERGERAISE`(merge key node 를 skip 하지 않음). 두 witness 는 `SWP-A`~`SWP-H` 를
    **구조적으로 보장된 PASS** 로 통과하므로 본 sweep 이 유일 담지자다.
    """
    text, document, _pin = _load_target()
    # ★ 교차 검증 — **텍스트 층 파생**과 **구조 층 파생**이 같은 정의역을 낸다 (독립 2 파생)
    composed = {p for p, _n in _composed_region_mapping_nodes(text)}
    structural = _sweep_domains(cut_envelope(document, JOB2))["mapping_nodes"]
    assert composed == structural, \
        f"텍스트 층 ↔ 구조 층 정의역 불일치: {sorted(composed ^ structural, key=str)}"

    out = _assert_sweep("SWP-I")
    wrong = {e: r[1] for e, r in out["(i) 리터럴 중복 키"].items() if "duplicate key" not in r[1]}
    assert not wrong, f"(i) exit 2 사유가 중복 키가 아니다: {list(wrong.items())[:4]}"


# ─────────────────────────────────────────────────────────────────────────────
# `SWP-J` — 직렬화 **표기** 전칭 (`ENV-4` 비적용역)
#
# ★ probe set 은 **「이름 집합」으로 pin** 한다 — 카디널리티 형(`n/30`) 금지.
#   담지 테스트는 분모를 세지 않고 **이름별 verdict** 를 대조한다.
# ★ 정의역이 대상 구조가 아니라 **직렬화기 시그니처**에 살아서 `_sweep_halves` 형태에 맞지 않는다.
# ─────────────────────────────────────────────────────────────────────────────

def _swp_j_probes() -> Dict[str, Callable[[Any], Any]]:
    def seq_order_reverse(d):
        _get_node_at_path(d, (True, "pull_request", "types")).reverse()
        return d

    def map_key_order_reverse(d):
        node = d["permissions"]
        items = list(node.items())
        for k, _v in items:
            del node[k]
        for k, v in reversed(items):
            node[k] = v
        return d

    def value_pad(d):
        d["jobs"][JOB2]["name"] = _pad(d["jobs"][JOB2]["name"])
        return d

    def key_pad(d):
        node = d["jobs"][JOB2]
        node[_pad("name")] = node.pop("name")
        return d

    def collision_pair(d):
        d["jobs"][JOB2][2] = "COLL"
        d["jobs"][JOB2]["2"] = "COLL"
        return d

    def date_value(d):
        d["jobs"][JOB2]["__probe__"] = datetime.date(2026, 8, 19)
        return d

    def nan_value(d):
        d["jobs"][JOB2]["__probe__"] = float("nan")
        return d

    def nonascii_value(d):
        d["jobs"][JOB2]["name"] = d["jobs"][JOB2]["name"] + "가"
        return d

    def seq_elem_duplicate(d):
        node = _get_node_at_path(d, (True, "pull_request", "types"))
        node.insert(0, node[0])
        return d

    def null_value(d):
        d["jobs"][JOB2]["__probe__"] = None
        return d

    return {
        "seq-order-reverse": seq_order_reverse,
        "map-key-order-reverse": map_key_order_reverse,
        "value-pad": value_pad,
        "key-pad": key_pad,
        "collision-int-str": collision_pair,
        "date-value": date_value,
        "nan-value": nan_value,
        "nonascii-value": nonascii_value,
        "seq-elem-duplicate": seq_elem_duplicate,
        "null-value": null_value,
    }


# ★ 비-기본값 (표기 축을 실제로 이동시키는 값). `cls`(값 렌더러) 는 **정의역 명시 제외** —
#   치역이 열려 있어 유한 파생 불가(`UM-16` 잔여로 declare, `SWP-J` 가 담지하지 않는다).
SWP_J_NONDEFAULT = {
    "skipkeys": True, "ensure_ascii": True, "check_circular": False, "allow_nan": False,
    "indent": 2, "separators": (", ", ": "), "default": str, "sort_keys": False,
}

# ★ redirect 축 — 「표기」가 아니라 **다른 성질/전제의 소관**임이 실측된 3종.
#   이동하는 probe 를 **이름으로** 지목한다(수치 금지).
SWP_J_REDIRECT = {
    "sort_keys": {"map-key-order-reverse"},   # `ENV-4` **적용** 소관 (census #7)
    "default": {"date-value"},                # 전제 축 (`P-E4` 미직렬화형)
    "allow_nan": {"nan-value"},               # 전제 축 (NaN/Inf)
}


def _swp_j_measure(document: Any, probes: Dict[str, Callable[[Any], Any]]) -> Dict[str, str]:
    ref, _d = _envelope_outcome(copy.deepcopy(document), JOB2)
    return {name: _verdict(fn(copy.deepcopy(document)), ref)[0] for name, fn in probes.items()}


def test_envelope_pin_swp_j_serialization_notation_universal():
    r"""**`SWP-J`** — `ENV-4` **비적용**(직렬화 표기) 전칭: ∀ 표기 파라미터 `q` 에 대해
    probe set 전건의 **verdict 가 불변**(= verdict-중립)이거나, 이동한다면 그 probe 가
    **redirect 축**으로 이미 귀속돼 있어야 한다.

    ★ 파생원 = `inspect.signature(json.dumps)` **명명 파라미터 9 − `cls` = 8**.
    ★ ablation = *"redirect 3 을 표기로 오분류"* — 그러면 `ENV-4` **적용** 판별(#7)과 **전제 축**이
      각각 무주공산이 된다. 그래서 **이동 probe 이름 집합**을 assert 하고, 형제 음성 대조가
      그 오분류를 실제로 주입해 검출됨을 실증한다.
    ★ `C₀` 이동은 허용된다(핀 재유도 대상) — 재는 것은 **verdict 열**이지 sha 값이 아니다.
    """
    _text, document, _pin = _load_target()

    params = [
        name for name, p in inspect.signature(json.dumps).parameters.items()
        if p.kind is inspect.Parameter.KEYWORD_ONLY
        or (p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD and name != "obj")
    ]
    assert len(params) == 9, f"명명 파라미터 파생 불일치: {params}"
    swept = [q for q in params if q != "cls"]
    assert set(swept) == set(SWP_J_NONDEFAULT), \
        f"표기 정의역 불일치 (cls 제외 8): {sorted(set(swept) ^ set(SWP_J_NONDEFAULT))}"

    probes = _swp_j_probes()
    base = _swp_j_measure(document, probes)
    print(f"  [SWP-J base] {base}")
    assert len(set(base.values())) >= 3, f"probe set 이 3-verdict 를 못 낸다: {base}"

    for q in sorted(swept):
        with _patched_serialize_kwargs(q, SWP_J_NONDEFAULT[q]):
            variant = _swp_j_measure(document, probes)
        moved = {name for name in base if base[name] != variant[name]}
        expected_moved = SWP_J_REDIRECT.get(q, set())
        print(f"  [SWP-J {q:15}] 이동 probe={sorted(moved) or '없음(verdict-중립)'}")
        assert moved == expected_moved, (
            f"SWP-J {q}: 이동 probe 이름 집합 불일치 — 기대 {sorted(expected_moved)} "
            f"실측 {sorted(moved)} ({[(n, base[n], variant[n]) for n in sorted(moved)]})"
        )

    assert envelope_pin_module._JSON_SERIALIZE_KWARGS == {
        "sort_keys": True, "ensure_ascii": False, "separators": (",", ":")}, \
        "표기 치환이 복원되지 않았다 (후속 테스트 오염)"

# ─────────────────────────────────────────────────────────────────────────────
# ablation witness (§8.B 「변종 정의 못박기」 — 구성 방식 **전문 고정**)
#
# ★★ witness 는 **정본의 변종**이어야 한다 — 정규화기를 복제하면 그 순간 "다른 함수"가 되고
#    표의 수치가 재현되지 않는다. ⇒ 전건 **참조 구현 모듈 속성의 런타임 치환**으로 구성하고
#    (`envelope_pin.py` **무접촉**), 원 함수를 감싸 최소 변형만 얹는다.
# ★★ witness 가 born-broken 이면 「판별 有」가 **거짓**이 된다(`V-DROPEMPTY` 를 `pre_val` 로
#    만들면 (a) 가 PASS 로 조용히 통과). ⇒ 음성 대조는 **정본 정의역에서 반드시 검출**을 요구한다.
# ─────────────────────────────────────────────────────────────────────────────

@contextlib.contextmanager
def _patched_envelope_pin(**attrs):
    r"""참조 구현 모듈 속성을 일시 치환 (원상 복구 보장).

    ★ `compute_envelope_from_document` 는 `cut_envelope`·`_normalize_mapping` 을 **모듈 전역**으로
      조회하므로, 모듈 속성 치환이 곧 「그 파이프라인의 변종」이 된다.
    """
    saved = {name: getattr(envelope_pin_module, name) for name in attrs}
    try:
        for name, value in attrs.items():
            setattr(envelope_pin_module, name, value)
        yield
    finally:
        for name, value in saved.items():
            setattr(envelope_pin_module, name, value)


@contextlib.contextmanager
def _patched_serialize_kwargs(param: str, value: Any):
    r"""직렬화 표기 파라미터 1개를 비-기본값으로 치환 (`SWP-J` 전용)."""
    saved = dict(envelope_pin_module._JSON_SERIALIZE_KWARGS)
    saved_key = dict(envelope_pin_module._JSON_KEY_KWARGS)
    try:
        envelope_pin_module._JSON_SERIALIZE_KWARGS[param] = value
        if param == "ensure_ascii":  # `ENV-6` — 키 렌더는 값 렌더와 같은 표기를 재사용한다
            envelope_pin_module._JSON_KEY_KWARGS[param] = value
        yield
    finally:
        envelope_pin_module._JSON_SERIALIZE_KWARGS.clear()
        envelope_pin_module._JSON_SERIALIZE_KWARGS.update(saved)
        envelope_pin_module._JSON_KEY_KWARGS.clear()
        envelope_pin_module._JSON_KEY_KWARGS.update(saved_key)


def _w_lossy_deep():
    r"""`V-LOSSY-DEEP` — `jobs.<JOB2>.steps[i].name` 을 봉투에서 **탈락**(`ENV-5` 위반)."""
    orig = envelope_pin_module.cut_envelope

    def cut(document, job2, *, path=None):
        env = copy.deepcopy(orig(document, job2, path=path))  # ★ 원 문서 오염 금지
        for step in env.get("jobs", {}).get(job2, {}).get("steps", []) or []:
            if isinstance(step, dict):
                step.pop("name", None)
        return env

    return {"cut_envelope": cut}


def _w_topcol():
    r"""`V-TOPCOL` — 충돌검사를 **봉투 root 한정**으로 축소.

    ★ 구성 **전문 고정** = **노드 동일성**(`cut_envelope` 가 만든 root 객체와 `is` 비교).
      깊이 카운터는 금지 구성이다 — 중첩 노드를 depth 1 로 오인해 *같은 이름의 다른 함수*가 된다.
    """
    orig_cut = envelope_pin_module.cut_envelope
    orig_norm = envelope_pin_module._normalize_mapping
    state = {"root": None}

    def cut(document, job2, *, path=None):
        env = orig_cut(document, job2, path=path)
        state["root"] = id(env)
        return env

    def norm(node, *, pre_val, post_map):
        if id(node) == state["root"]:
            return orig_norm(node, pre_val=pre_val, post_map=post_map)
        folded = {}
        for key, value in node.items():          # 렌더 키 기준 last-wins 로 접힘을 **흡수**
            folded[envelope_pin_module._render_key(key)] = value
        return orig_norm(folded, pre_val=pre_val, post_map=post_map)

    return {"cut_envelope": cut, "_normalize_mapping": norm}


def _w_alljobs():
    r"""`V-ALLJOBS` — 봉투 scope 를 **문서 전문**으로 확대 (`ENV-5` 비적용역 침범)."""
    orig = envelope_pin_module.cut_envelope

    def cut(document, job2, *, path=None):
        orig(document, job2, path=path)          # 전제 `P-E1`~`P-E3` 는 그대로 통과시킨다
        return copy.deepcopy(document)

    return {"cut_envelope": cut}


def _w_nostrip():
    r"""`V-NOSTRIP` — 값 strip 제거 (`ENV-2` 흡수 축 소거)."""
    orig = envelope_pin_module._normalize_map_value

    def norm_val(value, *, pre_val, post_map):
        if isinstance(value, str):
            return value
        return orig(value, pre_val=pre_val, post_map=post_map)

    return {"_normalize_map_value": norm_val}


def _w_keystrip():
    r"""`V-KEYSTRIP` — **키에도** strip 적용 (`ENV-2` 비적용역 침범).

    ★ 설계의 `V-KEYSTRIP-DEEP`(depth ≥ 1 한정)의 **depth-무관 형제**다 — 이름을 구분해 적는다
      (같은 이름으로 부르면 수치가 갈리는 자리다).
    """
    orig = envelope_pin_module._render_key

    def render(key):
        return key.strip() if isinstance(key, str) else orig(key)

    return {"_render_key": render}


def _w_seqdedup():
    r"""`V-SEQDEDUP` — sequence 원소 중복 제거 (`ENV-7` 다중도 소거).

    ★ 구성 **전문 고정** = **equality 기반**(`any(e == x for x in out)`) — 해시 불가 원소 포함
      전 원소에 적용. hashable-only(`set` 기반)는 mapping 원소를 조용히 통과시키는 *다른 함수*다.
    """
    orig = envelope_pin_module._normalize_sequence

    def norm_seq(node, *, pre_val, post_map):
        out = orig(node, pre_val=pre_val, post_map=post_map)
        res: List[Any] = []
        for elem in out:
            if not any(elem == seen for seen in res):
                res.append(elem)
        return res

    return {"_normalize_sequence": norm_seq}


def _w_dropnull():
    r"""`V-DROPNULL` — 정규화 **후**(`post_map` 위치) `None` 값 탈락 (`ENV-8`(a) 위반)."""
    orig = envelope_pin_module._normalize_mapping

    def norm(node, *, pre_val, post_map):
        out = orig(node, pre_val=pre_val, post_map=post_map)
        return {k: v for k, v in out.items() if v is not None}

    return {"_normalize_mapping": norm}


def _w_strkey():
    r"""`V-STRKEY` — 전 비-문자열 키를 `str()` 로 렌더 (`ENV-6` 렌더 동일성 위반).

    ★ `str(True) == 'True' != 'true'` 라 `ENV-3` fail-closed 가 **한 번도 발동하지 않는다**.
    """
    def render(key):
        return key if isinstance(key, str) else str(key)

    return {"_render_key": render}


def _dup_loader_variant(root_only: bool, merge_raise: bool):
    r"""`ENV-1` 파싱 층 변종 로더 — `dup_safe_load` 치환용."""
    class _Variant(yaml.SafeLoader):
        _root_node = None

        def construct_document(self, node):
            self._root_node = node          # ★ 노드 동일성 포착 (깊이 카운터 금지)
            return super().construct_document(node)

        def construct_mapping(self, node, deep=False):
            if merge_raise:
                for key_node, _v in node.value:
                    if getattr(key_node, "tag", None) == "tag:yaml.org,2002:merge":
                        raise yaml.constructor.ConstructorError(
                            "while constructing a mapping", node.start_mark,
                            "merge key rejected (V-MERGERAISE)", key_node.start_mark)
            if not root_only or node is self._root_node:
                seen = set()
                for key_node, _v in node.value:
                    if getattr(key_node, "tag", None) == "tag:yaml.org,2002:merge":
                        continue
                    try:
                        key = self.construct_object(key_node, deep=deep)
                    except yaml.constructor.ConstructorError:
                        continue
                    try:
                        duplicated = key in seen
                    except TypeError:
                        continue
                    if duplicated:
                        raise yaml.constructor.ConstructorError(
                            "while constructing a mapping", node.start_mark,
                            f"duplicate key {key!r}", key_node.start_mark)
                    seen.add(key)
            return super().construct_mapping(node, deep=deep)

    return lambda text: yaml.load(text, Loader=_Variant)


def _w_dupdepth():
    r"""`V-DUPDEPTH` — 중복 키 검출을 **봉투 root 한정**(노드 동일성)으로 축소 (`ENV-1` 위반)."""
    return {"dup_safe_load": _dup_loader_variant(root_only=True, merge_raise=False)}


def _w_mergeraise():
    r"""`V-MERGERAISE` — merge key node 를 skip 하지 않아 정상 merge 를 `exit 2` 로 낸다."""
    return {"dup_safe_load": _dup_loader_variant(root_only=False, merge_raise=True)}


# ★ sweep ↔ ablation target 배정 (§8.B 피복표 「ablation target」 열).
#   sweep 별로 **그 sweep 이 잡아야 하는 결함 구현**을 지목한다.
SWEEP_ABLATIONS: Dict[str, List[Tuple[str, Callable[[], Dict[str, Any]]]]] = {
    "SWP-A": [("V-LOSSY-DEEP", _w_lossy_deep)],
    "SWP-B": [("V-TOPCOL", _w_topcol)],
    "SWP-C": [("V-ALLJOBS", _w_alljobs)],
    "SWP-D": [("V-NOSTRIP", _w_nostrip)],
    "SWP-E": [("V-KEYSTRIP", _w_keystrip)],
    "SWP-F": [("V-SEQDEDUP", _w_seqdedup)],
    "SWP-G": [("V-DROPNULL", _w_dropnull)],
    "SWP-H": [("V-STRKEY", _w_strkey)],
    "SWP-I": [("V-DUPDEPTH", _w_dupdepth), ("V-MERGERAISE", _w_mergeraise)],
}

# ★ 퇴화 정의역 필터 (§8.B `DERIVE-*`) — **규칙으로 정의**하고 크기를 하드코딩하지 않는다.
DEGENERATE_DOMAIN_FILTERS: Dict[str, Callable[[set], set]] = {
    "DERIVE-EMPTY": lambda dom: set(),
    "DERIVE-TOPONLY": lambda dom: {e for e in dom if len(_elem_path(e)) <= 1},
    "DERIVE-SHALLOW": lambda dom: {e for e in dom if len(_elem_path(e)) <= 2},
}


@pytest.mark.parametrize("sweep_id", sorted(SWEEP_ABLATIONS))
def test_envelope_pin_derivation_negative_control(sweep_id):
    r"""★ 파생 유틸 자기검사 **(c) 음성 대조** — **sweep 별**로 *"검출은 정의역에서 온다"* 를 실증.

    §8.B: *"(a) 단독은 불충분하다 — `DERIVE-TOPONLY` 는 **비공허(1)** 이면서 여전히 무력하다."*
    ⇒ 전역 1회로 두면 *"어느 한 sweep 은 정의역에서 검출력이 온다"* 만 실증하고 **나머지 sweep 의
      정의역은 무인증**으로 남는다 — 그게 정확히 다음 층에서 뚫리는 형태다.

    각 sweep × 각 ablation witness 에 대해:
      (1) **정본 정의역**에서 그 witness 가 **검출**된다 (기대 미달 원소 ≥ 1)
          ★ witness 가 born-broken(미검출)이면 「판별 有」가 거짓이므로 이 assert 가 먼저 터진다.
      (2) **`DERIVE-EMPTY`**(정의역 0)에서는 **검출 0** — 검출이 셀이 아니라 **정의역**에서 옴을 실증
      (3) `DERIVE-TOPONLY`/`DERIVE-SHALLOW` 산출은 **관측 사실로 출력**한다.
          ★ 여전히 검출되는 witness 도 있다(그 결함이 얕은 정의역에도 발현하는 경우) —
            그 사실을 **숨기지 않고 그대로 적는다**. 없는 상실을 지어내지 않는다.
    """
    text, document, _pin = _load_target()

    for witness_name, builder in SWEEP_ABLATIONS[sweep_id]:
        patch = builder()
        with _patched_envelope_pin(**patch):
            halves = [h for h in _sweep_halves(document, text) if h.sweep == sweep_id]
            assert halves, f"{sweep_id} 반쪽 부재"

            full_detected, matrix = 0, {}
            for half in halves:
                _results, failures = _run_half(half)
                full_detected += len(failures)
                for deg_name, deg_filter in DEGENERATE_DOMAIN_FILTERS.items():
                    shrunk = deg_filter(half.domain)
                    _r2, f2 = _run_half(half, shrunk)
                    key = (deg_name, half.half)
                    matrix[key] = (len(shrunk), len(f2))

        print(f"  [음성 대조 {sweep_id} × {witness_name}] 정본 정의역 검출={full_detected}")
        for (deg_name, half_name), (size, detected) in sorted(matrix.items()):
            print(f"      {deg_name:16} {half_name:28} 정의역={size:5} 검출={detected}")

        # (1) witness 는 정본 정의역에서 **반드시 검출**된다 (born-broken witness 차단)
        assert full_detected > 0, (
            f"{sweep_id} 의 ablation target {witness_name} 이 **정본 정의역에서도 미검출** — "
            f"sweep 이 무력하거나 witness 가 born-broken 이다")
        # (2) 정의역이 0 이면 검출도 0 — 검출은 셀이 아니라 정의역에서 온다
        empty_detected = sum(d for (deg, _h), (_s, d) in matrix.items() if deg == "DERIVE-EMPTY")
        assert empty_detected == 0, f"DERIVE-EMPTY 에서 검출 {empty_detected} — 음성 대조 전제 붕괴"


def test_envelope_pin_swp_j_negative_control_redirect_misclassification():
    r"""★ `SWP-J` 의 음성 대조 — ablation = *"**redirect 3 을 표기로 오분류**"*.

    `SWP-J` 는 정의역이 대상 구조가 아니라 **직렬화기 시그니처**에 살아서 퇴화 *정의역* 축이
    형제 sweep 과 다르다. 대신 설계가 지목한 ablation 을 **실제로 주입**한다 — redirect 축을
    「표기(중립)」로 오분류하면 `ENV-4` **적용** 판별(#7)과 **전제 축**이 각각 무주공산이 되므로,
    그 오분류 아래에서 sweep 이 **불일치를 낸다**(= 검출)를 실증한다.
    """
    _text, document, _pin = _load_target()
    probes = _swp_j_probes()
    base = _swp_j_measure(document, probes)

    misclassified: Dict[str, set] = {}          # ★ redirect 3 을 통째로 「중립」으로 오분류
    detected = []
    for q in sorted(SWP_J_NONDEFAULT):
        with _patched_serialize_kwargs(q, SWP_J_NONDEFAULT[q]):
            variant = _swp_j_measure(document, probes)
        moved = {n for n in base if base[n] != variant[n]}
        if moved != misclassified.get(q, set()):
            detected.append((q, sorted(moved)))

    print(f"  [음성 대조 SWP-J × redirect-오분류] 검출 축={detected}")
    assert {q for q, _m in detected} == set(SWP_J_REDIRECT), (
        "redirect 축을 「표기」로 오분류했는데 sweep 이 그 사실을 검출하지 못했다: "
        f"{detected}")

    # ★ 정의역 declare — 설계 자유도 표의 `0/30` 은 **`separators`·`ensure_ascii` 행**에 붙은
    #   수치이고, `SWP-J` 로스터 행은 「중립 5 ∧ redirect 3」을 명시한다. 본 sweep 산출은
    #   양쪽과 일치한다. 단 본 probe set 은 **합성 값**(NaN·date)을 포함하므로, 그 값들이
    #   **실 대상에 부재**함을 실측해 「착지 형상의 verdict 는 불변」임을 함께 세운다.
    leaves = _all_leaf_paths(cut_envelope(document, JOB2))
    values = [_get_node_at_path(document, p) for p in leaves]
    assert not [v for v in values if isinstance(v, float) and v != v], "대상에 NaN 값 실재"
    assert not [v for v in values if isinstance(v, (datetime.date, datetime.datetime))], \
        "대상에 date/datetime 값 실재"
    print("  [SWP-J 정의역 declare] 실 대상 leaf 에 NaN 0 · date 0 — "
          "redirect 3 은 **합성 probe 정의역**에서만 이동한다 (착지 형상 verdict 불변)")


# ─────────────────────────────────────────────────────────────────────────────
# 로스터 완전성 (§8.B 「sweep 로스터」 ∧ `VU-4` 전칭 단위)
# ─────────────────────────────────────────────────────────────────────────────

# ★ 로스터는 **재현 규칙으로 지목**한다 — *"§8.B 피복표에서 역할 열이 `(sweep)` 인 행 전수"*.
#   현행 = `SWP-A`~`SWP-J` 10종. 각 id 는 담지 테스트 함수 1개와 결속된다.
SWEEP_ROSTER: Dict[str, str] = {
    "SWP-A": "test_envelope_pin_swp_a_applicable_leaf_universal",
    "SWP-B": "test_envelope_pin_swp_b_applicable_mapping_collision_universal",
    "SWP-C": "test_envelope_pin_swp_c_nonapplicable_jobs_other_universal",
    "SWP-D": "test_envelope_pin_swp_d_value_padding_absorbed_universal",
    "SWP-E": "test_envelope_pin_swp_e_nonabsorbed_padding_universal",
    "SWP-F": "test_envelope_pin_swp_f_datastructure_universal",
    "SWP-G": "test_envelope_pin_swp_g_value_kind_fidelity_universal",
    "SWP-H": "test_envelope_pin_swp_h_key_type_universal",
    "SWP-I": "test_envelope_pin_swp_i_text_layer_universal",
    "SWP-J": "test_envelope_pin_swp_j_serialization_notation_universal",
}


def test_envelope_pin_sweep_derivation_completeness():
    r"""**로스터 완전성** — `SWP-A`~`SWP-J` **10종 전건**이 실 담지 테스트로 존재하고, 정의역이
    **적용역 전체를 덮으며**, spine 이 **실제로 제외**돼 있는가.

    ★★ 구 판본은 `sweep_covered := mapping_nodes − SPINE_PATHS` 로 집합을 **구성한 뒤**
       `p ∈ SPINE ∨ p ∈ sweep_covered ∨ len(p) > 0` 을 단언했다 — 앞 두 항이 구성상 전체를
       덮으므로 **삼중 항진**이고, `_all_mapping_nodes` 를 `{()}` 로 파괴해도 통과했다.
       ⇒ 본 판본은 **독립 파생끼리 대조**한다(구성한 것을 확인하지 않는다).
    """
    text, document, _pin = _load_target()
    envelope = cut_envelope(document, JOB2)
    domains = _sweep_domains(envelope)

    # (1) 로스터 10종 전건이 **실재하는 담지 테스트**와 결속
    assert set(SWEEP_ROSTER) == {f"SWP-{c}" for c in "ABCDEFGHIJ"}, \
        f"로스터 id 집합 불일치: {sorted(SWEEP_ROSTER)}"
    for sweep_id, fn_name in sorted(SWEEP_ROSTER.items()):
        fn = globals().get(fn_name)
        assert callable(fn), f"{sweep_id} 담지 테스트 {fn_name} 부재"
        assert sweep_id in (fn.__doc__ or ""), f"{fn_name} docstring 이 {sweep_id} 를 지목하지 않는다"

    # (2) `SWP-A`~`SWP-I` 는 반쪽 등록 ∧ 정의역 비공허 / `SWP-J` 는 형태가 달라 별 담지
    halves = _sweep_halves(document, text)
    registered = {h.sweep for h in halves}
    assert registered == {f"SWP-{c}" for c in "ABCDEFGHI"}, \
        f"반쪽 등록 sweep 집합 불일치: {sorted(registered)}"
    assert "SWP-J" not in registered, "SWP-J 는 구조 정의역 sweep 이 아니다 (별 담지)"
    for half in halves:
        assert half.domain, f"{half.sweep} {half.half} 정의역 공허"

    # (3) **적용역 전체 피복** — 위치 4 범주가 각각 sweep 정의역에 담긴다 (여집합 0)
    covered_paths = set()
    for half in halves:
        covered_paths |= {_elem_path(e) for e in half.domain}
    census = (domains["leaves"] | domains["mapping_nodes"] | domains["sequences"]
              | {p for p, _k in domains["string_keys"]}
              | {p for p, _k in domains["nonstring_keys"]}
              | {p for p, _i in domains["bare_sequence_string_elements"]})
    uncovered = census - covered_paths
    assert not uncovered, f"sweep 정의역이 덮지 않는 적용역 위치: {sorted(uncovered, key=str)}"

    # (4) spine 이 **실제로 제외**됐다 (포함하면 정본이 born-RED 가 되는 자리)
    assert ("jobs",) not in domains["mapping_nodes"], "spine 합성 래퍼가 정의역에 남았다"
    assert ((), "jobs") not in domains["string_keys"], "spine 키(top-level jobs)가 정의역에 남았다"
    assert (("jobs",), JOB2) not in domains["string_keys"], "spine 키(JOB2)가 정의역에 남았다"

    # (5) **비-문자열 키 1종**을 이름 집합으로 pin (`SWP-E` 가 제외한 그 원소 — 카디널리티 형 금지)
    assert domains["nonstring_keys"] == {((), True)}, \
        f"비-문자열 키 이름 집합 불일치: {sorted(domains['nonstring_keys'], key=str)}"

    print(f"[PASS] 로스터 완전성 — sweep {len(SWEEP_ROSTER)}종 · 반쪽 {len(halves)} · "
          f"피복 위치 {len(covered_paths)} · 미피복 0")


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
                probed1 = _inject_probe_at_node(document, node_path, "__PROBE_KIND__", v1)
                probed2 = _inject_probe_at_node(document, node_path, "__PROBE_KIND__", v2)

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

    # ★★ 칸 기대치는 **파생식**이다 — 구 판본의 `14`/`28`/`42`/`56` **리터럴을 제거**한다
    #   (파생 규칙이 주석에만 살면 워크플로 형상이 바뀔 때 표가 조용히 거짓이 된다).
    #
    #   기대치 = (변종별 상수) × `num_nodes`
    #     (a) 상수 = 그 변종이 **흡수하는 값 종류 수** = `len(S) − 변화종수`
    #     (b) 상수 = 그 변종이 **구별하지 못하는 쌍 수**
    #   ★ 두 상수는 **변종 술어의 성질**이지 대상 형상의 성질이 아니다 ⇒ 형상이 바뀌면
    #     `num_nodes`(∧ `len(S)`) 만 움직이고 상수는 불변이다.
    #   ★★ 그리고 이 상수들은 표에만 살지 않는다 — 아래에서 **최소 문서(mapping node 1개)**
    #     위에서 **독립 재측정**해 대조한다. 상수가 표에만 살면 그것이 곧 「손으로 적은 열거」다.
    VARIANT_ABSORBED_KINDS = {          # (a) 흡수 값 종류 수
        "정본": 0,
        "V-DROPNULL": 1,                # None
        "V-DROPEMPTY": 3,               # {} · [] · () (정규화 후 [] 로 도달)
        "V-DROPEMPTYSTR": 2,            # "" · 공백만 문자열(strip 후 "")
        "V-DROPFALSE": 1,               # False (★identity 술어 — `not v` 는 *다른 변종*)
        "V-NUMCOERCE": 0,
        "V-NFC": 0,
        "V-NULLTOMAP": 0,
        "V-EMPTYSEQSTR": 0,
    }
    VARIANT_COLLAPSED_PAIRS = {         # (b) 구별 실패 쌍 수
        "정본": 0,
        "V-DROPNULL": 0,
        "V-DROPEMPTY": 2,
        "V-DROPEMPTYSTR": 0,
        "V-DROPFALSE": 0,
        "V-NUMCOERCE": 2,               # (0,0.0) · (1,1.0)
        "V-NFC": 4,
        "V-NULLTOMAP": 1,               # (None,{})
        "V-EMPTYSEQSTR": 4,             # ★`()` 포함 구성 — `list` 단독은 흡수쌍을 가르는 *다른 변종*
    }
    assert set(VARIANT_ABSORBED_KINDS) == {v for v, _p, _q in variants}, "변종 집합 불일치 (a)"
    assert set(VARIANT_COLLAPSED_PAIRS) == {v for v, _p, _q in variants}, "변종 집합 불일치 (b)"

    expected_table_a = {v: n * num_nodes for v, n in VARIANT_ABSORBED_KINDS.items()}
    expected_table_b = {v: n * num_nodes for v, n in VARIANT_COLLAPSED_PAIRS.items()}

    # ★ 독립 재측정 — 최소 문서(mapping node **1개**) 위에서 변종 상수를 다시 얻는다.
    #   14 node 대상 측정과 **다른 입력**이므로 두 산출의 일치가 곧 「상수 × node 수」 파생식의
    #   근거다(둘이 갈리면 파생식 자체가 거짓이므로 여기서 먼저 터진다).
    pair_idx = _distinguishing_pair_indices(S)

    def _minimal_variant_profile(pre, post):
        base_doc = {"jobs": {JOB2: {"anchor": "x"}}}
        ref_min = _compute_sha_with_hooks(base_doc, JOB2, pre_val=pre, post_map=post)
        shas = []
        for value in S:
            probe_doc = copy.deepcopy(base_doc)
            probe_doc["jobs"][JOB2]["__PROBE_KIND__"] = value
            shas.append(_compute_sha_with_hooks(probe_doc, JOB2, pre_val=pre, post_map=post))
        absorbed = sum(1 for sha in shas if sha == ref_min)
        collapsed = sum(1 for i, j in pair_idx if shas[i] == shas[j])
        return absorbed, collapsed

    for vname, pre, post in variants:
        measured = _minimal_variant_profile(pre, post)
        declared = (VARIANT_ABSORBED_KINDS[vname], VARIANT_COLLAPSED_PAIRS[vname])
        assert measured == declared, (
            f"{vname}: 변종 상수가 최소 문서 재측정과 어긋난다 — "
            f"declared(흡수,붕괴)={declared} measured={measured}")
    print(f"  [변종 상수 독립 재측정] 9 변종 × (흡수, 붕괴) 전건 일치 "
          f"(파생식 = 상수 × num_nodes={num_nodes})")

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


# ─────────────────────────────────────────────────────────────────────────────
# 전제 witness (`P-E1`~`P-E4`) ∧ CLI 3-verdict ∧ 대조기 술어
# ─────────────────────────────────────────────────────────────────────────────

def test_envelope_pin_premise_witnesses_pe1_to_pe4():
    r"""전제 `P-E1`~`P-E4` witness — `EnvelopeError.error_kind` **4종 전수**.

    ★ `P-E1`~`P-E3` 는 `cut_envelope` 가 직접 raise 한다.
    ★ `P-E4`(`envelope_meta_error`)는 **라이브러리가 raise 하지 않는다** — CLI `main()` 의
      광역 포획이 그 등급을 고정한다(전 구간 미포착 예외 = `exit 2`). ⇒ 이 kind 의 실
      witness 는 형제 CLI 테스트가 낸다(여기서는 어휘 집합 ∧ 광역 포획 대상 예외 실재만).
    ★ 정직 기재 — 4종을 전부 `pytest.raises` 로 세우려고 `EnvelopeError("envelope_meta_error", …)`
      를 **직접 생성해 assert 하는 것은 항진**이다(내가 만든 값을 내가 확인). 하지 않는다.
    """
    # P-E1 — top-level 이 mapping 아님
    with pytest.raises(EnvelopeError) as e1:
        compute_envelope_from_document(["not", "a", "mapping"], JOB2)
    assert e1.value.error_kind == "envelope_root_not_mapping"

    # P-E2 — `jobs` 부재 ∧ `jobs` 비-mapping (연언이라 위반 kind 는 1종)
    with pytest.raises(EnvelopeError) as e2a:
        compute_envelope_from_document({"name": "x"}, JOB2)
    assert e2a.value.error_kind == "envelope_jobs_missing"
    with pytest.raises(EnvelopeError) as e2b:
        compute_envelope_from_document({"jobs": "not-a-mapping"}, JOB2)
    assert e2b.value.error_kind == "envelope_jobs_missing"

    # P-E3 — JOB2 ∉ jobs
    with pytest.raises(EnvelopeError) as e3:
        compute_envelope_from_document({"jobs": {"other-job": {}}}, JOB2)
    assert e3.value.error_kind == "envelope_job_absent"

    # P-E4 — 「전 구간 미포착 예외」의 in-process 실재 확인 (등급 고정은 CLI 소관)
    #   (i) `ENV-3` 접힘 (ii) JSON 직렬화 불가형(비인용 date **값**)
    collision_doc = {"jobs": {JOB2: {"a": 1}}, 2: "COLL", "2": "COLL"}
    sha_c, detail_c = _envelope_outcome(collision_doc, JOB2)
    assert sha_c is None and "collision" in detail_c, f"접힘이 예외로 종결되지 않았다: {detail_c}"
    date_doc = {"jobs": {JOB2: {"when": datetime.date(2026, 8, 19)}}}
    sha_d, detail_d = _envelope_outcome(date_doc, JOB2)
    assert sha_d is None and "TypeError" in detail_d, f"직렬화 불가형이 통과했다: {detail_d}"

    # 어휘 집합 — 신규 어휘 발명 금지 (4종이 값 공간 전부)
    assert set(ENVELOPE_ERROR_KINDS) == {
        "envelope_root_not_mapping", "envelope_jobs_missing",
        "envelope_job_absent", "envelope_meta_error",
    }
    with pytest.raises(ValueError):  # self-guard — 미지 kind 는 생성 자체가 금지
        EnvelopeError("no_such_kind", "x")

    print(f"[PASS] P-E1~P-E4 witness — kinds={sorted(ENVELOPE_ERROR_KINDS)}")


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, ENVELOPE_PIN_SCRIPT, *args],
        capture_output=True, text=True, encoding="utf-8", cwd=REPO_ROOT,
    )


def test_envelope_pin_cli_three_verdicts():
    r"""CLI **3-verdict 전건** — `exit 0`(GREEN) / `exit 1`(RED) / `exit 2`(meta-error).

    ★★ **exit code 단독 판정 금지**. interpreter 표준 exit(파일 부재 `2` 등)이 도메인
       `exit 2` 와 **우연히 일치**하면 fork 가 안 일어나도 통과하는 거짓 GREEN 이 된다.
       ⇒ 매 갈래에서 **도메인 고유 stdout/stderr sentinel 을 병행 assert** 한다
       (`(returncode, sentinel)` 튜플 동시 판정 — 부분일치 차단):
         exit 0 → stdout == 64자 핀 hex  ·  exit 1 → stderr payload `verdict == "RED"`
         exit 2 → stderr payload `error_kind ∈ ENVELOPE_ERROR_KINDS`
       ★ 미 fork 시 stdout 은 빈 문자열 / stderr 은 interpreter 에러 텍스트라 `json.loads`
         가 실패한다 ⇒ sentinel assert 가 genuine 실패한다(실측 확인).
    """
    # ── exit 0 (GREEN) — 핀 대조 일치
    r0 = _run_cli(WF_PATH, "--job2", JOB2, "--expect", PIN_ENVELOPE_SHA256)
    assert (r0.returncode, r0.stdout.strip()) == (0, PIN_ENVELOPE_SHA256), \
        f"exit 0 갈래 실패: rc={r0.returncode} stdout={r0.stdout!r} stderr={r0.stderr!r}"

    def _payload(proc, branch: str) -> Dict[str, Any]:
        r"""stderr 마지막 줄을 도메인 payload 로 파싱 — ★**rc 를 먼저 단언**한다.

        rc 를 확인하지 않고 파싱하면 rc 가 어긋난 순간 `IndexError`/`JSONDecodeError` 가 나서
        **RED 의 사유가 「단언 실패」가 아니라 「하네스 사망」으로 흐려진다**
        (이 Story 의 규율 — *"RED 를 검출로 읽기 전에 사유를 확인하라"*).
        """
        tail = proc.stderr.strip().splitlines()
        assert tail, (f"{branch}: stderr 가 비었다 — rc={proc.returncode} "
                      f"stdout={proc.stdout.strip()!r} (도메인 payload 미방출)")
        return json.loads(tail[-1])

    # ── exit 1 (RED) — 핀 불일치
    r1 = _run_cli(WF_PATH, "--job2", JOB2, "--expect", "0" * 64)
    assert r1.returncode == 1, \
        f"exit 1 갈래 rc 불일치: rc={r1.returncode} stdout={r1.stdout.strip()!r} stderr={r1.stderr.strip()!r}"
    payload1 = _payload(r1, "exit 1")
    assert (payload1["verdict"], payload1["actual"]) == ("RED", PIN_ENVELOPE_SHA256), \
        f"exit 1 갈래 payload 실패: {payload1}"

    # ── exit 2 (meta-error) — `P-E4` 입력 읽기 구간 (파일 부재)
    r2 = _run_cli(os.path.join(REPO_ROOT, "no", "such", "workflow.yml"), "--job2", JOB2)
    assert r2.returncode == 2, \
        f"exit 2(P-E4) 갈래 rc 불일치: rc={r2.returncode} stderr={r2.stderr.strip()!r}"
    assert _payload(r2, "exit 2(P-E4)")["error_kind"] == "envelope_meta_error"

    # ── exit 2 (meta-error) — `P-E3` 전제 위반 (job 부재)
    r3 = _run_cli(WF_PATH, "--job2", "no-such-job")
    assert r3.returncode == 2, \
        f"exit 2(P-E3) 갈래 rc 불일치: rc={r3.returncode} stderr={r3.stderr.strip()!r}"
    assert _payload(r3, "exit 2(P-E3)")["error_kind"] == "envelope_job_absent"

    # ── 채취 모드 — `--expect` 미지정이면 GREEN 을 **주장하지 않는다**(sha 만 낸다)
    r4 = _run_cli(WF_PATH, "--job2", JOB2)
    assert (r4.returncode, r4.stdout.strip()) == (0, PIN_ENVELOPE_SHA256)

    print("[PASS] CLI 3-verdict — exit 0 / 1 / 2 전건 (sentinel 병행 assert)")


def test_envelope_pin_matches_predicate():
    r"""대조기 술어 `Envelope.matches()` **직접 호출** — 양성 ∧ 음성 공존.

    ★ 이 술어가 어디서도 호출되지 않으면 `return True` 오구현이 **전 스위트를 통과**한다
      (핀 대조 테스트는 `env.sha256 == PIN` 을 직접 비교하므로 `matches` 를 우회한다).
    """
    env = compute_envelope(WF_PATH, JOB2)

    # 양성 — 일치
    assert env.matches(PIN_ENVELOPE_SHA256) is True
    # 흡수 축 — 대소문자·양끝 공백은 흡수한다 (docstring 계약)
    assert env.matches("  " + PIN_ENVELOPE_SHA256.upper() + "\n") is True
    # ★ 음성 — 불일치는 반드시 False (`return True` 오구현 판별자)
    assert env.matches("0" * 64) is False
    assert env.matches(PIN_ENVELOPE_SHA256[:-1] + "0") is False
    assert env.matches("") is False

    print("[PASS] matches() — 양성 3 ∧ 음성 3 공존")


if __name__ == "__main__":
    # ★ 직접 실행도 **pytest 에 위임**한다 — 손으로 적은 호출 목록은 신규 테스트를 조용히
    #   빠뜨리는 자리이고(이 파일이 이미 담지하는 결함 형태 그 자체), parametrize 된
    #   음성 대조는 인자 없이 호출할 수도 없다.
    sys.exit(pytest.main([__file__, "-q", "-s"]))
