#!/usr/bin/env bash
# scripts/check-numeric-claim-write-time-verify.sh
# CFP-1612 / ADR-082 Amendment 25 sub-scope 1-N — numeric claim write-time verify thin wrapper
# CFP-1647 / ADR-082 Amendment 27 sub-scope 1-P — PR commit msg + PR body scope flag passthrough
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
#   bash scripts/check-numeric-claim-write-time-verify.sh --scope pr-commit-msg --pr <PR_NUMBER>
#   bash scripts/check-numeric-claim-write-time-verify.sh --scope pr-body --pr <PR_NUMBER>
#
# BYPASS:
#   BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: numeric-claim-write-time-verify (ADR-082 Amendment 25 sub-scope 1-N)
# CFP-1647 scope expansion: --scope pr-commit-msg / pr-body passthrough via "$@" (ADR-061 §결정 11)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_numeric_claim_write_time.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-numeric-claim-write-time-verify] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
