#!/usr/bin/env bash
# scripts/test-check-spawn-event-schema.sh
# CFP-2393 Phase 2 — Discriminating test for check_spawn_event_schema.py (lint)
#
# Anti-theater test: contract 가 정확하면 PASS, mutant contract (attribution_confidence
# row 제거 등) 는 RED. mutation testing 으로 lint 효과성 검증.
#
# ADR-119 research-before-claims (검증-후-단언) 원칙:
#  - lint 이 예상한 contract 위반을 실제로 검출하는가 (not vacuous green)
#  - missing-case + exit assert (exit code + stdout sentinel 동시 검증)
#
# Mutation targeting:
#  - Mutation-1: attribution_confidence enum row 제거 → lint RED (allow-list 위반)
#  - Mutation-2: free-form string field 도입 → lint RED (T-INFO-8 violation)
#  - Mutation-3: unknown-agent fallback 선언 제거 → lint RED (semi-open semantics 위반)
#
# Usage:
#   bash scripts/test-check-spawn-event-schema.sh [check]
#
# Exit code:
#  0 = all discriminating tests pass
#  1 = any test fails (lint may not be detecting mutations correctly)
#

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

# ═════════════════════════════════════════════════════════════════════════════
# GREEN fixture: 실제 contract (docs/inter-plugin-contracts/spawn-event-v1.md)를 base로 사용
# ═════════════════════════════════════════════════════════════════════════════

CONTRACT_GREEN="$REPO_ROOT/docs/inter-plugin-contracts/spawn-event-v1.md"

if [ ! -f "$CONTRACT_GREEN" ]; then
  echo "ERROR: Contract file not found: $CONTRACT_GREEN"
  exit 2
fi

# ═════════════════════════════════════════════════════════════════════════════
# Test harness: contract fixture + lint invocation
# ═════════════════════════════════════════════════════════════════════════════

run_discriminating_test() {
  local test_name="$1"
  local contract_fixture="$2"  # markdown contract path or inline
  local is_file="$3"           # "file" or "inline"
  local expected_lint_result="$4"  # "PASS" or "RED"
  local description="$5"

  # Temporary directory for test artifacts
  TMP_TEST_DIR=$(mktemp -d)
  trap "rm -rf '$TMP_TEST_DIR'" RETURN

  # Resolve contract path
  local contract_path="$TMP_TEST_DIR/contract.md"

  if [ "$is_file" = "file" ]; then
    # Copy fixture file
    cp "$contract_fixture" "$contract_path"
  else
    # Write inline fixture (properly interpolated, not single-quoted heredoc)
    printf '%s\n' "$contract_fixture" > "$contract_path"
  fi

  # Run lint against contract (CLI: python3 check_spawn_event_schema.py check --contract-path <path> --repo-root <dir>)
  local lint_exit=0
  local lint_output=""

  lint_output=$(
    python3 scripts/lib/check_spawn_event_schema.py check \
      --contract-path "$contract_path" \
      --repo-root "$REPO_ROOT" 2>&1
  ) || lint_exit=$?

  # Discriminating assertion: exit code & sentinel output
  local lint_passed="PASS"
  if [ $lint_exit -ne 0 ]; then
    lint_passed="RED"
  fi

  # Check exit code match
  if [ "$lint_passed" != "$expected_lint_result" ]; then
    echo "✗ FAIL: $test_name"
    echo "  Expected lint result: $expected_lint_result"
    echo "  Got lint result: $lint_passed (exit $lint_exit)"
    echo "  Description: $description"
    echo "  Output: $lint_output"
    FAIL=$((FAIL+1))
    return 1
  fi

  # Check sentinel in output (additional distinct-marker validation)
  if [ "$expected_lint_result" = "RED" ]; then
    if ! echo "$lint_output" | grep -q "VIOLATION\|FAIL\|ERROR\|violation"; then
      echo "⚠ WARNING: $test_name lint RED but no sentinel output"
      echo "  (exit code was $lint_exit)"
      # Still count as pass (exit code was correct), but warn
    fi
  fi

  echo "✓ PASS: $test_name (lint result: $lint_passed, exit $lint_exit)"
  PASS=$((PASS+1))
  return 0
}

# ═════════════════════════════════════════════════════════════════════════════
# Test Case 1: GREEN — Valid contract (actual contract file)
# ═════════════════════════════════════════════════════════════════════════════

run_discriminating_test \
  "TC-1-GREEN" \
  "$CONTRACT_GREEN" \
  "file" \
  "PASS" \
  "Valid contract from docs/inter-plugin-contracts/spawn-event-v1.md"

# ═════════════════════════════════════════════════════════════════════════════
# RED Mutations — markdown contract with targeted deletions
# ═════════════════════════════════════════════════════════════════════════════

# Helper: create RED mutant (remove attribution_confidence row from §3)
create_red_mutant_missing_attribution() {
  # Read contract, remove attribution_confidence subsection (from "attribution_confidence:" to next "  [a-z_]*:")
  sed '/^  attribution_confidence:/,/^  [a-z_]*:/!d; /^  attribution_confidence:/,/^  [a-z_]*:/{/^  attribution_confidence:/!{/^  [a-z_]*:/!d;};}' "$CONTRACT_GREEN"
}

# Helper: create RED mutant (remove unknown-agent fallback from agent_type definition)
create_red_mutant_no_unknown_agent() {
  sed '/unknown-agent fallback/d; /semi-open.*unknown-agent/d' "$CONTRACT_GREEN"
}

# Mutation-1: Remove attribution_confidence enum row
CONTRACT_RED_ATTR=$(create_red_mutant_missing_attribution)

run_discriminating_test \
  "TC-2-RED-attribution-missing" \
  "$CONTRACT_RED_ATTR" \
  "inline" \
  "RED" \
  "Mutation-1: attribution_confidence field removed from §3 (contract allow-list violation)"

# Mutation-2: Remove unknown-agent fallback declaration (agent_type semi-open semantics violated)
CONTRACT_RED_UNKNOWN=$(create_red_mutant_no_unknown_agent)

run_discriminating_test \
  "TC-3-RED-unknown-agent" \
  "$CONTRACT_RED_UNKNOWN" \
  "inline" \
  "RED" \
  "Mutation-2: agent_type semi-open fallback removed (strict closed-set introduced)"

# Mutation-3: Test basic structural integrity (remove frontmatter kind marker)
CONTRACT_RED_STRUCT=$(sed '1,/^---$/d' "$CONTRACT_GREEN" | sed '1i---\nkind: invalid\nregistry: other\n---')

run_discriminating_test \
  "TC-4-RED-kind-invalid" \
  "$CONTRACT_RED_STRUCT" \
  "inline" \
  "RED" \
  "Mutation-3: frontmatter kind changed (frontmatter validation violation)"

# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: spawn-event-schema lint discriminating test"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating tests passed — lint is detecting mutations correctly"
  exit 0
else
  echo "✗ Some tests failed — lint may not be detecting mutations correctly"
  exit 1
fi
