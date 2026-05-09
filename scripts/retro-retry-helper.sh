#!/usr/bin/env bash
# retro-retry-helper.sh — reads retro-attempts.jsonl, outputs due retry entries
#
# Called by: templates/github-workflows/retro-mandatory.yml retry-state-machine job
# Usage:     retro-retry-helper.sh <jsonl-file> <current-epoch-seconds>
# Output:    newline-separated JSON objects of due retry entries (or empty if none due)
# Exit:      0 always
#
# Retry wait thresholds (ADR-045 §D-4 cumulative offset spec):
#   attempt_n=1 (first attempt completed, waiting for retry 1): 300s (5min)
#   attempt_n=2 (retry 1 completed, waiting for retry 2):       600s (10min)
#   attempt_n=3 (retry 2 completed, waiting for retry 3):       900s (15min)
#   attempt_n>=4: ESCALATE (handled by caller, not this script)
#
# Status filter: only in_flight or failed entries are considered.
#   success  → skip (gate:retro-complete already attached)
#   escalated → skip (already ESCALATE-commented by caller)
#
# Idempotency: called every 5min by cron — outputs same entries until state updated.

set -uo pipefail

JSONL_FILE="${1:-}"
CURRENT_EPOCH="${2:-}"

# Validate args
if [ -z "$JSONL_FILE" ] || [ -z "$CURRENT_EPOCH" ]; then
    echo "Usage: retro-retry-helper.sh <jsonl-file> <current-epoch-seconds>" >&2
    exit 0
fi

if [ ! -f "$JSONL_FILE" ]; then
    echo "::notice::retro-retry-helper: file not found: $JSONL_FILE" >&2
    exit 0
fi

# Wait thresholds per attempt_n (seconds until next retry is due)
wait_for_attempt() {
    local attempt_n="$1"
    case "$attempt_n" in
        1) echo 300 ;;    # attempt_n=1 → retry 1: 5min wait
        2) echo 600 ;;    # attempt_n=2 → retry 2: 10min wait
        3) echo 900 ;;    # attempt_n=3 → retry 3: 15min wait
        *) echo 0 ;;      # attempt_n>=4: always due (ESCALATE path, caller handles)
    esac
}

# ISO 8601 to epoch conversion (portable: handles Z suffix)
iso8601_to_epoch() {
    local ts="$1"
    # Normalize: replace Z with +00:00 for date -d / date -j compatibility
    ts="${ts%Z}"
    # GNU date (Linux)
    if date --version >/dev/null 2>&1; then
        date -d "${ts}Z" +%s 2>/dev/null || echo 0
    else
        # BSD date (macOS) — for local dev / testing
        date -j -f "%Y-%m-%dT%H:%M:%S" "$ts" "+%s" 2>/dev/null || echo 0
    fi
}

# Process each JSONL line
while IFS= read -r line; do
    [ -z "$line" ] && continue

    # Extract fields with python3 (available in ubuntu-latest GitHub Actions runner)
    STATUS=$(echo "$line" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('status',''))" 2>/dev/null || echo "")
    ATTEMPT_N=$(echo "$line" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('attempt_n', 0))" 2>/dev/null || echo "0")
    LAST_ATTEMPTED=$(echo "$line" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('last_attempted_at',''))" 2>/dev/null || echo "")

    # Skip non-actionable statuses
    if [ "$STATUS" = "success" ] || [ "$STATUS" = "escalated" ]; then
        continue
    fi

    # Only process in_flight or failed entries
    if [ "$STATUS" != "in_flight" ] && [ "$STATUS" != "failed" ]; then
        continue
    fi

    # Calculate elapsed time since last attempt
    LAST_EPOCH=$(iso8601_to_epoch "$LAST_ATTEMPTED")
    if [ "$LAST_EPOCH" -eq 0 ]; then
        echo "::warning::retro-retry-helper: failed to parse timestamp '$LAST_ATTEMPTED'" >&2
        continue
    fi

    ELAPSED=$(( CURRENT_EPOCH - LAST_EPOCH ))
    WAIT_REQUIRED=$(wait_for_attempt "$ATTEMPT_N")

    # Emit due entries
    if [ "$ELAPSED" -ge "$WAIT_REQUIRED" ]; then
        echo "$line"
    fi

done < "$JSONL_FILE"

exit 0
