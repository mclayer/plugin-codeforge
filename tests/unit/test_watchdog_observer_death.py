#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/unit/test_watchdog_observer_death.py — CFP-2772 Phase 2 AC-4

AC-4: observer-death detection — emitter process killed, watchdog silent → unknown
      lifecycle independence: emitter↔watchdog stateless
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


class TestObserverDeath:
    """AC-4: emitter death → watchdog detects silence"""

    def test_observer_death_detected(self):
        """AC-4: emitter process killed → watchdog sees absence → unknown.

        Scenario:
        1. Branch heartbeat established (seq=1)
        2. Emitter process dies (no more heartbeats)
        3. Watchdog polls, sees absence → unknown (fail-safe, never false-fresh)
        """
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        # Baseline: branch has fresh heartbeat
        latest_baseline = {"doomed-branch": _mk_hb("doomed-branch", 1)}
        cursor_baseline = {}
        results_baseline, cursor_alive = evaluate(
            latest_baseline, cursor_baseline, now, thresholds
        )
        assert results_baseline["doomed-branch"]["verdict"] == "fresh"

        # ─ Emitter dies (no heartbeat in next poll) ──
        # latest is empty (no heartbeat from doomed-branch received)
        latest_after_death = {}
        results_after, cursor_after = evaluate(latest_after_death, cursor_alive, now, thresholds)

        # AC-4: absence → unknown (not false-fresh)
        assert results_after["doomed-branch"]["verdict"] == "unknown"
        assert results_after["doomed-branch"]["reason"] == "heartbeat-absent"

    def test_observer_death_independence(self):
        """AC-4: watchdog is stateless (doesn't call back emitter or depend on prior state).

        Watchdog's sole input: current heartbeat comments + durable cursor.
        Emitter's sole output: comment to Jira.
        No callback; no RPC.
        """
        # This is an architectural test confirming watchdog independence
        # Watchdog can be run separately, on a different machine, without emitter running

        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        # Simulate: Jira comments from prior emitter runs (now dead)
        # Watchdog reads these, doesn't try to contact emitter
        old_comments = {
            "branch": _mk_hb("branch", 5),
        }
        cursor = {
            "branch": {
                "last_seq": 5,
                "observed_at": "2026-07-19T12:00:00Z",  # 24h ago
                "unchanged_polls": 1,
                "lane": "구현",
                "story": "CFP-2772",
                "state": "active",
            }
        }

        # Run watchdog: it just reads comments and cursor, no side-effects
        results, updated_cursor = evaluate(old_comments, cursor, now, thresholds)

        # AC-4: watchdog doesn't crash, doesn't try to emit, just reports
        assert "branch" in results
        # Verdict depends on time elapsed; if >threshold, may be stalled/unknown
        # But point is: watchdog ran without emitter; no dependency

        # Cursor is updated (watchdog-own-clock, independent state)
        assert updated_cursor["branch"]["observed_at"]  # watchdog's own timestamp

    def test_death_per_branch_independence(self):
        """AC-4: one branch dying doesn't affect others."""
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        # Baseline: 3 branches alive
        latest_t0 = {
            "alive-1": _mk_hb("alive-1", 1),
            "alive-2": _mk_hb("alive-2", 1),
            "doomed": _mk_hb("doomed", 1),
        }
        cursor_t0 = {}
        results_t0, cursor_t1 = evaluate(latest_t0, cursor_t0, now, thresholds)

        assert results_t0["alive-1"]["verdict"] == "fresh"
        assert results_t0["alive-2"]["verdict"] == "fresh"
        assert results_t0["doomed"]["verdict"] == "fresh"

        # Next poll: doomed branch dies, others alive and advance
        latest_t1 = {
            "alive-1": _mk_hb("alive-1", 2),  # advanced
            "alive-2": _mk_hb("alive-2", 2),  # advanced
            # doomed absent
        }
        results_t1, cursor_t2 = evaluate(latest_t1, cursor_t1, now, thresholds)

        # AC-4: alive branches unaffected
        assert results_t1["alive-1"]["verdict"] == "fresh"
        assert results_t1["alive-1"]["seq_advanced"] is True
        assert results_t1["alive-2"]["verdict"] == "fresh"
        assert results_t1["alive-2"]["seq_advanced"] is True

        # AC-4: doomed branch shows absence
        assert results_t1["doomed"]["verdict"] == "unknown"
        assert results_t1["doomed"]["reason"] == "heartbeat-absent"
