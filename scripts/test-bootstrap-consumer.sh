#!/usr/bin/env bash
# test-bootstrap-consumer.sh — minimal smoke test for bootstrap-consumer.sh + check-debut-readiness.sh (CFP-125 Phase 2).
#
# 본 스모크 테스트 = `--dry-run` 으로 양 스크립트 실 변경 없이 exit code 검증.
# 향후 follow-up CFP 에서 3 fixture (clean / partial / complete) 로 end-to-end TDD 확장.
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

# Test 1 — bootstrap-consumer.sh --dry-run + --org/--repo 명시 + git repo 환경 ↦ exit 0
test_1_bootstrap_dry_run() {
    log "Test 1: bootstrap-consumer.sh --dry-run"
    local rc=0
    bash "$SCRIPT_DIR/bootstrap-consumer.sh" --dry-run --org test-org --repo test-repo >/tmp/bs-test.log 2>&1 || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc)"
        cat /tmp/bs-test.log >&2 || true
    fi
}

# Test 2 — bootstrap-consumer.sh --help ↦ exit 0 + usage in stdout
test_2_bootstrap_help() {
    log "Test 2: bootstrap-consumer.sh --help"
    local out rc=0
    out="$(bash "$SCRIPT_DIR/bootstrap-consumer.sh" --help 2>&1)" || rc=$?
    if [ $rc -eq 0 ] && printf '%s' "$out" | grep -q "bootstrap-consumer.sh"; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc)"
    fi
}

# Test 3 — bootstrap-consumer.sh unknown arg ↦ exit 2
test_3_bootstrap_unknown_arg() {
    log "Test 3: bootstrap-consumer.sh unknown arg"
    local rc=0
    bash "$SCRIPT_DIR/bootstrap-consumer.sh" --unknown-flag >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 2 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=2, got rc=$rc)"
    fi
}

# Test 4 — check-debut-readiness.sh ↦ exit 0 (default advisory mode)
test_4_check_debut_default() {
    log "Test 4: check-debut-readiness.sh (default advisory mode)"
    local rc=0
    bash "$SCRIPT_DIR/check-debut-readiness.sh" --quiet >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0 default advisory, got rc=$rc)"
    fi
}

# Test 5 — check-debut-readiness.sh --strict ↦ exit 0 (현재 release strict 미 land)
test_5_check_debut_strict_pre_cfp_127() {
    log "Test 5: check-debut-readiness.sh --strict (pre-CFP-127 — stderr 경고 + default 동작)"
    local out rc=0
    out="$(bash "$SCRIPT_DIR/check-debut-readiness.sh" --strict --quiet 2>&1)" || rc=$?
    if [ $rc -eq 0 ] && printf '%s' "$out" | grep -q "strict mode 는 CFP-127"; then
        PASS=$((PASS + 1))
        log "  PASS"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc, stderr 경고 누락 가능)"
    fi
}

# Test 6 — bootstrap-consumer.ps1 + check-debut-readiness.ps1 syntax 검증 (Windows native CI 시 활성)
test_6_powershell_syntax() {
    log "Test 6: PowerShell variant syntax (skip if pwsh 부재)"
    if ! command -v pwsh >/dev/null 2>&1; then
        log "  SKIP (pwsh 미설치 — Windows CI 에서 실 검증)"
        return
    fi
    local rc=0
    pwsh -File "$SCRIPT_DIR/bootstrap-consumer.ps1" -DryRun -Org test-org -Repo test-repo >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS bootstrap-consumer.ps1"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL bootstrap-consumer.ps1 (rc=$rc)"
    fi
    rc=0
    pwsh -File "$SCRIPT_DIR/check-debut-readiness.ps1" -Quiet >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS check-debut-readiness.ps1"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL check-debut-readiness.ps1 (rc=$rc)"
    fi
}

# Run
log "=== test-bootstrap-consumer 시작 ==="
test_1_bootstrap_dry_run
test_2_bootstrap_help
test_3_bootstrap_unknown_arg
test_4_check_debut_default
test_5_check_debut_strict_pre_cfp_127
test_6_powershell_syntax

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
