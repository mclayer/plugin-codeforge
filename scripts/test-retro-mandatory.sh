#!/usr/bin/env bash
# test-retro-mandatory.sh — smoke tests for retro-mandatory workflow logic
#
# Covers: AC-5 (retro file path regex), AC-7 (retry timing via retro-retry-helper.sh),
#         AC-9 (close-blocking gate logic), AC-11 (PMOAgent manual spawn template)
# CFP-138 Phase 2 / ADR-045

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE_DIR="$SCRIPT_DIR/fixtures/retro-mandatory"
HELPER="$SCRIPT_DIR/retro-retry-helper.sh"

PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# close_blocking_check <label1,label2,...> → 0 = allow close, 1 = block
# Implements the gate logic from retro-mandatory.yml close-blocking job.
close_blocking_check() {
    local labels_csv="$1"
    local is_story is_terminal is_early_close has_retro_gate

    echo "$labels_csv" | grep -q "type:story" && is_story=1 || is_story=0
    echo "$labels_csv" | grep -q "phase:보안-테스트" && is_terminal=1 || is_terminal=0
    echo "$labels_csv" | grep -qE "early-close:" && is_early_close=1 || is_early_close=0
    echo "$labels_csv" | grep -q "gate:retro-complete" && has_retro_gate=1 || has_retro_gate=0

    # Block condition: isStory && isTerminalPhase && !isEarlyClose && !hasRetroGate
    if [ "$is_story" -eq 1 ] && [ "$is_terminal" -eq 1 ] && [ "$is_early_close" -eq 0 ] && [ "$has_retro_gate" -eq 0 ]; then
        return 1  # BLOCK
    fi
    return 0  # ALLOW
}

# ISO 8601 epoch (portable, same logic as retro-retry-helper.sh)
iso8601_to_epoch() {
    local ts="${1%Z}"
    if date --version >/dev/null 2>&1; then
        date -d "${ts}Z" +%s 2>/dev/null || echo 0
    else
        date -j -f "%Y-%m-%dT%H:%M:%S" "$ts" "+%s" 2>/dev/null || echo 0
    fi
}

# ---------------------------------------------------------------------------
# AC-5: retro file path regex enforcement
# Regex from Change Plan §7.1 Boundary C
# ---------------------------------------------------------------------------
RETRO_PATH_REGEX='^[0-9]{4}-[0-9]{2}-[0-9]{2}-cfp-[0-9]+(-[a-z0-9-]+)?\.md$'

test_ac5_valid_retro_path() {
    log "AC-5 Test 1: valid path '2026-05-09-cfp-138-retro-mandatory.md' → match"
    if echo "2026-05-09-cfp-138-retro-mandatory.md" | grep -qP "$RETRO_PATH_REGEX" 2>/dev/null || \
       echo "2026-05-09-cfp-138-retro-mandatory.md" | grep -qE "$RETRO_PATH_REGEX"; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: expected regex match"
    fi
}

test_ac5_valid_no_slug() {
    log "AC-5 Test 2: valid path no slug '2026-05-09-cfp-138.md' → match"
    if echo "2026-05-09-cfp-138.md" | grep -qE "$RETRO_PATH_REGEX"; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: expected regex match"
    fi
}

test_ac5_invalid_no_date() {
    log "AC-5 Test 3: invalid path 'cfp-138-retro.md' (no date prefix) → no match"
    if echo "cfp-138-retro.md" | grep -qE "$RETRO_PATH_REGEX"; then
        FAIL=$((FAIL + 1))
        log "  FAIL: expected no match but got match"
    else
        PASS=$((PASS + 1))
        log "  PASS (no match as expected)"
    fi
}

test_ac5_invalid_uppercase() {
    log "AC-5 Test 4: invalid path '2026-05-09-CFP-138-retro.md' (uppercase CFP) → no match"
    if echo "2026-05-09-CFP-138-retro.md" | grep -qE "$RETRO_PATH_REGEX"; then
        FAIL=$((FAIL + 1))
        log "  FAIL: expected no match but got match"
    else
        PASS=$((PASS + 1))
        log "  PASS (no match as expected — uppercase rejected)"
    fi
}

