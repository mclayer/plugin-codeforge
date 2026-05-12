#!/usr/bin/env bash
# CFP-408 — test harness for sync-contract-bump.sh
#
# Smoke-tests dry-run mode against 3 fixtures:
#   1) review-verdict-v4 (canonical: codeforge-review, current Active)
#   2) fix-event-v1 (kind:registry — must be rejected: kind:contract only)
#   3) nonexistent-contract (must be rejected: not in MANIFEST.yaml)
#
# Each fixture verifies error / success behavior + dry-run side-effect-free.
#
# Exit 0 = all assertions pass. Exit 1 = any assertion fails.
set -uo pipefail
cd "$(dirname "$0")/.."

SCRIPT="scripts/sync-contract-bump.sh"
PASS_COUNT=0
FAIL_COUNT=0

assert_exit() {
    local label="$1"
    local expected="$2"
    local actual="$3"
    if [ "$expected" -eq "$actual" ]; then
        echo "  PASS: $label (exit=$actual)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "  FAIL: $label (expected exit=$expected, got=$actual)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

assert_contains() {
    local label="$1"
    local needle="$2"
    local haystack="$3"
    if echo "$haystack" | grep -q -- "$needle"; then
        echo "  PASS: $label (contains '$needle')"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "  FAIL: $label (missing '$needle')"
        echo "  --- haystack ---"
        echo "$haystack" | head -20
        echo "  ---"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

echo "=== Test 1: script existence + executable ==="
if [ -x "$SCRIPT" ]; then
    echo "  PASS: $SCRIPT is executable"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "  FAIL: $SCRIPT missing or not executable"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo ""
    echo "Summary: $PASS_COUNT passed, $FAIL_COUNT failed"
    exit 1
fi

echo ""
echo "=== Test 2: usage / missing args ==="
out=$(bash "$SCRIPT" 2>&1) || rc=$?
rc=${rc:-0}
assert_exit "no args returns non-zero" 2 "$rc"
assert_contains "no args prints usage" "Usage" "$out"
unset rc

echo ""
echo "=== Test 3: --help flag ==="
out=$(bash "$SCRIPT" --help 2>&1) || rc=$?
rc=${rc:-0}
assert_exit "--help returns 0" 0 "$rc"
assert_contains "--help mentions contract-name" "contract-name" "$out"
assert_contains "--help mentions --dry-run" "dry-run" "$out"
unset rc

echo ""
echo "=== Test 4: unknown contract rejected ==="
out=$(bash "$SCRIPT" nonexistent-contract 9.9.9 --dry-run 2>&1) || rc=$?
rc=${rc:-0}
assert_exit "unknown contract non-zero" 3 "$rc"
assert_contains "unknown contract error message" "MANIFEST" "$out"
unset rc

echo ""
echo "=== Test 5: invalid version format rejected ==="
out=$(bash "$SCRIPT" review-verdict abc --dry-run 2>&1) || rc=$?
rc=${rc:-0}
assert_exit "invalid version non-zero" 4 "$rc"
assert_contains "invalid version error" "version" "$out"
unset rc

echo ""
echo "=== Test 6: dry-run for review-verdict (existing) ==="
out=$(bash "$SCRIPT" review-verdict 4.2 --dry-run 2>&1) || rc=$?
rc=${rc:-0}
assert_exit "dry-run returns 0" 0 "$rc"
assert_contains "dry-run mentions wrapper sibling" "wrapper sibling" "$out"
assert_contains "dry-run mentions canonical" "canonical" "$out"
assert_contains "dry-run mentions merge order" "merge order" "$out"
assert_contains "dry-run is side-effect-free (no commits)" "DRY-RUN" "$out"
unset rc

echo ""
echo "=== Test 7: dry-run for debate-protocol (kind:registry — must reject) ==="
out=$(bash "$SCRIPT" debate-protocol 1.1 --dry-run 2>&1) || rc=$?
rc=${rc:-0}
assert_exit "kind:registry contract rejected" 3 "$rc"
assert_contains "registry rejection message" "kind:contract" "$out"
unset rc

echo ""
echo "=== Test 8: dry-run idempotent — re-run leaves no trace ==="
before=$(git status --porcelain)
bash "$SCRIPT" review-verdict 4.2 --dry-run >/dev/null 2>&1 || true
after=$(git status --porcelain)
if [ "$before" = "$after" ]; then
    echo "  PASS: dry-run preserves working tree"
    PASS_COUNT=$((PASS_COUNT + 1))
else
    echo "  FAIL: dry-run modified working tree"
    echo "  diff:"
    diff <(echo "$before") <(echo "$after")
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

echo ""
echo "================================================"
echo "Summary: $PASS_COUNT passed, $FAIL_COUNT failed"
echo "================================================"
[ "$FAIL_COUNT" -eq 0 ]
