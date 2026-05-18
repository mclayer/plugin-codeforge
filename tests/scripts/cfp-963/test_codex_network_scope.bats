#!/usr/bin/env bats
# tests/scripts/cfp-963/test_codex_network_scope.bats
# CFP-963 Phase 2 — Codex worker network_scope mechanical layer
# QADeveloperAgent TDD (RED written first → GREEN against Phase 2 implementation)
#
# TC map (Change Plan §6 + Story §8.5 coverage table):
#   TC-BAT-1  (P0): shell wrapper exit propagation — PASS case (file with network_scope)
#   TC-BAT-2  (P0): shell wrapper exit propagation — WARN case (file without network_scope)
#   TC-BAT-3  (P1): workflow continue-on-error semantic (warning tier)
#   TC-BAT-4a (P1): step pair (a) detect → declare marker presence in script
#   TC-BAT-4b (P1): step pair (b) verify-before-trust reference in script
#   TC-BAT-4c (P1): step pair (c) Story §10 marker string in script
#   TC-BAT-5  (P2): fixture pair discriminator — with field → exit 0
#   TC-BAT-6  (P2): fixture pair discriminator — without field → exit 1
#   TC-BAT-7  (P0): ADR-061 정합 — shell wrapper is thin (exec python3 only)
#   TC-BAT-8  (P0): byte-identical self-app (templates/ vs .github/workflows/)
#
# SecurityArch TH-2 applied: CBL_SKIP_ISSUE_CREATE=1 in setup()
# ADR-061 §결정 1: thin wrapper test confirms exec python3 single invocation

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

WRAPPER_SH="${WORKTREE_ROOT}/scripts/check-codex-network-scope.sh"
PYTHON_SSOT="${WORKTREE_ROOT}/scripts/lib/check_codex_network_scope.py"
WORKFLOW_TEMPLATE="${WORKTREE_ROOT}/templates/github-workflows/codex-network-scope-presence.yml"
WORKFLOW_SELFAPP="${WORKTREE_ROOT}/.github/workflows/codex-network-scope-presence.yml"
FIXTURE_WITH="${WORKTREE_ROOT}/tests/fixtures/codex_spawn_prompt_with_network_scope.txt"
FIXTURE_WITHOUT="${WORKTREE_ROOT}/tests/fixtures/codex_spawn_prompt_without_network_scope.txt"
FIXTURE_NON_SPAWN="${WORKTREE_ROOT}/tests/fixtures/non_spawn_prompt_file.txt"

# ──────────────────────────────────────── helpers ────────────────────────────

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  # SecurityArch TH-2: never create real Issues in CI (CBL_SKIP_ISSUE_CREATE env seam)
  export CBL_SKIP_ISSUE_CREATE=1
  export CFP963_SKIP_ISSUE_CREATE=1
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-963-unused}"
}

# ──────────────────────────────────────── TC-BAT-1: wrapper PASS exit propagation ─

@test "TC-BAT-1 (P0): shell wrapper exit 0 for prompt WITH network_scope field" {
  [ -f "${WRAPPER_SH}" ]
  [ -f "${FIXTURE_WITH}" ]
  run bash "${WRAPPER_SH}" "${FIXTURE_WITH}"
  [ "$status" -eq 0 ]
  # F-CR-963-1: verify enum-detection path engaged (output must contain network_scope=offline)
  echo "$output" | grep -q "network_scope=offline"
}

# ──────────────────────────────────────── TC-BAT-2: wrapper WARN exit propagation ─

@test "TC-BAT-2 (P0): shell wrapper exit 1 for prompt WITHOUT network_scope field" {
  [ -f "${WRAPPER_SH}" ]
  [ -f "${FIXTURE_WITHOUT}" ]
  run bash "${WRAPPER_SH}" "${FIXTURE_WITHOUT}"
  [ "$status" -eq 1 ]
}

# ──────────────────────────────────────── TC-BAT-3: workflow warning-tier semantic ─

@test "TC-BAT-3 (P1): workflow codex-network-scope-presence.yml continue-on-error: true" {
  [ -f "${WORKFLOW_TEMPLATE}" ]
  # warning tier = continue-on-error: true (ADR-060 §결정 5, §결정 28)
  grep -q "continue-on-error: true" "${WORKFLOW_TEMPLATE}"
}

# ──────────────────────────────────────── TC-BAT-4a/b/c: step pair markers ─────

@test "TC-BAT-4a (P1): step pair (a) marker — detect or declare present in Python SSOT" {
  [ -f "${PYTHON_SSOT}" ]
  # step (a): graceful degradation detect → declare
  grep -qE "detect|declare|offline_substitution_declared|graceful" "${PYTHON_SSOT}"
}

