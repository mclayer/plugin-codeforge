#!/usr/bin/env bash
# scripts/post-merge-telemetry.sh — Append telemetry entry to internal-docs JSONL counter
# Required env: GH_TOKEN (CODEFORGE_CROSS_REPO_PAT, contents:write on internal-docs)
# Args: --story-key CFP-NN --pr owner/repo#NUM --outcome auto_completed|partial|manual_only
#       --actions-completed comma,sep,list --decider DECIDER

set -euo pipefail

STORY_KEY=""; PR=""; OUTCOME=""; ACTIONS=""; DECIDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --story-key) STORY_KEY="$2"; shift 2 ;;
        --pr) PR="$2"; shift 2 ;;
        --outcome) OUTCOME="$2"; shift 2 ;;
        --actions-completed) ACTIONS="$2"; shift 2 ;;
        --decider) DECIDER="$2"; shift 2 ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$STORY_KEY" || -z "$PR" || -z "$OUTCOME" ]]; then
    echo "Usage: $0 --story-key CFP-NN --pr owner/repo#NUM --outcome auto_completed|partial|manual_only [--actions-completed list] [--decider X]" >&2
    exit 1
fi

case "$OUTCOME" in
    auto_completed|partial|manual_only) ;;
    *) echo "Invalid outcome: $OUTCOME" >&2; exit 1 ;;
esac

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
WORKFLOW_RUN_ID="${GITHUB_RUN_ID:-local}"
ACTIONS_JSON=$(echo "$ACTIONS" | jq -R 'split(",")')

# Build JSONL entry (single line, valid JSON)
ENTRY=$(jq -nc \
    --arg ts "$TIMESTAMP" \
    --arg sk "$STORY_KEY" \
    --arg pr "$PR" \
    --arg oc "$OUTCOME" \
    --argjson ac "$ACTIONS_JSON" \
    --arg dc "${DECIDER:-unknown}" \
    --arg rid "$WORKFLOW_RUN_ID" \
    '{
        contract_version: "1.0",
        timestamp: $ts,
        story_key: $sk,
        pr: $pr,
        outcome: $oc,
        actions_completed: $ac,
        actions_failed: [],
        decider: $dc,
        workflow_run_id: $rid
    }')

INTERNAL_DOCS_REPO="mclayer/codeforge-internal-docs"
PLUGIN_FOLDER="${PLUGIN_FOLDER:-wrapper}"
COUNTER_PATH="${PLUGIN_FOLDER}/post-merge-counters.jsonl"

# Fetch existing counter (or empty if not exists)
EXISTING=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")
NEW_CONTENT="${EXISTING}${ENTRY}"$'\n'
NEW_CONTENT_B64=$(printf "%s" "$NEW_CONTENT" | base64 -w0)

# Get SHA (or empty for new file)
SHA=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}" --jq '.sha' 2>/dev/null || echo "")

# PUT (create or update)
ARGS=(-X PUT "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}"
    -f message="telemetry(${STORY_KEY,,}): post-merge counter entry (PR ${PR}, outcome: ${OUTCOME})"
    -f content="$NEW_CONTENT_B64"
    -f branch="main")

if [[ -n "$SHA" ]]; then
    ARGS+=(-f sha="$SHA")
fi

gh api "${ARGS[@]}"

echo "::notice::Telemetry entry appended (story=$STORY_KEY, pr=$PR, outcome=$OUTCOME)"
