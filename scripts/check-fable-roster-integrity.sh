#!/usr/bin/env bash
# scripts/check-fable-roster-integrity.sh — fable tier roster-integrity 게이트 thin bash wrapper
#
# CFP-2803 Phase 2 §8 — 10 agents model: fable 정확 확보 + SecurityTestPL opus 유지 +
#   배포 census 41개 (haiku 7 / sonnet 10 / fable 10 / opus 14).
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-fable-roster-integrity.sh [--repo-root <path>] [--self-test]
#
# Exit codes (fail-closed):
#   0 = PASS
#   1 = FAIL (violations detected)
#   2 = SETUP error (python3 not found / setup failure)
#

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Windows/MSYS robustness: pwd yields MSYS form (/c/...) which native python.exe
# misreads as drive-relative (C:\c\...). Convert to a Windows path when cygpath exists.
# No-op on Linux CI (cygpath absent) — house thin-wrapper behavior preserved (ADR-061).
if command -v cygpath >/dev/null 2>&1; then _SCRIPT_DIR="$(cygpath -w "$_SCRIPT_DIR")"; fi

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-fable-roster-integrity: python3 not installed (exit 2)."
  exit 2
}

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_fable_roster_integrity.py" "$@"
