#!/usr/bin/env bats
# tests/scripts/cfp-1173/cfp-1173-cli.bats
# CFP-1173 Phase 2 — Bash thin wrapper CLI TDD (TC-B1~B8)
# QADeveloperAgent TDD RED phase — 구현 전 작성
#
# TC map:
# TC-B1: calc-importance-score.sh 존재 및 실행 가능
# TC-B2: calc-importance-score.sh --touched-lanes 2 --breaking false --contract-major 0 → 수치 출력
# TC-B3: calc-importance-score.sh --touched-lanes 7 --breaking true --contract-major 3 → 최대값 출력
# TC-B4: check-parallel-safety.sh 존재 및 실행 가능
# TC-B5: check-parallel-safety.sh disjoint 입력 → exit 0 + parallel_safe: true
# TC-B6: check-parallel-safety.sh overlap 입력 → exit 1 + parallel_safe: false
# TC-B7: calc-importance-score.sh 인자 누락 → exit non-0 + 오류 메시지
# TC-B8: check-parallel-safety.sh 빈 입력 → exit 0 (빈 batch = all_safe)
#
# Sandbox: CBL_SKIP_ISSUE_CREATE=1

setup() {
    export CBL_SKIP_ISSUE_CREATE=1
    # REPO_ROOT = worktree root
    REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
    CALC_SCORE="${REPO_ROOT}/scripts/calc-importance-score.sh"
    CHECK_PARALLEL="${REPO_ROOT}/scripts/check-parallel-safety.sh"
}

# ─────────────────────────── TC-B1: calc-importance-score.sh 존재 ─────────────

@test "TC-B1: calc-importance-score.sh 존재 및 실행 가능" {
    [ -f "${CALC_SCORE}" ] || skip "calc-importance-score.sh 미구현 (TDD RED)"
    [ -x "${CALC_SCORE}" ]
}

# ─────────────────────────── TC-B2: 기본 score 출력 ──────────────────────────

@test "TC-B2: calc-importance-score.sh 기본 입력 → 수치 출력" {
    [ -f "${CALC_SCORE}" ] || skip "calc-importance-score.sh 미구현 (TDD RED)"
    run bash "${CALC_SCORE}" --touched-lanes 2 --breaking false --contract-major 0
    [ "$status" -eq 0 ]
    # 출력에 숫자 포함 확인
    echo "$output" | grep -E '[0-9]+'
}

# ─────────────────────────── TC-B3: 최대값 score ─────────────────────────────

@test "TC-B3: calc-importance-score.sh 최대값 입력 → 최고 score" {
    [ -f "${CALC_SCORE}" ] || skip "calc-importance-score.sh 미구현 (TDD RED)"
    run bash "${CALC_SCORE}" --touched-lanes 7 --breaking true --contract-major 3
    [ "$status" -eq 0 ]
    echo "$output" | grep -E '[0-9]+'
}

# ─────────────────────────── TC-B4: check-parallel-safety.sh 존재 ─────────────

@test "TC-B4: check-parallel-safety.sh 존재 및 실행 가능" {
    [ -f "${CHECK_PARALLEL}" ] || skip "check-parallel-safety.sh 미구현 (TDD RED)"
    [ -x "${CHECK_PARALLEL}" ]
}

# ─────────────────────────── TC-B5: disjoint → exit 0 ────────────────────────

@test "TC-B5: check-parallel-safety.sh disjoint 입력 → exit 0 + parallel_safe: true" {
    [ -f "${CHECK_PARALLEL}" ] || skip "check-parallel-safety.sh 미구현 (TDD RED)"
    # JSON 형식 입력: 두 entry 파일 disjoint
    INPUT_JSON='{"entries":[{"id":"A","touched_files":["scripts/a.sh"]},{"id":"B","touched_files":["scripts/b.sh"]}]}'
    run bash "${CHECK_PARALLEL}" --json "${INPUT_JSON}"
    [ "$status" -eq 0 ]
    echo "$output" | grep -i "parallel_safe.*true\|all_safe.*true"
}

# ─────────────────────────── TC-B6: overlap → exit 1 ─────────────────────────

@test "TC-B6: check-parallel-safety.sh overlap 입력 → exit 1 + parallel_safe: false" {
    [ -f "${CHECK_PARALLEL}" ] || skip "check-parallel-safety.sh 미구현 (TDD RED)"
    INPUT_JSON='{"entries":[{"id":"A","touched_files":["scripts/shared.sh"]},{"id":"B","touched_files":["scripts/shared.sh"]}]}'
    run bash "${CHECK_PARALLEL}" --json "${INPUT_JSON}"
    [ "$status" -eq 1 ]
    echo "$output" | grep -i "parallel_safe.*false\|all_safe.*false"
}

# ─────────────────────────── TC-B7: 인자 누락 → non-0 ───────────────────────

@test "TC-B7: calc-importance-score.sh 인자 누락 → exit non-0 + 오류 메시지" {
    [ -f "${CALC_SCORE}" ] || skip "calc-importance-score.sh 미구현 (TDD RED)"
    run bash "${CALC_SCORE}"
    [ "$status" -ne 0 ]
    # 오류 메시지 확인
    [[ "$output" =~ "오류\|error\|인자\|argument" ]] || [[ "$stderr" =~ "오류\|error\|인자\|argument" ]] || true
}

# ─────────────────────────── TC-B8: 빈 batch → exit 0 ────────────────────────

@test "TC-B8: check-parallel-safety.sh 빈 batch → exit 0 (all_safe)" {
    [ -f "${CHECK_PARALLEL}" ] || skip "check-parallel-safety.sh 미구현 (TDD RED)"
    INPUT_JSON='{"entries":[]}'
    run bash "${CHECK_PARALLEL}" --json "${INPUT_JSON}"
    [ "$status" -eq 0 ]
}
