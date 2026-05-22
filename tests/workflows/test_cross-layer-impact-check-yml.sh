#!/usr/bin/env bash
# test_cross-layer-impact-check-yml.sh
# CFP-1241 — cross-layer-impact-check.yml pipefail guard (|| true)
# set -euo pipefail + grep 0-match (exit 1) → command-substitution abort
# 비-schema/code PR 마다 advisory step FAILURE
# TDD RED: 4 TOUCHED_* grep|wc 파이프에 || true 추가 전 FAIL
# TDD GREEN: 추가 후 PASS

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"

TEMPLATES_WORKFLOW="$REPO_ROOT/templates/github-workflows/cross-layer-impact-check.yml"
SELF_APP_WORKFLOW="$REPO_ROOT/.github/workflows/cross-layer-impact-check.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# Helper functions
# ============================================================================

assert_exit_code() {
    local desc="$1"
    local expected_code="$2"
    local script="$3"

    TESTS_RUN=$((TESTS_RUN + 1))

    set +e
    bash -c "$script"
    actual_code=$?
    set -e

    if [[ $actual_code -eq $expected_code ]]; then
        echo -e "${GREEN}PASS${NC} $desc (exit code: $actual_code)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} $desc (expected: $expected_code, got: $actual_code)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi
}

assert_contains() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qF "$pattern" "$file"; then
        echo -e "${GREEN}PASS${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} $desc"
        echo "    Pattern not found: $pattern"
        echo "    In file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi
}

# ============================================================================
# Test TC-1: grep 0-match with set -euo pipefail must exit 0 (after fix)
# ============================================================================
# This test MUST FAIL before the fix and PASS after.

test_tc1_pipefail_zero_match_exit_code() {
    echo ""
    echo "=== TC-1: Regression guard — set -euo pipefail + grep 0-match must exit 0 ==="

    # Extract the 4 TOUCHED_* assignment lines from the actual workflow file
    local extracted_lines
    extracted_lines=$(grep -E '^\s+TOUCHED_(SCHEMA|CODE|FRONTEND|BACKEND)=\$\(echo' "$TEMPLATES_WORKFLOW" | sed 's/^[[:space:]]*//')

    # Verify extraction succeeded (4 lines expected)
    local line_count
    line_count=$(echo "$extracted_lines" | wc -l)
    if [[ $line_count -ne 4 ]]; then
        echo -e "${RED}FAIL${NC} TC-1: Could not extract 4 TOUCHED_* lines (got $line_count)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi

    # Build the test script dynamically: preamble + extracted lines + assertions
    local test_script
    test_script=$(cat <<'TESTEOF'
set -euo pipefail

# Test with non-matching paths (the regression case)
CHANGED_FILES=$(printf 'docs/foo.md\nCLAUDE.md\ndocs/adr/ADR-106.md')
GITHUB_OUTPUT=$(mktemp)

# Extracted assignments from actual workflow (dynamically interpolated):
TESTEOF
)

    # Append the extracted lines verbatim
    test_script+=$'\n'"$extracted_lines"$'\n'

    # Append assertions
    test_script+=$(cat <<'TESTEOF'

# Verify all counts are 0 (only true after || true fix applied)
[[ "$TOUCHED_SCHEMA" == "0" ]] || { echo "TOUCHED_SCHEMA=$TOUCHED_SCHEMA"; exit 1; }
[[ "$TOUCHED_CODE" == "0" ]] || { echo "TOUCHED_CODE=$TOUCHED_CODE"; exit 1; }
[[ "$TOUCHED_FRONTEND" == "0" ]] || { echo "TOUCHED_FRONTEND=$TOUCHED_FRONTEND"; exit 1; }
[[ "$TOUCHED_BACKEND" == "0" ]] || { echo "TOUCHED_BACKEND=$TOUCHED_BACKEND"; exit 1; }

exit 0
TESTEOF
)

    assert_exit_code "TC-1: Zero-match grep should exit 0 (regression guard)" 0 "$test_script"
}

# ============================================================================
# Test TC-2: Positive case — grep with matches must capture counts correctly
# ============================================================================

