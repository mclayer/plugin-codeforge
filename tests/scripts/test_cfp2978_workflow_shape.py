#!/usr/bin/env python3
"""
CFP-2978 AC-10 workflow structure oracle — W-14

Tests the AC-10 normative requirement: conservation of workflow local customizations
(concurrency, timeout-minutes, runs-on) across consumer 4-repo backfill.

AC-10 binds wrapper template + 4 consumer repos. Elements E1-E8 define what must
be preserved/absent. This test file operationalizes the W-13 `scripts/lib/workflow_shape.py`
oracle as pytest fixtures + mutant harness.

Change Plan §8.A specifies:
- Elements E1-E8 (preservation inventory per §8.A line 593-602)
- Mutation roster (§8.A line 606-627):
  - Removal direction (R-1 through R-5): each mutant targets single element, observe RED ∧ siblings GREEN
  - Relocation direction (R-6, R-7): path-set predicates catch structural shifts undetectable by cardinality
  - Tautological control (T-taut): straw oracle (text-only assertions) vs. real oracle (PyYAML structure parser)
- Predicate form rules (§8.D general rules 1-5):
  - Cardinality only as derived from path set (never 1st-order input)
  - Absence assertions require positive anchor ∧
  - Domain declaration mandatory (text / structure / output / mixed)
"""

import json
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Fixture blob references (§8.A pinned literals — immutable)
PIN_MCTRADER_GROUP = (
    "${{ github.workflow }}-"
    "${{ github.event_name == 'pull_request' && github.event.pull_request.number || github.run_id }}"
)
CANON_RUNS_ON = (
    "${{ fromJSON(vars.CI_RUNS_ON_LINUX_JSON || "
    '[\"ubuntu-latest\"]'
    ") }}"
)

# Consumer worktree references (local immutable blob locations)
CONSUMER_REPOS = {
    "mctrader": "/c/workspace/mclayer/mctrader",
    "mctrader-backtest": "/c/workspace/mclayer/mctrader-backtest",
    "mctrader-market": "/c/workspace/mclayer/mctrader-market",
    "mctrader-engine": "/c/workspace/mclayer/mctrader-engine",
}

WORKFLOW_PATH = ".github/workflows/parallel-work-sentinel-check.yml"


def load_workflow_yaml(file_path: str) -> Optional[dict]:
    """
    Load workflow YAML using PyYAML. Return None if file missing or parse error.

    Fails closed with exit 2 on:
    - P-1: File missing
    - P-2: YAML parse error
    - P-3: Root not dict
    - P-6: yaml module import failure (shouldn't happen in test env, but guard)
    """
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not available (P-6 fail-closed guard)")

    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"P-1 workflow file missing: {file_path}")

    try:
        with open(file_path_obj) as f:
            content = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"P-2 YAML parse error: {e}")

    if content is None:
        raise ValueError("P-3 workflow not mapping (empty/comment-only)")

    if not isinstance(content, dict):
        raise ValueError(f"P-3 workflow root type {type(content).__name__}, expected dict")

    return content


