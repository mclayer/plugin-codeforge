#!/usr/bin/env bats
#
# check-plugin-declarative-seed-byte-parity.bats
# CFP-1367 / ADR-107 Amendment 1 §결정 1 — F1 plugin-declarative-seed-byte-parity-check
# TDD RED→GREEN stash proof per ADR-082 §결정 11.A + CFP-1334 bats-red-green-proof-presence
#
# Test cases:
#   TC-1: PASS — byte-parity 정합 (wrapper SSOT ↔ plugin seed identical sections)
#   TC-2: WARN — drift 발견 (extra field in plugin vs SSOT)
#   TC-3: BYPASS — env HOTFIX_BYPASS_PLUGIN_DECLARATIVE_SEED_BYTE_PARITY=1 → exit 0
#   TC-4: MALFORMED — invalid YAML frontmatter → exit 1
#   TC-5: NO_FILES — no changed files → exit 0 (INFO)
#   TC-6: BYPASS_LOG — BYPASS=1 prints [BYPASS] marker
#

FIXTURE_DIR="tests/fixtures/cfp-1367/check-plugin-declarative-seed-byte-parity"
SCRIPT_PATH="scripts/check-plugin-declarative-seed-byte-parity.sh"

setup_file() {
  export TEST_TMPDIR="${BATS_TMPDIR}/check-seed-parity-tests-$$"
  mkdir -p "$TEST_TMPDIR"
}

teardown_file() {
  rm -rf "$TEST_TMPDIR"
}

# TC-1: PASS — matching deploy section fields (byte-parity 정합)
@test "TC-1: PASS — matching wrapper SSOT and plugin seed sections" {
  # Use fixture files: project-config-schema-deploy-sample.md (SSOT) + deploy-mechanism-sample-parity.md (plugin)
  run bash "$SCRIPT_PATH" \
    --ssot-file "${FIXTURE_DIR}/input/project-config-schema-deploy-sample.md" \
    --plugin-file "${FIXTURE_DIR}/input/deploy-mechanism-sample-parity.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "[PASS]" ]] || [[ "$output" =~ "PASS" ]]
}

# TC-2: WARN — drift detected (plugin has extra_field_drift not in SSOT)
@test "TC-2: WARN — drift detected between SSOT and plugin seed" {
  run bash "$SCRIPT_PATH" \
    --ssot-file "${FIXTURE_DIR}/input/project-config-schema-deploy-sample.md" \
    --plugin-file "${FIXTURE_DIR}/input/deploy-mechanism-sample-drift.md"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "[WARN]" ]] || [[ "$output" =~ "WARN" ]] || [[ "$output" =~ "drift" ]]
}

# TC-3: BYPASS — env=1 → immediate exit 0 without running lint
@test "TC-3: BYPASS — HOTFIX_BYPASS_PLUGIN_DECLARATIVE_SEED_BYTE_PARITY=1 skips lint" {
  HOTFIX_BYPASS_PLUGIN_DECLARATIVE_SEED_BYTE_PARITY=1 \
    run bash "$SCRIPT_PATH" \
      --ssot-file "${FIXTURE_DIR}/input/project-config-schema-deploy-sample.md" \
      --plugin-file "${FIXTURE_DIR}/input/deploy-mechanism-sample-drift.md"
  [ "$status" -eq 0 ]
}

# TC-4: MALFORMED — invalid YAML frontmatter → exit 1 (hard error)
@test "TC-4: MALFORMED — invalid YAML in plugin file → exit 1" {
  cat > "$TEST_TMPDIR/malformed.md" << 'ENDOFFILE'
---
title: malformed
invalid_yaml: [unclosed bracket
---
# Content
ENDOFFILE

  run bash "$SCRIPT_PATH" \
    --ssot-file "${FIXTURE_DIR}/input/project-config-schema-deploy-sample.md" \
    --plugin-file "$TEST_TMPDIR/malformed.md"
  [ "$status" -eq 1 ]
}

# TC-5: NO_FILES — missing files → non-zero or INFO message
@test "TC-5: NO_FILES — missing plugin file path → error or INFO" {
  run bash "$SCRIPT_PATH" \
    --ssot-file "${FIXTURE_DIR}/input/project-config-schema-deploy-sample.md" \
    --plugin-file "/nonexistent/path/to/plugin.md"
  # either exit 2 (setup error) or exit 0 with INFO
  [ "$status" -le 2 ]
}

# TC-6: BYPASS log marker present when BYPASS=1
@test "TC-6: BYPASS — [BYPASS] marker emitted to stderr" {
  HOTFIX_BYPASS_PLUGIN_DECLARATIVE_SEED_BYTE_PARITY=1 \
    run bash "$SCRIPT_PATH" \
      --ssot-file "${FIXTURE_DIR}/input/project-config-schema-deploy-sample.md" \
      --plugin-file "${FIXTURE_DIR}/input/deploy-mechanism-sample-parity.md"
  [ "$status" -eq 0 ]
  # BYPASS marker in combined output (bats merges stderr+stdout by default)
  [[ "$output" =~ "BYPASS" ]]
}
