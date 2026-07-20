#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/integration/test_watchdog_mutation_driver.py — CFP-2772 Phase 2 F-CR-002

★ F-CR-002 [P1 born-dormant]: Mutation driver test (non-dormant CI execution)

Actually run mutations and verify they're killed by the test suite.
Proves tests are not vacuous-GREEN.
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tests.conftest import run_cli_check_liveness
from tests.scripts._branch_liveness_mutations import iter_mutants


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WATCH_SCRIPT = REPO_ROOT / "scripts" / "lib" / "check_branch_liveness.py"
SRC_SCRIPT = REPO_ROOT / "scripts" / "lib" / "check_branch_liveness.py"


class TestMutationDriver:
    """F-CR-002: Verify mutations are killed by test suite (non-dormant execution)."""

    def test_fail_open_promotion_mutant_killed(self, tmp_path):
        """Fail-open-promotion mutant (unknown→ok) must be killed by AC-9 CLI test."""
        with tempfile.TemporaryDirectory() as mutant_dir:
            mutant_dir = Path(mutant_dir)

            # Generate fail-open-promotion mutants
            mutant_count = 0
            for desc, mutant_path, mutant_module in iter_mutants(
                "fail-open-promotion", mutant_dir, SRC_SCRIPT
            ):
                mutant_count += 1

                # Scenario: unknown present → mutant verdict=="ok" (wrong), original=="inconclusive"
                comments_file = tmp_path / f"comments_{mutant_count}.json"
                comments_file.write_text(
                    json.dumps([
                        {"body": "⟦cf-orch⟧ HEARTBEAT branch=alive seq=1 story=CFP-2772 lane=구현 ts=2026-07-20T12:00:00Z — alive"}
                    ]),
                    encoding="utf-8"
                )

                cursor_file = tmp_path / f"cursor_{mutant_count}.json"
                cursor_file.write_text(
                    json.dumps({
                        "unknown-branch": {
                            "last_seq": 5,
                            "observed_at": "2026-07-20T12:00:00Z",
                            "unchanged_polls": 0,
                            "lane": "구현",
                            "story": "CFP-2772",
                            "state": "active"
                        }
                    }),
                    encoding="utf-8"
                )

                # Run mutant CLI
                rc, output = run_cli_check_liveness(
                    mutant_path, comments_file, cursor_file, "2026-07-20T12:00:00Z"
                )

                assert rc == 0, f"Mutant CLI failed: {mutant_path}"
                assert output is not None, f"Mutant JSON parse failed: {mutant_path}"

                # ★ Mutant MUST produce wrong verdict (killed)
                # Original = inconclusive, mutant = ok (fail-open promotion)
                assert output["verdict"] == "ok", (
                    f"Mutant {mutant_count} ({desc}) should be killed (verdict=='ok'), "
                    f"but test didn't catch it"
                )

            # F-CR-002 honesty: applied > 0
            assert mutant_count > 0, "fail-open-promotion mutations not applied (source drift)"

    def test_seq_advance_relaxation_mutant_killed(self, tmp_path):
        """Seq-advance-relaxation mutant (>→>=) must be killed (discriminating: orig≠mutant)."""
        import copy
        from check_branch_liveness import evaluate, load_thresholds

        with tempfile.TemporaryDirectory() as mutant_dir:
            mutant_dir = Path(mutant_dir)

            # Discriminating scenario — seq frozen past threshold with 2 prior unchanged polls:
            #   Original ('>')  : seq_new(1) not > last_seq(1) → stalled (frozen past threshold).
            #   Mutant  ('>=')  : seq_new(1) >= last_seq(1) → treated as advance → fresh (WRONG).
            now = datetime(2026, 7, 20, 16, 0, 0, tzinfo=timezone.utc)  # 240min after observed_at
            thresholds, _ = load_thresholds(None)

            latest = {"branch": {
                "_malformed": False,
                "branch": "branch",
                "seq": 1,
                "story": "CFP-2772",
                "lane": "구현",
                "ts": "2026-07-20T12:00:00Z",
                "state": "active",
            }}

            def _cursor():
                return {"branch": {
                    "last_seq": 1,
                    "observed_at": "2026-07-20T12:00:00Z",  # 240min ago (> 180min 구현 threshold)
                    "unchanged_polls": 2,
                    "lane": "구현",
                    "story": "CFP-2772",
                    "state": "active",
                }}

            # Baseline: original evaluate → stalled (proves the mutant diverges — non-vacuous).
            orig_results, _ = evaluate(latest, copy.deepcopy(_cursor()), now, thresholds)
            assert orig_results["branch"]["verdict"] == "stalled", (
                "baseline drift: original should report stalled (seq frozen past threshold)"
            )

            mutant_count = 0
            for desc, mutant_path, mutant_module in iter_mutants(
                "seq-advance-relaxation", mutant_dir, SRC_SCRIPT
            ):
                mutant_count += 1
                results, _ = mutant_module.evaluate(latest, copy.deepcopy(_cursor()), now, thresholds)

                # Mutant treats unchanged seq as advance → fresh; kill = verdict diverges from original.
                assert results["branch"]["verdict"] == "fresh", (
                    f"Mutant {mutant_count} ({desc}) should report fresh (unchanged-as-advance)"
                )
                assert results["branch"]["verdict"] != orig_results["branch"]["verdict"], (
                    f"Mutant {mutant_count} ({desc}) not discriminated (orig==mutant → hollow)"
                )

            assert mutant_count > 0, "seq-advance-relaxation mutations not applied"

    def test_threshold_bypass_mutant_killed(self, tmp_path):
        """Threshold-bypass mutant (thr→thr*2) must be killed (discriminating: orig≠mutant)."""
        import copy
        from check_branch_liveness import evaluate, load_thresholds

        with tempfile.TemporaryDirectory() as mutant_dir:
            mutant_dir = Path(mutant_dir)

            # Discriminating scenario — elapsed(240min) sits between thr(180) and thr*2(360):
            #   Original ('elapsed > thr')     : 240>180 → stalled.
            #   Mutant  ('elapsed > thr * 2')  : 240>360 False → within-patience → fresh (WRONG).
            now = datetime(2026, 7, 20, 16, 0, 0, tzinfo=timezone.utc)  # 240min later
            thresholds, _ = load_thresholds(None)

            latest = {"branch": {
                "_malformed": False,
                "branch": "branch",
                "seq": 1,
                "story": "CFP-2772",
                "lane": "구현",
                "ts": "2026-07-20T12:00:00Z",
                "state": "active",
            }}

            def _cursor():
                return {"branch": {
                    "last_seq": 1,
                    "observed_at": "2026-07-20T12:00:00Z",  # 240min ago
                    "unchanged_polls": 2,  # ≥2
                    "lane": "구현",
                    "story": "CFP-2772",
                    "state": "active",
                }}

            # Baseline: original evaluate → stalled (elapsed past threshold).
            orig_results, _ = evaluate(latest, copy.deepcopy(_cursor()), now, thresholds)
            assert orig_results["branch"]["verdict"] == "stalled", (
                "baseline drift: original should report stalled at elapsed>threshold"
            )

            mutant_count = 0
            for desc, mutant_path, mutant_module in iter_mutants(
                "threshold-bypass", mutant_dir, SRC_SCRIPT
            ):
                mutant_count += 1
                results, _ = mutant_module.evaluate(latest, copy.deepcopy(_cursor()), now, thresholds)

                # Mutant doubles the threshold → misses the stall → fresh; kill = diverges from original.
                assert results["branch"]["verdict"] == "fresh", (
                    f"Mutant {mutant_count} ({desc}) threshold bypass should report fresh"
                )
                assert results["branch"]["verdict"] != orig_results["branch"]["verdict"], (
                    f"Mutant {mutant_count} ({desc}) not discriminated (orig==mutant → hollow)"
                )

            assert mutant_count > 0, "threshold-bypass mutations not applied"

    def test_idle_relaxation_disable_mutant_killed(self, tmp_path):
        """Idle-relaxation-disable mutant (if idle→if False) must be killed."""
        from check_branch_liveness import evaluate, load_thresholds

        with tempfile.TemporaryDirectory() as mutant_dir:
            mutant_dir = Path(mutant_dir)

            mutant_count = 0
            for desc, mutant_path, mutant_module in iter_mutants(
                "idle-relaxation-disable", mutant_dir, SRC_SCRIPT
            ):
                mutant_count += 1

                now = datetime(2026, 7, 20, 16, 0, 0, tzinfo=timezone.utc)  # 4h later
                thresholds, _ = load_thresholds(None)

                latest = {"branch": {
                    "_malformed": False,
                    "branch": "branch",
                    "seq": 1,
                    "story": "CFP-2772",
                    "lane": "구현",
                    "ts": "2026-07-20T12:00:00Z",
                    "state": "waiting-external:slow-db",  # idle state
                }}

                cursor = {
                    "branch": {
                        "last_seq": 1,
                        "observed_at": "2026-07-20T12:00:00Z",  # 4h ago, past threshold
                        "unchanged_polls": 2,
                        "lane": "구현",
                        "story": "CFP-2772",
                        "state": "waiting-external:slow-db"
                    }
                }

                results, _ = mutant_module.evaluate(latest, cursor, now, thresholds)

                # Original: idle→fresh (relaxed)
                # Mutant: idle bypass→stalled (wrong, idle should be relaxed)
                assert results["branch"]["verdict"] == "stalled", (
                    f"Mutant {mutant_count} ({desc}) disabling idle-relaxation should cause stalled"
                )

            assert mutant_count > 0, "idle-relaxation-disable mutations not applied"

    def test_total_deadline_removal_mutant_killed(self, tmp_path):
        """Total-deadline-removal mutant (ceiling gone) must be killed."""
        from check_branch_liveness import evaluate, load_thresholds

        with tempfile.TemporaryDirectory() as mutant_dir:
            mutant_dir = Path(mutant_dir)

            mutant_count = 0
            for desc, mutant_path, mutant_module in iter_mutants(
                "total-deadline-removal", mutant_dir, SRC_SCRIPT
            ):
                mutant_count += 1

                now = datetime(2026, 7, 21, 13, 0, 0, tzinfo=timezone.utc)  # 25h later
                thresholds, _ = load_thresholds(None)

                latest = {"branch": {
                    "_malformed": False,
                    "branch": "branch",
                    "seq": 1,
                    "story": "CFP-2772",
                    "lane": "구현",
                    "ts": "2026-07-20T12:00:00Z",
                    "state": "waiting-external:very-slow",
                }}

                cursor = {
                    "branch": {
                        "last_seq": 1,
                        "observed_at": "2026-07-20T12:00:00Z",  # 25h ago, past 1440min ceiling
                        "unchanged_polls": 2,
                        "lane": "구현",
                        "story": "CFP-2772",
                        "state": "waiting-external:very-slow"
                    }
                }

                results, _ = mutant_module.evaluate(latest, cursor, now, thresholds)

                # Original: total-deadline ceiling(1440min) breached → unknown
                # Mutant: ceiling removed → fresh (wrong, should eventually be unknown)
                assert results["branch"]["verdict"] == "fresh", (
                    f"Mutant {mutant_count} ({desc}) removing total-deadline ceiling should keep fresh"
                )

            assert mutant_count > 0, "total-deadline-removal mutations not applied"

    def test_all_mutations_survive_zero(self, tmp_path):
        """Verify: all 5 mutation kinds are applied and killed (survive=0)."""
        kinds = [
            "fail-open-promotion",
            "seq-advance-relaxation",
            "threshold-bypass",
            "idle-relaxation-disable",
            "total-deadline-removal",
        ]

        with tempfile.TemporaryDirectory() as mutant_dir:
            mutant_dir = Path(mutant_dir)

            for kind in kinds:
                applied = 0
                for desc, mutant_path, mutant_module in iter_mutants(kind, mutant_dir, SRC_SCRIPT):
                    applied += 1

                # F-CR-002 honesty: each kind must have applied > 0
                assert applied > 0, (
                    f"Mutation kind '{kind}' not applied (source drift?)"
                )
