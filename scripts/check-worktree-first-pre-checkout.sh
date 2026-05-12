#!/usr/bin/env bash
# CFP-428 actual logic — Story 1 skeleton 전환.
# CFP-426 / ADR-040 Amendment 3 §결정 7 / ADR-060 §결정 5
# worktree-first pre-checkout hook check — verification-only pattern (Story 2 exec swap 부적용).
#
# Canonical = templates/.git-hooks/pre-checkout.sample (CFP-428 신설).
# 본 lint = sample 존재 + executable bit + install 가이드 출력 (warning tier).
#
# 환경 변수:
#   BYPASS_WORKTREE_FIRST (선택, 1 = skip)
#     ADR-040 Amendment 3 §결정 7.E — `BYPASS_WORKTREE_GC` 와 disjoint scope.
#
# Exit code:
#   0 — PASS (sample 존재 + executable) 또는 WARN (sample 부재 / mode 미충족 — warning tier)
#
# carrier: ADR-040 Amendment 3 §결정 7.A action: worktree-first-pre-checkout (actual wire)
set -euo pipefail

if [[ "${BYPASS_WORKTREE_FIRST:-}" == "1" ]]; then
  echo "[worktree-first-pre-checkout] BYPASS_WORKTREE_FIRST=1 — skip" >&2
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SAMPLE="$REPO_ROOT/templates/.git-hooks/pre-checkout.sample"

if [[ ! -f "$SAMPLE" ]]; then
  echo "[worktree-first-pre-checkout] WARN: $SAMPLE not found — CFP-428 git hook sample 미배포. ADR-040 Amendment 3 §결정 7.D self-application." >&2
  exit 0  # warning tier
fi

if [[ ! -x "$SAMPLE" ]]; then
  echo "[worktree-first-pre-checkout] WARN: $SAMPLE not executable (mode != 100755). git update-index --chmod=+x 필요." >&2
  exit 0  # warning tier
fi

# Install 가이드 출력 (opt-in 정합 — 강제 install 0)
INSTALLED="$REPO_ROOT/.git/hooks/pre-checkout"
if [[ ! -L "$INSTALLED" ]]; then
  echo "[worktree-first-pre-checkout] INFO: pre-checkout hook sample 존재 (mode 100755 OK). 활성화하려면: bash $REPO_ROOT/scripts/install-git-hooks.sh (opt-in)." >&2
fi

echo "[worktree-first-pre-checkout] OK"
exit 0
