#!/usr/bin/env bats
# tests/scripts/cfp-1179/cfp-1179-tier-split.bats
# CFP-1179 Story-9 — Tier 분리 classify_tier / atomic_scope_for_tier TDD
# QADeveloperAgent TDD (RED written against spec, GREEN against D2 implementation)
#
# TC map:
#
# PREREQ:  tier 상수 / classify_tier / atomic_scope_for_tier 존재 (RED 시 FAIL)
# TC-1:    classify_tier("codeforge") == TIER_1_WRAPPER
# TC-2:    classify_tier(6 lane 각각) == TIER_2_LANE (6 TC)
# TC-3:    classify_tier("unknown-plugin") raises ValueError (fail-closed)
# TC-4:    atomic_scope_for_tier(TIER_1) → 3 파일 + family_atomic=True
# TC-5:    atomic_scope_for_tier(TIER_2) → 2 파일 + family_atomic=False
# TC-6:    discriminating — CHANGELOG.md Tier 1 전용 (2 TC)
#
# 3-layer defense (3중 검증 — #960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture (구현 미존재 → RED, fail-closed TC-3)
#
# Python helper: tests/scripts/cfp-1179/test_tier_split.py (ADR-061 외부 .py)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# ADR ref: ADR-063 Amendment 8 §결정 19 (Tier 분리), ADR-083 (fail-closed-unknown)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
WALK_PLAN_DIR="${WORKTREE_ROOT}/scripts/lib"
TEST_HELPER="${WORKTREE_ROOT}/tests/scripts/cfp-1179/test_tier_split.py"

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
  : # filesystem 접촉 없음 (순수 함수 테스트)
}

# ──────────────────────────── prerequisite checks ────────────────────────────

@test "PREREQ: walk_plan.py 존재 확인" {
  [ -f "${WALK_PLAN_DIR}/walk_plan.py" ]
}

@test "PREREQ: test_tier_split.py 존재 확인" {
  [ -f "$TEST_HELPER" ]
}

@test "PREREQ: Tier 상수 4종 존재 확인 (RED phase: 미구현 시 FAIL)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_tier_constants"
  [ "$status" -eq 0 ]
}

@test "PREREQ: classify_tier 함수 존재 확인 (RED phase: 미구현 시 FAIL)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_classify_tier"
  [ "$status" -eq 0 ]
}

@test "PREREQ: atomic_scope_for_tier 함수 존재 확인 (RED phase: 미구현 시 FAIL)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_atomic_scope"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-1: wrapper tier ────────────────────────────────────────

@test "TC-1 (P0): classify_tier('codeforge') == TIER_1_WRAPPER" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc1_wrapper_tier"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-2: 6 lane 각각 TIER_2_LANE ─────────────────────────────

@test "TC-2a (P0): classify_tier('codeforge-requirements') == TIER_2_LANE" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_lane_requirements"
  [ "$status" -eq 0 ]
}

@test "TC-2b (P0): classify_tier('codeforge-design') == TIER_2_LANE" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_lane_design"
  [ "$status" -eq 0 ]
}

@test "TC-2c (P0): classify_tier('codeforge-develop') == TIER_2_LANE" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_lane_develop"
  [ "$status" -eq 0 ]
}

@test "TC-2d (P0): classify_tier('codeforge-review') == TIER_2_LANE" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_lane_review"
  [ "$status" -eq 0 ]
}

@test "TC-2e (P0): classify_tier('codeforge-test') == TIER_2_LANE" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_lane_test"
  [ "$status" -eq 0 ]
}

@test "TC-2f (P0): classify_tier('codeforge-pmo') == TIER_2_LANE" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_lane_pmo"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-3: unknown → ValueError (fail-closed discriminating) ───

@test "TC-3 (P0): classify_tier('unknown-plugin') raises ValueError (fail-closed)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc3_unknown_raises"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-4: Tier 1 atomic scope ──────────────────────────────────

@test "TC-4 (P0): atomic_scope_for_tier(TIER_1) → 3 파일 + family_atomic=True" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc4_atomic_scope_tier1"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-5: Tier 2 atomic scope ──────────────────────────────────

@test "TC-5 (P0): atomic_scope_for_tier(TIER_2) → 2 파일 + family_atomic=False" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc5_atomic_scope_tier2"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-6: discriminating (CHANGELOG.md Tier 1 전용) ────────────

@test "TC-6a (P0): Tier 1 atomic scope에 CHANGELOG.md 포함 (discriminating)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc6_discriminating_tier1"
  [ "$status" -eq 0 ]
}

@test "TC-6b (P0): Tier 2 atomic scope에 CHANGELOG.md 미포함 (discriminating)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc6_discriminating_tier2"
  [ "$status" -eq 0 ]
}
