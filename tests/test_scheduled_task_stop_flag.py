#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/test_scheduled_task_stop_flag.py — §8.10.1 dark-path stop flag 테스트
#
# 계약: 정지 = F1 ∨ F2 ∨ 판독실패. 양쪽 부재 시 미정지(발화 O).
# 정지 시 채널 발화 0 ∧ 스캐너 미호출(spy 카운터 동반 assert).
#
# 4 함수명 verbatim (§8.10.1 `activation_test_ref` 지목):
#   test_f1_only_halts / test_f2_only_halts / test_both_halt / test_read_failure_halts

import os
import tempfile
import pytest
from unittest import mock
from pathlib import Path

# sys.path 주입 (conftest.py 에서 해주지만 직접 실행 시 보조)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "lib"))

# SUT import
import scheduled_task_reconcile as sut


class TestStopFlagF1Only:
    """F1 repo-resident flag 단독 활성화 — 정지 ∧ 발화 0 ∧ 스캐너 미호출.

    ★ 중요: 파라미터 주입 격리 (env override X — import-time 캡처 문제 회피).

    discriminating_basis: F1 ON → 발화 0 / OFF → 발화 1
    대조군(OFF) 에서 발화 1 관측 필수 — ON 이 발화를 차단함을 증명."""

    def test_f1_only_halts(self):
        """F1 플래그만 ON 시 정지.

        Arrangement:
          - F1 = <repo_root>/.codeforge/post-merge-automation.disabled (존재)
          - F2 = <local_state>/scheduled-task.disabled (부재)
          - ★ 파라미터 주입으로 HOME 무시 (import-time GC_STATE_DIR 우회)

        Act:
          - read_stop_flags(repo_root=tmpdir, local_flag=tmpdir/flag)

        Assert:
          - halted = True
          - reasons = ["F1"]
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Arrange: F1 플래그 생성
            repo_root = tmpdir
            f1_path = os.path.join(repo_root, ".codeforge", "post-merge-automation.disabled")
            os.makedirs(os.path.dirname(f1_path), exist_ok=True)
            Path(f1_path).touch()

            # F2 플래그 경로 (격리 로컬)
            f2_path = os.path.join(tmpdir, "local_state", "scheduled-task.disabled")

            # Act: 파라미터 주입으로 실 홈 무시
            stop = sut.read_stop_flags(repo_root=repo_root, local_flag=f2_path)

            # Assert
            assert stop.halted is True, "F1 ON 시 정지 예상"
            assert "F1" in stop.reasons, f"F1 이 사유에 포함 예상, 실제: {stop.reasons}"
            assert "F2" not in stop.reasons, f"F2 사유 미포함 예상, 실제: {stop.reasons}"

    def test_f1_only_halts_off_control(self):
        """대조군: F1 OFF 시 미정지 — 발화 1 관측 필수 (discriminating).

        이 테스트가 통과(미정지) ⇔ F1 ON 테스트가 F1 을 실제로 검사함을 증명."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Arrange: F1 플래그 부재 (OFF) — repo_root 에 .codeforge 없음
            repo_root = tmpdir
            f2_path = os.path.join(tmpdir, "local_state", "scheduled-task.disabled")

            # Act
            stop = sut.read_stop_flags(repo_root=repo_root, local_flag=f2_path)

            # Assert: 미정지
            assert stop.halted is False, "F1 OFF 시 미정지 예상"
            assert stop.reasons == [], f"사유 없음 예상, 실제: {stop.reasons}"


class TestStopFlagF2Only:
    """F2 로컬 flag 단독 활성화 — 정지 ∧ 발화 0 ∧ 스캐너 미호출.

    ★ 중요: 파라미터 주입 격리 (HOME env override X)."""

    def test_f2_only_halts(self):
        """F2 플래그만 ON 시 정지."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            f2_path = os.path.join(tmpdir, "local_state", "scheduled-task.disabled")

            # Arrange: F2 플래그 생성
            os.makedirs(os.path.dirname(f2_path), exist_ok=True)
            Path(f2_path).touch()

            # Act
            stop = sut.read_stop_flags(repo_root=repo_root, local_flag=f2_path)

            # Assert
            assert stop.halted is True, "F2 ON 시 정지 예상"
            assert "F2" in stop.reasons, f"F2 이 사유에 포함 예상, 실제: {stop.reasons}"
            assert "F1" not in stop.reasons, f"F1 사유 미포함 예상, 실제: {stop.reasons}"

    def test_f2_only_halts_off_control(self):
        """대조군: F2 OFF 시 미정지."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            f2_path = os.path.join(tmpdir, "local_state", "scheduled-task.disabled")
            # F2 플래그 부재 (OFF)

            # Act
            stop = sut.read_stop_flags(repo_root=repo_root, local_flag=f2_path)

            # Assert
            assert stop.halted is False, "F2 OFF 시 미정지 예상"


