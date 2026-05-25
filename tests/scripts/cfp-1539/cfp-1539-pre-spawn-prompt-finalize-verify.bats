#!/usr/bin/env bats
# tests/scripts/cfp-1539/cfp-1539-pre-spawn-prompt-finalize-verify.bats
# CFP-1539 Wave 2 / CFP-FU-A Wave 2 — pre-spawn-prompt-finalize-verify mechanical lint TDD
# RED→GREEN stash proof pattern (CFP-1334 §8.4 / ADR-082 §결정 11.A precedent)
#
# Detection scope:
#   [USER-UTTERANCE-VERBATIM] block 내 pre_spawn_prompt_finalize_verified: <true|false> field presence
#
# Bats fixture 9 TC + 2 PREREQ (RED→GREEN stash proof target: 11/11 GREEN):
#   TC-1: PRESENCE — valid field (true) in block → PASS
#   TC-2: ABSENCE — block without field → [WARN-FIELD-ABSENT]
#   TC-3: INVALID-VALUE — field present but value != true|false → [WARN-FIELD-INVALID]
#   TC-4: SKIP-NON-STORY — non-Story file → silent skip
#   TC-4-negative: non-Story fixture 에서 exit 1 절대 발화 금지
#   TC-5: SKIP-TEMPLATES — file under templates/** → silent skip (FP guard 1)
#   TC-6: SKIP-TESTS — file under tests/** → silent skip (FP guard 2)
#   TC-7: DISCRIMINATING — present + absent blocks → absent wins (genuine fail)
#   TC-8: REGRESSION-GUARD — multiple blocks all field-present → PASS
#   TC-9: BYPASS-ENV — HOTFIX_BYPASS_PRE_SPAWN_PROMPT_FINALIZE_VERIFY=1 → immediate exit 0
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — positive + negative 2-assertion per TC
#   Layer 3 — 임시 fixture 파일 사용 (실제 repo 의존 금지)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# SSOT: ADR-082 Amendment 19 §결정 1 layer 1 sub-scope (1-I)
# Change-plan: <internal-docs>/plugin-codeforge/change-plans/cfp-1539-fu-a-wave2-pre-spawn-prompt-finalize-verify.md
# Precedent byte-pattern: tests/scripts/cfp-1489/cfp-1489-spawn-prompt-head-pin.bats

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
LINT_SCRIPT="${WORKTREE_ROOT}/scripts/lib/check_pre_spawn_prompt_finalize_verify.py"

# ─────────────────────────────────── sandbox setup ───────────────────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
}

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  export CBL_SKIP_ISSUE_CREATE=1
  # Ensure bypass env is NOT set (avoid contamination)
  unset HOTFIX_BYPASS_PRE_SPAWN_PROMPT_FINALIZE_VERIFY
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1539-unused}"
}

# ─────────────────────────────── prerequisite checks ─────────────────────────

@test "PREREQ: lint Python script 존재 확인" {
  [ -f "$LINT_SCRIPT" ]
}

@test "PREREQ: python3 사용 가능 확인" {
  command -v python3
}

# ─────────────────────────────── helper: fixture 생성 함수 ────────────────────

# fixture: Story file path helper (docs/stories/ prefix 필요)
make_story_fixture_path() {
  local base_dir="$1"
  local filename="$2"
  local story_dir="${base_dir}/docs/stories"
  mkdir -p "$story_dir"
  echo "${story_dir}/${filename}"
}

# fixture: [USER-UTTERANCE-VERBATIM] block + valid field (true)
make_fixture_field_present_true() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# Story CFP-1539 test fixture

[USER-UTTERANCE-VERBATIM]
진행해 (Wave 2 mechanical wire)
pre_spawn_prompt_finalize_verified: true
[/USER-UTTERANCE-VERBATIM]

## 본문
FIXTURE
}

# fixture: [USER-UTTERANCE-VERBATIM] block + valid field (false)
make_fixture_field_present_false() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# Story CFP-1539 test fixture (false value)

[USER-UTTERANCE-VERBATIM]
진행해
pre_spawn_prompt_finalize_verified: false
[/USER-UTTERANCE-VERBATIM]
FIXTURE
}

