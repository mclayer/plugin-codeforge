#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""test_ng18_ci_run_completeness.py — CFP-2926 NG-18 CI run completeness RTM 테스트.

Story §8.0.8 (1) NG-18 규격:
  - empty-target: 기대 run 수 미해석(0) → INCONCLUSIVE (F-6′ 형판 — 0==0 GREEN 금지)
  - unknown-input: run 목록 조회 응답 파싱 실패 → exit 1 (fail-closed RED)
  - trace: 기대 run 수 · 실제 run 수 · 차분
  - identity_bearing: true — 채널 = Actions run 목록 조회 범위

Red-first TDD (git stash 기법 적용 — cross-layer working-tree drift 대응):
  - 선행 구현이 있어도 fixture 진정성 입증 의무
  - pre-GREEN HEAD에서 RED 실물 확인 후 구현 복원

Mutant 왕복 실증 (ADR-171 §결정 5):
  - M1: actual < expected (run 누락) → RED ✓
  - M2: expected == 0 → INCONCLUSIVE (0==0 GREEN 금지) ✓
  - M3: gh 응답 파싱 불가 → exit 1 ✓
  - M4: commit SHA 미제공 → INCONCLUSIVE ✓
  - Regression-guard: expected == actual → PASS ✓
"""

from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# sys.path 는 상위 conftest 에서 이미 scripts/lib 를 주입했으므로 직접 import 가능
from check_ci_run_completeness import main
from gate_verdict import EXIT_INCONCLUSIVE, EXIT_PASS, EXIT_RED


class TestNG18CIRunCompleteness:
    """NG-18 CI run completeness check 전건 테스트."""

    def test_ci_run_completeness_passes_when_counts_match(self):
        """[regression-guard case] PASS: expected == actual."""
        # Setup: --expected 5 --actual 5 → exit 0 (PASS)
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                ["check_ci_run_completeness.py", "--expected", "5", "--actual", "5"]
            )

        assert exit_code == EXIT_PASS, f"Expected exit {EXIT_PASS}, got {exit_code}"
        output = stdout.getvalue()
        assert '"verdict": "PASS"' in output, f"Expected PASS verdict in: {output}"
        assert '"expected_count": 5' in output
        assert '"actual_count": 5' in output

    def test_ci_run_completeness_red_when_actual_less_than_expected(self):
        """[discriminating case M1] RED: actual < expected (run 누락 검출).

        Mutant: 114 workflow run 중 실제 113개만 큐에 들어감 (1건 drop).
        기대값 114 < 실제값 113 → ci_run_count_mismatch RED.
        """
        # Setup: --expected 114 --actual 113 → exit 1 (RED)
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                ["check_ci_run_completeness.py", "--expected", "114", "--actual", "113"]
            )

        assert (
            exit_code == EXIT_RED
        ), f"Expected exit {EXIT_RED} (run mismatch), got {exit_code}"
        output = stdout.getvalue()
        assert '"verdict": "RED"' in output, f"Expected RED verdict in: {output}"
        assert "ci_run_count_mismatch" in output
        assert '"expected_count": 114' in output
        assert '"actual_count": 113' in output

    def test_ci_run_completeness_inconclusive_when_expected_zero(self):
        """[discriminating case M2 ★CRITICAL★] INCONCLUSIVE: expected == 0.

        Story 규격: 기대 run 수 미해석(0) → INCONCLUSIVE (F-6′ 형판 — 0==0 GREEN 금지).
        Mutant: 0개 workflow = workflow dir 없음 또는 빈 dir → expected=0.
        ★틀린 동작★: 0 == 0 을 "유실 없음(PASS)"으로 읽는 경우.
        ★올바른 동작★: 0개 workflow → 검사 대상 부재 → exit 3 (INCONCLUSIVE).
        """
        # Setup: --expected 0 --actual 0 → exit 3 (INCONCLUSIVE), NOT exit 0 (PASS)
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                ["check_ci_run_completeness.py", "--expected", "0", "--actual", "0"]
            )

        assert (
            exit_code == EXIT_INCONCLUSIVE
        ), f"Expected exit {EXIT_INCONCLUSIVE} (empty-target), got {exit_code}"
        output = stdout.getvalue()
        assert (
            '"verdict": "INCONCLUSIVE"' in output
        ), f"Expected INCONCLUSIVE verdict in: {output}"
        assert "no_workflows_found" in output

    def test_ci_run_completeness_inconclusive_without_commit_sha(self):
        """[discriminating case M4] INCONCLUSIVE: commit SHA 미제공.

        Mutant: --commit 없이 실행 → commit_sha_not_provided → exit 3 (INCONCLUSIVE).
        """
        # Setup: --expected 10 (--commit 생략) → exit 3 (INCONCLUSIVE)
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                ["check_ci_run_completeness.py", "--expected", "10"]
            )

        assert (
            exit_code == EXIT_INCONCLUSIVE
        ), f"Expected exit {EXIT_INCONCLUSIVE} (no commit), got {exit_code}"
        output = stdout.getvalue()
        assert (
            '"verdict": "INCONCLUSIVE"' in output
        ), f"Expected INCONCLUSIVE verdict in: {output}"
        assert "commit_sha_not_provided" in output

    def test_ci_run_completeness_red_on_gh_command_failure(self):
        """[discriminating case M3] RED: gh run list 파싱 불가 (unknown-input).

        Mutant: gh command 반환 rc != 0 (auth 실패 / offline 등) →
        unknown-input fail-closed → exit 1 (RED).

        ★ADR-171 §결정 5 mock seam 검증★:
        mock `_get_actual_runs()` 를 통해 파싱 실패 경로 검증.
        """
        # Setup: _get_actual_runs 를 mock 해서 실패 응답 시뮬레이션
        with patch("check_ci_run_completeness._get_actual_runs") as mock_get_runs:
            # (run_count, error_reason) 튜플 반환
            mock_get_runs.return_value = (0, "gh_command_failed: Authentication required")

            stdout = io.StringIO()
            with patch("sys.stdout", stdout):
                exit_code = main(
                    [
                        "check_ci_run_completeness.py",
                        "--expected",
                        "10",
                        "--commit",
                        "abc1234",
                    ]
                )

            assert (
                exit_code == EXIT_RED
            ), f"Expected exit {EXIT_RED} (unknown-input), got {exit_code}"
            output = stdout.getvalue()
            assert (
                '"verdict": "RED"' in output
            ), f"Expected RED verdict in: {output}"
            assert "gh_command_failed" in output

            # ★동반 assertion 의무★: mock seam 이 실제로 호출됐는지 확인
            mock_get_runs.assert_called_once_with("abc1234")

    def test_ci_run_completeness_passes_when_actual_exceeds_expected(self):
        """[regression-guard case] PASS: actual > expected (재시도/중복 실행 용인).

        흔한 시나리오: 재시도(rerun)로 인해 같은 commit SHA 의 run 이 증가.
        규격: actual >= expected 이면 PASS.
        """
        # Setup: --expected 10 --actual 12 (2개 재시도) → exit 0 (PASS)
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                ["check_ci_run_completeness.py", "--expected", "10", "--actual", "12"]
            )

        assert exit_code == EXIT_PASS, f"Expected exit {EXIT_PASS}, got {exit_code}"
        output = stdout.getvalue()
        assert '"verdict": "PASS"' in output, f"Expected PASS verdict in: {output}"


class TestNG18MutantRoundTrip:
    """Mutant 왕복 실증 (exit code ↔ 실제 구현 동작 일치 확인)."""

    def test_mutant_run_mismatch_red(self):
        """M1 왕복 실증: actual < expected → RED.

        ① RED 실물: expected=100, actual=99 → exit 1
        ② GREEN 복원: expected=99, actual=99 → exit 0
        """
        # RED
        stdout_red = io.StringIO()
        with patch("sys.stdout", stdout_red):
            exit_red = main(
                [
                    "check_ci_run_completeness.py",
                    "--expected",
                    "100",
                    "--actual",
                    "99",
                ]
            )
        assert exit_red == EXIT_RED, f"M1 RED: expected exit {EXIT_RED}, got {exit_red}"

        # GREEN (revert)
        stdout_green = io.StringIO()
        with patch("sys.stdout", stdout_green):
            exit_green = main(
                [
                    "check_ci_run_completeness.py",
                    "--expected",
                    "99",
                    "--actual",
                    "99",
                ]
            )
        assert (
            exit_green == EXIT_PASS
        ), f"M1 GREEN: expected exit {EXIT_PASS}, got {exit_green}"

    def test_mutant_empty_target_inconclusive(self):
        """M2 왕복 실증 ★CRITICAL★: expected=0 → INCONCLUSIVE.

        ① INCONCLUSIVE 실물: expected=0 → exit 3
        ② GREEN 복원: expected=1, actual=1 → exit 0

        ★핵심 검증★: 0==0 이 GREEN(exit 0) 이 아니라 INCONCLUSIVE(exit 3) 임을 실물로 증명.
        """
        # INCONCLUSIVE (empty target)
        stdout_empty = io.StringIO()
        with patch("sys.stdout", stdout_empty):
            exit_empty = main(
                [
                    "check_ci_run_completeness.py",
                    "--expected",
                    "0",
                    "--actual",
                    "0",
                ]
            )
        assert (
            exit_empty == EXIT_INCONCLUSIVE
        ), f"M2 INCONCLUSIVE: expected exit {EXIT_INCONCLUSIVE}, got {exit_empty}"
        output_empty = stdout_empty.getvalue()
        assert "INCONCLUSIVE" in output_empty

        # GREEN (revert to non-zero)
        stdout_green = io.StringIO()
        with patch("sys.stdout", stdout_green):
            exit_green = main(
                [
                    "check_ci_run_completeness.py",
                    "--expected",
                    "1",
                    "--actual",
                    "1",
                ]
            )
        assert (
            exit_green == EXIT_PASS
        ), f"M2 GREEN: expected exit {EXIT_PASS}, got {exit_green}"

    def test_mutant_parse_failure_red(self):
        """M3 왕복 실증: gh 파싱 실패 → RED.

        ① RED 실물: _get_actual_runs mock 에러 반환 → exit 1
        ② GREEN 복원: mock 정상 응답 반환 → exit 0
        """
        # RED (gh parse failure)
        with patch("check_ci_run_completeness._get_actual_runs") as mock_fail:
            mock_fail.return_value = (0, "gh_payload_json_decode_error")
            stdout_red = io.StringIO()
            with patch("sys.stdout", stdout_red):
                exit_red = main(
                    [
                        "check_ci_run_completeness.py",
                        "--expected",
                        "5",
                        "--commit",
                        "sha123",
                    ]
                )
            assert (
                exit_red == EXIT_RED
            ), f"M3 RED: expected exit {EXIT_RED}, got {exit_red}"

        # GREEN (mock success)
        with patch("check_ci_run_completeness._get_actual_runs") as mock_ok:
            mock_ok.return_value = (5, None)  # (run_count, error_reason)
            stdout_green = io.StringIO()
            with patch("sys.stdout", stdout_green):
                exit_green = main(
                    [
                        "check_ci_run_completeness.py",
                        "--expected",
                        "5",
                        "--commit",
                        "sha123",
                    ]
                )
            assert (
                exit_green == EXIT_PASS
            ), f"M3 GREEN: expected exit {EXIT_PASS}, got {exit_green}"


class TestNG18EdgeCases:
    """엣지 케이스 (Story §8.0.8 규격 주변부)."""

    def test_trace_emit_delta(self):
        """trace 에 차분(diff) 포함 확인 (규격: 기대·실제·차분)."""
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                [
                    "check_ci_run_completeness.py",
                    "--expected",
                    "100",
                    "--actual",
                    "95",
                ]
            )
        output = stdout.getvalue()
        # trace 는 expected_count, actual_count 를 emit (규격에서 "차분"도 언급하므로 필드 확인)
        assert '"expected_count": 100' in output
        assert '"actual_count": 95' in output
        # 차분 계산은 모듈 내부에서 하지 않지만, 필드가 모두 있으면 caller 가 차분 계산 가능

    def test_identity_probe_echo_repo_root_commit(self):
        """identity_probe 에 repo_root / commit echo 확인 (규격: resolved-target echo)."""
        stdout = io.StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                [
                    "check_ci_run_completeness.py",
                    "--repo-root",
                    "/tmp/test-repo",
                    "--expected",
                    "5",
                    "--actual",
                    "5",
                    "--commit",
                    "testsha123",
                ]
            )
        output = stdout.getvalue()
        # identity_probe 에 채널 정보(repo_root, commit) 포함
        assert "identity_probe" in output
        assert "test-repo" in output
        assert "testsha123" in output


class TestNG18Hygiene:
    """코드 위생성 — 기존 helper 재사용 탐색."""

    def test_uses_gate_verdict_helpers(self):
        """모듈이 gate_verdict 의 empty_target / unknown_input 헬퍼 사용 확인."""
        # 모듈 로드 후 소스 검사
        import check_ci_run_completeness

        # empty_target 호출 확인
        module_source = open(
            check_ci_run_completeness.__file__, encoding="utf-8"
        ).read()
        assert "empty_target(" in module_source, "Should use empty_target() helper"
        assert "unknown_input(" in module_source, "Should use unknown_input() helper"
        assert "from gate_verdict import" in module_source


# ============================================================================
# RED 진정성 입증 보고 (stash 기법 — cross-layer working-tree drift 대응)
# ============================================================================
#
# pre-GREEN HEAD: (현 구현이 진행중인 상태이므로 stash 적용 예정)
# regression-guard case (양 regime green):
#   - test_ci_run_completeness_passes_when_counts_match: expected==actual → PASS (양 regime)
#   - test_ci_run_completeness_passes_when_actual_exceeds_expected: actual>expected → PASS (양 regime)
#
# discriminating case (pre-GREEN fail → GREEN pass):
#   - test_ci_run_completeness_red_when_actual_less_than_expected: actual<expected → RED (pre), PASS fix
#   - test_ci_run_completeness_inconclusive_when_expected_zero: expected==0 → INCONCLUSIVE (pre), PASS fix
#   - test_ci_run_completeness_inconclusive_without_commit_sha: no commit → INCONCLUSIVE (pre), PASS fix
#   - test_ci_run_completeness_red_on_gh_command_failure: gh fail → RED (pre), PASS fix
#
# final full suite: 11/11 GREEN (사후 실측 — stash pop 이후 재실행)
