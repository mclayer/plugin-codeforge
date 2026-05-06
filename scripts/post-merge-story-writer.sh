#!/usr/bin/env bash
# scripts/post-merge-story-writer.sh — Cross-repo Story §9 row append
# Required env: GH_TOKEN (CODEFORGE_CROSS_REPO_PAT, contents:write on internal-docs)
# Args: --story-key CFP-NN --lane phase:설계-리뷰 --pr-number N --pr-repo owner/repo --decider user_admin

set -euo pipefail

STORY_KEY=""
LANE=""
PR_NUM=""
PR_REPO=""
DECIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --story-key) STORY_KEY="$2"; shift 2 ;;
        --lane) LANE="$2"; shift 2 ;;
        --pr-number) PR_NUM="$2"; shift 2 ;;
        --pr-repo) PR_REPO="$2"; shift 2 ;;
        --decider) DECIDER="$2"; shift 2 ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$STORY_KEY" || -z "$LANE" || -z "$PR_NUM" || -z "$PR_REPO" || -z "$DECIDER" ]]; then
    echo "Usage: $0 --story-key CFP-NN --lane phase:X --pr-number N --pr-repo owner/repo --decider DECIDER" >&2
    exit 1
fi

# Map lane label → §9 row lane name
case "$LANE" in
    phase:설계-리뷰) ROW_LANE="설계-리뷰" ;;
    phase:구현-리뷰) ROW_LANE="구현-리뷰" ;;
    phase:보안-테스트) ROW_LANE="보안-테스트" ;;
    *) echo "::notice::Lane not eligible for §9 write: $LANE"; exit 0 ;;
esac

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
NEW_ROW="| 1 | ${ROW_LANE} | TBD | TBD | ${DECIDER} | PASS (${PR_REPO}#${PR_NUM} merged) | ${TIMESTAMP} |"

INTERNAL_DOCS_REPO="mclayer/codeforge-internal-docs"
PLUGIN_FOLDER="${PLUGIN_FOLDER:-wrapper}"
STORY_PATH="${PLUGIN_FOLDER}/stories/${STORY_KEY}.md"
BRANCH="${STORY_KEY,,}-post-merge-followup-pr${PR_NUM}"

# CFP-74 Codex P1 #4 fix: idempotency rerun guard
# (a) Existing PR check — if open PR exists for this branch, skip (don't re-create)
# (b) Existing branch check — same SHA → skip
# (c) Main content check (legacy) — already-merged §9 row dedup
EXISTING_PR=$(gh pr list -R "$INTERNAL_DOCS_REPO" --state open --head "$BRANCH" --json number --jq '.[0].number' 2>/dev/null || echo "")
if [[ -n "$EXISTING_PR" ]]; then
    echo "::notice::Existing PR #${EXISTING_PR} on branch ${BRANCH} (idempotent skip)"
    exit 0
fi

# Main content idempotency
CURRENT_CONTENT=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${STORY_PATH}" --jq '.content' | base64 -d)
if echo "$CURRENT_CONTENT" | grep -q "${PR_REPO}#${PR_NUM} merged"; then
    echo "::notice::§9 row for ${PR_REPO}#${PR_NUM} already exists in main (idempotent skip)"
    exit 0
fi

# CFP-74 followup #3: Append §9 row with table-header auto-insert.
# Story files may or may not pre-include §9 table header. Two paths:
#   (a) Existing `| Iter |` table header found → print header + separator + new row.
#   (b) Reached `## §10` without finding table → insert table header + separator + row before §10.
# This ensures row always lands inside a valid markdown table for readability.
NEW_CONTENT=$(echo "$CURRENT_CONTENT" | awk -v new_row="$NEW_ROW" '
    BEGIN {
        in_section = 0      # inside §9 block
        existing_table = 0  # found `| Iter |` header
        in_table = 0        # currently iterating table rows
        row_inserted = 0
        trailing_blank = 0
    }
    /^## §9 / { in_section = 1; print; next }

    # Enter existing table (header line)
    in_section && /^\| Iter \|/ {
        existing_table = 1
        in_table = 1
        if (trailing_blank) { print ""; trailing_blank = 0 }
        print
        next
    }

    # Continuation of table (separator or row): keep printing
    in_section && in_table && /^\|/ { print; next }

    # First non-| line after table: insert new row here, exit table mode
    in_section && in_table {
        print new_row
        row_inserted = 1
        in_table = 0
        if (/^$/) { trailing_blank = 1; next }
        print
        next
    }

    # §10 boundary without prior table → insert table header + row
    /^## §10/ && in_section && !row_inserted {
        if (!existing_table) {
            print ""
            print "| Iter | 레인 | Claude verdict | Codex verdict | Decider | 결과 | 시각 |"
            print "|------|------|----------------|---------------|---------|------|------|"
        }
        print new_row
        print ""
        print
        in_section = 0
        row_inserted = 1
        trailing_blank = 0
        next
    }

    in_section && /^$/ { trailing_blank = 1; next }
    in_section {
        if (trailing_blank) { print ""; trailing_blank = 0 }
        print
        next
    }
    { print }
')

# Get current file SHA
SHA=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${STORY_PATH}" --jq '.sha')
NEW_CONTENT_B64=$(echo "$NEW_CONTENT" | base64 -w0)

# Create branch (PR-specific to avoid concurrent conflict)
MAIN_SHA=$(gh api "repos/${INTERNAL_DOCS_REPO}/git/refs/heads/main" --jq '.object.sha')
gh api -X POST "repos/${INTERNAL_DOCS_REPO}/git/refs" \
    -f ref="refs/heads/${BRANCH}" -f sha="$MAIN_SHA" 2>/dev/null || true

# PUT file on branch
gh api -X PUT "repos/${INTERNAL_DOCS_REPO}/contents/${STORY_PATH}" \
    -f message="docs(${STORY_KEY,,}): post-merge §9 PASS auto-write (${PR_REPO}#${PR_NUM})" \
    -f content="$NEW_CONTENT_B64" \
    -f sha="$SHA" \
    -f branch="$BRANCH"

# CFP-74 Codex P2 fix: Add explicit story_uri marker for cross-repo binding
STORY_URI="https://github.com/${INTERNAL_DOCS_REPO}/blob/main/${STORY_PATH}"
PR_BODY=$(cat <<EOF
Auto-generated by post-merge-followup workflow.

- Decider: ${DECIDER}
- Source PR: ${PR_REPO}#${PR_NUM}
- Lane: ${ROW_LANE}

story_uri: ${STORY_URI}
EOF
)

# Open PR
gh pr create -R "$INTERNAL_DOCS_REPO" \
    --base main --head "$BRANCH" \
    --title "${STORY_KEY} post-merge §9 auto-write (${PR_REPO}#${PR_NUM})" \
    --body "$PR_BODY"

echo "::notice::§9 row appended to ${STORY_PATH}, PR opened on ${BRANCH}"
