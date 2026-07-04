#!/usr/bin/env bash
# scripts/test-check-disjoint-axis-whitelist.sh
# CFP-2572 Phase 2 — Discriminating test for check_disjoint_axis_whitelist.py (lint)
#
# Anti-theater test (ADR-119 검증-후-단언 / ADR-136 execution-liveness):
#   GREEN (real ADR-039 + real return-envelope-v1.md) 는 PASS,
#   surgical mutant fixture (R1/R2/R3) 는 각각 표적 check 만 RED 로 fire.
#   각 RED 는 required_sentinel(표적 violation) 등장 + forbidden_sentinel(off-target) 부재 검증.
#
# Mutation targeting (single-purpose surgical each):
#   R1: §결정2 base 표에 가짜 7번째 entry(표 row) 주입 → base != 4 / effective 7 → (C1) RED.
#   R2: return-envelope-v1.md 에서 "disjoint axis" 절 제거 → (C2) RED.
#   R3: return-envelope-v1.md 가 inline-whitelist entry 로 self-claim → (C3) RED.
#
# Usage: bash scripts/test-check-disjoint-axis-whitelist.sh
# Exit: 0 = all discriminating tests pass / 1 = any fails (lint 회귀 의심).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

ADR_GREEN="$REPO_ROOT/archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md"
LDOC_GREEN="$REPO_ROOT/docs/inter-plugin-contracts/return-envelope-v1.md"

for f in "$ADR_GREEN" "$LDOC_GREEN"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: fixture base 부재: $f"
    exit 2
  fi
done

# ═════════════════════════════════════════════════════════════════════════════
# Test harness — adr fixture + ldoc fixture 로 lint 실행 후 exit/sentinel 검증
# ═════════════════════════════════════════════════════════════════════════════
run_discriminating_test() {
  local test_name="$1"
  local adr_fixture="$2"          # ADR-039 fixture path
  local ldoc_fixture="$3"         # return-envelope-v1.md fixture path
  local expected="$4"             # "PASS" or "RED"
  local description="$5"
  local required_sentinel="${6:-}"   # RED output 에 반드시 등장 (표적 violation)
  local forbidden_sentinel="${7:-}"  # RED output 에 절대 등장 금지 (off-target = 비특이)

  local lint_exit=0
  local lint_output=""
  lint_output=$(
    python3 scripts/lib/check_disjoint_axis_whitelist.py check \
      --adr-path "$adr_fixture" \
      --ldoc-path "$ldoc_fixture" \
      --repo-root "$REPO_ROOT" 2>&1
  ) || lint_exit=$?

  local lint_result="PASS"
  if [ "$lint_exit" -ne 0 ]; then
    lint_result="RED"
  fi

  if [ "$lint_result" != "$expected" ]; then
    echo "X FAIL: $test_name"
    echo "  Expected: $expected / Got: $lint_result (exit $lint_exit)"
    echo "  Desc: $description"
    echo "  Output: $lint_output"
    FAIL=$((FAIL+1))
    return 0
  fi

  if [ "$expected" = "RED" ]; then
    if [ -n "$required_sentinel" ] && ! echo "$lint_output" | grep -qE "$required_sentinel"; then
      echo "X FAIL: $test_name — RED 했으나 표적 violation 부재 (비특이 mutant)"
      echo "  required_sentinel: $required_sentinel"
      echo "  Output: $lint_output"
      FAIL=$((FAIL+1))
      return 0
    fi
    if [ -n "$forbidden_sentinel" ] && echo "$lint_output" | grep -qE "$forbidden_sentinel"; then
      echo "X FAIL: $test_name — off-target violation 검출 (mutant 비특이)"
      echo "  forbidden_sentinel: $forbidden_sentinel"
      echo "  Output: $lint_output"
      FAIL=$((FAIL+1))
      return 0
    fi
  fi

  echo "OK PASS: $test_name (lint result: $lint_result, exit $lint_exit)"
  PASS=$((PASS+1))
  return 0
}

# ═════════════════════════════════════════════════════════════════════════════
# fixture 생성 헬퍼 (surgical single-purpose mutant)
# ═════════════════════════════════════════════════════════════════════════════
TMP_TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_TEST_DIR"' EXIT

# R1: §결정2 base 표 `| 4 | Status report` row 뒤에 가짜 `| 7 |` entry row 주입 → base=5, effective=7
ADR_R1="$TMP_TEST_DIR/adr_r1.md"
sed '/^| 4 | Status report/a | 7 | fake-7th-entry | injected fake whitelist entry | R1 RED fixture |' \
  "$ADR_GREEN" > "$ADR_R1"

# R2: return-envelope-v1.md 에서 리터럴 "disjoint axis" 전량 제거 → (C2) RED
LDOC_R2="$TMP_TEST_DIR/ldoc_r2.md"
sed 's/disjoint axis//g' "$LDOC_GREEN" > "$LDOC_R2"

# R3: return-envelope-v1.md 에 inline-whitelist entry self-claim 문장 append → (C3) RED
LDOC_R3="$TMP_TEST_DIR/ldoc_r3.md"
cp "$LDOC_GREEN" "$LDOC_R3"
printf '\n\nreturn-envelope 는 inline whitelist 의 7번째 entry 이다.\n' >> "$LDOC_R3"

# ═════════════════════════════════════════════════════════════════════════════
# TC-1 GREEN — real ADR-039 + real return-envelope-v1.md
# ═════════════════════════════════════════════════════════════════════════════
run_discriminating_test \
  "TC-1-GREEN" \
  "$ADR_GREEN" \
  "$LDOC_GREEN" \
  "PASS" \
  "real ADR-039 (effective inline-whitelist 6) + real return-envelope-v1.md (disjoint-axis 선언, self-claim 부재)"

# TC-2 R1 — 가짜 7번째 entry 주입 → (C1) only
run_discriminating_test \
  "TC-2-R1-fake-7th-entry" \
  "$ADR_R1" \
  "$LDOC_GREEN" \
  "RED" \
  "R1: §결정2 base 표 가짜 7번째 entry 주입 (base=5, effective=7) — (C1) 표적" \
  '\(C1\)' \
  '\(C2\)|\(C3\)'

# TC-3 R2 — disjoint-axis 절 제거 → (C2) only
run_discriminating_test \
  "TC-3-R2-remove-disjoint-axis" \
  "$ADR_GREEN" \
  "$LDOC_R2" \
  "RED" \
  "R2: return-envelope-v1.md 'disjoint axis' 절 제거 — (C2) 표적" \
  '\(C2\)' \
  '\(C1\)|\(C3\)'

# TC-4 R3 — self-claim → (C3) only
run_discriminating_test \
  "TC-4-R3-self-claim" \
  "$ADR_GREEN" \
  "$LDOC_R3" \
  "RED" \
  "R3: return-envelope-v1.md inline-whitelist entry self-claim — (C3) 표적" \
  '\(C3\)' \
  '\(C1\)|\(C2\)'

# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: disjoint-axis-whitelist lint discriminating test"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "OK All discriminating tests passed — lint is detecting mutations correctly"
  exit 0
else
  echo "X Some tests failed — lint may not be detecting mutations correctly"
  exit 1
fi
