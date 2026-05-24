#!/usr/bin/env bash
# scripts/check-subagent-sibling-story-polling.sh
# CFP-1366 / ADR-073 Amendment 6 — Subagent sibling Story polling thin wrapper
#
# ADR-061 thin wrapper convention — POSIX dispatch only, Python SSOT 호출.
#
# Usage:
#   bash scripts/check-subagent-sibling-story-polling.sh --input-file <path>
#   bash scripts/check-subagent-sibling-story-polling.sh --text "..." --own-cfp CFP-1366
#
# BYPASS:
#   BYPASS_SUBAGENT_SIBLING_STORY_POLLING=1 — unconditional skip
#
# Evidence-checks-registry entry: subagent-sibling-story-polling-evidence

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_subagent_sibling_story_polling.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-subagent-sibling-story-polling] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
