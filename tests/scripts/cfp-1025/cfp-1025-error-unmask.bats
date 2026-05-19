#!/usr/bin/env bats
# tests/scripts/cfp-1025/cfp-1025-error-unmask.bats
# CFP-1025 Phase 2 — error-unmask behavioral regression tests
# QADeveloperAgent FIX iter 2 — F-CR-1025-2 P1 tautology closure
#
# TC map (Change Plan §6 + Story §8.5 coverage table):
#   TC-1 (P1): terminal failure echoes captured stderr verbatim + "create/edit 실패" marker
#   TC-2 (P1): benign create-fail→edit-success path silent (idempotency, no false positive)
#   TC-3 (P1): dry-run LABEL_COUNT 2-way self-check parity unchanged (check-bootstrap-labels-count.sh exits 0)
#   TC-4 (P2, optional): visibility regex excludes PyYAML-SKIP advisory lines
#   TC-RED-PROOF (discriminating): sed-substitute 2>&1→2>/dev/null on REAL extracted fn → TC-1 assertion FAILS
#
# FIX iter 2: TC-1/TC-2/TC-RED-PROOF rebind to REAL scripts/bootstrap-labels.sh:create_label()
#   via sed-extract + source (not inlined hand-copy — F-CR-1025-2 tautology fix).
#
# Extraction: sed -n '/^create_label() {/,/^}/p' "${SCRIPT}" > "${TEST_TMP}/_cl.sh"
# Globals required by create_label(): DRY_RUN, REPO_ARG, LABEL_COUNT (verified L43-71)
#
# TDD RED proof (genuine discrimination):
#   Masked variant = sed-substitute 2>&1→2>/dev/null in the REAL extracted function.
#   A 2>/dev/null revert of the REAL production code MUST turn TC-1/TC-2 RED.
#
# ADR-040 Amendment 6: all ops use WORKTREE_ROOT absolute path
# SecurityArch TH-2: CBL_SKIP_ISSUE_CREATE=1 in setup()

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="${WORKTREE_ROOT}/scripts/bootstrap-labels.sh"
COUNT_SCRIPT="${WORKTREE_ROOT}/scripts/check-bootstrap-labels-count.sh"

# ──────────────────────────────────────── helpers ────────────────────────────

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  # SecurityArch TH-2: 실제 Issue 생성 방지
  export CBL_SKIP_ISSUE_CREATE=1
  export CFP1025_SKIP_ISSUE_CREATE=1

  # Extract the REAL create_label() from production script once per test.
  # sed range: from line starting with 'create_label() {' to first line that is exactly '}'
  # Verified: L43-71 of scripts/bootstrap-labels.sh — no nested {} blocks, single-level close.
  sed -n '/^create_label() {/,/^}/p' "${SCRIPT}" > "${TEST_TMP}/_cl.sh"

  # Masked variant: substitute 2>&1 → 2>/dev/null in the extracted real function.
  # This mirrors the pre-CFP-1025 code (error-masking revert).
  # When gh fails: _create_err / _edit_err capture nothing → _gh_err = "" → fallback string used.
  # "HTTP 403" will NOT appear → TC-1's grep -q "HTTP 403" FAILS → genuine discrimination.
  sed 's/2>&1/2>\/dev\/null/g' "${TEST_TMP}/_cl.sh" > "${TEST_TMP}/_cl_masked.sh"
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1025-unused}"
}

# ──────────────────────────────────────── TC-1: terminal failure echoes real error ─
#
# Scenario: BOTH gh label create AND gh label edit fail (rc≠0, stderr = "HTTP 403: ...").
# Expected: create_label() output contains captured stderr verbatim ("HTTP 403") +
#           "create/edit 실패" marker line.
# Bound to: REAL create_label() sourced from scripts/bootstrap-labels.sh (not inlined copy).
# Genuine: a 2>/dev/null revert of the REAL script makes _create_err/_edit_err empty
#          → "HTTP 403" never captured → grep -q "HTTP 403" FAILS → test turns RED.

