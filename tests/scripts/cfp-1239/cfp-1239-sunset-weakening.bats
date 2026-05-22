#!/usr/bin/env bats
# tests/scripts/cfp-1239/cfp-1239-sunset-weakening.bats
# CFP-1239 Phase 2 — ADR-058 Amendment 1 evidence-gate weakening lint TDD
# CFP-1249 — forbid-list 축소 감지 (2nd weakening pattern) 확장
# QADeveloperAgent TDD (RED written first, GREEN after implementation)
#
# 검사 대상: scripts/lib/check_sunset_weakening_evidence.py
#   [CFP-1239] is_transitional false→true (약화) + sunset_justification evidence 부재 → [WARN]
#   [CFP-1239] is_transitional false→true (약화) + sunset_justification evidence 보유 → PASS
#   [CFP-1239] is_transitional true→false (강화) → 항상 PASS (면제)
#   [CFP-1239] is_transitional 변경 없음 → PASS
#   [CFP-1249] 카테고리 (a) forbid-list row 제거 → [WARN]
#   [CFP-1249] 카테고리 (a) forbid-list row 추가 (강화) → PASS (WARN 없음)
#   [CFP-1249] 카테고리 (a) 표 무변경 / 비-표 변경 → PASS (WARN 없음)
#
# 3-layer defense (#960 always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — positive + negative 2-assertion per TC
#   Layer 3 — 임시 git 레포 fixture 사용 (실제 repo ADR 의존 금지)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#
# Framework: bats (codeforge convention)
# SSOT: ADR-058 Amendment 1 §결정 5 (evidence-gate)
# Change-plan: CFP-1239

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
LINT_SCRIPT="${WORKTREE_ROOT}/scripts/lib/check_sunset_weakening_evidence.py"

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

  # git temp 레포 초기화 (diff 기반 테스트용)
  GIT_REPO="${TEST_TMP}/repo"
  mkdir -p "$GIT_REPO"
  git -C "$GIT_REPO" init -q
  git -C "$GIT_REPO" config user.email "test@codeforge.test"
  git -C "$GIT_REPO" config user.name "CFP-1239 Test"
  export GIT_REPO
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1239-unused}"
}

# ─────────────────────────────── prerequisite checks ─────────────────────────

@test "PREREQ: lint Python script 존재 확인" {
  [ -f "$LINT_SCRIPT" ]
}

@test "PREREQ: pyyaml 설치 확인" {
  python3 -c "import yaml"
}

# ─────────────────────────── helper: git diff fixture 생성 ───────────────────

# OLD 버전 commit → NEW 버전 파일 작성 후 HEAD~1 기준 diff 구성
# 사용법: setup_git_diff <repo_dir> <filename> <old_content> <new_content>
setup_git_diff() {
  local repo="$1"
  local fname="$2"
  local old="$3"
  local new="$4"

  # OLD 상태 commit
  printf '%s' "$old" > "${repo}/${fname}"
  git -C "$repo" add "${fname}"
  git -C "$repo" commit -q -m "old state"

  # NEW 상태 (commit 안 함 — working tree diff 로 사용)
  printf '%s' "$new" > "${repo}/${fname}"
  git -C "$repo" add "${fname}"
  git -C "$repo" commit -q -m "new state"
}

# ─── fixture 내용 ─────────────────────────────────────────────────────────────

# OLD: is_transitional: false (영구 ADR)
adr_old_permanent() {
  cat << 'YAML'
---
adr_number: 999
title: 테스트 ADR
status: Accepted
category: governance
is_transitional: false
amendment_log: []
---

## 결정 내용

본문.
YAML
}

# NEW (약화): is_transitional: true + evidence-bearing sunset_justification
adr_new_weakened_with_evidence() {
  cat << 'YAML'
---
adr_number: 999
title: 테스트 ADR
status: Accepted
category: governance
is_transitional: true
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-999
    date: 2026-05-22
    summary: "Amendment 1 — 약화"
    sunset_justification: "pattern_count 0건 (6개월 기간, 측정 도구 check-foo.sh). 환경 변화로 원래 위험 소멸."
---

## 결정 내용

본문.

## 해소 기준

metric: pattern_count 0건 / who: PMOAgent / how: check-foo.sh 월간 cron.
YAML
}

