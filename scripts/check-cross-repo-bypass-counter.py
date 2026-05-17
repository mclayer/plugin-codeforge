#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-cross-repo-bypass-counter.py
CFP-845 / ADR-024 Amendment 8 §결정 6.A.5

cross-repo (3-repo) bypass counter extension lint.
wrapper + internal-docs + marketplace 3 repo 에 걸쳐
per-(repo, plugin, label) signature 누적 집계.

threshold = per-(repo, plugin, label) signature 누적 ≥3 reach-merged PR.
aggregate trigger = 3 repo 동시 reach 시 단일 carrier Issue 발의.
dedup_unit = (repo, PR number) 2-tuple (cross-repo PR number 충돌 회피).
single PAT = CODEFORGE_CROSS_REPO_PAT (ADR-066 reuse — 신규 secret 0건).
carrier Issue repository = mclayer/plugin-codeforge (wrapper governance owner SSOT, ADR-013).

Usage:
  python3 check-cross-repo-bypass-counter.py [--dry-run]
                                             [--threshold N]
                                             [--repos REPO1,REPO2,REPO3]

Exit codes (ADR-060 §결정 15 3-tier):
  0 = PASS (threshold 미달 또는 threshold reach + Issue auto-create 성공 — warning tier)
  1 = (reserved, current scope 미사용)
  2 = SETUP error (missing dependency / gh api auth failure)

Exempt channels (2종, §결정 6.A.5):
  (1) hotfix-bypass:cross-repo-bypass-counter (self-meta loop 회피)
  (2) hotfix-bypass:exempt:<entry> (rare 정당 declare template)

Test override env vars (bats TC mock 지원):
  CRC_MOCK_PRS_JSON_<REPO_SLUG>=<newline-delimited-json>
    e.g. CRC_MOCK_PRS_JSON_PLUGIN=... / CRC_MOCK_PRS_JSON_DOCS=... / CRC_MOCK_PRS_JSON_MARKETPLACE=...
  CBL_MOCK_DEDUP_COUNT=<int>  — dedup 검색 결과 total_count 강제
  CBL_SKIP_ISSUE_CREATE=1     — Issue create 차단 (dry-run / TC mode)
