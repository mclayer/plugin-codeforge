#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1502 / Wave 2-D of CFP-1389 (Sub-CFP D CFP-1438 mechanical wire) — FINAL Wave 2
# ADR-039 Amendment 5 §결정 17 chief author spawn span guideline (recommendation tier)
# + ADR-044 Amendment 3 §결정 9 multi-step chief author pattern paired sibling carrier
# + ADR-061 §결정 1 (multi-line Python > 5줄 외부 .py file 의무).
#
# Chief author span telemetry mechanical lint (warning-tier per ADR-060 §결정 5).
#
# Detection scope (declarative anchor — Wave 1 SSOT, CFP-1438 carrier hydrate):
#   Check (a) — chief author spawn entry telemetry marker presence (PRIMARY):
#     input: changed Story file (`docs/stories/**/*.md`) 안 §14 Lane Evidence
#       section 의 chief author spawn entry (line containing "chief author"
#       substring (case-insensitive))
#     cross-check: 같은 entry block 안 (next entry boundary 까지, 50-line cap)
#       다음 marker presence:
#       - `[chief-author-span: <minutes>, <class>]` inline marker, OR
#       - `chief_author_span_minutes:` YAML-like field
#     output: 양쪽 모두 부재 → [WARN-TELEMETRY-MARKER-ABSENT] (warning-tier, exit 0)
#
#   Check (b) — long-span chief author spawn `monolithic` class warning (SECONDARY):
#     input: same block 안 `[chief-author-span: N, <class>]` 가 있을 때 (N = integer)
#     heuristic: N ≥ CFP_CHIEF_AUTHOR_SPAN_MAX_MIN (env, default 10) AND class == "monolithic"
#     output: warn → [WARN-LONG-SPAN-MONOLITHIC] (warning-tier — recommendation tier,
#       ADR-039 Amendment 5 §결정 17 recommendation tier 정합. mandate-class 아닌 awareness annotation only.)
#
# FP-완화 guards (CFP-1500 패턴 verbatim 답습):
#   - (a) templates/** path = canonical example 면제
#   - (b) tests/** + fixtures/** path = bats fixture self-detection avoid
#   - (c) Story file (`docs/stories/**/*.md`) 아닌 모든 file = silent skip (lint scope 외)
#   - (d) markdown table row (line starts with `|`) = silent skip (table abstract row vs detail block 분리)
#
# CodeQL ReDoS guard (CFP-1497 PR #1499 sentinel verbatim 답습):
#   - **Line-by-line parse** 의무 (catastrophic backtracking 위험 nested quantifier
#     regex 절대 금지). 각 line 별로 단순 single-line anchored `re.match`.
#   - block boundary detection = next chief author spawn line 또는 empty line 2개 연속
#     또는 new section heading.
#   - per-entry scan cap = 50 line (pathological input 차단).
#
# Bypass channel:
#   - HOTFIX_BYPASS_CHIEF_AUTHOR_SPAN_TELEMETRY=1 env (label
#     `hotfix-bypass:chief-author-span-telemetry` 부착 시 workflow 에서 주입)
#
# Configurable threshold:
#   - CFP_CHIEF_AUTHOR_SPAN_MAX_MIN env (default 10) — long-span warning threshold
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (currently unused — warning-tier only)
#   2 — setup error (file system access error)
#
# Usage:
#   python3 measure_chief_author_span.py [file ...]
#
# SSOT carrier: CFP-1438 Wave 1 declarative anchor (PR #1488 merged) + 본 Wave 2-D wire.
# Precedent byte-pattern: scripts/lib/check_mid_spawn_drift_detection.py (CFP-1500).

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
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_CHIEF_AUTHOR_SPAN_TELEMETRY", "")
if BYPASS_ENV == "1":
    print("[check-chief-author-span-telemetry] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[check-chief-author-span-telemetry]"

# Story file 식별 — docs/stories/**/*.md
STORY_FILE_RE = re.compile(r"docs/stories/.*\.md$")

# Long-span threshold (env configurable, default 10 minutes)
_default_threshold = 10
try:
    LONG_SPAN_MAX_MIN = int(
        os.environ.get("CFP_CHIEF_AUTHOR_SPAN_MAX_MIN", str(_default_threshold))
    )
except (ValueError, TypeError):
    LONG_SPAN_MAX_MIN = _default_threshold

# chief author keyword (case-insensitive substring check — no regex backtracking)
CHIEF_AUTHOR_KEYWORD = "chief author"

# Telemetry marker regexes (single-line anchored, no nested quantifier)
# Inline form: `[chief-author-span: N, <class>]` — simple capture only
CHIEF_AUTHOR_SPAN_MARKER_RE = re.compile(
    r"\[chief-author-span:\s*(\d+|TBD)\s*,\s*([a-z_0-9]+)\s*\]",
    re.IGNORECASE,
)
# YAML-like form: `chief_author_span_minutes: N`
CHIEF_AUTHOR_SPAN_FIELD_RE = re.compile(
    r"^\s*chief_author_span_minutes:\s*(\d+|TBD)\s*$",
    re.IGNORECASE,
)

# Per-entry scan cap (CodeQL ReDoS guard — pathological input bound)
PER_ENTRY_SCAN_CAP = 50

# Block boundary detection: empty line 2-consecutive OR next chief author spawn line OR
# new section heading (`## ` / `### `).
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


def _is_chief_author_spawn_line(line):
    """
    line-level check: "chief author" AND "spawn" substring presence (case-insensitive).
    NO nested-quantifier regex — simple substring check (linear time).

    Pattern source: CFP-1500 `_is_agent_spawn_line` 답습 (role keyword + "spawn" keyword
    AND-condition). 본 lint 의 role keyword scope = chief author 만 (CFP-1500 deputy +
    9 role enum 보다 좁은 scope, ADR-039 Amendment 5 §결정 17 mandate).

    FP-completeness guard 4: markdown table row (line starts with `|`) skip —
    Story §14 Lane Evidence 는 table 형식 abstract row + detail block 양면 representation.
    table cell row 는 짧은 abstract 만 — detail block 만 lint scope 의무.

    FP-completeness guard 5: frontmatter / heading / title 영역 line (title:, name:,
    key:, type:, status: 등 YAML field 가 우측 value 로 "chief author" 포함) silent skip
    — `: ` 좌측이 `agent` / `spawn` 이 아닌 case skip (literal substring AND requirement,
    "spawn" keyword AND-condition 이 frontmatter 부분 차단 대부분 처리).
    """
    stripped = line.lstrip()
    # Markdown table row skip (FP guard 4)
    if stripped.startswith("|"):
        return False
    # AND-condition: BOTH "chief author" AND "spawn" must present (FP guard 5
    # via spawn keyword — frontmatter title/key/type lines rarely contain "spawn")
    ll = line.lower()
    if CHIEF_AUTHOR_KEYWORD not in ll:
        return False
    if "spawn" not in ll:
        return False
    return True


# ── block scan (CodeQL ReDoS guard — line-by-line, capped) ──────────────────
def _scan_entry_block(lines, start_idx):
    """
    From a `chief author` line, scan subsequent lines up to PER_ENTRY_SCAN_CAP
    until block boundary (empty-2-consecutive / next chief author spawn line /
    new section heading).
    Returns dict with keys:
      - `telemetry_marker_present`: bool (either inline `[chief-author-span: ...]` OR field form)
      - `span_minutes`: int or None (extracted from inline marker, None if TBD or absent)
      - `span_class`: str or None ("monolithic" / "multi_step_3" / etc, None if absent)
      - `end_idx`: int (exclusive end of block)
    Line-by-line parse — pathological-input safe.
    """
    result = {
        "telemetry_marker_present": False,
        "span_minutes": None,
        "span_class": None,
        "end_idx": min(start_idx + PER_ENTRY_SCAN_CAP, len(lines)),
    }
    empty_run = 0
    n = len(lines)
    end_at = min(start_idx + 1 + PER_ENTRY_SCAN_CAP, n)

    # Inspect the start_idx line itself for inline marker presence
    start_line = lines[start_idx]
    m = CHIEF_AUTHOR_SPAN_MARKER_RE.search(start_line)
    if m:
        result["telemetry_marker_present"] = True
        try:
            result["span_minutes"] = int(m.group(1))
        except (ValueError, TypeError):
            result["span_minutes"] = None  # TBD or non-int
        result["span_class"] = m.group(2).lower() if m.group(2) else None

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

        # Boundary: next chief author spawn line (start of new entry block)
        if _is_chief_author_spawn_line(line):
            result["end_idx"] = j
            return result

        # Inline marker `[chief-author-span: N, <class>]` (single-line, no backtracking)
        m = CHIEF_AUTHOR_SPAN_MARKER_RE.search(line)
        if m:
            result["telemetry_marker_present"] = True
            try:
                # Only override if not already set (first marker wins)
                if result["span_minutes"] is None:
                    result["span_minutes"] = int(m.group(1))
                    result["span_class"] = m.group(2).lower() if m.group(2) else None
            except (ValueError, TypeError):
                pass  # TBD — keep None

        # YAML-like field form
        if CHIEF_AUTHOR_SPAN_FIELD_RE.match(line):
            result["telemetry_marker_present"] = True
            # field form doesn't capture class — leave class None unless inline form also seen

    return result


# ── 단일 file 검사 ────────────────────────────────────────────────────────────
def _frontmatter_end_idx(lines):
    """
    FP-completeness guard 6: YAML frontmatter scope detection.

    Story file 가 `---\n` line 으로 시작하면, 다음 `---` line 까지가 frontmatter.
    frontmatter 안 title/key/type/active_sessions 등 field 가 우측 value 로
    "chief author" + "spawn" substring 보유해도 lint scope 외 (story metadata 영역).

    Returns:
      - int N — frontmatter 의 closing `---` line index (lines[N] == "---").
        scan 시작 idx = N + 1.
      - 0 — frontmatter 없음 (file 가 `---` 로 시작하지 않음).
    """
    if not lines or not lines[0].strip().startswith("---"):
        return 0
    for j in range(1, min(len(lines), 200)):  # cap 200 line scan
        if lines[j].strip() == "---":
            return j + 1  # start AFTER closing fence
    return 0  # malformed frontmatter — scan from start


def check_file(filepath):
    """
    단일 Story file 검사. 반환: warn_count (int).

    flow:
      1. path filter (templates/**, tests/** skip)
      2. Story file 식별 (docs/stories/**/*.md)
      3. read content
      4. frontmatter 영역 skip (FP guard 6)
      5. line-by-line scan — chief author spawn keyword line 식별
      6. 각 spawn entry block (PER_ENTRY_SCAN_CAP line cap) 안에서:
         (a) telemetry marker presence (inline `[chief-author-span: ...]` OR YAML field form)
         (b) long-span monolithic warning (span ≥ LONG_SPAN_MAX_MIN AND class == "monolithic")
      7. (a) 부재 → [WARN-TELEMETRY-MARKER-ABSENT]
         (b) 위반 → [WARN-LONG-SPAN-MONOLITHIC]
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
    # FP-완화 guard 6: skip YAML frontmatter (Story metadata 영역)
    i = _frontmatter_end_idx(lines)
    while i < n:
        line = lines[i]
        if _is_chief_author_spawn_line(line):
            spawn_count += 1
            block = _scan_entry_block(lines, i)

            # Check (a) — telemetry marker presence
            if not block["telemetry_marker_present"]:
                print(
                    f"{SCRIPT_NAME} [WARN-TELEMETRY-MARKER-ABSENT] {filepath}:{i + 1}: "
                    f"chief author spawn entry detected without "
                    f"`[chief-author-span: <minutes>, <class>]` inline marker OR "
                    f"`chief_author_span_minutes:` YAML field in entry block "
                    f"(scan cap {PER_ENTRY_SCAN_CAP} lines). "
                    f"ADR-039 Amendment 5 §결정 17 chief author spawn span guideline "
                    f"(recommendation tier) + ADR-044 Amendment 3 §결정 9 multi-step "
                    f"chief author pattern paired sibling. Add telemetry marker to "
                    f"Story §14 Lane Evidence chief author spawn entry "
                    f"(e.g. `[chief-author-span: 8, monolithic]` or "
                    f"`[chief-author-span: 12, multi_step_3]`). "
                    f"hotfix bypass: hotfix-bypass:chief-author-span-telemetry label",
                    file=sys.stderr,
                )
                warn_count += 1

            # Check (b) — long-span monolithic warning
            span_min = block["span_minutes"]
            span_class = block["span_class"]
            if (
                span_min is not None
                and span_min >= LONG_SPAN_MAX_MIN
                and span_class == "monolithic"
            ):
                print(
                    f"{SCRIPT_NAME} [WARN-LONG-SPAN-MONOLITHIC] {filepath}:{i + 1}: "
                    f"chief author spawn span = {span_min} min "
                    f"(≥ threshold {LONG_SPAN_MAX_MIN} min) with class `monolithic`. "
                    f"ADR-039 Amendment 5 §결정 17 — long-span chief author spawns "
                    f"should be decomposed into `multi_step_N` pattern (sub-spawn "
                    f"sequence) to narrow CFP-1336 amendment_number_stale_at_planning "
                    f"drift window. Consider refactoring to `multi_step_3` or higher "
                    f"(recommendation tier — awareness only, mandate 아님). "
                    f"hotfix bypass: hotfix-bypass:chief-author-span-telemetry label",
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
                f"({spawn_count} chief author spawn entry/entries all telemetry-marker-present)",
                file=sys.stderr,
            )
        else:
            print(
                f"{SCRIPT_NAME} OK: {filepath} (no chief author spawn entries — silent PASS)",
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
