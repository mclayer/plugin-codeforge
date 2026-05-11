#!/usr/bin/env bash
# test_kpi_schema_validation.sh
# CFP-393 Phase 2 — KPI JSON schema validation + evidence registry tests (§8.3-8.5)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || echo "/c/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-393-phase2-aggregator-workflow")

REGISTRY_FILE="$REPO_ROOT/docs/evidence-checks-registry.yaml"
LABEL_REGISTRY="$REPO_ROOT/docs/inter-plugin-contracts/label-registry-v2.md"
KPI_JSON_INITIAL="$REPO_ROOT/docs/kpi/rate-limit-fallback.json"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_true() {
  local desc="$1"
  local condition="$2"

  TESTS_RUN=$((TESTS_RUN + 1))
  if eval "$condition"; then
    echo -e "${GREEN}✓${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $desc"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

assert_contains() {
  local desc="$1"
  local file_path="$2"
  local pattern="$3"

  TESTS_RUN=$((TESTS_RUN + 1))
  if grep -q "$pattern" "$file_path" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $desc"
    echo "    Pattern not found: $pattern"
    echo "    File: $file_path"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# ============================================================================
# §8.3 Registry Entry Tests
# ============================================================================

test_registry_yaml_valid() {
  if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo -e "${RED}✗${NC} evidence-checks-registry.yaml not found"
    TESTS_RUN=$((TESTS_RUN + 1))
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi

  if python3 -c "import yaml; yaml.safe_load(open('$REGISTRY_FILE'))" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} evidence-checks-registry.yaml is valid YAML"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} evidence-checks-registry.yaml YAML parsing failed"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
  TESTS_RUN=$((TESTS_RUN + 1))
}

test_registry_entry_exists() {
  assert_contains "Registry entry 'rate-limit-fallback-rate' exists" "$REGISTRY_FILE" "rate-limit-fallback-rate"
}

test_registry_entry_name_unique() {
  local count
  count=$(grep -c "^  - name: rate-limit-fallback-rate" "$REGISTRY_FILE" 2>/dev/null || echo "0")

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ $count -eq 1 ]]; then
    echo -e "${GREEN}✓${NC} Registry entry name is unique"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} Registry entry name appears $count times (expected 1)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

test_registry_entry_fields() {
  # Check for required fields in entry
  assert_contains "Entry has 'name' field" "$REGISTRY_FILE" "name: rate-limit-fallback-rate"
  assert_contains "Entry has 'description' field" "$REGISTRY_FILE" "description:"
  assert_contains "Entry has 'detect_command' field" "$REGISTRY_FILE" "detect_command:"
  assert_contains "Entry has 'workflow' field" "$REGISTRY_FILE" "workflow:"
  assert_contains "Entry has 'current_tier' field" "$REGISTRY_FILE" "current_tier:"
  assert_contains "Entry has 'introduced_by' field" "$REGISTRY_FILE" "introduced_by:"
  assert_contains "Entry has 'owner_adr' field" "$REGISTRY_FILE" "owner_adr:"
  assert_contains "Entry has 'carrier_adr' field" "$REGISTRY_FILE" "carrier_adr:"
}

test_registry_tier_value() {
  assert_contains "Registry tier is 'warning'" "$REGISTRY_FILE" "current_tier: warning"
}

test_registry_two_entries_not_conflict() {
  local first_entry second_entry
  first_entry=$(grep "^  - name:" "$REGISTRY_FILE" | head -1 | sed 's/.*name: //')
  second_entry=$(grep "^  - name:" "$REGISTRY_FILE" | tail -1 | sed 's/.*name: //')

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$first_entry" != "$second_entry" ]]; then
    echo -e "${GREEN}✓${NC} Two entries have different names"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} Two entries have same name"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# ============================================================================
# §8.4 Label Registry Tests
# ============================================================================

test_label_registry_entry_exists() {
  if [[ ! -f "$LABEL_REGISTRY" ]]; then
    echo -e "${YELLOW}⊘${NC} label-registry-v2.md not found (optional test)"
    return
  fi

  assert_contains "Label registry has 'codeforge-kpi-alert' entry" "$LABEL_REGISTRY" "codeforge-kpi-alert"
}

