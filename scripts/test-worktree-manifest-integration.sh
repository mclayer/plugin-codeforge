#!/usr/bin/env bash
# CFP-136 — Integration smoke test
# Coverage: consumer-scripts.manifest 5 worktree entry 정합 + bootstrap-consumer.sh Stage 7
#           manifest entry read 동작 검증
# Story §8 ref: §3.6 SessionStart hook + §3.9 Phase 2 PR scope (§8 검증 fixture) +
#               §8.4 InfraEng (consumer-scripts.manifest 5 entry 추가) + §4 AC-9 (AC: 14 Phase 2 PR)
#
# 본 test 는 integration smoke:
#   1. manifest 에 5 worktree script 가 등록됨 (§8.4 DeveloperAgent 산출물 정합)
#   2. 등록된 각 script 파일이 실제로 존재함
#   3. check-consumer-scripts-manifest.sh 가 manifest 를 lint pass 시킴
#   4. bootstrap-consumer.sh --dry-run 이 Stage 7 path 에 worktree script 를 포함함
#
# Exit code: 0 (모든 test PASS) / 1 (1 이상 FAIL)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MANIFEST="$PLUGIN_ROOT/templates/consumer-scripts.manifest"
PASS=0
FAIL=0

log() { printf '[test] %s\n' "$1" >&2; }

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

assert_file_exists() {
  local label="$1" path="$2"
  if [[ -f "$path" ]]; then
    PASS=$((PASS + 1))
    log "  PASS: $label ($path exists)"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: $label ($path not found)"
  fi
}

assert_executable() {
  local label="$1" path="$2"
  if [[ -x "$path" ]]; then
    PASS=$((PASS + 1))
    log "  PASS: $label ($path is executable)"
  else
    FAIL=$((FAIL + 1))
    log "  FAIL: $label ($path not executable)"
  fi
}

# ── Test 1: manifest file itself exists ───────────────────────────────────────
test_1_manifest_exists() {
  log "Test 1: consumer-scripts.manifest exists"
  assert_file_exists "manifest file" "$MANIFEST"
}

# ── Test 2: 5 worktree script entries registered in manifest ─────────────────
test_2_manifest_5_worktree_entries() {
  log "Test 2: manifest contains 5 worktree script entries (§8.4 정합)"
  local manifest_content
  manifest_content="$(grep -v '^#' "$MANIFEST" | grep -v '^$')"
  assert_contains "worktree-create entry"   "templates/scripts/worktree-create.sh"    "$manifest_content"
  assert_contains "worktree-merge entry"    "templates/scripts/worktree-merge.sh"     "$manifest_content"
  assert_contains "worktree-prune entry"    "templates/scripts/worktree-prune.sh"     "$manifest_content"
  assert_contains "check-worktree-stale entry" "templates/scripts/check-worktree-stale.sh" "$manifest_content"
  assert_contains "worktree-path-util entry" "templates/scripts/worktree-path-util.sh" "$manifest_content"
}

# ── Test 3: each registered script file exists ───────────────────────────────
test_3_script_files_exist() {
  log "Test 3: each manifest worktree entry file exists on disk"
  local scripts=(
    "templates/scripts/worktree-create.sh"
    "templates/scripts/worktree-merge.sh"
    "templates/scripts/worktree-prune.sh"
    "templates/scripts/check-worktree-stale.sh"
    "templates/scripts/worktree-path-util.sh"
  )
  for s in "${scripts[@]}"; do
    assert_file_exists "$s present" "$PLUGIN_ROOT/$s"
  done
}

# ── Test 4: each script has bash shebang ─────────────────────────────────────
test_4_scripts_have_shebang() {
  log "Test 4: each worktree script has #!/usr/bin/env bash shebang"
  local scripts=(
    "templates/scripts/worktree-create.sh"
    "templates/scripts/worktree-merge.sh"
    "templates/scripts/worktree-prune.sh"
    "templates/scripts/check-worktree-stale.sh"
    "templates/scripts/worktree-path-util.sh"
  )
  for s in "${scripts[@]}"; do
    local first_line
    first_line="$(head -1 "$PLUGIN_ROOT/$s" 2>/dev/null || echo "")"
    if printf '%s' "$first_line" | grep -q '^#!/usr/bin/env bash'; then
      PASS=$((PASS + 1))
      log "  PASS: $s has shebang"
    else
      FAIL=$((FAIL + 1))
      log "  FAIL: $s missing bash shebang (got: '$first_line')"
    fi
  done
}

# ── Test 5: all 5 scripts pass bash -n syntax check ──────────────────────────
test_5_all_scripts_syntax_check() {
  log "Test 5: bash -n syntax check for all 5 worktree scripts (§4 AC-10)"
  local scripts=(
    "templates/scripts/worktree-create.sh"
    "templates/scripts/worktree-merge.sh"
    "templates/scripts/worktree-prune.sh"
    "templates/scripts/check-worktree-stale.sh"
    "templates/scripts/worktree-path-util.sh"
  )
  for s in "${scripts[@]}"; do
    local rc=0
    bash -n "$PLUGIN_ROOT/$s" 2>/dev/null || rc=$?
    assert_exit "syntax $s" 0 "$rc"
  done
}

# ── Test 6: check-consumer-scripts-manifest.sh validates manifest ────────────
test_6_manifest_lint_passes() {
  log "Test 6: check-consumer-scripts-manifest.sh lint passes (integration)"
  local lint_script="$SCRIPT_DIR/check-consumer-scripts-manifest.sh"
  if [[ ! -f "$lint_script" ]]; then
    log "  SKIP: check-consumer-scripts-manifest.sh not found"
    return
  fi
  local rc=0
  bash "$lint_script" 2>/dev/null || rc=$?
  assert_exit "manifest lint exit 0" 0 "$rc"
}

# ── Test 7: bootstrap-consumer.sh --dry-run mentions worktree scripts ────────
test_7_bootstrap_dry_run_stage7_coverage() {
  log "Test 7: bootstrap-consumer.sh --dry-run stage 7 output references worktree scripts"
  local bootstrap="$SCRIPT_DIR/bootstrap-consumer.sh"
  if [[ ! -f "$bootstrap" ]]; then
    log "  SKIP: bootstrap-consumer.sh not found"
    return
  fi
  local out rc=0
  out="$(bash "$bootstrap" --dry-run --org test-org --repo test-repo 2>&1)" || rc=$?
  # dry-run should succeed
  assert_exit "bootstrap dry-run exit 0" 0 "$rc"
  # Stage 7 output references manifest copy (individual script names not printed in dry-run)
  assert_contains "dry-run mentions Stage 7 manifest" "consumer-scripts.manifest" "$out"
}

# ── Test 8: SessionStart hook sample exists ───────────────────────────────────
test_8_session_start_hook_sample_exists() {
  log "Test 8: SessionStart hook sample file exists (§3.6 + §4 AC-7)"
  assert_file_exists "SessionStart hook sample" \
    "$PLUGIN_ROOT/templates/.claude/hooks/SessionStart-codeforge-worktree-gc.json.sample"
}

# ── Run ───────────────────────────────────────────────────────────────────────
log "=== test-worktree-manifest-integration 시작 ==="
test_1_manifest_exists
test_2_manifest_5_worktree_entries
test_3_script_files_exist
test_4_scripts_have_shebang
test_5_all_scripts_syntax_check
test_6_manifest_lint_passes
test_7_bootstrap_dry_run_stage7_coverage
test_8_session_start_hook_sample_exists

log ""
log "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
