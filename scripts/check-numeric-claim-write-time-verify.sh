#!/usr/bin/env bash
# scripts/check-numeric-claim-write-time-verify.sh
# CFP-1612 / ADR-082 Amendment 25 sub-scope 1-N — numeric claim write-time verify thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-numeric-claim-write-time-verify.sh --story-file=<path>
#   bash scripts/check-numeric-claim-write-time-verify.sh --change-plan=<path>
#   bash scripts/check-numeric-claim-write-time-verify.sh --mode=audit --story-file=<path>
#   bash scripts/check-numeric-claim-write-time-verify.sh --mode=strict --story-file=<path>
#
# BYPASS:
#   BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: numeric-claim-write-time-verify (ADR-082 Amendment 25 sub-scope 1-N)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_numeric_claim_write_time.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-numeric-claim-write-time-verify] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
