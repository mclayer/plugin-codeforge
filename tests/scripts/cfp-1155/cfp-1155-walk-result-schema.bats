#!/usr/bin/env bats
# tests/scripts/cfp-1155/cfp-1155-walk-result-schema.bats
# CFP-1155 Phase 2 — UpgradeAgent.md imperative walk 재정의 + walk_result schema fixture TDD
# QADeveloperAgent TDD (RED written against Phase 2 spec, GREEN against Phase 2 implementation)
#
# TC map (change-plan §8 TC-1~8 codify):
#
# TC-1:  walk_result enum closed_set (4-value: SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED)
# TC-2:  2-layer 4-field presence (외부 보고 4-field + 내부 schema 4-field)
# TC-3:  exit code → walk_result deterministic mapping (exit 비-0 → {PARTIAL_FAILURE, FAILED})
# TC-4:  dry-run filesystem touch 0 (mandate body walk+plan stage 선언 검증)
# TC-5:  min_prereq mismatch → fallback trigger (SUCCESS_WITH_DEGRADATION grace window 안)
# TC-6:  per-family atomic rollback → PARTIAL_FAILURE (부분 산출물 forbidden)
# TC-7:  customization marker 보존 (wrapper SSOT wins 안 / consumer 보존 밖)
# TC-8:  idempotency (동일 target version + entry hash = no-op)
#
# 3-layer defense (3중 검증 — #960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture (기존 UpgradeAgent.md = declarative → RED 검증)
#
# Mock seam: _CFP1155_MOCK_* namespace (CFP-1014 패턴 답습)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# SSOT: docs/inter-plugin-contracts/imperative-walker-protocol-v1.md §2.A
# Change-plan: docs/change-plans/cfp-1155-upgrade-walker-runtime.md §8
# ADR ref: ADR-093 (walk_result schema) / ADR-098 (UpgradeAgent ownership) / ADR-042 Amd 11 (model tier)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

UPGRADE_AGENT_MD="${WORKTREE_ROOT}/templates/agents/UpgradeAgent.md"
WALKER_CONTRACT="${WORKTREE_ROOT}/docs/inter-plugin-contracts/imperative-walker-protocol-v1.md"
WALK_RESULT_FIXTURE_YAML="${WORKTREE_ROOT}/tests/fixtures/cfp-1155/walk-result-schema.yaml"
WALK_RESULT_FIXTURE_JSON="${WORKTREE_ROOT}/tests/fixtures/cfp-1155/walk-result-schema.json"

# ──────────────────────────────────────────────── sandbox setup ───────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
  export CFP1155_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
  unset CFP1155_SKIP_ISSUE_CREATE
}

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown() {
  unset _CFP1155_MOCK_WALK_RESULT || true
  unset _CFP1155_MOCK_EXIT_CODE || true
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1155-unused}"
}

# ──────────────────────────── prerequisite checks ────────────────────────────

@test "PREREQ: UpgradeAgent.md 존재 확인" {
  [ -f "$UPGRADE_AGENT_MD" ]
}

@test "PREREQ: imperative-walker-protocol-v1.md 존재 확인" {
  [ -f "$WALKER_CONTRACT" ]
}

@test "PREREQ: walk-result-schema.yaml fixture 존재 확인" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
}

@test "PREREQ: walk-result-schema.json fixture 존재 확인" {
  [ -f "$WALK_RESULT_FIXTURE_JSON" ]
}

# ───────────────── TC-1: walk_result enum closed_set ─────────────────────────
# change-plan §8.1 TC-1 codify
# SSOT: imperative-walker-protocol-v1.md §2.A.1

