#!/usr/bin/env python3
# tests/scripts/cfp-1179/test_tier_split.py
# CFP-1179 Story-9 — Tier 분리 classify_tier / atomic_scope_for_tier TDD Python 테스트 헬퍼
#
# ADR-061 정합: 외부 .py 파일 (heredoc-python 0)
# Sandbox: CBL_SKIP_ISSUE_CREATE=1
#
# 사용법:
#   python3 test_tier_split.py <walk_plan_dir> <tc_name>
#
# TC 목록:
#   prereq_tier_constants      — TIER_1_WRAPPER / TIER_2_LANE / WRAPPER_PLUGIN / LANE_PLUGINS 상수 존재 확인 (RED 시 실패)
#   prereq_classify_tier       — classify_tier 함수 존재 확인 (RED 시 실패)
#   prereq_atomic_scope        — atomic_scope_for_tier 함수 존재 확인 (RED 시 실패)
#   tc1_wrapper_tier           — classify_tier("codeforge") == TIER_1_WRAPPER
#   tc2_lane_requirements      — classify_tier("codeforge-requirements") == TIER_2_LANE
#   tc2_lane_design            — classify_tier("codeforge-design") == TIER_2_LANE
#   tc2_lane_develop           — classify_tier("codeforge-develop") == TIER_2_LANE
#   tc2_lane_review            — classify_tier("codeforge-review") == TIER_2_LANE
#   tc2_lane_test              — classify_tier("codeforge-test") == TIER_2_LANE
#   tc2_lane_pmo               — classify_tier("codeforge-pmo") == TIER_2_LANE
#   tc3_unknown_raises         — classify_tier("unknown-plugin") raises ValueError (fail-closed)
#   tc4_atomic_scope_tier1     — atomic_scope_for_tier(TIER_1) → 3 파일 + family_atomic=True
#   tc5_atomic_scope_tier2     — atomic_scope_for_tier(TIER_2) → 2 파일 + family_atomic=False
#   tc6_discriminating_tier1   — TIER_1 atomic scope에 "CHANGELOG.md" 포함 (핵심 구분자)
#   tc6_discriminating_tier2   — TIER_2 atomic scope에 "CHANGELOG.md" 미포함 (핵심 구분자)

import os
import sys

os.environ.setdefault("CBL_SKIP_ISSUE_CREATE", "1")


def load_module(walk_plan_dir: str):
    """walk_plan.py 를 sys.path 방식으로 임포트 (Python 3.14 호환)."""
    abs_dir = os.path.abspath(walk_plan_dir)
    if abs_dir not in sys.path:
        sys.path.insert(0, abs_dir)
    import walk_plan as mod
    return mod


