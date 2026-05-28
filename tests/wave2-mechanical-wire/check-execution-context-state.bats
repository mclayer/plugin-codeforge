#!/usr/bin/env bats
# CFP-1787 — ADR-082 Amendment 33 sub-scope 1-V execution_context_reconciliation Wave 2 mechanical wire
# Lint script: scripts/lib/check_execution_context_state.py (exit 0/1/2)

setup() {
  export CBL_SKIP_ISSUE_CREATE=1
  export FIXTURE_DIR="$(mktemp -d)"
}

teardown() {
  rm -rf "${FIXTURE_DIR}"
}

@test "TC-1: 5 field present → exit 0 PASS" {
  cat > "${FIXTURE_DIR}/packet.json" <<'EOF'
{
  "execution_context_state": {
    "working_dir_abs_path": "/home/user/repo",
    "target_write_repo": "mclayer/codeforge-internal-docs",
    "staged_files_required": ["plugin-codeforge/specs/CFP-NNN.md"],
    "branch_required": "cfp-NNN-slug",
    "remote_sync_required": "pull"
  }
}
EOF
  run python scripts/lib/check_execution_context_state.py "${FIXTURE_DIR}/packet.json"
  [ "$status" -eq 0 ]
}

@test "TC-2: 4 field present (staged_files_required missing) → exit 1 missing field" {
  cat > "${FIXTURE_DIR}/packet.json" <<'EOF'
{
  "execution_context_state": {
    "working_dir_abs_path": "/home/user/repo",
    "target_write_repo": "mclayer/codeforge-internal-docs",
    "branch_required": "cfp-NNN-slug",
    "remote_sync_required": "N/A"
  }
}
EOF
  run python scripts/lib/check_execution_context_state.py "${FIXTURE_DIR}/packet.json"
  [ "$status" -eq 1 ]
  [[ "$output" == *"staged_files_required"* ]]
}

@test "TC-3: schema invalid (remote_sync_required = 'invalid_enum_value') → exit 2 schema invalid" {
  cat > "${FIXTURE_DIR}/packet.json" <<'EOF'
{
  "execution_context_state": {
    "working_dir_abs_path": "/home/user/repo",
    "target_write_repo": "mclayer/codeforge-internal-docs",
    "staged_files_required": ["file.md"],
    "branch_required": "cfp-NNN-slug",
    "remote_sync_required": "invalid_value"
  }
}
EOF
  run python scripts/lib/check_execution_context_state.py "${FIXTURE_DIR}/packet.json"
  [ "$status" -eq 2 ]
  [[ "$output" == *"remote_sync_required"* ]]
  [[ "$output" == *"enum"* ]]
}

@test "TC-4: execution_context_state field 자체 absent → exit 1 missing field" {
  echo '{"other_field": "value"}' > "${FIXTURE_DIR}/packet.json"
  run python scripts/lib/check_execution_context_state.py "${FIXTURE_DIR}/packet.json"
  [ "$status" -eq 1 ]
  [[ "$output" == *"execution_context_state"* ]]
}
