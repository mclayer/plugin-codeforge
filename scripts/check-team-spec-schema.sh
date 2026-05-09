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

    if [ ! -f "$file" ]; then
        log_err "[FAIL] $base: file 부재"
        total_fail=$((total_fail + 1))
        return
    fi

    # Single-pass awk: extract all needed values from the file in one subprocess call.
    # (Issue #304 optimization: replaces ~10 separate grep/sed subshell calls per file with 1 awk pass)
    # Output format (tab-separated, one value per line):
    #   lane=<value>
    #   dispatch_pattern=<value>
    #   has_env_divergent_fallback=1|0
    #   has_env_0_behavior=1|0
    #   name_count=<N>
    #   role_count=<N>
    #   spp_count=<N>
    #   model_count=<N>
    #   sm_count=<N>
    #   has_dispatch_mode_user_request_only=1|0
    #   has_adversarial=1|0
    #   has_parallelization=1|0
    local parsed
    parsed="$(awk '
        # Track teammates block scope (between "teammates:" and next top-level key)
        /^teammates:[[:space:]]*$/ || /^teammates:/ { in_tm=1; next }
        in_tm && /^[a-zA-Z]/ { in_tm=0 }

        # Top-level fields
        /^lane:[[:space:]]/ {
            v=$0; sub(/^lane:[[:space:]]*/,"",v); sub(/[[:space:]#].*/,"",v); gsub(/['"'"'"]/,"",v)
            lane=v
        }
        /^dispatch_pattern:[[:space:]]/ {
            v=$0; sub(/^dispatch_pattern:[[:space:]]*/,"",v); sub(/[[:space:]#].*/,"",v); gsub(/['"'"'"]/,"",v)
            dp=v
        }
        /^env_divergent_fallback:/ { has_edf=1 }
        /env_0_behavior:/          { has_e0b=1 }

        # Teammates block: count entries and required fields
        in_tm && /^[[:space:]]+-[[:space:]]+name:[[:space:]]/ { name_cnt++ }
        in_tm && /^[[:space:]]+role:[[:space:]]/ { role_cnt++ }
        in_tm && /^[[:space:]]+system_prompt_path:[[:space:]]/ { spp_cnt++ }
        in_tm && /^[[:space:]]+model:[[:space:]]/ { model_cnt++ }
        in_tm && /^[[:space:]]+spawn_mode:[[:space:]]/ { sm_cnt++ }

        # Adversarial / parallelization markers (anywhere in file)
        /dispatch_mode:[[:space:]]*user_request_only/ { has_uro=1 }
        /adversarial:/                                 { has_adv=1 }
        /parallelization:/                             { has_par=1 }

        END {
            print "lane=" lane
            print "dispatch_pattern=" dp
            print "has_env_divergent_fallback=" (has_edf+0)
            print "has_env_0_behavior=" (has_e0b+0)
            print "name_count=" (name_cnt+0)
            print "role_count=" (role_cnt+0)
            print "spp_count=" (spp_cnt+0)
            print "model_count=" (model_cnt+0)
            print "sm_count=" (sm_cnt+0)
            print "has_dispatch_mode_uro=" (has_uro+0)
            print "has_adversarial=" (has_adv+0)
            print "has_parallelization=" (has_par+0)
        }
    ' "$file")"

    # Parse awk output into local variables
    local lane_val="" dp_val="" has_edf=0 has_e0b=0
    local name_count=0 role_count=0 spp_count=0 model_count=0 sm_count=0
    local has_uro=0 has_adv=0 has_par=0
    while IFS='=' read -r key val; do
        case "$key" in
            lane)                       lane_val="$val" ;;
            dispatch_pattern)           dp_val="$val" ;;
            has_env_divergent_fallback) has_edf="$val" ;;
            has_env_0_behavior)         has_e0b="$val" ;;
            name_count)                 name_count="$val" ;;
            role_count)                 role_count="$val" ;;
            spp_count)                  spp_count="$val" ;;
            model_count)                model_count="$val" ;;
            sm_count)                   sm_count="$val" ;;
            has_dispatch_mode_uro)      has_uro="$val" ;;
            has_adversarial)            has_adv="$val" ;;
            has_parallelization)        has_par="$val" ;;
        esac
    done <<< "$parsed"

    # Check: lane field
    if [ -z "$lane_val" ]; then
        log_err "[FAIL] $base: 'lane:' 필드 부재"
        fail=$((fail + 1))
    else
        log "[OK] lane: $lane_val"
    fi

    # Check: teammates list (at least 1 entry)
    if [ "$name_count" -lt 1 ]; then
        log_err "[FAIL] $base: teammates 목록 비어있음 (name: 항목 0개)"
        fail=$((fail + 1))
    else
        log "[OK] teammates: $name_count 개"
    fi

    # Check: dispatch_pattern field
    if [ -z "$dp_val" ]; then
        log_err "[FAIL] $base: 'dispatch_pattern:' 필드 부재"
        fail=$((fail + 1))
    else
        log "[OK] dispatch_pattern: $dp_val"
    fi

    # Check: env_divergent_fallback field + env_0_behavior subkey
    if [ "$has_edf" -eq 0 ]; then
        log_err "[FAIL] $base: 'env_divergent_fallback:' 필드 부재"
        fail=$((fail + 1))
    elif [ "$has_e0b" -eq 0 ]; then
        log_err "[FAIL] $base: 'env_divergent_fallback.env_0_behavior' 서브키 부재"
        fail=$((fail + 1))
    else
        log "[OK] env_divergent_fallback.env_0_behavior 존재"
    fi

    # Check: each teammate entry has required fields (role / system_prompt_path / model / spawn_mode)
    if [ "$name_count" -gt 0 ]; then
        local counts_arr=("$role_count" "$spp_count" "$model_count" "$sm_count")
        local fields_arr=(role system_prompt_path model spawn_mode)
        local i
        for i in 0 1 2 3; do
            local fc="${counts_arr[$i]}"
            local fn="${fields_arr[$i]}"
            if [ "$fc" -lt "$name_count" ]; then
                log_err "[FAIL] $base: teammates[] 에 '${fn}:' 필드 부재 항목 있음 (name=$name_count, ${fn}=$fc)"
                fail=$((fail + 1))
            else
                log "[OK] teammates[] ${fn}: $fc/$name_count 항목 보유"
            fi
        done
    fi

    # Adversarial lane checks
    local is_adversarial=0
    for al in $ADVERSARIAL_LANES; do
        [ "$lane_val" = "$al" ] && is_adversarial=1 && break
    done
    if [ $is_adversarial -eq 1 ]; then
        if [ "$has_uro" -eq 0 ]; then
            log_err "[FAIL] $base (adversarial lane): dispatch_mode: user_request_only 인 teammate 없음 (Codex worker 정책 — ADR-044 §결정 2)"
            fail=$((fail + 1))
        else
            log "[OK] dispatch_mode: user_request_only teammate 존재"
        fi
        if [ "$has_adv" -eq 0 ]; then
            log_err "[FAIL] $base (adversarial lane): measurable_verification.adversarial 서브키 부재 (ADR-044 §결정 5)"
            fail=$((fail + 1))
        else
            log "[OK] measurable_verification.adversarial 존재"
        fi
    fi

    # Parallelization lane check
    if [ "$lane_val" = "$PARALLEL_LANE" ]; then
        if [ "$dp_val" != "parallel" ]; then
            log_err "[FAIL] $base (design lane): dispatch_pattern != parallel (got: '$dp_val')"
            fail=$((fail + 1))
        else
            log "[OK] dispatch_pattern: parallel (design lane 정합)"
        fi
        if [ "$has_par" -eq 0 ]; then
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
# Optimization (Issue #304): single-pass — build seen-lanes set from all yamls once (O(N)),
# then check each expected lane against the set (O(7)) → total O(N+7) vs old O(49).
if [ $found -gt 0 ] && [ $SKIP_COMPLETENESS -eq 0 ]; then
    log ""
    log "--- 7종 완전성 검사 ---"
    # Build newline-separated list of lane values found across all yaml files (1 grep per file, not per lane)
    seen_lanes=""
    for f in "$SPEC_DIR"/team-spec-*.yaml; do
        [ -f "$f" ] || continue
        lv="$(grep -E '^lane:[[:space:]]*' "$f" | head -1 | sed -E 's/^lane:[[:space:]]*([^[:space:]#]+).*/\1/' | tr -d "'\"")"
        [ -n "$lv" ] && seen_lanes="${seen_lanes}${lv}"$'\n'
    done
    for expected_lane in $EXPECTED_LANES; do
        if printf '%s' "$seen_lanes" | grep -qxF "$expected_lane"; then
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
