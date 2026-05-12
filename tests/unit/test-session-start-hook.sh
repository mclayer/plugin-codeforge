#!/usr/bin/env bash
# test-session-start-hook.sh
# CFP-475 Phase 2 — SessionStart hook unit test
#
# TestContractArch §8.1-T2 (Unix bash polyglot unit test) + §8.1-T6 (BYPASS_CODEFORGE_PREREQ short-circuit)
# + §3.4.0 결정 3 (control char grep verbatim assertion)
#
# Test scenarios:
#   (a) hooks/session-start exit 0
#   (b) stdout 안 `ToolSearch("select:TodoWrite")` substring 발화
#   (c) T6 control char grep verbatim — no control chars (§3.4.0 결정 3 + SecurityArch §7.S §7.6 T6 mitigation)
#   (d) BYPASS_CODEFORGE_PREREQ=1 → stdout empty + stderr audit echo + exit 0 (AC-8 + E-8)
#   (e) BYPASS_PREREQ_CHECK=1 (deprecated) → stdout empty + stderr deprecation warning + exit 0 (E-6)
#   (f) shebang #!/usr/bin/env bash verify
#   (g) set -euo pipefail verify
#
# Usage:
#   bash tests/unit/test-session-start-hook.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../..")
HOOK="$REPO_ROOT/hooks/session-start"

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
echo "CFP-475 Phase 2 — SessionStart hook unit test"
echo "Target: $HOOK"
echo "==================================================================="
echo ""

# Pre-flight — hook file 존재 + 실행 권한
if [[ ! -f "$HOOK" ]]; then
  echo -e "${RED}FATAL${NC} hook script 부재: $HOOK"
  exit 2
fi

echo "[1/3] 정적 검증 (shebang + set -euo pipefail)"
echo "-------------------------------------------------------------------"

# (f) shebang #!/usr/bin/env bash
assert_true "(f) shebang #!/usr/bin/env bash 보유" \
  "grep -q '^#!/usr/bin/env bash' '$HOOK'"

# (g) set -euo pipefail
assert_true "(g) set -euo pipefail 보유" \
  "grep -q 'set -euo pipefail' '$HOOK'"

echo ""
echo "[2/3] Runtime assertion — normal case (no BYPASS env)"
echo "-------------------------------------------------------------------"

# (a) hook exit 0
HOOK_OUTPUT="$(bash "$HOOK" 2>&1)"
HOOK_EXIT=$?
assert_true "(a) hook exit 0" \
  "[ $HOOK_EXIT -eq 0 ]"

# (b) stdout 안 ToolSearch("select:TodoWrite) substring
assert_true "(b) stdout 안 ToolSearch(\"select:TodoWrite) substring 존재" \
  "echo \"\$HOOK_OUTPUT\" | grep -q 'ToolSearch.*select:TodoWrite'"

# (c) T6 control char grep verbatim (§3.4.0 결정 3 + SecurityArch §7.S §7.6 T6 mitigation)
# Control char: \x00-\x08 \x0b-\x1f \x7f (탭 \x09, LF \x0a 제외)
HOOK_STDOUT_BIN="/tmp/hook-stdout-$$.bin"
bash "$HOOK" > "$HOOK_STDOUT_BIN" 2>/dev/null || true
if grep -P '[\x00-\x08\x0b-\x1f\x7f]' "$HOOK_STDOUT_BIN" >/dev/null 2>&1; then
  echo -e "${RED}FAIL${NC} (c) T6: hook stdout contains control char (§3.4.0 결정 3 regression)"
  TESTS_FAILED=$((TESTS_FAILED + 1))
  TESTS_RUN=$((TESTS_RUN + 1))
  rm -f "$HOOK_STDOUT_BIN"
else
  echo -e "${GREEN}PASS${NC} (c) T6 control char grep — no control chars (SecurityArch §7.S §7.6 T6 mitigation)"
  TESTS_PASSED=$((TESTS_PASSED + 1))
  TESTS_RUN=$((TESTS_RUN + 1))
  rm -f "$HOOK_STDOUT_BIN"
fi

echo ""
echo "[3/3] Bypass scenario — BYPASS_CODEFORGE_PREREQ + BYPASS_PREREQ_CHECK"
echo "-------------------------------------------------------------------"

# (d) BYPASS_CODEFORGE_PREREQ=1 → stdout empty + stderr audit echo + exit 0 (AC-8 + E-8)
BYPASS_OUTPUT="$(BYPASS_CODEFORGE_PREREQ=1 bash "$HOOK" 2>&1)"
BYPASS_EXIT=$?
BYPASS_STDOUT="$(BYPASS_CODEFORGE_PREREQ=1 bash "$HOOK" 2>/dev/null)"
BYPASS_STDERR="$(BYPASS_CODEFORGE_PREREQ=1 bash "$HOOK" 2>&1 >/dev/null)"

assert_true "(d) BYPASS_CODEFORGE_PREREQ=1 → exit 0" \
  "[ $BYPASS_EXIT -eq 0 ]"
assert_true "(d) BYPASS_CODEFORGE_PREREQ=1 → stdout empty (0 bytes, harness injection 0)" \
  "[ -z \"\$BYPASS_STDOUT\" ]"
assert_true "(d) BYPASS_CODEFORGE_PREREQ=1 → stderr audit echo" \
  "echo \"\$BYPASS_STDERR\" | grep -q 'BYPASS_CODEFORGE_PREREQ=1'"

# (e) BYPASS_PREREQ_CHECK=1 (deprecated) → stdout empty + stderr deprecation warning + exit 0 (E-6)
DEPRECATED_OUTPUT="$(BYPASS_PREREQ_CHECK=1 bash "$HOOK" 2>&1)"
DEPRECATED_EXIT=$?
DEPRECATED_STDOUT="$(BYPASS_PREREQ_CHECK=1 bash "$HOOK" 2>/dev/null)"
DEPRECATED_STDERR="$(BYPASS_PREREQ_CHECK=1 bash "$HOOK" 2>&1 >/dev/null)"

assert_true "(e) BYPASS_PREREQ_CHECK=1 (deprecated) → exit 0" \
  "[ $DEPRECATED_EXIT -eq 0 ]"
assert_true "(e) BYPASS_PREREQ_CHECK=1 → stdout empty (0 bytes)" \
  "[ -z \"\$DEPRECATED_STDOUT\" ]"
assert_true "(e) BYPASS_PREREQ_CHECK=1 → stderr deprecation warning" \
  "echo \"\$DEPRECATED_STDERR\" | grep -q 'deprecated'"
assert_true "(e) BYPASS_PREREQ_CHECK=1 → stderr mentions BYPASS_PREREQ_CHECK" \
  "echo \"\$DEPRECATED_STDERR\" | grep -q 'BYPASS_PREREQ_CHECK'"

echo ""
echo "==================================================================="
echo "Test summary: $TESTS_PASSED / $TESTS_RUN passed, $TESTS_FAILED failed"
echo "==================================================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi

exit 0
