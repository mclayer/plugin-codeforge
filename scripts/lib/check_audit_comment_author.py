#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/lib/check_audit_comment_author.py
CFP-2591 Phase 2 / ADR-060 §결정 6 — hotfix-bypass audit comment author-verify lint (warning tier)

hotfix-bypass audit comment (`[hotfix-bypass-audit] ...`) 는 GitHub Actions bot 이 발의해야
tamper-evident 하다 (사람이 손으로 audit comment 를 위조하면 bypass 감사 무력화). 본 lint 가
audit-tagged comment 의 author.login 이 `github-actions[bot]` 인지 검증한다.

판정 (ID-3, mutation-survivor-0):
  · tagged = body.strip().startswith("[hotfix-bypass-audit]")
  · tagged 0개                              → FAIL exit 1 (audit absent)
  · tagged 중 author != github-actions[bot] → FAIL exit 1 (human-spoof)
  · tagged ≥1 AND 전부 github-actions[bot]  → PASS exit 0
  (bot → PASS / human → FAIL / absent → FAIL)

honest forcing ceiling: exit 1 = advisory 표식 — 실 차단은 워크플로 continue-on-error 소관.

Usage:
  python3 check_audit_comment_author.py check [--comments-json <path>]   # 없으면 stdin
  python3 check_audit_comment_author.py selftest                          # 5 embedded case (bot/human/absent + flat-login/user.login spoof)

Input JSON (gh shape 둘 다 수용):
  [{"author": {"login": "..."}, "body": "..."}, ...]
  {"comments": [{"author": {"login": "..."}, "body": "..."}, ...]}

Exit codes:
  0 = PASS (tagged ≥1 AND 전부 bot)
  1 = FAIL (absent / human-spoof) OR selftest 불일치
  2 = SETUP error (JSON parse 실패 / 파일 read 실패)

ADR refs: ADR-060 §결정 6 / ADR-060 §결정 8 (audit comment schema) / ADR-061 / ADR-127
"""

import argparse
import json
import sys

# Windows cp949 인코딩 문제 회피: stdout/stderr 를 UTF-8 강제 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


AUDIT_TAG = "[hotfix-bypass-audit]"
BOT_LOGIN = "github-actions[bot]"


def _comment_author(comment):
    """comment dict 에서 author.login 전용 추출 (gh author-shape). 부재/타 shape → 빈 문자열.

    CFP-2594 Phase 2 (Stage 3 flip P3) — flat `login` + `user.login` fallback 제거.
    author-verify 는 gh `{author: {login}}` shape 만 신뢰한다 (PASS-set 축소, 0-regression,
    fail-open 불가): 타 shape(flat `login` / `user.login`) 는 "" 반환 → spoof 판정 → FAIL.
    상위 워크플로가 `--jq '{author: {login: .user.login}}'` 로 author-shape 정규화 후 넘긴다.
    ADR-060 §결정 6."""
    if not isinstance(comment, dict):
        return ""
    author = comment.get("author")
    if isinstance(author, dict):
        return str(author.get("login") or "")
    return ""


def _comment_body(comment):
    if not isinstance(comment, dict):
        return ""
    return str(comment.get("body") or "")


def _normalize_comments(data):
    """gh shape 둘 다 → comment list 로 정규화."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        comments = data.get("comments")
        if isinstance(comments, list):
            return comments
    return []


def evaluate(comments):
    """
    comment list 를 판정. Returns (passed: bool, reason: str, tagged_count: int, spoof_authors: list).

    tagged 0개 → FAIL(absent). tagged 중 non-bot 1+ → FAIL(human-spoof). 전부 bot → PASS.
    """
    tagged = [c for c in comments if _comment_body(c).strip().startswith(AUDIT_TAG)]
    if not tagged:
        return (False, "audit comment absent (tagged 0개)", 0, [])

    spoof = [_comment_author(c) for c in tagged if _comment_author(c) != BOT_LOGIN]
    if spoof:
        return (
            False,
            "human-spoof (audit comment author != %s): %s" % (BOT_LOGIN, ", ".join(spoof)),
            len(tagged),
            spoof,
        )
    return (True, "OK (tagged %d, 전부 %s)" % (len(tagged), BOT_LOGIN), len(tagged), [])


# ─────────────────────── 서브커맨드: check ───────────────────────────────────────

