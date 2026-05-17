#!/usr/bin/env bats
# tests/scripts/cfp-821/cfp-821-coverage-fanout.bats
# CFP-821 Phase 2 — D1+D2+D3 coverage fan-out discriminating tests
# QADeveloperAgent TDD (RED written before implementation exists)
#
# TC map (Change Plan §8):
#   TC-D1-1: D1 Issue template files exist (5 forms + config.yml)
#   TC-D1-2: D1 PULL_REQUEST_TEMPLATE.md byte-identical with .github/
#   TC-D1-3: D1 D4 marker block presence on *.yml (whole-line anchored)
#   TC-D1-3b: D1 D4 marker block presence on PULL_REQUEST_TEMPLATE.md (<!-- BEGIN/END wrapper-managed -->)
#   TC-D1-4: TC-D1-4 byte-identical: templates/.github/ forms == .github/ISSUE_TEMPLATE/ (3 new forms)
#   TC-D2-1: D2 setup-branch-protection.sh exists + --dry-run triggers ZERO API writes
#   TC-D2-2: D2 core 4 invariant: missing core context → exit 1
#   TC-D2-3: D2 exit codes: no-drift=0, drift=2, error=1
#   TC-D2-4: D2 idempotent: repeated --dry-run = same output, no side effects
#   TC-D3-1: D3 docs/script-boundary.md exists with 3 categories
#   TC-D3-2: D3 ADR cross-ref (ADR-039 + ADR-061) + (k) follow-up note
#   TC-INT-1: INT reconcile-protocol-v1 v1.6 + MANIFEST + ADR-027 Amd5 present (Phase 1 verify)
#   TC-AC11-1: AC-11 ZERO Administration:write — no gh api PUT/PATCH/POST to branch_protection
#   TC-YAML-1: evidence-checks-registry.yaml YAML parse + branch-protection-sync entry reachable + indent invariant

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

SETUP_SCRIPT="${WORKTREE_ROOT}/templates/scripts/setup-branch-protection.sh"
MANIFEST="${WORKTREE_ROOT}/templates/branch-protection-manifest.yaml"
MARKER_LINT="${WORKTREE_ROOT}/scripts/check-wrapper-managed-block.sh"

# ──────────────────────────────────────── helpers ────────────────────────────

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-821-unused}"
}

# ──────────────────────────────────────── D1 Tests ───────────────────────────

@test "TC-D1-1: templates/.github/ISSUE_TEMPLATE/ has exactly 5 yml forms + config.yml" {
  TMPL_DIR="${WORKTREE_ROOT}/templates/.github/ISSUE_TEMPLATE"

  # pre-change FAIL: directory does not exist → post-change PASS
  [ -d "${TMPL_DIR}" ]

  # exactly 5 .yml forms
  mapfile -t yml_files < <(find "${TMPL_DIR}" -maxdepth 1 -name "*.yml" -not -name "config.yml" | sort)
  [ "${#yml_files[@]}" -eq 5 ]

  # each expected form exists
  [ -f "${TMPL_DIR}/audit.yml" ]
  [ -f "${TMPL_DIR}/bug.yml" ]
  [ -f "${TMPL_DIR}/story.yml" ]
  [ -f "${TMPL_DIR}/discussion.yml" ]
  [ -f "${TMPL_DIR}/codeforge-improvement.yml" ]

  # config.yml exists
  [ -f "${TMPL_DIR}/config.yml" ]
}

@test "TC-D1-2: templates/.github/PULL_REQUEST_TEMPLATE.md byte-identical with .github/PULL_REQUEST_TEMPLATE.md" {
  TMPL_PR="${WORKTREE_ROOT}/templates/.github/PULL_REQUEST_TEMPLATE.md"
  LIVE_PR="${WORKTREE_ROOT}/.github/PULL_REQUEST_TEMPLATE.md"

  # pre-change FAIL: file doesn't exist
  [ -f "${TMPL_PR}" ]
  [ -f "${LIVE_PR}" ]

  # byte-identical (ADR-005) — diff must be empty
  run diff "${TMPL_PR}" "${LIVE_PR}"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "TC-D1-3: all templates/.github/ISSUE_TEMPLATE/*.yml have whole-line-anchored D4 marker block" {
  TMPL_DIR="${WORKTREE_ROOT}/templates/.github/ISSUE_TEMPLATE"

  [ -d "${TMPL_DIR}" ]

  # check-wrapper-managed-block.sh must PASS on all yml files
  # The lint validates: BEGIN/END pairing + whole-line anchored + flat-only
  local yml_files
  mapfile -t yml_files < <(find "${TMPL_DIR}" -maxdepth 1 -name "*.yml" -not -name "config.yml" | sort)

  for f in "${yml_files[@]}"; do
    # Each file must contain "# BEGIN wrapper-managed" as a whole-line marker
    run grep -c "^# BEGIN wrapper-managed$" "${f}"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]

    # Each file must contain matching "# END wrapper-managed" whole-line
    run grep -c "^# END wrapper-managed$" "${f}"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]

    # No nesting (BEGIN count must equal END count)
    begin_count=$(grep -c "^# BEGIN wrapper-managed$" "${f}" || true)
    end_count=$(grep -c "^# END wrapper-managed$" "${f}" || true)
    [ "${begin_count}" -eq "${end_count}" ]

    # Count must be exactly 1 pair (flat-only §결정 7.D.1)
    [ "${begin_count}" -eq 1 ]
  done
}

