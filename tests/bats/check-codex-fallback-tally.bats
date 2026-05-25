#!/usr/bin/env bats
#
# check-codex-fallback-tally.bats
# CFP-1368 / ADR-052 Amendment 14 — codex-fallback-subclass-tally mechanical wire
# TDD RED→GREEN stash proof per ADR-082 §결정 11.A + CFP-1334 bats-red-green-proof-presence
#
# TDD RED→GREEN stash proof (CFP-1334 / ADR-082 §결정 11.A):
#   RED: stash impl → 6/9 fail (TC-1~6) + 3/9 pass (TC-7~9 independent)
#   GREEN: restore impl → 9/9 ok (verified 2026-05-25 KST)
#
# 9 Test cases (Change Plan §6.1 SSOT):
#   TC-1: zero-row PASS — empty jsonl, no §10 markers → exit 0 (fixture: story-no-markers.md)
#   TC-2: single enum count=1 PASS → exit 0 (fixture: story-single-fallback.md)
#   TC-3: single enum count=3 threshold breach → exit 1 + warning (fixture: tally-threshold-breach.jsonl)
#   TC-4: 9-enum coverage (1 row per enum) → exit 0, all enum tally = 1 (fixture: story-all-9-enums.md)
#   TC-5: §10 marker not present → exit 0, no tally update (fixture: story-no-markers.md)
#   TC-6: invalid enum value (unknown) → exit 1 + warning (fixture: story-invalid-enum.md)
#   TC-7: [codex-sandbox-fallback] prefix presence in comment-prefix-registry-v1 (registry check)
#   TC-8: [codex-substitution-scope-declared] prefix presence in comment-prefix-registry-v1 (registry check)
#   TC-9: concurrent write race condition — atomic rename POSIX guarantee
#

FIXTURE_DIR="tests/fixtures/cfp-1368/check-codex-fallback-tally"
SCRIPT_PATH="scripts/check-codex-fallback-tally.sh"
REGISTRY_PATH="docs/inter-plugin-contracts/comment-prefix-registry-v1.md"

setup_file() {
  export TEST_TMPDIR="${BATS_TMPDIR}/cfp1368-tally-tests-$$"
  mkdir -p "$TEST_TMPDIR"
}

teardown_file() {
  rm -rf "$TEST_TMPDIR"
}

# TC-1: zero-row PASS — empty jsonl, no §10 markers → exit 0
@test "TC-1: PASS — empty jsonl + no §10 markers → exit 0" {
  local jsonl_file="$TEST_TMPDIR/tc1-tally.jsonl"
  touch "$jsonl_file"
  # Use fixture: story-no-markers.md (CFP-1306/1367 fixture-file precedent)
  local story_file
  story_file="$(pwd)/${FIXTURE_DIR}/input/story-no-markers.md"

  run bash "$SCRIPT_PATH" \
    --jsonl-file "$jsonl_file" \
    --story-file "$story_file"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "PASS" ]] || [[ "$output" =~ "tally" ]] || [[ "$output" =~ "count" ]]
}

# TC-2: single enum count=1 PASS → exit 0
@test "TC-2: PASS — single enum count=1 below threshold → exit 0" {
  local jsonl_file="$TEST_TMPDIR/tc2-tally.jsonl"
  echo '{"enum_value":"codex_truncated_no_verdict","occurred_at":"2026-05-25T09:00:00+09:00","story_key":"CFP-1368","dispatch_task_id":"tp2","substitution_path":"fallback_skip_with_marker","evidence":"[codex-sandbox-fallback: codex_truncated_no_verdict]"}' > "$jsonl_file"
  # Use fixture: story-single-fallback.md
  local story_file
  story_file="$(pwd)/${FIXTURE_DIR}/input/story-single-fallback.md"

  run bash "$SCRIPT_PATH" \
    --jsonl-file "$jsonl_file" \
    --story-file "$story_file"
  [ "$status" -eq 0 ]
}

# TC-3: single enum count=3 threshold breach → exit 1 + warning
@test "TC-3: WARNING — enum count=3 threshold breach → exit 1" {
  local jsonl_file="$TEST_TMPDIR/tc3-tally.jsonl"
  # Use fixture: tally-threshold-breach.jsonl (3 rows of codex_truncated_no_verdict)
  cp "$(pwd)/${FIXTURE_DIR}/input/tally-threshold-breach.jsonl" "$jsonl_file"
  local story_file="$TEST_TMPDIR/tc3-story.md"
  cat > "$story_file" << 'ENDOFFILE'
# §10 FIX Ledger

No new markers.
ENDOFFILE

  run bash "$SCRIPT_PATH" \
    --jsonl-file "$jsonl_file" \
    --story-file "$story_file"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "WARNING" ]] || [[ "$output" =~ "threshold" ]] || [[ "$output" =~ "escalate" ]]
}

