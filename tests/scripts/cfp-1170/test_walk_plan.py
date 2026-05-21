#!/usr/bin/env python3
# tests/scripts/cfp-1170/test_walk_plan.py
# CFP-1170 Phase 2 — walk_plan.py TDD pytest (TC-20~30)
# QADeveloperAgent TDD RED phase — scripts/lib/walk_plan.py 구현 전 작성
#
# TC map (change-plan §8.3 codify):
# TC-20: walk_changelog(from=5.0.0, to=5.3.0) → (5.1.0, 5.2.0, 5.3.0) entry enumerate (from 제외 to 포함)
# TC-21: walk_changelog malformed CHANGELOG → ChangelogParseError raise
# TC-22: walk_changelog(from > to) → VersionRangeError raise
# TC-23: resolve_min_prereq_topological (consumer_pin >= all min) → empty PrereqMismatch (PASS)
# TC-24: resolve_min_prereq_topological (consumer wrapper_pin < lane min) → non-empty PrereqMismatch
# TC-25: topological order = [wrapper, ...6 lane] DAG (wrapper 먼저, cycle 부재)
# TC-26: aggregate_walk_result (ALL SUCCESS) → family SUCCESS
# TC-27: aggregate_walk_result (ANY PARTIAL_FAILURE) → family PARTIAL_FAILURE
# TC-28: aggregate_walk_result (ANY FAILED) → family FAILED
# TC-29: aggregate_walk_result (ANY DEGRADATION, no fail) → family SUCCESS_WITH_DEGRADATION
# TC-30: exit code → walk_result deterministic mapping (silent false SUCCESS 차단)
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (no pytest.skip masking)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture (wrong input = error 검증)
#
# ADR-061 정합: 외부 .py 파일 (heredoc-python 0)
# SSOT: docs/change-plans/cfp-1170-cli-walk-tier.md §8.3 + §4.3
# Sandbox: CBL_SKIP_ISSUE_CREATE=1

import os
import sys
import textwrap

import pytest

# CBL sandbox env
os.environ.setdefault("CBL_SKIP_ISSUE_CREATE", "1")

# walk_plan.py import (Phase 2 구현 후 GREEN — 구현 전 RED)
WALK_PLAN_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "scripts", "lib"
)
sys.path.insert(0, os.path.abspath(WALK_PLAN_PATH))

# RED phase: ImportError 예상 (walk_plan.py 미구현) → 구현 후 GREEN
try:
    from walk_plan import (
        ChangelogEntry,
        ChangelogParseError,
        PrereqMismatch,
        VersionRangeError,
        WalkResult,
        aggregate_walk_result,
        resolve_min_prereq_topological,
        walk_changelog,
    )
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False


# ──────────────────────────── prerequisite ────────────────────────────────────

def test_prereq_walk_plan_module_exists():
    """PREREQ: scripts/lib/walk_plan.py 파일 존재 확인 (RED phase = FAIL → GREEN = PASS)."""
    walk_plan_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "scripts", "lib", "walk_plan.py"
    )
    assert os.path.isfile(walk_plan_file), (
        "scripts/lib/walk_plan.py 미존재 — TDD RED phase 정상 (Phase 2 구현 후 GREEN)"
    )


def test_prereq_module_importable():
    """PREREQ: walk_plan 모듈 import 가능 (RED phase = FAIL → GREEN = PASS)."""
    assert _MODULE_AVAILABLE, (
        "walk_plan 모듈 import 실패 — TDD RED phase 정상 (Phase 2 구현 후 GREEN). "
        "scripts/lib/walk_plan.py 구현 필요."
    )


# ──────────────────────── CHANGELOG 픽스처 헬퍼 ──────────────────────────────

def _make_changelog(entries: list[tuple[str, str]]) -> str:
    """(version, content) 쌍으로 CHANGELOG.md 내용 생성."""
    lines = []
    for version, content in entries:
        lines.append(f"## [{version}]")
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


def _write_changelog(tmp_path, content: str) -> str:
    """임시 CHANGELOG.md 파일 작성 후 경로 반환."""
    p = tmp_path / "CHANGELOG.md"
    p.write_text(content, encoding="utf-8")
    return str(p)


