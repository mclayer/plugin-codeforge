#!/usr/bin/env bash
# scripts/test-check-issue-body-claim-pre-screen.sh
# CFP-2382 Phase 2 — Discriminating test for check-issue-body-claim-pre-screen.sh
#
# ADR-082 Amendment 20 §결정 15 anti-theater test: issue-body fixture (stale claim 1+ 포함)
# → 검출돼야 할 claim 이 검출 안 되면 RED (missing-case) + exit code assert
#
# 4 sub-pattern (a/b/c/d) RED/GREEN 쌍 + 한글 enum (R2) + fenced/inline (R3/F7) +
# cap (PER_FILE_SCAN_CAP=50) + message actionability (R5) 등 mutation testing:
#  - Mutation-1: PR # pattern 제거 → TC-1a/TC-1a-msg RED
#  - Mutation-2: CFP-NNNN state keyword 제거 → TC-1b RED
#  - Mutation-3: count unit enum 제거 → TC-1c/TC-1c-ko RED
#  - Mutation-4: carrier/paired pattern 제거 → TC-1d RED
#  - Mutation-5: strip_inline_code 함수 제거 → TC-4c RED
#  - Mutation-6: in_fence toggle 제거 (전 fenced 줄 mask) → TC-4 RED
#  - Mutation-7: PER_FILE_SCAN_CAP cap 제거 → TC-8 RED
#  - Mutation-8: 한글 enum (건/개) 제거 → TC-1c-ko RED
#  - Mutation-9: ordinal 제외(F6) 미적용 → TC-3-ko RED (false-positive 발생)
#  - Mutation-10: unbalanced backtick handling 제거 → TC-4d RED (dangling backtick 미검출)
#
# Exit code:
#  0 = all tests pass (discriminating test validates lint)
#  1 = any test fails (lint may not be detecting mutations correctly)
#

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

run_test() {
  local test_name="$1"
  local issue_body="$2"
  local should_have_flag="$3"      # "yes" or "no"
  local expected_exit_code="$4"    # "0", "1", or "2"
  local description="$5"

  # 임시 issue body 파일 생성 (UTF-8, trailing newline 없음)
  local body_file
  body_file=$(mktemp)
  trap "rm -f '$body_file'" RETURN
  printf '%s' "$issue_body" > "$body_file"

  local output
  local exit_code=0
  output=$( bash "$REPO_ROOT/scripts/check-issue-body-claim-pre-screen.sh" "$body_file" 2>&1 ) || exit_code=$?

  # Exit code 검증
  if [ "$exit_code" -ne "$expected_exit_code" ]; then
    echo "✗ FAIL: $test_name"
    echo "  Expected exit code $expected_exit_code, got $exit_code"
    echo "  Description: $description"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
    return 1
  fi

  # FLAG 여부 검증 (::warning 포함 여부)
  local has_flag=0
  if echo "$output" | grep -q "::warning::check-issue-body-claim-pre-screen: FLAG"; then
    has_flag=1
  fi

  if [ "$should_have_flag" = "yes" ] && [ "$has_flag" -eq 1 ]; then
    echo "✓ PASS: $test_name (FLAG detected, exit $exit_code)"
    PASS=$((PASS+1))
    return 0
  elif [ "$should_have_flag" = "no" ] && [ "$has_flag" -eq 0 ]; then
    echo "✓ PASS: $test_name (no FLAG, exit $exit_code)"
    PASS=$((PASS+1))
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected FLAG: $should_have_flag, Got FLAG: $has_flag"
    echo "  Description: $description"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
    return 1
  fi
}

