#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_disjoint_axis_whitelist.py — ADR-039 inline-whitelist static-integrity lint
#
# Carrier: CFP-2572 Phase 2 (구현) / ADR-142 §결정 3 / ADR-039 §결정 2 Count 정합.
#
# Tier: [물리강제 — ADR-integrity 정적, 유일 물리강제].
#   본 lint 은 ADR **STATIC INTEGRITY** 만 단언한다 (behavior 강제 아님) — ADR-039
#   §결정 2 inline-whitelist 의 effective count 정합 + return-envelope-v1.md 의
#   disjoint-axis 선언 무결성. runtime 반환/inline-vs-spawn 행위를 강제하지 않는다.
#
# 책임 (3 check — 전부 hold 해야 PASS, 아니면 exit != 0):
#   (C1) effective inline-whitelist total == 6 (ADR-039 §결정 2 Count 정합 pin):
#        base-4 (§결정2 base 표 numbered entry 1-4) + Amd2 entry5 (§결정15 "5번째 entry")
#        + Amd6 entry6 (§결정18 "6번째 entry") = 6. 세 소스를 모두 세어 합이 6 이어야 한다.
#        §결정2 base 표만 세는(=4) 구현은 BORN-BROKEN (CFP-2530/2527/2535 self-defeating
#        lineage) — 회피. 명칭 = "inline-whitelist" (NOT "inline-write" — 6 entry 안에
#        read entry3 / status entry4 / merge-Codex entry6 포함, write-only 아님).
#   (C2) return-envelope-v1.md 가 리터럴 "disjoint axis" 선언 보유 (ADR-039 §결정 2 무침범).
#   (C3) return-envelope-v1.md 가 자신을 inline-whitelist entry 로 self-claim 하지 않음.
#
# RED 진정성 (test-check-disjoint-axis-whitelist.sh discriminating):
#   R1 = §결정2 base 표에 가짜 7번째 entry(추가 표 row) 주입 → base != 4 / effective 7 → C1 RED.
#   R2 = return-envelope-v1.md fixture 에서 "disjoint axis" 절 제거 → C2 RED.
#   R3 = return-envelope-v1.md fixture 가 inline-whitelist entry 로 self-claim → C3 RED.
#   각 RED 는 표적 check 만 fire (sentinel 규율 — required/forbidden).
#
#   주의(false-oracle 회피): ADR-039 본문에는 "7번째 entry 신설 = amendment 의무" 류 META
#   텍스트가 GREEN 에 이미 존재하므로 "7번째 entry" grep 으로 R1 을 잡을 수 없다 → base 표
#   numbered row COUNT 로 판정한다 (§결정2 섹션 경계 안).
#
# 불변식:
#   - 0 API call, local read only.
#   - 3-tier exit: 0 PASS / 1 violation / 2 setup error.
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
    "ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md",
)
_DEFAULT_LDOC_REL = os.path.join(
    "docs", "inter-plugin-contracts", "return-envelope-v1.md"
)

_EXPECTED_BASE = 4        # §결정2 base 표 numbered entry (1-4)
_EXPECTED_EFFECTIVE = 6   # base-4 + entry5(Amd2) + entry6(Amd6)


# ─────────────────────── 섹션 추출 유틸 ──────────────────────────────────────

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
    """§결정2 base 표에서 첫 cell 이 정수인 표 row 수 (numbered entry count).

    header `| # |` / separator `|---|` 는 첫 cell 이 숫자가 아니므로 미포함.
    """
    count = 0
    for line in section.splitlines():
        if re.match(r"^\s*\|\s*\d+\s*\|", line):
            count += 1
    return count


# ─────────────────────── (C1) ADR-039 effective count == 6 ───────────────────

def _check_adr_effective_count(adr_text, violations):
    """(C1) ADR-039 §결정 2 effective inline-whitelist total == 6.

    3 소스 합산: base 표(=4) + §결정15 entry5 + §결정18 entry6.
    """
    # §결정 2 base 표 섹션 경계 (§결정 2 → §결정 3). "결정 20" 오매칭 회피 (?![0-9]).
    section2 = _extract_section(
        adr_text, r"### 결정 2(?![0-9])", r"### 결정 3(?![0-9])"
    )
    if section2 is None:
        violations.append("(C1) ADR-039 §결정 2 섹션 부재 — inline-whitelist base 표 미검출")
        return

    base = _count_base_table_entries(section2)
    if base != _EXPECTED_BASE:
        violations.append(
            "(C1) ADR-039 §결정 2 base 표 numbered entry = %d (기대 4) — "
            "가짜 7번째 entry 주입 등 tamper 의심" % base
        )

    # entry5 = Amd2 §결정15 가 "5번째 entry" 선언
    has_e5 = bool(re.search(r"### 결정 15(?![0-9])", adr_text)) and ("5번째 entry" in adr_text)
    if not has_e5:
        violations.append("(C1) Amd2 §결정 15 '5번째 entry' 선언 부재 (entry5 소스 누락)")

    # entry6 = Amd6 §결정18 가 "6번째 entry" 선언
    has_e6 = bool(re.search(r"### 결정 18(?![0-9])", adr_text)) and ("6번째 entry" in adr_text)
    if not has_e6:
        violations.append("(C1) Amd6 §결정 18 '6번째 entry' 선언 부재 (entry6 소스 누락)")

    effective = base + (1 if has_e5 else 0) + (1 if has_e6 else 0)
    if effective != _EXPECTED_EFFECTIVE:
        violations.append(
            "(C1) effective inline-whitelist total = %d (기대 6) — "
            "base %d + entry5 %s + entry6 %s" % (effective, base, has_e5, has_e6)
        )


