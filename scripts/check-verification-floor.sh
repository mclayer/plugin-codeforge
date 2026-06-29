#!/usr/bin/env bash
# check-verification-floor.sh — lane verification floor mechanical 검출 (CFP-2471 / Epic CFP-2468 Track W / W3).
#
# 검증 floor = ≥1 independent peer (SoD: implementer ≠ certifier). ADR-044 Amendment 4 §결정 10 +
# concept docs/domain-knowledge/concept/lane-verification-floor.md SSOT. review-verdict-v4 (v4.15)
# verdict packet 의 peer_degrade block (peer_count / degrade_reason / degrade_acknowledged) 을 검사:
#
#   축① (self-audit verdict 무효): peer_count: 0 (implementer=certifier, 0 independent peer) +
#        pl_recommendation: PASS → floor 위반 = verdict 무효·차단 (ADR-119 Amd 2 ground-truth).
#        peer_count >= 1 + PASS → 통과 (floor 충족).
#
#   축② (silent degrade 차단): peer_count: 1 인데 degrade_acknowledged 부재/false (silent 2→1 degrade) →
#        차단 (ADR-094 (a) silent harm 거부). peer_count: 1 + degrade_acknowledged: true + degrade_reason
#        (honest degrade, ADR-094 (c)) → 통과 (single-peer honest degrade 가 정식 floor 충족).
#
# enforcement layer (PreToolUse Agent matcher deny) 는 본 Story 미구현 — 관측 baseline (verdict packet lint)
# 만. PreToolUse matcher P2 정확 토큰 + CLI 런타임 발동 empirical 미확정 ([empirical-source: TBD],
# 설계 §결정10d 보류). 보안 lane floor 차등 (≥1 peer + 1차 native layer + dependency manifest) = D2 — 본
# script 는 peer floor (축①②) 만 검사, native-layer presence 는 ClaudeReviewAgent ESCALATE_PACKET_INCOMPLETE
# 영역 (별 검사면).
#
# Usage:
#   bash scripts/check-verification-floor.sh --verdict <path>     # YAML verdict packet file 검사
#   bash scripts/check-verification-floor.sh < verdict.yaml       # stdin
#   bash scripts/check-verification-floor.sh --verdict <path> --strict   # 위반 시 exit 1
#
# Exit code:
#   Default mode: 0 always (advisory — stderr 출력, ADR-027 §결정 2 LLM-trust / ADR-128 warning-tier 정합)
#   Strict mode (--strict): 0 (floor 충족) / 1 (floor 위반: 축① 또는 축②)
#
# Tier: warning-tier (local-only, ADR-128 상속). branch protection 6-tuple 무변경.

set -uo pipefail

QUIET=0
STRICT=0
VERDICT_PATH=""

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT=1; shift ;;
        --verdict) VERDICT_PATH="$2"; shift 2 ;;
        -h|--help)
            sed -n '/^# check-verification-floor/,/^# Tier:/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

log() { [ $QUIET -eq 0 ] && printf '%s\n' "$1"; }
log_err() { printf '%s\n' "$1" >&2; }

# verdict packet 본문 취득 (file 우선 → stdin fallback)
read_verdict() {
    if [ -n "$VERDICT_PATH" ]; then
        if [ ! -f "$VERDICT_PATH" ]; then
            log_err "[FAIL] verdict packet file 부재: $VERDICT_PATH"
            return 1
        fi
        cat "$VERDICT_PATH"
    else
        cat
    fi
}

# scalar field 추출 — `key: value` (peer_degrade block 안 indented 도 포함). 첫 매치만.
#   주석(#) 제거 + 양끝 공백/따옴표 strip. 미발견 시 빈 문자열.
extract_scalar() {
    local body="$1" key="$2"
    printf '%s\n' "$body" \
        | grep -E "^[[:space:]]*${key}:[[:space:]]*" \
        | head -n1 \
        | sed -E "s/^[[:space:]]*${key}:[[:space:]]*//" \
        | sed -E 's/[[:space:]]*#.*$//' \
        | sed -E 's/^["'\'']//; s/["'\'']$//' \
        | sed -E 's/[[:space:]]*$//'
}

