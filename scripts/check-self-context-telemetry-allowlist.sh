#!/usr/bin/env bash
# scripts/check-self-context-telemetry-allowlist.sh — self-context-v1 allow-list conformance lint (thin wrapper)
#
# CFP-2572 Phase 2 / ADR-142 §결정 4 / ADR-043 Amendment 3 — [measurement] allow-list conformance.
#   L7 record-only proxy — 게이트/block/deny 언어 0. runtime 강제 아님.
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-self-context-telemetry-allowlist.sh check [--contract-path <p>] [--repo-root <p>]
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS / 1 = violation (warning, 비차단 advisory) / 2 = SETUP error (파일 부재 / python3 미설치)
#
# Prior art: scripts/check-spawn-event-schema.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-self-context-lint-setup-error] check-self-context-telemetry-allowlist: python3 not installed"
  exit 2
}

if [ "$#" -eq 0 ]; then
  set -- check
fi

exec python3 "${_SCRIPT_DIR}/lib/check_self_context_telemetry_allowlist.py" "$@"
