#!/usr/bin/env bash
# tests/scripts/test_check-codex-origin-main-directive-presence-sh.sh
# CFP-1412 / ADR-081 Amendment 8 §결정 D9 / ADR-060 §결정 28
#
# bats unit tests for check-codex-origin-main-directive-presence.sh
# (thin wrapper) + scripts/lib/check_codex_origin_main_directive_presence.py
#
# TDD RED -> GREEN sequence (CFP-1334 bats RED proof via stash pattern):
#   RED:  tests written FIRST before Python implementation present
#   GREEN: implementation written -> all pass
#
# Test coverage (T-1 through T-7):
#   T-1: [ORIGIN-MAIN-DIRECTIVE] block present -> PASS (exit 0)
#   T-2: directive absent + fallback marker network_scope_offline -> PASS (exit 0)
#   T-3: directive absent + fallback marker legacy_prompt_format -> PASS (exit 0)
#   T-4: directive absent + fallback marker intentional_working_tree_verify -> PASS (exit 0)
#   T-5: directive absent + invalid fallback enum -> WARNING (exit 1)
#   T-6: directive absent + no fallback marker -> WARNING (exit 1)
#   T-7 (Bonus): BYPASS_CODEX_ORIGIN_MAIN_DIRECTIVE=1 -> silent skip exit 0
#
# Fixture pair discrimination:
#   FX-1: codex_spawn_prompt_with_origin_main_directive.txt -> PASS
#   FX-2: codex_spawn_prompt_without_origin_main_directive.txt -> WARNING
#   FX-3: codex_spawn_prompt_with_fallback_marker.txt -> PASS
#
# SecurityArch TH-2: set +x guard in script under test (no PAT in output)
# ADR-061 §결정 1 정합: thin bash wrapper + Python SSOT (this tests both layers)

# bats setup
set -euo pipefail

SCRIPT_UNDER_TEST="$(cd "$(dirname "$0")/../.." && pwd)/scripts/check-codex-origin-main-directive-presence.sh"
FIXTURE_DIR="$(cd "$(dirname "$0")/.." && pwd)/fixtures"

# Helpers
pass() { echo "ok $1 - $2"; }
fail() { echo "not ok $1 - $2"; echo "  # FAILED: $3"; FAILED=$((FAILED + 1)); }

PASSED=0
FAILED=0
COUNT=0

run_test() {
    COUNT=$((COUNT + 1))
    local desc="$1"
    shift
    local expected_exit="$1"
    shift
    local tmpfile="$1"
    shift
    local extra_env="${1:-}"

    # Run the script
    if [ -n "$extra_env" ]; then
        actual_exit=0
        eval "env $extra_env bash '$SCRIPT_UNDER_TEST' '$tmpfile'" >/dev/null 2>&1 || actual_exit=$?
    else
        actual_exit=0
        bash "$SCRIPT_UNDER_TEST" "$tmpfile" >/dev/null 2>&1 || actual_exit=$?
    fi

    if [ "$actual_exit" -eq "$expected_exit" ]; then
        PASSED=$((PASSED + 1))
        pass "$COUNT" "$desc"
    else
        fail "$COUNT" "$desc" "expected exit $expected_exit, got $actual_exit"
    fi
}

echo "TAP version 13"
echo "1..10"

# -----------------------------------------------------------------------
# T-1: [ORIGIN-MAIN-DIRECTIVE] block present -> PASS (exit 0)
# -----------------------------------------------------------------------
TMP_T1=$(mktemp --suffix=.txt)
cat > "$TMP_T1" << 'EOF'
## Codex Worker Spawn Prompt
network_scope: repo-fetch-only
[ORIGIN-MAIN-DIRECTIVE]
Run: git fetch origin main
[/ORIGIN-MAIN-DIRECTIVE]
EOF
run_test "T-1: directive block present -> PASS (exit 0)" 0 "$TMP_T1"
rm -f "$TMP_T1"

# -----------------------------------------------------------------------
# T-2: directive absent + fallback network_scope_offline -> PASS (exit 0)
# -----------------------------------------------------------------------
TMP_T2=$(mktemp --suffix=.txt)
cat > "$TMP_T2" << 'EOF'
## Codex Worker Spawn Prompt
network_scope: offline
[origin-main-directive-fallback: network_scope_offline]
EOF
run_test "T-2: fallback network_scope_offline -> PASS (exit 0)" 0 "$TMP_T2"
rm -f "$TMP_T2"

# -----------------------------------------------------------------------
# T-3: directive absent + fallback legacy_prompt_format -> PASS (exit 0)
# -----------------------------------------------------------------------
TMP_T3=$(mktemp --suffix=.txt)
cat > "$TMP_T3" << 'EOF'
## Codex Worker Spawn Prompt
network_scope: offline
[origin-main-directive-fallback: legacy_prompt_format]
EOF
run_test "T-3: fallback legacy_prompt_format -> PASS (exit 0)" 0 "$TMP_T3"
rm -f "$TMP_T3"