# NEW (약화): is_transitional: true + bare "N/A" (evidence 미보유)
adr_new_weakened_no_evidence() {
  cat << 'YAML'
---
adr_number: 999
title: 테스트 ADR
status: Accepted
category: governance
is_transitional: true
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-999
    date: 2026-05-22
    summary: "Amendment 1 — 약화"
    sunset_justification: "N/A"
---

## 결정 내용

본문.
YAML
}

# NEW (약화): is_transitional: true + sunset_justification 완전 누락
adr_new_weakened_missing_justification() {
  cat << 'YAML'
---
adr_number: 999
title: 테스트 ADR
status: Accepted
category: governance
is_transitional: true
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-999
    date: 2026-05-22
    summary: "Amendment 1 — 약화, justification 없음"
---

## 결정 내용

본문.
YAML
}

# OLD: is_transitional: true (이미 transitional)
adr_old_transitional() {
  cat << 'YAML'
---
adr_number: 999
title: 테스트 ADR
status: Accepted
category: governance
is_transitional: true
amendment_log: []
---

## 결정 내용

본문.
YAML
}

# NEW (강화): is_transitional: false (permanent-ize, ratchet 강화)
adr_new_strengthened() {
  cat << 'YAML'
---
adr_number: 999
title: 테스트 ADR
status: Accepted
category: governance
is_transitional: false
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-888
    date: 2026-05-22
    summary: "Amendment 1 — 강화 (ratchet)"
    sunset_justification: "N/A — ratchet 강화"
---

## 결정 내용

본문.
YAML
}

# OLD = NEW: is_transitional 변경 없음 (false → false)
adr_unchanged_permanent() {
  cat << 'YAML'
---
adr_number: 999
title: 테스트 ADR
status: Accepted
category: governance
is_transitional: false
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-777
    date: 2026-05-20
    summary: "Amendment 1"
    sunset_justification: "N/A — ratchet 강화"
---

## 결정 내용

본문.
YAML
}

# ─────────────────────────────────── TC 그룹 A: 약화 감지 ────────────────────

@test "TC-A1: false→true 약화 + evidence 보유 → PASS (WARN 없음)" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_new_weakened_with_evidence)"

  # HEAD~1 기준 diff: lint 에 GIT_BASE + 파일 경로 전달
  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  # warning-tier — exit 0 항상
  [ "$status" -eq 0 ]
  # evidence 보유 시 WARN 없어야 함
  [[ "$output" != *"[WARN]"* ]]
}

@test "TC-A1-negative: evidence 보유 약화에서 exit 1 미발생" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_new_weakened_with_evidence)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -ne 1 ]
}

@test "TC-A2: false→true 약화 + bare N/A → WARN 발생 (exit 0 유지)" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_new_weakened_no_evidence)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  # warning-tier — exit 0 유지
  [ "$status" -eq 0 ]
  # evidence 미보유 → WARN 출력 의무
  [[ "$output" == *"[WARN]"* ]]
}

@test "TC-A2-negative: bare N/A 약화 에서 exit 0 보장 (warning-tier)" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_new_weakened_no_evidence)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -eq 0 ]
}

@test "TC-A3: false→true 약화 + sunset_justification 누락 → WARN 발생 (exit 0 유지)" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_new_weakened_missing_justification)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
}

@test "TC-A3-negative: sunset_justification 누락 약화 에서 exit 0 보장" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_new_weakened_missing_justification)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -eq 0 ]
}

# ─────────────────────────────────── TC 그룹 B: 강화 면제 ────────────────────

@test "TC-B1: true→false 강화 (ratchet) → PASS (WARN 없음, N/A 허용)" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_transitional)" "$(adr_new_strengthened)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -eq 0 ]
  # 강화 방향 → WARN 없음 (N/A sunset_justification 허용)
  [[ "$output" != *"[WARN]"* ]]
}

@test "TC-B1-negative: 강화 방향 에서 exit 0 보장" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_transitional)" "$(adr_new_strengthened)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -eq 0 ]
}