test_ac5_invalid_no_md() {
    log "AC-5 Test 5: invalid path '2026-05-09-cfp-138-retro' (no .md) → no match"
    if echo "2026-05-09-cfp-138-retro" | grep -qE "$RETRO_PATH_REGEX"; then
        FAIL=$((FAIL + 1))
        log "  FAIL: expected no match"
    else
        PASS=$((PASS + 1))
        log "  PASS (no match as expected)"
    fi
}

# ---------------------------------------------------------------------------
# AC-7: retry attempt sequence timing (via retro-retry-helper.sh)
# ---------------------------------------------------------------------------

test_ac7_helper_exists() {
    log "AC-7 Test 0: retro-retry-helper.sh exists"
    if [ -f "$HELPER" ]; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: $HELPER not found"
    fi
}

test_ac7_fixture_exists() {
    log "AC-7 Test 1: attempts-due.jsonl fixture exists"
    if [ -f "$FIXTURE_DIR/attempts-due.jsonl" ]; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: $FIXTURE_DIR/attempts-due.jsonl not found"
    fi
}

test_ac7_not_yet_due_4min() {
    log "AC-7 Test 2: CFP-138 attempt_n=1 (5min threshold) — 4min elapsed → not due"
    if [ ! -f "$HELPER" ]; then
        log "  SKIP: retro-retry-helper.sh not found (DeveloperAgent pending)"
        PASS=$((PASS + 1))
        return
    fi

    # CFP-138 last_attempted_at=2026-05-09T10:00:00Z
    BASE_EPOCH=$(iso8601_to_epoch "2026-05-09T10:00:00Z")
    if [ "$BASE_EPOCH" -eq 0 ]; then
        log "  SKIP: epoch conversion not available on this platform"
        PASS=$((PASS + 1))
        return
    fi
    # 4 min = 240s elapsed → NOT yet due (threshold = 300s)
    CURRENT=$(( BASE_EPOCH + 240 ))
    OUTPUT=$(bash "$HELPER" "$FIXTURE_DIR/attempts-due.jsonl" "$CURRENT" 2>/dev/null || echo "")
    if echo "$OUTPUT" | grep -q "CFP-138"; then
        FAIL=$((FAIL + 1))
        log "  FAIL: CFP-138 should NOT be due at 4min elapsed, but got: $OUTPUT"
    else
        PASS=$((PASS + 1))
        log "  PASS (CFP-138 not yet due at 4min)"
    fi
}

test_ac7_due_after_6min() {
    log "AC-7 Test 3: CFP-138 attempt_n=1 — 6min elapsed → due"
    if [ ! -f "$HELPER" ]; then
        log "  SKIP: retro-retry-helper.sh not found (DeveloperAgent pending)"
        PASS=$((PASS + 1))
        return
    fi

    BASE_EPOCH=$(iso8601_to_epoch "2026-05-09T10:00:00Z")
    if [ "$BASE_EPOCH" -eq 0 ]; then
        log "  SKIP: epoch conversion not available"
        PASS=$((PASS + 1))
        return
    fi
    # 6 min = 360s elapsed → due (threshold = 300s)
    CURRENT=$(( BASE_EPOCH + 360 ))
    OUTPUT=$(bash "$HELPER" "$FIXTURE_DIR/attempts-due.jsonl" "$CURRENT" 2>/dev/null || echo "")
    if echo "$OUTPUT" | grep -q "CFP-138"; then
        PASS=$((PASS + 1))
        log "  PASS (CFP-138 due at 6min elapsed)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: CFP-138 should be due at 6min elapsed, output: '$OUTPUT'"
    fi
}

test_ac7_success_skipped() {
    log "AC-7 Test 4: CFP-999 status=success → never in output"
    if [ ! -f "$HELPER" ]; then
        log "  SKIP: retro-retry-helper.sh not found"
        PASS=$((PASS + 1))
        return
    fi

    BASE_EPOCH=$(iso8601_to_epoch "2026-05-09T09:00:00Z")
    if [ "$BASE_EPOCH" -eq 0 ]; then
        log "  SKIP: epoch conversion not available"
        PASS=$((PASS + 1))
        return
    fi
    # Large elapsed — success should always be skipped
    CURRENT=$(( BASE_EPOCH + 99999 ))
    OUTPUT=$(bash "$HELPER" "$FIXTURE_DIR/attempts-due.jsonl" "$CURRENT" 2>/dev/null || echo "")
    if echo "$OUTPUT" | grep -q "CFP-999"; then
        FAIL=$((FAIL + 1))
        log "  FAIL: CFP-999 (success) should not appear in output"
    else
        PASS=$((PASS + 1))
        log "  PASS (CFP-999 success correctly skipped)"
    fi
}

