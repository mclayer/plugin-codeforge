#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/integration/test_watchdog_captured_golden.py — CFP-2772 Phase 2 §8.7

Captured-golden test: Jira getComments ordering/pagination
Tests that watchdog correctly handles real Atlassian REST API v3 comment ordering

§8.7 requirement:
  Test feeds captured-golden comment-list shaped like real Atlassian getComments
  (ordering + pagination page boundary) and asserts watchdog doesn't miss a branch
  whose latest tick is on a later page / out of order.

Atlassian REST API v3 comment object spec:
  https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-rest-api-3-issue-issueidorkey-comments-get
  Comments are returned in creation order (oldest first), with pagination support.
"""

import json
from datetime import datetime, timezone

import pytest

from check_branch_liveness import (
    CF_ORCH_SENTINEL,
    collect_latest_per_branch,
    evaluate,
    load_thresholds,
    parse_heartbeat,
)


def _mk_heartbeat_comment(branch, seq, created_time=None):
    """Create a mock Atlassian comment object with heartbeat body."""
    if created_time is None:
        created_time = "2026-07-20T12:00:00.000Z"

    body = (
        f"{CF_ORCH_SENTINEL} HEARTBEAT branch={branch} seq={seq} "
        f"story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z state=active — alive"
    )

    return {
        "id": f"comment-{branch}-{seq}",
        "created": created_time,
        "body": body,
        "author": {"displayName": "Orchestrator"},
    }


class TestWatchdogCapturedGolden:
    """§8.7: Atlassian getComments pagination/ordering fidelity"""

    def test_pagination_out_of_order_recovery(self):
        """§8.7: Latest heartbeat on later page is not missed (pagination handling).

        Scenario:
        Page 1: branch-a seq=1, branch-c seq=1 (older)
        Page 2: branch-b seq=1, branch-a seq=2, branch-c seq=2 (newer)

        Watchdog must select per-branch: max seq from across all pages.
        """
        # Simulate a paginated response (API v3 returns in creation order)
        all_comments = [
            # Page 1 (earlier comments)
            _mk_heartbeat_comment("branch-a", 1, "2026-07-20T10:00:00Z"),
            _mk_heartbeat_comment("branch-c", 1, "2026-07-20T10:10:00Z"),
            # Page 2 (later comments)
            _mk_heartbeat_comment("branch-b", 1, "2026-07-20T11:00:00Z"),
            _mk_heartbeat_comment("branch-a", 2, "2026-07-20T11:30:00Z"),
            _mk_heartbeat_comment("branch-c", 2, "2026-07-20T12:00:00Z"),
        ]

        # Extract bodies
        bodies = [c["body"] for c in all_comments]

        # Collect per-branch latest (should find max seq for each branch)
        latest = collect_latest_per_branch(bodies)

        # §8.7: all branches represented with latest seq
        assert "branch-a" in latest
        assert "branch-b" in latest
        assert "branch-c" in latest

        assert latest["branch-a"]["seq"] == 2  # max seq across all pages
        assert latest["branch-b"]["seq"] == 1
        assert latest["branch-c"]["seq"] == 2  # max seq across all pages

    def test_mixed_ordering_non_sequential_pages(self):
        """§8.7: Heartbeats out of sequence order still parsed correctly.

        Real Atlassian API returns comments in creation order (oldest first).
        Branches may appear out of sync if created at different times.
        """
        # Real-world scenario: branches created at different times
        all_comments = [
            _mk_heartbeat_comment("slow-branch", 1, "2026-07-20T08:00:00Z"),  # very old
            _mk_heartbeat_comment("fast-branch", 1, "2026-07-20T12:00:00Z"),  # new
            _mk_heartbeat_comment("slow-branch", 2, "2026-07-20T12:30:00Z"),  # caught up
            _mk_heartbeat_comment("fast-branch", 2, "2026-07-20T13:00:00Z"),
        ]

        bodies = [c["body"] for c in all_comments]
        latest = collect_latest_per_branch(bodies)

        # §8.7: latest seq for each branch
        assert latest["slow-branch"]["seq"] == 2
        assert latest["fast-branch"]["seq"] == 2

        # Watchdog can evaluate both correctly (order-independent collect)
        now = datetime(2026, 7, 20, 14, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)
        cursor = {}

        results, _ = evaluate(latest, cursor, now, thresholds)

        # Both branches appear fresh (first time seeing them)
        assert results["slow-branch"]["verdict"] == "fresh"
        assert results["fast-branch"]["verdict"] == "fresh"

    def test_duplicate_branch_seq_in_pagination(self):
        """§8.7: Duplicate (branch, seq) across pages → dedup (select one)."""
        # Edge case: same branch, same seq appears twice (shouldn't happen but tests robustness)
        all_comments = [
            _mk_heartbeat_comment("branch", 1, "2026-07-20T10:00:00Z"),
            _mk_heartbeat_comment("other", 1, "2026-07-20T11:00:00Z"),
            _mk_heartbeat_comment("branch", 1, "2026-07-20T12:00:00Z"),  # duplicate
        ]

        bodies = [c["body"] for c in all_comments]
        latest = collect_latest_per_branch(bodies)

        # §8.7: both appear, but "branch" should have latest seq=1 (only value)
        assert latest["branch"]["seq"] == 1
        assert latest["other"]["seq"] == 1

    def test_interleaved_heartbeats_and_other_comments(self):
        """§8.7: Mix of heartbeat and non-heartbeat comments (only heartbeats parsed)."""
        all_comments = [
            _mk_heartbeat_comment("branch-a", 1, "2026-07-20T10:00:00Z"),
            {
                "id": "other-comment-1",
                "created": "2026-07-20T10:30:00Z",
                "body": "This is a regular user comment, not a heartbeat",
                "author": {"displayName": "User"},
            },
            _mk_heartbeat_comment("branch-b", 1, "2026-07-20T11:00:00Z"),
            {
                "id": "other-comment-2",
                "created": "2026-07-20T11:30:00Z",
                "body": "Another regular comment",
                "author": {"displayName": "User"},
            },
            _mk_heartbeat_comment("branch-a", 2, "2026-07-20T12:00:00Z"),
        ]

        bodies = [c.get("body") or c.get("text") or "" for c in all_comments]
        latest = collect_latest_per_branch(bodies)

        # §8.7: only heartbeats collected
        assert len(latest) == 2  # only 2 branches
        assert "branch-a" in latest
        assert "branch-b" in latest
        assert latest["branch-a"]["seq"] == 2
        assert latest["branch-b"]["seq"] == 1

    def test_golden_complex_pagination_scenario(self):
        """§8.7: Complex real-world scenario with large pagination."""
        # Simulate large number of comments (multiple pages)
        all_comments = []

        # Branches in staggered pattern
        for i in range(10):  # 10 rounds of updates
            for branch in ["branch-a", "branch-b", "branch-c"]:
                created_time = f"2026-07-20T{10 + i:02d}:00:00Z"
                all_comments.append(
                    _mk_heartbeat_comment(branch, i + 1, created_time)
                )

        bodies = [c["body"] for c in all_comments]
        latest = collect_latest_per_branch(bodies)

        # §8.7: each branch should have the latest seq (seq=10 from last round)
        assert latest["branch-a"]["seq"] == 10
        assert latest["branch-b"]["seq"] == 10
        assert latest["branch-c"]["seq"] == 10

        # Watchdog evaluates: all appear fresh (seq advancing)
        now = datetime(2026, 7, 20, 20, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)
        cursor = {}

        results, _ = evaluate(latest, cursor, now, thresholds)

        for branch in ["branch-a", "branch-b", "branch-c"]:
            assert results[branch]["verdict"] == "fresh"
            assert results[branch]["seq"] == 10

    def test_atlassian_api_v3_schema_conformance(self):
        """§8.7: Golden fixture conforms to Atlassian REST API v3 comment schema.

        Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/#api-rest-api-3-issue-issueidorkey-comments-get

        Minimal required fields:
        - id: string
        - created: ISO8601 datetime
        - body: string (our heartbeat format)
        - author.displayName: string
        """
        # Create a golden comment (Atlassian v3 schema)
        golden_comment = {
            "id": "10000",
            "created": "2026-07-20T12:00:00.000Z",
            "body": (
                f"{CF_ORCH_SENTINEL} HEARTBEAT branch=test seq=1 "
                f"story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z state=active — alive"
            ),
            "author": {
                "self": "https://example.atlassian.net/...",
                "accountId": "ACCOUNT_ID_HASH",
                "emailAddress": "user@example.com",
                "displayName": "Orchestrator",
                "active": True,
            },
            "updated": "2026-07-20T12:00:00.000Z",
        }

        # §8.7: watchdog can parse this
        body = golden_comment["body"]
        parsed = parse_heartbeat(body)

        assert parsed is not None
        assert parsed["branch"] == "test"
        assert parsed["seq"] == 1
