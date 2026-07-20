#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/integration/test_watchdog_three_state.py — CFP-2772 Phase 2 AC-5

AC-5: monotonic seq 3-state verdict (fresh, stalled, unknown)
      3-state boundary value analysis (BVA): τ−ε, τ, τ+ε
"""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from check_branch_liveness import (
    CF_ORCH_SENTINEL,
    evaluate,
    load_thresholds,
    parse_heartbeat,
)


def _mk_hb(branch, seq, story=None, lane=None, ts=None, state="active"):
    """Create heartbeat dict (parsed-like structure)."""
    return {
        "_malformed": False,
        "branch": branch,
        "seq": seq,
        "story": story or "CFP-2772",
        "lane": lane or "구현",
        "ts": ts or "2026-07-20T10:00:00Z",
        "state": state,
    }


def _iso(dt):
    """Format datetime as ISO8601 string."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class TestWatchdogThreeState:
    """AC-5: fresh, stalled, unknown verdicts"""

    def test_fresh_stalled_unknown_branches(self):
        """AC-5: three-state BVA with lane threshold boundary.

        Scenario:
        - Branch A: seq advances → fresh
        - Branch B: seq frozen, elapsed < threshold → within-patience (fresh)
        - Branch C: seq frozen, elapsed > threshold, ≥2 polls → stalled
        - Branch D: absent → unknown (when in cursor)
        """
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)
        lane_threshold_min = thresholds.get("구현", 180)  # 3 hours

        # ─ First poll (t=0) ────────────────────────────────────────
        latest_t0 = {
            "branch-a": _mk_hb("branch-a", 1, lane="구현"),
            "branch-b": _mk_hb("branch-b", 1, lane="구현"),
            "branch-c": _mk_hb("branch-c", 1, lane="구현"),
        }
        cursor_t0 = {
            "branch-d": {
                "last_seq": 5,
                "observed_at": "2026-07-20T12:00:00Z",
                "unchanged_polls": 0,
                "lane": "구현",
                "story": "CFP-2772",
                "state": "active",
            }
        }

        results_t0, cursor_t1 = evaluate(latest_t0, cursor_t0, now, thresholds)

        # At t=0, A/B/C are first-sighting (fresh)
        assert results_t0["branch-a"]["verdict"] == "fresh"
        assert results_t0["branch-b"]["verdict"] == "fresh"
        assert results_t0["branch-c"]["verdict"] == "fresh"
        # D is absent (in cursor but no comment) → unknown
        assert results_t0["branch-d"]["verdict"] == "unknown"  # absent

        # ─ Second poll (t=30min, within threshold) ────────────────────
        elapsed_30min = now + timedelta(minutes=30)
        latest_t1 = {
            "branch-a": _mk_hb("branch-a", 2, lane="구현"),  # advanced
            "branch-b": _mk_hb("branch-b", 1, lane="구현"),  # unchanged
            "branch-c": _mk_hb("branch-c", 1, lane="구현"),  # unchanged
        }

        results_t1, cursor_t2 = evaluate(latest_t1, cursor_t1, elapsed_30min, thresholds)

        # AC-5: seq advance → fresh
        assert results_t1["branch-a"]["verdict"] == "fresh"
        assert results_t1["branch-a"]["reason"] == "seq-advance"

        # AC-5: seq unchanged but within patience window → fresh (not stalled yet)
        assert results_t1["branch-b"]["verdict"] == "fresh"
        assert results_t1["branch-b"]["reason"] == "within-patience-window"

        # AC-5: seq unchanged, 1 poll unchanged → fresh (need ≥2 polls stalled)
        assert results_t1["branch-c"]["verdict"] == "fresh"
        assert results_t1["branch-c"]["unchanged_polls"] == 1

        # ─ Third poll (t=4h, past threshold) ──────────────────────────
        elapsed_4h = now + timedelta(hours=4)
        latest_t2 = {
            "branch-a": _mk_hb("branch-a", 3, lane="구현"),  # advanced again
            "branch-b": _mk_hb("branch-b", 1, lane="구현"),  # still unchanged
            "branch-c": _mk_hb("branch-c", 1, lane="구현"),  # still unchanged
        }

        results_t2, cursor_t3 = evaluate(latest_t2, cursor_t2, elapsed_4h, thresholds)

        # AC-5: A continues advancing → fresh
        assert results_t2["branch-a"]["verdict"] == "fresh"

        # AC-5: B frozen 4h > 3h threshold, ≥2 unchanged polls → stalled
        assert results_t2["branch-b"]["verdict"] == "stalled"
        assert results_t2["branch-b"]["reason"] == "seq-frozen-past-threshold"
        assert results_t2["branch-b"]["unchanged_polls"] >= 2

        # AC-5: C same as B (stalled)
        assert results_t2["branch-c"]["verdict"] == "stalled"
        assert results_t2["branch-c"]["reason"] == "seq-frozen-past-threshold"

    def test_fresh_stalled_boundary_value_analysis(self):
        """AC-5: BVA at threshold boundary (τ−ε, τ, τ+ε)."""
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)
        lane_threshold_min = thresholds.get("구현", 180)  # 3 hours = 180 min

        # First poll
        latest_t0 = {"test-br": _mk_hb("test-br", 1, lane="구현")}
        cursor_t0 = {}
        results_t0, cursor_t1 = evaluate(latest_t0, cursor_t0, now, thresholds)
        assert results_t0["test-br"]["verdict"] == "fresh"

        # ─ 30min (advance seq, establish 1st unchanged baseline) ──
        t_30min = now + timedelta(minutes=30)
        latest_30min = {"test-br": _mk_hb("test-br", 2, lane="구현")}
        results_30min, cursor_30min = evaluate(latest_30min, cursor_t1, t_30min, thresholds)
        assert results_30min["test-br"]["verdict"] == "fresh"

        # ─ 90min (seq still unchanged, 1st unchanged poll) ──
        t_90min = now + timedelta(minutes=90)
        latest_90min = {"test-br": _mk_hb("test-br", 2, lane="구현")}  # seq unchanged
        results_90min, cursor_90min = evaluate(latest_90min, cursor_30min, t_90min, thresholds)
        # Still within patience window (90-30=60 min < 180)
        assert results_90min["test-br"]["verdict"] == "fresh"
        assert results_90min["test-br"]["unchanged_polls"] == 1

        # ─ 211min (seq still unchanged, 2nd unchanged poll, past threshold) ──
        # Elapsed from last seq-advance (30min) to now (211min) = 181 min > 180 threshold
        t_211min = now + timedelta(minutes=211)
        latest_211 = {"test-br": _mk_hb("test-br", 2, lane="구현")}  # seq still unchanged
        results_211, cursor_211 = evaluate(latest_211, cursor_90min, t_211min, thresholds)

        # AC-5: clearly stalled (unchanged_polls ≥ 2 AND elapsed > threshold)
        assert results_211["test-br"]["verdict"] == "stalled", (
            f"Expected stalled, got {results_211['test-br']['verdict']}; "
            f"unchanged_polls={results_211['test-br']['unchanged_polls']}, "
            f"elapsed={results_211['test-br']['elapsed_min']}"
        )
        assert results_211["test-br"]["elapsed_min"] > lane_threshold_min
        assert results_211["test-br"]["unchanged_polls"] >= 2

    def test_unknown_verdict_conditions(self):
        """AC-5: unknown verdicts (absent, malformed, regress, etc.)."""
        now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        thresholds, _ = load_thresholds(None)

        # Establish baseline
        latest_t0 = {"branch": _mk_hb("branch", 5)}
        cursor_t0 = {}
        results_t0, cursor_t1 = evaluate(latest_t0, cursor_t0, now, thresholds)
        assert results_t0["branch"]["verdict"] == "fresh"

        # ─ Regress (seq_new < last_seq) ──
        t_later = now + timedelta(minutes=10)
        latest_regress = {"branch": _mk_hb("branch", 3)}  # regress 5 → 3
        results_regress, _ = evaluate(latest_regress, cursor_t1, t_later, thresholds)

        # AC-5: seq regress → unknown (anomaly)
        assert results_regress["branch"]["verdict"] == "unknown"
        assert results_regress["branch"]["reason"] == "seq-regress"

        # ─ Malformed ──
        latest_malformed = {"branch": {"_malformed": True, "branch": "branch"}}
        results_mal, _ = evaluate(latest_malformed, cursor_t1, t_later, thresholds)

        # AC-5: malformed → unknown
        assert results_mal["branch"]["verdict"] == "unknown"
        assert results_mal["branch"]["reason"] == "malformed-heartbeat"

        # ─ Absent ──
        latest_absent = {}
        results_absent, _ = evaluate(latest_absent, cursor_t1, t_later, thresholds)

        # AC-5: absent → unknown
        assert results_absent["branch"]["verdict"] == "unknown"
        assert results_absent["branch"]["reason"] == "heartbeat-absent"
