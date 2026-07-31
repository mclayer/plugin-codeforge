#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_disjoint_axis_whitelist.py — ADR-170 inline-whitelist static-integrity lint
#
# Carrier: CFP-2572 Phase 2 (원 도입 — 구 ADR-039 대상) / CFP-2869 Phase 2 (ADR-039→ADR-170
#   재제정 대응 재저작 — 대상 재타깃 + declared-vs-actual self-consistency 전환).
# 근거: ADR-142 §결정 3 / ADR-170 §결정 2 (7-entry flat 단일표 + 정형 선언 라인).
#
# Tier: [물리강제 — ADR-integrity 정적, 유일 물리강제].
#   본 lint 은 ADR **STATIC INTEGRITY** 만 단언한다 (behavior 강제 아님) — ADR-170
#   §결정 2 inline-whitelist 의 문서 내부 self-consistency + return-envelope-v1.md 의
#   disjoint-axis 선언 무결성. runtime 반환/inline-vs-spawn 행위를 강제하지 않는다.
#
# 책임 (4 check — 전부 hold 해야 PASS, 아니면 exit != 0):
#   (C0) 동결사체 가드 (T-INV-2): lint 대상 ADR frontmatter `status` 가 Superseded 계열
#        (bare / `Superseded by ADR-NNN` / `Superseded-by-ADR-NNN` 3형) 이면 RED.
#        재제정으로 동결된 구본을 대상에 남긴 배선 오류가 영구-PASS hollow-gate 로
#        굳는 것을 차단한다 (CFP-2869 §8.2 T-INV-2). C0 발화 시 (C1) 은 skip —
#        동결 구본에는 신 구조가 없어 count 판정이 무의미(off-target 잡음 회피).
#   (C1) declared-vs-actual self-consistency (T-INV-1): ADR-170 §결정 2 절 안
#        정형 선언 라인("현행 effective inline-whitelist total = N-entry")의 declared N 이
#        같은 절 flat 단일표의 실 entry row 수(actual)와 일치. 상수 pin(구 `_EXPECTED_*`)
#        폐기 — 8번째 entry 신설 시 lint 무접촉(2-file 동기화 부담 → 단일 문서 내부
#        self-consistency 로 축소). 선언 라인 부재 / 2회 이상 출현 = fail-closed RED.
#   (C2) return-envelope-v1.md 가 리터럴 "disjoint axis" 선언 보유 (ADR-170 §결정 2 무침범).
#   (C3) return-envelope-v1.md 가 자신을 inline-whitelist entry 로 self-claim 하지 않음
#        (긍정 copula 만 RED — 부정 어미 자연 문구는 lookahead 로 비매칭, 오탐 0).
#
# RED 진정성 (test-check-disjoint-axis-whitelist.sh discriminating — M1~M9, Story CFP-2869 §8.3):
#   M1 = flat 표 마지막 row 뒤 out-of-band fake row `| 99 |` 주입 → declared 7 ≠ actual 8 → C1 RED.
#   M2 = 정형 선언 값 변조("= 7-entry" → "= 9-entry") → declared 9 ≠ actual 7 → C1 RED.
#   M3 = 정형 선언 라인 삭제 → 부재 fail-closed → C1 RED.
#   M4 = 대상 ADR 을 Superseded 동결 구본(ADR-039)으로 지정 → C0 RED.
#   M5 = flat 표 row 1개 삭제 → declared 7 ≠ actual 6 → C1 RED.
#   M6 = 무변조 정본 (negative control) → PASS.
#   M7 = LDOC "disjoint axis" 선언 제거 → C2 RED.
#   M8 = LDOC 긍정 copula self-claim 주입 → C3 RED (+ 부정 어미 3형 negative control = PASS).
#   M9 = §결정 2 절 **밖**(§결정 20/21)에 위장 row `| 8 |` 주입 → PASS 유지.
#        섹션 경계 lookahead(`### 결정 2(?![0-9])`→`### 결정 3(?![0-9])`)를 지키지 않아
#        절 밖을 계상하는 구현이면 declared 7 ≠ actual 8 로 자기 검출 (T-INV-4).
#
#   주의(false-oracle 회피): ADR-170 본문에는 "8번째 entry 신설 = amendment 의무" 류 META
#   텍스트가 GREEN 에 이미 존재하므로 "8번째 entry" grep 으로 M1 을 잡을 수 없다 → 표
#   numbered row COUNT 와 정형 선언 값의 **상호 대조**로 판정한다 (§결정 2 절 경계 안).
#
# 불변식:
#   - 0 API call, local read only.
#   - 3-tier exit: 0 PASS / 1 violation / 2 setup error.
#   - bounded quantifier only (무제한 `.*` 전문 스캔 미사용) + frontmatter linewise bounded
#     parse — resource 정직: bounded degradation 이지 "임의 입력 무해" 단정 아님
#     (ADR-168 §결정 16 honest ceiling 상속).
#
# 사용:
#   python3 check_disjoint_axis_whitelist.py check \
#     [--adr-path <path>] [--ldoc-path <path>] [--repo-root <path>]
#
# Prior art: check_spawn_event_schema.py (ADR-061 Python entry + thin wrapper convention).

