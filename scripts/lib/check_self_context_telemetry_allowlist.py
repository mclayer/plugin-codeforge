#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_self_context_telemetry_allowlist.py — self-context-v1 allow-list conformance lint
#
# Carrier: CFP-2572 Phase 2 (구현) / ADR-142 §결정 4 / ADR-043 Amendment 3.
#
# Tier: [measurement]. self-context-v1 record type 의 **allow-list conformance + channel liveness**
#   측정 — L7 게이트/block/deny 언어 0. record-only proxy 이지 runtime 강제 아니다
#   (delegation_ratio / pre_tokens = proxy, NOT lead-self ground-truth — ADR-119).
#   본 lint 은 spawn-event-v1.md §2.1 문서가 allow-list POLICY 를 well-formed 로 선언했는지만
#   측정한다 (well-formed 검증). emission liveness 는 test-check-*.sh 가 실 emit 경로 구동으로 검증.
#
# 책임 (spawn-event-v1.md §2.1 self-context-v1 record type — 전부 hold 해야 PASS):
#   (S1) allow-list membership — 정확히 6 field {schema_version, session_id, turn_index,
#        delegation_ratio, pre_tokens, cause_category}. 7번째 field 존재 = violation.
#   (S2) numeric/enum/hash only — free-form string field 0 (타입 cell 검증).
#   (S3) opt-in default-false 선언 존재.
#   (S4) FORBIDDEN list 존재 (file path / transcript / tool_input / free-form).
#   (S5) cause_category CLOSED enum 7값 전부 존재.
#   (S6) proxy != ground-truth verbatim — "delegation_ratio / pre_tokens = proxy ...
#        not ... ground-truth" 진술 존재 (ADR-119 hollow-gate 정직).
#
# RED 진정성 (test-check-self-context-telemetry-allowlist.sh discriminating):
#   RC1: 기존 field 타입을 free-form string 으로 변경 → (S2) RED.
#   RC2: opt-in default-false 선언 제거 → (S3) RED.
#   RC3: 7번째 non-allowlist field 추가 → (S1) RED.
#   RC4: proxy != ground-truth 진술 제거 → (S6) RED.
#   + EMISSION-LIVENESS: 실 emit 경로(append_self_context_event.py) 구동 → 1 record land 검증
#     (presence-grep false oracle 금지 — execution-backed).
#
# 불변식: 0 API call, local read only. 3-tier exit: 0 PASS / 1 violation / 2 setup error.
#
# 사용:
#   python3 check_self_context_telemetry_allowlist.py check [--contract-path <p>] [--repo-root <p>]

import argparse
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_DEFAULT_CONTRACT_REL = os.path.join(
    "docs", "inter-plugin-contracts", "spawn-event-v1.md"
)

# self-context-v1 6-field allow-list (정확 set — SSOT)
_ALLOWLIST_6 = {
    "schema_version", "session_id", "turn_index",
    "delegation_ratio", "pre_tokens", "cause_category",
}
_EXPECTED_FIELD_COUNT = 6

# cause_category CLOSED enum 7값
_CAUSE_ENUM_7 = [
    "read-heavy", "synthesis-inline", "fix-diagnosis", "spawn-dispatch",
    "skill-load", "env0-mediation", "other",
]

# 허용 타입 (numeric / enum / hash only) — 매칭 안 되면 free-form string 의심
_ALLOWED_TYPE_RE = re.compile(r"const string|sha256|hash|\bint\b|float|enum")

# 필드 표 row: `| \`name\` | type | ...`
_FIELD_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|", re.M)

# proxy != ground-truth verbatim — delegation_ratio & pre_tokens 를 한 줄에서 proxy/not-ground-truth 로 단언
_PROXY_RE = re.compile(
    r"delegation_ratio[^\n]{0,40}pre_tokens[^\n]{0,160}ground-truth[^\n]{0,12}(가\s*)?아니"
)


def _extract_section(text, start_pat, end_pat):
    ms = re.search(start_pat, text)
    if not ms:
        return None
    tail = text[ms.end():]
    me = re.search(end_pat, tail)
    end = ms.end() + me.start() if me else len(text)
    return text[ms.start():end]


# ─────────────────────── (S1)/(S2) field 표 conformance ──────────────────────

def _check_field_table(section21, subsection211, violations):
    """(S1) allow-list membership + count == 6 / (S2) numeric/enum/hash only."""
    rows = _FIELD_ROW_RE.findall(subsection211)
    names = [r[0].strip() for r in rows]

    # (S1) count == 6
    if len(names) != _EXPECTED_FIELD_COUNT:
        violations.append(
            "(S1) self-context field 표 row = %d (기대 6) — 7번째 field 주입 등 allow-list 위반"
            % len(names)
        )
    # (S1) membership — allow-list 밖 field 존재 금지
    extra = [n for n in names if n not in _ALLOWLIST_6]
    if extra:
        violations.append(
            "(S1) allow-list 밖 field 검출: %s (6-field allow-list 위반)" % ", ".join(extra)
        )
    # (S1) allow-list 6 전부 존재
    missing = [n for n in _ALLOWLIST_6 if n not in names]
    if missing:
        violations.append(
            "(S1) allow-list 6-field 중 표 미등장: %s" % ", ".join(sorted(missing))
        )

    # (S2) numeric/enum/hash only — 각 field 타입이 허용 타입 매칭 (free-form string 금지)
    for name, type_cell in rows:
        if not _ALLOWED_TYPE_RE.search(type_cell):
            violations.append(
                "(S2) field '%s' 타입 '%s' non-conforming — numeric/enum/hash only 위반 "
                "(free-form string 의심)" % (name.strip(), type_cell.strip())
            )


