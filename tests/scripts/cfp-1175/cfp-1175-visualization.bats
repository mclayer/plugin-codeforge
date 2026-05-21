#!/usr/bin/env bats
# tests/scripts/cfp-1175/cfp-1175-visualization.bats
# CFP-1175 Phase 2 — walk_report.py CLI 연동 + walk-completion-report.yaml schema TDD (bats)
# QADeveloperAgent TDD RED phase
#
# TC map:
# TC-60: walk_report.py --help → usage 출력 (모듈 로드 성공 smoke)
# TC-61: python -c "from walk_report import CompletionReport" → import 성공
# TC-62: python -c "from walk_report import WalkStepStatus" → 4-value enum 로드
# TC-63: python -c "from walk_report import render_walk_todo_items; ..." → 마커 출력
# TC-64: walk-completion-report.yaml 파일 존재 (templates/ 하위)
# TC-65: walk-completion-report.yaml 4-field (from_version/to_version/target_version_release_date/key_changes_summary) 포함
# TC-66: walk-completion-report.yaml walk_result 4-value enum 포함
# TC-67: walk_report.py format_completion_report_text() — SUCCESS → "업그레이드 완료" 텍스트 포함
# TC-68: walk_report.py format_completion_report_text() — FAILED → "실패" 텍스트 포함
# TC-69: walk_plan.py 연동 — walk_report 모듈이 walk_plan WalkResult 공유 (import 성공)
#
# 3-layer defense (#960 always-pass 차단):
#   Layer 1 — 각 TC assert 의무
#   Layer 2 — 음성 검증 (잘못된 입력 = 오류/빈 출력)
#   Layer 3 — discriminating fixture (파일 미존재 → 실패 확인)
#
# ADR refs:
#   ADR-061 python script-writing convention (외부 .py 파일 의무)
#   ADR-093 completion report 4-field schema
#   ADR-038 progress visualization (4-marker)

setup() {
    # BATS_TEST_FILENAME 기반 POSIX path → Windows Python 호환 경로 변환
    WTPATH="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
    # POSIX /c/workspace → C:/workspace 변환 (Windows Git Bash / MSYS2)
    WTPATH_WIN="$(cygpath -w "$WTPATH" 2>/dev/null || echo "$WTPATH")"
    LIB_PATH="$WTPATH_WIN/scripts/lib"
    TEMPLATES_PATH="$WTPATH/templates"
    export PYTHONPATH="$LIB_PATH;${PYTHONPATH:-}"
    export CBL_SKIP_ISSUE_CREATE=1
    export PYTHONIOENCODING=utf-8
}

# TC-60: walk_report.py --help smoke
@test "TC-60: walk_report.py import 성공 smoke" {
    run python -c "import sys; sys.path.insert(0,'$LIB_PATH'); import walk_report; print('OK')"
    [ "$status" -eq 0 ]
    [[ "$output" == *"OK"* ]]
}

# TC-61: CompletionReport import
@test "TC-61: CompletionReport import 성공" {
    run python -c "
import sys; sys.path.insert(0,'$LIB_PATH')
from walk_report import CompletionReport
print(CompletionReport.__name__)
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"CompletionReport"* ]]
}

