"""
scripts/lib/check_parallel_work_sentinel.py
CFP-967 / ADR-073 Amendment 2 — Parallel work sentinel 3 polling mode SSOT

기능:
  3 polling mode dispatch — parallel race detection mechanical wire.
  memory rule 6 (title-based search, CFP-953 incident) + rule 7 (Epic state poll,
  CFP-946 incident) + HEAD compare sibling commits (self-demo lane evidence).

Mode enum (argparse --mode):
  title-search:
    Input:  env CFP_CONTEXT (예: "CFP-967") + optional --epic-id
    Output: exit 0 + stdout JSON {"matches": [{"number": int, "title": str, "labels": [...]}]}
            exit 1: reserved
            exit 2: SETUP error (gh CLI 미인증 / dependency absent)
  epic-state-poll:
    Input:  --epic-id (required)
    Output: exit 0 + stdout JSON {"epic_state": str, "siblings": [...], "freshness_age_sec": int}
            exit 2: SETUP error
  head-compare-sibling-commits:
    Input:  env CFP_PRIOR_SHA (required) + optional --branch (default origin/main)
    Output: exit 0 + stdout JSON {"delta_commits": [...], "parallel_detected": bool}
            exit 2: SETUP error

BYPASS:
  BYPASS_PARALLEL_WORK_SENTINEL=1 — unconditional skip, exit 0 + audit marker

Graceful degradation 3 fail-mode (ADR-027 Amd 2 precedent):
  api_quota_exceeded: HTTP 403/429 → local git log fallback + stderr marker
  hook_self_fail:     syntax error → noop + stderr warning (ADR-038 Amd 1 §결정 8)
  stale_label_grace:  5min grace boundary marker

Exit-code 3-tier (ADR-060 §결정 15):
  0: PASS
  1: reserved (not used currently)
  2: SETUP error (dependency absent / auth failed)

Test seam:
  CFP967_GH_MOCK_RESPONSE=<fixture path> — gh CLI mock
  CFP967_GIT_LOG_MOCK=<fixture path>     — git log mock
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Optional

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_NAME = "check_parallel_work_sentinel"
CFP_PATTERN = re.compile(r"\bCFP-\d+\b")
BYPASS_ENV = "BYPASS_PARALLEL_WORK_SENTINEL"
GH_MOCK_ENV = "CFP967_GH_MOCK_RESPONSE"
GIT_LOG_MOCK_ENV = "CFP967_GIT_LOG_MOCK"
STALE_GRACE_SEC = 300  # 5min — ADR-073 §결정 1-C sustained polling


# ---------------------------------------------------------------------------
# Exit helpers
# ---------------------------------------------------------------------------
def _exit_pass(payload: dict) -> None:
    print(json.dumps(payload))
    sys.exit(0)


def _exit_setup_error(msg: str) -> None:
    print(json.dumps({"error": msg, "exit_code": 2}), file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# gh CLI / git invocation helpers
# ---------------------------------------------------------------------------
def _run_gh(args: list[str], mock_env: str = GH_MOCK_ENV) -> tuple[int, str]:
    """Run gh CLI or return mock fixture if CFP967_GH_MOCK_RESPONSE is set."""
    mock_path = os.environ.get(mock_env)
    if mock_path:
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                return 0, f.read()
        except FileNotFoundError:
            return 2, json.dumps({"error": f"mock file not found: {mock_path}"})
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout if result.returncode == 0 else result.stderr


def _run_git_log(prior_sha: str, branch: str = "origin/main") -> tuple[int, str]:
    """Run git log or return mock fixture."""
    mock_path = os.environ.get(GIT_LOG_MOCK_ENV)
    if mock_path:
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                return 0, f.read()
        except FileNotFoundError:
            return 2, f"mock file not found: {mock_path}"
    # git fetch origin first (sustained polling §결정 1-C)
    subprocess.run(["git", "fetch", "origin"], capture_output=True)
    result = subprocess.run(
        ["git", "log", "--format=%H %ci %s", f"{prior_sha}..{branch}"],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout


def _check_gh_auth() -> bool:
    """Check gh CLI authentication (exit 2 SETUP error if not authed)."""
    mock_path = os.environ.get(GH_MOCK_ENV)
    if mock_path:
        # mock mode — skip auth check
        return True
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Mode: title-search (memory rule 6 — CFP-953 incident carrier)
# ---------------------------------------------------------------------------
def mode_title_search(epic_id: Optional[str] = None) -> None:
    """
    title-search mode: gh issue list --search in:title + whole-word CFP regex filter.
    Carrier: memory rule 6 (title-based search 의무, CFP-953 label-based search miss incident).
    """
    if not _check_gh_auth():
        _exit_setup_error("gh CLI not authenticated — run: gh auth login")

    cfp_context = os.environ.get("CFP_CONTEXT", "")
    search_fragment = cfp_context if cfp_context else ""

    # Build gh issue list args
    gh_args = [
        "issue", "list",
        "--search", f'"{search_fragment}" in:title' if search_fragment else "CFP- in:title",
        "--state", "all",
        "--json", "number,title,labels,closedAt",
        "--limit", "50",
    ]

    rc, raw = _run_gh(gh_args)

    if rc == 403:
        # api_quota_exceeded graceful degradation
        _handle_api_quota_exceeded("title-search", search_fragment)
        return
    if rc == 429:
        print(
            json.dumps({
                "matches": [],
                "degradation": "api_quota_exceeded",
                "marker": "[parallel-work-sentinel-api-failed]",
                "fallback": "rate-limited (429) — retry later",
            })
        )
        sys.exit(0)
    if rc != 0:
        # non-auth non-quota error — try graceful
        _handle_api_quota_exceeded("title-search", search_fragment)
        return

    try:
        issues = json.loads(raw) if raw.strip() else []
    except json.JSONDecodeError:
        issues = []

    # F-CR-967-1: API error dict defense — gh API may return {"message":..,"status":"403"}
    # instead of a list when quota/auth errors slip through rc==0 (mock seam rc=0 path).
    if not isinstance(issues, list):
        if isinstance(issues, dict):
            status_str = str(issues.get("status", ""))
            if status_str in ("403", "429"):
                _handle_api_quota_exceeded("title-search", search_fragment)
                return
        # Any non-list unexpected payload — degrade gracefully
        issues = []

    # whole-word regex filter (CFP-953 false-positive 차단)
    matches = []
    for issue in issues:
        title = issue.get("title", "")
        number = issue.get("number", 0)
        labels = [lbl.get("name", "") if isinstance(lbl, dict) else str(lbl) for lbl in issue.get("labels", [])]
        if search_fragment and not CFP_PATTERN.search(title):
            # If context given, ensure title has a CFP-\d+ pattern
            continue
        matches.append({"number": number, "title": title, "labels": labels})

    _exit_pass({"matches": matches})


# ---------------------------------------------------------------------------
# Mode: epic-state-poll (memory rule 7 — CFP-946 incident carrier)
# ---------------------------------------------------------------------------
def mode_epic_state_poll(epic_id: str) -> None:
    """
    epic-state-poll mode: fetch Epic state + siblings from scope_manifest.
    Carrier: memory rule 7 (Epic 진행 중 polling 의무, CFP-946 Epic close miss incident).
    """
    if not _check_gh_auth():
        _exit_setup_error("gh CLI not authenticated — run: gh auth login")

    gh_args = [
        "issue", "view", str(epic_id),
        "--json", "state,closedAt,closedBy,labels,body",
    ]

    rc, raw = _run_gh(gh_args)

    if rc == 403 or rc == 429:
        _handle_api_quota_exceeded("epic-state-poll", f"epic#{epic_id}")
        return
    if rc != 0:
        _handle_api_quota_exceeded("epic-state-poll", f"epic#{epic_id}")
        return

    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        data = {}

    epic_state = data.get("state", "UNKNOWN")
    body = data.get("body", "")

    # Parse scope_manifest from Epic body (<!-- scope_manifest --> block)
    siblings = _parse_siblings_from_body(body)

    # Freshness: current time vs last fetch (session cache stale assumption §결정 1-C)
    freshness_age_sec = 0  # real-time fetch — age = 0

    _exit_pass({
        "epic_state": epic_state,
        "siblings": siblings,
        "freshness_age_sec": freshness_age_sec,
    })


def _parse_siblings_from_body(body: str) -> list[dict]:
    """Extract sibling Story references from Epic body scope_manifest block."""
    siblings = []
    # Look for <!-- scope_manifest --> block or plain CFP-\d+ references
    cfp_matches = CFP_PATTERN.findall(body)
    seen = set()
    for cfp_ref in cfp_matches:
        if cfp_ref not in seen:
            seen.add(cfp_ref)
            siblings.append({"cfp": cfp_ref})
    return siblings


# ---------------------------------------------------------------------------
# Mode: head-compare-sibling-commits (self-demo lane evidence)
# ---------------------------------------------------------------------------
def mode_head_compare(branch: str = "origin/main") -> None:
    """
    head-compare-sibling-commits mode: git log delta + parallel branch detection.
    """
    prior_sha = os.environ.get("CFP_PRIOR_SHA", "")
    if not prior_sha:
        _exit_setup_error(
            "CFP_PRIOR_SHA env var required for head-compare-sibling-commits mode"
        )

    rc, raw = _run_git_log(prior_sha, branch)

    if rc != 0:
        # git fetch/log failure — graceful degradation
        print(
            json.dumps({
                "delta_commits": [],
                "parallel_detected": False,
                "degradation": "git_fetch_failed",
                "marker": "[parallel-work-sentinel-api-failed]",
            })
        )
        sys.exit(0)

    delta_commits = []
    parallel_detected = False

    for line in raw.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split(" ", 2)
        sha = parts[0] if len(parts) > 0 else ""
        ci = parts[1] if len(parts) > 1 else ""
        msg = parts[2] if len(parts) > 2 else ""
        delta_commits.append({"sha": sha, "time": ci, "msg": msg})
        # parallel detection: any commit message containing CFP-\d+ pattern
        if CFP_PATTERN.search(msg):
            parallel_detected = True

    # stale_label_grace: check if prior_sha is older than STALE_GRACE_SEC
    _check_stale_grace(prior_sha)

    _exit_pass({
        "delta_commits": delta_commits,
        "parallel_detected": parallel_detected,
    })


def _check_stale_grace(prior_sha: str) -> None:
    """Check if prior_sha timestamp is older than STALE_GRACE_SEC — emit marker if stale."""
    # F-CR-967-2: skip stale check in mock-context (CFP967_GIT_LOG_MOCK set) to prevent
    # fixture SHA age false-positive stderr pollution (existing mock seam pattern — ADR-061).
    if os.environ.get(GIT_LOG_MOCK_ENV):
        return None
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ci", "-1", prior_sha],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return
        # timestamp check via python datetime
        from datetime import datetime, timezone
        ts_str = result.stdout.strip()
        # git log format: "2026-05-19 01:00:00 +0900"
        # normalize to parseable format
        ts_str_norm = ts_str.replace(" +", "+").replace(" -", "-")
        parts = ts_str.rsplit(" ", 1)
        if len(parts) == 2:
            dt_str, tz_str = parts
            # simple epoch via git show --format=%ct
            result2 = subprocess.run(
                ["git", "log", "--format=%ct", "-1", prior_sha],
                capture_output=True,
                text=True,
            )
            if result2.returncode == 0 and result2.stdout.strip():
                commit_epoch = int(result2.stdout.strip())
                now_epoch = int(time.time())
                age_sec = now_epoch - commit_epoch
                if age_sec > STALE_GRACE_SEC:
                    print(
                        f"[parallel-work-poll-freshness-mismatch] prior_sha={prior_sha} "
                        f"age={age_sec}s > {STALE_GRACE_SEC}s grace — verify-before-trust step required",
                        file=sys.stderr,
                    )
    except Exception:
        pass  # graceful — stale check advisory only


# ---------------------------------------------------------------------------
# Graceful degradation: api_quota_exceeded
# ---------------------------------------------------------------------------
def _handle_api_quota_exceeded(mode: str, context: str) -> None:
    """
    api_quota_exceeded fail-mode (ADR-027 Amd 2 precedent):
    gh api 403/429 → local git log -50 grep fallback + stderr marker.
    """
    print(
        f"[parallel-work-sentinel] WARNING: gh API call failed for mode={mode} context={context}. "
        "Falling back to local git log.",
        file=sys.stderr,
    )
    print("[parallel-work-sentinel-api-failed]", file=sys.stderr)

    # Local fallback: git log -50 | grep CFP-\d+
    try:
        result = subprocess.run(
            ["git", "log", "-50", "--format=%s"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            cfp_refs = []
            for line in result.stdout.splitlines():
                matches = CFP_PATTERN.findall(line)
                cfp_refs.extend(matches)
            print(
                json.dumps({
                    "matches": [{"cfp": ref} for ref in set(cfp_refs)],
                    "degradation": "api_quota_exceeded",
                    "marker": "[parallel-work-sentinel-api-failed]",
                    "fallback": "local git log -50 grep",
                })
            )
            sys.exit(0)
    except Exception:
        pass

    # Last resort — empty response, non-blocking
    print(
        json.dumps({
            "matches": [],
            "degradation": "api_quota_exceeded",
            "marker": "[parallel-work-sentinel-api-failed]",
            "fallback": "unavailable",
        })
    )
    sys.exit(0)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    # BYPASS check — unconditional (ADR-024 hotfix-bypass family, audit-trailed)
    if os.environ.get(BYPASS_ENV) == "1":
        print(
            json.dumps({
                "bypass": True,
                "marker": "[hotfix-bypass] BYPASS_PARALLEL_WORK_SENTINEL=1 invoked",
                "audit_comment": "bypass invoked",
            })
        )
        print("bypass invoked")
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="CFP-967 parallel work sentinel polling (ADR-073 Amendment 2)",
        prog="check_parallel_work_sentinel",
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["title-search", "epic-state-poll", "head-compare-sibling-commits"],
        help="Polling mode (ADR-073 Amendment 2 §결정 1-A transition trigger enum)",
    )
    parser.add_argument(
        "--epic-id",
        default=None,
        help="Epic issue number (required for epic-state-poll mode)",
    )
    parser.add_argument(
        "--branch",
        default="origin/main",
        help="Branch for head-compare mode (default: origin/main)",
    )

    args = parser.parse_args()

    if args.mode == "title-search":
        mode_title_search(epic_id=args.epic_id)
    elif args.mode == "epic-state-poll":
        if not args.epic_id:
            _exit_setup_error("--epic-id is required for epic-state-poll mode")
        mode_epic_state_poll(epic_id=args.epic_id)
    elif args.mode == "head-compare-sibling-commits":
        mode_head_compare(branch=args.branch)
    else:
        _exit_setup_error(f"unknown mode: {args.mode}")


if __name__ == "__main__":
    main()
