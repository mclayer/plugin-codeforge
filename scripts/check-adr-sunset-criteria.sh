#!/usr/bin/env bash
# CFP-389 / ADR-060 / ADR-058 — ADR sunset criteria mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_adr_sunset_criteria.py SSOT)
# Usage / exit code / semantics 상세: scripts/lib/check_adr_sunset_criteria.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_adr_sunset_criteria.py" "$@"
