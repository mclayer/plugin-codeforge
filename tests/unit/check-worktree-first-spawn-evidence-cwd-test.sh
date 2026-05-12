#!/usr/bin/env bash
# CFP-426 / ADR-040 Amendment 3 — unit test for check-worktree-first-spawn-evidence-cwd.sh
# Tests:
#   TC-1: BYPASS_WORKTREE_FIRST=1 env short-circuit
#   TC-2: normal run = skeleton mode (exit 0)
#   TC-3: POSIX strict mode (shebang + set -euo pipefail) presence
set -euo pipefail
cd "$(dirname "$0")/../.."

SCRIPT="scripts/check-worktree-first-spawn-evidence-cwd.sh"
FAIL=0

echo "=== TC-1: BYPASS_WORKTREE_FIRST=1 short-circuit ==="
OUT=$(BYPASS_WORKTREE_FIRST=1 bash "$SCRIPT" 2>&1)
STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "BYPASS_WORKTREE_FIRST=1 — skip"; then
    echo "  PASS — exit 0 + skip log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-2: normal run = skeleton mode (exit 0) ==="
OUT=$(bash "$SCRIPT" 2>&1)
STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "SKELETON"; then
    echo "  PASS — exit 0 + skeleton log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-3: POSIX strict mode (shebang + set -euo pipefail) ==="
SHEBANG=$(head -n 1 "$SCRIPT")
if [ "$SHEBANG" = "#!/usr/bin/env bash" ] && grep -q "^set -euo pipefail" "$SCRIPT"; then
    echo "  PASS — shebang + strict mode"
else
    echo "  FAIL — shebang=$SHEBANG"
    FAIL=$((FAIL + 1))
fi

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "FAIL count: $FAIL"
    exit 1
fi
echo ""
echo "ALL PASS (3/3)"
exit 0
