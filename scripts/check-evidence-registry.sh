#!/usr/bin/env bash
# CFP-455 / ADR-060 Amendment 2 §결정 14 — evidence-registry schema mechanical validation thin wrapper.
# CFP-455 FIX iter 1 / ADR-061 §결정 1 정합 — heredoc multi-line Python 외부 .py split (scripts/lib/check_evidence_registry.py SSOT).
# Usage / exit code / semantics 상세: scripts/lib/check_evidence_registry.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_evidence_registry.py" "$@"
