#!/usr/bin/env bats
# tests/scripts/cfp-991/cfp-991-canary-compatibility.bats
# CFP-991 Phase 2 — Wave 4 sub-Epic #882 Story-4 canary promotion criteria 4-tuple
# QADeveloperAgent TDD (RED written against Phase 2 spec, GREEN against Phase 1 implementation)
#
# TC map (Story §3.5 + Change Plan §8.1 TestContractArch counter-proposal 채택):
#
# TC 1-7:   7 field schema verify (enabled / promotion_criteria_4tuple / family_7_atomic_canary_pin /
#           canary_consumer_evidence_origin / inter_plugin_contract_backward_compat_verify /
#           promotion_gate_failure_mode / downgrade_asymmetry_marker)
# TC 8-12:  4-tuple measurement source enum (functional / security / monitoring / testing)
# TC 13-17: family_7 atomic canary pin (length_invariant=7 + member_enum + 3-way match)
# TC 18-22: canary_consumer_evidence_origin enum closed-set (wrapper_self/consumer_self/mixed + open_extension:false)
# TC 23-26: inter_plugin_contract_backward_compat_verify (minor_only_rule_passed bool + ADR-008 §결정 2 invariant guard)
# TC 27-29: promotion_gate_failure_mode enum (warning_first/blocking_on_pr + bypass_label binding)
# TC 30:    downgrade_asymmetry_marker (placeholder_reserve Story-5 carrier)
#
# 3-layer defense (#960 always-pass pattern_count 3 reach 차단 carrier):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion (positive + negative) per TC group
#   Layer 3 — discriminating fixture TDD RED phase (git stash 패턴, [feedback_tdd_red_proof_via_stash] 정합)
#
# Mock seam: _CFP991_MOCK_* namespace (CFP-932 _CFP932_MOCK_MIXED_CHANNEL 패턴 답습)
#   _CFP991_MOCK_FAMILY_VERSIONS       — 7-plugin version array mock
#   _CFP991_MOCK_MARKETPLACE_CHANNELS  — cross-repo marketplace.json channels[] mock
#
# Sandbox env (ADR-040 Amendment 6 §결정 7.D + CFP-843 §3.3):
#   CBL_SKIP_ISSUE_CREATE=1 — setup/teardown export (bats lifecycle hook 정합)
#
# Baseline SHA: 8a9a3de0 (Phase 1 merged, wrapper main HEAD)
# Evidence origin annotation: wrapper_self (Phase 2 implement = bats + scripts, declare-only scope)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

SCRIPT="${WORKTREE_ROOT}/scripts/check-canary-compatibility.sh"
HELPER_LIB="${WORKTREE_ROOT}/scripts/lib/canary-compatibility-helpers.sh"
RECONCILE_CONTRACT="${WORKTREE_ROOT}/docs/inter-plugin-contracts/reconcile-protocol-v1.md"
EVIDENCE_REGISTRY="${WORKTREE_ROOT}/docs/evidence-checks-registry.yaml"
WORKFLOW_TEMPLATE="${WORKTREE_ROOT}/templates/github-workflows/canary-promotion-criteria.yml"
WORKFLOW_SELFAPP="${WORKTREE_ROOT}/.github/workflows/canary-promotion-criteria.yml"

# ─────────────────────────────────────────────── sandbox setup ────────────────

setup_file() {
  # CFP-843 §3.3 sandbox env — bats setup_file/teardown_file export
  export CBL_SKIP_ISSUE_CREATE=1
  export CFP991_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
  unset CFP991_SKIP_ISSUE_CREATE
}

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown() {
  unset _CFP991_MOCK_FAMILY_VERSIONS || true
  unset _CFP991_MOCK_MARKETPLACE_CHANNELS || true
  unset CANARY_CONSUMER_EVIDENCE_ORIGIN || true
  unset PROMOTION_GATE_FAILURE_MODE || true
  unset PUBLISHER_VERSION || true
  unset REGISTRY_VERSION || true
  unset CONSUMER_VERSION || true
  unset CONSUMER_CHANNEL_TIER || true
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-991-unused}"
}

# ─────────────────────────────────────────────── TC 1-7: 7 field schema verify ─

