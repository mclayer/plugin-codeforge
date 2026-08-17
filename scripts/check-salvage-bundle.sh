#!/usr/bin/env bash
# scripts/check-salvage-bundle.sh — salvage 번들 · side-effect 원장 · 착지 직전 스캔 thin wrapper
#
# CFP-2984 Phase 2 — ADR-179(salvage 번들 인계) 실배선. 번들 스키마 하한·allowlist 상한 검증,
#   조각 usable|suspect 태깅 fail-closed, side-effect intent dedup(canonical sha256),
#   저장 실패 시 재시도 0 + degrade(F3), 착지 직전 secret·PII 스캔 + push 단일 경로(L1).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_salvage_bundle.py header.
#   bash scripts/check-salvage-bundle.sh --validate      --bundle <path>
#   bash scripts/check-salvage-bundle.sh --store         --bundle <path> --out <path>
#   bash scripts/check-salvage-bundle.sh --dedup         --ledger <path> --intents <path>
#   bash scripts/check-salvage-bundle.sh --land          --worktree <dir> --branch <b> [--remote r] [--sha S]
#   bash scripts/check-salvage-bundle.sh --pre-push-scan --worktree <dir> [--sha S]
#     0 = PASS / 1 = 위반·fail-closed·판정 불가·저장 실패 / 2 = usage error.
#
# ★ ADR-151 인벤토리 정의역 **밖**(tests/scripts/*.sh 아님) — 등재 금지(등재 시 record→missing file).
#   실행 liveness = AC-12b(test_nontest_script_execution_liveness.sh) 축이 담당.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[salvage-infra-error] check-salvage-bundle: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_salvage_bundle.py" "$@"