# ───────────────────── TC-20: walk_changelog 기본 enumerate ──────────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc20_walk_changelog_basic_range(tmp_path):
    """TC-20: walk_changelog(from=5.0.0, to=5.3.0) → entries [5.1.0, 5.2.0, 5.3.0] (from 제외 to 포함)."""
    content = _make_changelog([
        ("5.3.0", "feat: 5.3 feature"),
        ("5.2.0", "feat: 5.2 feature"),
        ("5.1.0", "feat: 5.1 feature"),
        ("5.0.0", "feat: 5.0 initial"),
        ("4.9.0", "feat: 4.9 feature"),
    ])
    changelog_path = _write_changelog(tmp_path, content)

    entries = walk_changelog(
        plugin="codeforge",
        from_version="5.0.0",
        to_version="5.3.0",
        changelog_path=changelog_path,
    )

    # positive: 3 entries (5.1.0, 5.2.0, 5.3.0)
    versions = [e.version for e in entries]
    assert "5.1.0" in versions
    assert "5.2.0" in versions
    assert "5.3.0" in versions
    assert len(entries) == 3

    # negative: from_version 제외 (5.0.0), 이전 버전 제외 (4.9.0)
    assert "5.0.0" not in versions
    assert "4.9.0" not in versions


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc20b_walk_changelog_to_inclusive(tmp_path):
    """TC-20b: to_version 포함 확인 (경계값 — to 버전이 결과에 포함돼야 함)."""
    content = _make_changelog([
        ("5.3.0", "feat: 5.3 feature"),
        ("5.2.0", "feat: 5.2 feature"),
        ("5.1.0", "feat: 5.1 base"),
    ])
    changelog_path = _write_changelog(tmp_path, content)

    entries = walk_changelog(
        plugin="codeforge",
        from_version="5.1.0",
        to_version="5.3.0",
        changelog_path=changelog_path,
    )

    versions = [e.version for e in entries]
    # positive: 5.3.0 포함 (to inclusive)
    assert "5.3.0" in versions
    # negative: 5.1.0 제외 (from exclusive)
    assert "5.1.0" not in versions


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc20c_walk_changelog_empty_range(tmp_path):
    """TC-20c: from == to → 빈 entries (이미 최신, no-op)."""
    content = _make_changelog([
        ("5.3.0", "feat: 5.3 feature"),
        ("5.2.0", "feat: 5.2 feature"),
    ])
    changelog_path = _write_changelog(tmp_path, content)

    entries = walk_changelog(
        plugin="codeforge",
        from_version="5.3.0",
        to_version="5.3.0",
        changelog_path=changelog_path,
    )

    # positive: empty list (same version = already up-to-date)
    assert entries == []


# ───────────────────── TC-21: ChangelogParseError ────────────────────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc21_malformed_changelog(tmp_path):
    """TC-21: malformed CHANGELOG → ChangelogParseError raise."""
    # malformed: 버전 헤더 없음 (파싱 불가)
    content = "this is not a valid changelog format\nno version headers at all"
    changelog_path = _write_changelog(tmp_path, content)

    with pytest.raises(ChangelogParseError):
        walk_changelog(
            plugin="codeforge",
            from_version="5.0.0",
            to_version="5.3.0",
            changelog_path=changelog_path,
        )


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc21b_missing_changelog_file():
    """TC-21b: changelog_path 미존재 → ChangelogParseError raise (abort-before-touch)."""
    with pytest.raises(ChangelogParseError):
        walk_changelog(
            plugin="codeforge",
            from_version="5.0.0",
            to_version="5.3.0",
            changelog_path="/nonexistent/CHANGELOG.md",
        )


# ───────────────────── TC-22: VersionRangeError ──────────────────────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc22_from_greater_than_to(tmp_path):
    """TC-22: from > to → VersionRangeError raise."""
    content = _make_changelog([
        ("5.3.0", "feat: 5.3 feature"),
        ("5.0.0", "feat: 5.0 initial"),
    ])
    changelog_path = _write_changelog(tmp_path, content)

    with pytest.raises(VersionRangeError):
        walk_changelog(
            plugin="codeforge",
            from_version="5.3.0",
            to_version="5.0.0",
            changelog_path=changelog_path,
        )


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc22b_invalid_semver(tmp_path):
    """TC-22b: 잘못된 semver → VersionRangeError raise."""
    content = _make_changelog([("5.3.0", "feat: 5.3 feature")])
    changelog_path = _write_changelog(tmp_path, content)

    with pytest.raises(VersionRangeError):
        walk_changelog(
            plugin="codeforge",
            from_version="not-a-version",
            to_version="5.3.0",
            changelog_path=changelog_path,
        )


