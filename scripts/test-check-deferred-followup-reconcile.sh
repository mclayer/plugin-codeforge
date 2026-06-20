#!/usr/bin/env bash
# scripts/test-check-deferred-followup-reconcile.sh
# CFP-2381 Phase 2 — Discriminating test for check-deferred-followup-reconcile.sh
#
# ADR-060 §결정 32 anti-theater test: registry fixture (over-threshold-uncarried entry 1+ 포함)
# → 검출돼야 할 entry 가 검출 안 되면 RED (missing-case) + exit code assert
#
# mutation testing: 검출 로직 1줄 깨뜨리면 RED (mutation 생존 0)
#  - Mutation-1: recurrence.count >= threshold 비교 제거 → TC-1/TC-2 RED
#  - Mutation-2: carrier_absent OR 결합 → false 상수화 → TC-4 RED
#  - Mutation-3: promotion_trigger == "auto_blocking" 검사 제거 → TC-1/TC-5/TC-5-output RED
#
# F-CR-2381 정정사항 (production code 확인됨):
#  - F-CR-2381-1: sh interpreter 등록 (_INTERPRETERS = {bash, sh, python, python3})
#  - F-CR-2381-2: spaceless pipe 정정 (regex `&&|;|\|` 무공백 포함)
#  - F-CR-2381-3: resolve 서브커맨드 argparse 정정
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

# 임시 테스트 repo 생성 (carrier 파일 실존/부재 제어용)
TMP_REPO=$(mktemp -d)
trap "rm -rf '$TMP_REPO'" EXIT

# 디렉터리 구조 초기화
mkdir -p "$TMP_REPO/scripts/lib"
mkdir -p "$TMP_REPO/docs"
mkdir -p "$TMP_REPO/templates/github-workflows"
mkdir -p "$TMP_REPO/.github/workflows"

# production script 복사
cp "$REPO_ROOT/scripts/check-deferred-followup-reconcile.sh" "$TMP_REPO/scripts/"
cp "$REPO_ROOT/scripts/lib/check_deferred_followup_reconcile.py" "$TMP_REPO/scripts/lib/"

