#!/usr/bin/env bats
# tests/scripts/cfp-1216/cfp-1216-amendment-stale.bats
# CFP-1216 Phase 2 — ADR amendment number frontmatter verify mechanical lint TDD
# QADeveloperAgent TDD (RED written first, GREEN after implementation)
#
# Check (a) — ADR frontmatter self-consistency:
#   - 연속 amendment id → PASS
#   - 중복 amendment id → WARN (exit 0)
#   - frontmatter max ≠ body max → WARN (exit 0)
#   - 의도적 gap (id 4 스킵) → WARN advisory (exit 0)
#
# Check (b) — cross-doc citation forward-staleness:
#   - "ADR-082 Amendment 99" (max+1 초과 많이) → WARN
#   - "ADR-082 Amendment 3" (실재 amendment) → WARN 없음
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — positive + negative 2-assertion per TC
#   Layer 3 — 임시 fixture 파일 사용 (실제 repo ADR 의존 금지)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# SSOT: ADR-082 Amendment 6 §결정 9 (amendment-number-frontmatter-verify)
# Change-plan: CFP-1216 Phase 2

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
LINT_SCRIPT="${WORKTREE_ROOT}/scripts/lib/check_amendment_number_stale.py"

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
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1216-unused}"
}

# ─────────────────────────────── prerequisite checks ─────────────────────────

@test "PREREQ: lint Python script 존재 확인" {
  [ -f "$LINT_SCRIPT" ]
}

@test "PREREQ: pyyaml 설치 확인" {
  python3 -c "import yaml"
}

# ─────────────────────────── helper: fixture 생성 함수 ────────────────────────

# 정상 fixture: 연속 amendment_id (1, 2, 3) + body Amendment 3 헤더 일치
make_fixture_clean() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
---
adr_number: 999
title: 테스트 ADR — 정상 연속 amendment
status: Accepted
category: governance
date: 2026-05-22
amendments:
  - amendment_id: 1
    carrier_story: CFP-100
    date: 2026-05-01
    summary: "Amendment 1 요약"
  - amendment_id: 2
    carrier_story: CFP-200
    date: 2026-05-10
    summary: "Amendment 2 요약"
  - amendment_id: 3
    carrier_story: CFP-300
    date: 2026-05-20
    summary: "Amendment 3 요약"
---

## 결정 내용

본문 내용.

## Amendment 1

첫 번째 Amendment.

## Amendment 2

두 번째 Amendment.

## Amendment 3

세 번째 Amendment.
FIXTURE
}

# 중복 id fixture: amendment_id 2 가 두 번 등장
make_fixture_dup_id() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
---
adr_number: 999
title: 테스트 ADR — 중복 amendment id
status: Accepted
category: governance
date: 2026-05-22
amendments:
  - amendment_id: 1
    carrier_story: CFP-100
    date: 2026-05-01
    summary: "Amendment 1"
  - amendment_id: 2
    carrier_story: CFP-200
    date: 2026-05-10
    summary: "Amendment 2 첫 번째"
  - amendment_id: 2
    carrier_story: CFP-201
    date: 2026-05-11
    summary: "Amendment 2 중복"
---

## Amendment 1

첫 번째.

## Amendment 2

두 번째.
FIXTURE
}

# frontmatter max ≠ body max fixture
# frontmatter = max 3, body = max Amendment 2 헤더만 존재
make_fixture_max_mismatch() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
---
adr_number: 999
title: 테스트 ADR — frontmatter ≠ body max
status: Accepted
category: governance
date: 2026-05-22
amendments:
  - amendment_id: 1
    carrier_story: CFP-100
    date: 2026-05-01
    summary: "Amendment 1"
  - amendment_id: 2
    carrier_story: CFP-200
    date: 2026-05-10
    summary: "Amendment 2"
  - amendment_id: 3
    carrier_story: CFP-300
    date: 2026-05-20
    summary: "Amendment 3 — frontmatter에만 존재"
---

## Amendment 1

첫 번째.

## Amendment 2

두 번째 (body 최대 = 2, frontmatter 최대 = 3 → mismatch WARN).
FIXTURE
}

