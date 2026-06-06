#!/usr/bin/env bats
# tests/scripts/test-check-fix-event-depth-scope-presence.bats
# CFP-842 Phase 2 -- check-fix-event-depth-scope-presence.py / .sh unit tests
# Change Plan §8 Test Contract: TC-1, TC-2, TC-3, TC-4, TC-5
#
# Test cases:
#   TC-1: broken-link FIX row with affected_paths_with_depth -> exit 0 PASS
#   TC-2: broken-link FIX row without affected_paths_with_depth -> exit 1 WARNING
#   TC-3: non-broken-link FIX row (no heuristic match) -> exit 0 PASS (의무 미적용)
#   TC-4: hotfix-bypass:fix-event-depth-scope label (workflow scope, bats = lint exit 검증)
#         -> 우회 label 부착 시 lint script 직접 호출은 여전히 exit 1 (workflow conditional skip 영역)
#         -> bats 는 bypass label 이 없어도 exit 1 반환 = TC-2 동일 케이스로 확인
#   TC-5: non-§10 commit (FIX Ledger 표 헤더 부재) -> exit 0 PASS (입력 무)
#
# Note on TC-4:
#   bypass label skip 은 workflow 레벨 conditional (steps.bypass.outputs.bypass == 'false').
#   lint 스크립트 자체는 label 을 인식하지 않음 (lint-only, live repo write 0).
#   TC-4 = bypass label 시 workflow 가 lint step 을 skip 하는 것 검증 영역.
#   bats level 에서는 "bypass label 없이 lint 호출 시 warning exit 1" 로 TC-2 동일 케이스.
#   TC-4 label description = workflow conditional 설계 의도 문서화 (bats TC 는 exit code 검증).

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-fix-event-depth-scope-presence.sh"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ------------------------------------------------------------------ helper: create story file with §10 table

create_story_with_fix_ledger() {
  local filepath="$1"
  local row_content="$2"

  cat > "$filepath" <<'STORY_EOF'
---
issue: 842
title: "[CFP-842] test story"
---

# CFP-842: test

## §10 FIX Ledger (FIX 카운터 SSOT)

STORY_EOF

  # 헤더 + 구분선 + row
  printf '| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? | debate_artifact_ref | reasoning_carryover | affected_scope | affected_paths_with_depth |\n' >> "$filepath"
  printf '|------|------|------|--------|-----------|-------------|--------|---------------------|---------------------|----------------|---------------------------|\n' >> "$filepath"
  printf '%s\n' "$row_content" >> "$filepath"

  cat >> "$filepath" <<'STORY_EOF'

## §11 참조

- GitHub Issue URL: https://github.com/mclayer/plugin-codeforge/issues/842
STORY_EOF
}

create_story_without_section_10() {
  local filepath="$1"
  cat > "$filepath" <<'STORY_EOF'
---
issue: 999
title: "[CFP-999] test story (no §10)"
---

# CFP-999: test

## §1 Issue body (verbatim, immutable)

본 Story 에는 §10 FIX Ledger 섹션이 없음 — non-§10 commit 시나리오.

## §11 참조

- GitHub Issue URL: https://github.com/mclayer/plugin-codeforge/issues/999
STORY_EOF
}

# ------------------------------------------------------------------ TC-1: broken-link FIX with depth -> PASS

@test "TC-1: broken-link FIX row with affected_paths_with_depth -> exit 0 PASS" {
  STORY_FILE="$TEST_DIR/CFP-TC1.md"

  # broken-link 트리거 + affected_paths_with_depth 채워진 row
  ROW='| 1 | 2026-05-17T11:00:00Z | 구현-리뷰 | CodeReviewPL P1 broken-link x 3 (CR-005 over-correction) | 구현 | DeveloperAgent 재스폰 (path adjust) | — | null | null | cross-module | [{path: "docs/adr/ADR-067.md", depth: 2}] |'

  create_story_with_fix_ledger "$STORY_FILE" "$ROW"

  run bash "$SCRIPT" "$STORY_FILE"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # broken-link FIX with depth -> PASS
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-2: broken-link FIX without depth -> WARNING

@test "TC-2: broken-link FIX row without affected_paths_with_depth -> exit 1 WARNING" {
  STORY_FILE="$TEST_DIR/CFP-TC2.md"

  # broken-link 트리거 + affected_paths_with_depth = null (누락)
  ROW='| 1 | 2026-05-17T12:00:00Z | 구현-리뷰 | CodeReviewPL P1 broken-link path 정정 (dangling ref) | 구현 | DeveloperAgent 재스폰 | — | null | null | cross-module | null |'

  create_story_with_fix_ledger "$STORY_FILE" "$ROW"

  run bash "$SCRIPT" "$STORY_FILE"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # broken-link FIX without depth -> WARNING exit 1
  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]]
}

# ------------------------------------------------------------------ TC-3: non-broken-link FIX -> PASS (의무 미적용)

@test "TC-3: non-broken-link FIX row (no heuristic match) -> exit 0 PASS" {
  STORY_FILE="$TEST_DIR/CFP-TC3.md"

  # 일반 FIX (broken-link 계열 어휘 없음) + affected_paths_with_depth = null
  ROW='| 1 | 2026-05-17T13:00:00Z | 구현-리뷰 | CodeReviewPL P1 test coverage 부족 | 구현 | DeveloperAgent 재스폰 (TC 추가) | — | null | null | single-file | null |'

  create_story_with_fix_ledger "$STORY_FILE" "$ROW"

  run bash "$SCRIPT" "$STORY_FILE"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # non-broken-link FIX -> PASS (depth 의무 미적용)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-4: bypass label (workflow conditional skip 설계 의도 문서화)
# bats scope: lint 스크립트 직접 호출 시 exit 1 (label 인식 없음) — workflow skip 영역과 분리

@test "TC-4: hotfix-bypass:fix-event-depth-scope label -- lint script level exit (workflow conditional skip 영역 분리 확인)" {
  STORY_FILE="$TEST_DIR/CFP-TC4.md"

  # broken-link 트리거 + depth 누락 row (bypass label 존재 여부와 관계없이 lint = WARNING)
  ROW='| 1 | 2026-05-17T14:00:00Z | 구현-리뷰 | CodeReviewPL P1 broken-link href 수정 (404 dangling) | 구현 | DeveloperAgent 재스폰 | — | null | null | cross-module | null |'

  create_story_with_fix_ledger "$STORY_FILE" "$ROW"

  # 스크립트 직접 호출 -- bypass label 은 workflow step conditional 영역
  # lint script 자체는 label 인식 없음 (read-only file lint only)
  run bash "$SCRIPT" "$STORY_FILE"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # lint script 직접 호출 = WARNING (label 인식 없음 — workflow skip 영역)
  # TC-4 설계 의도: workflow 레벨에서 bypass label 감지 시 이 step 자체가 실행되지 않음
  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]]
  # bypass lint hint 확인
  [[ "$output" == *"hotfix-bypass"* ]]
}

# ------------------------------------------------------------------ TC-5: non-§10 commit (FIX Ledger 부재) -> PASS

@test "TC-5: non-§10 commit (§10 FIX Ledger 섹션 부재) -> exit 0 PASS" {
  STORY_FILE="$TEST_DIR/CFP-TC5.md"

  create_story_without_section_10 "$STORY_FILE"

  run bash "$SCRIPT" "$STORY_FILE"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # §10 섹션 부재 -> PASS
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" == *"§10"* ]] || [[ "$output" == *"section"* ]] || [[ "$output" == *"섹션"* ]]
}
