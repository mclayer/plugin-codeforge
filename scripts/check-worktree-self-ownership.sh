#!/usr/bin/env bash
# scripts/check-worktree-self-ownership.sh
# CFP-1366 / ADR-073 Amendment 3 — Worktree self-ownership verify thin wrapper
#
# ADR-061 thin wrapper convention — POSIX dispatch only, Python SSOT 호출.
#
# Usage:
#   bash scripts/check-worktree-self-ownership.sh --input-file <path>
#   bash scripts/check-worktree-self-ownership.sh --text "<inline text>"
#
# BYPASS:
#   BYPASS_WORKTREE_SELF_OWNERSHIP=1 — unconditional skip
#
# Evidence-checks-registry entry: worktree-self-ownership-verify

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_worktree_self_ownership.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-worktree-self-ownership] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
