#!/usr/bin/env bash
# CFP-33 (ζ arc F2) — Label registry ↔ bootstrap-labels.sh sync check
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_label_registry.py SSOT)
#
# 검사: label-registry-v*.md ↔ bootstrap-labels.sh --dry-run 양방향 sync
# Usage / exit code / semantics 상세: scripts/lib/check_label_registry.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_label_registry.py" "$@"
