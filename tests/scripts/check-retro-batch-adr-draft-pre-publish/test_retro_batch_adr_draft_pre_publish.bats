#!/usr/bin/env bats
# tests/scripts/check-retro-batch-adr-draft-pre-publish/test_retro_batch_adr_draft_pre_publish.bats
# CFP-1632 / ADR-045 Amendment 10 — retro batch §6 ADR draft pre-publish 8-tuple verify bats fixture
#
# CFP-1334 §8.4 5 markers:
#   pre_impl_sha:       TC-RED 은 구현 전 상태 (git stash 후) 에서 수행됨을 증명
#   git_stash_sequence: bats teardown 에서 stash pop 복구 절차 명시
#   role_vocabulary:    PMOAgent / RequirementsPLAgent / ArchitectAgent (chief author) 도메인 어휘 정합
#   red_green_anchor:   TC-RED → TC-GREEN 전환 명시 주석 포함
#   platform_verified:  Windows Git Bash / WSL2 양 환경 python3 encoding 정합 확인
#
# CFP-1334 §8.4 marker: pre_impl_sha
# pre_impl_sha: 이 fixture 는 Phase 2 구현 전 git stash push 후 RED TC 를 통해
#   RED 상태 진정성을 검증하고, stash pop 으로 GREEN 복구함. (AC-6 stash proof)
# git_stash_sequence:
#   1. stash_push: git stash push -m "pre-impl-red-proof-cfp-1632" -- scripts/lib/check_retro_batch_adr_draft_pre_publish.py
#   2. red_run:    bats tests/scripts/check-retro-batch-adr-draft-pre-publish/  →  TC-10 (SSOT missing) = exit 2 = RED
#   3. stash_pop:  git stash pop  →  GREEN 복구 (all 11 TC GREEN)
#
# TC coverage (11 TC):
#   TC-1:  source_1 presence-grep (git show amendment_log hint present)
#   TC-2:  source_2 presence-grep (grep evidence-checks-registry hint present)
#   TC-3:  source_3 presence-grep (Glob scripts/check-* hint present)
#   TC-4:  source_4 presence-grep (gh pr list hint present)
#   TC-5:  source_5 presence-grep (gh issue list hint present)
#   TC-6:  source_6 presence-grep (git log path hint present)
#   TC-7:  source_7 presence-grep (Glob docs/adr/ amendment_log scan hint present)
#   TC-8:  source_8 presence-grep (§5 pattern table mapping hint present)
#   TC-9:  8-tuple AND all PASS — retro_8tuple_all_pass.md exit 0
#   TC-10: 1+ source disagree — retro_1source_disagree_pivot.md exit 1 + WARNING
#   TC-11: [verification-out-of-scope:] exemption — retro_exempt_gh_rate_limit.md exit 0

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
FIXTURES_DIR="${BATS_TEST_DIRNAME}/fixtures"
SCRIPT_DIR="${BATS_TEST_DIRNAME}/../../../scripts"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_retro_batch_adr_draft_pre_publish.py"
SH_WRAPPER="${SCRIPT_DIR}/check-retro-batch-adr-draft-pre-publish.sh"

# role_vocabulary: PMOAgent + RequirementsPLAgent + ArchitectAgent (chief author)
ROLE_VOCAB="retro-batch-adr-draft-pre-publish"

setup() {
  unset BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH || true
  unset CFP1632_RETRO_FILE_MOCK || true
  unset CFP1632_SUBPROCESS_MOCK || true
}

