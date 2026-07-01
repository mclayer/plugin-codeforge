#!/usr/bin/env bash
# tests/scripts/test-actionlint-workflows.sh
# CFP-2530 Phase 2 — Discriminating self-test for workflow schema validation (ADR-136 Amendment 2 결정13).
# CFP-2535 Phase 2 — N-class 일반화: class registry loop (ADR-136 Amendment 3 결정14).
#
# actionlint.yml 의 discriminating test job 이 호출(InfraEngineerAgent 가
#   `if: github.repository == 'mclayer/plugin-codeforge'` job 에서 `bash tests/scripts/test-actionlint-workflows.sh`).
#
# ── N-class 구조 (CFP-2535 Amendment 3 결정14) ────────────────────────────────
# 단일 class 하드코딩(CFP-2530) → class registry 기반 N-class loop 로 일반화.
# 각 class = 4-tuple { id, error_string_pattern, mutation_recipe, source_pin }.
# class 마다 discriminating 3-분기(C1 GREEN / C2 RED mutation-kill / anti-theater)를 loop.
#
# ── 등록 class (N=2) ─────────────────────────────────────────────────────────
# 1. context-availability — job-level hashFiles() 호출: context-availability 위반.
#    seed class(CFP-2530) 그대로 보존. regression 0.
# 2. undefined-context — 미정의 context 참조: steps.ghost.outputs.x 류.
#    actionlint 1.7.12 [expression] rule. 실측 ground-truth 확인.
#
# ── 후보 B/C DROP 이유 (comment-only, 등록 금지) ─────────────────────────────
# class B (`continue-on-error` + `exit 0` 삼킴) 및 class C (optional-install `|| true` skip)는
# BEHAVIORAL/semantic hollow-gate 패턴이다. actionlint 1.7.12 는 이 두 패턴을 정적 workflow
# 스키마 검사 범위에서 탐지하지 않는다(실측: 두 mutation 모두 exit 0, grep count 0).
# actionlint 는 정적 workflow schema linter — runtime gate-liveness semantics 는
# actionlint 의 detection surface 밖이다. mutation 이 actionlint finding 을 유발하지 않으므로
# discriminating power 가 없다. discriminating power 미확보 class 등록 = 검사연극(self-defeating)
# → ADR-136 결정14 §14.3 "실측으로 discriminating power 미확보 class 는 drop(hollow class 등록 금지)" 준수.
#
# ── 판정 스코프 ──────────────────────────────────────────────────────────────
# actionlint 는 `run:` 블록 shell 을 shellcheck 로 겸 검사한다. 본 repo 에는 장기 pre-existing
# shellcheck 부채(SC2086/SC2016/SC2034/SC2193/SC2126 "Double quote to prevent globbing" 등)가
# 다수 기존 workflow 의 run 블록에 존재한다. actionlint-check.yml 은 warning-tier(항상 exit 0)라
# 이 부채를 강제하지 않았다. 따라서 "whole-repo actionlint exit 0" 을 요구하면 CFP-2530/CFP-2535
# 무관한 shellcheck 부채까지 요구하게 되어 born-false-red 가 된다.
# → 본 게이트는 판정을 actionlint OVERALL EXIT CODE 가 아니라 CLASS-SCOPED COUNT(grep) 로 한정.
# 각 class 의 count 0/>=1 대조가 primary 판정 — shellcheck 부채는 스코프 밖(무영향).
# (ADR-136 §14.2 안① grep-count-per-class 정형화)
#
# ── anti-theater (비협상, class 마다) ────────────────────────────────────────
# GREEN count(0) ≠ RED count(>=1): mutation-kill discriminating.
# 동일하면 non-discriminating hollow → FAIL.
# mutation 미실행(fixture-missing/recipe-failed) = "NOT_RUN" sentinel → 대조 skip (FIX-3).
#
# ── AC-1 버전 pin drift-guard (ADR-136 §14.4) ───────────────────────────────
# N-class 문자열-판정은 actionlint pin 1.7.12 고정 하에서만 유효하다.
# 본 pin 은 actionlint-check.yml / actionlint-workflows-test.yml 의
# `download-actionlint.bash 1.7.12` 와 정합(양 workflow 실측).
# actionlint 버전 bump PR 은 각 class fixture 의 RED/GREEN 을 재검증하는 것을
# 동반 의무로 한다(error-string drift → grep miss → false-GREEN silent hollow 방지).
# error_string 무pin class 등록 금지.
#
# ── L2 full-scope (ADR-136 §14.1) ───────────────────────────────────────────
# GREEN scan = .github/workflows/*.yml + templates/github-workflows/*.yml 양쪽.
# (Amd2 F8 actionlint glob gap 봉인 무변경)
#
# ── graceful skip (로컬 / actionlint 미설치) ────────────────────────────────
# actionlint 부재 시 silent pass 위장 금지 → 명시 ::notice:: 로그 후 exit 0.
# CI(actionlint-workflows-test.yml)는 actionlint 설치 후 호출하므로 실 실행됨.
#
# Exit code:
#  0 = all discriminating cases pass (또는 명시적 graceful skip)
#  1 = any case fails (actionlint 에러 / discrimination 깨짐)

