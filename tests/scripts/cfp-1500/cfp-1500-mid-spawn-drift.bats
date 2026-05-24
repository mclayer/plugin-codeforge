#!/usr/bin/env bats
# tests/scripts/cfp-1500/cfp-1500-mid-spawn-drift.bats
# CFP-1500 Wave 2-B — Mid-spawn drift detection mechanical lint TDD
# RED→GREEN stash proof pattern (CFP-1334 §8.4 / ADR-082 §결정 11.A precedent)
#
# Detection scope:
#   Check (a) — agent spawn entry in Story §14 Lane Evidence without
#     `mid_spawn_drift_check_executed: <bool>` OR `drift_check_directive_present: true`
#   Check (b) — long-duration spawn (≥ 5 min) without `drift_detected: <bool>` flag
#
# Bats fixture 9 TC (RED first written, GREEN after implementation):
#   TC-1: PRESENCE — agent spawn + directive marker → PASS
#   TC-2: ABSENCE — agent spawn without directive → [WARN-DIRECTIVE-ABSENT]
#   TC-3: RETURN-PAYLOAD-COMPLETE — long-duration + drift_detected flag → PASS
#   TC-4: RETURN-PAYLOAD-INCOMPLETE — long-duration without drift_detected → [WARN-RETURN-PAYLOAD-INCOMPLETE]
#   TC-5: SKIP-NON-STORY — non-Story file → silent skip (no warn)
#   TC-6: SKIP-TEMPLATES-PATH — file under templates/** → silent skip (FP-완화 guard 1)
#   TC-7: DISCRIMINATING — matched + unmatched in same file → unmatched wins
#   TC-8: REGRESSION-GUARD — multiple spawns all directive-present → PASS
#   TC-9: BYPASS-ENV — HOTFIX_BYPASS_MID_SPAWN_DRIFT_DETECTION=1 → immediate exit 0
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
# SSOT: ADR-082 Amendment 16 §결정 1 layer 1 sub-scope (1-F) + ADR-073 Amendment 12
# Change-plan: <internal-docs>/plugin-codeforge/change-plans/cfp-1500-wave2b-mid-spawn-drift-wire.md
# Precedent byte-pattern: tests/scripts/cfp-1497/cfp-1497-amendment-slot-reservation.bats

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
LINT_SCRIPT="${WORKTREE_ROOT}/scripts/lib/check_mid_spawn_drift_detection.py"

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
  unset HOTFIX_BYPASS_MID_SPAWN_DRIFT_DETECTION
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1500-unused}"
}

# ─────────────────────────────── prerequisite checks ─────────────────────────

@test "PREREQ: lint Python script 존재 확인" {
  [ -f "$LINT_SCRIPT" ]
}

@test "PREREQ: python3 사용 가능 확인" {
  command -v python3
}

# ─────────────────────────── helper: fixture 생성 함수 ────────────────────────

# Story file with agent spawn entry + directive marker (PASS case).
# Usage: make_story_fixture_with_directive "<path>"
make_story_fixture_with_directive() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story for mid-spawn-drift-detection lint
status: phase:설계
type: story
---

## §14. Lane Evidence

| # | Lane | Agent | Start (KST) | End (KST) | Outcome |
|---|---|---|---|---|---|
| 1 | design | ArchitectAgent spawn (chief author) | 2026-05-24T16:10:00+09:00 | TBD | TBD |

agent: ArchitectAgent spawn (chief author)
mid_spawn_drift_check_executed: false
drift_check_directive_present: true
STORY
}

# Story file with agent spawn entry WITHOUT directive marker (WARN case).
make_story_fixture_without_directive() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story for mid-spawn-drift-detection lint (ABSENCE case)
status: phase:설계
type: story
---

## §14. Lane Evidence

| # | Lane | Agent | Start (KST) | End (KST) | Outcome |
|---|---|---|---|---|---|
| 1 | design | ArchitectAgent spawn (chief author) | 2026-05-24T16:10:00+09:00 | TBD | TBD |

agent: ArchitectAgent spawn (chief author)
outcome: TBD
STORY
}

# Story file with long-duration spawn + drift_detected flag (RETURN-COMPLETE case).
make_story_fixture_long_with_drift_flag() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story long-duration spawn complete payload
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent spawn (chief author) duration: 30 min
mid_spawn_drift_check_executed: true
drift_detected: false
outcome: PASS
STORY
}

# Story file with long-duration spawn WITHOUT drift_detected flag (WARN case).
make_story_fixture_long_without_drift_flag() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story long-duration spawn incomplete payload
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent spawn (chief author) duration: 30 min
mid_spawn_drift_check_executed: true
outcome: PASS
STORY
}

# Non-Story file (e.g. random markdown) — should be silent-skipped.
make_non_story_fixture() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# 일반 문서

이 file 은 docs/stories/**/*.md 영역이 아닌 일반 markdown 문서입니다.
agent ArchitectAgent spawn 문구가 있어도 silent skip (lint scope 외).
FIXTURE
}

# Story file with mixed: 1 entry with directive + 1 without (DISCRIMINATING case).
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

agent: ArchitectAgent spawn (chief author)
mid_spawn_drift_check_executed: false
drift_check_directive_present: true


