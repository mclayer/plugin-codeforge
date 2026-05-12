#!/usr/bin/env bash
# test_rate-limit-fallback-kpi-yml.sh
# CFP-393 Phase 2 — Workflow YAML validation tests (§8.2)
# Tests: YAML validity, permissions minimum, concurrency group, step ID uniqueness

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || echo "/c/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-393-phase2-aggregator-workflow")

WORKFLOW_FILE="$REPO_ROOT/templates/github-workflows/rate-limit-fallback-kpi.yml"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_equals() {
  local desc="$1"
  local expected="$2"
  local actual="$3"

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$expected" == "$actual" ]]; then
    echo -e "${GREEN}✓${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $desc"
    echo "    Expected: $expected"
    echo "    Actual:   $actual"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

assert_contains() {
  local desc="$1"
  local file_content="$2"
  local pattern="$3"

  TESTS_RUN=$((TESTS_RUN + 1))
  if echo "$file_content" | grep -q "$pattern"; then
    echo -e "${GREEN}✓${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $desc"
    echo "    Pattern not found: $pattern"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# ============================================================================
# Test: YAML is valid
# ============================================================================
test_yaml_valid() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  # Try to parse with python yaml (most portable)
  if command -v python3 &>/dev/null; then
    if python3 -c "import yaml; yaml.safe_load('''$file_content''')" 2>/dev/null; then
      echo -e "${GREEN}✓${NC} Workflow YAML is valid"
      TESTS_PASSED=$((TESTS_PASSED + 1))
    else
      echo -e "${RED}✗${NC} Workflow YAML is invalid (python3 parse failed)"
      TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
  fi
  TESTS_RUN=$((TESTS_RUN + 1))
}

# ============================================================================
# Test: Permissions minimum (deny-all top level, job override only)
# ============================================================================
test_permissions_minimum() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  # Should have "permissions: {}" at top level
  assert_contains "Workflow has top-level deny-all permissions" "$file_content" "^permissions: {}"

  # Should have job-level permissions override
  assert_contains "Job has contents:write permission" "$file_content" "contents: write"
  assert_contains "Job has pull-requests:write permission" "$file_content" "pull-requests: write"
  assert_contains "Job has issues:write permission" "$file_content" "issues: write"
}

# ============================================================================
# Test: Concurrency group defined
# ============================================================================
test_concurrency_group() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "Concurrency group defined" "$file_content" "concurrency:"
  assert_contains "Concurrency group has rate-limit-fallback-kpi" "$file_content" "group: rate-limit-fallback-kpi"
  assert_contains "Cancel-in-progress is false" "$file_content" "cancel-in-progress: false"
}

# ============================================================================
# Test: Schedule (cron) is defined
# ============================================================================
test_schedule_cron() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "Schedule trigger defined" "$file_content" "schedule:"
  assert_contains "Monthly cron (0 0 1 * *)" "$file_content" "0 0 1 \* \*"
}

# ============================================================================
# Test: Workflow dispatch input (as_of) exists
# ============================================================================
test_workflow_dispatch_input() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "Workflow dispatch defined" "$file_content" "workflow_dispatch:"
  assert_contains "as_of input defined" "$file_content" "as_of:"
}

# ============================================================================
# Test: Step IDs are unique and descriptive
# ============================================================================
test_step_ids_unique() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  local step_ids
  step_ids=$(echo "$file_content" | grep -E "^\s+id:" | sed 's/.*id: //; s/\s*$//' | sort)

  # Count duplicates
  local duplicate_count
  duplicate_count=$(echo "$step_ids" | uniq -d | wc -l)

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ $duplicate_count -eq 0 ]]; then
    echo -e "${GREEN}✓${NC} Step IDs are unique"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} Duplicate step IDs found: $(echo "$step_ids" | uniq -d)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi

  # Verify expected step IDs exist
  assert_contains "Step 'clone_internal' defined" "$file_content" "id: clone_internal"
  assert_contains "Step 'aggregate' defined" "$file_content" "id: aggregate"
  assert_contains "Step 'diff' defined" "$file_content" "id: diff"
  assert_contains "Step 'window' defined" "$file_content" "id: window"
  assert_contains "Step 'existing_alert' defined" "$file_content" "id: existing_alert"
  # CFP-451 신규 step id
  assert_contains "Step 'auto_pr' defined" "$file_content" "id: auto_pr"
  assert_contains "Step 'detect_infra' defined" "$file_content" "id: detect_infra"
}

