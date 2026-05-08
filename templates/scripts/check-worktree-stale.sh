#!/usr/bin/env bash
# CFP-136 — Stale worktree detection + auto-prune.
# Stale 정의: 7일 이상 + branch 가 closed Story (PR merged) 또는 origin 에 부재.
# SessionStart hook 에서 호출 권장.

set -euo pipefail

# BYPASS: BYPASS_WORKTREE_GC=1 skips all origin contact + prune (debugging only)
if [[ "${BYPASS_WORKTREE_GC:-}" == "1" ]]; then
  echo "[stale-check] BYPASS_WORKTREE_GC=1, skipping" >&2
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[stale-check] NOT_A_GIT_REPO — skipping (non-blocking)" >&2
  exit 0
}
REPO_NAME="$(basename "$REPO_ROOT")"
WORKTREE_BASE="$HOME/.claude/worktrees/$REPO_NAME"

if [[ ! -d "$WORKTREE_BASE" ]]; then
  echo "[stale-check] NO_WORKTREES: $WORKTREE_BASE 부재"
  exit 0
fi

STALE_DAYS=7
PRUNED=0

# Iterate git worktree list (process substitution keeps while in main shell — counter scope preserved)
while read -r wt_path; do
  # Skip main worktree
  if [[ "$wt_path" == "$REPO_ROOT" ]]; then
    continue
  fi

  # Skip non-claude worktrees
  if [[ "$wt_path" != "$WORKTREE_BASE/"* ]]; then
    continue
  fi

  # Check age (find -mtime)
  if [[ -z "$(find "$wt_path" -maxdepth 0 -mtime +$STALE_DAYS 2>/dev/null)" ]]; then
    continue  # Not stale
  fi

  # Get branch
  cd "$wt_path"
  BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
  cd "$REPO_ROOT"

  # Check if branch exists on origin
  if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
    # Branch on origin — keep
    echo "[stale-check] KEEP (origin): $wt_path branch=$BRANCH" >&2
    continue
  fi

  # Branch absent on origin → stale
  echo "[stale-check] PRUNING (stale ${STALE_DAYS}d, origin absent): $wt_path branch=$BRANCH"
  git worktree remove --force "$wt_path"
  git branch -D "$BRANCH" 2>/dev/null || true
  PRUNED=$((PRUNED + 1))
done < <(git worktree list --porcelain | awk '/^worktree / {print $2}')

echo "[stale-check] DONE: pruned=$PRUNED"
