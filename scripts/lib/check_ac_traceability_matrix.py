#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_ac_traceability_matrix.py
CFP-2603 (Epic CFP-2602 G1) / ADR-145 — 요건 traceability zero-drop **fail-closed** 게이트 pure core.

`scripts/lib/check_venue_shape_fidelity_presence.py` 구조 답습(offline-first / read-only /
`_extract_section_N` helper) 하되 **warning-tier → fail-closed 상향**: exit 0 = PASS only,
그 외(위반·판정불가) 전부 exit 1. skip-PASS / opt-out / default-green 경로 부재(AC-7).

3 seam = phase-aware 2-tier 의 구조적 불변식 (ADR-145 §결정 2/7):
  Hop1 = §5 AC well-formed   — AC-N 매칭(sub-letter) + tier/source enum.       [Phase 1 + 2]
  Hop2 = AC↔§8 coverage      — tier-aware: normative 만 ≥1 명명 테스트 필수.    [Phase 1 + 2]
  Hop3 = §8↔실 symbol         — 명명 테스트가 tests-root 아래 실 함수/클래스     [Phase 2 only]
                                node 로 실재(`ast` resolve, **grep 금지**).

phase 신호 = EXPLICIT (`--phase 1|2`) — diff 추론 금지(ADR-145 §결정 2, TestContract dissent-1).

━━ CEILING 정직 (AC-8 — no-hollow honesty; ADR-006 Amд2 L266 검사연극 isomorphic + ADR-119 §결정4) ━━
  본 게이트는 **presence/mapping 까지만** fail-closed 로 강제한다. 두 잔여는 강제하지 않는다:
    (i)  test-semantic 완전성 미강제 — 명명 테스트가 요건을 의미상 올바르게·완전히 검증하는지
         검사하지 않는다. semantic 적정성은 mutation-peer·리뷰(defense-in-depth)가 저감한다.
    (ii) user→AC 분해완결성 미강제 — AC 집합이 사용자 의도에 완전한지 검사하지 않는다
         (§5.6 RO-1 review + AC-10 advisory 로 mitigate).
  "완전 봉인" hard-claim 금지. declared/advisory AC 에 forged machine test 강제 = **over-reach 위반**
  (F-DECLARED/F-ADVISORY 가 반증) — Hop2 는 normative 만 커버 강제한다.
━━ SCOPE disjoint (AC-9; Epic CFP-2602) ━━
  검사 invariant set = AC↔§8 명명 테스트↔실 symbol(파일∧함수/클래스 node) 로 한정.
  runtime liveness(G2)·discriminating 행사(G3)는 검사하지 않는다 — 게이트 영역 disjoint.

━━ per-PR applicability (ADR-145 Amendment 1 §결정 8, CFP-2609) ━━
  적용성 verdict = **core 단일 소유**(classify_ac_source, adapter 재파싱 = drift 금지). 비적용 PR
  (추적할 normative AC 부재) = in-job genuine PASS(정의역 밖). 비적용 skip 은 오직 "비적용 positive
  확정"(resolve-success ∧ 0 normative AC)에서만 도달 — 판정불가(degraded: fetch/403/404/frontmatter/
  malformed-table/count-only)·적용-미추적 은 FAIL(anti-degradation, born-hollow 봉인). "opt-out ≠
  applicability-scoping"(§결정4 정의역 명확화). structural-signature keying — table 구조 present 면
  AC-ID 토큰 부재라도 NO_AC_SURFACE 아님(Hop1 malformed 경유 FAIL).

offline (네트워크 0 — 입력 전부 로컬 파일; cross-repo fetch·fs I/O 는 workflow adapter 층 전담).
read-only (verifier — write 0). 표준 라이브러리(ast/re/argparse/pathlib)만.

Usage:
  python3 check_ac_traceability_matrix.py --phase <1|2> --ac-source <FILE> --rtm <FILE> [--tests-root <DIR>]
  python3 check_ac_traceability_matrix.py --phase 1 --ac-source <FILE> --rtm-not-yet   # Phase-1 RTM not-yet

Exit codes (fail-closed):
  0 = PASS only (유일 success — 전 hop 통과).
  그 외 모든 non-zero exit = fail-closed FAIL (전부 차단):
    1 = 위반(Hop1/2/3) OR 판정불가(입력 부재·unreadable·파싱 실패·RTM 미해결·tests-root 부재).
    2 = argparse 인자오류(예: `--phase 3` = choices 위반) — 여전히 non-zero=차단.

ADR refs: ADR-145 (결정 SSOT) / ADR-006 Amd2 L266 (검사연극 isomorphic 선례) /
  ADR-119 §결정 4 (presence/mapping 만 fail-closed, semantic 강제 척 금지) /
  ADR-136 Amd3 L3 (born-missing = ast, grep-only = false-oracle) / ADR-061 §결정 1 (Python SSOT).