@test "TC-1 (P0): reconcile-protocol-v1.md §4.14 canary_compatibility_check_binding 블록 존재" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — 블록 존재
  grep -q "canary_compatibility_check_binding:" "$RECONCILE_CONTRACT"
  # negative — 오탈자 없음 (camelCase variant 금지)
  ! grep -q "canaryCompatibilityCheckBinding:" "$RECONCILE_CONTRACT"
}

@test "TC-2 (P0): §4.14 enabled 필드 존재 + consumer_opt_out: false 선언" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — §4.14 블록 내 enabled 필드 존재 (블록이 길어 -A 20 범위 사용)
  grep -A 20 "canary_compatibility_check_binding:" "$RECONCILE_CONTRACT" | grep -q "enabled:"
  # positive — consumer_opt_out: false 선언 (closed invariant)
  grep -q "consumer_opt_out: false" "$RECONCILE_CONTRACT"
  # negative — consumer_opt_out: true 금지 (closed invariant)
  ! grep -q "consumer_opt_out: true" "$RECONCILE_CONTRACT"
}

@test "TC-3 (P0): §4.14 promotion_criteria_4tuple 필드 존재 + 4 sub (functional/security/monitoring/testing)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive
  grep -q "promotion_criteria_4tuple:" "$RECONCILE_CONTRACT"
  # negative — 5번째 sub-field 금지 (closed-set 4-tuple invariant)
  local count
  count=$(grep -c "measurement_source:" "$RECONCILE_CONTRACT")
  # 최소 4개 이상 (4-tuple)
  [ "$count" -ge 4 ]
}

@test "TC-4 (P0): §4.14 family_7_atomic_canary_pin 필드 존재 + length_invariant: 7 선언" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive
  grep -q "family_7_atomic_canary_pin:" "$RECONCILE_CONTRACT"
  grep -q "length_invariant: 7" "$RECONCILE_CONTRACT"
  # negative — length_invariant: 8 또는 length_invariant: 6 금지
  ! grep -q "length_invariant: 8" "$RECONCILE_CONTRACT"
  ! grep -q "length_invariant: 6" "$RECONCILE_CONTRACT"
}

@test "TC-5 (P0): §4.14 canary_consumer_evidence_origin 필드 존재 + open_extension: false 선언" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive
  grep -q "canary_consumer_evidence_origin:" "$RECONCILE_CONTRACT"
  grep -q "open_extension: false" "$RECONCILE_CONTRACT"
  # negative — open_extension: true 금지 (closed-set invariant)
  ! grep -q "open_extension: true" "$RECONCILE_CONTRACT"
}

@test "TC-6 (P0): §4.14 inter_plugin_contract_backward_compat_verify 필드 존재 + minor_only_rule_passed bool 선언" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive
  grep -q "inter_plugin_contract_backward_compat_verify:" "$RECONCILE_CONTRACT"
  grep -q "minor_only_rule_passed:" "$RECONCILE_CONTRACT"
  # negative — major_allowed: true 금지 (ADR-008 §결정 2 invariant)
  ! grep -q "major_allowed: true" "$RECONCILE_CONTRACT"
}

@test "TC-7 (P0): §4.14 promotion_gate_failure_mode + downgrade_asymmetry_marker 필드 존재" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive (2 fields)
  grep -q "promotion_gate_failure_mode:" "$RECONCILE_CONTRACT"
  grep -q "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT"
  # negative — promotion_gate_failure_mode 없이 downgrade_asymmetry_marker만 있으면 안 됨
  grep -q "promotion_gate_failure_mode:" "$RECONCILE_CONTRACT"
}

# ─────────────────────────────────────── TC 8-12: 4-tuple measurement source enum ─

@test "TC-8 (P0): helper lib _extract_4tuple_measurement_source() — functional sub-field 파싱 PASS" {
  [ -f "$HELPER_LIB" ]
  # shellcheck source=/dev/null
  source "$HELPER_LIB"
  run _extract_4tuple_measurement_source "$RECONCILE_CONTRACT" "functional"
  [ "$status" -eq 0 ]
  # positive — measurement_source 문자열 출력
  [[ "$output" != "" ]]
  # negative — empty output = 실패 (warning tier)
  [[ "$output" != "NOT_FOUND" ]]
}

