#!/usr/bin/env bash
# scripts/check-active-sessions-presence.sh
# CFP-1057 / ADR-085 §결정 2 — active_sessions[] field presence-grep thin wrapper
#
# ADR-061 thin wrapper convention: POSIX dispatch only → Python SSOT 호출.
#
# Usage:
#   bash scripts/check-active-sessions-presence.sh --story-file <path>
#   bash scripts/check-active-sessions-presence.sh --issue-body <text>
#
# BYPASS:
#   BYPASS_ACTIVE_SESSIONS_PRESENCE=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: active-sessions-presence (ADR-085 §결정 2)

set -euo pipefail

if [[ "${BYPASS_ACTIVE_SESSIONS_PRESENCE:-0}" == "1" ]]; then
  echo "::warning::active-sessions-presence skipped (BYPASS_ACTIVE_SESSIONS_PRESENCE=1)"
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/lib/check_active_sessions_presence.py" "$@"
