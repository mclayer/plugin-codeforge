"""
test_cfp_478_workflow_dryrun.py
CFP-478 Phase 2 sub-PR b — Workflow dry-run test dispatch
ADR-061 Amendment 1 §결정 1.B (no Python heredoc > 5 lines)

Dispatches per-block dry-run tests for all 8 workflow blocks migrated in sub-PR b.
Each block: fixed input env → expected stdout byte-identical (or file-based) comparison.

Exit code: 0 = all 8 PASS, 1 = any FAIL
"""
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
FIXTURES = REPO_ROOT / "tests/fixtures/cfp-478"
SCRIPTS_LIB = REPO_ROOT / "scripts/lib"

PASS = "PASS"
FAIL = "FAIL"


def run_script(script: str, env_extra: dict) -> tuple[int, str, str]:
    """Run a Python script with extended environment, return (returncode, stdout, stderr)."""
    env = {**os.environ, **env_extra}
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_LIB / script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        cwd=str(REPO_ROOT),
    )
    return result.returncode, result.stdout, result.stderr


def load_env(env_path: Path) -> dict:
    """Load KEY=VALUE pairs from an .env file."""
    env = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def assert_stdout(label: str, actual: str, expected_path: Path) -> str:
    expected = expected_path.read_text(encoding="utf-8")
    if actual == expected:
        print(f"  [{PASS}] {label} — stdout byte-identical")
        return PASS
    else:
        print(f"  [{FAIL}] {label} — stdout MISMATCH")
        print(f"    expected: {repr(expected[:120])}")
        print(f"    actual  : {repr(actual[:120])}")
        return FAIL


def test_block_24() -> str:
    """Block #24 — story_key_prefix extraction"""
    env = load_env(FIXTURES / "workflow_block_24/input.env")
    rc, stdout, stderr = run_script("workflow_story_init_project_config_key_prefix.py", env)
    if rc != 0:
        print(f"  [{FAIL}] block_24 — exit {rc}: {stderr[:120]}")
        return FAIL
    return assert_stdout("block_24 key_prefix", stdout, FIXTURES / "workflow_block_24/expected_stdout.txt")


def test_block_25() -> str:
    """Block #25 — project_name extraction"""
    env = load_env(FIXTURES / "workflow_block_25/input.env")
    rc, stdout, stderr = run_script("workflow_story_init_project_config_name.py", env)
    if rc != 0:
        print(f"  [{FAIL}] block_25 — exit {rc}: {stderr[:120]}")
        return FAIL
    return assert_stdout("block_25 project_name", stdout, FIXTURES / "workflow_block_25/expected_stdout.txt")


def test_block_17() -> str:
    """Block #17 — compute key/slug/title_clean"""
    env = load_env(FIXTURES / "workflow_block_17/input.env")
    rc, stdout, stderr = run_script("workflow_story_init_compute_key.py", env)
    if rc != 0:
        print(f"  [{FAIL}] block_17 — exit {rc}: {stderr[:120]}")
        return FAIL
    return assert_stdout("block_17 compute_key", stdout, FIXTURES / "workflow_block_17/expected_stdout.txt")


def test_block_15() -> str:
    """Block #15 — render Story file content"""
    env = load_env(FIXTURES / "workflow_block_15/input.env")
    rc, stdout, stderr = run_script("workflow_story_init_render_story.py", env)
    if rc != 0:
        print(f"  [{FAIL}] block_15 — exit {rc}: {stderr[:120]}")
        return FAIL
    return assert_stdout("block_15 render_story", stdout, FIXTURES / "workflow_block_15/expected_stdout.txt")


def test_block_18() -> str:
    """Block #18 — Extract Story §1 section (workflow_section1_verbatim_postmerge_a)"""
    fixture_dir = FIXTURES / "workflow_block_18"
    story_src = fixture_dir / "story_CFP-TEST-001.md"
    # Script reads from docs/stories/<KEY>.md relative to cwd (REPO_ROOT)
    story_dst = REPO_ROOT / "docs/stories/CFP-TEST-001.md"
    story_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(story_src, story_dst)

    tmp_out = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    tmp_out.close()
    try:
        env = {"KEY": "CFP-TEST-001", "GITHUB_OUTPUT": tmp_out.name}
        rc, stdout, stderr = run_script("workflow_section1_verbatim_postmerge_a.py", env)
        if rc != 0:
            print(f"  [{FAIL}] block_18 — exit {rc}: {stderr[:120]}")
            return FAIL
        # Verify /tmp/story-section-1.txt written correctly
        section_file = Path("/tmp/story-section-1.txt")
        if not section_file.exists():
            print(f"  [{FAIL}] block_18 — /tmp/story-section-1.txt not written")
            return FAIL
        actual = section_file.read_text(encoding="utf-8")
        expected = (fixture_dir / "expected_section.txt").read_text(encoding="utf-8")
        if actual == expected:
            print(f"  [{PASS}] block_18 — §1 section extraction byte-identical")
            return PASS
        else:
            print(f"  [{FAIL}] block_18 — section MISMATCH")
            print(f"    expected: {repr(expected[:80])}")
            print(f"    actual  : {repr(actual[:80])}")
            return FAIL
    finally:
        os.unlink(tmp_out.name)
        if story_dst.exists():
            story_dst.unlink()


