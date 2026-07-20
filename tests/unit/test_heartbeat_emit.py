#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/unit/test_heartbeat_emit.py — CFP-2772 Phase 2 heartbeat emit AC-1/AC-2

AC-1: per-branch coarse tick carries branch_id (branch_key in heartbeat body)
AC-2: payload allowlist — no telemetry, only {branch_key, seq, story, lane, ts, state}

Red-first TDD: Tests written to FAIL against the emit behavior, then GREEN when
emit_branch_heartbeat.py is called.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Import check_branch_liveness to get the sentinel constant safely (avoids cp949 encoding issue)
from check_branch_liveness import CF_ORCH_SENTINEL


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_LIB = REPO_ROOT / "scripts" / "lib"
EMIT_SCRIPT = SCRIPTS_LIB / "emit_branch_heartbeat.py"


@pytest.fixture
def temp_ledger(tmp_path):
    """Temporary ledger directory for seq persistence."""
    ledger = tmp_path / "ledger"
    ledger.mkdir(exist_ok=True)
    return ledger


def _run_emit(story, lane, branch=None, state="active", ledger_dir=None, probe=False):
    """Run emit_branch_heartbeat.py and return (rc, stdout, stderr)."""
    cmd = [sys.executable, str(EMIT_SCRIPT), "--story", story, "--lane", lane]
    if branch:
        cmd.extend(["--branch", branch])
    if state != "active":
        cmd.extend(["--state", state])
    if ledger_dir:
        cmd.extend(["--ledger-dir", str(ledger_dir)])

    env = os.environ.copy()
    if probe:
        env["CBL_SKIP_ISSUE_CREATE"] = "1"

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


class TestHeartbeatEmit:
    """AC-1: per-branch tick carries branch_id"""

    def test_per_branch_tick_carries_branch_id(self, temp_ledger):
        """AC-1: emit body contains branch_key as intended branch identifier.

        RED: emit body should be parseable and contain the branch slug.
        """
        # Emit with explicit branch slug
        rc, stdout, stderr = _run_emit(
            story="CFP-2772",
            lane="구현",
            branch="cfp-2772-phase2",
            ledger_dir=temp_ledger,
            probe=True,
        )

        assert rc == 0, f"emit failed: {stderr}"
        body = stdout.strip()

        # AC-1: body must contain branch_key=<branch>
        assert "branch=cfp-2772-phase2" in body, f"branch_key not in body: {body}"

        # AC-1: must be able to parse out the branch
        assert body.startswith(CF_ORCH_SENTINEL), f"Missing sentinel: {body}"
        assert "HEARTBEAT" in body, f"Missing HEARTBEAT token: {body}"

    def test_per_branch_tick_multiple_branches(self, temp_ledger):
        """AC-1: different branches have distinct heartbeats."""
        rc1, stdout1, _ = _run_emit(
            story="CFP-2772",
            lane="구현",
            branch="branch-a",
            ledger_dir=temp_ledger,
            probe=True,
        )
        rc2, stdout2, _ = _run_emit(
            story="CFP-2772",
            lane="구현",
            branch="branch-b",
            ledger_dir=temp_ledger,
            probe=True,
        )

        assert rc1 == 0 and rc2 == 0
        body1 = stdout1.strip()
        body2 = stdout2.strip()

        # AC-1: distinct branch_key
        assert "branch=branch-a" in body1
        assert "branch=branch-b" in body2
        assert body1 != body2  # different bodies


