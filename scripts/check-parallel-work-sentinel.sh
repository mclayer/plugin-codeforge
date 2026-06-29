#!/usr/bin/env bash
# scripts/check-parallel-work-sentinel.sh
# CFP-967 / ADR-073 Amendment 2 — Parallel work sentinel thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-parallel-work-sentinel.sh --mode=title-search
#   bash scripts/check-parallel-work-sentinel.sh --mode=epic-state-poll --epic-id=882
#   bash scripts/check-parallel-work-sentinel.sh --mode=head-compare-sibling-commits
#
# BYPASS:
#   BYPASS_PARALLEL_WORK_SENTINEL=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: parallel-work-sentinel-pickup (ADR-073 Amendment 2)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_parallel_work_sentinel.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-parallel-work-sentinel] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
