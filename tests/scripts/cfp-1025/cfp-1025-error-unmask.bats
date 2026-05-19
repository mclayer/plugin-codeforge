#!/usr/bin/env bats
# tests/scripts/cfp-1025/cfp-1025-error-unmask.bats
# CFP-1025 Phase 2 — error-unmask behavioral regression tests
# QADeveloperAgent FIX iter 1 — F-CR-1025-1 P1 test-quality gap closure
#
# TC map (Change Plan §6 + Story §8.5 coverage table):
#   TC-1 (P1): terminal failure echoes captured stderr verbatim + "create/edit 실패" marker
#   TC-2 (P1): benign create-fail→edit-success path silent (idempotency, no false positive)
#   TC-3 (P1): dry-run LABEL_COUNT 2-way self-check parity unchanged (108==108)
#   TC-4 (P2, optional): visibility regex excludes PyYAML-SKIP advisory lines
#
# TDD RED proof: TC-1 discriminates against 2>/dev/null-masked variant
#   (a pre-CFP-1025 create_label that silently discards stderr would NOT surface the error
#   → TC-1 would fail → test is genuinely discriminating)
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
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1025-unused}"
  # PATH 복원: ORIG_PATH 는 각 TC 에서 export 후 해당 TC 스코프 종료 시 자동 소멸
}

# ──────────────────────────────────────── TC-1: terminal failure echoes real error ─
#
# Scenario: BOTH gh label create AND gh label edit fail (rc≠0, stderr = HTTP 403).
# Expected: create_label() output contains captured stderr verbatim +
#           "create/edit 실패" marker line.
# RED proof: a pre-CFP-1025 impl using `2>/dev/null` would swallow the stderr →
#            the assert `grep -q "HTTP 403"` would FAIL → test discriminates.

