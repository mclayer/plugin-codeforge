#!/usr/bin/env bats
# tests/scripts/cfp-1346/check-label-registry-frozen-baseline-count-parity.bats
# CFP-1346 Phase 2 — check-label-registry-frozen-baseline-count-parity.sh unit tests (QADev)
# ADR-108 §결정 3 — label-registry-v2 description count parity lint
#
# Test cases (TC-1..TC-6):
#   TC-1 PASS  — claim count == raw post-append
#   TC-2 FAIL  — claim count drift (CFP-1302 sentinel reproduction)
#   TC-3 SKIP  — bypass label attached
#   TC-4 PASS  — prior frozen entries ignored (historical narrative scope)
#   TC-5 PASS  — non-hotfix-bypass:* "N번째" citations not caught (regex precision)
#   TC-6 META  — self-application 1st applied case dogfood (74번째)
#
# Production code binding (memory feedback_test_must_bind_to_production):
#   실제 scripts/check-label-registry-frozen-baseline-count-parity.sh 호출.
#   sed-extract 금지, inline hand-copy 금지.
#
# Mock strategy:
#   LABEL_REGISTRY_PATH = $TEST_DIR/label-registry-v2.md (fixture override)
#   CHANGED_FILES = $LABEL_REGISTRY_PATH_FRAGMENT (registry touched 강제)
#   DIFF_ADDED_LINES = added lines fixture (diff scope override)
#   BYPASS_LABEL = bypass label value (TC-3)
#
# Windows Git Bash compatibility (CFP-418 evidence):
#   single-quoted heredoc for fixture content (backslash escape inconsistency 차단)

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-label-registry-frozen-baseline-count-parity.sh"
REGISTRY_FRAGMENT="docs/inter-plugin-contracts/label-registry-v2.md"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # python3 required
  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi

  # script must exist — false (not skip) to provide genuine RED signal in TDD phase
  if [[ ! -f "$SCRIPT" ]]; then
    echo "script not found: $SCRIPT" >&2
    false  # genuine RED: test fails when production script absent
  fi

  # Set env vars for all TCs
  export LABEL_REGISTRY_PATH="$TEST_DIR/label-registry-v2.md"
  export CHANGED_FILES="$REGISTRY_FRAGMENT"
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ------------------------------------------------------------------ helpers

# make_registry N: label-registry-v2.md fixture with N hotfix-bypass:* entries
make_registry() {
  local count="$1"
  local file="$TEST_DIR/label-registry-v2.md"
  {
    printf '## §3 hotfix-bypass label entries\n\n'
    for i in $(seq 1 "$count"); do
      printf '  - name: hotfix-bypass:entry-%d\n' "$i"
      printf '    description: "entry %d"\n' "$i"
    done
  } > "$file"
}

# make_diff_added DESCRIPTION_LINE: single added line describing last entry
make_diff_added() {
  local line="$1"
  export DIFF_ADDED_LINES="$line"
}

# ------------------------------------------------------------------ TC-1: PASS — claim == raw post-append
@test "TC-1 PASS: claim count 73 == raw post-append 73" {
  make_registry 73
  make_diff_added "    description: '73번째 hotfix-bypass:* family member'"

  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"parity verified"* ]]
}

# ------------------------------------------------------------------ TC-2: FAIL — claim drift (CFP-1302 sentinel reproduction)
@test "TC-2 FAIL: claim 71 != raw post-append 73 (CFP-1302 sentinel)" {
  make_registry 73
  make_diff_added "    description: '71번째 hotfix-bypass:* family member'"

  run bash "$SCRIPT"

  # exit 2 (advisory warning tier, ADR-060 exit-code 3-tier)
  [ "$status" -eq 2 ]
  [[ "$output" == *"FAIL"* ]]
  [[ "$output" == *"71"* ]]
  [[ "$output" == *"73"* ]]
}

# ------------------------------------------------------------------ TC-3: SKIP — bypass label attached
@test "TC-3 SKIP: bypass label attached -> exit 0 + SKIPPED" {
  make_registry 73
  make_diff_added "    description: '71번째 hotfix-bypass:* family member'"
  export BYPASS_LABEL="hotfix-bypass:label-registry-frozen-baseline-count-parity"

  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"SKIPPED"* ]]
  [[ "$output" == *"bypass label"* ]]

  unset BYPASS_LABEL
}

# ------------------------------------------------------------------ TC-4: PASS — prior frozen entries ignored
@test "TC-4 PASS: prior frozen entries ignored, last entry 73 == raw 73" {
  # File has 73 entries total
  make_registry 73

  # Only NEW append lines are in diff scope:
  # Prior frozen "45번째" / "70번째" are NOT in diff added lines (historical narrative scope)
  # Only the new entry is in diff added lines
  make_diff_added "    description: '73번째 hotfix-bypass:* family member'"

  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-5: PASS — non-hotfix-bypass:* "N번째" not caught (regex precision)
@test "TC-5 PASS: non-count 'N번째' citations not caught (regex precision)" {
  make_registry 73

  # Diff contains a non-count semantic line that must NOT be caught
  # plus the correct last hotfix-bypass entry
  export DIFF_ADDED_LINES="    description: '5번째 verdict-level optional bool field'
    description: '73번째 hotfix-bypass:* family member'"

  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-6: META self-application 1st applied case (74번째)
@test "TC-6 META self-application: claim 74 == raw post-append 74" {
  # CFP-1346 Phase 1 appended 74th entry (META self-application 1st applied case)
  make_registry 74
  make_diff_added "    description: '74번째 hotfix-bypass:* family member'"

  run bash "$SCRIPT"

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}
