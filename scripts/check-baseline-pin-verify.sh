#!/usr/bin/env bash
# scripts/check-baseline-pin-verify.sh
# baseline_pin field presence + freshness check thin wrapper (CFP-1410 Phase 2 / ADR-073 Amendment 9)
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-baseline-pin-verify.sh <story-file-path>
#
# BYPASS:
#   BYPASS_BASELINE_PIN_VERIFY=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: stale-local-main-checkout-divergence-check (ADR-073 Amendment 9)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_baseline_pin_verify.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-baseline-pin-verify] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
