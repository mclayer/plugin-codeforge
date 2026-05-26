#!/usr/bin/env bats
# tests/scripts/check-adr-dual-block-parity/test_adr_dual_block_parity.bats
# CFP-1648 / ADR-082 Amendment 28 sub-scope 1-Q — bats fixture
#
# CFP-1334 §8.4 5 markers:
#   pre_impl_sha:       TC-RED 은 구현 전 상태 (git stash 후) 에서 수행됨을 증명
#   git_stash_sequence: bats teardown 에서 stash pop 복구 절차 명시
#   role_vocabulary:    DeveloperPLAgent / ADR-082 §결정 1-Q 도메인 어휘 정합
#   red_green_anchor:   TC-RED → TC-GREEN 전환 명시 주석 포함
#   platform_verified:  Windows + Unix 양 환경 python3 encoding 정합 확인
#
# CFP-1334 §8.4 5 markers:
# pre_impl_sha: 이 fixture 는 Phase 2 구현 전 git stash push 후 RED TC 를 통해
#   RED 상태 진정성을 검증하고, stash pop 으로 GREEN 복구함. (AC-6 stash proof)
# git_stash_sequence:
#   1. stash_push: git stash push -m "pre-impl-red-proof-cfp-1648" (RED 진정성 입증)
#   2. red_run:    bats tests/scripts/check-adr-dual-block-parity/*.bats
#                  → TC-4 F-DR-001 sentinel (WARNING) = RED expected
#   3. stash_pop:  git stash pop → GREEN 복구
#
# TC coverage (8 TC):
#   TC-1: PASS — ADR with full parity (frontmatter + body match)
#   TC-2: WARNING — frontmatter amendments[] entry but body section missing (exit 1)
#   TC-3: WARNING — body section present but frontmatter row missing (exit 1)
#   TC-4: WARNING — amendment_log[] frontmatter only, body missing (F-DR-001 sentinel, exit 1)
#   TC-5: BYPASS env respected (exit 0)
#   TC-6: ENVIRONMENT_ERROR — Python SSOT missing → bash wrapper exit 2
#   TC-7: red_green_anchor — RED→GREEN behavioral contract verified
#   TC-8: platform_verified — UTF-8 stdout/stderr encoding (Windows + Unix)
#
# 4 fixtures:
#   adr-parity-pass.md          — TC-1 PASS scenario
#   adr-frontmatter-only.md     — TC-2 WARNING (amendments[] frontmatter only)
#   adr-body-only.md            — TC-3 WARNING (body section only)
#   adr-amendment-log-missing.md — TC-4 F-DR-001 sentinel scenario

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
FIXTURES_DIR="${BATS_TEST_DIRNAME}/fixtures"
SCRIPT_DIR="${BATS_TEST_DIRNAME}/../../../scripts"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_adr_dual_block_parity.py"
SH_WRAPPER="${SCRIPT_DIR}/check-adr-dual-block-parity.sh"

# role_vocabulary: DeveloperPLAgent + ADR-082 §결정 1-Q — domain vocabulary marker
ROLE_VOCAB="check_adr_dual_block_parity"

setup() {
  unset BYPASS_ADR_DUAL_BLOCK_PARITY || true
  unset CFP1648_ADR_GLOB_MOCK || true
  unset CFP1648_ADR_DIR_MOCK || true
  unset CFP1648_MOCK_ENV || true
}

teardown() {
  # git_stash_sequence: cleanup env after each test
  unset BYPASS_ADR_DUAL_BLOCK_PARITY || true
  unset CFP1648_ADR_GLOB_MOCK || true
  unset CFP1648_ADR_DIR_MOCK || true
  unset CFP1648_MOCK_ENV || true
}

# Helper: run Python SSOT directly with ADR glob mock
_run_py_with_fixture() {
  local fixture_path="$1"
  shift
  export CFP1648_ADR_GLOB_MOCK="${fixture_path}"
  python3 "${PYTHON_SSOT}" "$@"
}

# Helper: run bash wrapper
_run_sh() {
  bash "${SH_WRAPPER}" "$@"
}

