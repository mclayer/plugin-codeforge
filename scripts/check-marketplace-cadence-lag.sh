#!/usr/bin/env bash
# scripts/check-marketplace-cadence-lag.sh — Arc B 발행 cadence lag detect thin bash wrapper
#
# CFP-2310 S3 (#2313) — main↔marketplace version drift 자동 감지 + Issue 자동생성 (advisory).
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# ★ scope (Epic #2310 U5): detect + alert only. 실 sync PR 자동생성 절대 금지.
#   marketplace 선행 merge ordering(ADR-063 §결정 2)은 Orchestrator 책임 유지 (ADR-063 Amd 12).
#
# Usage:
#   bash scripts/check-marketplace-cadence-lag.sh check [--repo-root <path>] [--dry-run]
#   bash scripts/check-marketplace-cadence-lag.sh check --marketplace-json <path> [...]  # test override
#   bash scripts/check-marketplace-cadence-lag.sh roster [--repo-root <path>]
#   bash scripts/check-marketplace-cadence-lag.sh signature --plugin <name> --direction <dir>
#
# Test override env:
#   MLD_SKIP_ISSUE_CREATE=1 / CBL_SKIP_ISSUE_CREATE=1  — Issue auto-create 차단 (dry-run / self-test)
#   MLD_MOCK_401=1 — 401 fail-closed 강제 / MLD_MOCK_429=1 — 429 fail-open 강제
#
# Exit codes (ADR-060 §결정 15 3-tier — warning tier):
#   0 = PASS (lag 0 / lag 감지 + Issue auto-create — advisory, 비차단)
#   2 = SETUP error (missing dependency / 401 auth / marketplace fetch 실패)
#
# Prior art: scripts/check-governance-drift.sh (ADR-061 §결정 1 thin wrapper pattern).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-cadence-infra-error] check-marketplace-cadence-lag: python3 not installed"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_marketplace_cadence_lag.py" "$@"
