#!/usr/bin/env bats
# CFP-1057 / ADR-085 §결정 3 — lane-entry-ownership-verify bats fixture

setup() {
  SCRIPT="${BATS_TEST_DIRNAME}/../../../scripts/check-lane-entry-ownership.sh"
}

@test "BYPASS env skips check" {
  BYPASS_LANE_ENTRY_OWNERSHIP=1 run bash "${SCRIPT}" --branch some-branch
  [ "$status" -eq 0 ]
  [[ "$output" == *"BYPASS_LANE_ENTRY_OWNERSHIP=1"* ]]
}

@test "Missing --branch arg — error" {
  run bash "${SCRIPT}"
  [ "$status" -ne 0 ]
}

@test "Help-like invocation shows error gracefully" {
  run bash "${SCRIPT}" --branch ""
  # empty branch should be accepted by argparse but produce graceful degradation
  # exit 2 from graceful degradation OR 0 from advisory
  [ "$status" -eq 2 ] || [ "$status" -eq 0 ]
}

@test "Graceful degradation when gh CLI unavailable (PATH-stripped)" {
  PATH="/usr/bin" run bash "${SCRIPT}" --branch nonexistent-branch-xyz-test
  # gh may or may not be in /usr/bin depending on environment
  # If gh absent → exit 2 graceful degradation
  # If gh present → likely [advisory] no open PR found → exit 0
  [ "$status" -eq 0 ] || [ "$status" -eq 2 ]
}