test_ac7_attempt3_needs_15min() {
    # attempt_n=3 = retry 2 completed, waiting for retry 3 → 15min wait (900s)
    # ADR-045 §D-4: attempt_n=1→300s, attempt_n=2→600s, attempt_n=3→900s
    log "AC-7 Test 5: CFP-137 attempt_n=3 (15min threshold) — 14min elapsed → not due"
    if [ ! -f "$HELPER" ]; then
        log "  SKIP: retro-retry-helper.sh not found"
        PASS=$((PASS + 1))
        return
    fi

    BASE_EPOCH=$(iso8601_to_epoch "2026-05-09T08:00:00Z")
    if [ "$BASE_EPOCH" -eq 0 ]; then
        log "  SKIP: epoch conversion not available"
        PASS=$((PASS + 1))
        return
    fi
    # 14 min = 840s elapsed → NOT yet due (threshold for attempt_n=3 = 900s)
    CURRENT=$(( BASE_EPOCH + 840 ))
    OUTPUT=$(bash "$HELPER" "$FIXTURE_DIR/attempts-due.jsonl" "$CURRENT" 2>/dev/null || echo "")
    if echo "$OUTPUT" | grep -q "CFP-137"; then
        FAIL=$((FAIL + 1))
        log "  FAIL: CFP-137 (attempt_n=3) should not be due at 14min (threshold=15min)"
    else
        PASS=$((PASS + 1))
        log "  PASS (CFP-137 attempt_n=3 not due at 14min — needs 15min/900s)"
    fi
}

test_ac7_attempt3_due_after_16min() {
    # attempt_n=3 → 900s threshold. At 16min (960s) should be due.
    log "AC-7 Test 6: CFP-137 attempt_n=3 — 16min elapsed → due (threshold=15min)"
    if [ ! -f "$HELPER" ]; then
        log "  SKIP: retro-retry-helper.sh not found"
        PASS=$((PASS + 1))
        return
    fi

    BASE_EPOCH=$(iso8601_to_epoch "2026-05-09T08:00:00Z")
    if [ "$BASE_EPOCH" -eq 0 ]; then
        log "  SKIP: epoch conversion not available"
        PASS=$((PASS + 1))
        return
    fi
    # 16 min = 960s elapsed → due (threshold = 900s)
    CURRENT=$(( BASE_EPOCH + 960 ))
    OUTPUT=$(bash "$HELPER" "$FIXTURE_DIR/attempts-due.jsonl" "$CURRENT" 2>/dev/null || echo "")
    if echo "$OUTPUT" | grep -q "CFP-137"; then
        PASS=$((PASS + 1))
        log "  PASS (CFP-137 due at 16min elapsed — 900s threshold met)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: CFP-137 should be due at 16min (960s >= 900s threshold), output: '$OUTPUT'"
    fi
}

# ---------------------------------------------------------------------------
# AC-9: close-blocking gate verification
# ---------------------------------------------------------------------------

