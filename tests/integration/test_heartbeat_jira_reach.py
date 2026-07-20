#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/integration/test_heartbeat_jira_reach.py — CFP-2772 Phase 2 AC-3

AC-3: tick lands on durable surface (Jira control project comment body)
        emitted body is the durable-surface payload the skill posts

Integration test: emit → body is the heartbeat comment that reaches Jira.
No live Jira calls; mock the addComment boundary.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from check_branch_liveness import CF_ORCH_SENTINEL


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_LIB = REPO_ROOT / "scripts" / "lib"
EMIT_SCRIPT = SCRIPTS_LIB / "emit_branch_heartbeat.py"


def _run_emit_probe(story, lane, branch=None, state="active"):
    """Run emit in probe mode (CBL_SKIP_ISSUE_CREATE=1)."""
    import os
    cmd = [sys.executable, str(EMIT_SCRIPT), "--story", story, "--lane", lane]
    if branch:
        cmd.extend(["--branch", branch])
    if state != "active":
        cmd.extend(["--state", state])

    env = os.environ.copy()
    env["CBL_SKIP_ISSUE_CREATE"] = "1"

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


class TestHeartbeatJiraReach:
    """AC-3: emit body is the durable heartbeat comment body for Jira"""

    def test_tick_lands_on_durable_surface(self):
        """AC-3: emit stdout is a valid heartbeat comment body ready for Jira addComment.

        The body output by emit_branch_heartbeat.py is what the skill would post as
        a comment to the Jira control project.
        """
        rc, stdout, stderr = _run_emit_probe(
            story="CFP-2772",
            lane="구현",
            branch="heartbeat-test",
            state="active",
        )

        assert rc == 0, f"emit failed: {stderr}"
        body = stdout.strip()

        # AC-3: body is a valid heartbeat comment
        assert body.startswith(CF_ORCH_SENTINEL), "Missing sentinel"
        assert "HEARTBEAT" in body, "Missing HEARTBEAT token"
        assert "branch=heartbeat-test" in body
        assert "story=CFP-2772" in body
        assert "lane=구현" in body
        assert "seq=" in body
        assert "ts=" in body

        # AC-3: durable surface means it's structured and parseable
        # (watchdog will parse it in check_branch_liveness.py)
        from check_branch_liveness import parse_heartbeat
        parsed = parse_heartbeat(body)
        assert parsed is not None, "Emitted body should parse as valid heartbeat"
        assert not parsed.get("_malformed"), "Parsed heartbeat should not be malformed"
        assert parsed["branch"] == "heartbeat-test"
        assert parsed["story"] == "CFP-2772"
        assert parsed["lane"] == "구현"

    def test_durable_surface_format_fidelity(self):
        """AC-3: format is deterministic and reaches Jira unchanged."""
        # Emit same branch twice; format should be identical (deterministic)
        rc1, out1, _ = _run_emit_probe(
            story="CFP-2772", lane="설계", branch="format-test"
        )
        rc2, out2, _ = _run_emit_probe(
            story="CFP-2772", lane="설계", branch="format-test"
        )

        assert rc1 == 0 and rc2 == 0

        body1 = out1.strip()
        body2 = out2.strip()

        # AC-3: both emit the same format (only seq/ts differ, which is expected)
        # Extract the template and verify identity modulo seq/ts
        import re

        def norm_body(b):
            """Remove dynamic fields for comparison."""
            b = re.sub(r"seq=\d+", "seq=N", b)
            b = re.sub(r"ts=\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", "ts=TS", b)
            return b

        assert norm_body(body1) == norm_body(body2), (
            f"Format differs despite identical inputs:\n{body1}\nvs\n{body2}"
        )

    def test_probe_mode_honors_skip_create_env(self):
        """AC-3: probe mode (CBL_SKIP_ISSUE_CREATE=1) skips side-effects."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            ledger = Path(tmpdir) / "ledger"
            ledger.mkdir()

            # Run in probe mode
            cmd = [
                sys.executable,
                str(EMIT_SCRIPT),
                "--story", "CFP-2772",
                "--lane", "구현",
                "--branch", "probe-test",
                "--ledger-dir", str(ledger),
            ]

            env = os.environ.copy()
            env["CBL_SKIP_ISSUE_CREATE"] = "1"

            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
            assert result.returncode == 0

            # Probe mode: seq file should NOT be created (side-effect 0)
            seq_file = ledger / "probe-test.seq"
            assert not seq_file.exists(), "Probe mode should not persist seq file"

            # But body should still be emitted
            assert result.stdout.strip().startswith(CF_ORCH_SENTINEL)

    def test_durable_surface_no_network_calls(self):
        """AC-3: emit itself makes no network calls (Jira/skill are separate boundary)."""
        # This is enforced by the emit script design: it only writes to stdout
        # and local ledger. The skill/Orchestrator handle posting to Jira.

        # Verify by checking that emit doesn't import MCP or Jira libraries
        from emit_branch_heartbeat import SCRIPT_NAME
        import inspect

        # Get the source of emit_branch_heartbeat
        import emit_branch_heartbeat
        source = inspect.getsource(emit_branch_heartbeat)

        # Check for actual imports (not just comments)
        import_patterns = [
            r"^import\s+jira",
            r"^import\s+atlassian",
            r"^from\s+jira\s+",
            r"^from\s+atlassian\s+",
            r"requests\.",
            r"urllib\.",
        ]
        import re
        for pattern in import_patterns:
            matches = re.findall(pattern, source, re.MULTILINE)
            assert not matches, (
                f"emit_branch_heartbeat should not import from {pattern}: {matches}"
            )