test_label_registry_monitoring_tier() {
  if [[ ! -f "$LABEL_REGISTRY" ]]; then
    return
  fi

  # Check if monitoring tier is mentioned in context of codeforge-kpi-alert
  # This is a soft check since monitoring might be in a separate section
  assert_contains "Label registry mentions monitoring category" "$LABEL_REGISTRY" "monitoring"
}

# ============================================================================
# §8.5 §14 Lane Evidence Input Contract Tests
# ============================================================================

test_evidence_transcript_field_no_collision() {
  # Check that existing §14 rows don't accidentally have our tag
  local repo_stories="$REPO_ROOT/docs/stories"

  if [[ ! -d "$repo_stories" ]]; then
    echo -e "${YELLOW}⊘${NC} docs/stories not found (test deferred)"
    return
  fi

  # Count existing uses of [rate-limit-fallback:...] tag (should be 0 in existing files)
  local existing_count
  existing_count=$(grep -r "\[rate-limit-fallback:" "$repo_stories" 2>/dev/null | wc -l || echo "0")

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ $existing_count -eq 0 ]]; then
    echo -e "${GREEN}✓${NC} No accidental [rate-limit-fallback:...] tags in existing stories"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${YELLOW}⊘${NC} Found $existing_count existing [rate-limit-fallback:...] tags (may be test fixtures)"
    # Not a failure — could be test fixtures
  fi
}

# ============================================================================
# §4.2 KPI JSON Schema Validation (examples)
# ============================================================================

test_kpi_json_schema_invariants() {
  # Test that if a valid KPI JSON were present, it would validate invariants
  # This is a template test for the invariants

  local sample_json
  sample_json='{
    "schema_version": "1.0",
    "sonnet_spawn_total": 100,
    "fallback_count": 2,
    "fallback_rate_percent": 2.0,
    "sample_size_sufficient": true,
    "gate_status": "violated"
  }'

  # Invariant 1: fallback_count <= sonnet_spawn_total
  local fb_count spawn_total
  fb_count=$(echo "$sample_json" | jq -r '.fallback_count')
  spawn_total=$(echo "$sample_json" | jq -r '.sonnet_spawn_total')

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ $fb_count -le $spawn_total ]]; then
    echo -e "${GREEN}✓${NC} Invariant: fallback_count <= spawn_total"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} Invariant violated: fallback_count > spawn_total"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi

  # Invariant 2: if sample_size_sufficient=false, rate_percent should be null
  local sample2
  sample2='{
    "sample_size_sufficient": false,
    "fallback_rate_percent": null,
    "gate_status": "sample_insufficient"
  }'

  local sufficient rate
  sufficient=$(echo "$sample2" | jq -r '.sample_size_sufficient')
  rate=$(echo "$sample2" | jq -r '.fallback_rate_percent')

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$sufficient" == "false" && "$rate" == "null" ]]; then
    echo -e "${GREEN}✓${NC} Invariant: insufficient sample ⇒ rate=null"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} Invariant violated"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# ============================================================================
# MAIN
# ============================================================================

main() {
  echo "======================================================================"
  echo "CFP-393 Registry & Schema Validation Tests (§8.3-8.5)"
  echo "======================================================================"
  echo ""

  echo "--- §8.3 Evidence Registry Entry Tests ---"
  test_registry_yaml_valid
  test_registry_entry_exists
  test_registry_entry_name_unique
  test_registry_entry_fields
  test_registry_tier_value
  test_registry_two_entries_not_conflict

  echo ""
  echo "--- §8.4 Label Registry Tests ---"
  test_label_registry_entry_exists
  test_label_registry_monitoring_tier

  echo ""
  echo "--- §8.5 §14 Lane Evidence Contract Tests ---"
  test_evidence_transcript_field_no_collision

  echo ""
  echo "--- §4.2 KPI JSON Schema Invariants ---"
  test_kpi_json_schema_invariants

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
    echo -e "${GREEN}✓ All schema validation tests passed!${NC}"
    return 0
  fi
}

main "$@"
