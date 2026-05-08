#!/usr/bin/env bash
# worktree-create.sh — CFP-136 worktree create wrapper.
#
# Creates a git worktree at $HOME/.claude/worktrees/<repo-name>/<branch-name-flatten>
# from the specified base branch (default: origin/main). Branch name slashes are
# flattened to dashes for filesystem safety (cfp-135/design/mapper -> cfp-135-design-mapper).
#
# Usage:
#   bash templates/scripts/worktree-create.sh <branch-name>
#   bash templates/scripts/worktree-create.sh <branch-name> <base-branch>
#
# Output: stdout = worktree absolute path (single line, scriptable).
#         stderr = human-readable status messages.
#
# Exit code: 0 (created or already exists) / 1 (usage error or git failure).

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <branch-name> [<base-branch>]" >&2
  exit 1
fi

BRANCH="$1"
BASE="${2:-origin/main}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
BRANCH_FLAT="${BRANCH//\//-}"
WORKTREE_BASE="$HOME/.claude/worktrees/$REPO_NAME"
WORKTREE_PATH="$WORKTREE_BASE/$BRANCH_FLAT"

mkdir -p "$WORKTREE_BASE"

if [[ -d "$WORKTREE_PATH" ]]; then
  echo "[worktree-create] EXISTS: $WORKTREE_PATH" >&2
  echo "$WORKTREE_PATH"
  exit 0
fi

git worktree add -b "$BRANCH" "$WORKTREE_PATH" "$BASE"
echo "[worktree-create] CREATED: branch=$BRANCH path=$WORKTREE_PATH base=$BASE" >&2
echo "$WORKTREE_PATH"
