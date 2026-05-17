#!/usr/bin/env bats
# tests/scripts/test-check-bypass-justification-marker.bats
# CFP-845 Phase 2 -- check-bypass-justification-marker.py / .sh unit tests (TDD red phase)
# Change Plan §8 Test Contract: TC-3, TC-4, TC-8
#
# Test cases:
#   TC-3 (happy):     PR [bypass-justification] prefix comment 존재 -> grep PASS
#   TC-4 (empty):     marker present but body empty -> grep PASS (false-positive 영역)
#   TC-8 (event):     pull_request_review_comment event -- PR-time lint (--pr-number mode)
#   TC-extra-1:       marker missing -> WARNING exit 1
#   TC-extra-2:       exempt PR (bypass-justification-marker label) -> skipped
#   TC-extra-3:       marker in line middle (not line start) -> grep FAIL (line start anchor)
#
# Mock strategy:
#   CBJ_MOCK_PRS_JSON=<newline-delimited-JSON>      -- bypass PR list override
#   CBJ_MOCK_COMMENTS_JSON=<newline-delimited-JSON> -- PR comments override
#   CBL_SKIP_ISSUE_CREATE=1                         -- dry-run

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-bypass-justification-marker.sh"

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

# ------------------------------------------------------------------ TC-3: marker present -> PASS
@test "TC-3: PR with [bypass-justification] prefix comment -- grep PASS exit 0" {
  # 1 bypass PR, 1 comment starting with [bypass-justification]
  PR_JSON='{"number":301,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  COMMENTS_JSON='{"body":"[bypass-justification] Admin merge approved: KST-paren pattern safe variant. Reviewed by maintainer."}'

  run env \
    CBJ_MOCK_PRS_JSON="$PR_JSON" \
    CBJ_MOCK_COMMENTS_JSON="$COMMENTS_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # grep PASS -- exit 0
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-4: marker present but empty body -> false-positive
@test "TC-4: marker present but body empty after marker -- grep PASS (false-positive, reviewer responsibility)" {
  # body = "[bypass-justification]" with no description after
  # grep PASS because pattern is line-start match only
  PR_JSON='{"number":401,"labels":[{"name":"hotfix-bypass:claude-md-line-cap"}]}'

  COMMENTS_JSON='{"body":"[bypass-justification]"}'

  run env \
    CBJ_MOCK_PRS_JSON="$PR_JSON" \
    CBJ_MOCK_COMMENTS_JSON="$COMMENTS_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # grep PASS even with empty body (false-positive -- semantic adequacy not verified)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-8: PR-time single PR mode (--pr-number)
@test "TC-8: pull_request_review_comment event -- single PR mode (--pr-number) with marker present" {
  # Simulate PR-time event: single PR check via --pr-number flag
  # CBJ_MOCK_PRS_JSON with single PR + marker in comment
  PR_JSON='{"number":801,"labels":[{"name":"hotfix-bypass:bypass-label-counter"}]}'

  COMMENTS_JSON='{"body":"[bypass-justification] This PR itself carries bypass-label-counter exempt label. Self-referential exemption declared."}'

  run env \
    CBJ_MOCK_PRS_JSON="$PR_JSON" \
    CBJ_MOCK_COMMENTS_JSON="$COMMENTS_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 801

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # single PR marker present -> PASS
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-1: marker missing -> WARNING exit 1
@test "TC-extra-1: PR with hotfix-bypass:* but no [bypass-justification] comment -- WARNING exit 1" {
  PR_JSON='{"number":1101,"labels":[{"name":"hotfix-bypass:wording-dictionary"}]}'

  # comment body does NOT start with [bypass-justification]
  COMMENTS_JSON='{"body":"LGTM, merging per admin approval"}'

  run env \
    CBJ_MOCK_PRS_JSON="$PR_JSON" \
    CBJ_MOCK_COMMENTS_JSON="$COMMENTS_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # missing marker -> WARNING exit 1
  [ "$status" -eq 1 ]
  [[ "$output" == *"MISSING"* ]] || [[ "$output" == *"WARNING"* ]]
  [[ "$output" == *"1101"* ]]
}

# ------------------------------------------------------------------ TC-extra-2: exempt label -> skip
@test "TC-extra-2: PR with hotfix-bypass:bypass-justification-marker -- exempt, skip check" {
  # PR carries self-meta exempt label -> not checked for marker
  PR_JSON='{"number":1201,"labels":[{"name":"hotfix-bypass:wording-dictionary"},{"name":"hotfix-bypass:bypass-justification-marker"}]}'

  # no comments needed -- exempt PR is not checked
  COMMENTS_JSON='{"body":"no marker here"}'

  run env \
    CBJ_MOCK_PRS_JSON="$PR_JSON" \
    CBJ_MOCK_COMMENTS_JSON="$COMMENTS_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # exempt -> PASS (no marker check)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-extra-3: marker in middle of line -> FAIL (line start anchor)
@test "TC-extra-3: [bypass-justification] in middle of line -- line-start anchor mismatch, marker NOT found" {
  PR_JSON='{"number":1301,"labels":[{"name":"hotfix-bypass:unit-tests"}]}'

  # marker is NOT at line start (it follows "Note: ")
  COMMENTS_JSON='{"body":"Note: [bypass-justification] this is not at line start"}'

  run env \
    CBJ_MOCK_PRS_JSON="$PR_JSON" \
    CBJ_MOCK_COMMENTS_JSON="$COMMENTS_JSON" \
    CBL_SKIP_ISSUE_CREATE="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # line-start anchor requires marker at column 0 -> NOT found -> WARNING exit 1
  [ "$status" -eq 1 ]
  [[ "$output" == *"MISSING"* ]] || [[ "$output" == *"WARNING"* ]]
}