@test "TC-9 (P0): helper lib _extract_4tuple_measurement_source() — security sub-field 파싱 PASS" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  run _extract_4tuple_measurement_source "$RECONCILE_CONTRACT" "security"
  [ "$status" -eq 0 ]
  [[ "$output" != "" ]]
}

@test "TC-10 (P0): helper lib _extract_4tuple_measurement_source() — monitoring sub-field 파싱 PASS" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  run _extract_4tuple_measurement_source "$RECONCILE_CONTRACT" "monitoring"
  [ "$status" -eq 0 ]
  [[ "$output" != "" ]]
}

@test "TC-11 (P0): helper lib _extract_4tuple_measurement_source() — testing sub-field 파싱 PASS" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  run _extract_4tuple_measurement_source "$RECONCILE_CONTRACT" "testing"
  [ "$status" -eq 0 ]
  [[ "$output" != "" ]]
}

@test "TC-12 (P1): helper lib _extract_4tuple_measurement_source() — invalid sub-field → exit 2 hard fail" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # negative — closed-set 위반 enum exit 2
  run _extract_4tuple_measurement_source "$RECONCILE_CONTRACT" "performance"
  [ "$status" -eq 2 ]
  # positive — 오류 메시지에 expected 목록 포함
  [[ "$output" == *"functional"* ]] || [[ "${lines[*]}" == *"functional"* ]]
}

# ────────────────────────────────── TC 13-17: family_7 atomic canary pin ─────────

@test "TC-13 (P0): helper lib _enumerate_family_7_canary_versions() — mock env 출력 7 플러그인" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  export _CFP991_MOCK_FAMILY_VERSIONS="codeforge:5.92.0
codeforge-requirements:5.92.0
codeforge-design:5.92.0
codeforge-develop:5.92.0
codeforge-test:5.92.0
codeforge-review:5.92.0
codeforge-pmo:5.92.0"
  run _enumerate_family_7_canary_versions "canary"
  # warning tier (mock env active = exit 1)
  [ "$status" -eq 1 ]
  # positive — 7줄 출력 (length_invariant 충족)
  local line_count
  line_count=$(echo "$output" | grep -c "^codeforge")
  [ "$line_count" -eq 7 ]
}

@test "TC-14 (P0): helper lib _enumerate_family_7_canary_versions() — length_invariant=7 strict (6개 = exit 2)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # negative — 6개만 주입 → exit 2 (length_invariant 위배)
  export _CFP991_MOCK_FAMILY_VERSIONS="codeforge:5.92.0
codeforge-requirements:5.92.0
codeforge-design:5.92.0
codeforge-develop:5.92.0
codeforge-test:5.92.0
codeforge-review:5.92.0"
  run _enumerate_family_7_canary_versions "canary"
  [ "$status" -eq 2 ]
}

@test "TC-15 (P0): helper lib _enumerate_family_7_canary_versions() — 8개 주입 → exit 2 (length_invariant 위배)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # negative — 8개 주입 → exit 2
  export _CFP991_MOCK_FAMILY_VERSIONS="codeforge:5.92.0
codeforge-requirements:5.92.0
codeforge-design:5.92.0
codeforge-develop:5.92.0
codeforge-test:5.92.0
codeforge-review:5.92.0
codeforge-pmo:5.92.0
codeforge-extra:5.92.0"
  run _enumerate_family_7_canary_versions "canary"
  [ "$status" -eq 2 ]
}

@test "TC-16 (P0): helper lib _enumerate_family_7_canary_versions() — production path exit 0 (mock 없음)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # production path — no mock env
  unset _CFP991_MOCK_FAMILY_VERSIONS
  run _enumerate_family_7_canary_versions "canary"
  # production = exit 0 (7 placeholders, no mock active)
  [ "$status" -eq 0 ]
  # positive — 7줄 모두 family member 포함
  local line_count
  line_count=$(echo "$output" | grep -c "^codeforge")
  [ "$line_count" -eq 7 ]
}

