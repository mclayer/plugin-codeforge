#!/usr/bin/env bash
# test_bootstrap_labels_count.sh
# CFP-492 — check-bootstrap-labels-count.sh smoke test (3 case)
#
# Case 1 (OK): 현재 script state → exit 0 PASS
# Case 2 (drift): bootstrap-labels.sh 임시 사본에 stdout only extra echo 추가 (counter 증가 없음) → exit 1
# Case 3 (--help): check-bootstrap-labels-count.sh --help → exit 0
#
# Usage:
#   bash tests/scripts/test_bootstrap_labels_count.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../..")"
LINT_SCRIPT="$REPO_ROOT/scripts/check-bootstrap-labels-count.sh"
BOOTSTRAP_SCRIPT="$REPO_ROOT/scripts/bootstrap-labels.sh"

# Color output (TERM-aware)
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  NC='\033[0m'
else
  RED=''
  GREEN=''
  NC=''
fi

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_true() {
  local desc="$1"
  local condition="$2"

  TESTS_RUN=$((TESTS_RUN + 1))
  if eval "$condition"; then
    echo -e "${GREEN}PASS${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}FAIL${NC} $desc"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

echo "==================================================================="
echo "CFP-492 — check-bootstrap-labels-count.sh smoke test (3 case)"
echo "Lint:      $LINT_SCRIPT"
echo "Bootstrap: $BOOTSTRAP_SCRIPT"
echo "==================================================================="
echo ""

# Pre-flight
if [[ ! -f "$LINT_SCRIPT" ]]; then
  echo -e "${RED}FATAL${NC} lint script 부재: $LINT_SCRIPT"
  exit 2
fi
if [[ ! -f "$BOOTSTRAP_SCRIPT" ]]; then
  echo -e "${RED}FATAL${NC} bootstrap script 부재: $BOOTSTRAP_SCRIPT"
  exit 2
fi

echo "[Case 1/3] OK case — 현재 state dry-run line count == invocations"
echo "-------------------------------------------------------------------"

# Case 1: lint script 실행 → exit 0 (PASS)
CASE1_EXIT=0
bash "$LINT_SCRIPT" >/dev/null 2>&1 || CASE1_EXIT=$?

assert_true "Case 1: lint script exit 0 (PASS)" \
  "[ $CASE1_EXIT -eq 0 ]"

echo ""
echo "[Case 2/3] Drift simulation — stdout extra line (counter 미증가) → exit 1"
echo "-------------------------------------------------------------------"

# Case 2: bootstrap-labels.sh 임시 사본 생성 후 create_label 호출 없이 stdout extra echo 삽입.
# 방식: sed 로 스크립트 마지막 DRY_RUN self-check 앞에 "echo extra_drift_line" 삽입.
TMP_BOOTSTRAP="$(mktemp -t bootstrap-drift.XXXXXX.sh)"
TMP_LINT_DIR="$(mktemp -d -t bootstrap-lint-dir.XXXXXX)"
trap 'rm -f "$TMP_BOOTSTRAP"; rm -rf "$TMP_LINT_DIR"' EXIT

# 원본 복사 후 DRY_RUN self-check 블록 앞에 extra stdout echo 추가
# (LABEL_COUNT 증가 없이 stdout 1 line 추가 → drift)
cp "$BOOTSTRAP_SCRIPT" "$TMP_BOOTSTRAP"
# 마지막 self-check 주석 앞에 extra echo 삽입
echo "" >> "$TMP_BOOTSTRAP"
cat >> "$TMP_BOOTSTRAP" <<'PATCH'
# CFP-492 test drift injection: LABEL_COUNT 증가 없이 stdout 1 line 추가
if [ $DRY_RUN -eq 1 ]; then
    echo "DRIFT_INJECTION_EXTRA_LINE"
fi
PATCH

# 임시 lint wrapper: BOOTSTRAP_SCRIPT 를 TMP_BOOTSTRAP 으로 교체해서 실행
# check-bootstrap-labels-count.sh 는 내부에서 scripts/bootstrap-labels.sh 를 참조
# → 임시 디렉터리에 symlink 로 교체
mkdir -p "$TMP_LINT_DIR/scripts"
cp "$LINT_SCRIPT" "$TMP_LINT_DIR/scripts/check-bootstrap-labels-count.sh"
cp "$TMP_BOOTSTRAP" "$TMP_LINT_DIR/scripts/bootstrap-labels.sh"

CASE2_EXIT=0
bash "$TMP_LINT_DIR/scripts/check-bootstrap-labels-count.sh" >/dev/null 2>&1 || CASE2_EXIT=$?

assert_true "Case 2: drift simulation → exit 1 (FAIL detected)" \
  "[ $CASE2_EXIT -eq 1 ]"

echo ""
echo "[Case 3/3] --help → exit 0"
echo "-------------------------------------------------------------------"

CASE3_EXIT=0
bash "$LINT_SCRIPT" --help >/dev/null 2>&1 || CASE3_EXIT=$?

assert_true "Case 3: --help → exit 0" \
  "[ $CASE3_EXIT -eq 0 ]"

echo ""
echo "==================================================================="
echo "Test summary: $TESTS_PASSED / $TESTS_RUN passed, $TESTS_FAILED failed"
echo "==================================================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi

exit 0
