#!/usr/bin/env bash
# CFP-2521 Phase 2 D3 — delegation-ratio advisory lint (warning-tier, non-blocking).
#
# ADR-044 §결정 11 (DeveloperPLAgent delegation oversight early-signal) +
# ADR-039 Amendment 8 §결정 9 (deferred advisory slot) — layer 1 delegation-ratio
# proxy 측정 (spawn-event-v1 ledger reuse, layer 2 inline-detect 영구 deferred).
#
# spawn-event-v1 contract: docs/inter-plugin-contracts/spawn-event-v1.md §2/§3.
# ledger path: $SPAWN_EVENT_LEDGER (default .claude/ledger/spawn-event.jsonl, env 설정 필수).
#
# **warning-tier 불변**: 항상 exit 0 (비차단). advisory 신호는 ::warning:: 마커로만 표시.
# blocking 승격은 evidence 누적 후 별 CFP — 현 단계는 신호 제공까지 (advisory, CFP-2521 Phase 2).
# layer 2 inline-detect (read target 구별) = 영구 deferred (Change Plan §8.D, "Read-Q&A vs
# Read-수정 구별 불가 → 측정 불가" 근거).
#
# 동작 원리:
#   1. spawn-event-v1 ledger 읽기 (opt-in, default false — 부재/empty 시 vacuous).
#   2. lane 세그먼트별 delegation-ratio 계산:
#      - ratio = (worker spawn 수 in lane) / (PL lane segment 수)
#      - worker spawn = DeveloperAgent / QADeveloperAgent 종 등 (role:dev 동적 roster).
#      - PL spawn = DeveloperPLAgent 종 (PL agent 자신이 수행한 작업).
#   3. carve-out R5 (essential reads + trivial reads 제외):
#      - 단일 segment 는 fire 금지 (sustained pattern 요구, R5 §결정 2).
#      - worker spawn 충분 시 fire 금지 (delegation 충분 신호, R5 §결정 1).
#   4. sustained low-delegation pattern 탐지: ≥MIN_SEGMENTS 구간에서
#      worker count < MIN_WORKERS 이면 ::warning:: emit + status=advisory.
#
# 환경변수 (threshold):
#   PL_DELEGATION_MIN_WORKERS  — worker spawn floor (default 1; ratio 요구사항).
#                                 PL lane 에 ≥1 worker 있으면 delegation 충분으로 판정.
#   PL_DELEGATION_MIN_SEGMENTS — sustained pattern floor (default 2; single-segment
#                                 제외로 R5 trivial 제외). ≥2 segment 구간에서만 fire.
#   SPAWN_EVENT_LEDGER         — ledger file path (default .claude/ledger/spawn-event.jsonl).
#                                 env 미설정 시 그 default 로 시도, 미존재 시 vacuous.
#
# 종료 코드: 0 (항상 — warning-tier).
# 출력:
#   status=vacuous              (ledger 부재/empty/opt-out)
#   status=ok                   (delegation 충분)
#   status=advisory             (low-delegation pattern 탐지, ::warning:: emit)
#
# Usage:
#   bash scripts/check-pl-delegation-ratio.sh
#   PL_DELEGATION_MIN_WORKERS=1 bash scripts/check-pl-delegation-ratio.sh
#
# Exit code: 0 (always — warning-tier, non-blocking)
#

set -euo pipefail

# ─── 함수 정의 ───

# wrapper sourcing 진입점 — PL_DELEGATION_RATIO_LIB=1 로 source 하면 함수만 로드.
if [ "${PL_DELEGATION_RATIO_LIB:-0}" = "1" ]; then
  return 0 2>/dev/null || exit 0
fi

# ─── main 로직 ───

# 기본값 설정
MIN_WORKERS="${PL_DELEGATION_MIN_WORKERS:-1}"
MIN_SEGMENTS="${PL_DELEGATION_MIN_SEGMENTS:-2}"
LEDGER="${SPAWN_EVENT_LEDGER:-.claude/ledger/spawn-event.jsonl}"

# ledger 파일 존재 확인
if [ ! -f "$LEDGER" ]; then
  echo "status=vacuous"
  exit 0
fi

# ledger 비어있는지 확인 (row 0 = opt-out 또는 empty)
row_count=$(wc -l < "$LEDGER" 2>/dev/null || echo 0)
if [ "$row_count" -eq 0 ]; then
  echo "status=vacuous"
  exit 0
fi

# ─── 데이터 수집 (spawn-event-v1 행 파싱) ───
# jq 필수 (JSON 파싱). jq 부재 시 graceful vacuous.
if ! command -v jq >/dev/null 2>&1; then
  echo "status=vacuous"
  exit 0
fi

# jq query: agent_type 필터 + lane_label 집계
# jq -s = 전체 행 배열로 읽기 (JSONL → JSON array)
# 결과: JSON array of {lane, pl_count, worker_count}
jq_output=$(jq -s '
  group_by(.lane_label) |
  map({
    lane: .[0].lane_label,
    pl_count: map(select(.agent_type == "DeveloperPLAgent")) | length,
    worker_count: map(select(.agent_type == "DeveloperAgent" or .agent_type == "QADeveloperAgent")) | length
  })
' "$LEDGER" 2>/dev/null || true)

if [ -z "$jq_output" ]; then
  # jq 파싱 실패 → graceful vacuous
  echo "status=vacuous"
  exit 0
fi

# ─── delegation ratio 평가 (carve-out R5 honoring) ───
# R5 §결정 1: worker 충분 시 fire 금지 (≥MIN_WORKERS 면 adequate).
# R5 §결정 2: single segment 제외 (sustained pattern 요구 ≥MIN_SEGMENTS).
#
# jq 출력을 배열로 처리: map 으로 원소를 순회하면서 low-delegation 판정
low_delegation_lanes=$(echo "$jq_output" | jq -r '
  map(
    select(
      .pl_count >= '"$MIN_SEGMENTS"' and
      .worker_count < '"$MIN_WORKERS"'
    ) | .lane
  ) | .[]
' 2>/dev/null || true)

# ─── 결과 emit ───
if [ -z "$low_delegation_lanes" ]; then
  # 모든 lane 충분 또는 carve-out 적용
  echo "status=ok"
  exit 0
fi

# low-delegation pattern 탐지 → advisory warning emit
lane_list=$(echo "$low_delegation_lanes" | paste -sd, - || echo "$low_delegation_lanes")
echo "::warning::PL delegation ratio 저: $lane_list 레인 에서 sustained low-delegation 패턴 탐지 (worker spawn < $MIN_WORKERS). 설계 / 구현 결합도 및 PL 과부하 검토 (CFP-2521 Phase 2 D3 advisory)"
echo "status=advisory"

# warning-tier — 항상 exit 0
exit 0
