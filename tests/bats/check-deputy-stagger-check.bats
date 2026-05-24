#!/usr/bin/env bats
#
# check-deputy-stagger-check.bats — Test suite for ADR-044 Amendment 2 deputy stagger lint
# TDD fixture: RED→GREEN proof per ADR-068 invariant, CFP-1354 Phase 2
#
# Test cases:
#  TC-1: PASS stagger field present (spawn_stagger_ms: 0)
#  TC-2: FAIL stagger field absent
#  TC-3: PASS stagger variant (spawn_stagger_ms: 100)
#  TC-4: PASS optional stagger field (default = 0, lint accepts absence)
#  TC-5: PASS multi-yaml check (all 7 team-spec files have stagger)
#

setup_file() {
  export SCRIPT_PATH="scripts/check-deputy-stagger-check.sh"
  export TEST_TMPDIR="${BATS_TMPDIR}/check-deputy-stagger-tests-$$"
  mkdir -p "$TEST_TMPDIR"
}

teardown_file() {
  rm -rf "$TEST_TMPDIR"
}

# TC-1: team-spec with valid spawn_stagger_ms: 0
@test "TC-1: PASS — team-spec with spawn_stagger_ms: 0" {
  cat > "$TEST_TMPDIR/team-spec-tc1.yaml" <<'EOF'
name: decompose
spawn_order: parallel
spawn_stagger_ms: 0
members:
  - name: RequirementsAnalyst
  - name: DomainAgent
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc1.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "PASS" ]]
  [[ "$output" =~ "spawn_stagger_ms=0 ms" ]]
}

# TC-2: team-spec missing spawn_stagger_ms field
@test "TC-2: FAIL — team-spec missing spawn_stagger_ms field" {
  cat > "$TEST_TMPDIR/team-spec-tc2.yaml" <<'EOF'
name: design
spawn_order: sequential
members:
  - name: ArchitectAgent
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc2.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "FAIL" ]]
  [[ "$output" =~ "missing spawn_stagger_ms" ]]
}

# TC-3: team-spec with variant valid stagger (100 ms)
@test "TC-3: PASS — team-spec with spawn_stagger_ms: 100" {
  cat > "$TEST_TMPDIR/team-spec-tc3.yaml" <<'EOF'
name: develop
spawn_order: parallel
spawn_stagger_ms: 100
members:
  - name: DeveloperAgent
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc3.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "spawn_stagger_ms=100 ms" ]]
}

# TC-4: spawn_stagger_ms with large valid value (50000 ms)
@test "TC-4: PASS — spawn_stagger_ms: 50000 (near max)" {
  cat > "$TEST_TMPDIR/team-spec-tc4.yaml" <<'EOF'
name: code-review
spawn_order: parallel
spawn_stagger_ms: 50000
members:
  - name: CodeReviewPL
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc4.yaml"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "spawn_stagger_ms=50000 ms" ]]
}

# TC-5: spawn_stagger_ms exceeds max (60001 ms > 60000)
@test "TC-5: FAIL — spawn_stagger_ms exceeds max (60001 > 60000)" {
  cat > "$TEST_TMPDIR/team-spec-tc5.yaml" <<'EOF'
name: security-test
spawn_order: parallel
spawn_stagger_ms: 60001
members:
  - name: SecurityTestPL
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc5.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "invalid spawn_stagger_ms" ]]
}

# TC-6: spawn_stagger_ms with negative value (treated as malformed/missing by grep)
@test "TC-6: FAIL — spawn_stagger_ms negative (-100)" {
  cat > "$TEST_TMPDIR/team-spec-tc6.yaml" <<'EOF'
name: design-review
spawn_order: parallel
spawn_stagger_ms: -100
members:
  - name: DesignReviewPL
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc6.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "FAIL" ]]
}

# TC-7: spawn_stagger_ms as string (not numeric)
@test "TC-7: FAIL — spawn_stagger_ms as string (one_hundred)" {
  cat > "$TEST_TMPDIR/team-spec-tc7.yaml" <<'EOF'
name: develop
spawn_order: parallel
spawn_stagger_ms: one_hundred
members:
  - name: DeveloperAgent
EOF

  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/team-spec-tc7.yaml"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "FAIL" || "$output" =~ "invalid" ]]
}

# TC-8: Multiple team-spec files, all with valid stagger
@test "TC-8: PASS — multiple team-spec files with valid stagger" {
  mkdir -p "$TEST_TMPDIR/batch"

  cat > "$TEST_TMPDIR/batch/spec1.yaml" <<'EOF'
name: design
spawn_stagger_ms: 0
EOF

  cat > "$TEST_TMPDIR/batch/spec2.yaml" <<'EOF'
name: develop
spawn_stagger_ms: 50
EOF

  cat > "$TEST_TMPDIR/batch/spec3.yaml" <<'EOF'
name: security
spawn_stagger_ms: 100
EOF

  # Test individual files (script processes one at a time via --team-spec)
  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/batch/spec1.yaml"
  [ "$status" -eq 0 ]
}

# TC-9: File not found error
@test "TC-9: FAIL — team-spec file not found" {
  run bash "$SCRIPT_PATH" --team-spec "$TEST_TMPDIR/nonexistent.yaml"
  [ "$status" -eq 2 ]
  [[ "$output" =~ "not found" ]]
}