# 의도적 gap fixture: id 1, 2, 4 (3 생략)
make_fixture_gap() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
---
adr_number: 999
title: 테스트 ADR — 의도적 gap (id 3 생략)
status: Accepted
category: governance
date: 2026-05-22
amendments:
  - amendment_id: 1
    carrier_story: CFP-100
    date: 2026-05-01
    summary: "Amendment 1"
  - amendment_id: 2
    carrier_story: CFP-200
    date: 2026-05-10
    summary: "Amendment 2"
  - amendment_id: 4
    carrier_story: CFP-400
    date: 2026-05-22
    summary: "Amendment 4 (3 intentionally skipped)"
---

## Amendment 1

첫 번째.

## Amendment 2

두 번째.

## Amendment 4

네 번째 (gap Advisory WARN).
FIXTURE
}

# cross-doc citation fixture: way-forward citation (ADR-082 Amendment 99)
make_fixture_forward_citation() {
  local path="$1"
  local target_adr_path="$2"
  cat > "$path" << 'FIXTURE'
---
title: 테스트 change-plan — 전방 인용 포함
kind: change-plan
---

이 문서는 ADR-999 Amendment 99 를 인용합니다 (해당 ADR max+1 초과 — WARN 대상).
FIXTURE
}

# cross-doc citation fixture: 정상 기존 amendment 인용
make_fixture_existing_citation() {
  local path="$1"
  cat > "$path" << 'FIXTURE'
---
title: 테스트 change-plan — 정상 인용
kind: change-plan
---

이 문서는 ADR-999 Amendment 2 를 인용합니다 (실재 amendment — WARN 없음).
FIXTURE
}

# ─────────────────────────────── Check (a) TC ────────────────────────────────

@test "TC-A1: 연속 amendment_id → PASS (warning 없음, exit 0)" {
  local adr_file="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$adr_file"

  run python3 "$LINT_SCRIPT" "$adr_file"
  # 경고 모드 — exit 0 항상 (warning 이 있어도)
  [ "$status" -eq 0 ]
  # WARN 없음 확인 (clean fixture 는 WARN 없어야 함)
  [[ "$output" != *"[WARN]"* ]]
}

@test "TC-A1-negative: 연속 amendment_id 에서 ERROR 미발생 확인" {
  local adr_file="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$adr_file"

  run python3 "$LINT_SCRIPT" "$adr_file"
  [ "$status" -eq 0 ]
  # ERROR 미발생 확인
  [[ "$output" != *"[ERROR]"* ]]
}

@test "TC-A2: 중복 amendment_id → WARN 발생 (exit 0 유지)" {
  local adr_file="${TEST_TMP}/ADR-999-dup.md"
  make_fixture_dup_id "$adr_file"

  run python3 "$LINT_SCRIPT" "$adr_file"
  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # 중복 WARN 포함 확인
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"duplicate"* ]] || [[ "$output" == *"중복"* ]]
}

@test "TC-A2-negative: 중복 fixture 에서 exit 0 보장 확인" {
  local adr_file="${TEST_TMP}/ADR-999-dup.md"
  make_fixture_dup_id "$adr_file"

  run python3 "$LINT_SCRIPT" "$adr_file"
  # warning-tier = exit 0 강제 (차단 금지)
  [ "$status" -eq 0 ]
}

@test "TC-A3: frontmatter max ≠ body max → WARN 발생 (exit 0 유지)" {
  local adr_file="${TEST_TMP}/ADR-999-mismatch.md"
  make_fixture_max_mismatch "$adr_file"

  run python3 "$LINT_SCRIPT" "$adr_file"
  [ "$status" -eq 0 ]
  # mismatch WARN 포함
  [[ "$output" == *"[WARN]"* ]]
  # frontmatter max / body max 언급
  [[ "$output" == *"max"* ]] || [[ "$output" == *"mismatch"* ]] || [[ "$output" == *"body"* ]]
}

