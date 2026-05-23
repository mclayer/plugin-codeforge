#!/usr/bin/env bats
# tests/scripts/cfp-604/check-architect-marketplace-self-check.bats
# CFP-604 — Gap A check-architect-marketplace-self-check.sh TDD fixture
# QADeveloperAgent TDD (discriminating fixture — RED before GREEN)
#
# TC map:
#
# TC-1: marketplace_sync_required: true + 완전 선언 → PASS (exit 0)
# TC-2: marketplace_sync_required: true + mirrored_fields_changed[] empty → WARNING (exit 1)
# TC-3: field 자체 부재 (doc-only fast-path 아님) → WARNING (exit 1)
# TC-4: doc-only fast-path label 부착 + field 부재 → PASS (exit 0) [false-positive 차단]
# TC-5: cross-repo dogfood-out marker (dogfood-out:true) 감지 → conditional warning (exit 1)
#
# 3-layer defense (always-pass pattern 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — discriminating fixture (script 미존재 → RED, exit code 정확 검증)
#   Layer 3 — sandbox 격리 (임시 dir, 실제 git repo 접촉 없음)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# ADR refs: ADR-063 §결정 21 (Gap A), ADR-054 (doc-only fast-path), ADR-061 (외부 .py 금지 단순 shell test)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="$WORKTREE_ROOT/scripts/check-architect-marketplace-self-check.sh"

# ──────────────────────────────────── sandbox setup ────────────────────────────────────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
}

setup() {
  export CBL_SKIP_ISSUE_CREATE=1
  # 테스트별 격리된 임시 워킹 디렉토리 생성
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # 스크립트를 $TEST_DIR/scripts/ 에 복사 (SCRIPT_DIR/../ = TEST_DIR 이 되게)
  # CFP-1256 패턴 동형 — REPO_ROOT 가 $TEST_DIR 을 가리키게 한다
  mkdir -p "$TEST_DIR/scripts"
  cp "$SCRIPT" "$TEST_DIR/scripts/check-architect-marketplace-self-check.sh"
  chmod +x "$TEST_DIR/scripts/check-architect-marketplace-self-check.sh"
  SCRIPT_UNDER_TEST="$TEST_DIR/scripts/check-architect-marketplace-self-check.sh"
  export SCRIPT_UNDER_TEST

  # git repo 초기화 (diff 기반 감지용)
  git -C "$TEST_DIR" init --quiet
  git -C "$TEST_DIR" config user.email "test@example.com"
  git -C "$TEST_DIR" config user.name "Test"

  # .claude-plugin/ 디렉토리 및 plugin.json 초기화 (base 커밋)
  mkdir -p "$TEST_DIR/.claude-plugin"
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "6.3.0",
  "description": "base description",
  "author": {"name": "Josh"}
}
PJSON
  git -C "$TEST_DIR" add .
  git -C "$TEST_DIR" commit --quiet -m "base"

  # 실제 diff 를 만들기 위해 plugin.json 수정 후 스테이징
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "6.4.0",
  "description": "updated description - CFP-604",
  "author": {"name": "Josh"}
}
PJSON
  git -C "$TEST_DIR" add .
  # 스테이징된 diff (HEAD 대비)
  export BASE_REF="HEAD"
}

teardown() {
  rm -rf "$TEST_DIR"
  unset TEST_DIR
  unset BASE_REF
  unset PR_BODY
  unset PR_LABELS
}

# ──────────────────────────────── prerequisite check ───────────────────────────────────────────

@test "PREREQ: check-architect-marketplace-self-check.sh 존재 확인" {
  [ -f "$SCRIPT" ]
}

@test "PREREQ: script 실행 권한 확인" {
  chmod +x "$SCRIPT"
  [ -x "$SCRIPT" ]
}

# ──────────────────────────────── TC-1: 완전 선언 → PASS ───────────────────────────────────────

@test "TC-1: marketplace_sync_required: true + 완전 선언 → exit 0 (PASS)" {
  # Change Plan 파일 생성 (§13 완전 선언)
  mkdir -p "$TEST_DIR/docs/change-plans"
  cat > "$TEST_DIR/docs/change-plans/cfp-test.md" <<'PLAN'
---
slug: cfp-test
---

## §13. marketplace sync declare

marketplace_sync_required: true
mirrored_fields_changed: [version, description]
triggering_plugins:
  - codeforge (MINOR)
PLAN

  git -C "$TEST_DIR" add docs/change-plans/cfp-test.md

  export PR_LABELS=""
  export PR_BODY=""
  run bash "$SCRIPT_UNDER_TEST"
  # warning tier — exit 0 or exit 1 모두 가능하지만 완전 선언이면 exit 0
  [ "$status" -eq 0 ]
}