def cmd_check(args):
    # 입력 로드 (파일 or stdin)
    try:
        if args.comments_json:
            with open(args.comments_json, encoding="utf-8") as f:
                raw = f.read()
        else:
            raw = sys.stdin.read()
    except OSError as e:
        print(
            "[codeforge-audit-comment-author-infra-error] check-audit-comment-author: "
            "입력 read 실패: %s" % e,
            file=sys.stderr,
        )
        return 2

    try:
        data = json.loads(raw) if raw.strip() else []
    except json.JSONDecodeError as e:
        print(
            "[codeforge-audit-comment-author-infra-error] check-audit-comment-author: "
            "JSON parse 실패: %s" % e,
            file=sys.stderr,
        )
        return 2

    comments = _normalize_comments(data)
    passed, reason, tagged_count, _spoof = evaluate(comments)

    if passed:
        print("check-audit-comment-author: PASS — %s" % reason)
        return 0

    print("::warning::check-audit-comment-author: FAIL — %s" % reason)
    print(
        "check-audit-comment-author: FAIL (tagged=%d — bot→PASS / human→FAIL / absent→FAIL; warning tier)"
        % tagged_count
    )
    return 1


# ─────────────────────── 서브커맨드: selftest (anti-theater) ─────────────────────

_SELFTEST_CASES = [
    # (name, comments, expected_pass)
    (
        "bot-tagged → PASS",
        [{"author": {"login": BOT_LOGIN}, "body": "[hotfix-bypass-audit] PR=1 reason=x"}],
        True,
    ),
    (
        "human-tagged → FAIL (spoof)",
        [{"author": {"login": "mccho-mclayer"}, "body": "[hotfix-bypass-audit] PR=1 reason=x"}],
        False,
    ),
    (
        "absent → FAIL",
        [{"author": {"login": BOT_LOGIN}, "body": "just a normal comment, no audit tag"}],
        False,
    ),
    # CFP-2594 Phase 2 (Stage 3 flip P3) — ADDED-1/2: fallback 제거 lockstep.
    #   bot login 이 author-shape 밖(flat login / user.login)이면 이제 PASS 하지 않는다
    #   (PASS-set 축소 — _comment_author 가 author.login 전용, 타 shape → "" → spoof → FAIL).
    (
        "flat login spoof → FAIL (P3 fallback 제거 — author-shape 전용)",
        [{"login": BOT_LOGIN, "body": "[hotfix-bypass-audit] PR=1 reason=x"}],
        False,
    ),
    (
        "user.login spoof → FAIL (P3 fallback 제거 — author-shape 전용)",
        [{"user": {"login": BOT_LOGIN}, "body": "[hotfix-bypass-audit] PR=1 reason=x"}],
        False,
    ),
]


def cmd_selftest(_args):
    all_ok = True
    for name, comments, expected in _SELFTEST_CASES:
        passed, reason, _tagged, _spoof = evaluate(comments)
        ok = (passed == expected)
        status = "✓" if ok else "✗"
        print("%s selftest: %s → passed=%s expected=%s (%s)"
              % (status, name, passed, expected, reason))
        if not ok:
            all_ok = False

    n = len(_SELFTEST_CASES)
    if all_ok:
        print("check-audit-comment-author selftest: %d/%d PASS "
              "(bot→PASS / human→FAIL / absent→FAIL / flat-login·user.login spoof→FAIL)" % (n, n))
        return 0
    print("check-audit-comment-author selftest: FAIL — 판정 로직 불일치 (anti-theater breach)")
    return 1


# ─────────────────────── main ────────────────────────────────────────────────────

def main(argv):
    parser = argparse.ArgumentParser(
        description="hotfix-bypass audit comment author-verify lint (CFP-2591 / ADR-060 §결정 6)"
    )
    subparsers = parser.add_subparsers(dest="command")

    check_p = subparsers.add_parser("check", help="audit comment author-verify")
    check_p.add_argument(
        "--comments-json", default=None,
        help="comment JSON 파일 경로 (없으면 stdin)",
    )

    subparsers.add_parser(
        "selftest",
        help="5 embedded case 실행 (bot/human/absent + flat-login/user.login spoof)",
    )

    args = parser.parse_args(argv[1:])

    if args.command is None:
        args.command = "check"
        args.comments_json = None

    if args.command == "check":
        return cmd_check(args)
    if args.command == "selftest":
        return cmd_selftest(args)

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
