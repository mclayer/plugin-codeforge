#!/usr/bin/env bats
# tests/scripts/cfp-1497/cfp-1497-amendment-slot-reservation.bats
# CFP-1497 Wave 2-C — Amendment-slot reservation mechanical lint TDD
# RED→GREEN stash proof pattern (CFP-1334 §8.4 / ADR-082 §결정 11.A precedent)
#
# Detection scope:
#   Check (a) Amendment append without matching ADR-RESERVATION amendments_reserved[] row
#   Check (b) Concurrent reservation conflict (same (adr_number, amendment_id) slot 2+ rows)
#
# Bats fixture 8 TC (RED first written, GREEN after implementation):
#   TC-1: PRESENCE — Amendment + matching reservation row → PASS
#   TC-2: ABSENCE — Amendment without reservation row → [WARN-MISSING-RESERVATION]
#   TC-3: CONFLICT — 2+ rows claim same slot → [WARN-CONCURRENT-CONFLICT]
#   TC-4: SKIP-NON-ADR-FILE — non-ADR file → silent skip (no warn)
#   TC-5: SKIP-TEMPLATES-PATH — file under templates/** → silent skip (FP-완화 guard 1)
#   TC-6: DISCRIMINATING — Amendment with match + another Amendment without match → warn wins
#   TC-7: REGRESSION-GUARD — multiple Amendments all with matching rows → PASS
#   TC-8: BYPASS-ENV — HOTFIX_BYPASS_AMENDMENT_SLOT_RESERVATION=1 → immediate exit 0
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — positive + negative 2-assertion per TC (where applicable)
#   Layer 3 — 임시 fixture 파일 사용 (실제 repo 의존 금지, env injection of ADR-RESERVATION path)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# SSOT: ADR-082 Amendment 17 §결정 1 layer 1 sub-scope (1-G) + ADR-050 §결정 1
# Change-plan: <internal-docs>/plugin-codeforge/change-plans/cfp-1497-wave2c-amendment-slot-reservation-wire.md
# Precedent byte-pattern: tests/scripts/cfp-1489/cfp-1489-spawn-prompt-head-pin.bats

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
LINT_SCRIPT="${WORKTREE_ROOT}/scripts/lib/check_amendment_slot_reservation.py"

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
  unset HOTFIX_BYPASS_AMENDMENT_SLOT_RESERVATION
  unset AMENDMENT_SLOT_RESERVATION_FILE
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1497-unused}"
}

# ─────────────────────────────── prerequisite checks ─────────────────────────

@test "PREREQ: lint Python script 존재 확인" {
  [ -f "$LINT_SCRIPT" ]
}

@test "PREREQ: python3 사용 가능 확인" {
  command -v python3
}

# ─────────────────────────── helper: fixture 생성 함수 ────────────────────────

# Make a synthetic ADR-RESERVATION.md fixture with given amendments_reserved entries.
# Usage: make_reservation_fixture "<path>" "<adr1>:<amend1>:<cfp1>,<adr2>:<amend2>:<cfp2>,..."
make_reservation_fixture() {
  local path="$1"
  local entries="$2"
  {
    cat << 'HEADER'
---
adr_number: null
title: ADR Reservation Registry (test fixture)
status: Active
---

# ADR Reservation Registry

```yaml
amendments_reserved:
HEADER
    local IFS=','
    for e in $entries; do
      local adr_num="${e%%:*}"
      local rest="${e#*:}"
      local amend_id="${rest%%:*}"
      local cfp="${rest##*:}"
      cat << ENTRY
  - adr_number: ${adr_num}
    amendment_id: ${amend_id}
    reserved_by_cfp: ${cfp}
    reservation_date: 2026-05-24 KST
    status: active
ENTRY
    done
    echo '```'
  } > "$path"
}

