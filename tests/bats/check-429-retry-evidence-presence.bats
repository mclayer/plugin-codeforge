#!/usr/bin/env bats
#
# check-429-retry-evidence-presence.bats — Test suite for ADR-109 429 retry marker lint
# TDD fixture: RED→GREEN proof per ADR-068 invariant, CFP-1354 Phase 2
#
# Test cases:
#  TC-1: PASS marker present (count=2, final_status=success)
#  TC-2: FAIL marker absent
#  TC-3: PASS marker variant (count=10, final_status=failed)
#  TC-4: FAIL invalid enum (final_status=unknown)
#  TC-5: FAIL malformed marker
#  TC-6: PASS multiple markers
#

setup_file() {
  export SCRIPT_PATH="scripts/check-429-retry-evidence-presence.sh"
  export TEST_TMPDIR="${BATS_TMPDIR}/check-429-tests-$$"
  mkdir -p "$TEST_TMPDIR"
}

teardown_file() {
  rm -rf "$TEST_TMPDIR"
}

# TC-1: §14 with valid marker (count=2, success)
@test "TC-1: PASS — valid 429 marker with count=2, final_status=success" {
  cat > "$TEST_TMPDIR/story-tc1.md" <<'EOF'
# CFP-1354 Test Story

## §14 Lane Evidence

| Lane | Start | End | Notes |
|------|-------|-----|-------|
| DeveloperPL | 2026-05-24T10:00:00+09:00 | 2026-05-24T11:00:00+09:00 | [429-auto-retry: count=2, final_status=success] |

EOF

  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/story-tc1.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "429 marker found" ]]
}

# TC-2: §14 missing 429 marker entirely
@test "TC-2: FAIL — no 429 marker in §14" {
  cat > "$TEST_TMPDIR/story-tc2.md" <<'EOF'
# CFP-1354 Test Story

## §14 Lane Evidence

| Lane | Start | End | Notes |
|------|-------|-----|-------|
| DeveloperPL | 2026-05-24T10:00:00+09:00 | 2026-05-24T11:00:00+09:00 | Completed without incident |

EOF

  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/story-tc2.md"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "FAIL" ]]
  [[ "$output" =~ "missing 429 marker" ]]
}

# TC-3: §14 with variant marker (count=10, failed)
@test "TC-3: PASS — variant marker with count=10, final_status=failed" {
  cat > "$TEST_TMPDIR/story-tc3.md" <<'EOF'
# CFP-1354 Test Story

## §14 Lane Evidence

| Lane | Start | End | Notes |
|------|-------|-----|-------|
| DeveloperPL | 2026-05-24T10:00:00+09:00 | 2026-05-24T11:30:00+09:00 | [429-auto-retry: count=10, final_status=failed] Manual override applied. |

EOF

  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/story-tc3.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "429 marker found" ]]
}

# TC-4: §14 with malformed enum (final_status=unknown, invalid)
@test "TC-4: FAIL — invalid final_status enum value (unknown)" {
  cat > "$TEST_TMPDIR/story-tc4.md" <<'EOF'
# CFP-1354 Test Story

## §14 Lane Evidence

| Lane | Start | End | Notes |
|------|-------|-----|-------|
| DeveloperPL | 2026-05-24T10:00:00+09:00 | 2026-05-24T11:00:00+09:00 | [429-auto-retry: count=5, final_status=unknown] |

EOF

  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/story-tc4.md"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "marker format invalid" ]]
}

# TC-5: §14 with completely malformed marker
@test "TC-5: FAIL — malformed marker syntax" {
  cat > "$TEST_TMPDIR/story-tc5.md" <<'EOF'
# CFP-1354 Test Story

## §14 Lane Evidence

| Lane | Start | End | Notes |
|------|-------|-----|-------|
| DeveloperPL | 2026-05-24T10:00:00+09:00 | 2026-05-24T11:00:00+09:00 | [429-auto-retry count=3 status=success] |

EOF

  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/story-tc5.md"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "marker format invalid" ]]
}

# TC-6: §14 with multiple 429 markers (both should match)
@test "TC-6: PASS — multiple 429 markers in §14" {
  cat > "$TEST_TMPDIR/story-tc6.md" <<'EOF'
# CFP-1354 Test Story

## §14 Lane Evidence

| Lane | Start | End | Notes |
|------|-------|-----|-------|
| DeveloperPL | 2026-05-24T10:00:00+09:00 | 2026-05-24T11:00:00+09:00 | [429-auto-retry: count=2, final_status=success] |
| DesignReviewPL | 2026-05-24T11:15:00+09:00 | 2026-05-24T12:00:00+09:00 | [429-auto-retry: count=1, final_status=success] |

EOF

  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/story-tc6.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "429 marker found" ]]
}

# TC-7: Story file without §14 (early-stage story, should PASS)
@test "TC-7: PASS — story file without §14 section (early-stage)" {
  cat > "$TEST_TMPDIR/story-tc7.md" <<'EOF'
# CFP-1354 Early Stage

## §1 Summary

This is an early-stage story without §14 yet.

## §3 Acceptance Criteria

- Criteria 1

EOF

  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/story-tc7.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "early-stage story" || "$output" =~ "PASS" ]]
}

# TC-8: Non-existent story file
@test "TC-8: FAIL — story file not found" {
  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/nonexistent.md"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "not found" ]]
}
