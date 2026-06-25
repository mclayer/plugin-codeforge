#!/usr/bin/env bash
# check-bypass-justification-marker.sh
# CFP-845 / ADR-024 Amendment 8 §결정 6.A.4
#
# Thin bash wrapper — ADR-061 정합 (Python entry-point + thin wrapper 분리).
#
# Usage: bash scripts/check-bypass-justification-marker.sh [--dry-run] [--repo OWNER/REPO]
#                                                          [--pr-number N]
set -euo pipefail
exec python3 "$(dirname "$0")/check-bypass-justification-marker.py" "$@"
