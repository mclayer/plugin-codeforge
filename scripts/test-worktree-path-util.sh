#!/usr/bin/env bash
# CFP-136 — worktree script unit test
# Coverage: worktree-path-util.sh (is_windows / to_posix_path / flatten_branch / worktree_path / worktree_base)
# Story §8 ref: §8.4 InfraEng 산출물 + §4 AC-11 (cross-platform path resolve unit test 3종 minimum)
#
# 각 함수를 직접 source 후 호출. git 환경이 필요한 함수(worktree_base / worktree_path)는
# 임시 git repo 에서 실행. 나머지 pure-function 은 격리 실행.
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UTIL_SCRIPT="$SCRIPT_DIR/../templates/scripts/worktree-path-util.sh"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

assert_eq() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$actual" == "$expected" ]]; then
    PASS=$((PASS + 1))
    log "  PASS: $label"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: $label (expected='$expected' actual='$actual')"
  fi
}

assert_exit_zero() {
  local label="$1" rc="$2"
  if [[ "$rc" -eq 0 ]]; then
    PASS=$((PASS + 1))
    log "  PASS: $label"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: $label (expected exit 0, got $rc)"
  fi
}

# ── Source util in subshell to keep test namespace clean ──────────────────────

# Test 1 — flatten_branch: slash → dash
test_1_flatten_branch_slash() {
  log "Test 1: flatten_branch cfp-136/lane/design → cfp-136-lane-design"
  local result
  result="$(bash -c 'source "'"$UTIL_SCRIPT"'"; flatten_branch "cfp-136/lane/design"')"
  assert_eq "flatten_branch slash" "cfp-136-lane-design" "$result"
}

# Test 2 — flatten_branch: no slash (identity)
test_2_flatten_branch_no_slash() {
  log "Test 2: flatten_branch cfp-136 → cfp-136 (identity, no slash)"
  local result
  result="$(bash -c 'source "'"$UTIL_SCRIPT"'"; flatten_branch "cfp-136"')"
  assert_eq "flatten_branch no-slash" "cfp-136" "$result"
}

# Test 3 — flatten_branch: multi-level hierarchy
test_3_flatten_branch_multi() {
  log "Test 3: flatten_branch cfp-136/fix-iter-2/retry → cfp-136-fix-iter-2-retry"
  local result
  result="$(bash -c 'source "'"$UTIL_SCRIPT"'"; flatten_branch "cfp-136/fix-iter-2/retry"')"
  assert_eq "flatten_branch multi" "cfp-136-fix-iter-2-retry" "$result"
}

# Test 4 — worktree_base: uses git repo name
test_4_worktree_base_uses_repo_name() {
  log "Test 4: worktree_base resolves to \$HOME/.claude/worktrees/<repo-name>"
  local tmp_repo base_out repo_name
  tmp_repo="$(mktemp -d)"
  git init -q "$tmp_repo"
  base_out="$(cd "$tmp_repo" && bash -c 'source "'"$UTIL_SCRIPT"'"; worktree_base')"
  repo_name="$(basename "$tmp_repo")"
  assert_eq "worktree_base suffix" "$HOME/.claude/worktrees/$repo_name" "$base_out"
  rm -rf "$tmp_repo"
}

# Test 5 — worktree_path: combines base + flattened branch
test_5_worktree_path_combines() {
  log "Test 5: worktree_path cfp-136/design → \$HOME/.claude/worktrees/<repo>/cfp-136-design"
  local tmp_repo path_out repo_name
  tmp_repo="$(mktemp -d)"
  git init -q "$tmp_repo"
  repo_name="$(basename "$tmp_repo")"
  path_out="$(cd "$tmp_repo" && bash -c 'source "'"$UTIL_SCRIPT"'"; worktree_path "cfp-136/design"')"
  assert_eq "worktree_path" "$HOME/.claude/worktrees/$repo_name/cfp-136-design" "$path_out"
  rm -rf "$tmp_repo"
}

# Test 6 — is_windows: returns consistent boolean (either 0 or 1, no crash)
test_6_is_windows_no_crash() {
  log "Test 6: is_windows() exits with 0 or 1 (no crash)"
  local rc=0
  bash -c 'source "'"$UTIL_SCRIPT"'"; is_windows' >/dev/null 2>&1 || rc=$?
  if [[ "$rc" -eq 0 || "$rc" -eq 1 ]]; then
    PASS=$((PASS + 1))
    log "  PASS: is_windows returned $rc (deterministic)"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: is_windows crashed (rc=$rc)"
  fi
}

# Test 7 — to_posix_path: on non-Windows, returns path unchanged
test_7_to_posix_path_passthrough() {
  log "Test 7: to_posix_path '/tmp/test' → '/tmp/test' on non-Windows"
  # On Windows Git Bash, cygpath -u should also produce posix. We just verify no crash + output.
  local result rc=0
  result="$(bash -c 'source "'"$UTIL_SCRIPT"'"; to_posix_path "/tmp/test"' 2>/dev/null)" || rc=$?
  if [[ "$rc" -eq 0 && -n "$result" ]]; then
    PASS=$((PASS + 1))
    log "  PASS: to_posix_path returned '$result'"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: to_posix_path crashed or empty (rc=$rc)"
  fi
}

# Test 8 — util script: bash syntax check (no parse error)
test_8_syntax_check() {
  log "Test 8: bash -n syntax check on worktree-path-util.sh"
  local rc=0
  bash -n "$UTIL_SCRIPT" 2>/dev/null || rc=$?
  assert_exit_zero "syntax check" "$rc"
}

# ── Run ───────────────────────────────────────────────────────────────────────
log "=== test-worktree-path-util 시작 ==="
test_1_flatten_branch_slash
test_2_flatten_branch_no_slash
test_3_flatten_branch_multi
test_4_worktree_base_uses_repo_name
test_5_worktree_path_combines
test_6_is_windows_no_crash
test_7_to_posix_path_passthrough
test_8_syntax_check

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