# ─────────────────────────────────── TC 그룹 C: 변경 없음 ───────────────────

@test "TC-C1: is_transitional 변경 없음 (false→false) → PASS" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_unchanged_permanent)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -eq 0 ]
  [[ "$output" != *"[WARN]"* ]]
}

@test "TC-C1-negative: 변경 없음 에서 false positive WARN 없음 확인" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_unchanged_permanent)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -eq 0 ]
}

# ─────────────────────────────────── TC 그룹 D: bypass env ──────────────────

@test "TC-D1: HOTFIX_BYPASS_SUNSET_WEAKENING_EVIDENCE=1 → 즉시 exit 0 (WARN 없음)" {
  local adr_file="ADR-999-test.md"
  setup_git_diff "$GIT_REPO" "$adr_file" \
    "$(adr_old_permanent)" "$(adr_new_weakened_no_evidence)"

  HOTFIX_BYPASS_SUNSET_WEAKENING_EVIDENCE=1 \
    run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  [ "$status" -eq 0 ]
  [[ "$output" != *"[WARN]"* ]]
}

# ─────────────────────────────────── TC 그룹 E: edge case ───────────────────

@test "TC-E1: 신규 ADR (base 에 없음) — 모두 NEW → 약화 없음 (PASS)" {
  local adr_file="ADR-999-brand-new.md"
  # 신규 파일만 추가 (OLD 없음)
  printf '%s' "$(adr_new_weakened_no_evidence)" > "${GIT_REPO}/${adr_file}"
  git -C "$GIT_REPO" add "${adr_file}"
  git -C "$GIT_REPO" commit -q -m "initial commit (no prior state)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  # base 에 없어서 OLD frontmatter 없음 → 약화 판정 불가 → PASS
  [ "$status" -eq 0 ]
}

