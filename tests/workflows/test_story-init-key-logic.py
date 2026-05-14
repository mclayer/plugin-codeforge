#!/usr/bin/env python3
"""
CFP-671 — Story-init KEY computation logic semantic test.

본 test = story-init.yml 의 `Compute story key` step Python heredoc 와 동일 logic
verbatim copy + 5 TC (T-11.S~T-15.S, S=semantic) PASS evidence.

본 file = ADR-061 Amendment 1 (Python script-writing convention) 정합 — multi-line
Python 외부 .py file (workflow yml 안 heredoc 동일 logic 의 별 testable mirror).

Workflow yml 변경 시 본 file 갱신 의무 (ADR-068 I-4 wording SSOT).
"""

import os
import re
import sys


def compute_story_key(title: str, prefix: str, issue_number: str) -> tuple[str, str, str]:
    """
    story-init.yml `Compute story key` step Python heredoc 와 verbatim 동일 logic.

    Returns:
        (key, slug, title_clean)

    Decision tree (CFP-671 / ADR-036 Amendment 1):
        1. title `[STORY]` prefix 제거 → title_clean
        2. title pattern `[<PREFIX>-<N>]` or `<PREFIX>-<N>` 추출 → key_from_title
        3. key_from_title 가 prefix 와 match → key = key_from_title (title 우선)
        4. else → key = f"{prefix}-{issue_number}" (Issue # fallback — ADR-036 race-free)
    """
    # [STORY] prefix 제거 후 title clean
    title_clean = re.sub(r"^\[STORY\]\s*", "", title).strip()

    # Title pattern `[<PREFIX>-<N>]` or `<PREFIX>-<N>` 우선 추출
    m = re.search(r'\[?([A-Z]+-\d+)\]?', title_clean)
    key_from_title = m.group(1) if m else ""

    # Prefix guard — cross-project KEY injection 차단
    if key_from_title and key_from_title.startswith(prefix + "-"):
        key = key_from_title
    else:
        # Fallback to Issue # — ADR-036 결정 1 race-free guarantee 보존
        key = f"{prefix}-{issue_number}"

    # slug computation (CFP-596 base 동일)
    slug = re.sub(r"[^A-Za-z0-9가-힣]+", "-", title_clean, flags=re.UNICODE)
    slug = slug.strip("-")[:40].rstrip("-")

    return key, slug, title_clean


# ─── Test cases ───────────────────────────────────────────────────────────
test_cases = [
    # (TC name, title, prefix, issue_number, expected_key)
    (
        "T-11.S: title pattern matched + prefix matched → title KEY 우선",
        "[STORY] [CFP-662] bootstrap-labels workflow 신설 (RETRO-MCT-104 carrier)",
        "CFP",
        "670",
        "CFP-662",
    ),
    (
        "T-12.S: no title pattern → Issue # fallback (ADR-036 race-free 보존)",
        "[STORY] new feature 추가",
        "CFP",
        "680",
        "CFP-680",
    ),
    (
        "T-13.S: prefix mismatch → Issue # fallback (cross-project KEY injection 차단)",
        "[STORY] [ABC-123] external project carrier",
        "CFP",
        "680",
        "CFP-680",
    ),
    (
        "T-14.S: title pattern without [STORY] prefix → title KEY 우선",
        "[CFP-100] direct issue creation",
        "CFP",
        "200",
        "CFP-100",
    ),
    (
        "T-15.S: title pattern unbracketed → title KEY 우선",
        "[STORY] CFP-50 reservation followup",
        "CFP",
        "300",
        "CFP-50",
    ),
]


def main() -> int:
    passed = 0
    failed = 0

    print("--- CFP-671 Story-init KEY logic semantic tests ---")
    for tc_name, title, prefix, issue_number, expected_key in test_cases:
        actual_key, _, _ = compute_story_key(title, prefix, issue_number)
        if actual_key == expected_key:
            print(f"[PASS] {tc_name}")
            print(f"    title={title!r} prefix={prefix!r} issue#={issue_number}")
            print(f"    -> key={actual_key} (expected={expected_key})")
            passed += 1
        else:
            print(f"[FAIL] {tc_name}")
            print(f"    title={title!r} prefix={prefix!r} issue#={issue_number}")
            print(f"    -> key={actual_key} (expected={expected_key})")
            failed += 1

    print()
    print(f"--- Summary --- passed: {passed} / failed: {failed} / total: {len(test_cases)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