# -----------------------------------------------------------------------
# T-4: directive absent + fallback intentional_working_tree_verify -> PASS (exit 0)
# -----------------------------------------------------------------------
TMP_T4=$(mktemp --suffix=.txt)
cat > "$TMP_T4" << 'EOF'
## Codex Worker Spawn Prompt
network_scope: web-fetch
[origin-main-directive-fallback: intentional_working_tree_verify]
EOF
run_test "T-4: fallback intentional_working_tree_verify -> PASS (exit 0)" 0 "$TMP_T4"
rm -f "$TMP_T4"

# -----------------------------------------------------------------------
# T-5: directive absent + invalid fallback enum -> WARNING (exit 1)
# -----------------------------------------------------------------------
TMP_T5=$(mktemp --suffix=.txt)
cat > "$TMP_T5" << 'EOF'
## Codex Worker Spawn Prompt
network_scope: offline
[origin-main-directive-fallback: invalid_unknown_enum_value]
EOF
run_test "T-5: invalid fallback enum -> WARNING (exit 1)" 1 "$TMP_T5"
rm -f "$TMP_T5"

# -----------------------------------------------------------------------
# T-6: directive absent + no fallback marker -> WARNING (exit 1)
# -----------------------------------------------------------------------
TMP_T6=$(mktemp --suffix=.txt)
cat > "$TMP_T6" << 'EOF'
## Codex Worker Spawn Prompt
network_scope: offline
## Task
Perform analysis without origin/main directive.
EOF
run_test "T-6: both absent -> WARNING (exit 1)" 1 "$TMP_T6"
rm -f "$TMP_T6"

# -----------------------------------------------------------------------
# T-7: BYPASS_CODEX_ORIGIN_MAIN_DIRECTIVE=1 -> silent skip exit 0
# -----------------------------------------------------------------------
TMP_T7=$(mktemp --suffix=.txt)
cat > "$TMP_T7" << 'EOF'
## Codex Worker Spawn Prompt
## No directive, no fallback — but bypass env activated
EOF
run_test "T-7 (Bonus): bypass env -> silent skip exit 0" 0 "$TMP_T7" "BYPASS_CODEX_ORIGIN_MAIN_DIRECTIVE=1"
rm -f "$TMP_T7"

# -----------------------------------------------------------------------
# FX-1: fixture WITH directive -> PASS
# -----------------------------------------------------------------------
COUNT=$((COUNT + 1))
FX1_FILE="${FIXTURE_DIR}/codex_spawn_prompt_with_origin_main_directive.txt"
if [ -f "$FX1_FILE" ]; then
    actual_exit=0
    bash "$SCRIPT_UNDER_TEST" "$FX1_FILE" >/dev/null 2>&1 || actual_exit=$?
    if [ "$actual_exit" -eq 0 ]; then
        PASSED=$((PASSED + 1))
        pass "$COUNT" "FX-1: fixture with directive -> PASS (exit 0)"
    else
        fail "$COUNT" "FX-1: fixture with directive -> PASS (exit 0)" "got exit $actual_exit"
    fi
else
    fail "$COUNT" "FX-1: fixture with directive -> PASS (exit 0)" "fixture file not found: $FX1_FILE"
fi

# -----------------------------------------------------------------------
# FX-2: fixture WITHOUT directive -> WARNING
# -----------------------------------------------------------------------
COUNT=$((COUNT + 1))
FX2_FILE="${FIXTURE_DIR}/codex_spawn_prompt_without_origin_main_directive.txt"
if [ -f "$FX2_FILE" ]; then
    actual_exit=0
    bash "$SCRIPT_UNDER_TEST" "$FX2_FILE" >/dev/null 2>&1 || actual_exit=$?
    if [ "$actual_exit" -eq 1 ]; then
        PASSED=$((PASSED + 1))
        pass "$COUNT" "FX-2: fixture without directive -> WARNING (exit 1)"
    else
        fail "$COUNT" "FX-2: fixture without directive -> WARNING (exit 1)" "got exit $actual_exit"
    fi
else
    fail "$COUNT" "FX-2: fixture without directive -> WARNING (exit 1)" "fixture file not found: $FX2_FILE"
fi

# -----------------------------------------------------------------------
# FX-3: fixture WITH fallback marker -> PASS
# -----------------------------------------------------------------------
COUNT=$((COUNT + 1))
FX3_FILE="${FIXTURE_DIR}/codex_spawn_prompt_with_fallback_marker.txt"
if [ -f "$FX3_FILE" ]; then
    actual_exit=0
    bash "$SCRIPT_UNDER_TEST" "$FX3_FILE" >/dev/null 2>&1 || actual_exit=$?
    if [ "$actual_exit" -eq 0 ]; then
        PASSED=$((PASSED + 1))
        pass "$COUNT" "FX-3: fixture with fallback marker -> PASS (exit 0)"
    else
        fail "$COUNT" "FX-3: fixture with fallback marker -> PASS (exit 0)" "got exit $actual_exit"
    fi
else
    fail "$COUNT" "FX-3: fixture with fallback marker -> PASS (exit 0)" "fixture file not found: $FX3_FILE"
fi

# -----------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------
echo ""
echo "# Results: $PASSED passed, $FAILED failed (of $COUNT total)"
if [ "$FAILED" -eq 0 ]; then
    echo "# ALL PASS"
    exit 0
else
    echo "# FAILED: $FAILED test(s)"
    exit 1
fi
