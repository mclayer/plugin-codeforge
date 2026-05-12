#!/usr/bin/env bash
# test_evidence-registry-check-yml.sh
# CFP-455 Phase 2 — Workflow YAML validation tests
# Verifies templates/github-workflows/evidence-registry-check.yml + .github/workflows/ self-app copy
# (ADR-029 self-app pattern verbatim — CFP-393 prior art 정합)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"

TEMPLATES_WORKFLOW="$REPO_ROOT/templates/github-workflows/evidence-registry-check.yml"
SELF_APP_WORKFLOW="$REPO_ROOT/.github/workflows/evidence-registry-check.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_contains() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qF "$pattern" "$file"; then
        echo -e "${GREEN}✓${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $desc"
        echo "    Pattern not found: $pattern"
        echo "    In file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_yaml_valid() {
    local desc="$1"
    local file="$2"

    TESTS_RUN=$((TESTS_RUN + 1))
    if python3 -c "import yaml; yaml.safe_load(open('$file', encoding='utf-8').read())" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $desc"
        echo "    YAML parse failed: $file"
        python3 -c "import yaml; yaml.safe_load(open('$file', encoding='utf-8').read())" 2>&1 | sed 's/^/      /'
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_files_identical() {
    local desc="$1"
    local file_a="$2"
    local file_b="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if diff -q "$file_a" "$file_b" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $desc"
        echo "    Files differ:"
        diff "$file_a" "$file_b" | sed 's/^/      /' | head -20
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# Test: Templates file exists + valid YAML
# ============================================================================
test_templates_yaml_valid() {
    echo ""
    echo "--- Templates workflow YAML validity ---"
    if [[ ! -f "$TEMPLATES_WORKFLOW" ]]; then
        echo -e "${RED}ERROR: templates workflow file not found: $TEMPLATES_WORKFLOW${NC}" >&2
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TESTS_RUN=$((TESTS_RUN + 1))
        return 1
    fi
    assert_yaml_valid "templates/github-workflows/evidence-registry-check.yml parses as valid YAML" \
        "$TEMPLATES_WORKFLOW"
}

# ============================================================================
# Test: Self-app file exists + valid YAML + identical to templates
# ============================================================================
test_self_app_yaml_valid() {
    echo ""
    echo "--- Self-app workflow YAML validity (ADR-029) ---"
    if [[ ! -f "$SELF_APP_WORKFLOW" ]]; then
        echo -e "${RED}ERROR: self-app workflow file not found: $SELF_APP_WORKFLOW${NC}" >&2
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TESTS_RUN=$((TESTS_RUN + 1))
        return 1
    fi
    assert_yaml_valid ".github/workflows/evidence-registry-check.yml parses as valid YAML" \
        "$SELF_APP_WORKFLOW"
    assert_files_identical "templates and self-app workflow files are byte-identical (ADR-029)" \
        "$TEMPLATES_WORKFLOW" "$SELF_APP_WORKFLOW"
}

# ============================================================================
# Test: Trigger paths defined correctly
# ============================================================================
test_trigger_paths() {
    echo ""
    echo "--- Trigger configuration ---"
    assert_contains "pull_request trigger defined" \
        "$TEMPLATES_WORKFLOW" "pull_request:"
    assert_contains "path filter for registry yaml" \
        "$TEMPLATES_WORKFLOW" "docs/evidence-checks-registry.yaml"
    assert_contains "path filter for schema doc" \
        "$TEMPLATES_WORKFLOW" "docs/inter-plugin-contracts/evidence-check-registry-v1.md"
}

# ============================================================================
# Test: Warning mode (continue-on-error: true) — §결정 5
# ============================================================================
test_warning_mode() {
    echo ""
    echo "--- Warning mode (ADR-060 §결정 5) ---"
    assert_contains "continue-on-error: true (warning mode)" \
        "$TEMPLATES_WORKFLOW" "continue-on-error: true"
}

# ============================================================================
# Test: bypass_label omit (warning tier — §결정 16)
# ============================================================================
test_bypass_label_omit() {
    echo ""
    echo "--- bypass_label omit (ADR-060 Amendment 2 §결정 16) ---"
    TESTS_RUN=$((TESTS_RUN + 1))
    # Workflow should NOT define hotfix-bypass label check step (omit per §결정 16)
    if grep -qE 'hotfix-bypass:evidence-registry' "$TEMPLATES_WORKFLOW"; then
        echo -e "${RED}✗${NC} Workflow defines bypass label but §결정 16 says warning tier = bypass_label omit"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    else
        echo -e "${GREEN}✓${NC} Workflow correctly omits bypass label (warning tier per §결정 16)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
}

# ============================================================================
# Test: Required steps present
# ============================================================================
test_required_steps() {
    echo ""
    echo "--- Required workflow steps ---"
    assert_contains "Checkout step present" \
        "$TEMPLATES_WORKFLOW" "uses: actions/checkout"
    assert_contains "Python setup step present" \
        "$TEMPLATES_WORKFLOW" "uses: actions/setup-python"
    assert_contains "pyyaml install step present" \
        "$TEMPLATES_WORKFLOW" "pip install --user pyyaml"
    assert_contains "Lint execution step references check-evidence-registry.sh" \
        "$TEMPLATES_WORKFLOW" "bash scripts/check-evidence-registry.sh"
    assert_contains "PR comment step present" \
        "$TEMPLATES_WORKFLOW" "gh pr comment"
}

# ============================================================================
# Test: Permissions
# ============================================================================
test_permissions() {
    echo ""
    echo "--- Permissions configuration ---"
    assert_contains "permissions block defined" \
        "$TEMPLATES_WORKFLOW" "permissions:"
    assert_contains "pull-requests: write permission" \
        "$TEMPLATES_WORKFLOW" "pull-requests: write"
    assert_contains "contents: read permission" \
        "$TEMPLATES_WORKFLOW" "contents: read"
}

# ============================================================================
# Test: Exit code 3-tier handling (§결정 15)
# ============================================================================
test_exit_code_3_tier() {
    echo ""
    echo "--- Exit code 3-tier handling (ADR-060 Amendment 2 §결정 15) ---"
    assert_contains "exit_status captured to GITHUB_OUTPUT" \
        "$TEMPLATES_WORKFLOW" "exit_status="
    # Case branches for 0 / 1 / 2 should all exist
    TESTS_RUN=$((TESTS_RUN + 3))
    local case_block
    case_block=$(awk '/case "\$\{LINT_STATUS/,/esac/' "$TEMPLATES_WORKFLOW")
    if grep -qE '^[[:space:]]*0\)' <<< "$case_block"; then
        echo -e "${GREEN}✓${NC} case branch for exit 0 (PASS)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} case branch for exit 0 missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    if grep -qE '^[[:space:]]*1\)' <<< "$case_block"; then
        echo -e "${GREEN}✓${NC} case branch for exit 1 (validation FAIL)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} case branch for exit 1 missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    if grep -qE '^[[:space:]]*2\)' <<< "$case_block"; then
        echo -e "${GREEN}✓${NC} case branch for exit 2 (META-ERROR)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} case branch for exit 2 missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# ============================================================================
# Test: Timeout defined
# ============================================================================
test_timeout() {
    echo ""
    echo "--- Timeout configuration ---"
    assert_contains "timeout-minutes defined" \
        "$TEMPLATES_WORKFLOW" "timeout-minutes:"
}

# ============================================================================
# Test: Carrier references (CFP-455 + ADR-060)
# ============================================================================
test_carrier_references() {
    echo ""
    echo "--- Carrier references in workflow comments ---"
    assert_contains "CFP-455 carrier referenced" \
        "$TEMPLATES_WORKFLOW" "CFP-455"
    assert_contains "ADR-060 framework referenced" \
        "$TEMPLATES_WORKFLOW" "ADR-060"
    assert_contains "Amendment 2 referenced" \
        "$TEMPLATES_WORKFLOW" "Amendment 2"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo "======================================================================"
    echo "CFP-455 Workflow YAML Validation Tests"
    echo "Templates: $TEMPLATES_WORKFLOW"
    echo "Self-app:  $SELF_APP_WORKFLOW"
    echo "======================================================================"

    test_templates_yaml_valid
    test_self_app_yaml_valid
    test_trigger_paths
    test_warning_mode
    test_bypass_label_omit
    test_required_steps
    test_permissions
    test_exit_code_3_tier
    test_timeout
    test_carrier_references

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
        echo -e "${GREEN}All workflow YAML tests passed.${NC}"
        return 0
    fi
}

main "$@"
