#!/usr/bin/env bash
# test_lane-evidence-check-yml.sh
# CFP-490 Phase 2 — lane-evidence-check workflow duplicate heading collision tests (§8.2)
#
# Tests 6 test_function (Story §8.2 verbatim mapping):
#   1. test_5a_strict_mode_preserved        — heading 1회 (normal) — 5a 미발화 (AC-1)
#   2. test_5a_case_A_one_valid             — heading 2회, 1 valid (AC-2 Case A)
#   3. test_5a_case_B_zero_valid            — heading 2회, 0 valid (AC-2 Case B)
#   4. test_5a_case_C_two_or_more_valid     — heading 2회, 2 valid (AC-2 Case C)
#   5. test_fast_pass_invariants_preserved  — type:epic / doc-only / non-Phase 2 (AC-5)
#   6. test_BYPASS_honor_preserved          — BYPASS: <reason> line (AC-5)
#
# Strategy: .mjs extraction (Story §3.1 결정 2) — analyzeDuplicateHeadings() 함수를 node 로 직접 호출
#   해서 case A/B/C path coverage 측정. workflow yaml 의 require/import + GitHub Checks API 발화는
#   yaml grep + structural assertion 으로 검증 (workflow runtime simulation 곤란 — 기존
#   test_rate-limit-fallback-kpi-yml.sh 패턴과 동일).
#
# Reference: tests/workflows/test_rate-limit-fallback-kpi-yml.sh (CFP-393 Phase 2 precedent).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)

WORKFLOW_FILE="$REPO_ROOT/templates/github-workflows/lane-evidence-check.yml"
WORKFLOW_SELF_APP="$REPO_ROOT/.github/workflows/lane-evidence-check.yml"
MJS_FILE="$REPO_ROOT/.github/scripts/check-lane-evidence-block.mjs"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_equals() {
  local desc="$1"
  local expected="$2"
  local actual="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ "$expected" == "$actual" ]]; then
    echo -e "${GREEN}OK${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  fi
  echo -e "${RED}FAIL${NC} $desc"
  echo "    Expected: $expected"
  echo "    Actual:   $actual"
  TESTS_FAILED=$((TESTS_FAILED + 1))
  return 1
}

assert_contains() {
  local desc="$1"
  local content="$2"
  local pattern="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if echo "$content" | grep -qF "$pattern"; then
    echo -e "${GREEN}OK${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  fi
  echo -e "${RED}FAIL${NC} $desc"
  echo "    Pattern not found: $pattern"
  echo "    Actual content (head): $(echo "$content" | head -c 200)..."
  TESTS_FAILED=$((TESTS_FAILED + 1))
  return 1
}

assert_not_contains() {
  local desc="$1"
  local content="$2"
  local pattern="$3"
  TESTS_RUN=$((TESTS_RUN + 1))
  if ! echo "$content" | grep -qF "$pattern"; then
    echo -e "${GREEN}OK${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  fi
  echo -e "${RED}FAIL${NC} $desc"
  echo "    Unexpected pattern present: $pattern"
  TESTS_FAILED=$((TESTS_FAILED + 1))
  return 1
}

# Run analyzeDuplicateHeadings(body) and return JSON output to stdout.
# Argument: $1 = body content (string).
#
# Strategy: base64-encode body → pipe via env var → node decodes inside.
#   Cross-platform safe (no temp file path translation issues on Git Bash MSYS2).
run_analyzer() {
  local body="$1"
  # MJS_FILE 은 이미 git rev-parse --show-toplevel 결과 (POSIX-style on Git Bash,
  # 또는 Windows-style on plain Windows). file:// URL 로 변환 — Node 가 양쪽 해석 가능.
  local body_b64
  body_b64=$(printf '%s' "$body" | base64 -w 0 2>/dev/null || printf '%s' "$body" | base64)
  LANE_EVIDENCE_BODY_B64="$body_b64" MJS_PATH="$MJS_FILE" node --input-type=module -e "
    const body = Buffer.from(process.env.LANE_EVIDENCE_BODY_B64, 'base64').toString('utf8');
    const pathLib = await import('node:path');
    const url = await import('node:url');
    const mjsUrl = url.pathToFileURL(pathLib.resolve(process.env.MJS_PATH)).href;
    const mod = await import(mjsUrl);
    const result = mod.analyzeDuplicateHeadings(body);
    console.log(JSON.stringify(result));
  "
}

