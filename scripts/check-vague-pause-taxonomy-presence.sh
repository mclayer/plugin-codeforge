#!/usr/bin/env bash
# CFP-2573 / ADR-144 §결정 2/7 + ADR-025 Amendment 3 — vague-pause taxonomy presence lint (L1 방어층)
# ADR-061 §결정 1 — thin wrapper (scripts/lib/check_vague_pause_taxonomy_presence.py SSOT)
#
# 검사: archive/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md 에 vague-pause taxonomy 2 등재
#       (§결정 7 illegal 표 vague-pause 행 + §결정 10 policy_violation_vague_pause subclass)의 회귀 방어.
# Usage / exit code / semantics 상세: scripts/lib/check_vague_pause_taxonomy_presence.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_vague_pause_taxonomy_presence.py" "$@"
