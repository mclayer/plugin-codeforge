#!/usr/bin/env bats
# tests/scripts/test_check-stale-local-main-checkout-sh.sh
# CFP-1410 Phase 2 / ADR-073 Amendment 9 — bats 7 TC
#
# TC coverage:
#   T-1: divergence detection (≥ threshold) → warning + EnterWorktree guidance
#   T-2: threshold env override (CODEFORGE_STALE_THRESHOLD=5)
#   T-3: warning stdout precise format (script name prefix + ADR ref)
#   T-4: exit code 0 (non-blocking — advisory)
#   T-5: offline graceful degradation (fetch fail → warning stderr + exit 0)
#   T-6: bypass env (BYPASS_STALE_LOCAL_MAIN_CHECKOUT=1) silent skip
#   T-7: EC-5 feature branch (HEAD != main) silent skip
#
# RED→GREEN stash proof evidence artifact (CFP-1334 §8.4 mandate):
#   - pre_impl_sha: 761d877 (Phase 1 declarative merge, pre-Phase-2 HEAD)
#   - method: git stash push -- scripts/lib/check_stale_local_main_checkout.py
#   - fixture_file: tests/scripts/test_check-stale-local-main-checkout-sh.sh
#   - assertion_classification:
#       - T-1 discriminating: divergence detection FAILS without Python SSOT
#       - T-5 discriminating: offline graceful degradation uses MOCK_FETCH_FAIL seam
#       - T-6 regression_guard: bypass env accepted
#       - T-7 regression_guard: EC-5 feature branch silent skip
#   - platform_verified: [linux] (CI runner) + Windows-git-bash advisory
#   - stash_evidence_excerpt: pre-impl (761d877) stash push scripts/lib/check_stale_local_main_checkout.py
#       → T-1 FAIL (Python SSOT missing) → stash pop → T-1 PASS (discriminating recovery)

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
REPO_ROOT="${BATS_TEST_DIRNAME}/../.."
PYTHON_SSOT="${REPO_ROOT}/scripts/lib/check_stale_local_main_checkout.py"