run_test() {
  local test_name="$1"
  local registry_yaml="$2"
  local should_have_flag="$3"     # "yes" or "no"
  local expected_exit_code="$4"   # "0", "1", or "2"
  local description="$5"

  local registry_path="$TMP_REPO/docs/evidence-checks-registry.yaml"
  echo "$registry_yaml" > "$registry_path"

  local output
  local exit_code=0
  output=$( cd "$TMP_REPO" && bash scripts/check-deferred-followup-reconcile.sh check --repo-root . 2>&1 ) || exit_code=$?

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
  if echo "$output" | grep -q "::warning::check-deferred-followup-reconcile: FLAG"; then
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

run_test_with_output_assert() {
  local test_name="$1"
  local registry_yaml="$2"
  local should_have_flag="$3"
  local expected_exit_code="$4"
  local description="$5"
  local output_must_not_contain="$6"  # entry 이름 (grep -v 대상)

  local registry_path="$TMP_REPO/docs/evidence-checks-registry.yaml"
  echo "$registry_yaml" > "$registry_path"

  local output
  local exit_code=0
  output=$( cd "$TMP_REPO" && bash scripts/check-deferred-followup-reconcile.sh check --repo-root . 2>&1 ) || exit_code=$?

  # Exit code 검증
  if [ "$exit_code" -ne "$expected_exit_code" ]; then
    echo "✗ FAIL: $test_name"
    echo "  Expected exit code $expected_exit_code, got $exit_code"
    FAIL=$((FAIL+1))
    return 1
  fi

  # FLAG 여부 검증
  local has_flag=0
  if echo "$output" | grep -q "::warning::check-deferred-followup-reconcile: FLAG"; then
    has_flag=1
  fi

  if [ "$should_have_flag" = "yes" ] && [ "$has_flag" -eq 1 ]; then
    echo "✓ PASS: $test_name (FLAG detected, exit $exit_code)"
    PASS=$((PASS+1))
    return 0
  elif [ "$should_have_flag" = "no" ] && [ "$has_flag" -eq 0 ]; then
    # 강화: output_must_not_contain 검증 (scope filter mutation 감지)
    if [ -n "$output_must_not_contain" ]; then
      if echo "$output" | grep -q "$output_must_not_contain"; then
        echo "✗ FAIL: $test_name (output contains '$output_must_not_contain', should not)"
        echo "  Description: $description"
        FAIL=$((FAIL+1))
        return 1
      fi
    fi
    echo "✓ PASS: $test_name (no FLAG, output clean, exit $exit_code)"
    PASS=$((PASS+1))
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected FLAG: $should_have_flag, Got FLAG: $has_flag"
    FAIL=$((FAIL+1))
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-1: discriminating core case — over-threshold + auto_blocking + carrier ABSENT
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-1: discriminating — over-threshold + auto_blocking + carrier ABSENT" \
  'entries:
  - name: test-entry-1
    recurrence:
      count: 3
      threshold: 2
      promotion_trigger: auto_blocking
    detect_command: bash scripts/missing-detect.sh
    workflow: .github/workflows/missing-workflow.yml
    status: Active
' \
  "yes" \
  "1" \
  "핵심 케이스: count(3) >= threshold(2) AND auto_blocking AND 양 carrier ABSENT"

# ─────────────────────────────────────────────────────────────────────────────
# TC-2: boundary threshold match (count == threshold)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-2: boundary threshold match (count == threshold)" \
  'entries:
  - name: test-entry-2
    recurrence:
      count: 3
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/missing-boundary.sh
    workflow: .github/workflows/missing-boundary.yml
    status: Active
' \
  "yes" \
  "1" \
  "mutation-1 차단: count >= threshold 비교 제거 감지"

# ─────────────────────────────────────────────────────────────────────────────
# TC-3: clean case — 모든 carrier 실존 → FLAG 0 (자연 PASS)
# ─────────────────────────────────────────────────────────────────────────────
touch "$TMP_REPO/scripts/existing-detect.sh"
touch "$TMP_REPO/.github/workflows/existing-workflow.yml"

run_test \
  "TC-3: clean case — carrier 양 경로 EXISTS" \
  'entries:
  - name: test-entry-3
    recurrence:
      count: 5
      threshold: 2
      promotion_trigger: auto_blocking
    detect_command: bash scripts/existing-detect.sh
    workflow: .github/workflows/existing-workflow.yml
    status: Active
' \
  "no" \
  "0" \
  "carrier 실존 → 자연 PASS (검출 안 됨)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-4: boundary OR — script 부재 but workflow 실존 → FLAG 검출
# ─────────────────────────────────────────────────────────────────────────────
touch "$TMP_REPO/.github/workflows/or-test-workflow.yml"

run_test \
  "TC-4: boundary OR — script ABSENT, workflow EXISTS" \
  'entries:
  - name: test-entry-4-or-script
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/or-missing-script.sh
    workflow: .github/workflows/or-test-workflow.yml
    status: Active
' \
  "yes" \
  "1" \
  "mutation-2: OR 결합(detect_command ABSENT OR workflow ABSENT) 차단"

# ─────────────────────────────────────────────────────────────────────────────
# TC-5: scope exclusion — promotion_trigger=warning_tier_initial → 검출 제외
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-5: scope exclusion — promotion_trigger=warning_tier_initial" \
  'entries:
  - name: test-entry-5-warning
    recurrence:
      count: 5
      threshold: 2
      promotion_trigger: warning_tier_initial
    detect_command: bash scripts/warning-tier-missing.sh
    workflow: .github/workflows/warning-tier-missing.yml
    status: Active
' \
  "no" \
  "0" \
  "promotion_trigger ∉ {auto_blocking, advisory} → 검출 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-5-output 강화 (F-CR-2381-4): scope filter output 부재 assert
#   warning_tier_initial entry 가 출력에 나타나지 않음 (grep -v mutation 감지)
# ─────────────────────────────────────────────────────────────────────────────
run_test_with_output_assert \
  "TC-5-output: scope filter output 부재 — warning_tier_initial entry 미노출" \
  'entries:
  - name: warning-tier-victim
    recurrence:
      count: 5
      threshold: 2
      promotion_trigger: warning_tier_initial
    detect_command: bash scripts/warning-tier-missing.sh
    workflow: .github/workflows/warning-tier-missing.yml
    status: Active
' \
  "no" \
  "0" \
  "warning_tier_initial entry 는 출력에 나타나지 않음 (scope 제외)" \
  "warning-tier-victim"

# ─────────────────────────────────────────────────────────────────────────────
# TC-6: self-entry / carrier 실존 (자기 검출 방지)
# ─────────────────────────────────────────────────────────────────────────────
touch "$TMP_REPO/scripts/check-deferred-followup-reconcile.sh"
touch "$TMP_REPO/.github/workflows/deferred-followup-reconcile.yml"

run_test \
  "TC-6: self-entry — carrier 양 경로 EXISTS" \
  'entries:
  - name: deferred-followup-reconcile
    recurrence:
      count: 1
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/check-deferred-followup-reconcile.sh
    workflow: .github/workflows/deferred-followup-reconcile.yml
    status: Active
' \
  "no" \
  "0" \
  "self-entry: carrier 실존 → 자동으로 PASS (무한루프 회피)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-7: setup error — malformed yaml → exit 2
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-7: setup error — malformed yaml" \
  'invalid: yaml: [
  broken
' \
  "no" \
  "2" \
  "YAML parse 실패 → exit 2 (SETUP error)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-8: advisory INFO — promotion_trigger=advisory + over-threshold + carrier-absent
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-8: advisory INFO — promotion_trigger=advisory + carrier ABSENT" \
  'entries:
  - name: test-entry-8-advisory
    recurrence:
      count: 3
      threshold: 1
      promotion_trigger: advisory
    detect_command: bash scripts/advisory-missing.sh
    workflow: .github/workflows/advisory-missing.yml
    status: Active
' \
  "no" \
  "0" \
  "advisory → INFO (FLAG 아님, exit 0 — warning-first 정책)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-9: UNRESOLVED fail-loud — complex detect_command (bash -c inline)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-9: UNRESOLVED — detect_command 복합 (bash -c inline)" \
  'entries:
  - name: test-entry-9-complex
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: "bash -c \"echo hello\""
    workflow: .github/workflows/tc9-workflow.yml
    status: Active
' \
  "no" \
  "0" \
  "복합 detect_command → UNRESOLVED (fail-loud, 수동 판정 필요, FLAG 아님)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-9b: UNRESOLVED fail-loud — shell operator (&&) in detect_command
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-9b: UNRESOLVED — detect_command 다중 명령 (&&)" \
  'entries:
  - name: test-entry-9b-compound
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: "bash scripts/a.sh && bash scripts/b.sh"
    workflow: .github/workflows/tc9b-workflow.yml
    status: Active
' \
  "no" \
  "0" \
  "다중 명령 (&&) → UNRESOLVED, FLAG 0"

# ─────────────────────────────────────────────────────────────────────────────
# TC-10: prose/null skip — detect_command=null, workflow 실제 부재 판정 가능
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-10: skip detect_command axis (null), evaluate workflow" \
  'entries:
  - name: test-entry-10-prose
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: null
    workflow: .github/workflows/tc10-missing.yml
    status: Active
' \
  "yes" \
  "1" \
  "detect_command skip (null), workflow ABSENT → FLAG (skip 축 미포함, workflow 축만)"

# ─────────────────────────────────────────────────────────────────────────────
# TC-11: env-prefix path — detect_command = VAR=value bash scripts/X.sh
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-11: env-prefix path resolve" \
  'entries:
  - name: test-entry-11-env
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: "STORY_KEY=cfp-999 bash scripts/env-test.sh"
    workflow: .github/workflows/tc11-workflow.yml
    status: Active
' \
  "yes" \
  "1" \
  "env-prefix 무시, 경로 token 추출: scripts/env-test.sh ABSENT → FLAG"

# ─────────────────────────────────────────────────────────────────────────────
# TC-12: 2-root parity (templates/github-workflows/ + .github/workflows/)
# ─────────────────────────────────────────────────────────────────────────────
touch "$TMP_REPO/templates/github-workflows/parity-test.yml"
touch "$TMP_REPO/.github/workflows/parity-test.yml"

run_test \
  "TC-12: 2-root parity — both roots exist" \
  'entries:
  - name: test-entry-12-parity-ok
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/parity-detect.sh
    workflow: templates/github-workflows/parity-test.yml
    status: Active
' \
  "yes" \
  "1" \
  "detect_command ABSENT, templates 2-root 완비 → OR: detect_command ABSENT = FLAG"

# ─────────────────────────────────────────────────────────────────────────────
# TC-13: 2-root parity 미충족 — template 부재, self-app 존재 → carrier 부재 → FLAG
# ─────────────────────────────────────────────────────────────────────────────
mkdir -p "$TMP_REPO/.github/workflows"
touch "$TMP_REPO/.github/workflows/parity-incomplete.yml"

run_test \
  "TC-13: 2-root parity 미충족 — template ABSENT" \
  'entries:
  - name: test-entry-13-parity-incomplete
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/parity-check.sh
    workflow: templates/github-workflows/parity-incomplete.yml
    status: Active
' \
  "yes" \
  "1" \
  "template ABSENT (self-app 만 존재) → 2-root parity 미충족 → FLAG"

# ─────────────────────────────────────────────────────────────────────────────
# TC-14: threshold 미정의 → 검출 제외
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-14: threshold 미정의 — exclude from scan" \
  'entries:
  - name: test-entry-14-no-threshold
    recurrence:
      count: 5
      promotion_trigger: auto_blocking
    detect_command: bash scripts/no-threshold.sh
    workflow: .github/workflows/no-threshold.yml
    status: Active
' \
  "no" \
  "0" \
  "threshold 미정의 → count 비교 불가 → 검출 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-15: count < threshold — 미만 상태 (검출 제외)
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-15: count < threshold — under threshold" \
  'entries:
  - name: test-entry-15-under
    recurrence:
      count: 1
      threshold: 5
      promotion_trigger: auto_blocking
    detect_command: bash scripts/under-missing.sh
    workflow: .github/workflows/under-missing.yml
    status: Active
' \
  "no" \
  "0" \
  "count(1) < threshold(5) → 검출 제외"

# ─────────────────────────────────────────────────────────────────────────────
# TC-16: mixed multi-entry registry — FLAG + INFO + UNRESOLVED 혼합
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-16: mixed registry — FLAG + INFO + UNRESOLVED" \
  'entries:
  - name: flag-entry
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/flag-missing.sh
    workflow: .github/workflows/flag-missing.yml
  - name: info-entry
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: advisory
    detect_command: bash scripts/info-missing.sh
    workflow: .github/workflows/info-missing.yml
  - name: unresolved-entry
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: "bash -c \"echo test\""
    workflow: .github/workflows/unresolved.yml
' \
  "yes" \
  "1" \
  "FLAG 1개 포함 → exit 1 (FLAG > INFO > UNRESOLVED 우선순위)"

# ─────────────────────────────────────────────────────────────────────────────
# 신규 TC-17: sh interpreter 지원 (F-CR-2381-1)
#   detect_command = "sh scripts/missing-sh.sh" + auto_blocking + over-threshold + 파일 부재
#   → FLAG 검출 + exit 1
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-17: sh interpreter (F-CR-2381-1)" \
  'entries:
  - name: test-entry-17-sh
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: sh scripts/missing-sh.sh
    workflow: .github/workflows/tc17-workflow.yml
    status: Active
' \
  "yes" \
  "1" \
  "sh interpreter 명시 등록 (F-CR-2381-1): sh scripts/X.sh → resolve kind=path"

# ─────────────────────────────────────────────────────────────────────────────
# 신규 TC-18: spaceless pipe UNRESOLVED (F-CR-2381-2)
#   detect_command = "A.sh|B.sh" (무공백) + auto_blocking + over-threshold
#   → UNRESOLVED 분류 (FLAG 아님) + exit 0
# ─────────────────────────────────────────────────────────────────────────────
run_test \
  "TC-18: spaceless pipe UNRESOLVED (F-CR-2381-2)" \
  'entries:
  - name: test-entry-18-spaceless
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: "A.sh|B.sh"
    workflow: .github/workflows/tc18-workflow.yml
    status: Active
' \
  "no" \
  "0" \
  "무공백 pipe A.sh|B.sh → UNRESOLVED (fail-loud, FLAG 아님)"

# ─────────────────────────────────────────────────────────────────────────────
# 요약
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "Test Summary: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "All discriminating tests passed ✓"
  echo "Mutations detected: production lint detects"
  echo "  - count >= threshold 비교 제거 (mutation-1)"
  echo "  - carrier_absent OR 결합 제거 (mutation-2)"
  echo "  - promotion_trigger==auto_blocking 제거 (mutation-3)"
  echo ""
  echo "F-CR-2381 정정사항 검증:"
  echo "  ✓ TC-17: sh interpreter 등록 (F-CR-2381-1)"
  echo "  ✓ TC-18: spaceless pipe 정정 (F-CR-2381-2)"
  echo "  ✓ TC-5-output: scope filter output 강화 (F-CR-2381-4)"
  exit 0
else
  echo "Some tests failed ✗"
  exit 1
fi
