#!/usr/bin/env bash
# CFP-894 / ADR-060 §결정 6 — inter-plugin-contract MANIFEST↔frontmatter parity lint (warning tier)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (Python SSOT)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_inter_plugin_contracts_parity.py" "$@"
