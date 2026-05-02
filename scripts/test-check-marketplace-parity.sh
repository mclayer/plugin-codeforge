#!/usr/bin/env bash
# CFP-50 test harness for check-marketplace-parity.sh
# Runs 3 fixtures: passing (exit 0) + failing-version-drift (exit 1) + failing-name-missing (exit 1).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/check-marketplace-parity.sh"
FIXTURES="$SCRIPT_DIR/test-fixtures/cfp-50-marketplace-parity"

PASS_COUNT=0
FAIL_COUNT=0

run_case() {
  local name="$1"
  local expected_exit="$2"
  local fixture_dir="$3"
  local actual_exit=0
  CFP50_MARKETPLACE_PATH="$fixture_dir/marketplace.json" \
    bash "$SCRIPT" "$fixture_dir/plugin.json" >/dev/null 2>&1 || actual_exit=$?
  if [[ "$actual_exit" -eq "$expected_exit" ]]; then
    echo "  ✅ $name (exit $actual_exit)"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  ❌ $name (expected $expected_exit, got $actual_exit)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

echo "=== CFP-50 marketplace-parity test cases ==="
run_case "passing"               0 "$FIXTURES/passing"
run_case "failing-version-drift" 1 "$FIXTURES/failing-version-drift"
run_case "failing-name-missing"  1 "$FIXTURES/failing-name-missing"

echo ""
echo "Pass: $PASS_COUNT / Fail: $FAIL_COUNT"
[[ "$FAIL_COUNT" -eq 0 ]] || exit 1
