#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/decision_record_disposition.py
CFP-2697 / Epic #2696 (canary artifact D6) — decision-record cardinal 정정 disposition oracle.

목적:
  ADR / CLAUDE.md / audit-doc 등 "결정 기록(decision record)" 안에서 branch-protection
  `required_status_checks` context **개수**(예: `6-tuple`, `7-tuple`)를 embed 한 라인을,
  그 라인이 **어떤 조치를 받아야 하는가**(정정 / 효력박탈 / 삭제 / 이력-거짓 / 무조치)로
  분류(disposition)하는 **재사용 pure 모듈**.

feature-based (regex-only 금지 — Change Plan §3 F-1):
  분류 verdict 는 **단일 정규식 whole-line 매칭이 아니라 3개 독립 축(axis) feature 의 조합**으로
  결정된다. 정규식은 오직 **토큰 탐지 보조**(N-tuple 위치·날짜 헤더·live= 스냅샷)로만 쓰인다.
  각 축은 서로 독립이며 verdict 를 실제로 gate 한다 — self-test 가 축을 하나씩 ablate(치환)하면
  verdict 가 flip 하도록 설계됐다(축 load-bearing 실증).

anti-overfit (비협상):
  본 모듈의 어떤 함수도 **fixture 신원(file==X / lineno==N)** 을 참조하지 않는다.
  `classify()` 는 라인 텍스트(+ 선택적 사실)만 받고 경로/라인번호를 절대 받지 않는다 —
  구조적으로 fixture-identity 하드코딩이 불가능하다. 분류는 라인 FEATURE(토큰 집합·구조)로만 한다.

3 축(각 독립 feature — self-test ablation 대상):
  ① referent   (Q0 동음이의 prefilter) — 라인의 N-tuple/cardinal 이 실제로 branch-protection
                 `required_status_checks` context **개수**를 가리키는가? 산술("8-2 산술")·근거수
                 ("8-list evidence")·지표("metric 3-tuple")는 homonym 으로 reject.
                 referent ≠ bp-context-count → `no_action`. [N-1 killer 통과]
  ② tense/화행 (Q1) — 라인이 dated/historical/procedural(전이) 기록(## YYYY-MM-DD 블록 /
                 "live=N (HELD)" / **전이-화살표 `6→7-tuple`** / inline-date+등록동사 / 과거 reconcile
                 서술) 안에 있는가? dated ∧ 현재-거짓-normative 부재 → `no_action`(보존). dated ∧
                 보존된 이력 안의 거짓 present-normative → `historical_falsehood`. `dated_context`
                 override 수용; 없으면 라인에서 추론. [N-2 killer + 6→7 전이-history 보존]
                 부속 Q1-scope: **hypothetical/negated-scope(비침범)** cardinal 참조 → `no_action`
                 (present-live invariant 주장 아님 = 편집 대상 아님).
  ③ cardinal-bound (Q2) — 가변 측정 리터럴(count `6-tuple`/version/SHA)을 invariant/normative/
                 scope 문장(불변/무변경/invariant/MUST/금지/무손상 토큰 또는 scope-선언 주어)에
                 embed 하는가? yes ∧ referent-in-scope ∧ present-normative → `correct`. [P-1/2/3 검출]

