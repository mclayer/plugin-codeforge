#!/usr/bin/env bash
# CFP-428 / ADR-040 Amendment 3 — unit test for scripts/install-git-hooks.sh
# Tests:
#   TC-1: BYPASS_WORKTREE_FIRST=1 env (no-op — installer 자체는 env check 0, 단 lint chain 안 정합 verify)
#     Note: install-git-hooks.sh = installer (env-independent). 본 TC-1 = installer 호출 정상 verify.
#   TC-2: idempotent (1st call install + 2nd call all skip) — mktemp -d isolation
#   TC-3: 기존 symlink skip (already symlinked → no-op)
#   TC-4: non-symlink file skip + WARN (사용자 explicit conflict resolution 의무)
#   TC-5: chmod +x verify (sample executable bit propagation)
#   TC-6: POSIX strict mode (shebang + set -euo pipefail)
#   TC-7: missing TEMPLATE_HOOKS dir = exit 0 + WARN
set -euo pipefail
cd "$(dirname "$0")/../.."
REPO_ROOT="$(pwd)"

SCRIPT="$REPO_ROOT/scripts/install-git-hooks.sh"
FAIL=0

# OR-short-circuit pattern (FIX iter 2, F-001 P1): set -e race 회피.

echo "=== TC-1: installer 호출 정상 (env-independent, no-op installer self-check) ==="
# install-git-hooks.sh 는 env check 미보유. TC-1 = mktemp -d 안 정상 호출 verify.
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts" "$TMPDIR/templates/.git-hooks"
cp "$SCRIPT" "$TMPDIR/scripts/"
cp "$REPO_ROOT/templates/.git-hooks/pre-checkout.sample" "$TMPDIR/templates/.git-hooks/"
cp "$REPO_ROOT/templates/.git-hooks/pre-commit-main-block.sample" "$TMPDIR/templates/.git-hooks/"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
STATUS=0
OUT=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "linked"; then
    echo "  PASS — installer 정상 호출 + linked log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-2: idempotent (1st call install + 2nd call all skip) ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts" "$TMPDIR/templates/.git-hooks"
cp "$SCRIPT" "$TMPDIR/scripts/"
cp "$REPO_ROOT/templates/.git-hooks/pre-checkout.sample" "$TMPDIR/templates/.git-hooks/"
cp "$REPO_ROOT/templates/.git-hooks/pre-commit-main-block.sample" "$TMPDIR/templates/.git-hooks/"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
# 1st call
STATUS1=0
OUT1=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS1=$?
# 2nd call
STATUS2=0
OUT2=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS2=$?
cd "$REPO_ROOT"
LINKED_COUNT_1=$(echo "$OUT1" | grep -c "linked:" || true)
SKIP_COUNT_2_SYMLINK=$(echo "$OUT2" | grep -c "already symlinked" || true)
SKIP_COUNT_2_NONSYMLINK=$(echo "$OUT2" | grep -c "WARN.*non-symlink" || true)
# POSIX (Linux/macOS) = `ln -s` symlink → 2nd call "already symlinked" skip.
# Windows MSYS2 / Git Bash = `ln -s` copy fallback (winsymlinks 미설정 시) → 2nd call "WARN non-symlink" skip.
# 두 패턴 모두 idempotent 의미 (재실행 후 file 존재 + 추가 mutation 0).
SKIP_TOTAL=$((SKIP_COUNT_2_SYMLINK + SKIP_COUNT_2_NONSYMLINK))
if [ "$STATUS1" -eq 0 ] && [ "$STATUS2" -eq 0 ] && [ "$LINKED_COUNT_1" -ge 2 ] && [ "$SKIP_TOTAL" -ge 2 ]; then
    echo "  PASS — 1st linked=$LINKED_COUNT_1 + 2nd skip=$SKIP_TOTAL (symlink=$SKIP_COUNT_2_SYMLINK + non-symlink=$SKIP_COUNT_2_NONSYMLINK, cross-platform idempotent)"
else
    echo "  FAIL — status1=$STATUS1 status2=$STATUS2 linked=$LINKED_COUNT_1 skip_total=$SKIP_TOTAL"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-3: 기존 symlink skip (already symlinked → no-op) ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts" "$TMPDIR/templates/.git-hooks"
