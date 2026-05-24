#!/usr/bin/env bash
# scripts/check-mcp-token-freshness.sh
# CFP-1366 / ADR-073 Amendment 8 — MCP token freshness pre-check thin wrapper
#
# ADR-061 thin wrapper convention — POSIX dispatch only, Python SSOT 호출.
#
# Usage:
#   bash scripts/check-mcp-token-freshness.sh --input-file <path>
#   bash scripts/check-mcp-token-freshness.sh --text "..."
#
# BYPASS:
#   BYPASS_MCP_TOKEN_FRESHNESS=1 — unconditional skip
#
# Evidence-checks-registry entry: mcp-token-freshness-precheck

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_mcp_token_freshness.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-mcp-token-freshness] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