prefilter/보조:
  Q0′ phantom-enforcement (병렬 축 — 5번째 disposition 아님): 라인이 강제("차단/필수/required/
       blocking")를 주장하나 `live_required_contexts`(제공 시)로 뒷받침되지 않으면 axes 에
       `phantom_enforcement: true` 만 표기. routing: 값-embed → `correct`(Q2) / 순수주장 →
       `no_action` surface(Q4). 별도 disposition 값 없음.
  Q4 fail-closed: 순수 서술/설계-의도, 판정 가능한 feature 부재 → `no_action` reason=surface-only.
  존재-license(⑤/Q3): `is_living_list_membership_expired(...)` — DELETE 후보 판정을 **전달된 사실**
       로만 결정(신원 하드코딩 0).

트리 순서(§9): Q0 referent → Q0′ phantom → Q1 dated/scope(→ Q1-scope hypothetical) → Q2 cardinal
  → Q3 존재-license → Q4.

resource-safety honest-ceiling (ADR-082 §결정 16):
  정규식은 라인-단위 토큰 탐지에만 쓰이고 입력은 decision-record 라인(길이 bounded)이다. 수량자는
  전부 bounded 형태이나 본 주석은 "임의 입력 무해(ReDoS-safe)"를 단정하지 않는다 — bounded
  degradation(정상 결정-기록 라인에 대해 선형)만 주장한다. proof-reference/벤치 없는 절대 안전
  claim 은 하지 않는다.

pure: 네트워크 0, import side-effect 0. 파일 I/O 는 하단 `if __name__ == "__main__"` CLI 층 전용
  (census 파일 읽기). importable 함수는 순수(라인 텍스트 in → dict out).
"""

import argparse
import json
import os
import re
import sys

# ─────────────────────────────────────────────────────────────────────────────
# disposition enum (SSOT — 5 값)
# ─────────────────────────────────────────────────────────────────────────────
DISPOSITION_CORRECT = "correct"                       # 정정 / cardinal 갱신
DISPOSITION_STRIP = "strip_normativity"               # 효력 박탈 (bytes 보존, moot-mark)
DISPOSITION_DELETE = "delete"                         # 삭제
DISPOSITION_HISTORICAL_FALSEHOOD = "historical_falsehood"  # 이력-거짓 (D8)
DISPOSITION_NO_ACTION = "no_action"                   # 동음이의/dated/scope 영구참/Q4 fail-closed

DISPOSITIONS = (
    DISPOSITION_CORRECT,
    DISPOSITION_STRIP,
    DISPOSITION_DELETE,
    DISPOSITION_HISTORICAL_FALSEHOOD,
    DISPOSITION_NO_ACTION,
)

# referent 축 enum
REFERENT_BP_CONTEXT_COUNT = "branch_protection_context_count"
REFERENT_OTHER = "other"       # homonym (산술/근거수/지표) — bp context 개수 아님
REFERENT_ABSENT = "absent"     # N-tuple cardinal 자체가 없음

# ─────────────────────────────────────────────────────────────────────────────
# 토큰 집합 (feature vocabulary — 전부 소문자 substring 매칭)
#   ★ 신원(file/line) 하드코딩 0 — 오직 도메인 어휘/구조 토큰.
# ─────────────────────────────────────────────────────────────────────────────
# branch-protection 도메인 근접 토큰 — referent 를 bp-context-count 로 결정하는 주 신호.
_BP_DOMAIN_TOKENS = (
    "branch protection",
    "branch-protection",
    "브랜치 보호",
    "required_status_checks",
    "required status check",
    "required context",
    "required-context",
    "required contexts",
    "required_contexts",
    "status_checks",
    "status check",
    "contexts",
    "check-gate",
    "phase-gate",
)

# referent 를 homonym(other)으로 만드는 경쟁-주어 근접 토큰 (tuple 직전 window 검사).
#   산술/지표/근거수 tuple 은 bp context 개수가 아니다.
_COMPETING_ADJ_TOKENS = (
    "metric",
    "지표",
    "산술",
    "arithmetic",
    "latency",
    "evidence",
    "p50",
    "p95",
    "p99",
)

# 영구-불변(permanence) 토큰 — "그 값은 결코 바뀌지 않는다"는 hard-invariant 주장.
#   ※ "무침범"(not-encroached/not-touched)은 permanence-invariant 가 아니라 **non-intrusion(scope
#     비침범)** 마커이므로 여기서 제외 — 아래 _HYPOTHETICAL_NEGATED_TOKENS 로 이동(hypothetical/보존).
_PERMANENCE_TOKENS = (
    "불변",
    "무변경",
    "무손상",
    "invariant",
)

# 현재-normative 토큰 — 값이 갱신 대상인 present 규범(불변 주장 아님).
#   ★ FIX(F3): `"required"` 제거 — bp-도메인 명명어(이미 `_BP_DOMAIN_TOKENS` 의
#     "required contexts" 등에 속함)이지 present-normative 화행 동사가 아니다. 이 dual-membership 이
#     bp-context 서술 라인(대부분 "required" 포함)을 `cardinal_bound` vacuously True 로 만들어
#     false-green(과잉 `correct`)을 유발했다. 진성 규범 신호는 무변경/불변/무손상/must/유지/remain 이 진다.
_NORMATIVE_TOKENS = (
    "must",
    "금지",
    "의무",
    "remain",
    "유지",
    "준수",
    "정합",
    "확정",
    "불가",
    "무조건",
)

# cardinal-bound 축이 쓰는 invariant/normative 토큰 합집합.
_INVARIANT_OR_NORMATIVE_TOKENS = tuple(set(_PERMANENCE_TOKENS + _NORMATIVE_TOKENS))

# scope-선언 주어 토큰 — "활성 관리 표면 = ... 6-tuple" 류.
_SCOPE_SUBJECT_TOKENS = (
    "관리 표면",
    "관리 표면",
    "표면 =",
    "scope",
    "활성 관리",
    "단일 (",
    "단일(",
)

# 강제(enforcement) 주장 토큰 — Q0′ phantom 축.
_ENFORCEMENT_TOKENS = (
    "차단",
    "필수",
    "required",
    "blocking",
    "fail-closed",
    "차단한다",
    "게이트",
)

# dated/historical 강 신호 토큰 — tense 축.
_DATED_MARKERS = (
    "held",
    "잔존",
    "당시",
    "이력 보존",
    "supersede",
    "doc-ahead",
    "rollback",
    "롤백",
    "시점 기준",
)

# past-scope 토큰 — dated 블록 안에서 "이 규범 주장은 과거 스냅샷에 묶여 있다"는 신호.
#   (dated ∧ past-scoped → 참인 이력 기록 → 보존 / dated ∧ not past-scoped → 이력-거짓 후보)
_PAST_SCOPE_TOKENS = (
    "held",
    "당시",
    "시점",
    "잔존",
    "과거",
    "이력",
    "supersede",
    "rollback",
    "롤백",
    "pending",
    "doc-ahead",
    "예정",
    "선캡처",
    "snapshot",
    "스냅샷",
)

# 등록/전이(registration/transition) 과거-절차 동사 — inline-date 와 **결합**될 때만 dated 보강신호.
#   (단독으로는 dated 아님 — P-3 "6-tuple ... 등록"(present-normative)을 flip 시키지 않기 위함.)
_REGISTRATION_VERBS = (
    "등록",
    "narrowing",
    "정합 확정",
    "reconcile",
    "승격",
    "전이",
    "결정",
    "확정",
)

# hypothetical / negated-scope(비침범) 토큰 — cardinal 이 **비-집행/가정/scope-보존** 참조임을 시사.
#   (예: "결정 B(... 8-tuple) 무침범" = 그 결정의 8-tuple 을 우리가 건드리지 않음 = present-live invariant
#    주장 아님 → 편집 대상 아님 → no_action 보존.) referent 통과 후 Q1-scope 에서 short-circuit.
_HYPOTHETICAL_NEGATED_TOKENS = (
    "무침범",
    "불가침",
    "무침해",
    "미침범",
    "침범하지",
)

# ─────────────────────────────────────────────────────────────────────────────
# 정규식 (토큰 탐지 보조 — bounded, 라인-단위). classification verdict 는 여기서 안 나온다.
# ─────────────────────────────────────────────────────────────────────────────
_TUPLE_RE = re.compile(r"(\d+)\s*-\s*tuple")
_DATE_HEAD_RE = re.compile(r"^\s*#{0,6}\s*\d{4}-\d{2}-\d{2}\b")
_LIVE_TUPLE_RE = re.compile(r"live\s*=\s*(\d+)\s*-\s*tuple", re.IGNORECASE)
_VERSION_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)?\b")
_SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
_MEMBER_KEY_RE = re.compile(r"[\"'`]([a-z0-9][a-z0-9 _.()\-—–]{1,80})[\"'`]")
# inline ISO 날짜(라인 어디든) — 헤더 전용 _DATE_HEAD_RE 와 disjoint(보강).
_INLINE_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
# 전이-화살표 (→/->/~>/➔/⇒/⟶) — 변경 이벤트 서술의 구조적 신호.
_TRANSITION_ARROW_RE = re.compile(r"(→|->|~>|➔|⇒|⟶)")
# compact 전이 cardinal: "6→7-tuple" 류(화살표가 두 count 를 직접 잇고 -tuple 로 닫힘).
_COMPACT_TRANSITION_RE = re.compile(r"\d+\s*(?:→|->|~>|➔|⇒|⟶)\s*\d+\s*-\s*tuple")


def _low(text):
    return text.lower()


def _has_any(text_low, tokens):
    return any(tok in text_low for tok in tokens)


# ─────────────────────────────────────────────────────────────────────────────
# 축 ① referent — 동음이의 prefilter (Q0)
# ─────────────────────────────────────────────────────────────────────────────
def axis_referent(line_text, live_required_contexts=None):
    """N-tuple/cardinal 이 branch-protection required-context **개수**를 가리키는지 판정.

    feature:
      (a) `\\d+-tuple` 토큰 존재 (context 개수 표현 형태) — 없으면 REFERENT_ABSENT.
      (b) bp 도메인 근접 토큰(contexts/required_status_checks/branch protection/check-gate ...)
          존재 — 없으면 REFERENT_OTHER (metric/산술/evidence tuple 은 도메인 토큰이 없다).
      (c) tuple 직전 window 에 경쟁-주어(metric/지표/산술/evidence ...) 근접 → REFERENT_OTHER.

    반환: REFERENT_BP_CONTEXT_COUNT | REFERENT_OTHER | REFERENT_ABSENT.
    (live_required_contexts 는 여기선 미사용 — phantom 축에서 소비. 시그니처 대칭 유지용.)
    """
    low = _low(line_text)
    m = _TUPLE_RE.search(low)
    if not m:
        return REFERENT_ABSENT
    if not _has_any(low, _BP_DOMAIN_TOKENS):
        return REFERENT_OTHER
    window = low[max(0, m.start() - 16):m.start()]
    if _has_any(window, _COMPETING_ADJ_TOKENS):
        return REFERENT_OTHER
    return REFERENT_BP_CONTEXT_COUNT


# ─────────────────────────────────────────────────────────────────────────────
# 축 ② tense / 화행 — dated/historical (Q1)
# ─────────────────────────────────────────────────────────────────────────────
def _is_transition_event(line_text):
    """cardinal 이 **전이(change) 이벤트**로 서술되는지 — 현재-불변이 아니라 변경 서술의 구조적 신호.

    (규칙 1, general·비-fixture) 두 형태:
      (a) compact 전이: `\\d+→\\d+-tuple`(예 "6→7-tuple") — 화살표가 두 count 를 직접 잇고 -tuple 로 닫힘.
      (b) broad 전이: 라인에 전이-화살표(→/->/~>) ∧ **서로 다른** `\\d+-tuple` count 가 2개 이상
          (예 "6-tuple 정합 확정 → ... 7-tuple 로 narrowing" = from-6 to-7 변경 서술).
    현재-불변 문장은 "6-tuple 로 유지/불변"처럼 단일 count·화살표 없음 → 이 함수는 False(= P-fixture 무영향).
    """
    low = _low(line_text)
    if _COMPACT_TRANSITION_RE.search(low):
        return True
    if _TRANSITION_ARROW_RE.search(line_text):
        counts = set(m.group(1) for m in _TUPLE_RE.finditer(low))
        if len(counts) >= 2:
            return True
    return False


def _is_inline_dated_registration(line_text):
    """(규칙 2, general·비-fixture) inline ISO 날짜 ∧ 등록/전이/결정 과거-절차 동사 공존 → dated 보강.

    ※ **결합** 조건(날짜+동사)이라 단독 동사(예 P-3 의 "등록", 날짜 없음)를 flip 시키지 않는다.
    """
    if not _INLINE_DATE_RE.search(line_text):
        return False
    return _has_any(_low(line_text), _REGISTRATION_VERBS)


def axis_tense(line_text, dated_context=None):
    """라인이 dated/historical/procedural(전이) 기록 안에 있는지 판정.

    dated_context override 가 주어지면 그대로 사용(블록 컨텍스트를 CLI/호출자가 안다).
    없으면 라인에서 추론:
      - `## YYYY-MM-DD` 헤더 / 선두 날짜
      - `live=N-tuple` 스냅샷(현재-live 측정 기록 = 이력 스냅샷)
      - **전이 이벤트**(규칙 1): `6→7-tuple` / 화살표+복수 count = 변경 서술(현재-불변 아님)
      - **inline-date + 등록/결정 동사**(규칙 2): 날짜+절차동사 공존 = 과거 절차 기록
      - HELD / 잔존 / 당시 / 이력 보존 / supersede / doc-ahead / rollback / 시점 기준
    """
    if dated_context is not None:
        return bool(dated_context)
    if _DATE_HEAD_RE.search(line_text):
        return True
    if _LIVE_TUPLE_RE.search(line_text):
        return True
    if _is_transition_event(line_text):
        return True
    if _is_inline_dated_registration(line_text):
        return True
    return _has_any(_low(line_text), _DATED_MARKERS)


def is_hypothetical_negated_scope(line_text):
    """(규칙 3, general·비-fixture) cardinal 이 비침범/가정 scope 참조인지 — non-intrusion 마커 존재.

    "결정 B(... N-tuple) 무침범" = 그 결정의 N-tuple 을 **건드리지 않음** 선언 = present-live invariant
    주장이 아니라 scope-보존 참조 → 편집 대상 아님 → no_action. referent 통과 후 Q1-scope 에서 소비.
    (P/N fixture 는 이 토큰을 쓰지 않으므로 무영향.)
    """
    return _has_any(_low(line_text), _HYPOTHETICAL_NEGATED_TOKENS)


def _is_past_scoped(line_text):
    """dated 라인의 규범 주장이 과거 스냅샷에 묶여 있는지(참인 이력) 판정 — tense 축 내부 refinement.

    past-scoped(당시/시점/live=/HELD/잔존/과거/이력/pending/doc-ahead ...) → 참인 이력 기록 → 보존.
    not past-scoped(dated 블록인데 규범을 여전히-유효처럼 단언) → 이력-거짓 후보.
    """
    if _LIVE_TUPLE_RE.search(line_text):
        return True
    return _has_any(_low(line_text), _PAST_SCOPE_TOKENS)


# ─────────────────────────────────────────────────────────────────────────────
# 축 ③ cardinal-bound — 가변 리터럴의 invariant/normative/scope embed (Q2)
# ─────────────────────────────────────────────────────────────────────────────
def _scope_declaration(line_text):
    """scope-선언 주어(활성 관리 표면 = ... / 단일 (N-tuple)) 인지 — cardinal-bound 의 scope 경로."""
    low = _low(line_text)
    return _has_any(low, _SCOPE_SUBJECT_TOKENS)


def axis_cardinal_bound(line_text):
    """가변 측정 리터럴(count/version/SHA)을 invariant/normative/scope 문장에 embed 하는지 판정.

    feature:
      (a) 가변 리터럴 존재: `\\d+-tuple` | version `N.N[.N]` | SHA `[0-9a-f]{7,40}`.
      (b) invariant/normative 토큰(불변/무변경/MUST/금지/유지/정합 ...) 존재
          OR scope-선언 주어 존재.
    둘 다 성립 → True.
    """
    low = _low(line_text)
    has_literal = bool(
        _TUPLE_RE.search(low) or _VERSION_RE.search(low) or _SHA_RE.search(low)
    )
    if not has_literal:
        return False
    if _has_any(low, _INVARIANT_OR_NORMATIVE_TOKENS):
        return True
    if _scope_declaration(line_text):
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 축 Q0′ phantom-enforcement (병렬 축)
# ─────────────────────────────────────────────────────────────────────────────
def axis_phantom_enforcement(line_text, live_required_contexts=None):
    """라인이 강제(차단/필수/required/blocking)를 주장하나 live 근거가 없으면 True.

    live_required_contexts 미제공 시 근거 검증 불가 → False(phantom 단정 안 함, fail-open).
    제공 시: 강제 주장이 있는데 라인이 참조하는 context 키가 live 집합에 없으면 phantom=True.
    반환: bool (별도 disposition 값 아님 — axes 표기 + reason routing 용).
    """
    low = _low(line_text)
    if not _has_any(low, _ENFORCEMENT_TOKENS):
        return False
    if live_required_contexts is None:
        return False
    key = _extract_membership_key(line_text)
    if key is None:
        # 강제 주장은 있으나 특정 context 키를 못 뽑음 → 근거 대조 불가 → phantom 단정 안 함.
        return False
    return key not in set(live_required_contexts)


# ─────────────────────────────────────────────────────────────────────────────
# 존재-license 보조 (⑤/Q3) — DELETE 후보 판정
# ─────────────────────────────────────────────────────────────────────────────
def _extract_membership_key(line_text):
    """라인에서 living-list 멤버십 키(따옴표/백틱 안 context 이름) 추출 — 없으면 None."""
    m = _MEMBER_KEY_RE.search(line_text)
    if not m:
        return None
    return m.group(1).strip()


def is_living_list_membership_expired(line_text, *, live_members=None, member_key=None):
    """living-list(예: required_status_checks contexts) 멤버십이 만료됐는지 — 전달된 사실로만 판정.

    ★ decidable-from-passed-facts (신원 하드코딩 0):
      live_members(현행 멤버 집합)가 제공되고, 라인이 선언하는 멤버 키가 그 집합에 **없으면**
      만료(=삭제 후보). live_members 부재 → 판정 불가 → False(fail-closed, 삭제 후보 아님).
    """
    if live_members is None:
        return False
    key = member_key if member_key is not None else _extract_membership_key(line_text)
    if key is None:
        return False
    return key not in set(live_members)


# ─────────────────────────────────────────────────────────────────────────────
# permanence-falsification 보조 (Q2 refinement: correct vs strip_normativity)
# ─────────────────────────────────────────────────────────────────────────────
def _is_permanence_invariant(line_text):
    return _has_any(_low(line_text), _PERMANENCE_TOKENS)


def _embedded_value_contradicts_live(line_text, live_required_contexts):
    """embed 된 tuple 개수가 현행 live context 개수와 모순되는지 — live 미제공 시 판정 불가(False)."""
    if live_required_contexts is None:
        return False
    m = _TUPLE_RE.search(_low(line_text))
    if not m:
        return False
    try:
        embedded = int(m.group(1))
    except (TypeError, ValueError):
        return False
    return embedded != len(set(live_required_contexts))


# ─────────────────────────────────────────────────────────────────────────────
# classify — 3축 조합 decision table (§9 트리 순서)
# ─────────────────────────────────────────────────────────────────────────────
def _result(disposition, axes, reason):
    return {"disposition": disposition, "axes": dict(axes), "reason": reason}


def classify(line_text, *, live_required_contexts=None, dated_context=None):
    """decision-record 라인 1개를 disposition 으로 분류.

    Parameters
    ----------
    line_text : str
        분류 대상 라인 텍스트(경로/라인번호 아님 — anti-overfit 구조 보장).
    live_required_contexts : set[str] | None
        현행 branch-protection required context 집합(사실). 제공 시 phantom / permanence-falsify
        / membership-expiry 판정에 사용. 미제공 시 해당 판정은 fail-closed(보수적).
    dated_context : bool | None
        상위 블록이 dated(## YYYY-MM-DD) 임을 CLI/호출자가 알 때 override.

    Returns
    -------
    dict : {"disposition": <enum>, "axes": {...}, "reason": str}
    """
    axes = {}
    referent = axis_referent(line_text, live_required_contexts)
    axes["referent"] = referent
    phantom = axis_phantom_enforcement(line_text, live_required_contexts)
    axes["phantom_enforcement"] = phantom
    dated = axis_tense(line_text, dated_context)
    axes["dated_historical"] = dated
    cardinal_bound = axis_cardinal_bound(line_text)
    axes["cardinal_bound"] = cardinal_bound
    hypothetical = is_hypothetical_negated_scope(line_text)
    axes["hypothetical_negated_scope"] = hypothetical

    # Q0 — referent 동음이의 prefilter (N-1 killer 통과)
    if referent != REFERENT_BP_CONTEXT_COUNT:
        return _result(
            DISPOSITION_NO_ACTION,
            axes,
            "referent=%s: branch-protection context 개수가 아님(동음이의/scope-외)" % referent,
        )

    # Q1 — dated / scope (N-2 killer 보존)
    if dated:
        # 전이/절차 서술(6→7 등록 이벤트 등)은 변경-narration 이지 "보존된 이력 안의 거짓 present
        # invariant" 가 아니다 → historical_falsehood 대상 아님, 무조건 보존(no_action).
        # ("ordering invariant 준수" 같은 절차어가 cardinal_bound 을 올려도 D8 로 오분류 금지.)
        procedural = _is_transition_event(line_text) or _is_inline_dated_registration(line_text)
        if not procedural and cardinal_bound and not _is_past_scoped(line_text):
            return _result(
                DISPOSITION_HISTORICAL_FALSEHOOD,
                axes,
                "dated-historical 블록이 과거-scope 없이 거짓 present-normative cardinal 을 유지(D8)",
            )
        return _result(
            DISPOSITION_NO_ACTION,
            axes,
            "dated-historical/procedural(전이) 기록(당시-참) — 원문 보존",
        )

    # Q1-scope — hypothetical/negated-scope(비침범) cardinal 참조 → 보존 (규칙 3)
    if hypothetical:
        return _result(
            DISPOSITION_NO_ACTION,
            axes,
            "hypothetical/negated-scope(비침범) cardinal 참조 — present-live invariant 주장 아님, 원문 보존",
        )

    # Q2 — cardinal-bound present-normative (P-1/2/3 검출)
    if cardinal_bound:
        if (
            live_required_contexts is not None
            and _is_permanence_invariant(line_text)
            and _embedded_value_contradicts_live(line_text, live_required_contexts)
        ):
            return _result(
                DISPOSITION_STRIP,
                axes,
                "영구-불변 주장이 실제 변경으로 반증됨 — 값 갱신이 아니라 불변 프레임 효력 박탈",
            )
        return _result(
            DISPOSITION_CORRECT,
            axes,
            "invariant/scope 문장에 embed 된 present-normative cardinal — stale 리터럴 정정",
        )

    # Q3 — 존재-license(멤버십 만료) → delete 후보
    if is_living_list_membership_expired(line_text, live_members=live_required_contexts):
        return _result(
            DISPOSITION_DELETE,
            axes,
            "living-list 멤버십 만료(전달 사실 기준) — 삭제 후보",
        )

    # Q4 — fail-closed (순수 서술 / phantom 순수주장)
    if phantom:
        reason = "phantom 강제 주장(live 근거 부재) + 값 embed 없음 — surface-only(무조치)"
    else:
        reason = "surface-only 서술 — 판정 가능한 normative/scope feature 부재(fail-closed)"
    return _result(DISPOSITION_NO_ACTION, axes, reason)


# ─────────────────────────────────────────────────────────────────────────────
# smoke 표준 예제 (literal example strings — fixture 신원 아님)
#   P-1/2/3 → correct / N-1 homonym → no_action / N-2 dated → no_action
#   ※ N-1/N-2 는 cardinal_bound=True 로 구성 — 그래야 referent/tense 축 ablation 이 verdict 를 flip.
# ─────────────────────────────────────────────────────────────────────────────
SMOKE_CASES = (
    (
        "P-1",
        "wrapper 의 required_status_checks contexts 는 6-tuple 로 불변 유지",
        DISPOSITION_CORRECT,
    ),
    (
        "P-2",
        "branch protection 6-tuple contexts 무변경 (gate 매핑 무손상)",
        DISPOSITION_CORRECT,
    ),
    (
        "P-3",
        "required contexts MUST remain 6-tuple across the phase-gate 등록",
        DISPOSITION_CORRECT,
    ),
    (
        "N-1",
        "성능 metric 3-tuple 은 불변 baseline 으로 유지 (산술 evidence 별개)",
        DISPOSITION_NO_ACTION,
    ),
    (
        "N-2",
        "2026-07-12 당시 required contexts 6-tuple 불변 확정 (live=6-tuple, HELD) 잔존",
        DISPOSITION_NO_ACTION,
    ),
)


def smoke_report():
    """SMOKE_CASES 를 classify 로 돌려 (label, expected, got, ok, text) 리스트 반환."""
    rows = []
    for label, text, expected in SMOKE_CASES:
        got = classify(text)["disposition"]
        rows.append((label, expected, got, got == expected, text))
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# CLI 층 (파일 I/O 는 여기서만 — importable 함수는 순수 유지)
# ─────────────────────────────────────────────────────────────────────────────
def _census_over_files(paths, *, live_required_contexts=None, dated_provider=None, dated_context=None):
    """파일들을 읽어 `\\d+-tuple` 포함 라인을 classify, 조치-필요 항목(correct/strip/historical)만 수집.

    (DBM-4) 구 시그니처 `_census_over_files(paths, dated_context=None)` 를 keyword-only
    `live_required_contexts` + `dated_provider` 로 확장(census 층 threading — classify() 자체는
    불변).

    Parameters
    ----------
    paths : list[str]
        census 대상 파일 경로 목록.
    live_required_contexts : set[str] | None
        classify() 로 그대로 전달되는 현행 branch-protection required-context 집합(사실).
        phantom-enforcement / permanence-falsify / membership-expiry 축의 근거.
    dated_provider : callable(path, lineno) -> Optional[bool] | None
        `dated_block_mapper.make_dated_provider` 산출물 — per-block(라인별) dated 판정.
        제공되면 라인마다 우선 조회하되, provider 가 None(판정 불가/미해당) 을 반환하면
        아래 `dated_context`(있으면) 또는 classify() 자체의 line-level 추론으로 fall back한다
        (per-block dated 는 ADDITIVE 커버리지 — line-level 감지를 억제하지 않음).
    dated_context : bool | None
        구 `--dated`(global override) 하위호환 — `dated_provider` 가 없거나 그 판정이 None 일 때
        사용되는 global fallback.

    반환: {"scanned": int, "cardinal_lines": int, "needs_disposition": [ {...} ], "by_disposition": {...}}
    """
    needs = []
    by_disp = {}
    cardinal_lines = 0
    scanned = 0
    action_dispositions = {
        DISPOSITION_CORRECT,
        DISPOSITION_STRIP,
        DISPOSITION_HISTORICAL_FALSEHOOD,
        DISPOSITION_DELETE,
    }
    for path in paths:
        scanned += 1
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
        except (OSError, UnicodeDecodeError) as exc:
            needs.append({"file": path, "error": str(exc)})
            continue
        for idx, raw in enumerate(lines, start=1):
            line = raw.rstrip("\n")
            if not _TUPLE_RE.search(_low(line)):
                continue
            cardinal_lines += 1
            if dated_provider is not None:
                dated = dated_provider(path, idx)
                if dated is None:
                    dated = dated_context
            else:
                dated = dated_context
            res = classify(line, live_required_contexts=live_required_contexts, dated_context=dated)
            disp = res["disposition"]
            by_disp[disp] = by_disp.get(disp, 0) + 1
            if disp in action_dispositions:
                needs.append(
                    {
                        "file": path,
                        "line": idx,
                        "disposition": disp,
                        "reason": res["reason"],
                        "text": line.strip(),
                    }
                )
    return {
        "scanned": scanned,
        "cardinal_lines": cardinal_lines,
        "needs_disposition": needs,
        "by_disposition": by_disp,
    }


def _parse_live_contexts_arg(value):
    """`--live-contexts VALUE` 파싱 — comma-separated 목록 또는 파일 경로(줄당 1개 또는 JSON
    리스트)를 `set[str]` 로. value 가 None 이면 None(판정 불가 그대로 유지, fail-closed 상속)."""
    if value is None:
        return None
    if os.path.isfile(value):
        with open(value, "r", encoding="utf-8") as fh:
            content = fh.read()
        stripped = content.strip()
        if stripped.startswith("["):
            try:
                data = json.loads(stripped)
                return set(str(x).strip() for x in data if str(x).strip())
            except (ValueError, TypeError):
                pass
        return set(line.strip() for line in content.splitlines() if line.strip())
    return set(part.strip() for part in value.split(",") if part.strip())


def _common_ancestor(paths, fallback="."):
    """census 대상 파일들의 공통 상위 디렉터리(repo_root 추정) — 산출 불가 시 fallback(CWD)."""
    if not paths:
        return fallback
    try:
        abspaths = [os.path.abspath(p) for p in paths]
        common = os.path.commonpath(abspaths)
        if os.path.isdir(common):
            return common
        parent = os.path.dirname(common)
        return parent or fallback
    except (ValueError, OSError):
        return fallback


def _main(argv=None):
    ap = argparse.ArgumentParser(
        description="decision-record cardinal disposition oracle (feature-based)."
    )
    ap.add_argument("--smoke", action="store_true", help="5 표준 예제 verdict 출력")
    ap.add_argument("--line", help="단일 라인 텍스트를 classify 하고 JSON 출력")
    ap.add_argument("--census", action="store_true", help="파일 census (cardinal 라인 분류 리포트)")
    ap.add_argument(
        "--dated",
        action="store_true",
        help="census: 대상 라인을 dated 블록으로 간주(global override — 하위호환)",
    )
    ap.add_argument(
        "--live-contexts",
        help="census: 현행 required-context 집합 — comma-separated 목록 또는 파일 경로"
        "(줄당 1개 또는 JSON 리스트)",
    )
    ap.add_argument(
        "--dated-map",
        action="store_true",
        help="census: dated_block_mapper.make_dated_provider 로 파일별/블록별 dated 판정(DBM-4)",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="census: 조치-필요 항목 발견 시 exit 1",
    )
    ap.add_argument("files", nargs="*", help="census 대상 파일")
    args = ap.parse_args(argv)

    if args.smoke:
        for label, expected, got, ok, text in smoke_report():
            flag = "OK" if ok else "MISMATCH"
            print("[%s] expect=%s got=%s %s :: %s" % (label, expected, got, flag, text))
        return 0

    if args.line is not None:
        print(json.dumps(classify(args.line), ensure_ascii=False, indent=2))
        return 0

    if args.census or args.files:
        live_required_contexts = _parse_live_contexts_arg(args.live_contexts)
        dated_provider = None
        if args.dated_map:
            lib_dir = os.path.dirname(os.path.abspath(__file__))
            if lib_dir not in sys.path:
                sys.path.insert(0, lib_dir)
            import dated_block_mapper  # lazy import — 같은 scripts/lib 디렉터리(DBM-4)

            repo_root = _common_ancestor(args.files)
            dated_provider = dated_block_mapper.make_dated_provider(repo_root)
        report = _census_over_files(
            args.files,
            live_required_contexts=live_required_contexts,
            dated_provider=dated_provider,
            dated_context=(True if args.dated else None),
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        needs = [n for n in report["needs_disposition"] if "disposition" in n]
        # 사람용 요약은 stderr 로 (stdout=JSON 순수성 보존 — 소비자 파싱 무손상).
        sys.stderr.write(
            "SUMMARY: scanned=%d cardinal_lines=%d needs_disposition=%d by_disposition=%s\n"
            % (report["scanned"], report["cardinal_lines"], len(needs), report["by_disposition"])
        )
        if args.strict and needs:
            return 1
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    # FIX(F5): Windows cp949 콘솔에서 한글/em-dash 출력 시 UnicodeEncodeError 방지 (CI ubuntu 무영향).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(_main())
