#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-bypass-justification-marker.py
CFP-845 / ADR-024 Amendment 8 §결정 6.A.4

`[bypass-justification]` PR comment marker grep-presence lint.
hotfix-bypass:* label 부착 PR 에 대해 상단 PR comment 에 marker 존재 여부를 검증.
narrative audit trail 영속화 (grep-presence only — semantic adequacy 불가, reviewer responsibility).

grep pattern = `^\\[bypass-justification\\]` (line start anchor, case-sensitive).
scope = top-level PR comments (review comments 제외).
warning tier (exit 0 on finding — not blocking).

Usage:
  python3 check-bypass-justification-marker.py [--dry-run] [--repo OWNER/REPO]
                                               [--pr-number N]

Exit codes (ADR-060 §결정 15 3-tier):
  0 = PASS (모든 bypass PR 에 marker 존재 또는 warning 발화 — warning tier)
  1 = WARNING (marker 부재 PR 존재 — warning tier, phase 2 first iteration)
  2 = SETUP error (missing dependency / gh api auth failure)

Exempt channels (1종, §결정 6.A.4):
  hotfix-bypass:bypass-justification-marker (self-meta loop 회피 절대 invariant)

False-positive risk 명시 (Story §7.2 Spoofing):
  grep-presence 는 marker body 의 semantic 적절성을 보장하지 않음.
  body 가 비어 있거나 템플릿 그대로여도 grep PASS.
  이 경우 reviewer responsibility.

Test override env vars (bats TC mock 지원):
  CBJ_MOCK_PRS_JSON=<newline-delimited-json>  — bypass PR 목록 강제 (gh api 대체)
  CBJ_MOCK_COMMENTS_JSON=<newline-delimited-json>  — PR comments 강제 (gh api 대체)
  CBL_SKIP_ISSUE_CREATE=1  — dry-run (warning 출력만, Issue 없음)
