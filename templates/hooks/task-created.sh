#!/usr/bin/env bash
# CFP-137 — Task created hook.
# Triggered when a task is created in the shared task list.
# Use exit code 2 to reject creation (e.g., dependency cycle, invalid format).
#
# Env vars:
#   CLAUDE_TASK_ID            — task identifier
#   CLAUDE_TASK_TITLE         — task title (free-form)
#   CLAUDE_TASK_DEPENDENCIES  — comma-separated upstream task IDs
#
# Exit codes:
#   0 — allow creation (continue)
#   2 — reject creation (cycle / schema violation / ...)

set -euo pipefail

TASK_ID="${CLAUDE_TASK_ID:-unknown}"
TASK_TITLE="${CLAUDE_TASK_TITLE:-unknown}"
DEPS="${CLAUDE_TASK_DEPENDENCIES:-}"

echo "[task-created] id=$TASK_ID title=\"$TASK_TITLE\" deps=$DEPS" >&2

# Optional: dependency cycle check (compare DEPS against task list graph).
# Optional: schema validation (id format, title length, ...).

exit 0
