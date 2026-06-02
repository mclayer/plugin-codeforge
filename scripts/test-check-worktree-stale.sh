#!/usr/bin/env bash
# CFP-136 — worktree GC unit test (red-team 정정 후).
#
# Coverage:
#   - bash syntax
#   - BYPASS_WORKTREE_GC=1 fast-exit
#   - non-git dir graceful exit
#   - merged + old + clean              → PRUNED
#   - merged + old + DIRTY              → KEPT (data-loss 가드)
#   - NOT merged + old + clean          → KEPT
#   - merged + RECENT (age 미만)        → KEPT
#   - gh 불가                           → KEPT + WARN (fail-safe)
#   - alternate base dir worktree       → 여전히 EVALUATED (Defect A)
#   - locked worktree                   → KEPT
#
# 실제 worktree 는 절대 삭제하지 않음 — git/gh 를 stub (GC_GIT_BIN / GC_GH_BIN) 으로 주입하고
# fixture 디렉터리 mtime 을 touch 로 조작.
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STALE_SCRIPT="$SCRIPT_DIR/../templates/scripts/check-worktree-stale.sh"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

assert_exit() {
  local label="$1" expected="$2" actual="$3"
  if [[ "$actual" -eq "$expected" ]]; then
    PASS=$((PASS + 1)); log "  PASS: $label (rc=$actual)"
  else
    FAIL=$((FAIL + 1)); log "  FAIL: $label (expected rc=$expected, got rc=$actual)"
  fi
}

assert_contains() {
  local label="$1" needle="$2" haystack="$3"
  if printf '%s' "$haystack" | grep -q -- "$needle"; then
    PASS=$((PASS + 1)); log "  PASS: $label (found '$needle')"
  else
    FAIL=$((FAIL + 1)); log "  FAIL: $label (expected '$needle' in output)"
  fi
}

assert_not_contains() {
  local label="$1" needle="$2" haystack="$3"
  if printf '%s' "$haystack" | grep -q -- "$needle"; then
    FAIL=$((FAIL + 1)); log "  FAIL: $label (unexpected '$needle' present)"
  else
    PASS=$((PASS + 1)); log "  PASS: $label ('$needle' absent as expected)"
  fi
}

# ── Stub harness ────────────────────────────────────────────────────────────
# 각 시나리오는 SANDBOX 디렉터리 안에 git/gh stub 와 state 파일을 둔다.
# Stub git/gh 는 GC_GIT_BIN / GC_GH_BIN 으로 GC 스크립트에 주입된다.
#
# State (env 로 stub 에 전달):
#   STUB_DIR          stub state 디렉터리
#   STUB_WT_PORCELAIN `git worktree list --porcelain` 출력 파일 경로
#   STUB_DIRTY        "1" → status --porcelain 이 변경 출력 (dirty)
#   STUB_GH_AUTH      "1" → gh auth status 성공, 아니면 실패(=gh 불가)
#   STUB_GH_MERGED    "1" → gh pr list 가 merged PR 1건 반환
#   STUB_AHEAD        ahead commit 수 (has_unpushed_commits 용); 기본 0
#   STUB_REMOVE_LOG   worktree remove 호출 기록 파일

make_stub_git() {
  local path="$1"
  cat > "$path" <<'STUB'
#!/usr/bin/env bash
# fake git — GC 스크립트가 호출하는 subcommand 만 처리.
set -uo pipefail
# -C <dir> prefix 무시
args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -C) shift 2;;
    *) args+=("$1"); shift;;
  esac
done
set -- "${args[@]}"
cmd="${1:-}"; sub="${2:-}"
case "$cmd $sub" in
  "rev-parse --show-toplevel")
    echo "${STUB_REPO_ROOT:-/fake/repo}";;
  "rev-parse --abbrev-ref")
    # @{upstream} 조회 — 항상 실패 처리 (origin/main fallback 경로로)
    exit 1;;
  "rev-parse --verify")
    exit 1;;  # origin/main 없음 → main fallback (그래도 rev-list 가 ahead 반환)
  "worktree list")
    cat "$STUB_WT_PORCELAIN";;
  "status --porcelain")
    if [[ "${STUB_DIRTY:-0}" == "1" ]]; then echo " M somefile.txt"; fi;;
  "rev-list --count")
    echo "${STUB_AHEAD:-0}";;
  "worktree remove")
    # 마지막 인자 = path
    eval "wt=\${$#}"
    echo "REMOVE $wt" >> "$STUB_REMOVE_LOG"
    exit 0;;
  "branch -D")
    exit 0;;
  *)
    exit 0;;
