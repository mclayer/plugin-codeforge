#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1500 / Wave 2-B of CFP-1389 (Sub-CFP B CFP-1436 mechanical wire)
# ADR-082 Amendment 16 §결정 1 layer 1 sub-scope (1-F) spawn-internal periodic
# origin re-pin protocol 4-tuple primitive + ADR-073 Amendment 12
# `mid_spawn_origin_drift_detected` transition trigger 11번째 entry paired
# sibling + ADR-061 §결정 1 (multi-line Python > 5줄 외부 .py file 의무).
#
# Mid-spawn drift detection mechanical lint (warning-tier per ADR-060 §결정 5).
#
# Detection scope (declarative anchor — Wave 1 SSOT, CFP-1436 carrier):
#   Check (a) — agent spawn entry mid-spawn drift directive presence (PRIMARY):
#     input: changed Story file (`docs/stories/**/*.md`) 안 §14 Lane Evidence
#       section 의 agent spawn entry (line containing "spawn" keyword AND one of
#       ArchitectAgent / RequirementsPLAgent / DeveloperAgent / deputy / chief author)
#     cross-check: 같은 entry block 안 (next entry boundary 까지) 다음 marker presence:
#       - `mid_spawn_drift_check_executed: <true|false>` field, OR
#       - `drift_check_directive_present: true` marker
#     output: 양쪽 모두 부재 → [WARN-DIRECTIVE-ABSENT] (warning-tier, exit 0)
#
#   Check (b) — return packet drift_detected flag presence (SECONDARY):
#     input: 같은 entry block 안 spawn duration indicator (`spawn ≥` 또는
#       duration keyword 가 5분 이상 명시)
#     cross-check: same block 안 `drift_detected: <true|false>` flag presence verify
#     output: 누락 시 [WARN-RETURN-PAYLOAD-INCOMPLETE] (warning-tier)
#     Note: 정밀 duration timestamp 측정 = Wave 3 carrier (heuristic-based detect only).
#
# FP-완화 guards (CFP-1489 + CFP-1497 패턴 답습):
#   - (a) templates/** path = canonical example 면제
#   - (b) tests/** + fixtures/** path = bats fixture self-detection avoid
#   - (c) Story file (`docs/stories/**/*.md`) 아닌 모든 file = silent skip (lint scope 외)
#
# CodeQL ReDoS guard (CFP-1497 PR #1499 sentinel verbatim 답습):
#   - **Line-by-line parse** 의무 (catastrophic backtracking 위험 nested quantifier
#     regex 절대 금지). 각 line 별로 단순 single-line anchored `re.match`.
#   - block boundary detection = next agent spawn line 또는 empty line 2개 연속.
#   - per-entry scan cap = 50 line (pathological input 차단).
#
# Bypass channel:
#   - HOTFIX_BYPASS_MID_SPAWN_DRIFT_DETECTION=1 env (label
#     `hotfix-bypass:mid-spawn-drift-detection` 부착 시 workflow 에서 주입)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (currently unused — warning-tier only)
#   2 — setup error (file system access error)
#
# Usage:
#   python3 check_mid_spawn_drift_detection.py [file ...]
#
# SSOT carrier: CFP-1436 Wave 1 declarative anchor (PR #1475 merged) + 본 Wave 2-B wire.
# Precedent byte-pattern: scripts/lib/check_amendment_slot_reservation.py (CFP-1497).

import sys
import re
import os
from pathlib import Path

