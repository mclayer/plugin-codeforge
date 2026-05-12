#!/usr/bin/env bash
# test_check_codeforge_prereq.sh
# CFP-500 Phase 2 — SessionStart prereq-check hook bash smoke test
#
# AC-4 (5 runtime assertion): stdout non-empty + 4 keyword grep
# AC-11 (정적 grep 검증): single-quoted heredoc / set -euo pipefail / filesystem touch 0 / network call 0
#
# Usage:
#   bash tests/scripts/test_check_codeforge_prereq.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../..")
HELPER="$REPO_ROOT/scripts/check-codeforge-prereq.sh"

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
echo "CFP-500 Phase 2 — SessionStart prereq-check helper smoke test"
echo "Target: $HELPER"
echo "==================================================================="
echo ""

# Pre-flight — helper file 존재 + 실행 권한 (Windows Git Bash 에서는 mode 비신뢰)
if [[ ! -f "$HELPER" ]]; then
  echo -e "${RED}FATAL${NC} helper script 부재: $HELPER"
  exit 2
fi

echo "[1/2] 정적 grep 검증 (AC-11)"
echo "-------------------------------------------------------------------"

# AC-11 (a) shebang + set -euo pipefail
assert_true "(a) shebang #!/usr/bin/env bash 보유" \
  "grep -q '^#!/usr/bin/env bash' '$HELPER'"
assert_true "(a) set -euo pipefail 보유" \
  "grep -q 'set -euo pipefail' '$HELPER'"

# AC-11 (b) single-quoted heredoc
assert_true "(b) single-quoted heredoc (<<'EOF') — env interpolation 차단" \
  "grep -q \"<<'EOF'\" '$HELPER'"

# AC-11 (c)(d) — comment line (^#) 제거 후 정적 검증 (heredoc 본문 + script body 만 검사)
# helper 본문의 instruction 텍스트와 주석은 grep 대상에서 제외.
HELPER_BODY="$(grep -v '^[[:space:]]*#' "$HELPER" | sed -n '/<<.EOF.$/,/^EOF$/!p' || true)"
# Note: heredoc 본문은 instruction text — destructive command 검사 대상 외 (single-quoted heredoc 으로
#       env interpolation 차단된 정적 출력). 위 sed 가 heredoc 본문을 제거하고 script logic 만 남김.

assert_true "(c) filesystem touch 0 — no '>>' append redirect (script logic)" \
  "! echo \"\$HELPER_BODY\" | grep -qE '>>'"
assert_true "(c) filesystem touch 0 — no mkdir command (script logic)" \
  "! echo \"\$HELPER_BODY\" | grep -qE '(^|[^a-zA-Z_])mkdir([^a-zA-Z_]|$)'"
assert_true "(c) filesystem touch 0 — no rm command (script logic)" \
  "! echo \"\$HELPER_BODY\" | grep -qE '(^|[^a-zA-Z_])rm([^a-zA-Z_]|$)'"
assert_true "(c) filesystem touch 0 — no mv command (script logic)" \
  "! echo \"\$HELPER_BODY\" | grep -qE '(^|[^a-zA-Z_])mv([^a-zA-Z_]|$)'"

# AC-11 (d) network call 0
assert_true "(d) network call 0 — no curl (script logic)" \
  "! echo \"\$HELPER_BODY\" | grep -qE '(^|[^a-zA-Z_])curl([^a-zA-Z_]|$)'"
assert_true "(d) network call 0 — no wget (script logic)" \
  "! echo \"\$HELPER_BODY\" | grep -qE '(^|[^a-zA-Z_])wget([^a-zA-Z_]|$)'"
assert_true "(d) network call 0 — no 'gh api' call (script logic)" \
  "! echo \"\$HELPER_BODY\" | grep -qE 'gh[[:space:]]+api'"

echo ""
echo "[2/2] runtime assertion (AC-4)"
echo "-------------------------------------------------------------------"

# Helper 실행 (subshell, side-effect isolation)
OUTPUT="$(bash "$HELPER" 2>&1)"
EXIT_CODE=$?

# AC-4 (1) stdout non-empty
assert_true "(1) stdout non-empty" \
  "[ -n \"\$OUTPUT\" ]"

# AC-4 (2) 'ToolSearch' keyword
assert_true "(2) 'ToolSearch' keyword 존재" \
  "echo \"\$OUTPUT\" | grep -q 'ToolSearch'"

# AC-4 (3) 'select:TodoWrite' keyword
assert_true "(3) 'select:TodoWrite' keyword 존재" \
  "echo \"\$OUTPUT\" | grep -q 'select:TodoWrite'"

# AC-4 (4) 'ADR-038' reference
assert_true "(4) 'ADR-038' reference 존재" \
  "echo \"\$OUTPUT\" | grep -q 'ADR-038'"

# AC-4 (5) 'first tool actions' prompt
assert_true "(5) 'first tool actions' prompt 존재" \
  "echo \"\$OUTPUT\" | grep -q 'first tool actions'"

# Bonus — exit code 0
assert_true "(*) exit code = 0" \
  "[ $EXIT_CODE -eq 0 ]"

echo ""
echo "==================================================================="
echo "Test summary: $TESTS_PASSED / $TESTS_RUN passed, $TESTS_FAILED failed"
echo "==================================================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi

exit 0