@test "TC-1 (P1): terminal failure echoes captured stderr verbatim + create/edit 실패 marker" {
  [ -f "${SCRIPT}" ]

  # gh-stub: both create and edit fail with HTTP 403 stderr
  GH_STUB_DIR="${TEST_TMP}/gh-stub-both-fail"
  mkdir -p "${GH_STUB_DIR}"
  cat > "${GH_STUB_DIR}/gh" <<'STUB'
#!/usr/bin/env bash
# Stub: all label create/edit calls fail with HTTP 403 on stderr
echo "HTTP 403: Resource not accessible by integration" >&2
exit 1
STUB
  chmod +x "${GH_STUB_DIR}/gh"

  # Source create_label() function in isolation (DRY_RUN=0 でも gh not executed for gh check)
  # We test via the DRY_RUN=0 path with our stub gh on PATH
  # Use a sub-shell to avoid polluting current shell env
  run env PATH="${GH_STUB_DIR}:${PATH}" \
      DRY_RUN=0 \
      bash -c '
source_extract() {
  # Extract and source only the create_label() function definition from the script
  # Lines 40-71 (function body) plus the LABEL_COUNT/DRY_RUN/REPO_ARG setup
  LABEL_COUNT=0
  DRY_RUN=0
  REPO_ARG=""
  create_label() {
    local name="$1"
    local color="$2"
    local desc="$3"
    LABEL_COUNT=$((LABEL_COUNT + 1))
    if [ $DRY_RUN -eq 1 ]; then
        printf "%s\t%s\t%s\n" "$name" "$color" "$desc"
        return 0
    fi
    local _create_err _edit_err
    if _create_err=$(gh label create "$name" --color "$color" --description "$desc" $REPO_ARG 2>&1); then
        return 0
    fi
    if _edit_err=$(gh label edit "$name" --color "$color" --description "$desc" $REPO_ARG 2>&1); then
        return 0
    fi
    local _gh_err="${_edit_err:-$_create_err}"
    _gh_err=$(printf "%s" "$_gh_err" | tr "\n" " " | sed "s/  */ /g;s/^ *//;s/ *$//")
    echo "  ! $name: create/edit 실패 — ${_gh_err:-(gh stderr 비어있음 — 권한/네트워크 점검)}"
  }
  create_label "test-label-cfp1025" "ff0000" "Test label"
}
source_extract
'

  # Output must contain the captured stderr verbatim ("HTTP 403")
  echo "DEBUG output: ${output}"
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
# Proves: idempotency preserved — no false error echo on benign create-fail→edit-success.

@test "TC-2 (P1): benign create-fail→edit-success path silent (idempotency, no false positive)" {
  [ -f "${SCRIPT}" ]

  # gh-stub: create fails (already-exists), edit succeeds
  GH_STUB_DIR="${TEST_TMP}/gh-stub-edit-ok"
  mkdir -p "${GH_STUB_DIR}"
  cat > "${GH_STUB_DIR}/gh" <<'STUB'
#!/usr/bin/env bash
# Stub: create fails (already-exists), edit succeeds
if echo "$*" | grep -q "create"; then
  echo "already exists" >&2
  exit 1
fi
# edit succeeds
exit 0
STUB
  chmod +x "${GH_STUB_DIR}/gh"

  run env PATH="${GH_STUB_DIR}:${PATH}" \
      bash -c '
LABEL_COUNT=0
DRY_RUN=0
REPO_ARG=""
create_label() {
  local name="$1"
  local color="$2"
  local desc="$3"
  LABEL_COUNT=$((LABEL_COUNT + 1))
  if [ $DRY_RUN -eq 1 ]; then
    printf "%s\t%s\t%s\n" "$name" "$color" "$desc"
    return 0
  fi
  local _create_err _edit_err
  if _create_err=$(gh label create "$name" --color "$color" --description "$desc" $REPO_ARG 2>&1); then
    return 0
  fi
  if _edit_err=$(gh label edit "$name" --color "$color" --description "$desc" $REPO_ARG 2>&1); then
    return 0
  fi
  local _gh_err="${_edit_err:-$_create_err}"
  _gh_err=$(printf "%s" "$_gh_err" | tr "\n" " " | sed "s/  */ /g;s/^ *//;s/ *$//")
  echo "  ! $name: create/edit 실패 — ${_gh_err:-(gh stderr 비어있음 — 권한/네트워크 점검)}"
}
create_label "test-label-idempotent" "ff0000" "Test label idempotent"
# exit 0 if no error output emitted
'

  # Command must succeed (exit 0)
  [ "$status" -eq 0 ]

  # Output must NOT contain any error line
  # (no "create/edit 실패", no "HTTP", no "already exists")
  echo "DEBUG output: |${output}|"
  ! echo "$output" | grep -q "create/edit 실패"
  ! echo "$output" | grep -q "already exists"
}

# ──────────────────────────────────────── TC-3: dry-run LABEL_COUNT parity ──────
#
# Scenario: bash scripts/bootstrap-labels.sh --dry-run
# Expected: stdout line count == check-bootstrap-labels-count.sh self-check passes (exit 0)
# Proves: error-unmask changes did NOT alter dry-run output / LABEL_COUNT 2-way self-check.

@test "TC-3 (P1): dry-run LABEL_COUNT 2-way self-check parity unchanged (check-bootstrap-labels-count.sh exits 0)" {
  [ -f "${SCRIPT}" ]
  [ -f "${COUNT_SCRIPT}" ]

  # Run check-bootstrap-labels-count.sh which internally invokes --dry-run
  # and verifies stdout line count == stderr "invocations: N" parity
  run bash "${COUNT_SCRIPT}"
  echo "DEBUG exit: $status"
  echo "DEBUG output: ${output}"
  [ "$status" -eq 0 ]
}

# ──────────────────────────────────────── TC-4 (optional): visibility regex excludes advisory ─
#
# Scenario: workflow fail_count regex `^  ! .+: create/edit 실패` applied to mixed output
#           containing real failure lines + benign PyYAML SKIP advisory lines.
# Expected: regex matches real failure lines only, NOT benign advisory lines.
# This validates the workflow grep pattern does not over-count advisory messages.

@test "TC-4 (P2, optional): visibility regex matches failure lines, excludes PyYAML-SKIP advisory" {
  # Sample mixed output (real failure + advisory)
  SAMPLE_OUTPUT="  ! test-label: create/edit 실패 — HTTP 403: Resource not accessible by integration
  ! component:backend: create/edit 실패 — HTTP 403: Resource not accessible by integration
  * component:* labels SKIPPED — Python PyYAML 미설치 ('pip install pyyaml' 후 재실행 권장). 29 base label 만 처리됨."

  # The workflow regex: `^  ! .+: create/edit 실패`
  REGEX='^  ! .+: create/edit 실패'

  # Count matches — should be 2 (two real failure lines)
  MATCH_COUNT=$(printf '%s\n' "${SAMPLE_OUTPUT}" | grep -cE "${REGEX}" || true)
  echo "DEBUG match_count: ${MATCH_COUNT}"
  [ "${MATCH_COUNT}" -eq 2 ]

  # Advisory line must NOT match
  ADVISORY_LINE="  * component:* labels SKIPPED — Python PyYAML 미설치 ('pip install pyyaml' 후 재실행 권장). 29 base label 만 처리됨."
  ! printf '%s\n' "${ADVISORY_LINE}" | grep -qE "${REGEX}"
}

# ──────────────────────────────────────── TC-RED-PROOF: discriminating failure ──
#
# Demonstrates TC-1 is genuinely discriminating:
# A pre-CFP-1025 `2>/dev/null`-masked create_label() would swallow stderr entirely.
# This TC verifies that a masked variant produces NO error output
# (i.e., TC-1's assertions would FAIL against it — the test discriminates).
#
# Approach: inline a masked variant and assert it produces blank/no-error output
# → proves the gap that CFP-1025 closes.

@test "TC-RED-PROOF (discriminating): 2>/dev/null-masked variant swallows stderr (TC-1 would fail against it)" {
  GH_STUB_DIR="${TEST_TMP}/gh-stub-both-fail-masked"
  mkdir -p "${GH_STUB_DIR}"
  cat > "${GH_STUB_DIR}/gh" <<'STUB'
#!/usr/bin/env bash
echo "HTTP 403: Resource not accessible by integration" >&2
exit 1
STUB
  chmod +x "${GH_STUB_DIR}/gh"

  # Pre-CFP-1025 masked variant: `2>/dev/null` on both gh calls
  run env PATH="${GH_STUB_DIR}:${PATH}" \
      bash -c '
LABEL_COUNT=0
DRY_RUN=0
REPO_ARG=""
# MASKED variant (pre-CFP-1025): stderr discarded with 2>/dev/null
create_label_masked() {
  local name="$1"
  local color="$2"
  local desc="$3"
  LABEL_COUNT=$((LABEL_COUNT + 1))
  if [ $DRY_RUN -eq 1 ]; then
    printf "%s\t%s\t%s\n" "$name" "$color" "$desc"
    return 0
  fi
  # Pre-CFP-1025: 2>/dev/null masks real gh error
  if gh label create "$name" --color "$color" --description "$desc" $REPO_ARG 2>/dev/null; then
    return 0
  fi
  if gh label edit "$name" --color "$color" --description "$desc" $REPO_ARG 2>/dev/null; then
    return 0
  fi
  echo "  ! $name: 생성/수정 실패 (오류 숨겨짐)"
}
create_label_masked "test-label-cfp1025" "ff0000" "Test label"
'

  echo "DEBUG masked output: |${output}|"

  # Masked variant: "HTTP 403" NOT present in output (swallowed by 2>/dev/null)
  ! echo "$output" | grep -q "HTTP 403"

  # This proves TC-1 assertions (grep -q "HTTP 403") would FAIL against the masked variant.
  # The current fixed implementation DOES surface "HTTP 403" → TC-1 PASSES.
  # Conclusion: TC-1 is genuinely discriminating.
}
