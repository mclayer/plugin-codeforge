#!/usr/bin/env bash
# CFP-428 / ADR-040 Amendment 3 — unit test for templates/.git-hooks/pre-commit-main-block.sample
# Hook 자체 동작 검증 — mktemp -d + git init -q isolation 의무.
# Tests:
#   TC-1: BYPASS_WORKTREE_FIRST=1 env short-circuit
#   TC-2: worktree 내부 (git_dir != common_dir) → exit 0 무영향
#   TC-3: main + src/ staged → WARN + exit 0 (warning tier)
#   TC-4: main + docs/ staged → WARN + exit 0
#   TC-5: main + tests/ staged → 무영향 (path matching scope 외)
#   TC-6: main + 혼합 (src + tests) staged → WARN + exit 0 (src matches)
#   TC-7: POSIX strict mode (shebang + set -euo pipefail)
set -euo pipefail
cd "$(dirname "$0")/../.."
REPO_ROOT="$(pwd)"

HOOK="$REPO_ROOT/templates/.git-hooks/pre-commit-main-block.sample"
FAIL=0

# OR-short-circuit pattern (FIX iter 2, F-001 P1): set -e race 회피.

echo "=== TC-1: BYPASS_WORKTREE_FIRST=1 short-circuit ==="
STATUS=0
OUT=$(BYPASS_WORKTREE_FIRST=1 bash "$HOOK" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && [ -z "$OUT" ]; then
    echo "  PASS — exit 0 + no output (BYPASS short-circuit)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-2: worktree 내부 (git_dir != common_dir) → exit 0 무영향 ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/main"
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR/main" && git init -q 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
# Worktree 생성
git worktree add -q -b test-wt "$TMPDIR/wt" 2>&1 >/dev/null
cd "$TMPDIR/wt"
# src/ staged 시도 (worktree 내부)
mkdir -p src && echo "test" > src/a.txt
git add src/a.txt
STATUS=0
OUT=$(bash "$TMPDIR/hook.sh" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && [ -z "$OUT" ]; then
    echo "  PASS — worktree 내부 = exit 0 + no output (git_dir != common_dir short-circuit)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-3: main + src/ staged → WARN + exit 0 ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
mkdir -p src && echo "test" > src/a.txt
git add src/a.txt
STATUS=0
OUT=$(bash "$TMPDIR/hook.sh" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*src/docs"; then
    echo "  PASS — main + src/ = WARN + exit 0"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-4: main + docs/ staged → WARN + exit 0 ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
mkdir -p docs && echo "test" > docs/a.md
git add docs/a.md
STATUS=0
OUT=$(bash "$TMPDIR/hook.sh" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*src/docs"; then
    echo "  PASS — main + docs/ = WARN + exit 0"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-5: main + tests/ staged → 무영향 (path matching scope 외) ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
mkdir -p tests && echo "test" > tests/a.sh
git add tests/a.sh
STATUS=0
OUT=$(bash "$TMPDIR/hook.sh" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && [ -z "$OUT" ]; then
    echo "  PASS — main + tests/ = exit 0 + no output (scope 외)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-6: main + 혼합 (src + tests) staged → WARN + exit 0 (src matches) ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
mkdir -p src tests
echo "a" > src/a.txt
echo "b" > tests/b.sh
git add src/a.txt tests/b.sh
STATUS=0
OUT=$(bash "$TMPDIR/hook.sh" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*src/docs"; then
    echo "  PASS — main + 혼합 (src + tests) = WARN + exit 0 (src matches)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-7: POSIX strict mode (shebang + set -euo pipefail) ==="
SHEBANG=$(head -n 1 "$HOOK")
if [ "$SHEBANG" = "#!/usr/bin/env bash" ] && grep -q "^set -euo pipefail" "$HOOK"; then
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
echo "ALL PASS (7/7)"
exit 0
