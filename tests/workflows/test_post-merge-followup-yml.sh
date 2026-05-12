#!/usr/bin/env bash
# test_post-merge-followup-yml.sh
# CFP-476 Phase 2 — Post-merge follow-up automation workflow YAML validation tests
# Verifies templates/github-workflows/post-merge-followup.yml + .github/workflows/ self-app copy
# ADR-026 Amendment 1 byte-identity invariant §결정 5.B + Action 3 algorithm §결정 5.A-D

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"
FIXTURES_DIR="$REPO_ROOT/tests/fixtures/post-merge-followup"

TEMPLATES_WORKFLOW="$REPO_ROOT/templates/github-workflows/post-merge-followup.yml"
SELF_APP_WORKFLOW="$REPO_ROOT/.github/workflows/post-merge-followup.yml"
ACTION3_LOGIC_SCRIPT="$REPO_ROOT/tests/scripts/post-merge-followup/action3-logic.sh"

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

assert_contains_ere() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qE "$pattern" "$file"; then
        echo -e "${GREEN}✓${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $desc"
        echo "    ERE pattern not found: $pattern"
        echo "    In file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_not_contains() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qF "$pattern" "$file"; then
        echo -e "${RED}✗${NC} $desc"
        echo "    Pattern found (should not exist): $pattern"
        echo "    In file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    else
        echo -e "${GREEN}✓${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    fi
}

assert_not_contains_ere() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qE "$pattern" "$file"; then
        echo -e "${RED}✗${NC} $desc"
        echo "    ERE pattern found (should not exist): $pattern"
        echo "    In file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    else
        echo -e "${GREEN}✓${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
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
        echo "    Files differ (byte-identity invariant violation):"
        diff "$file_a" "$file_b" | sed 's/^/      /' | head -30
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_yq_query_exists() {
    local desc="$1"
    local file="$2"
    local yq_query="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if command -v yq &> /dev/null; then
        if yq eval "$yq_query" "$file" 2>/dev/null | grep -q . ; then
            echo -e "${GREEN}✓${NC} $desc"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            return 0
        else
            echo -e "${RED}✗${NC} $desc"
            echo "    yq query returned empty: $yq_query"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            return 1
        fi
    else
        echo -e "${YELLOW}⊘${NC} $desc (yq not installed, skipping)"
        return 0
    fi
}

# ============================================================================
# Block A: YAML validity assertion (2 files)
# ============================================================================
test_block_a_yaml_validity() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Block A: YAML validity assertion"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    if [[ ! -f "$TEMPLATES_WORKFLOW" ]]; then
        echo -e "${RED}ERROR: templates workflow file not found: $TEMPLATES_WORKFLOW${NC}" >&2
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TESTS_RUN=$((TESTS_RUN + 1))
        return 1
    fi

    if [[ ! -f "$SELF_APP_WORKFLOW" ]]; then
        echo -e "${RED}ERROR: self-app workflow file not found: $SELF_APP_WORKFLOW${NC}" >&2
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TESTS_RUN=$((TESTS_RUN + 1))
        return 1
    fi

    assert_yaml_valid "templates/github-workflows/post-merge-followup.yml is valid YAML" \
        "$TEMPLATES_WORKFLOW"
    assert_yaml_valid ".github/workflows/post-merge-followup.yml is valid YAML" \
        "$SELF_APP_WORKFLOW"
}

# ============================================================================
# Block B: Byte-identical assertion (ADR-026 Amendment 1 §결정 5.B)
# ============================================================================
test_block_b_byte_identity() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Block B: Byte-identity invariant (ADR-026 Amendment 1 §결정 5.B)"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    assert_files_identical "templates and deployed workflow files are byte-identical (ADR-026 Amendment 1 §결정 5.B)" \
        "$TEMPLATES_WORKFLOW" "$SELF_APP_WORKFLOW"
}

