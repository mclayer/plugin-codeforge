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