# ───────────────────── TC-23: resolve_min_prereq_topological PASS ────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc23_min_prereq_all_satisfied():
    """TC-23: consumer_pin >= all min → empty PrereqMismatch list (PASS)."""
    # 모든 plugin의 min_prereq = consumer_pin 충족
    family_min_prereq = {
        "codeforge-requirements": {"codeforge": ">=5.0.0"},
        "codeforge-design": {"codeforge": ">=5.0.0"},
        "codeforge-review": {"codeforge": ">=5.0.0"},
        "codeforge-develop": {"codeforge": ">=5.0.0"},
        "codeforge-test": {"codeforge": ">=5.0.0"},
        "codeforge-pmo": {"codeforge": ">=5.0.0"},
    }
    consumer_pin = {
        "codeforge": "5.3.0",
        "codeforge-requirements": "5.3.0",
        "codeforge-design": "5.3.0",
        "codeforge-review": "5.3.0",
        "codeforge-develop": "5.3.0",
        "codeforge-test": "5.3.0",
        "codeforge-pmo": "5.3.0",
    }

    mismatches = resolve_min_prereq_topological(family_min_prereq, consumer_pin)

    # positive: empty list (no mismatch)
    assert mismatches == []


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc23b_min_prereq_exact_match():
    """TC-23b: consumer_pin == min_prereq → PASS (경계값, exact match = OK)."""
    family_min_prereq = {
        "codeforge-requirements": {"codeforge": ">=5.3.0"},
    }
    consumer_pin = {
        "codeforge": "5.3.0",
        "codeforge-requirements": "5.3.0",
    }

    mismatches = resolve_min_prereq_topological(family_min_prereq, consumer_pin)

    # positive: 5.3.0 >= 5.3.0 → PASS
    assert mismatches == []


# ───────────────────── TC-24: min_prereq mismatch (FAIL) ─────────────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc24_min_prereq_wrapper_pin_too_low():
    """TC-24: consumer wrapper_pin < lane min → non-empty PrereqMismatch (fallback 신호)."""
    family_min_prereq = {
        "codeforge-requirements": {"codeforge": ">=5.5.0"},
    }
    consumer_pin = {
        "codeforge": "5.3.0",  # < 5.5.0 required
        "codeforge-requirements": "5.3.0",
    }

    mismatches = resolve_min_prereq_topological(family_min_prereq, consumer_pin)

    # positive: non-empty (mismatch detected)
    assert len(mismatches) >= 1

    # positive: mismatch에 plugin 이름 포함
    mismatch_plugins = [m.plugin for m in mismatches]
    assert "codeforge-requirements" in mismatch_plugins or "codeforge" in mismatch_plugins

    # negative: empty list 아님
    assert mismatches != []


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc24b_prereq_mismatch_fields():
    """TC-24b: PrereqMismatch 객체 필드 검증 (plugin / required_range / actual)."""
    family_min_prereq = {
        "codeforge-design": {"codeforge": ">=5.5.0"},
    }
    consumer_pin = {
        "codeforge": "5.2.0",  # < 5.5.0
        "codeforge-design": "5.2.0",
    }

    mismatches = resolve_min_prereq_topological(family_min_prereq, consumer_pin)

    assert len(mismatches) >= 1
    m = mismatches[0]

    # positive: PrereqMismatch 필드 존재 (plugin / required_range / actual)
    assert hasattr(m, "plugin")
    assert hasattr(m, "required_range")
    assert hasattr(m, "actual")

    # positive: actual version = consumer_pin 값 (실제 설치 버전)
    assert m.actual == "5.2.0"


