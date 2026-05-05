#!/usr/bin/env bash
# userprompt-reminder.sh — UserPromptSubmit hook (변경 착수 reminder inject).
#
# CFP-104 (Phase 2b of CFP-96 Epic) — Python core thin wrapper.
# Implementation SSOT: userprompt_reminder.py (cross-platform).
#
# Skip 조건 (silent):
#   - python3 부재
#   - userprompt_reminder.py 부재

set -u

if ! command -v python3 >/dev/null 2>&1; then
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CORE="$SCRIPT_DIR/userprompt_reminder.py"

if [ ! -f "$PYTHON_CORE" ]; then
    exit 0
fi

python3 "$PYTHON_CORE"
exit 0  # always non-blocking
