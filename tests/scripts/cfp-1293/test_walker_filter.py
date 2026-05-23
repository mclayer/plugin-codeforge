#!/usr/bin/env python3
# tests/scripts/cfp-1293/test_walker_filter.py
# CFP-1293 Phase 2 — ADR-083 consumer-applicability filter TDD Python helper
#
# ADR-061 정합: 외부 .py 파일 (heredoc-python 0)
# CFP-1177 test_overlay_apply.py 패턴 답습
# Sandbox: CBL_SKIP_ISSUE_CREATE=1
#
# 사용법:
#   python3 test_walker_filter.py <walk_plan_dir> <tc_name>
#
# TC 목록 (Change Plan §8.5 계약):
#   prereq_filter_decision        — FilterDecision dataclass 존재 (RED phase)
#   prereq_apply_filter           — apply_consumer_applicability_filter 함수 존재 (RED phase)
#   prereq_invoke_detect          — invoke_detect_repo_kind 함수 존재 (RED phase)
#   tc1_plugin_proceed            — repo_kind=plugin → all workflow proceed (filter skip 0)
#   tc2_consumer_whitelist_match  — repo_kind=consumer + workflow IN whitelist → proceed
#   tc3_consumer_whitelist_miss   — repo_kind=consumer + workflow NOT in whitelist → skip + report
#   tc4_mixed_proceed             — repo_kind=mixed → full set proceed (wrapper self-app exemption)
#   tc5_unknown_abort             — repo_kind=unknown → abort (fail-closed, ADR-068 I-3)
#   tc6_whitelist_read_fail       — whitelist 파일 부재 시 → abort (fail-closed)
#   tc7_non_enum_abort            — 비-enum repo_kind → abort (fail-closed defensive)
#   tc8_filter_decision_immutable — FilterDecision frozen 검증
#   tc9_detect_subprocess_success — invoke_detect_repo_kind subprocess 성공 경로
#   tc10_detect_subprocess_fail   — invoke_detect_repo_kind subprocess 실패 → unknown fallback
#   tc_int_wire_consumer          — F-CR-001 caller wire: mock consumer repo + wrapper-only workflow → skip + report
#   tc_int_wire_wrapper           — F-CR-001 caller wire: mock wrapper(mixed) repo → all proceed (filter skip 0)

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("CBL_SKIP_ISSUE_CREATE", "1")


def load_module(walk_plan_dir: str):
    """walk_plan.py 를 sys.path 방식으로 임포트 (Python 3.14 호환)."""
    abs_dir = os.path.abspath(walk_plan_dir)
    if abs_dir not in sys.path:
        sys.path.insert(0, abs_dir)
    import walk_plan as mod
    return mod


def _make_whitelist(tmp_dir: str, entries: list) -> Path:
    """테스트용 임시 whitelist 파일 생성."""
    wl_path = Path(tmp_dir) / "consumer_applicable_workflows.txt"
    with open(wl_path, "w", encoding="utf-8") as f:
        f.write("# test whitelist\n")
        for entry in entries:
            f.write(entry + "\n")
    return wl_path


