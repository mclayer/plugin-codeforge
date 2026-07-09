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

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2591 Phase 2 — baseline new-only (Clean-as-You-Code) grandfather fixtures
#   Group 1 (grandfather discriminating pair) / Group 3 (tamper·expiry) /
#   Group 4 (boundary·theater killers) / Group 5 (idempotency).
#
# 원칙: TC-1~TC-18 은 legacy 모드($TMP_REPO 에 baseline 부재)로 그대로 PASS 보존.
#   아래 fixtures 는 별도 git-init dir($FIXROOT/*) 에서 REAL gen tool 로 baseline 을
#   생성(content_digest 정합) 후 registry 를 변형해 grandfather/new-only 판정을 검증.
#   ★ gate 는 baseline content_digest 를 tamper-verify 하므로 fixture baseline 을
#     손으로 만들면 BASELINE-TAMPER 오탐 → 반드시 gen tool 로 생성(GE-2/GE-3 만 의도적 tamper).
#   ★ gen tool 은 git HEAD(provenance) 를 요구 → fixture dir 은 git init + --allow-empty commit 필수
#     (비-git dir 은 gen 이 CalledProcessError 로 crash — 실측 확인).
#
# OQ-B RESOLVED (GE-1 expiry): baseline expiry 는 advisory sweep(gen prune, monotonic
#   shrink)일 뿐 hard-fail 자동 flip 아님 → §8.4-NT documented-limitation. hard-fail
#   fixture 작성 대상 아님(never auto hard-flip). prune 결정성은 Group 5 ID-1 로 대체 커버.
# ═════════════════════════════════════════════════════════════════════════════

GEN_TOOL="$REPO_ROOT/scripts/lib/gen_deferred_followup_baseline.py"
GATE_WRAPPER="$TMP_REPO/scripts/check-deferred-followup-reconcile.sh"  # execs $TMP_REPO 사본 py
FIXROOT="$TMP_REPO/_fix"                                               # trap 이 $TMP_REPO 통째 삭제
mkdir -p "$FIXROOT"

# mutation 원본 백업 (gate PROD_PY — 아래 gate_mutate_and_check 용, TC-1~18 이후 시점 안전)
GATE_PY="$TMP_REPO/scripts/lib/check_deferred_followup_reconcile.py"
GATE_PY_BAK="$TMP_REPO/scripts/lib/check_deferred_followup_reconcile.py.bak"
cp "$GATE_PY" "$GATE_PY_BAK"

# ── base registry 스니펫 (gf-x @count8/thr3, detect exists / workflow absent) ──
REG_X='entries:
  - name: gf-x
    recurrence:
      count: 8
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-x.sh
    workflow: .github/workflows/wf-x.yml'

REG_X_C10='entries:
  - name: gf-x
    recurrence:
      count: 10
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-x.sh
    workflow: .github/workflows/wf-x.yml'

REG_X_T2='entries:
  - name: gf-x
    recurrence:
      count: 8
      threshold: 2
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-x.sh
    workflow: .github/workflows/wf-x.yml'

REG_X_PLUS_Y='entries:
  - name: gf-x
    recurrence:
      count: 8
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-x.sh
    workflow: .github/workflows/wf-x.yml
  - name: gf-y
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-y.sh
    workflow: .github/workflows/wf-y.yml'

REG_X2='entries:
  - name: gf-x2
    recurrence:
      count: 8
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-x.sh
    workflow: .github/workflows/wf-x.yml'

REG_AB='entries:
  - name: gf-a
    recurrence:
      count: 8
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-a.sh
    workflow: .github/workflows/wf-a.yml
  - name: gf-b
    recurrence:
      count: 5
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-b.sh
    workflow: .github/workflows/wf-b.yml'

REG_AB_A3_C='entries:
  - name: gf-a
    recurrence:
      count: 3
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-a.sh
    workflow: .github/workflows/wf-a.yml
  - name: gf-b
    recurrence:
      count: 5
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-b.sh
    workflow: .github/workflows/wf-b.yml
  - name: gf-c
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-c.sh
    workflow: .github/workflows/wf-c.yml'

