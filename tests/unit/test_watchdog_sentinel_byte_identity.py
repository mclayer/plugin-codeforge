#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/unit/test_watchdog_sentinel_byte_identity.py — CFP-2772 Phase 2 F-CR-005

★ F-CR-005 [P2]: Sentinel byte-identity self-test

Verifies that ⟦cf-orch⟧ sentinel is byte-identical across 4 sources:
  1. scripts/jira-channel/echo-guard.sh CF_ORCH_SENTINEL constant
  2. scripts/jira-channel/progress-format.sh CF_ORCH_SENTINEL usage
  3. scripts/jira-channel/heartbeat-format.sh CF_ORCH_SENTINEL constant
  4. scripts/lib/check_branch_liveness.py CF_ORCH_SENTINEL constant

Defends against UTF-8 encoding drift (cp949 mangling) across files.
"""

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _extract_sentinel_literal(file_path, var_name="CF_ORCH_SENTINEL"):
    """Extract ⟦cf-orch⟧ sentinel literal from source file.

    Supports bash (readonly CF_ORCH_SENTINEL='⟦cf-orch⟧') and Python (CF_ORCH_SENTINEL = "⟦cf-orch⟧").
    Returns raw UTF-8 bytes of the sentinel value.
    """
    with open(file_path, "rb") as f:
        content_bytes = f.read()

    # Try to find the literal (bash or Python syntax)
    patterns = [
        # Bash: readonly CF_ORCH_SENTINEL='⟦cf-orch⟧'
        rb"CF_ORCH_SENTINEL\s*=\s*'([^']+)'",
        # Python: CF_ORCH_SENTINEL = "⟦cf-orch⟧"
        rb'CF_ORCH_SENTINEL\s*=\s*"([^"]+)"',
    ]

    for pattern in patterns:
        match = re.search(pattern, content_bytes)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract {var_name} literal from {file_path}")


class TestSentinelByteIdentity:
    """F-CR-005: Sentinel ⟦cf-orch⟧ is byte-identical across 4 sources."""

    def test_sentinel_byte_identity(self):
        """F-CR-005: All 4 sources have byte-identical sentinel."""
        # Extract sentinel bytes from each source
        sources = {
            "echo-guard.sh": REPO_ROOT / "scripts" / "jira-channel" / "echo-guard.sh",
            "progress-format.sh": REPO_ROOT / "scripts" / "jira-channel" / "progress-format.sh",
            "heartbeat-format.sh": REPO_ROOT / "scripts" / "jira-channel" / "heartbeat-format.sh",
            "check_branch_liveness.py": REPO_ROOT / "scripts" / "lib" / "check_branch_liveness.py",
        }

        sentinel_bytes = {}
        for name, path in sources.items():
            assert path.exists(), f"Source file not found: {path}"
            sentinel_bytes[name] = _extract_sentinel_literal(path)

        # F-CR-005: All bytes must be identical
        reference_bytes = sentinel_bytes["echo-guard.sh"]

        for name, bytes_value in sentinel_bytes.items():
            assert bytes_value == reference_bytes, (
                f"Sentinel byte mismatch in {name}:\n"
                f"  Expected: {reference_bytes}\n"
                f"  Got:      {bytes_value}\n"
                f"  This indicates UTF-8 encoding drift (mojibake)"
            )

        # Decode and verify it's the expected sentinel
        sentinel_str = reference_bytes.decode("utf-8")
        assert sentinel_str == "⟦cf-orch⟧", (
            f"Sentinel decoded value incorrect: {sentinel_str}"
        )

    def test_sentinel_used_in_heartbeat_format(self):
        """F-CR-005: heartbeat-format.sh actually uses the sentinel in output."""
        heartbeat_path = REPO_ROOT / "scripts" / "jira-channel" / "heartbeat-format.sh"

        with open(heartbeat_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify the printf line includes the sentinel variable
        assert "printf" in content
        assert "$CF_ORCH_SENTINEL" in content
        assert "HEARTBEAT" in content
        assert "alive" in content

    def test_sentinel_used_in_check_branch_liveness(self):
        """F-CR-005: check_branch_liveness.py actually uses the sentinel for parsing."""
        check_path = REPO_ROOT / "scripts" / "lib" / "check_branch_liveness.py"

        with open(check_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify the constant is defined and used in parsing
        assert "CF_ORCH_SENTINEL = " in content
        assert "⟦cf-orch⟧" in content
        assert "HEARTBEAT_TOKEN" in content
        assert ".startswith(CF_ORCH_SENTINEL)" in content