@test "TC-A3-negative: mismatch fixture 에서 exit 1 발생하지 않음 확인" {
  local adr_file="${TEST_TMP}/ADR-999-mismatch.md"
  make_fixture_max_mismatch "$adr_file"

  run python3 "$LINT_SCRIPT" "$adr_file"
  # warning only — exit 1 차단 금지
  [ "$status" -ne 1 ]
}

@test "TC-A4: 의도적 gap (id 3 생략) → WARN advisory (exit 0 유지)" {
  local adr_file="${TEST_TMP}/ADR-999-gap.md"
  make_fixture_gap "$adr_file"

  run python3 "$LINT_SCRIPT" "$adr_file"
  # gap advisory는 경고 (exit 0)
  [ "$status" -eq 0 ]
  # gap 관련 WARN 출력
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"gap"* ]] || [[ "$output" == *"missing"* ]] || [[ "$output" == *"3"* ]]
}

@test "TC-A4-negative: gap fixture 에서 exit 0 보장 확인 (advisory = 차단 금지)" {
  local adr_file="${TEST_TMP}/ADR-999-gap.md"
  make_fixture_gap "$adr_file"

  run python3 "$LINT_SCRIPT" "$adr_file"
  [ "$status" -eq 0 ]
}

# ─────────────────────────────── Check (b) TC ────────────────────────────────

@test "TC-B1: forward citation (Amendment 99 >> max+1) → WARN 발생 (exit 0)" {
  # 대상 ADR fixture (max amendment_id = 3)
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  # cross-doc 파일 (ADR-999 Amendment 99 인용)
  local doc_file="${TEST_TMP}/test-change-plan.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: forward citation test
---

ADR-999 Amendment 99 를 인용합니다.
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  [ "$status" -eq 0 ]
  # forward citation WARN 포함
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"99"* ]] || [[ "$output" == *"stale"* ]] || [[ "$output" == *"forward"* ]]
}

@test "TC-B1-negative: forward citation 에서 exit 0 보장 (warning-tier)" {
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  local doc_file="${TEST_TMP}/test-change-plan-2.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: forward citation test 2
---

ADR-999 Amendment 99 를 인용합니다.
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  [ "$status" -eq 0 ]
}

@test "TC-B2 [Amendment 7 양방향]: 이미 land 된 amendment 인용 (Amendment 2 with max=3) → [BACKWARD-STALE] WARN" {
  # CFP-1312 / ADR-082 Amendment 7 — `M = max+1` 정확 next-slot 외 모두 stale.
  # M=2, max=3 → cited_m <= max → BACKWARD-STALE 인용 패턴 (CFP-1293 #3 occurrence 재현).
  # 본 TC 는 CFP-1216 기존 `M ≤ max → 정상` 가정을 정정 (Amendment 7 양방향 wording 정합).
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  # cross-doc 파일 (ADR-999 Amendment 2 인용 — backward stale, max=3 시점)
  local doc_file="${TEST_TMP}/test-backward-citation.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: backward citation test (Amendment 7 양방향 expanded)
---

이 문서는 ADR-999 Amendment 2 를 인용합니다 (max=3 시점, backward-staleness 패턴).
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # Amendment 7 — backward-staleness WARN 출력 확인
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"[BACKWARD-STALE]"* ]]
  [[ "$output" == *"Amendment 2"* ]]
}

@test "TC-B2-negative [Amendment 7]: backward fixture 에서 exit 0 보장 (warning-tier)" {
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  local doc_file="${TEST_TMP}/test-backward-citation-2.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: backward citation test 2
---

ADR-999 Amendment 2 backward staleness 패턴.
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  # warning-tier = exit 0 강제 (차단 금지)
  [ "$status" -eq 0 ]
}

# ─────────────────── Check (b) Amendment 7 양방향 staleness TC ─────────────────

@test "TC-B-BWD-EXACT [Amendment 7]: backward exact-match (M = max) → [BACKWARD-STALE] WARN" {
  # max=3 fixture, doc 가 Amendment 3 (M=max) 인용 → backward exact-match
  # 가장 자주 발생하는 패턴 — 이미 land 된 latest slot 을 next slot 으로 오해
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  local doc_file="${TEST_TMP}/test-bwd-exact.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: backward exact-match (M = max)
---

ADR-999 Amendment 3 인용 (M=max=3, exact backward stale).
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"[BACKWARD-STALE]"* ]]
  [[ "$output" == *"Amendment 3"* ]] || [[ "$output" == *"M=3"* ]]
}

