#!/usr/bin/env bats
# tests/scripts/check-worktree-self-ownership/test_worktree_self_ownership.bats
# CFP-1366 / ADR-073 Amendment 3 — Wave 2 mechanical wire bats fixture

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
SCRIPT="${BATS_TEST_DIRNAME}/../../../scripts/check-worktree-self-ownership.sh"

setup() { unset BYPASS_WORKTREE_SELF_OWNERSHIP || true; }
teardown() { unset BYPASS_WORKTREE_SELF_OWNERSHIP || true; }

@test "TC-1: no claim → PASS exit 0" {
  run bash "${SCRIPT}" --text "Standard PR body without any conflict claim"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "no ownership claim" ]]
}

@test "TC-2: claim + verified-via paired → PASS exit 0" {
  run bash "${SCRIPT}" --text "parallel_session_conflict detected; verified-via: git worktree list --porcelain"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "paired" ]]
}

@test "TC-3: claim without verified-via → WARN exit 1" {
  run bash "${SCRIPT}" --text "parallel_session_conflict found in branch X"
  [ "$status" -eq 1 ]
}

@test "TC-4: cross_session_collision claim → WARN exit 1" {
  run bash "${SCRIPT}" --text "cross_session_collision detected"
  [ "$status" -eq 1 ]
}

@test "TC-5: stand_down_recommended + git reflog verified → PASS" {
  run bash "${SCRIPT}" --text "stand_down_recommended; verified-via: git reflog show <branch>"
  [ "$status" -eq 0 ]
}

@test "TC-6: BYPASS env → PASS exit 0" {
  export BYPASS_WORKTREE_SELF_OWNERSHIP=1
  run bash "${SCRIPT}" --text "parallel_session_conflict detected"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "BYPASS" ]]
}

@test "TC-7: missing input args → SETUP error exit 2" {
  run bash "${SCRIPT}"
  [ "$status" -eq 2 ]
}

@test "TC-8: missing input file → SETUP error exit 2" {
  run bash "${SCRIPT}" --input-file "/nonexistent/path/xyz.txt"
  [ "$status" -eq 2 ]
}
