#!/usr/bin/env bash
# scripts/check-lane-entry-ownership.sh — lane-entry ownership verify thin wrapper
#
# CFP-2761 §5.2 / ADR-085 §결정3 + ADR-073 Amendment 2 (4th source) — lane 진입 4-step 소유 polling
#   (HOOK-ONLY, workflow:null). 진입 세션(--git-identity + --lane)의 active_sessions 소유 entry
#   (matching entry_phase) 존재 + 동일 lane 경합 concurrent 소유자 부재를 검증한다. --sessions-file
#   부재 시 live advisory no-op. warning tier (advisory).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_lane_entry_ownership.py header.
#   bash scripts/check-lane-entry-ownership.sh [--repo-root DIR] --lane NAME --git-identity ID \
#       [--sessions-file FILE]
#     0 = clean / warning finding / live advisory no-op (advisory)
#     2 = usage error (--lane/--git-identity 누락) OR sessions-file unparseable
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-lane-entry-ownership-infra-error] check-lane-entry-ownership: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_lane_entry_ownership.py" "$@"
