#!/usr/bin/env bash
# CFP-785 / ADR-077 §결정 3 — design-reading 깊이 강화 mandate mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (Python SSOT)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_adr_077_design_reading_mandate.py" "$@"
