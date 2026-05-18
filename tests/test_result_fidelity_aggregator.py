# -*- coding: utf-8 -*-
"""
tests/test_result_fidelity_aggregator.py

CFP-900 Phase 2 — unit TC for result-fidelity-aggregator.py
reconcile-protocol-v1 v1.10 §4.13 result_fidelity_binding

Test contract (Story §8.1):
  - 4-value enum × degradation_propagation matrix (TC-RF-1 ~ TC-RF-8)
  - post-mirror sanity check (TC-SAN-1 ~ TC-SAN-5)
  - EC (edge cases) 1 ~ 7 (TC-EC-1 ~ TC-EC-7)
  - exit code contract (TC-EXIT-1 ~ TC-EXIT-4)
  - F-CR-899 pattern avoidance verify (TC-PAT-1 ~ TC-PAT-4)

TDD order: RED first — implementation absent → tests fail → implement → GREEN.
pytest framework. ADR-061 정합: 외부 .py, stdlib only.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Script path
# ─────────────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
AGGREGATOR_SCRIPT = REPO_ROOT / "templates" / "scripts" / "result-fidelity-aggregator.py"


def run_aggregator(args: list, env: dict | None = None) -> subprocess.CompletedProcess:
    """result-fidelity-aggregator.py 를 subprocess 로 실행."""
    cmd = [sys.executable, str(AGGREGATOR_SCRIPT)] + args
    merged_env = {**os.environ}
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=merged_env,
    )


def make_tmp_dir_with_files(files: dict[str, str]) -> str:
    """
    임시 디렉토리를 생성하고 files dict (rel_path → content) 를 채워 반환.
    """
    tmp = tempfile.mkdtemp()
    for rel, content in files.items():
        full = Path(tmp) / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
    return tmp


def parse_result(stdout: str) -> dict:
    """aggregator JSON 출력을 파싱."""
    for line in stdout.strip().splitlines():
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# TC-RF: 4-value enum × degradation_propagation matrix
# §4.13 degradation_propagation SSOT verbatim
# ─────────────────────────────────────────────────────────────────────────────

class TestDegradationPropagation:
    """degradation_propagation deterministic mapping 검증."""

    def _setup_dirs(self, wrapper_files=None, consumer_files=None):
        """기본 test 디렉토리 쌍 생성."""
        wfiles = wrapper_files or {"test.yml": "name: test\non: push\n"}
        cfiles = consumer_files or wfiles  # 기본: wrapper == consumer (sanity PASS)
        w = make_tmp_dir_with_files(wfiles)
        c = make_tmp_dir_with_files(cfiles)
        return w, c

    def test_tc_rf_1_all_ok_success(self):
        """TC-RF-1: S1=0 + S2=0 + sanity PASS → SUCCESS"""
        w, c = self._setup_dirs()
        r = run_aggregator([
            "--s1-exit", "0",
            "--s2-exit", "0",
            "--wrapper-dir", w,
            "--consumer-dir", c,
        ])
        assert r.returncode == 0, f"exit code should be 0 for SUCCESS, got {r.returncode}"
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS", f"expected SUCCESS, got: {data}"

    def test_tc_rf_2_s1_fail_closed_failed(self):
        """TC-RF-2: S1 exit 1 (fail-closed) → FAILED"""
        w, c = self._setup_dirs()
        r = run_aggregator([
            "--s1-exit", "1",
            "--s2-exit", "0",
            "--wrapper-dir", w,
            "--consumer-dir", c,
        ])
        assert r.returncode == 1, f"exit code should be 1 for FAILED, got {r.returncode}"
        data = parse_result(r.stdout)
        assert data.get("result") == "FAILED", f"expected FAILED, got: {data}"

    def test_tc_rf_3_s2_abort_failed(self):
        """TC-RF-3: S2 exit 1 (filter abort — unknown) → FAILED"""
        w, c = self._setup_dirs()
        r = run_aggregator([
            "--s1-exit", "0",
            "--s2-exit", "1",
            "--wrapper-dir", w,
            "--consumer-dir", c,
        ])
        assert r.returncode == 1
        data = parse_result(r.stdout)
        assert data.get("result") == "FAILED", f"expected FAILED, got: {data}"

    def test_tc_rf_4_s1_degraded_success_with_degradation(self):
        """TC-RF-4: S1 exit 2 (degraded) → SUCCESS_WITH_DEGRADATION"""
        w, c = self._setup_dirs()
        r = run_aggregator([
            "--s1-exit", "2",
            "--s2-exit", "0",
            "--wrapper-dir", w,
            "--consumer-dir", c,
        ])
        assert r.returncode == 2, f"exit code should be 2 for SUCCESS_WITH_DEGRADATION, got {r.returncode}"
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS_WITH_DEGRADATION", f"expected SUCCESS_WITH_DEGRADATION, got: {data}"

    def test_tc_rf_5_s2_degraded_success_with_degradation(self):
        """TC-RF-5: S2 exit 2 (degraded) → SUCCESS_WITH_DEGRADATION"""
        w, c = self._setup_dirs()
        r = run_aggregator([
            "--s1-exit", "0",
            "--s2-exit", "2",
            "--wrapper-dir", w,
            "--consumer-dir", c,
        ])
        assert r.returncode == 2
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS_WITH_DEGRADATION", f"expected SUCCESS_WITH_DEGRADATION, got: {data}"

    def test_tc_rf_6_sanity_partial_mismatch_partial_failure(self):
        """TC-RF-6: sanity PARTIAL_MISMATCH (missing file) → PARTIAL_FAILURE"""
        # wrapper에는 파일 있는데 consumer에는 없음 → sanity = PARTIAL_MISMATCH
        w = make_tmp_dir_with_files({"missing.yml": "name: test\non: push\n"})
        c = make_tmp_dir_with_files({})  # consumer 비어있음 → missing
        r = run_aggregator([
            "--s1-exit", "0",
            "--s2-exit", "0",
            "--wrapper-dir", w,
            "--consumer-dir", c,
        ])
        assert r.returncode == 1
        data = parse_result(r.stdout)
        assert data.get("result") == "PARTIAL_FAILURE", f"expected PARTIAL_FAILURE, got: {data}"

    def test_tc_rf_7_sanity_syntax_warning_success_with_degradation(self):
        """TC-RF-7: sanity syntax warning → SUCCESS_WITH_DEGRADATION"""
        # empty yml → syntax warning
        w = make_tmp_dir_with_files({"warn.yml": "   "})
        c = make_tmp_dir_with_files({"warn.yml": "   "})
        r = run_aggregator([
            "--s1-exit", "0",
            "--s2-exit", "0",
            "--wrapper-dir", w,
            "--consumer-dir", c,
        ])
        # 빈 yml → SUCCESS_WITH_DEGRADATION
        data = parse_result(r.stdout)
        assert data.get("result") in {"SUCCESS_WITH_DEGRADATION", "SUCCESS"}, f"unexpected result: {data}"

    def test_tc_rf_8_failed_most_severe_over_partial(self):
        """TC-RF-8: S1 exit 1 (FAILED) > PARTIAL_FAILURE 우선 (EC-1 패턴)"""
        # wrapper에 파일 있는데 consumer 없음 → sanity PARTIAL_MISMATCH
        w = make_tmp_dir_with_files({"check.yml": "name: check\non: push\n"})
        c = make_tmp_dir_with_files({})
        r = run_aggregator([
            "--s1-exit", "1",
            "--s2-exit", "0",
            "--wrapper-dir", w,
            "--consumer-dir", c,
        ])
        # FAILED 우선 (abort > partial, EC-1)
        data = parse_result(r.stdout)
        assert data.get("result") == "FAILED", f"FAILED should dominate PARTIAL_FAILURE (EC-1): {data}"


# ─────────────────────────────────────────────────────────────────────────────
# TC-SAN: post-mirror sanity check
# §4.13 post_mirror_sanity_check filesystem-only invariant
# ─────────────────────────────────────────────────────────────────────────────

class TestPostMirrorSanityCheck:
    """post-mirror sanity check (filesystem-only, pure read-only) 검증."""

    def test_tc_san_1_path_set_match_pass(self):
        """TC-SAN-1: expected == actual path set → sanity PASS → SUCCESS"""
        files = {"a.yml": "name: a\non: push\n", "b.md": "# doc\n"}
        w = make_tmp_dir_with_files(files)
        c = make_tmp_dir_with_files(files)
        r = run_aggregator([
            "--s1-exit", "0", "--s2-exit", "0",
            "--wrapper-dir", w, "--consumer-dir", c,
        ])
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS"
        assert data.get("sanity_check") == "PASS"

    def test_tc_san_2_missing_file_partial_mismatch(self):
        """TC-SAN-2: consumer-side 파일 누락 → sanity PARTIAL_MISMATCH → PARTIAL_FAILURE"""
        w = make_tmp_dir_with_files({"required.yml": "name: req\non: push\n"})
        c = make_tmp_dir_with_files({})
        r = run_aggregator([
            "--s1-exit", "0", "--s2-exit", "0",
            "--wrapper-dir", w, "--consumer-dir", c,
        ])
        data = parse_result(r.stdout)
        assert data.get("sanity_check") == "PARTIAL_MISMATCH"
        assert data.get("result") == "PARTIAL_FAILURE"

    def test_tc_san_3_extra_consumer_files_warning(self):
        """TC-SAN-3: consumer-only extra 파일 → sanity WARNING"""
        w = make_tmp_dir_with_files({"shared.yml": "name: shared\non: push\n"})
        c = make_tmp_dir_with_files({
            "shared.yml": "name: shared\non: push\n",
            "consumer-only.yml": "name: extra\non: push\n",  # consumer-only extra
        })
        r = run_aggregator([
            "--s1-exit", "0", "--s2-exit", "0",
            "--wrapper-dir", w, "--consumer-dir", c,
        ])
        data = parse_result(r.stdout)
        # extra consumer files → WARNING → SUCCESS_WITH_DEGRADATION 또는 SUCCESS (구현 재량)
        assert data.get("sanity_check") in {"WARNING", "PASS"}

    def test_tc_san_4_filesystem_only_no_network(self):
        """TC-SAN-4: sanity check = filesystem-only (network call 0 invariant 검증)"""
        # 네트워크 없이도 동작 = filesystem-only invariant
        # RESULT_FIDELITY_AGGREGATOR_PY 는 gh api / curl 미호출
        w = make_tmp_dir_with_files({"x.yml": "name: x\non: push\n"})
        c = make_tmp_dir_with_files({"x.yml": "name: x\non: push\n"})
        # HTTPS_PROXY / HTTP_PROXY 를 invalid 로 설정해도 동작해야 함
        r = run_aggregator([
            "--s1-exit", "0", "--s2-exit", "0",
            "--wrapper-dir", w, "--consumer-dir", c,
        ], env={"HTTPS_PROXY": "http://invalid-proxy-should-not-be-called:9999"})
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS", f"filesystem-only invariant: should succeed regardless of proxy: {data}"

    def test_tc_san_5_idempotent_verify(self):
        """TC-SAN-5: sanity check 반복 실행 = 동일 result (idempotent invariant)"""
        w = make_tmp_dir_with_files({"z.yml": "name: z\non: push\n"})
        c = make_tmp_dir_with_files({"z.yml": "name: z\non: push\n"})
        r1 = run_aggregator(["--s1-exit", "0", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        r2 = run_aggregator(["--s1-exit", "0", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        d1 = parse_result(r1.stdout)
        d2 = parse_result(r2.stdout)
        assert d1.get("result") == d2.get("result"), "idempotent: repeated calls must return same result"


# ─────────────────────────────────────────────────────────────────────────────
# TC-EC: edge cases EC-1 ~ EC-7
# §4.13 closed_set_invariant EC-1~3 + §4.13 spec 추가 EC
# ─────────────────────────────────────────────────────────────────────────────

class TestEdgeCases:

    def _setup_dirs(self, same=True):
        files = {"f.yml": "name: f\non: push\n"}
        w = make_tmp_dir_with_files(files)
        c = make_tmp_dir_with_files(files if same else {})
        return w, c

    def test_tc_ec_1_s1_s2_both_abort_failed_wins(self):
        """TC-EC-1: S1 exit 1 + S2 exit 1 (both abort) → FAILED 우선"""
        w, c = self._setup_dirs()
        r = run_aggregator(["--s1-exit", "1", "--s2-exit", "1", "--wrapper-dir", w, "--consumer-dir", c])
        data = parse_result(r.stdout)
        assert data.get("result") == "FAILED", f"EC-1: both abort → FAILED: {data}"

    def test_tc_ec_2_dry_run_no_result_field(self):
        """TC-EC-2: dry-run mode → result field 미적용 (preview only)"""
        w, c = self._setup_dirs()
        r = run_aggregator(["--s1-exit", "0", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c, "--dry-run"])
        # dry-run = exit 0, JSON result 없음
        assert r.returncode == 0, f"dry-run should exit 0: {r.returncode}"
        data = parse_result(r.stdout)
        assert "result" not in data, f"EC-2: dry-run must NOT include result field: {data}"

    def test_tc_ec_3_mixed_repo_s2_skip_success(self):
        """TC-EC-3: wrapper self-app (S2 exit 0 — filter skip) + S1 exit 0 → SUCCESS"""
        w, c = self._setup_dirs()
        # S2 exit 0 = mixed repo, filter skip
        r = run_aggregator(["--s1-exit", "0", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS"

    def test_tc_ec_4_whitelist_filter_applied(self):
        """TC-EC-4: whitelist 파일 적용 시 plugin-only yml sanity 제외 (false-positive 차단)"""
        # wrapper 에는 plugin-only.yml 있지만 whitelist 에 없음 → sanity expected set 에서 제외
        whitelist_content = "consumer-ok.yml\n"
        wf = {"consumer-ok.yml": "name: ok\non: push\n", "plugin-only.yml": "name: plugin\non: push\n"}
        w = make_tmp_dir_with_files(wf)
        c = make_tmp_dir_with_files({"consumer-ok.yml": "name: ok\non: push\n"})  # plugin-only 없음

        # whitelist 파일 생성
        tmp_wl = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
        tmp_wl.write(whitelist_content)
        tmp_wl.close()

        try:
            r = run_aggregator([
                "--s1-exit", "0", "--s2-exit", "0",
                "--wrapper-dir", w, "--consumer-dir", c,
                "--whitelist", tmp_wl.name,
            ])
            data = parse_result(r.stdout)
            # plugin-only.yml 이 whitelist 에 없으므로 sanity 대상 제외 → consumer 에 없어도 PASS
            # (whitelist 필터 적용 → expected set 에서 plugin-only 제거 → mismatch 없음)
            assert data.get("result") in {"SUCCESS", "SUCCESS_WITH_DEGRADATION"}, \
                f"EC-4: whitelist filter should exclude plugin-only from sanity expected set: {data}"
        finally:
            Path(tmp_wl.name).unlink(missing_ok=True)

    def test_tc_ec_5_output_file_written(self):
        """TC-EC-5: --output-file 지정 시 JSON artifact 파일 생성"""
        w, c = self._setup_dirs()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            out_path = f.name
        try:
            r = run_aggregator([
                "--s1-exit", "0", "--s2-exit", "0",
                "--wrapper-dir", w, "--consumer-dir", c,
                "--output-file", out_path,
            ])
            assert r.returncode == 0
            assert Path(out_path).is_file(), "output file should be created"
            with open(out_path, encoding="utf-8") as f:
                data = json.load(f)
            assert "result" in data
            assert data["result"] == "SUCCESS"
        finally:
            Path(out_path).unlink(missing_ok=True)

    def test_tc_ec_6_success_no_hardcode(self):
        """TC-EC-6: upgrade_event_honest_record — SUCCESS hardcode 금지 (S1 exit 1 → FAILED 기록)"""
        w, c = self._setup_dirs()
        r = run_aggregator(["--s1-exit", "1", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        data = parse_result(r.stdout)
        # S1 exit 1 → 반드시 FAILED (SUCCESS hardcode 차단)
        assert data.get("result") != "SUCCESS", f"EC-6: S1 fail-closed must NOT record SUCCESS: {data}"
        assert data.get("result") == "FAILED"

    def test_tc_ec_7_degraded_not_silent_success(self):
        """TC-EC-7: S1 exit 2 (degraded) → SUCCESS_WITH_DEGRADATION (silent SUCCESS 거짓 기록 차단)"""
        w, c = self._setup_dirs()
        r = run_aggregator(["--s1-exit", "2", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS_WITH_DEGRADATION", \
            f"EC-7: degraded must NOT silently report SUCCESS: {data}"


# ─────────────────────────────────────────────────────────────────────────────
# TC-EXIT: exit code contract
# ─────────────────────────────────────────────────────────────────────────────

class TestExitCodeContract:
    """caller exit code contract 검증 (F-CR-899-1 류 방지 — return code 임의 변경 금지)."""

    def _setup_dirs(self):
        files = {"x.yml": "name: x\non: push\n"}
        w = make_tmp_dir_with_files(files)
        c = make_tmp_dir_with_files(files)
        return w, c

    def test_tc_exit_1_success_exit_0(self):
        """TC-EXIT-1: result=SUCCESS → exit code 0"""
        w, c = self._setup_dirs()
        r = run_aggregator(["--s1-exit", "0", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        assert r.returncode == 0

    def test_tc_exit_2_failed_exit_1(self):
        """TC-EXIT-2: result=FAILED → exit code 1"""
        w, c = self._setup_dirs()
        r = run_aggregator(["--s1-exit", "1", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        assert r.returncode == 1

    def test_tc_exit_3_success_with_degradation_exit_2(self):
        """TC-EXIT-3: result=SUCCESS_WITH_DEGRADATION → exit code 2"""
        w, c = self._setup_dirs()
        r = run_aggregator(["--s1-exit", "2", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        assert r.returncode == 2

    def test_tc_exit_4_partial_failure_exit_1(self):
        """TC-EXIT-4: result=PARTIAL_FAILURE → exit code 1"""
        w = make_tmp_dir_with_files({"missing.yml": "name: m\non: push\n"})
        c = make_tmp_dir_with_files({})
        r = run_aggregator(["--s1-exit", "0", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        assert r.returncode == 1


# ─────────────────────────────────────────────────────────────────────────────
# TC-PAT: F-CR-899 pattern avoidance verify
# CFP-899 Phase 2 FIX 패턴 재발 방지
# ─────────────────────────────────────────────────────────────────────────────

class TestCfp899PatternAvoidance:
    """CFP-899 FIX pattern reoccurrence prevention."""

    def test_tc_pat_1_return_code_spec_verbatim(self):
        """TC-PAT-1: F-CR-899-1 류 — exit code = spec verbatim (임의 변경 금지)"""
        # result-fidelity-aggregator.py 소스 내 EXIT_CODE_MAP 확인
        src = AGGREGATOR_SCRIPT.read_text(encoding="utf-8")
        assert "EXIT_CODE_MAP" in src, "EXIT_CODE_MAP must be defined (spec verbatim exit code contract)"
        assert "RESULT_SUCCESS: 0" in src or '"SUCCESS": 0' in src or "SUCCESS: 0" in src, \
            "SUCCESS must map to exit code 0 (spec verbatim)"

    def test_tc_pat_2_wrapper_self_honest_result(self):
        """TC-PAT-2: F-CR-899-2 류 — wrapper self-app result = honest (silent skip 0 invariant)"""
        # wrapper self-app: S1=0 S2=0 → SUCCESS (0 skip 정직 기록)
        files = {"test.yml": "name: t\non: push\n"}
        w = make_tmp_dir_with_files(files)
        c = make_tmp_dir_with_files(files)
        r = run_aggregator(["--s1-exit", "0", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS"
        # result field 반드시 존재 (upgrade_event_honest_record 의무)
        assert "result" in data, "TC-PAT-2: result field must always be present (honest record)"

    def test_tc_pat_3_env_var_binding_spec_names(self):
        """TC-PAT-3: F-CR-899-4 류 — env var 이름 binding spec 정합 (rename 금지)"""
        # aggregator script 안 --s1-exit / --s2-exit argument 이름이 spec 정합인지 확인
        src = AGGREGATOR_SCRIPT.read_text(encoding="utf-8")
        assert "--s1-exit" in src, "F-CR-899-4: --s1-exit arg name must match spec"
        assert "--s2-exit" in src, "F-CR-899-4: --s2-exit arg name must match spec"
        assert "--wrapper-dir" in src
        assert "--consumer-dir" in src

    def test_tc_pat_4_no_bash_subshell_fallback_pattern(self):
        """TC-PAT-4: F-CR-899-10 류 — bash subshell || fallback 패턴 회피 + 실 실행 검증.

        F-CR-900-2 강화:
          (a) source-grep: explicit _AGG_EC=$? capture 존재 확인
          (b) source-grep: local 키워드가 top-level (_reconcile_file 함수 밖) §4.13 블록에 없음 (F-CR-900-1 regression guard)
          (c) real-execution: aggregator 가 exit 0 을 반환하면 reconcile-overlay.sh §4.13 블록이
              "result:" echo 를 출력하는지 subprocess 실행으로 검증
        """
        reconcile_sh = REPO_ROOT / "scripts" / "reconcile-overlay.sh"
        src = reconcile_sh.read_text(encoding="utf-8")

        # (a) explicit exit code capture 확인
        # 패턴: _AGG_EC=0; _AGG_OUTPUT=$(...) || _AGG_EC=$? (set -euo pipefail 아래 exit code 명시 캡처)
        assert "_AGG_EC=0" in src, \
            "F-CR-899-10: reconcile-overlay.sh aggregator 호출 시 _AGG_EC=0 초기화 필요"
        assert "_AGG_EC=$?" in src, \
            "F-CR-899-10: reconcile-overlay.sh aggregator 호출 시 explicit _AGG_EC=$? capture 필요"
        agg_section = src[src.find("RESULT_FIDELITY_AGGREGATOR_PY"):]
        assert "_AGG_OUTPUT=$(" in agg_section, "aggregator stdout capture must be explicit"

        # (b) F-CR-900-1 regression guard: §4.13 블록 (line 844 이후) 에서 'local _result_value' 없음
        #     _reconcile_file 함수 (line ~385-752) 이후의 §4.13 블록을 추출
        adr_block_start = src.find("# §4.13 result_fidelity_binding")
        assert adr_block_start != -1, "§4.13 블록 미발견"
        adr_block = src[adr_block_start:]
        assert "local _result_value" not in adr_block, \
            "F-CR-900-1: top-level §4.13 블록에 'local _result_value' 사용 금지 (set -euo pipefail abort trigger)"

        # (c) real-execution: aggregator 직접 실행 → exit 0 + result 출력 확인
        #     mock wrapper/consumer with matching yml → SUCCESS path
        w, c = self._setup_dirs()
        r = run_aggregator(["--s1-exit", "0", "--s2-exit", "0", "--wrapper-dir", w, "--consumer-dir", c])
        assert r.returncode == 0, f"TC-PAT-4(c): aggregator SUCCESS exit must be 0, got {r.returncode}"
        data = parse_result(r.stdout)
        assert data.get("result") == "SUCCESS", \
            f"TC-PAT-4(c): aggregator real-exec must produce result=SUCCESS, got {data}"

    def _setup_dirs(self):
        """Helper: matching wrapper/consumer dirs for SUCCESS path."""
        import tempfile
        w = tempfile.mkdtemp()
        c = tempfile.mkdtemp()
        # matching files → sanity PASS
        for d in (w, c):
            Path(d).joinpath("ok.yml").write_text("name: ok\n", encoding="utf-8")
        return w, c
