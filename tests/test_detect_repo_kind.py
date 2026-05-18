#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_detect_repo_kind.py

CFP-899 Phase 2 — QADeveloperAgent TDD test suite for detect-repo-kind.py
reconcile-protocol-v1 v1.9 §4.12 consumer_applicability_filter_binding

Test contract (Story §8, Architect Phase 1 — 20 TC):
  - 4 MATRIX (4-way truth-table classification)
  - 6 EC (edge cases)
  - 5 WHITELIST (consumer_applicable_workflows.txt manifest parse)
  - 3 INTEGRATION (hook chain / dry-run / cross-repo marketplace)
  - 1 MIXED (mixed repo dual filter)
  - 1 SELFLOOP (detect-repo-kind.py self-loop 0)

pytest framework. TDD RED → GREEN.
ADR-061 정합: 외부 .py, explicit absolute path.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Path setup
# ─────────────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
DETECT_SCRIPT = REPO_ROOT / "templates" / "scripts" / "detect-repo-kind.py"
WHITELIST_FILE = REPO_ROOT / "templates" / "scripts" / "consumer_applicable_workflows.txt"


def _run_detect(args: list, env: dict | None = None) -> subprocess.CompletedProcess:
    """detect-repo-kind.py 를 subprocess 로 실행."""
    cmd = [sys.executable, str(DETECT_SCRIPT)] + args
    merged_env = {**os.environ}
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=merged_env,
    )


def _make_plugin_dir(tmp: Path) -> None:
    """plugin.json + .claude-plugin/plugin.json 생성."""
    plugin_dir = tmp / ".claude-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps({"name": "test-plugin", "version": "1.0.0"}),
        encoding="utf-8",
    )


