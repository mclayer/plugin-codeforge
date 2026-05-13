#!/usr/bin/env bash
# CFP-429 — E4 self-test (worktree-first mechanical enforcement 4 actual 발동 격리 시뮬레이션).
# carrier: ADR-040 Amendment 4 (CFP-429) + ADR-055 Amendment 2 integration test scope.
# R4 self-block 회피 5-layer:
#   (1) 본 self-test 실행 = 본 Story PR CI worktree 내부 (workflow `actions/checkout` 후 GITHUB_WORKSPACE 안)
#   (2) self-test fixture = `mktemp -d` 격리 directory (real working tree / `.git/hooks/` 영향 0)
#   (3) hook sample = `templates/.git-hooks/*.sample` 안 file (active `.git/hooks/` 미설치, install opt-in)
#   (4) 4 lint script warning tier exit 0 (false-positive 차단 0)
#   (5) `BYPASS_WORKTREE_FIRST=1` env reserved (fixture 안 4 hook 시뮬레이션 모두 적용 의무)
#
# E4-1: scripts/check-session-start-hook-presence.sh 가 SessionStart hook 부재 시 WARN 출력 verify
# E4-2: scripts/check-worktree-first-spawn-evidence-cwd.sh 가 Working dir: 누락 row 검출 verify
# E4-3: templates/.git-hooks/pre-checkout.sample 가 main working tree 에서 cfp-NNN checkout 시 WARN 출력 verify
# E4-4: templates/.git-hooks/pre-commit-main-block.sample 가 main working tree 에서 src/docs commit 시 WARN 출력 verify
set -euo pipefail

REPO_ROOT="${GITHUB_WORKSPACE:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
TMP=$(mktemp -d -t cfp-429-self-test-XXXXXXXX)
trap 'rm -rf "$TMP" 2>/dev/null || true' EXIT

PASS=0
FAIL=0
RESULTS=()

assert_warn() {
  # $1 = test name, $2 = expected pattern, $3 = actual stderr/stdout
  if echo "$3" | grep -E "$2" > /dev/null 2>&1; then
    RESULTS+=("PASS: $1")
    PASS=$((PASS+1))
  else
    RESULTS+=("FAIL: $1 — expected pattern '$2' not found in output")
    RESULTS+=("    output: $3")
    FAIL=$((FAIL+1))
  fi
}

# ── E4-1: scripts/check-session-start-hook-presence.sh SessionStart hook 부재 시 WARN ──
e4_1() {
  local fixture_dir="$TMP/e4-1"
  mkdir -p "$fixture_dir/.claude"
  # 의도적으로 hooks: {} 미지정 (SessionStart hook 부재 시뮬레이션)
  cat > "$fixture_dir/.claude/settings.json" <<'JSON'
{ "hooks": {} }
JSON
  local out
  out=$(cd "$fixture_dir" && bash "$REPO_ROOT/scripts/check-session-start-hook-presence.sh" 2>&1) || true
  assert_warn "E4-1 (SessionStart hook absence WARN)" "WARN|worktree" "$out"
}

# ── E4-2: scripts/check-worktree-first-spawn-evidence-cwd.sh Working dir: 누락 row 검출 ──
e4_2() {
  local fixture_dir="$TMP/e4-2"
  local stories_dir="$fixture_dir/docs/stories"
  mkdir -p "$stories_dir"
  # 의도적으로 Working dir: field 누락 — yaml block 형식 (canonical script awk pattern 정합)
  cat > "$stories_dir/CFP-TEST-FIXTURE.md" <<'MD'
# CFP-TEST-FIXTURE

## §14. Lane Evidence

```yaml
lane_evidence:
  - lane: requirements
    iteration: 1
    agent: RequirementsPLAgent
    started_at: 2026-05-13T15:00:00+09:00
    transcript: "(no Working dir field — 의도적 누락)"
    outcome: RETURN_PASS
```
MD
  # git repo 초기화 + fixture file commit → git log --diff-filter=A 정상 작동 보장
  # ENFORCE_FROM=2026-05-12T00:00:00Z (CFP-426 merge 후 시점) 보다 현재 commit timestamp가 크므로 enforce 조건 통과
  (cd "$fixture_dir" && git init -q -b main \
    && git -c user.email=test@local -c user.name=test add docs/stories/CFP-TEST-FIXTURE.md \
    && git -c user.email=test@local -c user.name=test commit -q -m "add fixture story") 2>/dev/null || true
  local out
  out=$(cd "$fixture_dir" && STORIES_DIR="$stories_dir" ENFORCE_FROM="2026-05-12T00:00:00Z" bash "$REPO_ROOT/scripts/check-spawn-evidence-cwd.sh" 2>&1) || true
  assert_warn "E4-2 (spawn-evidence cwd absence WARN)" "WARN|Working dir" "$out"
}