# Make a synthetic ADR file with given amendment_id entries in frontmatter.
# Usage: make_adr_fixture "<path>" "<adr_number>" "<amend_id1>,<amend_id2>,..."
make_adr_fixture() {
  local path="$1"
  local adr_num="$2"
  local amend_ids="$3"
  {
    cat << HEADER
---
adr_number: ${adr_num}
title: Test ADR ${adr_num}
status: Active
category: governance
amendments:
HEADER
    local IFS=','
    for aid in $amend_ids; do
      cat << ENTRY
  - amendment_id: ${aid}
    carrier_story: CFP-TEST
ENTRY
    done
    cat << 'FOOTER'
---

# Test ADR body
FOOTER
  } > "$path"
}

# Make a non-ADR file (e.g. random markdown) — should be silent-skipped.
make_non_adr_fixture() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
# 일반 문서

이 file 은 docs/adr/ADR-*.md 영역이 아닌 일반 markdown 문서입니다.
silent skip 대상 (lint scope 외).
FIXTURE
}

# ─────────────────────────────── TC: presence/absence/conflict ────────────────

@test "TC-1 PRESENCE: Amendment + matching reservation row → PASS (warn=0, exit 0)" {
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local reservation="${adr_dir}/ADR-RESERVATION.md"
  local adr_file="${adr_dir}/ADR-082-test.md"

  make_reservation_fixture "$reservation" "82:17:CFP-1435"
  make_adr_fixture "$adr_file" "82" "17"

  AMENDMENT_SLOT_RESERVATION_FILE="$reservation" run python3 "$LINT_SCRIPT" "$adr_file"
  # warning-tier — 항상 exit 0
  [ "$status" -eq 0 ]
  # WARN 없음 확인
  [[ "$output" != *"[WARN-MISSING-RESERVATION]"* ]]
  [[ "$output" != *"[WARN-CONCURRENT-CONFLICT]"* ]]
  # PASS marker 확인
  [[ "$output" == *"OK"* ]] || [[ "$output" == *"PASS"* ]]
}

@test "TC-2 ABSENCE: Amendment without matching reservation row → [WARN-MISSING-RESERVATION]" {
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local reservation="${adr_dir}/ADR-RESERVATION.md"
  local adr_file="${adr_dir}/ADR-082-test.md"

  # Reservation has DIFFERENT slot — ADR-099/99 not 82/17
  make_reservation_fixture "$reservation" "99:99:CFP-NONE"
  make_adr_fixture "$adr_file" "82" "17"

  AMENDMENT_SLOT_RESERVATION_FILE="$reservation" run python3 "$LINT_SCRIPT" "$adr_file"
  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # WARN-MISSING-RESERVATION 발화 확인
  [[ "$output" == *"[WARN-MISSING-RESERVATION]"* ]]
}

@test "TC-3 CONFLICT: 2+ rows claim same slot → [WARN-CONCURRENT-CONFLICT]" {
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local reservation="${adr_dir}/ADR-RESERVATION.md"

  # Two rows reserving SAME (adr_number=82, amendment_id=17) slot
  make_reservation_fixture "$reservation" "82:17:CFP-1435,82:17:CFP-1437"

  AMENDMENT_SLOT_RESERVATION_FILE="$reservation" run python3 "$LINT_SCRIPT" "$reservation"
  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # WARN-CONCURRENT-CONFLICT 발화 확인
  [[ "$output" == *"[WARN-CONCURRENT-CONFLICT]"* ]]
}

# ─────────────────────────────── TC: skip / FP-완화 guards ────────────────────

@test "TC-4 SKIP-NON-ADR-FILE: non-ADR file → silent skip (no warn)" {
  local fixture="${TEST_TMP}/normal-doc.md"
  make_non_adr_fixture "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # WARN 발화 금지 (silent skip)
  [[ "$output" != *"[WARN-MISSING-RESERVATION]"* ]]
  [[ "$output" != *"[WARN-CONCURRENT-CONFLICT]"* ]]
}

@test "TC-4-negative: non-ADR fixture 에서 exit 1 절대 발화 금지" {
  local fixture="${TEST_TMP}/normal-doc.md"
  make_non_adr_fixture "$fixture"

  run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  [ "$status" -ne 1 ]
}

