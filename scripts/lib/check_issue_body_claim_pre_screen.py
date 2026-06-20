#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_issue_body_claim_pre_screen.py
CFP-2382 / ADR-082 Amendment 20 §결정 15 (CFP-1559 carrier) — issue-body-claim-pre-screen 게이트 (warning tier)

Wave 1 declarative anchor (CFP-1559, evidence-checks-registry entry `issue-body-claim-pre-screen`)
의 Wave 2 mechanical wire. orchestrator-authored followup Issue body 안 4 sub-pattern (PR state /
CFP state / count / sister carrier) stale-claim 을 presence-only 로 검출 — claim regex 옆 동일-line
`[verified-via:` annotation 부재 시 FLAG. S1 (CFP-2381 check_deferred_followup_reconcile.py) 의
::warning::+_emit_flag+_ACTION_GUIDE 구조 답습.

Usage:
  python3 check_issue_body_claim_pre_screen.py <issue-body-file>
    → issue body 파일을 scan, FLAG 1+ 면 exit 1 (warning), FLAG 0 면 exit 0

입력 = live Issue event payload(workflow env ISSUE_BODY → /tmp file → 본 script file-input).
  thin wrapper (scripts/check-issue-body-claim-pre-screen.sh) 가 env → /tmp 파일 변환 담당.

