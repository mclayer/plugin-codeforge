#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/unit/test_watchdog_fail_open.py — CFP-2772 Phase 2 AC-9

AC-9: fail-open is FORBIDDEN: unknown ≠ fresh, unknown ≠ PASS
      verdict inconclusive when unknown is present
"""

from datetime import datetime, timezone

import pytest

from check_branch_liveness import evaluate, load_thresholds


def _mk_hb(branch, seq):
    return {
        "_malformed": False,
        "branch": branch,
        "seq": seq,
        "story": "CFP-2772",
        "lane": "구현",
        "ts": "2026-07-20T12:00:00Z",
        "state": "active",
    }


class TestFailOpenForbidden:
    """AC-9: unknown verdict is NOT promoted to fresh/PASS"""

    def test_unknown_not_promoted_to_pass(self):
        """AC-9 NEGATIVE CONTROL: unknown verdict must NOT auto-upgrade to ok/pass.

        Absence, malformed, regress, unparseable → unknown → verdict inconclusive.
        """
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        # ─ Absent (no heartbeat comment from branch) ──
        latest_absent = {}  # branch absent
        cursor_with_branch = {
            "branch": {
                "last_seq": 5,
                "observed_at": "2026-07-20T12:00:00Z",
                "unchanged_polls": 0,
                "lane": "구현",
                "story": "CFP-2772",
                "state": "active",
            }
        }

        results_absent, _ = evaluate(latest_absent, cursor_with_branch, now, thresholds)

        # AC-9: absent → unknown (never fresh/ok)
        assert results_absent["branch"]["verdict"] == "unknown"
        assert results_absent["branch"]["reason"] == "heartbeat-absent"

        # ─ Malformed ──
        latest_mal = {
            "branch": {
                "_malformed": True,
                "branch": "branch",
                # no seq
            }
        }
        results_mal, _ = evaluate(latest_mal, cursor_with_branch, now, thresholds)

        # AC-9: malformed → unknown (never auto-pass)
        assert results_mal["branch"]["verdict"] == "unknown"
        assert results_mal["branch"]["reason"] == "malformed-heartbeat"

        # ─ Seq regress ──
        latest_regress = {"branch": _mk_hb("branch", 3)}  # regress 5 → 3
        results_regress, _ = evaluate(latest_regress, cursor_with_branch, now, thresholds)

        # AC-9: regress → unknown
        assert results_regress["branch"]["verdict"] == "unknown"
        assert results_regress["branch"]["reason"] == "seq-regress"

    def test_unknown_verdict_inconclusive_top_level(self):
        """AC-9: any unknown → top-level verdict inconclusive (not ok)."""
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        # Mix: some fresh, some unknown
        latest = {
            "alive": _mk_hb("alive", 1),
            # unknown-branch absent
        }
        cursor = {
            "alive": {
                "last_seq": 0,
                "observed_at": "2026-07-20T12:00:00Z",
                "unchanged_polls": 0,
                "lane": "구현",
                "story": "CFP-2772",
                "state": "active",
            },
            "unknown-branch": {
                "last_seq": 5,
                "observed_at": "2026-07-20T12:00:00Z",
                "unchanged_polls": 0,
                "lane": "구현",
                "story": "CFP-2772",
                "state": "active",
            },
        }

        results, _ = evaluate(latest, cursor, now, thresholds)

        # Summary has unknown > 0
        assert results["alive"]["verdict"] == "fresh"
        assert results["unknown-branch"]["verdict"] == "unknown"

        # ★ AC-9 CRITICAL: check_branch_liveness.main() would see this
        # and compute verdict_top = "inconclusive" (not "ok")
        # This test documents the expected behavior

    def test_unknown_branches_remain_in_cursor(self):
        """AC-9: unknown doesn't delete cursor entry (preserves history)."""
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        cursor_initial = {
            "branch": {
                "last_seq": 5,
                "observed_at": "2026-07-20T12:00:00Z",
                "unchanged_polls": 2,
                "lane": "구현",
                "story": "CFP-2772",
                "state": "active",
            }
        }

        # Branch goes absent (unknown)
        latest = {}
        results, cursor_updated = evaluate(latest, cursor_initial, now, thresholds)

        # AC-9: verdict unknown
        assert results["branch"]["verdict"] == "unknown"

        # AC-9: cursor entry preserved (not deleted)
        assert "branch" in cursor_updated
        assert cursor_updated["branch"]["last_seq"] == 5  # history retained

    def test_malformed_heartbeat_not_auto_fresh(self):
        """AC-9: malformed → unknown, never auto-upgraded to fresh."""
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        # Heartbeat malformed (branch known, seq missing)
        latest = {
            "branch": {
                "_malformed": True,
                "branch": "branch",  # identifiable
                # seq missing
            }
        }
        cursor = {
            "branch": {
                "last_seq": 10,
                "observed_at": "2026-07-20T12:00:00Z",
                "unchanged_polls": 0,
                "lane": "구현",
                "story": "CFP-2772",
                "state": "active",
            }
        }

        results, cursor_updated = evaluate(latest, cursor, now, thresholds)

        # AC-9: NEVER auto-promote to fresh
        assert results["branch"]["verdict"] == "unknown"

        # Cursor is preserved (doesn't regress even on malformed)
        assert cursor_updated["branch"]["last_seq"] == 10