import argparse
import os
import re
import sys

# Windows cp949 인코딩 회피 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_DEFAULT_ADR_REL = os.path.join(
    "archive", "adr",
    "ADR-170-orchestrator-subagent-default-inline-whitelist.md",
)
_DEFAULT_LDOC_REL = os.path.join(
    "docs", "inter-plugin-contracts", "return-envelope-v1.md"
)

# §결정 2 절 경계 — 원번호 보존 전제(T-INV-4). lookahead 필수: `### 결정 20/21` over-match 금지.
_SECTION2_START = r"### 결정 2(?![0-9])"
_SECTION2_END = r"### 결정 3(?![0-9])"

# 정형 선언 라인 (ADR-170 §결정 2 실물 문구 앵커) — declared count 소스.
#   실물: `**현행 effective inline-whitelist total = 7-entry** — 위 flat 단일표가 ...`
_DECLARED_TOTAL_RE = re.compile(
    r"현행\s{0,8}effective\s{0,8}inline-whitelist\s{0,8}total\s{0,8}=\s{0,8}(\d{1,3})-entry"
)

# frontmatter linewise parse 상한 (bounded scan — 전문 regex backtracking 표면 0).
_FRONTMATTER_MAX_LINES = 400

# Superseded 계열 3형 판정 (delimiter-anchored — `supersededxyz` 류 garbage 배제).
#   semantics SSOT = scripts/lib/check_adr_amendment_threshold.py::is_superseded_status.
#   그 모듈 직접 import 미채택 근거 (firsthand): 해당 모듈은 import 시점 pyyaml 부재 시
#   `sys.exit(1)` fail-closed 이고(동 파일 `except ImportError` 블록), 본 lint 의
#   workflow(.github/workflows/disjoint-axis-whitelist-lint.yml)에는 pyyaml 설치 step 이
#   없다 → import 채택 시 본 게이트가 born-broken. 동일 semantics 를 1-line predicate 로 유지.
_SUPERSEDED_STATUS_RE = re.compile(r"superseded($|[\s\-])")


# ─────────────────────── 공통 유틸 ──────────────────────────────────────────────

def _setup_error(msg):
    """3-tier exit 의 SETUP error(2) 단일 진입점."""
    print(
        "[codeforge-disjoint-axis-lint-setup-error] check-disjoint-axis-whitelist: %s" % msg,
        file=sys.stderr,
    )
    sys.exit(2)


def _extract_section(text, start_pat, end_pat):
    """start_pat regex 매칭 지점 ~ 그 뒤 첫 end_pat 매칭 지점 사이 텍스트 반환.

    end 미발견 시 문서 끝까지. start 미발견 시 None.
    """
    ms = re.search(start_pat, text)
    if not ms:
        return None
    tail = text[ms.end():]
    me = re.search(end_pat, tail)
    end = ms.end() + me.start() if me else len(text)
    return text[ms.start():end]


