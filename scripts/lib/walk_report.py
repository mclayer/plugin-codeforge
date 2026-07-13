#!/usr/bin/env python3
# scripts/lib/walk_report.py — CFP-1175 Phase 2
# walk completion 4-field 보고 생성 + TodoWrite native status visualization (ADR-061 외부 .py 의무)
#
# 책임 (change-plan §3 / ADR-093 §결정 1):
#   (a) CompletionReport 생성 — walk_result + 외부 보고 4-field schema
#       from_version / to_version / target_version_release_date / key_changes_summary
#   (b) format_completion_report_text() — 사용자 발화 verbatim 4-field 텍스트 보고
#       업그레이드 전 버전 / 업그레이드 후 버전 / 최신 버전 업데이트 일자 / 주요 변경 내용
#   (c) render_walk_todo_items() — walk step 단위 TodoWrite content render
#       native status 매핑 (pending/in_progress/completed) — content 이모지 prefix 없음
#       (ADR-038 Amendment 5 / §결정 2/3)
#   (d) extract_key_changes() — changelog entry 에서 핵심 변경 요약 추출
#   (e) walk_plan.py 연동 — WalkResult enum 공유 (공유 import)
#
# ADR refs:
#   ADR-061 python script-writing convention (외부 .py 의무)
#   ADR-093 completion report 4-field schema (walk_result + 외부 보고 4-field closed-set)
#   ADR-038 progress visualization via TodoWrite (Amendment 5 — native status 렌더, content 이모지 폐지)
#   ADR-076 declarative reconciliation upgrade (walk_result semantic 원천)
#
# SSOT:
#   docs/inter-plugin-contracts/imperative-walker-protocol-v1.md §2.A
#   docs/adr/ADR-093-completion-report-4field-schema.md (wrapper: archive/adr/) §결정 1
#   docs/adr/ADR-038-progress-visualization-todowrite.md (wrapper: archive/adr/) §결정 2/3
#   (CFP-2661 #2223/AC-21: ADR 실 위치 = archive/adr, PR #1973. docs/adr = consumer 관례. 주석 union-normalize)
#
# closed_enum open_extension: false (ADR-093 §결정 2 정합)
#   - walk_result enum: 4-value closed-set (walk_plan.WalkResult 공유)
#   - CompletionReport 4-field: frozen dataclass (consumer overlay field 추가 불가)
#   - WalkStepStatus 4-value enum: closed-set
#
# sanity check 3종 (ADR-061 의무):
#   1. diff inspection — 구현 직후 reviewer 수행
#   2. lint re-run — flake8/ruff (CI)
#   3. sample file Read — 본 파일 상단 확인
#
# Sandbox env: CBL_SKIP_ISSUE_CREATE=1

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Any

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# walk_plan.WalkResult 공유 import (연동 의무 — CFP-1175 §3)
# walk_plan.py 가 같은 lib/ 디렉토리에 있으므로 직접 import
_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LIB_DIR not in sys.path:
    sys.path.insert(0, _LIB_DIR)

from walk_plan import WalkResult  # noqa: E402 (path insert 후)


# ──────────────────────────── WalkStepStatus enum ────────────────────────────
# ADR-038 Amendment 5 (CFP-2215) — content 이모지 marker 폐지, native status 렌더
# closed-set 4-value (ADR-093 §결정 2 open_extension: false 정합)

class WalkStepStatus(Enum):
    """walk step 진행 상태 enum (4-value closed-set).

    ADR-038 Amendment 5 — Claude Code 네이티브 TodoWrite status 대응:
      PENDING       → native status "pending" (빈 체크박스 — 도구 자체 렌더)
      IN_PROGRESS   → native status "in_progress" (✱ — 도구 자체 렌더)
      COMPLETED     → native status "completed" (체크 + 취소선 — 도구 자체 렌더)
      FIX_DETECTED  → native state 부재 특수 케이스 — "in_progress" + content
                      텍스트 label "FIX detected" (ADR-038 §결정 3, 이모지 없이)

    closed-set open_extension: false.
    5번째 값 신설 = 본 모듈 amendment (ADR-093 §결정 2 정합) 로만.
    """
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FIX_DETECTED = "FIX_DETECTED"


