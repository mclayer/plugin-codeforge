"""CFP-1844 — Orchestrator spawn-prompt-fact verify warning lint (Wave 2 mechanical wire).

Orchestrator 가 subagent spawn prompt 안에서 사실 단언을 할 때 (counter / version /
SHA / verify-result / file-existence) `verified-via:` annotation 없이 단언하는 패턴을
warning emit. ADR-082 Amendment 34 sub-scope 1-W + ADR-073 Amendment 18 paired sibling
mechanical wire.

5 fact category (C1-C5):
  C1 counter: e.g. "144 entries" / "111 hotfix-bypass labels" / "20 hits"
  C2 version: e.g. "v2.86" / "v6.10.0"
  C3 SHA: 40-char hex commit SHA OR `PRE-SPAWN-ORIGIN-MAIN-SHA:` block
  C4 verify-result: e.g. "sha256 PASS" / "byte-identical OK" / "MERGED" / "CLEAN"
  C5 file-existence: e.g. "<path>.md 존재" / "line count: 391"

Tier: warning (ADR-060 §결정 5 default — first introduction, exit 0).
Owner ADR: ADR-082 Amendment 34 sub-scope 1-W (carrier) + ADR-073 Amendment 18 (paired).
Bypass: `hotfix-bypass:orchestrator-spawn-prompt-fact-verify` label.

Implementation notes:
  - ADR-061 Amendment 3 §결정 11 정합 — line-by-line scan (`text.splitlines()`)
    + anchored simple regex + per-entry scan cap 50 line (ReDoS-safe).
  - per-match scan window = 5 line (configurable via --window).
  - annotation accept pattern: `verified-via:\\s+\\S+` within window.
  - drift = match without nearby annotation → warning emit (markdown table).

Exit codes:
  0 — PASS (no drift) OR FAIL-as-warning (drift detected, markdown table emitted)
  2 — usage error (e.g., input file unreadable)

Usage:
  python scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py --input <file|->
  echo "<text>" | python scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py --input -
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Windows Git Bash / cp949 console — force UTF-8 stdout/stderr (CFP-418 evidence inherit).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

# Per-entry scan cap (ADR-061 Amendment 3 §결정 11 boundary detection).
DEFAULT_SCAN_CAP = 50
DEFAULT_WINDOW = 5

# 5 fact category anchored simple regex (line-by-line scan target).
# Each pattern intentionally narrow (no nested quantifier, no alternation overlap).
PATTERNS = [
    (
        "C1-counter",
        re.compile(
            r"\b(\d{2,})\s+(entries|entry|labels|label|hotfix-bypass|hits|hit|occurrences|items)\b",
            re.IGNORECASE,
        ),
        "counter assertion (e.g., '144 entries') — add `verified-via: grep -c ...` annotation",
    ),
    (
        "C2-version",
        re.compile(r"\bv\d+\.\d+(?:\.\d+)?\b"),
        "version assertion (e.g., 'v2.86') — add `verified-via: grep ^version ...` annotation",
    ),
    (
        "C3-SHA",
        re.compile(r"\b[0-9a-f]{40}\b|PRE-SPAWN-ORIGIN-MAIN-SHA:\s*[0-9a-f]+"),
        "SHA assertion (40-char hex) — add `verified-via: git rev-parse ...` annotation",
    ),
    (
        "C4-verify-result",
        re.compile(
            r"\b(sha256 PASS|byte-identical (?:OK|PASS)|verify PASS|MERGED|CLEAN|drift 0)\b"
        ),
        "verify-result assertion — add `verified-via: <method>` annotation",
    ),
    (
        "C5-file-existence",
        re.compile(
            r"\b\S+\.(?:md|yml|yaml|sh|py|json|ts|tsx|toml)\s+(?:존재|absent|present|exists)\b"
            r"|line count:\s*\d+"
        ),
        "file-existence assertion — add `verified-via: ls / wc -l ...` annotation",
    ),
]

# Annotation accept pattern (verbatim text `verified-via:`).
ANNOTATION_RE = re.compile(r"verified-via:\s*\S+", re.IGNORECASE)

# Self-source skip — when lint scans this very file or registry definitions,
# pattern matches are expected meta-references, not actual unverified assertions.
SELF_SOURCE_PATTERNS = [
    "check_orchestrator_spawn_prompt_fact_verify",
    "orchestrator-spawn-prompt-fact-verify",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Orchestrator spawn-prompt-fact verify lint")
    p.add_argument(
        "--input",
        required=True,
        help="Input file path, or '-' for stdin",
    )
    p.add_argument(
        "--window",
        type=int,
        default=DEFAULT_WINDOW,
        help=f"Per-match scan window in lines (default {DEFAULT_WINDOW})",
    )
    p.add_argument(
        "--scan-cap",
        type=int,
        default=DEFAULT_SCAN_CAP,
        help=f"Per-entry scan cap in lines (default {DEFAULT_SCAN_CAP})",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress markdown header when no drift detected",
    )
    return p.parse_args()


def read_input(spec: str) -> str:
    if spec == "-":
        return sys.stdin.read()
    path = Path(spec)
    if not path.is_file():
        print(f"[error] input file not found: {spec}", file=sys.stderr)
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"[error] cannot read input: {spec} ({exc})", file=sys.stderr)
        sys.exit(2)


def has_nearby_annotation(lines: List[str], idx: int, window: int) -> bool:
    """Check if `verified-via:` annotation appears within [idx-window, idx+window]."""
    start = max(0, idx - window)
    end = min(len(lines), idx + window + 1)
    for j in range(start, end):
        if ANNOTATION_RE.search(lines[j]):
            return True
    return False


def is_self_source_context(lines: List[str], idx: int, window: int) -> bool:
    """Skip matches inside our own registry/script definitions."""
    start = max(0, idx - window)
    end = min(len(lines), idx + window + 1)
    for j in range(start, end):
        for marker in SELF_SOURCE_PATTERNS:
            if marker in lines[j]:
                return True
    return False


def scan(text: str, window: int, scan_cap: int) -> List[Tuple[int, str, str, str]]:
    """Return list of (line_no, category, match_text, suggestion)."""
    lines = text.splitlines()
    findings: List[Tuple[int, str, str, str]] = []
    per_category_count: dict = {}

    for idx, line in enumerate(lines):
        for category, regex, suggestion in PATTERNS:
            cnt = per_category_count.get(category, 0)
            if cnt >= scan_cap:
                continue
            m = regex.search(line)
            if not m:
                continue
            if has_nearby_annotation(lines, idx, window):
                continue
            if is_self_source_context(lines, idx, window):
                continue
            findings.append((idx + 1, category, m.group(0), suggestion))
            per_category_count[category] = cnt + 1

    return findings


def emit_markdown(findings: List[Tuple[int, str, str, str]], quiet: bool) -> None:
    if not findings:
        if not quiet:
            print("[orchestrator-spawn-prompt-fact-verify] PASS — no unverified fact assertions detected.")
        return

    print("## orchestrator-spawn-prompt-fact-verify (warning)")
    print()
    print(
        "ADR-082 Amendment 34 sub-scope 1-W + ADR-073 Amendment 18 — "
        "spawn-prompt-fact discipline (verified-via annotation 의무)."
    )
    print()
    print("| line | category | match | suggestion |")
    print("|------|----------|-------|------------|")
    for line_no, category, match_text, suggestion in findings:
        # markdown-escape pipes inside match_text
        safe = match_text.replace("|", "\\|")
        print(f"| {line_no} | {category} | `{safe}` | {suggestion} |")
    print()
    print(
        "_Bypass: attach `hotfix-bypass:orchestrator-spawn-prompt-fact-verify` label "
        "with `### Bypass reason` PR body section (ADR-024 Amendment 16 §결정 6.A.8)._"
    )


def main() -> int:
    args = parse_args()
    text = read_input(args.input)
    findings = scan(text, args.window, args.scan_cap)
    emit_markdown(findings, args.quiet)
    # warning-tier: always exit 0 (ADR-060 §결정 5 default).
    return 0


if __name__ == "__main__":
    sys.exit(main())