# ============================================================================
# Test: Timeout defined
# ============================================================================
test_timeout_defined() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "Timeout defined" "$file_content" "timeout-minutes: 10"
}

# ============================================================================
# Test: Key workflow steps present
# ============================================================================
test_required_steps() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "Checkout step present" "$file_content" "uses: actions/checkout"
  assert_contains "Clone internal-docs step" "$file_content" "Clone codeforge-internal-docs"
  assert_contains "Run aggregator step" "$file_content" "Run aggregator"
  assert_contains "Check JSON changed step" "$file_content" "Check JSON changed"
  assert_contains "Create auto-PR step" "$file_content" "Create or update auto-PR"
}

# ============================================================================
# Test: Environment variables usage
# ============================================================================
test_env_variables() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "GH_TOKEN environment variable used" "$file_content" "GH_TOKEN"
  assert_contains "AS_OF_INPUT environment variable used" "$file_content" "AS_OF_INPUT"
  assert_contains "GITHUB_OUTPUT environment variable used" "$file_content" "GITHUB_OUTPUT"
}

# ============================================================================
# Test: Conditional steps (if conditions)
# ============================================================================
test_conditional_steps() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "Step with conditional (if)" "$file_content" "if:"
  assert_contains "Window step conditional" "$file_content" "if: steps.aggregate.outputs.gate == 'violated'"
}

# ============================================================================
# CFP-451 — NEW tests (4 functions)
# ============================================================================

# ----------------------------------------------------------------------------
# Test: aggregate step exit_code capture pattern (AC-12 — PL 신규)
#   Story §5.1 row 부재, CP §1.3 + §3.5 + §8.1 table 단일 source.
#   DesignReview F-001 Option C 안전망 정합.
# ----------------------------------------------------------------------------
test_aggregate_exit_code_capture() {
  TESTS_RUN=$((TESTS_RUN + 1))
  # aggregate step block 추출: "- name: Run aggregator" ~ "- name: Check JSON changed" 사이.
  local agg_block
  agg_block=$(awk '/^      - name: Run aggregator$/,/^      - name: Check JSON changed/' "$WORKFLOW_FILE")

  local has_capture_mode=0
  if echo "$agg_block" | grep -qE "set -uo pipefail|set \+e"; then
    has_capture_mode=1
  fi

  local has_exit_code_var=0
  if echo "$agg_block" | grep -qE 'exit_code=\$\?'; then
    has_exit_code_var=1
  fi

  local has_output_export=0
  if echo "$agg_block" | grep -qE 'echo "exit_code='; then
    has_output_export=1
  fi

  if [ "$has_capture_mode" -eq 1 ] && [ "$has_exit_code_var" -eq 1 ] && [ "$has_output_export" -eq 1 ]; then
    echo -e "${GREEN}✓${NC} aggregate step 이 exit_code capture pattern 보유 (AC-12)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} aggregate step exit_code capture pattern 결손 (mode=$has_capture_mode var=$has_exit_code_var export=$has_output_export)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# ----------------------------------------------------------------------------
# Test: detect_infra step + case 분기 + *) fallback default
# ----------------------------------------------------------------------------
test_detect_infra_step_exists() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "detect_infra step 정의" "$file_content" "id: detect_infra"
  assert_contains "detect_infra 의 if: always()" "$file_content" "if: always()"
  assert_contains "detect_infra 의 case 분기" "$file_content" 'case "${agg_exit}" in'
  assert_contains "detect_infra 의 *) fallback default" "$file_content" '\*)'
  assert_contains "detect_infra 의 exit 3 sub-reason" "$file_content" 'exit 3'
  assert_contains "detect_infra 의 exit 4 sub-reason" "$file_content" 'exit 4'
}