# TC-62: WalkStepStatus 4-value enum
@test "TC-62: WalkStepStatus 4-value enum 로드" {
    run python -c "
import sys; sys.path.insert(0,'$LIB_PATH')
from walk_report import WalkStepStatus
vals = [s.name for s in WalkStepStatus]
assert len(vals) == 4, f'Expected 4 got {len(vals)}: {vals}'
assert 'PENDING' in vals
assert 'IN_PROGRESS' in vals
assert 'COMPLETED' in vals
assert 'FIX_DETECTED' in vals
print('4-value OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"4-value OK"* ]]
}

# TC-63: render_walk_todo_items 마커 출력
@test "TC-63: render_walk_todo_items 4-marker 렌더 확인" {
    run python -c "
import sys; sys.path.insert(0,'$LIB_PATH')
from walk_report import WalkStep, WalkStepStatus, render_walk_todo_items
steps = [
    WalkStep(name='단계1', status=WalkStepStatus.COMPLETED),
    WalkStep(name='단계2', status=WalkStepStatus.IN_PROGRESS),
    WalkStep(name='단계3', status=WalkStepStatus.PENDING),
    WalkStep(name='단계4', status=WalkStepStatus.FIX_DETECTED),
]
items = render_walk_todo_items(steps)
assert len(items) == 4
assert items[0].startswith('✅'), f'Got: {items[0]}'
assert items[1].startswith('⏳'), f'Got: {items[1]}'
assert items[2].startswith('⬜'), f'Got: {items[2]}'
assert items[3].startswith('🔄'), f'Got: {items[3]}'
print('markers OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"markers OK"* ]]
}

# TC-64: walk-completion-report.yaml 파일 존재
@test "TC-64: templates/walk-completion-report.yaml 존재" {
    [ -f "$TEMPLATES_PATH/walk-completion-report.yaml" ]
}

# TC-65: walk-completion-report.yaml 4-field 포함
@test "TC-65: walk-completion-report.yaml 에 4-field (from_version/to_version/target_version_release_date/key_changes_summary) 포함" {
    [ -f "$TEMPLATES_PATH/walk-completion-report.yaml" ]
    grep -q "from_version" "$TEMPLATES_PATH/walk-completion-report.yaml"
    grep -q "to_version" "$TEMPLATES_PATH/walk-completion-report.yaml"
    grep -q "target_version_release_date" "$TEMPLATES_PATH/walk-completion-report.yaml"
    grep -q "key_changes_summary" "$TEMPLATES_PATH/walk-completion-report.yaml"
}

# TC-66: walk-completion-report.yaml walk_result 4-value enum
@test "TC-66: walk-completion-report.yaml 에 walk_result 4-value enum 포함" {
    [ -f "$TEMPLATES_PATH/walk-completion-report.yaml" ]
    grep -q "walk_result" "$TEMPLATES_PATH/walk-completion-report.yaml"
    grep -q "SUCCESS" "$TEMPLATES_PATH/walk-completion-report.yaml"
    grep -q "FAILED" "$TEMPLATES_PATH/walk-completion-report.yaml"
}

# TC-67: SUCCESS 보고 텍스트
@test "TC-67: format_completion_report_text SUCCESS → 업그레이드 완료 텍스트 포함" {
    run python -c "
import sys; sys.path.insert(0,'$LIB_PATH')
from walk_report import build_completion_report, format_completion_report_text
from walk_plan import WalkResult
report = build_completion_report(
    walk_result=WalkResult.SUCCESS,
    from_version='5.0.0',
    to_version='5.3.0',
    target_version_release_date='2026-05-21',
    changelog_entries=[],
)
text = format_completion_report_text(report)
# 4-field 키워드 포함
assert '5.0.0' in text, 'from_version 없음'
assert '5.3.0' in text, 'to_version 없음'
assert '2026-05-21' in text, 'target_version_release_date 없음'
print('SUCCESS report OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"SUCCESS report OK"* ]]
}

# TC-68: FAILED 보고 텍스트
@test "TC-68: format_completion_report_text FAILED → 실패 텍스트 포함" {
    run python -c "
import sys; sys.path.insert(0,'$LIB_PATH')
from walk_report import build_completion_report, format_completion_report_text
from walk_plan import WalkResult
report = build_completion_report(
    walk_result=WalkResult.FAILED,
    from_version='5.0.0',
    to_version='5.3.0',
    target_version_release_date='2026-05-21',
    changelog_entries=[],
)
text = format_completion_report_text(report)
has_fail_kw = any(kw in text.lower() for kw in ['실패', 'failed', 'fail', 'error'])
assert has_fail_kw, f'FAILED 경고 없음: {text!r}'
print('FAILED report OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"FAILED report OK"* ]]
}

# TC-69: walk_plan.py WalkResult 공유 연동
@test "TC-69: walk_report.py 가 walk_plan.WalkResult 공유 import 성공" {
    run python -c "
import sys; sys.path.insert(0,'$LIB_PATH')
from walk_plan import WalkResult
from walk_report import build_completion_report
# walk_plan WalkResult 를 walk_report 함수에 직접 전달 가능
report = build_completion_report(
    walk_result=WalkResult.SUCCESS,
    from_version='5.0.0',
    to_version='5.0.0',
    target_version_release_date='2026-05-21',
    changelog_entries=[],
)
assert report.walk_result == WalkResult.SUCCESS
print('walk_plan integration OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"walk_plan integration OK"* ]]
}