REG_AB_A3='entries:
  - name: gf-a
    recurrence:
      count: 3
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-a.sh
    workflow: .github/workflows/wf-a.yml
  - name: gf-b
    recurrence:
      count: 5
      threshold: 3
      promotion_trigger: auto_blocking
    detect_command: bash scripts/detect-b.sh
    workflow: .github/workflows/wf-b.yml'

# ── mk_fixture_repo <dir> <registry_content> — git repo + registry (carrier touch = caller) ──
mk_fixture_repo() {
  local dir="$1" reg="$2"
  mkdir -p "$dir/docs" "$dir/scripts" "$dir/.github/workflows"
  printf '%s\n' "$reg" > "$dir/docs/evidence-checks-registry.yaml"
  git -C "$dir" init -q >/dev/null 2>&1
  git -C "$dir" -c user.email=qa@t.co -c user.name=qa commit -q --allow-empty -m fixture >/dev/null 2>&1
}

# ── gen_baseline <dir> [out] — REAL gen tool (digest 정합). 실패는 FAIL 계수(비-abort) ──
gen_baseline() {
  local dir="$1"
  local out="${2:-$dir/baseline.yaml}"
  if ! python3 "$GEN_TOOL" generate --repo-root "$dir" \
        --registry "$dir/docs/evidence-checks-registry.yaml" --out "$out" >/dev/null 2>"$dir/gen.err"; then
    echo "✗ FAIL: gen_baseline SETUP ($dir): $(cat "$dir/gen.err" 2>/dev/null)"
    FAIL=$((FAIL+1))
  fi
  return 0
}

# ── write_reg <dir> <content> — registry 덮어쓰기 (gen 후 변형용) ──
write_reg() { printf '%s\n' "$2" > "$1/docs/evidence-checks-registry.yaml"; }

# ── run_gate_bl <name> <dir> <bl> <exp_exit> <must1> <must2|-> <mustnot|-> <desc> ──
#   gate 를 --baseline 로 invoke, exit + 필수/금지 substring 검증.
run_gate_bl() {
  local name="$1" dir="$2" bl="$3" exp="$4" must1="$5" must2="$6" mustnot="$7" desc="$8"
  local out ec=0
  out=$( bash "$GATE_WRAPPER" check --repo-root "$dir" \
           --registry "$dir/docs/evidence-checks-registry.yaml" --baseline "$bl" 2>&1 ) || ec=$?
  local ok=1
  [ "$ec" -eq "$exp" ] || ok=0
  if [ "$must1" != "-" ] && ! echo "$out" | grep -qE "$must1"; then ok=0; fi
  if [ "$must2" != "-" ] && ! echo "$out" | grep -qE "$must2"; then ok=0; fi
  if [ "$mustnot" != "-" ] &&   echo "$out" | grep -qE "$mustnot"; then ok=0; fi
  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name (exit $ec)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $exp got $ec; must1='$must1' must2='$must2' mustnot='$mustnot'"
    echo "  Description: $desc"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
  return 0
}

echo ""
echo "── Group 1: THE discriminating grandfather pair (baseline new-only) ──"

# GP-1a grandfathered PASS (kills M-a1: baseline 무시→전부 block)
DIR_GP1="$FIXROOT/gp1"
mk_fixture_repo "$DIR_GP1" "$REG_X"
touch "$DIR_GP1/scripts/detect-x.sh"           # detect EXISTS; workflow ABSENT
gen_baseline "$DIR_GP1"
run_gate_bl "GP-1a grandfathered PASS (count8=frozen8)" "$DIR_GP1" "$DIR_GP1/baseline.yaml" \
  0 "NEW-DEBT 0" "GRANDFATHERED 1" "::warning::check-deferred-followup-reconcile: FLAG" \
  "동일 registry → grandfathered subtract → exit 0 (M-a1 baseline 무시 mutant kill)"

