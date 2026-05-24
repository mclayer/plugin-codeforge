#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1421 / ADR-111 §결정 5 — Issue body design content Confluence anchor link 의무 lint
#
# Scope: Issue body / PR body 안 design doc 4 mirror 대상 (ADR / Living Architecture
#        / Change Plan / Domain Knowledge) 참조 시 Confluence anchor link 동반
#        grep-presence 검증 (warning-tier, ADR-060 §결정 5 첫 도입 default).
#
# Detection regex:
#   - Design content inline indicator (ADR-111 §결정 1 4 mirror 대상 정합):
#       (?:ADR-\d+|docs/architecture|docs/change-plans|docs/domain-knowledge)
#   - Confluence link presence (ADR-100 §결정 1 mirror authoritative readable):
#       mclayer\.atlassian\.net|atlassian\.net/wiki
#
# Output:
#   - warning if design content inline 있는데 Confluence link 부재
#   - exit 0 always (warning tier — ADR-060 evidence-enforceable framework)
#
# Usage:
#   python3 check_issue_design_content_confluence_link.py            # env mode (GH_TOKEN + ISSUE_NUMBER)
#   python3 check_issue_design_content_confluence_link.py --body-file FILE  # local file mode
#   python3 check_issue_design_content_confluence_link.py --help
#
# ADR-061 §결정 1 — Python SSOT (heredoc 금지)
# ADR-060 §결정 5 — warning-tier (exit 0 default)
# CFP-1393 패턴 — Windows cp949 cross-platform encoding (sys.stdout.reconfigure)
# CFP-1369/1398 패턴 — ASCII status indicators ([OK] / [WARN] / [INFO])

import argparse
import os
import re
import subprocess
import sys

# Windows console 호환 — UTF-8 강제 (CFP-1393 패턴)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_NAME = "[check-issue-design-content-confluence-link]"

