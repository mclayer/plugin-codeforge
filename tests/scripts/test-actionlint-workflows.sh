#!/usr/bin/env bash
# tests/scripts/test-actionlint-workflows.sh
# CFP-2530 Phase 2 — Discriminating self-test for workflow schema validation (ADR-136 Amendment 2 결정13).
#
# actionlint.yml 의 discriminating test job 이 호출(InfraEngineerAgent 가
#   `if: github.repository == 'mclayer/plugin-codeforge'` job 에서 `bash tests/scripts/test-actionlint-workflows.sh`).
#
# 본 test 가 검증하는 ADR-136 결정13 invariant:
#  - 문제: css-lint.yml 의 job-level `if: hashFiles(...) != ''` 는 GitHub Actions context-availability 위반.
#    hashFiles() 는 step-level 등 특정 context 에서만 available — job-level if 에서는 불가.
#    actionlint ground-truth: `calling function "hashFiles" is not allowed here`
#  - 결과: workflow load-time schema-invalid → css-lint-test 게이트가 신설 이래 0회 실행된 dead gate.
#  - 방어: actionlint exit!=0 으로 이 class 의 결함(context-availability / schema-invalid)을 자동 검출.
#    [source: rhysd/actionlint — job-level if context restriction]
#  - 정정: css-lint.yml 의 job-level if 제거 (step-level 또는 workflow-level 다른 메커니즘으로 이동).
#
# ── 판정 스코프 = context-availability 위반 클래스 (recurrence class, NOT whole-repo 청결) ──
#  actionlint 는 `run:` 블록 shell 을 shellcheck 로 겸 검사한다. 본 repo 에는 장기 pre-existing
#  shellcheck 부채(SC2086/SC2016/SC2034/SC2193/SC2126 "Double quote to prevent globbing" 등)가
#  다수 기존 workflow(adr-citation-slug / auto-deploy / bidirectional-smoke / cross-layer-impact-check
#  / decision-principle-vocabulary / deferred-item-recovery …)의 run 블록에 존재한다. actionlint-check.yml
#  은 warning-tier(항상 exit 0)라 이 부채를 강제하지 않았다. 따라서 "whole-repo actionlint exit 0" 을
#  요구하면 CFP-2530 무관한 shellcheck 부채까지 요구하게 되어 born-false-red 가 된다.
#  → 본 게이트는 판정을 actionlint OVERALL EXIT CODE 가 아니라 CONTEXT-AVAILABILITY 위반 COUNT(grep)
#    로 한정한다. recurrence class = job-level `if: hashFiles(...)` 류(step-level 전용 함수의
#    job-level 사용). 이게 CFP-2530 이 봉인해야 하는 재유입 클래스이고, .github/ + templates/ 양쪽을
#    커버(안 B 차단 채널)한다. shellcheck 부채 전면 정리(150+ workflow)는 CFP-2530 scope 밖 —
#    별 governance Story(ADR-060 actionlint blocking 승격 path). ADR-136 §8 spec 의 "전체 workflow
#    exit 0" 은 이 실측 현실로 클래스-scoped refine(intent=job-level hashFiles 재유입 차단 보존).
#
# ── anti-theater (비협상) ────────────────────────────────────────────────────
#  - 정정 후(GREEN): 전체 workflow 에 actionlint 실행(exit code 무시) → context-availability 위반
#    count == 0. shellcheck SC-경고는 이 패턴 미매칭이라 무영향.
#  - 정정 전 (RED mutation): css-lint.yml 의 job-level `if: hashFiles(...)` 를 재삽입해 actionlint
#    가 context-availability 위반을 도입(count >= 1)하는지 확인. mutation 은 temp fixture 사본에만 —
#    실제 repo 파일은 오염시키지 않음.
#  - GREEN(count 0) ≠ RED(count >= 1): mutation-kill discriminating. 둘이 같으면 hollow → FAIL.
#  - context-availability 위반 판정 패턴: `not allowed here|not available in .*context`.
#    실측 문구: `calling function "hashFiles" is not allowed here`.
#
# ── graceful skip (로컬 / actionlint 미설치) ────────────────────────────────────
#  actionlint 부재 시 silent pass 위장 금지 → 명시 ::notice:: 로그 후 exit 0.
#  CI(actionlint-workflows-test.yml)는 actionlint 설치 후 호출하므로 실 실행됨.
#  로컬(actionlint 없는 환경)에서만 skip.
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
  # cwd 가 이미 repo root (CI 환경)
  REPO_ROOT="."
