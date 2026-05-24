#!/usr/bin/env bash
#
# measure-429-incident.sh — aggregate 429 incident markers from Story §14 Lane Evidence
# CFP-1354 / ADR-109 §결정 6 incident tracking policy
# Append to docs/kpi/429-incident.json + history.jsonl (idempotent weekly)
#
# Usage:
#   bash scripts/measure-429-incident.sh \
#     [--week YYYY-W##] [--as-of YYYY-MM-DD] \
#     [--out <path>] [--history-out <path>] [--repo-root <path>]
#
# CFP-1354 FIX iter 3 — workflow → bash → python 5-flag handshake contract.
# Unknown flags rejected with exit 2 (P2 #4 input-validation).
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEEK=""
AS_OF=""
OUT_FILE=""
HISTORY_OUT=""
REPO_ROOT="."

# Parse named arguments — reject unknown flags (P2 #4 input-validation)
while [ $# -gt 0 ]; do
  case "$1" in
    --week)
      WEEK="$2"
      shift 2
      ;;
    --as-of)
      AS_OF="$2"
      shift 2
      ;;
    --out)
      OUT_FILE="$2"
      shift 2
      ;;
    --history-out)
      HISTORY_OUT="$2"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="$2"
      shift 2
      ;;
    *)
      echo "Unknown flag: $1" >&2
      exit 2
      ;;
  esac
done

# Build argv for Python collector — forward all 5 flags
PY_ARGS=()
if [ -n "$WEEK" ]; then
  PY_ARGS+=(--week "$WEEK")
fi
if [ -n "$AS_OF" ]; then
  PY_ARGS+=(--as-of "$AS_OF")
fi
if [ -n "$OUT_FILE" ]; then
  PY_ARGS+=(--out "$OUT_FILE")
fi
if [ -n "$HISTORY_OUT" ]; then
  PY_ARGS+=(--history-out "$HISTORY_OUT")
fi
PY_ARGS+=(--repo-root "$REPO_ROOT")

exec python3 "$SCRIPT_DIR/lib/measure_429_incident.py" "${PY_ARGS[@]}"