# ── bypass env 확인 ──────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_ISSUE_DESIGN_CONTENT_CONFLUENCE_LINK", "")
if BYPASS_ENV == "1":
    print(f"{SCRIPT_NAME} BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── Detection patterns (ADR-111 §결정 1 + §결정 5 정합) ────────────────────────
# Design content inline indicator: 4 mirror 대상 (ADR / Living Architecture / Change Plan / Domain Knowledge)
DESIGN_CONTENT_RE = re.compile(
    r"(?:ADR-\d+|docs/architecture|docs/change-plans|docs/domain-knowledge)",
    re.IGNORECASE,
)
# Confluence link presence
CONFLUENCE_LINK_RE = re.compile(
    r"mclayer\.atlassian\.net|atlassian\.net/wiki",
    re.IGNORECASE,
)


def parse_args(argv):
    """CLI args parse — env mode (default) vs --body-file mode."""
    parser = argparse.ArgumentParser(
        prog="check_issue_design_content_confluence_link.py",
        description=(
            "CFP-1421 / ADR-111 §결정 5 — Issue body design content "
            "Confluence anchor link 의무 lint (warning tier)"
        ),
    )
    parser.add_argument(
        "--body-file",
        type=str,
        default=None,
        help="Local file path for body text (test / offline mode). "
        "Default: fetch via gh CLI using ISSUE_NUMBER env.",
    )
    parser.add_argument(
        "--issue-number",
        type=str,
        default=None,
        help="Issue or PR number (override ISSUE_NUMBER env).",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="org/repo (override GH_REPO env / gh default).",
    )
    return parser.parse_args(argv)


def fetch_body_via_gh(issue_number, repo):
    """gh CLI 로 Issue / PR body fetch.

    Returns body text (str) or None if fetch fails.
    Tries `gh issue view` then falls back to `gh pr view`.
    """
    if not issue_number:
        print(
            f"{SCRIPT_NAME} [SETUP-ERROR] ISSUE_NUMBER env 또는 --issue-number 인수 필요",
            file=sys.stderr,
        )
        return None
    if not os.environ.get("GH_TOKEN"):
        print(
            f"{SCRIPT_NAME} [INFO] GH_TOKEN env 미설정 — gh CLI 인증 상태에 의존",
            file=sys.stderr,
        )
    # 1) issue view 시도
    base_cmd = ["gh"]
    if repo:
        base_cmd.extend(["--repo", repo])
    for sub in (["issue", "view"], ["pr", "view"]):
        cmd = list(base_cmd)
        # gh issue view <N> --json body --jq .body
        cmd_full = ["gh"] + sub + [str(issue_number), "--json", "body", "--jq", ".body"]
        if repo:
            cmd_full = (
                ["gh", "--repo", repo]
                + sub
                + [str(issue_number), "--json", "body", "--jq", ".body"]
            )
        try:
            result = subprocess.run(
                cmd_full,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(
                f"{SCRIPT_NAME} [INFO] {' '.join(cmd_full[:3])} fetch 실패: {e}",
                file=sys.stderr,
            )
            continue
    print(
        f"{SCRIPT_NAME} [INFO] gh issue/pr view 모두 실패 — body fetch 불가",
        file=sys.stderr,
    )
    return None


def check_body(body_text, source_label):
    """Body text 검사 — design content inline 있는데 Confluence link 부재 시 [WARN].

    Returns warn_count (int).
    """
    if not body_text or not body_text.strip():
        print(
            f"{SCRIPT_NAME} [INFO] {source_label}: body 비어있음 — skip",
            file=sys.stderr,
        )
        return 0

    design_matches = DESIGN_CONTENT_RE.findall(body_text)
    if not design_matches:
        print(
            f"{SCRIPT_NAME} [OK] {source_label}: design content inline 0건 — Confluence link 의무 미발효",
            file=sys.stderr,
        )
        return 0

    confluence_present = bool(CONFLUENCE_LINK_RE.search(body_text))
    if confluence_present:
        print(
            f"{SCRIPT_NAME} [OK] {source_label}: design content {len(design_matches)}건 + "
            f"Confluence link present — cross-link discipline 정합 (ADR-111 §결정 5)",
            file=sys.stderr,
        )
        return 0

    # Warning case
    unique_indicators = sorted(set(design_matches))
    print(
        f"{SCRIPT_NAME} [WARN] {source_label}: design content inline {len(design_matches)}건 "
        f"(unique: {unique_indicators}) detected but Confluence anchor link 부재 — "
        f"cross-link discipline 위배 (ADR-111 §결정 5). "
        f"권장: Confluence anchor (https://mclayer.atlassian.net/wiki/...) 동반 부착.",
        file=sys.stderr,
    )
    return 1


def main():
    args = parse_args(sys.argv[1:])

    # body text 획득
    if args.body_file:
        try:
            with open(args.body_file, "r", encoding="utf-8", errors="replace") as f:
                body_text = f.read()
            source_label = f"file:{args.body_file}"
        except (OSError, IOError) as e:
            print(
                f"{SCRIPT_NAME} [SETUP-ERROR] --body-file 읽기 실패 ({args.body_file}): {e}",
                file=sys.stderr,
            )
            sys.exit(2)
    else:
        # env mode — gh CLI fetch
        issue_number = args.issue_number or os.environ.get("ISSUE_NUMBER", "")
        repo = args.repo or os.environ.get("GH_REPO", "")
        body_text = fetch_body_via_gh(issue_number, repo)
        if body_text is None:
            # fetch fail = warning-tier graceful skip (PR merge 미차단)
            print(
                f"{SCRIPT_NAME} [INFO] body fetch 불가 — skip (warning-tier exit 0)",
                file=sys.stderr,
            )
            sys.exit(0)
        source_label = f"issue/pr #{issue_number}"

    warn_count = check_body(body_text, source_label)

    if warn_count > 0:
        print(
            f"{SCRIPT_NAME} WARN: {warn_count}건 경고 감지 (warning-tier — PR merge 미차단)",
            file=sys.stderr,
        )
    else:
        print(f"{SCRIPT_NAME} PASS: 경고 0건", file=sys.stderr)

    # warning-tier — 경고 수에 무관하게 exit 0 (ADR-060 §결정 5)
    sys.exit(0)


if __name__ == "__main__":
    main()
