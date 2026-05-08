#!/usr/bin/env bash
# CFP-136 — worktree script unit test
# Coverage: worktree-prune.sh (already-absent idempotent / usage error / force flag / normal prune)
# Story §8 ref: §8.4 InfraEng 산출물 §3.4 worktree-prune + §4 AC-4
#               §8.5.4 Unbounded accumulation invariant (idempotency: prune of absent = exit 0)
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PRUNE_SCRIPT="$SCRIPT_DIR/../templates/scripts/worktree-prune.sh"
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

assert_no_dir() {
  local label="$1" path="$2"
  if [[ ! -d "$path" ]]; then
    PASS=$((PASS + 1))
    log "  PASS: $label (path absent as expected)"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: $label (path still exists: $path)"
  fi
}

setup_repo() {
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

# Test 1 — usage error: no args → exit 1
test_1_no_args_usage_error() {
  log "Test 1: no args → exit 1"
  local rc=0
  bash "$PRUNE_SCRIPT" 2>/dev/null || rc=$?
  assert_exit "no-args exit 1" 1 "$rc"
}

# Test 2 — usage error: too many args (3) → exit 1
test_2_too_many_args() {
  log "Test 2: 3 args → exit 1"
  local rc=0
  bash "$PRUNE_SCRIPT" branch extra1 extra2 2>/dev/null || rc=$?
  assert_exit "too-many-args exit 1" 1 "$rc"
}

# Test 3 — bash syntax check
test_3_syntax_check() {
  log "Test 3: bash -n syntax check"
  local rc=0
  bash -n "$PRUNE_SCRIPT" 2>/dev/null || rc=$?
  assert_exit "syntax check" 0 "$rc"
}

# Test 4 — §8.5.4 idempotency invariant: prune of non-existent worktree → exit 0
test_4_already_absent_idempotent() {
  log "Test 4: prune of non-existent worktree → exit 0 (§8.5.4 idempotency)"
  local repo rc=0
  repo="$(setup_repo)"
  local fake_home
  fake_home="$(mktemp -d)"

  (
    cd "$repo"
    HOME="$fake_home" bash "$PRUNE_SCRIPT" "cfp-136-nonexistent-branch" 2>/dev/null
  ) || rc=$?

  assert_exit "already-absent exit 0" 0 "$rc"

  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 5 — happy path: create then prune → exit 0, path removed
test_5_create_then_prune() {
  log "Test 5: create worktree then prune → exit 0, path absent"
  local repo rc_create=0 rc_prune=0 wt_path
  repo="$(setup_repo)"
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"
  local fake_home
  fake_home="$(mktemp -d)"

  # Create
  wt_path="$(
    cd "$repo"
    HOME="$fake_home" bash "$CREATE_SCRIPT" "cfp-136-prune-test" "$base" 2>/dev/null
  )" || rc_create=$?

  assert_exit "create for prune exit 0" 0 "$rc_create"

  # Prune
  (
    cd "$repo"
    HOME="$fake_home" bash "$PRUNE_SCRIPT" "cfp-136-prune-test" 2>/dev/null
  ) || rc_prune=$?

  assert_exit "prune exit 0" 0 "$rc_prune"
  assert_no_dir "worktree path removed" "$wt_path"

  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 6 — double prune: prune twice → both exit 0 (idempotency second call)
test_6_double_prune_idempotent() {
  log "Test 6: prune twice (second call idempotent) → both exit 0"
  local repo rc1=0 rc2=0 wt_path
  repo="$(setup_repo)"
  local base
  base="$(git -C "$repo" symbolic-ref --short HEAD 2>/dev/null || echo "main")"
  local fake_home
  fake_home="$(mktemp -d)"

  wt_path="$(
    cd "$repo"
    HOME="$fake_home" bash "$CREATE_SCRIPT" "cfp-136-double-prune" "$base" 2>/dev/null
  )"

  (
    cd "$repo"
    HOME="$fake_home" bash "$PRUNE_SCRIPT" "cfp-136-double-prune" 2>/dev/null
  ) || rc1=$?

  (
    cd "$repo"
    HOME="$fake_home" bash "$PRUNE_SCRIPT" "cfp-136-double-prune" 2>/dev/null
  ) || rc2=$?

  assert_exit "first prune exit 0" 0 "$rc1"
  assert_exit "second prune (idempotent) exit 0" 0 "$rc2"

  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# Test 7 — --force flag accepted (no extra positional args confusion)
test_7_force_flag_syntax_accepted() {
  log "Test 7: --force flag accepted without usage error"
  local repo rc=0
  repo="$(setup_repo)"
  local fake_home
  fake_home="$(mktemp -d)"

  # non-existent + --force → should exit 0 (path absent path)
  (
    cd "$repo"
    HOME="$fake_home" bash "$PRUNE_SCRIPT" "cfp-136-force-absent" "--force" 2>/dev/null
  ) || rc=$?

  assert_exit "--force + absent path exit 0" 0 "$rc"

  rm -rf "$fake_home"
  teardown_repo "$repo"
}

# ── Run ───────────────────────────────────────────────────────────────────────
log "=== test-worktree-prune 시작 ==="
test_1_no_args_usage_error
test_2_too_many_args
test_3_syntax_check
test_4_already_absent_idempotent
test_5_create_then_prune
test_6_double_prune_idempotent
test_7_force_flag_syntax_accepted

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
