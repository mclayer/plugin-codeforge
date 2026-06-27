#!/usr/bin/env bash
# check-stakes-tier-gating.sh — Story-shape 조건부 model tier 판정 로직 SSOT
#   (CFP-2432 / ADR-042 Amendment 16 — InfraOperationalArchitectAgent)
#   (CFP-2445 / ADR-042 Amendment 17 — DomainAgent financial-invariant-0 별 predicate)
#
# 같은 agent role 의 model tier 를 Story 의 stakes(결과 위험)로 분기한다 — tier = f(mandate depth, stakes).
#   InfraOperationalArchitectAgent: low-stakes shape(4-AND) → sonnet, high-stakes → opus (fail-safe).
#   DomainAgent (Amd17): (4-AND low-stakes) AND (financial-invariant-0 shape) → sonnet, else opus.
#     financial-invariant-0 = stakes 4-AND 와 orthogonal 한 financial-correctness 결과접촉 축의 별 predicate.
#     4-AND 가 끄는 것 = stakes·safety mandate, financial-invariant-0 가 끄는 것 = DomainAgent financial mandate.
#     두 predicate AND — 어느 한쪽이라도 false 면 opus (4-AND false=stakes-gated 보존 / inv-0 false=financial mandate 살아있음).
#
# 본 스크립트 = Orchestrator spawn-time 판정 로직의 **결정론적 단일 출처**.
#   Orchestrator 가 직접 호출(stdout 의 tier 를 opts.model 로 사용)하거나,
#   discriminating test(tests/scripts/test-check-stakes-tier-gating.sh)가
#   truth-table 행별 RED→GREEN 변별을 강제 검증한다 (anti-theater).
#
# ── 입력 (env var, 4 stakes 신호) ──
#   STAKES_REAL_FUNDS           실자금 mutation 여부          (yes=high / no=low)
#   STAKES_PRODUCTION_CUTOVER   production cutover 여부        (yes=high / no=low)
#   STAKES_NEW_TRUST_BOUNDARY   신규 신뢰경계 여부(5-enum)    (yes=high / no=low)
#   STAKES_LIVE_EXTERNAL_API    live 외부 API 호출 여부       (yes=high / no=low)
#                               (read-only 시세 수집 포함 — G3 가드)
#   STAKES_OVERLAY_FLOOR        consumer 보수 override         (opus = 강제 opus / 그 외 무시+로그)
#   STAKES_AGENT                대상 agent 이름                 (default InfraOperationalArchitectAgent)
#   STAKES_FINANCIAL_INVARIANT_ZERO  financial-invariant-0 shape 여부 (Amd17 별 predicate, DomainAgent 한정)
#                               (yes = financial 결과 비접촉(invariant-0 확정) / 그 외 = 결과 접촉/미상 → fail-safe opus)
#                               STAKES_AGENT != DomainAgent 면 본 신호 무시(InfraOpArch 동작 무변경).
#
# ── 판정 규칙 (change-plan §3.1 / §8.2) ──
#   INV-1 (fail-safe monotone): 신호 부재/파싱불가 → high(opus). 절대 sonnet 아님.
#   INV-2 (high-absorbing):     임의 1개 high → 전체 high(opus). "하나라도 high면 high".
#   INV-3 (확장-only monotone):  overlay 는 opus 방향(보수)으로만 이동 — sonnet 방향 불가.
#                               clamp = max(wrapper_floor, overlay). down-tier 무시+로그.
#   INV-fin0 (Amd17 별 predicate, DomainAgent): financial-invariant-0 신호가 'yes'(결과 비접촉 확정)
#                               아니면 wrapper_floor 를 opus 로 force (financial mandate 살아있음).
#                               별 predicate 이므로 4-AND 와 AND — 4-AND low 여도 inv-0 미확정이면 opus.
#                               fail-safe monotone (INV-1 동형) — 미상/파싱불가 → opus.
#
# ── 출력 ──
#   stdout: 최종 tier — "opus" 또는 "sonnet" (한 줄)
#   stderr: 판정 근거(어느 조건이 high 인지 / clamp 발화 여부)
#   exit:   0 (정상 판정) — 항상 판정값을 stdout 으로 emit (비차단)
#
# style: scripts/get_consumer_tier.py fail-loud 선례 + check-tier-downgrade-guard.sh rank 동형.
set -euo pipefail

AGENT="${STAKES_AGENT:-InfraOperationalArchitectAgent}"