def _count_base_table_entries(section):
    """§결정 2 flat 단일표에서 첫 cell 이 정수인 표 row 수 (actual entry count — 단일 카운트 함수).

    header `| # |` / separator `|---|` 는 첫 cell 이 숫자가 아니므로 미포함.
    본 함수가 actual 의 유일 소스다 (C1 declared-vs-actual 대조 — 이중 계상 경로 없음).
    """
    count = 0
    for line in section.splitlines():
        if re.match(r"^\s{0,8}\|\s{0,8}\d{1,3}\s{0,8}\|", line):
            count += 1
    return count


def _extract_frontmatter_status(text):
    """선두 YAML frontmatter 의 `status:` 스칼라 반환 (미검출 = None).

    linewise bounded scan — 전문 regex backtracking 표면 0.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:_FRONTMATTER_MAX_LINES]:
        if line.strip() == "---":
            break
        m = re.match(r"status:\s{0,8}(.{0,200})$", line)
        if m:
            return m.group(1).strip()
    return None


def _is_superseded_status(status):
    """Superseded 계열(bare / 공백 / 하이픈 3형) True. Accepted/Proposed/기타 False."""
    return bool(_SUPERSEDED_STATUS_RE.match(str(status).strip().casefold()))


# ────────── (C0) 동결사체 가드 + (C1) declared-vs-actual self-consistency ──────────

def _check_adr_self_consistency(adr_text, violations):
    """(C0) 대상 ADR 비-Superseded + (C1) §결정 2 정형 선언 == flat 표 row count."""
    # (C0) 동결사체 가드 — Superseded 구본을 대상에 남긴 배선 오류 차단 (T-INV-2).
    status = _extract_frontmatter_status(adr_text)
    if status is None:
        _setup_error(
            "대상 ADR frontmatter `status` 미검출 — lint 대상 파일 형식 아님 (배선 확인 필요)"
        )
    if _is_superseded_status(status):
        violations.append(
            "(C0) lint 대상 ADR 이 Superseded 계열 상태('%s') — 동결 구본을 대상에 남긴 "
            "배선 오류 (영구-PASS hollow-gate 차단). 대상 경로를 현행 ADR 로 재지향할 것" % status
        )
        return  # 동결사체에는 신 구조 부재 — (C1) skip (off-target 잡음 회피)

    # (C1) §결정 2 절 경계 안에서만 declared/actual 산출 (절 밖 decoy 미계상 — T-INV-4).
    section2 = _extract_section(adr_text, _SECTION2_START, _SECTION2_END)
    if section2 is None:
        violations.append(
            "(C1) 대상 ADR §결정 2 섹션 부재 — inline-whitelist flat 단일표 미검출"
        )
        return

    declared_hits = _DECLARED_TOTAL_RE.findall(section2)
    if not declared_hits:
        violations.append(
            "(C1) §결정 2 정형 선언 라인('현행 effective inline-whitelist total = N-entry') 부재 "
            "— fail-closed (declared 소스 소실 = 판정 불가)"
        )
        return
    if len(declared_hits) > 1:
        violations.append(
            "(C1) §결정 2 정형 선언 라인 %d 회 출현 (기대 정확히 1) — declared 소스 모호"
            % len(declared_hits)
        )
        return

    declared = int(declared_hits[0])
    actual = _count_base_table_entries(section2)
    if declared != actual:
        violations.append(
            "(C1) declared-vs-actual 불일치 — 정형 선언 %d-entry ≠ §결정 2 flat 표 실 row %d "
            "(표 row 주입·삭제 또는 선언 값 변조 의심)" % (declared, actual)
        )


# ─────────────────────── (C2)/(C3) return-envelope-v1.md ─────────────────────

# self-claim 탐지 — return-envelope 를 주어로 inline-whitelist entry 라고 긍정 copula 로 단언.
#   부정 판정 = 매치 후 필터가 아니라 **매치 시점 lookahead** (구 `"아니" not in group(0)`
#   후처리는 첫 매치만 보고, "…로 추가되지 않는다" 류를 오탐했다 — CFP-2869 A-6 해소).
#   GREEN 부정 어미 3형 전부 비매칭: "…entry 가 아니며"(copula 미도달) /
#   "…로 추가되지 않는다" / "…entry 로 등록하지 않는다"(부정 어미 lookahead 차단).
_SELF_CLAIM_RE = re.compile(
    r"(?:return-envelope|본 계약|본 contract|본 문서)"
    r"[^\n]{0,60}?(?:inline[- ]?whitelist|whitelist)"
    r"[^\n]{0,30}?(?:\d{1,3}\s{0,4}번째\s{0,4})?entry\s{0,4}"
    r"(?:이다|이며|입니다|로 등록|에 해당|로 추가)"
    r"(?!\s{0,4}(?:하지|되지|지)?\s{0,4}않)"
)


def _check_ldoc_disjoint_axis(ldoc_text, violations):
    """(C2) disjoint-axis 선언 존재 + (C3) self-claim 부재."""
    # (C2) 리터럴 "disjoint axis" 선언 (ADR-170 §결정 2 무침범 MANDATORY declaration)
    if not re.search(r"disjoint\s{0,4}axis", ldoc_text, re.IGNORECASE):
        violations.append(
            "(C2) return-envelope-v1.md 'disjoint axis' 선언 부재 — "
            "ADR-170 §결정 2 무침범 declaration(§5) 필수"
        )

    # (C3) self-claim 금지 — inline-whitelist entry 로 자칭 금지 (긍정 copula 한정)
    m = _SELF_CLAIM_RE.search(ldoc_text)
    if m:
        violations.append(
            "(C3) return-envelope-v1.md self-claim 검출 — inline-whitelist entry 로 "
            "자칭 ('%s') — disjoint axis 위반" % m.group(0).strip()
        )


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def _read_file(path, label):
    if not os.path.isfile(path):
        _setup_error("%s file 부재: %s" % (label, path))
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        _setup_error("%s read 실패: %s" % (label, e))


def cmd_check(args):
    repo_root = args.repo_root or "."
    adr_path = args.adr_path or os.path.join(repo_root, _DEFAULT_ADR_REL)
    ldoc_path = args.ldoc_path or os.path.join(repo_root, _DEFAULT_LDOC_REL)

    adr_text = _read_file(adr_path, "ADR-170")
    ldoc_text = _read_file(ldoc_path, "return-envelope-v1.md")

    violations = []
    _check_adr_self_consistency(adr_text, violations)   # (C0)/(C1)
    _check_ldoc_disjoint_axis(ldoc_text, violations)    # (C2)/(C3)

    if violations:
        for v in violations:
            print("::warning::check-disjoint-axis-whitelist: VIOLATION — %s" % v)
        print("")
        print(
            "check-disjoint-axis-whitelist: %d violation "
            "([물리강제] ADR-integrity 정적 — 대상 ADR 비-Superseded / §결정 2 "
            "declared-vs-actual self-consistency / disjoint-axis 선언 무결성)." % len(violations)
        )
        sys.exit(1)

    print(
        "check-disjoint-axis-whitelist: PASS — (C0) 대상 ADR 비-Superseded / "
        "(C1) §결정 2 정형 선언 == flat 표 row count / (C2) disjoint-axis 선언 존재 / "
        "(C3) self-claim 부재"
    )
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="ADR-170 inline-whitelist static-integrity lint "
        "(CFP-2869 Phase 2 재저작 — [물리강제] ADR-integrity, declared-vs-actual "
        "self-consistency + disjoint-axis)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_p = subparsers.add_parser("check", help="ADR-integrity 검증")
    check_p.add_argument("--adr-path", default="",
                         help="대상 ADR 경로 (default: <repo-root>/archive/adr/ADR-170-...md)")
    check_p.add_argument("--ldoc-path", default="",
                         help="return-envelope-v1.md 경로 (default: <repo-root>/docs/...)")
    check_p.add_argument("--repo-root", default=".",
                         help="repo root (default 현재 디렉터리)")

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
