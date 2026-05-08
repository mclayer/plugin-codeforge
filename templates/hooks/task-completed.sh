#!/usr/bin/env bash
# CFP-137 — Task completed hook.
# Triggered when a task is marked complete.
# Use exit code 2 to reject completion (e.g., insufficient evidence).
# Use this hook for gate label attachment automation.
#
# Env vars:
#   CLAUDE_TASK_ID         — task identifier
#   CLAUDE_TASK_COMPLETOR  — teammate identifier who marked complete
#
# Exit codes:
#   0 — accept completion (continue)
#   2 — reject completion (evidence missing / gate not satisfied)

set -euo pipefail

TASK_ID="${CLAUDE_TASK_ID:-unknown}"
COMPLETOR="${CLAUDE_TASK_COMPLETOR:-unknown}"

echo "[task-completed] id=$TASK_ID completor=$COMPLETOR" >&2

# Optional: gate label attachment via gh api (e.g., gate:design-review-pass).
# Optional: Story §9 / §11 update trigger.
# Optional: evidence pack presence check (Change Plan / review log / test artifact).

exit 0
