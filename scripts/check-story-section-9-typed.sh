#!/usr/bin/env bash
# CFP-410 — Story §9 sub-section yaml block schema validation
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_story_section_9_typed.py SSOT)
#
# trap_priority: set -uo pipefail (non-strict, warning tier — never fail)
# Usage / exit code / semantics 상세: scripts/lib/check_story_section_9_typed.py header.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SCRIPT_DIR/../docs/stories" ]; then
  echo "info docs/stories not present - skip"
  exit 0
fi

[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_story_section_9_typed.py" "$@"