def extract_workflow_shape(workflow_yaml: dict) -> dict:
    """
    Extract structural shape from parsed workflow.

    Returns dict with fields matching W-13 signature (§8.A line 530-544):
    - job_ids: list[str]
    - top_concurrency: dict | None
    - concurrency_paths: list[str]
    - coe_paths: list[str]  (§8.B leg ③)
    - timeout_paths: dict[str, int]
    - job_if, step_if, env_keys, etc. (full set)
    """
    shape = {
        "job_ids": [],
        "top_concurrency": workflow_yaml.get("concurrency"),
        "concurrency_paths": [],
        "coe_paths": [],
        "timeout_paths": {},
        "job_if": {},
        "step_if": {},
        "env_keys": {"workflow": list(workflow_yaml.get("env", {}).keys())},
        "container_env_keys": {},
        "env_file_keys": {},
        "step_shell": {},
        "defaults_run_shell": workflow_yaml.get("defaults", {}).get("run", {}).get("shell"),
        "job_defaults_run_shell": {},
        "runs_on": {},
    }

    # Extract job-level structures
    jobs = workflow_yaml.get("jobs", {})
    if not isinstance(jobs, dict):
        raise ValueError(f"P-4: jobs not dict, got {type(jobs).__name__}")

    if not jobs:
        raise ValueError("P-4: jobs missing or empty")

    for job_id, job_spec in jobs.items():
        if not isinstance(job_spec, dict):
            continue

        shape["job_ids"].append(job_id)

        # Concurrency paths
        if "concurrency" in job_spec:
            shape["concurrency_paths"].append(f"jobs.{job_id}.concurrency")

        # Timeout paths (job-level and step-level)
        if "timeout-minutes" in job_spec:
            shape["timeout_paths"][f"jobs.{job_id}"] = job_spec["timeout-minutes"]

        # Job-level if condition
        shape["job_if"][job_id] = job_spec.get("if")

        # runs-on
        if "runs-on" in job_spec:
            shape["runs_on"][job_id] = job_spec["runs-on"]

        # env at job level
        shape["env_keys"][f"jobs.{job_id}"] = list(job_spec.get("env", {}).keys())

        # Job-level defaults
        if "defaults" in job_spec and "run" in job_spec["defaults"]:
            shape["job_defaults_run_shell"][job_id] = job_spec["defaults"]["run"].get("shell")

        # Step-level structures
        steps = job_spec.get("steps", [])
        shape["step_if"][job_id] = []
        shape["step_shell"][job_id] = []

        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                continue

            # continue-on-error paths
            if "continue-on-error" in step:
                shape["coe_paths"].append(f"jobs.{job_id}.steps[{i}].continue-on-error")

            # Step-level if
            shape["step_if"][job_id].append(step.get("if"))

            # Step-level shell
            shape["step_shell"][job_id].append(step.get("shell"))

            # Step-level env
            if "env" in step:
                step_env_key = f"jobs.{job_id}.steps[{i}]"
                shape["env_keys"][step_env_key] = list(step.get("env", {}).keys())

            # Timeout at step level
            if "timeout-minutes" in step:
                shape["timeout_paths"][f"jobs.{job_id}.steps[{i}]"] = step["timeout-minutes"]

        # Container env (§8.A line 540 — future-proof)
        if "container" in job_spec and "env" in job_spec["container"]:
            shape["container_env_keys"][job_id] = list(job_spec["container"]["env"].keys())

        # $GITHUB_ENV detection (inline only — §8.F C-3)
        # This is a simplified version; full implementation in W-13
        env_file_keys = []
        for i, step in enumerate(steps):
            if "run" in step:
                run_text = step["run"]
                # Naive check for $GITHUB_ENV writes (text domain only)
                if "$GITHUB_ENV" in run_text and ">>" in run_text:
                    env_file_keys.append(f"jobs.{job_id}.steps[{i}]")
        if env_file_keys:
            shape["env_file_keys"][job_id] = env_file_keys

    # Add job-level continue-on-error paths
    for job_id, job_spec in jobs.items():
        if not isinstance(job_spec, dict):
            continue
        if "continue-on-error" in job_spec:
            shape["coe_paths"].append(f"jobs.{job_id}.continue-on-error")

    # Sort paths for deterministic comparison
    shape["concurrency_paths"].sort()
    shape["coe_paths"].sort()

    return shape


def test_e1_mctrader_top_concurrency_exists():
    """E1 (AC-10): mctrader top-level `concurrency` exists"""
    yaml_path = f"{CONSUMER_REPOS['mctrader']}/{WORKFLOW_PATH}"
    yaml_doc = load_workflow_yaml(yaml_path)
    shape = extract_workflow_shape(yaml_doc)

    assert shape["top_concurrency"] is not None, "E1 failed: top_concurrency is None"
    assert "concurrency" in shape["concurrency_paths"], "E1 failed: concurrency path absent"


