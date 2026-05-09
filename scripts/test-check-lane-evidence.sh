#!/usr/bin/env bash
# test-check-lane-evidence.sh — smoke test for check-lane-evidence.sh (CFP-126 Phase 2 + CFP-137 Phase 2).
#
# CFP-137 Phase 2 확장: T6 (--check-parallelization with design 6 deputy rows < 60s → PASS advisory)
# 기존 T1-T5 = CFP-126 Phase 2 original tests.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE_DIR="$SCRIPT_DIR/fixtures/check-lane-evidence"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

# Test 1 — single-pass fixture: §14 yaml block + 7-row valid PR description → PASS
test_1_single_pass_fixture() {
    log "Test 1: single-pass fixture (§14 + 7-row PR description) → PASS"
    local rc=0
    # Fixture story file 경로 + dummy PR (gh CLI mock 어려움 — story-only 검증)
    bash "$SCRIPT_DIR/check-lane-evidence.sh" \
        --story "$FIXTURE_DIR/single-pass-story.md" \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc)"
    fi
}

# Test 2 — missing story file → FAIL but exit 0 (default advisory mode)
test_2_missing_story_advisory() {
    log "Test 2: missing story (default advisory mode) → exit 0"
    local rc=0
    bash "$SCRIPT_DIR/check-lane-evidence.sh" \
        --story "/nonexistent/story.md" \
        --quiet \
        2>/dev/null || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc default advisory)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0 advisory, got rc=$rc)"
    fi
}

# Test 3 — missing story --strict → exit 1
test_3_missing_story_strict() {
    log "Test 3: missing story --strict → exit 1"
    local rc=0
    bash "$SCRIPT_DIR/check-lane-evidence.sh" \
        --story "/nonexistent/story.md" \
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

# Test 4 — --help → exit 0
test_4_help() {
    log "Test 4: --help → exit 0"
    local rc=0
    bash "$SCRIPT_DIR/check-lane-evidence.sh" --help >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc)"
    fi
}

# Test 5 — unknown arg → exit 2
test_5_unknown_arg() {
    log "Test 5: unknown arg → exit 2"
    local rc=0
    bash "$SCRIPT_DIR/check-lane-evidence.sh" --unknown-flag >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 2 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=2, got rc=$rc)"
    fi
}

# Test 6 — CFP-137 Phase 2: --check-parallelization with design 6 deputy rows within 60s → PASS (advisory, exit 0)
test_6_parallelization_design_rows() {
    log "Test 6: --check-parallelization (design 6 deputy rows < 60s) → exit 0 advisory PASS"
    local rc=0
    # Note: --quiet suppresses log() (stdout OK messages). Run without --quiet to capture OK.
    # stderr is captured for any WARN/FAIL messages.
    combined="$(bash "$SCRIPT_DIR/check-lane-evidence.sh" \
        --story "$FIXTURE_DIR/design-parallelization-story.md" \
        --check-parallelization \
        2>&1)" || rc=$?
    # Should exit 0 (advisory mode) and NOT contain PARALLELIZATION WARN
    para_warn="$(printf '%s' "$combined" | grep -c 'PARALLELIZATION WARN' || true)"
    para_skip="$(printf '%s' "$combined" | grep -c 'PARALLELIZATION SKIP' || true)"
    if [ $rc -eq 0 ] && [ "$para_warn" -eq 0 ] && [ "$para_skip" -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc, no WARN, no SKIP — PARALLELIZATION OK)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc, warn=$para_warn, skip=$para_skip)"
        printf '%s\n' "$combined" >&2
    fi
}

log "=== test-check-lane-evidence 시작 ==="
test_1_single_pass_fixture
test_2_missing_story_advisory
test_3_missing_story_strict
test_4_help
test_5_unknown_arg
test_6_parallelization_design_rows

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