"""

import argparse
import ast
import os
import re
import sys

# leaf primitive (역방향 의존 — ac_id 는 본 모듈을 import 하지 않음)
try:
    from ac_id import (  # noqa: F401  (AC_ID_RE re-export 편의)
        AC_ID_RE,
        parse_ac_id,
        validate_ac_record,
    )
except ImportError:  # 직접 실행(scripts/lib/ 를 sys.path 에 없는 컨텍스트) 대비
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ac_id import (  # noqa: F401
        AC_ID_RE,
        parse_ac_id,
        validate_ac_record,
    )

# 출력 인코딩 robust 화 (Windows MSYS/cp949 등 비-UTF-8 locale 에서 한글·em-dash print 차단).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

EXIT_PASS = 0  # 전 hop 통과
EXIT_FAIL = 1  # 위반 OR 판정불가 (fail-closed — skip/opt-out/default-green 부재)

# ─────────────────────────────────────────────────────────────────────────────
# per-PR applicability verdict (ADR-145 Amendment 1 §결정 8 — 적용성 3 축 중 (c) per-PR).
#   적용성 verdict = **core 단일 소유**(adapter 재파싱 = drift 금지). classify_ac_source 가 4-way.
#   비적용 skip 은 오직 "비적용 positive 확정"(resolve-success ∧ 0 normative AC)에서만 도달 —
#   판정불가(degraded)·적용-미추적 은 FAIL(anti-degradation, born-hollow 봉인).
# ─────────────────────────────────────────────────────────────────────────────
APPLIC_NO_AC_SURFACE = "NO_AC_SURFACE"      # 비적용 positive: AC 표 signature 부재 ∧ AC 선언 claim 부재 → PASS(정의역 밖)
APPLIC_SURFACE_EMPTY = "AC_SURFACE_EMPTY"   # AC 표 signature present + 0 rows = 빈-AC bypass(F-AC7-a) → FAIL
APPLIC_SURFACE_PRESENT = "AC_SURFACE_PRESENT"  # AC 표 present + ≥1 record → Hop1/normative 분기
APPLIC_UNDECIDABLE = "UNDECIDABLE"          # degradation: AC 선언 claim present 이나 parseable 표 부재 → FAIL(anti-degradation)

# ★ structural-signature keying (Codex P2 carry-forward): 비적용(NO_AC_SURFACE) 도달 = AC-table
#   구조 signature 부재 ∧ AC 선언 claim 부재 **둘 다**. AC 선언 claim = 산문 `AC-\d+` 토큰 OR
#   `acceptance_criteria_count: N`(N≥1, count-only). table 구조 present(header id/source/tier)면
#   claim 부재라도 NO_AC_SURFACE 아님(rows→SURFACE_PRESENT/EMPTY, Hop1 malformed 경유 FAIL).
#   token-only keying 금지 — 표 구조 손상(ID 컬럼 `XX-1` 등, AC-ID 토큰 부재)이 비적용 PASS 로
#   새면 anti-degradation 붕괴(F-APPLIC-DEGRADED-NOTOKEN 이 이를 self-test 로 봉인).
_AC_ID_TOKEN_RE = re.compile(r"\bAC-\d+[a-z]?\b")
_AC_COUNT_CLAIM_RE = re.compile(r"acceptance_criteria_count:\s*([1-9]\d*)")

# ─────────────────────────────────────────────────────────────────────────────
# CEILING/SCOPE 정직 공개 텍스트 — 코드 SSOT (AC-8/AC-9 테스트 anchor).
#   게이트가 semantic 완전성을 강제하지 않음 + 2 잔여를 기계 판독 가능하게 박제한다.
# ─────────────────────────────────────────────────────────────────────────────
CEILING_DISCLOSURE = (
    "본 게이트는 presence/mapping 까지만 fail-closed 로 강제한다(no-hollow honesty, ADR-145 §결정1(b)). "
    "2 잔여는 강제하지 않는다: "
    "(i) test-semantic 완전성 미강제 — 명명 테스트가 요건을 의미상 올바르게·완전히 검증하는지 검사하지 않음. "
    "(ii) user→AC 분해완결성 미강제 — AC 집합이 사용자 의도에 완전한지 검사하지 않음(§5.6 RO-1 review + AC-10 advisory). "
    "'완전 봉인' hard-claim 금지. declared/advisory AC 에 forged machine test 강제 = over-reach 위반."
)
SCOPE_DISCLOSURE = (
    "G1 검사 invariant set = AC↔§8 명명 테스트↔실 symbol(파일∧함수/클래스 node) 로 한정. "
    "runtime liveness(G2)·discriminating 행사(G3)는 검사하지 않음 — Epic CFP-2602 게이트 disjoint."
)
APPLICABILITY_DISCLOSURE = (
    "per-PR applicability(ADR-145 §결정8): 비적용 = resolve-success ∧ 0 normative AC(정의역 밖, "
    "in-job genuine PASS — skip-as-job 아님). 판정불가(degraded)·적용-미추적 은 FAIL — anti-degradation "
    "(어떤 degraded 경로도 비적용 skip 흡수 금지). 신호 = presence-based(semantic 판단 금지, §결정1 천장 상속)."
)

# §5 이 개발서사 placeholder(Story §8 형)일 때 authoritative RTM 아님을 감지하는 marker.
_PLACEHOLDER_RE = re.compile(r"작성\s*예정|DeveloperPL\s*작성|PMOAgent\s*작성|작성\s*예정임", re.IGNORECASE)

# 명명 테스트 이름 = 백틱 인용 식별자 (§8 authoring 규약). 백틱 안 토큰만 named-test 로 인정
#   (prose/주석 false-match 회피). 예: `test_ac_id_wellformed_and_schema`.
_BACKTICK_RE = re.compile(r"`([^`]+)`")
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")


def _error(msg):
    print(f"::error::check-ac-traceability-matrix: {msg}", file=sys.stderr)


def _notice(msg):
    print(f"::notice::check-ac-traceability-matrix: {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# 섹션·표 파싱 helper (venue-shape `_extract_section_N` 패턴 답습, §N 일반화)
# ─────────────────────────────────────────────────────────────────────────────
def _extract_section_n(text, n):
    """`## §N` / `## N` 헤딩 이후 ~ 다음 `## ` 헤딩 직전까지 섹션 본문 추출. 부재 시 None.

    §N vs §N0 충돌 차단 위해 N 뒤에 `[.\\s]` anchor (venue-shape SECTION_8_HEADER_RE 정합).
    """
    header_re = re.compile(rf"^##\s*§?{n}[.\s]", re.MULTILINE)
    m = header_re.search(text)
    if not m:
        return None
    start = m.end()
    nxt = re.compile(r"^##\s", re.MULTILINE).search(text, start)
    end = nxt.start() if nxt else len(text)
    return text[start:end]


def _strip_md(cell):
    """markdown 셀 정규화 — bold(`**`)·backtick(`` ` ``) 제거 후 strip. id/tier/source 셀용."""
    return cell.replace("*", "").replace("`", "").strip()


def _is_separator_row(line):
    s = line.strip()
    if "-" not in s:
        return False
    # 셀이 전부 `-`/`:`/공백/`|` 로만 구성 (표 구분선).
    return bool(re.match(r"^\|?[\s:|-]+\|?$", s))


def _is_table_row(line):
    return line.strip().startswith("|")


def _split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _iter_markdown_tables(text):
    """섹션 텍스트 안 모든 markdown 표를 (headers, rows) 로 yield. headers/rows = 원본 셀(정규화 전)."""
    lines = text.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        if _is_table_row(lines[i]) and i + 1 < n and _is_separator_row(lines[i + 1]):
            headers = _split_row(lines[i])
            rows = []
            j = i + 2
            while j < n and _is_table_row(lines[j]) and not _is_separator_row(lines[j]):
                rows.append(_split_row(lines[j]))
                j += 1
            yield headers, rows
            i = j
        else:
            i += 1


def _find_col_exact(norm_headers, names):
    for idx, h in enumerate(norm_headers):
        if h in names:
            return idx
    return None


def _find_col_contains(norm_headers, substrings):
    for idx, h in enumerate(norm_headers):
        if any(sub in h for sub in substrings):
            return idx
    return None


def _extract_named_tests(cell):
    """RTM 명명 테스트 셀에서 백틱 인용 식별자만 추출. dotted(Class.method)는 last-segment 반환.

    prose·`(명명 테스트 없음)` 등 non-backtick 텍스트는 무시(named-test 0).
    """
    names = []
    for tok in _BACKTICK_RE.findall(cell):
        tok = tok.strip()
        if _IDENT_RE.match(tok):
            names.append(tok.split(".")[-1])  # 메서드는 last-segment (ast bare-name 매칭)
    return names


# ─────────────────────────────────────────────────────────────────────────────
# AC source(§5.3) 파서 — id/source/tier 컬럼 표
# ─────────────────────────────────────────────────────────────────────────────
_ID_HEADER_NAMES = ("id", "ac", "ac id", "ac-id")


def _scan_ac_table(section):
    """§5 섹션에서 AC 표(id/source/tier 컬럼 structural signature) 1개 탐색 + records 추출.

    적용성 verdict 의 **structural-signature 원천**(Codex P2): signature 존재(header id/source/tier)는
    rows 파싱 가능 여부와 독립. classify_ac_source 와 parse_ac_source 가 공유(재파싱 drift 봉인, ADR-140).

    Returns:
      (records: list[dict{id, source, tier[, statement]}], has_signature: bool)
        has_signature=True  — id/source/tier signature 표 발견. records = 파싱된 행(0 rows 가능).
        has_signature=False — signature 표 미발견. records=[].
    """
    for headers, rows in _iter_markdown_tables(section):
        norm = [_strip_md(h).lower() for h in headers]
        id_idx = _find_col_exact(norm, _ID_HEADER_NAMES)
        src_idx = _find_col_exact(norm, ("source",))
        tier_idx = _find_col_exact(norm, ("tier",))
        if id_idx is None or src_idx is None or tier_idx is None:
            continue
        # statement 컬럼(§5.3 required 4 중 하나 — validate_ac_record 강제) 추출.
        stmt_idx = _find_col_contains(norm, ("statement",))
        records = []
        for row in rows:
            if max(id_idx, src_idx, tier_idx) >= len(row):
                continue
            rec = {
                "id": _strip_md(row[id_idx]),
                "source": _strip_md(row[src_idx]),
                "tier": _strip_md(row[tier_idx]),
            }
            if stmt_idx is not None and stmt_idx < len(row):
                # statement 는 prose(given-when-then) — non-empty 만 필요, strip 만(내용 보존).
                rec["statement"] = row[stmt_idx].strip()
            records.append(rec)
        return records, True
    return [], False


def parse_ac_source(ac_text):
    """AC 소스 문서의 §5 안 AC 표(§5.3: id/source/tier/statement) 파싱 (2-way 호환 seam).

    Returns:
      (records: list[dict{id, source, tier}], note: str)  — 성공(0 rows 가능).
      (None, reason: str)                                   — §5 부재 / AC 표 미발견 (판정불가).
    """
    section = _extract_section_n(ac_text, 5)
    if section is None:
        return None, "§5 섹션 부재 — AC source 파싱 불가"
    records, has_sig = _scan_ac_table(section)
    if not has_sig:
        return None, "§5 안 AC 표(id/source/tier 컬럼) 미발견 — AC source 미해결"
    return records, "§5.3 AC 표 파싱"


def classify_ac_source(ac_text):
    """per-PR applicability 4-way 분류 — 적용성 verdict **core 단일 소유**(ADR-145 §결정8 D).

    Returns (verdict, records, note):
      APPLIC_NO_AC_SURFACE   — 비적용 positive: AC 표 signature 부재 ∧ AC 선언 claim 부재 (둘 다). records=[].
      APPLIC_SURFACE_EMPTY   — AC 표 signature present + 0 well-formed rows (빈-AC bypass, F-AC7-a). records=[].
      APPLIC_SURFACE_PRESENT — AC 표 present + ≥1 record. records 채움.
      APPLIC_UNDECIDABLE     — degradation: AC 선언 claim(산문 AC-N 토큰 / count-only) present 이나
                               parseable AC 표 부재 (산문 선언 + 표 파손). records=[].

    ★ structural-signature keying (Codex P2): NO_AC_SURFACE(비적용 PASS) 도달 = AC-table structural
      signature 부재 ∧ AC 선언 claim 부재 **둘 다**. table signature present 면 claim 부재라도
      NO_AC_SURFACE 아님(has_sig 분기가 선행 — records→SURFACE_PRESENT/EMPTY, Hop1 malformed FAIL 경유).
      token-only keying(표 구조 무시) 금지 — F-APPLIC-DEGRADED-NOTOKEN 이 self-test 로 봉인.
    """
    section = _extract_section_n(ac_text, 5)
    if section is None:
        # §5 섹션 자체 부재 = AC 표 signature 부재 ∧ AC 선언 claim 부재 → 비적용 positive.
        return APPLIC_NO_AC_SURFACE, [], "§5 섹션 부재 — AC 선언 표면 부재(비적용 positive)"

    records, has_sig = _scan_ac_table(section)
    # AC 선언 claim = 산문 `AC-\d+` 토큰 OR count-only(`acceptance_criteria_count: N`, N≥1).
    #   anti-degradation 보조 signal — 표 없이 AC surface 를 *주장*했으나 itemize 안 됨.
    has_ac_surface_claim = bool(_AC_ID_TOKEN_RE.search(section)) or bool(_AC_COUNT_CLAIM_RE.search(section))

    if has_sig:
        if not records:
            # AC 표 signature present + 0 well-formed rows = 빈-AC bypass(F-AC7-a) — 비적용 아님.
            return APPLIC_SURFACE_EMPTY, [], "§5 AC 표 present + 0 rows — 빈-AC bypass(F-AC7-a)"
        return APPLIC_SURFACE_PRESENT, records, "§5.3 AC 표 파싱"

    if has_ac_surface_claim:
        # ★ AC 선언 claim present + parseable AC 표 부재 = degradation → 판정불가 FAIL(anti-degradation).
        return APPLIC_UNDECIDABLE, [], (
            "§5 에 AC 선언 claim(산문 AC-N 토큰 또는 acceptance_criteria_count) present 이나 parseable "
            "AC 표(id/source/tier signature) 부재 — 산문 선언 + 표 파손(degradation), 판정불가 fail-closed "
            "FAIL(anti-degradation, degraded→skip 흡수 금지)"
        )
    # table signature 부재 ∧ AC 선언 claim 부재 (둘 다) → 비적용 positive.
    return APPLIC_NO_AC_SURFACE, [], "§5 존재하나 AC 표 signature·AC 선언 claim 모두 부재 — AC 선언 표면 부재(비적용 positive)"


# ─────────────────────────────────────────────────────────────────────────────
# RTM(§8.1) 위치 resolve + 파서 — AC/명명 테스트 컬럼 표
# ─────────────────────────────────────────────────────────────────────────────
_RTM_TEST_HEADER_SUBSTR = ("명명 테스트", "테스트", "test")
_RTM_AC_HEADER_NAMES = ("ac", "id", "ac id", "ac-id")


def _find_rtm_table(section):
    """섹션 안 RTM 표(AC 컬럼[정확히 'ac'] ∧ 테스트 컬럼) 탐색.

    §8.10 Decision Table('AC well-formed'/'§8 명명 매핑') 오매칭 차단:
    AC 컬럼은 header 정확히 'ac'(=exact), 테스트 컬럼은 '테스트'/'test' 포함 필수.
    """
    for headers, rows in _iter_markdown_tables(section):
        norm = [_strip_md(h).lower() for h in headers]
        ac_idx = _find_col_exact(norm, _RTM_AC_HEADER_NAMES)
        test_idx = _find_col_contains(norm, _RTM_TEST_HEADER_SUBSTR)
        if ac_idx is not None and test_idx is not None:
            return ac_idx, test_idx, rows
    return None


def resolve_rtm_location(rtm_text):
    """authoritative RTM(§8) 위치 resolve (ADR-145 §결정 6 RTM location-resolution P1).

    wrapper-self dogfood = Change Plan §8 이 authoritative (Story §8=개발서사 placeholder → 파싱 금지).
    consumer = Story §8 mirror. 문서유형 판별 후 authoritative location 선택.

    Returns:
      (section_body: str, note: str)  — §8 안 RTM 표 발견.
      (None, reason: str)             — §8 부재 / placeholder / RTM 표 부재 (판정불가, fail-closed).
    """
    section = _extract_section_n(rtm_text, 8)
    if section is None:
        return None, "§8 섹션 부재 — authoritative RTM 위치 미해결"
    if _find_rtm_table(section) is not None:
        return section, "§8 RTM 표 resolved"
    # RTM 표 부재 — placeholder(개발서사) 인지 판별해 정직한 사유 반환.
    if _PLACEHOLDER_RE.search(section):
        return None, (
            "§8 이 개발서사 placeholder(작성 예정) — authoritative RTM 아님. "
            "wrapper-self dogfood 는 Change Plan §8 을 --rtm 으로 전달하라 "
            "(ADR-145 §결정6 RTM location-resolution P1; Story §8 하드코딩 = 자기 PR false-FAIL 함정)."
        )
    return None, "§8 에 RTM(AC↔명명 테스트) 표 부재 — authoritative RTM 미해결"


def parse_rtm_table(rtm_section):
    """RTM 섹션(§8)에서 AC↔명명 테스트 매핑 파싱.

    Returns:
      (mapping: dict{ac_id_str: list[test_name]}, tier_map: dict{ac_id_str: tier})  — 성공.
      (None, None)                                                                  — RTM 표 미발견.
    """
    found = _find_rtm_table(rtm_section)
    if found is None:
        return None, None
    ac_idx, test_idx, rows = found
    # tier 컬럼(선택) — 있으면 tier_map 채움(참고용; Hop2 authoritative tier = AC source).
    tier_idx = None
    for headers, _ in _iter_markdown_tables(rtm_section):
        norm = [_strip_md(h).lower() for h in headers]
        if _find_col_exact(norm, _RTM_AC_HEADER_NAMES) == ac_idx:
            tier_idx = _find_col_exact(norm, ("tier",))
            break
    mapping = {}
    tier_map = {}
    for row in rows:
        if ac_idx >= len(row):
            continue
        rid = _strip_md(row[ac_idx])
        if parse_ac_id(rid) is None:
            continue  # AC 아닌 행(구분/설명) skip
        tests = _extract_named_tests(row[test_idx]) if test_idx < len(row) else []
        mapping[rid] = tests
        if tier_idx is not None and tier_idx < len(row):
            tier_map[rid] = _strip_md(row[tier_idx])
    return mapping, tier_map


# ─────────────────────────────────────────────────────────────────────────────
# Hop1 / Hop2 / Hop3 (pure seam 함수 — QADev 가 개별 import 하여 반증)
# ─────────────────────────────────────────────────────────────────────────────
def hop1_ac_wellformed(records):
    """Hop1 (Phase 1+2) — §5 AC well-formed via `validate_ac_record` (AC-2 non-hollow 배선).

    machine-enforced required 4(id/statement/source/tier) present ∧ well-formed 검증
    (id=AC_ID_RE sub-letter / source·tier enum / statement non-empty). derived 3
    (verification/coverage_required/phase)은 present 시에만 format-only — §5.3 4-컬럼은
    derived 부재이므로 required-4 만족 시 PASS(born-broken 회피). R2 semantics(malformed=FAIL) 보존:
    malformed AC-ID = validate_ac_record 가 'id' AC_ID_RE 불일치로 flag → Hop1 위반 → FAIL.
    """
    violations = []
    for rec in records:
        for v in validate_ac_record(rec):
            violations.append(f"Hop1: {v}")
    return violations


def hop2_coverage(records, rtm_mapping):
    """Hop2 (Phase 1+2) — tier-aware coverage.

    normative AC 만 ≥1 명명 테스트 매핑 필수(미커버=FAIL, AC-4/R3/R8).
    declared/advisory 는 명명 테스트 요구하지 않음(CEILING — over-reach 금지, F-DECLARED/F-ADVISORY).
    """
    violations = []
    for rec in records:
        rid = rec.get("id")
        if parse_ac_id(rid or "") is None:
            continue  # Hop1 이 malformed 를 이미 잡음
        tier = rec.get("tier")
        tests = rtm_mapping.get(rid, [])
        if tier == "normative" and not tests:
            violations.append(
                f"Hop2: normative AC {rid} → §8 명명 테스트 매핑 0 (미커버). "
                f"unmapped=FAIL (AC-4; Phase 1/2 공통)."
            )
        # declared/advisory: 명명 테스트 요구 안 함 (CEILING — forged machine test 강제 금지)
    return violations


def collect_test_symbols(tests_root):
    """tests_root 아래 `*.py` 를 `ast` 로 파싱해 정의된 함수/클래스 이름 집합 수집 (**grep 금지**).

    Returns:
      set[str]  — 정의된 def/class/async-def node 이름 (nested·메서드 포함).
      None      — tests_root 부재(디렉터리 아님) → 판정불가 (호출자 fail-closed).

    grep(문자열 매칭)이 아닌 ast node 확인이므로 주석/docstring/문자열 안 함수명은 매칭 안 됨
    (F-ORACLE-GUARD — CFP-2545 false-oracle 방어). 개별 파일 SyntaxError/IOError 는 skip
    (해당 파일 symbol 미수집 → 그 명명 테스트는 born-missing 판정, fail-closed 방향).
    """
    if not os.path.isdir(tests_root):
        return None
    symbols = set()
    for dirpath, _dirnames, filenames in os.walk(tests_root):
        for name in filenames:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    src = fh.read()
                tree = ast.parse(src, filename=path)
            except (OSError, SyntaxError, ValueError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    symbols.add(node.name)
    return symbols


def hop3_born_missing(records, rtm_mapping, symbols):
    """Hop3 (Phase 2 only) — §8 명명 테스트 ↔ 실 symbol born-missing.

    normative AC 의 명명 테스트가 `symbols`(ast 수집)에 실재하지 않으면 born-missing FAIL(AC-6).
    stub(`def test_x(): pass`)은 파일∧symbol 실재하므로 PASS (G3 경계 — F-STUB confess).
    """
    violations = []
    required = set()
    for rec in records:
        if rec.get("tier") != "normative":
            continue
        rid = rec.get("id")
        if parse_ac_id(rid or "") is None:
            continue
        for test_name in rtm_mapping.get(rid, []):
            required.add((rid, test_name))
    for rid, test_name in sorted(required):
        if test_name not in symbols:
            violations.append(
                f"Hop3: {rid} 명명 테스트 '{test_name}' born-missing — tests-root 아래 실 함수/클래스 "
                f"node 부재 (ast resolve, grep 아님). AC-6 fail-closed FAIL."
            )
    return violations


# ─────────────────────────────────────────────────────────────────────────────
# 오케스트레이션
# ─────────────────────────────────────────────────────────────────────────────
def _read_file(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, ValueError):
        return None


def run(phase, ac_source_path, rtm_path, tests_root=None, rtm_not_yet=False):
    """게이트 실행 — phase × resolve-outcome 매트릭스 (ADR-145 §결정8 D) 를 그대로 구현.

    적용성 verdict = classify_ac_source 단일 소유(adapter 재파싱 금지). 매트릭스:
      판정불가(UNDECIDABLE)                 → FAIL(phase 1·2) — anti-degradation, skip 흡수 금지
      비적용(NO_AC_SURFACE / records·0 nrm) → PASS(exit 0, phase 1·2) — 정의역 밖(추적할 normative AC 부재)
      empty-AC(SURFACE_EMPTY)               → FAIL(F-AC7-a)
      적용 + rtm not-yet(EXPLICIT)          → phase1=Hop1 only / phase2=FAIL(RTM 필수)
      적용 + rtm placeholder/absent         → FAIL(F-AC7-b/b2)
      적용 + rtm resolved                   → Hop1+Hop2 / +Hop3(phase2)
    fail-closed: 위반·판정불가 전부 EXIT_FAIL. PASS 는 전 hop 통과 OR 비적용 positive 확정 시에만.
    rtm_not_yet = adapter EXPLICIT 신호(rtm_uri 마커 부재 ∧ phase 1) — placeholder fallback 흡수 아님.
    """
    if phase not in (1, 2):
        _error(f"--phase 는 1|2 만 허용 (받음: {phase!r}) — fail-closed.")
        return EXIT_FAIL

    # 입력 파일 read (부재·unreadable → 판정불가 fail-closed)
    ac_text = _read_file(ac_source_path)
    if ac_text is None:
        _error(f"--ac-source 읽기 실패/부재: {ac_source_path} (판정불가, fail-closed).")
        return EXIT_FAIL

    # ── per-PR applicability verdict (core 단일 소유, ADR-145 §결정8 D) ──
    verdict, records, ac_note = classify_ac_source(ac_text)
    if verdict == APPLIC_UNDECIDABLE:
        _error(f"AC source 판정불가: {ac_note} — anti-degradation(skip 흡수 금지), fail-closed FAIL.")
        return EXIT_FAIL
    if verdict == APPLIC_SURFACE_EMPTY:
        # 빈 AC 목록 = bypass vector F-AC7-a → FAIL (AC-7 no-optout, 재개방 금지)
        _error(f"빈 AC 목록(§5 표 present, 0 rows) — 빈 AC bypass(F-AC7-a) 차단, fail-closed FAIL. ({ac_note})")
        return EXIT_FAIL
    if verdict == APPLIC_NO_AC_SURFACE:
        # 비적용 positive 확정(§5 AC 선언 표면 부재) → in-job genuine PASS(skip-as-job 아님, §결정8 A/E).
        _notice(
            f"AC-traceability 게이트 비적용 PASS — {ac_note} (phase={phase}, 추적할 normative AC 0). "
            f"{APPLICABILITY_DISCLOSURE}"
        )
        return EXIT_PASS

    # ── verdict == APPLIC_SURFACE_PRESENT (records 실재) ──
    # Hop1 well-formedness 는 records 존재 시 항상 검증 (malformed = degraded → FAIL; F-AC2-MALFORMED 보존).
    hop1_violations = hop1_ac_wellformed(records)           # R2 (malformed → FAIL)

    # 비적용-유사: records present 이나 0 normative(전부 declared/advisory) = 추적할 normative AC 부재
    #   → PASS(§결정8 B(ii)). 단 malformed(Hop1 위반) 은 degraded → FAIL(well-formed 전제).
    normative_count = sum(1 for r in records if r.get("tier") == "normative")
    if normative_count == 0:
        if hop1_violations:
            for v in hop1_violations:
                _error(v)
            _error(f"AC 표 malformed(0 normative 이나 well-formed 아님) — degraded fail-closed FAIL. {CEILING_DISCLOSURE}")
            return EXIT_FAIL
        _notice(
            f"AC-traceability 게이트 비적용 PASS — records={len(records)} 전부 declared/advisory(0 normative). "
            f"{APPLICABILITY_DISCLOSURE}"
        )
        return EXIT_PASS

    # ── 적용 (≥1 normative) — RTM 필요 ──
    # RTM not-yet EXPLICIT 신호(Phase-1 §8 RTM = not-yet-applicable). placeholder fallback 흡수 아님.
    if rtm_not_yet:
        if phase == 2:
            _error("--phase 2 인데 --rtm-not-yet — RTM 은 Phase-2 필수 산출물(fail-closed FAIL).")
            return EXIT_FAIL
        # phase 1: Hop1 only (Hop2 skip — rtm 미해결). placeholder false-fail 제거.
        if hop1_violations:
            for v in hop1_violations:
                _error(v)
            _error(f"Phase-1 Hop1 위반 (fail-closed). {CEILING_DISCLOSURE}")
            return EXIT_FAIL
        _notice(
            f"AC-traceability 게이트 PASS — phase=1, AC={len(records)}, RTM not-yet-applicable "
            f"(rtm_uri EXPLICIT 부재 → Hop1 only, placeholder fallback 아님). {APPLICABILITY_DISCLOSURE} {CEILING_DISCLOSURE}"
        )
        return EXIT_PASS

    # rtm 필요 — read + resolve.
    if rtm_path is None:
        _error("--rtm 미지정(또한 --rtm-not-yet 아님) — RTM 판정불가 (fail-closed).")
        return EXIT_FAIL
    rtm_text = _read_file(rtm_path)
    if rtm_text is None:
        _error(f"--rtm 읽기 실패/부재: {rtm_path} (판정불가, fail-closed).")
        return EXIT_FAIL

    # RTM 위치 resolve (개발서사 placeholder 함정 방지 — ADR-145 §결정6 P1)
    rtm_section, rtm_note = resolve_rtm_location(rtm_text)
    if rtm_section is None:
        # 미선언 §8 / placeholder = bypass vector F-AC7-b/b2 → FAIL
        _error(f"RTM 미해결: {rtm_note} (판정불가/미선언 §8 F-AC7-b/b2, fail-closed).")
        return EXIT_FAIL
    rtm_mapping, _tier_map = parse_rtm_table(rtm_section)
    if rtm_mapping is None:
        _error("RTM(§8.1) 표 파싱 실패 — AC↔명명 테스트 매핑 미발견 (판정불가, fail-closed).")
        return EXIT_FAIL

    violations = list(hop1_violations)
    violations.extend(hop2_coverage(records, rtm_mapping))  # R3 / R8 (미매핑 → FAIL)

    if phase == 2:
        if tests_root is None:
            _error("--phase 2 인데 --tests-root 미지정 — born-missing 판정불가 (fail-closed).")
            return EXIT_FAIL
        symbols = collect_test_symbols(tests_root)
        if symbols is None:
            _error(f"--tests-root 부재(디렉터리 아님): {tests_root} — born-missing 판정불가 (fail-closed).")
            return EXIT_FAIL
        violations.extend(hop3_born_missing(records, rtm_mapping, symbols))  # R5 (born-missing → FAIL)

    if violations:
        for v in violations:
            _error(v)
        _error(
            f"AC-traceability 게이트 FAIL — phase={phase}, 위반 {len(violations)}건 "
            f"(fail-closed, exit 1). {CEILING_DISCLOSURE}"
        )
        return EXIT_FAIL

    _notice(
        f"AC-traceability 게이트 PASS — phase={phase}, AC={len(records)}, "
        f"RTM 매핑={len(rtm_mapping)} (AC source: {ac_note}; RTM: {rtm_note}). "
        f"{CEILING_DISCLOSURE} {SCOPE_DISCLOSURE}"
    )
    return EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "AC-ID zero-drop fail-closed 게이트 (Hop1 AC well-formed / Hop2 AC↔§8 coverage / "
            "Hop3 §8↔실 symbol born-missing). presence/mapping 만 강제 — semantic 완전성 미강제(AC-8)."
        )
    )
    parser.add_argument("--phase", required=True, type=int, choices=(1, 2),
                        help="EXPLICIT phase 신호 (1=문서·명명 / 2=구현·born-missing). diff 추론 금지.")
    parser.add_argument("--ac-source", required=True,
                        help="AC 목록 문서(§5 AC 표 포함) 경로.")
    parser.add_argument("--rtm", default=None,
                        help="RTM 문서(§8 Test Contract) 경로. wrapper-self=Change Plan §8 / consumer=Story §8. "
                             "적용 PR 필수 (단 --rtm-not-yet 시 생략 가능).")
    parser.add_argument("--rtm-not-yet", dest="rtm_not_yet", action="store_true",
                        help="Phase-1 RTM not-yet-applicable EXPLICIT 신호 (rtm_uri 마커 부재 ∧ phase 1). "
                             "적용 PR 이면 Hop1 only(Hop2 skip). placeholder fallback 흡수 아님. phase 2 = FAIL.")
    parser.add_argument("--tests-root", default=None,
                        help="born-missing 해석 루트(phase 2 필수). 명명 테스트 실 symbol ast resolve.")
    args = parser.parse_args(argv)
    return run(
        phase=args.phase,
        ac_source_path=args.ac_source,
        rtm_path=args.rtm,
        tests_root=args.tests_root,
        rtm_not_yet=args.rtm_not_yet,
    )


if __name__ == "__main__":
    sys.exit(main())
