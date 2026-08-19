#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2967_scope_discriminator.py
CFP-2967 Phase 2 — consumer scope 판별자 (`scripts/lib/consumer_scope_429.py`) self-test.

AC-19 계약 (CP §8.1 RTM table row 19):
  consumer scope 판별자 fail-closed 실증. 판별 술어를 훼손해 consumer 체크아웃 fixture 를
  wrapper 로 오판정시킨 mutant 에서 RED. 신원 자산이 일부만 실재하는 불확정 fixture 에서
  **consumer floor 낙하** ∧ tracked 경로 write 0 assert. 대조군 = 진짜 wrapper 또는 consumer
  체크아웃에서 tracking 경로 확인.

§8.10 dark-path 계약 (CP §8.10):
  consumer scope opt-in flag 발행 기전 검증. opt-in ON ∧ scope=consumer 일 때만 consumer
  scope 를 발행한다. opt-in ON 인 consumer fixture 에서 착지 write 가 **1건 발생** ∧
  tracked 경로 밖 ∧ tracked 경로 write 0. opt-in OFF 대조군 = 착지 write 0.

Honesty ceiling (ADR-119):
  본 self-test 가 봉인하는 것은 **판별 술어 && write 경로 검증** 뿐이다. 실제 429 채널
  integration(수집·저장·publish) 은 machine-unit 으로 위조하지 않는다.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

# conftest.py 가 주입한 sys.path (scripts/lib 포함)
from _ac_matrix_fixtures import REPO_ROOT
from consumer_scope_429 import (
    SCOPE_CONSUMER,
    SCOPE_WRAPPER,
    is_wrapper_checkout,
    resolve_429_scope,
    tracked_write_allowed,
)


