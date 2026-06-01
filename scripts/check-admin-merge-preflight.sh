#!/usr/bin/env bash
# check-admin-merge-preflight.sh
# CFP-1564 / ADR-113 Wave 2 mechanical wire — admin-merge pre-flight gate (thin wrapper).
# See scripts/lib/check_admin_merge_preflight.py for SSOT logic.
#
# ADR-113 §결정 1 — Orchestrator `gh pr merge --admin <PR>` attempt 직전 5-step pre-flight gate.
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (Python SSOT).
# Tier: warning (ADR-060 §결정 5 default — gate-block 시에도 exit 0, advisory).
#       단 fail-1 API call failure (gh 미설치/실행불가) = exit 2 meta-error.
# Bypass: hotfix-bypass:admin-merge-preflight-gate label (ADR-024 Amendment 6/8 §결정 6.A 5 lint chain 자동 covered).
# Requires: gh CLI authenticated (read-only: gh pr checks / gh pr view).
#
# Usage:
#   bash scripts/check-admin-merge-preflight.sh --pr <N> [--story CFP-NNN] [--head-sha SHA]
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — gate verdict 도달 (ALLOW / ABORT / STOP — warning-tier)
#   2 — meta-error (gh CLI 미설치 / fail-1 API call failure)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
  sed -n '2,/^set -euo/{ /^set -euo/q; s/^# \?//; p }' "$0"
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[admin-merge-preflight] python3 미설치 (meta-error)" >&2
  exit 2
fi

exec python3 "${SCRIPT_DIR}/lib/check_admin_merge_preflight.py" "$@"
