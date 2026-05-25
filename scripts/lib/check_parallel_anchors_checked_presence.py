#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1306 / ADR-060 Amendment 15 §결정 29 / ADR-068 I-2 cross-module propagation completeness
#
# review-verdict-v4 findings[].parallel_anchors_checked[] presence-grep heuristic lint
# Wave 3 mechanical enforcement layer (Wave 1=CFP-1291 prose, Wave 2=CFP-1303 schema)
#
# Purpose:
#   PR-time warning-tier lint for review-verdict-v4 packet files.
#   Checks presence of findings[].parallel_anchors_checked[] optional array field
#   for candidate findings (5 pattern_type 후보 category).
#
# 3-state semantic:
#   absent       → exit 1 (WARNING) — field missing, emit advisory
#   present+clean → exit 0 (PASS)   — all matched: false, "evidence of completeness"
#   present+matched → exit 0 (PASS) — matched: true found, "parallel anchor found" advisory
#
# 5 pattern_type enum closed-set (review-verdict-v4 v4.9 SSOT L55):
#   local_remote   — LOCAL_X ↔ REMOTE_X
#   client_server  — client side ↔ server side symmetric
#   read_write     — read path ↔ write path
#   forward_reverse — forward direction ↔ reverse direction
#   enum_closure   — enum value 전수 coverage
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (no candidate findings, or all have valid parallel_anchors_checked)
#   1 = WARNING (candidate finding without field, or field malformed)
#   2 = META-ERROR (file not found / IO error / YAML parse failure on non-markdown)
#
# ADR-061 Amendment 3 (CFP-1497 CodeQL ReDoS guard):
#   Literal string containment only — NO backtracking regex on multi-line content.
#   Line-by-line parse (split on newline, ops on single line only).
#
# AC-13 (DR iter 1): Markdown fenced ```yaml block extraction before yaml.safe_load
# AC-14 (DR iter 1): non-array parallel_anchors_checked → WARNING advisory + skip
# AC-15 (DR iter 1): pattern_type lives inside parallel_anchors_checked[] items, not findings[].type

import sys
import os
from pathlib import Path
from typing import Any, Optional

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Exit code 3-tier (ADR-060 §결정 15)
EXIT_PASS = 0
EXIT_WARNING = 1
EXIT_META_ERROR = 2

# 5 pattern_type enum closed-set (review-verdict-v4 v4.9 SSOT)
VALID_PATTERN_TYPES = frozenset({
    "local_remote",
    "client_server",
    "read_write",
    "forward_reverse",
    "enum_closure",
})

# Candidate finding category values — overlap with pattern_type (AC-15: lives in parallel_anchors_checked[], not findings[].type)
# However, findings[].category may use pattern_type values as hints for parallel parity check candidates.
CANDIDATE_CATEGORIES = frozenset({
    "local_remote",
    "client_server",
    "read_write",
    "forward_reverse",
    "enum_closure",
})

# Schema location confusion: if findings[].type (not category) uses a pattern_type value → WARNING
# This detects AC-15 confusion case (TC-9)


def _extract_yaml_from_markdown(content: str) -> Optional[str]:
    """
    Extract YAML content from a fenced ```yaml ... ``` block in markdown.
    Returns first fenced yaml block content, or None if no block found.

    ADR-061 Amendment 3 (ReDoS guard): line-by-line parse, no backtracking regex.
    """
    lines = content.splitlines()
    in_block = False
    block_lines = []

    for line in lines:
        stripped = line.strip()
        if not in_block:
            # Literal string containment — no regex (ReDoS guard)
            if stripped == "```yaml" or stripped == "```yaml\r":
                in_block = True
                block_lines = []
        else:
            if stripped == "```" or stripped == "```\r":
                in_block = False
                if block_lines:
                    return "\n".join(block_lines)
                # Empty block — reset and continue looking
                block_lines = []
            else:
                block_lines.append(line)

    return None


def _load_yaml_safe(content: str) -> Any:
    """Load YAML content safely. Returns parsed object or raises on error."""
    import yaml  # lazy import to keep startup fast
    return yaml.safe_load(content)


def _is_markdown_file(file_path: str) -> bool:
    """Check if file is a markdown file by extension."""
    return file_path.lower().endswith(".md")