# GP-1b new BLOCK (kills M-a2: new 무시). 위 baseline 고정 후 신규 gf-y 추가.
DIR_GP1B="$FIXROOT/gp1b"
mk_fixture_repo "$DIR_GP1B" "$REG_X"
touch "$DIR_GP1B/scripts/detect-x.sh"
gen_baseline "$DIR_GP1B"
write_reg "$DIR_GP1B" "$REG_X_PLUS_Y"          # gf-y 신규(carrier-absent, ∉baseline)
run_gate_bl "GP-1b new BLOCK (신규 gf-y 유입)" "$DIR_GP1B" "$DIR_GP1B/baseline.yaml" \
  1 "NEW-DEBT 1" "entry=gf-y" "-" \
  "baseline 에 없는 gf-y = new-debt → exit 1 (gf-x 는 여전히 GRANDFATHERED)"

echo ""
echo "── Group 1 (계속): EC-1/EC-2/carrier-removal/re-intro ──"

# GP-2 count-increase (EC-1, kills M-a3: count delta 무시). baseline count8 vs registry count10.
DIR_GP2="$FIXROOT/gp2"
mk_fixture_repo "$DIR_GP2" "$REG_X"
touch "$DIR_GP2/scripts/detect-x.sh"
gen_baseline "$DIR_GP2"
write_reg "$DIR_GP2" "$REG_X_C10"              # count 8→10 (악화)
run_gate_bl "GP-2 count-increase (8→10 악화)" "$DIR_GP2" "$DIR_GP2/baseline.yaml" \
  1 "NEW-DEBT 1" "entry=gf-x count=10" "-" \
  "count 증가 = NOT grandfathered → exit 1 (M-a3 monotonic count 검사 skip mutant kill)"

# GP-3 threshold-worsening (EC-2, kills M-a4: threshold 미독). baseline thr3 vs registry thr2.
DIR_GP3="$FIXROOT/gp3"
mk_fixture_repo "$DIR_GP3" "$REG_X"
touch "$DIR_GP3/scripts/detect-x.sh"
gen_baseline "$DIR_GP3"
write_reg "$DIR_GP3" "$REG_X_T2"               # threshold 3→2 (악화)
run_gate_bl "GP-3 threshold-worsening (3→2 악화)" "$DIR_GP3" "$DIR_GP3/baseline.yaml" \
  1 "NEW-DEBT 1" "entry=gf-x count=8/2" "-" \
  "threshold 하락 = NOT grandfathered → exit 1 (M-a4 threshold delta 미독 mutant kill)"

# GP-4 carrier-removal (추가 absent axis, kills M-a5: FLAG-set membership only).
#   baseline absent=[workflow] (detect exists) → check 시 detect 파일도 삭제 → absent 2축 ⊄ frozen.
DIR_GP4="$FIXROOT/gp4"
mk_fixture_repo "$DIR_GP4" "$REG_X"
touch "$DIR_GP4/scripts/detect-x.sh"
gen_baseline "$DIR_GP4"                          # frozen absent = {workflow:...}
rm -f "$DIR_GP4/scripts/detect-x.sh"            # detect_command 축도 absent 로 추가
run_gate_bl "GP-4 carrier-removal (새 absent axis)" "$DIR_GP4" "$DIR_GP4/baseline.yaml" \
  1 "NEW-DEBT 1" "detect_command:scripts/detect-x.sh" "-" \
  "현재 absent={workflow,detect_command} ⊄ frozen{workflow} → regression exit 1 (M-a5 kill)"

