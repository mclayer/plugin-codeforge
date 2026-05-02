#!/usr/bin/env bash
# CFP-60 detection script test harness
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_BASE="$SCRIPT_DIR/test-fixtures/cfp-60-debut-audit-signals"

run_case() {
  local fixture="$1" expected_exit="$2" label="$3"
  local story_file="$FIXTURE_BASE/$fixture/story.md"
  local change_plan="$FIXTURE_BASE/$fixture/change-plan.md"
  local actual=0
  if bash "$SCRIPT_DIR/check-debut-audit-signals.sh" "$story_file" "$change_plan" "$FIXTURE_BASE/$fixture" >/dev/null 2>&1; then
    actual=0
  else
    actual=$?
  fi
  if [[ "$actual" == "$expected_exit" ]]; then
    echo "  ✅ $label (exit $actual)"
  else
    echo "  ❌ $label — expected exit $expected_exit, got $actual"
    return 1
  fi
}

echo "Running CFP-60 debut-audit signals fixtures..."
run_case "passing" 0 "passing fixture (4 룰 모두 PASS)"
run_case "failing-r1-missing-agent" 1 "R1 FAIL fixture (Story §10 finding 5+ 반복)"
run_case "failing-r2-overload" 1 "R2 FAIL fixture (3 sub + FIX 3)"
run_case "failing-r3-phase-gap" 1 "R3 FAIL fixture (propagate 2 회)"
run_case "failing-r4-responsibility-leak" 1 "R4 FAIL fixture (✅ 0 또는 ≥2 row)"
echo "✅ All CFP-60 fixtures PASS"