def check_finding(finding: Any, finding_idx: int, file_path: str) -> list:
    """
    Check a single finding dict for parallel_anchors_checked field.

    Returns list of (severity, message) tuples.
      severity: "WARNING" | "PASS" | "NOTICE"
    """
    issues = []

    if not isinstance(finding, dict):
        return issues

    finding_id = finding.get("id", f"findings[{finding_idx}]")

    # AC-15: detect schema location confusion
    # If findings[].type uses a pattern_type value (not the correct location)
    finding_type = finding.get("type", "")
    if isinstance(finding_type, str) and finding_type in VALID_PATTERN_TYPES:
        issues.append((
            "WARNING",
            f"[parallel-anchors-checked-presence] WARNING: {file_path}:{finding_id}: "
            f"schema location confusion — findings[].type='{finding_type}' uses pattern_type enum value. "
            f"pattern_type belongs inside parallel_anchors_checked[] items, not findings[].type. "
            f"(AC-15, review-verdict-v4 v4.9)"
        ))
        return issues

    # Check if this is a candidate finding (category uses pattern_type values)
    category = finding.get("category", "")
    if not isinstance(category, str):
        return issues

    if category not in CANDIDATE_CATEGORIES:
        # Non-candidate finding — skip (TC-12)
        issues.append((
            "PASS",
            f"[parallel-anchors-checked-presence] PASS: {file_path}:{finding_id}: "
            f"non-candidate category='{category}', skip"
        ))
        return issues

    # Candidate finding — check parallel_anchors_checked field presence
    pac_field = finding.get("parallel_anchors_checked")

    if pac_field is None:
        # Field absent — WARNING (TC-1)
        issues.append((
            "WARNING",
            f"[parallel-anchors-checked-presence] WARNING: {file_path}:{finding_id}: "
            f"candidate finding (category='{category}') missing parallel_anchors_checked field. "
            f"Add parallel_anchors_checked[] array per review-verdict-v4 v4.9 (CFP-1303). "
            f"hotfix bypass: hotfix-bypass:parallel-anchors-checked-presence"
        ))
        return issues

    # AC-14: non-array type check (TC-10)
    if not isinstance(pac_field, list):
        type_name = type(pac_field).__name__
        issues.append((
            "WARNING",
            f"[parallel-anchors-checked-presence] WARNING: {file_path}:{finding_id}: "
            f"parallel_anchors_checked field type mismatch — expected array got {type_name}. "
            f"(AC-14 review-verdict-v4 v4.9)"
        ))
        return issues

    # Empty array — declarative zero-coverage (TC-7)
    if len(pac_field) == 0:
        issues.append((
            "WARNING",
            f"[parallel-anchors-checked-presence] WARNING: {file_path}:{finding_id}: "
            f"parallel_anchors_checked declarative zero-coverage — empty array present. "
            f"Populate with searched candidate sites (even if matched: false)."
        ))
        return issues

    # Validate each entry in parallel_anchors_checked[]
    has_matched_true = False
    all_valid = True

    for i, entry in enumerate(pac_field):
        if not isinstance(entry, dict):
            issues.append((
                "WARNING",
                f"[parallel-anchors-checked-presence] WARNING: {file_path}:{finding_id}: "
                f"parallel_anchors_checked[{i}] is not a dict — schema violation"
            ))
            all_valid = False
            continue

        # Check matched field presence (TC-5)
        if "matched" not in entry:
            issues.append((
                "WARNING",
                f"[parallel-anchors-checked-presence] WARNING: {file_path}:{finding_id}: "
                f"parallel_anchors_checked[{i}] missing 'matched' field (3-field schema: "
                f"file_line + pattern_type + matched). (review-verdict-v4 v4.9)"
            ))
            all_valid = False
            continue

        # Check pattern_type field presence and enum membership (TC-4)
        if "pattern_type" not in entry:
            issues.append((
                "WARNING",
                f"[parallel-anchors-checked-presence] WARNING: {file_path}:{finding_id}: "
                f"parallel_anchors_checked[{i}] missing 'pattern_type' field"
            ))
            all_valid = False
            continue

        pt = entry.get("pattern_type", "")
        if not isinstance(pt, str) or pt not in VALID_PATTERN_TYPES:
            issues.append((
                "WARNING",
                f"[parallel-anchors-checked-presence] WARNING: {file_path}:{finding_id}: "
                f"parallel_anchors_checked[{i}].pattern_type='{pt}' enum drift — "
                f"not in 5 closed-set (local_remote/client_server/read_write/forward_reverse/enum_closure). "
                f"(review-verdict-v4 v4.9 SSOT)"
            ))
            all_valid = False
            continue

        # matched: true found (TC-3)
        if entry.get("matched") is True:
            has_matched_true = True

    if all_valid:
        if has_matched_true:
            # present + matched: true → PASS with advisory (TC-3)
            issues.append((
                "PASS",
                f"[parallel-anchors-checked-presence] PASS: {file_path}:{finding_id}: "
                f"parallel_anchors_checked present, parallel anchor found (matched: true). "
                f"Consider appending new finding for the matched parallel site."
            ))
        else:
            # present + all matched: false → PASS (TC-2)
            issues.append((
                "PASS",
                f"[parallel-anchors-checked-presence] PASS: {file_path}:{finding_id}: "
                f"parallel_anchors_checked present (evidence of clean enumeration, all matched: false)"
            ))

    return issues


