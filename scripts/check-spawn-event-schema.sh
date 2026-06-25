#!/usr/bin/env bash
# scripts/check-spawn-event-schema.sh — spawn-event-v1 schema lint thin bash wrapper
#
# CFP-2393 Phase 2 / Epic CFP-2391 S3 — spawn-event-v1 registry schema validation.
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
# OMC MIT 차용 (oh-my-claudecode).
#
# Usage:
#   bash scripts/check-spawn-event-schema.sh check [--contract-path <path>] [--repo-root <path>]
#
# Exit codes (ADR-060 §결정 15 3-tier — warning tier):
#   0 = PASS
#   1 = schema validation failure (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
#   2 = SETUP error (spawn-event-v1.md 부재 / yaml parse 실패 / python3 미설치)
#
# Prior art: scripts/check-deferred-followup-reconcile.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-evidence-registry-infra-error] check-spawn-event-schema: python3 not installed"
  exit 2
}

# 인자 없으면 check 서브커맨드 default (workflow run: 본문 단순화)
if [ "$#" -eq 0 ]; then
  set -- check
fi

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_spawn_event_schema.py" "$@"
