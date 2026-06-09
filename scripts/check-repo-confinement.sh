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
  # fail-open: SSOT 부재 시 exit 0 (가드 best-effort 철학). exit 2 면 PreToolUse
  # 차단 신호라 lib deploy 누락 시 모든 Bash 명령 영구 차단(세션 brick) → 금지.
  echo "[check-repo-confinement] WARNING: Python SSOT not found, guard skipped (fail-open): ${PYTHON_SSOT}" >&2
  exit 0
fi

exec python3 "${PYTHON_SSOT}" "$@"
