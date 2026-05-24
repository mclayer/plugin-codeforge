#!/usr/bin/env bats
# tests/scripts/test_check-baseline-pin-verify-sh.sh
# CFP-1410 Phase 2 / ADR-073 Amendment 9 — bats 4 TC (T-7 ~ T-10)
#
# TC coverage:
#   T-7:  baseline_pin field 부재 → warning exit 1
#   T-8:  freshness ≥ 30min (stale) → warning exit 1
#   T-9:  field 존재 + freshness < 30min → silent PASS exit 0
#   T-10: bypass env (BYPASS_BASELINE_PIN_VERIFY=1) silent skip exit 0
#
# RED→GREEN stash proof evidence artifact (CFP-1334 §8.4 mandate):
#   - pre_impl_sha: 761d877 (Phase 1 declarative merge, pre-Phase-2 HEAD)
#   - method: git stash push -- scripts/lib/check_baseline_pin_verify.py
#   - fixture_file: tests/scripts/test_check-baseline-pin-verify-sh.sh
#   - assertion_classification:
#       - T-7 discriminating: field presence check FAILS without Python SSOT
#       - T-8 discriminating: freshness stale detection FAILS without Python SSOT
#       - T-9 regression_guard: PASS on valid input
#       - T-10 regression_guard: bypass env accepted
#   - platform_verified: [linux] (CI runner) + Windows-git-bash advisory
#   - stash_evidence_excerpt: pre-impl (761d877) stash push scripts/lib/check_baseline_pin_verify.py
#       → T-7 + T-8 FAIL (Python SSOT missing) → stash pop → T-7+T-8 PASS (discriminating recovery)

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
REPO_ROOT="${BATS_TEST_DIRNAME}/../.."
PYTHON_SSOT="${REPO_ROOT}/scripts/lib/check_baseline_pin_verify.py"

setup() {
    unset BYPASS_BASELINE_PIN_VERIFY || true
    unset BASELINE_PIN_MOCK_NOW_EPOCH || true
    unset BASELINE_PIN_STALE_MINUTES || true
    # Create temp dir for fixture files
    TMP_DIR="$(mktemp -d)"
}

teardown() {
    unset BYPASS_BASELINE_PIN_VERIFY || true
    unset BASELINE_PIN_MOCK_NOW_EPOCH || true
    unset BASELINE_PIN_STALE_MINUTES || true
    [ -n "${TMP_DIR:-}" ] && [ -d "${TMP_DIR}" ] && rm -rf "${TMP_DIR}"
}

# ---------------------------------------------------------------------------
# T-7: baseline_pin field 부재 → warning exit 1 (discriminating)
# ---------------------------------------------------------------------------
@test "T-7 (discriminating): baseline_pin fields absent → warning exit 1" {
    # Story file without baseline_pin fields
    cat > "${TMP_DIR}/story-no-pin.md" <<'STORY'
# Story CFP-1410

## §1 Problem Statement
Some story content without baseline pin fields.

## §3 Design
No pin here.
STORY

    run python3 "${PYTHON_SSOT}" "${TMP_DIR}/story-no-pin.md"
    [ "$status" -eq 1 ]
    [[ "$output" == *"WARNING"* ]]
    [[ "$output" == *"missing"* ]] || [[ "$output" == *"baseline_pin"* ]]
}

# ---------------------------------------------------------------------------
# T-8: freshness ≥ 30min (stale) → warning exit 1 (discriminating)
# ---------------------------------------------------------------------------
@test "T-8 (discriminating): stale baseline_pin_verified_at (≥ 30min old) → warning exit 1" {
    # Mock now = Unix epoch 3600 (1970-01-01T01:00:00Z)
    # Pin timestamp = 1970-01-01T00:00:00Z (epoch 0) → age = 60 min ≥ 30min → stale
    MOCK_NOW="3600"
    PIN_TS="1970-01-01T00:00:00Z"
    PIN_SHA="abc1234def5678"

    cat > "${TMP_DIR}/story-stale-pin.md" <<STORY
# Story CFP-1410

baseline_pin_sha: ${PIN_SHA}
baseline_pin_verified_at: ${PIN_TS}

## Content
Some story content.
STORY

    export BASELINE_PIN_MOCK_NOW_EPOCH="${MOCK_NOW}"
    run python3 "${PYTHON_SSOT}" "${TMP_DIR}/story-stale-pin.md"
    [ "$status" -eq 1 ]
    [[ "$output" == *"WARNING"* ]]
    [[ "$output" == *"stale"* ]] || [[ "$output" == *"minutes old"* ]]
}

# ---------------------------------------------------------------------------
# T-9: field 존재 + freshness < 30min → silent PASS exit 0 (regression_guard)
# ---------------------------------------------------------------------------
@test "T-9 (regression_guard): valid baseline_pin fields + fresh timestamp → PASS exit 0" {
    # Mock now = Unix epoch 1200 (20 min)
    # Pin timestamp = epoch 0 (1970-01-01T00:00:00Z) → age = 20 min < 30min → PASS
    MOCK_NOW="1200"
    PIN_TS="1970-01-01T00:00:00Z"
    PIN_SHA="deadbeef1234"

    cat > "${TMP_DIR}/story-fresh-pin.md" <<STORY
# Story CFP-1410

baseline_pin_sha: ${PIN_SHA}
baseline_pin_verified_at: ${PIN_TS}

## Content
Story with valid fresh pin.
STORY

    export BASELINE_PIN_MOCK_NOW_EPOCH="${MOCK_NOW}"
    run python3 "${PYTHON_SSOT}" "${TMP_DIR}/story-fresh-pin.md"
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"* ]]
}

# ---------------------------------------------------------------------------
# T-10: bypass env silent skip (regression_guard)
# ---------------------------------------------------------------------------
@test "T-10 (regression_guard): BYPASS_BASELINE_PIN_VERIFY=1 → silent skip exit 0" {
    # Even missing fields + stale → bypass takes precedence
    cat > "${TMP_DIR}/story-missing.md" <<'STORY'
# Story without pin
No baseline pin here.
STORY

    export BYPASS_BASELINE_PIN_VERIFY="1"
    run python3 "${PYTHON_SSOT}" "${TMP_DIR}/story-missing.md"
    [ "$status" -eq 0 ]
    [[ "$output" != *"WARNING"* ]]
}
