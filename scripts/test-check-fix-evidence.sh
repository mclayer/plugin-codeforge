#!/usr/bin/env bash
# test-check-fix-evidence.sh — smoke test for check-fix-evidence.sh (CFP-298).
#
# Fixture-based tests validating §10 FIX Ledger ↔ §14 Lane Evidence cross-validation.
# Pattern mirrors test-check-lane-evidence.sh.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE_DIR="$SCRIPT_DIR/fixtures/check-fix-evidence"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

# Test 1 — valid story: 1 FIX iteration + 1 fix-iter lane row → PASS (exit 0)
test_1_valid_1fix_1fix_iter() {
    log "Test 1: valid — 1 FIX iteration + 1 fix-iter row → PASS (exit 0)"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" \
        --story "$FIXTURE_DIR/valid-1fix-1fix-iter.md" \
        --strict \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0, got rc=$rc)"
    fi
}

# Test 2 — invalid story: 2 FIX iterations but only 1 fix-iter row → FAIL (exit 1 in strict)
test_2_invalid_2fix_1fix_iter_strict() {
    log "Test 2: invalid — 2 FIX iterations, 1 fix-iter row --strict → exit 1"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" \
        --story "$FIXTURE_DIR/invalid-2fix-1fix-iter.md" \
        --strict \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 1 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc strict fail)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=1, got rc=$rc)"
    fi
}

# Test 3 — invalid story: default (advisory) mode → exit 0 despite mismatch
test_3_invalid_advisory_mode() {
    log "Test 3: invalid — 2 FIX iterations, 1 fix-iter row (default advisory mode) → exit 0"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" \
        --story "$FIXTURE_DIR/invalid-2fix-1fix-iter.md" \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc advisory)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0 advisory, got rc=$rc)"
    fi
}

# Test 4 — valid story: 0 FIX iterations (empty ledger) → PASS (exit 0)
test_4_valid_no_fix() {
    log "Test 4: valid — 0 FIX iterations (empty ledger) → PASS (exit 0)"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" \
        --story "$FIXTURE_DIR/valid-no-fix-iterations.md" \
        --strict \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0, got rc=$rc)"
    fi
}

# Test 5 — missing story file → FAIL message on stderr, exit 0 (advisory) and exit 1 (strict)
test_5_missing_story_advisory() {
    log "Test 5: missing story (advisory mode) → exit 0"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" \
        --story "/nonexistent/story.md" \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0 advisory, got rc=$rc)"
    fi
}

# Test 6 — missing story --strict → exit 1
test_6_missing_story_strict() {
    log "Test 6: missing story --strict → exit 1"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" \
        --story "/nonexistent/story.md" \
        --strict \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 1 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=1, got rc=$rc)"
    fi
}

# Test 7 — --help → exit 0
test_7_help() {
    log "Test 7: --help → exit 0"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" --help >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc)"
    fi
}

# Test 8 — unknown arg → exit 2
test_8_unknown_arg() {
    log "Test 8: unknown arg → exit 2"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" --unknown-flag >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 2 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=2, got rc=$rc)"
    fi
}

# Test 9 — valid story: positional arg (no --story flag) → PASS
test_9_positional_arg() {
    log "Test 9: positional arg (no --story flag) → PASS"
    local rc=0
    bash "$SCRIPT_DIR/check-fix-evidence.sh" \
        "$FIXTURE_DIR/valid-1fix-1fix-iter.md" \
        --strict \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0, got rc=$rc)"
    fi
}

# Test 10 — FAIL output contains informative message (stderr check)
test_10_fail_message_content() {
    log "Test 10: FAIL message contains 'fix-iter row' detail in stderr"
    local stderr_out
    stderr_out="$(bash "$SCRIPT_DIR/check-fix-evidence.sh" \
        --story "$FIXTURE_DIR/invalid-2fix-1fix-iter.md" \
        --quiet \
        2>&1 >/dev/null)" || true
    if printf '%s' "$stderr_out" | grep -q "fix-iter row"; then
        PASS=$((PASS + 1))
        log "  PASS (stderr contains 'fix-iter row')"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected 'fix-iter row' in stderr, got: $stderr_out)"
    fi
}

log "=== test-check-fix-evidence 시작 ==="
test_1_valid_1fix_1fix_iter
test_2_invalid_2fix_1fix_iter_strict
test_3_invalid_advisory_mode
test_4_valid_no_fix
test_5_missing_story_advisory
test_6_missing_story_strict
test_7_help
test_8_unknown_arg
test_9_positional_arg
test_10_fail_message_content

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
