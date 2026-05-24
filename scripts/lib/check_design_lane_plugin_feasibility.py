#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1367 / ADR-107 Amendment 1 §결정 2 — F2 design-lane-plugin-feasibility-check
# ADR-061 §결정 1 — Python SSOT (heredoc 금지), ADR-060 §결정 5 warning-tier
# ADR-061 Amendment 3 (CFP-1507) — CodeQL ReDoS guard: line-by-line parse (no backtracking regex)
#
# 검사 목적:
#   Design lane PR 안에서 ArchitectAgent §3 / Change Plan §3 cross-repo plugin 영역
#   fact claim 에 verify-before-trust annotation presence 동적 검사.
#
#   Detection mechanism (Wave 1 heuristic):
#     - 문서 파일 내 cross-repo plugin path 인용 감지:
#       pattern: `mclayer/plugin-codeforge-` (line-by-line, no backtracking)
#     - 각 인용 직후 [verified-via: ...] annotation grep-presence verify
#       pattern: `[verified-via:` (line-by-line, ADR-061 Amendment 3 ReDoS guard)
#     - annotation present → PASS / missing → WARN
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (파일 인코딩 하드 오류 등)
#   2 — setup error (파일 없음 등)
#
# Usage:
#   python3 check_design_lane_plugin_feasibility.py --doc-file <story-or-changeplan-path>
#
# Bypass channel: HOTFIX_BYPASS_DESIGN_LANE_PLUGIN_FEASIBILITY=1 env

import sys
import os
import argparse
from pathlib import Path

# Windows console 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_DESIGN_LANE_PLUGIN_FEASIBILITY", "")
if BYPASS_ENV == "1":
    print("[design-feasibility-lint] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ──────────────────────────────────────────────────────────────────────
SCRIPT_NAME = "[design-feasibility-lint]"

# Wave 1 detection patterns (line-by-line — ADR-061 Amendment 3 ReDoS guard)
# No backtracking regex: literal prefix check on split lines
PLUGIN_PATH_PREFIX = "mclayer/plugin-codeforge-"
ANNOTATION_PREFIX = "[verified-via:"

# 5-enum verify scope hint (informational, ADR-107 §결정 2)
VERIFY_SCOPE_HINTS = [
    "file existence",
    "directory structure",
    "mechanism wire status",
    "schema structure",
    "cross-repo state freshness",
]


def find_plugin_refs_and_annotations(text: str) -> list[dict]:
    """line-by-line 으로 plugin path 인용 + annotation presence 탐지.

    Returns list of dicts:
      { 'line_no': int, 'line': str, 'has_annotation': bool }

    ADR-061 Amendment 3 ReDoS guard:
    - No backtracking regex on multi-line text
    - Split on newline, check each line with literal prefix containment
    """
    results = []
    lines = text.splitlines()

    for i, line in enumerate(lines, start=1):
        # check if line contains plugin path prefix (literal containment, no regex)
        if PLUGIN_PATH_PREFIX in line:
            # check same line for annotation (most common case)
            has_annotation = ANNOTATION_PREFIX in line
            if not has_annotation:
                # check next line too (annotation may be on following line)
                if i < len(lines):
                    next_line = lines[i]  # i is 1-based, lines is 0-based → lines[i] = line i+1
                    has_annotation = ANNOTATION_PREFIX in next_line
            results.append({
                "line_no": i,
                "line": line.strip(),
                "has_annotation": has_annotation,
            })

    return results


def check_file(doc_path: Path) -> list[dict]:
    """문서 파일을 검사하여 annotation 누락 결과 반환.

    Returns list of dicts for refs with missing annotation.
    Raises OSError on read failure.
    """
    text = doc_path.read_text(encoding="utf-8", errors="replace")
    refs = find_plugin_refs_and_annotations(text)

    missing = [r for r in refs if not r["has_annotation"]]
    return missing


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="design-lane-plugin-feasibility-check lint"
    )
    parser.add_argument("--doc-file", help="Story or Change Plan file to check")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if not args.doc_file:
        print(f"{SCRIPT_NAME} [INFO] --doc-file 미지정 — skip", file=sys.stderr)
        return 0

    doc_path = Path(args.doc_file)

    if not doc_path.exists():
        print(f"{SCRIPT_NAME} [INFO] doc file not found: {doc_path} — skip (exit 2)", file=sys.stderr)
        return 2

    try:
        missing_annotations = check_file(doc_path)
    except OSError as e:
        print(f"{SCRIPT_NAME} [ERROR] file read error: {e}", file=sys.stderr)
        return 2

    if not missing_annotations:
        # Count how many refs were found
        text = doc_path.read_text(encoding="utf-8", errors="replace")
        all_refs = find_plugin_refs_and_annotations(text)

        if all_refs:
            print(
                f"{SCRIPT_NAME} [PASS] {doc_path}: {len(all_refs)} plugin ref(s) — "
                "all have [verified-via: ...] annotation.",
                file=sys.stderr,
            )
        else:
            print(
                f"{SCRIPT_NAME} [PASS] {doc_path}: no cross-repo plugin path refs found — skip.",
                file=sys.stderr,
            )
        return 0
    else:
        print(
            f"{SCRIPT_NAME} [WARN] {doc_path}: {len(missing_annotations)} plugin ref(s) missing "
            "[verified-via: ...] annotation:",
            file=sys.stderr,
        )
        for ref in missing_annotations:
            print(
                f"  line {ref['line_no']}: {ref['line'][:120]}",
                file=sys.stderr,
            )
        print(
            f"{SCRIPT_NAME} [WARN] verify-before-trust annotation 의무 (ADR-107 §결정 2 + ADR-082 §결정 2).\n"
            f"  5-enum verify scope: {', '.join(VERIFY_SCOPE_HINTS)}\n"
            f"  annotation 예시: [verified-via: gh api repos/mclayer/plugin-codeforge-<name>/contents/<path>]\n"
            f"{SCRIPT_NAME} warning-tier (ADR-060 §결정 5) — PR merge 미차단.",
            file=sys.stderr,
        )
        # warning-tier: exit 0 (PR merge 미차단)
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
