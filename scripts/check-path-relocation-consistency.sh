#!/usr/bin/env bash
# scripts/check-path-relocation-consistency.sh — relocation-ledger 구동 dead-path 재유입 차단 lint thin wrapper
#
# CFP-2661 / ADR-136 Amendment 4 §결정 15 (22번째 warning-tier entry) — 게이트 execution-surface construct
#   (shell array / python literal / yaml sequence)가 relocation-ledger(docs/path-relocation-ledger.yaml)
#   등록 (old→new) pair 의 OLD 경로를 NEW 동반 없이 단독 지목(dead-path 재유입)하는지 construct-scoped 정적
#   스캔. census 3-count(candidates_scanned/inert_skipped/violations) + verdict fail-open/census fail-closed
#   비대칭 + active_when field-predicate selector + born-safe. ADR-119 게이트=ground-truth 정합.
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_path_relocation_consistency.py header.
#   bash scripts/check-path-relocation-consistency.sh [--repo-root DIR] [--ledger PATH] [--baseline PATH]
#     0 = PASS (new violation 0, candidate ≥ 1) / 1 = FLAG 1+ (warning) / 2 = usage·ledger 오류
#     / 3 = census fail-closed (candidate 0 = born-hollow guard).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-path-relocation-consistency-infra-error] check-path-relocation-consistency: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_path_relocation_consistency.py" "$@"
