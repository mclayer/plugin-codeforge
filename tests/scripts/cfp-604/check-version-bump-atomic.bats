#!/usr/bin/env bats
# tests/scripts/cfp-604/check-version-bump-atomic.bats
# CFP-604 — Gap B check-version-bump-atomic.sh regression fixture
# QADeveloperAgent TDD (discriminating fixture — RED before GREEN)
#
# TC map:
#
# TC-a: version mismatch blocking 회귀 PASS — Step 3 본체 line 124-147 기존 동작 invariant 보존
# TC-b: gh-skip CI 환경 fail-loud exit 2 — $CI=true AND $GITHUB_ACTIONS=true + gh 미설치
# TC-c: gh-skip non-CI 환경 graceful exit 0 + stderr warning — local advisory 성격 보존
# TC-d: name field drift detection (Step 4 name 축 신규)
# TC-e: author field drift detection (Step 4 author 축 신규)
#
# 3-layer defense (always-pass pattern 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — discriminating fixture (exit code 정확 검증)
#   Layer 3 — sandbox 격리 (mock gh, 실제 network 접촉 없음)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# ADR refs:
#   ADR-063 §결정 22 (Gap B SSOT — silent hole 차단 + mirrored field 4종 확장)
#   ADR-061 (external .py 금지, 단순 shell test)
#   §결정 3 (Change Plan §7 risk 1 — consumer self-hosted runner non-CI graceful skip)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="$WORKTREE_ROOT/scripts/check-version-bump-atomic.sh"

# ──────────────────────────────────── sandbox setup ────────────────────────────────────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
}

setup() {
  export CBL_SKIP_ISSUE_CREATE=1
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # mock gh 스크립트 디렉토리 생성
  MOCK_BIN="$(mktemp -d)"
  export MOCK_BIN

  # git repo 초기화
  git -C "$TEST_DIR" init --quiet
  git -C "$TEST_DIR" config user.email "test@example.com"
  git -C "$TEST_DIR" config user.name "Test"

  mkdir -p "$TEST_DIR/.claude-plugin"

  # 기본 plugin.json base 커밋
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "6.3.0",
  "description": "base description",
  "author": {"name": "Josh"}
}
PJSON
  cat > "$TEST_DIR/CHANGELOG.md" <<'CL'
# Changelog

## [6.3.0] - 2026-05-22

### Added
- base entry
CL
  git -C "$TEST_DIR" add .
  git -C "$TEST_DIR" commit --quiet -m "base"
  export BASE_REF="HEAD"
}

teardown() {
  rm -rf "$TEST_DIR" "$MOCK_BIN"
  unset TEST_DIR MOCK_BIN BASE_REF CI GITHUB_ACTIONS
}

# ──────────────────────────────── prerequisite check ───────────────────────────────────────────

@test "PREREQ: check-version-bump-atomic.sh 존재 확인" {
  [ -f "$SCRIPT" ]
}

@test "PREREQ: script 실행 권한 확인" {
  chmod +x "$SCRIPT"
  [ -x "$SCRIPT" ]
}

# ──────────────────────────────── TC-a: version mismatch blocking 회귀 PASS ───────────────────

@test "TC-a: version mismatch → blocking exit 1 (Step 3 기존 동작 invariant 보존)" {
  # plugin.json version bump — CHANGELOG 와 mismatch 유발
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "6.4.0",
  "description": "base description",
  "author": {"name": "Josh"}
}
PJSON
  git -C "$TEST_DIR" add .

  # CHANGELOG 는 여전히 6.3.0 → Step 2 에서 exit 1 (version mismatch)
  # 주의: Step 2 가 먼저 실행되므로 CHANGELOG 버전 불일치가 먼저 잡힘
  run bash -c "cd '$TEST_DIR' && BASE_REF=HEAD bash '$SCRIPT'"
  [ "$status" -eq 1 ]
  echo "$output" | grep -qi "violation\|mismatch\|CHANGELOG"
}

# ──────────────────────────────── TC-b: gh-skip CI 환경 fail-loud ─────────────────────────────

@test "TC-b: CI 환경에서 gh 미설치 → exit 2 fail-loud (ADR-063 §결정 22 (a) CI mandate)" {
  # plugin.json 변경 + CHANGELOG 버전 일치 (Step 1/2 통과 유도)
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "6.4.0",
  "description": "updated description",
  "author": {"name": "Josh"}
}
PJSON
  cat > "$TEST_DIR/CHANGELOG.md" <<'CL'
# Changelog

## [6.4.0] - 2026-05-23