# peer_degrade block 존재 여부 (key line presence — 주석 라인 제외)
has_peer_degrade_block() {
    local body="$1"
    printf '%s\n' "$body" | grep -Eq '^[[:space:]]*peer_degrade:[[:space:]]*$'
}

# degrade_acknowledged 가 true 로 명시됐는지 (presence + true 동시)
ack_is_true() {
    local body="$1"
    local val
    val="$(extract_scalar "$body" "degrade_acknowledged")"
    [ "$val" = "true" ]
}

run_check() {
    local body
    body="$(read_verdict)" || { [ $STRICT -eq 1 ] && exit 1; exit 0; }

    if [ -z "$body" ]; then
        log_err "[FAIL] verdict packet 본문 빈 — --verdict <path> 또는 stdin 으로 packet 주입"
        [ $STRICT -eq 1 ] && exit 1
        exit 0
    fi

    local pl_rec peer_count
    pl_rec="$(extract_scalar "$body" "pl_recommendation")"
    peer_count="$(extract_scalar "$body" "peer_count")"

    local violations=0

    # ── 축① self-audit verdict 무효 ──────────────────────────────────────────
    # peer_count: 0 (0 independent peer = implementer 자신만 = SoD 위반) + PASS → 무효.
    # peer_count 미제공 (block 부재) = degrade 없음 = 정상 2-peer (또는 by-design) → 검사 대상 외 (floor 충족 가정).
    if [ -n "$peer_count" ] && [[ "$peer_count" =~ ^[0-9]+$ ]]; then
        if [ "$peer_count" -eq 0 ]; then
            if [ "$pl_rec" = "PASS" ]; then
                log_err "[FAIL 축①] self-audit verdict 무효 — peer_count: 0 (0 independent peer, implementer=certifier = SoD 위반) + pl_recommendation: PASS. 검증 floor (≥1 independent peer) 미충족 → verdict 무효·차단 (ADR-044 Amd 4 §결정 10 / ADR-119 Amd 2 ground-truth)"
                violations=$((violations + 1))
            else
                log "[OK 축①] peer_count: 0 이나 pl_recommendation != PASS ($pl_rec) — self-audit PASS 발화 아님 (차단 비대상)"
            fi
        else
            log "[OK 축①] peer_count: $peer_count (>= 1 independent peer) — 검증 floor (SoD) 충족"
        fi
    else
        log "[OK 축①] peer_degrade block 부재 또는 peer_count 미제공 — degrade 없음 (정상 2-peer 또는 floor 충족 single-peer-by-design 가정)"
    fi

    # ── 축② silent degrade 차단 ──────────────────────────────────────────────
    # peer_count: 1 (single-peer degrade) 인데 degrade_acknowledged 부재/false (silent) → 차단.
    # peer_count: 1 + degrade_acknowledged: true (+ degrade_reason) = honest degrade → 통과.
    if [ -n "$peer_count" ] && [[ "$peer_count" =~ ^[0-9]+$ ]] && [ "$peer_count" -eq 1 ]; then
        if ack_is_true "$body"; then
            local reason
            reason="$(extract_scalar "$body" "degrade_reason")"
            if [ -z "$reason" ]; then
                log_err "[FAIL 축②] honest degrade 사유 부재 — peer_count: 1 + degrade_acknowledged: true 이나 degrade_reason 빈. ADR-094 (c) '사유 강제 기록' 미충족 → 차단"
                violations=$((violations + 1))
            else
                log "[OK 축②] honest degrade — peer_count: 1 + degrade_acknowledged: true + degrade_reason 존재 (single-peer honest degrade = 정식 floor 충족, ADR-094 (c))"
            fi
        else
            log_err "[FAIL 축②] silent degrade 차단 — peer_count: 1 (single-peer degrade) 인데 degrade_acknowledged true 명시 부재 (silent 2→1 degrade). ADR-094 (a) silent harm 거부 → 차단. degrade 시 peer_degrade block (degrade_acknowledged: true + degrade_reason) 명시 의무"
            violations=$((violations + 1))
        fi
    fi

    log ""
    log "=== Summary: $violations floor violation(s) ==="

    if [ $STRICT -eq 1 ] && [ $violations -gt 0 ]; then
        exit 1
    fi
    exit 0
}

run_check