# ──────────────────────────────── TC-2: completeness 불완전 → WARNING ─────────────────────────

@test "TC-2: marketplace_sync_required: true + mirrored_fields_changed[] empty → exit 1 (WARNING)" {
  mkdir -p "$TEST_DIR/docs/change-plans"
  cat > "$TEST_DIR/docs/change-plans/cfp-test.md" <<'PLAN'
---
slug: cfp-test
---

## §13. marketplace sync declare

marketplace_sync_required: true
mirrored_fields_changed: []
triggering_plugins:
  - codeforge (MINOR)
PLAN

  git -C "$TEST_DIR" add docs/change-plans/cfp-test.md

  export PR_LABELS=""
  export PR_BODY=""
  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "mirrored_fields_changed"
}

# ──────────────────────────────── TC-3: §13 field 부재 → WARNING ──────────────────────────────

@test "TC-3: Change Plan 없음 + doc-only fast-path 아님 → exit 1 (WARNING)" {
  # Change Plan 파일 없음 (git diff 에 없음)
  export PR_LABELS=""
  export PR_BODY=""
  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 1 ]
  echo "$output" | grep -qi "change plan\|§13\|marketplace_sync_required"
}

# ──────────────────────────────── TC-4: doc-only fast-path label → PASS ───────────────────────

@test "TC-4: doc-only fast-path label (phase:문서) 부착 → exit 0 (false-positive 차단, ADR-054)" {
  export PR_LABELS="phase:문서"
  export PR_BODY=""
  run bash "$SCRIPT_UNDER_TEST"
  [ "$status" -eq 0 ]
  echo "$output" | grep -qi "doc-only\|fast-path\|문서"
}

# ──────────────────────────────── TC-5: cross-repo dogfood-out marker → conditional warning ─────

@test "TC-5: dogfood-out:true marker 감지 → exit 1 conditional warning (cross-repo dogfood-out case)" {
  # PR body 에 dogfood-out:true 마커 설정 + Change Plan 파일 없음 (cross-repo 시나리오)
  export PR_LABELS=""
  export PR_BODY="$(printf 'dogfood-out:true\nThis PR bumps plugin.json version for CFP-604.')"
  run bash "$SCRIPT_UNDER_TEST"
  # cross-repo dogfood-out case: cross-repo fetch 불가 → conditional warning → exit 1
  [ "$status" -eq 1 ]
  echo "$output" | grep -qi "dogfood\|cross-repo\|conditional"
}

# ──────────────────────────────── TC-large-diff: production-scale DIFF SIGPIPE regression ────────
# FIX-CR-1 discriminating fixture (Gap A 스크립트용):
#   BEFORE FIX: echo "$DIFF" | grep -qE ... → SIGPIPE 시 pipefail 로 MIRRORED_CHANGED=0 → Change Plan 검증 미진입
#   AFTER  FIX: grep -qE ... <<< "$DIFF"    → pipe 없음 → SIGPIPE 발생 불가 → MIRRORED_CHANGED=1 → §13 검증 진행 → exit 1

@test "TC-large-diff: ~100KB description 변경 시 mirrored field 감지 + §13 검증 진입 (SIGPIPE regression)" {
  # ~100KB synthetic description 생성 (production-scale DIFF 시뮬레이션)
  LARGE_DESC=$(python3 -c "print('x' * 102400)" 2>/dev/null || printf '%102400s' '' | tr ' ' 'x')

  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<PJSON
{
  "name": "codeforge",
  "version": "6.4.0",
  "description": "$LARGE_DESC",
  "author": {"name": "Josh"}
}
PJSON
  git -C "$TEST_DIR" add .

  # Change Plan 없음 + doc-only label 없음 → §13 검증 진입 → warning exit 1 (§13 선언 부재)
  export PR_LABELS=""
  export PR_BODY=""
  run bash "$SCRIPT_UNDER_TEST"
  # production-scale DIFF 에서 mirrored field (description) 감지 → §13 검증 진입 → 선언 부재 → exit 1
  [ "$status" -eq 1 ]
  echo "$output" | grep -qi "change plan\|§13\|marketplace_sync_required\|mirrored"
}