@test "TC-E2: frontmatter 파싱 불가 → crash 없이 WARN + exit 0" {
  # 깨진 YAML frontmatter
  local adr_file="ADR-999-broken.md"
  local old_content="---
is_transitional: false
---
본문
"
  local new_content="---
is_transitional: true
: broken_yaml: [unclosed
---
본문
"
  setup_git_diff "$GIT_REPO" "$adr_file" "$old_content" "$new_content"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${adr_file}"

  # crash 금지 — exit 0 (fail-soft)
  [ "$status" -eq 0 ]
}

# ─────────────────────────────── 실제 repo self-test ─────────────────────────

@test "SELF-TEST: 실제 repo docs/adr/ 전체 — crash 없이 exit 0" {
  local adr_dir="${WORKTREE_ROOT}/docs/adr"
  [ -d "$adr_dir" ] || skip "docs/adr 디렉토리 없음"

  # 실제 repo 대상: base 미지정 (로컬 diff 없음 = 변경 없음 모드 → 전 파일 PASS)
  run python3 "$LINT_SCRIPT" --repo "$WORKTREE_ROOT" --base HEAD
  # crash 없이 exit 0
  [ "$status" -eq 0 ]
}

# ═══════════════════════════════════════════════════════════════════════════════
# CFP-1249 — forbid-list 축소 감지 (2nd weakening pattern) 테스트 케이스
# ═══════════════════════════════════════════════════════════════════════════════
#
# 테스트 대상 파일: docs/wording-dictionary.md 기반 git fixture
# 감지 패턴: 카테고리 (a) 표 데이터 row 제거 → [WARN]
# 면제: row 추가 / 표 무변경 / 비-표 변경 / 카테고리 (b) 변경 → PASS

# ─── forbid-list fixture 내용 ─────────────────────────────────────────────────

# OLD wording-dictionary.md — 카테고리 (a) 에 2개 row
wording_dict_old_two_rows() {
  cat << 'CONTENT'
---
schema_version: "1.0"
title: "테스트 wording dictionary"
---

# codeforge wording dictionary

## 카테고리 (a) — 사용 금지 어휘 (forbid)

| 어휘 | lint scope |
|---|---|
| 박제 / 못 박기 / pin / freezing | docs/** |
| 별 (standalone) | docs/adr/** |

## 카테고리 (b) — 사용 허용 + 평문 정의 동반 의무

| 어휘 | 평문 정의 |
|---|---|
| normative | "강제 규칙" |
CONTENT
}

# NEW wording-dictionary.md — 카테고리 (a) row 1개 제거 (약화 = WARN 대상)
wording_dict_new_one_row_removed() {
  cat << 'CONTENT'
---
schema_version: "1.0"
title: "테스트 wording dictionary"
---

# codeforge wording dictionary

## 카테고리 (a) — 사용 금지 어휘 (forbid)

| 어휘 | lint scope |
|---|---|
| 박제 / 못 박기 / pin / freezing | docs/** |

## 카테고리 (b) — 사용 허용 + 평문 정의 동반 의무

| 어휘 | 평문 정의 |
|---|---|
| normative | "강제 규칙" |
CONTENT
}

# NEW wording-dictionary.md — 카테고리 (a) row 추가 (강화 = PASS)
wording_dict_new_one_row_added() {
  cat << 'CONTENT'
---
schema_version: "1.0"
title: "테스트 wording dictionary"
---

# codeforge wording dictionary

## 카테고리 (a) — 사용 금지 어휘 (forbid)

| 어휘 | lint scope |
|---|---|
| 박제 / 못 박기 / pin / freezing | docs/** |
| 별 (standalone) | docs/adr/** |
| 신규어휘 | docs/** |

## 카테고리 (b) — 사용 허용 + 평문 정의 동반 의무

| 어휘 | 평문 정의 |
|---|---|
| normative | "강제 규칙" |
CONTENT
}

# NEW wording-dictionary.md — 카테고리 (a) 표 무변경, 카테고리 (b) 만 변경 (PASS)
wording_dict_new_only_cat_b_changed() {
  cat << 'CONTENT'
---
schema_version: "1.0"
title: "테스트 wording dictionary"
---

# codeforge wording dictionary

## 카테고리 (a) — 사용 금지 어휘 (forbid)

| 어휘 | lint scope |
|---|---|
| 박제 / 못 박기 / pin / freezing | docs/** |
| 별 (standalone) | docs/adr/** |

## 카테고리 (b) — 사용 허용 + 평문 정의 동반 의무

| 어휘 | 평문 정의 |
|---|---|
| normative | "강제 규칙" |
| ratchet | "강화 방향만 허용" |
CONTENT
}

# NEW wording-dictionary.md — 카테고리 (a) 표 완전 동일 + 비-표 산문 변경 (PASS)
# 주의: OLD==NEW 이면 git commit 이 "nothing to commit" 실패 → 비-표 산문 변경으로 구분
wording_dict_new_unchanged() {
  cat << 'CONTENT'
---
schema_version: "1.0"
title: "테스트 wording dictionary"
---

# codeforge wording dictionary

본문 설명 추가 (표는 동일 — PASS 검증용).

## 카테고리 (a) — 사용 금지 어휘 (forbid)

| 어휘 | lint scope |
|---|---|
| 박제 / 못 박기 / pin / freezing | docs/** |
| 별 (standalone) | docs/adr/** |

## 카테고리 (b) — 사용 허용 + 평문 정의 동반 의무

| 어휘 | 평문 정의 |
|---|---|
| normative | "강제 규칙" |
CONTENT
}

# ─────────────────────────── TC 그룹 F: forbid-list 축소 감지 ─────────────────

@test "TC-F1: 카테고리 (a) row 제거 (약화) → [WARN] 발생 (exit 0 유지)" {
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  setup_git_diff "$GIT_REPO" "$dict_file" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  # warning-tier — exit 0 항상
  [ "$status" -eq 0 ]
  # row 제거 감지 → WARN 출력 의무
  [[ "$output" == *"[WARN]"* ]]
}

@test "TC-F1-negative: 카테고리 (a) row 제거 시 exit 1 미발생" {
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  setup_git_diff "$GIT_REPO" "$dict_file" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  [ "$status" -ne 1 ]
}

@test "TC-F2: 카테고리 (a) row 추가 (강화) → PASS (WARN 없음)" {
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  setup_git_diff "$GIT_REPO" "$dict_file" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_added)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  [ "$status" -eq 0 ]
  # 강화 방향 → WARN 없음
  [[ "$output" != *"[WARN]"* ]]
}

@test "TC-F3: 카테고리 (a) 표 무변경 + 카테고리 (b) 만 변경 → PASS (WARN 없음)" {
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  setup_git_diff "$GIT_REPO" "$dict_file" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_only_cat_b_changed)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  [ "$status" -eq 0 ]
  [[ "$output" != *"[WARN]"* ]]
}

@test "TC-F4: 카테고리 (a) 표 완전 동일 (변경 없음) → PASS" {
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  setup_git_diff "$GIT_REPO" "$dict_file" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_unchanged)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  [ "$status" -eq 0 ]
  [[ "$output" != *"[WARN]"* ]]
}

@test "TC-F5: wording-dictionary.md 신규 파일 (base 에 없음) → PASS (면제)" {
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  # 신규 파일만 추가 (OLD 없음)
  printf '%s' "$(wording_dict_new_one_row_removed)" > "${GIT_REPO}/${dict_file}"
  git -C "$GIT_REPO" add "${dict_file}"
  git -C "$GIT_REPO" commit -q -m "initial commit (no prior state)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  # base 에 없음 → 약화 비교 불가 → PASS
  [ "$status" -eq 0 ]
}

@test "TC-F6: TC-F1 WARN 메시지에 제거된 row 내용 포함 확인" {
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  setup_git_diff "$GIT_REPO" "$dict_file" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  [ "$status" -eq 0 ]
  # WARN 메시지에 제거된 row 의 어휘 내용이 포함되어야 함
  [[ "$output" == *"별 (standalone)"* ]]
}

# ─── SELF-TEST: 실제 wording-dictionary.md (변경 없음 = PASS) ────────────────

@test "SELF-TEST-F: 실제 repo docs/wording-dictionary.md — crash 없이 exit 0" {
  local dict_file="${WORKTREE_ROOT}/docs/wording-dictionary.md"
  [ -f "$dict_file" ] || skip "docs/wording-dictionary.md 없음"

  # 실제 repo 대상: base=HEAD (변경 없음 모드 → PASS)
  run python3 "$LINT_SCRIPT" --repo "$WORKTREE_ROOT" --base HEAD "$dict_file"
  [ "$status" -eq 0 ]
}

# ═══════════════════════════════════════════════════════════════════════════════
# CFP-1255 — cross-file evidence 검증 (forbid-list 제거 + ADR-064 lockstep)
# ═══════════════════════════════════════════════════════════════════════════════
#
# 테스트 대상: check_wording_dict_file 의 cross-file ADR-064 evidence 검증 로직
#
# 4 시나리오:
#   TC-G1: forbid-list row 제거 + ADR-064 신규 amendment (evidence-bearing) → PASS (WARN 없음)
#   TC-G2: forbid-list row 제거 + ADR-064 미변경 → WARN
#   TC-G3: forbid-list row 제거 + ADR-064 변경됐으나 신규 amendment sunset_justification bare "N/A" → WARN
#   TC-G4: forbid-list row 제거 + ADR-064 변경됐으나 신규 amendment sunset_justification 완전 누락 → WARN
#
# cross-file 픽스처: git 레포에 wording-dictionary.md + docs/adr/ADR-064-*.md 양 파일 세팅

# ─── ADR-064 fixture helper ───────────────────────────────────────────────────

# OLD ADR-064: amendment_log 1 entry (신규 추가 기준선용)
adr064_old_base() {
  cat << 'YAML'
---
adr_number: 64
title: 테스트 ADR-064
status: Accepted
category: governance
is_transitional: false
amendment_log:
  - amendment: 1
    carrier_story: CFP-100
    date: 2026-01-01
    summary: "기존 amendment"
    sunset_justification: null
---

## 결정 내용

본문.
YAML
}

# NEW ADR-064: amendment_log 에 신규 entry 추가 (evidence-bearing sunset_justification)
adr064_new_with_evidence_amendment() {
  cat << 'YAML'
---
adr_number: 64
title: 테스트 ADR-064
status: Accepted
category: governance
is_transitional: false
amendment_log:
  - amendment: 1
    carrier_story: CFP-100
    date: 2026-01-01
    summary: "기존 amendment"
    sunset_justification: null
  - amendment: 2
    carrier_story: CFP-1255
    date: 2026-05-22
    summary: "forbid-list 축소 lockstep amendment"
    direction: weaken
    sunset_justification: "pattern_count 0건 (측정 기간 12개월). metric: 위반 incident 0건 검증. 환경 변화로 원래 위험 소멸."
---

## 결정 내용

본문.
YAML
}

# NEW ADR-064: amendment_log 에 신규 entry 추가 (bare "N/A" — evidence 미보유)
adr064_new_with_bare_na_amendment() {
  cat << 'YAML'
---
adr_number: 64
title: 테스트 ADR-064
status: Accepted
category: governance
is_transitional: false
amendment_log:
  - amendment: 1
    carrier_story: CFP-100
    date: 2026-01-01
    summary: "기존 amendment"
    sunset_justification: null
  - amendment: 2
    carrier_story: CFP-1255
    date: 2026-05-22
    summary: "forbid-list 축소 lockstep amendment"
    direction: weaken
    sunset_justification: "N/A"
---

## 결정 내용

본문.
YAML
}

# NEW ADR-064: amendment_log 에 신규 entry 추가 (sunset_justification 키 자체 누락)
adr064_new_with_missing_sj_amendment() {
  cat << 'YAML'
---
adr_number: 64
title: 테스트 ADR-064
status: Accepted
category: governance
is_transitional: false
amendment_log:
  - amendment: 1
    carrier_story: CFP-100
    date: 2026-01-01
    summary: "기존 amendment"
    sunset_justification: null
  - amendment: 2
    carrier_story: CFP-1255
    date: 2026-05-22
    summary: "forbid-list 축소 lockstep amendment — sunset_justification 키 없음"
    direction: weaken
---

## 결정 내용

본문.
YAML
}

# ─── cross-file fixture setup helper ─────────────────────────────────────────

# 양 파일(wording-dictionary.md + ADR-064)을 git diff 픽스처로 세팅
# 사용법: setup_crossfile_diff <repo_dir> <old_dict> <new_dict> <old_adr> <new_adr>
setup_crossfile_diff() {
  local repo="$1"
  local old_dict="$2"
  local new_dict="$3"
  local old_adr="$4"
  local new_adr="$5"

  local dict_file="docs/wording-dictionary.md"
  local adr_file="docs/adr/ADR-064-decision-principle-mandate.md"

  mkdir -p "${repo}/docs/adr"

  # OLD 상태 commit
  printf '%s' "$old_dict" > "${repo}/${dict_file}"
  printf '%s' "$old_adr" > "${repo}/${adr_file}"
  git -C "$repo" add "${dict_file}" "${adr_file}"
  git -C "$repo" commit -q -m "old state"

  # NEW 상태 commit
  printf '%s' "$new_dict" > "${repo}/${dict_file}"
  printf '%s' "$new_adr" > "${repo}/${adr_file}"
  git -C "$repo" add "${dict_file}" "${adr_file}"
  git -C "$repo" commit -q -m "new state"
}

# ─────────────────────────── TC 그룹 G: cross-file ADR-064 evidence 검증 ──────

@test "TC-G1: forbid-list row 제거 + ADR-064 evidence-bearing amendment → PASS (WARN 없음)" {
  setup_crossfile_diff "$GIT_REPO" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)" \
    "$(adr064_old_base)" "$(adr064_new_with_evidence_amendment)"

  local dict_path="${GIT_REPO}/docs/wording-dictionary.md"
  local adr_path="${GIT_REPO}/docs/adr/ADR-064-decision-principle-mandate.md"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "$dict_path" "$adr_path"

  # warning-tier — exit 0 항상
  [ "$status" -eq 0 ]
  # ADR-064 evidence-bearing amendment 존재 → WARN 없음 (cross-file PASS)
  [[ "$output" != *"[WARN]"* ]]
}

@test "TC-G1-negative: TC-G1 에서 exit 1 미발생" {
  setup_crossfile_diff "$GIT_REPO" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)" \
    "$(adr064_old_base)" "$(adr064_new_with_evidence_amendment)"

  local dict_path="${GIT_REPO}/docs/wording-dictionary.md"
  local adr_path="${GIT_REPO}/docs/adr/ADR-064-decision-principle-mandate.md"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "$dict_path" "$adr_path"

  [ "$status" -ne 1 ]
}

@test "TC-G2: forbid-list row 제거 + ADR-064 미변경 (단독 dict 파일만 전달) → WARN 발생" {
  # ADR-064 는 변경하지 않고 wording-dictionary.md 만 변경하는 시나리오
  # setup_git_diff 로 dict 만 변경 (ADR-064 미전달 = 미변경으로 인식)
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  setup_git_diff "$GIT_REPO" "$dict_file" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)"

  # ADR-064 파일은 존재하지 않음 (레포에 없음) → 미변경으로 처리
  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  [ "$status" -eq 0 ]
  # ADR-064 미변경 → WARN 발생 (cross-file evidence 부재)
  [[ "$output" == *"[WARN]"* ]]
}

@test "TC-G2-negative: TC-G2 에서 exit 0 보장 (warning-tier)" {
  local dict_file="docs/wording-dictionary.md"
  mkdir -p "${GIT_REPO}/docs"
  setup_git_diff "$GIT_REPO" "$dict_file" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "${GIT_REPO}/${dict_file}"

  [ "$status" -eq 0 ]
}

@test "TC-G3: forbid-list row 제거 + ADR-064 변경됐으나 신규 amendment bare N/A → WARN 발생" {
  setup_crossfile_diff "$GIT_REPO" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)" \
    "$(adr064_old_base)" "$(adr064_new_with_bare_na_amendment)"

  local dict_path="${GIT_REPO}/docs/wording-dictionary.md"
  local adr_path="${GIT_REPO}/docs/adr/ADR-064-decision-principle-mandate.md"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "$dict_path" "$adr_path"

  [ "$status" -eq 0 ]
  # 신규 amendment 존재하나 bare "N/A" → evidence-bearing 아님 → WARN
  [[ "$output" == *"[WARN]"* ]]
}

@test "TC-G3-negative: TC-G3 에서 exit 0 보장" {
  setup_crossfile_diff "$GIT_REPO" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)" \
    "$(adr064_old_base)" "$(adr064_new_with_bare_na_amendment)"

  local dict_path="${GIT_REPO}/docs/wording-dictionary.md"
  local adr_path="${GIT_REPO}/docs/adr/ADR-064-decision-principle-mandate.md"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "$dict_path" "$adr_path"

  [ "$status" -eq 0 ]
}

@test "TC-G4: forbid-list row 제거 + ADR-064 변경됐으나 신규 amendment sunset_justification 키 누락 → WARN 발생" {
  setup_crossfile_diff "$GIT_REPO" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)" \
    "$(adr064_old_base)" "$(adr064_new_with_missing_sj_amendment)"

  local dict_path="${GIT_REPO}/docs/wording-dictionary.md"
  local adr_path="${GIT_REPO}/docs/adr/ADR-064-decision-principle-mandate.md"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "$dict_path" "$adr_path"

  [ "$status" -eq 0 ]
  # sunset_justification 키 누락 → evidence-bearing 아님 → WARN
  [[ "$output" == *"[WARN]"* ]]
}

@test "TC-G4-negative: TC-G4 에서 exit 0 보장" {
  setup_crossfile_diff "$GIT_REPO" \
    "$(wording_dict_old_two_rows)" "$(wording_dict_new_one_row_removed)" \
    "$(adr064_old_base)" "$(adr064_new_with_missing_sj_amendment)"

  local dict_path="${GIT_REPO}/docs/wording-dictionary.md"
  local adr_path="${GIT_REPO}/docs/adr/ADR-064-decision-principle-mandate.md"

  run python3 "$LINT_SCRIPT" \
    --repo "$GIT_REPO" \
    --base HEAD~1 \
    "$dict_path" "$adr_path"

  [ "$status" -eq 0 ]
}