VALID_BLOCK=$'## Lane evidence\n- 요구사항: PASS\n- 설계: PASS\n- 설계-리뷰: PASS\n- 구현: PASS\n- 구현-리뷰: PASS\n- 구현-테스트: SKIPPED\n- 보안-테스트: SKIPPED\n'

TABLE_BLOCK=$'## Lane evidence\n\n| lane | outcome | duration |\n|---|---|---|\n| 요구사항 | PASS | 5m |\n| 설계 | PASS | 8m |\n'

PLACEHOLDER_BLOCK=$'## Lane evidence\n\n_TODO: lane outcome 7-row append_\n'

# ============================================================================
# Test 1: 5a strict mode preserved — heading 1회 (normal)
# ============================================================================
test_5a_strict_mode_preserved() {
  echo
  echo -e "${YELLOW}Test 1: test_5a_strict_mode_preserved${NC}"
  # NB: bash $'...' literal 안에서만 \n 이 actual newline. 일반 "..." 안에서는 literal 두 글자.
  local body
  body=$'Some PR description prelude.\n\n'"$VALID_BLOCK"$'\nMore content after.'
  local result
  result=$(run_analyzer "$body")
  assert_equals "1.1 heading 1회 → analyzeDuplicateHeadings() returns null (no duplicate)" "null" "$result"
  assert_contains "1.2 workflow yaml line 131 의 5 capture regex 진입 가능 (heading 1회 시 5a 미발화)" \
    "$(cat "$WORKFLOW_FILE")" \
    'const blockMatch = body.match(/^## Lane evidence\s*$([\s\S]*?)'
  assert_contains "1.3 5a guard 가 analyzeDuplicateHeadings() return null 일 때 6 step 진행 (분기 보존)" \
    "$(cat "$WORKFLOW_FILE")" \
    "if (dupResult !== null) {"
}

# ============================================================================
# Test 2: Case A — heading 2회, 1 valid
# ============================================================================
test_5a_case_A_one_valid() {
  echo
  echo -e "${YELLOW}Test 2: test_5a_case_A_one_valid (1 valid heading)${NC}"
  # 첫 heading = table format (mismatch), 두 번째 heading = valid 7-row
  local body
  body=$'Prelude.\n\n'"$TABLE_BLOCK"$'\nMore text.\n\n'"$VALID_BLOCK"
  local result
  result=$(run_analyzer "$body")
  assert_contains "2.1 case == 'A'" "$result" '"case":"A"'
  assert_contains "2.2 valid_heading_idx == 2 (두 번째 heading 이 valid)" "$result" '"valid_heading_idx":2'
  assert_contains "2.3 total == 2 (heading 2회)" "$result" '"total":2'
  assert_contains "2.4 summary 안 '**Case A**' 명시" "$result" "**Case A**"
  assert_contains "2.5 summary 안 invalid heading 1 삭제 권고" "$result" "heading [1] 삭제 권고"
  assert_contains "2.6 summary 안 ADR-031 §결정 2 정책 인용" "$result" "ADR-031 §결정 2"
}

# ============================================================================
# Test 3: Case B — heading 2회, 0 valid
# ============================================================================
test_5a_case_B_zero_valid() {
  echo
  echo -e "${YELLOW}Test 3: test_5a_case_B_zero_valid (0 valid heading)${NC}"
  local body
  body=$'Prelude.\n\n'"$TABLE_BLOCK"$'\nMore text.\n\n'"$PLACEHOLDER_BLOCK"
  local result
  result=$(run_analyzer "$body")
  assert_contains "3.1 case == 'B'" "$result" '"case":"B"'
  assert_contains "3.2 valid_heading_idx == null" "$result" '"valid_heading_idx":null'
  assert_contains "3.3 summary 안 '**Case B**' 명시" "$result" "**Case B**"
  assert_contains "3.4 summary 안 valid 형식 가이드 (7 lane 명시)" "$result" "lane: 요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트"
  assert_contains "3.5 summary 안 verdict enum 가이드" "$result" "verdict: PASS / SKIPPED / FIX / ESCALATED / BYPASS"
}