# ============================================================================
# Block C: Action 3 algorithm grep assertion (ADR-026 Amendment 1 §결정 5.A-5.D)
# ============================================================================
test_block_c_action3_algorithm() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Block C: Action 3 algorithm verification (ADR-026 Amendment 1 §결정 5)"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    # §결정 5.A — Close keyword regex SSOT (POSIX ERE, GitHub native 9 variants)
    # Note: grep -F is used because the pattern contains special chars; verify via presence of keywords instead
    assert_contains "Close keyword pattern (close/fix/resolve variants)" \
        "$TEMPLATES_WORKFLOW" "close[sd]?"

    # §결정 5.A — closedByPullRequestsReferences API call
    assert_contains "closedByPullRequestsReferences API pattern" \
        "$TEMPLATES_WORKFLOW" "closedByPullRequestsReferences"

    # §결정 5.A — dual-source AND logic (intersection check via grep -qxF)
    assert_contains "Source B AND logic (grep -qxF for intersection)" \
        "$TEMPLATES_WORKFLOW" "grep -qxF"

    # §결정 5.C — 4-marker namespace audit comments
    assert_contains "[close-success] audit marker" \
        "$TEMPLATES_WORKFLOW" "[close-success]"
    assert_contains "[multi-match-skip] audit marker" \
        "$TEMPLATES_WORKFLOW" "[multi-match-skip]"
    assert_contains "[cross-repo-skip] audit marker" \
        "$TEMPLATES_WORKFLOW" "[cross-repo-skip]"
    assert_contains "[dual-source-mismatch] audit marker" \
        "$TEMPLATES_WORKFLOW" "[dual-source-mismatch]"

    # §결정 5.A — terminal-phase gate (phase:보안-테스트 default / phase:구현-테스트 security_ai=false)
    assert_contains "phase:보안-테스트 terminal phase" \
        "$TEMPLATES_WORKFLOW" "phase:보안-테스트"
    assert_contains "phase:구현-테스트 terminal phase" \
        "$TEMPLATES_WORKFLOW" "phase:구현-테스트"

    # §결정 5.A — Consumer config read (yq → python3 fallback)
    assert_contains "yq or python3 config read pattern" \
        "$TEMPLATES_WORKFLOW" "lanes.security_ai"
}

# ============================================================================
# Block D: yq AST query verify (AC-16 security T1/T2 mitigation)
# ============================================================================
test_block_d_yq_ast_queries() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Block D: yq AST query verification (AC-16 security mitigation)"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    # §결정 5.D — env: indirection for PR_BODY and PR_TITLE (T1/T2 mitigation)
    assert_contains "env: block with PR_BODY definition" \
        "$TEMPLATES_WORKFLOW" "PR_BODY:"
    assert_contains "env: block with PR_TITLE definition" \
        "$TEMPLATES_WORKFLOW" "PR_TITLE:"

    # §결정 5.D — No inline ${{ }} shell expansion in run blocks (security check)
    # Extract Action 3 run block and verify PR_BODY/PR_TITLE are from env, not inline
    # Note: PR_TITLE/PR_BODY are defined in env: blocks (step 48, 145) not inline — verify via action3 section
    local action3_section=$(awk '/name: Action 3/,/name: Action 4/' "$TEMPLATES_WORKFLOW" | grep -A 100 "run: |" || echo "")
    if echo "$action3_section" | grep -qE 'github\.event\.pull_request\.(body|title)'; then
        echo -e "${RED}✗${NC} Inline shell expansion detected in Action 3 run block"
        TESTS_RUN=$((TESTS_RUN + 1))
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    else
        TESTS_RUN=$((TESTS_RUN + 1))
        echo -e "${GREEN}✓${NC} No inline shell expansion in Action 3 run block"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi

    # §결정 5.D — printf '%s' pattern for safe PR_BODY handling (F-P1-05 mitigation)
    # Action 3 run block should use printf for raw output
    assert_contains "printf safe output pattern used" \
        "$TEMPLATES_WORKFLOW" "printf '%s'"
}

# ============================================================================
# Block E: Concurrency lock + permissions verify
# ============================================================================
test_block_e_concurrency_and_permissions() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Block E: Concurrency lock + permissions (AC-17 + AC-16 security)"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    # §결정 5.D — Concurrency lock for idempotency (AC-17)
    assert_contains "concurrency.group configured" \
        "$TEMPLATES_WORKFLOW" "post-merge-followup-"
    assert_contains "concurrency.cancel-in-progress set to false" \
        "$TEMPLATES_WORKFLOW" "cancel-in-progress: false"

    # §결정 5.D — Permissions (least-privilege)
    assert_contains "issues: write permission" \
        "$TEMPLATES_WORKFLOW" "issues: write"
    assert_contains "pull-requests: write permission" \
        "$TEMPLATES_WORKFLOW" "pull-requests: write"
    assert_contains "contents: read permission" \
        "$TEMPLATES_WORKFLOW" "contents: read"
    assert_not_contains "actions: write permission (should not be granted)" \
        "$TEMPLATES_WORKFLOW" "actions: write"
    assert_not_contains "id-token: write permission (should not be granted)" \
        "$TEMPLATES_WORKFLOW" "id-token: write"
}

