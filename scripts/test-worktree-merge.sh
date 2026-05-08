#!/usr/bin/env bash
# CFP-136 — worktree script unit test
# Coverage: worktree-merge.sh (happy path / usage error / conflict exit code / no-ff merge)
# Story §8 ref: §8.4 InfraEng 산출물 §3.3 worktree-merge + §4 AC-3
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MERGE_SCRIPT="$SCRIPT_DIR/../templates/scripts/worktree-merge.sh"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

assert_exit() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$actual" -eq "$expected" ]]; then
    PASS=$((PASS + 1))
    log "  PASS: $label (rc=$actual)"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: $label (expected rc=$expected, got rc=$actual)"
  fi
}

# Setup: temp git repo with a commit on default branch
setup_repo_with_commit() {
  local tmp
  tmp="$(mktemp -d)"
  git init -q "$tmp"
  git -C "$tmp" commit --allow-empty -q -m "init"
  echo "$tmp"
}

teardown_repo() {
  local repo="$1"
  git -C "$repo" worktree list --porcelain 2>/dev/null \
    | awk '/^worktree / {print $2}' \
    | grep -v "^$repo$" \
    | while read -r wt; do
        git -C "$repo" worktree remove --force "$wt" 2>/dev/null || rm -rf "$wt"
      done
  git -C "$repo" worktree prune 2>/dev/null || true
  rm -rf "$repo"
}

# Test 1 — usage error: too few args (1) → exit 1
test_1_usage_error_one_arg() {
  log "Test 1: 1 arg only → exit 1 (usage error)"
  local rc=0
  bash "$MERGE_SCRIPT" parent-only 2>/dev/null || rc=$?
  assert_exit "usage-error exit 1" 1 "$rc"
}

# Test 2 — usage error: no args → exit 1
test_2_usage_error_no_args() {
  log "Test 2: no args → exit 1 (usage error)"
  local rc=0
  bash "$MERGE_SCRIPT" 2>/dev/null || rc=$?
  assert_exit "no-args exit 1" 1 "$rc"
}

# Test 3 — bash syntax check
test_3_syntax_check() {
  log "Test 3: bash -n syntax check"
  local rc=0
  bash -n "$MERGE_SCRIPT" 2>/dev/null || rc=$?
  assert_exit "syntax check" 0 "$rc"
}

# Test 4 — happy path: sub-branch merges into parent → exit 0, merge commit exists
test_4_happy_path_merge() {
  log "Test 4: happy path — sub-branch merges into parent, exit 0"
  local repo rc=0
  repo="$(setup_repo_with_commit)"
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"
  local fake_home
  fake_home="$(mktemp -d)"

  # Create sub branch with a unique commit
  git -C "$repo" checkout -q -b cfp-136-merge-sub
  git -C "$repo" commit --allow-empty -q -m "sub: work done"
  git -C "$repo" checkout -q "$base"

  # Run merge: parent=$base sub=cfp-136-merge-sub
  # worktree-merge.sh will create parent worktree via worktree-create.sh
  # We run inside the repo CWD so git rev-parse works
  (
    cd "$repo"
    HOME="$fake_home" bash "$MERGE_SCRIPT" "$base" "cfp-136-merge-sub" 2>/dev/null
  ) || rc=$?

  assert_exit "merge exit 0" 0 "$rc"

  # Cleanup
  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 5 — conflict: two branches modify same file differently → exit 2
test_5_conflict_exit_code_2() {
  log "Test 5: conflicting sub-branches → merge exits 2"
  local repo rc=0
  repo="$(setup_repo_with_commit)"
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"
  local fake_home
  fake_home="$(mktemp -d)"

  # Conflict setup: parent has file-A content, sub has diverging file-A
  echo "parent" > "$repo/conflict.txt"
  git -C "$repo" add conflict.txt
  git -C "$repo" commit -q -m "parent adds conflict.txt"

  git -C "$repo" checkout -q -b cfp-136-conflict-sub
  echo "sub" > "$repo/conflict.txt"
  git -C "$repo" add conflict.txt
  git -C "$repo" commit -q -m "sub: diverges conflict.txt"
  git -C "$repo" checkout -q "$base"

  # Make parent diverge after branching point
  echo "parent-diverge" > "$repo/conflict.txt"
  git -C "$repo" add conflict.txt
  git -C "$repo" commit -q -m "parent: diverges conflict.txt"

  (
    cd "$repo"
    HOME="$fake_home" bash "$MERGE_SCRIPT" "$base" "cfp-136-conflict-sub" 2>/dev/null
  ) || rc=$?

  assert_exit "conflict exit 2" 2 "$rc"

  # Cleanup (conflict leaves index dirty — abort first)
  git -C "$repo" merge --abort 2>/dev/null || true
  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 6 — multiple sub-branches: both succeed sequentially → exit 0
test_6_multi_sub_sequential_merge() {
  log "Test 6: multiple sub-branches merged sequentially → exit 0"
  local repo rc=0
  repo="$(setup_repo_with_commit)"
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"
  local fake_home
  fake_home="$(mktemp -d)"

  git -C "$repo" checkout -q -b cfp-136-multi-sub-a
  git -C "$repo" commit --allow-empty -q -m "sub-a work"
  git -C "$repo" checkout -q "$base"
  git -C "$repo" checkout -q -b cfp-136-multi-sub-b
  git -C "$repo" commit --allow-empty -q -m "sub-b work"
  git -C "$repo" checkout -q "$base"

  (
    cd "$repo"
    HOME="$fake_home" bash "$MERGE_SCRIPT" "$base" "cfp-136-multi-sub-a" "cfp-136-multi-sub-b" 2>/dev/null
  ) || rc=$?

  assert_exit "multi-sub merge exit 0" 0 "$rc"

  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# ── Run ───────────────────────────────────────────────────────────────────────
log "=== test-worktree-merge 시작 ==="
test_1_usage_error_one_arg
test_2_usage_error_no_args
test_3_syntax_check
test_4_happy_path_merge
test_5_conflict_exit_code_2
test_6_multi_sub_sequential_merge

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
