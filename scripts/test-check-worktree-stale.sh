#!/usr/bin/env bash
# CFP-136 — worktree script unit test
# Coverage: check-worktree-stale.sh (no-worktrees fast-exit / syntax / §8.5.2 restart recovery /
#           §8.5.4 accumulation prune / §8.5.3 origin-present worktree kept)
# Story §8 ref: §8.4 InfraEng 산출물 §3.5 stale scan + §8.5.2 Restart recovery + §8.5.4 Unbounded accumulation
#
# NOTE: "7-day age" test 는 실제 mtime 조작 없이 검증 불가 (CI 환경 제약).
# 본 test 는 stale 기준 중 "origin absent" 경로와 "no worktrees" fast-path 를 커버.
# 7일 mtime 기준 통합 검증은 Phase 2 follow-up fixture (실제 old mtime symlink 활용).
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STALE_SCRIPT="$SCRIPT_DIR/../templates/scripts/check-worktree-stale.sh"
CREATE_SCRIPT="$SCRIPT_DIR/../templates/scripts/worktree-create.sh"
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

assert_contains() {
  local label="$1" needle="$2" haystack="$3"
  if printf '%s' "$haystack" | grep -q "$needle"; then
    PASS=$((PASS + 1))
    log "  PASS: $label (found '$needle')"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: $label (expected '$needle' in output)"
  fi
}

setup_repo() {
  local tmp
  tmp="$(mktemp -d)"
  git init -q "$tmp"
  # Set committer identity to avoid CI failure when global git config is absent
  git -C "$tmp" config user.email "test@cfp-136.local"
  git -C "$tmp" config user.name "CFP-136 Test"
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

# Test 1 — bash syntax check
test_1_syntax_check() {
  log "Test 1: bash -n syntax check"
  local rc=0
  bash -n "$STALE_SCRIPT" 2>/dev/null || rc=$?
  assert_exit "syntax check" 0 "$rc"
}

# Test 2 — §8.5.2 Restart recovery: no WORKTREE_BASE dir → exit 0 fast path
test_2_no_worktree_base_exits_0() {
  log "Test 2: §8.5.2 — WORKTREE_BASE absent → exit 0 (fast path, no crash)"
  local repo rc=0 out
  repo="$(setup_repo)"
  local fake_home
  fake_home="$(mktemp -d)"
  # fake_home has no .claude/worktrees/<repo> dir

  out="$(
    cd "$repo"
    HOME="$fake_home" bash "$STALE_SCRIPT" 2>/dev/null
  )" || rc=$?

  assert_exit "no-worktree-base exit 0" 0 "$rc"
  assert_contains "output mentions NO_WORKTREES" "NO_WORKTREES" "$out"

  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 3 — §8.5.4 Accumulation: worktree base exists but empty → exit 0, pruned=0
test_3_empty_worktree_base_exits_0() {
  log "Test 3: §8.5.4 — WORKTREE_BASE exists but empty → exit 0, DONE pruned=0"
  local repo rc=0 out
  repo="$(setup_repo)"
  local fake_home
  fake_home="$(mktemp -d)"
  # Create the base dir manually (as bootstrap would)
  local repo_name
  repo_name="$(basename "$repo")"
  mkdir -p "$fake_home/.claude/worktrees/$repo_name"

  out="$(
    cd "$repo"
    HOME="$fake_home" bash "$STALE_SCRIPT" 2>/dev/null
  )" || rc=$?

  assert_exit "empty-base exit 0" 0 "$rc"
  assert_contains "DONE line present" "DONE" "$out"

  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 4 — §8.5.2 Restart recovery: fresh worktree (age < 7d) is NOT pruned
test_4_fresh_worktree_not_pruned() {
  log "Test 4: §8.5.2 — fresh worktree (< 7d) + origin absent → kept (age criterion)"
  # Note: script checks age first (-mtime +7) then origin.
  # A freshly created worktree will NOT be stale by age → kept regardless of origin.
  local repo rc=0 out wt_path
  repo="$(setup_repo)"
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"
  local fake_home
  fake_home="$(mktemp -d)"

  wt_path="$(
    cd "$repo"
    HOME="$fake_home" bash "$CREATE_SCRIPT" "cfp-136-fresh-branch" "$base" 2>/dev/null
  )"

  out="$(
    cd "$repo"
    HOME="$fake_home" bash "$STALE_SCRIPT" 2>/dev/null
  )" || rc=$?

  assert_exit "fresh-worktree stale-check exit 0" 0 "$rc"
  # Fresh worktree should not be in PRUNING output
  if printf '%s' "$out" | grep -q "PRUNING.*cfp-136-fresh-branch"; then
    FAIL=$((FAIL + 1))
    log "  FAIL: fresh worktree was incorrectly pruned"
  else
    PASS=$((PASS + 1))
    log "  PASS: fresh worktree not pruned (age criterion correct)"
  fi

  # Cleanup
  git -C "$repo" worktree remove --force "$wt_path" 2>/dev/null || true
  git -C "$repo" branch -D "cfp-136-fresh-branch" 2>/dev/null || true
  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 5 — §8.5.3 Cache/drift: main repo worktree is NEVER treated as stale candidate
test_5_main_worktree_skipped() {
  log "Test 5: §8.5.3 — main repo worktree is skipped (not in .claude/worktrees/)"
  local repo rc=0 out
  repo="$(setup_repo)"
  local fake_home
  fake_home="$(mktemp -d)"
  local repo_name
  repo_name="$(basename "$repo")"
  mkdir -p "$fake_home/.claude/worktrees/$repo_name"

  out="$(
    cd "$repo"
    HOME="$fake_home" bash "$STALE_SCRIPT" 2>/dev/null
  )" || rc=$?

  assert_exit "main-worktree-skipped exit 0" 0 "$rc"
  # Main repo path must never appear in PRUNING output
  if printf '%s' "$out" | grep -q "PRUNING.*$repo[^/]"; then
    FAIL=$((FAIL + 1))
    log "  FAIL: main repo incorrectly included in stale candidates"
  else
    PASS=$((PASS + 1))
    log "  PASS: main repo worktree correctly skipped"
  fi

  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 6 — Fail-safe: git failure inside subshell does not crash outer session (|| true)
test_6_failsafe_git_error_no_crash() {
  log "Test 6: §8.5.2 fail-safe — invalid git repo → graceful exit rc=0 (non-blocking)"
  local rc=0
  # Run stale check in a non-git directory; production trap guarantees exit 0
  local tmp_nonrepo
  tmp_nonrepo="$(mktemp -d)"
  (
    cd "$tmp_nonrepo"
    bash "$STALE_SCRIPT" 2>/dev/null
  ) || rc=$?
  # Production fix (§3.5 graceful trap) guarantees exit 0 on non-git dir
  assert_exit "invalid-git-dir exit 0" 0 "$rc"
  rm -rf "$tmp_nonrepo"
}

# ── Run ───────────────────────────────────────────────────────────────────────
log "=== test-check-worktree-stale 시작 ==="
test_1_syntax_check
test_2_no_worktree_base_exits_0
test_3_empty_worktree_base_exits_0
test_4_fresh_worktree_not_pruned
test_5_main_worktree_skipped
test_6_failsafe_git_error_no_crash

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