def test_block_21() -> str:
    """Block #21 — Extract Issue body §1 section (workflow_section1_verbatim_postmerge_b)"""
    fixture_dir = FIXTURES / "workflow_block_21"
    issue_body = (fixture_dir / "issue_body.txt").read_text(encoding="utf-8")
    # Script reads from /tmp/issue-body.txt
    Path("/tmp/issue-body.txt").write_text(issue_body, encoding="utf-8")

    tmp_out = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    tmp_out.close()
    try:
        env = {"GITHUB_OUTPUT": tmp_out.name}
        rc, stdout, stderr = run_script("workflow_section1_verbatim_postmerge_b.py", env)
        if rc != 0:
            print(f"  [{FAIL}] block_21 — exit {rc}: {stderr[:120]}")
            return FAIL
        section_file = Path("/tmp/issue-section-1.txt")
        if not section_file.exists():
            print(f"  [{FAIL}] block_21 — /tmp/issue-section-1.txt not written")
            return FAIL
        actual = section_file.read_text(encoding="utf-8")
        expected = (fixture_dir / "expected_section.txt").read_text(encoding="utf-8")
        if actual == expected:
            print(f"  [{PASS}] block_21 — Issue §1 section extraction byte-identical")
            return PASS
        else:
            print(f"  [{FAIL}] block_21 — section MISMATCH")
            print(f"    expected: {repr(expected[:80])}")
            print(f"    actual  : {repr(actual[:80])}")
            return FAIL
    finally:
        os.unlink(tmp_out.name)


def test_block_23() -> str:
    """Block #23 — security_ai config read (workflow_post_merge_followup)"""
    env = load_env(FIXTURES / "workflow_block_23/input.env")
    rc, stdout, stderr = run_script("workflow_post_merge_followup.py", env)
    if rc != 0:
        print(f"  [{FAIL}] block_23 — exit {rc}: {stderr[:120]}")
        return FAIL
    return assert_stdout("block_23 security_ai", stdout, FIXTURES / "workflow_block_23/expected_stdout.txt")


def test_block_26() -> str:
    """Block #26 — Extract expected contexts from branch-protection manifest"""
    env = load_env(FIXTURES / "workflow_block_26/input.env")
    rc, stdout, stderr = run_script("workflow_branch_protection_drift_check.py", env)
    if rc != 0:
        print(f"  [{FAIL}] block_26 — exit {rc}: {stderr[:120]}")
        return FAIL
    # Verify /tmp/expected_contexts.txt written correctly
    contexts_file = Path("/tmp/expected_contexts.txt")
    if not contexts_file.exists():
        print(f"  [{FAIL}] block_26 — /tmp/expected_contexts.txt not written")
        return FAIL
    actual = contexts_file.read_text(encoding="utf-8")
    expected = (FIXTURES / "workflow_block_26/expected_contexts.txt").read_text(encoding="utf-8")
    if actual == expected:
        print(f"  [{PASS}] block_26 — expected contexts byte-identical")
        return PASS
    else:
        print(f"  [{FAIL}] block_26 — contexts MISMATCH")
        print(f"    expected: {repr(expected[:120])}")
        print(f"    actual  : {repr(actual[:120])}")
        return FAIL


def main() -> None:
    # Ensure UTF-8 stdout for Korean/special chars (Windows compat)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("CFP-478 Phase 2 sub-PR b -- workflow dry-run test suite (8 blocks)")
    print("=" * 64)

    tests = [
        ("block_24", test_block_24),
        ("block_25", test_block_25),
        ("block_17", test_block_17),
        ("block_15", test_block_15),
        ("block_18", test_block_18),
        ("block_21", test_block_21),
        ("block_23", test_block_23),
        ("block_26", test_block_26),
    ]

    results = {}
    for name, fn in tests:
        print(f"\nRunning {name}...")
        results[name] = fn()

    print("\n" + "=" * 64)
    passed = sum(1 for r in results.values() if r == PASS)
    failed = sum(1 for r in results.values() if r == FAIL)
    print(f"Results: {passed}/8 PASS, {failed}/8 FAIL")
    for name, result in results.items():
        print(f"  {result:4s} {name}")

    if failed > 0:
        sys.exit(1)
    print("\nAll 8 workflow block dry-runs PASS.")


if __name__ == "__main__":
    main()
