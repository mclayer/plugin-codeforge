#!/usr/bin/env bash
# CFP-2491 / Epic CFP-2481 E3b / ADR-133 §결정2 — ADR-RESERVATION 번호 atomic claim (단일-셀 OCC)
# ADR-061 §결정6 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/adr-reservation-atomic-claim.py SSOT)
# Usage / 인터페이스 / OCC semantics 상세: scripts/lib/adr-reservation-atomic-claim.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/lib/adr-reservation-atomic-claim.py" "$@"
