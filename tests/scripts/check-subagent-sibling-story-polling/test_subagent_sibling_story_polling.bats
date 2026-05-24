#!/usr/bin/env bats
# tests/scripts/check-subagent-sibling-story-polling/test_subagent_sibling_story_polling.bats
# CFP-1366 / ADR-073 Amendment 6 — Wave 2 mechanical wire bats fixture

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
SCRIPT="${BATS_TEST_DIRNAME}/../../../scripts/check-subagent-sibling-story-polling.sh"

setup() { unset BYPASS_SUBAGENT_SIBLING_STORY_POLLING || true; }
teardown() { unset BYPASS_SUBAGENT_SIBLING_STORY_POLLING || true; }

@test "TC-1: no sibling CFP cite → PASS exit 0" {
  run bash "${SCRIPT}" --text "Standard PR body without sibling references"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "no sibling CFP" ]]
}

@test "TC-2: sibling cite + verified-via paired → PASS exit 0" {
  run bash "${SCRIPT}" --text "Sibling CFP-1318 complete; verified-via: gh issue view CFP-1318 --json state"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "verified-via" ]]
}

@test "TC-3: sibling cite without verified-via → WARN exit 1" {
  run bash "${SCRIPT}" --text "CFP-1319 is in progress; CFP-1347 is queued"
  [ "$status" -eq 1 ]
}

@test "TC-4: own carrier CFP excluded → PASS exit 0" {
  run bash "${SCRIPT}" --text "CFP-1366 work in progress" --own-cfp CFP-1366
  [ "$status" -eq 0 ]
}

@test "TC-5: verified-via gh pr list satisfies polling → PASS" {
  run bash "${SCRIPT}" --text "Sibling CFP-1319 active; verified-via: gh pr list --search head:cfp-1319"
  [ "$status" -eq 0 ]
}

@test "TC-6: BYPASS env → PASS exit 0" {
  export BYPASS_SUBAGENT_SIBLING_STORY_POLLING=1
  run bash "${SCRIPT}" --text "CFP-1318 cited without verify"
  [ "$status" -eq 0 ]
}

@test "TC-7: missing input args → SETUP error exit 2" {
  run bash "${SCRIPT}"
  [ "$status" -eq 2 ]
}

@test "TC-8: missing input file → SETUP error exit 2" {
  run bash "${SCRIPT}" --input-file "/nonexistent/path.txt"
  [ "$status" -eq 2 ]
}
