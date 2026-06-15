#!/usr/bin/env bash
# CFP-2285 S5 (#2291) — Arc B: 진행 미러 코멘트 본문 포맷터 (write-only)
# 인용 출처: 본 Story spawn packet (Arc B = Orchestrator → Jira 단방향 미러).
#   ADR-038 6-point lane 전이(진입/PASS/FIX 검출/원인 판정/재진입/완료) 각 시점에서
#   진행 코멘트를 게시할 때, 그 본문을 결정론적으로 포맷한다.
#
# Arc A 정합: 산출 본문 **선두**에 sentinel 을 박는다 — Arc A echo-guard.sh 가
#   exit 0(skip)으로 걸러 진행 미러 코멘트를 "사용자 답" 으로 재섭취하지 않게 한다
#   (같은 Jira control project 공유 시 self-echo 안전).
#
#   결정론적 순수 텍스트 처리만 수행한다(MCP 호출 없음 — MCP post 는 skill/Orchestrator 담당).
#
# ---- SENTINEL SSOT 정합 ----
#   본 sentinel 은 scripts/jira-channel/echo-guard.sh 의 CF_ORCH_SENTINEL 상수와
#   **byte-동일**해야 한다(불일치 시 echo-guard 가 진행 미러 코멘트를 못 걸러
#   Arc A 폴러가 self-echo 로 재섭취). echo-guard.sh = sentinel 단일 원본(SSOT).
readonly CF_ORCH_SENTINEL='⟦cf-orch⟧'
#
# 입력(인자):
#   $1 = 전이 종류 (6-point 중 1) — enter|pass|fix-detected|cause|re-enter|complete
#   $2 = lane 이름 (예: 설계, 구현, 보안테스트 …)
#   $3 = 1줄 요약 ("현재 무엇 하는중" — 단일 라인, secret/절대경로 금지)
#   $4 = (선택) Story KEY (예: CFP-2285-S5) — anchor 식별자만
#
# 출력/exit:
#   포맷 성공 -> exit 0 + sentinel 선두 진행 코멘트 본문 1줄 stdout
#   인자 오류 -> exit 3 (전이 종류 미인식 / 필수 인자 누락) + stderr
#
# NOTE: deny-scan(secret/절대경로 차단)은 호출 측(skill/Orchestrator)이 본 산출물에
#   대해 별도 수행한다(§2 deny-scan MUST). 본 스크립트는 포맷만 담당 — deny-scan 미포함.
#
# ADR-061 §결정 1 — bash 우선(복잡 로직 아님, 순수 텍스트 조립).
set -euo pipefail

# ---- 전이 종류 → 한글 라벨 정규화 (6-point SSOT, ADR-038) ----
# 진입 / PASS / FIX 검출 / 원인 판정 / 재진입 / 완료 (CLAUDE.md + ADR-038 §결정 2~6).
TRANSITION="${1:-}"
LANE="${2:-}"
SUMMARY="${3:-}"
STORY="${4:-}"

case "$TRANSITION" in
  enter)        LABEL="진입" ;;
  pass)         LABEL="PASS" ;;
  fix-detected) LABEL="FIX 검출" ;;
  cause)        LABEL="원인 판정" ;;
  re-enter)     LABEL="재진입" ;;
  complete)     LABEL="완료" ;;
  *)
    echo "progress-format: 전이 종류 미인식: '${TRANSITION}'" >&2
    echo "  허용: enter|pass|fix-detected|cause|re-enter|complete" >&2
    exit 3
    ;;
esac

if [ -z "$LANE" ]; then
  echo "progress-format: lane 인자(\$2) 누락" >&2
  exit 3
fi
if [ -z "$SUMMARY" ]; then
  echo "progress-format: 요약 인자(\$3) 누락" >&2
  exit 3
fi

# ---- 본문 조립 (sentinel 선두 — echo-guard 정합) ----
# 형식: ⟦cf-orch⟧ MIRROR <전이라벨> lane=<lane> [story=<KEY>] — <1줄 요약>
#   MIRROR 토큰 = Arc B 진행 미러임을 명시(Arc A 결정 post/mirror/PROCESSED 와 구분).
#   요약은 단일 라인으로 강제(개행 제거) — "현재 무엇 하는중" 1줄 입도.
SUMMARY_ONELINE="$(printf '%s' "$SUMMARY" | tr '\n' ' ')"

STORY_FIELD=""
if [ -n "$STORY" ]; then
  STORY_FIELD=" story=${STORY}"
fi

printf '%s MIRROR %s lane=%s%s — %s\n' \
  "$CF_ORCH_SENTINEL" "$LABEL" "$LANE" "$STORY_FIELD" "$SUMMARY_ONELINE"

exit 0
