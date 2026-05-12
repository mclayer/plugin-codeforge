#!/usr/bin/env bash
# CFP-427 — unit test for scripts/check-session-start-hook-presence.sh
# Tests:
#   TC-1: BYPASS_WORKTREE_FIRST=1 env short-circuit (exit 0 + skip log)
#   TC-2: normal run = hook wired (exit 0 + OK log)
#   TC-3: settings.json 부재 (exit 0 + WARN log) — 폐쇄루프 안전망
#   TC-4: hook 미wired (exit 0 + WARN log) — 폐쇄루프 self-detect
#   TC-5: POSIX strict mode (shebang + set -euo pipefail) presence
set -euo pipefail
cd "$(dirname "$0")/../.."

SCRIPT="scripts/check-session-start-hook-presence.sh"
FAIL=0

# OR-short-circuit pattern (Story 1 FIX iter 2 F-001 verbatim mirror): set -e race 회피.
# 직전 STATUS=0 명시 + command 실패 시 || branch 가 STATUS=$? 캡처 — set -e 가 abort 하기 전에.

echo "=== TC-1: BYPASS_WORKTREE_FIRST=1 short-circuit ==="
STATUS=0
OUT=$(BYPASS_WORKTREE_FIRST=1 bash "$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "BYPASS_WORKTREE_FIRST=1 — skip"; then
    echo "  PASS — exit 0 + skip log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-2: normal run = hook wired (exit 0 + OK log) ==="
STATUS=0
OUT=$(bash "$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "OK"; then
    echo "  PASS — exit 0 + OK log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-3: settings.json 부재 → WARN exit 0 ==="
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/.claude"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
STATUS=0
# repo root override = TMPDIR (no settings.json)
OUT=$(bash "$OLDPWD/$SCRIPT" 2>&1) || STATUS=$?
cd "$OLDPWD"
rm -rf "$TMPDIR"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*not found"; then
    echo "  PASS — exit 0 + WARN log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-4: hook 미wired → WARN exit 0 (폐쇄루프 self-detect) ==="
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/.claude"
echo '{"hooks":{"SessionStart":[]}}' > "$TMPDIR/.claude/settings.json"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
STATUS=0
OUT=$(bash "$OLDPWD/$SCRIPT" 2>&1) || STATUS=$?
cd "$OLDPWD"
rm -rf "$TMPDIR"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*hook not wired"; then
    echo "  PASS — exit 0 + WARN (폐쇄루프)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-5: POSIX strict mode (shebang + set -euo pipefail) ==="
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
echo "ALL PASS (5/5)"
exit 0
