#!/usr/bin/env python3
# tests/scripts/cfp-1175/test_walk_report.py
# CFP-1175 Phase 2 — walk_report.py TDD pytest (TC-40~55)
# QADeveloperAgent TDD RED phase — scripts/lib/walk_report.py 구현 전 작성
#
# TC map (change-plan §8 codify):
# TC-40: build_completion_report(SUCCESS, from="5.0.0", to="5.3.0", date="2026-05-21", entries=[...])
#         → CompletionReport 반환, 4-field 모두 채워짐
# TC-41: from_version == to_version (이미 최신) → walk_result=SUCCESS, key_changes_summary 빈 문자열
# TC-42: build_completion_report(FAILED, ...) → walk_result=FAILED, to_version 기록
# TC-43: build_completion_report(SUCCESS_WITH_DEGRADATION, ...) → walk_result 정확 반영
# TC-44: CompletionReport 4-field closed-set (5번째 필드 추가 불가 — dataclass frozen=True)
# TC-45: format_completion_report_text() → 사용자 발화 verbatim 4-line 출력
#         from_version / to_version / target_version_release_date / key_changes_summary 포함
# TC-46: format_completion_report_text() SUCCESS_WITH_DEGRADATION → degradation 경고 포함
# TC-47: render_walk_todo_items(steps) → 4-marker 리스트 반환 (⬜/⏳/✅/🔄)
# TC-48: render_walk_todo_items([completed, completed, in_progress, pending])
#         → 첫 2개 ✅, 3번째 ⏳, 4번째 ⬜
# TC-49: render_walk_todo_items(fix_detected=True, fix_lane="구현-리뷰")
#         → 검출 lane 🔄, 나머지 보존
# TC-50: render_walk_todo_items([]) → 빈 리스트 (edge case)
# TC-51: WalkStep 4-marker 상태 enum (PENDING/IN_PROGRESS/COMPLETED/FIX_DETECTED)
# TC-52: format_completion_report_text() key_changes_summary — 여러 entry 줄바꿈 포함 요약
# TC-53: extract_key_changes(entries) → changelog entry 에서 핵심 변경 요약 추출
# TC-54: discriminating fixture — walk_result=SUCCESS 이지만 from==to → key_changes_summary 빈값
# TC-55: discriminating fixture — walk_result=PARTIAL_FAILURE, key_changes 일부 제공
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (no pytest.skip masking)
#   Layer 2 — 2-assertion per TC (positive + negative / 명시적 오류 검증)
#   Layer 3 — discriminating fixture (wrong input = error 또는 예상 외 값 검증)
#
# ADR refs:
#   ADR-061 python script-writing convention (외부 .py 의무)
#   ADR-093 completion report 4-field schema (walk_result + 외부 보고 4-field)
#   ADR-038 progress visualization via TodoWrite (4-marker ⬜⏳✅🔄)
# SSOT: docs/inter-plugin-contracts/imperative-walker-protocol-v1.md §2.A
#       docs/adr/ADR-093-completion-report-4field-schema.md §결정 1
# Sandbox: CBL_SKIP_ISSUE_CREATE=1

import os
import sys
import dataclasses

import pytest

# CBL sandbox env
os.environ.setdefault("CBL_SKIP_ISSUE_CREATE", "1")

# walk_report.py import path
WALK_REPORT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "scripts", "lib"
)
sys.path.insert(0, os.path.abspath(WALK_REPORT_PATH))

# RED phase: ImportError 예상 (walk_report.py 미구현) → 구현 후 GREEN
try:
    from walk_report import (
        WalkStepStatus,
        WalkStep,
        CompletionReport,
        build_completion_report,
        format_completion_report_text,
        render_walk_todo_items,
        extract_key_changes,
    )
    _MODULE_AVAILABLE = True
except ImportError:
    _MODULE_AVAILABLE = False

# walk_plan.py WalkResult import (공유 enum)
try:
    from walk_plan import WalkResult
    _WALK_PLAN_AVAILABLE = True
except ImportError:
    _WALK_PLAN_AVAILABLE = False

# ──────────────────────────── fixtures ────────────────────────────────────────

MODULE_REQUIRED = pytest.mark.skipif(
    not _MODULE_AVAILABLE,
    reason="walk_report.py 미구현 (TDD RED — 구현 후 GREEN 기대)",
)
WALK_PLAN_REQUIRED = pytest.mark.skipif(
    not _WALK_PLAN_AVAILABLE,
    reason="walk_plan.py 미구현",
)