def check_file(file_path: str) -> int:
    """
    Lint a single file for parallel_anchors_checked field presence.

    Returns exit code (0/1/2).
    """
    path = Path(file_path)

    if not path.exists():
        print(
            f"[parallel-anchors-checked-presence] META-ERROR: file not found: {file_path}",
            file=sys.stderr,
        )
        return EXIT_META_ERROR

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(
            f"[parallel-anchors-checked-presence] META-ERROR: cannot read {file_path}: {e}",
            file=sys.stderr,
        )
        return EXIT_META_ERROR

    # AC-13: Markdown fenced yaml block extraction
    if _is_markdown_file(file_path):
        yaml_content = _extract_yaml_from_markdown(content)
        if yaml_content is None:
            # No fenced yaml block → scope empty, PASS (TC-8)
            print(
                f"[parallel-anchors-checked-presence] PASS: {file_path}: "
                f"markdown file without fenced yaml block — lint scope empty"
            )
            return EXIT_PASS
        content = yaml_content

    # Parse YAML
    try:
        import yaml
        data = yaml.safe_load(content)
    except Exception as e:
        print(
            f"[parallel-anchors-checked-presence] META-ERROR: YAML parse error in {file_path}: {e}",
            file=sys.stderr,
        )
        return EXIT_META_ERROR

    if not isinstance(data, dict):
        # No dict root — scope empty
        print(
            f"[parallel-anchors-checked-presence] PASS: {file_path}: "
            f"YAML root is not a dict — lint scope empty"
        )
        return EXIT_PASS

    findings = data.get("findings")

    if findings is None or not isinstance(findings, list) or len(findings) == 0:
        # No findings — scope empty (TC-11)
        print(
            f"[parallel-anchors-checked-presence] PASS: {file_path}: "
            f"no findings[] array — lint scope empty"
        )
        return EXIT_PASS

    max_exit = EXIT_PASS
    has_any_output = False

    for idx, finding in enumerate(findings):
        issues = check_finding(finding, idx, file_path)
        for severity, message in issues:
            print(message)
            has_any_output = True
            if severity == "WARNING" and max_exit < EXIT_WARNING:
                max_exit = EXIT_WARNING

    if not has_any_output:
        print(
            f"[parallel-anchors-checked-presence] PASS: {file_path}: "
            f"all findings checked — no issues"
        )

    return max_exit


def main() -> int:
    """Entry point — accepts 1+ file paths as positional arguments."""
    args = sys.argv[1:]

    if not args:
        print(
            "[parallel-anchors-checked-presence] META-ERROR: no file paths provided",
            file=sys.stderr,
        )
        print("Usage: python3 check_parallel_anchors_checked_presence.py <file> [...]", file=sys.stderr)
        return EXIT_META_ERROR

    max_exit = EXIT_PASS
    for file_path in args:
        result = check_file(file_path)
        if result > max_exit:
            max_exit = result

    return max_exit


if __name__ == "__main__":
    sys.exit(main())