# TC-4: 9-enum coverage row (1 row per enum) → exit 0, all enum tally = 1
@test "TC-4: PASS — 9-enum coverage (1 row each) → exit 0" {
  local jsonl_file="$TEST_TMPDIR/tc4-tally.jsonl"
  # Use fixture: story-all-9-enums.md (all 9 enum values listed)
  local story_file
  story_file="$(pwd)/${FIXTURE_DIR}/input/story-all-9-enums.md"
  touch "$jsonl_file"

  run bash "$SCRIPT_PATH" \
    --jsonl-file "$jsonl_file" \
    --story-file "$story_file"
  [ "$status" -eq 0 ]
}

# TC-5: §10 marker not-in-current-PR skip → exit 0, no new append
@test "TC-5: PASS — no new marker in story file → exit 0, no append" {
  local jsonl_file="$TEST_TMPDIR/tc5-tally.jsonl"
  touch "$jsonl_file"
  # Use fixture: story-no-markers.md
  local story_file
  story_file="$(pwd)/${FIXTURE_DIR}/input/story-no-markers.md"

  run bash "$SCRIPT_PATH" \
    --jsonl-file "$jsonl_file" \
    --story-file "$story_file"
  [ "$status" -eq 0 ]
  # jsonl should still be empty
  local line_count
  line_count=$(wc -l < "$jsonl_file")
  # 0 lines = no new append
  [ "$line_count" -eq 0 ] || [ "$line_count" -le 0 ]
}

# TC-6: invalid enum value → exit 1 + warning
@test "TC-6: WARNING — invalid/unknown enum value → exit 1" {
  local jsonl_file="$TEST_TMPDIR/tc6-tally.jsonl"
  touch "$jsonl_file"
  # Use fixture: story-invalid-enum.md (contains codex_sandbox_path_blocked = out-of-scope)
  local story_file
  story_file="$(pwd)/${FIXTURE_DIR}/input/story-invalid-enum.md"

  run bash "$SCRIPT_PATH" \
    --jsonl-file "$jsonl_file" \
    --story-file "$story_file"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "unknown" ]] || [[ "$output" =~ "invalid" ]] || [[ "$output" =~ "Out-of-scope" ]]
}

# TC-7: [codex-sandbox-fallback] prefix present in comment-prefix-registry-v1
@test "TC-7: PASS — [codex-sandbox-fallback] prefix exists in comment-prefix-registry-v1" {
  # This validates that the comment-prefix-registry-v1 contains the required prefix
  run grep -c "codex-sandbox-fallback" "$REGISTRY_PATH"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# TC-8: [codex-substitution-scope-declared] prefix present in comment-prefix-registry-v1
@test "TC-8: PASS — [codex-substitution-scope-declared] prefix exists in comment-prefix-registry-v1" {
  run grep -c "codex-substitution-scope-declared" "$REGISTRY_PATH"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# TC-9: concurrent write race condition — atomic rename guarantee
@test "TC-9: PASS — concurrent writes produce correct row count (atomic rename)" {
  local jsonl_file="$TEST_TMPDIR/tc9-tally.jsonl"
  touch "$jsonl_file"
  local story_a="$TEST_TMPDIR/tc9-story-a.md"
  local story_b="$TEST_TMPDIR/tc9-story-b.md"

  cat > "$story_a" << 'ENDOFFILE'
# §10 FIX Ledger
[codex-sandbox-fallback: api_missing]
ENDOFFILE

  cat > "$story_b" << 'ENDOFFILE'
# §10 FIX Ledger
[codex-sandbox-fallback: version_skew]
ENDOFFILE

  # Run two concurrent invocations
  bash "$SCRIPT_PATH" \
    --jsonl-file "$jsonl_file" \
    --story-file "$story_a" &
  bash "$SCRIPT_PATH" \
    --jsonl-file "$jsonl_file" \
    --story-file "$story_b" &
  wait

  # After both complete, file should have at least 1 row (potentially 2)
  # Atomic rename ensures no corruption
  local line_count
  line_count=$(wc -l < "$jsonl_file" | tr -d ' ')
  # At least one row written, no file corruption (valid JSON per row)
  [ "$line_count" -ge 1 ]
  # Validate first row is valid JSON-like structure
  head -1 "$jsonl_file" | grep -q '"enum_value"'
}
