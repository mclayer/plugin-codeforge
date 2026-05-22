#!/usr/bin/env bats
# tests/scripts/cfp-1215/check-no-atlassian-governance-allowlist.bats
# CFP-1215 Phase 2 — check-no-atlassian.sh governance allowlist 확장 검증 (TDD)
# ADR-100 §결정 1 — wrapper git-commit governance docs 의 Confluence authoritative 범위:
#   docs/inter-plugin-contracts/ + docs/domain-knowledge/ prefix allowlist 추가
#
# TC map:
#   TC-1: docs/inter-plugin-contracts/ 안 "Confluence" 평문 = allowlisted (exit 0)
#   TC-2: docs/domain-knowledge/ 안 "Atlassian" 평문 = allowlisted (exit 0)
#   TC-3 (discriminating negative): 非-governance 영역 안 "Jira" 평문 = 여전히 flagged (exit 1)
#   TC-4: 전체 repo lint 회귀 — 기존 동작 exit 0 유지 (flagged 0 유지)
#   TC-5: ALLOWLIST_GOVERNANCE_PREFIXES 배열이 script 에 존재 (ADR-100 §결정 1 wire 확인)
#
# ADR refs:
#   ADR-100: §결정 1 Confluence doc SSOT 인정 — wrapper governance docs 영역 확장
#   ADR-099: §결정 2 Layer 2 lint allowlist 기반 (ALLOWLIST_ADR_PREFIXES 패턴 답습)
#   ADR-061: external .py 불요 (bash script 대상)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="${WORKTREE_ROOT}/scripts/check-no-atlassian.sh"

# ────────────────────────────── setup / teardown ─────────────────────────────

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
}

teardown() {
  # worktree 안에 생성한 tmp fixture 는 각 TC 에서 개별 정리
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1215-unused}"
}

# ─── TC-1: docs/inter-plugin-contracts/ 안 Confluence 평문 = allowlisted ─────
# ADR-100 §결정 1: docs/inter-plugin-contracts/ = wrapper git-commit governance docs
# 해당 prefix 아래 파일의 Confluence 참조는 exit 0 이어야 함 (allowlist 통과)

@test "TC-1: docs/inter-plugin-contracts/<tmp>.md 안 Confluence 참조 = allowlisted (exit 0, ADR-100 §결정 1)" {
  [ -f "${SCRIPT}" ]

  local fixture_file="${WORKTREE_ROOT}/docs/inter-plugin-contracts/tmp-cfp1215-governance-test.md"
  printf '# 테스트 fixture\nConfluence authoritative readable source (ADR-100 §결정 1 대상)\n' \
    > "${fixture_file}"

  run bash "${SCRIPT}"
  local exit_code="$status"

  rm -f "${fixture_file}"

  [ "$exit_code" -eq 0 ]
}

# ─── TC-2: docs/domain-knowledge/ 안 Atlassian 평문 = allowlisted ─────────────
# ADR-100 §결정 1: docs/domain-knowledge/ = wrapper git-commit governance docs
# 해당 prefix 아래 파일의 Atlassian 참조는 exit 0 이어야 함 (allowlist 통과)

@test "TC-2: docs/domain-knowledge/<tmp>.md 안 Confluence 참조 = allowlisted (exit 0, ADR-100 §결정 1)" {
  [ -f "${SCRIPT}" ]

  local fixture_dir="${WORKTREE_ROOT}/docs/domain-knowledge/tmp-cfp1215-test-dir"
  mkdir -p "${fixture_dir}"
  local fixture_file="${fixture_dir}/tmp-cfp1215-domain-test.md"
  # Confluence (대문자 C) 참조 — grep 패턴 Confluence 에 매칭되어 allowlist 없으면 exit 1
  printf '# 도메인 지식\nConfluence authoritative readable source — ADR-100 §결정 1 대상 영역\n' \
    > "${fixture_file}"

  run bash "${SCRIPT}"
  local exit_code="$status"

  rm -f "${fixture_file}"
  rmdir "${fixture_dir}" 2>/dev/null || true

  [ "$exit_code" -eq 0 ]
}

# ─── TC-3 (discriminating negative): 非-governance 영역 안 Jira 평문 = flagged ─
# allowlist over-broad 방지 핵심 TC:
# docs/kpi/ 또는 allowlist 외 영역 의 Jira 참조는 여전히 exit 1 이어야 함
# impl 이 ALLOWLIST_GOVERNANCE_PREFIXES 를 docs/** 전체로 잘못 설정하면 이 TC 가 RED 가 됨

@test "TC-3 (discriminating negative): 非-governance 영역 안 Jira 참조 = 여전히 flagged (exit 1, allowlist over-broad 방지)" {
  [ -f "${SCRIPT}" ]

  # docs/kpi/ 는 governance allowlist 대상 외 — Jira 참조 시 exit 1 이어야 함
  local fixture_file="${WORKTREE_ROOT}/tmp-cfp1215-non-governance-test.md"
  printf '# 비-governance 영역\nJira project_key = PROJ-123 (이 파일은 allowlist 외)\n' \
    > "${fixture_file}"

  run bash "${SCRIPT}"
  local exit_code="$status"

  rm -f "${fixture_file}"

  # 非-governance 파일의 Jira 참조 = exit 1 (여전히 flagged)
  [ "$exit_code" -eq 1 ]
}

# ─── TC-4: 전체 repo lint 회귀 — 기존 동작 exit 0 유지 ──────────────────────
# governance allowlist 확장 후에도 기존 flagged 0 동작이 깨지면 안 됨
# (ADR-100 구현 이전에는 docs/inter-plugin-contracts/ 안 Confluence 참조가 없어야 하므로 exit 0 유지)

@test "TC-4: 전체 repo lint 회귀 — governance allowlist 확장 후 exit 0 유지 (flagged 0 회귀 없음)" {
  [ -f "${SCRIPT}" ]
  run bash "${SCRIPT}"
  [ "$status" -eq 0 ]
}

# ─── TC-5: ALLOWLIST_GOVERNANCE_PREFIXES 배열이 script 에 존재 ────────────────
# ADR-100 §결정 1 wire 확인 — script 안에 ALLOWLIST_GOVERNANCE_PREFIXES 선언 필요

@test "TC-5: ALLOWLIST_GOVERNANCE_PREFIXES 배열이 check-no-atlassian.sh 에 존재 (ADR-100 §결정 1 wire)" {
  [ -f "${SCRIPT}" ]
  run grep -F "ALLOWLIST_GOVERNANCE_PREFIXES" "${SCRIPT}"
  [ "$status" -eq 0 ]
}
