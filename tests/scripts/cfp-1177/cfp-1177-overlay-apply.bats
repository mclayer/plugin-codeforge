#!/usr/bin/env bats
# tests/scripts/cfp-1177/cfp-1177-overlay-apply.bats
# CFP-1177 Story-8 — consumer overlay apply_overlay_file TDD
# QADeveloperAgent TDD (RED written against spec, GREEN against D1 implementation)
#
# TC map:
#
# PREREQ:  apply_overlay_file + OverlayApplyResult 존재 (RED 시 FAIL)
# TC-4:    OverlayApplyResult dataclass 5 필드 존재 + frozen 검증
# TC-1:    MARKER_VALID 3-way — marker 안 wrapper wins
# TC-1b:   MARKER_VALID 3-way — marker 밖 consumer preserve (byte-identical)
# TC-1c:   MARKER_VALID — integrity_ok=True, loss_occurred=False
# TC-2:    MARKER_NONE — wholesale wrapper mirror
# TC-2b:   MARKER_NONE — loss_occurred=True, loss_report non-empty
# TC-2c:   MARKER_NONE — integrity_ok=True (N/A path)
# TC-6:    MARKER_NONE merged_content = wrapper_content
# TC-3:    MARKER_VALID outside-preservation round-trip (discriminating)
# TC-3b:   MARKER_VALID integrity_violation_reason='' 정상 경로
# TC-8:    integrity_ok=False 경로 — consumer fallback (abort-before-touch)
# TC-5:    MARKER_VALID loss_occurred=False + integrity_ok=True 동시 만족
# TC-7:    base_content 파라미터 시그니처 호환
# TC-7b:   base_content by-design unconditional wrapper wins
#
# 3-layer defense (3중 검증 — #960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture (apply_overlay_file 미존재 → RED)
#
# Python helper: tests/scripts/cfp-1177/test_overlay_apply.py (ADR-061 외부 .py)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# ADR ref: ADR-027 Amendment 9 (paradigm-agnostic preserved layer)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
WALK_PLAN_DIR="${WORKTREE_ROOT}/scripts/lib"
TEST_HELPER="${WORKTREE_ROOT}/tests/scripts/cfp-1177/test_overlay_apply.py"

# ──────────────────────────────────────────────── sandbox setup ───────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
}

setup() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown() {
  : # no tmp dirs needed (python helper uses no FS)
}

# ──────────────────────────── prerequisite checks ────────────────────────────

@test "PREREQ: walk_plan.py 존재 확인" {
  [ -f "${WALK_PLAN_DIR}/walk_plan.py" ]
}

@test "PREREQ: test_overlay_apply.py 존재 확인" {
  [ -f "$TEST_HELPER" ]
}

@test "PREREQ: apply_overlay_file 함수 존재 확인 (RED phase: 미구현 시 FAIL)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_apply_overlay_file"
  [ "$status" -eq 0 ]
}

@test "PREREQ: OverlayApplyResult dataclass 존재 확인 (RED phase: 미구현 시 FAIL)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_overlay_result"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-4: OverlayApplyResult dataclass 5 필드 ─────────────────

@test "TC-4 (P0): OverlayApplyResult dataclass 5 필드 존재" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc4_dataclass_fields"
  [ "$status" -eq 0 ]
}

@test "TC-4b (P0): OverlayApplyResult frozen dataclass 검증 (immutable)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc4b_frozen"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-1: MARKER_VALID 3-way merge ─────────────────────────────

@test "TC-1 (P0): MARKER_VALID — marker 안 wrapper wins" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc1_marker_inner"
  [ "$status" -eq 0 ]
}

@test "TC-1b (P0): MARKER_VALID — marker 밖 consumer preserve (byte-identical)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc1b_marker_outer"
  [ "$status" -eq 0 ]
}

@test "TC-1c (P0): MARKER_VALID — integrity_ok=True, loss_occurred=False" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc1c_integrity_ok"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-2: MARKER_NONE ──────────────────────────────────────────

@test "TC-2 (P0): MARKER_NONE — wholesale wrapper mirror" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_wholesale"
  [ "$status" -eq 0 ]
}

@test "TC-2b (P0): MARKER_NONE — loss_occurred=True, loss_report non-empty" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2b_loss_report"
  [ "$status" -eq 0 ]
}

@test "TC-2c (P1): MARKER_NONE — integrity_ok=True (N/A path)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2c_integrity_na"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-6: merged == wrapper ────────────────────────────────────

@test "TC-6 (P0): MARKER_NONE merged_content 정확히 wrapper_content 동일 확인" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc6_merged_equals_wrapper"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-3: integrity round-trip ─────────────────────────────────

@test "TC-3 (P0): MARKER_VALID outside-preservation round-trip (discriminating)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc3_roundtrip"
  [ "$status" -eq 0 ]
}

@test "TC-3b (P0): MARKER_VALID integrity_violation_reason='' 정상 경로" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc3b_violation_reason"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-8: integrity violation abort-before-touch ───────────────

@test "TC-8 (P0): integrity_ok=False 경로 — consumer_content fallback (abort-before-touch)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc8_integrity_fallback"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-5: 동시 만족 ───────────────────────────────────────────

@test "TC-5 (P1): MARKER_VALID — loss_occurred=False + integrity_ok=True 동시 만족" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc5_dual_invariant"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-7: 시그니처 호환 ───────────────────────────────────────

@test "TC-7 (P1): base_content 파라미터 — 시그니처 호환 + 기본값 \"\"" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc7_signature"
  [ "$status" -eq 0 ]
}

@test "TC-7b (P1): base_content by-design — unconditional wrapper wins" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc7b_unconditional_wrapper"
  [ "$status" -eq 0 ]
}
