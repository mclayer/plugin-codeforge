#!/usr/bin/env bash
# scripts/lib/soak-verdict-kernel.sh — soak 지속-liveness verdict kernel (순수 판정 함수)
#
# CFP-2613 (Epic CFP-2602 G2) / ADR-148 §결정3 (verdict-kernel seam) — single-source
#   soak 판정 로직. post-deploy-benchmark.yml 의 inline sink-monotone if/else 를
#   순수 함수 + 안정 reason-code enum 으로 single-source 화 (동작-불변 리팩터, §6).
#
# 호출자 3종 (ADR-148 §결정3): post-deploy-benchmark.yml(기존) + scripts/soak-runner.sh
#   (orchestration vehicle) + wrapper fixture-daemon self-test (wave 2).
#
# perf 필드 배제 (ADR-148 §결정10) — kernel = liveness verdict only, no p50/p95/throughput/rss.
#   soak verdict = liveness 스코프 고정 (성능 metric 진입 = ADR-121 deploy-review 부활선 = 금지).
#
# ── 계약 ──────────────────────────────────────────────────────────────────────
#   evaluate_soak_sample prev cur first threshold floor deadline_reached
#     순수 판정 함수 — reason-code 1개를 stdout 으로 echo, exit 0 반환.
#     side-effect 0 · exit-1 0 — 호출자(orchestration)가 reason-code 를 받아 행동 결정.
#
#   인자:
#     prev             = 직전 sink sample (-1 = 이전 sample 없음)
#     cur              = 현재 sink sample
#     first            = floor-window 최초 sample (fallback 경로 net 순증 판정 기준)
#     threshold        = 발현조건(manifestation) 임계 (0 = floor-fallback 경로)
#     floor            = duration_floor_seconds (informational — deadline 계산은
#                        orchestration 소관, kernel 판정은 deadline_reached 로 수신)
#     deadline_reached = "1" (now>=deadline) / "0"
#
#   reason-code enum (안정 · 단일소스 — caller re-encode 금지):
#     CONTINUE FAIL_REGRESSION FAIL_FREEZE PASS_THRESHOLD PASS_FLOOR FAIL_THRESHOLD_MISS
#     (design §결정3 enum = 5, +1 additive[FAIL_THRESHOLD_MISS] for behavior-invariance
#      of existing threshold-miss FAIL — 아래 절 3 주석 참조. impl-level single-sourcing,
#      게이트 의미 변경 아님.)
#
#   판정 로직 (현 post-deploy-benchmark.yml L148-177 semantics 를 정확 재현 — 동작-불변):
#     1) prev>=0 ∧ cur<prev                → FAIL_REGRESSION      (역행, workflow L148-151)
#     2) threshold>0 ∧ cur>=threshold      → PASS_THRESHOLD       (임계 도달, L154-157)
#     3) deadline_reached==1:
#          threshold>0 (임계 미도달)       → FAIL_THRESHOLD_MISS  (L161-164, additive)
#          threshold==0 ∧ cur<=first       → FAIL_FREEZE          (net 순증 없음, L168-171)
#          threshold==0 ∧ cur>first        → PASS_FLOOR           (net 순증 확인, L172-173)
#     4) 그 외                              → CONTINUE             (계속 구동, L176-177)
# ──────────────────────────────────────────────────────────────────────────────

# reason-code enum 단일 소스 (caller 참조용 — re-encode 금지, ADR-148 §결정3 안정 enum)
SOAK_VERDICT_CODES="CONTINUE FAIL_REGRESSION FAIL_FREEZE PASS_THRESHOLD PASS_FLOOR FAIL_THRESHOLD_MISS"
export SOAK_VERDICT_CODES

# evaluate_soak_sample: 순수 판정 함수 (부수효과 0, exit 0).
evaluate_soak_sample() {
  local prev="$1" cur="$2" first="$3" threshold="$4" floor="$5" deadline_reached="$6"
  : "$floor"  # floor = informational only (deadline 계산 orchestration 소관) — 미사용 명시

  # 1) sink 역행 (prev>=0 ∧ cur<prev) → FAIL_REGRESSION  [workflow L148-151]
  #    prev=-1 (이전 sample 없음) 이면 역행 판정 skip.
  if [ "$prev" -ge 0 ] && [ "$cur" -lt "$prev" ]; then
    printf '%s\n' "FAIL_REGRESSION"
    return 0
  fi

  # 2) 발현조건 임계 도달 (threshold>0 ∧ cur>=threshold) → PASS_THRESHOLD  [L154-157]
  if [ "$threshold" -gt 0 ] && [ "$cur" -ge "$threshold" ]; then
    printf '%s\n' "PASS_THRESHOLD"
    return 0
  fi

  # 3) deadline 도달 (종점 판정)  [L160-174]
  if [ "$deadline_reached" = "1" ]; then
    if [ "$threshold" -gt 0 ]; then
      # manifestation 경로: deadline 경과했으나 임계 미도달.
      # design §결정3 enum = 5, +1 additive for behavior-invariance of existing
      #   threshold-miss FAIL — 현 workflow L161-164 는 여기서 exit 1
      #   ("duration_floor 경과했으나 발현조건 임계 미도달"). additive reason-code 는
      #   기존 FAIL path 를 LABEL 만 함 (게이트 의미 변경 아님 · exit-1 FAIL 그대로).
      printf '%s\n' "FAIL_THRESHOLD_MISS"
      return 0
    fi
    # floor 경로 (threshold==0): floor-window net 순증 판정.
    if [ "$cur" -le "$first" ]; then
      printf '%s\n' "FAIL_FREEZE"   # net 순증 없음 (동결)  [L168-171]
      return 0
    fi
    printf '%s\n' "PASS_FLOOR"      # net 순증 확인          [L172-173]
    return 0
  fi

  # 4) 그 외 → 계속 구동  [L176-177]
  printf '%s\n' "CONTINUE"
  return 0
}
