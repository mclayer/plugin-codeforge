"""
CFP-2831 convergence validation: AC-level tests for normative requirements.

13 AC tests mapping Change Plan §8.1 RTM (13 normative AC).
Validates blob convergence, manifest state, workflow configuration, and document semantics.

Per Change Plan §3.5: tests must be in tests/ root for Hop3 AST parsing.
Per §8.2 ⑤: P-11b/c needles assembled at runtime to avoid self-match.
Per §8.3 P0-B: Do NOT call full manifest gate for AC-2 (use git ls-tree mode only).

RTM normative: Change Plan §8.1 only (§5.3 Story is placeholder, not parsed by gate).
"""

import ast
import subprocess
import sys
import tempfile
import shutil
import os
import re
import pytest
from pathlib import Path


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
WORKFLOW_BASENAME = "story-section-schema.yml"


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
        # ★ N 은 **상수 금지**(CP §8.1) — T3 소스를 ast 로 파싱해 산출한다.
        #   harness(:42-49) · T3-CI(:66-70) 와 동일 산출식이어야 3좌표가 대칭이다.
        #   (종전 판은 `n = 21` 상수였고 "from setup_class" 주석도 거짓이었다 — setup_class 는 N 을 산출하지 않는다.)
        t3_src_path = self.repo_root / PATH_T3
        assert t3_src_path.exists(), f"T3 not found for AST count: {t3_src_path}"
        with open(t3_src_path, encoding='utf-8') as _fh:
            _t3_tree = ast.parse(_fh.read())
        n = sum(
            1 for _node in ast.walk(_t3_tree)
            if isinstance(_node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and _node.name.startswith('test')
        )
        assert n > 0, "AST 로 T3 test def 0건 — 하네스 파손"

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
                [sys.executable, '-m', 'pytest', str(t3_file),
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

    def _run_reconcile_hermetic(self, tmpdir, consumer_bytes):
        """격리 fixture 에서 `reconcile-overlay.sh --dry-run` 을 돌리고 stdout+stderr 를 반환한다.

        ★ seam 을 **전부** 주입한다. 하나라도 빠지면 스크립트가 기본값으로
          **실 repo 의 templates/github-workflows(88 파일)** 와 **$HOME/.claude/_snapshots**
          를 걷는다. 그 결과:
            (i) 개발자 홈의 실 snapshot 유무가 `_base_state` 분기를 바꿔 **판정이 환경의 함수**가 된다
                (= 비-hermetic. 성능 문제가 아니라 격리 문제다)
            (ii) walk 가 O(88) 로 커져 이 호스트에서 900s 를 넘겼다
          선례 = `tests/scripts/test_reconcile-overlay-workflow-channel.sh:57-61` 동형 주입.
        """
        base = Path(tmpdir)
        wrapper_overlay = base / "wrapper/.claude/_overlay"
        src_dir = base / "wrapper/templates/github-workflows"
        wl_dir = base / "wrapper/templates/scripts"
        consumer = base / "consumer"
        overlay = consumer / ".claude/_overlay"
        dst_dir = consumer / ".github/workflows"
        snapshot = base / "snapshots"
        for d in (wrapper_overlay, src_dir, wl_dir, overlay, dst_dir, snapshot):
            d.mkdir(parents=True, exist_ok=True)

        # wrapper SSOT = 우리 파일 1건만 넣어 walk 를 O(1) 로 만든다
        wrapper_ssot = self.repo_root / PATH_T2
        assert wrapper_ssot.exists(), f"wrapper SSOT not found: {wrapper_ssot}"
        shutil.copyfile(wrapper_ssot, src_dir / WORKFLOW_BASENAME)

        whitelist = wl_dir / "consumer_applicable_workflows.txt"
        whitelist.write_text(WORKFLOW_BASENAME + "\n", encoding="utf-8")
        (overlay / "project.yaml").write_text(
            "name: cfp2831-test-consumer\n", encoding="utf-8")
        (dst_dir / WORKFLOW_BASENAME).write_bytes(consumer_bytes)

        # ★ POSIX(forward-slash) 경로로 넘긴다 — `str(Path)` 은 Windows 에서 역슬래시를 주고,
        #   그러면 스크립트의 rel_path 접두 제거(`${p#$base/}`)가 실패해 rel_path 가 **절대경로**가
        #   된다. 그 결과 consumer_file 을 못 찾아 `had_consumer_diff=false` 로 떨어지고
        #   **divergent 인데 loss 0** 이 나온다(= 수렴본과 구별 불가 = 판별력 0).
        #   실측 증상: `MARKER_NONE wholesale: C:\...\github-workflows/story-section-schema.yml`
        #   converged 쪽도 "내용이 같아서" 가 아니라 "파일을 못 찾아서" 통과하는 공허 GREEN 이었다.
        env = {
            **os.environ,
            'RECONCILE_OVERLAY_WORKFLOW_SRC_DIR': src_dir.as_posix(),
            'RECONCILE_OVERLAY_WORKFLOW_DST_DIR': dst_dir.as_posix(),
            'RECONCILE_OVERLAY_SNAPSHOT_DIR': snapshot.as_posix(),
            'RECONCILE_OVERLAY_WRAPPER_DIR': wrapper_overlay.as_posix(),
            'RECONCILE_OVERLAY_CONSUMER_OVERLAY_DIR': overlay.as_posix(),
            'CONSUMER_APPLICABLE_WHITELIST': whitelist.as_posix(),
            'CONSUMER_ROOT': consumer.as_posix(),
        }
        proc = subprocess.run(
            [resolve_bash(),
             str(self.repo_root / "scripts/reconcile-overlay.sh"), '--dry-run'],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            cwd=self.repo_root, env=env, timeout=300
        )
        return proc.stdout + proc.stderr

    def test_ac10_declarative_reconcile_reports_no_loss(self):
        """
        AC-10 (선언적 경로): reconcile --dry-run 이 대상 workflow 에 loss 를 보고하지 않는다.

        Change Plan §8.1 / §8.3. 2-conjunct + 판별력:
          1. reachability — 채널이 그 파일을 **실제로 처리**했다는 관측
                            (repo-kind 해소 ∧ 대상 파일 언급). 이게 없으면 2번이 공허 통과한다
                            (hollow-gate ③ 트리거 미도달 — 실제로 겪었다: repo-kind unknown
                             fail-closed abort 상태에서는 "loss 없음" 이 vacuous true 였다)
          2. 결과        — `=== LOSS REPORT ===` 블록 **안**에 대상 파일 지목 0건
          3. 판별력      — DIVERGENT fixture 에서 2번이 뒤집혀 1건 이상

        ※ 블록 **밖** 전역 'loss 발생' 문구는 술어로 쓰지 않는다 — overlay 채널 전반 신호라
          대상 파일과 무관하게 항상 뜨고, 채널이 abort 한 fixture 에서도 떴다(실측).
        """
        reconcile_script = self.repo_root / "scripts/reconcile-overlay.sh"
        assert reconcile_script.exists(), "reconcile-overlay.sh not found"

        ssot_bytes = (self.repo_root / PATH_T2).read_bytes()

        # ── CONVERGED: consumer 사본 == wrapper SSOT (byte 동일) ──────────
        with tempfile.TemporaryDirectory() as tmpdir:
            output = self._run_reconcile_hermetic(tmpdir, ssot_bytes)

        assert 'repo-kind unknown' not in output, (
            f"repo-kind 미해소 — 채널이 fail-closed abort 해서 결과 conjunct 가 공허해진다:\n"
            f"{output[-1500:]}"
        )
        # ※ CONVERGED 는 파일이 동일하면 스크립트가 **per-file 흔적을 출력하지 않는다**(실측:
        #   MARKER_NONE 행 0건). 따라서 reachability 는 여기서 잴 수 없고 **DIVERGENT 쪽에서**
        #   잰다 — 아래 divergent 블록이 "채널이 이 파일에 실제로 도달하며 rel_path 도 정확하다"
        #   를 증명하므로, 그와 동일 fixture 형상인 여기의 'loss 없음' 이 공허하지 않게 된다.

        loss_match = re.search(
            r'=== LOSS REPORT ===\n(.*?)\n=== END LOSS REPORT ===', output, re.DOTALL)
        loss_block = loss_match.group(1) if loss_match else ''
        assert WORKFLOW_BASENAME not in loss_block, (
            f"CONVERGED fixture 인데 대상 workflow 가 LOSS REPORT 에 등장:\n{loss_block}"
        )

        # ── DIVERGENT: CONVERGED + 1줄 (판별 원인을 content diff 로 고정) ──
        divergent_bytes = ssot_bytes + \
            b"\n# synthetic consumer customization (AC-10 discrimination probe)\n"
        with tempfile.TemporaryDirectory() as tmpdir_div:
            output_div = self._run_reconcile_hermetic(tmpdir_div, divergent_bytes)

        assert 'repo-kind unknown' not in output_div, (
            "DIVERGENT fixture 에서 repo-kind 미해소 — 판별력 증명이 공허해진다"
        )

        # ── reachability (여기서 잰다) ────────────────────────────────────
        # ★ 단순 `basename in output` 으로는 부족하다 — rel_path 가 절대경로로 깨져도
        #   basename 이 부분문자열로 들어 있어 통과한다(실제로 그렇게 통과했었다:
        #   `MARKER_NONE wholesale: C:\...\github-workflows/story-section-schema.yml`).
        #   그 상태면 consumer_file 을 못 찾아 had_consumer_diff=false → divergent 인데 loss 0.
        #   rel_path 가 **정확히 basename** 인지 단정해야 그 경로 계산 파손을 잡는다.
        assert re.search(
            r'MARKER_NONE wholesale:\s*' + re.escape(WORKFLOW_BASENAME) + r'\s*$',
            output_div, re.MULTILINE
        ), (
            f"reachability 실패: 'MARKER_NONE wholesale: {WORKFLOW_BASENAME}' 행이 없다 "
            f"= 채널이 그 파일에 도달하지 않았거나 rel_path 가 깨졌다.\n{output_div[-1500:]}"
        )
        loss_match_div = re.search(
            r'=== LOSS REPORT ===\n(.*?)\n=== END LOSS REPORT ===', output_div, re.DOTALL)
        # ★ 여기를 `if` 로 감싸면 블록 부재 시 **판별력 증명이 통째로 사라진다** — 절대 금지.
        assert loss_match_div is not None, (
            f"DIVERGENT fixture 인데 LOSS REPORT 블록이 없다 = 수렴본과 구별을 못 한다(판별력 0):\n"
            f"{output_div[-1500:]}"
        )
        assert WORKFLOW_BASENAME in loss_match_div.group(1), (
            f"DIVERGENT: 대상 workflow 가 loss 로 잡혀야 한다:\n"
            f"{loss_match_div.group(1)[:500]}"
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
        # sys.path 주입 불요 — tests/conftest.py:16-21 이 이미 scripts/ + scripts/lib 를 주입한다.
        walk_plan_path = self.repo_root / "scripts/lib/walk_plan.py"
        assert walk_plan_path.exists(), "walk_plan.py not found"

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

        # **POSITIVE CONTROL** — 독립 대조원 의무.
        #
        # ★ 종전 판은 `fixture = f"...{needle}..."` 를 만든 뒤 `needle in fixture` 를 단언했다.
        #   이는 needle 값과 무관하게 **항상 참**(항진)이라 판별력 0 이었다 — 깨진 needle 을
        #   막으려고 둔 장치가 정작 깨진 needle 을 통과시킨다(방어 장치가 방어 대상과 동일 결함).
        #   오타/쓰레기/빈 문자열 뮤턴트 4종이 전부 PASS 함이 실측으로 확인됐다.
        #
        # 교체: needle 로부터 **유도되지 않은** 대조원 = 수렴 *이전* 의 git 문면.
        #   각 needle 을 "그 needle 이 잡아내야 했던 바로 그 파일의 수렴 전 내용" 에 대조한다.
        #   ⇒ needle 이 조금이라도 어긋나면 여기서 즉시 FAIL 하고, 동시에 "이 needle 이
        #      실제로 구판 문면을 검출한다" 는 것까지 증명된다.
        BASE_REF = "3a7cae2f"  # Phase 2 브랜치 base (수렴 전 = 구판 문면 잔존 시점)
        positive_sources = [
            (needle_1, 'P-11b', f"{BASE_REF}:templates/story-page-structure.md"),
            (needle_2, 'P-11c', f"{BASE_REF}:docs/consumer-guide.md"),
        ]
        for needle, name, ref in positive_sources:
            # 빈 문자열/과단축 needle 은 어떤 대조원에도 자명하게 포함되므로 길이 하한을 건다.
            assert len(needle) >= 8, (
                f"{name} needle 이 비었거나 너무 짧다 (len={len(needle)}) — "
                f"빈 문자열은 모든 대조원에 자명 포함이라 positive control 이 공허해진다"
            )
            probe = subprocess.run(
                ['git', 'show', ref],
                cwd=self.repo_root, capture_output=True, text=True,
                encoding='utf-8', errors='replace', timeout=60
            )
            if probe.returncode != 0:
                pytest.fail(
                    f"{name} positive control 대조원 취득 실패: git show {ref} "
                    f"(rc={probe.returncode}) — fetch-depth:0 필요. skip 아니라 FAIL.\n"
                    f"{probe.stderr[:300]}"
                )
            assert needle in probe.stdout, (
                f"{name} POSITIVE CONTROL 실패: 조립된 needle 이 수렴 전 문면({ref})에 "
                f"매치되지 않는다 ⇒ needle 이 깨졌다(오타/조립 오류). "
                f"이 상태면 아래 negative control 은 0 매치로 **항상 통과**한다.\n"
                f"needle={repr(needle)}"
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

        # P-11e: 실배달 경로 명시 (D4-b 고유 문면으로 앵커)
        #
        # ★ 종전 패턴 `(manifest).*(수동|bootstrap)` 은 **base 3a7cae2f 에서 이미 2건 매치**했다
        #   (consumer-guide.md:1220 bootstrap Stage 7 · :1754 subissue-from-impl-manifest).
        #   ⇒ D4-b 문면을 전부 지워도 통과 = hollow-gate ⑥(baseline 이미 GREEN). 진행 게이트가 아니었다.
        #   좁힌 패턴 실측: base=0 / HEAD=1 ⇒ D4-b 문면이 사라지면 즉시 RED (판별력 실재).
        p11e_pattern = r'(실배달 경로).*(manifest).*(수동|bootstrap)'
        p11e_matches = re.findall(p11e_pattern, guide_content)
        assert len(p11e_matches) >= 1, (
            f"P-11e failed: pattern {p11e_pattern!r} "
            f"found {len(p11e_matches)} times, expected >= 1 "
            f"(D4-b 실배달 경로 문면이 사라졌다)"
        )