# native status 매핑 (ADR-038 Amendment 5 — content 이모지 prefix 폐지)
# TodoWrite status field 에 전달할 값. FIX_DETECTED = in_progress + content label.
_STEP_STATUS_NATIVE = {
    WalkStepStatus.PENDING: "pending",
    WalkStepStatus.IN_PROGRESS: "in_progress",
    WalkStepStatus.COMPLETED: "completed",
    WalkStepStatus.FIX_DETECTED: "in_progress",
}


# ──────────────────────────── WalkStep dataclass ─────────────────────────────

@dataclass
class WalkStep:
    """단일 walk step (name + status).

    TodoWrite render 입력 단위.
    """
    name: str
    status: WalkStepStatus


# ──────────────────────────── CompletionReport dataclass ─────────────────────
# ADR-093 §결정 1 외부 보고 layer (사용자 4-field)
# closed-set: frozen=True (consumer overlay field 추가 불가 — ADR-093 §결정 2)

@dataclass(frozen=True)
class CompletionReport:
    """walker 완료 보고 외부 보고 layer (사용자 4-field, human-facing).

    ADR-093 §결정 1 walk completion report (외부 보고 layer):
      from_version              — 업그레이드 전 버전 (consumer installed)
      to_version                — 업그레이드 후 버전 (target, changelog latest)
      target_version_release_date — target 버전 release 일자 (ISO 8601 date)
      key_changes_summary       — 핵심 변경 요약 (changelog entry 압축)

    walk_result: WalkResult enum (walk_plan 공유)

    closed-set invariant (ADR-093 §결정 2 open_extension: false):
      frozen=True → consumer overlay 가 임의 field 추가 불가.
      AttributeError / FrozenInstanceError raise.
    """
    walk_result: WalkResult
    from_version: str
    to_version: str
    target_version_release_date: str
    key_changes_summary: str


# ──────────────────────────── extract_key_changes ────────────────────────────

def extract_key_changes(changelog_entries: list) -> str:
    """changelog entry 에서 핵심 변경 요약 추출.

    Args:
        changelog_entries: ChangelogEntry list (version + content 속성 보유)
            빈 list = 빈 문자열 반환 (idempotent — already up-to-date)

    Returns:
        key_changes_summary 문자열 (빈 entries → "")
        버전별 핵심 항목 요약 (changelog content 압축)
    """
    if not changelog_entries:
        return ""

    lines = []
    for entry in changelog_entries:
        version = getattr(entry, "version", "")
        content = getattr(entry, "content", "")
        if not content.strip():
            continue
        # 첫 의미 있는 줄 추출 (### 헤더 또는 - 항목)
        content_lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        # 최대 3줄 요약 (가독성)
        summary_lines = content_lines[:3]
        entry_summary = f"[{version}] " + " / ".join(summary_lines)
        lines.append(entry_summary)

    return "\n".join(lines)


# ──────────────────────────── build_completion_report ────────────────────────

def build_completion_report(
    walk_result: WalkResult,
    from_version: str,
    to_version: str,
    target_version_release_date: str,
    changelog_entries: list,
) -> CompletionReport:
    """walker 완료 보고 CompletionReport 생성 (외부 보고 4-field).

    ADR-093 §결정 1 walk completion report (사용자 4-field):
      from_version              — consumer 설치 버전 (업그레이드 전)
      to_version                — 업그레이드 후 버전 (changelog latest)
      target_version_release_date — target 버전 release 일자
      key_changes_summary       — changelog entry 압축 요약

    exit code → walk_result deterministic mapping 의무:
      result field 미기록 / SUCCESS hardcode = forbidden (ADR-093 §결정 1).

    Args:
        walk_result: WalkResult enum (walk_plan 공유, deterministic)
        from_version: consumer 설치 버전 (업그레이드 전)
        to_version: 업그레이드 후 버전
        target_version_release_date: target 버전 release 일자 (ISO 8601 date)
        changelog_entries: ChangelogEntry list (walk_changelog() 결과)

    Returns:
        CompletionReport (frozen — closed-set field invariant)
    """
    # key_changes_summary: from==to 이면 이미 최신 (빈 문자열)
    key_changes = extract_key_changes(changelog_entries)

    return CompletionReport(
        walk_result=walk_result,
        from_version=from_version,
        to_version=to_version,
        target_version_release_date=target_version_release_date,
        key_changes_summary=key_changes,
    )


