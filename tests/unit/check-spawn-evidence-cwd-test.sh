#!/usr/bin/env bash
# CFP-427 — unit test for scripts/check-spawn-evidence-cwd.sh
# Tests:
#   TC-1: BYPASS_WORKTREE_FIRST=1 env short-circuit
#   TC-2: PLACEHOLDER sentinel safe-fallback (default ENFORCE_FROM = PLACEHOLDER → enforce skip)
#   TC-3: ENFORCE_FROM env override + valid worktree path → PASS (no WARN)
#   TC-4a: 30자+ N/A bypass → PASS (no WARN)
#   TC-4b: 30자 미만 N/A → WARN
#   TC-4c: read-only suffix → PASS (no WARN)
#   TC-4d: worktree 외 path → WARN
#   TC-5: enforce-from filter (pre-existing Story timestamp 이전 → skip)
#   TC-6: docs/stories 부재 → exit 0 + skip log
#   TC-7: POSIX strict mode (shebang + set -euo pipefail) presence
set -euo pipefail
cd "$(dirname "$0")/../.."

SCRIPT="scripts/check-spawn-evidence-cwd.sh"
FAIL=0

# OR-short-circuit pattern (Story 1 FIX iter 2 F-001 verbatim mirror): set -e race 회피.

echo "=== TC-1: BYPASS_WORKTREE_FIRST=1 short-circuit ==="
STATUS=0
OUT=$(BYPASS_WORKTREE_FIRST=1 bash "$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "BYPASS_WORKTREE_FIRST=1 — skip"; then
    echo "  PASS — exit 0 + skip log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-2: PLACEHOLDER sentinel safe-fallback ==="
STATUS=0
OUT=$(bash "$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && (echo "$OUT" | grep -q "PLACEHOLDER" || echo "$OUT" | grep -q "stories not found"); then
    echo "  PASS — exit 0 + PLACEHOLDER skip log (or stories dir absent)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

# TC-3 ~ TC-4d: 임시 docs/stories/ + Story file scaffold 생성 후 actual logic 검증
ORIG_DIR="$(pwd)"
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/docs/stories" "$TMPDIR/scripts"
cp "$SCRIPT" "$TMPDIR/scripts/"
cd "$TMPDIR" && git init -q 2>&1 >/dev/null
git config user.email "test@example.com"
git config user.name "test"

create_story() {
  local key="$1"; local working_dir="$2"
  cat > "docs/stories/$key.md" <<STORY_EOF
---
key: $key
title: test story
---

## §14 Lane Evidence

\`\`\`yaml
lane_evidence:
  - lane: 요구사항
    iteration: 1
    transcript: "test transcript Working dir: $working_dir"
\`\`\`
STORY_EOF
  git add "docs/stories/$key.md"
  git commit -q -m "add $key"
}

# TC-3: valid worktree path → PASS (no WARN)
echo "=== TC-3: ENFORCE_FROM override + valid worktree path → PASS ==="
create_story "TEST-A" "/c/Users/test/.claude/worktrees/repo/branch"
STATUS=0
OUT=$(ENFORCE_FROM="2020-01-01T00:00:00+00:00" bash "$ORIG_DIR/$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && ! echo "$OUT" | grep -q "WARN: TEST-A"; then
    echo "  PASS — exit 0 + no WARN for TEST-A"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

# TC-4a: 30자+ N/A bypass → PASS
echo "=== TC-4a: 30자+ N/A bypass → PASS ==="
create_story "TEST-B" "N/A — RequirementsPLAgent main worktree fallback (ADR-031 §결정 4 bypass)"
STATUS=0
OUT=$(ENFORCE_FROM="2020-01-01T00:00:00+00:00" bash "$ORIG_DIR/$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && ! echo "$OUT" | grep -q "WARN: TEST-B"; then
    echo "  PASS — exit 0 + no WARN for TEST-B"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

# TC-4b: 30자 미만 N/A → WARN
echo "=== TC-4b: 30자 미만 N/A → WARN ==="
create_story "TEST-C" "N/A"
STATUS=0
OUT=$(ENFORCE_FROM="2020-01-01T00:00:00+00:00" bash "$ORIG_DIR/$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN: TEST-C"; then
    echo "  PASS — exit 0 + WARN for TEST-C (30자 미만)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

# TC-4c: read-only suffix → PASS
echo "=== TC-4c: read-only suffix → PASS ==="
create_story "TEST-D" "read-only fetch deputy"
STATUS=0
OUT=$(ENFORCE_FROM="2020-01-01T00:00:00+00:00" bash "$ORIG_DIR/$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && ! echo "$OUT" | grep -q "WARN: TEST-D"; then
    echo "  PASS — exit 0 + no WARN for TEST-D"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

# TC-4d: worktree 외 path → WARN
echo "=== TC-4d: worktree 외 path → WARN ==="
create_story "TEST-E" "c:/workspace/mclayer/repo"
STATUS=0
OUT=$(ENFORCE_FROM="2020-01-01T00:00:00+00:00" bash "$ORIG_DIR/$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "WARN: TEST-E"; then
    echo "  PASS — exit 0 + WARN for TEST-E (worktree 외)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

# TC-5: enforce-from filter (future ENFORCE_FROM = pre-existing Story skip)
echo "=== TC-5: enforce-from filter (future ENFORCE_FROM → all skip) ==="
STATUS=0
OUT=$(ENFORCE_FROM="2099-01-01T00:00:00+00:00" bash "$ORIG_DIR/$SCRIPT" 2>&1) || STATUS=$?
if [ "$STATUS" -eq 0 ] && ! echo "$OUT" | grep -q "WARN: TEST-"; then
    echo "  PASS — all stories skipped (pre-existing)"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

cd "$ORIG_DIR"
rm -rf "$TMPDIR"

# TC-6: docs/stories 부재 → exit 0 + skip log
echo "=== TC-6: docs/stories 부재 → exit 0 + skip log ==="
TMPDIR2=$(mktemp -d)
cd "$TMPDIR2" && git init -q 2>&1 >/dev/null
STATUS=0
OUT=$(ENFORCE_FROM="2020-01-01T00:00:00+00:00" bash "$ORIG_DIR/$SCRIPT" 2>&1) || STATUS=$?
cd "$ORIG_DIR"
rm -rf "$TMPDIR2"
if [ "$STATUS" -eq 0 ] && echo "$OUT" | grep -q "stories not found"; then
    echo "  PASS — exit 0 + skip log"
else
    echo "  FAIL — exit=$STATUS output=$OUT"
    FAIL=$((FAIL + 1))
fi

echo "=== TC-7: POSIX strict mode (shebang + set -euo pipefail) ==="
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
echo "ALL PASS (9/9)"
exit 0