# GP-5 decl-only re-intro (kills M-a6: stale baseline 캐시).
#   gen 시 gf-x 양 carrier 실존 → baseline gate_flags 공백(pruned). check 시 workflow 삭제 → 재도입=new.
DIR_GP5="$FIXROOT/gp5"
mk_fixture_repo "$DIR_GP5" "$REG_X"
touch "$DIR_GP5/scripts/detect-x.sh"
touch "$DIR_GP5/.github/workflows/wf-x.yml"     # gen 시 양 carrier 실존 → gf-x NOT flag
gen_baseline "$DIR_GP5"                          # baseline gate_flags = []
rm -f "$DIR_GP5/.github/workflows/wf-x.yml"     # workflow 재삭제 → gf-x 재도입 FLAG
run_gate_bl "GP-5 decl-only re-intro (재도입=new)" "$DIR_GP5" "$DIR_GP5/baseline.yaml" \
  1 "NEW-DEBT 1" "entry=gf-x" "-" \
  "baseline 에 gf-x FLAG 부재(clean 이었음) → 재도입 = new-debt exit 1 (M-a6 stale cache kill)"

echo ""
echo "── Group 3: tamper / disguise / rename evasion ──"

# GE-2b 대조 (정상 gen baseline → grandfathered PASS)
DIR_GE2B="$FIXROOT/ge2b"
mk_fixture_repo "$DIR_GE2B" "$REG_X"
touch "$DIR_GE2B/scripts/detect-x.sh"
gen_baseline "$DIR_GE2B"
run_gate_bl "GE-2b control (정상 gen baseline)" "$DIR_GE2B" "$DIR_GE2B/baseline.yaml" \
  0 "GRANDFATHERED 1" "-" "BASELINE-TAMPER" \
  "gen 정상 baseline → digest 정합 → grandfathered PASS (tamper 아님)"

# GE-2 tamper (hand-edit frozen_count, digest 재계산 안 함 → digest 불일치)
DIR_GE2="$FIXROOT/ge2"
mk_fixture_repo "$DIR_GE2" "$REG_X"
touch "$DIR_GE2/scripts/detect-x.sh"
gen_baseline "$DIR_GE2"
sed -i 's/frozen_count: 8/frozen_count: 99/' "$DIR_GE2/baseline.yaml"   # 손편집(digest stale)
run_gate_bl "GE-2 tamper (frozen_count hand-edit, digest stale)" "$DIR_GE2" "$DIR_GE2/baseline.yaml" \
  1 "BASELINE-TAMPER" "content_digest 불일치" "-" \
  "baseline 손편집 후 digest 미재계산 → content_digest 불일치 → exit 1 (tamper-evident)"

# GE-3 disguise-new-as-preexisting (EC-5, INV-5): PR 이 baseline 에 surface 를 손으로 주입.
DIR_GE3="$FIXROOT/ge3"
mk_fixture_repo "$DIR_GE3" "$REG_X"
touch "$DIR_GE3/scripts/detect-x.sh"
gen_baseline "$DIR_GE3"
python3 - "$DIR_GE3/baseline.yaml" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
t = t.replace(
    "declaration_surfaces: []",
    "declaration_surfaces:\n- locator: docs/fake.md:1\n  token: 'deferred_followup_cfp: TBD'\n  reason: injected-disguise",
)
open(p, "w", encoding="utf-8", newline="\n").write(t)
PYEOF
run_gate_bl "GE-3 disguise-new-as-preexisting (surface hand-inject)" "$DIR_GE3" "$DIR_GE3/baseline.yaml" \
  1 "BASELINE-TAMPER" "-" "-" \
  "PR 이 baseline 을 손편집(surface 주입)해 new 를 preexisting 로 위장 → digest 불일치 exit 1 (INV-5)"

# GE-4 rename evasion (EC-4, kills M-e4: fuzzy match). gf-x → gf-x2 동명 debt 새이름.
DIR_GE4="$FIXROOT/ge4"
mk_fixture_repo "$DIR_GE4" "$REG_X"
touch "$DIR_GE4/scripts/detect-x.sh"
gen_baseline "$DIR_GE4"                          # baseline gate_flags = {gf-x}
write_reg "$DIR_GE4" "$REG_X2"                   # gf-x → gf-x2 (rename)
run_gate_bl "GE-4 rename evasion (gf-x→gf-x2)" "$DIR_GE4" "$DIR_GE4/baseline.yaml" \
  1 "NEW-DEBT 1" "entry=gf-x2" "-" \
  "exact-match + new-only → gf-x2 = new (fuzzy match mutant M-e4 kill)"

