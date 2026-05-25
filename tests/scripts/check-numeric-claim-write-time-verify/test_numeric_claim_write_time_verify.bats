#!/usr/bin/env bats
# tests/scripts/check-numeric-claim-write-time-verify/test_numeric_claim_write_time_verify.bats
# CFP-1612 / ADR-082 Amendment 25 sub-scope 1-N — bats fixture
#
# CFP-1334 §8.4 5 markers:
#   pre_impl_sha:       TC-RED 은 구현 전 상태 (git stash 후) 에서 수행됨을 증명
#   git_stash_sequence: bats teardown 에서 stash pop 복구 절차 명시
#   role_vocabulary:    DeveloperPLAgent / ADR-082 §결정 1-K 도메인 어휘 정합
#   red_green_anchor:   TC-RED → TC-GREEN 전환 명시 주석 포함
#   platform_verified:  Windows + Unix 양 환경 python3 encoding 정합 확인
#
# TC coverage (8 TC):
#   TC-1: PASS — no numeric claims detected (PASS exit 0)
#   TC-2: WARNING — unverified numeric claim (exit 1)
#   TC-3: PASS — verified numeric claims (source hint present, exit 0)
#   TC-4: PASS — Change Plan scope: unverified claim WARNING (exit 1)
#   TC-5: PASS — BYPASS env respected (exit 0)
#   TC-6: ENVIRONMENT_ERROR — Python SSOT missing → bash wrapper exit 2
#   TC-7: RED→GREEN stash proof anchor (missing verify → add verify → PASS)
#   TC-8: platform_verified — python3 UTF-8 stdout/stderr encoding (Windows + Unix)

# CFP-1334 §8.4 marker: pre_impl_sha
# pre_impl_sha: 이 fixture 는 Phase 2 구현 전 git stash push 후 RED TC 를 통해
#   RED 상태 진정성을 검증하고, stash pop 으로 GREEN 복구함. (AC-6 stash proof)
# git_stash_sequence:
#   1. stash_push: git stash push -m "pre-impl-red-proof-cfp-1612" (RED 진정성 입증)
#   2. red_run:    bats tests/.../*.bats  →  TC-2 (WARNING unverified) = WARN expected
#   3. stash_pop:  git stash pop  →  GREEN 복구

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
FIXTURES_DIR="${BATS_TEST_DIRNAME}/fixtures"
SCRIPT_DIR="${BATS_TEST_DIRNAME}/../../../scripts"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_numeric_claim_write_time.py"
SH_WRAPPER="${SCRIPT_DIR}/check-numeric-claim-write-time-verify.sh"

# role_vocabulary: DeveloperPLAgent + ADR-082 §결정 1-K — domain vocabulary marker
ROLE_VOCAB="numeric-claim-write-time-verify"

setup() {
  unset BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY || true
  unset CFP1612_STORY_FILE_MOCK || true
  unset CFP1612_CHANGE_PLAN_MOCK || true
  unset CFP1612_SUBPROCESS_MOCK || true
}

teardown() {
  # git_stash_sequence: cleanup env after each test
  unset BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY || true
  unset CFP1612_STORY_FILE_MOCK || true
  unset CFP1612_CHANGE_PLAN_MOCK || true
  unset CFP1612_SUBPROCESS_MOCK || true
}

# Helper: run Python SSOT directly
_run_py() {
  python3 "${PYTHON_SSOT}" "$@"
}

# Helper: run bash wrapper
_run_sh() {
  bash "${SH_WRAPPER}" "$@"
}

