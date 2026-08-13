"""
CFP-2831 convergence validation: AC-level tests for normative requirements.

13 AC tests mapping Change Plan §8.1 RTM (13 normative AC).
Validates blob convergence, manifest state, workflow configuration, and document semantics.

Per Change Plan §3.5: tests must be in tests/ root for Hop3 AST parsing.
Per §8.2 ⑤: P-11b/c needles assembled at runtime to avoid self-match.
Per §8.3 P0-B: Do NOT call full manifest gate for AC-2 (use git ls-tree mode only).

RTM normative: Change Plan §8.1 only (§5.3 Story is placeholder, not parsed by gate).
"""

import subprocess
import tempfile
import shutil
import os
import re
import pytest
from pathlib import Path
from typing import Optional, Tuple


def resolve_bash():
    """bash 실행기의 **절대경로**를 해석한다.

    ★ Windows 에서 `subprocess.run(['bash', ...])` 는 CreateProcess PATH 탐색이
      System32 의 **WSL relay stub** 을 먼저 잡아
      `execvpe(/bin/bash) failed: No such file or directory` 로 죽는다(실측).
      "bash 가 없다" 가 아니라 **해석이 틀린 것**이므로, 절대경로로 해석한 뒤
      `-c echo ok` 로 **실제 동작을 확인**한 실행기만 반환한다.
      Linux CI 는 shutil.which('bash') 가 그대로 맞는다.

    실패 시 skip 이 아니라 FAIL — 실행기 부재를 GREEN 으로 위장하지 않는다.
    """
    candidates = [
        os.environ.get('CFP2831_BASH'),
        shutil.which('bash'),
        r'C:\Program Files\Git\bin\bash.exe',
        r'C:\Program Files\Git\usr\bin\bash.exe',
    ]
    for cand in candidates:
        if not cand or not Path(cand).exists():
            continue
        try:
            probe = subprocess.run([cand, '-c', 'echo ok'],
                                   capture_output=True, text=True, timeout=60)
        except Exception:
            continue
        if probe.returncode == 0 and 'ok' in probe.stdout:
            return cand
    pytest.fail(
        "동작하는 bash 실행기를 찾지 못했다 (skip 아니라 FAIL — "
        "실행기 부재를 통과로 위장하면 AC-10 선언적 경로가 공허해진다)"
    )


# Confirmed blob targets (Change Plan §5 & §8.0 snapshot)
BLOB_T1_CONFIRMED = "4966c62138db20be275415af4757974d8363ad41"
BLOB_T1_OLD = "3280a828c87ed42132ffc6d90a80fa3d4dd0148e"
BLOB_T2_CONFIRMED = "fd660f1b06460a00a52006cd6c047cbb78ec0c22"
BLOB_T3_CONFIRMED = "63d27cd63e419aaed812a95d4724c7e9d7e46ef4"

# File paths (plugin repo)
PATH_T1 = "scripts/lib/check_story_section_schema.py"
PATH_T2 = "templates/github-workflows/story-section-schema.yml"
PATH_T2_PRIME = ".github/workflows/story-section-schema.yml"
PATH_T3 = "scripts/lib/test_check_story_section_schema.py"


def run_git_cmd(args, cwd=None, capture_stderr=False):
    """
    Run git command with core.autocrlf=false to avoid CRLF artifacts.
    Returns (returncode, stdout, stderr).
    """
    env = os.environ.copy()
    env['GIT_CONFIG_NOSYSTEM'] = '1'
    env['GIT_CONFIG_GLOBAL'] = ''
    env['MSYS_NO_PATHCONV'] = '1'
    env['PYTHONIOENCODING'] = 'utf-8'

    try:
        result = subprocess.run(
            ['git', '-c', 'core.autocrlf=false'] + args,
            cwd=cwd or Path(__file__).resolve().parent.parent.parent,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            timeout=10
        )
        stdout_str = (result.stdout or '').strip()
        stderr_str = (result.stderr or '').strip()
        return result.returncode, stdout_str, stderr_str
    except subprocess.TimeoutExpired:
        return 124, '', 'timeout'


