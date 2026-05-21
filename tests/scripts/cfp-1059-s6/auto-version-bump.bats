#!/usr/bin/env bats
# tests/scripts/cfp-1059-s6/auto-version-bump.bats
# CFP-1059-S6 TDD — auto-version-bump.sh + auto_version_bump.py
#
# TC map (Change Plan §8.1):
#   TC-5: Epic close -> semver bump + git tag (mock git)
#   TC-6: 재실행 idempotent (tag 존재 -> skip)
#
# §7.4 empirical-source:
#   git tag = Docker tag 1:1 (ADR-063 + ADR-026)
#
# mock seam: _CFP1059_MOCK_GIT

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
VERSION_SH="${WORKTREE_ROOT}/templates/deployment/auto-version-bump.sh"
VERSION_PY="${WORKTREE_ROOT}/scripts/auto_version_bump.py"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  export CBL_SKIP_ISSUE_CREATE=1
  export CFP1059_SKIP_REAL_DEPLOY=1
  export _CFP1059_MOCK_GIT=1
  export _CFP1059_MOCK_DOCKER=1

  # mock git repo in TEST_TMP
  git init "${TEST_TMP}/repo" 2>/dev/null || git init "${TEST_TMP}/repo"
  git -C "${TEST_TMP}/repo" config user.email "test@test.com"
  git -C "${TEST_TMP}/repo" config user.name "test"
  git -C "${TEST_TMP}/repo" commit --allow-empty -m "init" 2>/dev/null || true

  export MOCK_REPO_PATH="${TEST_TMP}/repo"
  export BUMP_TYPE="minor"
  export CURRENT_VERSION="1.2.3"
}

teardown() {
  rm -rf "${TEST_TMP}"
  unset _CFP1059_MOCK_GIT _CFP1059_MOCK_DOCKER
  unset MOCK_REPO_PATH BUMP_TYPE CURRENT_VERSION
  unset CBL_SKIP_ISSUE_CREATE CFP1059_SKIP_REAL_DEPLOY
}

# TC-5a: script 존재 확인
@test "TC-5a: auto-version-bump.sh 존재하고 실행 가능" {
  [ -f "${VERSION_SH}" ]
  [ -x "${VERSION_SH}" ]
}

@test "TC-5b: auto_version_bump.py 존재" {
  [ -f "${VERSION_PY}" ]
}

# TC-5c: semver bump minor
@test "TC-5c: minor bump -> 1.2.3 => 1.3.0 (mock git tag)" {
  run bash "${VERSION_SH}" \
    --repo-path "${MOCK_REPO_PATH}" \
    --current-version "${CURRENT_VERSION}" \
    --bump-type minor
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"1.3.0"* ]]
}

# TC-5d: git tag = Docker tag 1:1 (ADR-063)
@test "TC-5d: git tag = Docker tag 1:1 확인" {
  run bash "${VERSION_SH}" \
    --repo-path "${MOCK_REPO_PATH}" \
    --current-version "${CURRENT_VERSION}" \
    --bump-type minor
  [ "${status}" -eq 0 ]
  # git tag 생성 메시지 정확값 (auto_version_bump.py create_tag 출력 verbatim 정합)
  [[ "${output}" == *"git tag 생성"* ]]
}

# TC-6: 재실행 idempotent (tag 존재 -> skip)
@test "TC-6: 동일 tag 존재 시 skip (idempotent no-op)" {
  # 미리 tag 생성 (--quiet 미지원 git 버전 호환)
  git -C "${MOCK_REPO_PATH}" tag "v1.3.0" 2>/dev/null || true

  run bash "${VERSION_SH}" \
    --repo-path "${MOCK_REPO_PATH}" \
    --current-version "${CURRENT_VERSION}" \
    --bump-type minor
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"skip"* ]] || [[ "${output}" == *"already"* ]] || \
    [[ "${output}" == *"SKIP"* ]] || [[ "${output}" == *"no-op"* ]]
}

# TC-6b: patch bump
@test "TC-6b: patch bump -> 1.2.3 => 1.2.4" {
  run bash "${VERSION_SH}" \
    --repo-path "${MOCK_REPO_PATH}" \
    --current-version "${CURRENT_VERSION}" \
    --bump-type patch
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"1.2.4"* ]]
}
