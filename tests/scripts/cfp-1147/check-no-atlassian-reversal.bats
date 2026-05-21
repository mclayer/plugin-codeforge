#!/usr/bin/env bats
# tests/scripts/cfp-1147/check-no-atlassian-reversal.bats
# CFP-1147 Phase 2 — check-no-atlassian.sh 역전 검증 (TDD)
# ADR-099 §결정 1/2/3 mechanical 검증
#
# TC map:
#   TC-1: grep 패턴에 mcp__atlassian 토큰 부재 (Layer 2 역전 — 평문만)
#   TC-2: ADR-099 governance file — allowlist 통과 (exit 0)
#   TC-3: 기존 allowlist file (CHANGELOG.md) — atlassian 참조 통과 (exit 0)
#   TC-4: allowlist 외 fixture file 의 평문 atlassian → warning (exit 1) + 메시지
#   TC-5: evidence-checks-registry.yaml 에 check-atlassian-allow entry 존재
#
# ADR refs:
#   ADR-099: check-no-atlassian.sh 역전 + Atlassian-allow 재정의
#   ADR-060: evidence-enforceable promotion framework — warning tier
#   ADR-061: external .py 불요 (bash script 대상)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SCRIPT="${WORKTREE_ROOT}/scripts/check-no-atlassian.sh"
REGISTRY="${WORKTREE_ROOT}/docs/evidence-checks-registry.yaml"

# ────────────────────────────── setup / teardown ─────────────────────────────

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1147-unused}"
}

# ─────────────────── TC-1: grep 패턴에 mcp__atlassian 토큰 부재 ──────────────

@test "TC-1: grep 패턴에 mcp__atlassian 토큰 없음 — Layer 2 역전 (ADR-099 §결정 1 Layer 2)" {
  [ -f "${SCRIPT}" ]
  # 주석(#) 으로 시작하지 않는 실제 grep 명령 라인에 mcp__atlassian 이 없어야 함
  # 역전 전: grep -rEn 'atlassian|Confluence|Jira|mcp__atlassian' → 역전 후 mcp__atlassian 제거
  run grep -E "^[^#]*grep[^#]*mcp__atlassian" "${SCRIPT}"
  # 역전 후 실제 grep 명령에 mcp__atlassian 없어야 → match 없어야 → exit 1 (non-zero)
  [ "$status" -ne 0 ]
}

# ─────── TC-2: ADR-099 governance file — allowlist 통과 (exit 0) ─────────────

@test "TC-2: docs/adr/ADR-099 governance file — atlassian 평문 allowlist 통과 (exit 0)" {
  [ -f "${SCRIPT}" ]
  # ADR-099 파일이 allowlist 에 포함 → exit 0 이어야 함
  # (ADR-099 파일은 atlassian 평문 다수 포함)
  run bash "${SCRIPT}"
  [ "$status" -eq 0 ]
}

# ───────── TC-3: 기존 allowlist (CHANGELOG.md) — atlassian 참조 통과 ──────────

@test "TC-3: CHANGELOG.md (기존 allowlist) atlassian 참조 — exit 0 통과" {
  [ -f "${SCRIPT}" ]
  # CHANGELOG.md 는 기존 11-file allowlist 에 포함 → atlassian 참조 있어도 exit 0
  run bash "${SCRIPT}"
  [ "$status" -eq 0 ]
}

# ─── TC-4: allowlist 외 fixture 의 평문 atlassian → warning (exit 1) ──────────

@test "TC-4: allowlist 외 임시 파일에 atlassian 평문 → exit 1 (warning tier)" {
  [ -f "${SCRIPT}" ]

  # 프로젝트 루트 아래 임시 .md 파일 생성 (bats TEST_TMP 는 /tmp 등 외부 → 검색 대상 외)
  # WORKTREE_ROOT 안에 생성해야 grep 검색 대상에 포함됨
  local fixture_file="${WORKTREE_ROOT}/tmp-cfp1147-test-fixture.md"
  printf '# 테스트 fixture\nThis file references atlassian in a non-allowlisted location.\n' \
    > "${fixture_file}"

  run bash "${SCRIPT}"
  local exit_code="$status"

  # cleanup
  rm -f "${fixture_file}"

  [ "$exit_code" -eq 1 ]
}

# ─── TC-5: evidence-checks-registry.yaml 에 check-atlassian-allow entry 존재 ───

@test "TC-5: evidence-checks-registry.yaml — check-atlassian-allow entry 존재 (ADR-099 §결정 3)" {
  [ -f "${REGISTRY}" ]
  run grep -F "name: check-atlassian-allow" "${REGISTRY}"
  [ "$status" -eq 0 ]
}

# ─── TC-6: check-atlassian-allow entry 의 owner_adr = ADR-099 ────────────────

@test "TC-6: check-atlassian-allow entry owner_adr = ADR-099 (ADR-060 registry 정합)" {
  [ -f "${REGISTRY}" ]
  run grep -F "owner_adr: ADR-099" "${REGISTRY}"
  [ "$status" -eq 0 ]
}

# ─── TC-7: allowlist 외 exit 1 출력에 warning 메시지 포함 ────────────────────

@test "TC-7: allowlist 외 atlassian 발견 시 출력에 Atlassian-allow warning 메시지 포함" {
  [ -f "${SCRIPT}" ]

  local fixture_file="${WORKTREE_ROOT}/tmp-cfp1147-test-fixture2.md"
  printf '# 테스트\natlassian reference outside allowlist\n' > "${fixture_file}"

  run bash "${SCRIPT}"
  local exit_code="$status"
  local out="$output"

  rm -f "${fixture_file}"

  [ "$exit_code" -eq 1 ]
  # 역전 후 메시지는 "atlassian 잔재" 가 아니라 "Atlassian-allow" / warning 의미 메시지여야 함
  [[ "$out" =~ Atlassian-allow|atlassian-allow|warning|Warning ]]
}
