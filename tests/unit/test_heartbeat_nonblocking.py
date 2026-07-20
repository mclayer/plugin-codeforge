#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/unit/test_heartbeat_nonblocking.py — CFP-2772 Phase 2 AC-8

AC-8: emit is non-blocking (exit 0 ALWAYS)
      deny-scan self-test (bad branch_key rejected by heartbeat-format.sh)
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from check_branch_liveness import CF_ORCH_SENTINEL


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_LIB = REPO_ROOT / "scripts" / "lib"
SCRIPTS_JIRA_CHANNEL = REPO_ROOT / "scripts" / "jira-channel"
EMIT_SCRIPT = SCRIPTS_LIB / "emit_branch_heartbeat.py"
HEARTBEAT_FORMAT_SCRIPT = SCRIPTS_JIRA_CHANNEL / "heartbeat-format.sh"


def _run_emit(story, lane, branch=None, ledger_dir=None):
    """Run emit, return (rc, stdout, stderr)."""
    cmd = [sys.executable, str(EMIT_SCRIPT), "--story", story, "--lane", lane]
    if branch:
        cmd.extend(["--branch", branch])
    if ledger_dir:
        cmd.extend(["--ledger-dir", str(ledger_dir)])

    env = os.environ.copy()
    env["CBL_SKIP_ISSUE_CREATE"] = "1"

    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", env=env
    )
    return result.returncode, result.stdout, result.stderr


def _run_heartbeat_format(branch, seq, story, lane, ts=None, state="active"):
    """Run heartbeat-format.sh via bash, return (rc, stdout, stderr)."""
    import shutil
    bash_path = shutil.which("bash")
    if not bash_path:
        # Try common Windows Git Bash locations
        for candidate in [
            r"C:\Program Files\Git\usr\bin\bash.exe",
            r"C:\Program Files\Git\bin\bash.exe",
        ]:
            if os.path.exists(candidate):
                bash_path = candidate
                break

    if not bash_path:
        pytest.skip("bash not found")

    cmd = [bash_path, str(HEARTBEAT_FORMAT_SCRIPT), branch, str(seq), story, lane]
    if ts:
        cmd.extend([ts, state])
    else:
        cmd.append(state)

    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8"
    )
    return result.returncode, result.stdout, result.stderr


class TestEmitNonBlocking:
    """AC-8: emit is non-blocking (exit 0 always)"""

    def test_emit_non_blocking_record_only(self):
        """AC-8: emit exits 0 even with internal failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Path(tmpdir) / "ledger"
            ledger.mkdir()
            # Make ledger read-only
            ledger.chmod(0o444)

            try:
                rc, stdout, stderr = _run_emit(
                    story="CFP-2772",
                    lane="구현",
                    branch="test",
                    ledger_dir=ledger,
                )

                # AC-8: exit 0 ALWAYS (even on write failure)
                assert rc == 0, f"Expected exit 0, got {rc}: {stderr}"

                # AC-8: body is still emitted (record-only semantics)
                body = stdout.strip()
                assert body.startswith(CF_ORCH_SENTINEL)
                assert "HEARTBEAT" in body
            finally:
                ledger.chmod(0o755)


class TestDenyScanSelfTest:
    """AC-8: deny-scan self-test (bad branch_key rejected)"""

    def test_deny_scan_rejects_bad_branch_key(self):
        """AC-8: heartbeat-format.sh rejects branch_key with special chars (deny-scan).

        Bad inputs (email, path, free-form) should be rejected at construction time.
        """
        # AC-8: free-form branch_key (contains @ or /) should be rejected
        bad_branches = [
            "branch@email.com",  # email-like
            "/etc/passwd",  # path-like
            "branch\\path",  # backslash
            "branch with space",  # space
        ]

        for bad_branch in bad_branches:
            rc, stdout, stderr = _run_heartbeat_format(
                branch=bad_branch,
                seq=1,
                story="CFP-2772",
                lane="구현",
            )

            # AC-8: exit 3 (validation error)
            assert rc == 3, f"Expected exit 3 for bad branch '{bad_branch}', got {rc}"
            assert stderr, f"Expected stderr message for bad branch '{bad_branch}'"

    def test_deny_scan_rejects_bad_seq(self):
        """AC-8: seq must be numeric."""
        rc, stdout, stderr = _run_heartbeat_format(
            branch="valid-branch",
            seq="not-a-number",  # bad seq
            story="CFP-2772",
            lane="구현",
        )

        # AC-8: exit 3 (validation error)
        assert rc == 3
        assert "seq" in stderr.lower()

    def test_deny_scan_rejects_bad_story(self):
        """AC-8: story must be KEY-like (no free-form)."""
        bad_stories = [
            "/path/to/story",  # path
            "story@example.com",  # email
        ]

        for bad_story in bad_stories:
            rc, stdout, stderr = _run_heartbeat_format(
                branch="valid",
                seq=1,
                story=bad_story,
                lane="구현",
            )

            # AC-8: exit 3
            assert rc == 3

    def test_deny_scan_rejects_bad_lane(self):
        """AC-8: lane forbids @:=/\\ and control chars."""
        bad_lanes = [
            "lane@example.com",  # @
            "lane:value",  # :
            "lane=value",  # =
            "lane/path",  # /
            "lane\\path",  # \
        ]

        for bad_lane in bad_lanes:
            rc, stdout, stderr = _run_heartbeat_format(
                branch="valid",
                seq=1,
                story="CFP-2772",
                lane=bad_lane,
            )

            # AC-8: exit 3
            assert rc == 3

    def test_deny_scan_accepts_valid_inputs(self):
        """AC-8: valid inputs are accepted."""
        # heartbeat-format.sh: branch, seq, story, lane, [ts], [state]
        # If only 4 args, state defaults to "active"
        rc, stdout, stderr = _run_heartbeat_format(
            branch="cfp-2772-phase2",
            seq=1,
            story="CFP-2772",
            lane="구현",  # Korean lane name is allowed
            ts="2026-07-20T12:00:00Z",
            state="active",
        )

        # AC-8: exit 0 (valid)
        assert rc == 0, f"Expected exit 0, got {rc}: {stderr}"
        body = stdout.strip()
        assert body.startswith(CF_ORCH_SENTINEL)

    def test_deny_scan_bounded_lengths(self):
        """AC-8: fields have length bounds."""
        # Too-long branch_key
        rc, stdout, stderr = _run_heartbeat_format(
            branch="a" * 300,  # >200
            seq=1,
            story="CFP-2772",
            lane="구현",
        )

        # AC-8: exit 3 (length exceeded)
        assert rc == 3

        # Too-long seq (>18 digits)
        rc, stdout, stderr = _run_heartbeat_format(
            branch="valid",
            seq="123456789012345678901",  # 21 digits
            story="CFP-2772",
            lane="구현",
        )

        assert rc == 3

        # Too-long story
        rc, stdout, stderr = _run_heartbeat_format(
            branch="valid",
            seq=1,
            story="a" * 100,  # >64
            lane="구현",
        )

        assert rc == 3

        # Too-long lane
        rc, stdout, stderr = _run_heartbeat_format(
            branch="valid",
            seq=1,
            story="CFP-2772",
            lane="a" * 100,  # >64
        )

        assert rc == 3