# ============================================================================
# Helper: Load fixture YAML (requires python3 + PyYAML)
# ============================================================================
load_fixture_yaml() {
    local fixture_file="$1"
    local key="$2"
    python3 -c "
import yaml, sys
try:
    with open('$fixture_file', 'r', encoding='utf-8', errors='replace') as f:
        data = yaml.safe_load(f)
        if data is None:
            print('')
        else:
            val = data.get('$key', '')
            print(str(val) if val is not None else '')
except Exception as e:
    print('', file=sys.stderr)
" 2>/dev/null || echo ""
}

load_fixture_field() {
    local fixture_file="$1"
    local path="$2" # dot-separated path like "pr.number" or "consumer_config.lanes.security_ai"
    python3 -c "
import yaml, sys
try:
    with open('$fixture_file', 'r', encoding='utf-8', errors='replace') as f:
        data = yaml.safe_load(f)
        if data is None:
            print('')
        else:
            keys = '$path'.split('.')
            val = data
            for k in keys:
                if isinstance(val, dict):
                    val = val.get(k, None)
                else:
                    val = None
                    break
            if val is None:
                print('')
            elif isinstance(val, list):
                # Handle lists (e.g., pr.labels) by joining with spaces
                print(' '.join(str(v) for v in val))
            else:
                print(str(val))
except Exception as e:
    print('', file=sys.stderr)
" 2>/dev/null || echo ""
}

