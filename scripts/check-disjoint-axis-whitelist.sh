#!/usr/bin/env bash
# scripts/check-disjoint-axis-whitelist.sh — ADR-039 inline-whitelist static-integrity lint (thin wrapper)
#
# CFP-2572 Phase 2 / ADR-142 §결정 3 — [물리강제] ADR-integrity 정적 (유일 물리강제).
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-disjoint-axis-whitelist.sh check [--adr-path <p>] [--ldoc-path <p>] [--repo-root <p>]
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS
#   1 = violation (warning emit — workflow continue-on-error 로 비차단, advisory)
#   2 = SETUP error (ADR-039 / return-envelope-v1.md 부재 / python3 미설치)
#
# Prior art: scripts/check-spawn-event-schema.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-disjoint-axis-lint-setup-error] check-disjoint-axis-whitelist: python3 not installed"
  exit 2
}

# 인자 없으면 check 서브커맨드 default (workflow run: 본문 단순화)
if [ "$#" -eq 0 ]; then
  set -- check
fi

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_disjoint_axis_whitelist.py" "$@"
