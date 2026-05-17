#!/usr/bin/env bash
# check-per-plugin-cumulative-counter.sh
# CFP-845 / ADR-024 Amendment 8 §결정 6.A.3
#
# Thin bash wrapper — ADR-061 정합 (Python entry-point + thin wrapper 분리).
#
# Usage: bash scripts/check-per-plugin-cumulative-counter.sh [--dry-run] [--repo OWNER/REPO]
#                                                             [--threshold N] [--plugin-name NAME]
set -euo pipefail
exec python3 "$(dirname "$0")/check-per-plugin-cumulative-counter.py" "$@"
