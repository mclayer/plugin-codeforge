#!/usr/bin/env bash
# CFP-426 / ADR-040 Amendment 3 §결정 7 / ADR-060 §결정 5
# worktree-first SessionStart hook wire check — Story 1 skeleton (warning tier)
#
# Story 1 scope = skeleton only. actual logic 는 Story 2 (CFP-427) 가 wire.
# 현 단계 = exit 0 + skeleton notification log only.
#
# 환경 변수:
#   BYPASS_WORKTREE_FIRST (선택, 1 = skip)
#     ADR-040 Amendment 3 §결정 7.E — `BYPASS_WORKTREE_GC` 와 disjoint scope.
#
# Exit code:
#   0 — skeleton (Story 1) 또는 PASS (Story 2 CFP-427 wire 후)
#   1 — violation 1건 이상 (warning tier 에서는 0, blocking-on-pr 전환 시 1)
#
# carrier: ADR-040 Amendment 3 §결정 7.A action: worktree-first-session-start-wire
set -euo pipefail

# BYPASS env short-circuit (ADR-040 §결정 7.E)
if [ "${BYPASS_WORKTREE_FIRST:-}" = "1" ]; then
    echo "BYPASS_WORKTREE_FIRST=1 — skip"
    exit 0
fi

echo "[worktree-first-session-start-wire] SKELETON (Story 2 CFP-427 wires actual logic)"
echo "  - scope: wrapper repo .claude/settings.json hooks.SessionStart[] 안에 check-worktree-stale.sh 호출 entry 검증"
echo "  - actual logic carrier: CFP-427 (Story 2)"
echo "  - warning tier (continue-on-error: true) — PR merge 미차단"

exit 0