### Added
- CFP-604 entry
CL
  git -C "$TEST_DIR" add .

  # mock gh: 미설치 시뮬레이션 (PATH 에서 gh 제거)
  # MOCK_BIN 은 비어있으므로 gh 없음
  run bash -c "cd '$TEST_DIR' && BASE_REF=HEAD CI=true GITHUB_ACTIONS=true PATH='$MOCK_BIN:$PATH' bash '$SCRIPT'"
  [ "$status" -eq 2 ]
  # stderr 에 fail-loud 메시지 존재
  echo "$output" | grep -qi "CI\|gh CLI\|미설치\|environment\|exit 2"
}

# ──────────────────────────────── TC-c: gh-skip non-CI 환경 graceful skip + stderr warning ────

@test "TC-c: non-CI 환경에서 gh 미설치 → exit 0 graceful skip + stderr warning (local advisory)" {
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "6.4.0",
  "description": "updated description",
  "author": {"name": "Josh"}
}
PJSON
  cat > "$TEST_DIR/CHANGELOG.md" <<'CL'
# Changelog

## [6.4.0] - 2026-05-23

### Added
- CFP-604 entry
CL
  git -C "$TEST_DIR" add .

  # CI 환경 아님 (CI, GITHUB_ACTIONS 미설정)
  run bash -c "cd '$TEST_DIR' && BASE_REF=HEAD CI='' GITHUB_ACTIONS='' PATH='$MOCK_BIN:$PATH' bash '$SCRIPT'"
  [ "$status" -eq 0 ]
  # output (stdout+stderr) 에 warning 메시지 존재 (silent skip 금지 검증)
  echo "$output" | grep -qi "advisory\|skip\|warning\|⚠"
}

# ──────────────────────────────── TC-d: name field drift detection ─────────────────────────────

@test "TC-d: name field drift → exit 1 blocking (Step 4 name 축 신규 검증)" {
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge-renamed",
  "version": "6.4.0",
  "description": "base description",
  "author": {"name": "Josh"}
}
PJSON
  cat > "$TEST_DIR/CHANGELOG.md" <<'CL'
# Changelog

## [6.4.0] - 2026-05-23

### Added
- test
CL
  git -C "$TEST_DIR" add .

  # mock gh: 설치됨 + 인증됨 + marketplace.json 반환 (name 이 다른 버전)
  cat > "$MOCK_BIN/gh" <<'MOCKGH'
#!/usr/bin/env bash
if [[ "$*" == *"marketplace.json"* ]]; then
  cat <<'JSON'
{
  "plugins": [
    {
      "name": "codeforge",
      "version": "6.4.0",
      "description": "base description",
      "author": "Josh"
    }
  ]
}
JSON
  exit 0
fi
if [[ "$*" == *"auth status"* ]]; then
  exit 0
fi
exit 0
MOCKGH
  chmod +x "$MOCK_BIN/gh"

  run bash -c "cd '$TEST_DIR' && BASE_REF=HEAD CI=true GITHUB_ACTIONS=true PATH='$MOCK_BIN:$PATH' bash '$SCRIPT'"
  [ "$status" -eq 1 ]
  echo "$output" | grep -qi "name.*drift\|name.*mirrored"
}

# ──────────────────────────────── TC-e: author field drift detection ───────────────────────────

@test "TC-e: author field drift → exit 1 blocking (Step 4 author 축 신규 검증)" {
  cat > "$TEST_DIR/.claude-plugin/plugin.json" <<'PJSON'
{
  "name": "codeforge",
  "version": "6.4.0",
  "description": "base description",
  "author": {"name": "Josh Updated"}
}
PJSON
  cat > "$TEST_DIR/CHANGELOG.md" <<'CL'
# Changelog

## [6.4.0] - 2026-05-23

### Added
- test
CL
  git -C "$TEST_DIR" add .

  # mock gh: marketplace 가 author = "Josh" (로컬은 "Josh Updated")
  cat > "$MOCK_BIN/gh" <<'MOCKGH'
#!/usr/bin/env bash
if [[ "$*" == *"marketplace.json"* ]]; then
  cat <<'JSON'
{
  "plugins": [
    {
      "name": "codeforge",
      "version": "6.4.0",
      "description": "base description",
      "author": "Josh"
    }
  ]
}
JSON
  exit 0
fi
if [[ "$*" == *"auth status"* ]]; then
  exit 0
fi
exit 0
MOCKGH
  chmod +x "$MOCK_BIN/gh"

  run bash -c "cd '$TEST_DIR' && BASE_REF=HEAD CI=true GITHUB_ACTIONS=true PATH='$MOCK_BIN:$PATH' bash '$SCRIPT'"
  [ "$status" -eq 1 ]
  echo "$output" | grep -qi "author.*drift\|author.*mirrored"
}