# ============================================================================
# Test 4: Case C — heading 2회, 2 valid
# ============================================================================
test_5a_case_C_two_or_more_valid() {
  echo
  echo -e "${YELLOW}Test 4: test_5a_case_C_two_or_more_valid (2+ valid heading)${NC}"
  local body
  body=$'Prelude.\n\n'"$VALID_BLOCK"$'\nMore text.\n\n'"$VALID_BLOCK"
  local result
  result=$(run_analyzer "$body")
  assert_contains "4.1 case == 'C'" "$result" '"case":"C"'
  assert_contains "4.2 valid_idx_list == [1, 2] (둘 다 valid)" "$result" '"valid_idx_list":[1,2]'
  assert_contains "4.3 summary 안 '**Case C**' 명시" "$result" "**Case C**"
  assert_contains "4.4 summary 안 ADR-031 §결정 2 invariant 인용" "$result" "ADR-031 §결정 2 invariant"
  assert_contains "4.5 summary 안 '임의 1개 유지 + 나머지 삭제' 권고" "$result" "임의 1개 유지 + 나머지 삭제 권고"
}

# ============================================================================
# Test 5: fast-pass invariants preserved (CFP-106 정합)
# ============================================================================
test_fast_pass_invariants_preserved() {
  echo
  echo -e "${YELLOW}Test 5: test_fast_pass_invariants_preserved${NC}"
  local yaml_content
  yaml_content=$(cat "$WORKFLOW_FILE")
  assert_contains "5.1 type:epic fast-pass 분기 보존 (line 33-45 영역)" "$yaml_content" "if (labels.includes('type:epic')) {"
  assert_contains "5.2 doc-only fast-pass 분기 보존 (CFP-106)" "$yaml_content" "Fast-pass (doc-only PR — CFP-106 정합)"
  assert_contains "5.3 non-Phase 2 fast-pass 분기 보존 (phase detection)" "$yaml_content" "Phase 2 만 검사"
}

# ============================================================================
# Test 6: BYPASS honor preserved
# ============================================================================
test_BYPASS_honor_preserved() {
  echo
  echo -e "${YELLOW}Test 6: test_BYPASS_honor_preserved${NC}"
  local yaml_content
  yaml_content=$(cat "$WORKFLOW_FILE")
  assert_contains "6.1 BYPASS regex 보존 (line 97 영역)" "$yaml_content" "const bypassMatch = body.match(/BYPASS:"
  assert_contains "6.2 BYPASS honored summary 메시지 보존" "$yaml_content" "BYPASS honored"
  assert_contains "6.3 BYPASS audit trail ADR-026 인용 보존" "$yaml_content" "audit trail 의무 — ADR-026"
}

# ============================================================================
# Cross-cutting: byte-identical self-app + .mjs file existence
# ============================================================================
test_cross_cutting_invariants() {
  echo
  echo -e "${YELLOW}Cross-cutting: ADR-005 byte-identical + .mjs presence${NC}"
  TESTS_RUN=$((TESTS_RUN + 1))
  if diff -q "$WORKFLOW_FILE" "$WORKFLOW_SELF_APP" >/dev/null 2>&1; then
    echo -e "${GREEN}OK${NC} CX.1 templates ↔ .github byte-identical (ADR-005)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}FAIL${NC} CX.1 templates ↔ .github diff exists"
    diff "$WORKFLOW_FILE" "$WORKFLOW_SELF_APP" | head -20
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
  TESTS_RUN=$((TESTS_RUN + 1))
  if [[ -f "$MJS_FILE" ]]; then
    echo -e "${GREEN}OK${NC} CX.2 .github/scripts/check-lane-evidence-block.mjs 존재"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}FAIL${NC} CX.2 .mjs 파일 부재"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
  assert_contains "CX.3 workflow yaml 이 dynamic import (.mjs) 호출" \
    "$(cat "$WORKFLOW_FILE")" \
    "await import(mjsUrl)"
  assert_contains "CX.4 workflow yaml 이 analyzeDuplicateHeadings import" \
    "$(cat "$WORKFLOW_FILE")" \
    "const { analyzeDuplicateHeadings } = await import(mjsUrl);"
}

# ============================================================================
# Main
# ============================================================================
echo -e "${YELLOW}CFP-490 Phase 2 — lane-evidence-check.yml duplicate heading collision tests${NC}"
echo "Workflow: $WORKFLOW_FILE"
echo "Self-app: $WORKFLOW_SELF_APP"
echo ".mjs:     $MJS_FILE"
echo

test_5a_strict_mode_preserved
test_5a_case_A_one_valid
test_5a_case_B_zero_valid
test_5a_case_C_two_or_more_valid
test_fast_pass_invariants_preserved
test_BYPASS_honor_preserved
test_cross_cutting_invariants

echo
echo "============================================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN passed, $TESTS_FAILED failed"
echo "============================================================"

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi
exit 0