esac
STUB
  chmod +x "$path"
}

make_stub_gh() {
  local path="$1"
  cat > "$path" <<'STUB'
#!/usr/bin/env bash
set -uo pipefail
cmd="${1:-}"; sub="${2:-}"
case "$cmd $sub" in
  "auth status")
    [[ "${STUB_GH_AUTH:-0}" == "1" ]] && exit 0 || exit 1;;
  "pr list")
    if [[ "${STUB_GH_MERGED:-0}" == "1" ]]; then
      echo '[{"number":123}]'
    else
      echo '[]'
    fi;;
  *)
    exit 0;;
esac
STUB
  chmod +x "$path"
}

# 시나리오 실행 헬퍼.
# 인자: label, wt_old(1/0), dirty, gh_auth, gh_merged, locked, ahead, base_kind(default/alt)
# 출력: GC stdout+stderr 를 전역 RUN_OUT 에 / rc 를 RUN_RC 에 담는다.
RUN_OUT=""
RUN_RC=0
run_scenario() {
  local wt_old="$1" dirty="$2" gh_auth="$3" gh_merged="$4" locked="$5" ahead="${6:-0}" base_kind="${7:-default}"

  local sb; sb="$(mktemp -d)"
  local repo_root="$sb/repo"
  mkdir -p "$repo_root"

  # worktree fixture 디렉터리
  local wt_dir
  if [[ "$base_kind" == "alt" ]]; then
    wt_dir="$sb/other-base/.claude/worktrees/repo/cfp-999-feature"
  else
    wt_dir="$sb/.claude/worktrees/repo/cfp-999-feature"
  fi
  mkdir -p "$wt_dir"

  # 나이 조작
  if [[ "$wt_old" == "1" ]]; then
    touch -d "30 days ago" "$wt_dir" 2>/dev/null || touch -t 202001010000 "$wt_dir"
  fi

  # porcelain 출력 작성
  local porcelain="$sb/wt.porcelain"
  {
    echo "worktree $repo_root"
    echo "HEAD 1111111111111111111111111111111111111111"
    echo "branch refs/heads/main"
    echo ""
    echo "worktree $wt_dir"
    echo "HEAD 2222222222222222222222222222222222222222"
    echo "branch refs/heads/cfp-999-feature"
    [[ "$locked" == "1" ]] && echo "locked"
    echo ""
  } > "$porcelain"

  local stub_git="$sb/git" stub_gh="$sb/gh" remove_log="$sb/remove.log"
  : > "$remove_log"
  make_stub_git "$stub_git"
  make_stub_gh "$stub_gh"

  RUN_RC=0
  RUN_OUT="$(
    GC_GIT_BIN="$stub_git" \
    GC_GH_BIN="$stub_gh" \
    STUB_REPO_ROOT="$repo_root" \
    STUB_WT_PORCELAIN="$porcelain" \
    STUB_DIRTY="$dirty" \
    STUB_GH_AUTH="$gh_auth" \
    STUB_GH_MERGED="$gh_merged" \
    STUB_AHEAD="$ahead" \
    STUB_REMOVE_LOG="$remove_log" \
    PATH="$sb:$PATH" \
    bash "$STALE_SCRIPT" 2>&1
  )" || RUN_RC=$?

  RUN_REMOVE_LOG="$(cat "$remove_log" 2>/dev/null || true)"
  rm -rf "$sb"
}

# ── Tests ─────────────────────────────────────────────────────────────────────

# 1 — syntax
test_syntax() {
  log "Test: bash -n syntax check"
  local rc=0
  bash -n "$STALE_SCRIPT" 2>/dev/null || rc=$?
  assert_exit "syntax check" 0 "$rc"
}

# 2 — BYPASS
test_bypass() {
  log "Test: BYPASS_WORKTREE_GC=1 → exit 0 + skip log, no DONE"
  local rc=0 out
  out="$(BYPASS_WORKTREE_GC=1 bash "$STALE_SCRIPT" 2>&1)" || rc=$?
  assert_exit "bypass exit 0" 0 "$rc"
  assert_contains "bypass skip log" "skipping" "$out"
  assert_not_contains "bypass no DONE" "DONE" "$out"
}

# 3 — non-git dir graceful
test_non_git_dir() {
  log "Test: non-git dir → graceful exit 0"
  local rc=0 tmp
  tmp="$(mktemp -d)"
  ( cd "$tmp" && bash "$STALE_SCRIPT" >/dev/null 2>&1 ) || rc=$?
  assert_exit "non-git exit 0" 0 "$rc"
  rm -rf "$tmp"
}

