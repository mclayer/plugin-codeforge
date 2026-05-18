#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
templates/scripts/mirror-dependency-closure.py

CFP-898 Phase 2 — Dependency bundle integrity closure resolver
reconcile-protocol-v1 §4.11 binding block runtime implementation

Algorithm constraints (AM-1~4):
  AM-1: regex_primary — PyYAML 의존 없이 정규식으로 yml run: 블록 분석
  AM-2: transitive_depth_limit=1 — yml 직접 참조만 검사 (스크립트 내부 deps 미추적)
  AM-3: dependency_scope=shell_script_only_v1
        패턴: scripts/check-[a-z0-9-]+\\.sh / templates/scripts/[a-z0-9-]+\\.py
  AM-4: self_app_exemption — 본 파일 자체는 self-loop 0 invariant

Exit codes:
  0 = closure OK (all dependencies present)
  1 = dependency missing (fail-closed)
  2 = parse error / other (abort)

Usage:
  python3 mirror-dependency-closure.py --yml <path>      # single workflow yml
  python3 mirror-dependency-closure.py --all              # all .github/workflows/*.yml
  python3 mirror-dependency-closure.py --yml <path> --dry-run  # preview, exit 0

Environment:
  MIRROR_DEP_WRAPPER_ROOT — wrapper repo root (default: 2 levels up from this file)

ADR-061 정합: 외부 .py 파일, explicit absolute path 사용
ADR-040 Amendment 3 §결정 7.D: self-app verify mandate
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# AM-3: shell_script_only_v1 dependency patterns
# ─────────────────────────────────────────────────────────────────────────────
_DEP_PATTERNS = [
    # scripts/check-<name>.sh
    re.compile(r'\bscripts/check-[a-z0-9-]+\.sh\b'),
    # templates/scripts/<name>.py
    re.compile(r'\btemplates/scripts/[a-z0-9-]+\.py\b'),
]

# YAML comment line pattern (lines starting with optional whitespace then #)
_YAML_COMMENT_LINE = re.compile(r'^\s*#')


def _discover_wrapper_root() -> Path:
    """Determine wrapper repo root.

    Priority:
      1. MIRROR_DEP_WRAPPER_ROOT env var (test seam)
      2. 2 levels up from this file: templates/scripts/ -> templates/ -> repo root
    """
    env_root = os.environ.get("MIRROR_DEP_WRAPPER_ROOT")
    if env_root:
        return Path(env_root).resolve()
    # __file__ = <repo_root>/templates/scripts/mirror-dependency-closure.py
    return Path(__file__).resolve().parent.parent.parent


