#!/usr/bin/env bash
# Test runner for check-superpowers-schema-drift.sh
# 3 fixture cases.

set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURES="$SCRIPT_DIR/fixtures/superpowers-schema-drift"
LINT_SCRIPT="$SCRIPT_DIR/check-superpowers-schema-drift.sh"
FAILED=0

# Test 1: SSOT references all snapshot-known skills → pass
if bash "$LINT_SCRIPT" \
    --ssot "$FIXTURES/good_ssot.md" \
    --snapshot "$FIXTURES/good_snapshot.txt" \
    --local-install /nonexistent 2>/dev/null; then
  echo "PASS test 1 — good fixtures accepted"
else
  echo "FAIL test 1 — good fixtures rejected (expected pass)"
  FAILED=$((FAILED+1))
fi

# Test 2: SSOT references skill NOT in snapshot → fail (broken reference)
if ! bash "$LINT_SCRIPT" \
    --ssot "$FIXTURES/bad_ssot_unknown_skill.md" \
    --snapshot "$FIXTURES/good_snapshot.txt" \
    --local-install /nonexistent 2>/dev/null; then
  echo "PASS test 2 — broken reference detected"
else
  echo "FAIL test 2 — broken reference not detected (expected fail)"
  FAILED=$((FAILED+1))
fi

# Test 3: empty snapshot → SSOT references at least one skill → fail
if ! bash "$LINT_SCRIPT" \
    --ssot "$FIXTURES/good_ssot.md" \
    --snapshot "$FIXTURES/empty_snapshot.txt" \
    --local-install /nonexistent 2>/dev/null; then
  echo "PASS test 3 — empty snapshot detected"
else
  echo "FAIL test 3 — empty snapshot not detected (expected fail)"
  FAILED=$((FAILED+1))
fi

if [ "$FAILED" -gt 0 ]; then
  echo ""
  echo "FAILED: $FAILED test(s)"
  exit 1
fi
echo ""
echo "ALL PASS (3/3)"
exit 0