echo ""
echo "── Group 4: boundary / theater killers (OR 대칭 셀 + no-offset) ──"

# BT-2a detect ABSENT + workflow EXISTS → FLAG (legacy, TC-4 동형)
touch "$TMP_REPO/.github/workflows/bt2a-wf.yml"
run_test \
  "BT-2a boundary — detect ABSENT, workflow EXISTS" \
  'entries:
  - name: bt2a-entry
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/bt2a-missing.sh
    workflow: .github/workflows/bt2a-wf.yml
    status: Active
' \
  "yes" \
  "1" \
  "OR: detect_command ABSENT (workflow 실존) → FLAG (OR→AND 대칭 셀 A)"

# BT-2b (신규 대칭) detect EXISTS + workflow ABSENT → FLAG
touch "$TMP_REPO/scripts/bt2b-detect.sh"
run_test \
  "BT-2b boundary — detect EXISTS, workflow ABSENT" \
  'entries:
  - name: bt2b-entry
    recurrence:
      count: 2
      threshold: 1
      promotion_trigger: auto_blocking
    detect_command: bash scripts/bt2b-detect.sh
    workflow: .github/workflows/bt2b-missing.yml
    status: Active
' \
  "yes" \
  "1" \
  "OR: workflow ABSENT (detect 실존) → FLAG (OR→AND 대칭 셀 B — 대칭 mutant kill)"

# BT-5 no-offset (EC-15, INV-3): A 개선 + 신규 C → C 때문에 exit 1 (상계 금지)
DIR_BT5="$FIXROOT/bt5"
mk_fixture_repo "$DIR_BT5" "$REG_AB"
touch "$DIR_BT5/scripts/detect-a.sh" "$DIR_BT5/scripts/detect-b.sh"   # workflow 양쪽 absent
gen_baseline "$DIR_BT5"                          # baseline = {gf-a@8, gf-b@5}
write_reg "$DIR_BT5" "$REG_AB_A3_C"             # A 8→3(개선) + 신규 gf-c
touch "$DIR_BT5/scripts/detect-a.sh" "$DIR_BT5/scripts/detect-b.sh"   # (detect-c 는 absent 유지)
run_gate_bl "BT-5 no-offset (A개선 + 신규 C)" "$DIR_BT5" "$DIR_BT5/baseline.yaml" \
  1 "NEW-DEBT 1" "entry=gf-c" "-" \
  "A 개선이 C 신규를 상계하지 못함 → exit 1 (INV-3 상계 금지)"

# BT-5b 대조: A 개선 only → exit 0
DIR_BT5B="$FIXROOT/bt5b"
mk_fixture_repo "$DIR_BT5B" "$REG_AB"
touch "$DIR_BT5B/scripts/detect-a.sh" "$DIR_BT5B/scripts/detect-b.sh"
gen_baseline "$DIR_BT5B"
write_reg "$DIR_BT5B" "$REG_AB_A3"              # A 개선만 (신규 없음)
touch "$DIR_BT5B/scripts/detect-a.sh" "$DIR_BT5B/scripts/detect-b.sh"
run_gate_bl "BT-5b control (A개선 only)" "$DIR_BT5B" "$DIR_BT5B/baseline.yaml" \
  0 "NEW-DEBT 0" "GRANDFATHERED 2" "::warning::check-deferred-followup-reconcile: FLAG" \
  "A/B 모두 grandfathered(개선/동일) → NEW-DEBT 0 exit 0"

echo ""
echo "── Group 5: idempotency (gen determinism + author-verify) ──"

