#!/usr/bin/env bash
# Test runner for check-superpowers-integration.sh
# Asserts lint behavior on 4 fixture cases.

set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES="$SCRIPT_DIR/fixtures/superpowers-integration"
LINT_SCRIPT="$SCRIPT_DIR/check-superpowers-integration.sh"
FAILED=0

# Test 1: good fixtures pass
if OUTPUT=$("$LINT_SCRIPT" \
    --ssot "$FIXTURES/good_ssot.md" \
    --agent-glob "$FIXTURES/good_agent.md" \
    --helpers-dir "$FIXTURES/helpers_empty" 2>&1); then
  echo "PASS test 1 — good fixtures accepted"
else
  echo "FAIL test 1 — good fixtures rejected (expected pass)"
  echo "  --- lint output ---"
  echo "$OUTPUT" | sed 's/^/  /'
  echo "  --- end lint output ---"
  FAILED=$((FAILED+1))
fi

# Test 2: bad_stale_path detected
if ! "$LINT_SCRIPT" \
    --ssot "$FIXTURES/good_ssot.md" \
    --agent-glob "$FIXTURES/bad_stale_path.md" \
    --helpers-dir "$FIXTURES/helpers_empty" 2>/dev/null; then
  echo "PASS test 2 — stale path detected"
else
  echo "FAIL test 2 — stale path not detected (expected fail)"
  FAILED=$((FAILED+1))
fi

# Test 3: bad_ssot_drift detected
if ! "$LINT_SCRIPT" \
    --ssot "$FIXTURES/bad_ssot_drift.md" \
    --agent-glob "$FIXTURES/good_agent.md" \
    --helpers-dir "$FIXTURES/helpers_empty" 2>/dev/null; then
  echo "PASS test 3 — SSOT drift detected"
else
  echo "FAIL test 3 — SSOT drift not detected (expected fail)"
  FAILED=$((FAILED+1))
fi

# Test 4: bad_inline_copy detected
if ! "$LINT_SCRIPT" \
    --ssot "$FIXTURES/good_ssot.md" \
    --agent-glob "$FIXTURES/bad_inline_copy.md" \
    --helpers-dir "$FIXTURES/fixtures_helpers" 2>/dev/null; then
  echo "PASS test 4 — inline copy detected"
else
  echo "FAIL test 4 — inline copy not detected (expected fail)"
  FAILED=$((FAILED+1))
fi

if [ "$FAILED" -gt 0 ]; then
  echo ""
  echo "FAILED: $FAILED test(s)"
  exit 1
fi
echo ""
echo "ALL PASS (4/4)"
exit 0
