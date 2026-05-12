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
# Helper: line count assertion (CFP-453)
# ============================================================================
assert_line_count() {
  local description="$1"
  local file="$2"
  local expected="$3"

  TESTS_RUN=$((TESTS_RUN + 1))
  local actual
  if [[ -f "$file" ]]; then
    actual=$(wc -l < "$file" | tr -d ' ')
  else
    actual="FILE_NOT_FOUND"
  fi

  if [[ "$actual" == "$expected" ]]; then
    echo -e "${GREEN}✓${NC} $description"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗${NC} $description"
    echo "    File:     $file"
    echo "    Expected: $expected lines"
    echo "    Actual:   $actual"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# ============================================================================
# T-11: History append idempotency (CFP-453)
#   동일 month (--as-of) 로 2회 호출 → 라인 수 = 1 유지, measured_at 만 갱신
# ============================================================================
test_t11() {
  echo "  Running T-11..."
  local test_wrapper="$TEST_WRAPPER_BASE/t11"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T11.md"
  local history_file="$test_wrapper/history-t11.jsonl"

  cat > "$story" << 'STORY'
---
key: CFP-T11
---
# T-11: History idempotency
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

  # 1회 호출 — file 신규 생성, 1 entry.
  "$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" \
    --history-out "$history_file" >/dev/null 2>&1
  assert_line_count "T-11.a: 1st call line count = 1" "$history_file" "1" || return 1
  local measured_1
  measured_1=$(tail -n 1 "$history_file" | jq -r '.measured_at')

  # 동일 --as-of 재호출 — 라인 수 동일 유지, last entry 의 measured_at 갱신.
  sleep 1   # measured_at = current UTC → 1초 wait 로 timestamp 갱신 가시화.
  "$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" \
    --history-out "$history_file" >/dev/null 2>&1
  assert_line_count "T-11.b: 2nd call same month line count = 1 (idempotent replace)" "$history_file" "1" || return 1

  local measured_2
  measured_2=$(tail -n 1 "$history_file" | jq -r '.measured_at')

  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$measured_1" != "$measured_2" ]]; then
    echo -e "${GREEN}✓${NC} T-11.c: measured_at updated on idempotent replace"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} T-11.c: measured_at unchanged ($measured_1)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi

  # month value 보존 확인.
  local month_val
  month_val=$(tail -n 1 "$history_file" | jq -r '.month')
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$month_val" == "2026-06" ]]; then
    echo -e "${GREEN}✓${NC} T-11.d: month bucket = 2026-06 (window last)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} T-11.d: month bucket mismatch (got: $month_val)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# ============================================================================
# T-12: History file graceful create (CFP-453)
#   --history-out 가 가리키는 file 부재 시 자동 생성 + 1 entry 작성
# ============================================================================
test_t12() {
  echo "  Running T-12..."
  local test_wrapper="$TEST_WRAPPER_BASE/t12"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T12.md"
  # Nested non-existent directory — mkdir -p 까지 verify.
  local history_file="$test_wrapper/nested/sub/dir/history-t12.jsonl"

  cat > "$story" << 'STORY'
---
key: CFP-T12
---
# T-12: Graceful create
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

  # File / parent dir 부재 — graceful create 의무.
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ ! -e "$history_file" ]]; then
    echo -e "${GREEN}✓${NC} T-12.a: pre-condition — history file 부재"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} T-12.a: pre-condition 실패 (file 이미 존재)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi

  "$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" \
    --history-out "$history_file" >/dev/null 2>&1

  assert_line_count "T-12.b: history file created with 1 entry" "$history_file" "1" || return 1

  # JSON 유효성 + schema 필드 검증.
  local entry
  entry=$(tail -n 1 "$history_file")
  TESTS_RUN=$((TESTS_RUN + 1))
  if echo "$entry" | jq -e '.measured_at and .month and (.sonnet_spawn_total != null) and (.fallback_count != null) and (.sample_size_sufficient != null) and (.partial_data != null) and .gate_status' >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} T-12.c: entry schema 모든 필드 보유 (measured_at, month, spawn, fb, suff, partial, gate)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} T-12.c: entry schema 누락 필드 detect"
    echo "    Entry: $entry"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# ============================================================================
# T-13: Multi-month accumulation (CFP-453)
#   다른 --as-of 로 2회 호출 시 2 entry 누적 (다른 month bucket → append)
# ============================================================================
test_t13() {
  echo "  Running T-13..."
  local test_wrapper="$TEST_WRAPPER_BASE/t13"
  mkdir -p "$test_wrapper/docs/stories"

  local story="$test_wrapper/docs/stories/CFP-T13.md"
  local history_file="$test_wrapper/history-t13.jsonl"

  cat > "$story" << 'STORY'
---
key: CFP-T13
---
# T-13: Multi-month accumulation
## §14. Lane Evidence
STORY

  # 6 months of data — 2 windows (2026-01~03 / 2026-04~06) 둘 다 sufficient.
  for m in "2026-01" "2026-02" "2026-03" "2026-04" "2026-05" "2026-06"; do
    for i in {1..60}; do
      cat >> "$story" << ROW
  - lane: develop
    agent: DeveloperAgent
    spawned_at: ${m}-15T10:00:00Z
    transcript: "Normal"
ROW
    done
  done

  # 1st run — window ending 2026-03 (as-of 2026-04 → window = 2026-01/02/03, last = 2026-03)
  "$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-04" \
    --history-out "$history_file" >/dev/null 2>&1
  assert_line_count "T-13.a: 1st run (as-of 2026-04) line count = 1" "$history_file" "1" || return 1

  # 2nd run — window ending 2026-06 (as-of 2026-07 → window = 2026-04/05/06, last = 2026-06)
  "$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" \
    --history-out "$history_file" >/dev/null 2>&1
  assert_line_count "T-13.b: 2nd run (as-of 2026-07, different month) line count = 2 (append)" "$history_file" "2" || return 1

  # Entry month verify.
  local m1 m2
  m1=$(sed -n '1p' "$history_file" | jq -r '.month')
  m2=$(sed -n '2p' "$history_file" | jq -r '.month')
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$m1" == "2026-03" ]] && [[ "$m2" == "2026-06" ]]; then
    echo -e "${GREEN}✓${NC} T-13.c: entry months in order (2026-03, 2026-06)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}✗${NC} T-13.c: entry months mismatch (got: $m1, $m2)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi

  # 3rd run — 다시 2026-07 (same as 2nd run's month=2026-06) → idempotent replace, 라인 수 보존.
  "$TEST_AGGREGATOR" --wrapper-path "$test_wrapper" --as-of "2026-07" \
    --history-out "$history_file" >/dev/null 2>&1
  assert_line_count "T-13.d: 3rd run same month (idempotent replace) line count = 2" "$history_file" "2" || return 1
}

# ============================================================================
# MAIN
# ============================================================================

main() {
  setup

  echo "======================================================================"
  echo "CFP-393 + CFP-453 TDD Test Suite"
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
  # CFP-453 — history.jsonl tests
  test_t11
  test_t12
  test_t13

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
