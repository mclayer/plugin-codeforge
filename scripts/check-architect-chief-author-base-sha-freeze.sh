#!/usr/bin/env bash
# scripts/check-architect-chief-author-base-sha-freeze.sh
# CFP-1581 / ADR-073 Amendment 16 — ArchitectAgent chief author base SHA freeze thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-architect-chief-author-base-sha-freeze.sh --worktree-path=<path>
#   bash scripts/check-architect-chief-author-base-sha-freeze.sh --expected-files=<comma-list>
#   bash scripts/check-architect-chief-author-base-sha-freeze.sh --story-file=<path>
#
# BYPASS:
#   BYPASS_ARCHITECT_CHIEF_AUTHOR_BASE_SHA_FREEZE=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: architect-chief-author-base-sha-freeze-verify (ADR-073 Amendment 16)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_architect_chief_author_base_sha_freeze.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-architect-chief-author-base-sha-freeze] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
