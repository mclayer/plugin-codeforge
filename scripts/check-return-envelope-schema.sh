#!/usr/bin/env bash
# scripts/check-return-envelope-schema.sh — return-envelope-v1 문서 well-formed lint (thin wrapper)
#
# CFP-2572 Phase 2 / ADR-142 §결정 3 — [measurement] 문서 well-formed 검증 (schema file-lint).
#   runtime 반환 준수 강제 아님 (fix-event-v1 이 문서 schema 인 것과 동형). block/deny/강제 언어 0.
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-return-envelope-schema.sh check [--ldoc-path <p>] [--manifest-path <p>] [--repo-root <p>]
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS / 1 = violation (warning, 비차단 advisory) / 2 = SETUP error (파일 부재 / python3 미설치)
#
# Prior art: scripts/check-spawn-event-schema.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-return-envelope-lint-setup-error] check-return-envelope-schema: python3 not installed"
  exit 2
}

if [ "$#" -eq 0 ]; then
  set -- check
fi

exec python3 "${_SCRIPT_DIR}/lib/check_return_envelope_schema.py" "$@"