@test "TC-1 (P0): walk_result enum 4-value closed_set — contract §2.A.1 선언 존재" {
  [ -f "$WALKER_CONTRACT" ]
  # positive — 4 enum 값 모두 contract §2.A.1 에 선언됨
  grep -q "SUCCESS" "$WALKER_CONTRACT"
  grep -q "SUCCESS_WITH_DEGRADATION" "$WALKER_CONTRACT"
  grep -q "PARTIAL_FAILURE" "$WALKER_CONTRACT"
  grep -q "FAILED" "$WALKER_CONTRACT"
  # positive — open_extension: false 선언 존재 (closed-set 명문화)
  grep -A 5 "walk_result:" "$WALKER_CONTRACT" | grep -q "open_extension: false"
}

@test "TC-1b (P0): walk_result enum closed_set — fixture yaml 4-value 검증" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
  # positive — yaml fixture 에 4개 enum 값 존재
  grep -q "SUCCESS$" "$WALK_RESULT_FIXTURE_YAML" || grep -q "- SUCCESS" "$WALK_RESULT_FIXTURE_YAML"
  grep -q "SUCCESS_WITH_DEGRADATION" "$WALK_RESULT_FIXTURE_YAML"
  grep -q "PARTIAL_FAILURE" "$WALK_RESULT_FIXTURE_YAML"
  grep -q "FAILED" "$WALK_RESULT_FIXTURE_YAML"
  # negative — 5번째 값 (UNKNOWN, PARTIAL_SUCCESS 등) 이 valid_values 에 없어야 함
  # fixture invalid_values 섹션 에 UNKNOWN 이 명시되어 있어야 함
  grep -q "UNKNOWN" "$WALK_RESULT_FIXTURE_YAML"
}

@test "TC-1c (P0) [discriminating — RED phase]: UpgradeAgent.md 가 imperative walk 4-enum 선언 포함 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 UpgradeAgent.md 에 walk_result 4-value 선언 존재 필수
  # RED phase (기존 declarative body): reconcile-protocol-v1 citation → 이 TC FAIL
  # GREEN phase (imperative walk body): imperative-walker-protocol-v1 citation → PASS
  grep -q "imperative-walker-protocol-v1" "$UPGRADE_AGENT_MD"
}

# ───────────────── TC-2: 2-layer 4-field presence ────────────────────────────
# change-plan §8.1 TC-2 codify
# SSOT: imperative-walker-protocol-v1.md §2.A.2

@test "TC-2 (P0): 외부 보고 4-field — contract §2.A.2 선언 존재" {
  [ -f "$WALKER_CONTRACT" ]
  # positive — 외부 보고 layer 4-field 모두 선언
  grep -q "from_version" "$WALKER_CONTRACT"
  grep -q "to_version" "$WALKER_CONTRACT"
  grep -q "target_version_release_date" "$WALKER_CONTRACT"
  grep -q "key_changes_summary" "$WALKER_CONTRACT"
}

@test "TC-2b (P0): 내부 schema 4-field — contract §2.A.2 선언 존재" {
  [ -f "$WALKER_CONTRACT" ]
  # positive — 내부 schema layer 4-field 모두 선언
  grep -q "touched_files" "$WALKER_CONTRACT"
  grep -q "atomic_invariants" "$WALKER_CONTRACT"
  grep -q "verify_via" "$WALKER_CONTRACT"
  grep -q "lane_outcomes" "$WALKER_CONTRACT"
}

@test "TC-2c (P0) [discriminating — RED phase]: UpgradeAgent.md 에 2-layer 4-field 완료 보고 섹션 존재 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 UpgradeAgent.md 에 walk 완료 보고 섹션 존재
  # 외부 보고 4-field (from_version / to_version 등) 선언 필수
  grep -q "from_version" "$UPGRADE_AGENT_MD"
  grep -q "to_version" "$UPGRADE_AGENT_MD"
}

@test "TC-2d (P1): fixture json 2-layer 구조 검증" {
  [ -f "$WALK_RESULT_FIXTURE_JSON" ]
  # positive — json fixture 에 external_report 레이어 존재
  grep -q "external_report" "$WALK_RESULT_FIXTURE_JSON"
  # positive — json fixture 에 internal_schema 레이어 존재
  grep -q "internal_schema" "$WALK_RESULT_FIXTURE_JSON"
  # negative — cross_contamination_forbidden: true 선언 존재 (혼입 금지 명문화)
  grep -q "cross_contamination_forbidden" "$WALK_RESULT_FIXTURE_JSON"
}