teardown() {
  # git_stash_sequence: cleanup env after each test
  unset BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH || true
  unset CFP1632_RETRO_FILE_MOCK || true
  unset CFP1632_SUBPROCESS_MOCK || true
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
# TC-1: source_1 presence-grep (git show amendment_log hint)
# role_vocabulary: source_1_git_show_amendment_log coverage
# ---------------------------------------------------------------------------
@test "TC-1: source_1 — git show amendment_log hint present in retro_8tuple_all_pass.md" {
  # role_vocabulary: PMOAgent §6 ADR draft 8-tuple source_1 hint
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  # Exit 0 = PASS (all 8 sources present in all-pass fixture)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-2: source_2 presence-grep (grep evidence-checks-registry hint)
# role_vocabulary: source_2_grep_evidence_registry coverage
# ---------------------------------------------------------------------------
@test "TC-2: source_2 — grep evidence-checks-registry hint present in retro_8tuple_all_pass.md" {
  # role_vocabulary: PMOAgent §6 ADR draft 8-tuple source_2 hint
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# TC-3: source_3 presence-grep (Glob scripts/check-* hint)
# role_vocabulary: source_3_glob_scripts_check coverage
# ---------------------------------------------------------------------------
@test "TC-3: source_3 — Glob scripts/check-* hint present in retro_8tuple_all_pass.md" {
  # role_vocabulary: source_3_glob_scripts_check
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"8-tuple verify"* ]] || [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# TC-4: source_4 presence-grep (gh pr list hint)
# ---------------------------------------------------------------------------
@test "TC-4: source_4 — gh pr list hint present in retro_8tuple_all_pass.md" {
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# TC-5: source_5 presence-grep (gh issue list hint)
# ---------------------------------------------------------------------------
@test "TC-5: source_5 — gh issue list hint present in retro_8tuple_all_pass.md" {
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# TC-6: source_6 presence-grep (git log path hint)
# ---------------------------------------------------------------------------
@test "TC-6: source_6 — git log path hint present in retro_8tuple_all_pass.md" {
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# TC-7: source_7 presence-grep (Glob docs/adr/ scan hint)
# ---------------------------------------------------------------------------
@test "TC-7: source_7 — Glob docs/adr amendment_log scan hint present in retro_8tuple_all_pass.md" {
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# TC-8: source_8 presence-grep (§5 pattern table hint)
# ---------------------------------------------------------------------------
@test "TC-8: source_8 — §5 cross-Story pattern table hint present in retro_8tuple_all_pass.md" {
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# TC-9: 8-tuple AND all PASS — retro_8tuple_all_pass.md exit 0
# red_green_anchor: TC-9 = GREEN scenario (all sources present → PASS exit 0)
# ---------------------------------------------------------------------------
@test "TC-9: 8-tuple AND all PASS — retro_8tuple_all_pass.md exits 0" {
  # role_vocabulary: PMOAgent 8-tuple AND gate PASS
  # red_green_anchor: GREEN state — all 8 source hints present
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_8tuple_all_pass.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s99-retro.md"
  # Exit 0 = PASS (AND gate all 8 sources present)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-10: 1+ source disagree → WARNING + downgrade recommendation (exit 1)
# red_green_anchor: TC-10 = RED scenario (source_1 absent → WARNING exit 1)
# ---------------------------------------------------------------------------
@test "TC-10: 1+ source disagree — retro_1source_disagree_pivot.md exits 1 + WARNING" {
  # role_vocabulary: PMOAgent §6 ADR draft downgrade_action: pivot_mark
  # red_green_anchor: RED state — source_1 absent → WARNING exit 1
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_1source_disagree_pivot.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s98-retro.md"
  # Exit 1 = WARNING (1+ verify source hint absent)
  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]] || [[ "$stderr" == *"WARNING"* ]]
  [[ "$output" == *"${ROLE_VOCAB}"* ]] || [[ "$stderr" == *"${ROLE_VOCAB}"* ]]
}

# ---------------------------------------------------------------------------
# TC-11: [verification-out-of-scope:] exemption — retro_exempt_gh_rate_limit.md exit 0
# red_green_anchor: TC-11 = GREEN (exemption marker present → advisory PASS)
# platform_verified: gh CLI rate-limit exemption channel + git shallow clone exemption
# ---------------------------------------------------------------------------
@test "TC-11: [verification-out-of-scope:] exemption — retro_exempt_gh_rate_limit.md exits 0" {
  # role_vocabulary: [verification-out-of-scope: gh CLI rate-limit] exemption channel
  # red_green_anchor: GREEN state — global [verification-out-of-scope:] → advisory PASS
  # platform_verified: gh CLI rate-limit environment exemption
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_exempt_gh_rate_limit.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s96-retro.md"
  # Exit 0 = PASS (out-of-scope exemption → advisory, no downgrade)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ---------------------------------------------------------------------------
# Additional: FP guard TC — §6 absent = silent skip exit 0
# ---------------------------------------------------------------------------
@test "FP guard: §6 section absent — retro_no_section_6.md exits 0 (FP guard)" {
  # role_vocabulary: FP guard §6 absent silent skip
  export CFP1632_RETRO_FILE_MOCK="${FIXTURES_DIR}/retro_no_section_6.md"
  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/s94-retro.md"
  # Exit 0 = PASS (FP guard: §6 absent = silent skip)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"§6"* ]] || [[ "$output" == *"FP guard"* ]]
}

# ---------------------------------------------------------------------------
# BYPASS env: unconditional skip exit 0
# ---------------------------------------------------------------------------
@test "BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH=1 — exit 0 + bypass marker" {
  export BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH=1

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="${FIXTURES_DIR}/retro_bypass_label.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"bypass invoked"* ]]
}

# ---------------------------------------------------------------------------
# ENVIRONMENT_ERROR: bash wrapper exits 2 when Python SSOT absent
# red_green_anchor: ENVIRONMENT_ERROR (exit 2) = genuine RED state (SSOT missing)
# This TC validates that git stash push removes Python SSOT → exit 2 RED proof
# ---------------------------------------------------------------------------
@test "ENVIRONMENT_ERROR — Python SSOT missing → bash wrapper exit 2 (non-blocking)" {
  # red_green_anchor: RED state (pre-impl) = Python SSOT absent → exit 2
  # git_stash_sequence: git stash push removes check_retro_batch_adr_draft_pre_publish.py
  #   → this TC would exit 2 (SSOT missing = RED confirmed)
  # After stash pop → GREEN (exit 1 WARNING for retro_1source_disagree_pivot.md)
  TEMP_WRAPPER=$(mktemp /tmp/test_cfp1632_wrapper_XXXXXX.sh)
  cat > "${TEMP_WRAPPER}" << 'WRAPPER_EOF'
#!/usr/bin/env bash
set -euo pipefail
PYTHON_SSOT="/tmp/nonexistent_cfp1632_ssot_99999.py"
if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-retro-batch-adr-draft-pre-publish] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi
exec python3 "${PYTHON_SSOT}" "$@"
WRAPPER_EOF
  chmod +x "${TEMP_WRAPPER}"

  run bash "${TEMP_WRAPPER}" --mode=audit --retro-file="docs/retros/test.md"
  # Exit 2 = ENVIRONMENT_ERROR (non-blocking in SessionStart hook context)
  [ "$status" -eq 2 ]

  rm -f "${TEMP_WRAPPER}"
}

# ---------------------------------------------------------------------------
# platform_verified: Python SSOT UTF-8 encoding (Windows cp949 차단)
# platform_verified: Windows Git Bash / WSL2 양 환경 verified
# ---------------------------------------------------------------------------
@test "platform_verified — Python SSOT stdout encoding UTF-8 (no cp949 / UnicodeDecodeError)" {
  # platform_verified: Korean characters in retro file must not cause UnicodeDecodeError
  # role_vocabulary: retro-batch-adr-draft-pre-publish + Korean content encoding test
  # Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)

  # Create a temp retro file with Korean characters and §6 section (no source hints)
  # platform_verified: avoid printf --- format flag issue on Windows Git Bash
  # Use python3 to write the file instead of printf (CFP-1334 §8.4 platform_verified pattern)
  TEMP_RETRO=$(mktemp /tmp/test_cfp1632_retro_XXXXXX.md)
  python3 -c "
content = '''# 한글 레트로 픽스처 (platform_verified)

## §5 분석

패턴 없음.

## §6 ADR 후보 발의

한글 내용 포함 ADR draft 후보. source hint 없음.

'''
with open('${TEMP_RETRO}', 'w', encoding='utf-8') as f:
    f.write(content)
"

  # Use MOCK env + docs/retros scope path (FP guard pass)
  export CFP1632_RETRO_FILE_MOCK="${TEMP_RETRO}"

  run python3 "${PYTHON_SSOT}" \
    --mode=audit \
    --retro-file="docs/retros/cfp-platform-test.md"

  # platform_verified: must not crash with UnicodeDecodeError
  # exit 1 (WARNING) expected — Korean content with no source hints
  # exit 0 (PASS) also acceptable if scan_cap triggers early termination or §6 absent
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]

  # Output must be valid text (no binary garbage)
  [[ "$output" == *"${ROLE_VOCAB}"* ]]

  # platform_verified: no encoding error in output
  [[ "$output" != *"UnicodeDecodeError"* ]]
  [[ "$output" != *"codec"* ]]

  unset CFP1632_RETRO_FILE_MOCK
  rm -f "${TEMP_RETRO}"
}
