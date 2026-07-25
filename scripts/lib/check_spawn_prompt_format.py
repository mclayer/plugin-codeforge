#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1742 / ADR-115 §결정 1·4·6 — PreToolUse(Agent) spawn-format gate verifier
# ADR-061 Amendment 3 §결정 11 — Python script-writing convention + CodeQL ReDoS guard
#
# 4 block presence verifier (line-by-line parse, ReDoS guard):
#   1. [PRE-SPAWN-ORIGIN-MAIN-SHA]  — ADR-082 Amendment 15 1-E
#   2. [USER-UTTERANCE-VERBATIM]    — ADR-082 Amendment 5 1-C
#   3. worktree-first directive     — ADR-040 Amendment 6
#   4. parallel-dispatch directive  — ADR-064 Amendment 1 / parallel-dispatch-protocol-v1
#
# ADR-061 Amendment 3 §결정 11 CodeQL ReDoS guard (strict):
#   - line-by-line parse: text.splitlines() iteration only
#   - anchored simple regex per line: re.match() (NOT re.search() 전체 scan + dotall)
#   - lazy nested quantifier 금지: (?:...)*? 패턴 부재
#   - nested negated class + sentinel 금지
#   - alternation overlap 금지
#   - per-entry scan cap: SCAN_CAP_LINES = 50 (default N=50 line, ADR-061 Amendment 3)
#
# Entry-point:
#   python3 check_spawn_prompt_format.py --prompt-stdin
#   stdin: spawn prompt text
#   stdout JSON: {"missing": [<block-enum>], "found": [<block-enum>]}
#   exit 0: all blocks present (or bypass)
#   exit 1: 1+ block missing
#
# Block enum (closed-set — 4 블록 실 출처 = ADR-082 Amendment 15·Amendment 5 + ADR-040 Amendment 6 + ADR-064 Amendment 1, 4 분산 ADR):
#   "PRE-SPAWN-ORIGIN-MAIN-SHA"  / "USER-UTTERANCE-VERBATIM"
#   "WORKTREE-FIRST-DIRECTIVE"   / "PARALLEL-DISPATCH-DIRECTIVE"
#
# Bypass:
#   BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 — exit 0, stdout JSON {"bypass": true}
#
# Usage (Wave 1 warning-only — hook wrapper reads exit code):
#   echo "<prompt>" | python3 scripts/lib/check_spawn_prompt_format.py --prompt-stdin
#
# SSOT carrier: CFP-1742 Story-2 of Epic CFP-1740

import sys
import re
import os
import json

# Windows console 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── 상수 ─────────────────────────────────────────────────────────────────────

SCRIPT_NAME = "[check-spawn-prompt-format]"

# per-entry scan cap (ADR-061 Amendment 3 §결정 11 default N=50 line)
SCAN_CAP_LINES = 50

# Block enum closed-set (ADR-115 §결정 6)
BLOCK_PRE_SPAWN_SHA       = "PRE-SPAWN-ORIGIN-MAIN-SHA"
BLOCK_USER_UTTERANCE      = "USER-UTTERANCE-VERBATIM"
BLOCK_WORKTREE_FIRST      = "WORKTREE-FIRST-DIRECTIVE"
BLOCK_PARALLEL_DISPATCH   = "PARALLEL-DISPATCH-DIRECTIVE"

ALL_BLOCKS = [
    BLOCK_PRE_SPAWN_SHA,
    BLOCK_USER_UTTERANCE,
    BLOCK_WORKTREE_FIRST,
    BLOCK_PARALLEL_DISPATCH,
]

# ── Anchored simple regex (CodeQL ReDoS guard 준수) ──────────────────────────
#
# 규칙:
#   - re.match() 사용 (line 선두 앵커 — '^' 불필요하지만 명시적으로 같음)
#   - 양화사 중첩 금지: (?:...)*? / (.+)+ 등 부재
#   - 부정 문자 클래스 중첩 금지
#   - alternation overlap 금지 (패턴 범위 disjoint 보장)
#
# Block 1: [PRE-SPAWN-ORIGIN-MAIN-SHA] : <7~40 hex SHA>
#   anchored: 행 선두에서 시작 (re.match 자체가 선두 앵커)
#   SHA 범위: 7~40 자 소문자 hex (short SHA 7 허용, full SHA 40 허용)
#   후행 내용 허용: 행 나머지는 \s* 이후 종료 (비-hex 내용 허용)
#   NOTE: \s{0,20} bounded — open-ended lazy 금지 (ReDoS guard)
RE_PRE_SPAWN_SHA = re.compile(
    r"^\[PRE-SPAWN-ORIGIN-MAIN-SHA\]\s{0,20}:\s{0,20}[0-9a-f]{7,40}\b"
)

# Block 2: [USER-UTTERANCE-VERBATIM]
#   block opener line 만 검증 (body 후속 line 검증 범위 외)
#   trailing whitespace 허용: \s{0,20}$
RE_USER_UTTERANCE = re.compile(
    r"^\[USER-UTTERANCE-VERBATIM\]\s{0,20}$"
)

