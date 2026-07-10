#!/usr/bin/env bash
# scripts/check-deferred-followup-reconcile.sh — deferred-followup reconcile 게이트 thin bash wrapper
#
# CFP-2381 / ADR-060 Amendment 18 §결정 32 — "임계 초과 + auto_blocking + 전용 carrier 부재"
#   evidence-checks-registry entry 자동 검출 + 강제 action 3택 (CFP-2594 flip: blocking-on-pr surfacing).
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-deferred-followup-reconcile.sh check [--registry <path>] [--repo-root <path>]
#   bash scripts/check-deferred-followup-reconcile.sh resolve --command "<detect_command 값>"
#
# Exit codes (ADR-060 §결정 15 3-tier — blocking-on-pr surfacing, CFP-2594):
#   0 = PASS (FLAG 0)
#   1 = FLAG 1+ (red-X surface — workflow continue-on-error 제거, CFP-2594)
#   2 = SETUP error (registry 부재 / yaml parse 실패 / python3 미설치)
#
# Prior art: scripts/check-governance-drift.sh / scripts/check-increment-justification.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-evidence-registry-infra-error] check-deferred-followup-reconcile: python3 not installed"
  exit 2
}

# 인자 없으면 check 서브커맨드 default (workflow run: 본문 단순화)
if [ "$#" -eq 0 ]; then
  set -- check
fi

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_deferred_followup_reconcile.py" "$@"
