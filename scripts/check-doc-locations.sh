#!/usr/bin/env bash
# CFP-276 — Doc Location Registry validator (issue #276)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_doc_locations.py SSOT)
#
# Modes:
#   default  — validation only (6 checks)
#   --regen  — regenerate docs/doc-location-registry.md from docs/doc-locations.yaml
#   --check-freshness — round-trip diff (regen to /tmp + diff against committed)
#   --full   — validation + freshness check (CI default)
#
# SSOT: docs/doc-locations.yaml + ADR-038
# Usage / exit code / semantics 상세: scripts/lib/check_doc_locations.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."   # CFP-1408 — always cd (msys2 absolute POSIX→Windows path conversion 회피, relative path 전달)
export DOC_LOC_MODE="${1:-default}"
exec python3 "scripts/lib/check_doc_locations.py" "$@"
