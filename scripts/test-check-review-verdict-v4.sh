#!/usr/bin/env bash
# test-check-review-verdict-v4.sh — smoke test for check-review-verdict-v4.sh (CFP-137 Phase 2)
#
# Test matrix:
#   T1: contract file present + valid → PASS
#   T2: valid packet (PASS, worker_dialog_rounds=0) → PASS
#   T3: valid packet (adversarial, worker_dialog_rounds=3) → PASS
#   T4: invalid packet (v3 deprecated field decision_state 잔존) → FAIL advisory (exit 0)
#   T5: invalid packet (worker_dialog_rounds 부재) → FAIL advisory (exit 0)
#   T6: invalid packet + --strict → exit 1
#   T7: --help → exit 0
#   T8: unknown arg → exit 2

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE_BASE="$SCRIPT_DIR/fixtures/check-review-verdict-v4"
CHECK_SCRIPT="$SCRIPT_DIR/check-review-verdict-v4.sh"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

# ─────────────────────────────────────────
# T1: contract file present + valid → PASS (0 FAIL)
# ─────────────────────────────────────────
log "T1: contract file valid → 0 FAIL"
rc=0
output="$(bash "$CHECK_SCRIPT" \
    --contract "$REPO_ROOT/docs/inter-plugin-contracts/review-verdict-v4.md" \
    --quiet 2>&1)" || rc=$?
fail_count="$(printf '%s' "$output" | grep -c '\[FAIL\]' || true)"
if [ $rc -eq 0 ] && [ "$fail_count" -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc, fail_count=$fail_count)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (rc=$rc, fail_count=$fail_count)"
    printf '%s\n' "$output" | grep '\[FAIL\]' >&2
fi

# ─────────────────────────────────────────
# T2: valid packet PASS (worker_dialog_rounds=0) → 0 FAIL
# ─────────────────────────────────────────
log "T2: valid packet (PASS, rounds=0) → 0 FAIL"
rc=0
output="$(bash "$CHECK_SCRIPT" \
    --contract "$REPO_ROOT/docs/inter-plugin-contracts/review-verdict-v4.md" \
    --packet "$FIXTURE_BASE/valid-packet-pass.yaml" \
    --quiet 2>&1)" || rc=$?
fail_count="$(printf '%s' "$output" | grep -c '\[FAIL\]' || true)"
if [ $rc -eq 0 ] && [ "$fail_count" -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc, fail_count=$fail_count)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (rc=$rc, fail_count=$fail_count)"
    printf '%s\n' "$output" | grep '\[FAIL\]' >&2
fi

# ─────────────────────────────────────────
# T3: valid packet adversarial (worker_dialog_rounds=3) → 0 FAIL
# ─────────────────────────────────────────
log "T3: valid packet adversarial (rounds=3) → 0 FAIL"
rc=0
output="$(bash "$CHECK_SCRIPT" \
    --contract "$REPO_ROOT/docs/inter-plugin-contracts/review-verdict-v4.md" \
    --packet "$FIXTURE_BASE/valid-packet-adversarial.yaml" \
    --quiet 2>&1)" || rc=$?
fail_count="$(printf '%s' "$output" | grep -c '\[FAIL\]' || true)"
if [ $rc -eq 0 ] && [ "$fail_count" -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc, fail_count=$fail_count)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (rc=$rc, fail_count=$fail_count)"
    printf '%s\n' "$output" | grep '\[FAIL\]' >&2
fi

# ─────────────────────────────────────────
# T4: invalid packet (v3 deprecated field) → FAIL advisory (exit 0)
# ─────────────────────────────────────────
log "T4: invalid packet (v3 deprecated decision_state) → FAIL advisory (exit 0)"
rc=0
output="$(bash "$CHECK_SCRIPT" \
    --contract "$REPO_ROOT/docs/inter-plugin-contracts/review-verdict-v4.md" \
    --packet "$FIXTURE_BASE/invalid-packet-v3-deprecated-field.yaml" \
    --quiet 2>&1)" || rc=$?
fail_count="$(printf '%s' "$output" | grep -c '\[FAIL\]' || true)"
if [ $rc -eq 0 ] && [ "$fail_count" -gt 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc advisory, fail_count=$fail_count)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=0+fail_count>0, got rc=$rc fail_count=$fail_count)"
fi

# ─────────────────────────────────────────
# T5: invalid packet (worker_dialog_rounds missing) → FAIL advisory (exit 0)
# ─────────────────────────────────────────
log "T5: invalid packet (worker_dialog_rounds missing) → FAIL advisory (exit 0)"
rc=0
output="$(bash "$CHECK_SCRIPT" \
    --contract "$REPO_ROOT/docs/inter-plugin-contracts/review-verdict-v4.md" \
    --packet "$FIXTURE_BASE/invalid-packet-missing-worker-dialog-rounds.yaml" \
    --quiet 2>&1)" || rc=$?
fail_count="$(printf '%s' "$output" | grep -c '\[FAIL\]' || true)"
if [ $rc -eq 0 ] && [ "$fail_count" -gt 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc advisory, fail_count=$fail_count)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=0+fail_count>0, got rc=$rc fail_count=$fail_count)"
fi

# ─────────────────────────────────────────
# T6: invalid packet + --strict → exit 1
# ─────────────────────────────────────────
log "T6: invalid packet + --strict → exit 1"
rc=0
bash "$CHECK_SCRIPT" \
    --contract "$REPO_ROOT/docs/inter-plugin-contracts/review-verdict-v4.md" \
    --packet "$FIXTURE_BASE/invalid-packet-missing-worker-dialog-rounds.yaml" \
    --strict --quiet 2>/dev/null || rc=$?
if [ $rc -eq 1 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc strict)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=1, got rc=$rc)"
fi

# ─────────────────────────────────────────
# T7: --help → exit 0
# ─────────────────────────────────────────
log "T7: --help → exit 0"
rc=0
bash "$CHECK_SCRIPT" --help >/dev/null 2>&1 || rc=$?
if [ $rc -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (rc=$rc)"
fi

# ─────────────────────────────────────────
# T8: unknown arg → exit 2
# ─────────────────────────────────────────
log "T8: unknown arg → exit 2"
rc=0
bash "$CHECK_SCRIPT" --unknown-flag >/dev/null 2>&1 || rc=$?
if [ $rc -eq 2 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=2, got rc=$rc)"
fi

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
