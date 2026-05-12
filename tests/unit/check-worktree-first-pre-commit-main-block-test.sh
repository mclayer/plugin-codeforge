#!/usr/bin/env bash
# CFP-426 / CFP-428 / ADR-040 Amendment 3 — unit test for check-worktree-first-pre-commit-main-block.sh (actual logic)
# Tests:
#   TC-1: BYPASS_WORKTREE_FIRST=1 env short-circuit
#   TC-2: normal run = actual logic (sample 존재 + executable bit + install 가이드, exit 0 + OK log)
#   TC-3: POSIX strict mode (shebang + set -euo pipefail) presence
#   TC-4: sample 부재 = WARN exit 0 (warning tier)
#   TC-5: executable bit 부재 = WARN exit 0 (warning tier)
#   TC-6: git mode 100755 (executable bit, F-001 closing — Story 2 TC-10 정합)
set -euo pipefail
cd "$(dirname "$0")/../.."
REPO_ROOT="$(pwd)"

SCRIPT_REL="scripts/check-worktree-first-pre-commit-main-block.sh"
SAMPLE_REL="templates/.git-hooks/pre-commit-main-block.sample"
SCRIPT="$REPO_ROOT/$SCRIPT_REL"
SAMPLE="$REPO_ROOT/$SAMPLE_REL"
FAIL=0

# OR-short-circuit pattern (FIX iter 2, F-001 P1): set -e race 회피.

echo "=== TC-1: BYPASS_WORKTREE_FIRST=1 short-circuit ==="
STATUS=0
OUT=$(BYPASS_WORKTREE_FIRST=1 bash "$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "BYPASS_WORKTREE_FIRST=1 — skip"; then
    echo "  PASS — exit 0 + skip log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-2: normal run = actual logic (sample 존재 + executable + OK log) ==="
STATUS=0
OUT=$(bash "$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "\[worktree-first-pre-commit-main-block\] OK"; then
    echo "  PASS — exit 0 + actual logic OK log"
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

echo "=== TC-4: sample 부재 = WARN exit 0 (warning tier) ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts"
cp "$SCRIPT" "$TMPDIR/scripts/"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
STATUS=0
OUT=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*not found"; then
    echo "  PASS — exit 0 + WARN log (sample 부재)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-5: executable bit 부재 = WARN exit 0 ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts" "$TMPDIR/templates/.git-hooks"
cp "$SCRIPT" "$TMPDIR/scripts/"
cp "$SAMPLE" "$TMPDIR/$SAMPLE_REL"
chmod -x "$TMPDIR/$SAMPLE_REL"
# Platform check: Windows NTFS 는 chmod -x 가 무의미 (executable bit 영구 유지)
if [ -x "$TMPDIR/$SAMPLE_REL" ]; then
    echo "  SKIP — Windows NTFS 환경 (chmod -x 비효과). lint script 의 [[ -x ]] check 는 POSIX filesystem 한정 의미."
else
    cd "$TMPDIR" && git init -q 2>&1 >/dev/null
    STATUS=0
    OUT=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
    cd "$REPO_ROOT"
    if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*not executable"; then
        echo "  PASS — exit 0 + WARN log (executable bit 부재)"
    else
        echo "  FAIL — exit=$STATUS output=$OUT"
        FAIL=$((FAIL + 1))
    fi
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-6: git mode 100755 (executable bit, F-001 closing) ==="
ACTUAL_MODE=$(cd "$REPO_ROOT" && git ls-files -s "$SCRIPT_REL" 2>/dev/null | awk '{print $1}')
if [ "$ACTUAL_MODE" = "100755" ]; then
    echo "  PASS — git mode = 100755"
else
    echo "  FAIL — git mode = $ACTUAL_MODE (expected 100755)"
    FAIL=$((FAIL + 1))
fi

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "FAIL count: $FAIL"
    exit 1
fi
echo ""
echo "ALL PASS (6/6)"
exit 0
