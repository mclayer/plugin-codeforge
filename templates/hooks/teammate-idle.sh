#!/usr/bin/env bash
# CFP-137 — Teammate idle hook.
# Triggered when a teammate enters idle state.
# Use exit code 2 to nudge teammate back to work (e.g., if there are pending tasks).
#
# Env vars:
#   CLAUDE_TEAM_NAME       — team identifier (e.g., design / requirements)
#   CLAUDE_TEAMMATE_NAME   — teammate identifier (e.g., SecurityArch / OpRiskArch)
#
# Exit codes:
#   0 — allow idle (continue)
#   2 — block idle (teammate must continue working)

set -euo pipefail

TEAMMATE="${CLAUDE_TEAMMATE_NAME:-unknown}"
TEAM="${CLAUDE_TEAM_NAME:-unknown}"

echo "[teammate-idle] team=$TEAM teammate=$TEAMMATE entered idle state" >&2

# Optional: check task list for pending claims owned by this teammate.
# If 미완 task 발견:
#   echo "[teammate-idle] BLOCK: pending tasks detected, teammate should continue" >&2
#   exit 2

exit 0
