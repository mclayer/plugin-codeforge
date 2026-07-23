"""
CFP-2810 AC-1 (cancel==true) and AC-2 (cancel==false/expr) test suite.

AC-1: For rows cancel_spec=="true" (68 rows), actual concurrency.cancel-in-progress==True
      AND ${{ github.workflow }} in concurrency.group.

AC-2: For rows cancel_spec in {"false","expr"} (39 rows), actual cancel-in-progress is
      NOT True (false or absent or expression string, never literal True).
      count(with cancel==True)==0.
"""

import pytest
import yaml
import subprocess
from pathlib import Path
from _cfp2810_crosswalk import (
    MANIFEST, WIRED, CLASS_A_ROWS, resolve_path,
    COUNT_CLASS_A, COUNT_CLASS_B, COUNT_CLASS_C, COUNT_CLASS_D, COUNT_CLASS_M
)


@pytest.fixture(scope="session")
def wt_root():
    """Worktree root directory."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd="C:/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-2810",
        capture_output=True, text=True
    )
    return Path(result.stdout.strip())


def load_workflow_yaml(path_obj):
    """Load and parse YAML from workflow file."""
    with open(path_obj, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_ac1_cancel_true_has_cancel_in_progress(wt_root):
    """
    AC-1: Every row with cancel_spec=='true' must have
    concurrency.cancel-in-progress == True in actual workflow.
    """
    ac1_rows = [r for r in WIRED if r["cancel_spec"] == "true"]
    assert len(ac1_rows) == 68, f"Expected 68 AC-1 rows (cancel==true), got {len(ac1_rows)}"

    failures = []
    for row in ac1_rows:
        try:
            path = wt_root / resolve_path(row)
            wf = load_workflow_yaml(path)
            concurrency = wf.get("concurrency")

            if concurrency is None:
                failures.append(f"{row['name']}: missing top-level 'concurrency' block")
            elif not isinstance(concurrency, dict):
                failures.append(f"{row['name']}: 'concurrency' is not a dict")
            elif concurrency.get("cancel-in-progress") is not True:
                failures.append(
                    f"{row['name']}: cancel-in-progress={concurrency.get('cancel-in-progress')} (expected True)"
                )
        except Exception as e:
            failures.append(f"{row['name']}: {e}")

    assert not failures, f"AC-1 violations ({len(failures)}):\n" + "\n".join(failures)


def test_ac1_cancel_true_has_github_workflow_in_group(wt_root):
    """
    AC-1 (part b): Every row with cancel_spec=='true' must have
    ${{ github.workflow }} in concurrency.group.
    """
    ac1_rows = [r for r in WIRED if r["cancel_spec"] == "true"]

    failures = []
    for row in ac1_rows:
        try:
            path = wt_root / resolve_path(row)
            wf = load_workflow_yaml(path)
            concurrency = wf.get("concurrency", {})
            group = concurrency.get("group")

            if group is None:
                failures.append(f"{row['name']}: concurrency.group is missing")
            elif "${{ github.workflow }}" not in str(group):
                failures.append(f"{row['name']}: github.workflow not in group: {group}")
        except Exception as e:
            failures.append(f"{row['name']}: {e}")

    assert not failures, f"AC-1 github.workflow failures ({len(failures)}):\n" + "\n".join(failures)


def test_ac2_cancel_false_expr_not_true(wt_root):
    """
    AC-2: Every row with cancel_spec in {"false","expr"} must
    have cancel-in-progress that is NOT literally True.
    Allowed: absent, False, expression string.
    """
    ac2_rows = [r for r in WIRED if r["cancel_spec"] in {"false", "expr"}]
    # false rows: issue-body-claim-pre-screen, lane-evidence-check, parallel-epic-conflict-check,
    #             phase-gate-mergeable, phase-label-invariant, subissue-from-impl-manifest, fix-ledger-sync
    # + 32 expr rows
    expected_ac2_count = 39
    assert len(ac2_rows) == expected_ac2_count, f"Expected {expected_ac2_count} AC-2 rows, got {len(ac2_rows)}"

    failures = []
    for row in ac2_rows:
        try:
            path = wt_root / resolve_path(row)
            wf = load_workflow_yaml(path)
            concurrency = wf.get("concurrency", {})
            cancel_in_prog = concurrency.get("cancel-in-progress")

            # Fail only if literally True
            if cancel_in_prog is True:
                failures.append(
                    f"{row['name']}: cancel-in-progress=True (AC-2 violation, expected False/absent/expr)"
                )
        except Exception as e:
            failures.append(f"{row['name']}: {e}")

    assert not failures, f"AC-2 violations ({len(failures)}):\n" + "\n".join(failures)


def test_ac1_ac2_no_overlaps(wt_root):
    """
    AC-1 and AC-2 rows must be disjoint (no row in both).
    """
    ac1_rows = {r["name"] for r in WIRED if r["cancel_spec"] == "true"}
    ac2_rows = {r["name"] for r in WIRED if r["cancel_spec"] in {"false", "expr"}}

    overlap = ac1_rows & ac2_rows
    assert not overlap, f"AC-1 and AC-2 overlap: {overlap}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
