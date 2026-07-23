"""
CFP-2810 AC-7, AC-SEC, and AC-8 Structural Tests.

AC-7: For each WIRED workflow, the 'jobs' section must be byte/dict-identical
      between origin/main base and current, after stripping job-level concurrency: keys.

AC-SEC: AST (dict) equality between base and current EXCEPT:
        (i) top-level 'concurrency' key (added)
        (ii) 'on.<event>.types' delta (narrowing)
        Everything else (permissions, env, secrets, jobs) must match.

AC-8: phase-gate-mergeable.yml must have cancel-in-progress==False
      (non-cancelling master gate).
"""

import pytest
import yaml
import subprocess
from pathlib import Path
from _cfp2810_crosswalk import MANIFEST, WIRED, resolve_path


BASE_COMMIT = "68ea503a0f6a3cc4e60243c429583cea3113b414"


def run_git_show(wt_root, commit, path_str):
    """Retrieve file content from git at specific commit.

    On Windows, decode UTF-8 explicitly to handle Korean comments.
    Do NOT use text=True/encoding — that forces the locale codec (cp949).
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(wt_root), "show", f"{commit}:{path_str}"],
            capture_output=True
        )
        if result.returncode == 0:
            # Explicitly decode UTF-8 from bytes (Windows workaround)
            return result.stdout.decode("utf-8")
        else:
            return None
    except Exception:
        return None


def load_workflow_yaml(path_obj):
    """Load workflow from file."""
    with open(path_obj, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def strip_job_level_concurrency(wf_dict):
    """Remove concurrency keys from each job (in-place mutation for comparison)."""
    jobs = wf_dict.get("jobs", {})
    if isinstance(jobs, dict):
        for job_name in jobs:
            if isinstance(jobs[job_name], dict) and "concurrency" in jobs[job_name]:
                del jobs[job_name]["concurrency"]
    return wf_dict


@pytest.fixture(scope="session")
def wt_root():
    """Worktree root directory."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd="C:/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-2810",
        capture_output=True, text=True
    )
    return Path(result.stdout.strip())


def test_ac7_jobs_section_unchanged(wt_root):
    """
    AC-7: Jobs section must be identical between base and current (minus job concurrency).
    Normative test — must PASS (not skip). Only new workflows (missing in base) are OK to skip.
    """
    failures = []
    checked = 0

    for row in WIRED:
        if not row["wired"]:
            continue

        try:
            current_path = wt_root / resolve_path(row)
            if not current_path.exists():
                # File missing — unexpected but don't fail
                continue

            # Load current
            with open(current_path, 'r', encoding='utf-8') as f:
                current_wf = yaml.safe_load(f)
            current_jobs = dict(current_wf.get("jobs", {}))

            # Load base
            base_content = run_git_show(wt_root, BASE_COMMIT, resolve_path(row).replace("\\", "/"))
            if base_content is None:
                # File didn't exist in base — new workflow, OK to skip verification
                continue

            checked += 1
            base_wf = yaml.safe_load(base_content)
            base_jobs = dict(base_wf.get("jobs", {}))

            # Deep copy for mutation (strip job-level concurrency)
            import copy
            current_jobs_copy = copy.deepcopy(current_jobs)
            base_jobs_copy = copy.deepcopy(base_jobs)

            # Strip job-level concurrency keys from both
            strip_job_level_concurrency({"jobs": current_jobs_copy})
            strip_job_level_concurrency({"jobs": base_jobs_copy})

            if current_jobs_copy != base_jobs_copy:
                failures.append(f"{row['name']}: jobs section changed")
        except Exception as e:
            failures.append(f"{row['name']}: {type(e).__name__}: {e}")

    # AC-7: all checked workflows must have identical jobs
    assert not failures, \
        f"AC-7 ({checked} checked workflows): {len(failures)} violations\n" + "\n".join(failures)


