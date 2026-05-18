# -*- coding: utf-8 -*-
"""
tests/test_mirror_dependency_closure.py

CFP-898 Phase 2 — 15 TC unit tests for mirror-dependency-closure.py
TC-DEP-1~15 per Story §8.1 (Architect Phase 1, internal-docs commit b042469)

TDD order: RED first (all tests must fail before implementation)
pytest framework (ADR-005 정합)
"""

import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Test fixture helpers
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_PATH = Path(__file__).parent.parent / "templates" / "scripts" / "mirror-dependency-closure.py"


def run_script(*args, extra_env=None):
    """Run mirror-dependency-closure.py and return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def make_yml(content: str, suffix=".yml") -> str:
    """Write a temp workflow yml and return its path (caller must cleanup)."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return tmp.name


def make_sh(name: str, tmpdir: Path) -> Path:
    """Create a dummy shell script at tmpdir/name."""
    p = tmpdir / name
    p.write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
    return p


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-1: closure resolve happy path — scripts/check-foo.sh present
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_1_closure_happy_path_shell_script(tmp_path):
    """TC-DEP-1: yml references scripts/check-foo.sh which exists → exit 0."""
    (tmp_path / "scripts").mkdir(exist_ok=True)
    sh = make_sh("check-foo.sh", tmp_path / "scripts")

    yml_content = textwrap.dedent(f"""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: run check
                run: bash scripts/check-foo.sh
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 0, f"Expected exit 0, got {rc}. stderr={stderr}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-2: closure resolve happy path — templates/scripts/bar.py present
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_2_closure_happy_path_py_script(tmp_path):
    """TC-DEP-2: yml references templates/scripts/bar.py which exists → exit 0."""
    (tmp_path / "templates" / "scripts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "templates" / "scripts" / "bar.py").write_text(
        "#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8"
    )
    yml_content = textwrap.dedent(f"""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: run py
                run: python3 templates/scripts/bar.py
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 0, f"Expected exit 0, got {rc}. stderr={stderr}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-3: closure resolve happy path — mixed sh + py both present
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_3_closure_happy_path_mixed(tmp_path):
    """TC-DEP-3: yml references both scripts/check-foo.sh and templates/scripts/bar.py → exit 0."""
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "check-foo.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    (tmp_path / "templates" / "scripts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "templates" / "scripts" / "bar.py").write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: run both
                run: |
                  bash scripts/check-foo.sh
                  python3 templates/scripts/bar.py
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 0, f"Expected exit 0, got {rc}. stderr={stderr}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-4: fail-closed — scripts/check-X.sh missing
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_4_fail_closed_missing_shell_script(tmp_path):
    """TC-DEP-4: yml references scripts/check-missing.sh which does NOT exist → exit 1."""
    # Do NOT create the script — intentional missing
    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: run check
                run: bash scripts/check-missing.sh
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 1, f"Expected exit 1 (fail-closed), got {rc}. stdout={stdout}"
        assert "scripts/check-missing.sh" in stdout + stderr
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-5: fail-closed — templates/scripts/Y.py missing
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_5_fail_closed_missing_py_script(tmp_path):
    """TC-DEP-5: yml references templates/scripts/missing.py which does NOT exist → exit 1."""
    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: run py
                run: python3 templates/scripts/missing.py
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 1, f"Expected exit 1 (fail-closed), got {rc}. stdout={stdout}"
        assert "templates/scripts/missing.py" in stdout + stderr
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-6: fail-closed — both scripts/check-X.sh AND templates/scripts/Y.py missing
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_6_fail_closed_both_missing(tmp_path):
    """TC-DEP-6: yml references both missing deps → exit 1, both reported."""
    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: run
                run: |
                  bash scripts/check-alpha.sh
                  python3 templates/scripts/beta.py
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 1, f"Expected exit 1, got {rc}"
        combined = stdout + stderr
        assert "scripts/check-alpha.sh" in combined
        assert "templates/scripts/beta.py" in combined
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-7: dry-run mode — exit 0 + preview log even when deps missing
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_7_dry_run_exits_zero_with_preview(tmp_path):
    """TC-DEP-7: --dry-run → exit 0 regardless of missing deps + preview log."""
    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - run: bash scripts/check-not-exist.sh
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            "--dry-run",
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 0, f"dry-run must exit 0, got {rc}. stderr={stderr}"
        combined = stdout + stderr
        assert "[dry-run]" in combined
        assert "scripts/check-not-exist.sh" in combined
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-8: transitive depth limit — 1 hop only (AM-2)
# Script A calls script B; B is present, but B's own deps are irrelevant
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_8_transitive_depth_limit_one_hop(tmp_path):
    """TC-DEP-8: only direct deps (1 hop) are checked; transitive deps of deps are not."""
    # Create scripts/check-a.sh (direct dep — present)
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "check-a.sh").write_text(
        "#!/usr/bin/env bash\nbash scripts/check-b.sh\n", encoding="utf-8"
    )
    # scripts/check-b.sh is NOT created (transitive dep — should NOT be checked)

    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - run: bash scripts/check-a.sh
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        # check-a.sh is present → exit 0 (check-b.sh is not analyzed as it's depth>1)
        assert rc == 0, f"Expected exit 0 (1-hop only), got {rc}. stderr={stderr}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-9: self-app verify — mirror-dependency-closure.py must NOT reference itself
