#!/usr/bin/env bash
# scripts/check-audit-comment-author.sh — hotfix-bypass audit comment author-verify lint thin bash wrapper
#
# CFP-2591 Phase 2 / ADR-060 §결정 6 — audit-tagged comment ([hotfix-bypass-audit] ...) 의
#   author.login 이 github-actions[bot] 인지 검증 (bot→PASS / human→FAIL / absent→FAIL).
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-audit-comment-author.sh check [--comments-json <path>]   # 없으면 stdin
#   bash scripts/check-audit-comment-author.sh selftest                          # 5 embedded case
#
# Exit codes:
#   0 = PASS (tagged ≥1 AND 전부 bot) / selftest 5/5
#   1 = FAIL (absent / human-spoof) / selftest 불일치
#   2 = SETUP error (JSON parse 실패 / python3 미설치)
#
# Prior art: scripts/check-deferred-followup-reconcile.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-audit-comment-author-infra-error] check-audit-comment-author: python3 not installed"
  exit 2
}

# 인자 없으면 check 서브커맨드 default
if [ "$#" -eq 0 ]; then
  set -- check
fi

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_audit_comment_author.py" "$@"
