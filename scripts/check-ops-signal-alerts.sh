#!/usr/bin/env bash
# scripts/check-ops-signal-alerts.sh
# CFP-1195 — 단계 3 PMOAgent escalation pickup (ADR-045 §D-5 check-retro-alerts.sh 답습)
#
# 기능:
#   open `ops-signal` label Issue corpus → 동일 signal_type signature 별 pattern_count 집계.
#   pattern_count >= 2 (N=2, Google SRE/ITIL/NASA industry lower bound) → prompt-injection stdout.
#   → Orchestrator 가 PMOAgent 자동 spawn (도메인 disjoint 답습 — retro corpus vs ops-signal corpus).
#
# ADR-045 §D-9 forcing function 답습 (도메인 disjoint):
#   retro corpus (Story 완료 후) vs operational signal (배포 후 ongoing) — cross-pollinate 0.
#   같은 PMOAgent escalation 메커니즘 공유, 입력 corpus disjoint (label 채널 disjoint).
#
# 단계 4 (사용자 게이트):
#   PMOAgent escalation → Orchestrator → 사용자 확인 후 다음 Epic 후보 결정.
#   자동 Epic 개시 금지 (self-improving != self-executing, ADR-106 §결정 4).
#
# exit code:
#   0 = no alert (ops-signal Issue 부재 / pattern_count < threshold)
#   1 = alert detected (pattern_count >= threshold — Orchestrator PMOAgent spawn 필요)
#
# stdout (exit 1 시):
#   prompt-injection 포맷 — Orchestrator 가 인식해 PMOAgent 자동 spawn 의무 알림
#
# 환경변수:
#   GH_STUB_RESPONSE_FILE   — 테스트용 stub JSON 파일 (check-retro-alerts.sh 패턴 답습)
#   _CFP1195_MOCK_PATTERN_COUNT=<int>  — pattern_count override (mock seam)
#   CFP1195_PATTERN_THRESHOLD=<int>    — threshold override (default: 2)
#   CFP1195_REPO=<owner/repo>          — consumer repo (default: GH 환경변수에서 감지)
#
# SSOT: ADR-106 §결정 1 단계 3 + ADR-045 §D-9 답습 (도메인 disjoint)

set -uo pipefail

PATTERN_THRESHOLD="${CFP1195_PATTERN_THRESHOLD:-2}"  # N=2 (ADR-045 §D-9 industry lower bound)

# 의존성 확인
if ! command -v jq &>/dev/null; then
  echo "[check-ops-signal-alerts] ERROR: jq not found. Install jq and retry." >&2
  exit 0  # advisory — 의존성 없으면 non-blocking
fi

if ! command -v gh &>/dev/null; then
  echo "[check-ops-signal-alerts] ERROR: gh CLI not found." >&2
  exit 0  # advisory
fi

# ---------------------------------------------------------------
# open ops-signal Issue 목록 조회
# GH_STUB_RESPONSE_FILE 이 설정된 경우 stub 파일 사용 (bats 테스트용)
# check-retro-alerts.sh 패턴 verbatim 답습
# ---------------------------------------------------------------
fetch_ops_signal_issues() {
  if [ -n "${GH_STUB_RESPONSE_FILE:-}" ] && [ -f "$GH_STUB_RESPONSE_FILE" ]; then
    cat "$GH_STUB_RESPONSE_FILE"
    return
  fi

  # _CFP1195_MOCK_PATTERN_COUNT override (mock seam — gh 호출 우회)
  if [ -n "${_CFP1195_MOCK_PATTERN_COUNT:-}" ]; then
    # mock: signal_type 별로 mock count 개 Issue 반환 (JSON)
    local mock_count="${_CFP1195_MOCK_PATTERN_COUNT}"
    local signal_type="${_CFP1195_MOCK_SIGNAL_TYPE:-error_rate}"
    python3 -c "
import json, sys
count = int('${mock_count}')
stype = '${signal_type}'
issues = [{'number': i+1, 'title': f'[ops-signal] {stype} issue {i+1}', 'body': f'signal_type: {stype}\\nsignature: mock_sig_{i}'} for i in range(count)]
print(json.dumps(issues))
" 2>/dev/null || echo "[]"
    return
  fi

  # 실제 gh API: open Issue + ops-signal label + body 포함
  local repo_flag=""
  if [ -n "${CFP1195_REPO:-}" ]; then
    repo_flag="--repo ${CFP1195_REPO}"
  fi

  # shellcheck disable=SC2086
  gh issue list \
    ${repo_flag} \
    --state open \
    --label "ops-signal" \
    --json "number,title,body" \
    --limit 200 \
    2>/dev/null || echo "[]"
}

