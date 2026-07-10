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
#   축③ (peer-completion falsifiability): pl_recommendation: PASS (NOT honest single-peer degrade, NOT
#        peer_count: 0) → peer_verdicts[] ≥1 entry 의 target 이 check 시점 FS 실재 + non-empty 여야 통과.
#        자기단언 verify_status 불신·게이트 독립 stat (forged peer_count 구멍 봉합). non-version-gated
#        (anti-evasion). 미충족 → 차단 (ADR-044 Amd 6 §결정 12 falsifiability, warning-tier).
#        ※ 단 위조방지 게이트 아님 — 특정 zero-artifact 위조만 봉합, 임의 실재/stale 파일 pointing 은
#        warning-tier 수용 잔여 리스크 (§3.4: PL claim+proof 동시저작 → full falsifiability 원리상 불가).
#
# enforcement layer (PreToolUse Agent matcher deny) 는 본 Story 미구현 — 관측 baseline (verdict packet lint)
# 만. PreToolUse matcher P2 정확 토큰 + CLI 런타임 발동 empirical 미확정 ([empirical-source: TBD],
# 설계 §결정10d 보류). 보안 lane floor 차등 (≥1 peer + 1차 native layer + dependency manifest) = D2 — 본
# script 는 peer floor (축①②③) 만 검사, native-layer presence 는 ClaudeReviewAgent ESCALATE_PACKET_INCOMPLETE
# 영역 (별 검사면).
#
# Usage:
#   bash scripts/check-verification-floor.sh --verdict <path>     # YAML verdict packet file 검사
#   bash scripts/check-verification-floor.sh < verdict.yaml       # stdin
#   bash scripts/check-verification-floor.sh --verdict <path> --strict   # 위반 시 exit 1
#
# Exit code:
#   Default mode: 0 always (advisory — stderr 출력, ADR-027 §결정 2 LLM-trust / ADR-128 warning-tier 정합)
#   Strict mode (--strict): 0 (floor 충족) / 1 (floor 위반: 축①/②/③)
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

# degrade_acknowledged 가 true 로 명시됐는지 (presence + true 동시)
ack_is_true() {
    local body="$1"
    local val
    val="$(extract_scalar "$body" "degrade_acknowledged")"
    [ "$val" = "true" ]
}

