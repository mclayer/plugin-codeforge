#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_spawn_prompt_fact_verify.py
CFP-2383 / ADR-082 Amendment 37 sub-scope 1-Z (sub-scope 1-L Amd 23, CFP-1590 carrier) —
spawn-prompt-fact-verify 게이트 (warning tier)

sub-scope 1-L (worker→worker handoff spawn prompt fact verify-before-trust mandate) 의 Wave 2
mechanical wire. worker (lane agent / chief author 등) 가 다른 worker 에게 넘기는 spawn prompt 안에서
4 sub-source (사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file)
로부터 inherit 된 fact (C1-C5: counter / version / SHA / verify-result / file-existence) 를 단언할 때,
동일-window 안 `[verified-via:` annotation 부재 시 FLAG. S2 (CFP-2382 check_issue_body_claim_pre_screen.py)
의 ::warning::+_emit_flag+_ACTION_GUIDE+in_fence toggle+strip_inline_code 구조 답습 위에, 삭제된
1-W source (c84fadf3:scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py) 의 C1-C5 PATTERNS 이식.

PR-body-proxy 한계 명시 (anti-theater — 본 게이트 신뢰 경계):
  본 게이트는 PR body 를 spawn prompt 의 proxy 로만 검사한다. PR body 는 실 spawn prompt 가 아니다 —
  worker→worker handoff spawn prompt 안 inherit fact 가 PR body 에 transcribe 된 경우만 검출하며,
  실제 spawn prompt 텍스트를 직접 검사하지 못한다 (spawn prompt 는 런타임 ephemeral, repo 산출물 아님).
  이 한계 때문에 warning-tier advisory 로만 유지한다. blocking 으로 승격하면 `[verified-via:` 문자열을
  위조해 false-PASS 를 만드는 구조적 위조가 가능하므로 (presence-only static lint), 보안 통제로 신뢰하지
  않는다. annotation presence 는 author 의 verify 습관 nudge 일 뿐 검증 자체의 증명이 아니다.

Usage:
  python3 check_spawn_prompt_fact_verify.py <pr-body-file>
    → PR body 파일을 scan, FLAG 1+ 면 exit 1 (warning), FLAG 0 면 exit 0
    (S2 동형 single arg file-input)

