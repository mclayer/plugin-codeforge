#!/usr/bin/env bash
# CFP-136 — Cross-platform worktree path helper.
# Source in other scripts: source "$(dirname "$0")/worktree-path-util.sh"
# Provides functions:
#   worktree_base()       — repo-specific base directory
#   worktree_path BRANCH  — full path for branch
#   flatten_branch BRANCH — converts cfp-N/lane/sub → cfp-N-lane-sub

worktree_base() {
  local repo_root repo_name
  repo_root="$(git rev-parse --show-toplevel)"
  repo_name="$(basename "$repo_root")"
  echo "$HOME/.claude/worktrees/$repo_name"
}

flatten_branch() {
  local branch="$1"
  echo "${branch//\//-}"
}

worktree_path() {
  local branch="$1"
  local flat
  flat="$(flatten_branch "$branch")"
  echo "$(worktree_base)/$flat"
}

# Cross-platform path detection
is_windows() {
  [[ "$(uname -s)" =~ ^(MINGW|MSYS|CYGWIN) ]]
}

# Convert Windows path → POSIX (for git on Windows)
to_posix_path() {
  local p="$1"
  if is_windows; then
    cygpath -u "$p" 2>/dev/null || echo "$p"
  else
    echo "$p"
  fi
}