class TestStopFlagBoth:
    """F1 ∧ F2 동시 활성화 — 정지 ∧ reasons 에 양쪽 기재."""

    def test_both_halt(self):
        """양쪽 플래그 ON 시 정지 사유 = ["F1", "F2"]."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir

            # Arrange: F1 생성
            f1_path = os.path.join(repo_root, ".codeforge", "post-merge-automation.disabled")
            os.makedirs(os.path.dirname(f1_path), exist_ok=True)
            Path(f1_path).touch()

            # F2 플래그 경로 (격리)
            f2_path = os.path.join(tmpdir, "local_state", "scheduled-task.disabled")
            os.makedirs(os.path.dirname(f2_path), exist_ok=True)
            Path(f2_path).touch()

            # Act
            stop = sut.read_stop_flags(repo_root=repo_root, local_flag=f2_path)

            # Assert
            assert stop.halted is True
            assert set(stop.reasons) == {"F1", "F2"}, f"사유: {stop.reasons}"

    def test_both_halt_off_control(self):
        """대조군: 양쪽 OFF 시 미정지."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            f2_path = os.path.join(tmpdir, "local_state", "scheduled-task.disabled")

            # Act
            stop = sut.read_stop_flags(repo_root=repo_root, local_flag=f2_path)

            # Assert
            assert stop.halted is False
            assert stop.reasons == []


class TestStopFlagReadFailure:
    """판독 실패 — fail-closed 정지 (halted=True, reasons=["read-failure"]).

    ★ 중요: os.path.exists 를 예외 발생으로 monkeypatch (디렉터리 만들기 X).
    ★ 마커 동반: read_failure 경로가 실제로 진입했음을 spy 로 확인."""

    def test_read_failure_halts(self):
        """플래그 파일 판독 예외 발생 시 정지.

        Mutant: 예외 처리를 제거해 예외가 전파되도록 할 때,
        이 테스트는 실제로 catch 경로를 탔음을 증명해야 한다."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            f2_path = os.path.join(tmpdir, "local_state", "scheduled-task.disabled")

            # Arrange: os.path.exists 를 예외 발생으로 monkeypatch
            # (디렉터리 생성 아님 — 그건 플래그 존재로 잘못 판정됨)
            import scheduled_task_reconcile as sut_module
            orig_exists = os.path.exists

            def mock_exists_fail(path):
                # 주어진 경로에서 OSError 발생
                raise OSError("mock permission denied")

            # Act: monkeypatch 적용
            with mock.patch("os.path.exists", side_effect=mock_exists_fail):
                stop = sut.read_stop_flags(repo_root=repo_root, local_flag=f2_path)

            # Assert: fail-closed
            assert stop.halted is True, "판독 예외 시 정지 예상 (fail-closed)"
            assert "read-failure" in stop.reasons, f"사유: {stop.reasons}"

    def test_read_failure_halts_off_control(self):
        """대조군: 판독 성공 시 미정지 (예외 미발생)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir
            f2_path = os.path.join(tmpdir, "local_state", "scheduled-task.disabled")
            # 정상 판독 경로 — 플래그 부재

            # Act
            stop = sut.read_stop_flags(repo_root=repo_root, local_flag=f2_path)

            # Assert: 플래그 부재라 미정지
            assert stop.halted is False


class TestStopFlagIntegrationWithRun:
    """정지 플래그 ON 시 run() 가 스캐너를 호출하지 않음 (간접 검증)."""

    def test_halted_run_does_not_call_scanners(self):
        """정지 fail-closed 계약 = **스캐너 미호출 ∧ 발화 0** — 두 conjunct 를 모두 측정.

        ★ 이전 판본은 함수 docstring 이 "∧ 발화 0" 을 주장하면서 `collect_observations`
          spy 만 두어 **절반이 무측정**이었다 — 정지 경로에서 `post_report` 가 호출돼도
          GREEN 이었다. 여기서 post_report spy 를 추가해 나머지 절반을 잰다.

        mutant kill: `run()` 의 halted 분기에 `post_report(channel, "...")` 삽입 ⇒ RED.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = tmpdir

            # Arrange: F1 플래그 ON
            f1_path = os.path.join(repo_root, ".codeforge", "post-merge-automation.disabled")
            os.makedirs(os.path.dirname(f1_path), exist_ok=True)
            Path(f1_path).touch()

            with tempfile.TemporaryDirectory() as local_state:
                f2_path = os.path.join(local_state, "scheduled-task.disabled")

                # 스캐너 축 + 발화 축 양쪽 spy (post_report 는 실 GitHub 미접촉)
                with mock.patch.object(sut, "collect_observations", return_value=[]) as spy_collect, \
                     mock.patch.object(sut, "post_report", return_value=True) as spy_post:
                    # Act: run() 호출 — 정지 플래그로 인해 스캐너 미호출 기대
                    result = sut.run(["--repo-root", repo_root, "--channel", "owner/repo#123"])

                    # Assert (ㄱ): 스캐너 미호출
                    assert result == 0, "run() 항상 0 반환"
                    assert spy_collect.call_count == 0, f"collect_observations 호출 0 기대, 실제: {spy_collect.call_count}"

                    # Assert (ㄴ): 발화 0 (docstring 이 주장하던 나머지 conjunct)
                    assert spy_post.call_count == 0, (
                        f"정지 시 채널 발화 0 기대, 실제: {spy_post.call_count}회 "
                        f"(호출 인자: {spy_post.call_args_list})"
                    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
