#!/usr/bin/env bats
# tests/scripts/cfp-1059-s5/check-deployment-schema.bats
# CFP-1059-S5 Phase 2 — consumer overlay deploy.* schema validation (TDD)
# QADeveloperAgent TDD (RED written → GREEN against implemented check_deployment_schema.py)
#
# TC map (Change Plan §8.1):
#   TC-1: valid-full.yaml          → PASS (exit 0) — 5 sub-field 전부 정합
#   TC-2: missing-host-mapping     → FAIL (exit 1) — host_mapping 누락
#   TC-3: type-mismatch            → FAIL (exit 1) — traefik.enabled string != bool
#   TC-4: no-deploy-block          → PASS (exit 0, skip) — deploy block 부재 = opt-in
#   TC-5: 1password-disabled-prod  → PASS (exit 0) — warning emit, not FAIL
#
# ADR refs:
#   ADR-061: external .py mandatory (multi-line Python)
#   ADR-070: yaml.safe_load verify-before-trust (grep heuristic 금지)
#   ADR-089: fail-loud (yaml.YAMLError → exit 2)
#   ADR-060: exit code 3-tier (0 PASS / 1 FAIL / 2 lint-internal-error)
#   §7 SecurityArch: secret value dereference 0 (env-name only)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="${WORKTREE_ROOT}/scripts/check_deployment_schema.py"
FIXTURES="${WORKTREE_ROOT}/tests/scripts/cfp-1059-s5/fixtures"

# ────────────────────────────── setup / teardown ─────────────────────────────

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1059-s5-unused}"
}

# ────────────────────────────────── TC-1 ─────────────────────────────────────

@test "TC-1: valid-full.yaml — all 5 sub-fields valid → exit 0 (PASS)" {
  [ -f "${SCRIPT}" ]
  [ -f "${FIXTURES}/valid-full.yaml" ]

  run python3 "${SCRIPT}" "${FIXTURES}/valid-full.yaml"
  [ "$status" -eq 0 ]
}

# ────────────────────────────────── TC-2 ─────────────────────────────────────

@test "TC-2: missing-host-mapping.yaml — host_mapping absent → exit 1 (FAIL)" {
  [ -f "${SCRIPT}" ]
  [ -f "${FIXTURES}/missing-host-mapping.yaml" ]

  run python3 "${SCRIPT}" "${FIXTURES}/missing-host-mapping.yaml"
  [ "$status" -eq 1 ]
  # Output must mention host_mapping (finding name, not secret value)
  [[ "$output" =~ host_mapping ]]
}

# ────────────────────────────────── TC-3 ─────────────────────────────────────

@test "TC-3: type-mismatch.yaml — traefik.enabled is string not bool → exit 1 (FAIL)" {
  [ -f "${SCRIPT}" ]
  [ -f "${FIXTURES}/type-mismatch.yaml" ]

  run python3 "${SCRIPT}" "${FIXTURES}/type-mismatch.yaml"
  [ "$status" -eq 1 ]
  # Finding must reference traefik field
  [[ "$output" =~ traefik ]]
}

# ────────────────────────────────── TC-4 ─────────────────────────────────────

@test "TC-4: no-deploy-block.yaml — deploy block absent → exit 0 (opt-in PASS)" {
  [ -f "${SCRIPT}" ]
  [ -f "${FIXTURES}/no-deploy-block.yaml" ]

  run python3 "${SCRIPT}" "${FIXTURES}/no-deploy-block.yaml"
  [ "$status" -eq 0 ]
}

# ────────────────────────────────── TC-5 ─────────────────────────────────────

@test "TC-5: 1password-disabled-prod.yaml — 1password disabled + production → exit 0 (warning, not FAIL)" {
  [ -f "${SCRIPT}" ]
  [ -f "${FIXTURES}/1password-disabled-prod.yaml" ]

  run python3 "${SCRIPT}" "${FIXTURES}/1password-disabled-prod.yaml"
  # Must PASS (exit 0), warning only — not a hard FAIL
  [ "$status" -eq 0 ]
  # Warning must be emitted (output non-empty or contains warning indicator)
  [[ "$output" =~ [Ww]arning|WARN|warn ]]
}

# ────────────────────────── TC-security: no secret leak ──────────────────────

@test "TC-security: FAIL output contains field names only — no secret values leaked" {
  [ -f "${SCRIPT}" ]
  [ -f "${FIXTURES}/missing-host-mapping.yaml" ]

  # Inject a fake secret env value to ensure it does NOT appear in output
  export DOCKERHUB_TOKEN="SUPER_SECRET_VALUE_MUST_NOT_APPEAR"
  export OP_CONNECT_TOKEN="ANOTHER_SECRET_VALUE"
  export SSH_DEPLOY_KEY="SSH_SECRET_KEY_VALUE"

  run python3 "${SCRIPT}" "${FIXTURES}/missing-host-mapping.yaml"
  # Output must NOT contain the actual secret values (env-name only in findings)
  [[ ! "$output" =~ "SUPER_SECRET_VALUE_MUST_NOT_APPEAR" ]]
  [[ ! "$output" =~ "ANOTHER_SECRET_VALUE" ]]
  [[ ! "$output" =~ "SSH_SECRET_KEY_VALUE" ]]
}

# ─────────────────────────── TC-parse-error: exit 2 ─────────────────────────

@test "TC-parse-error: malformed YAML → exit 2 (lint-internal-error, fail-loud ADR-089)" {
  [ -f "${SCRIPT}" ]

  # Write malformed YAML to temp file
  printf 'deploy:\n  host_mapping: [\n  unclosed_bracket\n' > "${TEST_TMP}/malformed.yaml"

  run python3 "${SCRIPT}" "${TEST_TMP}/malformed.yaml"
  [ "$status" -eq 2 ]
}

# ─────────────────────────── TC-absent: exit 0 ───────────────────────────────

@test "TC-absent: overlay file absent → exit 0 (opt-in PASS)" {
  [ -f "${SCRIPT}" ]

  run python3 "${SCRIPT}" "/nonexistent/path/project.yaml"
  [ "$status" -eq 0 ]
}
