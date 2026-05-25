#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1539 / CFP-FU-A Wave 2 mechanical wire
# ADR-082 Amendment 19 §결정 1 layer 1 sub-scope (1-I)
# ADR-073 Amendment 13/14 paired sibling — sub-decision 1+2 axis
# ADR-061 §결정 1 (multi-line Python > 5줄 외부 .py file 의무)
#
# Pre-spawn-prompt-finalize-verify mechanical lint (warning-tier per ADR-060 §결정 5).
#
# Detection scope (declarative anchor — Wave 1 SSOT, CFP-FU-A carrier PR #1527):
#   Story file (docs/stories/**/*.md) 안 [USER-UTTERANCE-VERBATIM] block 안에서
#   `pre_spawn_prompt_finalize_verified: <true|false>` field presence 검증.
#
# 두 가지 검사 (warning-tier — exit 0 항상 for warnings):
#
#   Check (a) — pre_spawn_prompt_finalize_verified field presence (PRIMARY):
#     [USER-UTTERANCE-VERBATIM] block 감지 시:
#       field 부재 → [WARN-FIELD-ABSENT] (advisory, spawn prompt finalize verify 미수행)
#       field 존재 + value invalid → [WARN-FIELD-INVALID] (value != true|false)
#       field 존재 + value valid (true|false) → PASS
#
#   Check (b) — bool value strict (SECONDARY):
#     value 가 `true` 또는 `false` 이 아닌 경우 → [WARN-FIELD-INVALID].
#
# FP-완화 guards:
#   - (1) templates/** path = canonical example 면제
#   - (2) tests/** + fixtures/** path = bats fixture self-detection avoid
#   - (3) docs/stories/**/*.md 아닌 모든 file = silent skip (lint scope 외)
#   - (4) [USER-UTTERANCE-VERBATIM] block 부재 file = silent skip (spawn evidence marker 부재)
#
# CodeQL ReDoS guard (CFP-1497 PR #1499 sentinel verbatim 답습):
#   - **Line-by-line parse** 의무 (catastrophic backtracking 위험 nested quantifier regex 절대 금지).
#   - per-block scan cap = PER_BLOCK_SCAN_CAP=30 line (pathological input 차단).
#   - 각 line 별로 단순 single-line anchored re.match.
#
# Bypass channel:
#   - HOTFIX_BYPASS_PRE_SPAWN_PROMPT_FINALIZE_VERIFY=1 env
#     (label `hotfix-bypass:pre-spawn-prompt-finalize-verify` 부착 시 workflow 에서 주입)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (예: yaml 파싱 실패 — 본 lint 는 yaml 미사용으로 거의 없음)
#   2 — setup error (예: 파일 시스템 접근 오류)
#
# Usage:
#   python3 check_pre_spawn_prompt_finalize_verify.py [file ...]
#
# SSOT carrier: CFP-FU-A Wave 1 declarative anchor (PR #1527 merged) + 본 Wave 2 wire.
# Precedent byte-pattern: scripts/lib/check_spawn_prompt_head_pin.py (CFP-1489)
#                         scripts/lib/check_mid_spawn_drift_detection.py (CFP-1500, CodeQL ReDoS SSOT)

import sys
import re
import os
from pathlib import Path

