#!/usr/bin/env bash
# scripts/check-stray-scratch-leak.sh
# stray-scratch-leak SessionStart 안전망 thin wrapper (CFP-2092)
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-stray-scratch-leak.sh
#
# BYPASS:
#   BYPASS_STRAY_SCRATCH_LEAK=1 — unconditional skip (hotfix-bypass family)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_stray_scratch_leak.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  # fail-open: SSOT 부재 시 exit 0 (advisory + repo-confinement 와 통일).
  echo "[check-stray-scratch-leak] WARNING: Python SSOT not found, check skipped (fail-open): ${PYTHON_SSOT}" >&2
  exit 0
fi

exec python3 "${PYTHON_SSOT}" "$@"
