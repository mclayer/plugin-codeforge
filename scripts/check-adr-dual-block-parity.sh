#!/usr/bin/env bash
# scripts/check-adr-dual-block-parity.sh
# CFP-1648 / ADR-082 Amendment 28 sub-scope 1-Q — ADR dual-block parity lint thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-adr-dual-block-parity.sh
#   bash scripts/check-adr-dual-block-parity.sh --mode=audit
#   bash scripts/check-adr-dual-block-parity.sh --mode=strict
#   bash scripts/check-adr-dual-block-parity.sh --adr-glob="docs/adr/ADR-082-*.md"
#
# BYPASS:
#   BYPASS_ADR_DUAL_BLOCK_PARITY=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: adr-dual-block-parity
# F-DR-001 P0 origin: frontmatter amendment_log[] body section missing despite frontmatter present

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_adr_dual_block_parity.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-adr-dual-block-parity] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
