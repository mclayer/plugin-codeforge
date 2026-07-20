#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/integration/test_watchdog_cursor_persistence.py — CFP-2772 Phase 2 §8.5.2

Cursor persistence test (STATEFUL — AC-4, §8.5.2)

Discriminating pair:
  (a) Persisted cursor: durable cursor survives runs → stalled detected
  (b) Fresh-each-run (bug): new cursor per run → never stalled (false-negative)

Proves durable cursor is essential for hung detection (not just state verification).
"""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tests.conftest import run_cli_check_liveness


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WATCH_SCRIPT = REPO_ROOT / "scripts" / "lib" / "check_branch_liveness.py"


class TestCursorPersistence:
    """§8.5.2: Cursor durable state enables stalled detection across runs."""

    def test_persisted_cursor_detects_stalled(self):
        """(a) Persisted cursor: across 3 runs, stalled branch is detected.

        Run 1: branch=heartbeat(seq=1, fresh)
        Run 2 (90min later): seq=1 unchanged, unchanged_polls=1 (within patience window)
        Run 3 (211min later): seq=1 still unchanged, unchanged_polls=2, elapsed>180 → stalled
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            cursor_file = tmpdir / "cursor.json"
            comments_file = tmpdir / "comments.json"

            # ─ Run 1: baseline ──
            comments_file.write_text(
                json.dumps([{
                    "body": "⟦cf-orch⟧ HEARTBEAT branch=monitor seq=1 story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z — alive"
                }]),
                encoding="utf-8"
            )

            cursor_file.write_text("{}", encoding="utf-8")

            now1_iso = "2026-07-20T12:00:00Z"
            rc, out1 = run_cli_check_liveness(WATCH_SCRIPT, comments_file, cursor_file, now1_iso)

            assert rc == 0 and out1 is not None
            assert out1["branches"]["monitor"]["verdict"] == "fresh"
            assert out1["branches"]["monitor"]["unchanged_polls"] == 0

            # ─ Run 2 (90min later): unchanged, 1st poll ──
            now2_iso = "2026-07-20T13:30:00Z"
            comments_file.write_text(
                json.dumps([{
                    "body": "⟦cf-orch⟧ HEARTBEAT branch=monitor seq=1 story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z — alive"
                }]),
                encoding="utf-8"
            )
            # cursor persists from Run 1

            rc, out2 = run_cli_check_liveness(WATCH_SCRIPT, comments_file, cursor_file, now2_iso)

            assert rc == 0 and out2 is not None
            assert out2["branches"]["monitor"]["verdict"] == "fresh"
            assert out2["branches"]["monitor"]["unchanged_polls"] == 1

            # ─ Run 3 (211min later = 181min from first observation): unchanged, 2nd poll ──
            now3_iso = "2026-07-20T15:31:00Z"
            # cursor persists from Run 2
            # seq still 1 → unchanged_polls=2, elapsed=181min > 180min threshold

            rc, out3 = run_cli_check_liveness(WATCH_SCRIPT, comments_file, cursor_file, now3_iso)

            assert rc == 0 and out3 is not None

            # §8.5.2: persisted cursor enables stalled detection
            assert out3["branches"]["monitor"]["verdict"] == "stalled", (
                f"Persisted cursor should detect stalled after 181min + 2 unchanged polls, "
                f"but got {out3['branches']['monitor']['verdict']}"
            )

    def test_fresh_each_run_never_detects_stalled(self):
        """(b) Fresh-each-run (bug): new cursor per run → never stalled (false-negative).

        Same 3 runs, but cursor is wiped each time (no persistence).
        Result: branch appears fresh every time → false-negative, hung is missed.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Run 1 with fresh cursor
            comments_file = tmpdir / "comments.json"
            cursor_file = tmpdir / "cursor_run1.json"  # separate file each run

            comments_file.write_text(
                json.dumps([{
                    "body": "⟦cf-orch⟧ HEARTBEAT branch=monitor seq=1 story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z — alive"
                }]),
                encoding="utf-8"
            )

            cursor_file.write_text("{}", encoding="utf-8")
            now1_iso = "2026-07-20T12:00:00Z"
            rc, out1 = run_cli_check_liveness(WATCH_SCRIPT, comments_file, cursor_file, now1_iso)

            assert out1["branches"]["monitor"]["verdict"] == "fresh"

            # Run 2 with FRESH cursor (bug: not persisting)
            cursor_file2 = tmpdir / "cursor_run2.json"
            cursor_file2.write_text("{}", encoding="utf-8")  # empty, not persisted

            comments_file.write_text(
                json.dumps([{
                    "body": "⟦cf-orch⟧ HEARTBEAT branch=monitor seq=1 story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z — alive"
                }]),
                encoding="utf-8"
            )

            now2_iso = "2026-07-20T13:30:00Z"
            rc, out2 = run_cli_check_liveness(WATCH_SCRIPT, comments_file, cursor_file2, now2_iso)

            # Bug: fresh cursor means first-sighting again → fresh
            assert out2["branches"]["monitor"]["verdict"] == "fresh"
            assert out2["branches"]["monitor"]["unchanged_polls"] == 0  # reset

            # Run 3 with fresh cursor (bug continues)
            cursor_file3 = tmpdir / "cursor_run3.json"
            cursor_file3.write_text("{}", encoding="utf-8")

            comments_file.write_text(
                json.dumps([{
                    "body": "⟦cf-orch⟧ HEARTBEAT branch=monitor seq=1 story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z — alive"
                }]),
                encoding="utf-8"
            )

            now3_iso = "2026-07-20T15:31:00Z"
            rc, out3 = run_cli_check_liveness(WATCH_SCRIPT, comments_file, cursor_file3, now3_iso)

            # Bug: still fresh because cursor was reset each run
            assert out3["branches"]["monitor"]["verdict"] == "fresh"
            assert out3["branches"]["monitor"]["unchanged_polls"] == 0

    def test_persisted_vs_fresh_discriminating_pair(self):
        """§8.5.2 discriminating pair: (a) ≠ (b)

        Proves durable cursor is NECESSARY for stalled detection.

        stalled 판정은 unchanged_polls≥2 AND elapsed>threshold 를 요구한다. 따라서 persisted
        경로는 3-poll(advance→unchanged#1→unchanged#2) 을 거쳐야 stalled 에 도달한다.
        fresh 경로는 매 poll cursor 재생성 → 항상 first-sighting → 영구 fresh(false-negative).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            comments_file = tmpdir / "comments.json"
            comments_file.write_text(
                json.dumps([{
                    "body": "⟦cf-orch⟧ HEARTBEAT branch=test seq=1 story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z — alive"
                }]),
                encoding="utf-8"
            )

            # (a) Persisted cursor scenario — 3 runs build unchanged_polls up to 2.
            cursor_persisted = tmpdir / "cursor_persisted.json"
            cursor_persisted.write_text("{}", encoding="utf-8")

            # Run 1 (baseline) — first sighting → fresh, unchanged_polls=0.
            rc, out1 = run_cli_check_liveness(
                WATCH_SCRIPT, comments_file, cursor_persisted, "2026-07-20T12:00:00Z")
            assert out1["branches"]["test"]["verdict"] == "fresh"

            # Run 2 (90min later) — seq unchanged, unchanged_polls=1 (within patience).
            rc, out2 = run_cli_check_liveness(
                WATCH_SCRIPT, comments_file, cursor_persisted, "2026-07-20T13:30:00Z")
            assert out2["branches"]["test"]["verdict"] == "fresh"
            assert out2["branches"]["test"]["unchanged_polls"] == 1

            # Run 3 (211min from first obs) — unchanged_polls=2, elapsed=211>180 → stalled.
            rc, out3 = run_cli_check_liveness(
                WATCH_SCRIPT, comments_file, cursor_persisted, "2026-07-20T15:31:00Z")
            verdict_persisted = out3["branches"]["test"]["verdict"]

            # (b) Fresh cursor scenario — cursor wiped each run → never accumulates unchanged_polls.
            cursor_fresh = tmpdir / "cursor_fresh.json"
            cursor_fresh.write_text("{}", encoding="utf-8")  # always fresh
            rc, out_fresh = run_cli_check_liveness(
                WATCH_SCRIPT, comments_file, cursor_fresh, "2026-07-20T15:31:00Z")
            verdict_fresh = out_fresh["branches"]["test"]["verdict"]

            # §8.5.2: (a) persisted detects stalled, (b) fresh misses it (F-CR-003 회귀 방지).
            assert verdict_persisted == "stalled", "Persisted cursor should detect stalled"
            assert verdict_fresh == "fresh", "Fresh cursor causes false-negative (bug)"
            assert verdict_persisted != verdict_fresh, (
                "Persisted vs fresh cursors MUST produce different verdicts "
                "(this discriminates the importance of durable cursor)"
            )