# ─────────────────────── (C2)/(C3) return-envelope-v1.md ─────────────────────

# self-claim 탐지 — return-envelope 를 주어로 inline-whitelist entry 라고 긍정 copula 로 단언.
#   GREEN 의 부정 disclaimer("...entry 가 아니며")는 entry 직후 copula(이다/이며..)가
#   오지 않으므로 미매칭. R3 fixture "... whitelist 의 7번째 entry 이다" 는 매칭.
_SELF_CLAIM_RE = re.compile(
    r"(return-envelope|본 계약|본 contract|본 문서)"
    r"[^\n]{0,60}?(inline[- ]?whitelist|whitelist)"
    r"[^\n]{0,30}?(\d+\s*번째\s*)?entry\s*"
    r"(이다|이며|입니다|로 등록|에 해당|로 추가)"
)


def _check_ldoc_disjoint_axis(ldoc_text, violations):
    """(C2) disjoint-axis 선언 존재 + (C3) self-claim 부재."""
    # (C2) 리터럴 "disjoint axis" 선언 (ADR-039 §결정 2 무침범 MANDATORY declaration)
    if not re.search(r"disjoint\s+axis", ldoc_text, re.IGNORECASE):
        violations.append(
            "(C2) return-envelope-v1.md 'disjoint axis' 선언 부재 — "
            "ADR-039 §결정 2 무침범 declaration(§5) 필수"
        )

    # (C3) self-claim 금지 — inline-whitelist entry 로 자칭 금지 (긍정 copula, 부정 아님)
    m = _SELF_CLAIM_RE.search(ldoc_text)
    if m and "아니" not in m.group(0):
        violations.append(
            "(C3) return-envelope-v1.md self-claim 검출 — inline-whitelist entry 로 "
            "자칭 ('%s') — disjoint axis 위반" % m.group(0).strip()
        )


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def _read_file(path, label):
    if not os.path.isfile(path):
        print(
            "[codeforge-disjoint-axis-lint-setup-error] check-disjoint-axis-whitelist: "
            "%s file 부재: %s" % (label, path),
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        print(
            "[codeforge-disjoint-axis-lint-setup-error] check-disjoint-axis-whitelist: "
            "%s read 실패: %s" % (label, e),
            file=sys.stderr,
        )
        sys.exit(2)


def cmd_check(args):
    repo_root = args.repo_root or "."
    adr_path = args.adr_path or os.path.join(repo_root, _DEFAULT_ADR_REL)
    ldoc_path = args.ldoc_path or os.path.join(repo_root, _DEFAULT_LDOC_REL)

    adr_text = _read_file(adr_path, "ADR-039")
    ldoc_text = _read_file(ldoc_path, "return-envelope-v1.md")

    violations = []
    _check_adr_effective_count(adr_text, violations)   # (C1)
    _check_ldoc_disjoint_axis(ldoc_text, violations)   # (C2)/(C3)

    if violations:
        for v in violations:
            print("::warning::check-disjoint-axis-whitelist: VIOLATION — %s" % v)
        print("")
        print(
            "check-disjoint-axis-whitelist: %d violation "
            "([물리강제] ADR-integrity 정적 — effective inline-whitelist total 6 정합 / "
            "disjoint-axis 선언 무결성)." % len(violations)
        )
        sys.exit(1)

    print(
        "check-disjoint-axis-whitelist: PASS — (C1) effective inline-whitelist total == 6 "
        "(base4 + entry5 + entry6) / (C2) disjoint-axis 선언 존재 / (C3) self-claim 부재"
    )
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="ADR-039 inline-whitelist static-integrity lint "
        "(CFP-2572 Phase 2 — [물리강제] ADR-integrity, effective count 6 + disjoint-axis)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_p = subparsers.add_parser("check", help="ADR-integrity 검증")
    check_p.add_argument("--adr-path", default="",
                         help="ADR-039 경로 (default: <repo-root>/archive/adr/ADR-039-...md)")
    check_p.add_argument("--ldoc-path", default="",
                         help="return-envelope-v1.md 경로 (default: <repo-root>/docs/...)")
    check_p.add_argument("--repo-root", default=".",
                         help="repo root (default 현재 디렉터리)")

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