@test "TC-B-BWD-DEEP [Amendment 7]: deep backward (M < max-1) → [BACKWARD-STALE] WARN" {
  # max=3 fixture, doc 가 Amendment 1 (M = max-2) 인용 → deep backward (historical slot)
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  local doc_file="${TEST_TMP}/test-bwd-deep.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: deep backward citation
---

ADR-999 Amendment 1 인용 (M=1 < max=3, deep backward historical reference).
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"[BACKWARD-STALE]"* ]]
}

@test "TC-B-FWD-EXACT-NEXT [Amendment 7]: 정확 next-slot (M = max+1) → PASS no [WARN]" {
  # max=3 fixture, doc 가 Amendment 4 (M = max+1) 인용 → 정확 next-slot pass
  # AC-3 정확 next-slot pass false-positive 0 verify
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  local doc_file="${TEST_TMP}/test-fwd-exact-next.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: 정확 next-slot citation
---

ADR-999 Amendment 4 신설 예정 (M=max+1=4, 정확 next-slot 사용).
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  [ "$status" -eq 0 ]
  # Amendment 7 양방향 — M=max+1 = PASS, [WARN] 출력 0
  [[ "$output" != *"[WARN]"* ]] || [[ "$output" != *"Amendment 4"* ]]
  [[ "$output" != *"[BACKWARD-STALE]"* ]]
  [[ "$output" != *"[FORWARD-STALE]"* ]]
}

@test "TC-B-FWD-LABEL [Amendment 7]: forward staleness label 정확 codify ([FORWARD-STALE])" {
  # max=3 fixture, doc 가 Amendment 99 (M >> max+1) 인용 → forward staleness label
  # AC-2 forward retain regression 0 + Amendment 7 label format 확인
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  local doc_file="${TEST_TMP}/test-fwd-label.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: forward staleness label test
---

ADR-999 Amendment 99 way-forward (M=99 >> max+1=4).
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
  # Amendment 7 — [FORWARD-STALE] label 명시 codify
  [[ "$output" == *"[FORWARD-STALE]"* ]]
  [[ "$output" != *"[BACKWARD-STALE]"* ]]
}