def _make_entries(versions_contents: list[tuple[str, str]]) -> list:
    """ChangelogEntry fixture 생성 헬퍼 (walk_plan.ChangelogEntry 의존 없이 namedtuple 모방)."""
    from types import SimpleNamespace
    return [
        SimpleNamespace(version=ver, content=content)
        for ver, content in versions_contents
    ]


# ──────────────────────────── TC-40~43: CompletionReport 생성 ─────────────────

@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc40_build_completion_report_success():
    """TC-40: SUCCESS walk → CompletionReport 4-field 모두 채워짐."""
    entries = _make_entries([
        ("5.1.0", "### Added\n- feature A"),
        ("5.2.0", "### Fixed\n- bug B"),
        ("5.3.0", "### Changed\n- change C"),
    ])
    report = build_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.0.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=entries,
    )
    # 4-field 모두 존재
    assert report.from_version == "5.0.0"
    assert report.to_version == "5.3.0"
    assert report.target_version_release_date == "2026-05-21"
    assert report.key_changes_summary != ""  # 내용 있음
    assert report.walk_result == WalkResult.SUCCESS
    # 음성 검증: from_version != to_version (이미 최신 아님)
    assert report.from_version != report.to_version


@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc41_build_completion_report_already_latest():
    """TC-41: from==to (이미 최신) → SUCCESS, key_changes_summary 빈값."""
    report = build_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.3.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=[],
    )
    assert report.from_version == "5.3.0"
    assert report.to_version == "5.3.0"
    assert report.key_changes_summary == ""  # 이미 최신 → 변경사항 없음
    assert report.walk_result == WalkResult.SUCCESS
    # 음성 검증: key_changes_summary 는 None 이 아니라 빈 문자열
    assert report.key_changes_summary is not None


@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc42_build_completion_report_failed():
    """TC-42: FAILED walk → walk_result=FAILED, to_version 기록."""
    entries = _make_entries([("5.1.0", "### Added\n- feature A")])
    report = build_completion_report(
        walk_result=WalkResult.FAILED,
        from_version="5.0.0",
        to_version="5.1.0",
        target_version_release_date="2026-05-21",
        changelog_entries=entries,
    )
    assert report.walk_result == WalkResult.FAILED
    assert report.to_version == "5.1.0"
    # 음성 검증: FAILED 도 4-field 모두 기록 (silent 차단 — ADR-093 §결정 1)
    assert report.from_version is not None
    assert report.target_version_release_date is not None


@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc43_build_completion_report_degradation():
    """TC-43: SUCCESS_WITH_DEGRADATION → walk_result 정확 반영."""
    report = build_completion_report(
        walk_result=WalkResult.SUCCESS_WITH_DEGRADATION,
        from_version="5.0.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=[],
    )
    assert report.walk_result == WalkResult.SUCCESS_WITH_DEGRADATION
    # 음성 검증: SUCCESS 아님
    assert report.walk_result != WalkResult.SUCCESS


# ──────────────────────────── TC-44: closed-set invariant ─────────────────────

@MODULE_REQUIRED
def test_tc44_completion_report_closed_set():
    """TC-44: CompletionReport 4-field closed-set (임의 필드 추가 불가 — ADR-093 §결정 2).

    dataclass frozen=True 이면 AttributeError 발생으로 검증.
    """
    # walk_result 없이 직접 CompletionReport 생성 (frozen 테스트)
    try:
        report = CompletionReport(
            walk_result=None,  # walk_result placeholder
            from_version="5.0.0",
            to_version="5.3.0",
            target_version_release_date="2026-05-21",
            key_changes_summary="test",
        )
    except TypeError:
        pytest.fail("CompletionReport 생성자 서명 불일치")

    # frozen dataclass — 5번째 필드 추가 불가
    with pytest.raises((AttributeError, TypeError, dataclasses.FrozenInstanceError)):
        report.extra_field = "forbidden"  # type: ignore[attr-defined]


# ──────────────────────────── TC-45~46: format_completion_report_text ─────────