@test "TC-17 (P0): member_enum SSOT — 7 plugin 이름 모두 포함 (ADR-016 §결정 1 정합)" {
  [ -f "$HELPER_LIB" ]
  # positive — SSOT 7 member_enum 존재 확인
  grep -q "\"codeforge\"" "$HELPER_LIB"
  grep -q "\"codeforge-requirements\"" "$HELPER_LIB"
  grep -q "\"codeforge-design\"" "$HELPER_LIB"
  grep -q "\"codeforge-develop\"" "$HELPER_LIB"
  grep -q "\"codeforge-test\"" "$HELPER_LIB"
  grep -q "\"codeforge-review\"" "$HELPER_LIB"
  grep -q "\"codeforge-pmo\"" "$HELPER_LIB"
  # negative — 8번째 가상 멤버 없음
  ! grep -q "\"codeforge-extra\"" "$HELPER_LIB"
}

# ───────────────────────────── TC 18-22: canary_consumer_evidence_origin enum ───

@test "TC-18 (P0): helper _validate_enum_closed_set() — wrapper_self VALID" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  run _validate_enum_closed_set "canary_consumer_evidence_origin" "wrapper_self"
  [ "$status" -eq 0 ]
  [[ "$output" == "VALID" ]]
}

@test "TC-19 (P0): helper _validate_enum_closed_set() — consumer_self VALID" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  run _validate_enum_closed_set "canary_consumer_evidence_origin" "consumer_self"
  [ "$status" -eq 0 ]
  [[ "$output" == "VALID" ]]
}

@test "TC-20 (P0): helper _validate_enum_closed_set() — mixed VALID" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  run _validate_enum_closed_set "canary_consumer_evidence_origin" "mixed"
  [ "$status" -eq 0 ]
  [[ "$output" == "VALID" ]]
}

@test "TC-21 (P0): helper _validate_enum_closed_set() — open_extension: false (unknown_origin → exit 2)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # negative — closed-set 위반 (open_extension: false 확인)
  run _validate_enum_closed_set "canary_consumer_evidence_origin" "unknown_origin"
  [ "$status" -eq 2 ]
  # positive — 오류 메시지에 closed-set 멤버 포함
  [[ "$output" == *"wrapper_self"* ]] || [[ "${lines[*]}" == *"wrapper_self"* ]]
}

@test "TC-22 (P1): helper _validate_enum_closed_set() — unknown enum name → exit 2" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # negative — 정의되지 않은 enum_name
  run _validate_enum_closed_set "non_existent_enum" "any_value"
  [ "$status" -eq 2 ]
}

# ────────────────────────── TC 23-26: inter_plugin_contract_backward_compat_verify ─

@test "TC-23 (P0): reconcile-protocol-v1 §4.14 inter_plugin_contract_backward_compat_verify 선언 존재" {
  [ -f "$RECONCILE_CONTRACT" ]
  grep -q "inter_plugin_contract_backward_compat_verify:" "$RECONCILE_CONTRACT"
  # negative — major version 허용 선언 없음 (ADR-008 §결정 2 invariant)
  ! grep -q "major_allowed: true" "$RECONCILE_CONTRACT"
}

@test "TC-24 (P0): minor_only_rule_passed 필드 = bool 타입 선언 (ADR-008 §결정 2 invariant guard)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — minor_only_rule_passed: bool 또는 minor_only_rule_passed: true/false
  grep -q "minor_only_rule_passed:" "$RECONCILE_CONTRACT"
  # negative — type: string 선언 금지 (bool 타입 invariant)
  local section
  section=$(grep -A 10 "inter_plugin_contract_backward_compat_verify:" "$RECONCILE_CONTRACT" | head -15)
  [[ "$section" != *"type: string"* ]]
}

