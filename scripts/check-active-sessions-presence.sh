#!/usr/bin/env bash
# scripts/check-active-sessions-presence.sh — Story active_sessions presence PR-time lint thin wrapper
#
# CFP-2761 §5.2 / ADR-085 §결정8 — 멀티세션 협업 프로토콜(ADR-085)의 active_sessions[] 소유 기록이
#   Story 산출물에 존재하는지 PR 시점(committed-content observable)에 검사한다. frontmatter
#   active_sessions 키 OR 본문 <!-- active_sessions --> 블록 부재 시 warn. warning tier (PR 무차단).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_active_sessions_presence.py header.
#   bash scripts/check-active-sessions-presence.sh --repo-root DIR [--files STORY.md ...]
#     0 = clean / warning finding / zero-target honest no-op (advisory)
#     2 = usage error
#     3 = born-hollow (repo-root 부재/dir 아님)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-active-sessions-presence-infra-error] check-active-sessions-presence: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_active_sessions_presence.py" "$@"