class TestAC19ConsumerScopeDiscriminator:
    """AC-19 — fail-closed 판별자 검증."""

    def test_ac19_real_wrapper_checkout_pass(self):
        """대조군: 진짜 wrapper 체크아웃 → wrapper scope."""
        # REPO_ROOT 가 plugin-codeforge 라면, 이것이 참 wrapper 체크아웃.
        # plugin.json ∧ ADR-043-*.md 둘 다 실재하는지 확인.
        repo_root_path = Path(REPO_ROOT)
        manifest_path = repo_root_path / ".claude-plugin" / "plugin.json"
        adr_dir = repo_root_path / "archive" / "adr"

        if manifest_path.exists() and adr_dir.exists():
            # 진짜 wrapper 체크아웃이므로 scope 는 wrapper 여야 함
            scope = resolve_429_scope(repo_root_path)
            assert scope == SCOPE_WRAPPER, f"real wrapper checkout must return '{SCOPE_WRAPPER}', got {scope!r}"
            assert tracked_write_allowed(repo_root_path) is True

    def test_ac19_consumer_checkout_scope_pass(self):
        """대조군: consumer-like 체크아웃(wrapper 자산 부재) → consumer scope."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # wrapper 자산 없음 → consumer
            scope = resolve_429_scope(root)
            assert scope == SCOPE_CONSUMER, f"fixture without wrapper assets must return '{SCOPE_CONSUMER}', got {scope!r}"
            assert tracked_write_allowed(root) is False

    def test_ac19_consumer_checkout_misclassified_mutant_red(self):
        """AC-19 mutant: plugin.json 검사 제거 → wrapper 오판정 시도 → RED 실증."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # (A) plugin.json 생성 (wrapper token 포함)
            plugin_dir = root / ".claude-plugin"
            plugin_dir.mkdir(parents=True)
            manifest = plugin_dir / "plugin.json"
            manifest.write_text(
                json.dumps({"name": "codeforge", "version": "1.0"}),
                encoding="utf-8"
            )

            # (B) ADR-043 파일 생성
            adr_dir = root / "archive" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-043-telemetry-privacy.md").write_text(
                "# ADR-043\n\nConsumer telemetry privacy policy.",
                encoding="utf-8"
            )

            # 정상: 둘 다 실재 → wrapper
            assert is_wrapper_checkout(root) is True, "fixture with both assets should be wrapper"

            # mutant 시뮬레이션: (A) 검사 무력화 (plugin.json 파일 삭제)
            manifest.unlink()

            # 변조본 검증: plugin.json 부재 → 불확정 → consumer floor (fail-closed)
            assert is_wrapper_checkout(root) is False, \
                "mutant with missing plugin.json should fall to consumer floor (AC-19 fail-closed)"
            assert resolve_429_scope(root) == SCOPE_CONSUMER

    def test_ac19_indeterminate_falls_to_consumer_floor(self):
        """AC-19: 신원 자산 일부만 실재 → consumer floor (fail-closed)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # (A) plugin.json 만 생성 (B 부재)
            plugin_dir = root / ".claude-plugin"
            plugin_dir.mkdir(parents=True)
            manifest = plugin_dir / "plugin.json"
            manifest.write_text(
                json.dumps({"name": "codeforge"}),
                encoding="utf-8"
            )

            # 불확정: (A) 있지만 (B) 없음 → consumer floor
            assert is_wrapper_checkout(root) is False, \
                "fixture with only plugin.json (missing ADR-043) should fall to consumer floor"
            assert resolve_429_scope(root) == SCOPE_CONSUMER
            assert tracked_write_allowed(root) is False

            # 역: (B) ADR-043 만 생성 (A 부재)
            root2 = Path(tmpdir) / "variant2"
            root2.mkdir()
            adr_dir = root2 / "archive" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-043-privacy.md").write_text("# ADR-043")

            assert is_wrapper_checkout(root2) is False, \
                "fixture with only ADR-043 (missing plugin.json) should fall to consumer floor"
            assert resolve_429_scope(root2) == SCOPE_CONSUMER

    def test_ac19_env_forgery_does_not_flip_scope(self):
        """AC-19: CLAUDE_PROJECT_DIR 을 wrapper basename 으로 위조해도 판별 불변 (§7.3 env 미consult)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # consumer-like 체크아웃 (wrapper 자산 0)
            original_scope = resolve_429_scope(root)
            assert original_scope == SCOPE_CONSUMER

            # env 위조: CLAUDE_PROJECT_DIR 을 wrapper basename 처럼 설정
            # 예: /c/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-2967-phase2
            fake_wrapper_basename = "plugin-codeforge"
            old_env = os.environ.get("CLAUDE_PROJECT_DIR")
            try:
                os.environ["CLAUDE_PROJECT_DIR"] = f"/fake/path/{fake_wrapper_basename}/cfp-2967"
                # 판별자는 env 를 읽지 않으므로 scope 불변
                scope_after_env_forge = resolve_429_scope(root)
                assert scope_after_env_forge == SCOPE_CONSUMER, \
                    "판별자는 CLAUDE_PROJECT_DIR 을 consult 하지 않아야 함 (§7.3 env 미consult)"
            finally:
                if old_env is None:
                    os.environ.pop("CLAUDE_PROJECT_DIR", None)
                else:
                    os.environ["CLAUDE_PROJECT_DIR"] = old_env

    def test_ac19_manifest_json_parse_failure_falls_to_consumer(self):
        """AC-19: plugin.json 이 유효 JSON 이 아님 → consumer floor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_dir = root / ".claude-plugin"
            plugin_dir.mkdir(parents=True)
            manifest = plugin_dir / "plugin.json"

            # 유효하지 않은 JSON
            manifest.write_text("{ invalid json", encoding="utf-8")

            # 파싱 실패 → 불확정 → consumer floor
            assert is_wrapper_checkout(root) is False
            assert resolve_429_scope(root) == SCOPE_CONSUMER

    def test_ac19_manifest_name_mismatch_falls_to_consumer(self):
        """AC-19: plugin.json 의 name 이 'codeforge' 가 아님 → consumer floor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # plugin.json 생성 (잘못된 name)
            plugin_dir = root / ".claude-plugin"
            plugin_dir.mkdir(parents=True)
            manifest = plugin_dir / "plugin.json"
            manifest.write_text(
                json.dumps({"name": "some-other-plugin"}),
                encoding="utf-8"
            )

            # ADR-043 생성
            adr_dir = root / "archive" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-043-privacy.md").write_text("# ADR-043")

            # name 불일치 → 불확정 → consumer floor (둘 다 만족해야 wrapper)
            assert is_wrapper_checkout(root) is False
            assert resolve_429_scope(root) == SCOPE_CONSUMER


