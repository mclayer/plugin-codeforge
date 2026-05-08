#!/usr/bin/env bash
# worktree-prune.sh — CFP-136 worktree prune wrapper.
#
# Removes the worktree at $HOME/.claude/worktrees/<repo-name>/<branch-name-flatten>
# and attempts to delete the branch (only if merged — falls back to retain message).
# Pass --force to remove dirty worktrees.
#
# Usage:
#   bash templates/scripts/worktree-prune.sh <branch-name>
#   bash templates/scripts/worktree-prune.sh <branch-name> --force
#
# Exit code: 0 (pruned or already absent) / 1 (usage error or git failure).

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <branch-name> [--force]" >&2
  exit 1
fi

BRANCH="$1"
FORCE="${2:-}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
BRANCH_FLAT="${BRANCH//\//-}"
WORKTREE_PATH="$HOME/.claude/worktrees/$REPO_NAME/$BRANCH_FLAT"

if [[ ! -d "$WORKTREE_PATH" ]]; then
  echo "[worktree-prune] NOT_EXIST: $WORKTREE_PATH" >&2
  exit 0
fi

if [[ "$FORCE" == "--force" ]]; then
  git worktree remove --force "$WORKTREE_PATH"
else
  git worktree remove "$WORKTREE_PATH"
fi

git branch -d "$BRANCH" 2>/dev/null || \
  echo "[worktree-prune] branch $BRANCH retained (not merged; use 'git branch -D $BRANCH' to force)" >&2

echo "[worktree-prune] PRUNED: $WORKTREE_PATH" >&2
