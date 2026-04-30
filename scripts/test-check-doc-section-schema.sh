#!/usr/bin/env bash
# CFP-46 PR-G — Test harness for check-doc-section-schema.sh
#
# 3 fixture cases:
#   passing.md         — §7.4 5 항목 + CONDITIONAL N/A 사유 (10자+) 충족 → exit 0
#   failing-no-na.md   — Clock sync CONDITIONAL 본문/N/A 모두 부재 → exit 1
#   failing-empty-na.md — Clock sync CONDITIONAL 다음 'N/A' 만 (사유 부재, 10자 minimum 미충족) → exit 1
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
FIXTURE_DIR="$REPO_ROOT/scripts/test-fixtures/cfp-46-conditional-na"

PASS=0
FAIL=0

run_fixture_test() {
  local name="$1"
  local fixture_file="$2"
  local expected_exit="$3"

  local tmp
  tmp=$(mktemp -d)

  # Mirror minimum repo structure to tmp
  mkdir -p "$tmp/docs/change-plans" "$tmp/scripts"
  cp "$LINT_SCRIPT" "$tmp/scripts/"
  cp "$FIXTURE_DIR/$fixture_file" "$tmp/docs/change-plans/"

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

# T1: passing fixture — §7.4 5 항목 + CONDITIONAL N/A 사유 (10자+) 모두 충족
run_fixture_test "T1 passing.md (§7.4 + CONDITIONAL N/A 충족)" "passing.md" 0

# T2: failing — Clock sync CONDITIONAL 본문/N/A 모두 부재
run_fixture_test "T2 failing-no-na.md (CONDITIONAL 본문/N/A 부재)" "failing-no-na.md" 1

# T3: failing — N/A 만 (사유 부재, 10자 minimum 미충족)
run_fixture_test "T3 failing-empty-na.md (N/A 사유 부재, 10자 minimum 미충족)" "failing-empty-na.md" 1

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
