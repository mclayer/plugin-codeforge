#!/usr/bin/env bash
# check-team-spec-schema.sh — team-spec yaml 7종 schema 정합 검증 (CFP-137 Phase 2 / ADR-044)
#
# `templates/team-spec-<lane>.yaml` 7종 의 필수 필드 존재 + 값 정합 검증.
#
# 필수 필드 (각 yaml 최상위):
#   - lane        : string (7종: decompose / requirements / design / design-review /
#                           develop / code-review / security-test)
#   - teammates   : list (1개 이상)
#   - dispatch_pattern : string
#   - env_divergent_fallback : map (env_0_behavior key 포함)
#
# 각 teammate entry 필수 필드:
#   - name
#   - role
#   - system_prompt_path
#   - model
#   - spawn_mode
#
# Adversarial lane (design-review / code-review / security-test):
#   - teammate 중 dispatch_mode: user_request_only 가 1개 이상 존재 (Codex worker)
#   - measurable_verification 키 존재 + adversarial 서브키 존재
#
# Parallelization lane (design):
#   - dispatch_pattern: parallel
#   - measurable_verification 키 존재 + parallelization 서브키 존재
#
# Usage:
#   bash scripts/check-team-spec-schema.sh [--dir <dir>] [--strict] [--quiet]
#
# Defaults:
#   --dir: templates/ (team-spec-*.yaml 자동 탐색)
#
# Exit code:
#   Default mode: 0 (advisory — stderr FAIL 출력 후 exit 0)
#   Strict mode (--strict): exit 1 if any FAIL

set -uo pipefail

QUIET=0
STRICT=0
SPEC_DIR="templates"
SKIP_COMPLETENESS=0

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT=1; shift ;;
        --dir) SPEC_DIR="$2"; shift 2 ;;
        --skip-completeness) SKIP_COMPLETENESS=1; shift ;;
        -h|--help)
            sed -n '/^# check-team-spec-schema/,/^# Exit code/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

log() { [ $QUIET -eq 0 ] && printf '%s\n' "$1"; }
log_err() { printf '%s\n' "$1" >&2; }

# Expected 7 lane values
EXPECTED_LANES="decompose requirements design design-review develop code-review security-test"

# Adversarial lanes (require dispatch_mode: user_request_only + measurable_verification.adversarial)
ADVERSARIAL_LANES="design-review code-review security-test"

# Parallel lane (require dispatch_pattern: parallel + measurable_verification.parallelization)
PARALLEL_LANE="design"

total_fail=0
files_checked=0

