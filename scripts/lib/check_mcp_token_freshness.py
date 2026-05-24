"""
scripts/lib/check_mcp_token_freshness.py
CFP-1366 / ADR-073 Amendment 8 §결정 1-K/1-L — MCP token freshness pre-check Wave 2 mechanical wire

Heuristic: PR body / diff 안 MCP tool reference (`mcp__plugin_*` / `mcp__github__*`) 발견 시,
paired `mcp_token_freshness_verified:` field 또는 `verified-via: /mcp` annotation presence-grep.
Documentation context (ADR / Change Plan / Story / inter-plugin-contract) 안 reference 는 exempt.

Exit codes:
  0: PASS (no MCP usage claim OR claim + freshness annotation)
  1: WARN (MCP usage claim found, freshness annotation missing)
  2: SETUP error

BYPASS:
  BYPASS_MCP_TOKEN_FRESHNESS=1 — unconditional skip

CFP-1348 Amendment 8 Sentinel: CFP-1146 W5-S15+S16+S17 6 parallel dispatch token expiry
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# MCP tool reference patterns (active usage, not doc references)
MCP_USAGE_PATTERNS = [
    r"\bmcp__plugin_atlassian_atlassian__\w+",
    r"\bmcp__github__\w+",
    r"\bmcp__plugin_\w+__\w+",
]

# Doc-context patterns (exempt — talking about MCP, not using)
DOC_CONTEXT_PATTERNS = [
    r"`mcp__\w+`",         # inline code-span (markdown reference)
    r"\bADR-\d+",          # ADR cross-ref text
    r"\bChange Plan\b",
    r"deferred-followup",  # registry doc
]

# Freshness annotation patterns
FRESHNESS_PATTERNS = [
    r"mcp_token_freshness_verified:\s*(?:true|True|yes)",
    r"verified-via:\s*/mcp",
    r"verified-via:\s*session age",
    r"verified-via:\s*mcp token",
    r"mcp_session_age_estimate_min:\s*\d+",
]


def has_active_mcp_usage(text: str) -> bool:
    """
    Determine if text contains active MCP tool usage (not just documentation reference).
    """
    for pat in MCP_USAGE_PATTERNS:
        for m in re.finditer(pat, text):
            # Check context window around match — if dominant doc context, skip
            start = max(0, m.start() - 100)
            end = min(len(text), m.end() + 100)
            context = text[start:end]
            doc_score = sum(1 for dp in DOC_CONTEXT_PATTERNS if re.search(dp, context))
            # If 2+ doc indicators in window, treat as doc-only
            if doc_score >= 2:
                continue
            return True
    return False


def has_freshness_annotation(text: str) -> bool:
    """Check freshness annotation paired with MCP usage."""
    for pat in FRESHNESS_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def check_text(text: str) -> tuple[int, str]:
    """
    Returns (exit_code, message).
    """
    if not has_active_mcp_usage(text):
        return 0, "PASS: no active MCP tool usage detected"
    if has_freshness_annotation(text):
        return 0, "PASS: MCP usage + freshness annotation paired"
    return 1, (
        "WARN: active MCP tool usage found but no freshness annotation "
        "(ADR-073 Amd 8 §결정 1-L mcp_token_freshness_verified field)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="mcp-token-freshness-precheck CI lint (CFP-1366)"
    )
    parser.add_argument("--input-file", type=str)
    parser.add_argument("--text", type=str)
    args = parser.parse_args()

    if os.environ.get("BYPASS_MCP_TOKEN_FRESHNESS") == "1":
        print("[BYPASS] BYPASS_MCP_TOKEN_FRESHNESS=1 -- skip")
        return 0

    if args.input_file:
        path = Path(args.input_file)
        if not path.is_file():
            print(f"[SETUP] input file not found: {args.input_file}", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8", errors="replace")
    elif args.text is not None:
        text = args.text
    else:
        print("[SETUP] either --input-file or --text required", file=sys.stderr)
        return 2

    code, msg = check_text(text)
    if code == 0:
        print(msg)
    else:
        print(msg, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