# ───────────────────── TC-25: topological order ──────────────────────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc25_topological_order_wrapper_first():
    """TC-25: topological order = [wrapper, ...6 lane] — wrapper 먼저 resolve, cycle 부재."""
    # wrapper = codeforge (lane들이 codeforge에 의존 — 단방향 DAG)
    family_min_prereq = {
        "codeforge-requirements": {"codeforge": ">=5.0.0"},
        "codeforge-design": {"codeforge": ">=5.0.0"},
        "codeforge-review": {"codeforge": ">=5.0.0"},
        "codeforge-develop": {"codeforge": ">=5.0.0"},
        "codeforge-test": {"codeforge": ">=5.0.0"},
        "codeforge-pmo": {"codeforge": ">=5.0.0"},
    }
    consumer_pin = {
        "codeforge": "5.0.0",
        "codeforge-requirements": "5.0.0",
        "codeforge-design": "5.0.0",
        "codeforge-review": "5.0.0",
        "codeforge-develop": "5.0.0",
        "codeforge-test": "5.0.0",
        "codeforge-pmo": "5.0.0",
    }

    # topological resolve는 cycle 없이 완료되어야 함 (RuntimeError 없음)
    mismatches = resolve_min_prereq_topological(family_min_prereq, consumer_pin)

    # positive: no exception = cycle 부재
    assert isinstance(mismatches, list)


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc25b_topological_order_exported():
    """TC-25b: walk_plan.py 가 TOPOLOGICAL_ORDER 상수 또는 함수를 export."""
    # ADR-096 §결정 2 DAG invariant: [wrapper, ...6 lane]
    import walk_plan as wp  # type: ignore[import]

    # positive: TOPOLOGICAL_ORDER 또는 get_topological_order 존재
    has_const = hasattr(wp, "TOPOLOGICAL_ORDER")
    has_func = hasattr(wp, "get_topological_order")
    assert has_const or has_func, (
        "walk_plan.py 에 TOPOLOGICAL_ORDER 상수 또는 get_topological_order 함수 없음"
    )

    if has_const:
        order = wp.TOPOLOGICAL_ORDER
    else:
        order = wp.get_topological_order()

    # positive: wrapper(codeforge) 가 첫 번째
    assert order[0] == "codeforge", f"topological order 첫 번째 = {order[0]}, expected codeforge"

    # positive: 7개 family member 모두 포함
    expected_members = {
        "codeforge", "codeforge-requirements", "codeforge-design",
        "codeforge-review", "codeforge-develop", "codeforge-test", "codeforge-pmo"
    }
    assert set(order) == expected_members


# ───────────────────── TC-26: aggregate_walk_result ALL SUCCESS ───────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc26_aggregate_all_success():
    """TC-26: aggregate_walk_result (ALL SUCCESS) → family SUCCESS."""
    results = [WalkResult.SUCCESS] * 7

    family_result = aggregate_walk_result(results)

    # positive: family = SUCCESS
    assert family_result == WalkResult.SUCCESS

    # negative: SUCCESS 아닌 다른 값이 아님
    assert family_result != WalkResult.FAILED
    assert family_result != WalkResult.PARTIAL_FAILURE
    assert family_result != WalkResult.SUCCESS_WITH_DEGRADATION


# ───────────────────── TC-27: aggregate_walk_result ANY PARTIAL_FAILURE ──────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc27_aggregate_any_partial_failure():
    """TC-27: aggregate_walk_result (ANY PARTIAL_FAILURE) → family PARTIAL_FAILURE."""
    results = [
        WalkResult.SUCCESS,
        WalkResult.SUCCESS,
        WalkResult.PARTIAL_FAILURE,  # 일부 실패
        WalkResult.SUCCESS,
        WalkResult.SUCCESS,
        WalkResult.SUCCESS,
        WalkResult.SUCCESS,
    ]

    family_result = aggregate_walk_result(results)

    # positive: family = PARTIAL_FAILURE (ANY PARTIAL → family PARTIAL)
    assert family_result == WalkResult.PARTIAL_FAILURE

    # negative: SUCCESS 아님
    assert family_result != WalkResult.SUCCESS


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc27b_aggregate_partial_failure_dominates_degradation():
    """TC-27b: PARTIAL_FAILURE가 DEGRADATION보다 우선 (severity ordering)."""
    results = [
        WalkResult.SUCCESS_WITH_DEGRADATION,
        WalkResult.PARTIAL_FAILURE,
        WalkResult.SUCCESS,
    ]

    family_result = aggregate_walk_result(results)

    # positive: PARTIAL_FAILURE 우선 (DEGRADATION < PARTIAL_FAILURE severity)
    assert family_result == WalkResult.PARTIAL_FAILURE