# (AM-4: self_app_exemption — self-loop 0 invariant)
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_9_self_app_no_self_loop():
    """TC-DEP-9: mirror-dependency-closure.py must not reference itself as a dependency."""
    if not SCRIPT_PATH.exists():
        pytest.skip("Script not yet created (RED phase)")
    content = SCRIPT_PATH.read_text(encoding="utf-8")
    # The script must not contain a reference to itself as a dep to check
    # (i.e., it should not call itself via subprocess or list itself as dep)
    assert "mirror-dependency-closure" not in content.lower() or \
           "__file__" in content, \
        "Script must not reference itself as a dependency (AM-4 self-loop invariant)"


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-10: edge case — symlink to existing script → treated as present (exit 0)
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Symlink creation requires SeCreateSymbolicLinkPrivilege on Windows (Developer Mode or admin). "
           "Behavior is platform-identical: Path.exists() follows symlinks on all platforms.",
)
def test_dep_10_symlink_treated_as_present(tmp_path):
    """TC-DEP-10: symlink to an existing script is treated as present → exit 0."""
    (tmp_path / "scripts").mkdir(exist_ok=True)
    real = tmp_path / "scripts" / "check-real.sh"
    real.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    link = tmp_path / "scripts" / "check-link.sh"
    link.symlink_to(real)

    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - run: bash scripts/check-link.sh
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 0, f"Symlink should be treated as present, got {rc}. stderr={stderr}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-11: edge case — cyclic dependency hypothetical (A→B→A)
# Script scope only checks yml references, not script internals → exit 0 if both present
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_11_cyclic_dependency_not_followed(tmp_path):
    """TC-DEP-11: cyclic A→B→A in script internals does not cause infinite loop (1-hop only)."""
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / "check-a.sh").write_text(
        "#!/usr/bin/env bash\nbash scripts/check-b.sh\n", encoding="utf-8"
    )
    (tmp_path / "scripts" / "check-b.sh").write_text(
        "#!/usr/bin/env bash\nbash scripts/check-a.sh\n", encoding="utf-8"
    )
    # yml only references check-a.sh (direct); check-b.sh is depth-2 → not checked
    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - run: bash scripts/check-a.sh
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 0, f"Cyclic deps inside scripts should not be followed (1-hop), got {rc}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-12: edge case — comment-only mention is NOT a false positive
# YAML comment lines (# scripts/check-foo.sh) must not be treated as dependency references
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_12_comment_only_not_false_positive(tmp_path):
    """TC-DEP-12: scripts path in YAML comment line must not trigger dependency check."""
    # scripts/check-commented.sh does NOT exist
    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: example
                # This step used to run: bash scripts/check-commented.sh
                run: echo "no actual dep"
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        # Comment-only mention should not trigger failure
        assert rc == 0, f"Comment mention must not be a false positive, got {rc}. stdout={stdout}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-13: negative case — yml parse error → exit 2
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_13_yml_parse_error_exits_2(tmp_path):
    """TC-DEP-13: malformed yml with unclosed Jinja/flow braces → exit 2 (abort).

    Triggers _MALFORMED_PATTERNS: unclosed `{{ ... ` without closing `}}` on same line.
    Note: `name: [...]` inline sequences are valid GitHub Actions YAML (F-5 FIX iter 1).
    Only the `{{[^}]*$` pattern (unclosed Jinja template) triggers exit 2.
    """
    # `{{ invalid` (unclosed) triggers the heuristic → exit 2
    malformed = "name: workflow\non: push\njobs:\n  check:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo {{ invalid"
    yml_path = make_yml(malformed)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 2, f"Parse error must exit 2 (abort), got {rc}. stdout={stdout} stderr={stderr}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-14: negative case — dynamic fetch (curl/wget) is out-of-scope