# Block 3: worktree-first directive presence (loose match — directive 존재 여부만)
#   "worktree" 단어가 포함된 행
#   NOTE: .{0,200} bounded — open-ended .* 금지 (ReDoS guard)
RE_WORKTREE_FIRST = re.compile(
    r"^.{0,200}worktree.{0,200}$"
)

# Block 4: parallel-dispatch directive presence (loose match)
#   "parallel" 또는 "sequential" + "dispatch" 가 같은 행에 존재
#   NOTE: .{0,200} bounded — open-ended .* 금지 (ReDoS guard)
#   두 패턴 disjoint 검사 (alternation overlap 방지):
#     패턴 A: parallel.*dispatch
#     패턴 B: sequential.*dispatch
#   각자 독립 컴파일 후 OR 논리로 결합 (runtime 에서 조합, regex 안 alternation 금지)
RE_PARALLEL_DISPATCH_A = re.compile(
    r"^.{0,200}parallel.{0,200}dispatch.{0,200}$"
)
RE_PARALLEL_DISPATCH_B = re.compile(
    r"^.{0,200}sequential.{0,200}dispatch.{0,200}$"
)


# ── 핵심 검증 함수 ────────────────────────────────────────────────────────────

def check_blocks(text: str) -> dict:
    """
    spawn prompt text 안 4 block presence 검증.

    ADR-061 Amendment 3 §결정 11 CodeQL ReDoS guard:
      - text.splitlines() 로 line-by-line scan
      - per-entry scan cap SCAN_CAP_LINES (50 line) 적용
      - re.match() 단일 line 매칭 (multi-line dotall NOT used)
      - 각 block 발견 즉시 scan 종료 (early exit)

    반환:
      {
        "found": [<block-enum>, ...],
        "missing": [<block-enum>, ...],
      }
    """
    lines = text.splitlines()
    # scan cap 적용 — 전체 prompt 가 매우 길어도 첫 SCAN_CAP_LINES line 만 검사
    # (per-entry 각 block 이 상단부에 위치한다는 Change Plan §3.3 가정 정합)
    scan_lines = lines[:SCAN_CAP_LINES]

    found = set()
    missing = []

    for line in scan_lines:
        # Block 1: PRE-SPAWN-ORIGIN-MAIN-SHA
        if BLOCK_PRE_SPAWN_SHA not in found:
            if RE_PRE_SPAWN_SHA.match(line):
                found.add(BLOCK_PRE_SPAWN_SHA)

        # Block 2: USER-UTTERANCE-VERBATIM
        if BLOCK_USER_UTTERANCE not in found:
            if RE_USER_UTTERANCE.match(line):
                found.add(BLOCK_USER_UTTERANCE)

        # Block 3: WORKTREE-FIRST-DIRECTIVE
        if BLOCK_WORKTREE_FIRST not in found:
            if RE_WORKTREE_FIRST.match(line):
                found.add(BLOCK_WORKTREE_FIRST)

        # Block 4: PARALLEL-DISPATCH-DIRECTIVE (disjoint A or B)
        if BLOCK_PARALLEL_DISPATCH not in found:
            if RE_PARALLEL_DISPATCH_A.match(line) or RE_PARALLEL_DISPATCH_B.match(line):
                found.add(BLOCK_PARALLEL_DISPATCH)

        # 전부 발견 시 early exit
        if len(found) == len(ALL_BLOCKS):
            break

    # missing 목록 구성 (ALL_BLOCKS 순서 유지)
    for block in ALL_BLOCKS:
        if block not in found:
            missing.append(block)

    return {
        "found": [b for b in ALL_BLOCKS if b in found],
        "missing": missing,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv: list) -> int:
    """
    --prompt-stdin 모드: stdin 에서 spawn prompt 읽기 → 4 block presence 검증.
    stdout JSON: {"missing": [...], "found": [...]}
    exit 0: all present
    exit 1: 1+ missing
    """
    # Bypass check
    if os.environ.get("BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE", "") == "1":
        print(
            json.dumps({"bypass": True, "missing": [], "found": []}),
        )
        print(
            f"{SCRIPT_NAME} BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 — gate suppressed",
            file=sys.stderr,
        )
        return 0

    if "--prompt-stdin" not in argv:
        print(
            f"{SCRIPT_NAME} ERROR: --prompt-stdin flag required. "
            "Usage: python3 check_spawn_prompt_format.py --prompt-stdin",
            file=sys.stderr,
        )
        return 2

    # stdin 읽기 — graceful degradation: 실패 시 빈 문자열 (block 전부 missing 처리)
    try:
        prompt_text = sys.stdin.read()
    except Exception as e:
        print(
            f"{SCRIPT_NAME} WARN: stdin read error ({e}) — treating prompt as empty",
            file=sys.stderr,
        )
        prompt_text = ""

    result = check_blocks(prompt_text)

    # stdout JSON 출력 (hook wrapper 가 parse)
    print(json.dumps(result))

    if result["missing"]:
        print(
            f"{SCRIPT_NAME} WARN: missing blocks — {result['missing']}",
            file=sys.stderr,
        )
        return 1

    print(
        f"{SCRIPT_NAME} PASS: all 4 blocks present — {result['found']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