# fixture: [USER-UTTERANCE-VERBATIM] block WITHOUT field (WARN-FIELD-ABSENT 대상)
make_fixture_field_absent() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# Story CFP-1539 test fixture (field absent)

[USER-UTTERANCE-VERBATIM]
진행해 (pre_spawn_prompt_finalize_verified field 없음 — WARN-FIELD-ABSENT 대상)
[/USER-UTTERANCE-VERBATIM]

## Worktree directive
FIXTURE
}

# fixture: [USER-UTTERANCE-VERBATIM] block + INVALID value (not true|false)
make_fixture_field_invalid_value() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# Story CFP-1539 test fixture (invalid value)

[USER-UTTERANCE-VERBATIM]
진행해
pre_spawn_prompt_finalize_verified: yes
[/USER-UTTERANCE-VERBATIM]
FIXTURE
}

# fixture: NON-Story file (docs/ 아래지만 docs/stories/ 아님)
make_fixture_non_story_file() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# 일반 ADR file

[USER-UTTERANCE-VERBATIM]
이 file 은 docs/stories/ 경로 아님 — silent skip 대상 (FP guard 3).
[/USER-UTTERANCE-VERBATIM]
FIXTURE
}

# fixture: discriminating — 1st block has field, 2nd block has NO field
make_fixture_discriminating() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# Story CFP-1539 discriminating test fixture

[USER-UTTERANCE-VERBATIM]
1st block — field present
pre_spawn_prompt_finalize_verified: true
[/USER-UTTERANCE-VERBATIM]

## 중간 내용

[USER-UTTERANCE-VERBATIM]
2nd block — field ABSENT (regression: 모든 block 검사 의무)
[/USER-UTTERANCE-VERBATIM]
FIXTURE
}

# fixture: regression guard — multiple blocks all field-present
make_fixture_regression_guard() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# Story CFP-1539 regression guard fixture

[USER-UTTERANCE-VERBATIM]
block 1
pre_spawn_prompt_finalize_verified: true
[/USER-UTTERANCE-VERBATIM]

[USER-UTTERANCE-VERBATIM]
block 2
pre_spawn_prompt_finalize_verified: true
[/USER-UTTERANCE-VERBATIM]

[USER-UTTERANCE-VERBATIM]
block 3
pre_spawn_prompt_finalize_verified: false
[/USER-UTTERANCE-VERBATIM]
FIXTURE
}

# ─────────────────────────────── TC-1: PRESENCE ──────────────────────────────

@test "TC-1 PRESENCE: valid field (true) in block → PASS (warn=0, exit 0)" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc1.md")"
  make_fixture_field_present_true "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  # warning-tier — 항상 exit 0
  [ "$status" -eq 0 ]
  # WARN 없음 확인
  [[ "$output" != *"[WARN-FIELD-ABSENT]"* ]]
  [[ "$output" != *"[WARN-FIELD-INVALID]"* ]]
}

@test "TC-1-negative: valid field fixture 에서 ERROR 미발생 확인" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc1-neg.md")"
  make_fixture_field_present_true "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # ERROR 미발생 확인
  [[ "$output" != *"[ERROR]"* ]]
}

# ─────────────────────────────── TC-2: ABSENCE ───────────────────────────────

@test "TC-2 ABSENCE: block without field → [WARN-FIELD-ABSENT] (exit 0 유지)" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc2.md")"
  make_fixture_field_absent "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # WARN-FIELD-ABSENT 발화 확인
  [[ "$output" == *"[WARN-FIELD-ABSENT]"* ]]
}

@test "TC-2-negative: absence fixture 에서 exit 0 보장" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc2-neg.md")"
  make_fixture_field_absent "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # exit 1 절대 발화 금지
  [ "$status" -ne 1 ]
}

# ─────────────────────────────── TC-3: INVALID-VALUE ─────────────────────────

@test "TC-3 INVALID-VALUE: field present but value invalid → [WARN-FIELD-INVALID] (exit 0)" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc3.md")"
  make_fixture_field_invalid_value "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN-FIELD-INVALID 발화 확인
  [[ "$output" == *"[WARN-FIELD-INVALID]"* ]]
}

@test "TC-3-negative: invalid value fixture 에서 WARN-FIELD-ABSENT 발화 금지 (field 자체는 존재)" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc3-neg.md")"
  make_fixture_field_invalid_value "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN-FIELD-ABSENT 발화 금지 (field 자체는 있음 — value 만 위반)
  [[ "$output" != *"[WARN-FIELD-ABSENT]"* ]]
}