def _run_tc(mod, tc_name: str) -> None:
    """지정된 TC 실행 — 실패 시 SystemExit(1) + 메시지."""

    # ── PREREQ ──────────────────────────────────────────────────────────────
    if tc_name == "prereq_filter_decision":
        assert hasattr(mod, "FilterDecision"), \
            "FilterDecision dataclass 미존재 — RED phase"
        print("PASS: FilterDecision 존재 확인")

    elif tc_name == "prereq_apply_filter":
        assert hasattr(mod, "apply_consumer_applicability_filter"), \
            "apply_consumer_applicability_filter 함수 미존재 — RED phase"
        print("PASS: apply_consumer_applicability_filter 존재 확인")

    elif tc_name == "prereq_invoke_detect":
        assert hasattr(mod, "invoke_detect_repo_kind"), \
            "invoke_detect_repo_kind 함수 미존재 — RED phase"
        print("PASS: invoke_detect_repo_kind 존재 확인")

    # ── TC-1: plugin → proceed ───────────────────────────────────────────────
    elif tc_name == "tc1_plugin_proceed":
        with tempfile.TemporaryDirectory() as tmp:
            wl = _make_whitelist(tmp, ["story-init.yml", "phase-label-invariant.yml"])
            result = mod.apply_consumer_applicability_filter(
                filename="story-init.yml",
                repo_kind="plugin",
                whitelist_path=wl,
            )
        assert result.decision == "proceed", \
            f"plugin repo_kind 기대 proceed, 실제 {result.decision!r}"
        assert result.repo_kind == "plugin", \
            f"repo_kind 기대 'plugin', 실제 {result.repo_kind!r}"
        assert result.skip_filename == "", \
            f"plugin proceed 시 skip_filename 기대 '', 실제 {result.skip_filename!r}"
        # negative: plugin 은 whitelist miss 와 무관하게 proceed
        with tempfile.TemporaryDirectory() as tmp:
            wl = _make_whitelist(tmp, [])  # 빈 whitelist
            result2 = mod.apply_consumer_applicability_filter(
                filename="version-bump-atomic-check.yml",
                repo_kind="plugin",
                whitelist_path=wl,
            )
        assert result2.decision == "proceed", \
            f"plugin + empty whitelist 도 proceed 기대, 실제 {result2.decision!r}"
        print("PASS TC-1: repo_kind=plugin → proceed (whitelist 무관)")

    # ── TC-2: consumer + whitelist match → proceed ───────────────────────────
    elif tc_name == "tc2_consumer_whitelist_match":
        with tempfile.TemporaryDirectory() as tmp:
            wl = _make_whitelist(tmp, [
                "story-init.yml",
                "phase-label-invariant.yml",
                "retro-mandatory.yml",
            ])
            result = mod.apply_consumer_applicability_filter(
                filename="story-init.yml",
                repo_kind="consumer",
                whitelist_path=wl,
            )
        assert result.decision == "proceed", \
            f"consumer + whitelist match 기대 proceed, 실제 {result.decision!r}"
        assert result.repo_kind == "consumer", \
            f"repo_kind 기대 'consumer', 실제 {result.repo_kind!r}"
        assert result.skip_filename == "", \
            f"proceed 시 skip_filename 기대 '', 실제 {result.skip_filename!r}"
        print("PASS TC-2: consumer + whitelist match → proceed")

    # ── TC-3: consumer + whitelist miss → skip ───────────────────────────────
    elif tc_name == "tc3_consumer_whitelist_miss":
        with tempfile.TemporaryDirectory() as tmp:
            wl = _make_whitelist(tmp, [
                "story-init.yml",
                # version-bump-atomic-check.yml 은 포함하지 않음
            ])
            result = mod.apply_consumer_applicability_filter(
                filename="version-bump-atomic-check.yml",
                repo_kind="consumer",
                whitelist_path=wl,
            )
        assert result.decision == "skip", \
            f"consumer + whitelist miss 기대 skip, 실제 {result.decision!r}"
        assert result.repo_kind == "consumer", \
            f"repo_kind 기대 'consumer', 실제 {result.repo_kind!r}"
        assert result.skip_filename == "version-bump-atomic-check.yml", \
            f"skip_filename 기대 'version-bump-atomic-check.yml', 실제 {result.skip_filename!r}"
        # negative: "consumer-non-applicable" 사유 포함
        assert "consumer-non-applicable" in result.reason or "whitelist miss" in result.reason, \
            f"reason 에 consumer-non-applicable / whitelist miss 없음: {result.reason!r}"
        print("PASS TC-3: consumer + whitelist miss → skip + skip_filename + reason")

    # ── TC-4: mixed → proceed (wrapper self-app exemption) ───────────────────
    elif tc_name == "tc4_mixed_proceed":
        with tempfile.TemporaryDirectory() as tmp:
            wl = _make_whitelist(tmp, ["story-init.yml"])  # plugin-only workflow
            result = mod.apply_consumer_applicability_filter(
                filename="version-bump-atomic-check.yml",  # plugin-only
                repo_kind="mixed",
                whitelist_path=wl,
            )
        assert result.decision == "proceed", \
            f"mixed repo_kind 기대 proceed, 실제 {result.decision!r}"
        assert result.repo_kind == "mixed", \
            f"repo_kind 기대 'mixed', 실제 {result.repo_kind!r}"
        assert result.skip_filename == "", \
            f"mixed proceed 시 skip_filename 기대 '', 실제 {result.skip_filename!r}"
        print("PASS TC-4: mixed → proceed (wrapper self-app exemption, 0 file skip)")

    # ── TC-5: unknown → abort (fail-closed) ──────────────────────────────────
    elif tc_name == "tc5_unknown_abort":
        with tempfile.TemporaryDirectory() as tmp:
            wl = _make_whitelist(tmp, ["story-init.yml"])
            result = mod.apply_consumer_applicability_filter(
                filename="any-workflow.yml",
                repo_kind="unknown",
                whitelist_path=wl,
            )
        assert result.decision == "abort", \
            f"unknown repo_kind 기대 abort, 실제 {result.decision!r}"
        assert "unknown" in result.reason.lower() or "fail-closed" in result.reason.lower(), \
            f"reason 에 unknown / fail-closed 없음: {result.reason!r}"
        print("PASS TC-5: unknown → abort (fail-closed)")

    # ── TC-6: whitelist 파일 부재 → abort ────────────────────────────────────
    elif tc_name == "tc6_whitelist_read_fail":
        absent_wl = Path("/nonexistent/path/consumer_applicable_workflows.txt")
        result = mod.apply_consumer_applicability_filter(
            filename="story-init.yml",
            repo_kind="consumer",
            whitelist_path=absent_wl,
        )
        assert result.decision == "abort", \
            f"whitelist 부재 시 기대 abort, 실제 {result.decision!r}"
        assert "whitelist" in result.reason.lower() or "read fail" in result.reason.lower(), \
            f"reason 에 whitelist / read fail 없음: {result.reason!r}"
        print("PASS TC-6: whitelist 부재 → abort (fail-closed)")

    # ── TC-7: 비-enum repo_kind → abort ──────────────────────────────────────
    elif tc_name == "tc7_non_enum_abort":
        with tempfile.TemporaryDirectory() as tmp:
            wl = _make_whitelist(tmp, ["story-init.yml"])
            result = mod.apply_consumer_applicability_filter(
                filename="story-init.yml",
                repo_kind="invalid_kind",  # 비-enum 값
                whitelist_path=wl,
            )
        assert result.decision == "abort", \
            f"비-enum repo_kind 기대 abort, 실제 {result.decision!r}"
        print("PASS TC-7: 비-enum repo_kind → abort (fail-closed defensive)")

    # ── TC-8: FilterDecision frozen 검증 ────────────────────────────────────
    elif tc_name == "tc8_filter_decision_immutable":
        import dataclasses
        FD = mod.FilterDecision
        # dataclass fields 확인
        fields = {f.name for f in dataclasses.fields(FD)}
        for expected in ("decision", "repo_kind", "reason", "skip_filename"):
            assert expected in fields, \
                f"{expected} 필드 없음. fields={fields}"
        # frozen 확인
        instance = FD(
            decision="proceed",
            repo_kind="plugin",
            reason="test",
            skip_filename="",
        )
        try:
            instance.decision = "skip"
            raise AssertionError("frozen dataclass 가 아님 — 돌연변이 허용됨")
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            print(f"PASS TC-8: FilterDecision frozen 확인 ({type(e).__name__})")

    # ── TC-9: invoke_detect_repo_kind subprocess 성공 경로 ───────────────────
    elif tc_name == "tc9_detect_subprocess_success":
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # plugin repo 시뮬레이션: .claude-plugin/plugin.json 생성
            (tmp_path / ".claude-plugin").mkdir()
            (tmp_path / ".claude-plugin" / "plugin.json").write_text('{"name":"test"}')
            # detect-repo-kind.py 경로
            worktree_root = Path(__file__).parent.parent.parent.parent
            detect_py = worktree_root / "templates" / "scripts" / "detect-repo-kind.py"
            if not detect_py.exists():
                print(f"SKIP TC-9: detect-repo-kind.py 없음 ({detect_py})")
                return
            kind = mod.invoke_detect_repo_kind(
                consumer_root=tmp_path,
                detect_repo_kind_py=detect_py,
            )
        assert kind == "plugin", \
            f"plugin repo 기대 'plugin', 실제 {kind!r}"
        print("PASS TC-9: invoke_detect_repo_kind subprocess 성공 → 'plugin'")

    # ── TC-10: invoke_detect_repo_kind 실패 → unknown fallback ───────────────
    elif tc_name == "tc10_detect_subprocess_fail":
        kind = mod.invoke_detect_repo_kind(
            consumer_root=Path("/nonexistent/path"),
            detect_repo_kind_py=Path("/nonexistent/detect-repo-kind.py"),
        )
        assert kind == "unknown", \
            f"subprocess 실패 시 기대 'unknown', 실제 {kind!r}"
        print("PASS TC-10: subprocess 실패 → unknown (fail-closed fallback)")

    # ── TC-INT-WIRE-CONSUMER: F-CR-001 caller wire end-to-end (consumer repo, wrapper-only workflow) ──
    elif tc_name == "tc_int_wire_consumer":
        # consumer repo: .claude/_overlay/project.yaml 존재 (consumer signal)
        # wrapper-only workflow (version-bump-atomic-check.yml) = whitelist miss → skip
        # apply_changelog_entry caller wire 검증 (F-CR-001 integration end-to-end)
        with tempfile.TemporaryDirectory() as tmp:
            # consumer repo signal: .claude/_overlay/project.yaml
            overlay_dir = Path(tmp) / ".claude" / "_overlay"
            overlay_dir.mkdir(parents=True)
            (overlay_dir / "project.yaml").write_text("project_name: test-consumer\n")

            # whitelist: story-init.yml 만 포함 (consumer-applicable)
            wl = _make_whitelist(tmp, ["story-init.yml", "phase-label-invariant.yml"])

            # repo_kind: consumer (mock — skip subprocess, use direct enum)
            # 검증 대상 함수: apply_changelog_entry
            if not hasattr(mod, "apply_changelog_entry"):
                raise AssertionError("apply_changelog_entry 함수 없음 — F-CR-001 caller hook insertion 미완료")

            # wrapper-only workflow (whitelist miss) → skip
            result = mod.apply_changelog_entry(
                filename="version-bump-atomic-check.yml",  # whitelist miss
                wrapper_content="# wrapper content\n",
                consumer_content="# consumer content\n",
                repo_kind="consumer",  # mock consumer
                whitelist_path=wl,
            )
            assert result.skipped is True, \
                f"consumer + whitelist miss 기대 skipped=True, 실제 skipped={result.skipped!r}"
            assert result.applied is False, \
                f"skip 경로 applied 기대 False, 실제 applied={result.applied!r}"
            assert "consumer-non-applicable" in result.filter_reason or "whitelist miss" in result.filter_reason, \
                f"filter_reason 에 consumer-non-applicable / whitelist miss 없음: {result.filter_reason!r}"

            # consumer-applicable workflow (whitelist match) → applied
            result2 = mod.apply_changelog_entry(
                filename="story-init.yml",  # whitelist match
                wrapper_content="# wrapper content\n",
                consumer_content="# consumer content\n",
                repo_kind="consumer",
                whitelist_path=wl,
            )
            assert result2.applied is True, \
                f"consumer + whitelist match 기대 applied=True, 실제 applied={result2.applied!r}"
            assert result2.skipped is False, \
                f"proceed 경로 skipped 기대 False, 실제 skipped={result2.skipped!r}"

        print("PASS TC-INT-WIRE-CONSUMER: consumer repo → wrapper-only skip + consumer-applicable proceed")

    # ── TC-INT-WIRE-WRAPPER: F-CR-001 caller wire end-to-end (mixed/wrapper repo, all proceed) ──
    elif tc_name == "tc_int_wire_wrapper":
        # wrapper repo = mixed (plugin.json + overlay 양쪽 존재 가능) → full workflow set (0 file skip)
        # ADR-083 §결정 5 wrapper self-app exemption: mixed → proceed (filter skip 0)
        with tempfile.TemporaryDirectory() as tmp:
            # whitelist: consumer-only workflows (mixed 는 whitelist miss 여도 proceed 보장)
            wl = _make_whitelist(tmp, ["story-init.yml"])  # version-bump-atomic-check.yml 없음

            if not hasattr(mod, "apply_changelog_entry"):
                raise AssertionError("apply_changelog_entry 함수 없음 — F-CR-001 caller hook insertion 미완료")

            # wrapper-only workflow + mixed repo → proceed (0 file skip, wrapper self-app exemption)
            result = mod.apply_changelog_entry(
                filename="version-bump-atomic-check.yml",  # whitelist miss
                wrapper_content="# wrapper content\n",
                consumer_content="# consumer content\n",
                repo_kind="mixed",  # wrapper repo = mixed classification
                whitelist_path=wl,
            )
            assert result.applied is True, \
                f"mixed repo + any workflow 기대 applied=True (0 file skip), 실제 applied={result.applied!r}"
            assert result.skipped is False, \
                f"mixed repo skip 기대 False (wrapper self-app exemption), 실제 skipped={result.skipped!r}"
            assert result.filter_reason == "", \
                f"mixed proceed 시 filter_reason 기대 '', 실제 {result.filter_reason!r}"

            # plugin repo 도 동일 (plugin → proceed 보장)
            result2 = mod.apply_changelog_entry(
                filename="version-bump-atomic-check.yml",
                wrapper_content="# plugin wrapper\n",
                consumer_content="# plugin consumer\n",
                repo_kind="plugin",
                whitelist_path=wl,
            )
            assert result2.applied is True, \
                f"plugin repo 기대 applied=True, 실제 applied={result2.applied!r}"

        print("PASS TC-INT-WIRE-WRAPPER: mixed/plugin repo → all workflow proceed (filter skip 0, wrapper self-app exemption)")

    else:
        print(f"UNKNOWN TC: {tc_name}", file=sys.stderr)
        sys.exit(2)


def main():
    if len(sys.argv) < 3:
        print(f"사용법: {sys.argv[0]} <walk_plan_dir> <tc_name>", file=sys.stderr)
        sys.exit(2)
    walk_plan_dir = sys.argv[1]
    tc_name = sys.argv[2]

    try:
        mod = load_module(walk_plan_dir)
    except Exception as e:
        print(f"FAIL: walk_plan.py 로드 실패 — {e}", file=sys.stderr)
        sys.exit(1)

    try:
        _run_tc(mod, tc_name)
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