@test "TC-BAT-4b (P1): step pair (b) marker — verify-before-trust reference present" {
  [ -f "${PYTHON_SSOT}" ]
  # step (b): verify-before-trust 5 sub-scope reference
  grep -qE "verify.before.trust|verify_before_trust|substitution.path|ADR-070" "${PYTHON_SSOT}"
}

@test "TC-BAT-4c (P1): step pair (c) marker — Story §10 marker format present" {
  [ -f "${PYTHON_SSOT}" ]
  # step (c): [codex-sandbox-fallback: <fail-mode>] marker reference
  grep -qE "codex-sandbox-fallback|network_scope_actual|FAIL_MODE" "${PYTHON_SSOT}"
}

# ──────────────────────────────────────── TC-BAT-5/6: fixture pair discriminator ─

@test "TC-BAT-5 (P2): fixture WITH network_scope — wrapper exit 0 (discriminating)" {
  [ -f "${WRAPPER_SH}" ]
  [ -f "${FIXTURE_WITH}" ]
  run bash "${WRAPPER_SH}" "${FIXTURE_WITH}"
  # CX-963-3 P2 boundary: WITH field = PASS
  [ "$status" -eq 0 ]
  # F-CR-963-1: discriminating assertion — enum path engaged (network_scope=offline in output)
  echo "$output" | grep -q "network_scope=offline"
  # F-CR-963-1: legacy-grace path NOT triggered (no legacy-boolean-detected in output)
  ! echo "$output" | grep -q "legacy-boolean-detected"
}

@test "TC-BAT-6 (P2): fixture WITHOUT network_scope — wrapper exit 1 (discriminating)" {
  [ -f "${WRAPPER_SH}" ]
  [ -f "${FIXTURE_WITHOUT}" ]
  run bash "${WRAPPER_SH}" "${FIXTURE_WITHOUT}"
  # CX-963-3 P2 boundary: WITHOUT field = WARN
  [ "$status" -eq 1 ]
}

# ──────────────────────────────────────── TC-BAT-7: ADR-061 thin wrapper ─────────

@test "TC-BAT-7 (P0): ADR-061 정합 — shell wrapper is thin (exec python3 single invoke)" {
  [ -f "${WRAPPER_SH}" ]
  # ADR-061 §결정 1: thin wrapper = exec python3 single line, no multi-line logic
  grep -q "exec python3" "${WRAPPER_SH}"
  # No multi-line heredoc python (ADR-061 §결정 2 violation guard)
  ! grep -q "<<'PYEOF'" "${WRAPPER_SH}"
}

# ──────────────────────────────────────── TC-BAT-8: byte-identical self-app ──────

@test "TC-BAT-8 (P0): templates/ vs .github/workflows/ byte-identical (ADR-005 invariant)" {
  [ -f "${WORKFLOW_TEMPLATE}" ]
  [ -f "${WORKFLOW_SELFAPP}" ]
  run diff "${WORKFLOW_TEMPLATE}" "${WORKFLOW_SELFAPP}"
  # diff exit 0 = byte-identical
  [ "$status" -eq 0 ]
  # diff output must be empty
  [ -z "$output" ]
}

# ──────────────────────────────────────── TC-BAT-NEG: non-spawn-prompt filter (F-CR-963-2) ─

@test "TC-BAT-NEG (P2): non-spawn-prompt file does NOT trigger lint warning (content pre-screen)" {
  [ -f "${WRAPPER_SH}" ]
  [ -f "${FIXTURE_NON_SPAWN}" ]
  # Non-spawn-prompt file must NOT contain spawn-prompt markers (pre-screen grep must find nothing)
  # This validates the F-CR-963-2 filter logic: files without spawn-prompt anchors skip lint.
  run grep -E "(sandbox_network_required|network_scope|Codex Worker Spawn Prompt|spawn prompt boilerplate)" "${FIXTURE_NON_SPAWN}"
  # grep must find NO match (exit 1 = no match)
  [ "$status" -eq 1 ]
  # Running wrapper directly on non-spawn-prompt file returns WARNING (field absent)
  # BUT with the content pre-screen in the workflow, this file is never linted.
  # The test verifies that the fixture itself has no spawn-prompt markers (filter criterion).
  # Complementary: wrapper invoked directly exits 1 (absent) but workflow pre-screen skips it.
  run bash "${WRAPPER_SH}" "${FIXTURE_NON_SPAWN}"
  [ "$status" -eq 1 ]
  # Verify NO enum-detection output (confirms no false positive from spawn-prompt path)
  ! echo "$output" | grep -q "network_scope=offline"
}
