#!/usr/bin/env bash
# test_aggregator.sh - TDD RED tests for measure-rate-limit-fallback.sh
# CFP-393 Phase 2

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "/c/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-393-phase2-aggregator-workflow")

TEST_AGGREGATOR="$REPO_ROOT/scripts/measure-rate-limit-fallback.sh"

# Verify aggregator exists
if [[ ! -f "$TEST_AGGREGATOR" ]]; then
  echo "ERROR: aggregator script not found at $TEST_AGGREGATOR" >&2
  exit 1
fi

# Temporary directory for test fixtures (will be cleaned up via trap)
TEST_WRAPPER_BASE="/tmp/cfp393-test"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_json_field() {
  local description="$1"
  local json="$2"
  local field="$3"
  local expected="$4"

  TESTS_RUN=$((TESTS_RUN + 1))
  local actual
  actual=$(echo "$json" | jq -r "$field" 2>/dev/null || echo "ERROR")

  if [[ "$actual" == "$expected" ]]; then
    echo -e "${GREEN}✓${NC} $description"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $description"
    echo "    Expected: $expected"
    echo "    Actual:   $actual"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

setup() {
  mkdir -p "$TEST_WRAPPER_BASE"
}

cleanup() {
  rm -rf "$TEST_WRAPPER_BASE" 2>/dev/null || true
}

trap cleanup EXIT

# ============================================================================
# T-1: Normal case — 180 Sonnet rows (3 months × 60), 0 fallback, rate=0%
# ============================================================================
test_t1() {
  echo "  Running T-1..."
  local test_wrapper="$TEST_WRAPPER_BASE/t1"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T1.md"

  cat > "$story" << 'STORY'
---
key: CFP-T1
---
# T-1: Normal case (180 Sonnet across 3 months, no fallback)
## §14. Lane Evidence
STORY

  # Distribute 180 rows across 3 months (each month ≥ 50 for sample sufficiency)
  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent (codeforge-develop@mclayer)
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Normal operation, no fallback"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent (codeforge-develop@mclayer)
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal operation, no fallback"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent (codeforge-develop@mclayer)
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Normal operation, no fallback"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  assert_json_field "T-1: spawn_total = 180" "$output" '.sonnet_spawn_total' "180" || return 1
  assert_json_field "T-1: fallback_count = 0" "$output" '.fallback_count' "0" || return 1
  assert_json_field "T-1: rate_percent = 0" "$output" '.fallback_rate_percent' "0.0000" || return 1
  assert_json_field "T-1: sample_sufficient = true" "$output" '.sample_size_sufficient' "true" || return 1
  assert_json_field "T-1: gate = on_track" "$output" '.gate_status' "on_track" || return 1
}

# ============================================================================
# T-2: Monthly AND sample check — insufficient months (30/40/50 across 3 months)
# ============================================================================
test_t2() {
  echo "  Running T-2..."
  local test_wrapper="$TEST_WRAPPER_BASE/t2"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T2.md"

  cat > "$story" << 'STORY'
---
key: CFP-T2
---
# T-2: Sample insufficient (monthly AND: 30/40/50)
## §14. Lane Evidence
STORY

  for i in {1..30}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Month 1 - insufficient"
ROW
  done

  for i in {1..40}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Month 2 - insufficient"
ROW
  done

  for i in {1..50}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Month 3 - still insufficient"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  assert_json_field "T-2: sample_sufficient = false" "$output" '.sample_size_sufficient' "false" || return 1
  assert_json_field "T-2: gate = sample_insufficient" "$output" '.gate_status' "sample_insufficient" || return 1
}

# ============================================================================
# T-3: Threshold violation — 200 spawn (across 3 months), 6 fallback (3%)
# ============================================================================
test_t3() {
  echo "  Running T-3..."
  local test_wrapper="$TEST_WRAPPER_BASE/t3"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T3.md"

  cat > "$story" << 'STORY'
---
key: CFP-T3
---
# T-3: Threshold violated (200 spawn across 3 months, 6 fallback = 3%)
## §14. Lane Evidence
STORY

  # Distribute 194 normal rows across 3 months (each month ≥ 60)
  for i in {1..65}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..65}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..64}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  # Add 6 fallback entries
  for i in {1..6}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-16T10:00:00Z
    transcript: "[rate-limit-fallback:sonnet→opus] detected"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  assert_json_field "T-3: fallback_count = 6" "$output" '.fallback_count' "6" || return 1
  assert_json_field "T-3: gate = violated" "$output" '.gate_status' "violated" || return 1
}

# ============================================================================
# T-4: Boundary case — 1.0% (200 spawn across 3 months, 2 fallback = 1.0%)
# Chief decision: >= 1.0 is violation
# ============================================================================
test_t4() {
  echo "  Running T-4..."
  local test_wrapper="$TEST_WRAPPER_BASE/t4"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T4.md"

  cat > "$story" << 'STORY'
---
key: CFP-T4
---
# T-4: Boundary (200 spawn across 3 months, 2 fallback = 1.0%)
## §14. Lane Evidence
STORY

  # Distribute 198 normal rows across 3 months
  for i in {1..66}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..66}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..66}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  # Add 2 fallback entries (exactly 1.0% = 2/200)
  for i in {1..2}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-16T10:00:00Z
    transcript: "[rate-limit-fallback:sonnet→opus] Fallback occurred"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  assert_json_field "T-4: gate = violated (1.0%)" "$output" '.gate_status' "violated" || return 1
}

