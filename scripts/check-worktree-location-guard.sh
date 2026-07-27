#!/usr/bin/env bash
# scripts/check-worktree-location-guard.sh
# ① worktree 생성위치 PreToolUse(Bash) guard thin wrapper (CFP-2822, AC-10)
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출 (business logic 금지).
#
# Usage:
#   bash scripts/check-worktree-location-guard.sh   # stdin = PreToolUse JSON payload
#
# 판정 SSOT = scripts/lib/check_worktree_location_guard.py:
#   - payload JSON 판독(_read_input, 실패 시 {}) + `git worktree add <path>` target 추출
#   - is_nonstandard_location(cmd) + tier(WORKTREE_LOCATION_GUARD_TIER=warn|block, default=warn)
#     → exit 2(block) / stderr-warn+exit 0(warn)
#   - BYPASS_WORKTREE_LOCATION_GUARD=1 → skip + audit 한 줄 (repo-confinement 패턴)
#
# fail-open: SSOT/python 부재 시 exit 0. exit 2 는 PreToolUse 차단 신호라 lib deploy
#   누락 시 모든 Bash 명령 영구 차단(세션 brick) → 금지.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_worktree_location_guard.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[worktree-location-guard] WARNING: Python SSOT not found, guard skipped (fail-open): ${PYTHON_SSOT}" >&2
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "${PYTHON_SSOT}" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "${PYTHON_SSOT}" "$@"
fi
# python 부재 → fail-open (guard 미차단)
exit 0
