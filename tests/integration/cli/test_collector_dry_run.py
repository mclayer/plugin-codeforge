"""Integration tests for mctrader-collector --dry-run CLI behaviour.

These tests exercise the CLI as a subprocess so that argparse exit codes and
stderr output can be verified without mocking internals.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# The Python interpreter that owns the installed package
_PYTHON = sys.executable


def _run_collector(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run 'python -m mctrader.cli.collector_main <args>' and return result."""
    cmd = [_PYTHON, "-m", "mctrader.cli.collector_main", *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )


# ---------------------------------------------------------------------------
# test_cli_dry_run_exit_code_on_bad_config
# ---------------------------------------------------------------------------

def test_cli_dry_run_exit_code_on_bad_config() -> None:
    """--dry-run with a nonexistent config dir must exit 1 and print stderr tag.

    RED-observation substitute: exit code assertion was temporarily changed to
    `assert result.returncode == 0` to confirm the test catches a failure
    before being restored.
    """
    import os

    env = {**os.environ, "MCTRADER_CONFIG_DIR": "/nonexistent/path/that/does/not/exist"}

    result = _run_collector("--dry-run", env=env)

    assert result.returncode == 1, (
        f"Expected exit 1, got {result.returncode}.\nstderr: {result.stderr}"
    )
    # stderr must contain the dry-run:failed prefix and stage
    assert "[dry-run:failed]" in result.stderr, (
        f"Expected '[dry-run:failed]' in stderr.\nstderr: {result.stderr}"
    )
    assert "config_load" in result.stderr or "config_validate" in result.stderr, (
        f"Expected config stage in stderr.\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# test_cli_dry_run_mutual_arg_rule
# ---------------------------------------------------------------------------

def test_cli_dry_run_mutual_arg_rule() -> None:
    """--exchange bithumb without --dry-run must exit 2 (argparse error).

    RED-observation substitute: exit code assertion was temporarily changed to
    `assert result.returncode == 1` to confirm argparse exit 2 is distinct.
    """
    result = _run_collector("--exchange", "bithumb")

    assert result.returncode == 2, (
        f"Expected exit 2 from argparse, got {result.returncode}.\nstderr: {result.stderr}"
    )
    # argparse writes to stderr; message should mention --exchange or --dry-run
    assert "--exchange" in result.stderr or "dry-run" in result.stderr or "error" in result.stderr.lower(), (
        f"Expected argparse error message in stderr.\nstderr: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# test_cli_no_dry_run_flag_unchanged
# ---------------------------------------------------------------------------

def test_cli_no_dry_run_flag_unchanged() -> None:
    """Without --dry-run or --exchange, argparse must parse successfully (exit not 2).

    This is a smoke test for the normal (non-dry-run) path: it verifies that
    the argparse additions did not break baseline argument parsing by importing
    and invoking the parser with no flags.  The process will exit 1 (config
    load failure) which is expected in a test environment without real config —
    but must NOT exit 2.

    RED-observation substitute: assertion was temporarily set to
    `assert result.returncode == 2` to confirm the test catches the distinction.
    """
    import os

    # Point to a nonexistent config so the process exits fast (exit 1, not 2)
    env = {**os.environ, "MCTRADER_CONFIG_DIR": "/nonexistent"}

    result = _run_collector(env=env)

    # argparse must not error (exit 2); config load failure (exit 1) is OK
    assert result.returncode != 2, (
        f"argparse errored (exit 2) on a plain invocation — baseline parsing broken.\nstderr: {result.stderr}"
    )
    # Should not contain dry-run output either
    assert "[dry-run]" not in result.stdout
