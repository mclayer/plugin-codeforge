"""CFP-1807 — cross-repo branch protection contexts parity warning lint.

8 codeforge plugin family 의 `main` branch required_status_checks contexts 가
CLAUDE.md SSOT 표 "6 lane plugin branch protection contexts SSOT" 와 drift 시
warning emit (markdown table).

Tier: warning (ADR-060 §결정 5 default — first introduction, exit 0).
Owner ADR: ADR-024 §결정 6.A (hotfix-bypass family) — `hotfix-bypass:branch-protection-context-parity`.

Implementation notes:
- ADR-061 Amendment 3 §결정 11 정합 — CLAUDE.md table parse 시 line-by-line scan
  (`text.splitlines()` + anchored simple regex + per-entry scan cap), ReDoS-safe.
- gh CLI = primary; CI 환경 `GH_TOKEN` env 의무 (workflow 가 주입).
- mismatch 발견 시 markdown table 출력 + warning prefix, exit 0 (warning-tier).

Exit codes:
  0 — PASS (parity OK) OR FAIL-as-warning (drift detected, markdown table emitted)
  2 — usage error (e.g., gh CLI absent, CLAUDE.md table not found)

Usage:
  python scripts/lib/check_branch_protection_context_parity.py [--repo-root <path>]

SSOT bindings:
  - CLAUDE.md "6 lane plugin branch protection contexts SSOT" 표 (expected)
  - GitHub API `repos/<owner>/<repo>/branches/main/protection/required_status_checks` (actual)
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Windows Git Bash / cp949 console — force UTF-8 stdout/stderr to avoid
# UnicodeEncodeError on em-dash (U+2014) and Korean characters in output.
# CFP-418 cross-OS encoding evidence inherits.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

# 8 codeforge plugin family — closed-enum SSOT (CLAUDE.md "Development Agent Team" 표 + Marketplace cross-repo 동기화 의무)
# Wrapper + 8 lane plugin. ADR-016 §family 정합.
PLUGIN_FAMILY: List[str] = [
    "mclayer/plugin-codeforge",
    "mclayer/plugin-codeforge-requirements",
    "mclayer/plugin-codeforge-design",
    "mclayer/plugin-codeforge-review",
    "mclayer/plugin-codeforge-develop",
    "mclayer/plugin-codeforge-test",
    "mclayer/plugin-codeforge-pmo",
    "mclayer/plugin-codeforge-deploy",
    "mclayer/plugin-codeforge-deploy-review",
]

CLAUDE_MD_TABLE_ANCHOR = "6 lane plugin branch protection contexts SSOT"

# Line-by-line scan cap (ADR-061 Amendment 3 §결정 11 — per-entry scan cap default).
# CLAUDE.md table contains at most ~10 plugin rows; 50 line cap covers anchor → table end.
TABLE_SCAN_CAP = 50


def repo_short_name(slug: str) -> str:
    """`mclayer/plugin-codeforge-design` → `plugin-codeforge-design`."""
    return slug.split("/", 1)[1]


def claude_md_row_key(slug: str) -> str:
    """SSOT table row key for plugin slug.

    Mapping (CLAUDE.md 표 §319-329 verbatim):
      mclayer/plugin-codeforge              → wrapper (plugin-codeforge)
      mclayer/plugin-codeforge-design       → codeforge-design
      mclayer/plugin-codeforge-review       → codeforge-review
      mclayer/plugin-codeforge-develop      → codeforge-develop
      mclayer/plugin-codeforge-test         → codeforge-test
      mclayer/plugin-codeforge-deploy       → codeforge-deploy
      mclayer/plugin-codeforge-deploy-review → codeforge-deploy-review

    Plugin slugs not in the CLAUDE.md table (codeforge-requirements / codeforge-pmo
    currently absent) return empty string — caller treats as "no SSOT row, skip parity check".
    """
    short = repo_short_name(slug)
    if short == "plugin-codeforge":
        return "wrapper (plugin-codeforge)"
    # `plugin-codeforge-*` → `codeforge-*`
    if short.startswith("plugin-"):
        return short[len("plugin-"):]
    return ""


def parse_claude_md_table(claude_md_path: Path) -> dict[str, List[str]]:
    """Parse CLAUDE.md "6 lane plugin branch protection contexts SSOT" table.

    Returns mapping `row_key → expected contexts list`.

    Line-by-line scan (ADR-061 Amendment 3 §결정 11):
      1) find anchor line containing CLAUDE_MD_TABLE_ANCHOR
      2) skip until first `|--|` separator (table header)
      3) parse up to TABLE_SCAN_CAP subsequent table rows
      4) extract column 2 (required_status_checks contexts) as JSON-like array
      5) stop on first non-table line
    """
    if not claude_md_path.exists():
        raise SystemExit(
            f"CLAUDE.md not found: {claude_md_path} "
            "(expected at repo root or use --repo-root)"
        )

    text = claude_md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Step 1: locate anchor line — heading-strict (line starts with `**` bold marker).
    # CFP-1855 fix: prior implementation matched first occurrence including narrative
    # text mention (e.g., line 264 narrative reference) → scan cap exhausted before
    # actual heading at line 322. Strict pattern: heading line starts with `**`
    # AND contains anchor → narrative mention skipped.
    anchor_idx = -1
    for i, line in enumerate(lines):
        if CLAUDE_MD_TABLE_ANCHOR in line and line.lstrip().startswith("**"):
            anchor_idx = i
            break

    if anchor_idx == -1:
        raise SystemExit(
            f"CLAUDE.md table anchor heading '**{CLAUDE_MD_TABLE_ANCHOR}**' not found"
        )

    # Step 2: skip until table separator `|--`
    sep_idx = -1
    for i in range(anchor_idx + 1, min(anchor_idx + TABLE_SCAN_CAP, len(lines))):
        line = lines[i]
        if line.startswith("|--"):
            sep_idx = i
            break

    if sep_idx == -1:
        raise SystemExit("CLAUDE.md table separator '|--' not found within scan cap")

    # Step 3-5: parse table rows
    result: dict[str, List[str]] = {}
    for i in range(sep_idx + 1, min(sep_idx + 1 + TABLE_SCAN_CAP, len(lines))):
        line = lines[i].rstrip()
        if not line.startswith("|"):
            break  # end of table

        # Split on `|`; first/last elements are empty (leading/trailing pipes)
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 4:
            continue  # malformed row

        row_key = cells[1]
        contexts_cell = cells[2]

        # contexts_cell looks like:  `["phase-gate-mergeable","check-gate"]`  (wrapped in backticks)
        # OR  `NOT PROTECTED`
        if "NOT PROTECTED" in contexts_cell:
            result[row_key] = []  # marker: not yet protected
            continue

        # Extract JSON array from inside backticks
        # ADR-061 Amd 3 §결정 11 정합 — anchored simple regex (no nested quantifier)
        json_start = contexts_cell.find("[")
        json_end = contexts_cell.rfind("]")
        if json_start == -1 or json_end == -1 or json_end <= json_start:
            continue

        json_text = contexts_cell[json_start : json_end + 1]
        try:
            contexts = json.loads(json_text)
        except json.JSONDecodeError:
            continue

        if isinstance(contexts, list):
            result[row_key] = [str(c) for c in contexts]

    return result


def fetch_actual_contexts(slug: str) -> Tuple[List[str], str]:
    """Fetch actual `main` branch protection contexts via gh CLI.

    Returns `(contexts, status)` where status is one of:
      - "ok"
      - "not_protected" (404 — repos/.../branches/main/protection)
      - "error: <msg>" (other failures)
    """
    # Allow test override via env (CFP-1807 bats fixture — Windows .exe vs shim resolution).
    # Two modes:
    #   default: GH_CLI_BIN env (or 'gh') — production code path
    #   python_shim: invoke python3 with GH_SHIM_SCRIPT — bats fixture path (Windows CreateProcess
    #     cannot exec .sh shim files; this mode uses python3 directly).
    override_mode = os.environ.get("GH_CLI_BIN_OVERRIDE_MODE", "")
    if override_mode == "python_shim":
        shim_script = os.environ.get("GH_SHIM_SCRIPT", "")
        cmd = [
            sys.executable,
            shim_script,
            "api",
            f"repos/{slug}/branches/main/protection/required_status_checks",
            "--jq",
            ".contexts[]",
        ]
    else:
        gh_bin = os.environ.get("GH_CLI_BIN", "gh")
        cmd = [
            gh_bin,
            "api",
            f"repos/{slug}/branches/main/protection/required_status_checks",
            "--jq",
            ".contexts[]",
        ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except FileNotFoundError:
        return [], "error: gh CLI not available"
    except subprocess.TimeoutExpired:
        return [], "error: gh CLI timeout after 30s"

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        # 404 = branch protection not configured / branch not present
        if "Not Found" in stderr or "404" in stderr or "HTTP 404" in stderr:
            return [], "not_protected"
        return [], f"error: {stderr[:200]}"

    # stdout: one context per line
    stdout = result.stdout or ""
    contexts = [line.strip() for line in stdout.splitlines() if line.strip()]
    return contexts, "ok"


def compare(expected: List[str], actual: List[str]) -> Tuple[List[str], List[str]]:
    """Return `(missing_in_actual, unexpected_in_actual)`."""
    expected_set = set(expected)
    actual_set = set(actual)
    missing = sorted(expected_set - actual_set)
    unexpected = sorted(actual_set - expected_set)
    return missing, unexpected


def emit_markdown_table(rows: List[dict]) -> str:
    """Emit drift markdown table for human consumption (PR comment / stdout)."""
    if not rows:
        return ""

    lines = [
        "## branch-protection-context-parity — drift detected",
        "",
        "| plugin | status | expected | actual | missing | unexpected |",
        "|--------|--------|----------|--------|---------|------------|",
    ]
    for r in rows:
        expected_fmt = "`" + ", ".join(r["expected"]) + "`" if r["expected"] else "_(none)_"
        actual_fmt = "`" + ", ".join(r["actual"]) + "`" if r["actual"] else "_(none)_"
        missing_fmt = "`" + ", ".join(r["missing"]) + "`" if r["missing"] else "—"
        unexpected_fmt = "`" + ", ".join(r["unexpected"]) + "`" if r["unexpected"] else "—"
        lines.append(
            f"| `{r['plugin']}` | {r['status']} | {expected_fmt} | "
            f"{actual_fmt} | {missing_fmt} | {unexpected_fmt} |"
        )
    lines.extend(
        [
            "",
            "> Warning tier (ADR-060 §결정 5 default) — exit 0, no PR block.",
            "> Bypass channel: `hotfix-bypass:branch-protection-context-parity` label.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CFP-1807 cross-repo branch protection contexts parity warning lint"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Repo root path (default: 2 levels above script)",
    )
    parser.add_argument(
        "--claude-md",
        type=Path,
        default=None,
        help="Override CLAUDE.md path (default: <repo-root>/CLAUDE.md)",
    )
    parser.add_argument(
        "--plugins",
        nargs="+",
        default=None,
        help="Override plugin family list (default: closed-enum 8 plugin)",
    )
    args = parser.parse_args()

    claude_md_path: Path = args.claude_md or (args.repo_root / "CLAUDE.md")
    plugins: List[str] = args.plugins or list(PLUGIN_FAMILY)

    # Parse CLAUDE.md SSOT table
    expected_table = parse_claude_md_table(claude_md_path)

    # Check each plugin
    drift_rows: List[dict] = []
    skip_rows: List[dict] = []

    for slug in plugins:
        row_key = claude_md_row_key(slug)
        if not row_key or row_key not in expected_table:
            skip_rows.append(
                {
                    "plugin": slug,
                    "reason": f"no CLAUDE.md SSOT row (key='{row_key}')",
                }
            )
            continue

        expected = expected_table[row_key]
        actual, status = fetch_actual_contexts(slug)

        if status.startswith("error"):
            drift_rows.append(
                {
                    "plugin": slug,
                    "status": status,
                    "expected": expected,
                    "actual": [],
                    "missing": expected,
                    "unexpected": [],
                }
            )
            continue

        # "not_protected" — only flag drift if SSOT says it should be protected (non-empty expected)
        if status == "not_protected":
            if expected:  # SSOT says protected but actual not protected
                drift_rows.append(
                    {
                        "plugin": slug,
                        "status": "not_protected (SSOT says protected)",
                        "expected": expected,
                        "actual": [],
                        "missing": expected,
                        "unexpected": [],
                    }
                )
            # else: SSOT also says NOT PROTECTED (empty list) → parity OK
            continue

        missing, unexpected = compare(expected, actual)
        if missing or unexpected:
            drift_rows.append(
                {
                    "plugin": slug,
                    "status": "drift",
                    "expected": expected,
                    "actual": actual,
                    "missing": missing,
                    "unexpected": unexpected,
                }
            )

    # Emit output
    if drift_rows:
        print("WARNING: branch-protection-context-parity drift detected.")
        print()
        print(emit_markdown_table(drift_rows))
    else:
        print("PASS: branch-protection-context-parity — all checked plugins match SSOT.")

    if skip_rows:
        print()
        print("Skipped plugins (no CLAUDE.md SSOT row):")
        for r in skip_rows:
            print(f"  - {r['plugin']}: {r['reason']}")

    # Warning tier — always exit 0 (ADR-060 §결정 5 default)
    return 0


if __name__ == "__main__":
    sys.exit(main())