@test "TC-D1-3b: templates/.github/PULL_REQUEST_TEMPLATE.md has whole-line-anchored <!-- BEGIN/END wrapper-managed --> marker" {
  # ADR-027 Amendment 5 §결정 9.B: .md PR template = <!-- BEGIN wrapper-managed --> / <!-- END wrapper-managed -->
  TMPL_PR="${WORKTREE_ROOT}/templates/.github/PULL_REQUEST_TEMPLATE.md"
  LIVE_PR="${WORKTREE_ROOT}/.github/PULL_REQUEST_TEMPLATE.md"

  [ -f "${TMPL_PR}" ]
  [ -f "${LIVE_PR}" ]

  # Both must have exactly 1 whole-line-anchored <!-- BEGIN wrapper-managed --> marker
  for f in "${TMPL_PR}" "${LIVE_PR}"; do
    run grep -c "^<!-- BEGIN wrapper-managed -->$" "${f}"
    [ "$status" -eq 0 ]
    [ "$output" -eq 1 ]

    run grep -c "^<!-- END wrapper-managed -->$" "${f}"
    [ "$status" -eq 0 ]
    [ "$output" -eq 1 ]
  done

  # byte-identical after marker addition (ADR-005)
  run diff "${TMPL_PR}" "${LIVE_PR}"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "TC-D1-4: .github/ISSUE_TEMPLATE/{story,discussion,codeforge-improvement}.yml + config.yml byte-identical with templates/" {
  for f in story.yml discussion.yml codeforge-improvement.yml config.yml; do
    TMPL="${WORKTREE_ROOT}/templates/.github/ISSUE_TEMPLATE/${f}"
    LIVE="${WORKTREE_ROOT}/.github/ISSUE_TEMPLATE/${f}"

    # Both must exist
    [ -f "${TMPL}" ]
    [ -f "${LIVE}" ]

    # byte-identical (ADR-005)
    run diff "${TMPL}" "${LIVE}"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
  done
}

# ──────────────────────────────────────── D2 Tests ───────────────────────────

@test "TC-D2-1: setup-branch-protection.sh --dry-run issues ZERO API write calls" {
  [ -f "${SETUP_SCRIPT}" ]

  # Stub gh to record any calls and fail if write operations attempted
  GH_STUB="${TEST_TMP}/gh"
  cat > "${GH_STUB}" <<'STUB'
#!/usr/bin/env bash
# Record all gh invocations
echo "$@" >> "${GH_CALL_LOG:-/tmp/gh-calls.log}"

# Detect write operations to branch protection
for arg in "$@"; do
  case "${arg}" in
    PUT|POST|PATCH|DELETE|-XPUT|-XPOST|-XPATCH|-XDELETE)
      echo "ERROR: gh write call detected: $*" >&2
      exit 99
      ;;
  esac
done

# Handle GET for branch protection read
if [[ "$*" == *"branches"*"protection"* ]]; then
  # Return a minimal response indicating drift (missing one context)
  cat <<'JSON'
{
  "required_status_checks": {
    "contexts": ["phase-gate-mergeable"]
  }
}
JSON
  exit 0
fi

# Default: gh auth status
if [[ "$1" == "auth" && "$2" == "status" ]]; then
  echo "Logged in to github.com"
  exit 0
fi

exit 0
STUB
  chmod +x "${GH_STUB}"

  GH_CALL_LOG="${TEST_TMP}/gh-calls.log"
  touch "${GH_CALL_LOG}"

  # Run with stubbed gh — must complete without API write
  run env \
    PATH="${TEST_TMP}:${PATH}" \
    GH_TOKEN="test-token-stub" \
    GH_CALL_LOG="${GH_CALL_LOG}" \
    BRANCH_PROTECTION_MANIFEST="${MANIFEST}" \
    bash "${SETUP_SCRIPT}" --dry-run

  # Must not exit 99 (write detected)
  [ "$status" -ne 99 ]

  # Must not be a script error (status 1 = error from manifest read)
  # status 0 = no drift, status 2 = drift detected (informational)
  # status 1 = error (acceptable if gh auth fails in test)
  # We just care that no API write was triggered
  if [ -f "${GH_CALL_LOG}" ]; then
    # No PUT/POST/PATCH/DELETE should appear in log
    run grep -E "\-X\s*(PUT|POST|PATCH|DELETE)|^(PUT|POST|PATCH|DELETE)" "${GH_CALL_LOG}"
    [ "$status" -ne 0 ]  # grep should find nothing (exit 1 = not found)
  fi
}

