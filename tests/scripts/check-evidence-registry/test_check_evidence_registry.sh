#!/usr/bin/env bash
# test_check_evidence_registry.sh
# CFP-455 Phase 2 — scripts/check-evidence-registry.sh validation tests
# Story §8.6.1 verbatim — 8 coverage scenarios (1 positive + 6 negative + 1 meta-error tier)
# §8.6.2 perf baseline: 27 entries × 6 rules ~ 162 assertion, runtime < 5s (default ubuntu-latest)
#
# Exit codes verified (ADR-060 Amendment 2 §결정 15):
#   0 = PASS (positive)
#   1 = validation FAIL (each negative scenario a-f)
#   2 = META-ERROR (file 부재 / yaml parse fail)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"
LINT="$REPO_ROOT/scripts/check-evidence-registry.sh"
FIXTURES="$SCRIPT_DIR/fixtures"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# Helpers
# ============================================================================

assert_exit_code() {
    local desc="$1"
    local fixture="$2"
    local expected_exit="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    set +e
    bash "$LINT" "$fixture" > /tmp/lint.out 2>&1
    local actual_exit=$?
    set -e

    if [[ "$actual_exit" == "$expected_exit" ]]; then
        echo -e "${GREEN}✓${NC} $desc (exit=$actual_exit)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $desc"
        echo "    Expected exit: $expected_exit"
        echo "    Actual exit:   $actual_exit"
        echo "    Output:"
        sed 's/^/      /' /tmp/lint.out
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_output_contains() {
    local desc="$1"
    local fixture="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    set +e
    bash "$LINT" "$fixture" > /tmp/lint.out 2>&1
    set -e

    if grep -qF "$pattern" /tmp/lint.out; then
        echo -e "${GREEN}✓${NC} $desc (output contains '$pattern')"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $desc"
        echo "    Expected pattern: $pattern"
        echo "    Output:"
        sed 's/^/      /' /tmp/lint.out
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# Scenario 1 — Positive PASS (Story §8.6.1 row 1)
# ============================================================================
test_01_positive_pass() {
    echo ""
    echo "--- Scenario 1: Positive PASS ---"
    assert_exit_code "fixture 01 (positive minimal) exits 0" \
        "$FIXTURES/01-positive-minimal.yaml" 0
    assert_output_contains "fixture 01 outputs PASS message" \
        "$FIXTURES/01-positive-minimal.yaml" "validation PASS"
}

# ============================================================================
# Scenario 2 — Negative: schema_version absent (Story §8.6.1 row 2 / rule (a))
# ============================================================================
test_02_schema_version_absent() {
    echo ""
    echo "--- Scenario 2: schema_version 부재 ---"
    assert_exit_code "fixture 02 (schema_version absent) exits 1" \
        "$FIXTURES/02-negative-schema-version-absent.yaml" 1
    assert_output_contains "fixture 02 reports schema_version violation" \
        "$FIXTURES/02-negative-schema-version-absent.yaml" "schema_version"
}

# ============================================================================
# Scenario 3 — Negative: current_tier absent (Story §8.6.1 row 3 / rule (b))
# ============================================================================
test_03_current_tier_absent() {
    echo ""
    echo "--- Scenario 3: current_tier 부재 ---"
    assert_exit_code "fixture 03 (current_tier absent) exits 1" \
        "$FIXTURES/03-negative-current-tier-absent.yaml" 1
    assert_output_contains "fixture 03 reports missing current_tier" \
        "$FIXTURES/03-negative-current-tier-absent.yaml" "current_tier"
    assert_output_contains "fixture 03 references entry name 'test-no-tier'" \
        "$FIXTURES/03-negative-current-tier-absent.yaml" "test-no-tier"
}

# ============================================================================
# Scenario 4 — Negative: enum violation (Story §8.6.1 row 4 / rule (c))
# ============================================================================
test_04_enum_violation() {
    echo ""
    echo "--- Scenario 4: current_tier enum 위반 ---"
    assert_exit_code "fixture 04 (enum 'hard_block' rejected) exits 1" \
        "$FIXTURES/04-negative-enum-violation.yaml" 1
    assert_output_contains "fixture 04 reports 'hard_block' not in enum" \
        "$FIXTURES/04-negative-enum-violation.yaml" "hard_block"
    assert_output_contains "fixture 04 lists valid enum values" \
        "$FIXTURES/04-negative-enum-violation.yaml" "warning"
}

# ============================================================================
# Scenario 5 — Negative: bypass pair violation (Story §8.6.1 row 5 / rule (d))
# ============================================================================
test_05_bypass_pair_violation() {
    echo ""
    echo "--- Scenario 5: bypass_label↔bypass_audit_lint pair 위반 ---"
    assert_exit_code "fixture 05 (bypass_label without bypass_audit_lint) exits 1" \
        "$FIXTURES/05-negative-bypass-pair.yaml" 1
    assert_output_contains "fixture 05 reports bypass_audit_lint missing" \
        "$FIXTURES/05-negative-bypass-pair.yaml" "bypass_audit_lint"
}

# ============================================================================
# Scenario 6 — Negative: name duplicate (Story §8.6.1 row 6 / rule (e))
# ============================================================================
test_06_name_duplicate() {
    echo ""
    echo "--- Scenario 6: entry name 중복 ---"
    assert_exit_code "fixture 06 (duplicate name) exits 1" \
        "$FIXTURES/06-negative-name-duplicate.yaml" 1
    assert_output_contains "fixture 06 reports duplicate" \
        "$FIXTURES/06-negative-name-duplicate.yaml" "duplicate"
    assert_output_contains "fixture 06 references duplicated name" \
        "$FIXTURES/06-negative-name-duplicate.yaml" "adr-sunset-criteria"
}

# ============================================================================
# Scenario 7 — Negative: owner_adr file not found (Story §8.6.1 row 7 / rule (f))
# ============================================================================
test_07_owner_adr_missing() {
    echo ""
    echo "--- Scenario 7: owner_adr ADR file 부재 ---"
    assert_exit_code "fixture 07 (owner_adr ADR-999 not found) exits 1" \
        "$FIXTURES/07-negative-owner-adr-missing.yaml" 1
    assert_output_contains "fixture 07 reports ADR-999 not found" \
        "$FIXTURES/07-negative-owner-adr-missing.yaml" "ADR-999"
    assert_output_contains "fixture 07 references owner_adr field" \
        "$FIXTURES/07-negative-owner-adr-missing.yaml" "owner_adr"
}

# ============================================================================
# Scenario 8 — META-ERROR exit code 2 (Story §8.6.1 row 8 / §결정 15)
# ============================================================================
test_08_meta_error_file_absent() {
    echo ""
    echo "--- Scenario 8a: META-ERROR — registry yaml file 부재 ---"
    assert_exit_code "non-existent file path exits 2 (META-ERROR)" \
        "$FIXTURES/this-file-does-not-exist-CFP455.yaml" 2
    assert_output_contains "non-existent file outputs META-ERROR header" \
        "$FIXTURES/this-file-does-not-exist-CFP455.yaml" "META-ERROR"
}

test_08_meta_error_yaml_parse_fail() {
    echo ""
    echo "--- Scenario 8b: META-ERROR — yaml parse failure ---"
    assert_exit_code "fixture 08 (malformed yaml) exits 2 (META-ERROR)" \
        "$FIXTURES/08-meta-error-yaml-parse-fail.yaml" 2
    assert_output_contains "malformed yaml outputs META-ERROR" \
        "$FIXTURES/08-meta-error-yaml-parse-fail.yaml" "META-ERROR"
}

# ============================================================================
# Scenario 9 — Production registry self-validation (Story §8.6.2 perf baseline)
# ============================================================================
test_09_production_registry_pass() {
    echo ""
    echo "--- Scenario 9: Production registry self-validation ---"
    assert_exit_code "production registry yaml exits 0 (self-application PASS)" \
        "$REPO_ROOT/docs/evidence-checks-registry.yaml" 0
    assert_output_contains "production registry reports entries validated" \
        "$REPO_ROOT/docs/evidence-checks-registry.yaml" "entries validated"
}

# ============================================================================
# Scenario 10 — Perf baseline measurement (§8.6.2, < 5s on 27+ entries)
# ============================================================================
test_10_perf_baseline() {
    echo ""
    echo "--- Scenario 10: Perf baseline (< 5s, §8.6.2) ---"
    TESTS_RUN=$((TESTS_RUN + 1))

    local start_ns end_ns elapsed_ms
    start_ns=$(date +%s%N)
    bash "$LINT" "$REPO_ROOT/docs/evidence-checks-registry.yaml" > /dev/null 2>&1
    end_ns=$(date +%s%N)
    elapsed_ms=$(( (end_ns - start_ns) / 1000000 ))

    if [[ "$elapsed_ms" -lt 5000 ]]; then
        echo -e "${GREEN}✓${NC} perf baseline: ${elapsed_ms}ms < 5000ms threshold"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo "$elapsed_ms" > /tmp/cfp455-perf-baseline.txt
    else
        echo -e "${RED}✗${NC} perf baseline EXCEEDED: ${elapsed_ms}ms >= 5000ms threshold"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    if [[ ! -f "$LINT" ]]; then
        echo -e "${RED}ERROR: lint script not found: $LINT${NC}" >&2
        exit 1
    fi

    echo "======================================================================"
    echo "CFP-455 check-evidence-registry.sh Validation Tests (Story §8.6)"
    echo "Script: $LINT"
    echo "Fixtures: $FIXTURES"
    echo "======================================================================"

    test_01_positive_pass
    test_02_schema_version_absent
    test_03_current_tier_absent
    test_04_enum_violation
    test_05_bypass_pair_violation
    test_06_name_duplicate
    test_07_owner_adr_missing
    test_08_meta_error_file_absent
    test_08_meta_error_yaml_parse_fail
    test_09_production_registry_pass
    test_10_perf_baseline

    echo ""
    echo "======================================================================"
    echo "Test Results"
    echo "======================================================================"
    echo "Run:    $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    if [[ "$TESTS_FAILED" -gt 0 ]]; then
        echo -e "${RED}Failed: $TESTS_FAILED${NC}"
        return 1
    else
        echo -e "${GREEN}All tests passed.${NC}"
        if [[ -f /tmp/cfp455-perf-baseline.txt ]]; then
            echo "Perf baseline: $(cat /tmp/cfp455-perf-baseline.txt)ms (production registry)"
        fi
        return 0
    fi
}

main "$@"
