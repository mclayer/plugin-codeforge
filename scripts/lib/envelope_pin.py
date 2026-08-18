#!/usr/bin/env python3
"""CFP-2978 `W-21` — 봉투(envelope) 정규화 절차의 **유일 정본** (참조 구현).

설계 SSOT = Change Plan `cfp-2978-sentinel-copy-currency-gate.md` **§8.B**
(「봉투 계약 — 참조 구현 정본」 · 성질 `ENV-1`~`ENV-8` · 전제 `P-E1`~`P-E4` ·
 「봉투 spine declare」 · 「자유도 declare」 · 「변종 정의 못박기」).

이 모듈이 지는 책무 2가지 (`W-21` 행):
  (i)  대상 workflow 파일 경로 + JOB2 이름 → **봉투 문자열과 그 sha256** 산출
  (ii) `PIN_ENVELOPE_SHA256` **채취기 겸 대조기** (CLI 진입점)

★ **본 모듈은 핀 값을 보유하지 않는다.** `PIN_ENVELOPE_SHA256` 리터럴의 거처는
  담지 테스트(`tests/scripts/test_cfp2978_workflow_shape.py` — `W-16.S`)이며,
  이 모듈은 **산출자이자 대조기**일 뿐이다. 고정 수치를 이 파일에 박으면
  산출자와 기대값이 같은 파일에서 자기정합을 이루어 `UM-16`(참조 구현이 결함을
  포함한 채 정본이 되는 위험)을 **키운다**.

────────────────────────────────────────────────────────────────────────────────
봉투 정의 (§8.B — 집합 표기 그대로)

    envelope := { k: doc[k] | k ∈ doc.keys(), k ≠ "jobs" }
              ∪ { "jobs": { JOB2: doc["jobs"][JOB2] } }

정규화 → 직렬화 → 해시 (순서가 계약이다 — 「봉투 절단 ↔ 정규화 순서」 자유도는
§8.B 가 `ENV-5` 비적용역으로 귀속시켰고 `SWP-C` 가 판별한다. **절단이 먼저다**):

  1. `dup_safe_load` 로 문서 전문 파싱          … `ENV-1`  (재규정 금지 — 승계만)
  2. 봉투 절단 (위 집합 정의)                    … `ENV-5`
  3. 값 정규화: **mapping 값 위치의 str 만** `.strip()` … `ENV-2` (독법 `A`)
  4. 키 문자열화 + 접힘(충돌) fail-closed        … `ENV-3` · `ENV-6`
  5. `json.dumps(sort_keys=True, ensure_ascii=False, separators=(",", ":"))`
                                                 … `ENV-4` · `ENV-7` · `ENV-8`
  6. UTF-8 인코딩 → `sha256` → 64자 소문자 hex

★ 3 의 정의역(독법 `A`) — 이것이 iter9/iter10 이 두 라운드에 걸쳐 확정한 축이다:
    적용   = **모든 mapping 의 값 위치** (sequence 하위에 중첩된 mapping 의 값 포함
             — 예 `steps[i].run` · `steps[i].name` · `steps[i].with.<k>`,
             활성화 봉투의 값 `runs-on`·`if` 도 적용역 안)
    비적용 = **키 위치** (rename 이므로 RED) ∧ **sequence 의 직접 원소**
             (bare scalar element — 예 `on.pull_request.types[i]`, 활성화 축 P0)

★ 4 의 렌더러(`ENV-6`) — 성질은 **함수 이름이 아니라 렌더 동일성**이다:
    "직렬화기가 **값** 위치에 쓰는 렌더를 **비-문자열 키**에 재사용한다".
    ⇒ `str` 키는 **무변환**(`json.dumps` 를 씌우면 `runs-on` → `"runs-on"` 로
      따옴표가 덧붙어 `C₀` 가 어긋나고 충돌도 미발동한다), 비-문자열 키만
      `json.dumps(k, ensure_ascii=False)`.  `str(k)` 계열은 **금지**
      (`str(True)` == `'True'` ≠ `'true'` ⇒ `ENV-3` 의 fail-closed 가 한 번도
       발동하지 않아 판별 셀이 장식으로 퇴행한다 — 변종 `V-STRKEY`/`V-STRBOOL`).

────────────────────────────────────────────────────────────────────────────────
verdict 3값 (혼동 금지 — `exit 0` 은 "예외가 안 났다"가 아니라 "핀과 같다"이다)

  GREEN  = 산출 sha == 기대 핀            → exit 0
  RED    = 산출 sha != 기대 핀            → exit 1
  exit 2 = **meta-error** — GREEN 도 RED 도 아님. 전제 `P-E1`~`P-E4` 위반,
           키 접힘(`ENV-3` fail-closed), JSON 직렬화 불가형(예 비인용 date 값),
           그리고 **입력 읽기부터 핀 산출까지 전 구간의 미포착 예외 전건**.

전제 (§8.B — 위반 시 exit 2):
  `P-E1` top-level 이 mapping
  `P-E2` `"jobs"` 존재 ∧ mapping
  `P-E3` JOB2 ∈ jobs
  `P-E4` **입력 읽기부터 핀 산출까지 참조 구현이 실행되는 전 구간**에서
         미포착 예외 0 (파일 부재의 `FileNotFoundError` 도 이 정의역 안이다 —
         구 문면이 "①~④ 에서"로 좁혀 그 구간을 회수하지 못했던 것이 iter9 DR9-6)
  ★ `P-E5`(`|jobs| ≥ 2`) · `P-E6`(sweep 비공허)는 **담지 테스트 소관**이다.
    이 모듈은 범용 산출자이므로 job 다중도를 강제하지 않는다.

자유도 (§8.B 「자유도 declare」 — 성질이 결정하지 않는 축. 본 구현이 **택한** 값):
  `separators=(",", ":")` · `ensure_ascii=False`  … verdict 중립, `C₀` 값만 이동
      (실측 — 세 표기에서 피복 probe 8종 전건 verdict 동일, `SWP-J` 0/30)
  `.strip()` 문자류 = **파이썬 기본**(유니코드 공백 전체). ASCII 한정 변종은
      `C₀` 동일이면서 NBSP padding 에서 갈린다 (§8.B class (c) 자유도)
  `default` 미지정 · `allow_nan` 기본 = **전제 축으로 redirect** (자유도 아님) —
      `default=str` 를 주면 date **값**의 `exit 2` 전제가 무력화된다.
  `cls`(값 렌더러) = 치역이 열려 있어 전수 측정 불가 — `UM-16` 잔여로 declare.

────────────────────────────────────────────────────────────────────────────────
재현 규칙 (★고정 수치를 코드·주석에 박지 않는다 — 산출 명령만 적는다)

  핀 채취(현재 형상의 sha 를 얻는다):
    python scripts/lib/envelope_pin.py .github/workflows/parallel-work-sentinel-check.yml \
        --job2 parallel-work-sentinel-test

  핀 대조(GREEN/RED 판정):
    python scripts/lib/envelope_pin.py <workflow.yml> --job2 <JOB2> --expect <64hex>

  봉투 전문 확인(재유도·디버깅):
    python scripts/lib/envelope_pin.py <workflow.yml> --job2 <JOB2> --print-envelope

★ **핀 재채취 시점** (§5.1 `W-21` 착지 순서 결속): `PIN_ENVELOPE_SHA256` 은 본
  참조 구현의 산출로만 채취한다(수기 계산·타 구현 산출 금지). 채취는
  (a) `W-3d`(V1b) ∧ (b) node-ID 로스터 증설 ∧ (c) job2 pytest 파일 목록 배선이
  **전건 착지한 이후 형상**에서 한다. sweep 은 테스트 면이라 봉투를 바꾸지
  않으므로 **재채취 사유가 아니다**.

CLI:
    python scripts/lib/envelope_pin.py <workflow.yml> --job2 <JOB2>
        [--expect <sha256>] [--print-envelope] [--json]
      exit 0 → GREEN (stdout = sha256, `--expect` 미지정이면 채취 성공)
      exit 1 → RED   (핀 불일치 — stderr 에 expected/actual)
      exit 2 → meta-error (stderr 에 `{"error_kind": …}`)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

# ── `dup_safe_load` 는 `workflow_shape.py`(W-13) 가 **정의하는 쪽**이고, 본 모듈이
#    **import 주체**다. `workflow_shape.py` 자신은 수정 0 (재설계 경계 OUT).
#    ★ 파싱·중복 키·merge 의미론의 정본은 그 모듈의 소스 주석이며 여기서
#      재규정하지 않는다 (`ENV-1` — 재규정이 iter9 DR9-1 의 발생원이었다).
try:  # pragma: no cover - import path 분기
    from workflow_shape import dup_safe_load  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from workflow_shape import dup_safe_load  # noqa: E402


# ── 오류 계약 ────────────────────────────────────────────────────────────────
#  신규 어휘 발명 금지 — 아래 4종이 값 공간 전부다.
ENVELOPE_ERROR_KINDS = (
    "envelope_root_not_mapping",   # P-E1
    "envelope_jobs_missing",       # P-E2
    "envelope_job_absent",         # P-E3
    "envelope_meta_error",         # P-E4 (전 구간 미포착 예외 · 직렬화 불가 · 접힘)
)

#  직렬화 표기 — §8.B 「자유도 declare」가 verdict 중립으로 실증한 축이나,
#  `C₀` 값을 결정하므로 **한 곳에서만** 정한다 (두 곳에 적으면 갈린다).
_JSON_SERIALIZE_KWARGS: Dict[str, Any] = {
    "sort_keys": True,
    "ensure_ascii": False,
    "separators": (",", ":"),
}
#  `ENV-6` — 키 렌더는 값 렌더와 **같은 표기**를 재사용한다 (렌더 동일성이 성질).
_JSON_KEY_KWARGS: Dict[str, Any] = {
    "ensure_ascii": _JSON_SERIALIZE_KWARGS["ensure_ascii"],
}


class EnvelopeError(Exception):
    """전제 `P-E1`~`P-E3` 위반. CLI 경로에서 exit 2 로 번역된다 (exit 0 금지)."""

    def __init__(self, error_kind: str, message: str, path: Optional[str] = None) -> None:
        super().__init__(message)
        if error_kind not in ENVELOPE_ERROR_KINDS:  # 어휘 발명 방지 self-guard
            raise ValueError(f"unknown error_kind: {error_kind!r}")
        self.error_kind = error_kind
        self.message = message
        self.path = path

    def to_payload(self) -> Dict[str, Any]:
        return {"error_kind": self.error_kind, "message": self.message, "path": self.path}


# ── 반환형 ───────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Envelope:
    """봉투 산출 1건.

    `text`  — 정규화·직렬화된 봉투 문자열 (UTF-8 인코딩 **이전**의 str)
    `sha256`— `text.encode("utf-8")` 의 sha256, 64자 **소문자** hex
    """

    job2: str
    text: str
    sha256: str
    path: Optional[str] = None

    def matches(self, expected_sha256: str) -> bool:
        """대조기 술어 — GREEN 판정. 대소문자·공백 차이는 흡수한다."""
        return self.sha256 == expected_sha256.strip().lower()


# ── 정규화 (`ENV-2` 독법 `A` · `ENV-3` · `ENV-6` · `ENV-7` · `ENV-8`) ─────────
#
#  훅 2종은 **변종(witness) 구성 전용**이다. 정본 경로에서는 둘 다 `None` 이고
#  그때 동작은 훅이 없는 코드와 **완전히 동일**하다. 훅을 두는 이유는 §8.B
#  「변종 정의 못박기」가 witness 를 **훅 위치로 못박았기** 때문이다
#  (`V-DROPEMPTY` = `post_map` · `V-NULLTOMAP`/`V-EMPTYSEQSTR` = `pre_val`).
#  훅이 없으면 담지 테스트가 정규화기를 통째로 복제해야 하고, 그 순간
#  witness 는 "정본의 변종"이 아니라 **다른 함수**가 된다 (= 표의 수치가
#  재현되지 않는 정확히 그 실패 형태).
#
#    `pre_val(v) -> v'`   : **mapping 값 위치**에서 정규화 **직전**
#    `post_map(m) -> m'`  : 한 mapping 의 키 렌더·충돌검사·값 정규화가 끝난 **직후**
#
def _render_key(key: Any) -> str:
    """`ENV-6` — 값 위치 렌더를 비-문자열 키에 재사용한다.

    ★ `str` 키는 무변환. 비-문자열 키만 `json.dumps` — 이 비대칭이 성질이다.
      직렬화 불가형(예 비인용 date)은 여기서 `TypeError` 로 종결한다 → exit 2.
    """
    if isinstance(key, str):
        return key
    return json.dumps(key, **_JSON_KEY_KWARGS)


def _normalize_mapping(
    node: Dict[Any, Any],
    *,
    pre_val: Optional[Callable[[Any], Any]],
    post_map: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]],
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in node.items():
        rendered = _render_key(key)
        if rendered in out:
            # `ENV-3` — 접힘은 **흡수 금지**. 흡수하면 한 키가 다른 키를 조용히
            # 덮어 봉투가 원 문서를 담지 않게 된다 (오라클 우회).
            raise ValueError(f"post-normalization key collision: {rendered!r}")
        if pre_val is not None:
            value = pre_val(value)
        out[rendered] = _normalize_map_value(value, pre_val=pre_val, post_map=post_map)
    if post_map is not None:
        out = post_map(out)
    return out


def _normalize_map_value(
    value: Any,
    *,
    pre_val: Optional[Callable[[Any], Any]],
    post_map: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]],
) -> Any:
    """mapping **값 위치** — `ENV-2` 적용역. str 이면 양 끝 공백을 흡수한다."""
    if isinstance(value, str):
        # ★ "선행·후행" = **양 끝만**. 내부 공백 런은 정규화 대상이 아니다
        #   (`CTS-2` 가 그 판정을 RED 로 고정 — 변종 `V-COLLAPSE`).
        return value.strip()
    if isinstance(value, dict):
        return _normalize_mapping(value, pre_val=pre_val, post_map=post_map)
    if isinstance(value, (list, tuple)):
        return _normalize_sequence(value, pre_val=pre_val, post_map=post_map)
    return value


def _normalize_sequence(
    node: Any,
    *,
    pre_val: Optional[Callable[[Any], Any]],
    post_map: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]],
) -> List[Any]:
    """sequence — `ENV-2` **비적용역** ∧ `ENV-7` 다중도 보존.

    ★ 직접 원소가 str 이면 **건드리지 않는다**(독법 `A`). 여기서 strip 하면
      활성화 축(`on.pull_request.types`)이 흡수돼 P0 가 새어 나간다(독법 `A0`).
    ★ 중복 제거 금지 — 같은 값이 두 번 나오면 **두 번인 채로** 담는다
      (변종 `V-SEQDEDUP` 이 정확히 이 지점을 깬다). 길이도 보존한다.
    ★ tuple(PyYAML 이 `!!omap` 등에서 만든다)은 list 로 되돌린다 — `json.dumps`
      가 어차피 배열로 렌더하므로 `[]`(list) ~ `()`(tuple) 은 **흡수쌍**이다.
    """
    out: List[Any] = []
    for element in node:
        if isinstance(element, str):
            out.append(element)
        elif isinstance(element, dict):
            out.append(_normalize_mapping(element, pre_val=pre_val, post_map=post_map))
        elif isinstance(element, (list, tuple)):
            out.append(_normalize_sequence(element, pre_val=pre_val, post_map=post_map))
        else:
            out.append(element)
    return out


# ── 봉투 절단 (`ENV-5`) ──────────────────────────────────────────────────────
def cut_envelope(document: Any, job2: str, *, path: Optional[str] = None) -> Dict[Any, Any]:
    """파싱된 문서에서 봉투를 **절단**한다 (정규화 이전 — 순서가 계약이다).

    ★ 절단이 정규화보다 **먼저**다. 뒤집으면 `jobs.<other>` 하위의 키 충돌이
      `exit 2` 로 새어 나가 비적용역 자기 가드가 깨진다 (변종 `V-NORMFIRST`,
      `SWP-C` 충돌 축이 판별).
    ★ spine — top-level `jobs` 키 · JOB2 키 · `jobs` 합성 래퍼 노드는 봉투
      *내용*이 아니라 봉투를 *만드는 수단*이다. 앞 둘의 변형은 여기서 exit 2 가
      되고, 래퍼는 아래 재구성으로 원 노드의 다른 키를 **버린다**(GREEN).
    """
    if not isinstance(document, dict):  # P-E1
        raise EnvelopeError(
            "envelope_root_not_mapping",
            f"top-level is not a mapping: {type(document).__name__}",
            path,
        )
    jobs = document.get("jobs")  # ★ `on` 은 bool 키지만 `jobs` 는 str 키다
    if not isinstance(jobs, dict):  # P-E2
        raise EnvelopeError("envelope_jobs_missing", "missing top-level 'jobs'", path)
    if job2 not in jobs:  # P-E3
        raise EnvelopeError("envelope_job_absent", f"missing job: {job2}", path)

    envelope: Dict[Any, Any] = {k: v for k, v in document.items() if k != "jobs"}
    envelope["jobs"] = {job2: jobs[job2]}
    return envelope


# ── 산출 3계층 (path ← text ← document) ──────────────────────────────────────
#  각 층은 **얇다**. 텍스트 층 sweep(`SWP-I` — 리터럴 중복 키·merge override)은
#  `..._from_text` 를, 구조 층 sweep(`SWP-A`~`SWP-H`)은 `..._from_document` 를
#  쓰면 되므로 담지 테스트가 파이프라인을 복제할 필요가 없다.
def compute_envelope_from_document(
    document: Any,
    job2: str,
    *,
    path: Optional[str] = None,
    pre_val: Optional[Callable[[Any], Any]] = None,
    post_map: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Envelope:
    """이미 파싱된 문서 → 봉투. (`ENV-1` 은 호출측이 이미 통과시킨 상태)"""
    envelope = cut_envelope(document, job2, path=path)
    normalized = _normalize_mapping(envelope, pre_val=pre_val, post_map=post_map)
    text = json.dumps(normalized, **_JSON_SERIALIZE_KWARGS)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return Envelope(job2=job2, text=text, sha256=digest, path=path)


def compute_envelope_from_text(
    text: str,
    job2: str,
    *,
    path: Optional[str] = None,
    pre_val: Optional[Callable[[Any], Any]] = None,
    post_map: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Envelope:
    """workflow YAML **원문** → 봉투. 파싱 판정은 `dup_safe_load` 승계(`ENV-1`)."""
    document = dup_safe_load(text)
    return compute_envelope_from_document(
        document, job2, path=path, pre_val=pre_val, post_map=post_map
    )


def compute_envelope(
    workflow_path: str,
    job2: str,
    *,
    pre_val: Optional[Callable[[Any], Any]] = None,
    post_map: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Envelope:
    """★ `W-21` 책무 (i) — **단일 진입 함수**.

    대상 workflow 파일 경로 + JOB2 이름 → 봉투 문자열과 그 sha256.

    ★ 읽기 표기 2축은 **의도된 흡수**다 (§8.B CRLF·BOM 선례):
      `utf-8-sig`  — BOM 이 있으면 벗긴다
      universal newlines(기본) — CRLF/CR 을 `\\n` 으로 접는다 ⇒ 같은 내용이
      Windows 와 Linux CI 에서 **같은 sha** 를 낸다. 이 두 축을 흡수하지 않으면
      핀이 체크아웃 환경에 의존하게 된다.
    ★ 파일 부재·읽기 불가는 여기서 예외로 종결하고 CLI 가 exit 2 로 번역한다
      (`P-E4` 정의역 = 입력 읽기부터 핀 산출까지 **전 구간**).
    """
    with open(workflow_path, encoding="utf-8-sig", newline=None) as fh:
        text = fh.read()
    return compute_envelope_from_text(
        text, job2, path=workflow_path, pre_val=pre_val, post_map=post_map
    )


# ── CLI (책무 (ii) — 채취기 겸 대조기) ───────────────────────────────────────
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envelope_pin.py",
        description=(
            "CFP-2978 W-21 — 봉투 sha256 채취기 겸 대조기 "
            "(PIN_ENVELOPE_SHA256 의 유일 산출자)"
        ),
    )
    parser.add_argument("workflow", help="대상 workflow yml 경로")
    parser.add_argument("--job2", required=True, metavar="JOB_ID", help="봉투에 담을 JOB2 이름")
    parser.add_argument(
        "--expect",
        metavar="SHA256",
        help="기대 핀(64자 hex). 지정 시 대조기로 동작 — 일치 exit 0 / 불일치 exit 1",
    )
    parser.add_argument(
        "--print-envelope",
        action="store_true",
        help="봉투 전문을 stderr 로 함께 낸다 (stdout 은 sha 단독 유지)",
    )
    parser.add_argument(
        "--json", action="store_true", help="stdout 을 JSON 오브젝트로 낸다"
    )
    args = parser.parse_args(argv)

    try:
        envelope = compute_envelope(args.workflow, args.job2)
    except EnvelopeError as exc:  # P-E1~P-E3
        print(json.dumps(exc.to_payload(), ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 — P-E4: 전 구간 미포착 예외 = meta-error
        # ★ 삼키는 것이 아니라 **등급을 고정**하는 것이다. 여기서 GREEN(exit 0)을
        #   내면 "읽지 못한 상태"가 통과한다. exit 2 는 GREEN 도 RED 도 아니다.
        payload = {
            "error_kind": "envelope_meta_error",
            "message": f"{type(exc).__name__}: {exc}",
            "path": args.workflow,
        }
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return 2

    if args.print_envelope:
        print(envelope.text, file=sys.stderr)

    if args.json:
        print(
            json.dumps(
                {"job2": envelope.job2, "path": envelope.path, "sha256": envelope.sha256},
                ensure_ascii=False,
            )
        )
    else:
        print(envelope.sha256)

    if args.expect is None:
        return 0  # 채취 모드 — 대조하지 않았으므로 GREEN 을 주장하지 않는다

    if envelope.matches(args.expect):
        return 0  # GREEN
    print(
        json.dumps(
            {
                "verdict": "RED",
                "expected": args.expect.strip().lower(),
                "actual": envelope.sha256,
                "path": args.workflow,
                "job2": args.job2,
            },
            ensure_ascii=False,
        ),
        file=sys.stderr,
    )
    return 1  # RED


if __name__ == "__main__":
    sys.exit(main())