@test "TC-D2-2: setup-branch-protection.sh exits 1 when core 4 contexts are missing" {
  [ -f "${SETUP_SCRIPT}" ]

  # Create a manifest missing all core 4 contexts
  BROKEN_MANIFEST="${TEST_TMP}/broken-manifest.yaml"
  cat > "${BROKEN_MANIFEST}" <<'YAML'
required_status_checks:
  contexts:
    - name: "my-custom-check"
      type: workflow-job-name
      description: "custom only — no core 4"
YAML

  run env \
    GH_TOKEN="test-token-stub" \
    BRANCH_PROTECTION_MANIFEST="${BROKEN_MANIFEST}" \
    bash "${SETUP_SCRIPT}" --dry-run

  # exit 1 = error (core 4 missing)
  [ "$status" -eq 1 ]
}

@test "TC-D2-3: setup-branch-protection.sh exit codes: valid manifest → 0 or 2 only" {
  [ -f "${SETUP_SCRIPT}" ]

  # Stub gh to simulate no drift (current API == manifest)
  GH_STUB="${TEST_TMP}/gh"
  cat > "${GH_STUB}" <<'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"branches"*"protection"* && "$*" != *"-X"* ]]; then
  cat <<'JSON'
{
  "required_status_checks": {
    "contexts": [
      "phase-gate-mergeable",
      "invariant-check",
      "doc frontmatter schema (CFP-28 — strict)",
      "doc section schema (CFP-28 — strict)"
    ]
  }
}
JSON
  exit 0
fi
if [[ "$1" == "auth" ]]; then exit 0; fi
exit 0
STUB
  chmod +x "${GH_STUB}"

  run env \
    PATH="${TEST_TMP}:${PATH}" \
    GH_TOKEN="test-token-stub" \
    BRANCH_PROTECTION_MANIFEST="${MANIFEST}" \
    bash "${SETUP_SCRIPT}" --dry-run

  # exit 0 (no drift) or exit 2 (drift detected) — both valid informational
  # exit 1 only for error (we have valid manifest + valid gh stub)
  [ "$status" -eq 0 ] || [ "$status" -eq 2 ]
}

@test "TC-D2-4: setup-branch-protection.sh --dry-run is idempotent (no filesystem side effects)" {
  [ -f "${SETUP_SCRIPT}" ]

  GH_STUB="${TEST_TMP}/gh"
  cat > "${GH_STUB}" <<'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"branches"*"protection"* && "$*" != *"-X"* ]]; then
  echo '{"required_status_checks":{"contexts":["phase-gate-mergeable"]}}'
  exit 0
fi
if [[ "$1" == "auth" ]]; then exit 0; fi
exit 0
STUB
  chmod +x "${GH_STUB}"

  # Run twice — filesystem should not change between runs
  BEFORE_HASH=$(find "${WORKTREE_ROOT}" -name "*.lock" -o -name "*.tmp" 2>/dev/null | sort | md5sum || echo "empty")

  run env \
    PATH="${TEST_TMP}:${PATH}" \
    GH_TOKEN="test-token-stub" \
    BRANCH_PROTECTION_MANIFEST="${MANIFEST}" \
    bash "${SETUP_SCRIPT}" --dry-run
  FIRST_OUTPUT="${output}"
  FIRST_STATUS="${status}"

  run env \
    PATH="${TEST_TMP}:${PATH}" \
    GH_TOKEN="test-token-stub" \
    BRANCH_PROTECTION_MANIFEST="${MANIFEST}" \
    bash "${SETUP_SCRIPT}" --dry-run
  SECOND_OUTPUT="${output}"
  SECOND_STATUS="${status}"

  AFTER_HASH=$(find "${WORKTREE_ROOT}" -name "*.lock" -o -name "*.tmp" 2>/dev/null | sort | md5sum || echo "empty")

  # Same exit status
  [ "${FIRST_STATUS}" -eq "${SECOND_STATUS}" ]
  # No new lock/tmp files created
  [ "${BEFORE_HASH}" = "${AFTER_HASH}" ]
}

