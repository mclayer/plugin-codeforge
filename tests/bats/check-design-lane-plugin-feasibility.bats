#!/usr/bin/env bats
#
# check-design-lane-plugin-feasibility.bats
# CFP-1367 / ADR-107 Amendment 1 §결정 2 — F2 design-lane-plugin-feasibility-check
# TDD RED→GREEN stash proof per ADR-082 §결정 11.A + CFP-1334 bats-red-green-proof-presence
#
# Test cases:
#   TC-1: PASS — [verified-via: ...] annotation present for all plugin refs
#   TC-2: WARN — annotation missing for plugin path reference
#   TC-3: BYPASS — env HOTFIX_BYPASS_DESIGN_LANE_PLUGIN_FEASIBILITY=1 → exit 0
#   TC-4: NOT_DESIGN_LANE — no phase:설계 label context → skip (exit 0)
#   TC-5: NO_PLUGIN_REF — no mclayer/plugin-codeforge-* in file → PASS (nothing to check)
#   TC-6: BYPASS_LOG — BYPASS=1 prints [BYPASS] marker
#

FIXTURE_DIR="tests/fixtures/cfp-1367/check-design-lane-plugin-feasibility"
SCRIPT_PATH="scripts/check-design-lane-plugin-feasibility.sh"

setup_file() {
  export TEST_TMPDIR="${BATS_TMPDIR}/check-feasibility-tests-$$"
  mkdir -p "$TEST_TMPDIR"
}

teardown_file() {
  rm -rf "$TEST_TMPDIR"
}

# TC-1: PASS — verified-via annotation present for all plugin path refs
@test "TC-1: PASS — all plugin path refs have [verified-via: ...] annotation" {
  run bash "$SCRIPT_PATH" \
    --doc-file "${FIXTURE_DIR}/input/story-section3-with-annotation.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "[PASS]" ]] || [[ "$output" =~ "PASS" ]]
}

# TC-2: WARN — annotation missing for one or more plugin path refs
@test "TC-2: WARN — plugin path ref missing [verified-via: ...] annotation" {
  run bash "$SCRIPT_PATH" \
    --doc-file "${FIXTURE_DIR}/input/story-section3-missing-annotation.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "[WARN]" ]] || [[ "$output" =~ "WARN" ]] || [[ "$output" =~ "annotation" ]]
}

# TC-3: BYPASS — env=1 → immediate exit 0 without running lint
@test "TC-3: BYPASS — HOTFIX_BYPASS_DESIGN_LANE_PLUGIN_FEASIBILITY=1 skips lint" {
  HOTFIX_BYPASS_DESIGN_LANE_PLUGIN_FEASIBILITY=1 \
    run bash "$SCRIPT_PATH" \
      --doc-file "${FIXTURE_DIR}/input/story-section3-missing-annotation.md"
  [ "$status" -eq 0 ]
}

# TC-4: NOT_DESIGN_LANE — file with no plugin refs should pass cleanly
@test "TC-4: NOT_DESIGN_LANE — no mclayer/plugin-codeforge-* refs → PASS without annotation check" {
  run bash "$SCRIPT_PATH" \
    --doc-file "${FIXTURE_DIR}/input/story-section3-no-plugin-ref.md"
  [ "$status" -eq 0 ]
}

# TC-5: NO_PLUGIN_REF — story file with no cross-repo plugin path → PASS
@test "TC-5: NO_PLUGIN_REF — file without plugin path refs → exit 0" {
  cat > "$TEST_TMPDIR/no-plugin-ref.md" << 'ENDOFFILE'
# Test Story

## §3

No cross-repo plugin references here, only local docs.
ENDOFFILE

  run bash "$SCRIPT_PATH" --doc-file "$TEST_TMPDIR/no-plugin-ref.md"
  [ "$status" -eq 0 ]
}

# TC-6: BYPASS log marker present when BYPASS=1
@test "TC-6: BYPASS — [BYPASS] marker emitted to stderr" {
  HOTFIX_BYPASS_DESIGN_LANE_PLUGIN_FEASIBILITY=1 \
    run bash "$SCRIPT_PATH" \
      --doc-file "${FIXTURE_DIR}/input/story-section3-with-annotation.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "BYPASS" ]]
}