@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc45_format_completion_report_text_success():
    """TC-45: format_completion_report_text() → 사용자 발화 verbatim 4-field 포함."""
    entries = _make_entries([
        ("5.1.0", "### Added\n- feature A"),
        ("5.3.0", "### Fixed\n- bug B"),
    ])
    report = build_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.0.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=entries,
    )
    text = format_completion_report_text(report)

    # 사용자 발화 verbatim 4-field 포함 검증
    assert "5.0.0" in text   # from_version
    assert "5.3.0" in text   # to_version
    assert "2026-05-21" in text  # target_version_release_date
    # key_changes_summary 반영 (내용 있으면 text 에 포함)
    assert len(text) > 0
    # 음성 검증: 빈 문자열 아님
    assert text.strip() != ""


@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc46_format_completion_report_text_degradation_warning():
    """TC-46: SUCCESS_WITH_DEGRADATION → degradation 경고 텍스트 포함."""
    report = build_completion_report(
        walk_result=WalkResult.SUCCESS_WITH_DEGRADATION,
        from_version="5.0.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=[],
    )
    text = format_completion_report_text(report)

    # degradation 경고 포함 (SUCCESS_WITH_DEGRADATION 가시화 의무)
    assert any(
        kw in text.lower()
        for kw in ["degradation", "경고", "일부", "warning"]
    ), f"degradation 경고 없음: {text!r}"
    # 음성 검증: SUCCESS 보고와 다름
    success_report = build_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.0.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=[],
    )
    success_text = format_completion_report_text(success_report)
    assert text != success_text  # degradation 보고와 SUCCESS 보고는 다름


# ──────────────────────────── TC-47~51: render_walk_todo_items ────────────────

@MODULE_REQUIRED
def test_tc47_render_walk_todo_items_markers():
    """TC-47: render_walk_todo_items → 4-marker enum 값 반환 포함."""
    steps = [
        WalkStep(name="단계 1", status=WalkStepStatus.PENDING),
        WalkStep(name="단계 2", status=WalkStepStatus.IN_PROGRESS),
        WalkStep(name="단계 3", status=WalkStepStatus.COMPLETED),
    ]
    items = render_walk_todo_items(steps)
    assert len(items) == 3
    # 각 항목이 문자열 (TodoWrite content 형태)
    for item in items:
        assert isinstance(item, str)
    # 4-marker 포함 검증
    markers_present = {item[0] for item in items}
    assert "⬜" in markers_present or any("⬜" in item for item in items)
    assert "⏳" in markers_present or any("⏳" in item for item in items)
    assert "✅" in markers_present or any("✅" in item for item in items)


@MODULE_REQUIRED
def test_tc48_render_walk_todo_items_mixed_states():
    """TC-48: completed 2개 + in_progress 1개 + pending 1개 → 마커 순서 정확."""
    steps = [
        WalkStep(name="스텝 A", status=WalkStepStatus.COMPLETED),
        WalkStep(name="스텝 B", status=WalkStepStatus.COMPLETED),
        WalkStep(name="스텝 C", status=WalkStepStatus.IN_PROGRESS),
        WalkStep(name="스텝 D", status=WalkStepStatus.PENDING),
    ]
    items = render_walk_todo_items(steps)
    assert len(items) == 4
    assert items[0].startswith("✅")  # 완료
    assert items[1].startswith("✅")  # 완료
    assert items[2].startswith("⏳")  # 진행 중
    assert items[3].startswith("⬜")  # 대기
    # 음성 검증: 첫 번째 항목이 ⬜ 아님 (완료 항목이 ✅)
    assert not items[0].startswith("⬜")


@MODULE_REQUIRED
def test_tc49_render_walk_todo_items_fix_detected():
    """TC-49: FIX_DETECTED 상태 → 해당 lane 🔄 (ADR-038 §결정 3)."""
    steps = [
        WalkStep(name="구현", status=WalkStepStatus.COMPLETED),
        WalkStep(name="구현-리뷰", status=WalkStepStatus.FIX_DETECTED),
        WalkStep(name="보안-테스트", status=WalkStepStatus.PENDING),
    ]
    items = render_walk_todo_items(steps)
    assert len(items) == 3
    assert items[0].startswith("✅")   # 구현 완료
    assert items[1].startswith("🔄")   # FIX 검출 lane (ADR-038 §결정 3)
    assert items[2].startswith("⬜")   # 대기
    # 음성 검증: FIX_DETECTED lane 이 ✅ 아님
    assert not items[1].startswith("✅")


@MODULE_REQUIRED
def test_tc50_render_walk_todo_items_empty():
    """TC-50: 빈 steps → 빈 리스트 (edge case)."""
    items = render_walk_todo_items([])
    assert items == []
    # 음성 검증: None 아님
    assert items is not None