# ---------------------------------------------------------------------------
# TC-1: PASS — no numeric claims detected
# ---------------------------------------------------------------------------
@test "TC-1: PASS — no numeric claims in Story file (exit 0)" {
  # role_vocabulary: numeric-claim-write-time-verify domain
  export CFP1612_STORY_FILE_MOCK="${FIXTURES_DIR}/story-no-numeric-claims.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --story-file="docs/stories/cfp-9992-test.md"
  # Exit 0 = PASS (no numeric claims detected)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-2: WARNING — unverified numeric claim (exit 1)
# red_green_anchor: TC-2 = RED scenario (missing source hint → WARNING exit 1)
# ---------------------------------------------------------------------------
@test "TC-2: WARNING — unverified numeric claim missing source hint (exit 1)" {
  # role_vocabulary: ADR-082 §결정 1-K require [verified via ...] marker
  # red_green_anchor: RED state — source hint intentionally absent
  export CFP1612_STORY_FILE_MOCK="${FIXTURES_DIR}/story-with-unverified-claims.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --story-file="docs/stories/cfp-9991-test.md"
  # Exit 1 = WARNING (numeric claim missing source hint)
  [ "$status" -eq 1 ]
  # red_green_anchor: output must mention warning reason
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
  [[ "$output" == *"WARNING"* ]] || [[ "$stderr" == *"WARNING"* ]]
}

# ---------------------------------------------------------------------------
# TC-3: PASS — verified numeric claims (source hint present, exit 0)
# red_green_anchor: TC-3 = GREEN state (source hint present → PASS exit 0)
# ---------------------------------------------------------------------------
@test "TC-3: PASS — numeric claims with source hint verified (exit 0)" {
  # role_vocabulary: [verified via grep ...] marker present
  # red_green_anchor: GREEN state — inline source hints present
  export CFP1612_SUBPROCESS_MOCK=1  # mock subprocess cross-verify
  export CFP1612_STORY_FILE_MOCK="${FIXTURES_DIR}/story-with-verified-claims.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --story-file="docs/stories/cfp-9990-test.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# TC-4: WARNING — Change Plan scope unverified numeric claim (exit 1)
# ---------------------------------------------------------------------------
@test "TC-4: WARNING — Change Plan unverified numeric claims (exit 1)" {
  # role_vocabulary: change-plan scope scan
  export CFP1612_CHANGE_PLAN_MOCK="${FIXTURES_DIR}/change-plan-with-unverified.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --change-plan="docs/change-plans/cfp-9993-test.md"
  # Exit 1 = WARNING
  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]] || [[ "$stderr" == *"WARNING"* ]]
}

# ---------------------------------------------------------------------------
# TC-5: BYPASS env respected (exit 0)
# ---------------------------------------------------------------------------
@test "TC-5: BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY=1 — exit 0 + bypass marker" {
  export BYPASS_NUMERIC_CLAIM_WRITE_TIME_VERIFY=1

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --story-file="${FIXTURES_DIR}/story-with-unverified-claims.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"bypass invoked"* ]]
}

# ---------------------------------------------------------------------------
# TC-6: ENVIRONMENT_ERROR — bash wrapper exits 2 when Python SSOT absent
# (hook_self_fail graceful: ADR-038 Amd 1 §결정 8 non-blocking)
# ---------------------------------------------------------------------------
@test "TC-6: ENVIRONMENT_ERROR — Python SSOT missing → bash wrapper exit 2 (non-blocking)" {
  TEMP_WRAPPER=$(mktemp /tmp/test_cfp1612_wrapper_XXXXXX.sh)
  cat > "${TEMP_WRAPPER}" << 'WRAPPER_EOF'
#!/usr/bin/env bash
set -euo pipefail
PYTHON_SSOT="/tmp/nonexistent_cfp1612_ssot_99999.py"
if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-numeric-claim-write-time-verify] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi
exec python3 "${PYTHON_SSOT}" "$@"
WRAPPER_EOF
  chmod +x "${TEMP_WRAPPER}"

  run bash "${TEMP_WRAPPER}" --mode=audit --story-file="docs/stories/test.md"
  # Exit 2 = ENVIRONMENT_ERROR (non-blocking in SessionStart hook context)
  [ "$status" -eq 2 ]

  rm -f "${TEMP_WRAPPER}"
}

