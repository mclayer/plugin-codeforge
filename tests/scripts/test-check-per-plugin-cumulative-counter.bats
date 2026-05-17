#!/usr/bin/env bats
# tests/scripts/test-check-per-plugin-cumulative-counter.bats
# CFP-845 Phase 2 -- check-per-plugin-cumulative-counter.py / .sh unit tests (TDD red phase)
# Change Plan §8 Test Contract: TC-1, TC-2, TC-7
#
# Test cases:
#   TC-1 (happy):      plugin 5 entry 각 1회 = 5 PR 누적 -> carrier Issue 발의
#   TC-2 (disjoint):   단일 entry 5회 -> per-plugin aggregate trigger (per-entry는 별개)
#   TC-7 (self-meta):  hotfix-bypass:per-plugin-cumulative-counter 부착 PR -> count 제외
#   TC-extra-1:        below threshold (4 PR) -> no Issue
#   TC-extra-2:        dedup existing open Issue -> skip create
#   TC-extra-3:        all exempt (exempt:per-plugin) -> PASS no Issue
#
# Mock strategy: CBL_MOCK_PRS_JSON + CBL_MOCK_DEDUP_COUNT + CBL_SKIP_ISSUE_CREATE
#   CBL_MOCK_PRS_JSON=<newline-delimited-JSON>  -- merged PR list override
#   CBL_MOCK_DEDUP_COUNT=<int>                 -- dedup total_count override
#   CBL_SKIP_ISSUE_CREATE=1                    -- suppress actual gh api call
#
# Windows Git Bash compatibility (ADR-061 evidence):
#   single-quoted heredoc / export env vars / bats 'run' stdout+stderr capture

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-per-plugin-cumulative-counter.sh"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ------------------------------------------------------------------ TC-1: 5 PRs different entries -> carrier Issue
@test "TC-1: plugin with 5 bypass PRs (different entries) -- carrier Issue created" {
  # 5 PRs, each with a different hotfix-bypass:* entry -> per-plugin aggregate = 5
  # threshold=5 (default) -> reached -> Issue create
  PR_JSON='{"number":101,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":102,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'$'\n'
  PR_JSON+='{"number":103,"labels":[{"name":"hotfix-bypass:bypass-label-counter"}]}'$'\n'
  PR_JSON+='{"number":104,"labels":[{"name":"hotfix-bypass:unit-tests"}]}'$'\n'
  PR_JSON+='{"number":105,"labels":[{"name":"hotfix-bypass:auto-phase-label"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_MOCK_DEDUP_COUNT="0" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --plugin-name plugin-codeforge --threshold 5

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier -- exit 0
  [ "$status" -eq 0 ]
  # [DRY-RUN] Issue create called
  [[ "$output" == *"[DRY-RUN]"* ]]
  # plugin name in output
  [[ "$output" == *"plugin-codeforge"* ]]
  # PASS summary
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-2: single entry 5 times -> also per-plugin aggregate trigger
@test "TC-2: single entry repeated 5 times -- per-plugin aggregate threshold reached" {
  # TC-2: 1개 entry 5회 반복 = per-plugin aggregate = 5 (threshold=5 reached)
  # Note: per-(plugin,label) bypass-label-counter 도 별도 trigger 되지만,
  # per-plugin aggregate 는 독립 scope (disjoint invariant §11.7)
  PR_JSON='{"number":201,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":202,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":203,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":204,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":205,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_MOCK_DEDUP_COUNT="0" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --plugin-name plugin-codeforge --threshold 5

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier -- exit 0
  [ "$status" -eq 0 ]
  # [DRY-RUN] Issue create (per-plugin reached)
  [[ "$output" == *"[DRY-RUN]"* ]]
  # PASS summary
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-7: self-meta loop 차단
@test "TC-7: PR with hotfix-bypass:per-plugin-cumulative-counter -- excluded from count" {
  # 4 normal bypass PRs + 2 self-meta exempt PRs -> non-exempt count = 4 < threshold=5
  PR_JSON='{"number":701,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":702,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'$'\n'
  PR_JSON+='{"number":703,"labels":[{"name":"hotfix-bypass:bypass-label-counter"}]}'$'\n'
  PR_JSON+='{"number":704,"labels":[{"name":"hotfix-bypass:unit-tests"}]}'$'\n'
  PR_JSON+='{"number":705,"labels":[{"name":"hotfix-bypass:wording-dictionary"},{"name":"hotfix-bypass:per-plugin-cumulative-counter"}]}'$'\n'
  PR_JSON+='{"number":706,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"},{"name":"hotfix-bypass:per-plugin-cumulative-counter"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --plugin-name plugin-codeforge --threshold 5

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # warning tier -- exit 0
  [ "$status" -eq 0 ]
  # [DRY-RUN] should NOT appear (4 non-exempt < threshold=5)
  [[ "$output" != *"[DRY-RUN]"* ]]
  # below threshold message OR no carrier Issue
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-1: 4 PRs below threshold
@test "TC-extra-1: 4 bypass PRs (below threshold=5) -- no Issue created" {
  PR_JSON='{"number":801,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":802,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'$'\n'
  PR_JSON+='{"number":803,"labels":[{"name":"hotfix-bypass:unit-tests"}]}'$'\n'
  PR_JSON+='{"number":804,"labels":[{"name":"hotfix-bypass:auto-phase-label"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --plugin-name plugin-codeforge --threshold 5

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" != *"[DRY-RUN]"* ]]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-2: dedup skip
@test "TC-extra-2: threshold reached but dedup open Issue found -- skip create" {
  PR_JSON='{"number":901,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PR_JSON+='{"number":902,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'$'\n'
  PR_JSON+='{"number":903,"labels":[{"name":"hotfix-bypass:unit-tests"}]}'$'\n'
  PR_JSON+='{"number":904,"labels":[{"name":"hotfix-bypass:auto-phase-label"}]}'$'\n'
  PR_JSON+='{"number":905,"labels":[{"name":"hotfix-bypass:bypass-label-counter"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_MOCK_DEDUP_COUNT="1" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --plugin-name plugin-codeforge --threshold 5

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" != *"[DRY-RUN]"* ]]
  [[ "$output" == *"dedup"* ]]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-3: exempt:per-plugin -> all excluded
@test "TC-extra-3: PRs with hotfix-bypass:exempt:per-plugin -- excluded from count" {
  # 5 PRs but all carry hotfix-bypass:exempt:per-plugin -> count = 0 -> PASS no Issue
  PR_JSON='{"number":1001,"labels":[{"name":"hotfix-bypass:wording-dictionary"},{"name":"hotfix-bypass:exempt:per-plugin"}]}'$'\n'
  PR_JSON+='{"number":1002,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"},{"name":"hotfix-bypass:exempt:per-plugin"}]}'$'\n'
  PR_JSON+='{"number":1003,"labels":[{"name":"hotfix-bypass:unit-tests"},{"name":"hotfix-bypass:exempt:per-plugin"}]}'$'\n'
  PR_JSON+='{"number":1004,"labels":[{"name":"hotfix-bypass:auto-phase-label"},{"name":"hotfix-bypass:exempt:per-plugin"}]}'$'\n'
  PR_JSON+='{"number":1005,"labels":[{"name":"hotfix-bypass:bypass-label-counter"},{"name":"hotfix-bypass:exempt:per-plugin"}]}'

  run env \
    CBL_MOCK_PRS_JSON="$PR_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --plugin-name plugin-codeforge --threshold 5

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" != *"[DRY-RUN]"* ]]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-4: rate-limit-disconnected sentinel (F-CR-845-P1-1)
@test "TC-extra-4: empty CBL_MOCK_PRS_JSON='[]' -- env key exists, no live gh api call (rate-limit-disconnected)" {
  # F-CR-845-P1-1 FIX 검증: CBL_MOCK_PRS_JSON key 가 set 되어 있으면 live gh api fallback 금지.
  # '[]' empty JSON array = explicit empty mock (no PRs) -> PASS below threshold.
  run env \
    CBL_MOCK_PRS_JSON='[]' \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --plugin-name plugin-codeforge --threshold 5

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # empty mock -> no bypass PRs -> PASS
  [ "$status" -eq 0 ]
  [[ "$output" != *"[DRY-RUN]"* ]]
  [[ "$output" == *"PASS"* ]]
}
