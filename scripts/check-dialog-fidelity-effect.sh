#!/usr/bin/env bash
# CFP-833 Phase 2 — DialogFidelityAgent effectiveness measurement (ADR-071 Amendment 3)
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_dialog_fidelity_effect.py SSOT)
# Usage / exit code / semantics 상세: scripts/lib/check_dialog_fidelity_effect.py header.
#
# proxy signal qualification: advisory operational signal only, not causal effectiveness measure.
# warning tier — advisory dashboard, no PR block.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_dialog_fidelity_effect.py" "$@"
