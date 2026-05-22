#!/usr/bin/env bats
# tests/scripts/cfp-1256/atlassian-tool-drift.bats
# CFP-1256 W4-S13 — ADR-103 §결정 3 atlassian-tool-drift check TDD
# QADeveloperAgent TDD (RED written first, GREEN after implementation)
#
# TC 3종 discriminating:
#   (a) snapshot placeholder = advisory exit 0
#   (b) snapshot 에 tool 있고 deny 누락 = drift warning exit 1
#   (c) snapshot 전부 deny 됨 = OK exit 0
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — positive + negative 2-assertion per TC
#   Layer 3 — 임시 fixture 파일 사용 (실제 repo 파일 의존 금지)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# SSOT: ADR-103 §결정 3 (atlassian-tool-drift check 의무)
# Change-plan: CFP-1256 W4-S13

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
DRIFT_SCRIPT="${WORKTREE_ROOT}/scripts/check-atlassian-tool-drift.sh"

# ──────────────────────────────── sandbox setup ────────────────────────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
}

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  export CBL_SKIP_ISSUE_CREATE=1

  # 임시 snapshot 파일 경로
  export SNAPSHOT_FIXTURE="${TEST_TMP}/atlassian-tool-snapshot.txt"
  # 임시 settings.json 경로
  export SETTINGS_FIXTURE="${TEST_TMP}/settings.json"
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1256-unused}"
}

# ── helper: snapshot + settings 를 환경변수로 override 하는 wrapper ─────────────
# check-atlassian-tool-drift.sh 가 파일 경로를 고정으로 계산하므로
# 테스트에서는 symlink 방식으로 tmpdir 안에 repo 구조를 재현한다
_run_drift_check_with_fixtures() {
  local snapshot_content="$1"
  local settings_content="$2"

  # tmpdir 안에 필요한 디렉터리 구조 생성
  mkdir -p "${TEST_TMP}/docs"
  mkdir -p "${TEST_TMP}/.claude"
  mkdir -p "${TEST_TMP}/scripts"

  echo "${snapshot_content}" > "${TEST_TMP}/docs/atlassian-tool-snapshot.txt"
  echo "${settings_content}" > "${TEST_TMP}/.claude/settings.json"

  # 스크립트를 tmpdir 안 scripts/ 에 복사해 SCRIPT_DIR 기반 REPO_ROOT 가 TEST_TMP 를 가리키게 한다
  cp "${DRIFT_SCRIPT}" "${TEST_TMP}/scripts/check-atlassian-tool-drift.sh"
  chmod +x "${TEST_TMP}/scripts/check-atlassian-tool-drift.sh"

  run bash "${TEST_TMP}/scripts/check-atlassian-tool-drift.sh"
}

# ──────────────────────────────── TC-A: snapshot placeholder ────────────────────
# 기대: exit 0 + advisory 메시지 (ADVISORY 포함)
@test "TC-A: snapshot placeholder → advisory exit 0" {
  local placeholder_content
  placeholder_content="$(cat <<'EOF'
# PLACEHOLDER — Atlassian 인스턴스 /mcp enumeration 후 채움 (ADR-103 §결정 3)
# 빈 줄 / 주석만 존재 = placeholder
EOF
)"

  local settings_content
  settings_content='{"permissions": {"deny": []}}'

  _run_drift_check_with_fixtures "${placeholder_content}" "${settings_content}"

  # Layer 1: exit code 검증 (|| true 금지)
  [ "${status}" -eq 0 ]

  # Layer 2: positive — ADVISORY 메시지 포함 확인
  [[ "${output}" == *"ADVISORY"* ]]

  # Layer 2: negative — drift warning 발화 금지
  [[ "${output}" != *"deny 누락 발견"* ]]
}

# ──────────────────────────────── TC-B: snapshot 있고 deny 누락 ──────────────────
# 기대: exit 1 + drift warning 메시지
@test "TC-B: snapshot tool 있고 deny 누락 → drift warning exit 1" {
  local snapshot_content
  snapshot_content="$(cat <<'EOF'
# Atlassian MCP tool snapshot
mcp__plugin_atlassian_atlassian__get_page
mcp__plugin_atlassian_atlassian__update_page
mcp__plugin_atlassian_atlassian__create_page
EOF
)"

  # settings.json 에 mcp__plugin_atlassian_atlassian__get_page 만 deny, update_page + create_page 누락
  local settings_content
  settings_content='{"permissions": {"deny": ["mcp__plugin_atlassian_atlassian__get_page"]}}'

  _run_drift_check_with_fixtures "${snapshot_content}" "${settings_content}"

  # Layer 1: exit code 검증
  [ "${status}" -eq 1 ]

  # Layer 2: positive — drift warning 메시지 포함
  [[ "${output}" == *"deny 누락 발견"* ]] || [[ "${output}" == *"allow-by-omission drift"* ]]

  # Layer 2: negative — OK 메시지 금지
  [[ "${output}" != *"[OK]"* ]]
}

# ──────────────────────────────── TC-C: snapshot 전부 deny ──────────────────────
# 기대: exit 0 + OK 메시지
@test "TC-C: snapshot 전부 deny 됨 → OK exit 0" {
  local snapshot_content
  snapshot_content="$(cat <<'EOF'
# Atlassian MCP tool snapshot
mcp__plugin_atlassian_atlassian__get_page
mcp__plugin_atlassian_atlassian__update_page
EOF
)"

  # settings.json 에 snapshot 전부 deny
  local settings_content
  settings_content='{"permissions": {"deny": ["mcp__plugin_atlassian_atlassian__get_page", "mcp__plugin_atlassian_atlassian__update_page"]}}'

  _run_drift_check_with_fixtures "${snapshot_content}" "${settings_content}"

  # Layer 1: exit code 검증
  [ "${status}" -eq 0 ]

  # Layer 2: positive — OK 메시지 포함
  [[ "${output}" == *"[OK]"* ]]

  # Layer 2: negative — drift warning / ADVISORY 금지
  [[ "${output}" != *"deny 누락 발견"* ]]
  [[ "${output}" != *"ADVISORY"* ]]
}
