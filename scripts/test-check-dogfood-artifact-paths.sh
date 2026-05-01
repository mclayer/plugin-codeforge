#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_BASE="$SCRIPT_DIR/test-fixtures/cfp-56-dogfood-artifact-paths"

run_case() {
  local fixture_path="$1" expected_exit="$2" label="$3"
  if CFP56_USE_FIND=1 bash "$SCRIPT_DIR/check-dogfood-artifact-paths.sh" "$fixture_path" >/dev/null 2>&1; then
    actual=0
  else
    actual=$?
  fi
  if [[ "$actual" == "$expected_exit" ]]; then
    echo "  ✅ $label"
  else
    echo "  ❌ $label — expected exit $expected_exit, got $actual"
    return 1
  fi
}

echo "Running CFP-56 dogfood-artifact-paths fixtures (CFP56_USE_FIND=1 force-find mode)..."
run_case "$FIXTURE_BASE/passing-no-forbidden-paths" 0 "passing fixture"
run_case "$FIXTURE_BASE/failing-spec" 1 "failing fixture (spec violation)"
run_case "$FIXTURE_BASE/failing-plan" 1 "failing fixture (plan violation)"
echo "✅ All CFP-56 fixtures PASS"
