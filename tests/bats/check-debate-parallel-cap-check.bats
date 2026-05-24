#!/usr/bin/env bats
#
# check-debate-parallel-cap-check.bats — Test suite for ADR-044 Amendment 2 parallel spawn cap lint
# TDD fixture: RED→GREEN proof per ADR-068 invariant, CFP-1354 Phase 2
#
# Test cases:
#  TC-1: PASS cap field present (parallel_spawn_cap: 7)
#  TC-2: FAIL cap field absent
#  TC-3: PASS variant cap value (parallel_spawn_cap: 3)
#  TC-4: FAIL cap type error (string instead of int)
#  TC-5: PASS multi-yaml check (all 7 team-spec files have cap)
#

setup_file() {
  export SCRIPT_PATH="scripts/check-debate-parallel-cap-check.sh"
  export TEST_TMPDIR="${BATS_TMPDIR}/check-debate-cap-tests-$$"
  mkdir -p "$TEST_TMPDIR"
}

teardown_file() {
  rm -rf "$TEST_TMPDIR"
}

# TC-1: team-spec with valid parallel_spawn_cap: 7
@test "TC-1: PASS — team-spec with parallel_spawn_cap: 7" {
  cat > "$TEST_TMPDIR/team-spec-tc1.yaml" <<'EOF'
name: decompose
spawn_order: parallel
parallel_spawn_cap: 7
members:
  - name: RequirementsAnalyst
  - name: DomainAgent
  - name: ChangeImpactAgent
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc1.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "PASS" ]]
  [[ "$output" =~ "parallel_spawn_cap=7" ]]
}

# TC-2: team-spec missing parallel_spawn_cap field
@test "TC-2: FAIL — team-spec missing parallel_spawn_cap field" {
  cat > "$TEST_TMPDIR/team-spec-tc2.yaml" <<'EOF'
name: design
spawn_order: sequential
members:
  - name: ArchitectAgent
  - name: SecurityArch
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc2.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "FAIL" ]]
  [[ "$output" =~ "missing parallel_spawn_cap" ]]
}

# TC-3: team-spec with variant valid cap (3)
@test "TC-3: PASS — team-spec with parallel_spawn_cap: 3" {
  cat > "$TEST_TMPDIR/team-spec-tc3.yaml" <<'EOF'
name: develop
spawn_order: parallel
parallel_spawn_cap: 3
members:
  - name: DeveloperAgent
  - name: QADeveloperAgent
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc3.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "parallel_spawn_cap=3" ]]
}

# TC-4: team-spec with string cap value (invalid type)
@test "TC-4: FAIL — parallel_spawn_cap as string (seven)" {
  cat > "$TEST_TMPDIR/team-spec-tc4.yaml" <<'EOF'
name: code-review
spawn_order: parallel
parallel_spawn_cap: "seven"
members:
  - name: CodeReviewPL
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc4.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "FAIL" || "$output" =~ "invalid" ]]
}

# TC-5: parallel_spawn_cap value out of valid range (8)
@test "TC-5: FAIL — parallel_spawn_cap exceeds max (8 > 7)" {
  cat > "$TEST_TMPDIR/team-spec-tc5.yaml" <<'EOF'
name: security-test
spawn_order: parallel
parallel_spawn_cap: 8
members:
  - name: SecurityTestPL
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc5.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "invalid parallel_spawn_cap" ]]
}

# TC-6: parallel_spawn_cap = 0 (below minimum)
@test "TC-6: FAIL — parallel_spawn_cap below minimum (0 < 1)" {
  cat > "$TEST_TMPDIR/team-spec-tc6.yaml" <<'EOF'
name: design-review
spawn_order: parallel
parallel_spawn_cap: 0
members:
  - name: DesignReviewPL
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc6.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "invalid" ]]
}

# TC-7: Boundary: parallel_spawn_cap = 1 (minimum valid)
@test "TC-7: PASS — parallel_spawn_cap: 1 (minimum valid)" {
  cat > "$TEST_TMPDIR/team-spec-tc7.yaml" <<'EOF'
name: minimal-spawn
parallel_spawn_cap: 1
members:
  - name: SingleAgent
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc7.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "parallel_spawn_cap=1" ]]
}

# TC-8: File not found error
@test "TC-8: FAIL — team-spec file not found" {
  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/nonexistent.yaml"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "not found" ]]
}