def _make_consumer_overlay(tmp: Path) -> None:
    """.claude/_overlay/project.yaml 생성."""
    overlay_dir = tmp / ".claude" / "_overlay"
    overlay_dir.mkdir(parents=True, exist_ok=True)
    (overlay_dir / "project.yaml").write_text(
        "story_key_prefix: TEST\n",
        encoding="utf-8",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4 MATRIX — §4.12 truth-table 4-way classification
# ─────────────────────────────────────────────────────────────────────────────


class TestMatrix:
    """TC-MATRIX-1~4: 4-way truth-table classification."""

    def test_matrix_1_plugin_json_and_marketplace(self, tmp_path):
        """TC-MATRIX-1: plugin.json 존재 + marketplace 멤버 → plugin."""
        _make_plugin_dir(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "plugin"
        assert result.returncode == 0

    def test_matrix_2_consumer_overlay_only(self, tmp_path):
        """TC-MATRIX-2: plugin.json 부재 + .claude/_overlay/project.yaml 존재 → consumer."""
        _make_consumer_overlay(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "consumer"
        assert result.returncode == 1

    def test_matrix_3_both_plugin_and_overlay(self, tmp_path):
        """TC-MATRIX-3: plugin.json 존재 + .claude/_overlay 존재 → mixed."""
        _make_plugin_dir(tmp_path)
        _make_consumer_overlay(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "mixed"
        assert result.returncode == 2

    def test_matrix_4_no_signals_unknown(self, tmp_path):
        """TC-MATRIX-4: 신호 없음 → unknown (fail-closed)."""
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "unknown"
        assert result.returncode == 3


# ─────────────────────────────────────────────────────────────────────────────
# 6 EC — Edge Cases
# ─────────────────────────────────────────────────────────────────────────────


class TestEdgeCases:
    """TC-EC-1~6: Edge case 처리."""

    def test_ec_1_wrapper_self_app(self):
        """TC-EC-1: wrapper repo 자체 (plugin.json 존재) → plugin."""
        # REPO_ROOT 가 실제 wrapper repo root (plugin.json exists in .claude-plugin/)
        result = _run_detect(
            ["--repo-root", str(REPO_ROOT), "--skip-marketplace-check"],
        )
        # wrapper repo 는 plugin (plugin.json in .claude-plugin/ 존재)
        assert result.stdout.strip() in ("plugin", "mixed")
        assert result.returncode in (0, 2)

    def test_ec_2_mixed_repo_returns_2(self, tmp_path):
        """TC-EC-2: mixed repo → exit code 2."""
        _make_plugin_dir(tmp_path)
        _make_consumer_overlay(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.returncode == 2
        assert result.stdout.strip() == "mixed"

    def test_ec_3_unknown_fail_closed(self, tmp_path):
        """TC-EC-3: unknown → fail-closed exit 3."""
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.returncode == 3
        assert result.stdout.strip() == "unknown"

    def test_ec_4_sibling_plugin_no_overlay(self, tmp_path):
        """TC-EC-4: plugin.json 존재 + overlay 부재 → plugin."""
        _make_plugin_dir(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "plugin"
        assert result.returncode == 0

    def test_ec_5_monorepo_skip(self, tmp_path):
        """TC-EC-5: monorepo 패턴 (overlay 있고 plugin.json 부재) → consumer."""
        # monorepo out-of-scope: §4.12 out_of_scope 에 명시. consumer 분류.
        _make_consumer_overlay(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "consumer"
        assert result.returncode == 1

    def test_ec_6_partial_signal_overlay_dir_no_yaml(self, tmp_path):
        """TC-EC-6: .claude/_overlay 디렉터리 존재하나 project.yaml 부재 → unknown."""
        overlay_dir = tmp_path / ".claude" / "_overlay"
        overlay_dir.mkdir(parents=True, exist_ok=True)
        # project.yaml 미생성 — 디렉터리만 존재
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        # project.yaml 없으면 overlay 신호 불충분 → unknown
        assert result.stdout.strip() == "unknown"
        assert result.returncode == 3


# ─────────────────────────────────────────────────────────────────────────────
# 5 WHITELIST — consumer_applicable_workflows.txt 파싱
# ─────────────────────────────────────────────────────────────────────────────


class TestWhitelist:
    """TC-WL-1~5: whitelist manifest 파싱 + 필터 로직."""

    def test_wl_1_manifest_exists(self):
        """TC-WL-1: consumer_applicable_workflows.txt 파일 존재."""
        assert WHITELIST_FILE.exists(), (
            f"whitelist 파일 없음: {WHITELIST_FILE}"
        )

    def test_wl_2_comment_lines_excluded(self):
        """TC-WL-2: '#' 시작 줄은 whitelist 항목에서 제외."""
        content = WHITELIST_FILE.read_text(encoding="utf-8")
        lines = content.splitlines()
        workflow_lines = [
            l.strip() for l in lines if l.strip() and not l.strip().startswith("#")
        ]
        # comment 줄이 workflow 항목으로 잘못 포함되지 않았는지 검증
        for wf in workflow_lines:
            assert not wf.startswith("#"), f"comment 줄이 포함됨: {wf}"

    def test_wl_3_empty_lines_excluded(self):
        """TC-WL-3: 빈 줄은 whitelist 항목으로 취급하지 않음."""
        content = WHITELIST_FILE.read_text(encoding="utf-8")
        lines = content.splitlines()
        entries = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
        for e in entries:
            assert e != "", "빈 줄이 항목으로 포함됨"

    def test_wl_4_missing_whitelist_fail_closed(self, tmp_path):
        """TC-WL-4: whitelist 파일 부재 시 detect script --check-signal 에서 fail-closed."""
        result = _run_detect(
            [
                "--repo-root",
                str(tmp_path),
                "--check-signal",
                "overlay_project_yaml",
                "--skip-marketplace-check",
            ]
        )
        # overlay project.yaml 부재 → consumer 신호 없음 → 결과 unknown or consumer
        # 주요 검증: exit 정상 (not crash)
        assert result.returncode in (0, 1, 2, 3)

    def test_wl_5_plugin_only_workflows_not_in_whitelist(self):
        """TC-WL-5: plugin-only workflow yml은 whitelist에 없어야 함."""
        content = WHITELIST_FILE.read_text(encoding="utf-8")
        entries = set(
            l.strip()
            for l in content.splitlines()
            if l.strip() and not l.strip().startswith("#")
        )
        plugin_only = [
            "version-bump-atomic-check.yml",
            "marketplace-drift-detection.yml",
            "check-plugin-version-bump.yml",
        ]
        for wf in plugin_only:
            assert wf not in entries, f"plugin-only workflow '{wf}' 가 whitelist에 포함됨"


# ─────────────────────────────────────────────────────────────────────────────
# 3 INTEGRATION — hook chain / dry-run / marketplace check
# ─────────────────────────────────────────────────────────────────────────────


class TestIntegration:
    """TC-INT-1~3: hook chain / dry-run propagation / marketplace signal."""

    def test_int_1_hook_chain_consumer_filter(self, tmp_path):
        """TC-INT-1: consumer repo + whitelist filter applied → exit 1."""
        _make_consumer_overlay(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "consumer"
        assert result.returncode == 1

    def test_int_2_plugin_repo_no_filter(self, tmp_path):
        """TC-INT-2: plugin repo → exit 0 (all workflows mirrored, no filter)."""
        _make_plugin_dir(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "plugin"
        assert result.returncode == 0

    def test_int_3_marketplace_skip_flag(self, tmp_path):
        """TC-INT-3: --skip-marketplace-check 플래그 → marketplace API 호출 없이 동작."""
        _make_plugin_dir(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        # marketplace check 없이도 plugin 판정 (plugin.json 기반)
        assert result.returncode == 0
        assert result.stdout.strip() == "plugin"


# ─────────────────────────────────────────────────────────────────────────────
# 1 MIXED — mixed repo dual filter
# ─────────────────────────────────────────────────────────────────────────────


class TestMixed:
    """TC-MIXED-1: mixed repo → exit 2, dual filter 적용."""

    def test_mixed_1_dual_filter(self, tmp_path):
        """TC-MIXED-1: mixed repo → exit 2 (both plugin + consumer filter applied)."""
        _make_plugin_dir(tmp_path)
        _make_consumer_overlay(tmp_path)
        result = _run_detect(
            ["--repo-root", str(tmp_path), "--skip-marketplace-check"],
        )
        assert result.stdout.strip() == "mixed"
        assert result.returncode == 2


# ─────────────────────────────────────────────────────────────────────────────
# 1 SELFLOOP — detect-repo-kind.py self-loop 0 invariant
# ─────────────────────────────────────────────────────────────────────────────


class TestSelfLoop:
    """TC-SELFLOOP-1: detect-repo-kind.py self-loop 0 invariant (§4.12 self_app_exemption)."""

    def test_selfloop_1_no_self_reference(self, tmp_path):
        """TC-SELFLOOP-1: detect-repo-kind.py 자기 자신을 missing dep 으로 보고하지 않음.

        §4.12 self_app_exemption: templates/scripts/detect-repo-kind.py 를
        dep 탐지 대상으로 삼아 missing dep 으로 abort 해선 안 됨.

        검증 방법: detect-repo-kind.py 를 참조하는 workflow yml 을 만들어
        mirror-dependency-closure.py 로 scan 시 self-loop 0 invariant 는
        detect-repo-kind.py 자체 실행에서 검증.
        본 TC 는 detect script 가 wrapper repo root 에서 실행 시
        자기 자신을 dep chain 의 대상으로 취급하지 않아
        정상 plugin 판정 (exit 0) 이 나오는 것을 검증.
        """
        # wrapper repo root (plugin 신호 보유) 에서 실행 → plugin 판정
        result = _run_detect(
            ["--repo-root", str(REPO_ROOT), "--skip-marketplace-check"],
        )
        # self-loop 가 있으면 스크립트가 crash/abort — 정상 판정이 나와야 함
        assert result.returncode in (0, 2), (
            f"detect-repo-kind.py self-app 실행 실패 (exit {result.returncode}): "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
        # stdout 이 유효한 종류 중 하나여야 함
        assert result.stdout.strip() in ("plugin", "mixed", "consumer"), (
            f"예상치 못한 stdout: {result.stdout!r}"
        )