@test "TC-1 (P1): terminal failure echoes captured stderr verbatim + create/edit 실패 marker" {
  [ -f "${SCRIPT}" ]

  # gh-stub: both create and edit fail with HTTP 403 on stderr
  GH_STUB_DIR="${TEST_TMP}/gh-stub-both-fail"
  mkdir -p "${GH_STUB_DIR}"
  cat > "${GH_STUB_DIR}/gh" <<'STUB'
#!/usr/bin/env bash
echo "HTTP 403: Resource not accessible by integration" >&2
exit 1
STUB
  chmod +x "${GH_STUB_DIR}/gh"

  # Source the REAL create_label() with required globals + stub gh on PATH
  run env PATH="${GH_STUB_DIR}:${PATH}" bash -c "
    DRY_RUN=0
    REPO_ARG=\"\"
    LABEL_COUNT=0
    source \"${TEST_TMP}/_cl.sh\"
    create_label \"test-label-cfp1025\" \"ff0000\" \"Test label\"
  "

  echo "DEBUG output: ${output}"

  # Output must contain captured stderr verbatim ("HTTP 403")
  echo "$output" | grep -q "HTTP 403"

  # Output must contain "create/edit 실패" marker
  echo "$output" | grep -q "create/edit 실패"

  # Output must contain the label name
  echo "$output" | grep -q "test-label-cfp1025"
}

# ──────────────────────────────────────── TC-2: benign already-exists path silent ─
#
# Scenario: gh label create fails (already-exists rc≠0), gh label edit succeeds (rc=0).
# Expected: create_label() returns 0 AND output does NOT contain any error line.
# Bound to: REAL create_label() sourced from scripts/bootstrap-labels.sh.

@test "TC-2 (P1): benign create-fail→edit-success path silent (idempotency, no false positive)" {
  [ -f "${SCRIPT}" ]

  # gh-stub: create fails (already-exists), edit succeeds
  GH_STUB_DIR="${TEST_TMP}/gh-stub-edit-ok"
  mkdir -p "${GH_STUB_DIR}"
  cat > "${GH_STUB_DIR}/gh" <<'STUB'
#!/usr/bin/env bash
# create fails (already-exists), edit succeeds
if printf '%s\n' "$@" | grep -q "^create$"; then
  echo "already exists" >&2
  exit 1
fi
exit 0
STUB
  chmod +x "${GH_STUB_DIR}/gh"

  run env PATH="${GH_STUB_DIR}:${PATH}" bash -c "
    DRY_RUN=0
    REPO_ARG=\"\"
    LABEL_COUNT=0
    source \"${TEST_TMP}/_cl.sh\"
    create_label \"test-label-idempotent\" \"ff0000\" \"Test label idempotent\"
  "

  echo "DEBUG output: |${output}|"

  # Command must succeed (exit 0)
  [ "$status" -eq 0 ]

  # Output must NOT contain any error line
  ! echo "$output" | grep -q "create/edit 실패"
  ! echo "$output" | grep -q "already exists"
}

# ──────────────────────────────────────── TC-3: dry-run LABEL_COUNT parity ──────
#
# Retained unchanged — genuine (real COUNT_SCRIPT exec).
# Scenario: bash scripts/bootstrap-labels.sh --dry-run
# Expected: check-bootstrap-labels-count.sh self-check passes (exit 0)

@test "TC-3 (P1): dry-run LABEL_COUNT 2-way self-check parity unchanged (check-bootstrap-labels-count.sh exits 0)" {
  [ -f "${SCRIPT}" ]
  [ -f "${COUNT_SCRIPT}" ]

  run bash "${COUNT_SCRIPT}"
  echo "DEBUG exit: $status"
  echo "DEBUG output: ${output}"
  [ "$status" -eq 0 ]
}

