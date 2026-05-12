#!/usr/bin/env bash
# CFP-428 / ADR-040 Amendment 3 — unit test for templates/.git-hooks/pre-checkout.sample
# Hook 자체 동작 검증 — mktemp -d + git init -q isolation 의무.
# Tests:
#   TC-1: BYPASS_WORKTREE_FIRST=1 env short-circuit
#   TC-2: worktree 내부 (git_dir != common_dir) → exit 0 무영향
#   TC-3: main + file checkout ($3 == "0") → exit 0 무영향
#   TC-4: main + branch checkout + cfp-NNN match → WARN + exit 0 (warning tier)
#   TC-5: main + branch checkout + main branch → 무영향
#   TC-6: hierarchical branch (cfp-NNN/lane) match → WARN + exit 0
#   TC-7: POSIX strict mode (shebang + set -euo pipefail)
set -euo pipefail
cd "$(dirname "$0")/../.."
REPO_ROOT="$(pwd)"

HOOK="$REPO_ROOT/templates/.git-hooks/pre-checkout.sample"
FAIL=0

# OR-short-circuit pattern (FIX iter 2, F-001 P1): set -e race 회피.

echo "=== TC-1: BYPASS_WORKTREE_FIRST=1 short-circuit ==="
STATUS=0
# pre-checkout hook 3-args: prev_HEAD, next_HEAD (ref form), branch_flag(1)
OUT=$(BYPASS_WORKTREE_FIRST=1 bash "$HOOK" "HEAD" "refs/heads/cfp-428" "1" 2>&1) || STATUS=$?
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
# Initial commit (worktree 생성 prerequisite)
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
# Worktree 생성 (git_dir != common_dir 강제)
git worktree add -q -b test-wt "$TMPDIR/wt" 2>&1 >/dev/null
cd "$TMPDIR/wt"
STATUS=0
OUT=$(bash "$TMPDIR/hook.sh" "HEAD" "refs/heads/cfp-428" "1" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && [ -z "$OUT" ]; then
    echo "  PASS — worktree 내부 = exit 0 + no output"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-3: main + file checkout (\$3 == \"0\") → exit 0 무영향 ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
STATUS=0
# 3rd arg = "0" (file checkout, not branch checkout)
OUT=$(bash "$TMPDIR/hook.sh" "HEAD" "refs/heads/cfp-428" "0" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && [ -z "$OUT" ]; then
    echo "  PASS — file checkout = exit 0 + no output"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-4: main + branch checkout + cfp-NNN match → WARN + exit 0 ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
# cfp-428 branch 생성 (next_branch resolve 가능 상태)
git branch cfp-428
STATUS=0
# pre-checkout hook 의 $2 인자 = git 가 ref form (refs/heads/<branch>) 전달
OUT=$(bash "$TMPDIR/hook.sh" "HEAD" "refs/heads/cfp-428" "1" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*cfp-428"; then
    echo "  PASS — main + cfp-428 = WARN + exit 0"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-5: main + branch checkout + main branch → 무영향 ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR" && git init -q -b main 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
STATUS=0
OUT=$(bash "$TMPDIR/hook.sh" "HEAD" "refs/heads/main" "1" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && [ -z "$OUT" ]; then
    echo "  PASS — main branch checkout = exit 0 + no output"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-6: hierarchical branch (cfp-NNN/lane) match → WARN + exit 0 ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cp "$HOOK" "$TMPDIR/hook.sh"
chmod +x "$TMPDIR/hook.sh"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
git -c user.email=t@t -c user.name=t commit --allow-empty -q -m "init"
git branch "cfp-428/design"
STATUS=0
OUT=$(bash "$TMPDIR/hook.sh" "HEAD" "refs/heads/cfp-428/design" "1" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*cfp-428/design"; then
    echo "  PASS — hierarchical branch cfp-428/design = WARN + exit 0"
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