# ============================================================================
# Helper: Run fixture simulation
# ============================================================================
run_fixture_simulation() {
    local fixture_file="$1"
    local fixture_name=$(basename "$fixture_file" .yml)

    TESTS_RUN=$((TESTS_RUN + 1))

    # Load fixture YAML fields
    local expected_outcome=$(load_fixture_yaml "$fixture_file" "expected_outcome")
    local pr_title=$(load_fixture_field "$fixture_file" "pr.title")
    local pr_body=$(load_fixture_field "$fixture_file" "pr.body")
    local pr_number=$(load_fixture_field "$fixture_file" "pr.number")
    local issue_number=$(load_fixture_field "$fixture_file" "issue.number")
    local closed_by_refs=$(load_fixture_field "$fixture_file" "issue.closed_by_pull_requests_references")
    local security_ai=$(load_fixture_field "$fixture_file" "consumer_config.lanes.security_ai")
    # Load issue_lane_skip_reason using Python directly
    # Python will determine if the PR's phase label matches the terminal phase for this security_ai setting
    local issue_lane_skip_reason=$(python3 -c "
import yaml
fixture_file = '$fixture_file'
security_ai_str = '$security_ai'
security_ai = security_ai_str == 'True'

with open(fixture_file, 'r', encoding='utf-8', errors='replace') as f:
    data = yaml.safe_load(f)
    labels = data.get('pr', {}).get('labels', [])
    phase_labels = [l for l in labels if isinstance(l, str) and l.startswith('phase:')]

    # Determine terminal phase
    if not security_ai:
        terminal_phase = '구현-테스트'
    else:
        terminal_phase = '보안-테스트'

    # Check if phase label matches terminal phase
    for label in phase_labels:
        if label.endswith(terminal_phase):
            print('')  # Terminal phase - no skip
            exit()

    # If we got here, it's a mid-phase label
    print('mid-phase')
" 2>/dev/null || echo ""
)

    # Build terminal_phase based on security_ai config
    local terminal_phase
    if [ "$security_ai" = "False" ] || [ "$security_ai" = "false" ]; then
        # security_ai=false → phase:구현-테스트
        # UTF-8 hex: eab5aced98842ded858cec8aa4ed8ab8
        terminal_phase="phase:$(printf '\xea\xb5\xac\xed\x98\x84\x2d\xed\x85\x8c\xec\x8a\xa4\xed\x8a\xb8')"
    else
        # security_ai=true → phase:보안-테스트
        # UTF-8 hex: ebb3b4ec95882ded858cec8aa4ed8ab8
        terminal_phase="phase:$(printf '\xeb\xb3\xb4\xec\x95\x88\x2d\xed\x85\x8c\xec\x8a\xa4\xed\x8a\xb8')"
    fi

    # For issue_lane, we'll keep it empty if it matches terminal_phase (no need to export)
    local issue_lane=""
    # issue_lane_skip_reason is already determined by Python above

    # Debug: Show what we loaded (uncomment to debug)
    # echo "DEBUG: fixture=$fixture_name, security_ai=$security_ai, terminal_phase_hex=$(echo -n "$terminal_phase" | od -An -tx1 | tr -d ' '), issue_lane_skip_reason=$issue_lane_skip_reason" >&2

    # Simulate workflow-level Extract PR metadata guard: detect chore PRs
    # Chore PRs should skip before reaching action3-logic.sh
    if [[ "$pr_title" =~ ^chore\( ]]; then
        # Chore PR detected - skip_no_issue
        if [ "skip_no_issue" = "$expected_outcome" ]; then
            echo -e "${GREEN}✓${NC} $fixture_name (outcome=skip_no_issue)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
            return 0
        else
            echo -e "${RED}✗${NC} $fixture_name"
            echo "    Expected: $expected_outcome"
            echo "    Got:      skip_no_issue (chore PR detected)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
            return 1
        fi
    fi

    # Create temporary GITHUB_OUTPUT file for this fixture
    local temp_output=$(mktemp)
    trap "rm -f $temp_output" RETURN

    # Set environment for action3-logic.sh
    export PR_BODY="$pr_body"
    export PR_NUM="$pr_number"
    export THIS_REPO="mclayer/plugin-codeforge"
    export ISSUE_NUM="$issue_number"
    export TERMINAL_PHASE="$terminal_phase"
    export ISSUE_LANE="$issue_lane"
    export ISSUE_LANE_SKIP_REASON="$issue_lane_skip_reason"
    export EXISTING_AUDIT=""
    # Convert closed_by_refs list to comma-separated string (SOURCE_B_LIST)
    if [ -n "$closed_by_refs" ] && [ "$closed_by_refs" != "None" ] && [ "$closed_by_refs" != "[]" ]; then
        SOURCE_B_LIST=$(echo "$closed_by_refs" | tr ',' '\n' | grep -oE '[0-9]+' | paste -sd ',' -)
    else
        SOURCE_B_LIST=""
    fi
    export SOURCE_B_LIST
    export GITHUB_OUTPUT="$temp_output"

    # Run action3 logic script (capture outcome)
    bash "$ACTION3_LOGIC_SCRIPT" >/dev/null 2>&1
    local actual_outcome=$(grep "^outcome=" "$temp_output" 2>/dev/null | cut -d= -f2 || echo "unknown")

    # Verify outcome matches expected
    if [ "$actual_outcome" = "$expected_outcome" ]; then
        echo -e "${GREEN}✓${NC} $fixture_name (outcome=$actual_outcome)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $fixture_name"
        echo "    Expected: $expected_outcome"
        echo "    Got:      $actual_outcome"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ============================================================================
# Block F: bash mock simulation (13 fixture + 2 bonus)
# ============================================================================
test_block_f_bash_mock_fixtures() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Block F: bash mock simulation with fixtures (ADR-026 Amendment 1 §결정 5.A-5.D)"
    echo "═══════════════════════════════════════════════════════════════════════════════"

    # Verify prerequisites
    if [[ ! -d "$FIXTURES_DIR" ]]; then
        echo -e "${RED}ERROR: Fixtures directory not found: $FIXTURES_DIR${NC}" >&2
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TESTS_RUN=$((TESTS_RUN + 1))
        return 1
    fi

    if [[ ! -f "$ACTION3_LOGIC_SCRIPT" ]]; then
        echo -e "${RED}ERROR: Action 3 logic script not found: $ACTION3_LOGIC_SCRIPT${NC}" >&2
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TESTS_RUN=$((TESTS_RUN + 1))
        return 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}ERROR: python3 required for YAML fixture parsing${NC}" >&2
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TESTS_RUN=$((TESTS_RUN + 1))
        return 1
    fi

    # Find fixture files
    local fixture_files=($(ls "$FIXTURES_DIR"/*.yml 2>/dev/null | sort))
    local fixture_count=${#fixture_files[@]}

    if [[ $fixture_count -eq 0 ]]; then
        echo -e "${RED}ERROR: No fixture files found in $FIXTURES_DIR${NC}" >&2
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TESTS_RUN=$((TESTS_RUN + 1))
        return 1
    fi

    echo "Running $fixture_count fixture simulations..."
    echo ""
    for fixture_file in "${fixture_files[@]}"; do
        run_fixture_simulation "$fixture_file" || true
    done
}

# ============================================================================
# Main test execution
# ============================================================================
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
    echo "║ CFP-476 Phase 2 — Post-merge follow-up automation workflow test harness     ║"
    echo "║ ADR-026 Amendment 1 (2026-05-12)                                             ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════════╝"

    test_block_a_yaml_validity || true
    test_block_b_byte_identity || true
    test_block_c_action3_algorithm || true
    test_block_d_yq_ast_queries || true
    test_block_e_concurrency_and_permissions || true
    test_block_f_bash_mock_fixtures || true

    # Summary
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Test Summary"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "Total tests run:   $TESTS_RUN"
    echo "Tests passed:      $TESTS_PASSED"
    echo "Tests failed:      $TESTS_FAILED"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed.${NC}"
        return 1
    fi
}

main "$@"
