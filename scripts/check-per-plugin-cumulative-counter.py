#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-per-plugin-cumulative-counter.py
CFP-845 / ADR-024 Amendment 8 §결정 6.A.3

per-plugin scope 누적 카운터 lint.
단일 plugin 이 모든 hotfix-bypass:* entry 에 걸쳐 누적 bypass 횟수를 집계.
1개 plugin 이 5개 entry × 1회씩 = 5회 분산 우회 = 체계적 회피 신호 감지.

signature = (plugin) only (entry 무관 aggregate).
dedup_unit = PR number.
window = all-time.
threshold = ≥5 reach-merged PR (보수적, ADR-024 Amendment 8 §결정 6.A.3).
plugin 식별 = wrapper plugin.json `.name` 필드 (ADR-063 mirror field SSOT).

Usage:
  python3 check-per-plugin-cumulative-counter.py [--dry-run] [--repo OWNER/REPO]
                                                  [--threshold N] [--plugin-name NAME]

Exit codes (ADR-060 §결정 15 3-tier):
  0 = PASS (threshold 미달 또는 threshold reach + Issue auto-create 성공 — warning tier)
  1 = (reserved, current scope 미사용)
  2 = SETUP error (missing dependency / gh api auth failure)

Exempt channels (3종, Change Plan §3.1 §결정 6.A.3):
  (1) hotfix-bypass:per-plugin-cumulative-counter (self-meta loop 회피 절대 invariant)
  (2) hotfix-bypass:exempt:<entry> (rare 정당 declare template)
  (3) hotfix-bypass:exempt:per-plugin (per-plugin aggregate 전용 exempt)

Test override env vars (bats TC mock 지원):
  CBL_MOCK_PRS_JSON=<newline-delimited-json>  — merged PR 목록 강제 (gh api 대체)
  CBL_MOCK_DEDUP_COUNT=<int>                  — dedup 검색 결과 total_count 강제
  CBL_SKIP_ISSUE_CREATE=1                     — Issue create 차단 (dry-run / TC mode)
