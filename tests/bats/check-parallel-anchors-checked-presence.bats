#!/usr/bin/env bats
#
# check-parallel-anchors-checked-presence.bats — TDD fixture for CFP-1306
# review-verdict-v4 findings[].parallel_anchors_checked[] presence-grep heuristic lint
#
# ADR-060 Amendment 15 §결정 29 — 13번째 warning-tier entry
# ADR-068 I-2 cross-module propagation completeness review-verdict layer realization
# ADR-061 §결정 1 — thin bash wrapper + Python SSOT
# ADR-082 §결정 11.A — TDD RED→GREEN stash proof mandate
#
# RED→GREEN proof procedure (CFP-1334 mandate):
#   git stash push -- tests/fixtures/cfp-1306/ → run bats → ALL FAIL (RED)
#   git stash pop → run bats → ALL PASS (GREEN)
#
# 12 TCs per §8.1 Test Contract (Change Plan CFP-1306):
#   TC-1  : WARNING — candidate finding, parallel_anchors_checked absent
#   TC-2  : PASS — present, all matched: false (clean enumeration evidence)
#   TC-3  : PASS — present, matched: true (parallel anchor found)
#   TC-4  : WARNING — pattern_type enum drift (outside 5 closed-set)
#   TC-5  : WARNING — matched field missing (schema violation)
#   TC-6  : META-ERROR — malformed YAML (parse failure)
#   TC-7  : WARNING — present, empty array (declarative zero-coverage)
#   TC-8  : PASS — markdown file without fenced yaml block (scope empty)
#   TC-9  : WARNING — schema location confusion (pattern_type as findings[].type)
#   TC-10 : WARNING — non-array type (AC-14: string not array)
#   TC-11 : PASS — no findings[] (scope empty)
#   TC-12 : PASS — non-candidate finding category (boundary-completeness)

SCRIPT_PATH="scripts/check-parallel-anchors-checked-presence.sh"
FIXTURE_DIR="tests/fixtures/cfp-1306/check-parallel-anchors-checked-presence/input"

# TC-1: finding with candidate category (local_remote) but parallel_anchors_checked absent
@test "TC-1: WARNING — candidate finding (local_remote), parallel_anchors_checked absent" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc1-absent-warning.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "WARNING" ]]
  [[ "$output" =~ "parallel_anchors_checked" ]]
}

# TC-2: parallel_anchors_checked present, all matched: false (clean enumeration evidence)
@test "TC-2: PASS — parallel_anchors_checked present, all matched: false" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc2-present-clean-pass.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "PASS" ]]
}

# TC-3: parallel_anchors_checked present, matched: true (parallel anchor found)
@test "TC-3: PASS — parallel_anchors_checked present, matched: true" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc3-present-matched-pass.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "PASS" ]]
}

# TC-4: pattern_type outside 5 enum closed-set (enum drift)
@test "TC-4: WARNING — pattern_type enum drift (local_only not in closed-set)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc4-pattern-type-enum-drift.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "WARNING" ]]
  [[ "$output" =~ "enum" ]]
}

# TC-5: matched field missing in parallel_anchors_checked entry
@test "TC-5: WARNING — matched field missing (schema violation)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc5-matched-field-missing.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "WARNING" ]]
  [[ "$output" =~ "matched" ]]
}

# TC-6: malformed YAML input
@test "TC-6: META-ERROR — malformed YAML (parse failure)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc6-malformed-yaml.txt"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "META-ERROR" || "$output" =~ "parse" || "$output" =~ "error" ]]
}

# TC-7: parallel_anchors_checked present but empty array
@test "TC-7: WARNING — parallel_anchors_checked present but empty (declarative zero-coverage)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc7-present-empty-array.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "WARNING" ]]
  [[ "$output" =~ "zero-coverage" || "$output" =~ "empty" ]]
}

# TC-8: markdown file without fenced yaml block
@test "TC-8: PASS — markdown file without fenced yaml block (scope empty)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc8-markdown-no-yaml-block.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "PASS" ]]
}

# TC-9: schema location confusion — pattern_type value as findings[].type
@test "TC-9: WARNING — schema location confusion (pattern_type used as findings[].type)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc9-schema-location-confusion.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "WARNING" ]]
  [[ "$output" =~ "confusion" || "$output" =~ "location" || "$output" =~ "type" ]]
}

# TC-10: non-array type (string instead of array) — AC-14
@test "TC-10: WARNING — parallel_anchors_checked is string (expected array, AC-14)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc10-non-array-type.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "WARNING" ]]
  [[ "$output" =~ "array" || "$output" =~ "type" ]]
}

# TC-11: no findings array at all
@test "TC-11: PASS — no findings[] array (lint scope empty)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc11-no-findings.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "PASS" ]]
}

# TC-12: finding with non-candidate category (boundary-completeness)
@test "TC-12: PASS — non-candidate finding category (boundary-completeness, skip)" {
  run bash "$SCRIPT_PATH" "$FIXTURE_DIR/tc12-non-candidate-finding.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "PASS" ]]
}
