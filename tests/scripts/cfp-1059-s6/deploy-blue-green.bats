#!/usr/bin/env bats
# tests/scripts/cfp-1059-s6/deploy-blue-green.bats
# CFP-1059-S6 TDD (RED -> GREEN) — deploy-blue-green.sh + deploy_blue_green.py
#
# TC map (Change Plan §8.1):
#   TC-1: green container start mock
#   TC-2: health PASS -> atomic swap (Traefik label flip)
#   TC-3: health FAIL -> auto-rollback (blue 유지)
#   TC-4: 3시간 보존 timer mock (blue 즉시 삭제 금지)
#   TC-5: green 이미 실행 중 -> idempotent skip
#   TC-6: swap 실패 -> blue 유지 (no partial state)
#   TC-7: §8.5 process restart invariant (swap 직전 재시작 -> blue 유지)
#
# §7.4 empirical-source:
#   3시간 보존: Issue #1059 카테고리 3/9 (dimension: lifecycle)
#   healthcheck window 60s: ADR-087 §결정 5 (dimension: latency)
#   HTTP drain 30s / WebSocket 5min: ADR-087 §결정 5 (dimension: latency)
#
# mock seam: _CFP1059_MOCK_DOCKER / _CFP1059_MOCK_SSH / _CFP1059_MOCK_HEALTH / _CFP1059_MOCK_GIT

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
DEPLOY_BG_SH="${WORKTREE_ROOT}/templates/deployment/deploy-blue-green.sh"
DEPLOY_BG_PY="${WORKTREE_ROOT}/scripts/deploy_blue_green.py"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  # CFP-843 sandbox env
  export CBL_SKIP_ISSUE_CREATE=1
  export CFP1059_SKIP_REAL_DEPLOY=1

  # mock seam 기본값: MOCK 활성
  export _CFP1059_MOCK_DOCKER=1
  export _CFP1059_MOCK_SSH=1
  export _CFP1059_MOCK_HEALTH=pass   # pass | fail
  export _CFP1059_MOCK_GIT=1

  # 기본 배포 설정
  export DEPLOY_REPO="test-repo"
  export DEPLOY_IMAGE="test-image:v1.0.0"
  export DEPLOY_HOST="127.0.0.1"
  export DEPLOY_RETENTION_HOURS=3   # [empirical-source: Issue #1059 카테고리 3/9]
}

teardown() {
  rm -rf "${TEST_TMP}"
  unset _CFP1059_MOCK_DOCKER _CFP1059_MOCK_SSH _CFP1059_MOCK_HEALTH _CFP1059_MOCK_GIT
  unset DEPLOY_REPO DEPLOY_IMAGE DEPLOY_HOST DEPLOY_RETENTION_HOURS
  unset CBL_SKIP_ISSUE_CREATE CFP1059_SKIP_REAL_DEPLOY
}

# TC-1: green container start mock
@test "TC-1: deploy-blue-green.sh 존재하고 실행 가능" {
  [ -f "${DEPLOY_BG_SH}" ]
  [ -x "${DEPLOY_BG_SH}" ]
}

@test "TC-1b: deploy_blue_green.py 존재" {
  [ -f "${DEPLOY_BG_PY}" ]
}

# TC-2: health PASS -> atomic swap
@test "TC-2: health PASS 시 swap 실행 (Traefik label flip)" {
  export _CFP1059_MOCK_HEALTH=pass
  run bash "${DEPLOY_BG_SH}" --repo "${DEPLOY_REPO}" --image "${DEPLOY_IMAGE}" --host "${DEPLOY_HOST}"
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"atomic swap"* ]] || [[ "${output}" == *"SWAP"* ]] || \
    [[ "${output}" == *"swap"* ]]
}

@test "TC-2b: health PASS 시 출력에 swap 완료 메시지 포함" {
  export _CFP1059_MOCK_HEALTH=pass
  run bash "${DEPLOY_BG_SH}" --repo "${DEPLOY_REPO}" --image "${DEPLOY_IMAGE}" --host "${DEPLOY_HOST}"
  [ "${status}" -eq 0 ]
  # blue 보존 메시지 (3시간)
  [[ "${output}" == *"retention"* ]] || [[ "${output}" == *"보존"* ]] || \
    [[ "${output}" == *"RETENTION"* ]]
}

