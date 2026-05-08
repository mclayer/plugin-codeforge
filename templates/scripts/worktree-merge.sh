#!/usr/bin/env bash
# worktree-merge.sh — CFP-136 sequential merge of sub-worktrees into parent branch.
#
# Checks out <parent-branch> worktree (creates via worktree-create.sh if missing),
# then merges each <sub-branch> sequentially with --no-ff. On conflict, exits with
# code 2 and reports the parent worktree path for manual resolution.
#
# Usage:
#   bash templates/scripts/worktree-merge.sh <parent-branch> <sub-branch1> [<sub-branch2> ...]
#
# Exit code: 0 (all sub merged) / 1 (usage error) / 2 (merge conflict).

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <parent-branch> <sub-branch1> [<sub-branch2> ...]" >&2
  exit 1
fi

PARENT="$1"; shift
SUBS=("$@")

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
PARENT_FLAT="${PARENT//\//-}"
PARENT_PATH="$HOME/.claude/worktrees/$REPO_NAME/$PARENT_FLAT"

if [[ ! -d "$PARENT_PATH" ]]; then
  echo "[worktree-merge] CREATE parent worktree: $PARENT" >&2
  mkdir -p "$HOME/.claude/worktrees/$REPO_NAME"
  # Check out existing local branch (no -b); branch must already exist on local or origin.
  if git show-ref --verify --quiet "refs/heads/$PARENT"; then
    git worktree add "$PARENT_PATH" "$PARENT"
  else
    git worktree add -b "$PARENT" "$PARENT_PATH" "origin/main"
  fi
fi

cd "$PARENT_PATH"

for SUB in "${SUBS[@]}"; do
  echo "[worktree-merge] MERGING: $SUB -> $PARENT" >&2
  if ! git merge --no-ff "$SUB" -m "merge: $SUB into $PARENT (CFP-136 worktree-merge)"; then
    echo "[worktree-merge] CONFLICT: $SUB -> $PARENT" >&2
    echo "[worktree-merge] Manual resolution required at: $PARENT_PATH" >&2
    exit 2
  fi
done

echo "[worktree-merge] DONE: ${#SUBS[@]} sub-branch merged -> $PARENT" >&2
