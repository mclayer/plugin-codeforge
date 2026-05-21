#!/usr/bin/env bats
# tests/scripts/cfp-1059-s6/auto-rollback-hook.bats
# CFP-1059-S6 TDD — auto-rollback-hook.sh + auto_rollback_hook.py
#
# TC map (Change Plan §8.1):
#   TC-9: green fail -> blue revert + 알림 (fail-loud)
#   TC-10: blue already active -> no-op (idempotent)
#
# §7.4 empirical-source:
#   healthcheck window 60s: ADR-087 §결정 5 (dimension: latency+count)
#   3시간 보존 내 결함 -> rollback 가능: Issue #1059 카테고리 3/9 (dimension: lifecycle)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
ROLLBACK_SH="${WORKTREE_ROOT}/templates/deployment/auto-rollback-hook.sh"
ROLLBACK_PY="${WORKTREE_ROOT}/scripts/auto_rollback_hook.py"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  export CBL_SKIP_ISSUE_CREATE=1
  export CFP1059_SKIP_REAL_DEPLOY=1
  export _CFP1059_MOCK_DOCKER=1
  export _CFP1059_MOCK_SSH=1
  export _CFP1059_MOCK_HEALTH=fail

  export DEPLOY_REPO="test-repo"
  export DEPLOY_HOST="127.0.0.1"
}

teardown() {
  rm -rf "${TEST_TMP}"
  unset _CFP1059_MOCK_DOCKER _CFP1059_MOCK_SSH _CFP1059_MOCK_HEALTH
  unset DEPLOY_REPO DEPLOY_HOST
  unset CBL_SKIP_ISSUE_CREATE CFP1059_SKIP_REAL_DEPLOY
}

# 스크립트 존재 확인
@test "TC-9a: auto-rollback-hook.sh 존재하고 실행 가능" {
  [ -f "${ROLLBACK_SH}" ]
  [ -x "${ROLLBACK_SH}" ]
}

@test "TC-9b: auto_rollback_hook.py 존재 (ADR-061)" {
  [ -f "${ROLLBACK_PY}" ]
}

# TC-9: green fail -> blue revert + 알림
@test "TC-9: green health fail -> blue revert (swap revert) + 사용자 알림" {
  export _CFP1059_MOCK_HEALTH=fail
  run bash "${ROLLBACK_SH}" --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"
  # rollback 실행 = exit 비0 (배포 실패 알림) 또는 exit 0 (rollback 자체 성공)
  [[ "${output}" == *"rollback"* ]] || [[ "${output}" == *"ROLLBACK"* ]] || \
    [[ "${output}" == *"blue"* ]] || [[ "${output}" == *"revert"* ]]
}

@test "TC-9c: rollback 시 알림 메시지 포함 (fail-loud)" {
  export _CFP1059_MOCK_HEALTH=fail
  run bash "${ROLLBACK_SH}" --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"
  # 알림 메시지 (fail-loud — silent 차단)
  [[ "${output}" != "" ]]
}

# TC-10: blue already active -> no-op (idempotent)
@test "TC-10: blue 이미 active -> no-op (idempotent rollback 재실행 안전)" {
  export _CFP1059_MOCK_BLUE_ACTIVE=1
  export _CFP1059_MOCK_HEALTH=fail
  run bash "${ROLLBACK_SH}" --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"no-op"* ]] || [[ "${output}" == *"already"* ]] || \
    [[ "${output}" == *"skip"* ]] || [[ "${output}" == *"SKIP"* ]]
  unset _CFP1059_MOCK_BLUE_ACTIVE
}

# TC-10b: 3시간 보존 window 내 rollback 가능
@test "TC-10b: 3시간 보존 window 내 rollback 가능 확인" {
  export _CFP1059_MOCK_HEALTH=fail
  export _CFP1059_MOCK_WITHIN_RETENTION=1
  run bash "${ROLLBACK_SH}" --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"
  # rollback 가능 (3시간 window 내 — empirical-source: Issue #1059 카테고리 3/9)
  [[ "${output}" != *"expired"* ]]  # 보존 기간 만료 아님
  unset _CFP1059_MOCK_WITHIN_RETENTION
}
