#!/usr/bin/env bash
# CFP-426 / CFP-427 / ADR-040 Amendment 3 — unit test for check-worktree-first-session-start-wire.sh (exec swap wrapper)
# Tests:
#   TC-1: BYPASS_WORKTREE_FIRST=1 env short-circuit (canonical 안에서 처리)
#   TC-2: normal run = exec swap → canonical OK log
#   TC-3: POSIX strict mode (shebang + set -euo pipefail)
#   TC-4: 폐쇄루프 — settings.json 부재 시 canonical WARN exit 0
#   TC-8: recursive-call guard — wrapper 가 canonical 이름으로 invoke 시 exit 2 (FIX iter 1 F-5)
#   TC-9: missing-script guard — canonical 부재 시 wrapper exit 0 + WARN (FIX iter 1 F-5)
set -euo pipefail
cd "$(dirname "$0")/../.."

SCRIPT="scripts/check-worktree-first-session-start-wire.sh"
CANONICAL="scripts/check-session-start-hook-presence.sh"
FAIL=0

# OR-short-circuit pattern (FIX iter 2, F-001 P1): set -e race 회피.

echo "=== TC-1: BYPASS_WORKTREE_FIRST=1 short-circuit ==="
STATUS=0
OUT=$(BYPASS_WORKTREE_FIRST=1 bash "$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "BYPASS_WORKTREE_FIRST=1 — skip"; then
    echo "  PASS — exit 0 + skip log (canonical 처리)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-2: normal run = exec swap → canonical OK log ==="
STATUS=0
OUT=$(bash "$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "OK"; then
    echo "  PASS — exit 0 + canonical OK log (drift 0)"
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

echo "=== TC-4: 폐쇄루프 — settings.json 부재 시 canonical WARN exit 0 ==="
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/scripts"
cp "$SCRIPT" "$CANONICAL" "$TMPDIR/scripts/"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
STATUS=0
OUT=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
cd "$OLDPWD"
rm -rf "$TMPDIR"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*not found"; then
    echo "  PASS — exit 0 + WARN log (폐쇄루프 detect)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-8: recursive-call guard — wrapper invoked as canonical name → exit 2 ==="
TMPDIR=$(mktemp -d)
# wrapper script 를 canonical 이름으로 copy 하여 self-invocation 시뮬레이션
cp "$SCRIPT" "$TMPDIR/check-session-start-hook-presence.sh"
chmod +x "$TMPDIR/check-session-start-hook-presence.sh"
STATUS=0
OUT=$(bash "$TMPDIR/check-session-start-hook-presence.sh" 2>&1) || STATUS=$?
rm -rf "$TMPDIR"
if [ "$STATUS" -eq 2 ] && echo "$OUT" | grep -q "recursive call detected"; then
    echo "  PASS — exit 2 + ERROR log"
else
    echo "  FAIL — exit=$STATUS (expected 2) output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-9: missing-script guard — canonical 부재 시 wrapper exit 0 + WARN ==="
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/scripts"
cp "$SCRIPT" "$TMPDIR/scripts/"
# canonical 미복사
STATUS=0
OUT=$(bash "$TMPDIR/scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
rm -rf "$TMPDIR"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*canonical script not found"; then
    echo "  PASS — exit 0 + WARN log (missing-script guard)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
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