# ── E4-3: templates/.git-hooks/pre-checkout.sample main working tree 에서 cfp-NNN checkout WARN ──
# NOTE: git 'pre-checkout'은 공식 git hook 이름이 아니므로 git checkout 자동 트리거 불가.
#       CFP-428 unit test TC-4 패턴과 동일하게 hook 스크립트를 직접 bash로 호출해 검증.
#       hook 인자 규약 (Pro Git §8.3 verbatim): $1=prev_HEAD SHA, $2=next_HEAD (ref form), $3=branch_flag(1)
e4_3() {
  local fixture_dir="$TMP/e4-3"
  mkdir -p "$fixture_dir"
  (cd "$fixture_dir" && git init -q -b main && git -c user.email=test@local -c user.name=test commit --allow-empty -q -m "initial")
  # cfp-99999 branch 생성 (next_branch resolve 가능 상태 — hook L36 git rev-parse --abbrev-ref 정합)
  (cd "$fixture_dir" && git branch cfp-99999)
  local out
  # hook 직접 호출: $1=HEAD (prev), $2=refs/heads/cfp-99999 (next ref form), $3=1 (branch checkout)
  out=$(cd "$fixture_dir" && bash "$REPO_ROOT/templates/.git-hooks/pre-checkout.sample" "HEAD" "refs/heads/cfp-99999" "1" 2>&1) || true
  assert_warn "E4-3 (pre-checkout main → cfp-NNN WARN)" "WARN|worktree-first" "$out"
}

# ── E4-4: templates/.git-hooks/pre-commit-main-block.sample main working tree 에서 src/docs commit WARN ──
e4_4() {
  local fixture_dir="$TMP/e4-4"
  mkdir -p "$fixture_dir"
  (cd "$fixture_dir" && git init -q -b main && git -c user.email=test@local -c user.name=test commit --allow-empty -q -m "initial")
  install -m 0755 "$REPO_ROOT/templates/.git-hooks/pre-commit-main-block.sample" "$fixture_dir/.git/hooks/pre-commit"
  mkdir -p "$fixture_dir/src" "$fixture_dir/docs"
  echo "x" > "$fixture_dir/src/test.txt"
  echo "y" > "$fixture_dir/docs/test.md"
  (cd "$fixture_dir" && git add src/test.txt docs/test.md)
  local out
  out=$(cd "$fixture_dir" && git -c user.email=test@local -c user.name=test commit -m "test commit on main" 2>&1) || true
  assert_warn "E4-4 (pre-commit main → src/docs WARN)" "WARN|worktree-first" "$out"
}

# ── bypass env propagation subset (R4 mitigation layer (5) verification) ──
e4_bypass() {
  local fixture_dir="$TMP/e4-bypass"
  mkdir -p "$fixture_dir/.claude"
  cat > "$fixture_dir/.claude/settings.json" <<'JSON'
{ "hooks": {} }
JSON
  local out
  out=$(cd "$fixture_dir" && BYPASS_WORKTREE_FIRST=1 bash "$REPO_ROOT/scripts/check-session-start-hook-presence.sh" 2>&1) || true
  # BYPASS_WORKTREE_FIRST=1 시 canonical script 출력 = "[hook-presence] BYPASS_WORKTREE_FIRST=1 — skip"
  # else fallback 제거 → grep pattern 미매칭 시 FAIL (false-positive 검출 능력 보장)
  if echo "$out" | grep -E "BYPASS_WORKTREE_FIRST=1|skip" > /dev/null 2>&1; then
    RESULTS+=("PASS: E4-bypass (BYPASS_WORKTREE_FIRST=1 early exit)")
    PASS=$((PASS+1))
  else
    RESULTS+=("FAIL: E4-bypass — BYPASS skip pattern not detected in output")
    RESULTS+=("    output: $out")
    FAIL=$((FAIL+1))
  fi
}

# 실행
echo "CFP-429 E4 self-test starting (REPO_ROOT=$REPO_ROOT)"
e4_1
e4_2
e4_3
e4_4
e4_bypass

# Reporting
echo ""
printf '%s\n' "${RESULTS[@]}"
echo ""
echo "E4 self-test summary: $PASS PASS, $FAIL FAIL"
if [[ $FAIL -gt 0 ]]; then
  exit 1
fi
exit 0
