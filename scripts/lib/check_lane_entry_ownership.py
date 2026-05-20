#!/usr/bin/env python3
"""lane-entry sentinel ownership verify (CFP-1057, ADR-085 §결정 3 Wave 2).

ADR-073 Amendment 2 polling enum 4번째 source `active_sessions_check`
cross-ref. `gh pr list --search "head:<branch>" --state open` ownership
verify primitive. Multi-session collaboration protocol pre-lane-spawn
mechanical guard.

Wave 2 mechanical lint (declarative-only-Wave-1 promoted by CFP-1057).
Warning tier. Exit codes:
  0 = clear ownership (PASS) OR no existing PR on branch (advisory)
  1 = ownership conflict detected (FAIL — different session has open PR on branch)
  2 = invocation error / gh API failure (graceful degradation per ADR-073 Amd 2)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--branch", required=True, help="branch name to verify ownership")
    p.add_argument("--repo", default=None, help="owner/repo (default: gh CLI auto-detect)")
    p.add_argument("--expected-author", default=None, help="expected author login (default: current gh user)")
    return p.parse_args()


def run_gh(args: list[str]) -> tuple[int, str, str]:
    if not shutil.which("gh"):
        return 2, "", "gh CLI not found"
    try:
        r = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 2, "", "gh CLI timeout (30s)"
    except OSError as e:
        return 2, "", f"gh CLI exec failed: {e}"


def main() -> int:
    args = parse_args()
    cmd = ["pr", "list", "--state", "open", "--search", f"head:{args.branch}",
           "--json", "number,headRefName,author,createdAt,headRepository"]
    if args.repo:
        cmd.extend(["--repo", args.repo])
    code, out, err = run_gh(cmd)
    if code == 2:
        print(f"::warning::lane-entry-ownership-verify graceful degradation — {err}")
        return 2
    if code != 0:
        print(f"::warning::gh pr list failed (exit {code}): {err}")
        return 2
    try:
        prs = json.loads(out) if out.strip() else []
    except json.JSONDecodeError as e:
        print(f"::warning::gh output malformed JSON: {e}")
        return 2
    if not prs:
        print(f"[advisory] no open PR found for head:{args.branch} — clear to spawn")
        return 0
    # determine expected author
    expected = args.expected_author
    if not expected:
        c2, o2, _ = run_gh(["api", "user", "--jq", ".login"])
        if c2 == 0 and o2.strip():
            expected = o2.strip()
    conflicts = [p for p in prs if expected and p.get("author", {}).get("login") != expected]
    if conflicts:
        msg = ", ".join(f"#{p['number']} by {p.get('author', {}).get('login', '?')}" for p in conflicts)
        print(f"[fail] ownership conflict on head:{args.branch} — other session(s) open PR: {msg}")
        return 1
    if expected:
        own = ", ".join(f"#{p['number']}" for p in prs if p.get("author", {}).get("login") == expected)
        print(f"[pass] own PR on head:{args.branch} (author={expected}): {own}")
    else:
        prs_summary = ", ".join(f"#{p['number']} by {p.get('author', {}).get('login', '?')}" for p in prs)
        print(f"[advisory] PR(s) on head:{args.branch}: {prs_summary} (expected author unknown — graceful degradation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
