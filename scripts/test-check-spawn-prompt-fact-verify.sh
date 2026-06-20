#!/usr/bin/env bash
# scripts/test-check-spawn-prompt-fact-verify.sh
# CFP-2383 Phase 2 — Discriminating test for check-spawn-prompt-fact-verify.sh
#
# ADR-082 Amendment 34 sub-scope 1-W anti-theater test: spawn-prompt fixture (unverified fact 1+ 포함)
# → 검출돼야 할 fact 이 검출 안 되면 RED (missing-case) + exit code assert
#
# 5 fact category (C1-C5) RED/GREEN 쌍 + message-assert (pattern + line 동시) +
# EXEMPT 4종(fenced/inline-code/blockquote/self-source) +
# PER_BLOCK_SCAN_CAP=50 cap + 1-L vs 1-W hint 변별 + multi-pattern 등 mutation testing:
#
#  - Mutation-1: C1 counter regex 제거 → TC-C1-RED, TC-C1-msg RED
#  - Mutation-2: C2 version regex 제거 → TC-C2-RED RED
#  - Mutation-3: C3 SHA regex 제거 → TC-C3-RED RED
#  - Mutation-4: C4 verify-result regex 제거 → TC-C4-RED RED
#  - Mutation-5: C5 file-existence regex 제거 → TC-C5-RED RED
#  - Mutation-6: in_fence toggle 제거 → TC-fenced RED
#  - Mutation-7: strip_inline_code 제거 → TC-inline-code RED
#  - Mutation-8: blockquote continue 제거 → TC-blockquote RED
#  - Mutation-9: self-source skip 제거 → TC-self-source RED
#  - Mutation-10: PER_BLOCK_SCAN_CAP cap 제거 → TC-cap RED
#  - Mutation-11: ANNOTATION_MARKER 검사 제거 → 전 GREEN(annotation) 케이스가 FLAG 로 RED
#  - Mutation-12: 1-L hint 를 1-W 잔재로 되돌림 → TC-1W-hint-red TC RED (§B P1 anti-theater)
#  - Mutation-13: multi-fact 혼합 → TC-multi RED
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
# Helper functions (S2 동형)
# ─────────────────────────────────────────────────────────────────────────────