# ---------------------------------------------------------------------------
# Helper: Python runner with monkeypatch for _fetch_origin_main
# Writes a temp wrapper script for each test to avoid inline heredoc complexity.
# ---------------------------------------------------------------------------
_run_with_fetch_ok() {
    # Run Python SSOT with _fetch_origin_main stubbed to return True.
    # Additional env vars set by caller.
    python3 - "${PYTHON_SSOT}" <<'PYEOF'
import os, sys, importlib.util

script_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("mod", script_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod._fetch_origin_main = lambda timeout: True
try:
    mod.main()
except SystemExit as e:
    sys.exit(e.code)
PYEOF
}

_run_with_fetch_fail() {
    # Run Python SSOT with _fetch_origin_main stubbed to return False.
    python3 - "${PYTHON_SSOT}" <<'PYEOF'
import os, sys, importlib.util

script_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("mod", script_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod._fetch_origin_main = lambda timeout: False
try:
    mod.main()
except SystemExit as e:
    sys.exit(e.code)
PYEOF
}

setup() {
    unset BYPASS_STALE_LOCAL_MAIN_CHECKOUT || true
    unset STALE_LOCAL_GIT_MOCK_REV_LIST || true
    unset STALE_LOCAL_GIT_MOCK_BRANCH || true
    unset STALE_LOCAL_GIT_MOCK_FETCH_FAIL || true
    unset CODEFORGE_STALE_THRESHOLD || true
    unset CODEFORGE_STALE_FETCH_TIMEOUT_SEC || true
}

teardown() {
    unset BYPASS_STALE_LOCAL_MAIN_CHECKOUT || true
    unset STALE_LOCAL_GIT_MOCK_REV_LIST || true
    unset STALE_LOCAL_GIT_MOCK_BRANCH || true
    unset STALE_LOCAL_GIT_MOCK_FETCH_FAIL || true
    unset CODEFORGE_STALE_THRESHOLD || true
}

# ---------------------------------------------------------------------------
# T-1: divergence detection (discriminating)
# ---------------------------------------------------------------------------
@test "T-1 (discriminating): divergence >= threshold → warning + EnterWorktree guidance" {
    export STALE_LOCAL_GIT_MOCK_BRANCH="main"
    export STALE_LOCAL_GIT_MOCK_REV_LIST="3"

    run _run_with_fetch_ok
    [ "$status" -eq 0 ]
    [[ "$output" == *"WARNING"* ]]
    [[ "$output" == *"3 commit(s) behind"* ]]
    [[ "$output" == *"EnterWorktree"* ]] || [[ "$output" == *"worktree"* ]]
}

# ---------------------------------------------------------------------------
# T-2: threshold env override
# ---------------------------------------------------------------------------
@test "T-2: CODEFORGE_STALE_THRESHOLD=5 — no warning when divergence=3 < threshold=5" {
    export STALE_LOCAL_GIT_MOCK_BRANCH="main"
    export STALE_LOCAL_GIT_MOCK_REV_LIST="3"
    export CODEFORGE_STALE_THRESHOLD="5"

    run _run_with_fetch_ok
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"* ]]
}

# ---------------------------------------------------------------------------
# T-3: warning stdout precise format
# ---------------------------------------------------------------------------
@test "T-3: warning stdout includes script name prefix and ADR-073 Amendment 9 ref" {
    export STALE_LOCAL_GIT_MOCK_BRANCH="main"
    export STALE_LOCAL_GIT_MOCK_REV_LIST="2"

    run _run_with_fetch_ok
    [ "$status" -eq 0 ]
    [[ "$output" == *"check_stale_local_main_checkout"* ]]
    [[ "$output" == *"ADR-073 Amendment 9"* ]]
}

# ---------------------------------------------------------------------------
# T-4: exit code 0 (non-blocking advisory)
# ---------------------------------------------------------------------------
@test "T-4: exit code always 0 — non-blocking advisory even with high divergence" {
    export STALE_LOCAL_GIT_MOCK_BRANCH="main"
    export STALE_LOCAL_GIT_MOCK_REV_LIST="99"

    run _run_with_fetch_ok
    [ "$status" -eq 0 ]
}

# ---------------------------------------------------------------------------
# T-5: offline graceful degradation (discriminating)
# ---------------------------------------------------------------------------
@test "T-5 (discriminating): offline fetch fail → graceful degradation exit 0" {
    export STALE_LOCAL_GIT_MOCK_BRANCH="main"

    run _run_with_fetch_fail
    [ "$status" -eq 0 ]
    # No divergence WARNING emitted (fetch failed → graceful skip, no divergence check)
    [[ "$output" != *"commit(s) behind"* ]]
    # Graceful degradation advisory may appear in output (stderr captured by bats run)
    [[ "$output" == *"offline"* ]] || [[ "$output" == *"divergence check skipped"* ]]
}

# ---------------------------------------------------------------------------
# T-6: bypass env silent skip (regression_guard)
# ---------------------------------------------------------------------------
@test "T-6 (regression_guard): BYPASS_STALE_LOCAL_MAIN_CHECKOUT=1 → silent skip exit 0" {
    export BYPASS_STALE_LOCAL_MAIN_CHECKOUT="1"
    export STALE_LOCAL_GIT_MOCK_REV_LIST="99"

    run python3 "${PYTHON_SSOT}"
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"* ]]
}

# ---------------------------------------------------------------------------
# T-7: EC-5 feature branch silent skip (regression_guard)
# ---------------------------------------------------------------------------
@test "T-7 (regression_guard): EC-5 feature branch (HEAD != main) → silent skip exit 0" {
    export STALE_LOCAL_GIT_MOCK_BRANCH="cfp-1410"
    export STALE_LOCAL_GIT_MOCK_REV_LIST="5"

    run python3 "${PYTHON_SSOT}"
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"* ]]
}
