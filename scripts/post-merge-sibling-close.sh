#!/usr/bin/env bash
# scripts/post-merge-sibling-close.sh — Auto-close sibling PRs with archive markers
# Required env: GH_TOKEN (current repo scope sufficient, no PAT)
# Args: $1 = story key (CFP-NN)
# Behavior: PRs with title containing story_key AND body containing
#           "Closed (deferral)" OR "archive 보존" markers → auto-close with comment

set -euo pipefail

STORY_KEY="${1:-}"
if [[ -z "$STORY_KEY" ]]; then
    echo "Usage: $0 <CFP-NN>" >&2
    exit 1
fi

# List open PRs with story_key in title
PRS=$(gh pr list --state open --search "$STORY_KEY in:title" --json number,title,body --jq '.[]')

if [[ -z "$PRS" ]]; then
    echo "::notice::No open sibling PRs for $STORY_KEY"
    exit 0
fi

echo "$PRS" | while IFS= read -r pr; do
    PR_NUM=$(echo "$pr" | jq -r '.number')
    PR_BODY=$(echo "$pr" | jq -r '.body')

    if echo "$PR_BODY" | grep -qE "(Closed \(deferral\)|archive 보존)"; then
        gh pr close "$PR_NUM" --comment "Auto-closed by post-merge-sibling-close workflow ($STORY_KEY follow-up). Archive marker detected."
        echo "::notice::Closed PR #$PR_NUM ($STORY_KEY archive)"
    fi
done