# ──────────────────────────── format_completion_report_text ──────────────────

# walk_result 별 상태 메시지 (사용자 발화 verbatim 4-field 보고 템플릿)
_RESULT_LABEL = {
    WalkResult.SUCCESS: "업그레이드 완료",
    WalkResult.SUCCESS_WITH_DEGRADATION: "업그레이드 완료 (일부 degradation 경고)",
    WalkResult.PARTIAL_FAILURE: "업그레이드 부분 실패",
    WalkResult.FAILED: "업그레이드 실패",
}


def format_completion_report_text(report: CompletionReport) -> str:
    """CompletionReport → 사용자 발화 verbatim 4-field 완료 보고 텍스트.

    사용자 발화 verbatim (CFP-1175 §1 사용자 요구사항):
      "업그레이드 완료/종결 시에는 업그레이드 전 버전 / 업그레이드 후 버전 /
       최신 버전 업데이트 일자 / 주요 변경 내용을 반드시 알려라"

    출력 형식 (4-field):
      - 업그레이드 전 버전: {from_version}
      - 업그레이드 후 버전: {to_version}
      - 최신 버전 업데이트 일자: {target_version_release_date}
      - 주요 변경 내용: {key_changes_summary}

    walk_result 별 상태 헤더 포함:
      SUCCESS                  → "업그레이드 완료"
      SUCCESS_WITH_DEGRADATION → "업그레이드 완료 (일부 degradation 경고)"
      PARTIAL_FAILURE          → "업그레이드 부분 실패"
      FAILED                   → "업그레이드 실패"

    idempotent case (from == to):
      "이미 최신 버전" 메시지 포함.

    Args:
        report: CompletionReport (build_completion_report() 결과)

    Returns:
        사용자 보고 텍스트 (str, 비어있지 않음)
    """
    result_label = _RESULT_LABEL.get(report.walk_result, str(report.walk_result.value))
    lines = [f"=== {result_label} ==="]

    # 이미 최신 (from == to)
    if report.from_version == report.to_version:
        lines.append(f"이미 최신 버전입니다 (현재 버전: {report.from_version})")
        lines.append(f"- 최신 버전 업데이트 일자: {report.target_version_release_date}")
        return "\n".join(lines)

    # 4-field 보고 (사용자 발화 verbatim)
    lines.append(f"- 업그레이드 전 버전: {report.from_version}")
    lines.append(f"- 업그레이드 후 버전: {report.to_version}")
    lines.append(f"- 최신 버전 업데이트 일자: {report.target_version_release_date}")

    if report.key_changes_summary:
        lines.append("- 주요 변경 내용:")
        for change_line in report.key_changes_summary.splitlines():
            lines.append(f"  {change_line}")
    else:
        lines.append("- 주요 변경 내용: (상세 changelog 없음)")

    # degradation 경고 (SUCCESS_WITH_DEGRADATION)
    if report.walk_result == WalkResult.SUCCESS_WITH_DEGRADATION:
        lines.append("")
        lines.append("[경고] 일부 plugin 이 degradation 모드로 동작 중입니다.")
        lines.append("  min_prerequisite_version grace window 안 — 업그레이드 권장 (ADR-094)")

    # 실패 경고 (FAILED / PARTIAL_FAILURE)
    elif report.walk_result == WalkResult.FAILED:
        lines.append("")
        lines.append("[실패] 업그레이드가 실패하였습니다. 이전 상태로 롤백됩니다.")

    elif report.walk_result == WalkResult.PARTIAL_FAILURE:
        lines.append("")
        lines.append("[부분 실패] 일부 plugin 업그레이드가 실패하였습니다.")

    return "\n".join(lines)


# ──────────────────────────── render_walk_todo_items ─────────────────────────