# ───────────────── TC-3: exit code deterministic mapping ─────────────────────
# change-plan §8.1 TC-3 codify
# SSOT: imperative-walker-protocol-v1.md §2.A.1 exit_code_mapping

@test "TC-3 (P0): exit code → walk_result deterministic mapping 선언 — contract §2.A.1" {
  [ -f "$WALKER_CONTRACT" ]
  # positive — deterministic mapping 의무 선언 존재
  grep -q "deterministic" "$WALKER_CONTRACT"
  # positive — silent false SUCCESS 차단 선언
  grep -q "silent false SUCCESS" "$WALKER_CONTRACT" || grep -q "SUCCESS hardcode" "$WALKER_CONTRACT"
}

@test "TC-3b (P0): fixture — exit_code_deterministic: true 선언 확인" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
  grep -q "exit_code_deterministic: true" "$WALK_RESULT_FIXTURE_YAML"
  # positive — forbidden_combination 섹션 존재 (silent false SUCCESS 금지 fixture)
  grep -q "forbidden_combination" "$WALK_RESULT_FIXTURE_YAML"
}

@test "TC-3c (P0) [discriminating — RED phase]: UpgradeAgent.md 에 walk_result + exit code 매핑 섹션 존재 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 UpgradeAgent.md 에 walk_result enum 선언 존재
  grep -q "walk_result" "$UPGRADE_AGENT_MD"
}

# ───────────────── TC-4: dry-run filesystem touch 0 ──────────────────────────
# change-plan §8.2 TC-4 codify

@test "TC-4 (P1): dry-run mandate — UpgradeAgent.md walk + plan stage = filesystem touch 0 선언 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 walk stage = read-only / filesystem touch 0 선언 필수
  # RED phase: 기존 declarative body 에는 dry_run 섹션이 있으나 walk stage 선언 없음
  grep -q "filesystem touch 0" "$UPGRADE_AGENT_MD"
  # positive — walk stage read-only invariant 선언
  grep -q "read-only" "$UPGRADE_AGENT_MD" || grep -q "walk.*read" "$UPGRADE_AGENT_MD"
}

@test "TC-4b (P1): fixture — TC-4 filesystem_touch: 0 선언 확인" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
  grep -q "filesystem_touch: 0" "$WALK_RESULT_FIXTURE_YAML"
  grep -q "apply_stage_active: false" "$WALK_RESULT_FIXTURE_YAML"
}

# ───────────────── TC-5: min_prereq mismatch → fallback ─────────────────────
# change-plan §8.2 TC-5 codify
# SSOT: imperative-walker-protocol-v1.md §2.C / §2.E

@test "TC-5 (P1): min_prereq mismatch 처리 — contract §2.C / §2.E 선언 존재" {
  [ -f "$WALKER_CONTRACT" ]
  # positive — hybrid grace period 선언 존재
  grep -q "hybrid_grace_period" "$WALKER_CONTRACT"
  # positive — SUCCESS_WITH_DEGRADATION = grace window 안 degraded mode walk_result
  grep -q "SUCCESS_WITH_DEGRADATION" "$WALKER_CONTRACT"
}

@test "TC-5b (P1): fixture — TC-5 fallback_trigger_fired: true + expected_walk_result 검증" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
  grep -q "expected_walk_result: SUCCESS_WITH_DEGRADATION" "$WALK_RESULT_FIXTURE_YAML"
  grep -q "fallback_trigger_fired: true" "$WALK_RESULT_FIXTURE_YAML"
}

@test "TC-5c (P1) [discriminating — RED phase]: UpgradeAgent.md 에 min_prereq + fallback 처리 섹션 존재 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 plan stage §3.3 fallback trigger 선언 필수
  grep -q "min_prereq" "$UPGRADE_AGENT_MD" || grep -q "min_prerequisite" "$UPGRADE_AGENT_MD"
}