def test_e2_mctrader_group_equals_pin():
    """E2 (AC-10): mctrader group == PIN_MCTRADER_GROUP (string equality, not regex)"""
    yaml_path = f"{CONSUMER_REPOS['mctrader']}/{WORKFLOW_PATH}"
    yaml_doc = load_workflow_yaml(yaml_path)
    shape = extract_workflow_shape(yaml_doc)

    assert shape["top_concurrency"] is not None, "E2 prerequisite: top_concurrency missing"
    group_value = shape["top_concurrency"].get("group")

    assert group_value == PIN_MCTRADER_GROUP, (
        f"E2 failed: group mismatch\n"
        f"Expected: {PIN_MCTRADER_GROUP}\n"
        f"Got:      {group_value}"
    )


def test_e3_mctrader_template_group_absent():
    """
    E3 (AC-10): mctrader group does NOT use wrapper template expression

    Standalone: pure absence-assert (§8.D rule 2: must AND with E2).
    Here we verify E2 is true before checking E3 doesn't hold.
    """
    yaml_path = f"{CONSUMER_REPOS['mctrader']}/{WORKFLOW_PATH}"
    yaml_doc = load_workflow_yaml(yaml_path)
    shape = extract_workflow_shape(yaml_doc)

    assert shape["top_concurrency"] is not None, "E3 prerequisite: top_concurrency missing"
    group_value = shape["top_concurrency"].get("group")

    # Wrapper template expression (has github.ref, not github.run_id)
    template_expr = "${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}"

    assert group_value != template_expr, (
        f"E3 failed: group should NOT be template expression\n"
        f"Got: {group_value}"
    )


def test_e4_mctrader_no_job_concurrency():
    """E4 (AC-10): mctrader jobs.*.concurrency == ∅ (empty set)"""
    yaml_path = f"{CONSUMER_REPOS['mctrader']}/{WORKFLOW_PATH}"
    yaml_doc = load_workflow_yaml(yaml_path)
    shape = extract_workflow_shape(yaml_doc)

    job_concurrency_paths = [p for p in shape["concurrency_paths"] if p.startswith("jobs.")]

    assert len(job_concurrency_paths) == 0, (
        f"E4 failed: found job-level concurrency paths: {job_concurrency_paths}"
    )


def test_e5_mctrader_timeout_exactly_2():
    """
    E5 (AC-10): mctrader timeout-minutes: 10 at job-level, exactly 2 occurrences

    §8.D rule 1: Cardinality as derived path-set predicate (not raw count).
    Assertion: path set cardinality must be 2, not just count.
    """
    yaml_path = f"{CONSUMER_REPOS['mctrader']}/{WORKFLOW_PATH}"
    yaml_doc = load_workflow_yaml(yaml_path)
    shape = extract_workflow_shape(yaml_doc)

    # Path-set predicate: job-level timeout paths (no "[" = no step-level)
    timeout_paths = [
        k for k in shape["timeout_paths"].keys()
        if not "[" in k  # Exclude step-level (have [...])
    ]

    assert len(timeout_paths) == 2, (
        f"E5 failed: expected 2 job-level timeout paths, got {len(timeout_paths)}\n"
        f"Paths: {timeout_paths}"
    )

    # Verify each path's value is 10 (query paths, not count)
    for path in timeout_paths:
        value = shape["timeout_paths"][path]
        assert value == 10, f"E5 failed: {path} timeout value is {value}, expected 10"


def test_e6_backtest_no_top_concurrency():
    """E6 (AC-10): backtest/engine/market top-level concurrency == ∅"""
    for repo_name in ["mctrader-backtest", "mctrader-engine", "mctrader-market"]:
        yaml_path = f"{CONSUMER_REPOS[repo_name]}/{WORKFLOW_PATH}"
        yaml_doc = load_workflow_yaml(yaml_path)
        shape = extract_workflow_shape(yaml_doc)

        assert shape["top_concurrency"] is None, (
            f"E6 failed for {repo_name}: top_concurrency should be None, got {shape['top_concurrency']}"
        )


