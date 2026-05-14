#!/usr/bin/env bash
# test_retro_mandatory_yml.sh
# CFP-645 — retro-mandatory.yml regression test (secrets context if-conditional 차단)
# 3 TC:
#   TC1: no 'secrets.X != ...' job/step-level if expression
#   TC2: YAML parses successfully (python yaml.safe_load)
#   TC3: template byte-identical with .github/workflows

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"

WORKFLOW_FILE="$REPO_ROOT/.github/workflows/retro-mandatory.yml"
TEMPLATE_FILE="$REPO_ROOT/templates/github-workflows/retro-mandatory.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

pass() {
    echo -e "${GREEN}PASS${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
}

fail() {
    echo -e "${RED}FAIL${NC} $1"
    if [ -n "${2:-}" ]; then echo "  $2"; fi
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
}

# TC1: secrets context if-conditional 부재 확인 (CFP-645 regression guard)
echo "TC1: no 'secrets.X != ...' job/step-level if expression (CFP-645 regression)"
if grep -qE "secrets\.[A-Z_]+[[:space:]]*!=[[:space:]]*''" "$WORKFLOW_FILE"; then
    MATCH=$(grep -nE "secrets\.[A-Z_]+[[:space:]]*!=[[:space:]]*''" "$WORKFLOW_FILE")
    fail "TC1" "secrets context if-expression still present: $MATCH"
else
    pass "TC1"
fi

# TC2: YAML 문법 검증
echo "TC2: YAML parses successfully (python yaml.safe_load)"
if python3 -c "import yaml; yaml.safe_load(open('$WORKFLOW_FILE', encoding='utf-8'))" 2>/dev/null; then
    pass "TC2"
else
    fail "TC2" "yaml.safe_load failed on $WORKFLOW_FILE"
fi

# TC3: template byte-identical with .github/workflows
echo "TC3: template byte-identical with .github/workflows"
if diff "$TEMPLATE_FILE" "$WORKFLOW_FILE" > /dev/null 2>&1; then
    pass "TC3"
else
    DIFF_OUT=$(diff "$TEMPLATE_FILE" "$WORKFLOW_FILE" | head -20)
    fail "TC3" "Files differ: $DIFF_OUT"
fi

# Summary
echo ""
echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
if [ "$TESTS_FAILED" -gt 0 ]; then
    echo -e "${RED}FAILED: $TESTS_FAILED test(s) failed${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed${NC}"
    exit 0
fi
