#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/decision_record_disposition_deathmarker.py
CFP-2799 / Epic #2696 B(#2698) gray-zone 완결 — death-marker / amendment 광의 corpus 의
**additive detection 축**(신규 pure sibling module, canary Q0' 병렬 detection 축 패턴).

목적:
  core oracle(`decision_record_disposition.classify`)의 SCOPE = `\d+-tuple` bp-context 라인.
  death-marker(규칙 사망 선언) / amendment(개정 블록) 광의 corpus 는 그 SCOPE 밖이라 census
  진입조차 못 한다. 본 module 은 그 두 domain 의 **candidate predicate + classifier** 를
  additive 하게 공급한다 — core 의 `classify()` 는 **일절 무변경**(5-enum · 3축 · SMOKE_CASES
  git diff 0, AC-12). 신규 disposition enum 을 만들지 않는다(각 반환부 `assert ... in DISPOSITIONS`).

honest ceiling(ADR-119 / ADR-136 §결정15 / ADR-151 §결정7):
  death/amendment 는 tuple 의 `live_required_contexts` 같은 조회가능 staleness 레지스트리가
  **구조적으로 없다** = 미결정성의 뿌리. 따라서 본 module 은 기계 결정 가능 부분집합(dated →
  보존)만 확정하고, "죽은 규칙 잔재 vs 정당 역사기록"의 화행 판정은 **auto-correct 하지 않고
  `pl_review=True` 로 surface**(no-blind-apply, C-3). "전수 완결/봉인" 주장 금지.

의존 방향(ModuleArch — 단방향):
  본 sibling → core(`decision_record_disposition`) + `sweep_executor`(마커 상수 SSOT).
  core 는 본 sibling 을 **모른다**(census DI 는 composition root 가 주입). sweep_executor 는
  본 sibling 을 import 하지 않는다 → cycle 없음.

resource-safety honest-ceiling (ADR-082 §결정16):
  death 어휘 매칭은 feature-축(단일 whole-line regex 아님) + bounded substring. "임의 입력
  무해(ReDoS-safe)" 단정 금지 — bounded-degradation(정상 corpus 라인 선형)만 주장.

anti-overfit: 파일 신원(경로/특정 라인 번호) 하드코딩 0 — 입력은 라인 텍스트뿐.
"""

import os
import re
import sys

_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)

from decision_record_disposition import (  # noqa: E402
    _result,
    DISPOSITIONS,
    DISPOSITION_NO_ACTION,
    axis_tense,
)
from sweep_executor import _has_death_or_moot_marker  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# death 어휘집 (feature-축 — 전부 소문자 substring/feature 매칭, UTF-8 리터럴)
#   ★ 신원 하드코딩 0. single whole-line regex 아님(#2698 F-1 상속).
# ─────────────────────────────────────────────────────────────────────────────
_DEATH_TOKENS = (
    "폐기",
    "효력박탈",
    "효력 상실",
    "철회",
    "더 이상",
    "deprecated",
    "sunset",
    "superseded",
    "moot",
    "no longer",
    "obsolete",
)

# ─────────────────────────────────────────────────────────────────────────────
# homonym prefilter 정규식
# ─────────────────────────────────────────────────────────────────────────────
# bare ADR cross-ref 리스트 원소(`- ADR-033`) — 라인 전체가 bare 참조면 death 선언 아님.
_BARE_ADR_XREF_ITEM_RE = re.compile(r"^-?\s*ADR-\d+\s*$", re.IGNORECASE)
# frontmatter/구조 key 라인(`status: deprecated` / `amendment_log:` 등) — 산문 death 선언 아님.
_FRONTMATTER_KEY_RE = re.compile(r"^\s*[A-Za-z_][\w-]*\s*:")
# amendment 헤더 라인(`## Amendment N`) — key 라인 예외(candidate 유지).
_AMENDMENT_HEADER_LINE_RE = re.compile(r"^\s*#{1,6}\s*amendment\s+\d+", re.IGNORECASE)


def _low(text):
    return text.lower()


def _passes_homonym_prefilter(line):
    """death/amendment 후보 공통 prefilter — 통과 시 True(후보 가능), reject 시 False.

    reject 대상(§3.4 homonym prefilter):
      - self-reflag-exempt: 이미 효력박탈 마커 보유(재surface 0, §11.6 / T2 완화 수렴).
      - `sunset_justification:` 필드명(1409 occ, ADR-064 §결정7 evidence-gate audit 필드 — death 선언 아님).
      - bare ADR cross-ref 라인(`- ADR-033`).
    """
    if _has_death_or_moot_marker(line):
        return False  # self-reflag-exempt
    low = _low(line)
    if "sunset_justification" in low:
        return False  # ADR-064 evidence-gate audit 필드 — homonym
    if _BARE_ADR_XREF_ITEM_RE.match(line.strip()):
        return False  # bare ADR cross-ref
    return True


def _is_deathmarker_candidate(line):
    """라인이 death-marker census 후보인지(homonym prefilter + self-reflag-exempt 통과 후
    death 어휘 feature 매칭)."""
    if not _passes_homonym_prefilter(line):
        return False
    if _FRONTMATTER_KEY_RE.match(line):
        return False  # frontmatter/구조 key: 라인 — 산문 death 선언 아님(homonym)
    low = _low(line)
    return any(tok in low for tok in _DEATH_TOKENS)


def _is_amendment_candidate(line):
    """라인이 amendment census 후보인지 — `## Amendment N` 헤더 또는 amendment 언급 산문.
    구조 key 라인(`amendment_log:`/`amendments:`)은 후보 아님(DBM-3 이 처리, 여기선 dated region
    라인만 흐른다)."""
    if not _passes_homonym_prefilter(line):
        return False
    if _AMENDMENT_HEADER_LINE_RE.match(line):
        return True
    if _FRONTMATTER_KEY_RE.match(line):
        return False  # 구조 key 라인 — DBM-3 소관
    low = _low(line)
    return "amendment" in low or "개정" in line


def _ext_result(disposition, reason, *, pl_review, domain, axes=None):
    """core `_result` 재사용 + additive key(`pl_review`/`domain`). 5-enum 원천 차단 assert."""
    assert disposition in DISPOSITIONS, "5-enum 밖 disposition 원천 차단: %r" % (disposition,)
    base = _result(disposition, axes or {}, reason)
    base["pl_review"] = bool(pl_review)
    base["domain"] = domain
    return base


def classify_deathmarker(line, *, live_required_contexts=None, dated_context=None):
    """death-marker 라인 1개를 5-enum 으로 분류.

    - dated(이력 안 death 선언 = 과거 사망의 역사기록, 당시-참) → no_action 보존(INV-R2), PL 회부 불요.
    - undated death 어휘(규칙 사망 vs 서술 언급 = 화행 판정 불가, death 레지스트리 0) → no_action
      보존(fail-closed) + `pl_review=True`(PL firsthand adjudication 회부, no-blind-apply).
    """
    dated = axis_tense(line, dated_context)
    if dated:
        return _ext_result(
            DISPOSITION_NO_ACTION,
            "dated-historical death 선언(당시-참) — 원문 보존(INV-R2)",
            pl_review=False,
            domain="deathmarker",
            axes={"dated_historical": True},
        )
    return _ext_result(
        DISPOSITION_NO_ACTION,
        "undated death 어휘 — 규칙 사망 vs 서술 언급 화행 판정 불가(staleness 레지스트리 부재) → PL 회부",
        pl_review=True,
        domain="deathmarker",
        axes={"dated_historical": False},
    )


def classify_amendment(line, *, live_required_contexts=None, dated_context=None):
    """amendment 라인 1개를 5-enum 으로 분류.

    - dated(amendment ratchet 결정기록 대다수) → no_action 보존(INV-R2 불가침), PL 회부 불요.
    - undated amendment 라인(드묾) → no_action fail-closed 보존(불확실=보존, C-4) + `pl_review=True`.
    """
    dated = axis_tense(line, dated_context)
    if dated:
        return _ext_result(
            DISPOSITION_NO_ACTION,
            "dated amendment ratchet 결정기록 — INV-R2 불가침 보존",
            pl_review=False,
            domain="amendment",
            axes={"dated_historical": True},
        )
    return _ext_result(
        DISPOSITION_NO_ACTION,
        "undated amendment 라인 — fail-closed 보존(불확실=보존) + PL 확인 회부",
        pl_review=True,
        domain="amendment",
        axes={"dated_historical": False},
    )


def build_domain_classifiers():
    """composition root 가 census 에 주입할 domain_classifiers dict 조립.
    core↔sibling 직접 import 순환 회피 — core 는 이 dict 를 주입받아 candidate→classify 라우팅만."""
    return {
        "deathmarker": {"candidate": _is_deathmarker_candidate, "classify": classify_deathmarker},
        "amendment": {"candidate": _is_amendment_candidate, "classify": classify_amendment},
    }