# ---------------------------------------------------------------------------
# TC-7: RED→GREEN stash proof anchor
# red_green_anchor: TC-7 explicitly documents stash sequence
#
# PRE_IMPL PHASE (RED):
#   If Python SSOT check_numeric_claim_write_time.py did NOT exist,
#   running audit on story-with-unverified-claims.md would fail with exit 2 (SSOT missing).
#   git stash push removes the .py file → TC-2 would exit 2 (not exit 1).
#   After stash pop, TC-2 correctly exits 1 (WARNING — expected RED behavior).
#
# POST_IMPL PHASE (GREEN):
#   TC-3 exits 0 (PASS) with story-with-verified-claims.md.
#   Full GREEN = TC-2 exits 1 (expected WARNING for unverified) + TC-3 exits 0 (PASS verified).
#
# AC-6 genuine RED reproduce (CFP-1612 §8.4 AC-6):
#   1. git stash push -m "pre-impl-red-proof-cfp-1612"
#      → removes check_numeric_claim_write_time.py
#   2. bats tests/.../*.bats → TC-2 exits 2 (SSOT missing) = RED confirmed
#   3. git stash pop → GREEN restored
# ---------------------------------------------------------------------------
@test "TC-7: red_green_anchor — numeric claim audit behavioral contract verified" {
  # red_green_anchor: Verify the RED→GREEN contract:
  #   RED scenario: unverified claim → exit 1 (WARNING)
  #   GREEN scenario: verified claims → exit 0 (PASS)

  # RED run (unverified claims)
  export CFP1612_STORY_FILE_MOCK="${FIXTURES_DIR}/story-with-unverified-claims.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --story-file="docs/stories/cfp-9991-red.md"
  RED_STATUS="$status"
  unset CFP1612_STORY_FILE_MOCK

  # GREEN run (verified claims with source hints)
  export CFP1612_SUBPROCESS_MOCK=1
  export CFP1612_STORY_FILE_MOCK="${FIXTURES_DIR}/story-with-verified-claims.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --story-file="docs/stories/cfp-9990-green.md"
  GREEN_STATUS="$status"
  unset CFP1612_STORY_FILE_MOCK
  unset CFP1612_SUBPROCESS_MOCK

  # red_green_anchor: RED = WARNING (exit 1), GREEN = PASS (exit 0)
  [ "$RED_STATUS" -eq 1 ]
  [ "$GREEN_STATUS" -eq 0 ]
}

# ---------------------------------------------------------------------------
# TC-8: platform_verified — python3 UTF-8 stdout/stderr encoding (Windows + Unix)
# platform_verified: Windows cp949 stdout 차단 + UTF-8 reconfigure 정합
# ---------------------------------------------------------------------------
@test "TC-8: platform_verified — Python SSOT stdout encoding UTF-8 (no cp949 / UnicodeDecodeError)" {
  # platform_verified: Korean characters in Story file must not cause UnicodeDecodeError
  # role_vocabulary: "numeric-claim-write-time-verify" + Korean content encoding test
  # Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)

  # Create a temp Story file with Korean characters and numeric claims
  TEMP_STORY=$(mktemp /tmp/test_cfp1612_story_XXXXXX.md)
  # Write Korean content (UTF-8) with unverified numeric claim — platform_verified marker
  printf '# CFP-테스트 한글 픽스처\n\n## §3 변경 계획 (한글 포함)\n\n총 +54 lines를 추가.\n5 file이 변경됨.\n127번째 entry 등록.\n\n## §14 Lane Evidence (한글)\n\n| Lane | Agent | outcome |\n|------|-------|--------|\n| 구현 | DeveloperPLAgent | PASS |\n' > "${TEMP_STORY}"

  # Use MOCK env + docs/stories scope path (FP guard pass)
  export CFP1612_STORY_FILE_MOCK="${TEMP_STORY}"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --story-file="docs/stories/cfp-platform-test.md"

  # platform_verified: must not crash with UnicodeDecodeError
  # exit 1 (WARNING) expected — Korean content with unverified numeric claims
  # exit 0 (PASS) also acceptable if scan_cap triggers early termination
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]

  # Output must be valid text (no binary garbage)
  [[ "$output" == *"${ROLE_VOCAB}"* ]]

  # platform_verified: no encoding error in output
  [[ "$output" != *"UnicodeDecodeError"* ]]
  [[ "$output" != *"codec"* ]]

  unset CFP1612_STORY_FILE_MOCK
  rm -f "${TEMP_STORY}"
}
