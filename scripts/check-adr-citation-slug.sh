#!/usr/bin/env bash
# CFP-2057 / ADR-060 — ADR citation slug lint (warning-tier)
# 2-layer: L1 slug-existence + L2 deny-list (ALLOWED_HUB_REPOS/SECURITY_PATHS 맥락 오인용 차단)
# ADR-061 §결정 1 thin wrapper — 로직 SSOT: scripts/lib/check_adr_citation_slug.py
# Usage / exit code / semantics 상세: scripts/lib/check_adr_citation_slug.py header.
#
# hotfix-bypass: hotfix-bypass:adr-citation-slug (ADR-024 §결정 6.A per-entry namespace)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_adr_citation_slug.py" "$@"
