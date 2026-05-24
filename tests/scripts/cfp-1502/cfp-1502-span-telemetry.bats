#!/usr/bin/env bats
# tests/scripts/cfp-1502/cfp-1502-span-telemetry.bats
# CFP-1502 Wave 2-D — Chief author span telemetry mechanical lint TDD (FINAL Wave 2)
# RED→GREEN stash proof pattern (CFP-1334 §8.4 / ADR-082 §결정 11.A precedent)
#
# Detection scope:
#   Check (a) — chief author spawn entry in Story §14 Lane Evidence without
#     `[chief-author-span: <minutes>, <class>]` inline marker OR
#     `chief_author_span_minutes:` YAML-like field presence → [WARN-TELEMETRY-MARKER-ABSENT]
#   Check (b) — long-span chief author spawn (≥ 10 min) with class `monolithic`
#     → [WARN-LONG-SPAN-MONOLITHIC] (recommendation tier)
#
# Bats fixture 9 TC (RED first written, GREEN after implementation):
#   TC-1: PRESENCE — chief author spawn + `[chief-author-span: 8, monolithic]` → PASS
#   TC-2: ABSENCE — chief author spawn without telemetry marker → [WARN-TELEMETRY-MARKER-ABSENT]
#   TC-3: LONG-SPAN-MULTI-STEP — spawn ≥ 10 min + `multi_step_3` class → PASS
#   TC-4: LONG-SPAN-MONOLITHIC — spawn ≥ 10 min + `monolithic` class → [WARN-LONG-SPAN-MONOLITHIC]
#   TC-5: SKIP-NON-STORY — non-Story file → silent skip (no warn)
#   TC-6: SKIP-TEMPLATES-PATH — file under templates/** → silent skip (FP-완화 guard 1)
#   TC-7: DISCRIMINATING — matched + unmatched spawn in same file → unmatched wins
#   TC-8: REGRESSION-GUARD — multiple spawns all telemetry-marker-present → PASS
#   TC-9: BYPASS-ENV — HOTFIX_BYPASS_CHIEF_AUTHOR_SPAN_TELEMETRY=1 → immediate exit 0
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — positive + negative 2-assertion per TC (where applicable)
#   Layer 3 — 임시 fixture 파일 사용 (실제 repo 의존 금지)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# SSOT: ADR-039 Amendment 5 §결정 17 + ADR-044 Amendment 3 §결정 9
# Change-plan: <internal-docs>/plugin-codeforge/change-plans/cfp-1502-wave2d-span-telemetry-wire.md
# Precedent byte-pattern: tests/scripts/cfp-1500/cfp-1500-mid-spawn-drift.bats

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
LINT_SCRIPT="${WORKTREE_ROOT}/scripts/lib/measure_chief_author_span.py"

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
  unset HOTFIX_BYPASS_CHIEF_AUTHOR_SPAN_TELEMETRY
  # Ensure threshold uses default (10) — avoid env contamination
  unset CFP_CHIEF_AUTHOR_SPAN_MAX_MIN
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1502-unused}"
}

# ─────────────────────────────── prerequisite checks ─────────────────────────

@test "PREREQ: lint Python script 존재 확인" {
  [ -f "$LINT_SCRIPT" ]
}

@test "PREREQ: python3 사용 가능 확인" {
  command -v python3
}

# ─────────────────────────── helper: fixture 생성 함수 ────────────────────────

# Story file with chief author spawn entry + telemetry marker (PASS case).
make_story_fixture_with_marker() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story for chief-author-span-telemetry lint
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent (chief author) spawn
[chief-author-span: 8, monolithic]
outcome: PASS
STORY
}

# Story file with chief author spawn entry WITHOUT telemetry marker (WARN case).
make_story_fixture_without_marker() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story for chief-author-span-telemetry lint (ABSENCE case)
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent (chief author) spawn
outcome: TBD
STORY
}

# Story file with long-span chief author spawn + multi_step class (PASS case).
make_story_fixture_long_multi_step() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story long-span chief author multi_step
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent (chief author) spawn
[chief-author-span: 15, multi_step_3]
outcome: PASS
STORY
}

# Story file with long-span chief author spawn + monolithic class (WARN case).
make_story_fixture_long_monolithic() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story long-span chief author monolithic
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent (chief author) spawn
[chief-author-span: 20, monolithic]
outcome: PASS
STORY
}

# Non-Story file (e.g. random markdown) — should be silent-skipped.
make_non_story_fixture() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# 일반 문서

이 file 은 docs/stories/**/*.md 영역이 아닌 일반 markdown 문서입니다.
chief author 문구가 있어도 silent skip (lint scope 외).
FIXTURE
}

# Story file with mixed: 1 entry with marker + 1 without (DISCRIMINATING case).
make_story_fixture_mixed() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story mixed entries
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent (chief author) spawn first
[chief-author-span: 5, monolithic]


agent: ArchitectAgent (chief author) spawn second
outcome: TBD
STORY
}

# Story file with 3 spawn entries all telemetry-marker-present (REGRESSION case).
make_story_fixture_3spawns_all_marker() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story 3 chief author spawn entries
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent (chief author) spawn 1
[chief-author-span: 3, monolithic]