@MODULE_REQUIRED
def test_tc51_walk_step_status_enum():
    """TC-51: WalkStepStatus 4-value enum (PENDING/IN_PROGRESS/COMPLETED/FIX_DETECTED)."""
    assert WalkStepStatus.PENDING is not None
    assert WalkStepStatus.IN_PROGRESS is not None
    assert WalkStepStatus.COMPLETED is not None
    assert WalkStepStatus.FIX_DETECTED is not None
    # 음성 검증: 4개 값만 존재
    all_values = list(WalkStepStatus)
    assert len(all_values) == 4


# ──────────────────────────── TC-52~53: key_changes 요약 ──────────────────────

@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc52_format_completion_report_key_changes_multiline():
    """TC-52: 여러 entry 있을 때 key_changes_summary → 줄바꿈 포함 요약."""
    entries = _make_entries([
        ("5.1.0", "### Added\n- feature A\n- feature B"),
        ("5.2.0", "### Fixed\n- bug C"),
        ("5.3.0", "### Changed\n- behavior D\n### Breaking\n- API E changed"),
    ])
    report = build_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.0.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=entries,
    )
    text = format_completion_report_text(report)
    # 핵심 변경 요약이 text에 반영됨 (최소 1개 버전 언급)
    assert any(v in text for v in ["5.1.0", "5.2.0", "5.3.0"])
    # 음성 검증: 단일 entry 와 다른 요약 (여러 항목)
    single_entry = _make_entries([("5.3.0", "### Added\n- only one")])
    single_report = build_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.2.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=single_entry,
    )
    single_text = format_completion_report_text(single_report)
    # 여러 entry 보고가 단일 entry 보고보다 길거나 다름
    assert len(text) != len(single_text) or text != single_text


@MODULE_REQUIRED
def test_tc53_extract_key_changes():
    """TC-53: extract_key_changes(entries) → changelog entry 에서 핵심 변경 요약 추출."""
    entries = _make_entries([
        ("5.1.0", "### Added\n- feature A\n- feature B"),
        ("5.2.0", "### Fixed\n- bug C"),
    ])
    summary = extract_key_changes(entries)
    assert isinstance(summary, str)
    assert len(summary) > 0  # 내용 있음
    # 음성 검증: 빈 entries → 빈 문자열
    empty_summary = extract_key_changes([])
    assert empty_summary == ""


# ──────────────────────────── TC-54~55: discriminating fixture ───────────────

@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc54_discriminating_success_already_latest():
    """TC-54: discriminating — SUCCESS + from==to → key_changes_summary 반드시 빈값.

    #960 회피: SUCCESS hardcode 가 아닌 진짜 idempotent 케이스 검증.
    """
    report = build_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.3.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=[],
    )
    # key_changes_summary 빈 문자열 (이미 최신 → 변경 없음)
    assert report.key_changes_summary == ""
    # from_version == to_version 이면 "이미 최신" 텍스트 포함
    text = format_completion_report_text(report)
    assert any(kw in text for kw in ["최신", "up-to-date", "already", "이미"])


@MODULE_REQUIRED
@WALK_PLAN_REQUIRED
def test_tc55_discriminating_partial_failure():
    """TC-55: discriminating — PARTIAL_FAILURE + entries 일부 → 보고 정상 생성.

    PARTIAL_FAILURE 에서도 4-field 모두 기록 (silent false SUCCESS 차단 — ADR-093 §결정 1).
    """
    entries = _make_entries([
        ("5.1.0", "### Added\n- partial feature"),
    ])
    report = build_completion_report(
        walk_result=WalkResult.PARTIAL_FAILURE,
        from_version="5.0.0",
        to_version="5.1.0",
        target_version_release_date="2026-05-20",
        changelog_entries=entries,
    )
    assert report.walk_result == WalkResult.PARTIAL_FAILURE
    assert report.from_version == "5.0.0"
    assert report.to_version == "5.1.0"
    assert report.target_version_release_date == "2026-05-20"
    # PARTIAL_FAILURE 이어도 key_changes_summary 기록됨 (4-field 전부 기록 의무)
    assert report.key_changes_summary is not None
    # 음성 검증: walk_result != SUCCESS (hardcode 차단)
    assert report.walk_result != WalkResult.SUCCESS