def _extract_deps_from_yml(yml_path: Path) -> list[str]:
    """Parse yml and extract dependency references matching AM-3 patterns.

    AM-1: regex_primary — no PyYAML; line-by-line regex scan of run: blocks.
    AM-2: transitive_depth_limit=1 — only yml's direct `run:` references.
    AM-4: self-loop exclusion is implicit (script path not in yml run blocks).

    Comment lines (YAML # comments) are excluded from dep extraction.
    Supports both:
      - `run: <inline>` (scalar)
      - `run: |` (block scalar, following indented lines)
    Also handles YAML list item prefix: `- run: ...`
    """
    try:
        text = yml_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"Cannot read yml file: {exc}") from exc

    # Reject clearly malformed content early (lightweight heuristic).
    # AM-1 regex_primary: only patterns that do NOT false-positive on valid
    # GitHub Actions YAML (e.g. `types: [opened, ...]` is valid inline sequence).
    # Pattern: unclosed Jinja/flow mapping `{{ ...` without closing `}}` on same line.
    # This covers the test case: "broken: yaml: {{ invalid"
    # Deliberately excluded: `^\s*\w+:\s*\[` (false-positives on `types:`/`branches:`/
    # `paths:`/`tags:`/`runs-on:` inline sequences — valid GitHub Actions YAML).
    _MALFORMED_PATTERNS = [
        re.compile(r'\{\{[^}]*$'),  # unclosed flow mapping / Jinja template (no closing }})
    ]
    for line_no, raw_line in enumerate(text.splitlines()):
        for mp in _MALFORMED_PATTERNS:
            if mp.search(raw_line):
                raise ValueError(
                    f"Likely malformed YAML at line {line_no + 1}: {raw_line!r}"
                )

    deps: list[str] = []
    in_run_block = False
    run_indent: int | None = None

    for line in text.splitlines():
        stripped = line.rstrip()

        # Skip pure YAML comment lines (AM-1: regex_primary filter)
        if _YAML_COMMENT_LINE.match(stripped):
            continue

        # Detect `run:` key (scalar or block scalar).
        # Supports both:
        #   `      run: ...`          (plain mapping key)
        #   `      - run: ...`        (YAML list item with run: key)
        # Capture group 1 = full indentation including optional `- ` marker
        run_match = re.match(r'^(\s+(?:-\s+)?)run:\s*', stripped)
        if run_match is None:
            # Also match top-level `run:` with no leading space (edge case)
            run_match = re.match(r'^((?:-\s+)?)run:\s*', stripped)

        if run_match:
            in_run_block = True
            # Logical indent = length of whitespace portion only (exclude `- `)
            prefix = run_match.group(1)
            # Count actual spaces only (strip list marker for indent tracking)
            run_indent = len(re.match(r'^\s*', prefix).group(0))
            # Extract inline value: `run: bash scripts/check-foo.sh`
            inline_val = stripped[run_match.end():]
            if inline_val and not inline_val.lstrip().startswith("|"):
                for pat in _DEP_PATTERNS:
                    for m in pat.finditer(inline_val):
                        deps.append(m.group(0))
            continue

        if in_run_block:
            # Continuation lines of a block scalar (|) must be more indented
            if not stripped:
                # Blank lines inside block scalar are allowed
                continue
            line_indent = len(stripped) - len(stripped.lstrip())
            # Skip block scalar indicator lines (|, |-, |+, etc.)
            if stripped.lstrip().startswith("|"):
                continue
            if line_indent > run_indent:
                # Inside run block body — scan for dep patterns
                for pat in _DEP_PATTERNS:
                    for m in pat.finditer(stripped):
                        deps.append(m.group(0))
            else:
                # Exited run block (different YAML key or less indentation)
                in_run_block = False
                run_indent = None

    return list(dict.fromkeys(deps))  # deduplicate, preserve order


def _check_deps(
    yml_path: Path,
    wrapper_root: Path,
    dry_run: bool,
) -> int:
    """Check dependency closure for a single yml file.

    Returns exit code: 0 / 1 / 2.
    """
    try:
        deps = _extract_deps_from_yml(yml_path)
    except ValueError as exc:
        print(f"[ERR] Parse error for {yml_path}: {exc}", file=sys.stderr)
        return 2

    missing: list[str] = []
    for dep in deps:
        dep_path = wrapper_root / dep
        # AM-2: 1-hop only — check dep_path existence (os.path.exists follows symlinks)
        if not dep_path.exists():
            missing.append(dep)

    if dry_run:
        if missing:
            print(f"[dry-run] missing deps in {yml_path.name}: {', '.join(missing)}")
        else:
            print(f"[dry-run] all deps present for {yml_path.name}")
        return 0

    if missing:
        for dep in missing:
            print(
                f"[ERR] Dependency missing: {dep} (referenced by: {yml_path})",
                file=sys.stderr,
            )
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dependency bundle integrity closure resolver (CFP-898 §4.11)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--yml", metavar="PATH", help="Single workflow yml to check")
    group.add_argument(
        "--all",
        action="store_true",
        help="Check all .github/workflows/*.yml in wrapper root",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview missing deps without failing (exit 0)",
    )

    args = parser.parse_args()
    wrapper_root = _discover_wrapper_root()

    if args.yml:
        yml_path = Path(args.yml).resolve()
        if not yml_path.exists():
            print(f"[ERR] yml file not found: {yml_path}", file=sys.stderr)
            return 2
        return _check_deps(yml_path, wrapper_root, dry_run=args.dry_run)

    # --all mode: scan .github/workflows/*.yml
    workflows_dir = wrapper_root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        print(f"[ERR] workflows dir not found: {workflows_dir}", file=sys.stderr)
        return 2

    yml_files = sorted(workflows_dir.glob("*.yml"))
    if not yml_files:
        print(f"[WARN] No yml files found in {workflows_dir}")
        return 0

    overall_rc = 0
    for yf in yml_files:
        rc = _check_deps(yf, wrapper_root, dry_run=args.dry_run)
        if rc != 0 and not args.dry_run:
            overall_rc = rc

    return overall_rc


if __name__ == "__main__":
    sys.exit(main())
