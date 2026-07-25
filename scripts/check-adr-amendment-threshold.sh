#!/usr/bin/env bash
# CFP-2812 / ADR-NNN(adr-amendment-compaction-ratchet) / ADR-060 — ADR amendment 누적 임계 재제정 ratchet lint (warning mode)
# thin wrapper (scripts/lib/check_adr_amendment_threshold.py SSOT). Usage/exit/semantics 상세 = lib header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_adr_amendment_threshold.py" --mode threshold "$@"