입력 = live PR event payload (workflow env PR_BODY → /tmp file → 본 script file-input).
  thin wrapper (scripts/check-spawn-prompt-fact-verify.sh) 가 env → /tmp 파일 변환 담당.

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (FLAG 0)
  1 = FLAG 1+ (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
  2 = SETUP error (입력 파일 부재 / 읽기 실패)

검출 알고리즘 (S2 답습 — blank-split 폐기, line-by-line in_fence toggle masking):
  scripts/lib/check_issue_body_claim_pre_screen.py:152-203 동형 — line-by-line in_fence boolean +
  fence_marker 추적 + fenced/blockquote 줄 continue masking + inline code-span strip.
  fenced 블록 내부 빈줄 fragmentation 불가능 → fenced 내부 예시 claim FP=0.

5 fact category (C1-C5 — 1-W source c84fadf3 PATTERNS 이식, ReDoS-safe anchored bounded quantifier):
  C1 counter   : "\d{2,}\s+(entries|labels|hits|...)" — e.g. "144 entries" / "111 hotfix-bypass labels"
  C2 version   : "v\d+\.\d+(\.\d+)?" — e.g. "v2.86" / "v6.10.0"
  C3 SHA       : 40-char hex commit SHA OR "PRE-SPAWN-ORIGIN-MAIN-SHA:" block
  C4 verify    : "sha256 PASS|byte-identical OK|MERGED|CLEAN|..." — verify-result 단언
  C5 file-exist: "<path>.md 존재|absent|present|exists" OR "line count: \d+"

FP guard 4종 EXEMPT (S2 답습 — PR body 도 markdown):
  (1) in_fence (fenced code block) (2) inline code-span (backtick `...`)
  (3) blockquote (> prefix)        (4) SELF_SOURCE (자기 정의 meta-reference)

ADR refs: ADR-082 Amendment 37 §결정 1 layer 1 sub-scope 1-Z (CFP-2383) /
  sub-scope 1-L (Amd 23, CFP-1590) declaration parent / sub-scope 1-W (Amd 34, CFP-1842) C1-C5 source /
  ADR-082 §결정 15 (Amd 20, CFP-1559) S2 구조 답습 base / ADR-060 / ADR-061 / ADR-127
"""

import re
import sys

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# unbounded scan 차단 (CFP-1497 PR #1499 sentinel 정신 — 대형 body ReDoS/DoS 보호).
# 목적 = unbounded scan 차단이지 의도적 truncation 아님. PR body 길이 분포 실측 후 상향 가능.
PER_BLOCK_SCAN_CAP = 50

# annotation presence 마커 (정적 substring grep — regex 아님, ReDoS-free)
ANNOTATION_MARKER = "[verified-via:"

# ─────────────── 5 fact category closed-set regex (1-W source c84fadf3 이식, anchored, ReDoS-safe) ──
# 모두 bounded quantifier — nested quantifier 절대 금지 (CFP-1497 PR #1499 sentinel 답습).
# pattern key = "C1".."C5" — QADev 계약: FLAG message 에 `pattern=C{N}` grep 가능 형식.

_PATTERNS = [
    # C1 counter assertion — "\d{2,}\s+(enum)" (1-W verbatim 이식)
    ("C1", re.compile(
        r"\b\d{2,}\s+(?:entries|entry|labels|label|hotfix-bypass|hits|hit|occurrences|items)\b",
        re.IGNORECASE,
    )),
    # C2 version assertion — "v\d+.\d+(.\d+)?" (1-W verbatim 이식)
    ("C2", re.compile(r"\bv\d+\.\d+(?:\.\d+)?\b")),
    # C3 SHA assertion — 40-char hex OR PRE-SPAWN-ORIGIN-MAIN-SHA block (1-W verbatim 이식)
    ("C3", re.compile(r"\b[0-9a-f]{40}\b|PRE-SPAWN-ORIGIN-MAIN-SHA:\s*[0-9a-f]+")),
    # C4 verify-result assertion (1-W verbatim 이식)
    ("C4", re.compile(
        r"\b(?:sha256 PASS|byte-identical (?:OK|PASS)|verify PASS|MERGED|CLEAN|drift 0)\b"
    )),
    # C5 file-existence assertion — "<path>.<ext> 존재/exists" OR "line count: N" (1-W verbatim 이식)
    ("C5", re.compile(
        r"\b\S+\.(?:md|yml|yaml|sh|py|json|ts|tsx|toml)\s+(?:존재|absent|present|exists)\b"
        r"|line count:\s*\d+"
    )),
]

# pattern 별 verified-via hint — 1-L scope (worker→worker handoff, 4 sub-source) 용 재작성.
# 1-W 잔재(Orchestrator-side "git rev-parse" 단독 등) 금지 — 4 sub-source inherit fact verify hint.
# 4 sub-source = 사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file.
_PATTERN_HINT = {
    "C1": "[verified-via: grep -c / wc -l <대상> — sibling Issue body·retro file 인용 count 직접 재측정]",
    "C2": "[verified-via: grep ^version <파일> — sister PR / sibling Issue body 인용 version 직접 확인]",
    "C3": "[verified-via: git rev-parse <ref> — sister PR commit 직접 확인]",
    "C4": "[verified-via: <검증 방법 직접 실행> — 사용자 발화·sister PR commit message 인용 결과 재확인]",
    "C5": "[verified-via: ls / wc -l <path> — sibling Issue body·retro file 인용 파일 존재·줄수 직접 확인]",
}

# Self-source skip — 본 lint 가 자기 정의·registry 정의를 scan 할 때 pattern 매치는
# 실제 unverified 단언이 아닌 expected meta-reference 이므로 EXEMPT (S2 SELF_SOURCE 답습).
SELF_SOURCE_PATTERNS = [
    "check_spawn_prompt_fact_verify",
    "spawn-prompt-fact-verify",
]


# ─────────────────────── inline code-span strip (S2 답습, F-CR-2382-1 정정 반영본) ──

def strip_inline_code(line):
    """
    line 내 inline code-span (backtick `...` pair) 구간을 공백으로 masking.

    S2 check_issue_body_claim_pre_screen.py:92-147 동형 (F-CR-2382-1 ambiguous-backtick claim 보존
    정정본 그대로 답습):
      - line 의 backtick run 들을 좌→우로 동일-길이 delimited pairing.
      - 모든 run 이 깨끗이 쌍지어지면 → 각 pair 의 [open..close] 구간 공백 masking (GFM inline code 정합).
      - run 이 하나라도 짝 못 찾으면 (홀수 / 길이 불일치 / 경계 모호) → strip 생략, raw line 그대로 반환
        (§7.5 FP-안전 = 불확실 시 검출 보존). claim 이 임의로 사라지지 않는다.

    반환: code-span 구간이 동일 길이 공백으로 치환된 line, 또는 ambiguous 시 raw line.
    """
    if "`" not in line:
        return line

    # 1) backtick run 위치·길이 수집 (run = 연속 backtick 묶음)
    runs = []  # (start_idx, run_len)
    i = 0
    n = len(line)
    while i < n:
        if line[i] != "`":
            i += 1
            continue
        run_start = i
        while i < n and line[i] == "`":
            i += 1
        runs.append((run_start, i - run_start))

    # 2) 좌→우 동일-길이 delimited pairing. 짝 못 찾으면 ambiguous → 전체 strip 생략.
    spans = []  # (open_start, close_end) — masking 대상 구간
    idx = 0
    while idx < len(runs):
        open_start, open_len = runs[idx]
        close_pos = None
        for j in range(idx + 1, len(runs)):
            if runs[j][1] == open_len:        # 정확히 동일 길이 run 만 close 후보 (delimited)
                close_pos = j
                break
        if close_pos is None:
            # 짝 없는 run 존재 → ambiguous line → strip 생략, claim 보존 (FP-안전)
            return line
        close_start, close_len = runs[close_pos]
        spans.append((open_start, close_start + close_len))
        idx = close_pos + 1               # close run 다음부터 재개 (내부 run 은 code literal 로 소비)

    # 3) 깨끗이 쌍지어진 경우에만 masking (길이 보존)
    chars = list(line)
    for s, e in spans:
        for k in range(s, e):
            chars[k] = " "
    return "".join(chars)


# ─────────────────────── scan (line-by-line in_fence toggle masking, S2 동형) ─────────

def scan_pr_body(body_text):
    """
    PR body 본문을 line-by-line state machine 으로 scan (S2 scan_issue_body 동형).

    in_fence toggle masking (check_issue_body_claim_pre_screen.py:152-203 답습 — fenced/blockquote 줄
    continue, fenced 내부 빈줄 fragmentation 불가능 → fenced 내부 예시 claim FP=0) + inline code-span
    strip + SELF_SOURCE EXEMPT.

    Returns: list of (line_num, raw_line, pattern_name, matched_text) — unverified claim.
    """
    findings = []
    in_fence = False
    fence_marker = None
    for line_num, raw_line in enumerate(body_text.splitlines(), start=1):
        if line_num > PER_BLOCK_SCAN_CAP:
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

        # ── SELF_SOURCE EXEMPT (자기 정의 meta-reference 줄) ──
        if any(marker in raw_line for marker in SELF_SOURCE_PATTERNS):
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
                # 라인당 매칭 패턴마다 1 finding (라인 단일 suppression 없음 — break 부재로 동일 라인
                # 다중 패턴 각각 별도 finding). 동일 (line, pattern) 쌍은 pat.search 첫 매치 1회만.
    return findings


# ─────────────────────── 출력 (S2 _emit_flag + _ACTION_GUIDE 답습) ───────

def _emit_flag(item):
    line_num, raw_line, pat_name, matched = item
    hint = _PATTERN_HINT.get(pat_name, "[verified-via: ...]")
    print(
        "::warning::check-spawn-prompt-fact-verify: FLAG — "
        "pattern=%s line=%s claim=\"%s\" hint='%s'"
        % (pat_name, line_num, matched, hint)
    )


_ACTION_GUIDE = (
    "[spawn-prompt-fact-verify] 강제 action 2택 (warning mode — merge 비차단, advisory):\n"
    "  ① inherit fact 검증 후 동일 line 에 `[verified-via: ...]` annotation 부착\n"
    "     (pattern 별 hint 참조 — 4 sub-source 인용 fact 를 직접 재측정/재확인:\n"
    "      사용자 발화 / sibling Issue body / sister PR commit message / 별 carrier retro file)\n"
    "  ② hotfix-bypass:spawn-prompt-fact-verify label + audit comment\n"
    "     (check-bypass-audit-comment.sh 마커 패턴)\n"
    "한계: PR body 는 spawn prompt 의 proxy — 실 spawn prompt 아님 (transcribe 케이스만 검출). "
    "warning-tier advisory (presence-only, 위조 false-PASS 구조적 가능 → 보안 통제 신뢰 금지).\n"
    "근거: ADR-082 Amendment 37 §결정 1 layer 1 sub-scope 1-Z (CFP-2383) — sub-scope 1-L (CFP-1590) "
    "worker→worker handoff spawn prompt fact verify-before-trust mandate Wave 2 mechanical wire."
)


# ─────────────────────── main (S2 동형) ────────────────────────────────────────────────

def main(argv):
    if len(argv) != 2:
        print(
            "[codeforge-spawn-prompt-fact-verify-infra-error] "
            "usage: check_spawn_prompt_fact_verify.py <pr-body-file>",
            file=sys.stderr,
        )
        return 2

    body_path = argv[1]
    try:
        with open(body_path, encoding="utf-8", errors="replace") as f:
            body_text = f.read()
    except FileNotFoundError:
        print(
            "[codeforge-spawn-prompt-fact-verify-infra-error] "
            "PR body file not found: %s" % body_path,
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(
            "[codeforge-spawn-prompt-fact-verify-infra-error] "
            "PR body file read error: %s" % exc,
            file=sys.stderr,
        )
        return 2

    findings = scan_pr_body(body_text)

    for item in findings:
        _emit_flag(item)

    if findings:
        print("")
        print(_ACTION_GUIDE)
        print("")
        print(
            "check-spawn-prompt-fact-verify: FLAG %d "
            "(warning tier — continue-on-error 로 비차단, advisory only)"
            % len(findings)
        )
        return 1

    print(
        "check-spawn-prompt-fact-verify: PASS — FLAG 0 (warning tier)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