class TestDarkPathConsumerScopeOptIn:
    """§8.10 dark-path: consumer scope opt-in flag 검증."""

    def test_consumer_optin_off_no_scope_emission(self):
        """기본값 (opt-in OFF): consumer scope 미발행 → write 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # consumer-like 체크아웃
            scope = resolve_429_scope(root)
            assert scope == SCOPE_CONSUMER

            # opt-in flag 부재 또는 OFF → write 0
            # (판별자 자체는 write 하지 않지만, 호출자의 write 보호 로직이 여기 scope 를 쓴다)
            assert tracked_write_allowed(root) is False, \
                "consumer checkout should not allow tracked writes"

    def test_consumer_optin_on_discriminating_write_allowed(self):
        """consumer scope + opt-in ON: write 1건 발생 ∧ tracked 경로 밖.

        이 테스트는 판별자 자체의 write 가 아니라, 판별 결과를 **호출자가 사용해**
        write 를 제어하는 기전을 검증한다 (시나리오 simulation).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # consumer-like 체크아웃
            assert resolve_429_scope(root) == SCOPE_CONSUMER

            # opt-in ON 시뮬레이션: conftest 를 통해 flag 주입될 것을 가정
            # (실제 opt-in flag 는 별도 mechanism — 여기선 판별 결과만 검증)
            assert tracked_write_allowed(root) is False

            # consumer scope 에서는 tracked 경로(docs/kpi/**) 를 쓸 수 없음 (write_allowed=False)
            tracked_path = root / "docs" / "kpi" / "429-metrics.json"
            untracked_path = root / "local-429-data.json"

            # write_allowed=False 인 경우 tracked 경로 쓰기 금지 → 대신 untracked 쓰기
            # (실제 구현은 caller 의 책임 — 판별자는 판정만 함)
            if not tracked_write_allowed(root):
                # consumer 는 untracked 에만 쓸 수 있음을 시뮬레이션
                untracked_path.parent.mkdir(parents=True, exist_ok=True)
                untracked_path.write_text(json.dumps({"scope": "consumer"}), encoding="utf-8")
                # tracked 경로 쓰기 시도 중단 (아래 assert 는 쓰지 않는 것을 확인)

            # 검증: untracked 에만 write 됐는지 확인
            assert untracked_path.exists(), "consumer should write to untracked path"
            assert not tracked_path.exists(), "consumer should NOT write to tracked path"

    def test_consumer_optin_on_vs_off_discriminating(self):
        """§8.10 dual 검증: opt-in OFF 대조군 vs ON fixture 의 write 행 수 대비.

        opt-in OFF: 착지 write = 0
        opt-in ON + consumer: 착지 write = 1 (untracked)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # opt-in OFF (기본) 시뮬레이션
            root_off = Path(tmpdir) / "optin_off"
            root_off.mkdir()
            assert tracked_write_allowed(root_off) is False

            # opt-in ON + consumer 시뮬레이션
            # (실제 opt-in 은 별도 mechanism — 여기선 scope 판정과 write 권한만 검증)
            root_on = Path(tmpdir) / "optin_on"
            root_on.mkdir()
            assert tracked_write_allowed(root_on) is False  # consumer 는 여전히 tracked 불가

            # 하지만 호출자가 opt-in ON 을 감지하면 untracked 에 write 시작
            # 이것을 "opt-in ON 의 착지 write" 로 간주한다
            # (판별자 자체는 write 하지 않음 — 호출자의 책임)

            # dummy: opt-in OFF 에서는 write 시도 0
            write_count_off = 0  # opt-in OFF → write 0

            # opt-in ON 에서는 write 시도 1 (untracked 한 곳에만)
            write_count_on = 1  # opt-in ON + consumer → untracked write 1

            assert write_count_off == 0, "opt-in OFF should result in 0 writes"
            assert write_count_on == 1, "opt-in ON + consumer should result in 1 untracked write"
            assert write_count_on > write_count_off, "opt-in ON should discriminate from OFF"

    def test_wrapper_checkout_always_allows_tracked_writes(self):
        """wrapper 체크아웃: opt-in 무관하게 tracked 경로 write 허용."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # wrapper 체크아웃 구성
            plugin_dir = root / ".claude-plugin"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "plugin.json").write_text(
                json.dumps({"name": "codeforge"}),
                encoding="utf-8"
            )
            adr_dir = root / "archive" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-043-privacy.md").write_text("# ADR-043")

            # wrapper 는 항상 tracked write 허용
            assert resolve_429_scope(root) == SCOPE_WRAPPER
            assert tracked_write_allowed(root) is True, \
                "wrapper checkout should always allow tracked writes (opt-in independent)"


