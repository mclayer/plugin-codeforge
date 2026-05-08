#!/usr/bin/env bash
# CFP-136 — worktree script unit test
# Coverage: worktree-create.sh (happy path / already-exists / usage error / base resolution)
# Story §8 ref: §8.4 InfraEng 산출물 §3.2 worktree-create + §4 AC-2
#
# 각 test 는 독립 temp git repo 에서 실행. 실제 worktree add 는 git 이 처리하므로
# local repo 내 branch test 로 격리 (origin/main 의존 X).
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
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

# Setup: temp bare-like git repo with an initial commit so branches exist
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
  # Force-remove any dangling worktrees before rm -rf
  git -C "$repo" worktree list --porcelain 2>/dev/null \
    | awk '/^worktree / {print $2}' \
    | grep -v "^$repo$" \
    | while read -r wt; do
        git -C "$repo" worktree remove --force "$wt" 2>/dev/null || rm -rf "$wt"
      done
  git -C "$repo" worktree prune 2>/dev/null || true
  rm -rf "$repo"
}

# Test 1 — usage error: no args → exit 1
test_1_no_args_usage_error() {
  log "Test 1: no args → exit 1 (usage error)"
  local rc=0
  bash "$CREATE_SCRIPT" 2>/dev/null || rc=$?
  assert_exit "no-args exit 1" 1 "$rc"
}

# Test 2 — usage error: too many args (3) → exit 1
test_2_too_many_args() {
  log "Test 2: 3 args → exit 1 (usage error)"
  local rc=0
  bash "$CREATE_SCRIPT" a b c 2>/dev/null || rc=$?
  assert_exit "too-many-args exit 1" 1 "$rc"
}

# Test 3 — bash syntax check
test_3_syntax_check() {
  log "Test 3: bash -n syntax check"
  local rc=0
  bash -n "$CREATE_SCRIPT" 2>/dev/null || rc=$?
  assert_exit "syntax check" 0 "$rc"
}

# Test 4 — happy path: new branch from local base → exit 0 + outputs path
test_4_happy_path_new_branch() {
  log "Test 4: happy path — new branch, exit 0, stdout = worktree path"
  local repo rc=0 out
  repo="$(setup_repo)"

  # Use main/master as base (whichever exists)
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"

  local fake_home
  fake_home="$(mktemp -d)"

  out="$(cd "$repo" && HOME="$fake_home" bash "$CREATE_SCRIPT" "cfp-136-test-branch" "$base" 2>/dev/null)" \
    || rc=$?

  assert_exit "happy path exit 0" 0 "$rc"
  assert_contains "stdout contains path" "cfp-136-test-branch" "$out"

  # Cleanup
  git -C "$repo" worktree remove --force "$out" 2>/dev/null || true
  git -C "$repo" branch -D "cfp-136-test-branch" 2>/dev/null || true
  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 5 — idempotent: already-exists → exit 0 (no error)
test_5_already_exists_idempotent() {
  log "Test 5: already-exists worktree path → exit 0 (idempotent)"
  local repo rc1=0 rc2=0 out1 out2
  repo="$(setup_repo)"
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"
  local fake_home
  fake_home="$(mktemp -d)"

  # First create (CWD = repo so git rev-parse resolves correctly)
  out1="$(cd "$repo" && HOME="$fake_home" bash "$CREATE_SCRIPT" "cfp-136-idem-branch" "$base" 2>/dev/null)" || rc1=$?
  # Second create (same branch/path — idempotent)
  out2="$(cd "$repo" && HOME="$fake_home" bash "$CREATE_SCRIPT" "cfp-136-idem-branch" "$base" 2>/dev/null)" || rc2=$?

  assert_exit "first create exit 0" 0 "$rc1"
  assert_exit "second create (idempotent) exit 0" 0 "$rc2"

  # Cleanup
  git -C "$repo" worktree remove --force "$out1" 2>/dev/null || true
  git -C "$repo" branch -D "cfp-136-idem-branch" 2>/dev/null || true
  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 6 — branch name flattening: slash is replaced with dash in output path
test_6_branch_name_slash_flattened_in_path() {
  log "Test 6: branch cfp-136/design → path contains cfp-136-design (slash flattened)"
  local repo rc=0 out
  repo="$(setup_repo)"
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"
  local fake_home
  fake_home="$(mktemp -d)"

  out="$(cd "$repo" && HOME="$fake_home" bash "$CREATE_SCRIPT" "cfp-136/design" "$base" 2>/dev/null)" || rc=$?

  assert_exit "slash-flatten exit 0" 0 "$rc"
  assert_contains "path uses dash not slash" "cfp-136-design" "$out"

  # Cleanup
  git -C "$repo" worktree remove --force "$out" 2>/dev/null || true
  git -C "$repo" branch -D "cfp-136/design" 2>/dev/null || true
  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# ── Run ───────────────────────────────────────────────────────────────────────
log "=== test-worktree-create 시작 ==="
test_1_no_args_usage_error
test_2_too_many_args
test_3_syntax_check
test_4_happy_path_new_branch
test_5_already_exists_idempotent
test_6_branch_name_slash_flattened_in_path

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