test_tc2_positive_case_with_matches() {
    echo ""
    echo "=== TC-2: Positive case — grep with matches captures correct counts ==="

    # Extract the 4 TOUCHED_* assignment lines from the actual workflow file
    local extracted_lines
    extracted_lines=$(grep -E '^\s+TOUCHED_(SCHEMA|CODE|FRONTEND|BACKEND)=\$\(echo' "$TEMPLATES_WORKFLOW" | sed 's/^[[:space:]]*//')

    # Verify extraction succeeded (4 lines expected)
    local line_count
    line_count=$(echo "$extracted_lines" | wc -l)
    if [[ $line_count -ne 4 ]]; then
        echo -e "${RED}FAIL${NC} TC-2: Could not extract 4 TOUCHED_* lines (got $line_count)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi

    # Build the test script dynamically: preamble + extracted lines + assertions
    local test_script
    test_script=$(cat <<'TESTEOF'
set -euo pipefail

# Test with matching paths
CHANGED_FILES=$(printf 'migrations/001_add_users.sql\nsrc/app.py\nfrontend/index.html\nCLAUDE.md')
GITHUB_OUTPUT=$(mktemp)

# Extracted assignments from actual workflow (dynamically interpolated):
TESTEOF
)

    # Append the extracted lines verbatim
    test_script+=$'\n'"$extracted_lines"$'\n'

    # Append assertions
    test_script+=$(cat <<'TESTEOF'

# Verify counts match expected values
[[ "$TOUCHED_SCHEMA" == "1" ]] || { echo "TOUCHED_SCHEMA=$TOUCHED_SCHEMA, expected 1"; exit 1; }
[[ "$TOUCHED_CODE" == "1" ]] || { echo "TOUCHED_CODE=$TOUCHED_CODE, expected 1"; exit 1; }
[[ "$TOUCHED_FRONTEND" == "1" ]] || { echo "TOUCHED_FRONTEND=$TOUCHED_FRONTEND, expected 1"; exit 1; }
[[ "$TOUCHED_BACKEND" == "0" ]] || { echo "TOUCHED_BACKEND=$TOUCHED_BACKEND, expected 0"; exit 1; }

exit 0
TESTEOF
)

    assert_exit_code "TC-2: Positive case with matches exits 0 and captures correct counts" 0 "$test_script"
}

# ============================================================================
# Test TC-3: ADR-005 parity — template and .github/ self-app must be byte-identical
# ============================================================================

test_tc3_adr005_parity() {
    echo ""
    echo "=== TC-3: ADR-005 parity — template and .github/ self-app byte-identical ==="

    TESTS_RUN=$((TESTS_RUN + 1))

    if diff -q "$TEMPLATES_WORKFLOW" "$SELF_APP_WORKFLOW" > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC} TC-3: template and .github/ files are byte-identical"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} TC-3: template and .github/ files differ"
        echo "    Template: $TEMPLATES_WORKFLOW"
        echo "    Self-app: $SELF_APP_WORKFLOW"
        diff "$TEMPLATES_WORKFLOW" "$SELF_APP_WORKFLOW" || true
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi
}

# ============================================================================
# Structural checks: verify || true is present on all 4 lines (after fix)
# ============================================================================

test_pipeline_guard_present() {
    echo ""
    echo "=== Structural: || true guard present on all 4 TOUCHED_* lines ==="

    assert_contains "TOUCHED_SCHEMA has || true guard" "$TEMPLATES_WORKFLOW" "TOUCHED_SCHEMA=\$(echo \"\${CHANGED_FILES}\" | grep -E \"^(migrations|schema)/\" | wc -l || true)"
    assert_contains "TOUCHED_CODE has || true guard" "$TEMPLATES_WORKFLOW" "TOUCHED_CODE=\$(echo \"\${CHANGED_FILES}\" | grep -E \"^src/\" | wc -l || true)"
    assert_contains "TOUCHED_FRONTEND has || true guard" "$TEMPLATES_WORKFLOW" "TOUCHED_FRONTEND=\$(echo \"\${CHANGED_FILES}\" | grep -E \"^(frontend|web|ui)/\" | wc -l || true)"
    assert_contains "TOUCHED_BACKEND has || true guard" "$TEMPLATES_WORKFLOW" "TOUCHED_BACKEND=\$(echo \"\${CHANGED_FILES}\" | grep -E \"^(backend|api|server)/\" | wc -l || true)"
}

# ============================================================================
# Main test runner
# ============================================================================

main() {
    echo "=========================================="
    echo "CFP-1241 cross-layer-impact-check.yml tests"
    echo "=========================================="

    echo ""
    echo "[Files under test]"
    echo "  Template: $TEMPLATES_WORKFLOW"
    echo "  Self-app: $SELF_APP_WORKFLOW"

    # Run tests in order
    test_tc1_pipefail_zero_match_exit_code || true
    test_tc2_positive_case_with_matches || true
    test_tc3_adr005_parity || true
    test_pipeline_guard_present || true

    # Summary
    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="
    echo "Tests run: $TESTS_RUN"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
        exit 1
    else
        echo "Failed: $TESTS_FAILED"
        exit 0
    fi
}

main
