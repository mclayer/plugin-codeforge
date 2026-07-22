#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/integration/test_watchdog_threshold.py — CFP-2772 Phase 2 AC-6

AC-6: lane-differentiated thresholds + waiting-external idle-relaxation
      external-idle branch quiet within window ≠ stalled
"""

from datetime import datetime, timedelta, timezone

import pytest

from check_branch_liveness import evaluate, load_thresholds


def _mk_hb(branch, seq, lane=None, state="active"):
    return {
        "_malformed": False,
        "branch": branch,
        "seq": seq,
        "story": "CFP-2772",
        "lane": lane or "구현",
        "ts": "2026-07-20T12:00:00Z",
        "state": state,
    }


class TestWatchdogThreshold:
    """AC-6: lane threshold differentiation + idle-relaxation"""

    def test_lane_threshold_baseline(self):
        """AC-6: different lanes have different thresholds.

        short/mechanical = 45 min
        medium (구현/설계) = 180 min
        long (리뷰) = 240 min
        """
        thresholds, _ = load_thresholds(None)

        # Verify proposal values
        assert thresholds.get("mechanical", 0) <= 60  # 45 min
        assert thresholds.get("구현", 0) == 180  # 3 hours
        assert thresholds.get("구현리뷰", 0) == 240  # 4 hours
        assert thresholds.get("short", 0) == 45  # short (구 deploy lane fixture = CFP-2782 제거, short 대표로 대체)

        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)

        # ─ short lane ──
        latest_short = {"short-br": _mk_hb("short-br", 1, lane="short")}
        cursor = {}
        results, cursor_updated = evaluate(latest_short, cursor, now, thresholds)
        assert results["short-br"]["threshold_min"] == 45

        # ─ medium lane ──
        latest_med = {"med-br": _mk_hb("med-br", 1, lane="구현")}
        results, cursor_updated = evaluate(latest_med, cursor, now, thresholds)
        assert results["med-br"]["threshold_min"] == 180

        # ─ long (review) lane ──
        latest_long = {"long-br": _mk_hb("long-br", 1, lane="구현리뷰")}
        results, cursor_updated = evaluate(latest_long, cursor, now, thresholds)
        assert results["long-br"]["threshold_min"] == 240

    def test_external_idle_not_hung(self):
        """AC-6: waiting-external branch in patience window ≠ stalled.

        waiting-external/idle-yield has INV-L1 total-deadline ceiling but
        is exempt from lane-threshold stalling within its context window.
        """
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        # First poll
        latest_t0 = {
            "external-br": _mk_hb("external-br", 1, lane="구현", state="waiting-external:db-query")
        }
        cursor_t0 = {}
        results_t0, cursor_t1 = evaluate(latest_t0, cursor_t0, now, thresholds)
        assert results_t0["external-br"]["verdict"] == "fresh"

        # ─ Poll at 200 minutes later (past 구현 threshold 180) ──
        # But branch is in waiting-external state
        t_200min = now + timedelta(minutes=200)
        latest_t1 = {
            "external-br": _mk_hb("external-br", 1, lane="구현", state="waiting-external:db-query")
        }
        results_t1, cursor_t2 = evaluate(latest_t1, cursor_t1, t_200min, thresholds)

        # AC-6: idle-relaxation — waiting-external is exempt from threshold stalling
        # (though will eventually hit total-deadline ceiling at 1440 min)
        assert results_t1["external-br"]["verdict"] == "fresh"
        assert results_t1["external-br"]["idle_relaxed"] is True
        assert results_t1["external-br"]["reason"] == "idle-relaxed-within-ceiling"

    def test_idle_yield_state_relaxation(self):
        """AC-6: idle-yield state (no-op yield) also exempt from threshold."""
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        latest_t0 = {"idle-br": _mk_hb("idle-br", 1, lane="구현", state="idle-yield")}
        cursor_t0 = {}
        results_t0, cursor_t1 = evaluate(latest_t0, cursor_t0, now, thresholds)

        # Much later (500 min, well past threshold)
        t_500min = now + timedelta(minutes=500)
        latest_t1 = {"idle-br": _mk_hb("idle-br", 1, lane="구현", state="idle-yield")}
        results_t1, _ = evaluate(latest_t1, cursor_t1, t_500min, thresholds)

        # AC-6: idle-yield → fresh (relaxed, within ceiling)
        assert results_t1["idle-br"]["verdict"] == "fresh"
        assert results_t1["idle-br"]["idle_relaxed"] is True

    def test_total_deadline_ceiling_breaks_idle(self):
        """AC-6: INV-L1 total-deadline (1440 min) ceiling — even idle exhausts patience."""
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        latest_t0 = {
            "ceiling-br": _mk_hb("ceiling-br", 1, lane="구현", state="waiting-external:slow-backend")
        }
        cursor_t0 = {}
        results_t0, cursor_t1 = evaluate(latest_t0, cursor_t0, now, thresholds)

        # At total-deadline (1440 min) + epsilon
        t_ceiling_breach = now + timedelta(minutes=1441)
        latest_t1 = {"ceiling-br": _mk_hb("ceiling-br", 1, lane="구현", state="waiting-external:slow-backend")}
        results_t1, _ = evaluate(latest_t1, cursor_t1, t_ceiling_breach, thresholds)

        # AC-6: total-deadline ceiling breach → unknown (not even idle relaxation)
        assert results_t1["ceiling-br"]["verdict"] == "unknown"
        assert results_t1["ceiling-br"]["reason"] == "total-deadline-ceiling-breached"

    def test_unknown_lane_uses_default(self):
        """AC-6: unknown lane falls back to default threshold."""
        thresholds, _ = load_thresholds(None)

        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)

        # Unknown lane (not in proposal)
        latest = {"unknown-lane-br": _mk_hb("unknown-lane-br", 1, lane="미등록레인")}
        cursor = {}
        results, _ = evaluate(latest, cursor, now, thresholds)

        # AC-6: unknown lane → default threshold (180 min, "medium")
        assert results["unknown-lane-br"]["threshold_min"] == 180  # _DEFAULT_THRESHOLD_MIN