check_yaml_file() {
    local file="$1"
    local fail=0
    local base
    base="$(basename "$file")"

    log ""
    log "--- $base ---"

    # Read file content
    if [ ! -f "$file" ]; then
        log_err "[FAIL] $base: file 부재"
        total_fail=$((total_fail + 1))
        return
    fi

    local content
    content="$(cat "$file")"

    # Check: lane field
    local lane_val
    lane_val="$(printf '%s' "$content" | grep -E '^lane:' | head -1 | sed -E 's/^lane:\s*([^\s#]+).*/\1/' | tr -d "'\"")"
    if [ -z "$lane_val" ]; then
        log_err "[FAIL] $base: 'lane:' 필드 부재"
        fail=$((fail + 1))
    else
        log "[OK] lane: $lane_val"
    fi

    # Check: teammates list (at least 1 entry)
    local teammate_count
    teammate_count="$(printf '%s' "$content" | grep -cE '^\s*- name:' || true)"
    if [ "$teammate_count" -lt 1 ]; then
        log_err "[FAIL] $base: teammates 목록 비어있음 (name: 항목 0개)"
        fail=$((fail + 1))
    else
        log "[OK] teammates: $teammate_count 개"
    fi

    # Check: dispatch_pattern field
    if ! printf '%s' "$content" | grep -qE '^dispatch_pattern:'; then
        log_err "[FAIL] $base: 'dispatch_pattern:' 필드 부재"
        fail=$((fail + 1))
    else
        local dp_val
        dp_val="$(printf '%s' "$content" | grep -E '^dispatch_pattern:' | head -1 | sed -E 's/^dispatch_pattern:\s*([^\s#]+).*/\1/' | tr -d "'\"")"
        log "[OK] dispatch_pattern: $dp_val"
    fi

    # Check: env_divergent_fallback field + env_0_behavior subkey
    if ! printf '%s' "$content" | grep -qE '^env_divergent_fallback:'; then
        log_err "[FAIL] $base: 'env_divergent_fallback:' 필드 부재"
        fail=$((fail + 1))
    elif ! printf '%s' "$content" | grep -qE 'env_0_behavior:'; then
        log_err "[FAIL] $base: 'env_divergent_fallback.env_0_behavior' 서브키 부재"
        fail=$((fail + 1))
    else
        log "[OK] env_divergent_fallback.env_0_behavior 존재"
    fi

    # Check: each teammate entry has required fields (name / role / system_prompt_path / model / spawn_mode)
    # Strategy: extract only the teammates: list block (between 'teammates:' and next top-level key)
    # then count '- name:' entries and check that required sibling fields appear the same number of times
    local teammates_block
    teammates_block="$(printf '%s' "$content" | awk '
        /^teammates:/ { in_tm=1; next }
        in_tm && /^[a-z]/ { in_tm=0 }
        in_tm { print }
    ')"

    local name_count
    name_count="$(printf '%s' "$teammates_block" | grep -cE '^\s+- name:' || true)"

    if [ "$name_count" -gt 0 ]; then
        for field in role system_prompt_path model spawn_mode; do
            local field_count
            field_count="$(printf '%s' "$teammates_block" | grep -cE "^\s+${field}:" || true)"
            if [ "$field_count" -lt "$name_count" ]; then
                log_err "[FAIL] $base: teammates[] 에 '${field}:' 필드 부재 항목 있음 (name=$name_count, ${field}=$field_count)"
                fail=$((fail + 1))
            else
                log "[OK] teammates[] ${field}: $field_count/$name_count 항목 보유"
            fi
        done
    fi

    # Adversarial lane checks
    local is_adversarial=0
    for al in $ADVERSARIAL_LANES; do
        [ "$lane_val" = "$al" ] && is_adversarial=1 && break
    done
    if [ $is_adversarial -eq 1 ]; then
        # dispatch_mode: user_request_only in at least 1 teammate
        if ! printf '%s' "$content" | grep -qE 'dispatch_mode:\s*user_request_only'; then
            log_err "[FAIL] $base (adversarial lane): dispatch_mode: user_request_only 인 teammate 없음 (Codex worker 정책 — ADR-044 §결정 2)"
            fail=$((fail + 1))
        else
            log "[OK] dispatch_mode: user_request_only teammate 존재"
        fi
        # measurable_verification.adversarial
        if ! printf '%s' "$content" | grep -qE 'adversarial:'; then
            log_err "[FAIL] $base (adversarial lane): measurable_verification.adversarial 서브키 부재 (ADR-044 §결정 5)"
            fail=$((fail + 1))
        else
            log "[OK] measurable_verification.adversarial 존재"
        fi
    fi

    # Parallelization lane check
    if [ "$lane_val" = "$PARALLEL_LANE" ]; then
        local dp_val2
        dp_val2="$(printf '%s' "$content" | grep -E '^dispatch_pattern:' | head -1 | sed -E 's/^dispatch_pattern:\s*([^\s#]+).*/\1/' | tr -d "'\"")"
        if [ "$dp_val2" != "parallel" ]; then
            log_err "[FAIL] $base (design lane): dispatch_pattern != parallel (got: '$dp_val2')"
            fail=$((fail + 1))
        else
            log "[OK] dispatch_pattern: parallel (design lane 정합)"
        fi
        if ! printf '%s' "$content" | grep -qE 'parallelization:'; then
            log_err "[FAIL] $base (design lane): measurable_verification.parallelization 서브키 부재 (ADR-044 §결정 5)"
            fail=$((fail + 1))
        else
            log "[OK] measurable_verification.parallelization 존재"
        fi
    fi

    if [ $fail -eq 0 ]; then
        log "[PASS] $base — 모든 schema 검증 통과"
    else
        log_err "[FAIL] $base — $fail 개 항목 실패"
        total_fail=$((total_fail + fail))
    fi
    files_checked=$((files_checked + 1))
}

# Discover and check all team-spec-*.yaml files
found=0
for f in "$SPEC_DIR"/team-spec-*.yaml; do
    [ -f "$f" ] || continue
    check_yaml_file "$f"
    found=$((found + 1))
done

if [ $found -eq 0 ]; then
    log_err "[FAIL] $SPEC_DIR 에서 team-spec-*.yaml 파일을 찾을 수 없음"
    total_fail=$((total_fail + 1))
fi

# Check 7종 모두 존재하는지 (lane value 기준) — --skip-completeness 시 생략
if [ $found -gt 0 ] && [ $SKIP_COMPLETENESS -eq 0 ]; then
    log ""
    log "--- 7종 완전성 검사 ---"
    for expected_lane in $EXPECTED_LANES; do
        local_found=0
        for f in "$SPEC_DIR"/team-spec-*.yaml; do
            [ -f "$f" ] || continue
            if grep -qE "^lane:\s*${expected_lane}(\s|$|#)" "$f"; then
                local_found=1
                break
            fi
        done
        if [ $local_found -eq 1 ]; then
            log "[OK] lane=$expected_lane 파일 존재"
        else
            log_err "[FAIL] lane=$expected_lane 에 해당하는 team-spec yaml 파일 부재"
            total_fail=$((total_fail + 1))
        fi
    done
fi

log ""
log "=== Summary: $found 파일 검사, $total_fail FAIL ==="

if [ $STRICT -eq 1 ] && [ $total_fail -gt 0 ]; then
    exit 1
fi
exit 0