@test "TC-5 SKIP-TEMPLATES-PATH: file under templates/** → silent skip (FP-완화 guard 1)" {
  local templates_dir="${TEST_TMP}/templates/adr-canonical"
  mkdir -p "$templates_dir"
  local fixture="${templates_dir}/ADR-082-canonical-example.md"
  make_adr_fixture "$fixture" "82" "99"  # 99 not reserved

  # Reservation has nothing matching — would normally warn, but templates/** = skip
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local reservation="${adr_dir}/ADR-RESERVATION.md"
  make_reservation_fixture "$reservation" "1:1:CFP-NONE"

  AMENDMENT_SLOT_RESERVATION_FILE="$reservation" run python3 "$LINT_SCRIPT" "$fixture"
  [ "$status" -eq 0 ]
  # templates/** path = silent skip
  [[ "$output" != *"[WARN-MISSING-RESERVATION]"* ]]
  [[ "$output" != *"[WARN-CONCURRENT-CONFLICT]"* ]]
}

# ─────────────────────────────── TC: discriminating + regression ─────────────

@test "TC-6 DISCRIMINATING: matched + unmatched Amendment in same file → unmatched wins (genuine warn)" {
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local reservation="${adr_dir}/ADR-RESERVATION.md"
  local adr_file="${adr_dir}/ADR-082-test.md"

  # Reserve only amendment_id 17 (NOT 18)
  make_reservation_fixture "$reservation" "82:17:CFP-1435"
  # ADR file has BOTH amendment_id 17 (matched) and 18 (unmatched)
  make_adr_fixture "$adr_file" "82" "17,18"

  AMENDMENT_SLOT_RESERVATION_FILE="$reservation" run python3 "$LINT_SCRIPT" "$adr_file"
  [ "$status" -eq 0 ]
  # Unmatched Amendment 18 → WARN-MISSING-RESERVATION 발화 의무
  [[ "$output" == *"[WARN-MISSING-RESERVATION]"* ]]
  [[ "$output" == *"Amendment 18"* ]]
}

@test "TC-7 REGRESSION-GUARD: multiple Amendments all with matching rows → PASS" {
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local reservation="${adr_dir}/ADR-RESERVATION.md"
  local adr_file="${adr_dir}/ADR-082-test.md"

  # Reserve all three amendments
  make_reservation_fixture "$reservation" "82:15:CFP-1437,82:16:CFP-1436,82:17:CFP-1435"
  make_adr_fixture "$adr_file" "82" "15,16,17"

  AMENDMENT_SLOT_RESERVATION_FILE="$reservation" run python3 "$LINT_SCRIPT" "$adr_file"
  [ "$status" -eq 0 ]
  # 모든 Amendment matched → PASS
  [[ "$output" != *"[WARN-MISSING-RESERVATION]"* ]]
  [[ "$output" != *"[WARN-CONCURRENT-CONFLICT]"* ]]
}

# ─────────────────────────────── TC: bypass env ──────────────────────────────

@test "TC-8 BYPASS-ENV: HOTFIX_BYPASS_AMENDMENT_SLOT_RESERVATION=1 → immediate exit 0" {
  local adr_dir="${TEST_TMP}/docs/adr"
  mkdir -p "$adr_dir"
  local reservation="${adr_dir}/ADR-RESERVATION.md"
  local adr_file="${adr_dir}/ADR-082-test.md"

  # Setup would normally warn (no matching reservation)
  make_reservation_fixture "$reservation" "99:99:CFP-NONE"
  make_adr_fixture "$adr_file" "82" "17"

  HOTFIX_BYPASS_AMENDMENT_SLOT_RESERVATION=1 \
    AMENDMENT_SLOT_RESERVATION_FILE="$reservation" \
    run python3 "$LINT_SCRIPT" "$adr_file"
  [ "$status" -eq 0 ]
  # bypass = WARN 발화 금지 (lint 자체가 skip)
  [[ "$output" != *"[WARN-MISSING-RESERVATION]"* ]]
  [[ "$output" != *"[WARN-CONCURRENT-CONFLICT]"* ]]
  # BYPASS marker 확인
  [[ "$output" == *"BYPASS=1"* ]]
}