# Windows console 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_MID_SPAWN_DRIFT_DETECTION", "")
if BYPASS_ENV == "1":
    print("[check-mid-spawn-drift-detection] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[check-mid-spawn-drift-detection]"

# Story file 식별 — docs/stories/**/*.md
STORY_FILE_RE = re.compile(r"docs/stories/.*\.md$")

# agent spawn line detection — single-line anchored, no nested quantifier
# block 진입 keyword: "spawn" (case-insensitive substring) + role keyword
# CodeQL ReDoS guard: 각 line 별 단순 substring/regex 호출 (line-by-line)
AGENT_ROLE_KEYWORDS = (
    "ArchitectAgent",
    "RequirementsPLAgent",
    "DeveloperAgent",
    "DesignReviewPLAgent",
    "DeveloperPLAgent",
    "QADeveloperAgent",
    "deputy",
    "chief author",
    "SubAgent",
)

# Drift directive marker regexes (single-line anchored)
MID_SPAWN_DRIFT_FIELD_RE = re.compile(
    r"^\s*mid_spawn_drift_check_executed:\s*(true|false)\s*$",
    re.IGNORECASE,
)
DRIFT_DIRECTIVE_PRESENT_RE = re.compile(
    r"^\s*drift_check_directive_present:\s*true\s*$",
    re.IGNORECASE,
)
DRIFT_DETECTED_RE = re.compile(
    r"^\s*drift_detected:\s*(true|false)\s*$",
    re.IGNORECASE,
)

# Long spawn duration heuristic — "spawn ≥ Nmin" or "duration: Nmin" with N >= 5
# Conservative: search line for explicit "≥ 5" / "5 분" / "minutes" with number
# Use a SIMPLE substring check (no regex backtracking) — line-by-line.
LONG_DURATION_KEYWORDS = (
    "spawn ≥ 5",  # "spawn ≥ 5분" / "spawn ≥ 5 min"
    "spawn>=5",
    "duration: 5 min",
    "duration: 5분",
    "duration: 10 min",
    "duration: 10분",
    "duration: 15 min",
    "duration: 15분",
    "duration: 20 min",
    "duration: 20분",
    "duration: 30 min",
    "duration: 30분",
    "long-duration spawn",
)

# Per-entry scan cap (CodeQL ReDoS guard — pathological input bound)
PER_ENTRY_SCAN_CAP = 50

# Block boundary detection: empty line 2-consecutive OR next agent spawn line OR
# non-indented heading-like line (`## ` / `### `).
NEW_SECTION_RE = re.compile(r"^#{1,6}\s")


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
    """docs/stories/**/*.md path 식별."""
    p = Path(filepath).as_posix()
    return bool(STORY_FILE_RE.search(p))


def _is_agent_spawn_line(line):
    """
    line-level check: "spawn" keyword + role keyword presence.
    NO nested-quantifier regex — simple substring check (linear time).

    FP-completeness guard 4: markdown table row (line starts with `|`) skip —
    Story §14 Lane Evidence 는 table 형식 abstract row + detail block 양면 representation.
    table cell row 는 짧은 abstract 만 (scan 50 line cap 안 multiple rows clustering
    가능, 다음 detail block 의 markers 가 cross-row scan 차단 가능). table row 는
    lint scope 외 (detail block 만 의무 — Story §14 Lane Evidence detail entry 영역).
    """
    stripped = line.lstrip()
    # Markdown table row skip (FP guard 4)
    if stripped.startswith("|"):
        return False
    if "spawn" not in line.lower():
        return False
    for kw in AGENT_ROLE_KEYWORDS:
        if kw in line:
            return True
    return False


def _line_indicates_long_duration(line):
    """
    line-level heuristic: spawn duration ≥ 5 min indicator presence.
    Simple substring scan — no regex backtracking risk.
    """
    ll = line.lower()
    for kw in LONG_DURATION_KEYWORDS:
        if kw.lower() in ll:
            return True
    return False


# ── block scan (CodeQL ReDoS guard — line-by-line, capped) ──────────────────
def _scan_entry_block(lines, start_idx):
    """
    From a `spawn` line, scan subsequent lines up to PER_ENTRY_SCAN_CAP
    until block boundary (empty-2-consecutive / next spawn line / new section heading).
    Returns dict with keys:
      - `directive_present`: bool (mid_spawn_drift_check_executed OR drift_check_directive_present)
      - `long_duration`: bool
      - `drift_detected_present`: bool
      - `end_idx`: int (exclusive end of block)
    Line-by-line parse — pathological-input safe.
    """
    result = {
        "directive_present": False,
        "long_duration": False,
        "drift_detected_present": False,
        "end_idx": min(start_idx + PER_ENTRY_SCAN_CAP, len(lines)),
    }
    empty_run = 0
    n = len(lines)
    end_at = min(start_idx + 1 + PER_ENTRY_SCAN_CAP, n)

    # Inspect the start_idx line itself for long_duration hint
    if _line_indicates_long_duration(lines[start_idx]):
        result["long_duration"] = True

    for j in range(start_idx + 1, end_at):
        line = lines[j]

        # Boundary: empty line 2-consecutive
        if not line.strip():
            empty_run += 1
            if empty_run >= 2:
                result["end_idx"] = j
                return result
            continue
        empty_run = 0

        # Boundary: new section heading
        if NEW_SECTION_RE.match(line):
            result["end_idx"] = j
            return result

        # Boundary: next agent spawn line (start of new entry block)
        if _is_agent_spawn_line(line):
            result["end_idx"] = j
            return result

        # Directive marker presence (single-line anchored, no backtracking)
        if MID_SPAWN_DRIFT_FIELD_RE.match(line):
            result["directive_present"] = True
        if DRIFT_DIRECTIVE_PRESENT_RE.match(line):
            result["directive_present"] = True

        # drift_detected flag presence
        if DRIFT_DETECTED_RE.match(line):
            result["drift_detected_present"] = True

        # Long duration heuristic (further lines)
        if _line_indicates_long_duration(line):
            result["long_duration"] = True

    return result


# ── 단일 file 검사 ────────────────────────────────────────────────────────────
def check_file(filepath):
    """
    단일 Story file 검사. 반환: warn_count (int).

    flow:
      1. path filter (templates/**, tests/** skip)
      2. Story file 식별 (docs/stories/**/*.md)
      3. read content
      4. line-by-line scan — agent spawn keyword line 식별
      5. 각 spawn entry block (PER_ENTRY_SCAN_CAP line cap) 안에서:
         (a) directive (mid_spawn_drift_check_executed OR drift_check_directive_present) presence
         (b) long_duration indicator 있을 시 drift_detected flag presence
      6. (a) 부재 → [WARN-DIRECTIVE-ABSENT]
         (b) long_duration AND drift_detected_present == False → [WARN-RETURN-PAYLOAD-INCOMPLETE]
    """
    path = Path(filepath)
    if not path.exists():
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
    spawn_count = 0
    i = 0
    while i < n:
        line = lines[i]
        if _is_agent_spawn_line(line):
            spawn_count += 1
            block = _scan_entry_block(lines, i)

            # Check (a) — directive presence
            if not block["directive_present"]:
                print(
                    f"{SCRIPT_NAME} [WARN-DIRECTIVE-ABSENT] {filepath}:{i + 1}: "
                    f"agent spawn entry detected without "
                    f"`mid_spawn_drift_check_executed: <bool>` field OR "
                    f"`drift_check_directive_present: true` marker in entry block "
                    f"(scan cap {PER_ENTRY_SCAN_CAP} lines). "
                    f"ADR-082 Amendment 16 §결정 1 layer 1 sub-scope (1-F) + "
                    f"ADR-073 Amendment 12 — Mid-spawn rebase auto-detection "
                    f"protocol mandate. Add directive presence marker to Story "
                    f"§14 Lane Evidence agent spawn entry. "
                    f"hotfix bypass: hotfix-bypass:mid-spawn-drift-detection label",
                    file=sys.stderr,
                )
                warn_count += 1

            # Check (b) — long_duration spawn drift_detected flag presence
            if block["long_duration"] and not block["drift_detected_present"]:
                print(
                    f"{SCRIPT_NAME} [WARN-RETURN-PAYLOAD-INCOMPLETE] {filepath}:{i + 1}: "
                    f"long-duration agent spawn (≥ 5 min) detected without "
                    f"`drift_detected: <bool>` return packet flag in entry block. "
                    f"ADR-073 Amendment 12 §결정 1-O step 3 — drift detected "
                    f"RETURN early protocol 4-key payload (pre_spawn_sha + "
                    f"current_origin_main_sha + commits_drift + drift_detected_at_step) "
                    f"mandate. Add `drift_detected: <bool>` flag to return packet section. "
                    f"hotfix bypass: hotfix-bypass:mid-spawn-drift-detection label",
                    file=sys.stderr,
                )
                warn_count += 1

            # Advance to end of this block (linear time guarantee)
            i = block["end_idx"]
            continue
        i += 1

    if warn_count == 0:
        if spawn_count > 0:
            print(
                f"{SCRIPT_NAME} OK: {filepath} "
                f"({spawn_count} spawn entry/entries all directive-present)",
                file=sys.stderr,
            )
        else:
            print(
                f"{SCRIPT_NAME} OK: {filepath} (no agent spawn entries — silent PASS)",
                file=sys.stderr,
            )

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
