#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/ac_id.py
CFP-2603 (Epic CFP-2602 G1) / ADR-145 §결정 4 — AC-ID grammar + §5.2 스키마 파서 pure leaf.

본 모듈 = AC-ID zero-drop 게이트의 **재사용 primitive SSOT**. lint·계약·후속 Story 가 공유한다.
leaf 불변식: 역방향 의존만 — `check_ac_traceability_matrix` 를 import 하지 않는다(순환 금지).
pure: 네트워크 0, 파일 I/O 0, 표준 라이브러리(`re`)만.

핵심 (CRITICAL TRAP — RefactorAgent):
  본 Story 자체의 sub-letter ID(`AC-1a`/`AC-1b`)가 naive `AC-\d+` regex 에 조용히 drop 되면
  zero-drop 위반이다. AC_ID_RE 는 sub-letter 를 수용(`^AC-(\d+)([a-z])?$`)해 이를 봉인한다.

ADR refs: ADR-145 §결정 4 (AC_ID_RE SSOT + Story-local namespace + cross-Story `<KEY>:AC-N`) /
  ADR-061 §결정 1 (Python SSOT leaf).
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# AC-ID grammar SSOT (ADR-145 §결정 4) — sub-letter 수용.
#   본 Story 의 AC-1a/AC-1b 가 naive `AC-\d+` 에 silent-drop 되면 zero-drop 위반(CRITICAL TRAP).
# ─────────────────────────────────────────────────────────────────────────────
AC_ID_RE = re.compile(r"^AC-(\d+)([a-z])?$")

# cross-Story 참조 = `<KEY>:AC-N` (ADR-145 §결정 4 — AC-ID namespace 는 Story-local).
#   KEY prefix 를 분리한 뒤 로컬 AC-N 을 파싱한다. KEY = `CFP-2603` 형(문자 시작 + 영숫자/하이픈).
_CROSS_STORY_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9-]*):(?P<local>AC-\d+[a-z]?)$")

# §5.2 "항목화 AC" 스키마 필드 등급 + enum SSOT (ADR-145 §결정1(i)/§결정6 — Option (a)
#   rationalized minimal field-set).
#   REQUIRED (machine-enforced — Hop1 강제) = id/statement/source/tier.
#   DERIVED  (§결정6 파생 — coverage_required←tier+Hop2 / phase←run-phase+tier /
#            verification←tier+Hop2·review 로 파생. present 시에만 format-only 검증, 완결성은
#            계약/Hop2/review 층 강제 — Hop1 미재검증).
REQUIRED_FIELDS = ("id", "statement", "source", "tier")
DERIVED_FIELDS = ("verification", "coverage_required", "phase")
AC_SCHEMA_FIELDS = REQUIRED_FIELDS + DERIVED_FIELDS  # 전체 §5.2 스키마 (계약/문서 정합 참조용)
SOURCE_ENUM = ("user", "derived")
PHASE_ENUM = (1, 2)
TIER_ENUM = ("normative", "declared", "advisory")


def parse_ac_id(s):
    """AC-ID 문자열 파싱.

    Args:
      s: AC-ID 문자열. `AC-N` / `AC-Na`(sub-letter) / `<KEY>:AC-N`(cross-Story) 수용.

    Returns:
      (number: int, sub_letter: str | None)  — 매칭 시 (sub_letter 부재 시 None).
      None                                     — 불일치(malformed).
    """
    if not isinstance(s, str):
        return None
    token = s.strip()
    # cross-Story `<KEY>:AC-N` → KEY 분리 후 로컬 AC-N 만 파싱.
    cross = _CROSS_STORY_RE.match(token)
    if cross:
        token = cross.group("local")
    m = AC_ID_RE.match(token)
    if not m:
        return None
    number = int(m.group(1))
    sub_letter = m.group(2)  # None if 부재
    return (number, sub_letter)


def validate_ac_record(record):
    """§5.2 AC 레코드 스키마 검증 — Option (a) rationalized minimal field-set (ADR-145 §결정1(i)/§결정6).

    Args:
      record: AC 레코드 dict.

    Returns:
      위반 메시지 list[str] (빈 list = 통과). 각 메시지에 위반 field 이름 포함(테스트 grep 계약).

    등급:
      REQUIRED (machine-enforced — 누락 = 위반):
        id        : present ∧ AC_ID_RE 매칭(sub-letter).
        statement : present ∧ strip 후 non-empty str.
        source    : present ∧ ∈ SOURCE_ENUM {user, derived}.
        tier      : present ∧ ∈ TIER_ENUM {normative, declared, advisory}.
      DERIVED (optional — 누락 = OK; present 시에만 format-only 검증. 완결성은 계약/Hop2/review 층):
        verification      : present 시 non-empty str.
        coverage_required : present 시 list.
        phase             : present 시 ∈ PHASE_ENUM {1,2} ("1"/"2" 문자열 int 정규화 수용).
    """
    if not isinstance(record, dict):
        return [f"AC record 가 dict 아님: {type(record).__name__}"]

    violations = []
    rid = record.get("id")
    rid_disp = rid if rid is not None else "<no-id>"

    # ── REQUIRED (machine-enforced) — 누락 = 위반 ──
    if "id" not in record:
        violations.append(f"{rid_disp}: required 필드 'id' 부재")
    elif parse_ac_id(rid) is None:
        violations.append(f"{rid_disp}: 'id' 가 AC_ID_RE(^AC-(\\d+)([a-z])?$) 불일치 (sub-letter 수용)")

    if "statement" not in record:
        violations.append(f"{rid_disp}: required 필드 'statement' 부재")
    elif not (isinstance(record.get("statement"), str) and record.get("statement").strip()):
        violations.append(f"{rid_disp}: 'statement' 가 non-empty str 아님")

    if "source" not in record:
        violations.append(f"{rid_disp}: required 필드 'source' 부재")
    elif record.get("source") not in SOURCE_ENUM:
        violations.append(f"{rid_disp}: 'source' '{record.get('source')}' 가 enum {SOURCE_ENUM} 아님")

    if "tier" not in record:
        violations.append(f"{rid_disp}: required 필드 'tier' 부재")
    elif record.get("tier") not in TIER_ENUM:
        violations.append(f"{rid_disp}: 'tier' '{record.get('tier')}' 가 enum {TIER_ENUM} 아님")

    # ── DERIVED (optional — present 시에만 format-only; 누락 = OK, Hop1 미재검증) ──
    if "verification" in record:
        val = record.get("verification")
        if not (isinstance(val, str) and val.strip()):
            violations.append(f"{rid_disp}: 'verification' present-but-malformed — non-empty str 아님 (format-only)")

    if "coverage_required" in record and not isinstance(record.get("coverage_required"), list):
        violations.append(f"{rid_disp}: 'coverage_required' present-but-malformed — list 아님 (format-only)")

    if "phase" in record:
        phase_val = record.get("phase")
        try:
            phase_norm = int(phase_val)
        except (TypeError, ValueError):
            phase_norm = None
        if phase_norm not in PHASE_ENUM:
            violations.append(f"{rid_disp}: 'phase' present-but-malformed — '{phase_val}' 가 enum {PHASE_ENUM} 아님 (format-only)")

    return violations
