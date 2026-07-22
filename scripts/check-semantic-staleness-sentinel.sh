#!/usr/bin/env bash
# scripts/check-semantic-staleness-sentinel.sh
# CFP-2786 / Epic #2783 Child B — Semantic staleness sentinel thin wrapper (ADR-061)
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무). BYPASS 분기는 py 내부.
#
# Usage:
#   bash scripts/check-semantic-staleness-sentinel.sh --mode carrier-cross-match
#
# BYPASS:
#   BYPASS_SEMANTIC_STALENESS_SENTINEL=1 — unconditional skip (hotfix-bypass family)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_semantic_staleness_sentinel.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-semantic-staleness-sentinel] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