# Windows console 호환 — UTF-8 강제 (CFP-1489 line 50-55 verbatim 답습 + CFP-1540 cp949 fix paired sibling)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_PRE_SPAWN_PROMPT_FINALIZE_VERIFY", "")
if BYPASS_ENV == "1":
    print("[check-pre-spawn-prompt-finalize-verify] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[check-pre-spawn-prompt-finalize-verify]"

# Story file 식별 — docs/stories/**/*.md
STORY_FILE_RE = re.compile(r"docs/stories/.*\.md$")

# [USER-UTTERANCE-VERBATIM] block open/close detection (single-line anchored)
USER_UTTERANCE_OPEN_RE = re.compile(r"^\[USER-UTTERANCE-VERBATIM\]\s*$")
USER_UTTERANCE_CLOSE_RE = re.compile(r"^\[/USER-UTTERANCE-VERBATIM\]\s*$")

# pre_spawn_prompt_finalize_verified field detection (single-line anchored, no nested quantifier)
# ADR-082 Amd 19 §1-I annotation field name verbatim
FIELD_LOOSE_RE = re.compile(
    r"^\s*pre_spawn_prompt_finalize_verified\s*:\s*(.*)$",
    re.IGNORECASE,
)

# Strict bool value (true|false only)
STRICT_BOOL_RE = re.compile(r"^(true|false)\s*$", re.IGNORECASE)

# Per-block scan cap (CodeQL ReDoS guard — pathological input bound)
# 30 line (보수적, CFP-1500 50 line 대비 축소 — [USER-UTTERANCE-VERBATIM] 블록 평균 10-20 line 가정)
PER_BLOCK_SCAN_CAP = 30


# ── path filter (FP-완화 guard 1/2/3) ─────────────────────────────────────────
def _is_template_path(filepath):
    """templates/** 경로 식별 — canonical example 면제."""
    parts = Path(filepath).parts
    return "templates" in parts


def _is_test_fixture_path(filepath):
    """tests/** + fixtures/** 경로 식별 — bats fixture self-detection avoid."""
    parts = Path(filepath).parts
    return "tests" in parts or "fixtures" in parts


def _is_story_file(filepath):
    """docs/stories/**/*.md path 식별 (FP guard 3)."""
    p = Path(filepath).as_posix()
    return bool(STORY_FILE_RE.search(p))


# ── block scan (CodeQL ReDoS guard — line-by-line, capped) ──────────────────
def _scan_utterance_block(lines, start_idx):
    """
    [USER-UTTERANCE-VERBATIM] open line 으로부터 block content scan.
    PER_BLOCK_SCAN_CAP 이내에서 field presence + value validity 검사.

    Returns dict:
      - field_present: bool
      - field_valid: bool (field_present=True 시만 유효)
      - field_value: str (matched raw value, stripped)
      - end_idx: int (exclusive end of block scan, [/USER-UTTERANCE-VERBATIM] 다음 줄)

    Line-by-line parse — pathological-input safe (no nested quantifier).
    """
    result = {
        "field_present": False,
        "field_valid": False,
        "field_value": "",
        "end_idx": min(start_idx + 1 + PER_BLOCK_SCAN_CAP, len(lines)),
    }
    n = len(lines)
    end_at = min(start_idx + 1 + PER_BLOCK_SCAN_CAP, n)

    for j in range(start_idx + 1, end_at):
        line = lines[j]

        # Block close detection
        if USER_UTTERANCE_CLOSE_RE.match(line):
            result["end_idx"] = j + 1
            return result

        # New open block = abort current (malformed nesting guard)
        if USER_UTTERANCE_OPEN_RE.match(line):
            result["end_idx"] = j
            return result

        # Field detection (single-line anchored, no backtracking)
        m = FIELD_LOOSE_RE.match(line)
        if m:
            result["field_present"] = True
            raw_value = m.group(1).strip()
            result["field_value"] = raw_value
            if STRICT_BOOL_RE.match(raw_value):
                result["field_valid"] = True
            # continue scanning (multiple entries = last wins for value, first presence is flag)

    return result


# ── 단일 file 검사 ────────────────────────────────────────────────────────────
def check_file(filepath):
    """
    단일 Story file 검사. 반환: warn_count (int).

    flow:
      1. path filter (templates/**, tests/** skip)
      2. Story file 식별 (docs/stories/**/*.md)
      3. read content
      4. line-by-line scan — [USER-UTTERANCE-VERBATIM] block 식별
      5. 각 block (PER_BLOCK_SCAN_CAP line cap) 안에서:
         (a) pre_spawn_prompt_finalize_verified field presence
         (b) field value strict bool (true|false)
      6. (a) 부재 → [WARN-FIELD-ABSENT]
         (b) 부재는 아니지만 value invalid → [WARN-FIELD-INVALID]
    """
    path = Path(filepath)
    if not path.exists():
        # 삭제된 file — silent skip
        return 0

    # FP-완화 guard 1: templates/** 면제
    if _is_template_path(filepath):
        return 0

    # FP-완화 guard 2: tests/** + fixtures/** 면제
    if _is_test_fixture_path(filepath):
        return 0

    # FP-완화 guard 3: Story file 아닌 모든 file = silent skip
    if not _is_story_file(filepath):
        return 0

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError) as e:
        print(
            f"{SCRIPT_NAME} [WARN] {filepath}: file read error ({e}) — skip",
            file=sys.stderr,
        )
        return 0

    lines = text.splitlines()
    n = len(lines)

    warn_count = 0
    block_count = 0
    i = 0
    while i < n:
        line = lines[i]

        # [USER-UTTERANCE-VERBATIM] block open detection
        if USER_UTTERANCE_OPEN_RE.match(line):
            block_count += 1
            block = _scan_utterance_block(lines, i)

            # Check (a) — field presence
            if not block["field_present"]:
                print(
                    f"{SCRIPT_NAME} [WARN-FIELD-ABSENT] {filepath}:{i + 1}: "
                    f"[USER-UTTERANCE-VERBATIM] block detected but "
                    f"`pre_spawn_prompt_finalize_verified: <true|false>` field absent in block "
                    f"(scan cap {PER_BLOCK_SCAN_CAP} lines). "
                    f"ADR-082 Amendment 19 §결정 1 layer 1 sub-scope (1-I) — "
                    f"spawn prompt finalize verify 완료 후 [USER-UTTERANCE-VERBATIM] block 안에 "
                    f"`pre_spawn_prompt_finalize_verified: true` field 부착 의무. "
                    f"hotfix bypass: hotfix-bypass:pre-spawn-prompt-finalize-verify label",
                    file=sys.stderr,
                )
                warn_count += 1

            # Check (b) — field value strict bool
            elif not block["field_valid"]:
                raw_val = block["field_value"]
                print(
                    f"{SCRIPT_NAME} [WARN-FIELD-INVALID] {filepath}:{i + 1}: "
                    f"pre_spawn_prompt_finalize_verified field detected but value invalid "
                    f"(expected `true` or `false`, got '{raw_val[:50]}'). "
                    f"ADR-082 Amendment 19 §결정 1 layer 1 sub-scope (1-I) — "
                    f"valid values = `true` (verify 완료) | `false` (미수행 명시). "
                    f"hotfix bypass: hotfix-bypass:pre-spawn-prompt-finalize-verify label",
                    file=sys.stderr,
                )
                warn_count += 1

            else:
                # field present + valid = PASS
                val = block["field_value"]
                print(
                    f"{SCRIPT_NAME} OK: {filepath}:{i + 1}: "
                    f"pre_spawn_prompt_finalize_verified={val} (valid)",
                    file=sys.stderr,
                )

            # Advance to end of this block (linear time guarantee)
            i = block["end_idx"]
            continue
        i += 1

    # FP guard 4: [USER-UTTERANCE-VERBATIM] block 부재 file = silent skip
    if block_count == 0:
        # silent skip (spawn evidence marker 부재 = lint scope 외)
        return 0

    return warn_count


# ── main ──────────────────────────────────────────────────────────────────────
def main(argv):
    if not argv:
        print(f"{SCRIPT_NAME} INFO: no files supplied — skip (exit 0)", file=sys.stderr)
        return 0

    total_warn = 0
    for filepath in argv:
        try:
            total_warn += check_file(filepath)
        except Exception as e:
            # 단일 file 검사 실패 = 다음 file 계속 진행 (graceful degradation)
            print(
                f"{SCRIPT_NAME} [WARN] {filepath}: unexpected error "
                f"({type(e).__name__}: {e}) — skip",
                file=sys.stderr,
            )

    if total_warn == 0:
        print(
            f"{SCRIPT_NAME} PASS: all files validated ({len(argv)} file(s) scanned)",
            file=sys.stderr,
        )
    else:
        print(
            f"{SCRIPT_NAME} SUMMARY: {total_warn} warning(s) emitted (warning-tier, exit 0)",
            file=sys.stderr,
        )

    # warning-tier — 항상 exit 0 (PR merge 미차단, ADR-060 §결정 5 정합)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
