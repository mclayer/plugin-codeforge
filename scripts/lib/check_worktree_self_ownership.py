"""
scripts/lib/check_worktree_self_ownership.py
CFP-1366 / ADR-073 Amendment 3 §결정 1-D — Worktree self-ownership verify Wave 2 mechanical wire

ADR-073 Amendment 3 path-based 3-tuple verify primitive 의 CI lint sentinel:
  (a) cwd ↔ worktree path equality
  (b) HEAD lineage ↔ session reflog membership
  (c) git worktree list + reflog 2-source AND ownership

Workflow context (CI runtime) heuristic — PR body / commit message 안 `parallel_session_conflict`
또는 동형 ownership claim (`parallel_session` / `cross_session_collision` / `stand_down_recommended`)
발화 시 paired `verified-via:` annotation presence-grep.

Exit codes:
  0: PASS (claim 부재 OR claim + verified-via paired)
  1: WARN (claim 발견 + verified-via 부재)
  2: SETUP error (script invocation 오류)

BYPASS:
  BYPASS_WORKTREE_SELF_OWNERSHIP=1 — unconditional skip, exit 0 + audit marker

CFP-689 Amendment 3 Sentinel: 2026-05-19~20 KST single session 3 occurrences
  (CFP-1026 STAND-DOWN + CFP-681 cfp-1014 dup + CFP-681 ArchitectPL 00b7d8a mis-flag)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Conflict / ownership claim keywords (case-insensitive scan)
CLAIM_KEYWORDS = [
    r"parallel_session_conflict",
    r"parallel_session\b",
    r"cross_session_collision",
    r"stand_down_recommended",
    r"external_work_detected",
    r"sibling_session_conflict",
]

# verified-via annotation patterns (paired evidence)
VERIFIED_VIA_PATTERNS = [
    r"verified-via:\s*git worktree list",
    r"verified-via:\s*git reflog",
    r"verified-via:\s*git rev-parse",
    r"verified-via:\s*self-ownership\s+verify",
]


def has_claim(text: str) -> bool:
    """PR body / commit message 안 conflict claim keyword 발견 여부."""
    for kw in CLAIM_KEYWORDS:
        if re.search(kw, text, re.IGNORECASE):
            return True
    return False


def has_verified_via(text: str) -> bool:
    """verified-via annotation paired 여부."""
    for pat in VERIFIED_VIA_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def check_text(text: str) -> tuple[int, str]:
    """
    Returns (exit_code, message).
      0: PASS (no claim OR claim+verified)
      1: WARN (claim found, verified-via missing)
    """
    if not has_claim(text):
        return 0, "PASS: no ownership claim detected"
    if has_verified_via(text):
        return 0, "PASS: claim + verified-via paired"
    return 1, "WARN: ownership claim found but verified-via annotation missing (ADR-073 Amd 3 §결정 1-D)"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="worktree-self-ownership-verify CI lint (CFP-1366)"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Path to text file to scan (PR body / commit message)",
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Direct text input (alternative to --input-file)",
    )
    args = parser.parse_args()

    if os.environ.get("BYPASS_WORKTREE_SELF_OWNERSHIP") == "1":
        print("[BYPASS] BYPASS_WORKTREE_SELF_OWNERSHIP=1 -- skip")
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
