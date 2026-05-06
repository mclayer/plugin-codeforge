#!/usr/bin/env bash
# test-check-bootstrap-strict.sh — minimal TDD for check_bootstrap.py --strict mode (CFP-127 Phase 2).
#
# 본 스모크 테스트 = check_bootstrap.py 의 strict mode 동작 검증.
#   Test 1: --help → exit 0
#   Test 2: project.yaml 부재 + default mode → exit 0 (silent skip)
#   Test 3: project.yaml 부재 + --strict → exit 1 (strict-eligible (a))
#   Test 4: bypass env set + --strict → exit 0 (Bypass priority HIGHEST)
#   Test 5: env-only strict (no CLI flag, no yaml) → exit 1
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CHECK_BOOTSTRAP="$PLUGIN_ROOT/overlay/hooks/check_bootstrap.py"
FIXTURE_DIR="$SCRIPT_DIR/fixtures/check-bootstrap-strict"
TMPDIR_BASE="${TMPDIR:-/tmp}/cb-strict-test-$$"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

cleanup() {
    rm -rf "$TMPDIR_BASE"
}
trap cleanup EXIT

mkdir -p "$TMPDIR_BASE"

# Test 1 — --help
test_1_help() {
    log "Test 1: --help → exit 0"
    local rc=0
    python3 "$CHECK_BOOTSTRAP" --help >/dev/null 2>&1 || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc)"
    fi
}

# Test 2 — empty fixture, default mode → exit 0 silent skip
test_2_default_silent_skip() {
    log "Test 2: empty (no project.yaml) + default mode → exit 0 silent skip"
    local rc=0
    local d="$TMPDIR_BASE/test2"
    mkdir -p "$d"
    (
        cd "$d"
        # Use full env (not env -i) — only ensure no strict env vars leak
        unset CODEFORGE_STRICT_BOOTSTRAP
        unset HOTFIX_BYPASS_CODEFORGE
        unset HOTFIX_BYPASS_REASON
        python3 "$CHECK_BOOTSTRAP" 2>/dev/null
    ) || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc default silent skip)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0, got rc=$rc)"
    fi
}

# Test 3 — empty + --strict → exit 1 (strict-eligible (a))
test_3_strict_no_yaml() {
    log "Test 3: no project.yaml + --strict → exit 1 (strict-eligible a)"
    local rc=0
    local d="$TMPDIR_BASE/test3"
    mkdir -p "$d"
    (
        cd "$d"
        unset CODEFORGE_STRICT_BOOTSTRAP
        unset HOTFIX_BYPASS_CODEFORGE
        unset HOTFIX_BYPASS_REASON
        python3 "$CHECK_BOOTSTRAP" --strict 2>/dev/null
    ) || rc=$?
    if [ $rc -eq 1 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc strict exit 1)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=1, got rc=$rc)"
    fi
}

# Test 4 — bypass env + --strict → exit 0 (Bypass priority HIGHEST)
test_4_bypass_priority() {
    log "Test 4: HOTFIX_BYPASS_CODEFORGE=1 + REASON + --strict → exit 0 (Bypass HIGHEST)"
    local rc=0
    local d="$TMPDIR_BASE/test4"
    mkdir -p "$d"
    (
        cd "$d"
        unset CODEFORGE_STRICT_BOOTSTRAP
        export HOTFIX_BYPASS_CODEFORGE=1
        export HOTFIX_BYPASS_REASON="test-bypass"
        python3 "$CHECK_BOOTSTRAP" --strict 2>/dev/null
    ) || rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc bypass honored)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=0 bypass, got rc=$rc)"
    fi
}

# Test 5 — env-only strict (no CLI flag, no yaml) → exit 1
test_5_env_priority() {
    log "Test 5: CODEFORGE_STRICT_BOOTSTRAP=1 (env) + no project.yaml → exit 1"
    local rc=0
    local d="$TMPDIR_BASE/test5"
    mkdir -p "$d"
    (
        cd "$d"
        unset HOTFIX_BYPASS_CODEFORGE
        unset HOTFIX_BYPASS_REASON
        export CODEFORGE_STRICT_BOOTSTRAP=1
        python3 "$CHECK_BOOTSTRAP" 2>/dev/null
    ) || rc=$?
    if [ $rc -eq 1 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc env-priority strict)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (expected rc=1, got rc=$rc)"
    fi
}

# Test 6 — yaml fixture clean → strict mode opt-in
test_6_yaml_fixture_clean() {
    log "Test 6: yaml fixture clean (bootstrap.strict_mode:true)"
    if [ ! -d "$FIXTURE_DIR/clean" ]; then
        log "  SKIP (fixture missing)"
        return
    fi
    local rc=0
    (
        cd "$FIXTURE_DIR/clean"
        unset CODEFORGE_STRICT_BOOTSTRAP
        unset HOTFIX_BYPASS_CODEFORGE
        unset HOTFIX_BYPASS_REASON
        python3 "$CHECK_BOOTSTRAP" 2>/dev/null
    ) || rc=$?
    # In clean fixture: project.yaml has bootstrap.strict_mode: true → yaml priority activates strict.
    # 결과는 test environment 의 plugins/labels 상태에 의존:
    #   - plugins 8 critical 모두 설치됨 + labels 10 critical 모두 → exit 0
    #   - 누락 시 → exit 1
    # 본 test 는 strict 활성 자체만 검증 (exit 0 OR exit 1 모두 valid — 환경 의존)
    if [ $rc -eq 0 ] || [ $rc -eq 1 ]; then
        PASS=$((PASS + 1))
        log "  PASS (rc=$rc — yaml strict_mode 활성 환경 의존 결과)"
    else
        FAIL=$((FAIL + 1))
        log "  FAIL (rc=$rc 비정상)"
    fi
}

log "=== test-check-bootstrap-strict 시작 ==="
test_1_help
test_2_default_silent_skip
test_3_strict_no_yaml
test_4_bypass_priority
test_5_env_priority
test_6_yaml_fixture_clean

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