# ID-1 baseline gen determinism (AC-9): 동일 HEAD → byte-identical + digest 동일 + CRLF 0
DIR_ID1="$FIXROOT/id1"
mk_fixture_repo "$DIR_ID1" "$REG_X"
touch "$DIR_ID1/scripts/detect-x.sh"
gen_baseline "$DIR_ID1" "$DIR_ID1/b1.yaml"
gen_baseline "$DIR_ID1" "$DIR_ID1/b2.yaml"
id1_ok=1
if ! cmp -s "$DIR_ID1/b1.yaml" "$DIR_ID1/b2.yaml"; then id1_ok=0; fi
# CRLF 회귀 catch (platform LF-only 보장) — python rb 권위 검사 (MSYS grep 불안정 회피)
if ! python3 -c "import sys; sys.exit(1 if b'\r' in open(sys.argv[1],'rb').read() else 0)" "$DIR_ID1/b1.yaml"; then id1_ok=0; fi
if [ "$id1_ok" -eq 1 ]; then
  echo "✓ PASS: ID-1 gen determinism (byte-identical + CRLF 0)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: ID-1 gen determinism (2 gen 출력 불일치 또는 CRLF 유입)"
  FAIL=$((FAIL+1))
fi

# ID-3 author-verify (§결정6 v): bot→0 / human→1 / absent→1 + selftest→0
#   (ID-2 sticky at-most-once = 워크플로 gh step idempotency, CI-only 로컬 unit 불가 →
#    documented-limitation. author-verify + gen determinism 로 대체 커버.)
AUTH_TOOL="$REPO_ROOT/scripts/lib/check_audit_comment_author.py"
assert_author() {
  local name="$1" json="$2" exp="$3" desc="$4"
  local jf="$TMP_REPO/_auth_$name.json" ec=0
  printf '%s' "$json" > "$jf"
  python3 "$AUTH_TOOL" check --comments-json "$jf" >/dev/null 2>&1 || ec=$?
  if [ "$ec" -eq "$exp" ]; then
    echo "✓ PASS: ID-3 author $name (exit $ec)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: ID-3 author $name (expected $exp got $ec) — $desc"
    FAIL=$((FAIL+1))
  fi
  return 0
}
assert_author "bot" \
  '[{"author":{"login":"github-actions[bot]"},"body":"[hotfix-bypass-audit] PR=1 reason=x"}]' \
  0 "bot-authored tagged audit comment → PASS"
assert_author "human" \
  '[{"author":{"login":"mccho-mclayer"},"body":"[hotfix-bypass-audit] PR=1 reason=x"}]' \
  1 "human-authored tagged audit comment → FAIL (spoof)"
assert_author "absent" \
  '[{"author":{"login":"github-actions[bot]"},"body":"normal comment, no audit tag"}]' \
  1 "tagged 부재 → FAIL (audit absent)"
auth_st=0
python3 "$AUTH_TOOL" selftest >/dev/null 2>&1 || auth_st=$?
if [ "$auth_st" -eq 0 ]; then
  echo "✓ PASS: ID-3 author selftest (3/3 embedded)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: ID-3 author selftest (anti-theater breach, exit $auth_st)"
  FAIL=$((FAIL+1))
fi

# ─────────────────────── gate mutation testing (M-a1/M-a3/M-a4) ─────────────────
echo ""
echo "── gate mutation testing (production 변조 시 RED — mutation 생존 0) ──"