# ─────────────────────── (S3)~(S6) ──────────────────────────────────────────

def _check_opt_in(section21, violations):
    """(S3) opt-in default-false 선언 존재."""
    if not re.search(r"opt-in default[- ]?false", section21, re.IGNORECASE):
        violations.append("(S3) opt-in default-false 선언 부재 (always-on 금지 상속 누락)")


def _check_forbidden_list(section21, violations):
    """(S4) FORBIDDEN list 존재 (file path / transcript / tool_input / free-form)."""
    if "FORBIDDEN" not in section21:
        violations.append("(S4) FORBIDDEN 선언 부재 (T-INFO-8 구조적 차단 목록 누락)")
        return
    for token in ("file path", "transcript", "tool_input", "free-form"):
        if token not in section21:
            violations.append("(S4) FORBIDDEN 목록 '%s' 항목 부재" % token)


def _check_cause_enum(section21, violations):
    """(S5) cause_category CLOSED enum 7값 전부 존재."""
    missing = [v for v in _CAUSE_ENUM_7 if v not in section21]
    if missing:
        violations.append(
            "(S5) cause_category CLOSED enum 7값 중 미명시: %s" % ", ".join(missing)
        )


def _check_proxy_not_ground_truth(section21, violations):
    """(S6) proxy != ground-truth verbatim (ADR-119 hollow-gate 정직)."""
    if not _PROXY_RE.search(section21):
        violations.append(
            "(S6) 'delegation_ratio / pre_tokens = proxy ... not ... ground-truth' verbatim 부재 "
            "(ADR-119 hollow-gate 정직 진술 누락)"
        )


# ─────────────────────── 서브커맨드: check ───────────────────────────────────

def cmd_check(args):
    repo_root = args.repo_root or "."
    contract_path = args.contract_path or os.path.join(repo_root, _DEFAULT_CONTRACT_REL)

    if not os.path.isfile(contract_path):
        print(
            "[codeforge-self-context-lint-setup-error] check-self-context-telemetry-allowlist: "
            "contract file 부재: %s" % contract_path,
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        with open(contract_path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(
            "[codeforge-self-context-lint-setup-error] check-self-context-telemetry-allowlist: "
            "contract read 실패: %s" % e,
            file=sys.stderr,
        )
        sys.exit(2)

    # §2.1 self-context-v1 record type 섹션 (## 2.1 ~ ## 3)
    section21 = _extract_section(text, r"(?m)^## 2\.1 ", r"(?m)^## 3\.")
    if section21 is None:
        print(
            "[codeforge-self-context-lint-setup-error] check-self-context-telemetry-allowlist: "
            "spawn-event-v1.md §2.1 self-context-v1 섹션 부재",
            file=sys.stderr,
        )
        sys.exit(2)

    # §2.1.1 field 표 sub-block (### 2.1.1 ~ ### 2.1.2)
    subsection211 = _extract_section(section21, r"(?m)^### 2\.1\.1", r"(?m)^### 2\.1\.2")
    if subsection211 is None:
        subsection211 = section21  # fallback — §2.1 전체에서 표 파싱

    violations = []
    _check_field_table(section21, subsection211, violations)  # (S1)/(S2)
    _check_opt_in(section21, violations)                      # (S3)
    _check_forbidden_list(section21, violations)              # (S4)
    _check_cause_enum(section21, violations)                  # (S5)
    _check_proxy_not_ground_truth(section21, violations)      # (S6)

    if violations:
        for v in violations:
            print("::warning::check-self-context-telemetry-allowlist: VIOLATION — %s" % v)
        print("")
        print(
            "check-self-context-telemetry-allowlist: %d violation "
            "([measurement] allow-list conformance — L7 게이트/block/deny 아님)." % len(violations)
        )
        sys.exit(1)

    print(
        "check-self-context-telemetry-allowlist: PASS — [measurement] allow-list conformance "
        "((S1) 6-field allow-list / (S2) numeric·enum·hash only / (S3) opt-in default-false / "
        "(S4) FORBIDDEN list / (S5) cause_category 7-enum / (S6) proxy != ground-truth verbatim). "
        "L7 record-only proxy — 게이트/block/deny 아님."
    )
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="self-context-v1 allow-list conformance lint "
        "(CFP-2572 Phase 2 — [measurement], L7 record-only proxy)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_p = subparsers.add_parser("check", help="allow-list conformance 검증")
    check_p.add_argument("--contract-path", default="",
                         help="spawn-event-v1.md 경로 (default: <repo-root>/docs/...)")
    check_p.add_argument("--repo-root", default=".", help="repo root (default 현재 디렉터리)")

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)


if __name__ == "__main__":
    main()