class TestPayloadAllowlist:
    """AC-2: payload contains only {branch_key, seq, story, lane, ts, state} + telemetry-free"""

    def test_payload_allowlist_no_telemetry(self, temp_ledger):
        """AC-2: body carries ONLY {branch, seq, story, lane, ts, state} + '— alive'.
        NO tool-call, prompt, diff, telemetry.
        """
        rc, stdout, _ = _run_emit(
            story="CFP-2772",
            lane="구현",
            branch="test-branch",
            state="waiting-external:slow-review",
            ledger_dir=temp_ledger,
            probe=True,
        )

        assert rc == 0
        body = stdout.strip()

        # AC-2: required fields must be present
        assert "branch=test-branch" in body
        assert "story=CFP-2772" in body
        assert "lane=구현" in body
        assert "seq=" in body  # seq is numeric, checked by parser
        assert "ts=" in body  # ISO8601 timestamp
        assert "state=waiting-external:slow-review" in body

        # AC-2: FORBIDDEN content (telemetry, tool-call, etc.)
        forbidden_patterns = [
            "prompt_text", "tool_call", "diff", "memory", "context",
            "api_call", "endpoint", "credential", "token", "secret",
            "query", "result", "output", "trace", "debug",
        ]
        for pattern in forbidden_patterns:
            assert pattern.lower() not in body.lower(), (
                f"Telemetry pattern '{pattern}' found in body: {body}"
            )

    def test_payload_state_enum(self, temp_ledger):
        """AC-2: state field must be enum (active|waiting-external|idle-yield)."""
        for state in ["active", "idle-yield", "waiting-external:db-slow"]:
            rc, stdout, _ = _run_emit(
                story="CFP-2772",
                lane="구현",
                branch="test",
                state=state,
                ledger_dir=temp_ledger,
                probe=True,
            )
            assert rc == 0
            assert f"state={state}" in stdout.strip()

    def test_payload_bounded_fields(self, temp_ledger):
        """AC-2: fields are bounded (no unbounded free-form)."""
        # branch_key validation happens in emit (slug format)
        rc, stdout, _ = _run_emit(
            story="MYSTORY-2772",  # alphanumeric + dash + dot + underscore
            lane="test-lane",
            branch="valid-slug-123",
            ledger_dir=temp_ledger,
            probe=True,
        )

        assert rc == 0
        body = stdout.strip()

        # AC-2: fields bounded in format SSOT
        assert "story=MYSTORY-2772" in body
        assert "lane=test-lane" in body
        assert "branch=valid-slug-123" in body


class TestEmitNonBlocking:
    """AC-8: emit exit 0 ALWAYS, non-blocking (even on internal failure)"""

    def test_emit_non_blocking_record_only(self, tmp_path):
        """AC-8: emit exits 0 even when ledger dir is unwritable."""
        # Create a read-only directory
        ledger = tmp_path / "ledger"
        ledger.mkdir()
        ledger.chmod(0o444)  # read-only

        try:
            rc, stdout, stderr = _run_emit(
                story="CFP-2772",
                lane="구현",
                branch="test",
                ledger_dir=ledger,
                probe=False,  # Actually attempt to write
            )

            # AC-8: exit 0 ALWAYS (non-blocking)
            assert rc == 0, f"Should exit 0 even on write failure: {stderr}"

            # AC-8: body should still be emitted (record-only, seq write is optional)
            body = stdout.strip()
            assert body.startswith(CF_ORCH_SENTINEL)
            assert "HEARTBEAT" in body
        finally:
            ledger.chmod(0o755)  # restore for cleanup


class TestEmitSequenceMonotonic:
    """AC-5/AC-6 preparation: seq is monotonically increasing"""

    def test_seq_persists_and_increments(self, temp_ledger):
        """Emit twice to same branch: seq should increment (1 → 2)."""
        rc1, stdout1, _ = _run_emit(
            story="CFP-2772",
            lane="구현",
            branch="increment-test",
            ledger_dir=temp_ledger,
            probe=False,  # persist seq
        )

        rc2, stdout2, _ = _run_emit(
            story="CFP-2772",
            lane="구현",
            branch="increment-test",
            ledger_dir=temp_ledger,
            probe=False,
        )

        assert rc1 == 0 and rc2 == 0
        body1 = stdout1.strip()
        body2 = stdout2.strip()

        # Extract seq values (simple string search)
        import re
        seq1_match = re.search(r"seq=(\d+)", body1)
        seq2_match = re.search(r"seq=(\d+)", body2)

        assert seq1_match and seq2_match
        seq1 = int(seq1_match.group(1))
        seq2 = int(seq2_match.group(1))

        # AC-5/AC-6: monotonic increase
        assert seq2 > seq1, f"seq not monotonic: {seq1} → {seq2}"