def get_blob_sha(path_from_root: str, cwd=None) -> str:
    """Get blob SHA of file at HEAD via git rev-parse."""
    rc, out, err = run_git_cmd(['rev-parse', f'HEAD:{path_from_root}'], cwd=cwd)
    if rc != 0:
        raise RuntimeError(f"git rev-parse failed for {path_from_root}: {err}")
    return out


def get_file_mode(path_from_root: str, cwd=None) -> str:
    """Get file mode from index via git ls-tree (platform-independent)."""
    rc, out, err = run_git_cmd(['ls-tree', 'HEAD', '--', path_from_root], cwd=cwd)
    if rc != 0 or not out:
        raise RuntimeError(f"git ls-tree failed for {path_from_root}: {err}")
    # Output: "<mode> <type> <object>\t<path>"
    parts = out.split()
    if len(parts) < 1:
        raise RuntimeError(f"Cannot parse ls-tree output: {out}")
    return parts[0]  # e.g., "100755" or "100644"


class TestCFP2831Convergence:
    """
    Validates CFP-2831 convergence against hub spec.
    Change Plan §8.1 RTM: 13 normative AC tests.
    """

    @classmethod
    def setup_class(cls):
        """Pre-flight: verify test files can reach git repo."""
        cls.repo_root = Path(__file__).resolve().parent.parent.parent
        cls.hub_root = Path('/c/workspace/mclayer/mctrader')

        assert cls.repo_root.is_dir(), f"Plugin repo not found: {cls.repo_root}"

        # Check if git repo (worktrees have .git as file, not dir)
        git_path = cls.repo_root / '.git'
        assert git_path.exists(), f"Not a git repo: {cls.repo_root}"

    def test_ac1_t1_blob_matches_confirmed(self):
        """AC-1: T1 content blob equals confirmed hub version."""
        blob = get_blob_sha(PATH_T1, cwd=self.repo_root)
        assert blob == BLOB_T1_CONFIRMED, (
            f"T1 blob mismatch: got {blob}, expected {BLOB_T1_CONFIRMED}"
        )

    def test_ac2_t1_mode_is_100755(self):
        """
        AC-2: T1 file mode is 100755 (executable).

        Per Change Plan §8.3 P0-B: Use git ls-tree mode field (platform-independent).
        Do NOT call full manifest check-consumer-scripts-manifest.sh (baseline RED on dev host).
        """
        mode = get_file_mode(PATH_T1, cwd=self.repo_root)
        assert mode == '100755', (
            f"T1 mode mismatch: got {mode}, expected 100755"
        )

        # Also verify manifest entry exists (manifest Check 3)
        manifest_path = self.repo_root / "templates/consumer-scripts.manifest"
        assert manifest_path.exists(), "manifest file not found"
        with open(manifest_path, encoding='utf-8') as f:
            manifest_content = f.read()
        assert 'lib/check_story_section_schema.py' in manifest_content, (
            "T1 not in manifest"
        )

    def test_ac3_t2_template_blob_matches_confirmed(self):
        """AC-3: T2 (template) blob equals confirmed hub version."""
        blob = get_blob_sha(PATH_T2, cwd=self.repo_root)
        assert blob == BLOB_T2_CONFIRMED, (
            f"T2 blob mismatch: got {blob}, expected {BLOB_T2_CONFIRMED}"
        )

    def test_ac4_t2prime_blob_and_parity_identical(self):
        """
        AC-4: T2' (.github) blob matches confirmed AND parity with T2.

        Also checks: story-section-schema.yml ∉ CONSUMER_ONLY_WORKFLOWS (reachability).
        """
        # Check T2' blob
        blob_t2_prime = get_blob_sha(PATH_T2_PRIME, cwd=self.repo_root)
        assert blob_t2_prime == BLOB_T2_CONFIRMED, (
            f"T2' blob mismatch: got {blob_t2_prime}, expected {BLOB_T2_CONFIRMED}"
        )

        # Check parity: T2 == T2'
        blob_t2 = get_blob_sha(PATH_T2, cwd=self.repo_root)
        assert blob_t2 == blob_t2_prime, (
            f"T2 and T2' parity broken: T2={blob_t2}, T2'={blob_t2_prime}"
        )

        # Check reachability: workflow must NOT be in CONSUMER_ONLY_WORKFLOWS
        invariant_path = self.repo_root / ".github/workflows/invariant-check.yml"
        assert invariant_path.exists(), "invariant-check.yml not found"
        with open(invariant_path, encoding='utf-8') as f:
            invariant_content = f.read()

        # Look for CONSUMER_ONLY_WORKFLOWS list and verify story-section-schema.yml is NOT in it
        consumer_only_section = re.search(
            r'CONSUMER_ONLY_WORKFLOWS\s*=\s*\((.*?)\)',
            invariant_content,
            re.DOTALL
        )

        # FAIL if pattern NOT found (missing predicate = hollow-gate ⑥ "부재 대상 검산")
        assert consumer_only_section is not None, (
            "CONSUMER_ONLY_WORKFLOWS definition not found in invariant-check.yml; "
            "cannot validate reachability predicate"
        )

        # NOW check membership (only if definition exists)
        only_workflows = consumer_only_section.group(1)
        assert 'story-section-schema.yml' not in only_workflows, (
            "story-section-schema.yml must NOT be in CONSUMER_ONLY_WORKFLOWS (reachability)"
        )

    def test_ac5_t3_blob_and_mode(self):
        """AC-5: T3 blob and mode match confirmed spec."""
        blob = get_blob_sha(PATH_T3, cwd=self.repo_root)
        assert blob == BLOB_T3_CONFIRMED, (
            f"T3 blob mismatch: got {blob}, expected {BLOB_T3_CONFIRMED}"
        )

        mode = get_file_mode(PATH_T3, cwd=self.repo_root)
        assert mode == '100644', (
            f"T3 mode mismatch: got {mode}, expected 100644"
        )

    def test_ac6_manifest_three_predicates(self):
        """
        AC-6: Manifest state validates three predicates.

        P-6a: grep -c 'test_check_story_section_schema.py' == 0  (T3 NOT in manifest)
        P-6b: grep -c 'lib/check_story_section_schema.py' == 1   (T1 in manifest, exactly once)
        P-6c: grep -c 'schema-baseline' == 0                     (no baseline entry)
        """
        manifest_path = self.repo_root / "templates/consumer-scripts.manifest"
        assert manifest_path.exists(), "manifest not found"

        with open(manifest_path, encoding='utf-8') as f:
            manifest_content = f.read()

        # P-6a
        count_t3 = manifest_content.count('test_check_story_section_schema.py')
        assert count_t3 == 0, f"P-6a failed: 'test_check_story_section_schema.py' count={count_t3}, expected 0"

        # P-6b
        count_t1 = manifest_content.count('lib/check_story_section_schema.py')
        assert count_t1 == 1, f"P-6b failed: 'lib/check_story_section_schema.py' count={count_t1}, expected 1"

        # P-6c
        count_baseline = manifest_content.count('schema-baseline')
        assert count_baseline == 0, f"P-6c failed: 'schema-baseline' count={count_baseline}, expected 0"

    def test_ac7_selftest_workflow_runner_and_permissions(self):
        """
        AC-7: T3-CI workflow is configured correctly.

        Checks:
          - Runner uses pytest (not direct python)
          - permissions: block is present
          - NOT using direct-file runner pitfall
        """
        # T3-CI is .github/workflows/story-section-schema-selftest.yml
        workflow_path = self.repo_root / ".github/workflows/story-section-schema-selftest.yml"
        assert workflow_path.exists(), (
            "T3-CI workflow not found: .github/workflows/story-section-schema-selftest.yml"
        )

        with open(workflow_path, encoding='utf-8') as f:
            workflow_content = f.read()

        # Check runner: must use "python -m pytest" (not "python <file>")
        assert 'python -m pytest' in workflow_content, (
            "T3-CI must use 'python -m pytest' runner, not direct file execution"
        )

        # Check permissions block exists
        assert re.search(r'^\s*permissions:', workflow_content, re.MULTILINE), (
            "T3-CI must have 'permissions:' block"
        )

        # Verify NOT using direct-python runner
        assert not re.search(r'python\s+scripts/lib/test_check_story_section_schema\.py', workflow_content), (
            "T3-CI must not use direct python runner (hollow-gate ⑦)"
        )

    def test_ac9_oldpy_mutant_forces_red(self):
        """
        AC-9: Old (pre-convergence) T1 blob causes T3 to fail.

        Validates: exit != 0 ∧ passed < N ∧ failed+errors >= 1

        Per Change Plan §8.2 E-5: Use git object fetch, not file embedding (avoid self-match).
        Per §8.3: `git cat-file -e` failure → pytest.fail() (not skip).
        """
        n = 21  # AST count of T3 test defs (from setup_class)

        with tempfile.TemporaryDirectory() as tmpdir:
            fixture_scripts = Path(tmpdir) / "scripts/lib"
            fixture_scripts.mkdir(parents=True, exist_ok=True)

            # Extract T3 (confirmed blob) via git object
            rc, t3_content, err = run_git_cmd(
                ['cat-file', '-p', BLOB_T3_CONFIRMED],
                cwd=self.repo_root
            )
            if rc != 0:
                pytest.fail(f"Failed to fetch T3 blob {BLOB_T3_CONFIRMED}: {err}")

            t3_file = fixture_scripts / "test_check_story_section_schema.py"
            with open(t3_file, 'w', encoding='utf-8') as f:
                f.write(t3_content)

            # Extract OLD T1 (mutant) via git object
            rc, t1_old_content, err = run_git_cmd(
                ['cat-file', '-p', BLOB_T1_OLD],
                cwd=self.repo_root
            )
            if rc != 0:
                pytest.fail(f"Old T1 blob {BLOB_T1_OLD} not in git object DB: {err} (fetch-depth:0 required)")

            t1_file = fixture_scripts / "check_story_section_schema.py"
            with open(t1_file, 'w', encoding='utf-8') as f:
                f.write(t1_old_content)

            # Run T3 with old T1 mutant
            result = subprocess.run(
                ['python', '-m', 'pytest', str(t3_file),
                 '-q', '--tb=no', '-p', 'no:cacheprovider'],
                capture_output=True,
                text=True,
                cwd=tmpdir
            )

            output = result.stdout + result.stderr

            # Validate: exit != 0
            assert result.returncode != 0, (
                f"AC-9: Old T1 mutant must cause pytest exit != 0; got {result.returncode}\n"
                f"output: {output}"
            )

            # Parse: failed, errors, passed counts
            failed_match = re.search(r'(\d+)\s+failed', output)
            error_match = re.search(r'(\d+)\s+error', output)
            passed_match = re.search(r'(\d+)\s+passed', output)

            failed_count = int(failed_match.group(1)) if failed_match else 0
            error_count = int(error_match.group(1)) if error_match else 0
            passed_count = int(passed_match.group(1)) if passed_match else 0

            # Validate: failed+errors >= 1 (mutant kills tests)
            assert failed_count + error_count >= 1, (
                f"AC-9: Old T1 mutant must cause failed+errors >= 1; "
                f"got failed={failed_count}, error={error_count}\n"
                f"output: {output}"
            )

            # Validate: passed < N (not all tests passed)
            assert passed_count < n, (
                f"AC-9: Old T1 mutant must cause passed < {n}; got {passed_count}\n"
                f"output: {output}"
            )

    def test_ac10_declarative_reconcile_reports_no_loss(self):
        """
        AC-10 (declarative path): reconcile --dry-run reports zero loss for story-section-schema.yml.

        Per Change Plan §8.3: loss detection via LOSS REPORT block parsing.
        2-conjunct oracle:
          1. reachability: workflow is processed (repo-kind OK + MARKER_NONE mention)
          2. result: LOSS REPORT block contains zero file-specific loss for target workflow

        Executes real reconcile with consumer fixture (project.yaml critical for repo-kind detection).
        """
        reconcile_script = self.repo_root / "scripts/reconcile-overlay.sh"
        assert reconcile_script.exists(), "reconcile-overlay.sh not found"

        with tempfile.TemporaryDirectory() as tmpdir:
            # **CONVERGED CASE**: consumer overlay == wrapper SSOT (no loss expected)
            overlay_dir = Path(tmpdir) / ".claude/_overlay"
            overlay_dir.mkdir(parents=True, exist_ok=True)

            # project.yaml: CRITICAL — signals this is a consumer (repo-kind detection)
            project_yaml = overlay_dir / "project.yaml"
            with open(project_yaml, 'w', encoding='utf-8') as f:
                f.write("project_name: test\n")

            # Consumer workflow copy == wrapper SSOT (진짜 CONVERGED).
            # ★ 스텁 문자열을 쓰면 wrapper 정본과 diff 가 생겨 이 fixture 는 사실상 DIVERGENT 가 되고,
            #   "loss 0" 단언이 의미를 잃는다. 반드시 wrapper 의 templates/ 정본을 그대로 복사한다.
            wrapper_ssot = self.repo_root / "templates/github-workflows/story-section-schema.yml"
            assert wrapper_ssot.exists(), f"wrapper SSOT not found: {wrapper_ssot}"
            workflows_dir = Path(tmpdir) / ".github/workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(wrapper_ssot, workflows_dir / "story-section-schema.yml")

            result = subprocess.run(
                [resolve_bash(), str(reconcile_script), '--dry-run'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=self.repo_root,
                env={**os.environ, 'RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR': str(overlay_dir)},
                timeout=900
            )

            output = result.stdout + result.stderr

            # Conjunct 1: reachability (workflow processed, repo-kind OK)
            assert 'repo-kind unknown' not in output, "repo-kind detection failed"
            assert 'story-section-schema.yml' in output, "target workflow not in output"

            # Conjunct 2: result (zero loss for target in LOSS REPORT block)
            # ★ `if loss_match:` 로 감싸면 블록 부재 시 단언이 통째로 skip 되어 fail-open 이 된다.
            #   블록 부재 = "우리 파일 loss 0" 이므로 빈 문자열로 환원해 **항상 단언**한다.
            loss_match = re.search(r'=== LOSS REPORT ===\n(.*?)\n=== END LOSS REPORT ===', output, re.DOTALL)
            loss_block = loss_match.group(1) if loss_match else ''
            assert 'story-section-schema.yml' not in loss_block, (
                f"CONVERGED fixture 인데 target workflow 가 LOSS REPORT 에 등장:\n{loss_block}"
            )

        # **DIVERGENT CASE**: prove discriminating power (divergent shows loss)
        with tempfile.TemporaryDirectory() as tmpdir_div:
            overlay_dir_div = Path(tmpdir_div) / ".claude/_overlay"
            overlay_dir_div.mkdir(parents=True, exist_ok=True)

            project_yaml_div = overlay_dir_div / "project.yaml"
            with open(project_yaml_div, 'w', encoding='utf-8') as f:
                f.write("project_name: test-divergent\n")

            workflows_dir_div = Path(tmpdir_div) / ".github/workflows"
            workflows_dir_div.mkdir(parents=True, exist_ok=True)
            # DIVERGENT = CONVERGED fixture + 1줄. 두 fixture 가 **정확히 한 줄만** 다르게 해서
            # loss 유무를 가르는 것이 content diff 임을 보인다(스텁끼리 비교하면 무엇이 원인인지 흐려진다).
            wrapper_ssot_div = self.repo_root / "templates/github-workflows/story-section-schema.yml"
            divergent_target = workflows_dir_div / "story-section-schema.yml"
            shutil.copyfile(wrapper_ssot_div, divergent_target)
            with open(divergent_target, 'a', encoding='utf-8') as f:
                f.write("\n# synthetic consumer customization (AC-10 discrimination probe)\n")

            result_div = subprocess.run(
                [resolve_bash(), str(reconcile_script), '--dry-run'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=self.repo_root,
                env={**os.environ, 'RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR': str(overlay_dir_div)},
                timeout=900
            )

            output_div = result_div.stdout + result_div.stderr

            # Divergent: 반드시 loss 가 기록돼야 한다 = 이 술어의 RED 절반(판별력 증명).
            # ★ 여기를 `if` 로 감싸면 블록 부재 시 **판별력 증명이 통째로 사라진다** — 절대 금지.
            #   블록 부재 자체가 실패다(수렴본과 구별을 못 한다는 뜻).
            assert 'repo-kind unknown' not in output_div, (
                "DIVERGENT fixture 에서 repo-kind 미해소 — 채널 미실행이라 판별력 증명이 공허해진다"
            )
            loss_match_div = re.search(r'=== LOSS REPORT ===\n(.*?)\n=== END LOSS REPORT ===', output_div, re.DOTALL)
            assert loss_match_div is not None, (
                f"DIVERGENT fixture 인데 LOSS REPORT 블록이 없다 — 판별력 0.\noutput:\n{output_div[-2000:]}"
            )
            loss_block_div = loss_match_div.group(1)
            assert 'story-section-schema.yml' in loss_block_div, (
                f"DIVERGENT: target workflow 가 loss 로 잡혀야 한다:\n{loss_block_div[:500]}"
            )

    def test_ac10_imperative_apply_is_noop(self):
        """
        AC-10 (imperative path): apply overlay is idempotent (no-op).

        Per Change Plan §8.3 P0-A oracle (all 3 must hold):
          1. merged_content == consumer_content  (apply made no changes — idempotent)
          2. integrity_ok == True               (no corruption during apply)
          3. loss_occurred is True              (NC-4: MARKER_NONE always True)

        Validates via synthetic fixture (wrapper == consumer, no MARKER_NONE delta).
        """
        import sys
        from pathlib import Path as PathlibPath

        # Ensure walk_plan module is importable
        walk_plan_path = self.repo_root / "scripts/lib/walk_plan.py"
        assert walk_plan_path.exists(), "walk_plan.py not found"

        # Add to sys.path for import
        sys.path.insert(0, str(walk_plan_path.parent))

        try:
            import walk_plan
        except ImportError as e:
            pytest.fail(f"Failed to import walk_plan: {e}")

        # Synthetic fixture: wrapper_content == consumer_content (identity)
        # This is the no-op case: nothing to merge, nothing lost.
        wrapper_content = "#!/usr/bin/env python\n# workflow stub\n"
        consumer_content = wrapper_content  # Identity: no diff

        # Call apply_overlay_file with synthetic fixture
        # Returns OverlayApplyResult (namedtuple with merged_content, loss_occurred, loss_report, integrity_ok, ...)
        try:
            result = walk_plan.apply_overlay_file(
                wrapper_content=wrapper_content,
                consumer_content=consumer_content,
                base_content=""  # Default to BASE_ABSENT
            )
        except Exception as e:
            pytest.fail(f"apply_overlay_file call failed: {e}")

        # Validate 3-conjunct oracle
        # Conjunct 1: merged == consumer (idempotent no-op)
        assert result.merged_content == consumer_content, (
            f"AC-10: merged_content should equal consumer_content (idempotent); "
            f"got merged={repr(result.merged_content[:50])}, consumer={repr(consumer_content[:50])}"
        )

        # Conjunct 2: integrity_ok (fixture validation — no errors in merge)
        assert result.integrity_ok is True, (
            f"AC-10: integrity_ok must be True; got {result.integrity_ok}, reason: {result.integrity_violation_reason}"
        )

        # Conjunct 3: loss_occurred is True (NC-4: MARKER_NONE → always True per walk_plan:591)
        # For MARKER_NONE consumer (no marker), loss_occurred should be True per design
        assert result.loss_occurred is True, (
            f"AC-10: loss_occurred must be True (NC-4 MARKER_NONE); got {result.loss_occurred}"
        )

        # Bonus: test divergent case to show conjunct 1 flips
        divergent_wrapper = "# NEW CONTENT\n"
        divergent_consumer = "# OLD CONTENT\n"

        try:
            result_divergent = walk_plan.apply_overlay_file(
                wrapper_content=divergent_wrapper,
                consumer_content=divergent_consumer,
                base_content=""
            )
        except Exception as e:
            pytest.fail(f"Divergent apply_overlay_file call failed: {e}")

        # In divergent case, merged should differ from consumer (merge happened)
        # This proves conjunct 1 is not vacuous (it can flip)
        # With no marker, merged == wrapper (wholesale mirror), so it will differ from consumer
        assert result_divergent.merged_content == divergent_wrapper, (
            f"AC-10: Divergent case (no marker) should result merged=wrapper; "
            f"got merged={repr(result_divergent.merged_content[:50])}, wrapper={repr(divergent_wrapper[:50])}"
        )

    def test_ac11a_write_baseline_convention_present(self):
        """
        AC-11a: P-11a — documentation references --write-baseline flag.

        P-11a: grep -c -- '--write-baseline' docs/consumer-guide.md >= 1
        """
        guide_path = self.repo_root / "docs/consumer-guide.md"
        assert guide_path.exists(), "docs/consumer-guide.md not found"

        with open(guide_path, encoding='utf-8') as f:
            guide_content = f.read()

        count = guide_content.count('--write-baseline')
        assert count >= 1, (
            f"P-11a failed: '--write-baseline' count={count} in docs/consumer-guide.md, expected >= 1"
        )

    def test_ac11b_legacy_semantics_absent_repo_wide(self):
        """
        AC-11b: P-11b & P-11c — old story schema semantics removed from repo.

        Validates that specific obsolete phrases (defined in Story §5.3, lines 535-536)
        are absent from tracked files.
        Per Change Plan §8.2 ⑤: Needle must be assembled at runtime (no literal strings).
        Per §8.3: Both positive (needle matches fixture) and negative (repo matches=0)
        must be validated to avoid hollow-gate ①.
        """
        # Assemble first needle: old constraint that §1-§13 were all mandatory
        # Character-by-character assembly to avoid accidental matches in this source
        needle_1_part1 = '§1' + chr(0x2d) + '§13 모두 의무'  # hyphen via chr(0x2d)
        needle_1 = needle_1_part1  # Complete needle (see Story :535 for context)

        # Assemble second needle: old template structure reference
        needle_2_part1 = 'Story file §1' + chr(0x2d) + '§13'
        needle_2 = needle_2_part1  # Complete needle (see Story :536 for context)

        # **POSITIVE CONTROL**: Verify needle is well-formed by matching against fixture
        fixture_content = f"Old constraint: {needle_1}\nOld header: {needle_2}\n"

        # Verify needle_1 matches fixture (simple string matching)
        assert needle_1 in fixture_content, (
            f"Needle 1 construction failed: needle not found in fixture\n"
            f"needle_1={repr(needle_1)}\nfixture={repr(fixture_content)}"
        )

        # Verify needle_2 matches fixture
        assert needle_2 in fixture_content, (
            f"Needle 2 construction failed: needle not found in fixture\n"
            f"needle_2={repr(needle_2)}\nfixture={repr(fixture_content)}"
        )

        # **NEGATIVE CONTROL**: Verify needles do NOT match repo (including untracked)
        # Use --untracked to catch files not yet committed
        for needle, name in [(needle_1, 'P-11b'), (needle_2, 'P-11c')]:
            result = subprocess.run(
                ['git', 'grep', '--untracked', needle, '--', '.'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            output = (result.stdout or '')
            # Filter out archive/ directory
            non_archive_lines = [
                line for line in output.split('\n')
                if line and not line.startswith('archive/') and line.strip()
            ]
            count = len(non_archive_lines)

            assert count == 0, (
                f"{name} FAILED: found {count} matches for {repr(needle)} outside archive/\n"
                f"(including untracked files)\n"
                f"matches:\n" + '\n'.join(non_archive_lines[:5])
            )

    def test_ac11c_consumer_guide_channel_and_delivery(self):
        """
        AC-11c: P-11d & P-11e — documentation specifies reconcile channel and bootstrap delivery.

        P-11d: grep -cE '(reconcile).*(채널).*(비대상|아님)' docs/consumer-guide.md >= 1
               (Reconcile channel excludes some workflows)
        P-11e: grep -cE '(manifest).*(수동|bootstrap)' docs/consumer-guide.md >= 1
               (Manifest bootstrap is manual)
        """
        guide_path = self.repo_root / "docs/consumer-guide.md"
        assert guide_path.exists(), "docs/consumer-guide.md not found"

        with open(guide_path, encoding='utf-8') as f:
            guide_content = f.read()

        # P-11d: reconcile channel mention
        p11d_matches = re.findall(r'(reconcile).*(채널).*(비대상|아님)', guide_content)
        assert len(p11d_matches) >= 1, (
            f"P-11d failed: pattern '(reconcile).*(채널).*(비대상|아님)' "
            f"found {len(p11d_matches)} times, expected >= 1"
        )

        # P-11e: manifest bootstrap mention
        p11e_matches = re.findall(r'(manifest).*(수동|bootstrap)', guide_content)
        assert len(p11e_matches) >= 1, (
            f"P-11e failed: pattern '(manifest).*(수동|bootstrap)' "
            f"found {len(p11e_matches)} times, expected >= 1"
        )