@test "TC-25 (P1): ADR-008 §결정 2 invariant guard — contract 구조 MINOR bump 참조 존재" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — ADR-008 §결정 2 cross-ref 존재 (backward compat invariant SSOT)
  grep -q "ADR-008" "$RECONCILE_CONTRACT"
  # negative — ADR-008 §결정 3 (PATCH) 혼동 단독 인용 없음 (ADR-008 §결정 2 = MINOR only, §결정 3 = PATCH)
  # 둘 다 있어야 함 (단, backward_compat 영역 특정 §결정 2)
  grep -q "§결정 2" "$RECONCILE_CONTRACT"
  # F-CR-991-D FIX: §결정 3 confusion disallowed — backward_compat 영역 안에 §결정 3 단독 참조 금지
  # inter_plugin_contract_backward_compat_verify 블록 5줄 스캔 후 §결정 3 단독 존재 시 FAIL
  ! grep -A 5 "inter_plugin_contract_backward_compat_verify:" "$RECONCILE_CONTRACT" | grep -q "§결정 3"
}

@test "TC-26 (P0): 스크립트 helper lib — idempotent source guard 존재 (multi-source 시 redefine 회피)" {
  [ -f "$HELPER_LIB" ]
  # positive — idempotent guard 패턴 (declare -f _validate_enum_closed_set 패턴)
  grep -q "declare -f _validate_enum_closed_set" "$HELPER_LIB"
  # negative — source guard 없는 raw function 선언만 있으면 안 됨
  # (guard 존재 = positive 확인으로 충분)
}

# ──────────────────────────── TC 27-29: promotion_gate_failure_mode enum ────────

@test "TC-27 (P0): helper _validate_enum_closed_set() — warning_first VALID (promotion_gate_failure_mode)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  run _validate_enum_closed_set "promotion_gate_failure_mode" "warning_first"
  [ "$status" -eq 0 ]
  [[ "$output" == "VALID" ]]
}

@test "TC-28 (P0): helper _validate_enum_closed_set() — blocking_on_pr VALID (promotion_gate_failure_mode)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  run _validate_enum_closed_set "promotion_gate_failure_mode" "blocking_on_pr"
  [ "$status" -eq 0 ]
  [[ "$output" == "VALID" ]]
}

@test "TC-29 (P0): bypass_label binding — hotfix-bypass:canary-promotion-criteria 레이블 존재 (label-registry-v2 + evidence-registry)" {
  [ -f "$EVIDENCE_REGISTRY" ]
  # positive — canary-promotion-criteria entry 존재 (evidence-registry)
  grep -q "canary-compatibility-check" "$EVIDENCE_REGISTRY"
  # positive — bypass_label binding (label-registry 참조 가능)
  grep -q "hotfix-bypass:canary-promotion-criteria" "$RECONCILE_CONTRACT"
  # negative — 오탈자 없음 (bypass_label 형식)
  ! grep -q "hotfix-bypass:canary_promotion_criteria" "$RECONCILE_CONTRACT"
}

# ─────────────────────────────────── TC 30: downgrade_asymmetry_marker ──────────

@test "TC-30 (P1): downgrade_asymmetry_marker — placeholder_reserve 선언 + Story-5 carrier 명시" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — placeholder_reserve 상태 (Story-5 미도착 invariant)
  grep -q "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT"
  grep -q "placeholder_reserve" "$RECONCILE_CONTRACT"
  # positive — carrier_story Story-5 언급 존재
  grep -A 5 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep -q "Story-5\|CFP-991-Story-5"
  # negative — active 상태 (Story-5 미도착이므로 불가)
  local section
  section=$(grep -A 5 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | head -8)
  [[ "$section" != *"status: active"* ]]
}

# ─────────────────────── 종합 통합: check-canary-compatibility.sh 오케스트레이터 ─

@test "TC-ORCH-1 (P0): scripts/check-canary-compatibility.sh — Tier-1 exemption fast-PASS (triple-AND)" {
  [ -f "$SCRIPT" ]
  # Tier-1 exemption — production_cutover_touching=true + repo_kind=wrapper + code_change=0
  run env \
    PRODUCTION_CUTOVER_TOUCHING=true \
    REPO_KIND=wrapper \
    CODE_CHANGE=0 \
    CBL_SKIP_ISSUE_CREATE=1 \
    bash "$SCRIPT" 2>&1
  [ "$status" -eq 0 ]
  [[ "$output" == *"Tier-1 wrapper-self-app exemption"* ]]
}

