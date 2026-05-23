#!/usr/bin/env python3
"""active_sessions[] field presence-grep (CFP-1057, ADR-085 §결정 2 Wave 2).

Story Issue body `<!-- active_sessions -->` HTML comment block OR
Story file frontmatter `active_sessions:` array presence verify.
5-tuple schema: git_identity / worktree_path / entry_phase /
entered_at_kst (ADR-079 KST +09:00 ISO 8601) / last_heartbeat_kst.

Wave 2 mechanical lint (declarative-only-Wave-1 promoted by CFP-1057).
Warning tier (continue-on-error: true via workflow). Exit codes:
  0 = present (PASS) OR field absent + Story not adopting (advisory)
  1 = present but malformed (FAIL)
  2 = invocation error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ACTIVE_SESSIONS_BLOCK_RE = re.compile(
    r"<!--\s*active_sessions\s*-->\s*(.+?)\s*<!--\s*/\s*active_sessions\s*-->",
    re.DOTALL,
)
FRONTMATTER_KEY_RE = re.compile(r"^active_sessions:\s*(\[\]|\n.*?)(?=^\w)", re.MULTILINE | re.DOTALL)
REQUIRED_FIELDS = {"git_identity", "worktree_path", "entry_phase", "entered_at_kst", "last_heartbeat_kst"}
KST_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+09:00$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--story-file", type=Path, help="Story file path (frontmatter active_sessions: array)")
    p.add_argument("--issue-body", type=str, help="Issue body text (<!-- active_sessions --> HTML comment block)")
    return p.parse_args()


def check_story_frontmatter(path: Path) -> tuple[int, str]:
    if not path.exists():
        return 0, f"[advisory] Story file not found: {path} — skip (file may not yet exist)"
    text = path.read_text(encoding="utf-8")
    # frontmatter block
    if not text.startswith("---"):
        return 0, "[advisory] Story file missing frontmatter delimiter — skip"
    fm_end = text.find("\n---", 4)
    if fm_end == -1:
        return 0, "[advisory] Story file frontmatter unterminated — skip"
    fm = text[4:fm_end]
    if "active_sessions:" not in fm:
        return 0, "[advisory] active_sessions: field absent in frontmatter (Story not adopting protocol — Wave 1 backward-compat default [])"
    return 0, "[pass] active_sessions: field present in frontmatter"


def check_issue_body(body: str) -> tuple[int, str]:
    match = ACTIVE_SESSIONS_BLOCK_RE.search(body)
    if not match:
        return 0, "[advisory] <!-- active_sessions --> HTML comment block absent in Issue body (Story not adopting protocol — Wave 1 backward-compat)"
    raw = match.group(1).strip()
    if not raw or raw == "[]":
        return 0, "[pass] active_sessions block present but empty (Wave 1 declarative)"
    try:
        sessions = json.loads(raw)
    except json.JSONDecodeError as e:
        return 1, f"[fail] active_sessions block present but malformed JSON: {e}"
    if not isinstance(sessions, list):
        return 1, f"[fail] active_sessions must be JSON array, got {type(sessions).__name__}"
    for i, s in enumerate(sessions):
        if not isinstance(s, dict):
            return 1, f"[fail] active_sessions[{i}] must be dict, got {type(s).__name__}"
        missing = REQUIRED_FIELDS - set(s.keys())
        if missing:
            return 1, f"[fail] active_sessions[{i}] missing required fields: {sorted(missing)}"
        for kst_field in ("entered_at_kst", "last_heartbeat_kst"):
            if not KST_ISO_RE.match(str(s[kst_field])):
                return 1, f"[fail] active_sessions[{i}].{kst_field} must match ISO 8601 KST +09:00 format (ADR-079)"
    return 0, f"[pass] active_sessions block present with {len(sessions)} entry/entries (5-tuple schema valid)"


def main() -> int:
    args = parse_args()
    if args.story_file:
        code, msg = check_story_frontmatter(args.story_file)
    elif args.issue_body is not None:
        code, msg = check_issue_body(args.issue_body)
    else:
        print("::error::--story-file OR --issue-body required", file=sys.stderr)
        return 2
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