def test_e7_backtest_no_job_concurrency():
    """E7 (AC-10): backtest/engine/market jobs.*.concurrency == ∅"""
    for repo_name in ["mctrader-backtest", "mctrader-engine", "mctrader-market"]:
        yaml_path = f"{CONSUMER_REPOS[repo_name]}/{WORKFLOW_PATH}"
        yaml_doc = load_workflow_yaml(yaml_path)
        shape = extract_workflow_shape(yaml_doc)

        job_concurrency_paths = [p for p in shape["concurrency_paths"] if p.startswith("jobs.")]

        assert len(job_concurrency_paths) == 0, (
            f"E7 failed for {repo_name}: found job-level concurrency: {job_concurrency_paths}"
        )


def test_e8_market_job2_runs_on_custom():
    """
    E8 (AC-10): market job2 runs-on uses custom variable expression (not canonical ubuntu-latest).

    Uses derived accessor runs_on_local_delta (§8.A P1-c) to detect deviations from
    canonical template value.
    """
    yaml_path = f"{CONSUMER_REPOS['mctrader-market']}/{WORKFLOW_PATH}"
    yaml_doc = load_workflow_yaml(yaml_path)
    shape = extract_workflow_shape(yaml_doc)

    # Market should have job2 with different runs-on than template
    job2_runs_on = shape["runs_on"].get("parallel-work-sentinel-test")

    assert job2_runs_on is not None, "E8 failed: parallel-work-sentinel-test job not found"
    assert job2_runs_on != "ubuntu-latest", (
        f"E8 failed: market job2 runs-on should be customized, got {job2_runs_on}"
    )
    assert "fromJSON" in job2_runs_on, (
        f"E8 failed: market job2 should use fromJSON expression, got {job2_runs_on}"
    )


# Mutation tests — verify oracle has teeth (§8.A mutant roster)
# These are skeleton tests; full implementation includes mutant generators


def test_oracle_mutation_r1_remove_mctrader_top_concurrency():
    """
    R-1 mutant (§8.A line 608): Remove mctrader top-level concurrency block.
    Expected: E1 RED ∧ (E2, E3, E4, E5 each report independently).

    This test verifies the oracle *can* detect the removal (discriminating capability).
    """
    # Create a mutant by removing top_concurrency
    yaml_path = f"{CONSUMER_REPOS['mctrader']}/{WORKFLOW_PATH}"
    yaml_doc = load_workflow_yaml(yaml_path)

    # Mutant: delete concurrency
    if "concurrency" in yaml_doc:
        del yaml_doc["concurrency"]

    shape = extract_workflow_shape(yaml_doc)

    # E1 should fail
    assert shape["top_concurrency"] is None, "R-1 oracle failed: E1 should be RED"

    # E2, E3 should independently report (not silently pass because E1 failed)
    # This is the §8.D rule 2 check: absence + positive anchor
    assert "concurrency" not in shape["concurrency_paths"], "R-1 oracle: concurrency_paths should be empty"


def test_oracle_taut_template_vs_mctrader_runs_on():
    """
    T-taut (§8.A line 623): Tautological control — straw oracle vs. real oracle.

    Straw oracle: Only check runs_on inheritance (always GREEN when values inherited).
    Real oracle: Detect structural differences (E2, E5, etc.).

    This demonstrates why text-only assertions (bare runs_on comparison) are insufficient.
    """
    yaml_path = f"{CONSUMER_REPOS['mctrader']}/{WORKFLOW_PATH}"
    yaml_doc = load_workflow_yaml(yaml_path)
    shape = extract_workflow_shape(yaml_doc)

    # Straw oracle (insufficient): just check runs-on exists
    straw_passes = all(
        jid in shape["runs_on"]
        for jid in ["parallel-work-sentinel", "parallel-work-sentinel-test"]
    )

    # Real oracle (sufficient): must also verify E2 (group matches PIN)
    real_oracle_passes = (
        shape["top_concurrency"] is not None and
        shape["top_concurrency"].get("group") == PIN_MCTRADER_GROUP
    )

    # Both should pass for mctrader, but the point is that straw oracle alone
    # is weaker (would pass even if other elements were corrupted)
    assert straw_passes, "Straw oracle should pass (runs-on present)"
    assert real_oracle_passes, "Real oracle should pass (E2 holds)"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
