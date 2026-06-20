#!/usr/bin/env bash
# scripts/check-spawn-prompt-fact-verify.sh — spawn-prompt-fact-verify 게이트 thin bash wrapper
#
# CFP-2383 / ADR-082 Amendment 37 §결정 1 layer 1 sub-scope 1-Z (sub-scope 1-L Amd 23, CFP-1590
#   carrier) — worker→worker handoff spawn prompt PR-body-proxy 안 5 fact category
#   (C1 counter / C2 version / C3 SHA / C4 verify-result / C5 file-existence) inherit fact 단언 시
#   동일-line `[verified-via:` annotation presence 로 pre-screen (warning tier, advisory).
# ADR-061: Python entry-point + thin bash wrapper convention (python3 직접 실행 — NO heredoc, NO logic).
#
# 입력: 환경변수 PR_BODY (workflow 가 github.event.pull_request.body 주입) 또는 인자로 파일 경로.
#   - 인자 1개 (파일 경로) 제공 시: 그 파일을 직접 scan (테스트/디버그용).
#   - 인자 없을 시: PR_BODY → /tmp 파일 → python file-input (workflow 경로).
#
# Usage:
#   PR_BODY="$(...)" bash scripts/check-spawn-prompt-fact-verify.sh
#   bash scripts/check-spawn-prompt-fact-verify.sh /path/to/pr-body.txt
#
# Exit codes (ADR-060 §결정 5 3-tier — warning tier):
#   0 = PASS (FLAG 0)
#   1 = FLAG 1+ (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
#   2 = SETUP error (python3 미설치 / 입력 부재)
#
# Prior art: scripts/check-issue-body-claim-pre-screen.sh (S2, ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-spawn-prompt-fact-verify-infra-error] check-spawn-prompt-fact-verify: python3 not installed"
  exit 2
}

# 입력 파일 결정: 인자 우선, 없으면 PR_BODY env → /tmp 파일
if [ "$#" -ge 1 ]; then
  _BODY_FILE="$1"
else
  _BODY_FILE="$(mktemp)"
  trap 'rm -f "$_BODY_FILE"' EXIT
  # printf 로 trailing newline 처리 (env 가 비어 있어도 빈 파일 생성 — PASS 경로)
  printf '%s' "${PR_BODY:-}" > "$_BODY_FILE"
fi

# ADR-061 §결정 1 thin wrapper — exec 불가 (trap cleanup 필요) → python 직접 실행 + exit code passthrough
python3 "${_SCRIPT_DIR}/lib/check_spawn_prompt_fact_verify.py" "$_BODY_FILE"
