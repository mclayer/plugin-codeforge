#!/usr/bin/env bash
# scripts/check-script-exec-bit.sh — exec bit invariant for directly-invoked workflow scripts
#
# Rule: Scripts referenced as `./scripts/X.sh` from `.github/workflows/` or
#       `templates/github-workflows/` must have git index mode 100755 (executable).
#       Linux runners refuse to exec 100644 files → workflow fail.
#
# Scripts invoked via `bash scripts/X.sh` (with explicit `bash` prefix) are
# exempt — bash interpreter doesn't require exec bit.
#
# Origin: CFP-74 followup #1 (PR #225) — 4 new scripts (post-merge-*.sh) deployed
# without exec bit because git defaults to 100644 on Windows clones. CI runner
# `Permission denied` discovered post-merge. This check prevents recurrence.
#
# Usage: bash scripts/check-script-exec-bit.sh
# Exit codes: 0 = all clean, 1 = drift detected

set -euo pipefail

EXIT=0
WORKFLOW_DIRS=(".github/workflows" "templates/github-workflows")

# Collect all `./scripts/X.sh` references from workflow yaml files (deduplicated).
# Codex audit P2 #2 fix: exclude `bash ./scripts/X.sh` form (bash prefix doesn't
# require exec bit — interpreter skips Linux exec check).
INVOKED_DIRECT=$(
    grep -rEh '\./scripts/[a-zA-Z0-9_./-]+\.sh' "${WORKFLOW_DIRS[@]}" 2>/dev/null \
    | grep -v 'bash[[:space:]]\+\./scripts' \
    | grep -oE '\./scripts/[a-zA-Z0-9_./-]+\.sh' \
    | sort -u || true
)

if [ -z "$INVOKED_DIRECT" ]; then
    echo "✓ No directly-invoked scripts found in workflows (no enforcement needed)"
    exit 0
fi

echo "Checking directly-invoked scripts (require git mode 100755):"
for ref in $INVOKED_DIRECT; do
    rel_path="${ref#./}"
    if [ ! -f "$rel_path" ]; then
        echo "  ⚠ $rel_path referenced in workflow but file does not exist (skip)"
        continue
    fi
    mode=$(git ls-files --stage "$rel_path" | awk '{print $1}' | head -1)
    if [ "$mode" = "100755" ]; then
        echo "  ✓ $rel_path (mode=$mode)"
    else
        echo "::error file=$rel_path::Mode $mode — expected 100755 (directly invoked from workflow)"
        echo "    Fix: git update-index --chmod=+x $rel_path"
        EXIT=1
    fi
done

if [ "$EXIT" -eq 0 ]; then
    echo ""
    echo "✓ All directly-invoked scripts have exec bit (CFP-74 invariant)"
fi

exit "$EXIT"
