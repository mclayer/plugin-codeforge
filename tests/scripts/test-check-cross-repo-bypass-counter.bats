#!/usr/bin/env bats
# tests/scripts/test-check-cross-repo-bypass-counter.bats
# CFP-845 Phase 2 -- check-cross-repo-bypass-counter.py / .sh unit tests (TDD red phase)
# Change Plan §8 Test Contract: TC-5, TC-6
#
# Test cases:
#   TC-5 (aggregate):  3 repo 동일 label 동시 threshold reach -> 단일 aggregate carrier Issue
#   TC-6 (disjoint):  1 repo 만 reach -> 해당 repo Issue 발의 (disjoint invariant)
#   TC-extra-1:       all repos below threshold -> no Issue
#   TC-extra-2:       dedup existing Issue -> skip
#   TC-extra-3:       self-meta exempt label -> PR excluded
#
# Mock strategy:
#   CRC_MOCK_PRS_JSON_PLUGIN=<newline-delimited-JSON>      -- mclayer/plugin-codeforge PR list
#   CRC_MOCK_PRS_JSON_DOCS=<newline-delimited-JSON>        -- mclayer/codeforge-internal-docs PR list
#   CRC_MOCK_PRS_JSON_MARKETPLACE=<newline-delimited-JSON> -- mclayer/marketplace PR list
#   CBL_MOCK_DEDUP_COUNT=<int>                             -- dedup total_count override
#   CBL_SKIP_ISSUE_CREATE=1                                -- suppress actual gh api call

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-cross-repo-bypass-counter.sh"

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