# TC-3: health FAIL -> auto-rollback (blue 유지)
@test "TC-3: health FAIL 시 rollback (swap 미실행, exit 비0)" {
  export _CFP1059_MOCK_HEALTH=fail
  run bash "${DEPLOY_BG_SH}" --repo "${DEPLOY_REPO}" --image "${DEPLOY_IMAGE}" --host "${DEPLOY_HOST}"
  [ "${status}" -ne 0 ]
  # rollback 메시지
  [[ "${output}" == *"rollback"* ]] || [[ "${output}" == *"ROLLBACK"* ]] || \
    [[ "${output}" == *"blue"* ]]
}

@test "TC-3b: health FAIL 시 swap 미실행 (blue 유지)" {
  export _CFP1059_MOCK_HEALTH=fail
  run bash "${DEPLOY_BG_SH}" --repo "${DEPLOY_REPO}" --image "${DEPLOY_IMAGE}" --host "${DEPLOY_HOST}"
  # swap 성공 메시지 미포함 (unconditional guard — De Morgan 수정: 단독 negation)
  [[ "${output}" != *"swap complete"* ]]
}

# TC-4: 3시간 보존 timer mock (즉시 삭제 금지)
@test "TC-4: blue 3시간 보존 timer mock — 즉시 삭제 금지 메시지" {
  export _CFP1059_MOCK_HEALTH=pass
  run bash "${DEPLOY_BG_SH}" --repo "${DEPLOY_REPO}" --image "${DEPLOY_IMAGE}" --host "${DEPLOY_HOST}"
  [ "${status}" -eq 0 ]
  # 3시간 보존 명시 정확값 (empirical-source: Issue #1059 카테고리 3/9, dimension: lifecycle)
  [[ "${output}" == *"3시간 보존"* ]]
}

# TC-5: green 이미 실행 중 -> idempotent skip
@test "TC-5: green 이미 실행 중 -> idempotent skip (no-op)" {
  export _CFP1059_MOCK_HEALTH=pass
  export _CFP1059_MOCK_GREEN_RUNNING=1
  run bash "${DEPLOY_BG_SH}" --repo "${DEPLOY_REPO}" --image "${DEPLOY_IMAGE}" --host "${DEPLOY_HOST}"
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"skip"* ]] || [[ "${output}" == *"already"* ]] || \
    [[ "${output}" == *"SKIP"* ]] || [[ "${output}" == *"idempotent"* ]]
  unset _CFP1059_MOCK_GREEN_RUNNING
}

# TC-6: swap 실패 -> blue 유지 (no partial state)
@test "TC-6: swap 실패 -> blue 유지 + fail-loud (exit 비0)" {
  export _CFP1059_MOCK_HEALTH=pass
  export _CFP1059_MOCK_SWAP_FAIL=1
  run bash "${DEPLOY_BG_SH}" --repo "${DEPLOY_REPO}" --image "${DEPLOY_IMAGE}" --host "${DEPLOY_HOST}"
  [ "${status}" -ne 0 ]
  unset _CFP1059_MOCK_SWAP_FAIL
}

# TC-7: §8.5 process restart invariant
@test "TC-7: §8.5 swap 직전 재시작 시 blue 유지 (restart invariant)" {
  export _CFP1059_MOCK_HEALTH=pass
  export _CFP1059_MOCK_RESTART_BEFORE_SWAP=1
  run bash "${DEPLOY_BG_SH}" --repo "${DEPLOY_REPO}" --image "${DEPLOY_IMAGE}" --host "${DEPLOY_HOST}"
  # §8.5 재시작 감지 메시지 정확값 (unconditional guard — 출력 verbatim 정합)
  [[ "${output}" == *"no partial swap"* ]]
  unset _CFP1059_MOCK_RESTART_BEFORE_SWAP
}