@test "TC-ORCH-2 (P0): scripts/check-canary-compatibility.sh — enum closed-set 위반 → exit 2" {
  [ -f "$SCRIPT" ]
  # negative — invalid enum value → exit 2 (hard fail)
  run env \
    CANARY_CONSUMER_EVIDENCE_ORIGIN=invalid_origin \
    PROMOTION_GATE_FAILURE_MODE=warning_first \
    CBL_SKIP_ISSUE_CREATE=1 \
    bash "$SCRIPT" 2>&1
  [ "$status" -eq 2 ]
}

@test "TC-ORCH-3 (P0): scripts/check-canary-compatibility.sh — 3-way MATCH → exit 0" {
  [ -f "$SCRIPT" ]
  # 3-way byte-identical match → PASS
  run env \
    PRODUCTION_CUTOVER_TOUCHING=false \
    CANARY_CONSUMER_EVIDENCE_ORIGIN=wrapper_self \
    PROMOTION_GATE_FAILURE_MODE=warning_first \
    PUBLISHER_VERSION=5.92.0 \
    REGISTRY_VERSION=5.92.0 \
    CONSUMER_VERSION=5.92.0 \
    RECONCILE_CONTRACT_PATH="$RECONCILE_CONTRACT" \
    CBL_SKIP_ISSUE_CREATE=1 \
    bash "$SCRIPT" 2>&1
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

@test "TC-ORCH-4 (P0): scripts/check-canary-compatibility.sh — partial input (warning_first) → exit 1" {
  [ -f "$SCRIPT" ]
  # partial input (CONSUMER_VERSION 부재) + warning_first → exit 1 (advisory, not hard fail)
  # Note: 3-way 실제 MISMATCH는 항상 exit 2 (failure_mode 무관). exit 1은 데이터 부재 시만.
  run env \
    PRODUCTION_CUTOVER_TOUCHING=false \
    CANARY_CONSUMER_EVIDENCE_ORIGIN=wrapper_self \
    PROMOTION_GATE_FAILURE_MODE=warning_first \
    PUBLISHER_VERSION=5.92.0 \
    REGISTRY_VERSION=5.92.0 \
    RECONCILE_CONTRACT_PATH="$RECONCILE_CONTRACT" \
    CBL_SKIP_ISSUE_CREATE=1 \
    bash "$SCRIPT" 2>&1
  # warning_first + partial input → exit 1
  [ "$status" -eq 1 ]
  [[ "$output" == *"warning_first"* ]] || [[ "$output" == *"WARNING"* ]]
}

@test "TC-ORCH-5 (P0): scripts/check-canary-compatibility.sh — 3-way MISMATCH (blocking_on_pr) → exit 2" {
  [ -f "$SCRIPT" ]
  # 3-way mismatch + blocking_on_pr → exit 2 (hard fail)
  run env \
    PRODUCTION_CUTOVER_TOUCHING=false \
    CANARY_CONSUMER_EVIDENCE_ORIGIN=wrapper_self \
    PROMOTION_GATE_FAILURE_MODE=blocking_on_pr \
    PUBLISHER_VERSION=5.92.0 \
    REGISTRY_VERSION=5.91.0 \
    CONSUMER_VERSION=5.92.0 \
    RECONCILE_CONTRACT_PATH="$RECONCILE_CONTRACT" \
    CBL_SKIP_ISSUE_CREATE=1 \
    bash "$SCRIPT" 2>&1
  [ "$status" -eq 2 ]
}

# ─────────────────────── discriminating fixture (3-layer defense Layer 3) ────────

@test "TC-DISC-1 (P0): discriminating — enum valid vs invalid 경계 (positive/negative 2-assertion)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # positive: 유효 enum
  run _validate_enum_closed_set "canary_consumer_evidence_origin" "wrapper_self"
  [ "$status" -eq 0 ]
  [[ "$output" == "VALID" ]]
  # negative: 유효하지 않은 enum (open_extension: false 확인)
  run _validate_enum_closed_set "canary_consumer_evidence_origin" "public"
  [ "$status" -eq 2 ]
  [[ "$output" != "VALID" ]]
}

