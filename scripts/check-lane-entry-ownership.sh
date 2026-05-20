#!/usr/bin/env bash
# scripts/check-lane-entry-ownership.sh
# CFP-1057 / ADR-085 §결정 3 — lane-entry sentinel ownership verify thin wrapper
#
# ADR-061 thin wrapper convention: POSIX dispatch only → Python SSOT 호출.
#
# Usage:
#   bash scripts/check-lane-entry-ownership.sh --branch <branch-name> [--repo <owner/repo>]
#
# BYPASS:
#   BYPASS_LANE_ENTRY_OWNERSHIP=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: lane-entry-ownership-verify (ADR-085 §결정 3)

set -euo pipefail

if [[ "${BYPASS_LANE_ENTRY_OWNERSHIP:-0}" == "1" ]]; then
  echo "::warning::lane-entry-ownership-verify skipped (BYPASS_LANE_ENTRY_OWNERSHIP=1)"
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/lib/check_lane_entry_ownership.py" "$@"