# peer_verdicts[] 파싱 — block walk 로 entry별 target + worker_recommendation 추출 (pure awk, hermetic; yq/python 미사용).
#   출력: entry 당 1 line "<target><US 0x1f><worker_recommendation>" (빈 field 는 빈 문자열). entry 0 (block 부재/빈) → 빈 출력.
#   self-asserted verify_status 는 미추출 — gate 가 독립 stat 으로 판별 (자기단언 불신, ADR-044 Amd 6 §결정 12).
extract_peer_verdicts() {
    local body="$1"
    printf '%s\n' "$body" | awk '
        function indent(s,   n) { n = 0; while (substr(s, n + 1, 1) == " ") n++; return n }
        function clean(v) {
            sub(/[ \t]*#.*$/, "", v)
            sub(/[ \t]+$/, "", v)
            sub(/^["\047]/, "", v)
            sub(/["\047]$/, "", v)
            return v
        }
        { line = $0; sub(/\r$/, "", line); ind = indent(line); rest = substr(line, ind + 1) }
        !in_block {
            if (rest ~ /^peer_verdicts:[ \t]*$/) { in_block = 1; block_indent = ind }
            next
        }
        {
            if (rest ~ /^[ \t]*$/) next
            if (ind <= block_indent) {
                if (have_entry) { print t "\037" w; have_entry = 0 }
                in_block = 0
                next
            }
            if (rest ~ /^-[ \t]/ || rest == "-") {
                if (have_entry) print t "\037" w
                have_entry = 1; t = ""; w = ""
                sub(/^-[ \t]*/, "", rest)
            }
            if (rest ~ /^target:[ \t]*/) { v = rest; sub(/^target:[ \t]*/, "", v); t = clean(v) }
            if (rest ~ /^worker_recommendation:[ \t]*/) { v = rest; sub(/^worker_recommendation:[ \t]*/, "", v); w = clean(v) }
        }
        END { if (have_entry) print t "\037" w }
    '
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

    # ── 축③ peer-completion falsifiability ────────────────────────────────────
    # pl_recommendation: PASS 는 falsifiable peer 완료 증거 (peer_verdicts[] artifact) 로 뒷받침돼야.
    # 발동: pl_rec==PASS AND NOT honest-single-peer-degrade (축② 소관) AND NOT peer_count==0 (축① 선차단).
    # ★non-version-gated: contract_version 게이트 없음 (anti-evasion — version-gating 시 4.15+peer_count:2 우회).
    # ★독립 stat 검증 — entry 자기단언 verify_status 필드 불신 (forged peer_count 구멍 봉합, ADR-044 Amd 6 §결정 12).
    if [ "$pl_rec" = "PASS" ]; then
        # honest single-peer degrade stand-down (축② 소관 = AC-A3 무회귀) — MUT-5 anchor (단일 조건)
        if [ "$peer_count" = "1" ] && ack_is_true "$body" && [ -n "$(extract_scalar "$body" "degrade_reason")" ]; then
            log "[OK 축③] honest single-peer degrade (peer_count: 1 + ack: true + degrade_reason) — 축② 소관, 축③ stand-down (skip)"
        elif [ "$peer_count" = "0" ]; then
            log "[OK 축③] peer_count: 0 — 축① 선차단 영역, 축③ 미도달 (skip)"
        else
            local pv_entries base_dir target wrec resolved_target
            local entry_bad=0
            pv_entries="$(extract_peer_verdicts "$body")"
            if [ -z "$pv_entries" ]; then
                # Violation A (missing): bare PASS / claimed-multi 조기종합 (non-version-gated 조임)
                log_err "[FAIL 축③-missing] peer-completion 미증명 — pl_recommendation: PASS 인데 peer_verdicts[] 부재/0 entry (bare PASS 또는 claimed-multi 조기종합). ≥1 peer verdict artifact 참조 의무 (ADR-044 Amd 6 §결정 12 falsifiability)"
                violations=$((violations + 1))
            else
                if [ -n "$VERDICT_PATH" ]; then base_dir="$(dirname "$VERDICT_PATH")"; else base_dir="."; fi
                while IFS=$'\037' read -r target wrec; do
                    # empty target string → 빈≠증거
                    if [ -z "$target" ]; then
                        log_err "[FAIL 축③-empty] peer_verdict entry 의 target 부재/빈 문자열 — 빈 target 은 증거 아님 (falsifiable artifact 참조 의무)"
                        violations=$((violations + 1)); entry_bad=1; continue
                    fi
                    # target resolution: absolute → as-is, 상대 → dirname(VERDICT_PATH) 기준 (stdin → cwd). Win/Linux portable.
                    case "$target" in
                        /*) resolved_target="$target" ;;
                        [A-Za-z]:/*) resolved_target="$target" ;;
                        [A-Za-z]:\\*) resolved_target="$target" ;;
                        *) resolved_target="$base_dir/$target" ;;
                    esac
                    # 축③-unresolved (MUT-3 anchor): 독립 stat 존재검사 = -unresolved 유일 게이트 (self-asserted verify_status 불신)
                    if [ ! -e "$resolved_target" ]; then
                        log_err "[FAIL 축③-unresolved] peer_verdict target 미실재 — '$resolved_target' (self-asserted verify_status 불신, gate 독립 stat 판별). forged peer_count 구멍 봉합 (ADR-044 Amd 6)"
                        violations=$((violations + 1)); entry_bad=1; continue
                    fi
                    # 축③-empty (MUT-4 anchor): resolved target 실재하나 빈 파일 (0 bytes) = non-empty 유일 게이트
                    if [ -e "$resolved_target" ] && [ ! -s "$resolved_target" ]; then
                        log_err "[FAIL 축③-empty] peer_verdict target 빈 파일 (0 bytes) — '$resolved_target' (빈≠증거, non-empty 판별)"
                        violations=$((violations + 1)); entry_bad=1; continue
                    fi
                    # 축③-content (2차 advisory, existence-verify=P0 대비 P1): worker_recommendation (peer verdict token) 존재
                    if [ -z "$wrec" ]; then
                        log_err "[FAIL 축③-content] peer_verdict entry ('$target') worker_recommendation 부재/빈 — peer 판정 token (PASS/FIX 등) 미기재 (content-binding)"
                        violations=$((violations + 1)); entry_bad=1
                    fi
                done <<< "$pv_entries"
                if [ "$entry_bad" -eq 0 ]; then
                    log "[OK 축③] peer-completion falsifiable — 전 peer_verdict entry target 실재+non-empty AND worker_recommendation 존재 (독립 stat, 위조 불가)"
                fi
            fi
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
