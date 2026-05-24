#!/usr/bin/env bash
# CFP-1495 / ADR-103 §결정 1 영역 — Confluence-mirror drift detection (MCP-direct staleness check)
#
# Thin wrapper around scripts/lib/check_confluence_drift.py (ADR-061 §결정 1 + Amendment 1).
# Python SSOT — heredoc/inline 금지, multi-line logic 외부 .py split.
#
# Usage: bash scripts/check-confluence-drift.sh
#
# Test override env (6종):
#   CFP1495_IA_TREE_PATH=<path>           — IA tree schema location override (default: docs/confluence-ia-tree.yaml)
#   CFP1495_DRIFT_THRESHOLD_DAYS=<int>    — staleness threshold (default: 7)
#   CFP1495_SKIP_ISSUE_CREATE=1           — Issue auto-create 차단 (dry-run / TC mode)
#   CFP1495_MOCK_MODE=1                   — synthetic mock mode (no REST call)
#   CFP1495_MOCK_DRIFT_FIXTURE=<path>     — synthetic Confluence response JSON
#   CFP1495_API_MOCK_401=1                — 401 fail-closed 강제
#   CFP1495_API_MOCK_429=1                — 429 fail-open 강제
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (drift 없음 또는 drift 감지 + Issue auto-create 성공 — warning tier)
#   1 = (reserved, current scope 미사용)
#   2 = SETUP error (missing dependency / IA tree schema 부재 / 401 auth fail)
#
# Signature dedup: sha256("<page_id>|<drift_type>") | head -c 16
# active drift Issue body 안 "signature: <sig>" substring 포함 의무.
#
# MCP-direct deviation (ADR-103 §결정 1 mark engine path 미활성 영역):
#   - ATLASSIAN_API_TOKEN 부재 시 silent skip per page (warning emit, exit 0)
#   - mark engine path #1320 활성 후 REST API 자동 호출 영역으로 확장
#   - 3-anchor stamp 부착 영역 = exempt (mark engine path 활성 영역 정합)

set -euo pipefail

# --- Setup verify ---
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || {
  echo "[codeforge-kpi-infra-error] check-confluence-drift: python3 (or python) not installed" >&2
  exit 2
}

PY_BIN="python3"
command -v python3 >/dev/null 2>&1 || PY_BIN="python"

_SCRIPT_DIR_CONF="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PY_SSOT="${_SCRIPT_DIR_CONF}/lib/check_confluence_drift.py"

if [[ ! -f "$PY_SSOT" ]]; then
  echo "[codeforge-kpi-infra-error] check-confluence-drift: Python SSOT not found: $PY_SSOT" >&2
  exit 2
fi

# Delegate to Python SSOT (all logic, env handling, exit code mapping)
exec "$PY_BIN" "$PY_SSOT" "$@"
