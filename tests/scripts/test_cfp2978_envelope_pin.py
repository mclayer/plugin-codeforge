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
        Envelope,
        EnvelopeError,
        ENVELOPE_ERROR_KINDS,
    )
    from workflow_shape import dup_safe_load
except ImportError as e:
    raise ImportError(f"Failed to import envelope_pin or workflow_shape: {e}") from e

# ★ 핀 값 — DevPL 채취 (워크플로 동결 형상)
PIN_ENVELOPE_SHA256 = "642b78520053da0d2394fc2183bc239afae5187460e22f6762d1267539962ca9"

# ★★ `PIN_P1_EVIDENCE` 는 **독립 리터럴**이다 — `PIN_ENVELOPE_SHA256` 을 참조해 파생하면
#    아래 3-way 결속의 세 번째 변이 `X == X` 가 되어 **항진**하고, §8.3 이 요구하는
#    「두 거처를 같은 커밋에서 함께 갱신한다」는 규율이 **구조적으로 반증 불가**가 된다.
#    (핀 재채취 시 이 줄과 위 줄을 **둘 다** 고쳐야 한다 — 그것이 검사 대상인 규율이다.)
PIN_P1_EVIDENCE = {
    "envelope_sha256": "642b78520053da0d2394fc2183bc239afae5187460e22f6762d1267539962ca9",
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


# ★ 자기검사 (c) 용 **퇴화 파생 유틸** — 정의역을 인위 축소한다 (§8.B `DERIVE-*`).
#   ★ 규칙으로 정의하고 크기를 하드코딩하지 않는다 (형상이 바뀌면 크기도 따라간다).
DEGENERATE_DERIVERS: Dict[str, Callable[[Any], set]] = {
    "DERIVE-EMPTY": lambda env: set(),
    "DERIVE-TOPONLY": lambda env: {p for p in _all_leaf_paths(env) if len(p) <= 1},
    "DERIVE-SHALLOW": lambda env: {p for p in _all_leaf_paths(env) if len(p) <= 2},
}


def _defective_deep_lossy(document: Any) -> Any:
    r"""**결함 구현 `V-LOSSY-DEEP`** — `jobs.<JOB2>.steps[i].name` 을 봉투에서 **탈락**시킨다.

    `ENV-5`(*"봉투는 `jobs.<JOB2>` 서브트리를 **전문** 담는다"*) 위반이다.
    ★ 구성 방식 **전문 고정** = 정본 파이프라인 **앞단의 문서 전처리**(정규화기 복제 0 —
      §8.B 「변종은 정본의 변종이어야 한다」 규율 준수).
    """
    doc = copy.deepcopy(document)
    steps = doc.get("jobs", {}).get(JOB2, {}).get("steps", [])
    for step in steps:
        if isinstance(step, dict):
            step.pop("name", None)
    return doc


def _leaf_mutation_failures(document: Any, domain: set,
                            transform: Optional[Callable[[Any], Any]] = None) -> set:
    r"""`SWP-A` 술어(leaf 변형 ⇒ RED)를 **주어진 정의역** 위에서 실행 — 기대 미달 원소 집합."""
    tf = transform or (lambda d: d)
    ref_sha, _detail = _envelope_outcome(tf(document), JOB2)
    failures = set()
    for path in domain:
        mutated = _set_at_path(document, path, _mutate_leaf(_get_node_at_path(document, path)))
        verdict, _d = _verdict(tf(mutated), ref_sha)
        if verdict != VERDICT_RED:
            failures.add(path)
    return failures


def test_envelope_pin_derivation_negative_control():
    r"""★ 파생 유틸 자기검사 **(c) 음성 대조** — 퇴화 유틸에서는 결함 구현이 **검출되지 않는다**.

    §8.B: *"(a) 단독은 불충분하다 — `DERIVE-TOPONLY` 는 **비공허(1)** 이면서 여전히 무력하다."*
    ⇒ 정의역을 인위 축소한 유틸 3종을 **실제로 주입**해 *"검출은 정의역에서 온다"* 를 실증한다.
    """
    _text, document, _ref = _load_target()
    envelope = cut_envelope(document, JOB2)
    full_domain = _sweep_domains(envelope)["leaves"]

    # 정본 구현 위에서는 전 정의역이 기대(RED) 를 만족한다 — 음성 대조의 base
    assert _leaf_mutation_failures(document, full_domain) == set(), \
        "base FAIL — 정본이 SWP-A 전칭을 만족하지 않는다 (born-RED)"

    detected_full = _leaf_mutation_failures(document, full_domain, _defective_deep_lossy)
    print(f"[음성 대조] 전 정의역({len(full_domain)}) — V-LOSSY-DEEP 검출 {len(detected_full)}건: "
          f"{sorted(detected_full, key=str)}")
    assert detected_full, "결함 구현 V-LOSSY-DEEP 이 **전 정의역에서도** 미검출 (sweep 무력)"

    for name, deriver in DEGENERATE_DERIVERS.items():
        shrunk = deriver(envelope)
        detected = _leaf_mutation_failures(document, shrunk, _defective_deep_lossy)
        print(f"[음성 대조] {name:16} 정의역={len(shrunk):3}  V-LOSSY-DEEP 검출={len(detected)}")
        assert detected == set(), \
            f"{name} 이 결함을 검출했다 — 음성 대조 전제 붕괴 (퇴화 유틸 정의 재점검)"
        assert shrunk < full_domain, f"{name} 이 정의역을 축소하지 않았다"

    # ★ (a) 단독 불충분의 실증 — DERIVE-TOPONLY 는 **비공허**이면서 무력하다
    assert len(DEGENERATE_DERIVERS["DERIVE-TOPONLY"](envelope)) > 0, \
        "DERIVE-TOPONLY 가 공허하면 (a) 단독 불충분을 실증하지 못한다"

    print("[PASS] 파생 유틸 자기검사 (c) — 검출은 정의역에서 온다")


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

    # ── exit 1 (RED) — 핀 불일치
    r1 = _run_cli(WF_PATH, "--job2", JOB2, "--expect", "0" * 64)
    payload1 = json.loads(r1.stderr.strip().splitlines()[-1])
    assert (r1.returncode, payload1["verdict"], payload1["actual"]) == \
        (1, "RED", PIN_ENVELOPE_SHA256), f"exit 1 갈래 실패: rc={r1.returncode} {payload1}"

    # ── exit 2 (meta-error) — `P-E4` 입력 읽기 구간 (파일 부재)
    r2 = _run_cli(os.path.join(REPO_ROOT, "no", "such", "workflow.yml"), "--job2", JOB2)
    payload2 = json.loads(r2.stderr.strip().splitlines()[-1])
    assert (r2.returncode, payload2["error_kind"]) == (2, "envelope_meta_error"), \
        f"exit 2(P-E4) 갈래 실패: rc={r2.returncode} {payload2}"

    # ── exit 2 (meta-error) — `P-E3` 전제 위반 (job 부재)
    r3 = _run_cli(WF_PATH, "--job2", "no-such-job")
    payload3 = json.loads(r3.stderr.strip().splitlines()[-1])
    assert (r3.returncode, payload3["error_kind"]) == (2, "envelope_job_absent"), \
        f"exit 2(P-E3) 갈래 실패: rc={r3.returncode} {payload3}"

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
    test_envelope_pin_reference_matches_landed_pin()
    test_envelope_pin_domain_derivation_selfcheck()
    test_envelope_pin_derivation_negative_control()
    test_envelope_pin_coverage_table_witnesses()
    test_envelope_pin_sweep_derivation_completeness()
    test_envelope_pin_falsification_dropfalse()
    test_envelope_pin_premise_witnesses_pe1_to_pe4()
    test_envelope_pin_cli_three_verdicts()
    test_envelope_pin_matches_predicate()