@test "TC-B-TEMPLATE-EXEMPT [Amendment 7]: templates/** path filter — canonical example 면제" {
  # templates/ 디렉토리 안 fixture 가 stale citation 보유해도 lint scope 제외 (FP-완화 guard 2)
  local target_adr="${TEST_TMP}/ADR-999-clean.md"
  make_fixture_clean "$target_adr"

  # templates/ subdirectory 안 doc 생성
  local templates_dir="${TEST_TMP}/templates"
  mkdir -p "$templates_dir"
  local doc_file="${templates_dir}/test-canonical-example.md"
  cat > "$doc_file" << 'CROSSDOC'
---
title: canonical template example (templates/** exempt)
---

이 template fixture 안에 ADR-999 Amendment 99 와 ADR-999 Amendment 1 가 의도된 canonical example 으로 들어 있다 (lint 면제 대상).
CROSSDOC

  run python3 "$LINT_SCRIPT" --adr-dir "$TEST_TMP" "$doc_file"
  [ "$status" -eq 0 ]
  # templates/** exempt — WARN 출력 0 (path filter guard 2 정합)
  [[ "$output" != *"[WARN]"* ]]
  [[ "$output" != *"[FORWARD-STALE]"* ]]
  [[ "$output" != *"[BACKWARD-STALE]"* ]]
}

# ────────────────────────────── bypass env TC ────────────────────────────────

@test "TC-BYPASS: HOTFIX_BYPASS_AMENDMENT_NUMBER_STALE=1 → 즉시 exit 0" {
  # 중복 amendment_id fixture (WARN 대상)
  local adr_file="${TEST_TMP}/ADR-999-dup.md"
  make_fixture_dup_id "$adr_file"

  HOTFIX_BYPASS_AMENDMENT_NUMBER_STALE=1 run python3 "$LINT_SCRIPT" "$adr_file"
  [ "$status" -eq 0 ]
  # bypass 시 WARN 출력 없음
  [[ "$output" != *"[WARN]"* ]]
}

# ─────────────────────────── 실제 repo ADR self-test ─────────────────────────

@test "SELF-TEST: 실제 ADR-082 frontmatter 파싱 — crash 없음 (grace)" {
  local adr_082="${WORKTREE_ROOT}/docs/adr/ADR-082-write-time-self-write-verification-mandate.md"
  [ -f "$adr_082" ] || skip "ADR-082 부재 — skip"

  run python3 "$LINT_SCRIPT" "$adr_082"
  # crash 없이 exit 0 (amendment_id shape → amendments: list)
  [ "$status" -eq 0 ]
}

@test "SELF-TEST: 실제 ADR-063 frontmatter 파싱 — crash 없음 (amendment: N shape)" {
  local adr_063="${WORKTREE_ROOT}/docs/adr/ADR-063-marketplace-atomic-invariant.md"
  [ -f "$adr_063" ] || skip "ADR-063 부재 — skip"

  run python3 "$LINT_SCRIPT" "$adr_063"
  # crash 없이 exit 0 (amendment: N shape)
  [ "$status" -eq 0 ]
}

@test "SELF-TEST: 실제 ADR-027 frontmatter 파싱 — crash 없음 (string list shape + gap)" {
  local adr_027="${WORKTREE_ROOT}/docs/adr/ADR-027-consumer-adoption-protocol.md"
  [ -f "$adr_027" ] || skip "ADR-027 부재 — skip"

  run python3 "$LINT_SCRIPT" "$adr_027"
  # crash 없이 exit 0 (string list shape — amendment_id 미추출)
  [ "$status" -eq 0 ]
}

# ────── Amendment 7 — self-reference exemption (FP-완화 guard 1) ──────

@test "TC-B-SELF-REF-EXEMPT [Amendment 7]: ADR file 자체 안 자기 인용 → Check (b) skip (non-ADR filter)" {
  # ADR file (filename ADR-NNN*) 자체는 Check (a) 영역 / Check (b) 비대상.
  # caller (main()) 가 file name regex 로 ADR vs non-ADR 분류 → ADR file 은 check_doc_citations 호출 영역 외.
  # 본 TC = ADR file 자체에서 자기 amendment 인용 시 [WARN] 출력 0 verify.
  local adr_file="${TEST_TMP}/ADR-999-self-ref.md"
  cat > "$adr_file" << 'FIXTURE'
---
adr_number: 999
title: 테스트 ADR — self-reference exempt
status: Accepted
category: governance
date: 2026-05-23
amendments:
  - amendment_id: 1
    carrier_story: CFP-100
    date: 2026-05-01
    summary: "Amendment 1"
  - amendment_id: 2
    carrier_story: CFP-200
    date: 2026-05-10
    summary: "Amendment 2"
  - amendment_id: 3
    carrier_story: CFP-300
    date: 2026-05-20
    summary: "Amendment 3"
---

## Amendment 1

본 ADR-999 Amendment 1 의 본문 — 자기 인용 (self-reference, Check (b) 비대상).

## Amendment 2

ADR-999 Amendment 2 또한 본 ADR 자체 안 정상 historical reference.

## Amendment 3

ADR-999 Amendment 3 본문 — current latest slot.
FIXTURE

  # ADR file 명시 (basename ADR-*) → main() ADR 분류 → Check (a) only, Check (b) 비대상
  run python3 "$LINT_SCRIPT" "$adr_file"
  [ "$status" -eq 0 ]
  # self-reference [BACKWARD-STALE] [WARN] 출력 0 (Check (b) 미적용 — ADR-file = Check (a) 영역)
  [[ "$output" != *"[BACKWARD-STALE]"* ]]
  [[ "$output" != *"[FORWARD-STALE]"* ]]
}