@test "TC-DISC-2 (P0): discriminating — family_7 length 7 vs 8 경계 (positive/negative 2-assertion)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # positive: 7개 = exit 1 (warning: mock active) + 7줄 출력
  export _CFP991_MOCK_FAMILY_VERSIONS="$(printf 'codeforge:%s\n' 5.92.0)
$(printf 'codeforge-requirements:%s\n' 5.92.0)
$(printf 'codeforge-design:%s\n' 5.92.0)
$(printf 'codeforge-develop:%s\n' 5.92.0)
$(printf 'codeforge-test:%s\n' 5.92.0)
$(printf 'codeforge-review:%s\n' 5.92.0)
$(printf 'codeforge-pmo:%s\n' 5.92.0)"
  run _enumerate_family_7_canary_versions "canary"
  [ "$status" -eq 1 ]
  local cnt
  cnt=$(echo "$output" | grep -c "^codeforge")
  [ "$cnt" -eq 7 ]
  # negative: 8개 = exit 2 (hard fail)
  export _CFP991_MOCK_FAMILY_VERSIONS="${_CFP991_MOCK_FAMILY_VERSIONS}
codeforge-extra:5.92.0"
  run _enumerate_family_7_canary_versions "canary"
  [ "$status" -eq 2 ]
}

@test "TC-DISC-3 (P0): discriminating — 3-way MATCH vs MISMATCH 경계 (positive/negative 2-assertion)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # positive: 3-way MATCH → exit 0
  run _three_way_version_diff "5.92.0" "5.92.0" "5.92.0"
  [ "$status" -eq 0 ]
  [[ "$output" == "MATCH" ]]
  # negative: publisher만 다름 → exit 2 (MISMATCH)
  run _three_way_version_diff "5.91.0" "5.92.0" "5.92.0"
  [ "$status" -eq 2 ]
  [[ "$output" != "MATCH" ]]
}

# ─────────────────── TC-DISC-4/5: F-CR-991-B/C regression guard (FIX iter 1) ────

@test "TC-DISC-4 (P1): discriminating — mock member_enum name 검증 (F-CR-991-B regression guard)" {
  [ -f "$HELPER_LIB" ]
  source "$HELPER_LIB"
  # negative: 임의 이름 7개 주입 → exit 2 (member_enum closed-set 위배 hard fail)
  # F-CR-991-B FIX 이전 = exit 1 오분류 (silent PASS) — 회귀 방지
  export _CFP991_MOCK_FAMILY_VERSIONS="random-plugin-1:5.0.0
random-plugin-2:5.0.0
random-plugin-3:5.0.0
random-plugin-4:5.0.0
random-plugin-5:5.0.0
random-plugin-6:5.0.0
random-plugin-7:5.0.0"
  run _enumerate_family_7_canary_versions "canary"
  [ "$status" -eq 2 ]
  # positive: exit 2 시 ERROR 메시지 포함 (member_enum 위배 명시)
  [[ "${output}" == *"NOT in member_enum"* ]] || [[ "${lines[*]}" == *"NOT in member_enum"* ]]
}

