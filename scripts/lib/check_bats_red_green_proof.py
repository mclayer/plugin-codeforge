#!/usr/bin/env python3
"""CFP-1334 Phase 2 — bats fixture RED→GREEN proof presence lint.

ADR-060 framework warning-tier mechanical enforcement of CFP-1334 declaration
(discriminating fixture mandate). Detects bats fixtures (`tests/**/*.bats`)
that lack RED→GREEN proof artifact markers — emits advisory warning.

Heuristic = grep-presence of 5 markers in the bats fixture body:
  1. ``pre_impl_sha`` — git SHA pin of pre-implementation HEAD
  2. ``git stash push`` OR ``git stash pop`` — stash sequence reference
  3. ``discriminating`` OR ``regression_guard`` — role classification vocabulary
  4. ``RED.{1,5}GREEN`` OR ``pre-impl HEAD`` — narrative anchor
  5. ``platform_verified`` — cross-platform marker

Threshold: >=3/5 markers present per file → PASS. <3/5 → warning emit.

Bypass: ``hotfix-bypass:bats-red-green-proof`` label (label-registry-v2 family).

Reference:
  - ADR-060: evidence-enforceable promotion framework
  - ADR-061 §결정 1 + Amendment 1 §결정 6.A: external .py split convention
  - docs/domain-knowledge/domain/test-discipline/red-green-stash-proof-pattern.md:
    narrative SSOT (codeforge governance 어휘 promotion)
  - evidence-checks-registry.yaml: bats-red-green-proof-presence entry SSOT

Usage::

  bash scripts/check-bats-red-green-proof.sh [bats-file...]

If no files passed, all ``tests/**/*.bats`` are scanned.

Exit codes:
  - 0: PASS (all files >=3/5 markers OR no files)
  - 1: WARNING (1+ files <3/5 markers)  --- non-blocking, advisory
  - 2: SCRIPT ERROR (unexpected exception, file IO error etc.)
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Iterable

# 5 marker patterns (closed-set, ordered for stable reporting)
MARKER_PATTERNS = [
    ("pre_impl_sha", re.compile(r"pre_impl_sha", re.IGNORECASE)),
    ("git_stash_sequence", re.compile(r"git stash (push|pop|--include-untracked)", re.IGNORECASE)),
    ("role_vocabulary", re.compile(r"\b(discriminating|regression_guard)\b", re.IGNORECASE)),
    ("red_green_anchor", re.compile(r"RED.{1,5}GREEN|pre-impl HEAD|pre-GREEN HEAD", re.IGNORECASE)),
    ("platform_verified", re.compile(r"platform_verified", re.IGNORECASE)),
]

PASS_THRESHOLD = 3   # >=3/5 markers required


def detect_markers(content: str) -> list[str]:
    """Return list of marker names that appear in content."""
    return [name for name, pattern in MARKER_PATTERNS if pattern.search(content)]


def scan_file(path: Path) -> tuple[int, list[str]]:
    """Scan one bats file. Returns (marker_count, marker_names)."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"  [ERROR] cannot read {path}: {exc}", file=sys.stderr)
        return (0, [])
    markers = detect_markers(content)
    return (len(markers), markers)


def collect_bats_files(repo_root: Path) -> list[Path]:
    """Collect tests/**/*.bats files relative to repo_root."""
    tests_dir = repo_root / "tests"
    if not tests_dir.is_dir():
        return []
    return sorted(tests_dir.rglob("*.bats"))


def main(argv: list[str]) -> int:
    repo_root = Path(os.environ.get("CFP_REPO_ROOT", ".")).resolve()

    if len(argv) > 1:
        files = [Path(p).resolve() for p in argv[1:]]
    else:
        files = collect_bats_files(repo_root)

    if not files:
        print("CFP-1334 bats-red-green-proof-presence: no bats files to scan")
        return 0

    warnings = 0
    passes = 0
    for path in files:
        count, markers = scan_file(path)
        rel = path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
        if count >= PASS_THRESHOLD:
            print(f"  [PASS] {rel}: {count}/5 markers ({', '.join(markers)})")
            passes += 1
        else:
            print(
                f"  [WARN] {rel}: {count}/5 markers "
                f"({', '.join(markers) or 'none'}) — vacuous-green risk"
            )
            warnings += 1

    total = len(files)
    print(
        f"\nCFP-1334 bats-red-green-proof-presence: {passes}/{total} PASS, "
        f"{warnings} WARNING (threshold >={PASS_THRESHOLD}/5 markers)"
    )

    if warnings > 0:
        print(
            "  Bypass label: hotfix-bypass:bats-red-green-proof "
            "(per evidence-checks-registry.yaml + label-registry-v2)"
        )
        return 1   # advisory warning
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:   # noqa: BLE001
        print(f"CFP-1334 bats-red-green-proof: script error: {exc}", file=sys.stderr)
        sys.exit(2)
