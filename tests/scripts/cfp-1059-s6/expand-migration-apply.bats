#!/usr/bin/env bats
# tests/scripts/cfp-1059-s6/expand-migration-apply.bats
# CFP-1059-S6 TDD — expand-migration-apply.sh + expand_migration_apply.py
#
# TC map (Change Plan §8.1):
#   TC-7: Alembic upgrade mock + 재apply no-op (idempotent)
#   TC-8: 빅데이터 expand mock + idempotent marker check
#
# §11.6 idempotency:
#   Alembic = revision-based (재apply = no-op if already at head)
#   빅데이터 expand = rekey-migration oneshot (idempotent marker check 후 skip)
#
# §7.4 empirical-source:
#   expand migration timeout = Alembic transaction-per-revision (no fixed timeout)
#   batch size = consumer 데이터 volume 의존 (design-time 미고정)
#   [empirical-source: TBD — consumer 데이터 volume 실측 후 lock-in]

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
EXPAND_SH="${WORKTREE_ROOT}/templates/deployment/expand-migration-apply.sh"
EXPAND_PY="${WORKTREE_ROOT}/scripts/expand_migration_apply.py"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  export CBL_SKIP_ISSUE_CREATE=1
  export CFP1059_SKIP_REAL_DEPLOY=1
  export _CFP1059_MOCK_DOCKER=1
  export _CFP1059_MOCK_SSH=1
}

teardown() {
  rm -rf "${TEST_TMP}"
  unset _CFP1059_MOCK_DOCKER _CFP1059_MOCK_SSH
  unset CBL_SKIP_ISSUE_CREATE CFP1059_SKIP_REAL_DEPLOY
}

# 스크립트 존재 확인
@test "TC-7a: expand-migration-apply.sh 존재하고 실행 가능" {
  [ -f "${EXPAND_SH}" ]
  [ -x "${EXPAND_SH}" ]
}

@test "TC-7b: expand_migration_apply.py 존재 (ADR-061)" {
  [ -f "${EXPAND_PY}" ]
}

# TC-7c: Alembic upgrade mock
@test "TC-7c: Alembic upgrade mock — exit 0 + upgrade 메시지" {
  export _CFP1059_MOCK_ALEMBIC=1
  export MIGRATION_TYPE=alembic
  run bash "${EXPAND_SH}" --type alembic --target head
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"upgrade"* ]] || [[ "${output}" == *"alembic"* ]] || \
    [[ "${output}" == *"UPGRADE"* ]] || [[ "${output}" == *"head"* ]]
  unset _CFP1059_MOCK_ALEMBIC MIGRATION_TYPE
}

# TC-7d: Alembic 재apply no-op (idempotent)
@test "TC-7d: Alembic 이미 head -> no-op (idempotent)" {
  export _CFP1059_MOCK_ALEMBIC=1
  export _CFP1059_MOCK_ALEMBIC_AT_HEAD=1
  run bash "${EXPAND_SH}" --type alembic --target head
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"no-op"* ]] || [[ "${output}" == *"already"* ]] || \
    [[ "${output}" == *"skip"* ]] || [[ "${output}" == *"SKIP"* ]]
  unset _CFP1059_MOCK_ALEMBIC _CFP1059_MOCK_ALEMBIC_AT_HEAD
}

# TC-8a: 빅데이터 expand mock
@test "TC-8a: 빅데이터 expand mock (rekey-migration oneshot)" {
  export _CFP1059_MOCK_BIGDATA_EXPAND=1
  run bash "${EXPAND_SH}" --type bigdata --target rekey-migration
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"expand"* ]] || [[ "${output}" == *"rekey"* ]] || \
    [[ "${output}" == *"EXPAND"* ]]
  unset _CFP1059_MOCK_BIGDATA_EXPAND
}

# TC-8b: 빅데이터 idempotent marker check
@test "TC-8b: 빅데이터 이미 expand 완료 -> idempotent skip" {
  export _CFP1059_MOCK_BIGDATA_EXPAND=1
  export _CFP1059_MOCK_BIGDATA_ALREADY_DONE=1
  run bash "${EXPAND_SH}" --type bigdata --target rekey-migration
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"skip"* ]] || [[ "${output}" == *"already"* ]] || \
    [[ "${output}" == *"SKIP"* ]] || [[ "${output}" == *"no-op"* ]]
  unset _CFP1059_MOCK_BIGDATA_EXPAND _CFP1059_MOCK_BIGDATA_ALREADY_DONE
}

# TC-8c: partial apply -> fail-loud
@test "TC-8c: partial apply 검출 -> fail-loud (exit 비0)" {
  export _CFP1059_MOCK_ALEMBIC=1
  export _CFP1059_MOCK_PARTIAL_APPLY=1
  run bash "${EXPAND_SH}" --type alembic --target head
  [ "${status}" -ne 0 ]
  unset _CFP1059_MOCK_ALEMBIC _CFP1059_MOCK_PARTIAL_APPLY
}
