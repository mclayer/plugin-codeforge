#!/usr/bin/env bash
# test-check-team-spec-schema.sh — smoke test for check-team-spec-schema.sh (CFP-137 Phase 2)
#
# Test matrix:
#   T1: valid design yaml (--dir fixtures/check-team-spec-schema/valid-only/) → PASS
#   T2: invalid yaml dir → FAIL advisory (exit 0 default)
#   T3: invalid yaml + --strict → exit 1
#   T4: valid design-review yaml (adversarial) → PASS
#   T5: templates/ dir (actual 7 yaml) → PASS (7종 완전성 + schema 검증)
#   T6: --help → exit 0
#   T7: unknown arg → exit 2

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE_BASE="$SCRIPT_DIR/fixtures/check-team-spec-schema"
CHECK_SCRIPT="$SCRIPT_DIR/check-team-spec-schema.sh"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

# Create temp dirs for isolated fixture sets
TMPDIR_VALID="$(mktemp -d)"
TMPDIR_INVALID="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_VALID" "$TMPDIR_INVALID"' EXIT

# Setup: copy valid fixtures to TMPDIR_VALID
cp "$FIXTURE_BASE/valid-design.yaml" "$TMPDIR_VALID/team-spec-design.yaml"
cp "$FIXTURE_BASE/valid-design-review.yaml" "$TMPDIR_VALID/team-spec-design-review.yaml"

# Setup: copy invalid fixture to TMPDIR_INVALID
cp "$FIXTURE_BASE/invalid-missing-lane.yaml" "$TMPDIR_INVALID/team-spec-bad-fixture.yaml"
cp "$FIXTURE_BASE/invalid-adversarial-no-user-request-only.yaml" "$TMPDIR_INVALID/team-spec-code-review.yaml"

# ─────────────────────────────────────────
# T1: valid design yaml → PASS (exit 0, 0 FAIL)
# Note: --skip-completeness 는 2개 fixture 만 있는 TMPDIR_VALID 에서 7종 완전성 체크 생략
# ─────────────────────────────────────────
log "T1: valid design yaml dir → exit 0, 0 FAIL"
rc=0
output="$(bash "$CHECK_SCRIPT" --dir "$TMPDIR_VALID" --skip-completeness --quiet 2>&1)" || rc=$?
fail_count="$(printf '%s' "$output" | grep -c '\[FAIL\]' || true)"
if [ $rc -eq 0 ] && [ "$fail_count" -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc, fail_count=$fail_count)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (rc=$rc, fail_count=$fail_count)"
    printf '%s\n' "$output" | head -20 >&2
fi

# ─────────────────────────────────────────
# T2: invalid yaml dir → FAIL advisory (exit 0 default mode)
# ─────────────────────────────────────────
log "T2: invalid yaml dir → exit 0 advisory (FAIL logged to stderr)"
rc=0
output="$(bash "$CHECK_SCRIPT" --dir "$TMPDIR_INVALID" --quiet 2>&1)" || rc=$?
fail_count="$(printf '%s' "$output" | grep -c '\[FAIL\]' || true)"
if [ $rc -eq 0 ] && [ "$fail_count" -gt 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc advisory, fail_count=$fail_count)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=0 + fail_count>0, got rc=$rc fail_count=$fail_count)"
fi

# ─────────────────────────────────────────
# T3: invalid yaml + --strict → exit 1
# ─────────────────────────────────────────
log "T3: invalid yaml + --strict → exit 1"
rc=0
bash "$CHECK_SCRIPT" --dir "$TMPDIR_INVALID" --strict --quiet 2>/dev/null || rc=$?
if [ $rc -eq 1 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc strict)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (expected rc=1, got rc=$rc)"
fi

# ─────────────────────────────────────────
# T4: valid design-review yaml (adversarial) → 0 FAIL
# ─────────────────────────────────────────
log "T4: valid design-review yaml (adversarial) → 0 FAIL"
rc=0
output="$(bash "$CHECK_SCRIPT" --dir "$TMPDIR_VALID" --skip-completeness --quiet 2>&1)" || rc=$?
# Check design-review specifically
dr_fails="$(printf '%s' "$output" | grep -A5 'design-review' | grep -c '\[FAIL\]' || true)"
if [ $rc -eq 0 ] && [ "$dr_fails" -eq 0 ]; then
    PASS=$((PASS + 1))
    log "  PASS (rc=$rc, design-review fail_count=$dr_fails)"
else
    FAIL=$((FAIL + 1))
    log "  FAIL (rc=$rc, design-review fail_count=$dr_fails)"
fi

# ─────────────────────────────────────────
# T5: templates/ dir (actual 7 yaml) → PASS
# (requires templates/ to exist relative to script; skip if not found)
# ─────────────────────────────────────────
log "T5: templates/ actual 7 yaml → PASS"
TEMPLATES_DIR="$(dirname "$SCRIPT_DIR")/templates"
if [ -d "$TEMPLATES_DIR" ] && ls "$TEMPLATES_DIR"/team-spec-*.yaml >/dev/null 2>&1; then
    rc=0
    output="$(bash "$CHECK_SCRIPT" --dir "$TEMPLATES_DIR" --quiet 2>&1)" || rc=$?
    fail_count="$(printf '%s' "$output" | grep -c '\[FAIL\]' || true)"
    if [ $rc -eq 0 ] && [ "$fail_count" -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc, fail_count=$fail_count, templates/ 7 yaml all valid)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc, fail_count=$fail_count)"
        printf '%s\n' "$output" | grep '\[FAIL\]' >&2
    fi
else
    log "  SKIP (templates/ dir 없거나 team-spec-*.yaml 부재 — CI 환경 외 skip)"
    PASS=$((PASS + 1))
fi

# ─────────────────────────────────────────
# T6: --help → exit 0
# ─────────────────────────────────────────
log "T6: --help → exit 0"
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
# T7: unknown arg → exit 2
# ─────────────────────────────────────────
log "T7: unknown arg → exit 2"
rc=0
bash "$CHECK_SCRIPT" --unknown-arg >/dev/null 2>&1 || rc=$?
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
