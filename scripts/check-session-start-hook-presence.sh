#!/usr/bin/env bash
# CFP-427 actual logic (canonical)
# CFP-427 — SessionStart-worktree-gc hook presence check (warning).
# Verify .claude/settings.json has hooks.SessionStart[] entry referencing check-worktree-stale.sh.
# 폐쇄루프 self-detect: hook wire 자체가 lint 대상 (Researcher Unknown 1).
#
# 환경 변수:
#   BYPASS_WORKTREE_FIRST (선택, 1 = skip)
#     ADR-040 Amendment 3 §결정 7.E — `BYPASS_WORKTREE_GC` 와 disjoint scope.
#
# Exit code:
#   0 — PASS (hook wired) 또는 WARN (warning tier — non-blocking)
#
# carrier: ADR-040 Amendment 3 §결정 7.A action: worktree-first-session-start-wire (actual wire)
set -euo pipefail

if [[ "${BYPASS_WORKTREE_FIRST:-}" == "1" ]]; then
  echo "[hook-presence] BYPASS_WORKTREE_FIRST=1 — skip" >&2
  exit 0
fi

# wrapper repo 자체 dogfood = $(git rev-parse --show-toplevel) 사용
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SETTINGS="${REPO_ROOT}/.claude/settings.json"

if [[ ! -f "$SETTINGS" ]]; then
  echo "[hook-presence] WARN: $SETTINGS not found" >&2
  exit 0  # warning tier — exit 0 (non-blocking)
fi

# 폐쇄루프 self-detect: hook wire 자체가 lint 대상
if ! grep -q "check-worktree-stale.sh" "$SETTINGS"; then
  echo "[hook-presence] WARN: SessionStart hook not wired (sample exists in templates/.claude/hooks/SessionStart-codeforge-worktree-gc.json.sample, but .claude/settings.json missing wire). See ADR-040 §결정 5 + CFP-427." >&2
  exit 0  # warning tier
fi

echo "[hook-presence] OK"
exit 0
