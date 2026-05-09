#!/usr/bin/env bash
# check-review-verdict-v4.sh — review-verdict v4 packet schema 정합 검증 (CFP-137 Phase 2 / ADR-044)
#
# review-verdict v4 inter-plugin contract 의 핵심 field 검증:
#   (A) wrapper sibling file (`docs/inter-plugin-contracts/review-verdict-v4.md`) 필수 섹션 존재 검증
#   (B) v4 packet fixture (yaml) 의 worker_dialog_rounds field 정합 검증 (Adversarial measurable)
#   (C) v3 deprecated fields (decision_state / sonnet_final_status / decider_decision_ref) 부재 검증
#
# Usage:
#   bash scripts/check-review-verdict-v4.sh [--contract <path>] [--packet <path>] [--strict] [--quiet]
#
# Defaults:
#   --contract: docs/inter-plugin-contracts/review-verdict-v4.md
#   --packet:   (없음 — packet check 선택적)
#
# Exit code:
#   Default mode: 0 (advisory)
#   Strict mode (--strict): exit 1 if any FAIL

set -uo pipefail

QUIET=0
STRICT=0
CONTRACT_PATH="docs/inter-plugin-contracts/review-verdict-v4.md"
PACKET_PATH=""

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT=1; shift ;;
        --contract) CONTRACT_PATH="$2"; shift 2 ;;
        --packet) PACKET_PATH="$2"; shift 2 ;;
        -h|--help)
            sed -n '/^# check-review-verdict-v4/,/^# Exit code/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

log() { [ $QUIET -eq 0 ] && printf '%s\n' "$1"; }
log_err() { printf '%s\n' "$1" >&2; }

fail=0

# ─────────────────────────────────────────
# Check A: wrapper sibling contract file 검증
# ─────────────────────────────────────────
log "=== Check A: review-verdict-v4.md contract file ==="

if [ ! -f "$CONTRACT_PATH" ]; then
    log_err "[FAIL] review-verdict-v4.md 부재: $CONTRACT_PATH"
    fail=$((fail + 1))
else
    log "[OK] contract file 존재: $CONTRACT_PATH"

    local_content="$(cat "$CONTRACT_PATH")"

    # A1: frontmatter contract_version: "4.0"
    if printf '%s' "$local_content" | grep -qE 'contract_version:[[:space:]]*"4\.0"'; then
        log "[OK] contract_version: 4.0"
    else
        log_err "[FAIL] contract_version: \"4.0\" 부재 — v4 marker 미확인"
        fail=$((fail + 1))
    fi

    # A2: frontmatter status: Active
    if printf '%s' "$local_content" | grep -qE '^status:[[:space:]]*Active'; then
        log "[OK] status: Active"
    else
        log_err "[FAIL] frontmatter status: Active 부재 — v4 Active 미확인"
        fail=$((fail + 1))
    fi

    # A3: worker_dialog_rounds field 정의 존재
    if printf '%s' "$local_content" | grep -qE 'worker_dialog_rounds'; then
        log "[OK] worker_dialog_rounds field 정의 존재 (Adversarial measurable — ADR-044 §결정 5)"
    else
        log_err "[FAIL] worker_dialog_rounds field 정의 부재 — ADR-044 §결정 5 measurable field 미확인"
        fail=$((fail + 1))
    fi

    # A4: v3 deprecated fields NOT present in schema definition block (## 2. Schema 섹션 내)
    # Extract schema section
    schema_block="$(printf '%s' "$local_content" | awk '
        /^## 2\. Schema/ { in_schema=1; next }
        in_schema && /^## [0-9]/ { in_schema=0 }
        in_schema { print }
    ')"

    v3_deprecated_fields="decision_state sonnet_final_status decider_decision_ref"
    for f in $v3_deprecated_fields; do
        if printf '%s' "$schema_block" | grep -qE "^[[:space:]]+${f}:" ; then
            log_err "[FAIL] schema §2 에 v3 deprecated field '${f}' 잔존 — v4 정식 제거 미완료"
            fail=$((fail + 1))
        else
            log "[OK] v3 deprecated field '${f}' schema §2 에 부재 (제거 완료)"
        fi
    done

    # A5: 4-step Orchestrator algorithm 언급 (v3 5-step → v4 4-step)
    if printf '%s' "$local_content" | grep -qE '4-step'; then
        log "[OK] 4-step Orchestrator algorithm 언급 존재"
    else
        log_err "[FAIL] 4-step Orchestrator algorithm 언급 부재 — v4 algorithm 정의 미완료"
        fail=$((fail + 1))
    fi

    # A6: pl_recommendation 4-value enum 언급 (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE)
    if printf '%s' "$local_content" | grep -qE 'ESCALATE_PACKET_INCOMPLETE'; then
        log "[OK] pl_recommendation 4-value enum (ESCALATE_PACKET_INCOMPLETE) 존재"
    else
        log_err "[FAIL] pl_recommendation ESCALATE_PACKET_INCOMPLETE 부재 — v4 enum 미정의"
        fail=$((fail + 1))
    fi
