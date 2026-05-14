#!/usr/bin/env bash
# scripts/check-retro-alerts.sh
# CFP-628 Story 2 / ADR-045 §D-5 — retro alert pre-screen (SessionStart hook)
#
# 기능:
#   open `phase:완료` issue 안 `[PMO] retro alert` prefix comment scan.
#   created_at filter: PR merge + 35min 경과 (retry 4회 완료 후) = 2100초.
#   35min 미만 = retry 진행 중 false positive → filter (exit 0).
#   ESCALATE comment (`[PMO] Retro automation failed`) 는 별 prefix → skip (exit 0).
#
# exit code:
#   0 = no alert detected (정상 / 35min 미만 / ESCALATE comment 만)
#   1 = alert detected (retro 미처리 issue 존재 — Orchestrator PMOAgent spawn 필요)
#
# stdout (exit 1 시):
#   prompt-injection 포맷 — Orchestrator 가 인식해 PMOAgent 자동 spawn 의무 알림
#
# 사용:
#   bash scripts/check-retro-alerts.sh
#
# SSOT: spec §3.3 verbatim + plan Task 2.2 verbatim (CFP-628)
# ADR-061 정합 — bash 전용 (Python heredoc 금지, jq dependency 명시)
#
# 환경:
#   GH_STUB_RESPONSE_FILE (테스트용) — 설정 시 gh api 대신 해당 파일 사용

set -uo pipefail

ALERT_PREFIX="[PMO] retro alert"
FILTER_SECONDS=2100  # 35 min = 35 * 60

# 의존성 확인
if ! command -v jq &>/dev/null; then
  echo "[check-retro-alerts] ERROR: jq not found. Install jq and retry." >&2
  exit 0  # advisory — 의존성 없으면 non-blocking
fi

# gh 명령어 확인
if ! command -v gh &>/dev/null; then
  echo "[check-retro-alerts] ERROR: gh CLI not found." >&2
  exit 0  # advisory
fi

# ---------------------------------------------------------------
# open phase:완료 issue 목록 + comments 조회
# GH_STUB_RESPONSE_FILE 이 설정된 경우 stub 파일 사용 (bats 테스트용)
# ---------------------------------------------------------------
fetch_issues() {
  if [ -n "${GH_STUB_RESPONSE_FILE:-}" ] && [ -f "$GH_STUB_RESPONSE_FILE" ]; then
    cat "$GH_STUB_RESPONSE_FILE"
    return
  fi

  # 실제 gh API: open issue + phase:완료 label + comments 포함
  gh issue list \
    --state open \
    --label "phase:완료" \
    --json "number,title,comments" \
    --limit 100 \
    2>/dev/null || echo "[]"
}

# 현재 UTC epoch
NOW=$(date -u +%s 2>/dev/null || python3 -c "import time; print(int(time.time()))")

ISSUES_JSON=$(fetch_issues)

ALERT_FOUND=0
ALERT_MESSAGES=()

# jq 로 issue / comment 파싱
while IFS= read -r line; do
  ISSUE_NUMBER=$(echo "$line" | jq -r '.number')
  ISSUE_TITLE=$(echo "$line" | jq -r '.title')
  COMMENTS=$(echo "$line" | jq -c '.comments[]?' 2>/dev/null || true)

  while IFS= read -r comment; do
    [ -z "$comment" ] && continue
    BODY=$(echo "$comment" | jq -r '.body // ""')
    CREATED_AT=$(echo "$comment" | jq -r '.created_at // ""')

    # prefix 매칭: "[PMO] retro alert" (대소문자 구분)
    if [[ "$BODY" != "${ALERT_PREFIX}"* ]]; then
      continue
    fi

    # created_at 파싱 → epoch
    if [ -z "$CREATED_AT" ]; then
      continue
    fi

    # epoch 변환 (GNU date / BSD date 호환)
    COMMENT_EPOCH=$(date -u -d "$CREATED_AT" +%s 2>/dev/null) || \
      COMMENT_EPOCH=$(date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$CREATED_AT" +%s 2>/dev/null) || \
      COMMENT_EPOCH=$(python3 -c "
import sys
from datetime import datetime, timezone
try:
    ts = datetime.strptime('$CREATED_AT', '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    print(int(ts.timestamp()))
except Exception as e:
    print(0)
" 2>/dev/null) || COMMENT_EPOCH=0

    ELAPSED=$(( NOW - COMMENT_EPOCH ))

    if [ "$ELAPSED" -lt "$FILTER_SECONDS" ]; then
      # 35min 미만 — retry 진행 중, false positive 차단
      continue
    fi

    # alert detected
    ALERT_FOUND=1
    ALERT_MESSAGES+=("Issue #${ISSUE_NUMBER} (${ISSUE_TITLE}): ${BODY}")
  done <<< "$COMMENTS"
done < <(echo "$ISSUES_JSON" | jq -c '.[]?' 2>/dev/null || true)

if [ "$ALERT_FOUND" -eq 1 ]; then
  echo ""
  echo "============================================================"
  echo "[ADR-045 §D-5] retro alert detected — PMOAgent spawn 필요"
  echo "============================================================"
  for msg in "${ALERT_MESSAGES[@]}"; do
    echo "  - ${msg}"
  done
  echo ""
  echo "ORCHESTRATOR DIRECTIVE: 위 issue 에 대해 PMOAgent 를 spawn 하여"
  echo "retro file 을 생성하십시오 (ADR-045 §D-5 / CFP-628 Story 2)."
  echo "============================================================"
  exit 1
fi

exit 0