"""

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict


SELF_META_EXEMPT_LABEL = "hotfix-bypass:cross-repo-bypass-counter"
EXEMPT_PREFIX = "hotfix-bypass:exempt:"
BYPASS_PREFIX = "hotfix-bypass:"
CARRIER_ISSUE_LABEL = "from-bypass-as-norm"
# §결정 6.A.5 empirical-source: ADR-068 Amendment 1 I-5 dimensional grounding
# threshold dimension = count, source = per-entry threshold 3 (CFP-825) 동일 적용
# (cross-repo 는 단일 repo 대비 동일 pattern 이 3 repo 에 전파된 경우 — noise floor 동일)
DEFAULT_THRESHOLD = 3
DEFAULT_REPOS = [
    "mclayer/plugin-codeforge",
    "mclayer/codeforge-internal-docs",
    "mclayer/marketplace",
]
CARRIER_REPO = "mclayer/plugin-codeforge"

# repo → env slug 매핑 (bats mock key 용)
REPO_SLUG_MAP = {
    "mclayer/plugin-codeforge": "PLUGIN",
    "mclayer/codeforge-internal-docs": "DOCS",
    "mclayer/marketplace": "MARKETPLACE",
}


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
    # Test override: CRC_MOCK_PRS_JSON_<SLUG>
    slug = REPO_SLUG_MAP.get(repo, repo.replace("/", "_").upper())
    mock_var_name = f"CRC_MOCK_PRS_JSON_{slug}"
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
    """PR 이 cross-repo count 에서 exempt 대상인지."""
    if SELF_META_EXEMPT_LABEL in labels:
        return True
    if any(lbl.startswith(EXEMPT_PREFIX) for lbl in labels):
        return True
    return False


def tally_signatures(repo, prs):
    """
    per-(repo, plugin, label) signature tally.
    Returns: {(repo, label): set(pr_numbers)}
    plugin = 고정 (단일 repo 단일 plugin context — 확장 시 plugin field 주입)
    """
    tally = defaultdict(set)
    for pr in prs:
        labels = pr["labels"]
        pr_number = pr["number"]
        if is_exempt_pr(labels):
            continue
        for lbl in labels:
            if not lbl.startswith(BYPASS_PREFIX):
                continue
            if lbl.startswith(EXEMPT_PREFIX):
                continue
            key = (repo, lbl)
            tally[key].add(pr_number)
    return dict(tally)


def check_dedup(carrier_repo, label):
    """carrier Issue 중복 확인."""
    mock_count = os.environ.get("CBL_MOCK_DEDUP_COUNT", "")
    if mock_count:
        return int(mock_count) > 0

    search_q = (
        f'repo:{carrier_repo} is:issue is:open label:{CARRIER_ISSUE_LABEL} '
        f'"[cross-repo-counter] {label}"'
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


def create_carrier_issue(carrier_repo, label, repo_tallies, threshold, dry_run=False):
    """
    carrier Issue 발의 (aggregate = mclayer/plugin-codeforge, ADR-013).
    repo_tallies: {repo: set(pr_numbers)}
    """
    total_count = sum(len(v) for v in repo_tallies.values())
    repo_summary = "; ".join(
        f"{repo}: {sorted(prs)}" for repo, prs in sorted(repo_tallies.items())
    )
    title = f"[cross-repo-counter] {label} {total_count}+ reach across {len(repo_tallies)} repos"
    body = (
        f"## Cross-Repo Bypass Counter — {label}\n\n"
        f"**Label**: `{label}`\n\n"
        f"**Repos reaching threshold** ({threshold}+):\n\n"
    )
    for repo, prs in sorted(repo_tallies.items()):
        pr_list_str = ", ".join(f"#{n}" for n in sorted(prs))
        body += f"- `{repo}`: {len(prs)} PRs — {pr_list_str}\n"
    body += (
        f"\n## Context\n\n"
        f"Label `{label}` has accumulated ≥{threshold} reach-merged PRs in "
        f"{len(repo_tallies)} repos simultaneously.\n"
        f"Aggregate signal: {repo_summary}\n\n"
        f"## Follow-up Evaluation (ADR-024 Amendment 8 §결정 6.A.5)\n\n"
        f"1. **Cross-repo pattern review**: Is the same bypass justification propagating "
        f"systematically across multiple repos (wrapper + docs + marketplace)?\n\n"
        f"2. **Threshold recalibration**: Adjust threshold={threshold} per repo if signal "
        f"represents expected cross-repo coordination rather than systemic bypass.\n\n"
        f"3. **Blocking-on-merge escalation**: If cross-repo mutation risk confirmed, "
        f"evaluate escalation per ADR-060 4-tier gate (Story-2 #861 carrier).\n\n"
        f"---\n"
        f"Source: `scripts/check-cross-repo-bypass-counter.py` "
        f"(CFP-845 / ADR-024 Amendment 8 §결정 6.A.5)\n"
        f"ADR: [ADR-024](docs/adr/ADR-024-story-scoped-branch-policy.md)"
    )

    if dry_run or os.environ.get("CBL_SKIP_ISSUE_CREATE", "") == "1":
        print(f"[DRY-RUN] would create Issue: {title}")
        for repo, prs in sorted(repo_tallies.items()):
            print(f"  {repo}: {sorted(prs)}")
        return

    run_gh([
        "api", "-X", "POST", f"/repos/{carrier_repo}/issues",
        "-f", f"title={title}",
        "-f", f"body={body}",
        "-f", f"labels[]={CARRIER_ISSUE_LABEL}",
    ])
    print(f"[cross-repo-counter] Issue created: {title}")


def main():
    parser = argparse.ArgumentParser(
        description="cross-repo (3-repo) bypass counter extension lint "
                    "(CFP-845 / ADR-024 Amendment 8 §결정 6.A.5)"
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
        help=f"per-(repo, label) signature reach threshold. default: {DEFAULT_THRESHOLD}",
    )
    parser.add_argument(
        "--repos",
        default=",".join(DEFAULT_REPOS),
        help="comma-separated repo list (OWNER/REPO). default: 3 codeforge family repos",
    )
    args = parser.parse_args()

    repos = [r.strip() for r in args.repos.split(",") if r.strip()]

    # gh CLI 존재 확인 (mock env key 가 set 되어 있으면 live gh 불필요 — key existence 기반)
    needs_gh = not any(
        f"CRC_MOCK_PRS_JSON_{REPO_SLUG_MAP.get(r, r.replace('/', '_').upper())}" in os.environ
        for r in repos
    )
    if needs_gh:
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "[codeforge-cross-repo-counter-error] gh CLI not installed or not in PATH",
                file=sys.stderr,
            )
            sys.exit(2)

    # Step 1: 각 repo 의 merged bypass PR 수집 + signature tally
    all_tallies = {}  # {(repo, label): set(pr_numbers)}
    for repo in repos:
        try:
            prs = fetch_merged_bypass_prs(repo)
        except subprocess.CalledProcessError as e:
            print(
                f"[codeforge-cross-repo-counter-error] gh api failed for {repo}: {e.stderr}",
                file=sys.stderr,
            )
            sys.exit(2)
        tally = tally_signatures(repo, prs)
        all_tallies.update(tally)

    if not all_tallies:
        print(
            "check-cross-repo-bypass-counter: PASS -- "
            "no hotfix-bypass:* signatures found across all repos"
        )
        sys.exit(0)

    # Step 2: per-label aggregate (label → {repo: set(pr_numbers)})
    # label 별로 몇 repo 가 threshold 에 도달했는지 집계
    label_repo_map = defaultdict(dict)  # {label: {repo: set(pr_numbers)}}
    for (repo, label), pr_numbers in all_tallies.items():
        label_repo_map[label][repo] = pr_numbers

    # Step 3: threshold check per (repo, label) + aggregate trigger
    issues_created = 0
    issues_skipped = 0
    below_threshold = 0

    for label, repo_prs in sorted(label_repo_map.items()):
        # threshold reach 한 repo 목록
        reaching_repos = {
            repo: prs
            for repo, prs in repo_prs.items()
            if len(prs) >= args.threshold
        }

        if not reaching_repos:
            below_threshold += len(repo_prs)
            for repo, prs in repo_prs.items():
                print(f"  below threshold: {label} in {repo} ({len(prs)}/{args.threshold})")
            continue

        # 1+ repo 가 threshold reach — aggregate trigger
        # dedup 확인 (carrier Issue 은 mclayer/plugin-codeforge 에 발의)
        if check_dedup(CARRIER_REPO, label):
            issues_skipped += 1
            print(f"  dedup: existing open carrier Issue for {label} -- skip create")
            continue

        create_carrier_issue(
            CARRIER_REPO, label, reaching_repos, args.threshold, dry_run=args.dry_run
        )
        issues_created += 1

    # Step 4: 결과 요약
    total_labels = len(label_repo_map)
    print(
        f"check-cross-repo-bypass-counter: PASS -- "
        f"{total_labels} label(s) scanned across {len(repos)} repos, "
        f"{issues_created} carrier Issue(s) created, "
        f"{issues_skipped} dedup skip(s)"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