cp "$SCRIPT" "$TMPDIR/scripts/"
cp "$REPO_ROOT/templates/.git-hooks/pre-checkout.sample" "$TMPDIR/templates/.git-hooks/"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
# 기존 symlink 생성 — Windows MSYS2 환경에서는 copy fallback (winsymlinks 미설정)
ln -s "$TMPDIR/templates/.git-hooks/pre-checkout.sample" "$TMPDIR/.git/hooks/pre-checkout"
# Platform check: symlink 생성 성공 여부 (Linux/macOS = true symlink, Windows MSYS2 = copy fallback)
if [ -L "$TMPDIR/.git/hooks/pre-checkout" ]; then
    EXPECTED_LOG="already symlinked"
else
    # Windows MSYS2: ln -s 가 copy fallback → installer 가 non-symlink WARN 출력 (의미 동등 — 둘 다 skip)
    EXPECTED_LOG="WARN.*non-symlink"
fi
STATUS=0
OUT=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -qE "$EXPECTED_LOG"; then
    echo "  PASS — 기존 file skip (POSIX symlink 또는 Windows MSYS2 copy fallback 모두 skip 의미)"
else
    echo "  FAIL — exit=$STATUS expected=$EXPECTED_LOG output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-4: non-symlink file skip + WARN ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts" "$TMPDIR/templates/.git-hooks"
cp "$SCRIPT" "$TMPDIR/scripts/"
cp "$REPO_ROOT/templates/.git-hooks/pre-checkout.sample" "$TMPDIR/templates/.git-hooks/"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
# 기존 non-symlink file 생성 (regular file)
echo "#!/bin/sh" > "$TMPDIR/.git/hooks/pre-checkout"
chmod +x "$TMPDIR/.git/hooks/pre-checkout"
STATUS=0
OUT=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*non-symlink"; then
    echo "  PASS — non-symlink file skip + WARN"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-5: chmod +x verify (sample executable bit propagation) ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts" "$TMPDIR/templates/.git-hooks"
cp "$SCRIPT" "$TMPDIR/scripts/"
cp "$REPO_ROOT/templates/.git-hooks/pre-checkout.sample" "$TMPDIR/templates/.git-hooks/"
# 의도적으로 executable bit 제거 — Windows NTFS 에서는 무효 (executable bit 영구 유지)
chmod -x "$TMPDIR/templates/.git-hooks/pre-checkout.sample"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
STATUS=0
OUT=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
# 설치 후 sample 자체 executable 확인 (POSIX) 또는 install 성공 verify (Windows)
if [ -x "$TMPDIR/templates/.git-hooks/pre-checkout.sample" ] && [ "$STATUS" -eq 0 ]; then
    # POSIX 환경 = chmod +x 발동 결과 verify / Windows 환경 = 항상 -x true (skip-equiv pass)
    if echo "$OUT" | grep -q "linked\|already symlinked"; then
        echo "  PASS — installer 정상 + sample executable (POSIX) 또는 Windows NTFS noop pass"
    else
        echo "  FAIL — exit=$STATUS output=$OUT"
        FAIL=$((FAIL + 1))
    fi
else
    EXECUTABLE_CHECK=$([ -x "$TMPDIR/templates/.git-hooks/pre-checkout.sample" ] && echo "yes" || echo "no")
    echo "  FAIL — exit=$STATUS executable=$EXECUTABLE_CHECK output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

echo "=== TC-6: POSIX strict mode (shebang + set -euo pipefail) ==="
SHEBANG=$(head -n 1 "$SCRIPT")
if [ "$SHEBANG" = "#!/usr/bin/env bash" ] && grep -q "^set -euo pipefail" "$SCRIPT"; then
    echo "  PASS — shebang + strict mode"
else
    echo "  FAIL — shebang=$SHEBANG"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-7: missing TEMPLATE_HOOKS dir = exit 0 + WARN ==="
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
mkdir -p "$TMPDIR/scripts"
cp "$SCRIPT" "$TMPDIR/scripts/"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
# templates/.git-hooks 부재
STATUS=0
OUT=$(bash "scripts/$(basename "$SCRIPT")" 2>&1) || STATUS=$?
cd "$REPO_ROOT"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN.*not found"; then
    echo "  PASS — exit 0 + WARN log (missing TEMPLATE_HOOKS dir)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi
rm -rf "$TMPDIR"
trap - EXIT

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "FAIL count: $FAIL"
    exit 1
fi
echo ""
echo "ALL PASS (7/7)"
exit 0