agent: DeveloperAgent spawn (worker)
outcome: TBD
STORY
}

# Story file with 3 spawn entries all directive-present (REGRESSION case).
make_story_fixture_3spawns_all_directive() {
  local path="$1"
  local story_dir="$(dirname "$path")"
  mkdir -p "$story_dir"
  cat > "$path" << 'STORY'
---
key: CFP-TEST
title: Test Story 3 spawn entries
status: phase:설계
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent spawn (chief author)
drift_check_directive_present: true


agent: DeveloperAgent spawn (worker)
mid_spawn_drift_check_executed: false


agent: QADeveloperAgent spawn (test)
drift_check_directive_present: true
STORY
}

# ─────────────────────────────── TC: presence/absence ────────────────────────

@test "TC-1 PRESENCE: agent spawn + directive marker → PASS (warn=0, exit 0)" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_with_directive "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  # warning-tier — 항상 exit 0
  [ "$status" -eq 0 ]
  # WARN 없음 확인
  [[ "$output" != *"[WARN-DIRECTIVE-ABSENT]"* ]]
  [[ "$output" != *"[WARN-RETURN-PAYLOAD-INCOMPLETE]"* ]]
  # PASS marker 확인
  [[ "$output" == *"OK"* ]] || [[ "$output" == *"PASS"* ]]
}

@test "TC-2 ABSENCE: agent spawn without directive → [WARN-DIRECTIVE-ABSENT]" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_without_directive "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # WARN-DIRECTIVE-ABSENT 발화 확인
  [[ "$output" == *"[WARN-DIRECTIVE-ABSENT]"* ]]
}

# ─────────────────────────────── TC: return packet flag ──────────────────────

@test "TC-3 RETURN-PAYLOAD-COMPLETE: long-duration + drift_detected flag → PASS" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_long_with_drift_flag "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  [[ "$output" != *"[WARN-DIRECTIVE-ABSENT]"* ]]
  [[ "$output" != *"[WARN-RETURN-PAYLOAD-INCOMPLETE]"* ]]
}

@test "TC-4 RETURN-PAYLOAD-INCOMPLETE: long-duration without drift_detected → [WARN-RETURN-PAYLOAD-INCOMPLETE]" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_long_without_drift_flag "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN-RETURN-PAYLOAD-INCOMPLETE]"* ]]
}

# ─────────────────────────────── TC: skip / FP-완화 guards ────────────────────

@test "TC-5 SKIP-NON-STORY: non-Story file → silent skip (no warn)" {
  local fixture="${TEST_TMP}/normal-doc.md"
  make_non_story_fixture "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN 발화 금지 (silent skip)
  [[ "$output" != *"[WARN-DIRECTIVE-ABSENT]"* ]]
  [[ "$output" != *"[WARN-RETURN-PAYLOAD-INCOMPLETE]"* ]]
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
  # would normally warn (no directive), but templates/** = skip
  cat > "$fixture" << 'STORY'
---
key: CFP-CANONICAL
type: story
---

## §14. Lane Evidence

agent: ArchitectAgent spawn (chief author)
outcome: TBD
STORY

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # templates/** path = silent skip
  [[ "$output" != *"[WARN-DIRECTIVE-ABSENT]"* ]]
  [[ "$output" != *"[WARN-RETURN-PAYLOAD-INCOMPLETE]"* ]]
}

# ─────────────────────────────── TC: discriminating + regression ─────────────

@test "TC-7 DISCRIMINATING: matched + unmatched spawn in same file → unmatched wins (genuine warn)" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_mixed "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  # 2번째 spawn (DeveloperAgent) directive 부재 → WARN 발화 의무
  [[ "$output" == *"[WARN-DIRECTIVE-ABSENT]"* ]]
}

@test "TC-8 REGRESSION-GUARD: multiple spawn entries all directive-present → PASS" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  make_story_fixture_3spawns_all_directive "$story_file"

  run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  # 모든 spawn directive-present → PASS
  [[ "$output" != *"[WARN-DIRECTIVE-ABSENT]"* ]]
  [[ "$output" != *"[WARN-RETURN-PAYLOAD-INCOMPLETE]"* ]]
}

# ─────────────────────────────── TC: bypass env ──────────────────────────────

@test "TC-9 BYPASS-ENV: HOTFIX_BYPASS_MID_SPAWN_DRIFT_DETECTION=1 → immediate exit 0" {
  local story_file="${TEST_TMP}/docs/stories/CFP-TEST.md"
  # Setup would normally warn (no directive)
  make_story_fixture_without_directive "$story_file"

  HOTFIX_BYPASS_MID_SPAWN_DRIFT_DETECTION=1 \
    run python3 "$LINT_SCRIPT" "$story_file"
  [ "$status" -eq 0 ]
  # bypass = WARN 발화 금지 (lint 자체가 skip)
  [[ "$output" != *"[WARN-DIRECTIVE-ABSENT]"* ]]
  [[ "$output" != *"[WARN-RETURN-PAYLOAD-INCOMPLETE]"* ]]
  # BYPASS marker 확인
  [[ "$output" == *"BYPASS=1"* ]]
}