run_test() {
  local test_name="$1"
  local prompt_text="$2"
  local should_have_flag="$3"      # "yes" or "no"
  local expected_exit_code="$4"    # "0", "1", or "2"
  local description="$5"

  # 임시 prompt 파일 생성 (UTF-8, trailing newline 없음)
  local prompt_file
  prompt_file=$(mktemp)
  trap "rm -f '$prompt_file'" RETURN
  printf '%s' "$prompt_text" > "$prompt_file"

  local output
  local exit_code=0
  output=$( bash "$REPO_ROOT/scripts/check-spawn-prompt-fact-verify.sh" "$prompt_file" 2>&1 ) || exit_code=$?

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
  if echo "$output" | grep -q "::warning::check-spawn-prompt-fact-verify: FLAG"; then
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
  local prompt_text="$2"
  local should_have_flag="$3"
  local expected_exit_code="$4"
  local description="$5"
  local pattern_name="$6"          # expected pattern name (C1-C5)
  local line_num="$7"              # expected line number

  local prompt_file
  prompt_file=$(mktemp)
  trap "rm -f '$prompt_file'" RETURN
  printf '%s' "$prompt_text" > "$prompt_file"

  local output
  local exit_code=0
  output=$( bash "$REPO_ROOT/scripts/check-spawn-prompt-fact-verify.sh" "$prompt_file" 2>&1 ) || exit_code=$?

  # Exit code 검증
  if [ "$exit_code" -ne "$expected_exit_code" ]; then
    echo "✗ FAIL: $test_name (exit code)"
    echo "  Expected exit code $expected_exit_code, got $exit_code"
    FAIL=$((FAIL+1))
    return 1
  fi

  # FLAG 여부 검증
  local has_flag=0
  if echo "$output" | grep -q "::warning::check-spawn-prompt-fact-verify: FLAG"; then
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
# TC-C1-RED: C1 counter "144 entries" annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C1-RED: C1 counter RED — 144 entries annotation 부재" \
  "The spawn prompt mentions 144 entries in the registry." \
  "yes" \
  "1" \
  "mutation-1 차단: C1 counter pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C1-GREEN: C1 counter "144 entries [verified-via:...]" annotation 부착
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C1-GREEN: C1 counter GREEN — 144 entries with annotation" \
  "The spawn prompt mentions 144 entries [verified-via: grep -c] in the registry." \
  "no" \
  "0" \
  "annotation 부착 시 검출 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C2-RED: C2 version "v2.86" annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C2-RED: C2 version RED — v2.86 annotation 부재" \
  "This references v2.86 of the specification." \
  "yes" \
  "1" \
  "mutation-2 차단: C2 version pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C2-GREEN: C2 version "v2.86 [verified-via:...]" annotation 부착
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C2-GREEN: C2 version GREEN — v2.86 with annotation" \
  "This references v2.86 [verified-via: grep ^version] of the specification." \
  "no" \
  "0" \
  "version annotation 부착 시 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C3-RED: C3 SHA 40-char hex annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C3-RED: C3 SHA RED — 40-char hex annotation 부재" \
  "The commit a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 is referenced." \
  "yes" \
  "1" \
  "mutation-3 차단: C3 SHA pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C3-GREEN: C3 SHA with annotation
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C3-GREEN: C3 SHA GREEN — with annotation" \
  "The commit a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 [verified-via: git rev-parse] is referenced." \
  "no" \
  "0" \
  "SHA annotation 부착 시 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C3-PRE-SPAWN-RED: C3 PRE-SPAWN-ORIGIN-MAIN-SHA block annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C3-PRE-SPAWN-RED: C3 PRE-SPAWN block RED — annotation 부재" \
  "PRE-SPAWN-ORIGIN-MAIN-SHA: abc123def456" \
  "yes" \
  "1" \
  "mutation-3 차단: C3 PRE-SPAWN pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C4-RED: C4 verify-result "MERGED" annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C4-RED: C4 verify-result RED — MERGED annotation 부재" \
  "The current status is MERGED in main." \
  "yes" \
  "1" \
  "mutation-4 차단: C4 verify-result pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C4-GREEN: C4 verify-result with annotation
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C4-GREEN: C4 verify-result GREEN — with annotation" \
  "The current status is MERGED [verified-via: gh pr view] in main." \
  "no" \
  "0" \
  "verify-result annotation 부착 시 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C4-CLEAN: C4 verify-result "CLEAN"
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C4-CLEAN-RED: C4 CLEAN RED — annotation 부재" \
  "The PR state is CLEAN now." \
  "yes" \
  "1" \
  "mutation-4 차단: C4 CLEAN pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C5-RED: C5 file-existence "docs/test.md 존재" annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C5-RED: C5 file-existence RED — docs/test.md 존재 annotation 부재" \
  "The file docs/test.md 존재 in the repo." \
  "yes" \
  "1" \
  "mutation-5 차단: C5 file-existence pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C5-GREEN: C5 file-existence with annotation
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C5-GREEN: C5 file-existence GREEN — with annotation" \
  "The file docs/test.md 존재 [verified-via: ls] in the repo." \
  "no" \
  "0" \
  "file-existence annotation 부착 시 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C5-line-count-RED: C5 "line count: 391" annotation 부재
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-C5-line-count-RED: C5 line count RED — annotation 부재" \
  "The file has line count: 391 lines total." \
  "yes" \
  "1" \
  "mutation-5 차단: C5 line count pattern 검출"

# ─────────────────────────────────────────────────────────────────────────────
# TC-fenced: EXEMPT fenced — fenced 블록 내부 claim (annotation 부재) → no FLAG
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-fenced: EXEMPT fenced — claim inside code block" \
  '문서:
```
144 entries are listed in the registry.
PRE-SPAWN-ORIGIN-MAIN-SHA: abc123
```
추가 설명.' \
  "no" \
  "0" \
  "mutation-6 차단: fenced 블록 내부 claim mask"

# ─────────────────────────────────────────────────────────────────────────────
# TC-fenced-tilde: EXEMPT fenced with tilde marker
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-fenced-tilde: EXEMPT fenced with ~~~ — claim inside" \
  '설명:
~~~
v2.86 is the current version.
~~~
끝.' \
  "no" \
  "0" \
  "tilde fence marker 도 mask"

# ─────────────────────────────────────────────────────────────────────────────
# TC-fenced-blank-fragmentation: fenced 내부 빈줄 + claim (fragmentation 회피)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-fenced-blank: EXEMPT fenced with blank line inside" \
  '예시:
```
첫 줄 코드.

144 entries in nested paragraph
```
끝.' \
  "no" \
  "0" \
  "fenced 내 blank-split 무시 → 빈줄 이후 claim 도 mask"

# ─────────────────────────────────────────────────────────────────────────────
# TC-inline-code: EXEMPT inline code-span — `144 entries` backtick 쌍 masking
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-inline-code: EXEMPT inline code-span — backtick pair strip" \
  "In the example, use \`144 entries\` for reference." \
  "no" \
  "0" \
  "mutation-7 차단: inline code-span backtick masking"

# ─────────────────────────────────────────────────────────────────────────────
# TC-inline-code-double: EXEMPT double backtick ``v2.86``
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-inline-code-double: EXEMPT double-backtick span" \
  "The version is \`\`v2.86\`\` in the spec." \
  "no" \
  "0" \
  "double-backtick pair strip 동작"

# ─────────────────────────────────────────────────────────────────────────────
# TC-inline-code-dangling: unbalanced backtick — claim 보존 → FLAG (검출됨)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-inline-code-dangling: unbalanced backtick dangling 144 entries (검출)" \
  "Use \`144 entries is unclosed" \
  "yes" \
  "1" \
  "mutation-7 차단: unbalanced backtick 안전 (dangling 이후 claim 보존)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-blockquote: EXEMPT blockquote — > 줄 내부 claim
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-blockquote: EXEMPT blockquote — > prefix claim" \
  "> 144 entries are referenced in the quoted text" \
  "no" \
  "0" \
  "mutation-8 차단: blockquote 줄 mask"

# ─────────────────────────────────────────────────────────────────────────────
# TC-self-source: EXEMPT self-source — "check_spawn_prompt_fact_verify" 근방 claim
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-self-source: EXEMPT self-source — lint meta-ref in window" \
  "See check_spawn_prompt_fact_verify for 144 entries registry." \
  "no" \
  "0" \
  "mutation-9 차단: self-source skip (meta-ref context)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-self-source-alternate: EXEMPT with alternate name
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-self-source-alt: EXEMPT self-source alternate name" \
  "The spawn-prompt-fact-verify pattern recognizes v2.86." \
  "no" \
  "0" \
  "alternate self-source name skip"

# ─────────────────────────────────────────────────────────────────────────────
# TC-cap: PER_BLOCK_SCAN_CAP=50 줄 초과 (51번째 줄 unverified claim 무시)
# ─────────────────────────────────────────────────────────────────────────────
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
  "144 entries on line 51 (beyond cap)")
run_test \
  "TC-cap: cap — 51번째 줄 unverified claim (초과)" \
  "$body_with_cap" \
  "no" \
  "0" \
  "mutation-10 차단: PER_BLOCK_SCAN_CAP=50 (51줄 이후 무시)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-clean: claim 0개 clean body
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-clean: clean — claim 0개 body" \
  "This prompt text contains no unverified facts about counters, versions, or commits." \
  "no" \
  "0" \
  "claim 없음 → PASS"

# ─────────────────────────────────────────────────────────────────────────────
# TC-empty: empty prompt body
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-empty: empty — prompt body 비어있음" \
  "" \
  "no" \
  "0" \
  "empty input → PASS"

# ─────────────────────────────────────────────────────────────────────────────
# TC-setup-error: setup error (존재하지 않는 파일)
# ─────────────────────────────────────────────────────────────────────────────
# 직접 호출로 exit 2 검증 (set -e 회피)
setup_exit=0
bash "$REPO_ROOT/scripts/check-spawn-prompt-fact-verify.sh" /nonexistent/file.txt >/dev/null 2>&1 || setup_exit=$?
if [ "$setup_exit" -eq 2 ]; then
  echo "✓ PASS: TC-setup-error (exit code 2 for missing file)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: TC-setup-error"
  echo "  Expected exit code 2, got $setup_exit"
  FAIL=$((FAIL+1))
fi

# ─────────────────────────────────────────────────────────────────────────────
# TC-C1-msg: message actionability — pattern=C1 + line 동시 assert
# ─────────────────────────────────────────────────────────────────────────────
run_test_with_message_assert \
  "TC-C1-msg: message actionability (pattern=C1 + line=1)" \
  "We found 99 entries in the scan." \
  "yes" \
  "1" \
  "message actionability assert: pattern 과 line 번호 포함" \
  "C1" \
  "1"

# ─────────────────────────────────────────────────────────────────────────────
# TC-C3-msg: message actionability — C3 SHA
# ─────────────────────────────────────────────────────────────────────────────
run_test_with_message_assert \
  "TC-C3-msg: message actionability (pattern=C3 SHA)" \
  "Spawn-commit a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 found." \
  "yes" \
  "1" \
  "SHA pattern message actionability" \
  "C3" \
  "1"

# ─────────────────────────────────────────────────────────────────────────────
# TC-multi: multi-fact 혼합 — C1+C2 혼합, annotation 일부만 부착
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-multi: multi-pattern — (C1)+(C2) 혼합, annotation 불완전" \
  "We have 144 entries and version v2.86 deployed." \
  "yes" \
  "1" \
  "다중 fact + 부분 annotation → FLAG 1개 이상"

# ─────────────────────────────────────────────────────────────────────────────
# TC-1W-hint-RED (§B P1 anti-theater): C3 SHA 의 hint 가 1-L 스코프여야 함
# → hint 에서 "sister PR" / "sibling" / "Orchestrator spawn" 등의 1-L sink 신호 검증
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-1W-hint: C3 SHA hint contains 1-L signal (not 1-W residue)" \
  "The spawn source a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 is referenced." \
  "yes" \
  "1" \
  "mutation-12 차단: 1-L hint verification (§B P1 anti-theater)"

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
  echo "Mutation-1 (C1 counter regex remove):"
  echo "  Remove '\\d{2,}\\s+(entries|...)' regex → TC-C1-RED, TC-C1-msg, TC-multi RED"
  echo ""
  echo "Mutation-2 (C2 version regex remove):"
  echo "  Remove 'v\\d+\\.\\d+' regex → TC-C2-RED RED"
  echo ""
  echo "Mutation-3 (C3 SHA regex remove):"
  echo "  Remove '[0-9a-f]{40}|PRE-SPAWN-ORIGIN-MAIN-SHA' regex → TC-C3-RED, TC-C3-PRE-SPAWN-RED, TC-C3-msg, TC-multi RED"
  echo ""
  echo "Mutation-4 (C4 verify-result regex remove):"
  echo "  Remove '(MERGED|CLEAN|...)' regex → TC-C4-RED, TC-C4-CLEAN-RED RED"
  echo ""
  echo "Mutation-5 (C5 file-existence regex remove):"
  echo "  Remove '.md\\s+존재|line count' regex → TC-C5-RED, TC-C5-line-count-RED RED"
  echo ""
  echo "Mutation-6 (in_fence toggle remove):"
  echo "  Remove fenced block masking → TC-fenced, TC-fenced-tilde, TC-fenced-blank RED"
  echo ""
  echo "Mutation-7 (strip_inline_code function remove):"
  echo "  Disable backtick masking → TC-inline-code, TC-inline-code-double RED"
  echo ""
  echo "Mutation-8 (blockquote continue remove):"
  echo "  Remove blockquote prefix masking → TC-blockquote RED"
  echo ""
  echo "Mutation-9 (self-source skip remove):"
  echo "  Remove SELF_SOURCE_PATTERNS check → TC-self-source, TC-self-source-alt RED"
  echo ""
  echo "Mutation-10 (PER_BLOCK_SCAN_CAP remove):"
  echo "  Remove scan cap limit → TC-cap RED"
  echo ""
  echo "Mutation-11 (ANNOTATION_MARKER check remove):"
  echo "  Disable verified-via annotation check → all GREEN(annotation) cases RED"
  echo ""
  echo "Mutation-12 (1-L hint to 1-W residue):"
  echo "  Replace 1-L hint with 1-W 'Orchestrator subagent spawn' → TC-1W-hint-RED RED (§B anti-theater)"
  echo ""
  echo "Mutation-13 (unbalanced backtick handling remove):"
  echo "  Disable dangling backtick safety → TC-inline-code-dangling RED"
  echo ""
  exit 0
else
  echo "✗ Some tests failed"
  exit 1
fi
