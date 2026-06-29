#!/usr/bin/env bash
# scripts/check-mutation-disposition.sh
# CFP-2464 Phase 2 — mutation peer (touchpoint #8) surviving-mutant disposition thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-mutation-disposition.sh <fixture.json>   # 파일 인자
#   echo '<json>' | bash scripts/check-mutation-disposition.sh  # stdin
#
# Output:
#   stdout: JSON {"dispositions": [...], "provenance": {...}}
#   exit:   0 = hollow_gate_verified 0건 (차단 trigger 없음 — undetermined/reject/clean/fail-open)
#           1 = hollow_gate_verified 1+ (재현된 hollow-gate 검출)
#           2 = SETUP error (python3 미설치 / 입력 malformed)
#
# Prior art: scripts/check-merge-gate-disposition.sh (CFP-2458 — ADR-061 thin wrapper).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_mutation_disposition.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-mutation-disposition] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

command -v python3 >/dev/null 2>&1 || {
  echo "[check-mutation-disposition] ERROR: python3 not installed" >&2
  exit 2
}

exec python3 "${PYTHON_SSOT}" "$@"
