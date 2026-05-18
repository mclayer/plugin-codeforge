#!/usr/bin/env bash
# CFP-923 / ADR-078 P-S4 mechanism — architecture-drift mechanical lint (warning mode)
# ADR-061 §결정 1 — thin wrapper (scripts/lib/check_architecture_drift.py SSOT)
# Usage / exit code / semantics 상세: scripts/lib/check_architecture_drift.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_architecture_drift.py" "$@"