else
  # git rev-parse 시도
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
fi
REPO_ROOT="$(cd "$REPO_ROOT" && pwd)"

# ─────────────────────────────────────────────────────────────────────────────
# run_actionlint <glob-pattern...> → echo exit code (stdout 으로 반환).
#   $REPO_ROOT 에서 actionlint 실행. 모든 pattern match 파일 한 번에 검증.
# ─────────────────────────────────────────────────────────────────────────────
run_actionlint_exit() {
  local ec=0
  ( cd "$REPO_ROOT" && timeout 60 actionlint "$@" >/dev/null 2>&1 ) || ec=$?
  echo "$ec"
}

# ─────────────────────────────────────────────────────────────────────────────
# ctx_avail_violation_count <actionlint-args...> → echo count (stdout).
#   actionlint 실행(exit code 무시 — `|| true`, shellcheck 부채로 non-zero 나와도 무시),
#   stdout+stderr 합쳐 context-availability 위반 라인만 grep count. shellcheck SC-경고는
#   이 패턴에 미매칭이라 count 에 안 잡힌다(스코프 = recurrence class).
# ─────────────────────────────────────────────────────────────────────────────
CTX_AVAIL_PATTERN='not allowed here|not available in .*context'
ctx_avail_violation_count() {
  local out
  out=$( ( cd "$REPO_ROOT" && timeout 60 actionlint "$@" ) 2>&1 || true )
  # grep -c 는 매칭 0 시 exit 1 → `|| true` 로 count 0 을 정상 반환.
  echo "$out" | grep -Ec "$CTX_AVAIL_PATTERN" || true
}