fi

# ─────────────────────────────────────────
# Check B: v4 packet yaml fixture 검증 (선택)
# ─────────────────────────────────────────
if [ -n "$PACKET_PATH" ]; then
    log ""
    log "=== Check B: review-verdict v4 packet file: $PACKET_PATH ==="

    if [ ! -f "$PACKET_PATH" ]; then
        log_err "[FAIL] packet file 부재: $PACKET_PATH"
        fail=$((fail + 1))
    else
        packet_content="$(cat "$PACKET_PATH")"

        # B1: contract_version: "4.0" present
        if printf '%s' "$packet_content" | grep -qE 'contract_version:[[:space:]]*"4\.0"'; then
            log "[OK] packet contract_version: 4.0"
        else
            log_err "[FAIL] packet contract_version: \"4.0\" 부재"
            fail=$((fail + 1))
        fi

        # B2: worker_dialog_rounds field present and is integer
        if printf '%s' "$packet_content" | grep -qE 'worker_dialog_rounds:[[:space:]]*[0-9]+'; then
            wdr="$(printf '%s' "$packet_content" | grep -E 'worker_dialog_rounds:' | head -1 | sed -E 's/.*worker_dialog_rounds:[[:space:]]*([0-9]+).*/\1/')"
            log "[OK] worker_dialog_rounds: $wdr (int — Adversarial measurable)"
        else
            log_err "[FAIL] packet worker_dialog_rounds field 부재 또는 비정수 — v4 Adversarial field 미기입"
            fail=$((fail + 1))
        fi

        # B3: v3 deprecated fields NOT present
        for f in decision_state sonnet_final_status decider_decision_ref; do
            if printf '%s' "$packet_content" | grep -qE "^[[:space:]]+${f}:"; then
                log_err "[FAIL] packet 에 v3 deprecated field '${f}' 잔존"
                fail=$((fail + 1))
            else
                log "[OK] v3 field '${f}' packet 에 부재"
            fi
        done

        # B4: pl_recommendation valid value
        pl_rec="$(printf '%s' "$packet_content" | grep -E 'pl_recommendation:' | head -1 | sed -E 's/.*pl_recommendation:[[:space:]]*([^[:space:]#]+).*/\1/' | tr -d "'\"")"
        case "$pl_rec" in
            PASS|FIX|FIX_DISCRETIONARY|ESCALATE_PACKET_INCOMPLETE)
                log "[OK] pl_recommendation: $pl_rec (valid)"
                ;;
            "")
                log_err "[FAIL] pl_recommendation field 부재"
                fail=$((fail + 1))
                ;;
            *)
                log_err "[FAIL] pl_recommendation: '$pl_rec' (invalid — must be PASS/FIX/FIX_DISCRETIONARY/ESCALATE_PACKET_INCOMPLETE)"
                fail=$((fail + 1))
                ;;
        esac

        # B5: lane field present
        if printf '%s' "$packet_content" | grep -qE '^[[:space:]]+lane:[[:space:]]*(design|code|security)'; then
            log "[OK] lane field present (design/code/security)"
        else
            log_err "[FAIL] lane field 부재 또는 invalid (must be design|code|security)"
            fail=$((fail + 1))
        fi
    fi
fi

log ""
log "=== Summary: $fail FAIL ==="

if [ $STRICT -eq 1 ] && [ $fail -gt 0 ]; then
    exit 1
fi
exit 0