"""

import argparse
import json
import os
import subprocess
import sys


SELF_META_EXEMPT_LABEL = "hotfix-bypass:per-plugin-cumulative-counter"
EXEMPT_PREFIX = "hotfix-bypass:exempt:"
EXEMPT_PER_PLUGIN_LABEL = "hotfix-bypass:exempt:per-plugin"
BYPASS_PREFIX = "hotfix-bypass:"
CARRIER_ISSUE_LABEL = "from-bypass-as-norm"
# §결정 6.A.3 empirical-source: ADR-068 Amendment 1 I-5 dimensional grounding
# threshold dimension = count, source = per-entry threshold 3 의 entry 다양성 cover
# + CFP-825 evidence cluster (per-entry 관찰 ≥3 대비 per-plugin = conservative +2)
DEFAULT_THRESHOLD = 5


def run_gh(args, capture=True):
    """gh CLI 호출 wrapper. 실패 시 CalledProcessError 발생."""
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
    mock_prs = os.environ.get("CBL_MOCK_PRS_JSON", "")
    if mock_prs:
        prs = []
        for line in mock_prs.strip().splitlines():
            line = line.strip()
            if line:
                obj = json.loads(line)
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
    """
    PR 이 per-plugin 누적 count 에서 exempt 대상인지 확인.
    exempt channels 3종 (§결정 6.A.3):
      (1) self-meta: hotfix-bypass:per-plugin-cumulative-counter 부착
      (2) entry-exempt: hotfix-bypass:exempt:* 부착
      (3) per-plugin-exempt: hotfix-bypass:exempt:per-plugin 부착
    """
    if SELF_META_EXEMPT_LABEL in labels:
        return True
    if EXEMPT_PER_PLUGIN_LABEL in labels:
        return True
    if any(lbl.startswith(EXEMPT_PREFIX) for lbl in labels):
        return True
    return False


def tally_per_plugin(prs, plugin_name):
    """
    per-plugin aggregate tally.
    PR 당 모든 hotfix-bypass:* label count 를 plugin 에 귀속.
    Returns: set of PR numbers that are non-exempt bypass PRs for this plugin.
    """
    pr_numbers = set()
    for pr in prs:
        labels = pr["labels"]
        if is_exempt_pr(labels):
            continue
        # 이 PR 에 hotfix-bypass:* 이 있으면 plugin 의 aggregate count += 1
        has_bypass = any(
            lbl.startswith(BYPASS_PREFIX) and not lbl.startswith(EXEMPT_PREFIX)
            for lbl in labels
        )
        if has_bypass:
            pr_numbers.add(pr["number"])
    return pr_numbers


def check_dedup(repo, plugin_name):
    """
    동일 plugin 의 기존 open carrier Issue 존재 여부 확인.
    Returns: True if existing Issue found (dedup → skip create).
    """
    mock_count = os.environ.get("CBL_MOCK_DEDUP_COUNT", "")
    if mock_count:
        return int(mock_count) > 0

    # title pattern: [per-plugin-counter] <plugin_name>
    search_q = (
        f'repo:{repo} is:issue is:open label:{CARRIER_ISSUE_LABEL} '
        f'"[per-plugin-counter] {plugin_name}"'
    )
    raw = run_gh([
        "api", "-X", "GET", "search/issues",
        "-f", f"q={search_q}",
        "--jq", ".total_count",
    ])
    try:
        count = int(raw.strip() or "0")
        return count > 0
    except ValueError:
        return False


def create_carrier_issue(repo, plugin_name, pr_numbers, threshold, dry_run=False):
    """carrier Issue 발의."""
    title = f"[per-plugin-counter] {plugin_name} {len(pr_numbers)}+ reach (threshold={threshold})"
    pr_list_str = ", ".join(f"#{n}" for n in sorted(pr_numbers))
    body = (
        f"## Per-Plugin Cumulative Bypass Counter — {plugin_name}\n\n"
        f"**Plugin**: `{plugin_name}`\n\n"
        f"**Aggregated merged PRs** ({len(pr_numbers)}+): {pr_list_str}\n\n"
        f"## Context\n\n"
        f"Plugin `{plugin_name}` has attached `hotfix-bypass:*` labels to {len(pr_numbers)} "
        f"merged PRs across all entries — per-plugin aggregate threshold ≥{threshold} reached.\n"
        f"This signals systematic bypass pattern across multiple exception channels.\n\n"
        f"## Follow-up Evaluation (ADR-024 Amendment 8 §결정 6.A.3)\n\n"
        f"Review the following 3-axis evaluation for this plugin:\n\n"
        f"1. **Threshold recalibration**: Is threshold={threshold} appropriate? "
        f"Adjust if this plugin represents legitimate repeated exception use.\n\n"
        f"2. **Blocking-on-merge tier escalation**: If mutation risk confirmed, evaluate "
        f"escalation per ADR-060 4-tier promotion gate (Story-2 #861 evidence-gated).\n\n"
        f"3. **Plugin governance review**: Review overall bypass pattern for `{plugin_name}` "
        f"across all entry namespaces to identify systemic avoidance patterns.\n\n"
        f"---\n"
        f"Source: `scripts/check-per-plugin-cumulative-counter.py` "
        f"(CFP-845 / ADR-024 Amendment 8 §결정 6.A.3)\n"
        f"ADR: [ADR-024](docs/adr/ADR-024-story-scoped-branch-policy.md)"
    )

    if dry_run or os.environ.get("CBL_SKIP_ISSUE_CREATE", "") == "1":
        print(f"[DRY-RUN] would create Issue: {title}")
        print(f"  PR list: {sorted(pr_numbers)}")
        return

    run_gh([
        "api", "-X", "POST", f"/repos/{repo}/issues",
        "-f", f"title={title}",
        "-f", f"body={body}",
        "-f", f"labels[]={CARRIER_ISSUE_LABEL}",
    ])
    print(f"[per-plugin-counter] Issue created: {title}")


def main():
    parser = argparse.ArgumentParser(
        description="per-plugin scope 누적 bypass 카운터 lint (CFP-845 / ADR-024 Amendment 8 §결정 6.A.3)"
    )
    parser.add_argument(
        "--repo",
        default="mclayer/plugin-codeforge",
        help="GitHub repo (OWNER/REPO). default: mclayer/plugin-codeforge",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="dry-run 모드: Issue 실제 생성 없이 결과 출력만",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"per-plugin aggregate reach threshold. default: {DEFAULT_THRESHOLD} (ADR-024 Amd 8 §결정 6.A.3)",
    )
    parser.add_argument(
        "--plugin-name",
        default="plugin-codeforge",
        help="plugin name (wrapper plugin.json .name SSOT). default: plugin-codeforge",
    )
    args = parser.parse_args()

    # gh CLI 존재 확인
    if not os.environ.get("CBL_MOCK_PRS_JSON", ""):
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "[codeforge-per-plugin-counter-error] gh CLI not installed or not in PATH",
                file=sys.stderr,
            )
            sys.exit(2)

    # Step 1: merged PR 수집
    try:
        prs = fetch_merged_bypass_prs(args.repo)
    except subprocess.CalledProcessError as e:
        print(
            f"[codeforge-per-plugin-counter-error] gh api failed: {e.stderr}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Step 2: per-plugin aggregate tally (exempt 제외)
    pr_numbers = tally_per_plugin(prs, args.plugin_name)

    if not pr_numbers:
        print(
            f"check-per-plugin-cumulative-counter: PASS -- "
            f"no hotfix-bypass:* signatures found for plugin={args.plugin_name} in {args.repo}"
        )
        sys.exit(0)

    count = len(pr_numbers)
    print(f"  per-plugin aggregate: {args.plugin_name} ({count}/{args.threshold})")

    # Step 3: threshold check
    if count < args.threshold:
        print(
            f"check-per-plugin-cumulative-counter: PASS -- "
            f"below threshold: {args.plugin_name} ({count}/{args.threshold})"
        )
        sys.exit(0)

    # Step 4: dedup check
    if check_dedup(args.repo, args.plugin_name):
        print(
            f"  dedup: existing open carrier Issue for {args.plugin_name} -- skip create"
        )
        print(
            f"check-per-plugin-cumulative-counter: PASS -- "
            f"threshold reached but carrier Issue already open (dedup)"
        )
        sys.exit(0)

    # Step 5: create carrier Issue
    create_carrier_issue(args.repo, args.plugin_name, pr_numbers, args.threshold, dry_run=args.dry_run)

    print(
        f"check-per-plugin-cumulative-counter: PASS -- "
        f"threshold reached: {args.plugin_name} ({count}/{args.threshold}), "
        f"carrier Issue created"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