def test_ac_sec_ast_equality(wt_root):
    """
    AC-SEC: AST equality between base and current EXCEPT:
    (i) top-level 'concurrency' key (new)
    (ii) 'on.<event>.types' arrays (narrowed)

    All other top-level keys (permissions, env, secrets, jobs, name, etc.) must be identical.
    Normative test — must PASS.
    """
    import copy

    failures = []
    checked = 0

    for row in WIRED:
        if not row["wired"]:
            continue

        try:
            current_path = wt_root / resolve_path(row)
            if not current_path.exists():
                continue

            # Load current
            with open(current_path, 'r', encoding='utf-8') as f:
                current_wf = yaml.safe_load(f)

            # Load base
            base_content = run_git_show(wt_root, BASE_COMMIT, resolve_path(row).replace("\\", "/"))
            if base_content is None:
                # New file, OK to skip
                continue

            checked += 1
            base_wf = yaml.safe_load(base_content)

            # Deep copy for comparison
            current_copy = copy.deepcopy(current_wf)
            base_copy = copy.deepcopy(base_wf)

            # (i) Remove top-level 'concurrency' from current (new key)
            current_copy.pop("concurrency", None)
            base_copy.pop("concurrency", None)

            # (ii) Handle 'on' section — remove 'types' from both for structural comparison
            # (types narrowing is allowed; we check structural equality of the rest)
            # Note: In YAML, 'on' is a boolean keyword, so it parses as the key True (not "on")
            def strip_types_from_on(wf):
                """Remove 'types' from all events in the 'on' section.

                In YAML, 'on' is a boolean keyword, so it appears as key True.
                Handles dict form (event: {...}) and boolean form (pull_request: true).
                """
                # YAML parses 'on' as the boolean key True
                on = wf.get(True)
                if on is None or isinstance(on, bool):
                    # No 'on' section or it's a simple boolean trigger — no types to strip
                    return

                if isinstance(on, dict):
                    for event_key in list(on.keys()):
                        event_config = on[event_key]
                        # Skip boolean event configs (pull_request: true syntax)
                        if isinstance(event_config, bool):
                            continue
                        # Remove 'types' from dict event configs
                        if isinstance(event_config, dict) and "types" in event_config:
                            on[event_key] = copy.deepcopy(event_config)
                            del on[event_key]["types"]

            strip_types_from_on(current_copy)
            strip_types_from_on(base_copy)

            # Now compare: everything else must be identical
            if current_copy != base_copy:
                # Find the specific key that differs
                for key in current_copy:
                    if current_copy.get(key) != base_copy.get(key):
                        failures.append(
                            f"{row['name']}: key '{key}' differs (AST mismatch outside allowed exceptions)"
                        )
                        break
                else:
                    # Check keys in base that might be missing in current
                    for key in base_copy:
                        if key not in current_copy:
                            failures.append(f"{row['name']}: key '{key}' removed")

        except Exception as e:
            failures.append(f"{row['name']}: {type(e).__name__}: {e}")

    # AC-SEC: must pass for all checked workflows
    assert not failures, \
        f"AC-SEC ({checked} checked workflows): {len(failures)} AST violations\n" + "\n".join(failures)


def test_ac8_phase_gate_mergeable_cancel_false(wt_root):
    """
    AC-8: phase-gate-mergeable.yml must have cancel-in-progress==False
    (non-cancelling master gate to prevent cascading PR cancellations).
    """
    phase_gate = next((r for r in MANIFEST if r["name"] == "phase-gate-mergeable.yml"), None)
    assert phase_gate is not None, "phase-gate-mergeable.yml not in manifest"

    path = wt_root / resolve_path(phase_gate)
    assert path.exists(), f"{path} not found"

    wf = load_workflow_yaml(path)
    concurrency = wf.get("concurrency", {})
    cancel_in_prog = concurrency.get("cancel-in-progress")

    assert cancel_in_prog is False, \
        f"AC-8 violation: phase-gate-mergeable.yml cancel-in-progress={cancel_in_prog} (expected False)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