# ───────────────── TC-6: per-family atomic rollback ──────────────────────────
# change-plan §8.2 TC-6 codify
# SSOT: change-plan §3.1 Stage 3 / §7.4.1

@test "TC-6 (P0): per-family atomic rollback — contract §2.A.1 PARTIAL_FAILURE 의미 선언" {
  [ -f "$WALKER_CONTRACT" ]
  # positive — PARTIAL_FAILURE = 일부 plugin apply 실패 + per-family rollback 후 보고
  grep -q "PARTIAL_FAILURE" "$WALKER_CONTRACT"
  # positive — 부분 산출물 forbidden
  grep -q "부분 산출물 forbidden\|partial.*forbidden" "$WALKER_CONTRACT"
}

@test "TC-6b (P0): fixture — TC-6 family_rollback: true + PARTIAL_FAILURE 선언" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
  grep -q "expected_walk_result: PARTIAL_FAILURE" "$WALK_RESULT_FIXTURE_YAML"
  grep -q "family_rollback: true" "$WALK_RESULT_FIXTURE_YAML"
  grep -q "partial_artifact_forbidden: true" "$WALK_RESULT_FIXTURE_YAML"
}

@test "TC-6c (P0) [discriminating — RED phase]: UpgradeAgent.md 에 per-family atomic rollback 선언 존재 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 per-family atomic rollback boundary 선언 필수
  # RED phase: 기존 declarative body 에는 "9 영역 reconcile" 있으나 "per-family atomic" 없음
  grep -q "per-family" "$UPGRADE_AGENT_MD"
}

# ───────────────── TC-7: customization marker 보존 ───────────────────────────
# change-plan §8.2 TC-7 codify / §R-2 결정

@test "TC-7 (P1): customization marker 보존 — walk apply stage 흡수 R-2 선언 존재 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 walk apply stage 에 R-2 흡수 선언 필수
  # RED phase: 기존 declarative body 에서 marker block 은 "9 영역 reconcile" 맥락이지 "walk apply stage 흡수" 아님
  # GREEN phase: "apply" + "customization" 또는 "R-2" + "walk" 병존 필수
  grep -q "walk\|apply" "$UPGRADE_AGENT_MD"
  # discriminating: 기존 declarative 에는 "reconcile-overlay.sh 흡수" 또는 "apply stage 흡수" 없음
  grep -q "apply.*marker\|marker.*apply\|reconcile-overlay.*흡수\|walk apply" "$UPGRADE_AGENT_MD"
}

@test "TC-7b (P1): fixture — TC-7 rollback_restores_marker: true 선언" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
  grep -q "rollback_restores_marker: true" "$WALK_RESULT_FIXTURE_YAML"
}

# ───────────────── TC-8: idempotency ─────────────────────────────────────────
# change-plan §8.2 TC-8 codify / §11.6

@test "TC-8 (P1): idempotency — UpgradeAgent.md idempotency 섹션 존재 (GREEN 후 변경 확인)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 idempotency key = (target version + applied changelog entry hash)
  # RED phase: 기존 declarative body idempotency key = "9 영역 desired state content hash"
  # GREEN phase: idempotency key 에 "changelog entry" 포함 필수
  grep -q "idempotency" "$UPGRADE_AGENT_MD"
  # positive — idempotency key 에 changelog entry hash 포함 (GREEN assertion)
  grep -q "changelog entry" "$UPGRADE_AGENT_MD"
}

@test "TC-8b (P1): fixture — TC-8 idempotency no-op 선언" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
  grep -q "second_apply_result: \"no-op\"" "$WALK_RESULT_FIXTURE_YAML"
  grep -q "diff_empty: true" "$WALK_RESULT_FIXTURE_YAML"
}

# ───────────────── ADR-042 Amendment 11 model tier ───────────────────────────
# change-plan §3.4 / ADR-042 Amendment 11

