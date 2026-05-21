#!/usr/bin/env bats
# tests/scripts/cfp-1199/cfp-1199-9plugin.bats
# CFP-1199 F1 — 9-plugin family reconciliation TDD
# QADeveloperAgent TDD (RED written against spec, GREEN after D1/D2 in walk_plan.py)
#
# TC map:
#
# PREREQ:  walk_plan.py import + 필수 심볼 존재
# TC-1:    len(get_topological_order()) == 9 (7 → 9 reconciliation)
# TC-2:    get_topological_order()[0] == "codeforge" (wrapper 먼저 — DAG invariant)
# TC-3:    "codeforge-deploy" 포함 (ADR-087 신설 lane)
# TC-4:    "codeforge-deploy-review" 포함 (ADR-088 신설 lane)
# TC-5:    deploy 두 lane 이 pmo 이후 위치 (보수 lifecycle 순서)
#          + deploy-review 이 deploy 이후 (배포 전 리뷰 불가)
# TC-6:    classify_tier("codeforge-deploy") == TIER_2_LANE (auto-derive 확인)
# TC-7:    classify_tier("codeforge-deploy-review") == TIER_2_LANE
# TC-8:    TOPOLOGICAL_ORDER 9개 항목 정확히 일치 (중복/누락 0)
# TC-9:    resolve_min_prereq_topological — 9-plugin manifest 포함 acyclic resolve
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture (구현 미적용 → RED, 정확한 기대값 명시)
#
# Python helper: tests/scripts/cfp-1199/test_9plugin.py (ADR-061 외부 .py)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# ADR ref: ADR-087 (deploy lane), ADR-088 (deploy-review lane),
#          ADR-096 §결정 2 (DAG invariant), ADR-063 §결정 19 (Tier 분리)
# SSOT: scripts/lib/walk_plan.py TOPOLOGICAL_ORDER

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
WALK_PLAN_DIR="${WORKTREE_ROOT}/scripts/lib"
TEST_HELPER="${WORKTREE_ROOT}/tests/scripts/cfp-1199/test_9plugin.py"

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

@test "PREREQ: test_9plugin.py 존재 확인" {
  [ -f "$TEST_HELPER" ]
}

@test "PREREQ: walk_plan 모듈 import + 필수 심볼 존재 확인" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "prereq_module_importable"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-1: 9-plugin family 총 수 ───────────────────────────────

@test "TC-1 (P0): len(get_topological_order()) == 9 (7→9 reconciliation, CFP-1199 D1)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc1_topological_count_9"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-2: wrapper 가 첫 번째 ──────────────────────────────────

@test "TC-2 (P0): get_topological_order()[0] == 'codeforge' (DAG invariant 보존)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc2_wrapper_first"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-3: codeforge-deploy 포함 ───────────────────────────────

@test "TC-3 (P0): 'codeforge-deploy' TOPOLOGICAL_ORDER 포함 (ADR-087 신설 lane)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc3_deploy_present"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-4: codeforge-deploy-review 포함 ────────────────────────

@test "TC-4 (P0): 'codeforge-deploy-review' TOPOLOGICAL_ORDER 포함 (ADR-088 신설 lane)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc4_deploy_review_present"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-5: deploy 두 lane 이 pmo 이후 위치 ─────────────────────

@test "TC-5 (P0): deploy 두 lane 이 pmo 이후 + deploy-review 가 deploy 이후 (lifecycle 순서)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc5_deploy_after_pmo"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-6: codeforge-deploy → TIER_2_LANE (auto-derive) ────────

@test "TC-6 (P0): classify_tier('codeforge-deploy') == TIER_2_LANE (TOPOLOGICAL_ORDER auto-derive)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc6_deploy_tier2"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-7: codeforge-deploy-review → TIER_2_LANE ───────────────

@test "TC-7 (P0): classify_tier('codeforge-deploy-review') == TIER_2_LANE" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc7_deploy_review_tier2"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-8: 9개 항목 정확히 일치 ────────────────────────────────

@test "TC-8 (P0): TOPOLOGICAL_ORDER 9개 항목 정확히 일치 (중복/누락 0)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc8_topological_exact_9"
  [ "$status" -eq 0 ]
}

# ───────────────── TC-9: 9-plugin manifest acyclic resolve ───────────────────

@test "TC-9 (P0): 9-plugin manifest deploy lane min_prereq resolve 정상 (acyclic)" {
  run python3 "$TEST_HELPER" "$WALK_PLAN_DIR" "tc9_resolve_deploy_prereq"
  [ "$status" -eq 0 ]
}
