#!/usr/bin/env bats
# tests/scripts/test_check_wording_dictionary.bats
# CFP-610 / ADR-064 Amendment 2 — wording-dictionary lint unit tests
# Change Plan §8 Test Contract verbatim — 4 TC categories + integration tests

setup() {
  TEST_DIR="$(mktemp -d)"
  export WORDING_TEST_DIR="$TEST_DIR"
}

teardown() {
  rm -rf "$TEST_DIR"
}

# TC-1: 카테고리 (a) 어휘 발견 시 exit 1 + 어휘 출력
@test "TC-1: 카테고리 (a) forbid 어휘 '박제' 발견 → exit 1 + 어휘 출력" {
  echo "이 문장은 박제된 결정이다" > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"박제"* ]]
}

@test "TC-1b: 카테고리 (a) forbid 어휘 'pin' 발견 → exit 1 + 어휘 출력" {
  echo "이 설정을 pin 해두자" > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"pin"* ]]
}

@test "TC-1c: 카테고리 (a) forbid 어휘 '못 박기' 발견 → exit 1 + 어휘 출력" {
  echo "결정 못 박기를 진행한다" > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"못 박기"* ]]
}

@test "TC-1d: 카테고리 (a) forbid 어휘 'freezing' 발견 → exit 1 + 어휘 출력" {
  echo "이 값을 freezing 처리한다" > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"freezing"* ]]
}

# TC-2: 카테고리 (b) 어휘 평문 정의 없을 시 → exit 0 (advisory warning, console warn only)
# wording-dictionary.md spec: "정의 누락 시 lint advisory warning (exit 0 + console warn)"
@test "TC-2: 카테고리 (b) 어휘 'normative' 평문 정의 없을 시 → exit 0 + advisory 출력" {
  echo "이건 normative 한 규칙이다" > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"normative"* ]]
}

@test "TC-2b: 카테고리 (b) 어휘 'sibling sync' 평문 정의 없을 시 → exit 0 + advisory 출력" {
  echo "sibling sync 의무가 있다" > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
  [[ "$output" == *"sibling sync"* ]]
}

