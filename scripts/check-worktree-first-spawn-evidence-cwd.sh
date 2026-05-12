#!/usr/bin/env bash
# CFP-426 / ADR-040 Amendment 3 §결정 7 / ADR-031 §결정 4 / ADR-060 §결정 5
# worktree-first spawn evidence cwd check — Story 1 skeleton (warning tier)
#
# Story 1 scope = skeleton only. actual wire 첫 사례 = Story 2 (CFP-427).
# 현 단계 = exit 0 + skeleton notification log only.
#
# 검증 대상 (Story 2 CFP-427 가 actual logic 도입 시):
#   docs/stories/**.md 의 §14 Lane Evidence row 의 `Working dir:` field 가 다음 둘 중 하나 일치
#     - regex `(^|/)Users/[^/]+/\.claude/worktrees/[^/]+/[^"]+` (worktree path)
#     - `N/A — <30자 이상 사유>` (ADR-031 §결정 4 bypass mechanism)
#
# 환경 변수:
#   BYPASS_WORKTREE_FIRST (선택, 1 = skip)
#     ADR-040 Amendment 3 §결정 7.E — `BYPASS_WORKTREE_GC` 와 disjoint scope.
#
# Exit code:
#   0 — skeleton (Story 1) 또는 PASS (Story 2 CFP-427 wire 후)
#   1 — violation 1건 이상 (warning tier 에서는 0, blocking-on-pr 전환 시 1)
#
# carrier: ADR-040 Amendment 3 §결정 7.A action: worktree-first-spawn-evidence-cwd
set -euo pipefail

if [ "${BYPASS_WORKTREE_FIRST:-}" = "1" ]; then
    echo "BYPASS_WORKTREE_FIRST=1 — skip"
    exit 0
fi

echo "[worktree-first-spawn-evidence-cwd] SKELETON (Story 2 CFP-427 wires actual logic)"
echo "  - scope: docs/stories/**.md §14 Lane Evidence row 의 Working dir field regex 검증"
echo "  - allowed: worktree path 또는 'N/A — <30자 이상 사유>' (ADR-031 §결정 4 bypass)"
echo "  - actual logic carrier: CFP-427 (Story 2)"
echo "  - warning tier (continue-on-error: true) — PR merge 미차단"

exit 0