@test "TC-MODEL (P0): UpgradeAgent.md frontmatter model: opus 선언 (ADR-042 Amd 11 — GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 model: opus 필수 (ADR-042 Amendment 11)
  # RED phase: 기존 model: sonnet → 이 TC FAIL
  local model_value
  model_value=$(head -20 "$UPGRADE_AGENT_MD" | grep "^model:" | awk '{print $2}' | tr -d '"')
  [ "$model_value" = "opus" ]
}

# ───────────────── reconcile-protocol-v1 citation 금지 ───────────────────────
# change-plan §3.4 / ADR-098 §결정 3

@test "TC-CITATION (P0): UpgradeAgent.md 에 reconcile-protocol-v1 1st-class citation 0 건 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 reconcile-protocol-v1 citation 금지 (ADR-098 §결정 3)
  # RED phase: 기존 declarative body 에 reconcile-protocol-v1 v1.2 citation 존재 → FAIL
  # GREEN phase: citation 제거 → PASS
  # "reconcile-protocol-v1" 가 1st-class 참조 계약으로 사용되면 FAIL
  # (Deprecated 이므로 참조 계약 섹션에 나타나면 안 됨)
  if grep -q "reconcile-protocol-v1" "$UPGRADE_AGENT_MD"; then
    # citation 이 있더라도 "Deprecated" 와 함께 있으면 허용 (역사적 언급)
    # 단 "참조 계약" 섹션에 1st-class 로 있으면 FAIL
    local ref_section_citation
    ref_section_citation=$(grep -A 20 "## 참조 계약" "$UPGRADE_AGENT_MD" | grep "reconcile-protocol-v1" || true)
    [ -z "$ref_section_citation" ]
  fi
}

# ───────────────── walk + plan + apply 3-stage mandate ───────────────────────
# change-plan §3.1 / §3.4

@test "TC-3STAGE (P0): UpgradeAgent.md walk + plan + apply 3-stage 선언 존재 (GREEN 후 PASS)" {
  [ -f "$UPGRADE_AGENT_MD" ]
  # GREEN assertion — Phase 2 구현 후 3-stage mandate 선언 필수
  grep -q "walk" "$UPGRADE_AGENT_MD"
  grep -q "plan" "$UPGRADE_AGENT_MD"
  grep -q "apply" "$UPGRADE_AGENT_MD"
}

# ───────────────── schema fixture 정합성 자체 검증 ────────────────────────────

@test "TC-FIXTURE-YAML (P1): walk-result-schema.yaml schema_version + carrier 필드 검증" {
  [ -f "$WALK_RESULT_FIXTURE_YAML" ]
  grep -q 'schema_version: "1.0"' "$WALK_RESULT_FIXTURE_YAML"
  grep -q 'carrier: CFP-1155' "$WALK_RESULT_FIXTURE_YAML"
  grep -q 'contract_ref:' "$WALK_RESULT_FIXTURE_YAML"
}

@test "TC-FIXTURE-JSON (P1): walk-result-schema.json schema_version + carrier 필드 검증" {
  [ -f "$WALK_RESULT_FIXTURE_JSON" ]
  grep -q '"schema_version": "1.0"' "$WALK_RESULT_FIXTURE_JSON"
  grep -q '"carrier": "CFP-1155"' "$WALK_RESULT_FIXTURE_JSON"
  grep -q '"contract_ref"' "$WALK_RESULT_FIXTURE_JSON"
}

@test "TC-FIXTURE-JSON-VALID (P1): walk-result-schema.json Python 파싱 + 구조 검증 (ADR-061 외부 .py)" {
  [ -f "$WALK_RESULT_FIXTURE_JSON" ]
  local validator
  validator="$(dirname "$BATS_TEST_FILENAME")/validate_walk_result_schema.py"
  [ -f "$validator" ]
  python3 "$validator" "$WALK_RESULT_FIXTURE_JSON"
}
