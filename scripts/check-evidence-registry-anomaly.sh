#!/usr/bin/env bash
# CFP-442 / ADR-060 Amendment 11 §결정 25 — evidence-registry inventory anomaly lint thin wrapper.
# Usage / exit code / semantics 상세: scripts/lib/check_evidence_registry_anomaly.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_evidence_registry_anomaly.py" "$@"
