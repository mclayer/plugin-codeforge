#!/usr/bin/env bash
# CFP-843 Phase 2 — write-target-path worktree-membership lint (bash wrapper)
# ADR-040 Amendment 6 §결정 7.J.2 — scope CWD → write-target-path 확장
# ADR-061 정합: thin bash wrapper → canonical Python logic
#
# canonical implementation = scripts/check-write-target-membership.py
# 본 wrapper = bats + CI 호출 진입점 (exec swap 으로 drift 0 보장)
#
# 환경 변수:
#   WRITE_TARGET_PATHS — 검사할 write target 경로 (newline-delimited)
#   EXPECTED_WORKTREE_ROOT — 기대되는 worktree root prefix
#   ENFORCE_FROM — ISO8601 timestamp 기준 (이 시각 이후만 enforce)
#   BYPASS_WORKTREE_FIRST — 1 = short-circuit (5-layer layer 4)
#
# Exit code:
#   0 — always (warning tier, non-blocking)
#
# 5-layer self-block 회피 (ADR-040 §결정 7.J.4 / CFP-428 R3 동형):
#   layer 1: worktree-internal work → PASS
#   layer 2: EXPECTED_WORKTREE_ROOT 미설정 환경 → skip
#   layer 3: ENFORCE_FROM 미래 → skip (false-positive 회피)
#   layer 4: BYPASS_WORKTREE_FIRST=1 → short-circuit
#   layer 5: common-dir path → skip
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANONICAL_PY="$SCRIPT_DIR/check-write-target-membership.py"

# python3 필수
if ! command -v python3 &>/dev/null; then
  echo "[write-target-membership] WARN: python3 not available — skip" >&2
  exit 0
fi

if [[ ! -f "$CANONICAL_PY" ]]; then
  echo "[write-target-membership] WARN: canonical Python script not found: $CANONICAL_PY — skip" >&2
  exit 0
fi

exec python3 "$CANONICAL_PY" "$@"
