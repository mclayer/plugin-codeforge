#!/usr/bin/env bash
# scripts/check-issue-body-claim-pre-screen.sh — issue-body-claim-pre-screen 게이트 thin bash wrapper
#
# CFP-2382 / ADR-082 Amendment 20 §결정 15 (CFP-1559 carrier) — orchestrator-authored followup
#   Issue body 안 4 sub-pattern (PR state / CFP state / count / sister carrier) stale-claim 을
#   동일-line `[verified-via:` annotation presence 로 pre-screen (warning tier, advisory).
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# 입력: 환경변수 ISSUE_BODY (workflow 가 github.event.issue.body 주입) 또는 인자로 파일 경로.
#   - 인자 1개 (파일 경로) 제공 시: 그 파일을 직접 scan (테스트/디버그용).
#   - 인자 없을 시: ISSUE_BODY → /tmp 파일 → python file-input (workflow 경로).
#
# Usage:
#   ISSUE_BODY="$(...)" bash scripts/check-issue-body-claim-pre-screen.sh
#   bash scripts/check-issue-body-claim-pre-screen.sh /path/to/issue-body.txt
#
# Exit codes (ADR-060 §결정 15 3-tier — warning tier):
#   0 = PASS (FLAG 0)
#   1 = FLAG 1+ (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
#   2 = SETUP error (python3 미설치 / 입력 부재)
#
# Prior art: scripts/check-deferred-followup-reconcile.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-issue-body-pre-screen-infra-error] check-issue-body-claim-pre-screen: python3 not installed"
  exit 2
}

# 입력 파일 결정: 인자 우선, 없으면 ISSUE_BODY env → /tmp 파일
if [ "$#" -ge 1 ]; then
  _BODY_FILE="$1"
else
  _BODY_FILE="$(mktemp)"
  trap 'rm -f "$_BODY_FILE"' EXIT
  # printf 로 trailing newline 처리 (env 가 비어 있어도 빈 파일 생성 — PASS 경로)
  printf '%s' "${ISSUE_BODY:-}" > "$_BODY_FILE"
fi

# ADR-061 §결정 1 thin wrapper — exec 불가 (trap cleanup 필요) → python 직접 실행 + exit code passthrough
python3 "${_SCRIPT_DIR}/lib/check_issue_body_claim_pre_screen.py" "$_BODY_FILE"
