#!/usr/bin/env bash
# scripts/check-deferral-carrier-declared.sh — deferral carrier declared (no-TBD) lint thin bash wrapper
#
# CFP-2591 Phase 2 / ADR-060 §결정 6 — deferred-followup placeholder carrier
#   (deferred_followup_cfp: TBD / CFP-TBD / unwired FU-N-N) mechanical 검출 + baseline new-only
#   grandfather subtract (Clean-as-You-Code). (a) registry FLAG 은 sibling gate 소관.
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-deferral-carrier-declared.sh check [--repo-root <p>] [--paths <glob> ...] [--baseline <p>]
#
# Exit codes (ADR-060 §결정 15 3-tier — blocking-on-pr surfacing, CFP-2594):
#   0 = PASS (NEW 0)
#   1 = NEW 1+ (red-X surface — workflow continue-on-error 제거, CFP-2594)
#   2 = SETUP error (검사 경로 부재 / --baseline missing·malformed / python3 미설치)
#
# Prior art: scripts/check-lane-count-ssot.sh / scripts/check-deferred-followup-reconcile.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-deferral-carrier-declared-infra-error] check-deferral-carrier-declared: python3 not installed"
  exit 2
}

# 인자 없으면 check 서브커맨드 default (workflow run: 본문 단순화)
if [ "$#" -eq 0 ]; then
  set -- check
fi

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_deferral_carrier_declared.py" "$@"
