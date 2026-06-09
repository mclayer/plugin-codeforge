#!/usr/bin/env bash
# scripts/check-governance-drift.sh — 거버넌스 지표 drift 감지 thin bash wrapper
#
# CFP-2061-S4 / ADR-060 §결정 31 — governance-drift-detection warning tier (15번째)
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc)
#
# Usage: bash scripts/check-governance-drift.sh [--baseline <path>] [--repo-root <path>] [--dry-run]
#
# Test override env:
#   _CSGD_SKIP_ISSUE_CREATE=1  — Issue auto-create 차단 (dry-run / TC mode)
#   _CSGD_MOCK_401=1           — 401 fail-closed 강제
#   _CSGD_MOCK_429=1           — 429 fail-open 강제
#   _CSGD_MOCK_5XX=1           — 5xx 3-retry 강제
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (drift 없음 또는 drift 감지 + Issue auto-create 성공 — warning tier)
#   1 = (reserved, current scope 미사용)
#   2 = SETUP error (missing dependency / 401 auth / 5xx unrecoverable)
#
# Prior art: scripts/check-bypass-label-counter.sh (ADR-061 §결정 1 thin wrapper pattern)

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-kpi-infra-error] check-governance-drift: python3 not installed"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_governance_drift.py" "$@"
