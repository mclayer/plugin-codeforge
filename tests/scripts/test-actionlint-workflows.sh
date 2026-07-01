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
# ── anti-theater (비협상) ────────────────────────────────────────────────────
#  - 정정 후(GREEN): 전체 workflow 이 actionlint 를 통과(exit 0). 하나라도 violation 있으면 FAIL.
#  - 정정 전 (RED mutation): css-lint.yml 의 job-level `if: hashFiles(...)` 를 재삽입해
#    actionlint 가 context-availability 위반을 검출(exit != 0) 하는지 확인. mutation 은 temp fixture
#    사본에만 — 실제 repo 파일은 오염시키지 않음.
#  - GREEN ≠ RED mutation-kill: 양 regime 의 exit code 가 다르면 test pass (discriminating).
#    둘이 같으면(둘 다 0 또는 둘 다 non-0) hollow → test FAIL.
#  - RED 판정: exit != 0 (primary). regex 매칭 optional secondary (diagnostics).
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

assert_nonzero() {
  local name="$1" actual="$2" desc="$3"
  if [ "$actual" != "0" ]; then
    echo "✓ PASS: $name (got non-zero exit $actual = 차단) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected non-zero (차단), got 0 (통과) — RED 보장 깨짐"
    echo "  Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# 케이스1 — GREEN: 정정된 전체 workflow(양 css-lint.yml 포함)이 actionlint 통과
#   .github/workflows/*.yml + templates/github-workflows/*.yml
# ═════════════════════════════════════════════════════════════════════════════
WORKFLOWS_GITHUB="$REPO_ROOT/.github/workflows/*.yml"
WORKFLOWS_TEMPLATE="$REPO_ROOT/templates/github-workflows/*.yml"
EC_GREEN=0
( cd "$REPO_ROOT" && timeout 60 actionlint .github/workflows/*.yml templates/github-workflows/*.yml >/dev/null 2>&1 ) || EC_GREEN=$?
assert_eq "C1-green-all-workflows-valid" "0" "$EC_GREEN" "정정 후 전체 workflow 이 actionlint 통과(exit 0) — schema valid"

# ═════════════════════════════════════════════════════════════════════════════
# 케이스2 — RED mutation: css-lint.yml 에 job-level `if: hashFiles(...)` 재삽입 후 actionlint
#   mutation 은 temp fixture 사본에만 — repo 실제 파일 무변경.
#   원본 read → temp copy → temp copy 에 mutation insert → actionlint temp file.
# ═════════════════════════════════════════════════════════════════════════════
# EC_RED 미리 초기화 (mutation 실패 시 참조).
EC_RED=0

# Mutation 대상 파일 결정 — wrapper css-lint.yml 우선(표본 선택).
CSS_LINT_WRAPPER="$REPO_ROOT/.github/workflows/css-lint.yml"
CSS_LINT_TEMPLATE="$REPO_ROOT/templates/github-workflows/css-lint.yml"

# wrapper 의 css-lint.yml 이 있는지 확인.
if [ ! -f "$CSS_LINT_WRAPPER" ]; then
  note "[test-actionlint-workflows] .github/workflows/css-lint.yml 부재 — RED mutation fixture 생성 불가. FAIL."
  echo "✗ FAIL: C2-red-mutation-fixture-missing"
  echo "  Expected .github/workflows/css-lint.yml 존재, got 파일 부재"
  FAIL=$((FAIL+1))
  EC_RED=999  # mutation 실패하면 구분 가능한 high value
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
    # mutation 적용 확인됨 — actionlint 실행 (RED 예상).
    EC_RED=0
    ( cd "$REPO_ROOT" && timeout 60 actionlint "$MUTATED_FILE" >/dev/null 2>&1 ) || EC_RED=$?
    assert_nonzero "C2-red-mutation-hashfiles-blocked" "$EC_RED" "job-level if: hashFiles(...) 재삽입 → actionlint context-availability 위반 검출(exit !=0 = 차단)"
  else
    note "[test-actionlint-workflows] mutation sed 적용 실패 또는 pattern 부매칭 — temp fixture 재점검"
    TEMP_FIXTURE_CONTENTS=$(cat "$MUTATED_FILE" 2>/dev/null | head -50)
    echo "Temp fixture head-50:"
    echo "$TEMP_FIXTURE_CONTENTS"
    echo "✗ FAIL: C2-red-mutation-sed-failed"
    echo "  Mutation insert 가 작동하지 않음 — sed pattern 재검토 필요"
    FAIL=$((FAIL+1))
    EC_RED=0
  fi

  rm -rf "$TEMP_FIXTURE"
fi

# ── anti-theater discriminating 검증: GREEN(0) ≠ RED(non-0) ──
if [ "$EC_GREEN" = "$EC_RED" ]; then
  echo "✗ FAIL: ANTI-THEATER — GREEN(exit=$EC_GREEN) 과 RED mutation(exit=$EC_RED) 결과 동일 = non-discriminating hollow gate"
  FAIL=$((FAIL+1))
else
  echo "✓ PASS: ANTI-THEATER discriminating — GREEN(exit=$EC_GREEN) ≠ RED mutation(exit=$EC_RED)"
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
echo "Discriminating evidence (anti-theater):"
echo "  GREEN(정정 후 전체 workflow) exit=$EC_GREEN (0=valid)"
echo "  RED mutation(job-level if: hashFiles 재삽입) exit=$EC_RED (non-zero=context-availability 위반 검출)"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (SKIP=$SKIP 은 명시적 graceful skip — silent pass 아님)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
