#!/usr/bin/env bash
# scripts/check-deferred-item-recovery.sh — deferred follow-up 회수 게이트 thin bash wrapper
#
# CFP-2470 / ADR-128 Amendment 1 — no-silent-drop 게이트 (warning tier, advisory).
#   retro/Story 서사의 narrative-recorded deferred 각각이 (추적 Issue 전환) OR
#   (관찰-only + 사유 명시) 중 하나로 명시 판정됐는지 검사. silent drop 만 차단.
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-deferred-item-recovery.sh <retro-file> [<retro-file> ...]
#
# cross-repo PAT graceful skip (EC-2, ADR-066): CODEFORGE_CROSS_REPO_PAT → GH_TOKEN env.
#   미설정 시 Python SSOT 가 ::warning + exit 0 (graceful, hard-block 아님).
#
# Exit codes (ADR-060 §결정 5 3-tier — warning tier):
#   0 = PASS (WARN 0) / graceful skip (PAT 부재)
#   1 = WARN 1+ (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
#   2 = SETUP error (입력 파일 전부 부재 / python3 미설치)
#
# Prior art: scripts/check-deferred-followup-reconcile.sh / scripts/check-governance-drift.sh
#   (ADR-061 thin wrapper convention).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-evidence-registry-infra-error] check-deferred-item-recovery: python3 not installed"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_deferred_item_recovery.py" "$@"
