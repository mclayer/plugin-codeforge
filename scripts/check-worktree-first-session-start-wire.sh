#!/usr/bin/env bash
# CFP-427 — exec swap to canonical actual logic (Story 1 skeleton replaced)
# CFP-426 / ADR-040 Amendment 3 §결정 7 / ADR-060 §결정 5
# worktree-first SessionStart hook wire check — Story 2 (CFP-427) actual wire wrapper.
#
# canonical implementation = scripts/check-session-start-hook-presence.sh (CFP-427 신설).
# 본 entry point = Story 1 (CFP-426) 의 4 entry 정합 wrapper — exec swap 으로 drift 0 보장.
#
# 환경 변수:
#   BYPASS_WORKTREE_FIRST (선택, 1 = skip — canonical 안에서 처리)
#
# Exit code:
#   0 — PASS / WARN (warning tier)
#   2 — recursive-call detected (FIX iter 1 F-5 guard)
#
# carrier: ADR-040 Amendment 3 §결정 7.A action: worktree-first-session-start-wire
set -euo pipefail

# Recursive-call guard (FIX iter 1 F-5): canonical 이름 invocation 검출 → exit 2
SCRIPT_NAME=$(basename "$0")
CANONICAL="check-session-start-hook-presence.sh"
if [[ "$SCRIPT_NAME" == "$CANONICAL" ]]; then
  echo "[wrapper] ERROR: recursive call detected — wrapper invoked as canonical name. ADR-040 Amendment 3 §결정 7.D + CFP-427 §3.4." >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANONICAL_PATH="$SCRIPT_DIR/$CANONICAL"

# Missing-script guard (FIX iter 1 F-5): canonical 부재 → exit 0 + WARN (warning tier 일관)
if [[ ! -x "$CANONICAL_PATH" ]]; then
  echo "[wrapper] WARN: canonical script not found or not executable: $CANONICAL_PATH. CFP-427 §3.4." >&2
  exit 0
fi

exec "$CANONICAL_PATH" "$@"