def render_walk_todo_items(steps: list[WalkStep]) -> list[str]:
    """walk step 리스트 → TodoWrite content 문자열 리스트 (이모지 prefix 없음).

    ADR-038 Amendment 5 (CFP-2215) 정합 — content 이모지 4-marker 폐지:
      상태는 TodoWrite native status field 가 표현 (호출자가 _STEP_STATUS_NATIVE
      매핑으로 전달 — pending / in_progress / completed, 도구 자체 렌더).
      content = step name 텍스트만.
      FIX_DETECTED 는 native state 부재 특수 케이스 — content 텍스트 label
      "FIX detected" suffix 로 표현 (ADR-038 §결정 3, 이모지 없이).

    hierarchical render: 본 함수는 lane-level row 생성 (agent sub-row = 호출자 책임).

    Args:
        steps: WalkStep list (name + status)
            빈 list → 빈 리스트 반환

    Returns:
        문자열 리스트 — 각 원소 = "{name}" (FIX_DETECTED 는 "{name} — FIX detected")
    """
    if not steps:
        return []

    items = []
    for step in steps:
        if step.status == WalkStepStatus.FIX_DETECTED:
            items.append(f"{step.name} — FIX detected")
        else:
            items.append(step.name)
    return items


# ──────────────────────────── CLI entry point ────────────────────────────────

if __name__ == "__main__":
    # sanity check self-test (ADR-061 §결정 3 sanity check 3종 중 sample)
    print("walk_report.py sanity check:")
    print(f"  WalkStepStatus values: {[s.value for s in WalkStepStatus]}")
    print(f"  native status map: { {s.value: m for s, m in _STEP_STATUS_NATIVE.items()} }")

    # CompletionReport 생성 sanity
    report = build_completion_report(
        walk_result=WalkResult.SUCCESS,
        from_version="5.0.0",
        to_version="5.3.0",
        target_version_release_date="2026-05-21",
        changelog_entries=[],
    )
    assert report.walk_result == WalkResult.SUCCESS, f"sanity FAIL: {report.walk_result}"
    assert report.from_version == "5.0.0"
    assert report.to_version == "5.3.0"
    print("  build_completion_report() = SUCCESS ✓")

    # render_walk_todo_items sanity
    steps = [
        WalkStep(name="단계 A", status=WalkStepStatus.COMPLETED),
        WalkStep(name="단계 B", status=WalkStepStatus.IN_PROGRESS),
        WalkStep(name="단계 C", status=WalkStepStatus.PENDING),
        WalkStep(name="단계 D", status=WalkStepStatus.FIX_DETECTED),
    ]
    items = render_walk_todo_items(steps)
    # ADR-038 Amendment 5 — content 이모지 prefix 부재 + native status 매핑 검증
    assert items[0] == "단계 A", f"sanity FAIL: {items[0]}"
    assert items[1] == "단계 B", f"sanity FAIL: {items[1]}"
    assert items[2] == "단계 C", f"sanity FAIL: {items[2]}"
    assert items[3] == "단계 D — FIX detected", f"sanity FAIL: {items[3]}"
    # 폐지된 4-marker glyph (U+2B1C/U+23F3/U+2705/U+1F504 — chr() 표기 = 본 파일 자체 grep 잔존 0 유지)
    _banned_glyphs = (chr(0x2B1C), chr(0x23F3), chr(0x2705), chr(0x1F504))
    for it in items:
        assert not any(g in it for g in _banned_glyphs), \
            f"sanity FAIL emoji remnant: {it!r}"
    assert _STEP_STATUS_NATIVE[WalkStepStatus.FIX_DETECTED] == "in_progress"
    print("  render_walk_todo_items() native (no emoji) ✓")

    # format_completion_report_text sanity
    text = format_completion_report_text(report)
    assert "5.0.0" in text, f"sanity FAIL from_version: {text!r}"
    assert "5.3.0" in text, f"sanity FAIL to_version: {text!r}"
    assert "2026-05-21" in text, f"sanity FAIL release_date: {text!r}"
    print("  format_completion_report_text() ✓")

    print("sanity check PASS")
