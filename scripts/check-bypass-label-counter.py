#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-bypass-label-counter.py
CFP-825 / ADR-024 Amendment 6 §결정 6.A.2

per-(plugin, label) signature 누적 사용 카운터 lint.
hotfix-bypass:<entry> per-entry namespace label 이 merged PR 에 ≥3 reach 시
carrier Issue 자동 발의 (dedup: (plugin, label) signature per open Issue).

Usage:
  python3 check-bypass-label-counter.py [--dry-run] [--repo OWNER/REPO] [--threshold N]

Exit codes (ADR-060 §결정 15 3-tier):
  0 = PASS (threshold 미달 또는 threshold reach + Issue auto-create 성공 — warning tier)
  1 = (reserved, current scope 미사용)
  2 = SETUP error (missing dependency / gh api auth failure)

Exempt channels (2종, Change Plan §3.3):
  (1) hotfix-bypass:bypass-label-counter (self-meta loop 회피 absolute invariant)
  (2) hotfix-bypass:exempt:<entry> (rare 정당 declare template)

Dedup unit: PR number (merged PR 고유 idempotent).
Measurement window: all-time (rolling window = stale pollution carry-forward 차단 불가 — Change Plan §2).

Threshold empirical source: CFP-770/771/819 corpus 5+ 사용 evidence cluster
  - CFP-770/771 PR #788: claude-md-line-cap + wording-dictionary 2 label admin merge
  - CFP-819 PR #823: wording-dictionary cosmetic 7 occurrences
  - CFP-786/801/795: unit-tests pre-existing pytest 부재
  threshold=3 은 evidence cluster 관찰값 ≥3 에 기반 (ADR-068 Amendment 1 I-5 dimensional empirical grounding).

PAT scope requirement (OQ-1 / Change Plan §3.3 EC-3):
  CODEFORGE_CROSS_REPO_PAT 는 issues:write + repo:read (contents:read) scope 필요.
  workflow permissions: block 에 issues: write + contents: read 명시 (ADR-066 단일 PAT).

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


SELF_META_EXEMPT_LABEL = "hotfix-bypass:bypass-label-counter"
EXEMPT_PREFIX = "hotfix-bypass:exempt:"
BYPASS_PREFIX = "hotfix-bypass:"
CARRIER_ISSUE_LABEL = "bypass-label-counter"


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
    # Test override: CBL_MOCK_PRS_JSON — 줄바꿈 구분 JSON 배열 (bats stub 지원)
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

    # gh api search/issues — merged PR with any hotfix-bypass:* label
    # --paginate 로 전체 수집 (window=all-time)
    query = f"repo:{repo} is:pr is:merged label:hotfix-bypass:bypass-label-counter"
    # hotfix-bypass:* wildcard 는 GitHub search API 미지원 — label:bypass-label-counter 로
    # 대신 전체 PR 목록에서 hotfix-bypass: prefix label 필터링
    # NOTE: GitHub search API 는 label: wildcard 미지원.
    # 전략: is:pr is:merged 전체에서 hotfix-bypass: prefix label 가진 것 수집.
    # --jq 로 서버 측 필터 적용 (label 이름 prefix 확인).
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
    """PR 이 exempt 대상인지 확인 (2종 exempt channel)."""
    # (1) self-meta loop 회피: hotfix-bypass:bypass-label-counter 부착
    if SELF_META_EXEMPT_LABEL in labels:
        return True
    # (2) 명시적 exempt template: hotfix-bypass:exempt:* 부착
    if any(lbl.startswith(EXEMPT_PREFIX) for lbl in labels):
        return True
    return False


def tally_signatures(prs):
    """
    per-(plugin, label) signature tally.
    Returns: {(plugin, label): set(pr_numbers)}
    exempt PR 은 자동 제외.
    """
    tally = {}
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
            key = lbl  # label name 자체가 signature key
            if key not in tally:
                tally[key] = set()
            tally[key].add(pr_number)

    return tally


