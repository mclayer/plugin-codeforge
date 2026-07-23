"""
CFP-2810 AC-3: Class-A Misclassification Seal Test.

AC-3(a): Every WIRED workflow's concurrency.group contains ${{ github.workflow }}.
AC-3(b): Class-A workflows (side_effect_class=="A") must NOT contain disqualifying
         state-mutation markers in job bodies.
AC-3(c): Positive-control mutation-kill: inject a disqualifying marker and verify
         the seal function detects it (RED).

Disqualifying marker set (FROZEN):
  - addLabels, removeLabel(s), setLabels
  - pulls.update, issues.create (NOT createComment), issues.update
  - git.createRef, git push/commit/tag
  - checks.create

Non-disqualifying (reporting-only):
  - issues.createComment, gh pr comment, gh issue comment
"""

import pytest
import yaml
import re
from pathlib import Path
from _cfp2810_crosswalk import (
    MANIFEST, WIRED, CLASS_A_ROWS, resolve_path, COUNT_CLASS_A
)


DISQUALIFYING_MARKERS = [
    r"addLabels",
    r"removeLabels?",
    r"setLabels",
    r"pulls\.update",
    r"issues\.create(?!Comment)",
    r"issues\.update",
    r"git\.createRef",
    r"git\s+(push|commit|tag)",
    r"checks\.create",
]

DISQUALIFYING_PATTERN = "|".join(f"({m})" for m in DISQUALIFYING_MARKERS)


def strip_comments(text):
    """Strip YAML and shell comments before marker matching."""
    lines = []
    for line in text.split('\n'):
        # Remove YAML comments (# after content)
        if '#' in line:
            # Preserve quoted strings
            if '"' not in line and "'" not in line:
                line = line.split('#')[0]
        lines.append(line)
    return '\n'.join(lines)


def has_disqualifying_marker(yaml_text):
    """Check if YAML text contains disqualifying state-mutation markers."""
    clean = strip_comments(yaml_text)
    return bool(re.search(DISQUALIFYING_PATTERN, clean))


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


def test_ac3a_wired_have_github_workflow_in_group(wt_root):
    """
    AC-3(a): Every WIRED workflow's concurrency.group contains ${{ github.workflow }}.
    """
    failures = []
    for row in WIRED:
        if not row["wired"]:
            continue
        try:
            path = wt_root / resolve_path(row)
            wf = load_workflow_yaml(path)
            concurrency = wf.get("concurrency", {})
            group = concurrency.get("group")

            if group is None:
                failures.append(f"{row['name']}: concurrency.group missing")
            elif "${{ github.workflow }}" not in str(group):
                failures.append(f"{row['name']}: github.workflow not in group: {group}")
        except Exception as e:
            failures.append(f"{row['name']}: {e}")

    assert not failures, f"AC-3(a) violations ({len(failures)}):\n" + "\n".join(failures)


def test_ac3b_class_a_no_disqualifying_markers(wt_root):
    """
    AC-3(b): Class-A workflows must NOT contain disqualifying markers.
    """
    assert len(CLASS_A_ROWS) == COUNT_CLASS_A, \
        f"Expected {COUNT_CLASS_A} Class-A rows, got {len(CLASS_A_ROWS)}"

    failures = []
    for row in CLASS_A_ROWS:
        try:
            path = wt_root / resolve_path(row)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            if has_disqualifying_marker(content):
                # Find which markers were found (for debugging)
                markers_found = []
                for marker in DISQUALIFYING_MARKERS:
                    if re.search(marker, content):
                        markers_found.append(marker)

                failures.append(
                    f"{row['name']}: contains disqualifying marker(s): {markers_found}"
                )
        except Exception as e:
            failures.append(f"{row['name']}: {e}")

    assert not failures, f"AC-3(b) Class-A seal violations ({len(failures)}):\n" + "\n".join(failures)


def test_ac3c_positive_control_mutation_kill(wt_root):
    """
    AC-3(c): Positive-control mutation-kill.
    Inject a known disqualifying marker (addLabels) into an in-memory Class-A workflow
    and verify the seal function detects it (returns RED).
    """
    if not CLASS_A_ROWS:
        pytest.skip("No Class-A rows to test mutation kill")

    # Use first Class-A row as test subject
    test_row = CLASS_A_ROWS[0]
    path = wt_root / resolve_path(test_row)

    with open(path, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Create in-memory mutant by injecting addLabels marker in a more realistic context
    # (as it would appear in a GitHub action call)
    mutant_content = original_content + "\n        - uses: actions/github-script@v7\n          with:\n            script: github.rest.issues.addLabels(...)"

    # Verify injection is detected
    assert has_disqualifying_marker(mutant_content), \
        f"Mutation injection failed: 'addLabels' marker not detected in mutant"

    # Verify original was clean (no marker)
    assert not has_disqualifying_marker(original_content), \
        f"Original {test_row['name']} already contains marker before injection"

    # Test passes: the seal detects the injected marker
    assert True, "AC-3(c) mutation kill confirmed: seal detected injected marker"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