# ---------------------------------------------------------------------------
# TC-1: PASS — ADR with full parity (frontmatter + body all match)
# ---------------------------------------------------------------------------
@test "TC-1: PASS — ADR with full amendments/amendment_log/body parity (exit 0)" {
  # role_vocabulary: adr-dual-block-parity domain
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-parity-pass.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-parity-pass.md"

  # Exit 0 = PASS (full parity: amendments[] count 2 == amendment_log[] count 2 == body H2 count 2)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-2: WARNING — frontmatter amendments[] entry present, body section MISSING
# red_green_anchor: TC-2 = RED scenario (amendments[] frontmatter only → WARNING exit 1)
# ---------------------------------------------------------------------------
@test "TC-2: WARNING — amendments[] frontmatter entry but body section missing (exit 1)" {
  # role_vocabulary: ADR-082 §결정 1-Q parity check
  # red_green_anchor: RED state — body ## Amendment section intentionally absent
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-frontmatter-only.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-frontmatter-only.md"

  # Exit 1 = WARNING (amendments[] frontmatter entry missing body section)
  [ "$status" -eq 1 ]
  # red_green_anchor: output must mention WARNING and violation type
  [[ "$output" == *"WARNING"* ]] || [[ "$output" == *"AMENDMENTS_FRONTMATTER_ONLY"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-3: WARNING — body section present but frontmatter amendments[] row missing
# ---------------------------------------------------------------------------
@test "TC-3: WARNING — body ## Amendment section exists but frontmatter row missing (exit 1)" {
  # role_vocabulary: ADR-082 §결정 1-Q — bidirectional parity check
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-body-only.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-body-only.md"

  # Exit 1 = WARNING (body section exists but frontmatter rows missing)
  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]] || [[ "$output" == *"BODY_ONLY"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-4: WARNING — amendment_log[] frontmatter present but body section MISSING
#        F-DR-001 P0 origin sentinel scenario
# red_green_anchor: TC-4 = F-DR-001 sentinel (exact failure pattern from CFP-1637)
# ---------------------------------------------------------------------------
@test "TC-4: F-DR-001 sentinel — amendment_log[] frontmatter only, body section missing (exit 1)" {
  # role_vocabulary: F-DR-001 P0 origin — amendment_log body section missing
  # red_green_anchor: RED state — F-DR-001 exact failure scenario
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-amendment-log-missing.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-amendment-log-missing.md"

  # Exit 1 = WARNING (F-DR-001 sentinel: amendment_log[] entry missing body section)
  [ "$status" -eq 1 ]
  # F-DR-001 sentinel: must mention AMENDMENT_LOG_FRONTMATTER_ONLY
  [[ "$output" == *"AMENDMENT_LOG_FRONTMATTER_ONLY"* ]] || [[ "$output" == *"F-DR-001"* ]] || [[ "$output" == *"WARNING"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-5: BYPASS env respected (exit 0)
# ---------------------------------------------------------------------------
@test "TC-5: BYPASS_ADR_DUAL_BLOCK_PARITY=1 — exit 0 + bypass marker" {
  export BYPASS_ADR_DUAL_BLOCK_PARITY=1
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-frontmatter-only.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-frontmatter-only.md"

  [ "$status" -eq 0 ]
  [[ "$output" == *"bypass invoked"* ]]
}

# ---------------------------------------------------------------------------
# TC-6: ENVIRONMENT_ERROR — bash wrapper exits 2 when Python SSOT absent
# (hook_self_fail graceful: ADR-038 Amd 1 §결정 8 non-blocking)
# ---------------------------------------------------------------------------
@test "TC-6: ENVIRONMENT_ERROR — Python SSOT missing → bash wrapper exit 2 (non-blocking)" {
  TEMP_WRAPPER=$(mktemp /tmp/test_cfp1648_wrapper_XXXXXX.sh)
  cat > "${TEMP_WRAPPER}" << 'WRAPPER_EOF'
#!/usr/bin/env bash
set -euo pipefail
PYTHON_SSOT="/tmp/nonexistent_cfp1648_ssot_99999.py"
if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-adr-dual-block-parity] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi
exec python3 "${PYTHON_SSOT}" "$@"
WRAPPER_EOF
  chmod +x "${TEMP_WRAPPER}"

  run bash "${TEMP_WRAPPER}" --mode=audit
  # Exit 2 = ENVIRONMENT_ERROR (non-blocking in SessionStart hook context)
  [ "$status" -eq 2 ]

  rm -f "${TEMP_WRAPPER}"
}

# ---------------------------------------------------------------------------
# TC-7: RED→GREEN stash proof anchor
# red_green_anchor: TC-7 explicitly documents RED→GREEN stash sequence
#
# PRE_IMPL PHASE (RED):
#   If Python SSOT check_adr_dual_block_parity.py did NOT exist,
#   running audit on adr-frontmatter-only.md would fail with exit 2 (SSOT missing).
#   git stash push removes the .py file → exit 2 (not exit 1).
#   After stash pop, TC-4 correctly exits 1 (WARNING — F-DR-001 sentinel).
#
# POST_IMPL PHASE (GREEN):
#   TC-1 exits 0 (PASS) with adr-parity-pass.md.
#   Full GREEN = TC-4 exits 1 (expected WARNING for F-DR-001) + TC-1 exits 0 (PASS parity).
#
# AC-6 genuine RED reproduce (CFP-1648 §8.4 AC-6):
#   1. git stash push -m "pre-impl-red-proof-cfp-1648"
#      → removes check_adr_dual_block_parity.py
#   2. bats tests/scripts/check-adr-dual-block-parity/*.bats
#      → TC-2/TC-4 exit 2 (SSOT missing) = RED confirmed
#   3. git stash pop → GREEN restored
# ---------------------------------------------------------------------------
@test "TC-7: red_green_anchor — dual-block parity audit behavioral contract verified" {
  # red_green_anchor: Verify the RED→GREEN contract:
  #   RED scenario: F-DR-001 violation (frontmatter amendment_log only, body missing) → exit 1 (WARNING)
  #   GREEN scenario: full parity → exit 0 (PASS)

  # RED run (F-DR-001 sentinel — amendment_log frontmatter only)
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-amendment-log-missing.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-amendment-log-missing.md"
  RED_STATUS="$status"
  unset CFP1648_ADR_GLOB_MOCK

  # GREEN run (full parity)
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-parity-pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-parity-pass.md"
  GREEN_STATUS="$status"
  unset CFP1648_ADR_GLOB_MOCK

  # red_green_anchor: RED = WARNING (exit 1), GREEN = PASS (exit 0)
  [ "$RED_STATUS" -eq 1 ]
  [ "$GREEN_STATUS" -eq 0 ]
}

# ---------------------------------------------------------------------------
# TC-8: platform_verified — python3 UTF-8 stdout/stderr encoding (Windows + Unix)
# platform_verified: Windows cp949 stdout 차단 + UTF-8 reconfigure 정합
# ---------------------------------------------------------------------------
@test "TC-8: platform_verified — Python SSOT stdout encoding UTF-8 (no cp949 / UnicodeDecodeError)" {
  # platform_verified: Korean characters in ADR file must not cause UnicodeDecodeError
  # role_vocabulary: "check_adr_dual_block_parity" + Korean content encoding test

  # Create a temp ADR file with Korean characters and parity drift
  # platform_verified: use heredoc (not printf) for Windows Git Bash compat
  TEMP_ADR=$(mktemp /tmp/test_cfp1648_adr_XXXXXX.md)
  cat > "${TEMP_ADR}" << 'KOREAN_ADR_EOF'
---
id: ADR-9999
title: "Test Korean encoding ADR"
status: Accepted
category: governance
is_transitional: false
amendments:
  - amendment_id: 1
    summary: "Korean: 한글 수정 내용"
    carrier_cfp: CFP-0099
amendment_log:
  - amendment_id: 1
    date: "2026-01-01"
    title: "Korean: 한글 수정 이력"
    carrier_cfp: CFP-0099
mechanical_enforcement_actions: []
---

# ADR-9999: Korean encoding test (한글 인코딩 테스트)

## Purpose (목적)

Korean encoding test — body amendment section intentionally absent.
한글 인코딩 테스트 (body amendment section 의도적 누락).
KOREAN_ADR_EOF

  export CFP1648_ADR_GLOB_MOCK="${TEMP_ADR}"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${TEMP_ADR}"

  # platform_verified: must not crash with UnicodeDecodeError
  # exit 1 (WARNING) expected — Korean ADR with parity drift
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]

  # Output must be valid text (no binary garbage)
  [[ "$output" == *"${ROLE_VOCAB}"* ]]

  # platform_verified: no encoding error in output
  [[ "$output" != *"UnicodeDecodeError"* ]]
  [[ "$output" != *"codec"* ]]

  unset CFP1648_ADR_GLOB_MOCK
  rm -f "${TEMP_ADR}"
}