# Dynamically fetched scripts are not tracked by dependency closure (shell_script_only_v1)
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_14_dynamic_fetch_out_of_scope(tmp_path):
    """TC-DEP-14: curl/wget fetched script is out-of-scope → no false positive, exit 0."""
    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: fetch and run
                run: |
                  curl -fsSL https://example.com/some-script.sh | bash
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        # No local path reference → nothing to check → exit 0
        assert rc == 0, f"Dynamic fetch is out-of-scope, should exit 0, got {rc}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-15: negative case — runtime dep (npm package, pip package) is out-of-scope
# Only shell_script_only_v1 scope (scripts/check-*.sh + templates/scripts/*.py)
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_15_runtime_dep_out_of_scope(tmp_path):
    """TC-DEP-15: runtime package deps (pip/npm) are out-of-scope → no false positive, exit 0."""
    yml_content = textwrap.dedent("""\
        name: test-workflow
        on: push
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: install and run
                run: |
                  pip install some-package
                  npm install -g some-tool
                  some-tool --check
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 0, f"Runtime deps are out-of-scope, should exit 0, got {rc}"
    finally:
        os.unlink(yml_path)


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEP-Trigger-1: F-5 regression guard — GitHub Actions inline sequence
# `types: [opened, synchronize, ...]` is valid YAML, must NOT trigger exit 2
# (F-5 FIX iter 1 — _MALFORMED_PATTERNS first pattern removed)
# ─────────────────────────────────────────────────────────────────────────────
def test_dep_trigger_1_github_actions_inline_sequence_not_false_positive(tmp_path):
    """TC-DEP-Trigger-1: valid GitHub Actions yml with inline sequence triggers → exit 0.

    Regression guard for F-5 (_MALFORMED_PATTERNS false-positive fix).
    `types: [opened, synchronize, reopened, labeled, unlabeled]` is valid YAML.
    `branches: [main, develop]` is valid YAML.
    These must NOT be treated as malformed YAML (old first pattern `^\\s*\\w+:\\s*\\[`).
    """
    yml_content = textwrap.dedent("""\
        name: test-pull-request-workflow
        on:
          pull_request:
            types: [opened, synchronize, reopened, labeled, unlabeled]
            branches: [main, develop]
        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - name: lint check
                run: echo "no local dep script here"
    """)
    yml_path = make_yml(yml_content)
    try:
        rc, stdout, stderr = run_script(
            "--yml", yml_path,
            extra_env={"MIRROR_DEP_WRAPPER_ROOT": str(tmp_path)},
        )
        assert rc == 0, (
            f"Valid GitHub Actions inline sequence must not be a false positive (F-5), "
            f"got exit {rc}. stderr={stderr}"
        )
    finally:
        os.unlink(yml_path)
