#!/usr/bin/env bash
# CFP-508 / ADR-060 Amendment 7 / §결정 20 — evidence-checks-registry entry name ↔ workflow
# file naming convention lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_evidence_registry_naming.py SSOT)
# Usage / exit code / semantics 상세: scripts/lib/check_evidence_registry_naming.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    sed -n '2,/^[^#]/{ /^[^#]/q; s/^# \?//; p }' "$0"
    exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "check-evidence-registry-naming: python3 미설치 (meta-error)" >&2
    exit 2
fi

exec python3 "$SCRIPT_DIR/lib/check_evidence_registry_naming.py" "$@"