# ------------------------------------------------------------------ TC-5: 3-repo aggregate -> single carrier Issue
@test "TC-5: 3 repos all reach threshold for same label -- single aggregate carrier Issue" {
  # all 3 repos have 3 PRs with hotfix-bypass:wording-dictionary -> threshold=3 reached in all
  PLUGIN_JSON='{"number":501,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PLUGIN_JSON+='{"number":502,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PLUGIN_JSON+='{"number":503,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  DOCS_JSON='{"number":504,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  DOCS_JSON+='{"number":505,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  DOCS_JSON+='{"number":506,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  MKT_JSON='{"number":507,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  MKT_JSON+='{"number":508,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  MKT_JSON+='{"number":509,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  run env \
    CRC_MOCK_PRS_JSON_PLUGIN="$PLUGIN_JSON" \
    CRC_MOCK_PRS_JSON_DOCS="$DOCS_JSON" \
    CRC_MOCK_PRS_JSON_MARKETPLACE="$MKT_JSON" \
    CBL_MOCK_DEDUP_COUNT="0" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --threshold 3 \
    --repos "mclayer/plugin-codeforge,mclayer/codeforge-internal-docs,mclayer/marketplace"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # aggregate -> 1 Issue created
  [ "$status" -eq 0 ]
  [[ "$output" == *"[DRY-RUN]"* ]]
  [[ "$output" == *"wording-dictionary"* ]]
  # single Issue (not 3)
  DRY_RUN_COUNT=$(echo "$output" | grep -c "\[DRY-RUN\]" || true)
  echo "# dry-run count: $DRY_RUN_COUNT" >&3
  [ "$DRY_RUN_COUNT" -eq 1 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-6: only 1 repo reaches -> per-repo Issue only
@test "TC-6: only wrapper repo reaches threshold, docs and marketplace below -- per-repo carrier Issue (1 repo)" {
  # wrapper: 3 PRs with hotfix-bypass:wording-dictionary (reach)
  # docs: 2 PRs (below threshold=3)
  # marketplace: 1 PR (below threshold=3)
  PLUGIN_JSON='{"number":601,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PLUGIN_JSON+='{"number":602,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PLUGIN_JSON+='{"number":603,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  DOCS_JSON='{"number":604,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  DOCS_JSON+='{"number":605,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  MKT_JSON='{"number":606,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  run env \
    CRC_MOCK_PRS_JSON_PLUGIN="$PLUGIN_JSON" \
    CRC_MOCK_PRS_JSON_DOCS="$DOCS_JSON" \
    CRC_MOCK_PRS_JSON_MARKETPLACE="$MKT_JSON" \
    CBL_MOCK_DEDUP_COUNT="0" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --threshold 3 \
    --repos "mclayer/plugin-codeforge,mclayer/codeforge-internal-docs,mclayer/marketplace"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  # 1 DRY-RUN (only wrapper reached threshold)
  [[ "$output" == *"[DRY-RUN]"* ]]
  DRY_RUN_COUNT=$(echo "$output" | grep -c "\[DRY-RUN\]" || true)
  echo "# dry-run count: $DRY_RUN_COUNT" >&3
  [ "$DRY_RUN_COUNT" -eq 1 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-1: all below threshold -> no Issue
@test "TC-extra-1: all repos below threshold -- no carrier Issue" {
  PLUGIN_JSON='{"number":701,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PLUGIN_JSON+='{"number":702,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  DOCS_JSON='{"number":703,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  MKT_JSON=''  # no PRs

  run env \
    CRC_MOCK_PRS_JSON_PLUGIN="$PLUGIN_JSON" \
    CRC_MOCK_PRS_JSON_DOCS="$DOCS_JSON" \
    CRC_MOCK_PRS_JSON_MARKETPLACE="$MKT_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --threshold 3 \
    --repos "mclayer/plugin-codeforge,mclayer/codeforge-internal-docs,mclayer/marketplace"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" != *"[DRY-RUN]"* ]]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-2: dedup existing Issue -> skip
@test "TC-extra-2: threshold reached but dedup open Issue found -- skip create" {
  PLUGIN_JSON='{"number":801,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PLUGIN_JSON+='{"number":802,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'$'\n'
  PLUGIN_JSON+='{"number":803,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  DOCS_JSON=''
  MKT_JSON=''

  run env \
    CRC_MOCK_PRS_JSON_PLUGIN="$PLUGIN_JSON" \
    CRC_MOCK_PRS_JSON_DOCS="$DOCS_JSON" \
    CRC_MOCK_PRS_JSON_MARKETPLACE="$MKT_JSON" \
    CBL_MOCK_DEDUP_COUNT="1" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --threshold 3 \
    --repos "mclayer/plugin-codeforge,mclayer/codeforge-internal-docs,mclayer/marketplace"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" != *"[DRY-RUN]"* ]]
  [[ "$output" == *"dedup"* ]]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-3: self-meta exempt -> excluded
@test "TC-extra-3: PRs with hotfix-bypass:cross-repo-bypass-counter -- excluded from count" {
  # 3 PRs but all carry self-meta exempt label -> count = 0 -> below threshold
  PLUGIN_JSON='{"number":901,"labels":[{"name":"hotfix-bypass:wording-dictionary"},{"name":"hotfix-bypass:cross-repo-bypass-counter"}]}'$'\n'
  PLUGIN_JSON+='{"number":902,"labels":[{"name":"hotfix-bypass:wording-dictionary"},{"name":"hotfix-bypass:cross-repo-bypass-counter"}]}'$'\n'
  PLUGIN_JSON+='{"number":903,"labels":[{"name":"hotfix-bypass:wording-dictionary"},{"name":"hotfix-bypass:cross-repo-bypass-counter"}]}'

  DOCS_JSON=''
  MKT_JSON=''

  run env \
    CRC_MOCK_PRS_JSON_PLUGIN="$PLUGIN_JSON" \
    CRC_MOCK_PRS_JSON_DOCS="$DOCS_JSON" \
    CRC_MOCK_PRS_JSON_MARKETPLACE="$MKT_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --threshold 3 \
    --repos "mclayer/plugin-codeforge,mclayer/codeforge-internal-docs,mclayer/marketplace"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" != *"[DRY-RUN]"* ]]
  [[ "$output" == *"PASS"* ]]
}
