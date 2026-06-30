#!/usr/bin/env bash
# scripts/check-fix-replay-disposition.sh
# CFP-2480 (Epic CFP-2476 E3) — FIX ground-truth replay close-gate disposition thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-fix-replay-disposition.sh <fixture.json>   # 파일 인자
#   echo '<json>' | bash scripts/check-fix-replay-disposition.sh  # stdin
#
# Output:
#   stdout: JSON {"dispositions": [{"id","disposition"}], "provenance": {...}}
#   exit:   0 = 닫기 거부 trigger 없음 (PASS / replay-impossible / undetermined / fail-open)
#           1 = falsified 1+ (close 거부 검출 — 보류 계열 신호)
#           2 = SETUP error (python3 미설치 / 입력 malformed / replay-impossible reason 부재)
#
# Prior art: scripts/check-merge-gate-disposition.sh / scripts/check-mutation-disposition.sh (ADR-061 thin wrapper).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/fix_replay_disposition.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-fix-replay-disposition] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

command -v python3 >/dev/null 2>&1 || {
  echo "[check-fix-replay-disposition] ERROR: python3 not installed" >&2
  exit 2
}

exec python3 "${PYTHON_SSOT}" "$@"