agent: ArchitectAgent (chief author) spawn 2
[chief-author-span: 7, monolithic]


agent: ArchitectAgent (chief author) spawn 3
[chief-author-span: 12, multi_step_3]
STORY
}

# ─────────────────────────────── TC: presence/absence ────────────────────────

@test "TC-1 PRESENCE: chief author spawn + telemetry marker → PASS (warn=0, exit 0)" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_with_marker "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  # warning-tier — 항상 exit 0
  [ "$status" -eq 0 ]
  # WARN 없음 확인
  [[ "$output" != *"[WARN-TELEMETRY-MARKER-ABSENT]"* ]]
  [[ "$output" != *"[WARN-LONG-SPAN-MONOLITHIC]"* ]]
  # PASS marker 확인
  [[ "$output" == *"OK"* ]] || [[ "$output" == *"PASS"* ]]
}

@test "TC-2 ABSENCE: chief author spawn without telemetry marker → [WARN-TELEMETRY-MARKER-ABSENT]" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_without_marker "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # WARN-TELEMETRY-MARKER-ABSENT 발화 확인
  [[ "$output" == *"[WARN-TELEMETRY-MARKER-ABSENT]"* ]]
}

# ─────────────────────────────── TC: long-span class semantics ───────────────

@test "TC-3 LONG-SPAN-MULTI-STEP: spawn ≥ 10 min + multi_step_3 → PASS" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_long_multi_step "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  [[ "$output" != *"[WARN-TELEMETRY-MARKER-ABSENT]"* ]]
  [[ "$output" != *"[WARN-LONG-SPAN-MONOLITHIC]"* ]]
}

@test "TC-4 LONG-SPAN-MONOLITHIC: spawn ≥ 10 min + monolithic → [WARN-LONG-SPAN-MONOLITHIC]" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_long_monolithic "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN-LONG-SPAN-MONOLITHIC]"* ]]
}

# ─────────────────────────────── TC: skip / FP-완화 guards ────────────────────

@test "TC-5 SKIP-NON-STORY: non-Story file → silent skip (no warn)" {
  local fixture="${TEST_TMP}/normal-doc.md"
  make_non_story_fixture "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN 발화 금지 (silent skip)
  [[ "$output" != *"[WARN-TELEMETRY-MARKER-ABSENT]"* ]]
  [[ "$output" != *"[WARN-LONG-SPAN-MONOLITHIC]"* ]]
}

@test "TC-5-negative: non-Story fixture 에서 exit 1 절대 발화 금지" {
  local fixture="${TEST_TMP}/normal-doc.md"
  make_non_story_fixture "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  [ "$status" -ne 1 ]
}

@test "TC-6 SKIP-TEMPLATES-PATH: file under templates/** → silent skip (FP-완화 guard 1)" {
  local templates_dir="${TEST_TMP}/templates/stories-canonical"
  mkdir -p "$templates_dir"
  local fixture="${templates_dir}/CFP-CANONICAL.md"
  # would normally warn (no marker), but templates/** = skip
  cat > "$fixture" << 'STORY'
---
key: CFP-CANONICAL
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent (chief author) spawn
outcome: TBD
STORY

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # templates/** path = silent skip
  [[ "$output" != *"[WARN-TELEMETRY-MARKER-ABSENT]"* ]]
  [[ "$output" != *"[WARN-LONG-SPAN-MONOLITHIC]"* ]]
}

# ─────────────────────────────── TC: discriminating + regression ─────────────

@test "TC-7 DISCRIMINATING: matched + unmatched spawn in same file → unmatched wins (genuine warn)" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_mixed "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  # 2번째 spawn (without marker) → WARN 발화 의무
  [[ "$output" == *"[WARN-TELEMETRY-MARKER-ABSENT]"* ]]
}

@test "TC-8 REGRESSION-GUARD: multiple spawn entries all telemetry-marker-present → PASS" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_3spawns_all_marker "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  # 모든 spawn marker-present → no marker-absent warn
  [[ "$output" != *"[WARN-TELEMETRY-MARKER-ABSENT]"* ]]
  # spawn 3 = 12 min multi_step_3 = no monolithic warn
  [[ "$output" != *"[WARN-LONG-SPAN-MONOLITHIC]"* ]]
}

# ─────────────────────────────── TC: bypass env ──────────────────────────────

@test "TC-9 BYPASS-ENV: HOTFIX_BYPASS_CHIEF_AUTHOR_SPAN_TELEMETRY=1 → immediate exit 0" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  # Setup would normally warn (no marker)
  make_story_fixture_without_marker "$story_file"

  HOTFIX_BYPASS_CHIEF_AUTHOR_SPAN_TELEMETRY=1 \
    run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  # bypass = WARN 발화 금지 (lint 자체가 skip)
  [[ "$output" != *"[WARN-TELEMETRY-MARKER-ABSENT]"* ]]
  [[ "$output" != *"[WARN-LONG-SPAN-MONOLITHIC]"* ]]
  # BYPASS marker 확인
  [[ "$output" == *"BYPASS=1"* ]]
}
