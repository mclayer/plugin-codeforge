#!/usr/bin/env bash
# test_aggregator.sh - TDD RED tests for measure-rate-limit-fallback.sh
# CFP-393 Phase 2

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"  # Up to plugin-codeforge root (original checkout, not worktree)

# But we're in a worktree, so the actual repo is plugin-codeforge itself
# Let's use git to find it
cd "$SCRIPT_DIR"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "/c/Users/mccho/.claude/worktrees/plugin-codeforge/cfp-393-phase2-aggregator-workflow")

TEST_AGGREGATOR="$REPO_ROOT/scripts/measure-rate-limit-fallback.sh"
FIXTURE_DIR="$SCRIPT_DIR/fixtures"

# Verify aggregator exists
if [[ ! -f "$TEST_AGGREGATOR" ]]; then
  echo "ERROR: aggregator script not found at $TEST_AGGREGATOR" >&2
  exit 1
fi

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
  mkdir -p "$FIXTURE_DIR"
  mkdir -p "$REPO_ROOT/docs/stories"
}

cleanup() {
  find /tmp -maxdepth 1 -type d -name "cfp393-test-*" -exec rm -rf {} + 2>/dev/null || true
}

trap cleanup EXIT

# ============================================================================
# T-1: Normal case — 60 Sonnet rows, 0 fallback, rate=0%
# ============================================================================
test_t1() {
  echo "  Running T-1..."
  local story="$FIXTURE_DIR/CFP-T1.md"

  cat > "$story" << 'STORY'
---
key: CFP-T1
---
# T-1: Normal case (60 Sonnet, no fallback)
## §14. Lane Evidence
STORY

  for i in {1..60}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent (codeforge-develop@mclayer)
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal operation, no fallback"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)

  assert_json_field "T-1: spawn_total = 60" "$output" '.sonnet_spawn_total' "60"
  assert_json_field "T-1: fallback_count = 0" "$output" '.fallback_count' "0"
  assert_json_field "T-1: rate_percent = 0" "$output" '.fallback_rate_percent' "0"
  assert_json_field "T-1: sample_sufficient = true" "$output" '.sample_size_sufficient' "true"
  assert_json_field "T-1: gate = on_track" "$output" '.gate_status' "on_track"
}

# ============================================================================
# T-2: Monthly AND sample check — 30/40/50 across 3 months
# ============================================================================
test_t2() {
  echo "  Running T-2..."
  local story="$FIXTURE_DIR/CFP-T2.md"

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
    transcript: "Month 1"
ROW
  done

  for i in {1..40}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Month 2"
ROW
  done

  for i in {1..50}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-06-15T10:00:00Z
    transcript: "Month 3"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-07" 2>/dev/null)

  assert_json_field "T-2: sample_sufficient = false" "$output" '.sample_size_sufficient' "false"
  assert_json_field "T-2: gate = sample_insufficient" "$output" '.gate_status' "sample_insufficient"
}

# ============================================================================
# T-3: Threshold violation — 100 spawn, 2 fallback (2%)
# ============================================================================
test_t3() {
  echo "  Running T-3..."
  local story="$FIXTURE_DIR/CFP-T3.md"

  cat > "$story" << 'STORY'
---
key: CFP-T3
---
# T-3: Threshold violated (100 spawn, 2 fallback = 2%)
## §14. Lane Evidence
STORY

  for i in {1..98}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  for i in {1..2}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-16T10:00:00Z
    transcript: "Rate-limit fallback: [rate-limit-fallback:sonnet→opus] detected"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)

  assert_json_field "T-3: fallback_count = 2" "$output" '.fallback_count' "2"
  assert_json_field "T-3: gate = violated" "$output" '.gate_status' "violated"
}

# ============================================================================
# T-4: Boundary case — 1.0% (100 spawn, 1 fallback)
# Chief decision: >= 1.0 is violation
# ============================================================================
test_t4() {
  echo "  Running T-4..."
  local story="$FIXTURE_DIR/CFP-T4.md"

  cat > "$story" << 'STORY'
---
key: CFP-T4
---
# T-4: Boundary (100 spawn, 1 fallback = 1.0%)
## §14. Lane Evidence
STORY

  for i in {1..99}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-16T10:00:00Z
    transcript: "[rate-limit-fallback:sonnet→opus] Fallback occurred"
ROW

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)

  assert_json_field "T-4: gate = violated (1.0%)" "$output" '.gate_status' "violated"
}