def _run_tc(mod, tc_name: str) -> None:
    """지정된 TC 실행 — 실패 시 SystemExit(1) + 메시지."""

    # ── PREREQ ─────────────────────────────────────────────────────────────────
    if tc_name == "prereq_tier_constants":
        for const in ("TIER_1_WRAPPER", "TIER_2_LANE", "WRAPPER_PLUGIN", "LANE_PLUGINS"):
            assert hasattr(mod, const), f"{const} 상수 미존재 — RED phase"
        print("PASS: Tier 상수 4종 존재 확인")

    elif tc_name == "prereq_classify_tier":
        assert hasattr(mod, "classify_tier"), \
            "classify_tier 함수 미존재 — RED phase"
        print("PASS: classify_tier 함수 존재 확인")

    elif tc_name == "prereq_atomic_scope":
        assert hasattr(mod, "atomic_scope_for_tier"), \
            "atomic_scope_for_tier 함수 미존재 — RED phase"
        print("PASS: atomic_scope_for_tier 함수 존재 확인")

    # ── TC-1: wrapper tier ──────────────────────────────────────────────────────
    elif tc_name == "tc1_wrapper_tier":
        result = mod.classify_tier("codeforge")
        assert result == mod.TIER_1_WRAPPER, \
            f"codeforge tier 기대 TIER_1_WRAPPER({mod.TIER_1_WRAPPER!r}), 실제 {result!r}"
        # 음성 검증 (discriminating — TIER_2_LANE 이 아님)
        assert result != mod.TIER_2_LANE, \
            "codeforge 가 TIER_2_LANE 으로 잘못 분류됨"
        print(f"PASS TC-1: classify_tier('codeforge') == TIER_1_WRAPPER({mod.TIER_1_WRAPPER!r})")

    # ── TC-2: 6 lane 각각 TIER_2_LANE ──────────────────────────────────────────
    elif tc_name == "tc2_lane_requirements":
        result = mod.classify_tier("codeforge-requirements")
        assert result == mod.TIER_2_LANE, \
            f"codeforge-requirements tier 기대 TIER_2_LANE, 실제 {result!r}"
        assert result != mod.TIER_1_WRAPPER, "codeforge-requirements 가 TIER_1_WRAPPER 로 잘못 분류됨"
        print(f"PASS TC-2: classify_tier('codeforge-requirements') == TIER_2_LANE")

    elif tc_name == "tc2_lane_design":
        result = mod.classify_tier("codeforge-design")
        assert result == mod.TIER_2_LANE, \
            f"codeforge-design tier 기대 TIER_2_LANE, 실제 {result!r}"
        assert result != mod.TIER_1_WRAPPER
        print(f"PASS TC-2: classify_tier('codeforge-design') == TIER_2_LANE")

    elif tc_name == "tc2_lane_develop":
        result = mod.classify_tier("codeforge-develop")
        assert result == mod.TIER_2_LANE, \
            f"codeforge-develop tier 기대 TIER_2_LANE, 실제 {result!r}"
        assert result != mod.TIER_1_WRAPPER
        print(f"PASS TC-2: classify_tier('codeforge-develop') == TIER_2_LANE")

    elif tc_name == "tc2_lane_review":
        result = mod.classify_tier("codeforge-review")
        assert result == mod.TIER_2_LANE, \
            f"codeforge-review tier 기대 TIER_2_LANE, 실제 {result!r}"
        assert result != mod.TIER_1_WRAPPER
        print(f"PASS TC-2: classify_tier('codeforge-review') == TIER_2_LANE")

    elif tc_name == "tc2_lane_test":
        result = mod.classify_tier("codeforge-test")
        assert result == mod.TIER_2_LANE, \
            f"codeforge-test tier 기대 TIER_2_LANE, 실제 {result!r}"
        assert result != mod.TIER_1_WRAPPER
        print(f"PASS TC-2: classify_tier('codeforge-test') == TIER_2_LANE")

    elif tc_name == "tc2_lane_pmo":
        result = mod.classify_tier("codeforge-pmo")
        assert result == mod.TIER_2_LANE, \
            f"codeforge-pmo tier 기대 TIER_2_LANE, 실제 {result!r}"
        assert result != mod.TIER_1_WRAPPER
        print(f"PASS TC-2: classify_tier('codeforge-pmo') == TIER_2_LANE")

    # ── TC-3: 알 수 없는 plugin → ValueError (fail-closed) ────────────────────
    elif tc_name == "tc3_unknown_raises":
        try:
            mod.classify_tier("unknown-plugin")
            raise AssertionError(
                "classify_tier('unknown-plugin') 이 ValueError 를 raise 하지 않음 — fail-closed 위반"
            )
        except ValueError as e:
            # 기대 경로 — fail-closed (ADR-083 정합)
            assert "unknown-plugin" in str(e), \
                f"ValueError 메시지에 plugin 이름 없음: {e}"
            print(f"PASS TC-3: classify_tier('unknown-plugin') raises ValueError (fail-closed)")
        except AssertionError:
            raise

    # ── TC-4: Tier 1 atomic scope — 3 파일 + family_atomic=True ───────────────
    elif tc_name == "tc4_atomic_scope_tier1":
        scope = mod.atomic_scope_for_tier(mod.TIER_1_WRAPPER)
        # scope 는 tuple 또는 dataclass — files 속성 or [0] 접근
        if hasattr(scope, "files"):
            files = scope.files
            family_atomic = scope.family_atomic
        else:
            files, family_atomic = scope[0], scope[1]
        assert len(files) == 3, \
            f"Tier 1 파일 수 기대 3, 실제 {len(files)}: {files}"
        for f in ("plugin.json", "CHANGELOG.md", "marketplace.json"):
            assert f in files, \
                f"Tier 1 atomic scope에 '{f}' 없음. files={files}"
        assert family_atomic is True, \
            f"Tier 1 family_atomic 기대 True, 실제 {family_atomic}"
        print(f"PASS TC-4: Tier 1 atomic scope = 3 파일 + family_atomic=True")

    # ── TC-5: Tier 2 atomic scope — 2 파일 + family_atomic=False ──────────────
    elif tc_name == "tc5_atomic_scope_tier2":
        scope = mod.atomic_scope_for_tier(mod.TIER_2_LANE)
        if hasattr(scope, "files"):
            files = scope.files
            family_atomic = scope.family_atomic
        else:
            files, family_atomic = scope[0], scope[1]
        assert len(files) == 2, \
            f"Tier 2 파일 수 기대 2, 실제 {len(files)}: {files}"
        for f in ("plugin.json", "marketplace.json"):
            assert f in files, \
                f"Tier 2 atomic scope에 '{f}' 없음. files={files}"
        assert family_atomic is False, \
            f"Tier 2 family_atomic 기대 False, 실제 {family_atomic}"
        print(f"PASS TC-5: Tier 2 atomic scope = 2 파일 + family_atomic=False")

    # ── TC-6: discriminating — CHANGELOG.md Tier 1 전용 ─────────────────────
    elif tc_name == "tc6_discriminating_tier1":
        scope = mod.atomic_scope_for_tier(mod.TIER_1_WRAPPER)
        if hasattr(scope, "files"):
            files = scope.files
        else:
            files = scope[0]
        assert "CHANGELOG.md" in files, \
            f"Tier 1 에 CHANGELOG.md 없음 — discriminating 검증 실패. files={files}"
        print("PASS TC-6a: Tier 1 atomic scope에 CHANGELOG.md 포함 확인")

    elif tc_name == "tc6_discriminating_tier2":
        scope = mod.atomic_scope_for_tier(mod.TIER_2_LANE)
        if hasattr(scope, "files"):
            files = scope.files
        else:
            files = scope[0]
        assert "CHANGELOG.md" not in files, \
            f"Tier 2 에 CHANGELOG.md 포함됨 — Tier 간 구분 실패. files={files}"
        print("PASS TC-6b: Tier 2 atomic scope에 CHANGELOG.md 미포함 확인 (discriminating)")

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