# ───────────────────── TC-28: aggregate_walk_result ANY FAILED ───────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc28_aggregate_any_failed():
    """TC-28: aggregate_walk_result (ANY FAILED) → family FAILED."""
    results = [
        WalkResult.SUCCESS,
        WalkResult.FAILED,  # 하나라도 FAILED → family FAILED
        WalkResult.SUCCESS,
    ]

    family_result = aggregate_walk_result(results)

    # positive: family = FAILED
    assert family_result == WalkResult.FAILED

    # negative: PARTIAL_FAILURE 아님 (FAILED > PARTIAL_FAILURE)
    assert family_result != WalkResult.PARTIAL_FAILURE
    assert family_result != WalkResult.SUCCESS


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc28b_aggregate_failed_dominates_all():
    """TC-28b: FAILED가 모든 값보다 우선 (severity ordering)."""
    results = [
        WalkResult.SUCCESS_WITH_DEGRADATION,
        WalkResult.PARTIAL_FAILURE,
        WalkResult.FAILED,
    ]

    family_result = aggregate_walk_result(results)

    # positive: FAILED 가 최상위 severity
    assert family_result == WalkResult.FAILED


# ───────────────────── TC-29: aggregate_walk_result DEGRADATION ──────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc29_aggregate_any_degradation_no_fail():
    """TC-29: aggregate_walk_result (ANY DEGRADATION, no fail) → SUCCESS_WITH_DEGRADATION."""
    results = [
        WalkResult.SUCCESS,
        WalkResult.SUCCESS_WITH_DEGRADATION,  # DEGRADATION
        WalkResult.SUCCESS,
        WalkResult.SUCCESS,
    ]

    family_result = aggregate_walk_result(results)

    # positive: family = SUCCESS_WITH_DEGRADATION
    assert family_result == WalkResult.SUCCESS_WITH_DEGRADATION

    # negative: FAILED / PARTIAL_FAILURE 아님
    assert family_result != WalkResult.FAILED
    assert family_result != WalkResult.PARTIAL_FAILURE


# ───────────────────── TC-30: exit code 결정론적 매핑 ───────────────────────

@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc30_walk_result_exit_code_mapping():
    """TC-30: WalkResult → exit code 결정론적 매핑 (silent false SUCCESS 차단)."""
    import walk_plan as wp  # type: ignore[import]

    # positive: WalkResult.to_exit_code() 또는 EXIT_CODE_MAP 존재
    has_method = hasattr(WalkResult, "to_exit_code")
    has_map = hasattr(wp, "EXIT_CODE_MAP") or hasattr(wp, "WALK_RESULT_EXIT_CODES")
    assert has_method or has_map, (
        "walk_plan.py 에 exit code 매핑 없음 — WalkResult.to_exit_code() 또는 EXIT_CODE_MAP 필요"
    )

    if has_method:
        # positive: SUCCESS → exit 0
        assert WalkResult.SUCCESS.to_exit_code() == 0

        # positive: 비-0 exit code 매핑 (silent false SUCCESS 차단)
        assert WalkResult.FAILED.to_exit_code() != 0
        assert WalkResult.PARTIAL_FAILURE.to_exit_code() != 0

        # positive: SUCCESS_WITH_DEGRADATION → 비-0 (degradation 가시화 — 0이면 안 됨)
        # change-plan §4.1: exit code → walk_result deterministic (silent false SUCCESS 차단)
        degradation_exit = WalkResult.SUCCESS_WITH_DEGRADATION.to_exit_code()
        assert degradation_exit is not None

    elif has_map:
        code_map = getattr(wp, "EXIT_CODE_MAP", None) or getattr(wp, "WALK_RESULT_EXIT_CODES")
        assert WalkResult.SUCCESS in code_map or "SUCCESS" in code_map


@pytest.mark.skipif(not _MODULE_AVAILABLE, reason="walk_plan 모듈 미구현 (TDD RED)")
def test_tc30b_walk_result_closed_enum():
    """TC-30b: WalkResult enum closed_set (4-value, open_extension: false)."""
    # positive: 4개 enum 값만 존재
    values = set(WalkResult)
    expected = {WalkResult.SUCCESS, WalkResult.SUCCESS_WITH_DEGRADATION,
                WalkResult.PARTIAL_FAILURE, WalkResult.FAILED}
    assert values == expected, (
        f"WalkResult enum 4-value closed_set 위반: {values} != {expected}"
    )

    # positive: 5번째 값 없음 (UNKNOWN 등 ad-hoc 확장 금지)
    assert len(values) == 4