# ============================================================================
# T-5: Agent name substring match (3 months × 60 = 180 total)
# ============================================================================
test_t5() {
  echo "  Running T-5..."
  local test_wrapper="$TEST_WRAPPER_BASE/t5"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T5.md"

  cat > "$story" << 'STORY'
---
key: CFP-T5
---
# T-5: Agent with namespace
## §14. Lane Evidence
STORY

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent (codeforge-develop@mclayer)
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Namespaced agent"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent (codeforge-develop@mclayer)
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Namespaced agent"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent (codeforge-develop@mclayer)
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Namespaced agent"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  assert_json_field "T-5: spawn_total = 180" "$output" '.sonnet_spawn_total' "180" || return 1
}

# ============================================================================
# T-6: Graceful skip of malformed rows (3 months × 60 + 1 malformed = 180 valid)
# ============================================================================
test_t6() {
  echo "  Running T-6..."
  local test_wrapper="$TEST_WRAPPER_BASE/t6"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T6.md"

  cat > "$story" << 'STORY'
---
key: CFP-T6
---
# T-6: Malformed rows
## §14. Lane Evidence
STORY

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  # Malformed row (missing transcript)
  cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-16T10:00:00Z
ROW

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  # Malformed row is skipped, but the spawned_at without transcript still increments count
  # Aggregator counts all rows with valid agent+spawned_at, regardless of transcript
  assert_json_field "T-6: spawn_total = 181" "$output" '.sonnet_spawn_total' "181" || return 1
  assert_json_field "T-6: partial_data = true" "$output" '.partial_data' "true" || return 1
}

# ============================================================================
# T-7: Zero stories (division by zero)
# ============================================================================
test_t7() {
  echo "  Running T-7..."
  local test_wrapper="$TEST_WRAPPER_BASE/t7"
  mkdir -p "$test_wrapper/docs/stories"

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-06" 2>/dev/null)

  assert_json_field "T-7: spawn_total = 0" "$output" '.sonnet_spawn_total' "0" || return 1
  assert_json_field "T-7: gate = sample_insufficient" "$output" '.gate_status' "sample_insufficient" || return 1
}

# ============================================================================
# T-8: Unicode and ASCII arrows (3 months × 60 + 2 fallback = 182 total)
# ============================================================================
test_t8() {
  echo "  Running T-8..."
  local test_wrapper="$TEST_WRAPPER_BASE/t8"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T8.md"

  cat > "$story" << 'STORY'
---
key: CFP-T8
---
# T-8: Unicode and ASCII arrows
## §14. Lane Evidence
STORY

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-16T10:00:00Z
    transcript: "[rate-limit-fallback:sonnet→opus] Unicode arrow"
ROW

  cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-17T10:00:00Z
    transcript: "[rate-limit-fallback:sonnet->opus] ASCII arrow"
ROW

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  assert_json_field "T-8: fallback_count = 2" "$output" '.fallback_count' "2" || return 1
}

# ============================================================================
# T-9: Idempotency (3 months × 60 = 180 total)
# ============================================================================
test_t9() {
  echo "  Running T-9..."
  local test_wrapper="$TEST_WRAPPER_BASE/t9"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T9.md"

  cat > "$story" << 'STORY'
---
key: CFP-T9
---
# T-9: Idempotency
## §14. Lane Evidence
STORY

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Idempotent input"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Idempotent input"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Idempotent input"
ROW
  done

  local output1 output2 norm1 norm2
  output1=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)
  output2=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  norm1=$(echo "$output1" | jq 'del(.measured_at, .last_updated)')
  norm2=$(echo "$output2" | jq 'del(.measured_at, .last_updated)')

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$norm1" == "$norm2" ]]; then
    echo -e "${GREEN}✓${NC} T-9: idempotent (excluding timestamps)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} T-9: idempotent check failed"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# ============================================================================
# T-10: Wrapper-only mode (3 months × 60 = 180 total)
# ============================================================================
test_t10() {
  echo "  Running T-10..."
  local test_wrapper="$TEST_WRAPPER_BASE/t10"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T10.md"

  cat > "$story" << 'STORY'
---
key: CFP-T10
---
# T-10: Wrapper-only mode
## §14. Lane Evidence
STORY

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-04-15T10:00:00Z
    transcript: "Wrapper-only"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Wrapper-only"
ROW
  done

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Wrapper-only"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" 2>/dev/null)

  assert_json_field "T-10: partial_data = true" "$output" '.partial_data' "true" || return 1
  assert_json_field "T-10: spawn_total = 180" "$output" '.sonnet_spawn_total' "180" || return 1
}

# ============================================================================
# MAIN
# ============================================================================

main() {
  setup

  echo "======================================================================"
  echo "CFP-393 TDD Test Suite — RED Phase"
  echo "Testing: measure-rate-limit-fallback.sh"
  echo "Script:  $TEST_AGGREGATOR"
  echo "Repo:    $REPO_ROOT"
  echo "======================================================================"
  echo ""

  test_t1
  test_t2
  test_t3
  test_t4
  test_t5
  test_t6
  test_t7
  test_t8
  test_t9
  test_t10

  echo ""
  echo "======================================================================"
  echo "Test Results"
  echo "======================================================================"
  echo "Run:    $TESTS_RUN"
  echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
  if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo ""
    return 1
  fi
  echo ""
  echo -e "${GREEN}✓ All tests passed!${NC}"
  return 0
}

main "$@"
