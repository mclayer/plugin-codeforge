#!/usr/bin/env bats
# tests/scripts/check-adr-dual-block-parity/test_adr_dual_block_parity.bats
# CFP-1648 / ADR-082 Amendment 28 sub-scope 1-Q — bats fixture
# CFP-1688 / ADR-082 Amendment 30 sub-scope 1-S — single-block + H3 + Fix C bats fixture
# CFP-1734 / ADR-082 Amendment 32 sub-scope 1-U — dual-block gate (Fix A supersede)
#
# CFP-1334 §8.4 5 markers:
#   pre_impl_sha:       TC-RED 은 구현 전 상태 (git stash 후) 에서 수행됨을 증명
#   git_stash_sequence: bats teardown 에서 stash pop 복구 절차 명시
#   role_vocabulary:    DeveloperPLAgent / ADR-082 §결정 1-Q/1-S/1-U 도메인 어휘 정합
#   red_green_anchor:   TC-RED → TC-GREEN 전환 명시 주석 포함
#   platform_verified:  Windows + Unix 양 환경 python3 encoding 정합 확인
#
# pre_impl_sha: e2d0ffd1 (Phase 1 ADR-082 Amd 32 + ADR-RESERVATION committed, before Phase 2 fix)
# git_stash_sequence:
#   1. stash_push: git stash push -m "pre-impl-red-proof-cfp-1734" (RED 진정성 입증)
#   2. red_run:    bats tests/scripts/check-adr-dual-block-parity/*.bats
#                  TC-10: single-block missing-body → exit 1 (WARNING Block 2 retained, CFP-1688) = RED
#                  TC-16: parens-convention → exit 1 (FP AMENDMENTS_FRONTMATTER_ONLY, CFP-1688) = RED
#   3. stash_pop:  git stash pop → GREEN 복구
#
# TC coverage (17 TC — CFP-1688 16 TC + TC-16 신규, TC-3/9/10 BREAKING, TC-12/13 rationale):
#   TC-1:  PASS — ADR with full parity (frontmatter + body match)
#   TC-2:  WARNING — dual-block: frontmatter amendments[] entry but body section missing (exit 1)
#   TC-3:  PASS — body section present but frontmatter rows empty (degenerate, EXEMPT, exit 0)
#          [BREAKING from CFP-1688: was WARNING exit 1]
#   TC-4:  WARNING — dual-block F-DR-001 sentinel: amendment_log[] frontmatter only, body missing (exit 1)
#   TC-5:  BYPASS env respected (exit 0)
#   TC-6:  ENVIRONMENT_ERROR — Python SSOT missing → bash wrapper exit 2
#   TC-7:  red_green_anchor — RED→GREEN behavioral contract verified
#   TC-8:  platform_verified — UTF-8 stdout/stderr encoding (Windows + Unix)
#   TC-9:  PASS — single-block ADR (amendment_log[] only + H3 body, all present) — EXEMPT (Amd 32)
#          [CFP-1688: Fix A single-block mode skip; Amd 32: dual-block gate EXEMPT]
#   TC-10: PASS — single-block ADR genuinely missing body section — EXEMPT (Amd 32)
#          [BREAKING from CFP-1688: was WARNING exit 1 (Block 2 retained)]
#   TC-11: PASS — dual-block ADR regression guard (unchanged behavior)
#   TC-12: PASS — H3 body section detection — Fix B (dual-block path; single-block = EXEMPT)
#   TC-13: PASS — H4 sub-section NOT matched (bounded {2,3} guard) — Fix B
#          [rationale: single-block → EXEMPT, H4 guard still holds conceptually]
#   TC-14: PASS — dual-block ADR with H2 body (H3 addition no FP) — Fix B regression
#   TC-15: PASS — long-frontmatter ADR (>300 line) — Fix C scan cap (dual-block path)
#   TC-16: PASS — parens-convention ADR (amendments[]-only, no amendment_log[]) — EXEMPT (Amd 32)
#          [BREAKING from CFP-1688: was WARNING exit 1 AMENDMENTS_FRONTMATTER_ONLY FP]
#          [red_green_anchor: RED (pre-impl) = exit 1 FP; GREEN (post-impl) = exit 0 EXEMPT]
#
# 8 fixtures (7 existing + 1 new):
#   adr-parity-pass.md            — TC-1/TC-11/TC-14 PASS scenario
#   adr-frontmatter-only.md       — TC-2 WARNING dual-block (amendments[] frontmatter only)
#   adr-body-only.md              — TC-3 PASS EXEMPT (degenerate empty both blocks)
#   adr-amendment-log-missing.md  — TC-4 F-DR-001 sentinel scenario (dual-block)
#   adr-single-block-h3-pass.md   — TC-9/TC-12/TC-13 single-block H3 EXEMPT
#   adr-single-block-missing-body.md — TC-10 single-block EXEMPT (Amd 32)
#   adr-long-frontmatter.md       — TC-15 Fix C RED/GREEN scan cap proof (dual-block)
#   adr-parens-convention.md      — TC-16 parens-convention EXEMPT (amendments[]-only)

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
# TC-3: PASS — body section present but frontmatter rows empty (degenerate, EXEMPT)
# BREAKING (CFP-1734 Amendment 32): was WARNING exit 1 in CFP-1688.
# adr-body-only.md has amendments: [] + amendment_log: [] (both empty arrays).
# dual_block = bool([]) AND bool([]) = False → EXEMPT → trivial PASS exit 0.
# red_green_anchor: pre-impl (CFP-1688) = exit 1 BODY_ONLY; post-impl (Amd 32) = exit 0 PASS.
# ---------------------------------------------------------------------------
@test "TC-3: PASS — degenerate body-only ADR (empty both frontmatter blocks) EXEMPT (Amd 32, exit 0)" {
  # role_vocabulary: ADR-082 §결정 1-U dual-block gate — degenerate non-dual-block ADR
  # red_green_anchor: GREEN state after Amendment 32 — empty amendments[]+amendment_log[] → EXEMPT
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-body-only.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-body-only.md"

  # Exit 0 = PASS (degenerate: amendments[] empty + amendment_log[] empty → dual_block false → EXEMPT)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
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

# ===========================================================================
# CFP-1688 / ADR-082 Amendment 30 sub-scope 1-S — Fix A / Fix B / Fix C TCs
# pre_impl_sha: cc8e18628f734fbf0ca118f8f6435aa91765ca31
# ===========================================================================

# ---------------------------------------------------------------------------
# TC-9: PASS — single-block ADR (amendment_log[] only + H3 body, all present) — EXEMPT
# CFP-1688 Fix A: single-block mode skip Block1/3, Block 2 PASS.
# Amendment 32 (CFP-1734): dual-block gate — single-block → EXEMPT (no blocks run).
# Exit 0 result unchanged; rationale shifts from "Fix A single-block mode" to "EXEMPT".
# red_green_anchor: exit 0 maintained across both fixes.
# ---------------------------------------------------------------------------
@test "TC-9: PASS — single-block ADR amendment_log-only EXEMPT via dual-block gate (Amd 32, exit 0)" {
  # role_vocabulary: ADR-082 §결정 1-U dual-block gate — single-block ADR amendment_log[]-only EXEMPT
  # Amd 32: amendments[] absent → dual_block = False → early-return PASS (gate, no blocks run)
  # CFP-1688 Fix A behavior superseded: Block 2 no longer runs for single-block ADRs
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-single-block-h3-pass.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-single-block-h3-pass.md"

  # Exit 0 = PASS (single-block: dual_block gate → EXEMPT, no blocks executed)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-10: PASS — single-block ADR genuinely missing body section — EXEMPT (Amd 32)
# BREAKING (CFP-1734 Amendment 32): was WARNING exit 1 in CFP-1688 (Block 2 retained).
# Amendment 32 dual-block gate: single-block (amendment_log[]-only) → EXEMPT, Block 2 NOT run.
# F-DR-001 P0 sentinel protection preserved for dual-block ADRs (TC-4); single-block = accepted tradeoff.
# red_green_anchor: RED (pre-impl CFP-1688) = exit 1 AMENDMENT_LOG_FRONTMATTER_ONLY Amendment 2
#                  GREEN (post-impl Amd 32) = exit 0 PASS EXEMPT
# ---------------------------------------------------------------------------
@test "TC-10: PASS — single-block ADR missing body EXEMPT via dual-block gate (Amd 32, exit 0)" {
  # role_vocabulary: ADR-082 §결정 1-U dual-block gate — single-block ADR amendment_log[]-only EXEMPT
  # Amd 32: amendments[] absent → dual_block = False → early-return PASS (gate supersedes Block 2)
  # red_green_anchor: GREEN state after Amendment 32 (this TC was RED in CFP-1688)
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-single-block-missing-body.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-single-block-missing-body.md"

  # Exit 0 = PASS (single-block: dual_block gate → EXEMPT, Block 2 not executed)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-11: PASS — dual-block ADR regression guard
# Fix A: dual-block mode (amendments[] present) unchanged behavior
# ---------------------------------------------------------------------------
@test "TC-11: PASS — dual-block ADR regression guard (Fix A unchanged, exit 0)" {
  # role_vocabulary: dual-block mode — amendments[] + amendment_log[] + body H2 all present
  # red_green_anchor: dual-block path untouched by Fix A — regression guard
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-parity-pass.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-parity-pass.md"

  # Exit 0 = PASS (dual-block ADR: all 3 blocks verified, no regression from Fix A)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-12: PASS — H3 body section detection (Fix B, dual-block path only)
# Fix B: BODY_AMENDMENT_PATTERN detects ### Amendment N (H3).
# Note (Amd 32): adr-single-block-h3-pass.md is single-block → EXEMPT (gate).
# Fix B still serves the dual-block path (e.g. adr-parity-pass.md H2; TC-14).
# Exit 0 unchanged; rationale: EXEMPT (not "Fix B H3 detect parity OK").
# ---------------------------------------------------------------------------
@test "TC-12: PASS — H3 body amendment section fixture EXEMPT via dual-block gate (exit 0)" {
  # role_vocabulary: ADR-082 §결정 1-U dual-block gate — single-block fixture → EXEMPT
  # Fix B (H3 detect) retained for dual-block path; single-block = EXEMPT before Fix B logic runs
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-single-block-h3-pass.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-single-block-h3-pass.md"

  # Exit 0 = PASS (single-block → EXEMPT; Fix B H3 detection active in dual-block path)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-13: PASS — H4 sub-section NOT matched (bounded {2,3} guard) — Fix B
# Fix B: BODY_AMENDMENT_PATTERN {2,3} excludes H4 (####).
# The fixture contains "#### §D-1 적용 evidence" which is NOT extracted as amendment.
# Note (Amd 32): adr-single-block-h3-pass.md is single-block → EXEMPT (gate early-return).
# The H4 exclusion guard still holds logically; EXEMPT means no blocks run → no H4 FP possible.
# ---------------------------------------------------------------------------
@test "TC-13: PASS — H4 sub-section guard (Fix B) + EXEMPT via dual-block gate (exit 0)" {
  # role_vocabulary: H4 guard — BODY_AMENDMENT_PATTERN {2,3} upper bound; dual-block gate EXEMPT
  # Single-block → dual_block = False → EXEMPT → no BODY_ONLY_NO_LOG from H4 or any heading
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-single-block-h3-pass.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-single-block-h3-pass.md"

  # Exit 0 = PASS (single-block EXEMPT; H4 sub-sections also correctly excluded by {2,3} bound)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  # No BODY_ONLY_NO_LOG from H4 heading (EXEMPT gate, no blocks run)
  [[ "$output" != *"BODY_ONLY_NO_LOG"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-14: PASS — dual-block ADR with H2 body (Fix B regression guard)
# Fix B: adding H3 detection must not introduce new FP in existing H2-only dual-block ADRs
# ---------------------------------------------------------------------------
@test "TC-14: PASS — dual-block ADR H2 body Fix B regression guard (exit 0)" {
  # role_vocabulary: dual-block H2 body — Fix B must not FP existing behavior
  # adr-parity-pass.md uses ## Amendment N (H2) — Fix B H3 pattern must not break it
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-parity-pass.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-parity-pass.md"

  # Exit 0 = PASS (dual-block H2 ADR still passes after Fix B H3 detection added)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-15: PASS — long-frontmatter ADR (>300 line) — Fix C scan cap
# red_green_anchor: RED (unfixed cap=300) = amendment_log: never reached → empty → violations
#                  GREEN (Fix C cap=5000) = full frontmatter scanned → all entries found → PASS
# platform_verified: Korean UTF-8 path + long file parity
# ---------------------------------------------------------------------------
@test "TC-15: PASS — long-frontmatter ADR amendment_log extracted past line 300 (Fix C, exit 0)" {
  # role_vocabulary: Fix C frontmatter scan cap — amendment_log[] past line 300
  # pre_impl_sha: cc8e18628f734fbf0ca118f8f6435aa91765ca31
  # red_green_anchor:
  #   RED (unfixed): lines[:300] cap truncates at line 300, never reaches amendment_log:
  #   at line 308 → amendment_log_ids = [] → false violations:
  #     BODY_ONLY_NO_LOG: Amendment 1-20 (all 20 body sections appear log-less)
  #     CROSS_BLOCK_COUNT_MISMATCH: amendments[] 20 != amendment_log[] 0
  #   GREEN (Fix C): lines[:5000] cap → 2nd "---" delimiter at line 390 reached →
  #   all 20 amendment_log entries extracted → counts match + Block 2 parity OK → exit 0
  # platform_verified: long file (484 lines total) with ASCII content, no encoding issue
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-long-frontmatter.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-long-frontmatter.md"

  # Exit 0 = PASS (Fix C: full frontmatter scanned, all 20 amendment_log entries extracted)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  # No false BODY_ONLY_NO_LOG or CROSS_BLOCK_COUNT_MISMATCH from truncation
  [[ "$output" != *"BODY_ONLY_NO_LOG"* ]]
  [[ "$output" != *"CROSS_BLOCK_COUNT_MISMATCH"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-16: PASS — parens-convention ADR (amendments[]-only, no amendment_log[]) — EXEMPT
# NEW in CFP-1734 / Amendment 32 (sub-scope 1-U): Option A key evidence TC.
# Fixture: adr-parens-convention.md — amendments[] present + body uses `## §결정 N (Amendment M, CFP-XXX)`
#   + NO amendment_log[].
# amendments[]-only → dual_block = bool([1]) AND bool([]) = False → EXEMPT → PASS exit 0.
# CFP-1688 (pre-impl) behavior: dual-block path → Block 1 `AMENDMENTS_FRONTMATTER_ONLY` FP = RED.
# Amendment 32 (post-impl): dual-block gate → EXEMPT = GREEN.
# red_green_anchor: RED (pre-impl) = exit 1 FP; GREEN (post-impl) = exit 0 EXEMPT.
# This TC is a primary RED anchor for CFP-1334 §8.4 RED→GREEN stash proof.
# ---------------------------------------------------------------------------
@test "TC-16: PASS — parens-convention ADR amendments[]-only EXEMPT via dual-block gate (Amd 32, exit 0)" {
  # role_vocabulary: ADR-082 §결정 1-U dual-block gate — amendments[]-only ADR EXEMPT
  # red_green_anchor: GREEN state after Amendment 32 — amendments[]-only → dual_block false → EXEMPT
  # pre_impl_sha: e2d0ffd1 (before this Phase 2 fix) — running TC-16 against CFP-1688 code = exit 1 FP
  export CFP1648_ADR_GLOB_MOCK="${FIXTURES_DIR}/adr-parens-convention.md"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${FIXTURES_DIR}/adr-parens-convention.md"

  # Exit 0 = PASS (amendments[]-only: dual_block = False → EXEMPT, no AMENDMENTS_FRONTMATTER_ONLY FP)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  # No FP violations from parens-convention body (not detected by BODY_AMENDMENT_PATTERN)
  [[ "$output" != *"AMENDMENTS_FRONTMATTER_ONLY"* ]]
  [[ "$output" != *"WARNING"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-15-RED: long-frontmatter truncation behavior — Amendment 32 updated
# Under CFP-1688: cap-300 truncation → amendment_log[] not seen → BODY_ONLY_NO_LOG exit 1 = RED.
# Under Amendment 32 (CFP-1734): truncated file has amendments[] but no amendment_log[]
#   → amendments[]-only → dual_block = False → EXEMPT → exit 0.
# Fix C (cap-5000) still serves dual-block ADR-082 (TC-15 above).
# This TC now demonstrates: truncated (amendments[]-only) → EXEMPT, not policed.
# ---------------------------------------------------------------------------
@test "TC-15-RED: long-frontmatter truncated amendments[]-only EXEMPT via dual-block gate (Amd 32, exit 0)" {
  # red_green_anchor: Amendment 32 supersedes the CFP-1688 RED state:
  #   CFP-1688 RED: truncated → amendment_log[] empty → CROSS_BLOCK_COUNT_MISMATCH exit 1
  #   Amendment 32: truncated → amendments[]-only → dual_block false → EXEMPT exit 0
  # Fix C relevance preserved for TC-15 (full dual-block adr-long-frontmatter.md → PASS).
  TEMP_TRUNCATED=$(mktemp /tmp/test_cfp1688_truncated_XXXXXX.md)

  # Extract first 300 lines of long-frontmatter fixture (simulates cap-300 behavior)
  head -300 "${FIXTURES_DIR}/adr-long-frontmatter.md" > "${TEMP_TRUNCATED}"
  # Append closing --- so it forms valid ADR structure
  # amendment_log: block will be absent (starts past line 300 in original)
  echo '---' >> "${TEMP_TRUNCATED}"

  export CFP1648_ADR_GLOB_MOCK="${TEMP_TRUNCATED}"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --adr-glob="${TEMP_TRUNCATED}"

  # Exit 0 = PASS (truncated: amendments[] present but amendment_log[] absent → amendments[]-only
  #   → dual_block = False → EXEMPT. Amendment 32 gate supersedes CFP-1688 exit 1 behavior.)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]

  rm -f "${TEMP_TRUNCATED}"
}
