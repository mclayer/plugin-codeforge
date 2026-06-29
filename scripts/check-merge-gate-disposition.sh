#!/usr/bin/env bash
# scripts/check-merge-gate-disposition.sh
# CFP-2458 Phase 2 — merge-time 적대적 반증 게이트 disposition thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-merge-gate-disposition.sh <fixture.json>   # 파일 인자
#   echo '<json>' | bash scripts/check-merge-gate-disposition.sh  # stdin
#
# Output:
#   stdout: JSON {"disposition": "...", "provenance": {...}}
#   exit:   0 = PASS / DEGRADED_PASS (통과 계열)
#           1 = BLOCKED / FAIL_CLOSED (보류 계열)
#           2 = SETUP error (python3 미설치 / 입력 malformed)
#
# Prior art: scripts/check-parallel-work-sentinel.sh / scripts/check-lane-count-ssot.sh (ADR-061 thin wrapper).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_merge_gate_disposition.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-merge-gate-disposition] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

command -v python3 >/dev/null 2>&1 || {
  echo "[check-merge-gate-disposition] ERROR: python3 not installed" >&2
  exit 2
}

exec python3 "${PYTHON_SSOT}" "$@"