set -uo pipefail

PASS=0
FAIL=0
SKIP=0

note() { echo "::notice::$*"; }

# ─────────────────────────────────────────────────────────────────────────────
# Precondition: actionlint 존재 확인. 부재 시 graceful skip(명시 로그) + exit 0.
# ─────────────────────────────────────────────────────────────────────────────
if ! command -v actionlint >/dev/null 2>&1; then
  note "[test-actionlint-workflows] actionlint 미설치 — 로컬 graceful skip (CI actionlint 사전설치 후 실 실행 전제). NOT a silent pass."
  echo "SKIP: actionlint 부재 (0 discriminating case 실행). CI 에서 재검증 필요."
  exit 0
fi

note "[test-actionlint-workflows] actionlint 가용 — 실 실행 모드."

# ─────────────────────────────────────────────────────────────────────────────
# Repo root 결정 (현재 cwd 사용 또는 git rev-parse).
# CI 환경(checkout root 에서 호출): cwd = repo root 이미 설정.
# 로컬(script 직접 실행): git rev-parse --show-toplevel 사용.
# ─────────────────────────────────────────────────────────────────────────────
if [ -d ".github/workflows" ] && [ -d "templates/github-workflows" ]; then
  REPO_ROOT="."
else
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
fi
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"

# ─────────────────────────────────────────────────────────────────────────────
# violation_count_for_pattern <pattern> <actionlint-args...> → echo count (stdout).
#   actionlint 실행(exit code 무시 — `|| true`, shellcheck 부채로 non-zero 나와도 무시),
#   stdout+stderr 합쳐 지정 pattern 위반 라인만 grep count.
# ─────────────────────────────────────────────────────────────────────────────
violation_count_for_pattern() {
  local pattern="$1"
  shift
  local out
  out=$( ( cd "$REPO_ROOT" && timeout 60 actionlint "$@" ) 2>&1 || true )
  echo "$out" | grep -Ec "$pattern" || true
}

