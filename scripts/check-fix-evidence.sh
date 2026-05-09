#!/usr/bin/env bash
# check-fix-evidence.sh — FIX Ledger ↔ Lane Evidence cross-validation (CFP-298).
#
# Story §10 FIX Ledger 의 FIX iteration 건수 ↔ §14 Lane Evidence 의 fix-iter lane row 건수
# cross-validation. Escalation 패턴 (FIX iteration → TEAM-FIX spawn) 의 measurable verification.
# ADR-044 §결정 5 Escalation pattern — CFP-298 신설.
#
# Validation 규칙:
#   §10 에 N 개의 FIX iteration 이 존재하면, §14 에 최소 N 개의 fix_iteration 지정 row 가 있어야 함.
#   §10 FIX iteration = 0 이면 §14 fix-iter row 0 이어도 PASS.
#   §14 fix-iter row 가 §10 FIX count 보다 많아도 PASS (추가 lane sweep 허용).
#
# Usage:
#   bash scripts/check-fix-evidence.sh <story-file-path> [--strict] [--quiet]
#   bash scripts/check-fix-evidence.sh --story <story-file-path> [--strict] [--quiet]
#
# Exit code:
#   Default mode: 0 (PASS) / 0 (FAIL — stderr advisory 만, LLM-trust 정합 ADR-027 §결정 2)
#   Strict mode (--strict): 0 (PASS) / 1 (FAIL)

set -uo pipefail

QUIET=0
STRICT=0
STORY_PATH=""

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT=1; shift ;;
        --story) STORY_PATH="$2"; shift 2 ;;
        -h|--help)
            sed -n '/^# check-fix-evidence/,/^# Exit code/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        -*)
            echo "Unknown arg: $1" >&2; exit 2 ;;
        *)
            # positional arg → story path
            if [ -z "$STORY_PATH" ]; then
                STORY_PATH="$1"
                shift
            else
                echo "Unexpected positional arg: $1" >&2; exit 2
            fi
            ;;
    esac
done

log()     { [ $QUIET -eq 0 ] && printf '%s\n' "$1"; }
log_err() { printf '%s\n' "$1" >&2; }

# Parse Story §10 FIX Ledger table and count FIX iterations
# Returns the max iter number found (= number of distinct FIX iterations)
parse_section_10_fix_count() {
    local story="$1"
    # Find §10 section, scan table rows (lines starting with | that have a number in the Iter column)
    # §10 FIX Ledger table format: | Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
    # Iter column = first column after leading |. Skip header row (contains 'Iter') and separator rows (---).
    awk '
        /^## §10|^### §10|^#### §10/ { in10=1; next }
        in10 && /^## §|^### §[0-9]/ { in10=0; next }
        in10 && /^\|[[:space:]]*[0-9]+[[:space:]]*\|/ {
            # Extract iter number from first column
            line=$0
            sub(/^\|[[:space:]]*/, "", line)
            sub(/[[:space:]]*\|.*/, "", line)
            if (line+0 > max) max = line+0
        }
        END { print max+0 }
    ' "$story"
}

# Parse Story §14 Lane Evidence YAML block and count rows with non-null fix_iteration
# A fix-iter lane row = any row in §14 where fix_iteration is not null / not empty
parse_section_14_fix_iter_count() {
    local story="$1"
    # Extract §14 YAML block first
    local yaml
    yaml="$(awk '
        /^## §14|^### §14|^#### §14/ { in14=1; next }
        in14 && /^## §|^### §[0-9]/ { in14=0 }
        in14 && /^```yaml/ { yaml=1; next }
        in14 && /^```/ && yaml { yaml=0; next }
        in14 && yaml { print }
    ' "$story")"

    if [ -z "$yaml" ]; then
        echo "0"
        return
    fi

    # Count rows where fix_iteration: is a positive integer (not null, not 0, not empty)
    # Row delimiter: "- lane:" starts a new entry
    # We count entries where fix_iteration is a number >= 1
    # Strategy: finalize each row when next "- lane:" is seen, and finalize last row at END
    printf '%s' "$yaml" | awk '
        # Skip YAML comment lines
        /^[[:space:]]*#/ { next }
        /[[:space:]]*- lane:/ {
            # Finalize previous row before starting a new one
            if (in_row && fi_val ~ /^[1-9][0-9]*$/) count++
            in_row=1; fi_val=""
            next
        }
        in_row && /fix_iteration:/ {
            val=$0
            sub(/.*fix_iteration:[[:space:]]*/, "", val)
            sub(/[[:space:]]*$/, "", val)
            fi_val=val
        }
        END {
            # Finalize the last row
            if (in_row && fi_val ~ /^[1-9][0-9]*$/) count++
            print count+0
        }
    '
}

# Main validation
run_check() {
    local fail=0

    # 1. Story file 존재 확인
    if [ -z "$STORY_PATH" ]; then
        log_err "[FAIL] story file path 미지정 — --story <path> 또는 positional arg 로 지정"
        fail=$((fail + 1))
    elif [ ! -f "$STORY_PATH" ]; then
        log_err "[FAIL] Story file 부재: $STORY_PATH"
        fail=$((fail + 1))
    else
        log "[OK] Story file: $STORY_PATH"
    fi

    if [ $fail -gt 0 ]; then
        log ""
        log "=== Summary: $fail FAIL ==="
        [ $STRICT -eq 1 ] && exit 1
        exit 0
    fi

    # 2. §10 FIX Ledger iteration count 파싱
    local fix_count
    fix_count="$(parse_section_10_fix_count "$STORY_PATH")"
    log "[INFO] §10 FIX Ledger iteration count: $fix_count"

    # 3. §14 fix-iter lane row count 파싱
    local fix_iter_count
    fix_iter_count="$(parse_section_14_fix_iter_count "$STORY_PATH")"
    log "[INFO] §14 fix_iteration row count: $fix_iter_count"

    # 4. Cross-validation
    if [ "$fix_count" -eq 0 ]; then
        log "[PASS] §10 FIX iteration = 0 — §14 fix-iter row 없어도 정합 (FIX 미발생)"
    elif [ "$fix_iter_count" -ge "$fix_count" ]; then
        log "[PASS] §14 fix-iter row ($fix_iter_count) >= §10 FIX iteration ($fix_count) — Escalation 패턴 evidence 충족"
    else
        log_err "[FAIL] §14 fix-iter row ($fix_iter_count) < §10 FIX iteration ($fix_count) — Escalation evidence 부족"
        log_err "  → FIX iteration 마다 §14 에 fix_iteration: <N> lane row 추가 필요 (ADR-044 Escalation 패턴)"
        fail=$((fail + 1))
    fi

    log ""
    log "=== Summary: $fail FAIL ==="

    [ $STRICT -eq 1 ] && [ $fail -gt 0 ] && exit 1
    exit 0
}

run_check
