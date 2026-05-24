#!/usr/bin/env bash
#
# measure-429-incident.sh — aggregate 429 incident markers from Story §14 Lane Evidence
# CFP-1354 / ADR-109 §결정 6 incident tracking policy
# Append to docs/kpi/429-incident.json + history.jsonl (idempotent weekly)
#
# Usage:
#   bash scripts/measure-429-incident.sh [--week YYYY-W##] [--repo-root <path>]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEEK=""
REPO_ROOT="."

# Parse named arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --week)
      WEEK="$2"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$WEEK" ]; then
  WEEK=$(date -u +%Y-W%V)
fi

python3 "$SCRIPT_DIR/lib/measure_429_incident.py" \
  --week "$WEEK" \
  --repo-root "$REPO_ROOT"
