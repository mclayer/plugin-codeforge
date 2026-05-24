#!/usr/bin/env bats
# tests/scripts/check-mcp-token-freshness/test_mcp_token_freshness.bats
# CFP-1366 / ADR-073 Amendment 8 — Wave 2 mechanical wire bats fixture

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
SCRIPT="${BATS_TEST_DIRNAME}/../../../scripts/check-mcp-token-freshness.sh"

setup() { unset BYPASS_MCP_TOKEN_FRESHNESS || true; }
teardown() { unset BYPASS_MCP_TOKEN_FRESHNESS || true; }

@test "TC-1: no MCP usage → PASS exit 0" {
  run bash "${SCRIPT}" --text "Standard PR body without MCP references"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "no active MCP" ]]
}

@test "TC-2: MCP usage + freshness annotation → PASS exit 0" {
  run bash "${SCRIPT}" --text "Using mcp__github__list_issues. mcp_token_freshness_verified: true"
  [ "$status" -eq 0 ]
  [[ "$output" =~ "paired" ]]
}

@test "TC-3: MCP usage without freshness annotation → WARN exit 1" {
  run bash "${SCRIPT}" --text "Calling mcp__github__create_pull_request to open PR"
  [ "$status" -eq 1 ]
}

@test "TC-4: MCP plugin tool usage → WARN exit 1" {
  run bash "${SCRIPT}" --text "mcp__plugin_atlassian_atlassian__createConfluencePage invoked"
  [ "$status" -eq 1 ]
}

@test "TC-5: verified-via /mcp satisfies → PASS" {
  run bash "${SCRIPT}" --text "mcp__github__issue_read; verified-via: /mcp re-auth session age 5min"
  [ "$status" -eq 0 ]
}

@test "TC-6: BYPASS env → PASS exit 0" {
  export BYPASS_MCP_TOKEN_FRESHNESS=1
  run bash "${SCRIPT}" --text "mcp__github__list_pulls without freshness"
  [ "$status" -eq 0 ]
}

@test "TC-7: missing input args → SETUP error exit 2" {
  run bash "${SCRIPT}"
  [ "$status" -eq 2 ]
}

@test "TC-8: doc context exempt (ADR + Change Plan + inline code) → PASS" {
  run bash "${SCRIPT}" --text "ADR-073 Amendment 8 references \`mcp__github__list_issues\` Change Plan defines deferred-followup"
  [ "$status" -eq 0 ]
}
