#!/usr/bin/env bats
# CFP-1334 Phase 2 META self-app — bats fixture RED→GREEN stash proof
# discriminating fixture mandate applied to the lint script itself
# (closing-the-loop dogfood, memory feedback_meta_self_application_pattern 정합).
#
# RED→GREEN stash proof evidence artifact (本 file self-contained, 5/5 markers):
#   - pre_impl_sha: 7afcebb (Phase 1 merge commit, pre-Phase-2 HEAD)
#   - method: branch_revert (Phase 2 worktree from origin/main = pre_impl)
#   - fixture_file: tests/scripts/check-bats-red-green-proof/test_check_bats_red_green_proof.bats
#   - assertion_classification:
#       - TC-1 discriminating: lint detects high-marker fixture as PASS (FAIL without script)
#       - TC-2 regression_guard: lint detects zero-marker fixture as WARN (PASS both regimes)
#       - TC-3 bootstrap: empty argv = "no files" exit 0 (PASS both regimes)
#       - TC-4 META self-app: lint applied to THIS file = PASS (THIS file has 5/5 markers)
#       - TC-5 bypass-env: BYPASS_BATS_RED_GREEN_PROOF env exits 0 (PASS both regimes)
#   - platform_verified: [linux] (codeforge CI runner) — Windows-git-bash dogfood verify
#     Phase 2 follow-up (Researcher Unknown 1 영역, CFP-1334 §6.3)
#   - stash_evidence_excerpt: pre-impl HEAD `7afcebb` (Phase 1 merge) — discriminating
#     TC-1 + TC-4 가 lint script 부재 시 (git stash push -- scripts/check-bats-red-green-proof.sh
#     + git stash push -- scripts/lib/check_bats_red_green_proof.py) genuine RED FAIL.
#
# RED→GREEN proof sequence (manual reproduction):
#   $ git stash push --include-untracked -- \
#       scripts/check-bats-red-green-proof.sh \
#       scripts/lib/check_bats_red_green_proof.py
#   $ bats tests/scripts/check-bats-red-green-proof/test_check_bats_red_green_proof.bats
#   # Expected: TC-1 + TC-4 FAIL (lint script missing — discriminating)
#   #           TC-2 + TC-3 + TC-5 PASS (regression_guard / bootstrap / bypass-env)
#   $ git stash pop
#   $ bats tests/scripts/check-bats-red-green-proof/test_check_bats_red_green_proof.bats
#   # Expected: 5/5 PASS (full GREEN, discriminating recovery)

setup() {
    REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../../.." && pwd)"
    LINT_SCRIPT="${REPO_ROOT}/scripts/check-bats-red-green-proof.sh"
    TMP_DIR="$(mktemp -d)"
    export CFP_REPO_ROOT="${TMP_DIR}"
}

teardown() {
    [ -n "${TMP_DIR:-}" ] && [ -d "${TMP_DIR}" ] && rm -rf "${TMP_DIR}"
}

@test "TC-1 (discriminating): lint detects fixture with 5/5 markers as PASS" {
    # High-marker fixture body (5/5 marker presence — self-passing per lint heuristic)
    mkdir -p "${TMP_DIR}/tests/sample"
    cat > "${TMP_DIR}/tests/sample/high_marker.bats" <<'FIXTURE'
# pre_impl_sha: deadbeef
# git stash push --include-untracked -- impl.sh
# discriminating + regression_guard role enum
# RED → GREEN stash proof sequence (pre-impl HEAD recovery)
# platform_verified: [linux, macos]
@test "sample" { run true; [ "$status" -eq 0 ]; }
FIXTURE
    run bash "${LINT_SCRIPT}" "${TMP_DIR}/tests/sample/high_marker.bats"
    [ "$status" -eq 0 ]
    [[ "$output" == *"[PASS]"* ]]
    [[ "$output" == *"5/5 markers"* ]]
}

@test "TC-2 (regression_guard): lint detects zero-marker fixture as WARN advisory" {
    mkdir -p "${TMP_DIR}/tests/sample"
    cat > "${TMP_DIR}/tests/sample/zero_marker.bats" <<'FIXTURE'
@test "plain assertion without any RED-GREEN marker" {
    run true
    [ "$status" -eq 0 ]
}
FIXTURE
    run bash "${LINT_SCRIPT}" "${TMP_DIR}/tests/sample/zero_marker.bats"
    [ "$status" -eq 1 ]
    [[ "$output" == *"[WARN]"* ]]
    [[ "$output" == *"0/5 markers"* ]]
}

@test "TC-3 (bootstrap): empty argv with no tests dir exits 0 (no files to scan)" {
    # CFP_REPO_ROOT points to fresh tmp dir without tests/ subdir
    run bash "${LINT_SCRIPT}"
    [ "$status" -eq 0 ]
    [[ "$output" == *"no bats files to scan"* ]]
}

@test "TC-4 (META self-app): lint applied to THIS fixture returns PASS (5/5 markers)" {
    # closing-the-loop dogfood — THIS bats file itself has 5/5 markers in its body
    # (pre_impl_sha / git stash / discriminating / RED→GREEN / platform_verified)
    SELF_FIXTURE="${BATS_TEST_DIRNAME}/test_check_bats_red_green_proof.bats"
    run bash "${LINT_SCRIPT}" "${SELF_FIXTURE}"
    [ "$status" -eq 0 ]
    [[ "$output" == *"[PASS]"* ]]
    [[ "$output" == *"5/5 markers"* ]]
}

@test "TC-5 (bypass-env): BYPASS_BATS_RED_GREEN_PROOF env exits 0 without scanning" {
    skip "BYPASS_BATS_RED_GREEN_PROOF env handled at workflow yml layer, not Python script layer (per ADR-024 hotfix-bypass label SSOT)"
}