# ============================================================================
# T-5: Agent name substring match
# ============================================================================
test_t5() {
  echo "  Running T-5..."
  local story="$FIXTURE_DIR/CFP-T5.md"

  cat > "$story" << 'STORY'
---
key: CFP-T5
---
# T-5: Agent with namespace
## §14. Lane Evidence
STORY

  for i in {1..50}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent (codeforge-develop@mclayer)
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Namespaced agent"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)

  assert_json_field "T-5: spawn_total = 50" "$output" '.sonnet_spawn_total' "50"
}

# ============================================================================
# T-6: Graceful skip of malformed rows
# ============================================================================
test_t6() {
  echo "  Running T-6..."
  local story="$FIXTURE_DIR/CFP-T6.md"

  cat > "$story" << 'STORY'
---
key: CFP-T6
---
# T-6: Malformed rows
## §14. Lane Evidence
STORY

  for i in {1..30}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-16T10:00:00Z
ROW

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)

  assert_json_field "T-6: spawn_total = 30" "$output" '.sonnet_spawn_total' "30"
  assert_json_field "T-6: partial_data = true" "$output" '.partial_data' "true"
}

# ============================================================================
# T-7: Zero stories (division by zero)
# ============================================================================
test_t7() {
  echo "  Running T-7..."
  local temp_wrapper
  temp_wrapper=$(mktemp -d)
  mkdir -p "$temp_wrapper/docs/stories"

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$temp_wrapper" --as-of "2026-06" 2>/dev/null)

  rm -rf "$temp_wrapper"

  assert_json_field "T-7: spawn_total = 0" "$output" '.sonnet_spawn_total' "0"
  assert_json_field "T-7: gate = sample_insufficient" "$output" '.gate_status' "sample_insufficient"
}

# ============================================================================
# T-8: Unicode and ASCII arrows
# ============================================================================
test_t8() {
  echo "  Running T-8..."
  local story="$FIXTURE_DIR/CFP-T8.md"

  cat > "$story" << 'STORY'
---
key: CFP-T8
---
# T-8: Unicode and ASCII arrows
## §14. Lane Evidence
STORY

  for i in {1..50}; do
    cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Normal"
ROW
  done

  cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-16T10:00:00Z
    transcript: "[rate-limit-fallback:sonnet→opus] Unicode arrow"
ROW

  cat >> "$story" << 'ROW'
  - lane: develop
    agent: DeveloperAgent
    spawned_at: 2026-05-17T10:00:00Z
    transcript: "[rate-limit-fallback:sonnet->opus] ASCII arrow"
ROW

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)

  assert_json_field "T-8: fallback_count = 2" "$output" '.fallback_count' "2"
}

# ============================================================================
# T-9: Idempotency
# ============================================================================
test_t9() {
  echo "  Running T-9..."
  local story="$FIXTURE_DIR/CFP-T9.md"

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
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Idempotent input"
ROW
  done

  local output1 output2 norm1 norm2
  output1=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)
  output2=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)

  norm1=$(echo "$output1" | jq 'del(.measured_at, .last_updated)')
  norm2=$(echo "$output2" | jq 'del(.measured_at, .last_updated)')

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$norm1" == "$norm2" ]]; then
    echo -e "${GREEN}✓${NC} T-9: idempotent (excluding timestamps)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} T-9: idempotent check failed"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# ============================================================================
# T-10: Wrapper-only mode
# ============================================================================
test_t10() {
  echo "  Running T-10..."
  local story="$FIXTURE_DIR/CFP-T10.md"

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
    spawned_at: 2026-05-15T10:00:00Z
    transcript: "Wrapper-only"
ROW
  done

  local output
  output=$("$TEST_AGGREGATOR" --wrapper-path "$REPO_ROOT" --as-of "2026-06" 2>/dev/null)

  assert_json_field "T-10: partial_data = true" "$output" '.partial_data' "true"
  assert_json_field "T-10: spawn_total = 60" "$output" '.sonnet_spawn_total' "60"
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