# ── 단일 stakes 신호 정규화 ──
#   no / false / 0 / none = low 신호 (소문자+공백 trim 후 비교). 그 외(yes / 빈 값 / 미상 /
#   파싱불가 임의 토큰) = high (fail-safe, INV-1).
#   반환: "low" 또는 "high"
normalize_signal() {
  local raw="$1"
  # 소문자 + 공백 trim
  raw="$(printf '%s' "$raw" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
  case "$raw" in
    no|false|0|none) echo "low" ;;
    *)               echo "high" ;;   # yes / 빈 값 / 미상 = fail-safe high (INV-1)
  esac
}

REAL_FUNDS="$(normalize_signal "${STAKES_REAL_FUNDS:-}")"
CUTOVER="$(normalize_signal "${STAKES_PRODUCTION_CUTOVER:-}")"
NEW_BOUNDARY="$(normalize_signal "${STAKES_NEW_TRUST_BOUNDARY:-}")"
LIVE_API="$(normalize_signal "${STAKES_LIVE_EXTERNAL_API:-}")"

# ── 4-AND 판정 (INV-2 high-absorbing) ──
#   low_stakes := real_funds=low ∧ cutover=low ∧ new_boundary=low ∧ live_api=low
#   하나라도 high → wrapper_floor = opus
HIGH_REASONS=""
[ "$REAL_FUNDS" = "high" ]   && HIGH_REASONS="${HIGH_REASONS} real_funds"
[ "$CUTOVER" = "high" ]      && HIGH_REASONS="${HIGH_REASONS} production_cutover"
[ "$NEW_BOUNDARY" = "high" ] && HIGH_REASONS="${HIGH_REASONS} new_trust_boundary"
[ "$LIVE_API" = "high" ]     && HIGH_REASONS="${HIGH_REASONS} live_external_api"

if [ -n "$HIGH_REASONS" ]; then
  WRAPPER_FLOOR="opus"
else
  WRAPPER_FLOOR="sonnet"
fi

# ── financial-invariant-0 별 predicate (CFP-2445 / ADR-042 Amd17, DomainAgent 한정) ──
#   stakes 4-AND 와 orthogonal 한 financial-correctness 결과접촉 축의 *별* predicate.
#   판정 = (4-AND low-stakes) AND (financial-invariant-0 shape). 두 predicate AND.
#   - STAKES_AGENT != DomainAgent → 본 predicate 미적용 (InfraOpArch 동작 무변경, 4-AND 단독).
#   - STAKES_AGENT == DomainAgent →
#       · 4-AND 가 이미 opus (WRAPPER_FLOOR=opus) → financial-invariant-0 여부 무관 opus 유지 (stakes-gated 보존).
#       · 4-AND low (WRAPPER_FLOOR=sonnet) → financial-invariant-0 신호가 'yes' 확정일 때만 sonnet 유지.
#         그 외(결과 접촉 / 미상 / 파싱불가) → opus 로 force (financial mandate 살아있음, fail-safe INV-fin0).
#   fail-safe monotone (INV-1 동형) — financial-invariant-0 신호는 'yes' 명시 외 전부 보수 opus.
if [ "$AGENT" = "DomainAgent" ]; then
  FIN_INV0_RAW="$(printf '%s' "${STAKES_FINANCIAL_INVARIANT_ZERO:-}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
  case "$FIN_INV0_RAW" in
    yes)
      FIN_INV0="confirmed" ;;     # financial 결과 비접촉 확정 (5-AND 전부 충족)
    *)
      FIN_INV0="not_confirmed" ;; # no / 빈 값 / 미상 / 파싱불가 = 결과 접촉 가능 → fail-safe opus
  esac

  if [ "$WRAPPER_FLOOR" = "sonnet" ] && [ "$FIN_INV0" = "confirmed" ]; then
    # 2-predicate AND 충족 (4-AND low ∧ financial-invariant-0 확정) → sonnet 유지 (tier-flip)
    echo "[stakes-tier] ${AGENT}: financial-invariant-0 확정(STAKES_FINANCIAL_INVARIANT_ZERO=yes) ∧ 4-AND low → sonnet eligible (Amd17 2-predicate AND)" >&2
  else
    # 어느 한 predicate false → opus force (별 predicate AND, financial mandate 살아있음)
    if [ "$WRAPPER_FLOOR" = "opus" ]; then
      echo "[stakes-tier] ${AGENT}: 4-AND high → opus (financial-invariant-0 여부 무관, stakes-gated 보존, Amd17 §결정1)" >&2
    else
      echo "[stakes-tier] ${AGENT}: 4-AND low 이나 financial-invariant-0 미확정(STAKES_FINANCIAL_INVARIANT_ZERO='${FIN_INV0_RAW:-(unset)}') → opus force (financial mandate 살아있음, fail-safe INV-fin0)" >&2
    fi
    WRAPPER_FLOOR="opus"
  fi