assert_eq() {
  local name="$1" expected="$2" actual="$3" desc="$4"
  if [ "$actual" = "$expected" ]; then
    echo "✓ PASS: $name (got $actual) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected $expected, got $actual"
    echo "  Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

assert_ge1() {
  local name="$1" actual="$2" desc="$3"
  if [ "$actual" -ge 1 ] 2>/dev/null; then
    echo "✓ PASS: $name (got count $actual >= 1 = 위반 검출) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected count >= 1 (위반 검출), got $actual — RED mutation-kill 보장 깨짐"
    echo "  Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# 케이스1 — GREEN: 정정된 전체 workflow(양 css-lint.yml 포함)에 context-availability 위반 0.
#   .github/workflows/*.yml + templates/github-workflows/*.yml 전체 actionlint 실행(exit code 무시).
#   판정 = context-availability 위반 count == 0 (shellcheck 부채는 무영향 — 스코프 밖).
# ═════════════════════════════════════════════════════════════════════════════
C1_COUNT=$(ctx_avail_violation_count .github/workflows/*.yml templates/github-workflows/*.yml)
assert_eq "C1-green-no-context-availability-violation" "0" "$C1_COUNT" \
  "정정 후 전체 workflow(.github + templates)에 context-availability 위반 0건 — job-level hashFiles 류 부재(shellcheck 부채는 스코프 밖, 무영향)"

# ═════════════════════════════════════════════════════════════════════════════
# 케이스2 — RED mutation: css-lint.yml 에 job-level `if: hashFiles(...)` 재삽입 후 actionlint
#   mutation 은 temp fixture 사본에만 — repo 실제 파일 무변경.
#   원본 read → temp copy → temp copy 에 mutation insert → actionlint temp file.
# ═════════════════════════════════════════════════════════════════════════════
# C2_COUNT 미리 초기화 — sentinel "NOT_RUN" = mutation 미실행(fixture-missing / sed-failed).
#   정상 mutation 실행 경로에서만 실제 count(0/>=1)로 덮어씀. anti-theater 대조는
#   NOT_RUN 이면 skip(대조 불가) — false "✓ PASS: ANTI-THEATER" 오보 차단(FIX-3).
C2_COUNT="NOT_RUN"

# Mutation 대상 파일 결정 — wrapper css-lint.yml 우선(표본 선택).
CSS_LINT_WRAPPER="$REPO_ROOT/.github/workflows/css-lint.yml"
CSS_LINT_TEMPLATE="$REPO_ROOT/templates/github-workflows/css-lint.yml"

# wrapper 의 css-lint.yml 이 있는지 확인.
if [ ! -f "$CSS_LINT_WRAPPER" ]; then
  note "[test-actionlint-workflows] .github/workflows/css-lint.yml 부재 — RED mutation fixture 생성 불가. FAIL."
  echo "✗ FAIL: C2-red-mutation-fixture-missing"
  echo "  Expected .github/workflows/css-lint.yml 존재, got 파일 부재"
  FAIL=$((FAIL+1))
  # C2_COUNT 는 NOT_RUN 유지 — mutation 미실행이므로 anti-theater 대조 skip.
else
  # temp dir 에 원본 복사 후 mutation 삽입.
  TEMP_FIXTURE=$(mktemp -d)
  cp "$CSS_LINT_WRAPPER" "$TEMP_FIXTURE/css-lint-mutated.yml"
  MUTATED_FILE="$TEMP_FIXTURE/css-lint-mutated.yml"

  # 원본에서 css-lint: job 찾기 — sed 로 그 아래에 job-level if 삽입.
  # 패턴: `  css-lint:` → 그 다음 줄에 `    if: hashFiles('**/*.css', '**/*.scss', '**/*.html') != ''` 삽입.
  sed -i '/^  css-lint:$/a\    if: hashFiles('"'"'**/*.css'"'"', '"'"'**/*.scss'"'"', '"'"'**/*.html'"'"') != '"'"''"'"'' "$MUTATED_FILE"

  # 검증: mutation 이 제대로 적용됐는지 grep 확인 (선택적, 디버깅용).
  if grep -q "if: hashFiles.*css-lint" "$MUTATED_FILE" 2>/dev/null || grep -q "hashFiles.*\*\*/\*\.css" "$MUTATED_FILE" 2>/dev/null; then
    # mutation 적용 확인됨 — actionlint 실행 후 context-availability 위반 count 측정 (RED 예상 >= 1).
    C2_COUNT=$(ctx_avail_violation_count "$MUTATED_FILE")
    assert_ge1 "C2-red-mutation-hashfiles-blocked" "$C2_COUNT" "job-level if: hashFiles(...) 재삽입 → actionlint context-availability 위반 검출(count >= 1 = 차단)"
  else
    note "[test-actionlint-workflows] mutation sed 적용 실패 또는 pattern 부매칭 — temp fixture 재점검"
    TEMP_FIXTURE_CONTENTS=$(cat "$MUTATED_FILE" 2>/dev/null | head -50)
    echo "Temp fixture head-50:"
    echo "$TEMP_FIXTURE_CONTENTS"
    echo "✗ FAIL: C2-red-mutation-sed-failed"
    echo "  Mutation insert 가 작동하지 않음 — sed pattern 재검토 필요"
    FAIL=$((FAIL+1))
    # C2_COUNT 는 NOT_RUN 유지 — mutation 미실행이므로 anti-theater 대조 skip.
  fi

  rm -rf "$TEMP_FIXTURE"
fi

# ── anti-theater discriminating 검증: C1 count(0) ≠ C2 count(>=1) ──
#   mutation 미실행(C2_COUNT=NOT_RUN: fixture-missing / sed-failed)이면 대조 불가 → skip (FIX-3).
#   이미 위에서 해당 실패는 FAIL++ 되었으므로 게이트 verdict 는 정확히 exit 1. 여기선 로그 정합만 보장:
#   NOT_RUN 을 C1 count(0)과 비교해 "✓ PASS: ANTI-THEATER" 오보를 내지 않는다.
if [ "$C2_COUNT" = "NOT_RUN" ]; then
  echo "⊘ SKIP: ANTI-THEATER 대조 불가 — RED mutation 미실행(fixture-missing / sed-failed). 대조 skip(위 mutation 실패가 이미 FAIL 처리)."
elif [ "$C1_COUNT" = "$C2_COUNT" ]; then
  echo "✗ FAIL: ANTI-THEATER — C1 count($C1_COUNT) 과 RED mutation count($C2_COUNT) 동일 = non-discriminating hollow gate"
  FAIL=$((FAIL+1))
else
  echo "✓ PASS: ANTI-THEATER discriminating — C1 context-availability count=$C1_COUNT ≠ RED mutation count=$C2_COUNT"
  PASS=$((PASS+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "Test Summary (CFP-2530 Phase 2 — actionlint workflow validation)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "SKIP: $SKIP"
echo "TOTAL ASSERT: $((PASS + FAIL))"
echo ""
echo "Discriminating evidence (anti-theater) — 판정 = context-availability 위반 count (shellcheck 부채 스코프 밖):"
echo "  C1 GREEN(정정 후 전체 workflow) context-availability count=$C1_COUNT (0=클래스 청결)"
echo "  C2 RED mutation(job-level if: hashFiles 재삽입) context-availability count=$C2_COUNT (>=1=위반 도입 검출)"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (SKIP=$SKIP 은 명시적 graceful skip — silent pass 아님)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
