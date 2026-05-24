#!/usr/bin/env bash
# scripts/check-stale-local-main-checkout.sh
# stale-local-main-checkout divergence check thin wrapper (CFP-1410 Phase 2 / ADR-073 Amendment 7+9)
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-stale-local-main-checkout.sh
#
# BYPASS:
#   BYPASS_STALE_LOCAL_MAIN_CHECKOUT=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: stale-local-main-checkout-divergence-check (ADR-073 Amendment 9)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_stale_local_main_checkout.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-stale-local-main-checkout] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
