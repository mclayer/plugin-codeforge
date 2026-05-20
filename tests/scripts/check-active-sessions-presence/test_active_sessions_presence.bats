#!/usr/bin/env bats
# CFP-1057 / ADR-085 §결정 2 — active-sessions-presence bats fixture

setup() {
  TMPDIR_TEST="$(mktemp -d)"
  SCRIPT="${BATS_TEST_DIRNAME}/../../../scripts/check-active-sessions-presence.sh"
}

teardown() {
  rm -rf "${TMPDIR_TEST}"
}

@test "Story file absent — advisory pass" {
  run bash "${SCRIPT}" --story-file "${TMPDIR_TEST}/nonexistent.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[advisory]"* ]]
}

@test "Story file frontmatter missing active_sessions — advisory pass (backward-compat)" {
  cat > "${TMPDIR_TEST}/CFP-X.md" << 'EOF'
---
key: CFP-X
title: test
---

body
EOF
  run bash "${SCRIPT}" --story-file "${TMPDIR_TEST}/CFP-X.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[advisory]"* ]]
}

@test "Story file with active_sessions: field present — pass" {
  cat > "${TMPDIR_TEST}/CFP-Y.md" << 'EOF'
---
key: CFP-Y
active_sessions: []
---

body
EOF
  run bash "${SCRIPT}" --story-file "${TMPDIR_TEST}/CFP-Y.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[pass]"* ]]
}

@test "Issue body with empty active_sessions block — pass" {
  run bash "${SCRIPT}" --issue-body $'<!-- active_sessions -->\n[]\n<!-- /active_sessions -->'
  [ "$status" -eq 0 ]
  [[ "$output" == *"[pass]"* ]]
}

@test "Issue body with valid 5-tuple session — pass" {
  run bash "${SCRIPT}" --issue-body $'<!-- active_sessions -->\n[{"git_identity":"a@b.c","worktree_path":"/tmp/x","entry_phase":"design","entered_at_kst":"2026-05-20T10:00:00+09:00","last_heartbeat_kst":"2026-05-20T10:30:00+09:00"}]\n<!-- /active_sessions -->'
  [ "$status" -eq 0 ]
  [[ "$output" == *"[pass]"* ]]
  [[ "$output" == *"1 entry"* ]]
}

@test "Issue body missing required field — fail" {
  run bash "${SCRIPT}" --issue-body $'<!-- active_sessions -->\n[{"git_identity":"a@b.c"}]\n<!-- /active_sessions -->'
  [ "$status" -eq 1 ]
  [[ "$output" == *"[fail]"* ]]
  [[ "$output" == *"missing required fields"* ]]
}

@test "Issue body malformed JSON — fail" {
  run bash "${SCRIPT}" --issue-body $'<!-- active_sessions -->\n[{broken\n<!-- /active_sessions -->'
  [ "$status" -eq 1 ]
  [[ "$output" == *"[fail]"* ]]
  [[ "$output" == *"malformed JSON"* ]]
}

@test "Issue body with invalid KST timestamp format — fail" {
  run bash "${SCRIPT}" --issue-body $'<!-- active_sessions -->\n[{"git_identity":"a","worktree_path":"/","entry_phase":"x","entered_at_kst":"2026-05-20","last_heartbeat_kst":"2026-05-20"}]\n<!-- /active_sessions -->'
  [ "$status" -eq 1 ]
  [[ "$output" == *"ISO 8601 KST"* ]]
}

@test "BYPASS env skips check" {
  BYPASS_ACTIVE_SESSIONS_PRESENCE=1 run bash "${SCRIPT}" --story-file "${TMPDIR_TEST}/nonexistent.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"BYPASS_ACTIVE_SESSIONS_PRESENCE=1"* ]]
}