# 4 — merged + old + clean → PRUNED
test_merged_old_clean_pruned() {
  log "Test: merged + old + clean → PRUNED"
  run_scenario 1 0 1 1 0 0 default
  assert_exit "exit 0" 0 "$RUN_RC"
  assert_contains "PRUNING line" "PRUNING" "$RUN_OUT"
  assert_contains "pruned=1" "pruned=1" "$RUN_OUT"
  assert_contains "remove called" "cfp-999-feature" "$RUN_REMOVE_LOG"
}

# 5 — merged + old + DIRTY → KEPT (data-loss 가드)
test_merged_old_dirty_kept() {
  log "Test: merged + old + DIRTY → KEPT (data-loss 가드)"
  run_scenario 1 1 1 1 0 0 default
  assert_exit "exit 0" 0 "$RUN_RC"
  assert_contains "KEEP dirty" "dirty" "$RUN_OUT"
  assert_contains "pruned=0" "pruned=0" "$RUN_OUT"
  assert_not_contains "no PRUNING" "PRUNING" "$RUN_OUT"
}

# 6 — NOT merged + old + clean → KEPT
test_notmerged_old_clean_kept() {
  log "Test: NOT merged + old + clean → KEPT"
  run_scenario 1 0 1 0 0 0 default
  assert_exit "exit 0" 0 "$RUN_RC"
  assert_contains "KEEP merged 없음" "merged PR 없음" "$RUN_OUT"
  assert_contains "pruned=0" "pruned=0" "$RUN_OUT"
}

# 7 — merged + RECENT (age 미만) → KEPT
test_merged_recent_kept() {
  log "Test: merged + recent (age 미만) → KEPT"
  run_scenario 0 0 1 1 0 0 default
  assert_exit "exit 0" 0 "$RUN_RC"
  assert_contains "pruned=0" "pruned=0" "$RUN_OUT"
  assert_not_contains "no PRUNING" "PRUNING" "$RUN_OUT"
}

# 8 — gh 불가 → KEPT + WARN (fail-safe)
test_gh_unavailable_failsafe() {
  log "Test: gh 불가 (미인증) → KEPT + WARN (fail-safe)"
  run_scenario 1 0 0 1 0 0 default
  assert_exit "exit 0" 0 "$RUN_RC"
  assert_contains "WARN gh" "WARN" "$RUN_OUT"
  assert_contains "pruned=0" "pruned=0" "$RUN_OUT"
  assert_not_contains "no PRUNING" "PRUNING" "$RUN_OUT"
}

# 9 — alternate base dir worktree → 여전히 EVALUATED (Defect A)
test_alt_base_evaluated() {
  log "Test: alternate base dir worktree → 여전히 EVALUATED (Defect A)"
  run_scenario 1 0 1 1 0 0 alt
  assert_exit "exit 0" 0 "$RUN_RC"
  # 다른 base 에 있어도 prune 까지 도달해야 함 (이전 결함이면 무시됐을 것)
  assert_contains "PRUNING (alt base)" "PRUNING" "$RUN_OUT"
  assert_contains "pruned=1" "pruned=1" "$RUN_OUT"
}

# 10 — locked worktree → KEPT
test_locked_kept() {
  log "Test: locked worktree → KEPT"
  run_scenario 1 0 1 1 1 0 default
  assert_exit "exit 0" 0 "$RUN_RC"
  assert_contains "KEEP locked" "locked" "$RUN_OUT"
  assert_contains "pruned=0" "pruned=0" "$RUN_OUT"
  assert_not_contains "no PRUNING" "PRUNING" "$RUN_OUT"
}

# 11 — merged + old + clean BUT unpushed commits → KEPT (data-loss 가드 2)
test_unpushed_commits_kept() {
  log "Test: merged + old + clean + unpushed commits → KEPT"
  run_scenario 1 0 1 1 0 3 default
  assert_exit "exit 0" 0 "$RUN_RC"
  assert_contains "KEEP unpushed" "unpushed" "$RUN_OUT"
  assert_contains "pruned=0" "pruned=0" "$RUN_OUT"
}

# ── Run ─────────────────────────────────────────────────────────────────────
log "=== test-check-worktree-stale 시작 ==="
test_syntax
test_bypass
test_non_git_dir
test_merged_old_clean_pruned
test_merged_old_dirty_kept
test_notmerged_old_clean_kept
test_merged_recent_kept
test_gh_unavailable_failsafe
test_alt_base_evaluated
test_locked_kept
test_unpushed_commits_kept

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