# ----------------------------------------------------------------------------
# Test: Open infra error issue step + --label codeforge-kpi-infra-error
# ----------------------------------------------------------------------------
test_open_infra_issue_step_exists() {
  local file_content
  file_content=$(cat "$WORKFLOW_FILE")

  assert_contains "Open infra error issue step 정의" "$file_content" "Open infra error issue"
  assert_contains "infra_error 조건부 발화" "$file_content" "steps.detect_infra.outputs.infra_error == 'true'"

  # `--label codeforge-kpi-infra-error` 검증 — grep `--` 옵션 종결자 사용 (assert_contains 우회).
  TESTS_RUN=$((TESTS_RUN + 1))
  if grep -q -- "--label codeforge-kpi-infra-error" "$WORKFLOW_FILE"; then
    echo -e "${GREEN}✓${NC} infra error 의 --label codeforge-kpi-infra-error 부착"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} infra error 의 --label codeforge-kpi-infra-error 부착"
    echo "    Pattern not found: --label codeforge-kpi-infra-error"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# ----------------------------------------------------------------------------
# Test: alert dual-open invariant — Open KPI alert issue 의 if 조건이
#       detect_infra.outputs.infra_error 참조 0 (suppression 안 함, 사용자 결정 3)
# ----------------------------------------------------------------------------
test_alert_dual_open_with_infra_error() {
  TESTS_RUN=$((TESTS_RUN + 1))
  # Open KPI alert issue step 의 if 조건 라인 추출
  local alert_if_line
  alert_if_line=$(grep -A1 "Open KPI alert issue" "$WORKFLOW_FILE" | grep "^[[:space:]]*if:")

  if [ -z "$alert_if_line" ]; then
    echo -e "${RED}✗${NC} Open KPI alert issue 의 if 조건 라인 미발견"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return
  fi

  # if 조건이 detect_infra.outputs.infra_error 참조하지 않아야 dual-open 정합
  if echo "$alert_if_line" | grep -q "detect_infra.outputs.infra_error"; then
    echo -e "${RED}✗${NC} Open KPI alert issue 의 if 조건이 detect_infra.outputs.infra_error 참조 — dual-open invariant 위반 (사용자 결정 3)"
    echo "    alert_if_line: $alert_if_line"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  else
    echo -e "${GREEN}✓${NC} Open KPI alert issue dual-open 보존 (detect_infra 미참조)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  fi
}

# ============================================================================
# MAIN
# ============================================================================

main() {
  if [[ ! -f "$WORKFLOW_FILE" ]]; then
    echo -e "${RED}ERROR: Workflow file not found: $WORKFLOW_FILE${NC}" >&2
    exit 1
  fi

  echo "======================================================================"
  echo "CFP-393 + CFP-451 Workflow YAML Validation (§8.2)"
  echo "File: $WORKFLOW_FILE"
  echo "======================================================================"
  echo ""

  test_yaml_valid
  test_permissions_minimum
  test_concurrency_group
  test_schedule_cron
  test_workflow_dispatch_input
  test_step_ids_unique
  test_timeout_defined
  test_required_steps
  test_env_variables
  test_conditional_steps

  # CFP-451 신규 — 4 tests
  test_aggregate_exit_code_capture
  test_detect_infra_step_exists
  test_open_infra_issue_step_exists
  test_alert_dual_open_with_infra_error

  echo ""
  echo "======================================================================"
  echo "Test Results"
  echo "======================================================================"
  echo "Run:    $TESTS_RUN"
  echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
  if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    return 1
  else
    echo -e "${GREEN}✓ All workflow tests passed!${NC}"
    return 0
  fi
}

main "$@"
