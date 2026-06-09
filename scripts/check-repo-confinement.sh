#!/usr/bin/env bash
# scripts/check-repo-confinement.sh
# repo-confinement PreToolUse(Bash) guard thin wrapper (CFP-2092)
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-repo-confinement.sh   # stdin = PreToolUse JSON payload
#
# BYPASS:
#   BYPASS_REPO_CONFINEMENT=1 — unconditional skip (hotfix-bypass family)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_repo_confinement.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-repo-confinement] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
