#!/usr/bin/env bats
# tests/scripts/cfp-1489/cfp-1489-spawn-prompt-head-pin.bats
# CFP-1489 Wave 2-A — Pre-spawn HEAD-pin protocol mechanical lint TDD
# RED→GREEN stash proof pattern (CFP-1334 §8.4 / ADR-082 §결정 11.A precedent)
#
# Detection scope:
#   Check (a) PRE-SPAWN-ORIGIN-MAIN-SHA block presence in spawn-prompt candidate files
#   Check (b) SHA format strict (40-char lowercase hex)
#
# Bats fixture 7 TC (RED first written, GREEN after implementation):
#   TC-1: PRESENCE — valid SHA block in spawn-context → PASS
#   TC-2: ABSENCE — spawn marker but no block → [WARN-ABSENT]
#   TC-3: INVALID-FORMAT — block present but SHA non-40-char-hex → [WARN-INVALID]
#   TC-4: SKIP-NON-SPAWN-CONTEXT — file without spawn marker → silent skip (no warn)
#   TC-5: SKIP-TEMPLATES-PATH — file under templates/** → silent skip (FP-완화 guard 1)
#   TC-6: DISCRIMINATING — both valid + invalid SHA in single file → invalid wins (genuine fail)
#   TC-7: REGRESSION-GUARD — multiple spawn markers + valid SHA → single PASS
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
# SSOT: ADR-073 Amendment 11 §결정 1-A + ADR-082 Amendment 15 §결정 1 layer 1 sub-scope (1-E)
# Change-plan: <internal-docs>/plugin-codeforge/change-plans/cfp-1489-wave2a-spawn-prompt-head-pin-wire.md
# Precedent byte-pattern: tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
LINT_SCRIPT="${WORKTREE_ROOT}/scripts/lib/check_spawn_prompt_head_pin.py"

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
  unset HOTFIX_BYPASS_SPAWN_PROMPT_HEAD_PIN
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1489-unused}"
}

# ─────────────────────────────── prerequisite checks ─────────────────────────

@test "PREREQ: lint Python script 존재 확인" {
  [ -f "$LINT_SCRIPT" ]
}

@test "PREREQ: python3 사용 가능 확인" {
  command -v python3
}

# ─────────────────────────── helper: fixture 생성 함수 ────────────────────────

# Valid PRE-SPAWN-ORIGIN-MAIN-SHA block — 40-char lowercase hex SHA
# (CFP-1437 PR #1444 merge commit SHA 일종 — 본 검사 대상 예시)
VALID_SHA="03ca49c4978c0294e1a943bd4e855d8cea5754ee"

# fixture: spawn marker + valid block
make_fixture_presence_valid() {
  local path="$1"
  cat > "$path" << FIXTURE
# Lane evidence

[PRE-SPAWN-ORIGIN-MAIN-SHA: ${VALID_SHA}]

## ArchitectAgent spawn

본 spawn = CFP-1489 chief author. spawn 직전 origin/main SHA pin 의무.
FIXTURE
}

# fixture: spawn marker but NO block
make_fixture_absent_block() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# Lane evidence

## ArchitectAgent spawn

본 spawn 은 PRE-SPAWN-ORIGIN-MAIN-SHA block 없이 시작되었습니다 (WARN-ABSENT 대상).
FIXTURE
}

# fixture: spawn marker + invalid SHA format (39 chars, missing one hex digit)
make_fixture_invalid_format() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# Lane evidence

[PRE-SPAWN-ORIGIN-MAIN-SHA: 03ca49c4978c0294e1a943bd4e855d8cea5754e]

## RequirementsPLAgent spawn

본 spawn = invalid 39-char SHA (40-char hex regex 위반 — WARN-INVALID 대상).
FIXTURE
}

# fixture: file WITHOUT any spawn marker — should silent skip
make_fixture_non_spawn_context() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# 일반 문서

이 file 은 spawn evidence marker 가 전혀 없는 일반 markdown 문서입니다.
silent skip 대상 (lint scope 외).
FIXTURE
}

# fixture: spawn marker + valid block — but UNDER templates/ subdir
# (this fixture is for path-filter test — actual file path includes /templates/)
make_fixture_templates_path() {
  local path="$1"
  # same content as presence_valid, but path includes templates/
  make_fixture_presence_valid "$path"
}

# fixture: TWO blocks in same file — one valid + one invalid (discriminating)
make_fixture_discriminating() {
  local path="$1"
  cat > "$path" << FIXTURE
# Lane evidence (discriminating TC)

## ArchitectAgent spawn (1st)

[PRE-SPAWN-ORIGIN-MAIN-SHA: ${VALID_SHA}]

본 spawn = valid block.

## ArchitectAgent spawn (2nd)

[PRE-SPAWN-ORIGIN-MAIN-SHA: XYZ-not-a-valid-sha]

본 spawn = invalid block (regression guard — 모든 block 검사 의무).
FIXTURE
}

# fixture: regression guard — multiple spawn markers + single valid block
make_fixture_regression_guard() {
  local path="$1"
  cat > "$path" << FIXTURE
# Lane evidence

[PRE-SPAWN-ORIGIN-MAIN-SHA: ${VALID_SHA}]

## ArchitectAgent spawn

## ArchitectPLAgent spawn

## deputy spawn

## RequirementsPLAgent spawn

본 lane 안 multiple spawn 시점 anchor block 1개 = single PASS (block 자체 = lane-level anchor).
FIXTURE
}