def check_dedup(repo, label):
    """
    동일 (plugin, label) signature 의 기존 open carrier Issue 존재 여부 확인.
    Returns: True if existing Issue found (dedup → skip create), False otherwise.
    """
    # Test override: CBL_MOCK_DEDUP_COUNT
    mock_count = os.environ.get("CBL_MOCK_DEDUP_COUNT", "")
    if mock_count:
        return int(mock_count) > 0

    signature = f"{repo}::{label}"
    # title pattern 검색: [bypass-counter] <signature>
    search_q = f'repo:{repo} is:issue is:open label:{CARRIER_ISSUE_LABEL} "[bypass-counter] {signature}"'
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


def create_carrier_issue(repo, label, pr_numbers, dry_run=False):
    """
    carrier Issue 발의.
    dry_run=True 시 실제 create 없이 print 만.
    """
    signature = f"{repo}::{label}"
    pr_list_str = ", ".join(f"#{n}" for n in sorted(pr_numbers))
    title = f"[bypass-counter] {signature} {len(pr_numbers)}+ reach"
    body = (
        f"## Bypass Label Counter - {label}\n\n"
        f"**Signature**: `{signature}`\n\n"
        f"**Reaching merged PRs** ({len(pr_numbers)}+): {pr_list_str}\n\n"
        f"## Context\n\n"
        f"per-entry namespace `{label}` label attached to {len(pr_numbers)} merged PRs.\n"
        f"threshold=3 reached (ADR-024 Amendment 6 section 6.A.2 ratchet rule).\n\n"
        f"## Action\n\n"
        f"exception -> norm mutation (bypass-as-norm mutation) risk accumulation review required.\n"
        f"Subsequent carrier decides blocking-on-merge tier escalation.\n\n"
        f"---\n"
        f"Source: `scripts/check-bypass-label-counter.py` (CFP-825 / ADR-024 Amendment 6)\n"
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
    print(f"[bypass-counter] Issue created: {title}")


def main():
    parser = argparse.ArgumentParser(
        description="bypass-label per-entry namespace 누적 사용 카운터 lint (CFP-825)"
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
        default=3,
        help="per-(plugin,label) signature reach threshold. default: 3 (ADR-024 Amd 6 §결정 6.A.2)",
    )
    args = parser.parse_args()

    # gh CLI 존재 확인
    if not os.environ.get("CBL_MOCK_PRS_JSON", ""):
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[codeforge-bypass-label-counter-error] gh CLI not installed or not in PATH", file=sys.stderr)
            sys.exit(2)

    # Step 1: merged PR 수집
    try:
        prs = fetch_merged_bypass_prs(args.repo)
    except subprocess.CalledProcessError as e:
        print(f"[codeforge-bypass-label-counter-error] gh api failed: {e.stderr}", file=sys.stderr)
        sys.exit(2)

    # Step 2: signature tally (exempt 제외)
    tally = tally_signatures(prs)

    if not tally:
        print(f"check-bypass-label-counter: PASS -- no hotfix-bypass:* signatures found in {args.repo}")
        sys.exit(0)

    # Step 3: threshold check + dedup + Issue create
    issues_created = 0
    issues_skipped_dedup = 0
    issues_below_threshold = 0

    for label, pr_numbers in sorted(tally.items()):
        count = len(pr_numbers)
        if count < args.threshold:
            issues_below_threshold += 1
            print(f"  below threshold: {label} ({count}/{args.threshold})")
            continue

        # threshold reached -- dedup check
        if check_dedup(args.repo, label):
            issues_skipped_dedup += 1
            print(f"  dedup: existing open carrier Issue for {args.repo}::{label} -- skip create")
            continue

        # no existing Issue -- create
        create_carrier_issue(args.repo, label, pr_numbers, dry_run=args.dry_run)
        issues_created += 1

    # Step 4: 결과 요약
    total_signatures = len(tally)
    print(
        "check-bypass-label-counter: PASS -- "
        f"{total_signatures} signature(s) scanned, "
        f"{issues_created} carrier Issue(s) created, "
        f"{issues_skipped_dedup} dedup skip(s), "
        f"{issues_below_threshold} below threshold (threshold={args.threshold})"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
