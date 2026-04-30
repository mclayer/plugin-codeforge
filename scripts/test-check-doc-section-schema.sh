#!/usr/bin/env bash
# CFP-46 PR-G — Test harness for check-doc-section-schema.sh
# CFP-47 PR-G — §8.5 applicability fixtures 추가 (4 신규 case)
#
# CFP-46 4 fixture cases (passing + 3 failure tiers):
#   passing.md           — §7.4 5 항목 + CONDITIONAL N/A 사유 (10자+) 충족 → exit 0
#   failing-no-na.md     — Tier 1: CONDITIONAL 본문/N/A 모두 부재 → exit 1
#   failing-empty-na.md  — Tier 2: CONDITIONAL 다음 'N/A' 만 (사유 부재) → exit 1
#   failing-short-na.md  — Tier 3: 'N/A — TBD' (사유 10자 minimum 미충족) → exit 1
#
# CFP-47 4 fixture cases (passing 2 + failing 2):
#   passing-y-applies.md      — applicability 1+ Y + §8.5.1 본문 → exit 0
#   passing-n-substantive.md  — applicability 4 N + §8.5.4 substantive N/A (30자+) → exit 0
#   failing-y-no-section.md   — 1+ Y but §8.5.1 헤딩 부재 → exit 1
#   failing-n-vague.md        — 4 N but §8.5.4 vague N/A (30자 minimum 미충족) → exit 1
#
# 각 case 마다:
#   1. tmp dir 생성 + scripts/ + docs/change-plans/<fixture>.md mirror
#   2. cwd=tmp 로 lint 실행
#   3. expected exit code 검증
#
# Usage: bash scripts/test-check-doc-section-schema.sh
# Exit: 0 if all pass, 1 if any fail.

set -euo pipefail
cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
LINT_SCRIPT="$REPO_ROOT/scripts/check-doc-section-schema.sh"
FIXTURE_DIR_46="$REPO_ROOT/scripts/test-fixtures/cfp-46-conditional-na"
FIXTURE_DIR_47="$REPO_ROOT/scripts/test-fixtures/cfp-47-section-8-5"

PASS=0
FAIL=0

run_fixture_test() {
  local name="$1"
  local fixture_path="$2"
  local expected_exit="$3"

  local tmp
  tmp=$(mktemp -d)

  # Mirror minimum repo structure to tmp
  mkdir -p "$tmp/docs/change-plans" "$tmp/scripts"
  cp "$LINT_SCRIPT" "$tmp/scripts/"
  cp "$fixture_path" "$tmp/docs/change-plans/"

  # Run lint with cwd at tmp (PYTHONIOENCODING=utf-8 required on Windows/cp949 locales)
  local actual_exit=0
  ( cd "$tmp" && PYTHONIOENCODING=utf-8 bash scripts/check-doc-section-schema.sh ) >/dev/null 2>&1 || actual_exit=$?

  if [ "$actual_exit" = "$expected_exit" ]; then
    echo "✓ $name (exit $actual_exit)"
    PASS=$((PASS+1))
  else
    echo "✗ $name (expected exit $expected_exit, got $actual_exit)"
    # Re-run with output for debugging
    echo "  --- lint output ---"
    ( cd "$tmp" && PYTHONIOENCODING=utf-8 bash scripts/check-doc-section-schema.sh ) 2>&1 | sed 's/^/  /'
    echo "  --- end lint output ---"
    FAIL=$((FAIL+1))
  fi

  rm -rf "$tmp"
}

# CFP-46 fixtures
# T1: passing fixture — §7.4 5 항목 + CONDITIONAL N/A 사유 (10자+) 모두 충족
run_fixture_test "T1 passing.md (§7.4 + CONDITIONAL N/A 충족)" "$FIXTURE_DIR_46/passing.md" 0

# T2: Tier 1 — Clock sync CONDITIONAL 본문/N/A 모두 부재
run_fixture_test "T2 failing-no-na.md (Tier 1: CONDITIONAL 본문/N/A 부재)" "$FIXTURE_DIR_46/failing-no-na.md" 1

# T3: Tier 2 — N/A 만 (사유 부재)
run_fixture_test "T3 failing-empty-na.md (Tier 2: N/A 사유 부재)" "$FIXTURE_DIR_46/failing-empty-na.md" 1

# T4: Tier 3 — 'N/A — TBD' (사유 10자 minimum 미충족, NA_JUSTIFY_RE 검증)
run_fixture_test "T4 failing-short-na.md (Tier 3: N/A 사유 10자 minimum 미충족)" "$FIXTURE_DIR_46/failing-short-na.md" 1

# CFP-47 §8.5 applicability fixtures
# T5: passing fixture — 1+ Y + §8.5.1 본문 충족
run_fixture_test "T5 passing-y-applies.md (1+ Y + §8.5.1 본문)" "$FIXTURE_DIR_47/passing-y-applies.md" 0

# T6: passing fixture — 4 N + §8.5.4 substantive N/A (30자+) 충족
run_fixture_test "T6 passing-n-substantive.md (4 N + substantive N/A)" "$FIXTURE_DIR_47/passing-n-substantive.md" 0

# T7: failing fixture — 1+ Y but §8.5.1 헤딩 부재
run_fixture_test "T7 failing-y-no-section.md (1+ Y but §8.5.1 부재)" "$FIXTURE_DIR_47/failing-y-no-section.md" 1

# T8: failing fixture — 4 N but §8.5.4 vague N/A (30자 minimum 미충족)
run_fixture_test "T8 failing-n-vague.md (4 N but vague N/A)" "$FIXTURE_DIR_47/failing-n-vague.md" 1

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