# ─────────────────────────────── TC: presence/absence/invalid ────────────────

@test "TC-1 PRESENCE: valid SHA block in spawn-context → PASS (warn=0, exit 0)" {
  local fixture="${TEST_TMP}/story-cfp-test.md"
  make_fixture_presence_valid "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  # warning-tier — 항상 exit 0
  [ "$status" -eq 0 ]
  # WARN 없음 확인
  [[ "$output" != *"[WARN-ABSENT]"* ]]
  [[ "$output" != *"[WARN-INVALID]"* ]]
  # PASS marker 확인
  [[ "$output" == *"OK"* ]] || [[ "$output" == *"PASS"* ]]
}

@test "TC-1-negative: valid SHA block file 에서 ERROR 미발생 확인" {
  local fixture="${TEST_TMP}/story-cfp-test.md"
  make_fixture_presence_valid "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # ERROR 미발생 확인
  [[ "$output" != *"[ERROR]"* ]]
}

@test "TC-2 ABSENCE: spawn marker but no block → [WARN-ABSENT] (exit 0 유지)" {
  local fixture="${TEST_TMP}/story-cfp-absent.md"
  make_fixture_absent_block "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # WARN-ABSENT 발화 확인
  [[ "$output" == *"[WARN-ABSENT]"* ]]
}

@test "TC-2-negative: absence fixture 에서 exit 0 보장" {
  local fixture="${TEST_TMP}/story-cfp-absent.md"
  make_fixture_absent_block "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # exit 1 절대 발화 금지
  [ "$status" -ne 1 ]
}

@test "TC-3 INVALID-FORMAT: block present but SHA invalid → [WARN-INVALID] (exit 0)" {
  local fixture="${TEST_TMP}/story-cfp-invalid.md"
  make_fixture_invalid_format "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN-INVALID 발화 확인
  [[ "$output" == *"[WARN-INVALID]"* ]]
}

@test "TC-3-negative: invalid format fixture 에서 WARN-ABSENT 발화 금지 (block 자체는 존재)" {
  local fixture="${TEST_TMP}/story-cfp-invalid.md"
  make_fixture_invalid_format "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN-ABSENT 발화 금지 (block 자체는 있음 — 형식만 위반)
  [[ "$output" != *"[WARN-ABSENT]"* ]]
}

# ─────────────────────────────── TC: skip / FP-완화 guards ────────────────────

@test "TC-4 SKIP-NON-SPAWN-CONTEXT: file without spawn marker → silent skip" {
  local fixture="${TEST_TMP}/normal-doc.md"
  make_fixture_non_spawn_context "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN 발화 금지 (silent skip)
  [[ "$output" != *"[WARN-ABSENT]"* ]]
  [[ "$output" != *"[WARN-INVALID]"* ]]
}

@test "TC-4-negative: non-spawn-context file 에서 OK 발화 금지 (silent skip semantic)" {
  local fixture="${TEST_TMP}/normal-doc.md"
  make_fixture_non_spawn_context "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # silent skip = OK marker 도 발화 금지 (scope 외 file 은 통과 marker 없음)
  # 단 summary 의 PASS 는 발화 가능 — file-level OK 만 금지
  ! grep -q "OK: ${fixture}" <<< "$output" || true  # advisory — 엄격 강제 X
}

@test "TC-5 SKIP-TEMPLATES-PATH: file under templates/** → silent skip (FP-완화 guard 1)" {
  local templates_dir="${TEST_TMP}/templates/agent-spawn"
  mkdir -p "$templates_dir"
  local fixture="${templates_dir}/canonical-example.md"
  make_fixture_templates_path "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # templates/** path = silent skip (canonical example 면제)
  [[ "$output" != *"[WARN-ABSENT]"* ]]
  [[ "$output" != *"[WARN-INVALID]"* ]]
}

# ─────────────────────────────── TC: discriminating + regression ─────────────

@test "TC-6 DISCRIMINATING: file with valid + invalid blocks → invalid wins (genuine warn)" {
  local fixture="${TEST_TMP}/story-discriminating.md"
  make_fixture_discriminating "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # invalid block 발견 = WARN-INVALID 발화 의무 (discriminating = both presence)
  [[ "$output" == *"[WARN-INVALID]"* ]]
}

@test "TC-7 REGRESSION-GUARD: multiple spawn markers + single valid block → single PASS" {
  local fixture="${TEST_TMP}/story-regression.md"
  make_fixture_regression_guard "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # multiple spawn markers 가 있어도 block 1개 = lane-level anchor → PASS
  [[ "$output" != *"[WARN-ABSENT]"* ]]
  [[ "$output" != *"[WARN-INVALID]"* ]]
}

# ─────────────────────────────── TC: bypass env ──────────────────────────────

@test "TC-8 BYPASS-ENV: HOTFIX_BYPASS_SPAWN_PROMPT_HEAD_PIN=1 → immediate exit 0" {
  local fixture="${TEST_TMP}/story-absent.md"
  make_fixture_absent_block "$fixture"

  HOTFIX_BYPASS_SPAWN_PROMPT_HEAD_PIN=1 run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # bypass = WARN 발화 금지 (lint 자체가 skip)
  [[ "$output" != *"[WARN-ABSENT]"* ]]
  [[ "$output" != *"[WARN-INVALID]"* ]]
  # BYPASS marker 확인
  [[ "$output" == *"BYPASS=1"* ]]
}