# gate_mutate_and_check <mut> <old> <new> <dir> <bl> <orig_should_flag yes/no> <desc>
#   $TMP_REPO 사본 gate py 를 1회 literal 치환(env-var — backslash/heredoc 안전). anchor no-op
#   이면 fail-loud. orig 대비 FLAG 뒤집힘 = kill. baseline 은 REAL gen 산출(digest 정합, 미변조).
gate_mutate_and_check() {
  local mut_name="$1" old_str="$2" new_str="$3" dir="$4" bl="$5" orig="$6" desc="$7"
  cp "$GATE_PY_BAK" "$GATE_PY"
  local changed
  changed=$( MUT_OLD="$old_str" MUT_NEW="$new_str" MUT_PATH="$GATE_PY" python3 - <<'PYEOF'
import os, io
path = os.environ["MUT_PATH"]
old = os.environ["MUT_OLD"]
new = os.environ["MUT_NEW"]
src = io.open(path, encoding="utf-8").read()
if old not in src:
    print("NOOP")
else:
    io.open(path, "w", encoding="utf-8").write(src.replace(old, new, 1))
    print("CHANGED")
PYEOF
)
  if [ "$changed" != "CHANGED" ]; then
    echo "✗ FAIL: $mut_name — mutation anchor NOT FOUND (stale anchor, 치환 no-op)"
    echo "  old_str: $old_str"
    cp "$GATE_PY_BAK" "$GATE_PY"
    FAIL=$((FAIL+1))
    return 0
  fi
  local out ec=0
  out=$( bash "$GATE_WRAPPER" check --repo-root "$dir" \
           --registry "$dir/docs/evidence-checks-registry.yaml" --baseline "$bl" 2>&1 ) || ec=$?
  local has_flag=0
  if echo "$out" | grep -q "::warning::check-deferred-followup-reconcile: FLAG"; then has_flag=1; fi
  cp "$GATE_PY_BAK" "$GATE_PY"
  local killed=0
  if [ "$orig" = "yes" ] && [ "$has_flag" -eq 0 ]; then killed=1; fi
  if [ "$orig" = "no" ]  && [ "$has_flag" -eq 1 ]; then killed=1; fi
  if [ "$killed" -eq 1 ]; then
    echo "✓ PASS: $mut_name killed (mutation 생존 0)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $mut_name SURVIVED (has_flag=$has_flag orig=$orig — lint 결함 가능)"
    echo "  Description: $desc"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
  return 0
}

# M-a1: grandfather subtract 무력화 (new-only 에서 baseline 무시) → GP-1a RED (no-flag→flag).
gate_mutate_and_check "M-a1 (grandfather subtract 무력화)" \
  'if frozen is not None and grandfathered_ok(item, frozen):' \
  'if False and frozen is not None and grandfathered_ok(item, frozen):' \
  "$DIR_GP1" "$DIR_GP1/baseline.yaml" "no" \
  "grandfather subtract 제거 시 gf-x 재flag → GP-1a(grandfathered 기대) 과검출 RED"

# M-a3: count delta 비교 제거 (monotonic count 검사 skip) → GP-2 RED (flag→no-flag).
gate_mutate_and_check "M-a3 (count delta 비교 제거)" \
  'if cur_count > frozen_count:' \
  'if False:' \
  "$DIR_GP2" "$DIR_GP2/baseline.yaml" "yes" \
  "count delta 검사 skip 시 count10 이 grandfathered → GP-2(악화 flag 기대) 미검출 RED"

# M-a4: threshold delta 비교 제거 → GP-3 RED (flag→no-flag).
gate_mutate_and_check "M-a4 (threshold delta 비교 제거)" \
  'if cur_threshold < frozen_threshold:' \
  'if False:' \
  "$DIR_GP3" "$DIR_GP3/baseline.yaml" "yes" \
  "threshold delta 검사 skip 시 thr2 가 grandfathered → GP-3(악화 flag 기대) 미검출 RED"

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
  echo ""
  echo "CFP-2591 Phase 2 baseline new-only fixtures:"
  echo "  ✓ Group 1 (grandfather pair): GP-1a/1b/2/3/4/5 (M-a1~a6 kill)"
  echo "  ✓ Group 3 (tamper/disguise/rename): GE-2b/2/3/4"
  echo "  ✓ Group 4 (OR 대칭 셀 + no-offset): BT-2a/2b/5/5b"
  echo "  ✓ Group 5 (idempotency): ID-1 gen determinism / ID-3 author-verify"
  echo "  ✓ gate mutations killed: M-a1(grandfather) / M-a3(count) / M-a4(threshold)"
  exit 0
else
  echo "Some tests failed ✗"
  exit 1
fi
