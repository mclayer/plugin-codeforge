#!/usr/bin/env bash
# CFP-426 / ADR-040 Amendment 3 §결정 7 / ADR-060 §결정 5
# worktree-first pre-commit main-block hook check — Story 1 skeleton (warning tier)
#
# Story 1 scope = skeleton only. actual git hook 도입 = Story 3 (CFP-428).
# 현 단계 = exit 0 + skeleton notification log only.
#
# 환경 변수:
#   BYPASS_WORKTREE_FIRST (선택, 1 = skip)
#     ADR-040 Amendment 3 §결정 7.E — `BYPASS_WORKTREE_GC` 와 disjoint scope.
#
# Exit code:
#   0 — skeleton (Story 1) 또는 PASS (Story 3 CFP-428 wire 후)
#   1 — violation 1건 이상 (warning tier 에서는 0, blocking-on-pr 전환 시 1)
#
# carrier: ADR-040 Amendment 3 §결정 7.A action: worktree-first-pre-commit-main-block
set -euo pipefail

if [ "${BYPASS_WORKTREE_FIRST:-}" = "1" ]; then
    echo "BYPASS_WORKTREE_FIRST=1 — skip"
    exit 0
fi

echo "[worktree-first-pre-commit-main-block] SKELETON (Story 3 CFP-428 wires actual git hook)"
echo "  - scope: main working tree 에서 src/docs commit 차단 (worktree-first 정책 정합)"
echo "  - actual logic carrier: CFP-428 (Story 3)"
echo "  - warning tier (continue-on-error: true) — PR merge 미차단"

exit 0