assert_eq() {
  local name="$1" expected="$2" actual="$3" desc="$4"
  if [ "$actual" = "$expected" ]; then
    echo "  ✓ PASS: $name (got $actual) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "  ✗ FAIL: $name"
    echo "    Expected $expected, got $actual"
    echo "    Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

assert_ge1() {
  local name="$1" actual="$2" desc="$3"
  if [ "$actual" -ge 1 ] 2>/dev/null; then
    echo "  ✓ PASS: $name (got count $actual >= 1 = 위반 검출) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "  ✗ FAIL: $name"
    echo "    Expected count >= 1 (위반 검출), got $actual — RED mutation-kill 보장 깨짐"
    echo "    Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# run_class_discriminating <class_id> <error_pattern> <source_file_for_mutation> <mutation_fn_name>
#
# 각 class 마다 3-분기를 실행한다:
#   C1 GREEN:       전체 workflow 에 해당 class pattern count == 0
#   C2 RED:         temp fixture 에 mutation 삽입 후 count >= 1
#   ANTI-THEATER:   C1(0) ≠ C2(>=1) — discriminating 확인
#
# <mutation_fn_name> = 아래 정의된 mutation 함수명. 함수 시그니처:
#   <fn_name> <temp_dir> <source_file> → 0=성공(mutation 적용), 1=실패
# 함수는 성공 시 "$temp_dir/mutated.yml" 에 변이 파일 생성.
# ─────────────────────────────────────────────────────────────────────────────
run_class_discriminating() {
  local class_id="$1"
  local error_pattern="$2"
  local source_file="$3"
  local mutation_fn="$4"

  echo ""
  echo "══════════════════════════════════════════════════════════════════════"
  echo "CLASS: $class_id"
  echo "  pattern: $error_pattern"
  echo "══════════════════════════════════════════════════════════════════════"

  # ── C1 GREEN: 정정 후 전체 workflow(양 copy)에 해당 class count == 0 ──────
  echo "  [C1 GREEN] 전체 workflow 실행 (exit code 무시, pattern count 판정)"
  local c1_count
  c1_count=$(violation_count_for_pattern "$error_pattern" \
    "$REPO_ROOT/.github/workflows/"*.yml \
    "$REPO_ROOT/templates/github-workflows/"*.yml)
  assert_eq "C1-green-${class_id}" "0" "$c1_count" \
    "정정 후 전체 workflow(.github + templates)에 '${class_id}' 위반 0건"

  # ── C2 RED mutation: temp fixture 에 mutation 삽입 후 count >= 1 ───────────
  echo "  [C2 RED] mutation-kill 검증 (temp fixture only — repo 실파일 무오염)"
  local c2_count="NOT_RUN"

  if [ ! -f "$source_file" ]; then
    note "[test-actionlint-workflows] ${class_id}: mutation source file 부재(${source_file}) — RED fixture 생성 불가. FAIL."
    echo "  ✗ FAIL: C2-red-${class_id}-fixture-missing"
    echo "    Expected source file 존재: $source_file, got 파일 부재"
    FAIL=$((FAIL+1))
    # c2_count = NOT_RUN 유지 → anti-theater skip
  else
    local temp_dir
    temp_dir="$(mktemp -d)"
    if "$mutation_fn" "$temp_dir" "$source_file"; then
      local mutated_file="$temp_dir/mutated.yml"
      if [ -f "$mutated_file" ]; then
        c2_count=$(violation_count_for_pattern "$error_pattern" "$mutated_file")
        assert_ge1 "C2-red-${class_id}" "$c2_count" \
          "mutation 삽입 후 '${class_id}' 위반 검출(count >= 1 = 차단 확인)"
      else
        note "[test-actionlint-workflows] ${class_id}: mutation 함수가 mutated.yml 을 생성하지 않았음. FAIL."
        echo "  ✗ FAIL: C2-red-${class_id}-mutation-output-missing"
        FAIL=$((FAIL+1))
      fi
    else
      note "[test-actionlint-workflows] ${class_id}: mutation 적용 실패. FAIL."
      echo "  ✗ FAIL: C2-red-${class_id}-mutation-failed"
      FAIL=$((FAIL+1))
    fi
    rm -rf "$temp_dir"
  fi

  # ── ANTI-THEATER: C1(0) ≠ C2(>=1) — discriminating (FIX-3 상속) ─────────
  echo "  [ANTI-THEATER] discriminating 대조: C1=$c1_count / C2=$c2_count"
  if [ "$c2_count" = "NOT_RUN" ]; then
    echo "  ⊘ SKIP: ANTI-THEATER 대조 불가 — RED mutation 미실행(fixture-missing / mutation-failed)."
    echo "    대조 skip(위 mutation 실패가 이미 FAIL 처리). false 'ANTI-THEATER PASS' 오보 차단(FIX-3)."
    SKIP=$((SKIP+1))
  elif [ "$c1_count" = "$c2_count" ]; then
    echo "  ✗ FAIL: ANTI-THEATER — C1 count($c1_count) 과 RED mutation count($c2_count) 동일"
    echo "    = non-discriminating hollow gate. class '$class_id' 가 discriminating power 없음."
    FAIL=$((FAIL+1))
  else
    echo "  ✓ PASS: ANTI-THEATER discriminating — C1 count=$c1_count ≠ RED mutation count=$c2_count"
    PASS=$((PASS+1))
  fi

  # 클래스별 증거 라인 출력 (summary block 에서도 재참조)
  echo "  → class=$class_id | GREEN count=$c1_count | RED count=$c2_count"
}

# ═════════════════════════════════════════════════════════════════════════════
# CLASS REGISTRY MUTATION FUNCTIONS
# 각 함수: mutation_<class_id> <temp_dir> <source_file> → 0=성공 / non-0=실패
#   성공 시 "$temp_dir/mutated.yml" 에 변이 파일 생성 (repo 실파일 무오염).
# ═════════════════════════════════════════════════════════════════════════════

# ── mutation_context_availability ────────────────────────────────────────────
# class: context-availability (seed, CFP-2530)
# source_pin: actionlint v1.7.12, rule ctx-spfunc-availability
#   literal ground-truth: `calling function "hashFiles" is not allowed here`
# mutation_recipe: css-lint.yml 의 css-lint: job 에 job-level `if: hashFiles(...)` 재삽입.
#   sed 로 `  css-lint:` 줄 다음에 job-level if 삽입 → actionlint context-availability 위반 유발.
mutation_context_availability() {
  local temp_dir="$1"
  local source_file="$2"
  local mutated="$temp_dir/mutated.yml"

  cp "$source_file" "$mutated"

  # `  css-lint:` job 헤더 다음 줄에 job-level if: hashFiles(...) 삽입.
  sed -i '/^  css-lint:$/a\    if: hashFiles('"'"'**/*.css'"'"', '"'"'**/*.scss'"'"', '"'"'**/*.html'"'"') != '"'"''"'"'' "$mutated"

  # mutation 적용 확인 (grep: hashFiles 가 실제로 들어갔는지).
  if grep -q "hashFiles.*\*\*/\*\.css" "$mutated" 2>/dev/null; then
    return 0
  else
    echo "    mutation sed 적용 실패 또는 pattern 부매칭 — temp fixture 점검 필요"
    head -50 "$mutated" >&2
    return 1
  fi
}

# ── mutation_undefined_context ────────────────────────────────────────────────
# class: undefined-context (CFP-2535 신규)
# source_pin: actionlint v1.7.12, rule [expression]
#   literal ground-truth: `property "<name>" is not defined in object type {} [expression]`
#   tolerant regex: `is not defined in object type`
#   (주의: [expression] 을 regex 에 넣지 않음 — seed class hashFiles 에러도 [expression] 을
#    포함하므로 cross-contamination 발생. `is not defined in object type` 은 seed pattern
#    `not allowed here|not available in .*context` 와 완전히 disjoint. 양방향 count 격리 실측 확인.)
# mutation_recipe: css-lint.yml 을 temp copy 후, 미정의 context 참조를 포함한 신규 job append.
#   steps.ghost_step_never_defined.outputs.x → actionlint [expression] 위반 유발.
#   append 방식 = source file 형태에 무관하게 deterministic (sed anchor 의존 불필요).
mutation_undefined_context() {
  local temp_dir="$1"
  local source_file="$2"
  local mutated="$temp_dir/mutated.yml"

  cp "$source_file" "$mutated"

  # 미정의 context 참조 신규 job 을 파일 끝에 append.
  # steps.ghost_step_never_defined.outputs.x 는 해당 job 내 어느 step 도 id=ghost_step_never_defined 가 없어
  # actionlint [expression] 위반: `property "ghost_step_never_defined" is not defined in object type {}`
  cat >> "$mutated" <<'MUTATION_EOF'

  __mutation_undefined_context__:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ steps.ghost_step_never_defined.outputs.x }}"
MUTATION_EOF

  # mutation 적용 확인 (append 한 job 이 실제로 들어갔는지).
  if grep -q "__mutation_undefined_context__" "$mutated" 2>/dev/null; then
    return 0
  else
    echo "    undefined-context mutation append 실패 — temp fixture 점검 필요"
    return 1
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# CLASS REGISTRY (N=2)
# 형식: run_class_discriminating <id> <error_pattern> <source_file> <mutation_fn>
#
# 버전 pin (AC-1 drift-guard, ADR-136 §14.4):
#   actionlint 1.7.12 하에서만 유효. pin bump 시 각 class RED/GREEN 재검증 의무.
#   error_string 무pin class 등록 금지.
#
# L2 full-scope (ADR-136 §14.1):
#   C1 GREEN 은 항상 .github/workflows/*.yml + templates/github-workflows/*.yml 양쪽 실행.
#   (run_class_discriminating 함수 내부에서 양쪽 glob 을 고정으로 전달.)
# ═════════════════════════════════════════════════════════════════════════════

echo ""
echo "============================================================"
echo "test-actionlint-workflows.sh — N-class registry loop"
echo "actionlint pin: 1.7.12 (AC-1 drift-guard, ADR-136 §14.4)"
echo "N=2 classes, L2 full-scope (.github/ + templates/)"
echo "============================================================"

# ── Class 1: context-availability (seed, CFP-2530 — regression 보존) ─────────
# source_pin: actionlint v1.7.12, rule ctx-spfunc-availability
#   literal: `calling function "hashFiles" is not allowed here`
#   tolerant regex: `not allowed here|not available in .*context`
#   (CFP-2530 실측 그대로 — regression 0)
run_class_discriminating \
  "context-availability" \
  'not allowed here|not available in .*context' \
  "$REPO_ROOT/.github/workflows/css-lint.yml" \
  "mutation_context_availability"

# ── Class 2: undefined-context (CFP-2535 신규) ───────────────────────────────
# source_pin: actionlint v1.7.12, rule [expression]
#   literal: `property "<name>" is not defined in object type {} [expression]`
#   tolerant regex: `is not defined in object type`
#   (disjoint from class 1 pattern — cross-contamination 0, 실측 count 격리 확인)
run_class_discriminating \
  "undefined-context" \
  'is not defined in object type' \
  "$REPO_ROOT/.github/workflows/css-lint.yml" \
  "mutation_undefined_context"

# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "Test Summary (CFP-2530 Phase 2 + CFP-2535 N-class — actionlint workflow validation)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "SKIP: $SKIP"
echo "TOTAL ASSERT: $((PASS + FAIL))"
echo ""
echo "Discriminating evidence (anti-theater) — 판정 = class-scoped count (shellcheck 부채 스코프 밖):"
echo "  actionlint pin: 1.7.12 (AC-1 drift-guard)"
echo "  L2 full-scope: .github/workflows/*.yml + templates/github-workflows/*.yml"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (SKIP=$SKIP 은 명시적 graceful skip — silent pass 아님)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
