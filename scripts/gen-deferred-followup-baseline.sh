#!/usr/bin/env bash
# scripts/gen-deferred-followup-baseline.sh — deferred-followup baseline generator thin bash wrapper
#
# CFP-2591 Phase 2 / ADR-060 §결정 6 — docs/deferred-followup-baseline.yaml single writer
#   (generate / prune). baseline 수기 편집 금지 — 반드시 본 tool 로 생성.
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/gen-deferred-followup-baseline.sh generate [--repo-root <p>] [--registry <p>] [--out <p>]
#   bash scripts/gen-deferred-followup-baseline.sh prune    [--repo-root <p>] [--baseline <p>]
#
# Exit codes:
#   0 = generated / pruned
#   2 = SETUP error (registry 부재 / baseline malformed / python3 미설치)
#
# Prior art: scripts/check-deferred-followup-reconcile.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-evidence-registry-infra-error] gen-deferred-followup-baseline: python3 not installed"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/gen_deferred_followup_baseline.py" "$@"
