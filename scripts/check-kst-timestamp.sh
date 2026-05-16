#!/usr/bin/env bash
# CFP-771 / ADR-079 Amendment 1 — KST timestamp display mechanical lint (warning mode)
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_kst_timestamp.py SSOT)
# Usage / exit code / semantics 상세: scripts/lib/check_kst_timestamp.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_kst_timestamp.py" "$@"
