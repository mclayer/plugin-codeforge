#!/usr/bin/env bash
# CFP-2478 / ADR-068 Amendment 7 — ADR cross-ref consistency lint (layer A, warning-tier)
# 5 검사: (a) cross-ADR 존재 / (b) phantom ID ownership / (c) enum SSOT / (d) 버전 opt-in / (e) content-anchor
# ADR-061 §결정 1 thin wrapper — 로직 SSOT: scripts/lib/check_adr_cross_ref_consistency.py
# Usage / exit code / semantics 상세: scripts/lib/check_adr_cross_ref_consistency.py header.
#
# hotfix-bypass: hotfix-bypass:boundary-wording (ADR-024 §결정 6.A per-entry namespace)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_adr_cross_ref_consistency.py" "$@"