# ─────────────────────────────── TC-4: SKIP-NON-STORY ────────────────────────

@test "TC-4 SKIP-NON-STORY: non-Story file → silent skip (no warn)" {
  # docs/adr/ 경로 (Story file 아님)
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local fixture="${adr_dir}/ADR-test.md"
  make_fixture_non_story_file "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN 발화 금지 (silent skip — FP guard 3)
  [[ "$output" != *"[WARN-FIELD-ABSENT]"* ]]
  [[ "$output" != *"[WARN-FIELD-INVALID]"* ]]
}

@test "TC-4-negative: non-Story file 에서 exit 1 절대 발화 금지" {
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local fixture="${adr_dir}/ADR-test-neg.md"
  make_fixture_non_story_file "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  [ "$status" -ne 1 ]
}

# ─────────────────────────────── TC-5: SKIP-TEMPLATES ────────────────────────

@test "TC-5 SKIP-TEMPLATES: file under templates/** → silent skip (FP guard 1)" {
  local templates_dir="${TEST_TMP}/templates/agent-spawn"
  mkdir -p "$templates_dir"
  local fixture="${templates_dir}/canonical-example.md"
  make_fixture_field_absent "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # templates/** path = silent skip (canonical example 면제)
  [[ "$output" != *"[WARN-FIELD-ABSENT]"* ]]
  [[ "$output" != *"[WARN-FIELD-INVALID]"* ]]
}

# ─────────────────────────────── TC-6: SKIP-TESTS ────────────────────────────

@test "TC-6 SKIP-TESTS: file under tests/** → silent skip (FP guard 2)" {
  local tests_dir="${TEST_TMP}/tests/scripts"
  mkdir -p "$tests_dir"
  local fixture="${tests_dir}/test-fixture.md"
  make_fixture_field_absent "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # tests/** path = silent skip (bats fixture 면제)
  [[ "$output" != *"[WARN-FIELD-ABSENT]"* ]]
  [[ "$output" != *"[WARN-FIELD-INVALID]"* ]]
}

# ─────────────────────────────── TC-7: DISCRIMINATING ────────────────────────

@test "TC-7 DISCRIMINATING: present + absent blocks → absent wins (genuine warn)" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc7.md")"
  make_fixture_discriminating "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # 2nd block absent → WARN-FIELD-ABSENT 발화 의무 (discriminating = 모든 block 검사)
  [[ "$output" == *"[WARN-FIELD-ABSENT]"* ]]
}

@test "TC-7-negative: discriminating fixture 에서 WARN-FIELD-ABSENT 발화 시 exit 1 금지 (warning tier)" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc7-neg.md")"
  make_fixture_discriminating "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  # warning-tier — exit 1 절대 금지
  [ "$status" -eq 0 ]
}

# ─────────────────────────────── TC-8: REGRESSION-GUARD ──────────────────────

@test "TC-8 REGRESSION-GUARD: multiple blocks all field-present → PASS (no warn)" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc8.md")"
  make_fixture_regression_guard "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # all blocks field-present = PASS (no warn)
  [[ "$output" != *"[WARN-FIELD-ABSENT]"* ]]
  [[ "$output" != *"[WARN-FIELD-INVALID]"* ]]
}

# ─────────────────────────────── TC-9: BYPASS-ENV ────────────────────────────

@test "TC-9 BYPASS-ENV: HOTFIX_BYPASS_PRE_SPAWN_PROMPT_FINALIZE_VERIFY=1 → immediate exit 0" {
  local fixture
  fixture="$(make_story_fixture_path "$TEST_TMP" "story-tc9.md")"
  make_fixture_field_absent "$fixture"

  HOTFIX_BYPASS_PRE_SPAWN_PROMPT_FINALIZE_VERIFY=1 run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # bypass = WARN 발화 금지 (lint 자체가 skip)
  [[ "$output" != *"[WARN-FIELD-ABSENT]"* ]]
  [[ "$output" != *"[WARN-FIELD-INVALID]"* ]]
  # BYPASS marker 확인
  [[ "$output" == *"BYPASS=1"* ]]
}