# ──────────────────────────────────────── D3 Tests ───────────────────────────

@test "TC-D3-1: docs/script-boundary.md exists with 3 categories defined" {
  DOC="${WORKTREE_ROOT}/docs/script-boundary.md"

  # pre-change FAIL: file doesn't exist
  [ -f "${DOC}" ]

  # 3 categories must be present
  run grep -c "Wrapper SSOT" "${DOC}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "Consumer overlay" "${DOC}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "Mixed-zone" "${DOC}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # Each category must have upgrade behavior described
  run grep -c "upgrade" "${DOC}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 3 ]
}

@test "TC-D3-2: docs/script-boundary.md has ADR-039 + ADR-061 cross-refs + (k) follow-up note" {
  DOC="${WORKTREE_ROOT}/docs/script-boundary.md"
  [ -f "${DOC}" ]

  # ADR-039 cross-ref
  run grep -c "ADR-039" "${DOC}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # ADR-061 cross-ref
  run grep -c "ADR-061" "${DOC}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # (k) follow-up note — bash top-level local issue is OOS (ADR-064 minimal-change)
  run grep -c "follow-up" "${DOC}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ──────────────────────────────────────── INT + AC-11 Tests ──────────────────

@test "TC-INT-1: Phase 1 artifacts present — reconcile-protocol-v1 v1.6 + MANIFEST + ADR-027 Amd5" {
  # reconcile-protocol-v1 must be at version 1.6
  PROTOCOL="${WORKTREE_ROOT}/docs/inter-plugin-contracts/reconcile-protocol-v1.md"
  [ -f "${PROTOCOL}" ]

  run grep -c 'version: "1.6"' "${PROTOCOL}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # MANIFEST must have v1.6 row
  MANIFEST_FILE="${WORKTREE_ROOT}/docs/inter-plugin-contracts/MANIFEST.yaml"
  [ -f "${MANIFEST_FILE}" ]
  run grep -c "1.6" "${MANIFEST_FILE}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # ADR-027 must have Amendment 5 (§결정 9)
  ADR027="${WORKTREE_ROOT}/docs/adr/ADR-027-consumer-adoption-protocol.md"
  [ -f "${ADR027}" ]
  run grep -c "Amendment 5" "${ADR027}"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "TC-AC11-1: setup-branch-protection.sh has ZERO Administration:write API writes" {
  [ -f "${SETUP_SCRIPT}" ]

  # Direct grep of the script source — must not contain PUT/POST/PATCH to branch_protection
  # (FORM (b) absolute: no gh api -X PUT ... branch_protection)
  run grep -E "gh api.*-X (PUT|POST|PATCH|DELETE).*branch.?protection" "${SETUP_SCRIPT}"
  [ "$status" -ne 0 ]  # grep must find nothing

  # Also check for any gh api mutation variants
  run grep -E "\-X PUT|\-XPUT" "${SETUP_SCRIPT}"
  [ "$status" -ne 0 ]  # Must have zero API write calls

  # And no curl PUT to branch_protection either
  run grep -E "curl.*-X PUT.*branch.?protection" "${SETUP_SCRIPT}"
  [ "$status" -ne 0 ]
}

@test "TC-YAML-1: evidence-checks-registry.yaml YAML parse + branch-protection-sync entry reachable + indent invariant" {
  REGISTRY="${WORKTREE_ROOT}/docs/evidence-checks-registry.yaml"
  [ -f "${REGISTRY}" ]

  # YAML must parse cleanly (no column-0 orphan sequence items)
  PARSE_PY="${BATS_TMPDIR}/parse_registry_$$.py"
  cat > "${PARSE_PY}" <<'PYEOF'
import sys, yaml
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
entries = data.get('entries', [])
names = [e['name'] for e in entries]
assert 'branch-protection-sync' in names, f"branch-protection-sync not found in entries: {names[:5]}"
print(f"PARSE OK: {len(entries)} entries, branch-protection-sync found")
PYEOF
  run python "${PARSE_PY}" "${REGISTRY}"
  [ "$status" -eq 0 ]

  # No column-0 sequence items (all entries must be 2-space indented)
  run grep -c "^- name:" "${REGISTRY}"
  [ "$status" -ne 0 ]  # grep must find ZERO column-0 "- name:" lines

  # All 66 entries must be at 2-space indent
  run grep -c "^  - name:" "${REGISTRY}"
  [ "$status" -eq 0 ]
  [ "$output" -eq 66 ]
}
