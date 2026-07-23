"""
CFP-2810 Group-Shape AC: State-Bearing Workflow Concurrency Group Validation.

F-CR-006: For each WIRED workflow with side_effect_class in {B,D} that has
issues or push event triggers, verify concurrency.group contains:
  - github.ref: ABSENT (no git ref anchoring)
  - github.event.issue.number OR github.event.pull_request.number: PRESENT

Class-D workflows (phase-gate-mergeable, lane-evidence-check) are PR-only exempt.
Class-B workflows with issues/push triggers (phase-label-invariant, fix-ledger-sync)
must use issue/PR number anchoring (not ref-based).
"""

import pytest
import yaml
from pathlib import Path
from _cfp2810_crosswalk import MANIFEST, WIRED, resolve_path


BASE_COMMIT = "68ea503a0f6a3cc4e60243c429583cea3113b414"


def load_workflow_yaml(path_obj):
    """Load workflow from file."""
    with open(path_obj, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def wt_root():
    """Worktree root directory."""
    import subprocess
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd="C:/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-2810",
        capture_output=True, text=True
    )
    return Path(result.stdout.strip())


def test_ac_group_shape_state_bearing_workflows(wt_root):
    """
    F-CR-006: Verify state-bearing (B/D) workflows use issue/PR number anchoring.

    For workflows with side_effect_class in {B, D}:
    - If on: includes issues or push: concurrency.group must have issue.number OR pr.number
    - If on: is issues or push-only: concurrency.group must NOT have github.ref

    Exempt: Class-D PR-only workflows (phase-gate-mergeable, lane-evidence-check)
    """
    failures = []
    checked = 0

    for row in WIRED:
        if not row["wired"]:
            continue

        # Only check state-bearing workflows
        if row["side_effect_class"] not in {"B", "D"}:
            continue

        try:
            path = wt_root / resolve_path(row)
            if not path.exists():
                continue

            wf = load_workflow_yaml(path)
            on_section = wf.get(True)  # YAML parses 'on' as key True

            # Skip if no on section or purely push/issues
            if on_section is None or isinstance(on_section, bool):
                continue

            # Check if workflow has issues or push triggers
            has_issues = "issues" in on_section if isinstance(on_section, dict) else False
            has_push = "push" in on_section if isinstance(on_section, dict) else False

            if not (has_issues or has_push):
                # Not a state-mutation workflow (no issues/push), skip
                continue

            checked += 1
            concurrency = wf.get("concurrency", {})
            if not isinstance(concurrency, dict):
                failures.append(f"{row['name']}: concurrency is not a dict (is {type(concurrency).__name__})")
                continue

            group = concurrency.get("group")
            if group is None:
                failures.append(f"{row['name']}: concurrency.group missing")
                continue

            group_str = str(group)

            # Check for disqualifying ref-based grouping (must use issue/PR number)
            if "github.ref" in group_str:
                failures.append(
                    f"{row['name']}: group contains 'github.ref' (disqualified for state mutation: {group})"
                )
                continue

            # Check for required issue/PR number anchor
            has_issue_anchor = "github.event.issue.number" in group_str or "event.issue.number" in group_str
            has_pr_anchor = "github.event.pull_request.number" in group_str or "event.pull_request.number" in group_str

            if not (has_issue_anchor or has_pr_anchor):
                failures.append(
                    f"{row['name']}: group missing issue/PR number anchor (found: {group})"
                )

        except Exception as e:
            failures.append(f"{row['name']}: {type(e).__name__}: {e}")

    assert not failures, \
        f"Group-shape AC violations ({checked} checked): {len(failures)} failures\n" + "\n".join(failures)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