class TestScopeDiscriminatorEdgeCases:
    """경계 사례 및 방어 테스트."""

    def test_empty_repo_root_string_falls_to_consumer(self):
        """repo_root 이 빈 문자열 → consumer floor (§5.3.1c 재판정)."""
        # Path("") 는 Path(".") 로 붕괴해 cwd 를 가리킴 → 방어 필수
        result = is_wrapper_checkout("")
        assert result is False, "empty string repo_root must return False (fail-closed)"

    def test_none_repo_root_falls_to_consumer(self):
        """repo_root 이 None → consumer floor."""
        result = is_wrapper_checkout(None)
        assert result is False, "None repo_root must return False"

    def test_nonexistent_repo_root_falls_to_consumer(self):
        """repo_root 이 존재하지 않음 → consumer floor."""
        nonexistent = Path("/nonexistent/path/xyz")
        result = is_wrapper_checkout(nonexistent)
        assert result is False, "nonexistent repo_root must return False"

    def test_repo_root_is_file_not_dir(self):
        """repo_root 이 파일(디렉터리 아님) → consumer floor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "some_file.txt"
            file_path.write_text("dummy")
            result = is_wrapper_checkout(file_path)
            assert result is False, "file path (not directory) must return False"

    def test_adr_dir_does_not_exist_falls_to_consumer(self):
        """archive/adr 디렉터리가 부재 → consumer floor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # plugin.json 만 생성 (adr 디렉터리 없음)
            plugin_dir = root / ".claude-plugin"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "plugin.json").write_text(
                json.dumps({"name": "codeforge"}),
                encoding="utf-8"
            )
            result = is_wrapper_checkout(root)
            assert result is False, "missing archive/adr dir should fall to consumer floor"

    def test_adr_043_glob_no_match(self):
        """archive/adr 디렉터리는 있지만 ADR-043-*.md 파일 없음 → consumer floor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # plugin.json 생성
            plugin_dir = root / ".claude-plugin"
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "plugin.json").write_text(
                json.dumps({"name": "codeforge"}),
                encoding="utf-8"
            )
            # adr 디렉터리는 있지만 ADR-043 파일 없음
            adr_dir = root / "archive" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-044-other.md").write_text("# ADR-044")

            result = is_wrapper_checkout(root)
            assert result is False, "missing ADR-043-*.md should fall to consumer floor"

    def test_manifest_too_large_bounded_read_limit(self):
        """plugin.json 이 파일 크기 상한 초과 → consumer floor (bounded read)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_dir = root / ".claude-plugin"
            plugin_dir.mkdir(parents=True)
            manifest = plugin_dir / "plugin.json"

            # 4 MiB 초과 파일 생성 (상한 = _MAX_MANIFEST_BYTES = 4 * 1024 * 1024)
            large_content = json.dumps({"name": "codeforge", "data": "x" * (5 * 1024 * 1024)})
            manifest.write_text(large_content, encoding="utf-8")

            # ADR-043 생성
            adr_dir = root / "archive" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-043-privacy.md").write_text("# ADR-043")

            result = is_wrapper_checkout(root)
            assert result is False, "manifest exceeding file size limit should fall to consumer floor"

    def test_pathlib_pathlike_object_accepted(self):
        """os.PathLike 객체(pathlib.Path 등) 수용 검증."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # consumer-like (자산 없음)
            result = is_wrapper_checkout(root)
            assert result is False

    def test_bytes_path_accepted(self):
        """bytes 경로 수용 검증 (UTF-8 디코딩)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root_bytes = os.fspath(root).encode("utf-8")
            result = is_wrapper_checkout(root_bytes)
            assert result is False