Exit codes (ADR-060 §결정 15 3-tier — warning tier):
  0 = PASS (FLAG 0)
  1 = FLAG 1+ (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
  2 = SETUP error (입력 파일 부재 / 읽기 실패)

검출 알고리즘 (rev2 R3 — blank-split 폐기, line-by-line in_fence toggle masking):
  scripts/lib/check_decision_principle_vocabulary.py:95-118 (line-by-line in_fence boolean +
  fence_marker 추적 + fenced/blockquote 줄 continue masking) 답습 — fenced 블록 내부 빈줄
  fragmentation 불가능 → fenced 내부 예시 claim FP=0. 추가로 inline code-span strip (본 lint 신규).

4 sub-pattern (rev2 R2 — count enum 한글 확장, F6 — count-명백 단위만):
  (a) PR #NNNN  — anchored `PR #\d+` (bounded, nested quantifier 금지 — CFP-1497 ReDoS-safe)
  (b) CFP-NNNN MERGED/CLOSED state — `CFP-\d{4,5}` + state keyword (MERGED|CLOSED|merged|closed)
  (c) count number — `\d+\s*(영문 enum|한글 count-명백 단위)` ; ordinal-모호(번/항목/차례) 제외 (F6 FP 보수)
  (d) sister carrier — `(carrier|sibling|paired)\s*:?\s*CFP-\d+`

ADR refs: ADR-082 Amendment 20 §결정 15 / ADR-060 / ADR-061 / ADR-127
"""

import re
import sys

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# unbounded scan 차단 (CFP-1497 PR #1499 sentinel 정신 — 대형 body ReDoS/DoS 보호).
# 목적 = unbounded scan 차단이지 의도적 truncation 아님. followup body 길이 분포 실측 후 상향 가능.
PER_FILE_SCAN_CAP = 50

# annotation presence 마커 (정적 substring grep — regex 아님, ReDoS-free)
ANNOTATION_MARKER = "[verified-via:"

# ─────────────────────── 4 sub-pattern closed-set regex (anchored, ReDoS-safe) ──
# 모두 bounded quantifier — nested quantifier 절대 금지 (CFP-1497 PR #1499 sentinel 답습).

# (c) count 단위 enum (rev2 R2 한글 확장 + F6 ordinal-모호 단위 제외):
#   영문 (registry verbatim) + 한글 count-명백 단위(건/개/곳/줄/회/어휘)만.
#   ordinal-모호(번/항목/차례)는 제외 — `4번째`(ordinal≠count) FP 보수.
_COUNT_UNIT_ENUM = (
    r"VIOLATIONs?|defects?|occurrences?|times?|pattern_count"  # 영문 (registry verbatim)
    r"|건|개|곳|줄|회|어휘"                                       # 한글 count-명백 단위 (F6 — ordinal-모호 제외)
)

# state keyword (b) — PR/CFP merge state stale 신호
_STATE_KEYWORD = r"MERGED|CLOSED|merged|closed"

_PATTERNS = [
    # (a) PR #NNNN merge state mention
    ("a", re.compile(r"PR #\d+")),
    # (b) CFP-NNNN + state keyword 동반 (state 미동반 단순 CFP 인용은 미검출 — stale state claim 한정)
    ("b", re.compile(r"CFP-\d{4,5}\b.{0,40}?(?:" + _STATE_KEYWORD + r")")),
    # (c) count number + count-명백 단위 (직접 인접, 한글 공백 무/유 양립 \s*)
    ("c", re.compile(r"\d+\s*(?:" + _COUNT_UNIT_ENUM + r")")),
    # (d) sister carrier attribution
    ("d", re.compile(r"(?:carrier|sibling|paired)\s*:?\s*CFP-\d+")),
]

# pattern 별 verified-via hint (R5 — author 가 부착할 annotation 가이드)
_PATTERN_HINT = {
    "a": "[verified-via: gh pr view <N> state=MERGED pinned_at:<ts>]",
    "b": "[verified-via: gh issue view <CFP> state=...]",
    "c": "[verified-via: <grep/count 명령> count=<N>]",
    "d": "[verified-via: <carrier 출처 확인>]",
}


# ─────────────────────── inline code-span strip (rev2 R3, F7) ────────────────

def strip_inline_code(line):
    """
    line 내 inline code-span (backtick `...` pair) 구간을 공백으로 masking.

    F7 (잔여 P2) — unbalanced / double-backtick(``) / nested 경계 안전 처리:
      - balanced pair 만 strip (정규 markdown inline code).
      - dangling(홀수) backtick 은 strip 안 함 (마지막 미닫힘 backtick 이후 텍스트 보존 —
        unbalanced 일 때 claim 을 임의로 삼키지 않음, FP-안전 방향: 오히려 검출 보존).
      - double-backtick(``code``) span: GFM 은 동일 run 길이 fence pair 매칭. 본 strip 은
        run-length 매칭으로 ``...`` 도 한 쌍으로 인식 (single 보다 longer run 우선).
      - nested 는 markdown inline code 에 부재 (code-span 내부는 literal) — run-length 매칭이
        자연 처리 (open run 과 동일 길이 close run 까지 literal).

    반환: code-span 구간이 동일 길이 공백으로 치환된 line (line_num/offset 보존).
    """
    if "`" not in line:
        return line

    out = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch != "`":
            out.append(ch)
            i += 1
            continue
        # backtick run 길이 측정 (open fence)
        run_start = i
        while i < n and line[i] == "`":
            i += 1
        run_len = i - run_start
        open_ticks = "`" * run_len
        # 동일 길이 close run 탐색 (GFM run-length 매칭)
        close_idx = line.find(open_ticks, i)
        if close_idx == -1:
            # unbalanced — 닫는 run 부재 → strip 안 함 (open ticks literal 보존, FP-안전)
            out.append(open_ticks)
            continue
        # balanced span: open run + 내부 + close run 전체를 공백으로 masking (길이 보존)
        span_end = close_idx + run_len
        out.append(" " * (span_end - run_start))
        i = span_end
    return "".join(out)


# ─────────────────────── scan (line-by-line in_fence toggle masking) ─────────

def scan_issue_body(body_text):
    """
    issue body 본문을 line-by-line state machine 으로 scan.

    rev2 R3: blank-split 폐기 → in_fence toggle masking
      (check_decision_principle_vocabulary.py:95-118 답습 — fenced/blockquote 줄 continue,
       fenced 내부 빈줄 fragmentation 불가능 → fenced 내부 예시 claim FP=0).

    Returns: list of (line_num, raw_line, pattern_name, matched_text) — unverified claim.
    """
    findings = []
    in_fence = False
    fence_marker = None
    for line_num, raw_line in enumerate(body_text.splitlines(), start=1):
        if line_num > PER_FILE_SCAN_CAP:
            break
        stripped = raw_line.lstrip()

        # ── fence toggle masking (code-span EXEMPT) — claim regex 보다 먼저 ──
        if not in_fence:
            for marker in ("```", "~~~"):
                if stripped.startswith(marker):
                    in_fence = True
                    fence_marker = marker
                    break
            if in_fence:
                continue  # fence 개시 줄도 mask
        else:
            if fence_marker and stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = None
            continue  # fence 내부 全 줄 mask (내부 빈줄 무관 — fragmentation 0)

        # ── blockquote EXEMPT ──
        if stripped.startswith(">"):
            continue

        # ── inline code-span 제거 (line 내 `...` 구간 masking, F7 safe) ──
        line_masked = strip_inline_code(raw_line)

        # ── 동일-line annotation presence (raw_line 기준 — annotation 자체는 mask 무관) ──
        has_annotation = ANNOTATION_MARKER in raw_line

        # ── claim regex 매치 시 (annotation 부재면 FLAG) ──
        for pat_name, pat in _PATTERNS:
            m = pat.search(line_masked)
            if m and not has_annotation:
                findings.append((line_num, raw_line.rstrip(), pat_name, m.group(0)))
                # 동일 line 다중 패턴 누적: 한 line 에서 패턴별 1회만 (중복 noise 회피)
    return findings


# ─────────────────────── 출력 (S1 _emit_flag + _ACTION_GUIDE 답습, R5) ───────

def _emit_flag(item):
    line_num, raw_line, pat_name, matched = item
    hint = _PATTERN_HINT.get(pat_name, "[verified-via: ...]")
    print(
        "::warning::check-issue-body-claim-pre-screen: FLAG — "
        "pattern=%s line=%s claim=\"%s\" hint='%s'"
        % (pat_name, line_num, matched, hint)
    )


_ACTION_GUIDE = (
    "[issue-body-claim-pre-screen] 강제 action 2택 (warning mode — merge 비차단, advisory):\n"
    "  ① claim 검증 후 동일 line 에 `[verified-via: ...]` annotation 부착\n"
    "     (pattern 별 hint 참조 — gh pr view / gh issue view / grep count / carrier 출처)\n"
    "  ② hotfix-bypass:issue-body-claim-pre-screen label + audit comment\n"
    "     (check-bypass-audit-comment.sh 마커 패턴)\n"
    "근거: ADR-082 Amendment 20 §결정 15 (CFP-1559) — Issue body stale-claim verify-before-trust "
    "write-time pre-screen mandate."
)


# ─────────────────────── main ────────────────────────────────────────────────

def main(argv):
    if len(argv) != 2:
        print(
            "[codeforge-issue-body-pre-screen-infra-error] "
            "usage: check_issue_body_claim_pre_screen.py <issue-body-file>",
            file=sys.stderr,
        )
        return 2

    body_path = argv[1]
    try:
        with open(body_path, encoding="utf-8", errors="replace") as f:
            body_text = f.read()
    except FileNotFoundError:
        print(
            "[codeforge-issue-body-pre-screen-infra-error] "
            "issue body file not found: %s" % body_path,
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(
            "[codeforge-issue-body-pre-screen-infra-error] "
            "issue body file read error: %s" % exc,
            file=sys.stderr,
        )
        return 2

    findings = scan_issue_body(body_text)

    for item in findings:
        _emit_flag(item)

    if findings:
        print("")
        print(_ACTION_GUIDE)
        print("")
        print(
            "check-issue-body-claim-pre-screen: FLAG %d "
            "(warning tier — continue-on-error 로 비차단, advisory only)"
            % len(findings)
        )
        return 1

    print(
        "check-issue-body-claim-pre-screen: PASS — FLAG 0 (warning tier)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