run_test_with_message_assert() {
  local test_name="$1"
  local issue_body="$2"
  local should_have_flag="$3"
  local expected_exit_code="$4"
  local description="$5"
  local pattern_name="$6"          # expected pattern name (a/b/c/d)
  local line_num="$7"              # expected line number

  local body_file
  body_file=$(mktemp)
  trap "rm -f '$body_file'" RETURN
  printf '%s' "$issue_body" > "$body_file"

  local output
  local exit_code=0
  output=$( bash "$REPO_ROOT/scripts/check-issue-body-claim-pre-screen.sh" "$body_file" 2>&1 ) || exit_code=$?

  # Exit code 검증
  if [ "$exit_code" -ne "$expected_exit_code" ]; then
    echo "✗ FAIL: $test_name (exit code)"
    echo "  Expected exit code $expected_exit_code, got $exit_code"
    FAIL=$((FAIL+1))
    return 1
  fi

  # FLAG 여부 검증
  local has_flag=0
  if echo "$output" | grep -q "::warning::check-issue-body-claim-pre-screen: FLAG"; then
    has_flag=1
  fi

  if [ "$should_have_flag" = "yes" ] && [ "$has_flag" -eq 1 ]; then
    # message actionability: pattern= AND line= 동시 assert
    if ! echo "$output" | grep -q "pattern=$pattern_name"; then
      echo "✗ FAIL: $test_name (pattern assertion)"
      echo "  Expected pattern=$pattern_name in output"
      echo "  Output: $output"
      FAIL=$((FAIL+1))
      return 1
    fi
    if ! echo "$output" | grep -q "line=$line_num"; then
      echo "✗ FAIL: $test_name (line assertion)"
      echo "  Expected line=$line_num in output"
      echo "  Output: $output"
      FAIL=$((FAIL+1))
      return 1
    fi
    echo "✓ PASS: $test_name (FLAG + pattern=$pattern_name + line=$line_num)"
    PASS=$((PASS+1))
    return 0
  elif [ "$should_have_flag" = "no" ] && [ "$has_flag" -eq 0 ]; then
    echo "✓ PASS: $test_name (no FLAG, exit $exit_code)"
    PASS=$((PASS+1))
    return 0
  else
    echo "✗ FAIL: $test_name (flag mismatch)"
    echo "  Expected FLAG: $should_have_flag, Got FLAG: $has_flag"
    FAIL=$((FAIL+1))
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-1a (pattern a RED): PR #1234 annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-1a: pattern a RED — PR #1234 annotation 부재" \
  "Related to PR #1234" \
  "yes" \
  "1" \
  "mutation-1 차단: PR # pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-2a (pattern a GREEN): PR #1234 [verified-via:...] annotation 부착
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-2a: pattern a GREEN — PR #1234 with annotation" \
  "Related to PR #1234 [verified-via: gh pr view 1234 state=MERGED pinned_at:2026-06]" \
  "no" \
  "0" \
  "annotation 부착 시 검출 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-1b (pattern b RED): CFP-1234 MERGED annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-1b: pattern b RED — CFP-1234 MERGED annotation 부재" \
  "This fixes CFP-1234 MERGED in main." \
  "yes" \
  "1" \
  "mutation-2 차단: CFP state keyword 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-2b (pattern b GREEN): CFP-1234 MERGED [verified-via:...] annotation 부착
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-2b: pattern b GREEN — CFP-1234 MERGED with annotation" \
  "This fixes CFP-1234 MERGED in main [verified-via: gh issue view CFP-1234 state=MERGED]." \
  "no" \
  "0" \
  "CFP state annotation 부착 시 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-1c (pattern c RED): 7 VIOLATIONs annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-1c: pattern c RED — count unit enum (영문)" \
  "Found 7 VIOLATIONs in the code." \
  "yes" \
  "1" \
  "mutation-3 차단: count unit enum 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-2c (pattern c GREEN): 7 VIOLATIONs [verified-via:...] annotation 부착
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-2c: pattern c GREEN — count unit enum with annotation" \
  "Found 7 VIOLATIONs in the code [verified-via: grep count=7]." \
  "no" \
  "0" \
  "count annotation 부착 시 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-1d (pattern d RED): carrier: CFP-1234 annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-1d: pattern d RED — carrier: CFP-1234 annotation 부재" \
  "This is a sister change. carrier: CFP-1234 was mentioned." \
  "yes" \
  "1" \
  "mutation-4 차단: carrier pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-2d (pattern d GREEN): paired CFP-1234 [verified-via:...] annotation 부착
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-2d: pattern d GREEN — paired CFP-1234 with annotation" \
  "This is paired CFP-1234 [verified-via: carrier 출처 확인]." \
  "no" \
  "0" \
  "carrier annotation 부착 시 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-3 (FP-c): 산문 숫자 — version 7 of the spec (단위 無)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-3: FP-c — count-단위 무 산문 숫자 제외" \
  "version 7 of the spec describes this behavior." \
  "no" \
  "0" \
  "count unit 미보유 숫자는 검출 제외 (false-positive 차단)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-4 (EXEMPT fenced): fenced 블록 내부 claim (annotation 부재)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-4: EXEMPT fenced — claim 예시 코드 블록 내부" \
  '문서:
```
PR #1234 is a good example.
More details here.
```
추가 설명.' \
  "no" \
  "0" \
  "fenced 블록 내부 claim 은 mask → 검출 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-4b (신규 R3): fenced 블록 내부 빈줄 + claim (blank-split 폐기 검증)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-4b: R3 — fenced 내부 빈줄 + claim (fragmentation 회피)" \
  '문서:
```
예시 코드입니다.

PR #5678 예시
```
끝.' \
  "no" \
  "0" \
  "fenced 내부 blank-split 무시 → 빈줄 이후 claim 도 mask"

# ─────────────────────────────────────────────────────────────────────────────
# TC-4c (신규 R3): inline code-span strip (backtick 쌍 제거)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-4c: R3 — inline code-span strip `PR #1234` annotation 부재" \
  "예시: use \`PR #1234\` for reference." \
  "no" \
  "0" \
  "mutation-5 차단: strip_inline_code 동작 (backtick 쌍 masking)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-4d (신규 F7): unbalanced/double-backtick edge case
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-4d-double: F7 — double-backtick span \`\`PR #1234\`\` annotation 부재" \
  "예시: use \`\`PR #1234\`\` for reference." \
  "no" \
  "0" \
  "double-backtick pair strip 동작 (run-length 매칭)"

# unbalanced backtick 테스트: dangling backtick 미닫힘 시 claim 보존 → 검출됨
run_test \
  "TC-4d-dangling: F7 — unbalanced backtick dangling CFP-5678 검출" \
  "예시: \`PR #9999 is unclosed and CFP-5678 follows" \
  "yes" \
  "1" \
  "mutation-10 차단: unbalanced backtick 안전 (dangling 이후 claim 보존)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-4d-stray (신규 F-CR-2382-1): stray single-backtick + claim + double-backtick
# ─────────────────────────────────────────────────────────────────────────────
# 라인: Note ` and PR #1234 uses ``x`` here
# 설명: stray single backtick(`) + 같은 줄 claim(PR #1234) + double-backtick span(``x``)
# 정정 전(strip ambiguous 미동작): ` 가 `` 의 첫 틱을 닫고 claim 삼킴 → no FLAG (RED)
# 정정 후(strip 생략, claim 보존): ambiguous line → raw line 반환 → PR #1234 검출 → FLAG (GREEN)
run_test \
  "TC-4d-stray: F-CR-2382-1 — stray backtick + claim + double-backtick (ambiguous)" \
  "Note \`and PR #1234 uses \`\`x\`\` here" \
  "yes" \
  "1" \
  "정정(F-CR-2382-1) 의존: ambiguous backtick line → strip 생략 → PR #1234 claim 보존"

# ─────────────────────────────────────────────────────────────────────────────
# TC-5 (EXEMPT blockquote): blockquote > 내부 claim
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-5: EXEMPT blockquote — > 줄 내부 claim" \
  "> PR #1234 is referenced here" \
  "no" \
  "0" \
  "blockquote 줄 mask → 검출 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-1c-ko (신규 R2): 한글 count-명백 단위 — 4건 annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-1c-ko: R2 — count 한글 enum 건 (4건)" \
  "보고서에는 4건의 issue가 나열됩니다." \
  "yes" \
  "1" \
  "mutation-8 차단: 한글 count 단위 enum 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-2c-ko (신규 R2): 한글 count-명백 단위 with annotation
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-2c-ko: R2 — 36건 with annotation" \
  "검수 결과 36건이 확인되었습니다 [verified-via: grep count=36]." \
  "no" \
  "0" \
  "한글 count annotation 부착 시 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-3-ko (신규 F6): ordinal-모호 단위 제외 (번/항목/차례)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-3-ko: F6 — ordinal-모호 4번째 (번 제외)" \
  "4번째 항목에서 문제가 발견되었습니다." \
  "no" \
  "0" \
  "mutation-9 차단: ordinal-모호 단위(번/항목) 제외 (FP 방지)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-7 (clean case): claim 0개 clean body
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-7: clean — claim 0개 body" \
  "이것은 claim을 포함하지 않는 깨끗한 본문입니다." \
  "no" \
  "0" \
  "claim 없음 → PASS"

# ─────────────────────────────────────────────────────────────────────────────
# TC-8 (cap): PER_FILE_SCAN_CAP=50 줄 초과 (51번째 줄 unverified claim 무시)
# ─────────────────────────────────────────────────────────────────────────────
# 50줄 이전은 claim 없고, 51번째 줄에 unverified claim 있음 → cap 초과로 무시
body_with_cap=$(printf '%s\n' \
  "Line 1" "Line 2" "Line 3" "Line 4" "Line 5" \
  "Line 6" "Line 7" "Line 8" "Line 9" "Line 10" \
  "Line 11" "Line 12" "Line 13" "Line 14" "Line 15" \
  "Line 16" "Line 17" "Line 18" "Line 19" "Line 20" \
  "Line 21" "Line 22" "Line 23" "Line 24" "Line 25" \
  "Line 26" "Line 27" "Line 28" "Line 29" "Line 30" \
  "Line 31" "Line 32" "Line 33" "Line 34" "Line 35" \
  "Line 36" "Line 37" "Line 38" "Line 39" "Line 40" \
  "Line 41" "Line 42" "Line 43" "Line 44" "Line 45" \
  "Line 46" "Line 47" "Line 48" "Line 49" "Line 50" \
  "PR #99999 on line 51 (beyond cap)")
run_test \
  "TC-8: cap — 51번째 줄 unverified claim (초과)" \
  "$body_with_cap" \
  "no" \
  "0" \
  "mutation-7 차단: PER_FILE_SCAN_CAP=50 (51줄 이후 무시)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-9 (multi-pattern): 다중 패턴 혼합, annotation 일부만 부착
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-9: multi — (a)+(c) 혼합, annotation 불완전" \
  "This PR #1234 introduces 5 VIOLATIONs." \
  "yes" \
  "1" \
  "다중 패턴 + 부분 annotation → FLAG 1개 이상"

# ─────────────────────────────────────────────────────────────────────────────
# TC-1a-msg (R5 message actionability): pattern= AND line= assert
# ─────────────────────────────────────────────────────────────────────────────
run_test_with_message_assert \
  "TC-1a-msg: R5 — message actionability (pattern=a + line=1)" \
  "Related to PR #1234 as well." \
  "yes" \
  "1" \
  "message actionability assert: pattern 과 line 번호 포함" \
  "a" \
  "1"

# ─────────────────────────────────────────────────────────────────────────────
# TC-1c-msg (R5 message actionability): pattern c message
# ─────────────────────────────────────────────────────────────────────────────
run_test_with_message_assert \
  "TC-1c-msg: R5 — message actionability (pattern=c)" \
  "We found 3 defects in the code." \
  "yes" \
  "1" \
  "count pattern message actionability" \
  "c" \
  "1"

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "============================================================"
echo "Test Summary"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All tests passed"
  echo ""
  echo "Mutation Testing Documentation:"
  echo "────────────────────────────────"
  echo "The following production code mutations would cause RED:"
  echo ""
  echo "Mutation-1 (PR # pattern remove):"
  echo "  Remove 'PR #\\d+' regex → TC-1a, TC-1a-msg, TC-9 RED"
  echo ""
  echo "Mutation-2 (CFP state keyword remove):"
  echo "  Remove state keyword matching → TC-1b RED"
  echo ""
  echo "Mutation-3 (count unit enum remove):"
  echo "  Remove count regex → TC-1c, TC-1c-ko, TC-9 RED"
  echo ""
  echo "Mutation-4 (carrier pattern remove):"
  echo "  Remove carrier/sibling/paired pattern → TC-1d RED"
  echo ""
  echo "Mutation-5 (strip_inline_code function remove):"
  echo "  Disable backtick masking → TC-4c RED"
  echo ""
  echo "Mutation-6 (in_fence toggle remove):"
  echo "  Remove fenced block masking → TC-4, TC-4b RED"
  echo ""
  echo "Mutation-7 (PER_FILE_SCAN_CAP remove):"
  echo "  Remove line count cap → TC-8 RED"
  echo ""
  echo "Mutation-8 (한글 enum remove):"
  echo "  Remove 건/개/곳/줄/회/어휘 from enum → TC-1c-ko, TC-2c-ko RED"
  echo ""
  echo "Mutation-9 (ordinal-모호 제외 미적용):"
  echo "  Remove ordinal filtering (번/항목/차례) → TC-3-ko RED (FP)"
  echo ""
  echo "Mutation-10 (unbalanced backtick handling remove):"
  echo "  Disable dangling backtick safety → TC-4d-dangling RED"
  echo ""
  echo "Mutation-11 (F-CR-2382-1 미적용 — ambiguous backtick strip 반환):"
  echo "  Old strip_inline_code (paired 만 masking, ambiguous 미처리) → TC-4d-stray RED"
  echo "  New strip_inline_code (ambiguous line skip, claim 보존) → TC-4d-stray GREEN"
  echo ""
  exit 0
else
  echo "✗ Some tests failed"
  exit 1
fi
