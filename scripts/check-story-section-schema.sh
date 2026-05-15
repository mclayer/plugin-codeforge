#!/usr/bin/env bash
# CFP-91 (CFP-84 follow-up) — Story file section schema lint
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_story_section_schema.py SSOT)
# mode_preserve: 100755
#
# Validates docs/stories/*.md against templates/story-page-structure.md schema.
# Usage / exit code / semantics 상세: scripts/lib/check_story_section_schema.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SCRIPT_DIR/../docs/stories" ]; then
  echo "ℹ️  docs/stories/ 부재 — lint skip (plugin repo or pre-init consumer)"
  exit 0
fi

[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_story_section_schema.py" "$@"
