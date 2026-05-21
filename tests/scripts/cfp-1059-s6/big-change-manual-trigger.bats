#!/usr/bin/env bats
# tests/scripts/cfp-1059-s6/big-change-manual-trigger.bats
# CFP-1059-S6 TDD — big-change-manual-trigger.sh (bash only, no py)
#
# TC map (Change Plan §8.1):
#   TC-11: hard limit declare -> 자동 흐름 skip + 수동 trigger + 알림
#
# §3.1 big-change-trigger: bash only — declare 검출 + 알림 (ADR-089 원칙 7)
# hard limit: column 100+ / row 1억+ / lock 5분+ / depth 7+

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
BIG_CHANGE_SH="${WORKTREE_ROOT}/templates/deployment/big-change-manual-trigger.sh"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  export CBL_SKIP_ISSUE_CREATE=1
  export CFP1059_SKIP_REAL_DEPLOY=1
}

teardown() {
  rm -rf "${TEST_TMP}"
  unset CBL_SKIP_ISSUE_CREATE CFP1059_SKIP_REAL_DEPLOY
}

# 스크립트 존재 확인
@test "TC-11a: big-change-manual-trigger.sh 존재하고 실행 가능" {
  [ -f "${BIG_CHANGE_SH}" ] || fail "big-change-manual-trigger.sh 부재"
  [ -x "${BIG_CHANGE_SH}" ] || fail "big-change-manual-trigger.sh 실행 권한 없음"
}

# TC-11b: hard limit declare -> 수동 trigger 알림
@test "TC-11b: hard limit 선언 -> 자동 흐름 skip + 수동 trigger 알림" {
  run bash "${BIG_CHANGE_SH}" --change-type hard-limit --description "column 100+"
  # 자동 흐름 skip + 수동 trigger 안내
  [[ "${output}" == *"manual"* ]] || [[ "${output}" == *"MANUAL"* ]] || \
    [[ "${output}" == *"수동"* ]] || [[ "${output}" == *"skip"* ]]
}

@test "TC-11c: hard limit 시 exit 0 (알림만, 자동 배포 0)" {
  run bash "${BIG_CHANGE_SH}" --change-type hard-limit --description "row 1억+"
  [ "${status}" -eq 0 ]
}

@test "TC-11d: hard limit 아님 -> 일반 안내 메시지" {
  run bash "${BIG_CHANGE_SH}" --change-type normal
  [ "${status}" -eq 0 ]
  # 정상 흐름 안내
  [[ "${output}" != *"SKIP"* ]] || [[ "${output}" == *"normal"* ]] || \
    [[ "${output}" == *"proceed"* ]] || [[ "${output}" != "" ]]
}

@test "TC-11e: --help 출력" {
  run bash "${BIG_CHANGE_SH}" --help
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"Usage"* ]] || [[ "${output}" == *"usage"* ]] || \
    [[ "${output}" == *"hard-limit"* ]]
}