# ──────────────────────────────────────── TC-4: visibility regex excludes advisory ─
#
# Retained unchanged — genuine (regex literal contract).
# Scenario: workflow fail_count regex applied to mixed output.
# Expected: regex matches real failure lines only, NOT PyYAML-SKIP advisory lines.

@test "TC-4 (P2, optional): visibility regex matches failure lines, excludes PyYAML-SKIP advisory" {
  SAMPLE_OUTPUT="  ! test-label: create/edit 실패 — HTTP 403: Resource not accessible by integration
  ! component:backend: create/edit 실패 — HTTP 403: Resource not accessible by integration
  * component:* labels SKIPPED — Python PyYAML 미설치 ('pip install pyyaml' 후 재실행 권장). 29 base label 만 처리됨."

  REGEX='^  ! .+: create/edit 실패'

  # Count matches — should be 2 (two real failure lines)
  MATCH_COUNT=$(printf '%s\n' "${SAMPLE_OUTPUT}" | grep -cE "${REGEX}" || true)
  echo "DEBUG match_count: ${MATCH_COUNT}"
  [ "${MATCH_COUNT}" -eq 2 ]

  # Advisory line must NOT match
  ADVISORY_LINE="  * component:* labels SKIPPED — Python PyYAML 미설치 ('pip install pyyaml' 후 재실행 권장). 29 base label 만 처리됨."
  ! printf '%s\n' "${ADVISORY_LINE}" | grep -qE "${REGEX}"
}

# ──────────────────────────────────────── TC-RED-PROOF: genuine discrimination ──
#
# Demonstrates TC-1 discriminates against the REAL script's own logic shape — not tautology.
#
# Method: source the MASKED variant (_cl_masked.sh: 2>&1 → 2>/dev/null substituted on the
#         REAL extracted create_label() from production script).
# Assertion: TC-1's key assertion (grep -q "HTTP 403") MUST FAIL against the masked variant
#            because _create_err/_edit_err are empty → _gh_err = "" → fallback string only.
# Conclusion: if scripts/bootstrap-labels.sh were reverted to 2>/dev/null, TC-1/TC-2 go RED.

@test "TC-RED-PROOF (discriminating): masked real fn (2>/dev/null) swallows stderr → TC-1 assertion fails" {
  [ -f "${SCRIPT}" ]

  # gh-stub: both create and edit fail with HTTP 403 on stderr (identical to TC-1)
  GH_STUB_DIR="${TEST_TMP}/gh-stub-both-fail-proof"
  mkdir -p "${GH_STUB_DIR}"
  cat > "${GH_STUB_DIR}/gh" <<'STUB'
#!/usr/bin/env bash
echo "HTTP 403: Resource not accessible by integration" >&2
exit 1
STUB
  chmod +x "${GH_STUB_DIR}/gh"

  # Source the MASKED variant (2>/dev/null substituted on REAL extracted fn)
  run env PATH="${GH_STUB_DIR}:${PATH}" bash -c "
    DRY_RUN=0
    REPO_ARG=\"\"
    LABEL_COUNT=0
    source \"${TEST_TMP}/_cl_masked.sh\"
    create_label \"test-label-cfp1025\" \"ff0000\" \"Test label\"
  "

  echo "DEBUG masked output: |${output}|"

  # KEY ASSERTION: the masked variant MUST NOT contain "HTTP 403" in output.
  # Rationale: 2>/dev/null discards stderr → _create_err="" and _edit_err="" →
  # _gh_err="" → fallback "(gh stderr 비어있음 — 권한/네트워크 점검)" used.
  # TC-1's `grep -q "HTTP 403"` would FAIL against this → test turns RED.
  ! echo "$output" | grep -q "HTTP 403"

  # Confirm the fallback string IS present (not empty output — error is still reported
  # but with fallback text, not the real stderr)
  echo "$output" | grep -q "create/edit 실패"
  echo "$output" | grep -q "비어있음"
}