ISSUES_JSON=$(fetch_ops_signal_issues)

# signal_type 별 pattern_count 집계
# ops-signal Issue body 안 "signal_type: <type>" 파싱
declare -A signal_counts
declare -A signal_examples

while IFS= read -r issue; do
  [ -z "$issue" ] && continue
  ISSUE_NUMBER=$(echo "$issue" | jq -r '.number // 0')
  ISSUE_TITLE=$(echo "$issue" | jq -r '.title // ""')
  BODY=$(echo "$issue" | jq -r '.body // ""')

  # signal_type 추출 (body 안 "signal_type: <type>" 패턴)
  SIGNAL_TYPE=$(echo "$BODY" | grep -oP 'signal_type:\s*\K\S+' 2>/dev/null | head -1 || true)
  if [ -z "$SIGNAL_TYPE" ]; then
    # title 안 [ops-signal] <type> 패턴 fallback
    SIGNAL_TYPE=$(echo "$ISSUE_TITLE" | grep -oP '\[ops-signal\]\s+\K[a-z_]+' 2>/dev/null | head -1 || true)
  fi
  [ -z "$SIGNAL_TYPE" ] && SIGNAL_TYPE="unknown"

  # pattern_count 증가
  signal_counts["${SIGNAL_TYPE}"]=$(( ${signal_counts["${SIGNAL_TYPE}"]:-0} + 1 ))
  signal_examples["${SIGNAL_TYPE}"]="${signal_examples["${SIGNAL_TYPE}"]:-}Issue #${ISSUE_NUMBER} (${ISSUE_TITLE}); "
done < <(echo "$ISSUES_JSON" | jq -c '.[]?' 2>/dev/null || true)

# pattern_count >= threshold 체크
ALERT_FOUND=0
declare -A ALERT_TYPES
declare -A ALERT_COUNTS

for stype in "${!signal_counts[@]}"; do
  count="${signal_counts[$stype]}"
  if [ "${count}" -ge "${PATTERN_THRESHOLD}" ]; then
    ALERT_FOUND=1
    ALERT_TYPES["${stype}"]="${stype}"
    ALERT_COUNTS["${stype}"]="${count}"
  fi
done

if [ "$ALERT_FOUND" -eq 1 ]; then
  echo ""
  echo "============================================================"
  echo "[ADR-106 §결정 1 단계 3] ops-signal alert — PMOAgent spawn 필요"
  echo "  pattern_count threshold: ${PATTERN_THRESHOLD} (Google SRE/ITIL/NASA industry lower bound)"
  echo "  label 채널: ops-signal (retro alert 와 domain disjoint — ADR-045 §D-9 답습)"
  echo "============================================================"
  for stype in "${!ALERT_TYPES[@]}"; do
    echo "  - signal_type=${stype}: pattern_count=${ALERT_COUNTS[$stype]} (>= ${PATTERN_THRESHOLD})"
    echo "    examples: ${signal_examples[$stype]:-N/A}"
  done
  echo ""
  echo "ORCHESTRATOR DIRECTIVE: 위 ops-signal Issue 누적에 대해 PMOAgent 를 spawn 하여"
  echo "운영 신호 분석 후 다음 Epic 후보를 사용자에게 보고하십시오."
  echo ""
  echo "단계 4 사용자 게이트 의무:"
  echo "  - PMOAgent 보고 → Orchestrator → 사용자 확인 후 Epic 개시 결정"
  echo "  - 자동 Epic 개시 금지 (self-improving != self-executing, ADR-106 §결정 4)"
  echo "  - escalation_action enum: adr_draft_emitted | escalate_user"
  echo "============================================================"
  exit 1
fi

exit 0