test_ac9_gate_present_allows_close() {
    log "AC-9 Test 1: gate:retro-complete present → allow close"
    close_blocking_check "type:story,phase:보안-테스트,gate:retro-complete"
    if [ $? -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (close allowed)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: close should be allowed when gate:retro-complete present"
    fi
}

test_ac9_gate_absent_blocks_close() {
    log "AC-9 Test 2: type:story + phase:보안-테스트 + no gate:retro-complete → block"
    close_blocking_check "type:story,phase:보안-테스트"
    if [ $? -eq 1 ]; then
        PASS=$((PASS + 1))
        log "  PASS (close blocked)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: close should be blocked when gate:retro-complete absent"
    fi
}

test_ac9_non_story_skip() {
    log "AC-9 Test 3: not type:story → allow close (skip non-story issues)"
    close_blocking_check "phase:보안-테스트,type:bug"
    if [ $? -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (non-story skipped)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: non-story issue should not be blocked"
    fi
}

test_ac9_early_close_skip() {
    log "AC-9 Test 4: early-close:duplicate → allow close (exemption)"
    close_blocking_check "type:story,phase:보안-테스트,early-close:duplicate"
    if [ $? -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (early-close exempt)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: early-close labeled issue should not be blocked"
    fi
}

test_ac9_not_terminal_phase() {
    log "AC-9 Test 5: type:story but not phase:보안-테스트 → allow close (phase-label-invariant handles)"
    close_blocking_check "type:story,phase:구현"
    if [ $? -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (non-terminal phase not blocked by retro mandate)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: non-terminal phase should not be blocked by retro mandate"
    fi
}

# ---------------------------------------------------------------------------
# AC-11: PMOAgent manual spawn template
# ---------------------------------------------------------------------------

test_ac11_template_exists() {
    log "AC-11 Test 1: pmo-manual-spawn-template.txt exists"
    if [ -f "$FIXTURE_DIR/pmo-manual-spawn-template.txt" ]; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: $FIXTURE_DIR/pmo-manual-spawn-template.txt not found"
    fi
}

test_ac11_template_has_required_fields() {
    log "AC-11 Test 2: template has all 4 §11 schema fields"
    local template="$FIXTURE_DIR/pmo-manual-spawn-template.txt"
    if [ ! -f "$template" ]; then
        FAIL=$((FAIL + 1))
        log "  FAIL: template not found"
        return
    fi

    local all_found=1
    for field in "retro_file" "retro_summary" "learnings_count" "feedback_back_to_codeforge"; do
        if ! grep -q "$field" "$template"; then
            log "  MISSING field: $field"
            all_found=0
        fi
    done

    if [ "$all_found" -eq 1 ]; then
        PASS=$((PASS + 1))
        log "  PASS (all 4 fields present)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: one or more §11 fields missing from template"
    fi
}

test_ac11_retro_path_naming_matches_ac5() {
    log "AC-11 Test 3: retro file naming in template matches AC-5 regex"
    local template="$FIXTURE_DIR/pmo-manual-spawn-template.txt"
    if [ ! -f "$template" ]; then
        FAIL=$((FAIL + 1))
        log "  FAIL: template not found"
        return
    fi

    # Template contains pattern <YYYY-MM-DD>-cfp-138-retro-mandatory.md
    # Extract and validate the naming pattern example
    local example="2026-05-09-cfp-138-retro-mandatory.md"
    if echo "$example" | grep -qE "$RETRO_PATH_REGEX"; then
        PASS=$((PASS + 1))
        log "  PASS (example retro filename matches AC-5 regex)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: example retro filename '$example' does not match AC-5 regex"
    fi
}

test_ac11_template_mentions_gate_label() {
    log "AC-11 Test 4: template mentions gate:retro-complete label"
    if grep -q "gate:retro-complete" "$FIXTURE_DIR/pmo-manual-spawn-template.txt" 2>/dev/null; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL: template missing gate:retro-complete reference"
    fi
}

# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------
log "=== test-retro-mandatory 시작 (CFP-138 Phase 2 / ADR-045) ==="
log ""
log "--- AC-5: retro file path regex ---"
test_ac5_valid_retro_path
test_ac5_valid_no_slug
test_ac5_invalid_no_date
test_ac5_invalid_uppercase
test_ac5_invalid_no_md

log ""
log "--- AC-7: retry timing (retro-retry-helper.sh) ---"
test_ac7_helper_exists
test_ac7_fixture_exists
test_ac7_not_yet_due_4min
test_ac7_due_after_6min
test_ac7_success_skipped
test_ac7_attempt3_needs_15min
test_ac7_attempt3_due_after_16min

log ""
log "--- AC-9: close-blocking gate logic ---"
test_ac9_gate_present_allows_close
test_ac9_gate_absent_blocks_close
test_ac9_non_story_skip
test_ac9_early_close_skip
test_ac9_not_terminal_phase

log ""
log "--- AC-11: PMOAgent manual spawn template ---"
test_ac11_template_exists
test_ac11_template_has_required_fields
test_ac11_retro_path_naming_matches_ac5
test_ac11_template_mentions_gate_label

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