"""

import argparse
import json
import os
import re
import subprocess
import sys


SELF_META_EXEMPT_LABEL = "hotfix-bypass:bypass-justification-marker"
BYPASS_PREFIX = "hotfix-bypass:"
MARKER_PATTERN = re.compile(r"^\[bypass-justification\]", re.MULTILINE)


def run_gh(args, capture=True):
    """gh CLI 호출 wrapper."""
    cmd = ["gh"] + args
    if capture:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True,
            encoding="utf-8", errors="replace",
        )
        return result.stdout.strip()
    else:
        subprocess.run(cmd, check=True)
        return ""


def fetch_merged_bypass_prs(repo):
    """
    repo 의 merged PR 중 hotfix-bypass:* label 이 부착된 것을 수집.
    Returns: list of {number: int, labels: [str]}
    """
    mock_var_name = "CBJ_MOCK_PRS_JSON"
    if mock_var_name in os.environ:
        mock_prs = os.environ[mock_var_name]
        prs = []
        for line in mock_prs.strip().splitlines():
            line = line.strip()
            if line:
                obj = json.loads(line)
                # dict = single PR object, list (예: '[]') = PR 없음, skip
                if isinstance(obj, dict):
                    prs.append({
                        "number": obj["number"],
                        "labels": [lbl["name"] for lbl in obj.get("labels", [])],
                    })
        return prs

    raw_output = run_gh([
        "api", "-X", "GET", "search/issues",
        "-f", f"q=repo:{repo} is:pr is:merged",
        "-f", "per_page=100",
        "--paginate",
        "--jq",
        '.items[] | select(.labels | map(.name) | any(startswith("hotfix-bypass:")))',
    ])

    prs = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            prs.append({
                "number": obj["number"],
                "labels": [lbl["name"] for lbl in obj.get("labels", [])],
            })
        except json.JSONDecodeError:
            continue
    return prs


def is_exempt_pr(labels):
    """PR 이 marker check 에서 exempt 대상인지."""
    return SELF_META_EXEMPT_LABEL in labels


def fetch_pr_comments(repo, pr_number):
    """
    PR 의 top-level comments body list 반환.
    review comments (pull_request_review_comment) 는 제외.
    Returns: list of str (comment bodies)
    """
    mock_comments_var = "CBJ_MOCK_COMMENTS_JSON"
    if mock_comments_var in os.environ:
        mock_comments = os.environ[mock_comments_var]
        bodies = []
        for line in mock_comments.strip().splitlines():
            line = line.strip()
            if line:
                obj = json.loads(line)
                # dict = single comment object, list (예: '[]') = comment 없음, skip
                if isinstance(obj, dict):
                    bodies.append(obj.get("body", ""))
        return bodies

    raw = run_gh([
        "api", "-X", "GET", f"/repos/{repo}/issues/{pr_number}/comments",
        "--paginate",
        "--jq", ".[].body",
    ])
    return raw.splitlines() if raw else []


def has_justification_marker(comment_bodies):
    """
    comment body 목록 중 `[bypass-justification]` marker 가 하나라도 있으면 True.
    grep pattern: line start anchor (^\\[bypass-justification\\]), case-sensitive.
    """
    for body in comment_bodies:
        if MARKER_PATTERN.search(body):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="[bypass-justification] PR comment marker grep-presence lint "
                    "(CFP-845 / ADR-024 Amendment 8 §결정 6.A.4)"
    )
    parser.add_argument(
        "--repo",
        default="mclayer/plugin-codeforge",
        help="GitHub repo (OWNER/REPO). default: mclayer/plugin-codeforge",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="dry-run 모드: warning 출력만, Issue 생성 없음",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        default=None,
        help="특정 PR number 만 검사 (PR-time lint 용). 미지정 시 전체 merged bypass PR 스캔.",
    )
    args = parser.parse_args()

    # gh CLI 존재 확인 (mock env key 가 set 되어 있으면 live gh 불필요)
    mock_prs_set = "CBJ_MOCK_PRS_JSON" in os.environ
    mock_comments_set = "CBJ_MOCK_COMMENTS_JSON" in os.environ
    if not mock_prs_set and not mock_comments_set:
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "[codeforge-bypass-justification-marker-error] gh CLI not installed or not in PATH",
                file=sys.stderr,
            )
            sys.exit(2)

    # Step 1: PR 목록 결정
    if args.pr_number is not None:
        # single PR mode (PR-time workflow 용)
        # labels 는 gh api 로 별도 fetch (mock 없을 때)
        if mock_prs_set:
            mock_prs_val = os.environ["CBJ_MOCK_PRS_JSON"]
            prs = []
            for line in mock_prs_val.strip().splitlines():
                line = line.strip()
                if line:
                    obj = json.loads(line)
                    # dict = single PR object, list (예: '[]') = PR 없음, skip
                    if isinstance(obj, dict):
                        prs.append({
                            "number": obj["number"],
                            "labels": [lbl["name"] for lbl in obj.get("labels", [])],
                        })
            prs = [p for p in prs if p["number"] == args.pr_number]
        else:
            try:
                raw = run_gh([
                    "api", "-X", "GET", f"/repos/{args.repo}/pulls/{args.pr_number}",
                    "--jq", '{number: .number, labels: .labels}',
                ])
                obj = json.loads(raw)
                prs = [{
                    "number": obj["number"],
                    "labels": [lbl["name"] for lbl in obj.get("labels", [])],
                }]
            except subprocess.CalledProcessError as e:
                print(
                    f"[codeforge-bypass-justification-marker-error] gh api failed: {e.stderr}",
                    file=sys.stderr,
                )
                sys.exit(2)
    else:
        # full scan mode (cron)
        try:
            prs = fetch_merged_bypass_prs(args.repo)
        except subprocess.CalledProcessError as e:
            print(
                f"[codeforge-bypass-justification-marker-error] gh api failed: {e.stderr}",
                file=sys.stderr,
            )
            sys.exit(2)

    # Step 2: bypass PR 필터 + exempt 제거
    bypass_prs = [
        pr for pr in prs
        if any(lbl.startswith(BYPASS_PREFIX) for lbl in pr["labels"])
        and not is_exempt_pr(pr["labels"])
    ]

    if not bypass_prs:
        print(
            f"check-bypass-justification-marker: PASS -- "
            f"no hotfix-bypass:* PRs found (or all exempt) in {args.repo}"
        )
        sys.exit(0)

    # Step 3: 각 PR 의 comment marker 검사
    missing_marker_prs = []
    for pr in bypass_prs:
        pr_number = pr["number"]
        try:
            comment_bodies = fetch_pr_comments(args.repo, pr_number)
        except subprocess.CalledProcessError as e:
            print(
                f"  [warning] failed to fetch comments for PR #{pr_number}: {e.stderr}",
                file=sys.stderr,
            )
            continue

        if not has_justification_marker(comment_bodies):
            missing_marker_prs.append(pr_number)
            print(f"  [bypass-justification-marker] MISSING: PR #{pr_number}")

    # Step 4: 결과 요약
    total_scanned = len(bypass_prs)
    missing_count = len(missing_marker_prs)

    if missing_count == 0:
        print(
            f"check-bypass-justification-marker: PASS -- "
            f"{total_scanned} bypass PR(s) scanned, all have [bypass-justification] marker"
        )
        sys.exit(0)
    else:
        print(
            f"check-bypass-justification-marker: WARNING -- "
            f"{missing_count}/{total_scanned} bypass PR(s) missing [bypass-justification] marker: "
            f"{missing_marker_prs}"
        )
        print(
            "  Note: semantic adequacy not verified (grep-presence only) -- "
            "reviewer responsibility (ADR-024 Amendment 8 section 6.A.4)"
        )
        # warning tier: exit 1 (not 0, not 2)
        sys.exit(1)


if __name__ == "__main__":
    main()
