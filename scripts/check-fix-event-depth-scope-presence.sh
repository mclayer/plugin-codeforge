#!/usr/bin/env bash
# check-fix-event-depth-scope-presence.sh
# CFP-842 / ADR-067 Amendment 1 §결정 4 / ADR-060 §결정 5
#
# Thin bash wrapper — ADR-061 정합 (Python entry-point + thin wrapper 분리).
#
# Usage: bash scripts/check-fix-event-depth-scope-presence.sh <story-file-path>
set -euo pipefail
exec python3 "$(dirname "$0")/check-fix-event-depth-scope-presence.py" "$@"