fi

# ── tier rank (확장-only clamp 용, 사다리 haiku<sonnet<opus) ──
tier_rank() {
  case "$1" in
    haiku)  echo 1 ;;
    sonnet) echo 2 ;;
    opus)   echo 3 ;;
    *)      echo 3 ;;   # 미지 tier = 보수적으로 opus rank (fail-safe)
  esac
}

# ── consumer overlay clamp (INV-3 확장-only) ──
#   overlay 는 보수 방향(opus 강제)만 honor. down-tier 요청은 무시 + stderr 로그.
#   clamp = max(WRAPPER_FLOOR, overlay)  (rank 기준 큰 쪽 = 더 보수적)
FINAL_TIER="$WRAPPER_FLOOR"
OVERLAY_RAW="$(printf '%s' "${STAKES_OVERLAY_FLOOR:-}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
if [ -n "$OVERLAY_RAW" ]; then
  floor_rank="$(tier_rank "$WRAPPER_FLOOR")"
  overlay_rank="$(tier_rank "$OVERLAY_RAW")"
  if [ "$overlay_rank" -gt "$floor_rank" ]; then
    # overlay 가 더 보수적 → honor (확장 방향, INV-3 정합).
    # **F-CR-001**: honor 대입 전 known-enum 검증 — 미지 tier 가 tier_rank() 의 unknown→3
    #   fallback 때문에 sonnet floor 를 out-rank 해 raw 값이 누출되는 leak 차단 (INV-1 정합).
    case "$OVERLAY_RAW" in
      haiku|sonnet|opus)
        FINAL_TIER="$OVERLAY_RAW"
        echo "[stakes-tier] overlay 보수 override honored — ${WRAPPER_FLOOR} → ${OVERLAY_RAW} (확장-only, ADR-127 §결정6)" >&2
        ;;
      *)
        # 미지 tier (rank3 fallback 으로 floor 를 out-rank) = sanitize 없이 누출 위험 → fail-safe opus (INV-1)
        echo "[stakes-tier] overlay 미지 tier '${OVERLAY_RAW}' 무시 — fail-safe opus (INV-1, 미지=보수)" >&2
        FINAL_TIER="opus"
        ;;
    esac
  elif [ "$overlay_rank" -lt "$floor_rank" ]; then
    # overlay 가 더 약함(down-tier 공격적 override) → 무시 + 명시 거부 로그 (INV-3 / AC-3)
    echo "[stakes-tier] overlay down-tier 거부 — overlay='${OVERLAY_RAW}' < wrapper_floor='${WRAPPER_FLOOR}', clamp=max() 적용 (확장-only enforcement, ADR-127 §결정6)" >&2
    # FINAL_TIER 는 WRAPPER_FLOOR 유지 (clamp)
  fi
  # overlay == floor → no-op (변경 없음)
fi

# ── 최종 emit clamp (이중 안전망, F-CR-001) ──
#   stdout 으로 나가는 값이 {haiku,sonnet,opus} 아니면 opus 로 강제 (어떤 경로로도 raw 누출 0, INV-1).
case "$FINAL_TIER" in
  haiku|sonnet|opus) ;;   # 정상 enum
  *)
    echo "[stakes-tier] 최종 tier '${FINAL_TIER}' 가 known-enum 아님 — fail-safe opus 강제 (INV-1 이중 안전망)" >&2
    FINAL_TIER="opus"
    ;;
esac

# ── 판정 근거 stderr ──
if [ -n "$HIGH_REASONS" ]; then
  echo "[stakes-tier] ${AGENT}: high-stakes (high 조건:${HIGH_REASONS}) → wrapper_floor=opus (INV-2 high-absorbing)" >&2
else
  echo "[stakes-tier] ${AGENT}: low-stakes (4-AND 모두 low) → wrapper_floor=sonnet (tier-flip)" >&2
fi
echo "[stakes-tier] ${AGENT}: 최종 tier = ${FINAL_TIER}" >&2

# ── 출력 ──
echo "$FINAL_TIER"
exit 0