# TC-3: 카테고리 (b) 어휘 평문 정의 동반 시 → exit 0
@test "TC-3: 카테고리 (b) 어휘 'normative' 평문 정의 동반 → exit 0" {
  echo 'normative ("강제 규칙") 한 규칙이다' > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

@test "TC-3b: 카테고리 (b) 어휘 'sibling sync' 평문 정의 동반 → exit 0" {
  echo 'sibling sync ("관련 다른 plugin 동시 갱신 의무") 가 있다' > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

@test "TC-3c: 카테고리 (b) 어휘 'kind:contract' 평문 정의 동반 → exit 0" {
  echo 'kind:contract ("다른 plugin과의 데이터 교환 표준") 파일이다' > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

@test "TC-3d: 카테고리 (b) 어휘 'ratchet' 평문 정의 동반 → exit 0" {
  echo 'ratchet ("강화 방향만 허용") 규칙이다' > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

@test "TC-3e: 카테고리 (b) 어휘 'mirrored field' 평문 정의 동반 → exit 0" {
  echo 'mirrored field ("동기화 의무가 있는 공유 필드") 가 있다' > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

# TC-4: dictionary 외 일반 어휘 → exit 0
@test "TC-4: dictionary 외 일반 어휘 → exit 0" {
  echo "이건 일반 문장이다" > "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

@test "TC-4b: 빈 파일 → exit 0" {
  touch "$TEST_DIR/test-doc.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

# Integration: exempt path — blockquote 안 forbid 어휘 → exit 0 (false positive 차단)
@test "IT-1: blockquote 안 forbid 어휘 → exempt (exit 0)" {
  cat > "$TEST_DIR/test-doc.md" <<'EOF'
> 이 blockquote 안에 박제 라는 단어가 있다
> 하지만 blockquote 는 exempt 대상
EOF
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

# Integration: fenced code block 안 forbid 어휘 → exit 0 (false positive 차단)
@test "IT-2: fenced code block 안 forbid 어휘 → exempt (exit 0)" {
  cat > "$TEST_DIR/test-doc.md" <<'EOF'
```bash
# 이 코드 안에 pin 이라는 변수명이 있다
PIN_VALUE="test"
```
EOF
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-doc.md"
  [ "$status" -eq 0 ]
}

# Integration: self-app baseline 0 — wording-dictionary.md 자체는 0 warning
@test "IT-3: self-app baseline — wording-dictionary.md 자체 0 warning (exit 0)" {
  DICT_FILE="$(dirname "$BATS_TEST_FILENAME")/../../docs/wording-dictionary.md"
  if [ ! -f "$DICT_FILE" ]; then
    skip "docs/wording-dictionary.md 파일 없음 — Story 1 이미 merge 완료여야 함"
  fi
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$DICT_FILE"
  [ "$status" -eq 0 ]
}

# F-3 TC: word-boundary + case-insensitive + false-positive 차단 (FIX iter 1 / CFP-610 Story 2)
@test "F-3 TC-1e: false-positive — 'scoping' 안 substring 'pin' 차단 (word-boundary)" {
  echo "We are scoping this feature for next sprint" > "$TEST_DIR/test-wording-fp.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-wording-fp.md"
  [ "$status" -eq 0 ]
  [[ ! "$output" =~ "pin" ]]
}

@test "F-3 TC-1f: case-insensitive — 'Pin' / 'PIN' / 'FREEZING' 검출" {
  echo "Pin this decision. PIN ban-list. FREEZING the spec." > "$TEST_DIR/test-wording-case.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-wording-case.md"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "Pin" ]] || [[ "$output" =~ "PIN" ]] || [[ "$output" =~ "FREEZING" ]]
}

@test "F-3 TC-1g: word-boundary hit — 'pin to top' 의도된 검출" {
  echo "Let's pin to top the spec" > "$TEST_DIR/test-wording-wb.md"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-wording-dictionary.sh" "$TEST_DIR/test-wording-wb.md"
  [ "$status" -eq 1 ]
  [[ "$output" =~ "pin" ]]
}

# CI-only: hotfix-bypass label skip (CI 환경 only)
@test "CI-1: hotfix-bypass:wording-dictionary label skip — CI 환경 only" {
  skip "CI-1 = GitHub Actions 환경 only (label API 상호작용)"
}

# ════════════════════════════════════════════════════════════════════════════
# CFP-750 / ADR-064 Amendment 5 — scope 확장 + per-word scope decoupling +
#   `박제` 전수 sweep + inline code-span EXEMPT
# Change Plan §8.0 INV-T1~T5 + §8.1 IT-4/IT-4-neg/IT-4a~d/IT-5/IT-self-app/
#   IT-treaty-invariance instantiation. TDD RED phase (DeveloperAgent GREEN target).
#
# 스코프 모델 (Amendment 결정 2 / §3.2.1·§3.2.2): no-arg 모드 = per-word lookup
#   mode. 어휘별 scope 분리, WORD_TARGETS 의 상대경로를 cwd 기준 해석.
#   박제/못 박기/pin/freezing = expanded scope (docs/** + CLAUDE.md + CHANGELOG.md + templates/**)
#   별 standalone            = 5-scope 유지 (docs/adr docs/change-plans CLAUDE.md
#                              docs/orchestrator-playbook.md templates)
# args 모드 = uniform override (§3.2.1) — 모든 어휘 동일 path 적용 (기존 의미 보존).
# 본 fixture 는 합성 repo tree 를 mktemp 하위에 만들고 그 안으로 cd 후 no-arg
# 호출 (subshell `cd ... && bash <abs script>`) — design 의 no-arg + cwd-relative
# scope 해석 model 과 정확히 정합 (out-of-contract env 변수 미도입).
# ════════════════════════════════════════════════════════════════════════════

SCRIPT() {
  local root
  root="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  echo "$root/scripts/check-wording-dictionary.sh"
}

# 합성 repo tree 헬퍼: $TEST_DIR/repo 하위에 repo-root 모사 디렉터리 구성 후
# 지정 상대경로에 내용 기록.
_mk_in_scope() {
  local relpath="$1" content="$2"
  local full="$TEST_DIR/repo/$relpath"
  mkdir -p "$(dirname "$full")"
  printf '%s\n' "$content" > "$full"
}

# 합성 repo 안에서 no-arg 호출 (per-word lookup mode, cwd = $TEST_DIR/repo).
_run_noarg_in_repo() {
  run bash -c "cd '$TEST_DIR/repo' && bash '$(SCRIPT)'"
}

# ─── INV-T1 / IT-4: Per-word scope decoupling — positive case (4 case) ───────
@test "IT-4a-pos: '박제' in docs/inter-plugin-contracts/*.md (expanded scope) → exit 1 warning" {
  _mk_in_scope "docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md" "이 결정을 박제한다"
  _run_noarg_in_repo
  [ "$status" -eq 1 ]
  [[ "$output" == *"박제"* ]]
}

@test "IT-4b-pos: '박제' in docs/adr/ADR-XXX.md (existing 5-scope hit) → exit 1 warning" {
  _mk_in_scope "docs/adr/ADR-XXX-test.md" "이 결정을 박제한다"
  _run_noarg_in_repo
  [ "$status" -eq 1 ]
  [[ "$output" == *"박제"* ]]
}

@test "IT-4c-pos: '별' in docs/inter-plugin-contracts/*.md (expanded scope MISS — 별 5-scope 유지) → exit 0 silent" {
  # 별 standalone 은 expanded scope 진입 안 함 (per-word scope decoupling).
  # inter-plugin-contracts 는 별의 5-scope 밖 → 검출 미발화.
  _mk_in_scope "docs/inter-plugin-contracts/label-registry-v2.md" "이건 별 도리가 없다"
  _run_noarg_in_repo
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '별'"* ]]
}

@test "IT-4d-pos: '별' in docs/adr/ADR-YYY.md (existing 5-scope hit) → exit 1 warning" {
  _mk_in_scope "docs/adr/ADR-YYY-test.md" "이건 별 도리가 없다"
  _run_noarg_in_repo
  [ "$status" -eq 1 ]
  [[ "$output" == *"별"* ]]
}

# ─── INV-T3 + INV-T4 / IT-4-neg: scope decoupling — negative case (3 case) ───
@test "IT-4-neg-a: '박제' in tests/scripts/test.bats (.md-only filter miss) → exit 0 silent (INV-T4 (iv))" {
  _mk_in_scope "tests/scripts/test.bats" "이 결정을 박제한다"
  _run_noarg_in_repo
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

@test "IT-4-neg-b: '박제' in docs/wording-dictionary.md (EXEMPT_FILES) → exit 0 silent (INV-T3a + INV-T4 (ii))" {
  _mk_in_scope "docs/wording-dictionary.md" "박제 라는 어휘를 정의한다"
  _run_noarg_in_repo
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

@test "IT-4-neg-c: '박제' in docs/adr/ADR-064-decision-principle-mandate.md (EXEMPT_FILES) → exit 0 silent (INV-T3a + INV-T4 (iii))" {
  _mk_in_scope "docs/adr/ADR-064-decision-principle-mandate.md" "박제 어휘를 forbid-list 표에 명시한다"
  _run_noarg_in_repo
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

# ─── INV-T3d / IT-4a~d: inline code-span strip (5 case) ──────────────────────
@test "IT-4a: \`박제\` inline code-span in docs/inter-plugin-contracts/label-registry-v2.md → exit 0 silent (INV-T3d)" {
  echo 'forbid 어휘 목록에 `박제` 가 포함된다' > "$TEST_DIR/icode-1.md"
  run bash "$(SCRIPT)" "$TEST_DIR/icode-1.md"
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

@test "IT-4b: 일반 '박제' 인용 (backtick 없음) → exit 1 warning (non-EXEMPT)" {
  echo '이 결정을 박제한다' > "$TEST_DIR/icode-2.md"
  run bash "$(SCRIPT)" "$TEST_DIR/icode-2.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"박제"* ]]
}

@test "IT-4c: \`의무 박제\` multi-word inline code-span → exit 0 silent (INV-T3d)" {
  echo '핵심 용어 `의무 박제` 를 인용한다' > "$TEST_DIR/icode-3.md"
  run bash "$(SCRIPT)" "$TEST_DIR/icode-3.md"
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

@test "IT-4d-mixed: \`박제\` + 그 외 평문 '박제' (mixed) → exit 1 (non-EXEMPT 부분만 검출)" {
  echo '메타 인용 `박제` 이지만 본문에서 결정을 박제한다' > "$TEST_DIR/icode-4.md"
  run bash "$(SCRIPT)" "$TEST_DIR/icode-4.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"박제"* ]]
}

@test "IT-4d-double: \`\`박제\`\` double backtick → exit 1 (single backtick 만 처리 — 본 Story 채택)" {
  # Change Plan §8.1 #3: 본 Story 채택 = single backtick 만 (markdown 표준).
  # double backtick pair 는 strip 대상 아님 → 내부 박제 검출.
  echo '이중 백틱 ``박제`` 표기' > "$TEST_DIR/icode-5.md"
  run bash "$(SCRIPT)" "$TEST_DIR/icode-5.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"박제"* ]]
}

# 인접 backtick / multiline backtick edge (§4.2 R7 — 4+ edge case 의무)
@test "IT-4-edge-adjacent: 인접 inline code-span 2개 (\`a\`\`박제\`) → 내부 박제 EXEMPT (exit 0)" {
  echo '인접 코드 `pin해제` `박제` 표기' > "$TEST_DIR/icode-adj.md"
  run bash "$(SCRIPT)" "$TEST_DIR/icode-adj.md"
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

@test "IT-4-edge-unbalanced: 짝 없는 single backtick + 평문 박제 → exit 1 (non-pair, 검출 유지)" {
  echo '백틱 시작만 `있고 결정을 박제한다' > "$TEST_DIR/icode-unbal.md"
  run bash "$(SCRIPT)" "$TEST_DIR/icode-unbal.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"박제"* ]]
}

# ─── INV-T3b + INV-T3c / IT-5: blockquote + fenced + inline code-span 조합 ───
@test "IT-5a: blockquote 안 '박제' → exit 0 (blockquote EXEMPT, INV-T3b)" {
  cat > "$TEST_DIR/it5-bq.md" <<'EOF'
> "결정 트리 박제" 는 사용자 verbatim 인용이다
EOF
  run bash "$(SCRIPT)" "$TEST_DIR/it5-bq.md"
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

@test "IT-5b: fenced code block 안 '박제' → exit 0 (fenced EXEMPT, INV-T3c)" {
  cat > "$TEST_DIR/it5-fence.md" <<'EOF'
```text
박제
```
EOF
  run bash "$(SCRIPT)" "$TEST_DIR/it5-fence.md"
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

@test "IT-5c: blockquote + inline code-span 합성 (> 어휘 \`박제\`) → exit 0 (양 EXEMPT 합성)" {
  cat > "$TEST_DIR/it5-combo.md" <<'EOF'
> 어휘 `박제` 를 메타-언급한다
EOF
  run bash "$(SCRIPT)" "$TEST_DIR/it5-combo.md"
  [ "$status" -eq 0 ]
  [[ "$output" != *"카테고리 (a) forbid]: '박제'"* ]]
}

@test "IT-5d-edge: blockquote 밖 + inline code-span 박제 1줄, 다른 줄 평문 박제 → exit 1 (평문만 검출)" {
  cat > "$TEST_DIR/it5-multiline.md" <<'EOF'
메타 인용 `박제` 만 있는 줄
다른 줄에서 결정을 박제한다
EOF
  run bash "$(SCRIPT)" "$TEST_DIR/it5-multiline.md"
  [ "$status" -eq 1 ]
  [[ "$output" == *"박제"* ]]
}

# ─── INV-T4 / IT-self-app: self-referential exempt class verify (1 case) ─────
@test "IT-self-app: lint script + dictionary + bats fixture self-app → exit 0 (INV-T4 (i)+(ii)+(iv))" {
  local root
  root="$(dirname "$BATS_TEST_FILENAME")/../.."
  if [ ! -f "$root/docs/wording-dictionary.md" ]; then
    skip "docs/wording-dictionary.md 없음 — Phase 1 merge 선행 필요"
  fi
  run bash "$(SCRIPT)" \
    "$root/scripts/check-wording-dictionary.sh" \
    "$root/docs/wording-dictionary.md" \
    "$root/tests/scripts/test_check_wording_dictionary.bats"
  [ "$status" -eq 0 ]
}

# ─── INV-T2 / IT-treaty-invariance: contract schema 의미 불변 verify ─────────
# Phase 2 PR sweep diff 측정 — docs/inter-plugin-contracts/ 의 yaml frontmatter /
# 표 row / 코드 블록 hunk = 0 (prose hunk only) + registry version bump 0.
@test "IT-treaty-invariance: contract sweep diff = prose hunk only (INV-T2)" {
  local root
  root="$(dirname "$BATS_TEST_FILENAME")/../.."
  if [ ! -d "$root/.git" ] && [ ! -f "$root/.git" ]; then
    skip "git repo 아님 — treaty invariance diff 측정 불가"
  fi
  if [ ! -d "$root/docs/inter-plugin-contracts" ]; then
    skip "docs/inter-plugin-contracts/ 없음"
  fi
  # Phase 2 sweep diff: contract 영역 변경의 yaml frontmatter (^schema_version /
  # ^version: 등) + markdown 표 row (^\|) + fenced code block hunk 변경 = 0.
  # GREEN 구현은 advisory helper (tests/contracts/test_cfp750_treaty_invariance.sh)
  # 를 제공하고, 본 케이스는 해당 helper exit 0 을 계약한다.
  local helper="$root/tests/contracts/test_cfp750_treaty_invariance.sh"
  if [ ! -f "$helper" ]; then
    # RED: helper 미존재 → 실패하여 GREEN 구현 유도
    echo "treaty invariance advisory helper 미존재: $helper" >&2
    return 1
  fi
  run bash "$helper"
  [ "$status" -eq 0 ]
}

# ─── INV-T5: 기존 bats 박제 fixture 4건 보존 (sweep 금지) ────────────────────
# Phase 2 PR diff 안 본 bats 파일 영역의 기존 fixture 보존 self-check.
# TC-1/TC-1b/TC-1c/TC-1d + IT-1/IT-2 + F-3 TC-1e/TC-1f/TC-1g 의 어휘 인용 보존.
@test "IT-5-preserve: 기존 박제/pin/못 박기/freezing fixture 4건 + IT-1/IT-2 + F-3 보존" {
  local self="$BATS_TEST_FILENAME"
  # 기존 fixture 의 핵심 어휘 인용 라인이 보존돼야 함 (sweep 금지 — .md-only
  # filter 로 본 .bats 파일 자동 exempt 이므로 어휘 인용 보존이 정합).
  grep -q '박제된 결정이다' "$self"
  grep -q 'pin 해두자' "$self"
  grep -q '못 박기를 진행한다' "$self"
  grep -q 'freezing 처리한다' "$self"
  grep -q 'IT-1: blockquote' "$self"
  grep -q 'IT-2: fenced code block' "$self"
  grep -q 'F-3 TC-1e' "$self"
  grep -q 'F-3 TC-1f' "$self"
  grep -q 'F-3 TC-1g' "$self"
}