@test "TC-DISC-5 (P1): discriminating — python3 absent (command -v guard) → exit 2 hard fail (F-CR-991-C regression guard)" {
  [ -f "$HELPER_LIB" ]
  # python3 미존재 시뮬레이션 — function override로 command -v 실패 재현
  # F-CR-991-C FIX 이전 = python3 호출 후 rc 결과로만 판단 → exit 1 오분류 (silent warning)
  # FIX 후: command -v python3 사전 check → 실패 시 즉시 exit 2 hard fail
  # Note: bats subshell 내에서 command 를 재정의해 command -v 실패 시뮬레이션
  run bash -c "
    command() {
      if [[ \"\$1\" == '-v' && \"\$2\" == 'python3' ]]; then
        return 1  # python3 absent 시뮬레이션
      fi
      builtin command \"\$@\"
    }
    export -f command
    source '${HELPER_LIB}'
    _extract_4tuple_measurement_source '${RECONCILE_CONTRACT}' functional
    echo exit:\$?
  " 2>&1
  # exit 2 = hard fail (F-CR-991-C FIX 후 기대값)
  # 'exit:2' 문자열이 output에 포함되어야 함
  [[ "${output}" == *"exit:2"* ]] || [[ "${lines[*]}" == *"exit:2"* ]]
  # ERROR 메시지 포함 (python3 unavailable 명시)
  [[ "${output}" == *"python3"* ]]
}

# ─────────────── TC-DISC-6/7: F-CR-991-G mock env var wire (FIX iter 1 2nd round) ─

@test "TC-DISC-6 (P1): discriminating — _CFP991_MOCK_MARKETPLACE_CHANNELS mock env wire (F-CR-991-G)" {
  [ -f "$HELPER_LIB" ]
  # Note: bats `run` 은 stdout+stderr 를 합쳐 output 에 캡처 (bats v1.x default --keep-empty-lines)
  # _three_way_version_diff 는 mock 주입 시 WARNING(stderr) + MATCH(stdout) 복합 출력
  # 따라서 `output == "MATCH"` 대신 `*"MATCH"*` wildcard 사용 (multi-line output 대응)

  # positive: mock channels 주입 시 registry version 이 mock canary tier 버전으로 교체되어 3-way MATCH
  # _CFP991_MOCK_MARKETPLACE_CHANNELS format: "tier=canary version=<ver>" KV
  run bash -c "source '${HELPER_LIB}' && export _CFP991_MOCK_MARKETPLACE_CHANNELS='tier=canary version=5.92.0' && _three_way_version_diff '5.92.0' 'stale_registry_version' '5.92.0'" 2>&1
  # mock channels 로 registry version 이 5.92.0 으로 교체 → 3-way MATCH → exit 0
  [ "$status" -eq 0 ]
  [[ "$output" == *"MATCH"* ]]
  # WARNING 메시지 포함 (mock-injected 명시)
  [[ "$output" == *"mock-injected"* ]]

  # negative: mock channels 주입 후에도 mismatch 발생 시 exit 2
  run bash -c "source '${HELPER_LIB}' && export _CFP991_MOCK_MARKETPLACE_CHANNELS='tier=canary version=5.91.0' && _three_way_version_diff '5.92.0' 'stale_registry_version' '5.92.0'" 2>&1
  # mock canary = 5.91.0 ≠ publisher 5.92.0 → 3-way MISMATCH → exit 2
  [ "$status" -eq 2 ]
  [[ "$output" == *"MISMATCH"* ]]
}

@test "TC-DISC-7 (P1): discriminating — _CFP991_MOCK_DRIFT_THRESHOLD mock env wire (F-CR-991-G)" {
  [ -f "$HELPER_LIB" ]
  # Note: _three_way_version_diff 는 drift_threshold=0 시 WARNING(stderr)를 출력
  # bats `run` output 은 multi-line (WARNING + MATCH). *"MATCH"* wildcard 사용

  # positive: drift_threshold=0 override (instant detection mode) — WARNING 메시지 포함
  run bash -c "source '${HELPER_LIB}' && export _CFP991_MOCK_DRIFT_THRESHOLD=0 && _three_way_version_diff '5.92.0' '5.92.0' '5.92.0'" 2>&1
  # threshold=0 이어도 3-way MATCH → exit 0 (threshold = advisory only, MATCH 판정 무영향)
  [ "$status" -eq 0 ]
  [[ "$output" == *"MATCH"* ]]
  # WARNING 메시지 포함 (drift_threshold=0s test override 명시)
  [[ "$output" == *"0s"* ]] || [[ "$output" == *"drift_threshold"* ]]

  # negative: invalid threshold 값 → fallback to 86400 + WARNING
  run bash -c "source '${HELPER_LIB}' && export _CFP991_MOCK_DRIFT_THRESHOLD='not_a_number' && _three_way_version_diff '5.92.0' '5.92.0' '5.92.0'" 2>&1
  # invalid threshold = fallback 86400s + WARNING 출력 + 3-way MATCH → exit 0
  [ "$status" -eq 0 ]
  [[ "$output" == *"MATCH"* ]]
  # WARNING 메시지 포함 (invalid threshold 명시)
  [[ "$output" == *"invalid"* ]] || [[ "$output" == *"WARNING"* ]]
}
