#!/usr/bin/env bats
# tests/scripts/test-check-bypass-label-counter.bats
# CFP-825 Phase 2 -- check-bypass-label-counter.py / .sh unit tests (TDD red phase)
# Change Plan §8 Test Contract verbatim
#
# Test cases (TC-1..TC-5):
#   TC-1 (happy):     per-(plugin,label) signature 3 merged PR -> Issue create 1 time
#   TC-2 (threshold): signature 2 merged PR (below threshold) -> no Issue create
#   TC-3 (dedup):     existing open carrier Issue for same signature -> no duplicate Issue
#   TC-4 (exempt):    hotfix-bypass:bypass-label-counter or hotfix-bypass:exempt:* -> count excluded
#   TC-5 (multi-entry): multiple (plugin,label) signatures reach threshold -> independent Issues
#
# Mock strategy: CBL_MOCK_PRS_JSON + CBL_MOCK_DEDUP_COUNT env vars (Python script test overrides)
#   CBL_SKIP_ISSUE_CREATE=1 -> Issue create suppressed (dry-run / TC mode)
#   CBL_MOCK_PRS_JSON=<newline-delimited-JSON> -> merged PR list override (gh api bypass)
#   CBL_MOCK_DEDUP_COUNT=<int> -> dedup search result total_count override
#
# Windows Git Bash compatibility (CFP-418 evidence):
#   - single-quoted heredoc for stub scripts (backslash escape inconsistency avoidance)
#   - CBL_MOCK_PRS_JSON via export (no subshell quoting issues)
#   - bats 'run' captures stdout/stderr correctly on Git Bash

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-bypass-label-counter.sh"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # python3 required
  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ------------------------------------------------------------------ TC-1: happy path -- 3 PR -> Issue create 1 time
@test "TC-1: per-(plugin,label) signature 3 merged PR -- Issue create called once" {
  # CBL_MOCK_PRS_JSON: 3 merged PRs all with hotfix-bypass:wording-dictionary
  # CBL_MOCK_DEDUP_COUNT=0: no existing carrier Issue (dedup pass)
  # CBL_SKIP_ISSUE_CREATE=1: suppress actual GitHub API call, output [DRY-RUN] instead

  PR_JSON='{"number":101,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":102,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":103,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_MOCK_DEDUP_COUNT="0" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier -- exit 0
  [ "$status" -eq 0 ]
  # dry-run Issue create message present
  [[ "$output" == *"[DRY-RUN]"* ]]
  # signature contains the label
  [[ "$output" == *"wording-dictionary"* ]]
  # PASS summary
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-2: threshold miss -- 2 PR -> no Issue
@test "TC-2: per-(plugin,label) signature 2 merged PR (below threshold=3) -- no Issue created" {
  # 2 PRs only (below default threshold=3) -> no Issue create
  PR_JSON='{"number":201,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'$'\n'
  PR_JSON+='{"number":202,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier -- exit 0
  [ "$status" -eq 0 ]
  # [DRY-RUN] should NOT appear (below threshold = no Issue attempt)
  [[ "$output" != *"[DRY-RUN]"* ]]
  # below threshold message present
  [[ "$output" == *"below threshold"* ]]
  # PASS summary
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-3: dedup -- existing open carrier Issue -> no duplicate
@test "TC-3: existing open carrier Issue for same signature -- no duplicate Issue created" {
  # 3 PRs (threshold reached) but CBL_MOCK_DEDUP_COUNT=1 (existing Issue found)
  PR_JSON='{"number":301,"labels":[{"name":"hotfix-bypass:unit-tests"}]}'$'\n'
  PR_JSON+='{"number":302,"labels":[{"name":"hotfix-bypass:unit-tests"}]}'$'\n'
  PR_JSON+='{"number":303,"labels":[{"name":"hotfix-bypass:unit-tests"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_MOCK_DEDUP_COUNT="1" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier -- exit 0
  [ "$status" -eq 0 ]
  # [DRY-RUN] should NOT appear (dedup blocks Issue create)
  [[ "$output" != *"[DRY-RUN]"* ]]
  # dedup skip message present
  [[ "$output" == *"dedup"* ]]
  # PASS summary
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-4: exempt -- bypass-label-counter or exempt:* -> count excluded
@test "TC-4: PR with hotfix-bypass:bypass-label-counter or hotfix-bypass:exempt:* -- excluded from count" {
  # PR 401: hotfix-bypass:wording-dictionary + hotfix-bypass:bypass-label-counter (self-meta exempt)
  # PR 402: hotfix-bypass:wording-dictionary + hotfix-bypass:exempt:wording-dictionary (exempt template)
  # PR 403: hotfix-bypass:wording-dictionary (normal -- counts)
  # -> only 1 non-exempt wording-dictionary PR (below threshold=3) -> no Issue
  PR_JSON='{"number":401,"labels":[{"name":"hotfix-bypass:wording-dictionary"},{"name":"hotfix-bypass:bypass-label-counter"}]}'$'\n'
  PR_JSON+='{"number":402,"labels":[{"name":"hotfix-bypass:wording-dictionary"},{"name":"hotfix-bypass:exempt:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":403,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier -- exit 0
  [ "$status" -eq 0 ]
  # [DRY-RUN] should NOT appear (only 1 non-exempt PR < threshold=3)
  [[ "$output" != *"[DRY-RUN]"* ]]
  # below threshold message present (1 non-exempt < 3)
  [[ "$output" == *"below threshold"* ]]
  # PASS summary
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-5: multi-entry -- multiple signatures -> independent Issues
@test "TC-5: multiple (plugin,label) signatures reach threshold -- independent Issues per signature" {
  # 3 PRs with hotfix-bypass:wording-dictionary + 3 PRs with hotfix-bypass:claude-md-line-cap
  # -> 2 signatures both reach threshold -> 2 carrier Issues
  # CBL_MOCK_DEDUP_COUNT=0 -> no existing Issues for either signature
  PR_JSON='{"number":501,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":502,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":503,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":504,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'$'\n'
  PR_JSON+='{"number":505,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'$'\n'
  PR_JSON+='{"number":506,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_MOCK_DEDUP_COUNT="0" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier -- exit 0
  [ "$status" -eq 0 ]
  # 2 DRY-RUN messages (one per signature)
  DRY_RUN_COUNT=$(echo "$output" | grep -c "\[DRY-RUN\]" || true)
  echo "# dry-run count: $DRY_RUN_COUNT" >&3
  [ "$DRY_RUN_COUNT" -eq 2 ]
  # both signatures mentioned
  [[ "$output" == *"wording-dictionary"* ]]
  [[ "$output" == *"claude-md-line-cap"* ]]
  # PASS summary with 2 Issues created
  [[ "$output" == *"2 carrier Issue(s) created"* ]]
}
