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

# CFP-74 Codex P0 fix: ADR-026 §결정 4 — main 직접 push 금지 invariant.
# Telemetry 도 cross-repo write 이므로 branch + PR 패턴 적용.
# Long-lived branch `telemetry-counters` 에 누적 commit, 단일 PR 가 update.
TELEMETRY_BRANCH="telemetry-counters"

# Ensure long-lived telemetry branch exists (idempotent — create if missing)
MAIN_SHA=$(gh api "repos/${INTERNAL_DOCS_REPO}/git/refs/heads/main" --jq '.object.sha')
gh api -X POST "repos/${INTERNAL_DOCS_REPO}/git/refs" \
    -f ref="refs/heads/${TELEMETRY_BRANCH}" -f sha="$MAIN_SHA" 2>/dev/null || true

# Fetch existing counter from telemetry branch (preferred — accumulates across runs).
# Fallback to main if branch is fresh.
EXISTING=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}?ref=${TELEMETRY_BRANCH}" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || \
           gh api "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || \
           echo "")

# CFP-74 Codex P1 #3 fix: trailing-newline preservation.
# Command substitution strips trailing newlines. Use printf with explicit \n separator.
if [[ -n "$EXISTING" ]]; then
    NEW_CONTENT=$(printf '%s\n%s\n' "$EXISTING" "$ENTRY")
else
    NEW_CONTENT=$(printf '%s\n' "$ENTRY")
fi
NEW_CONTENT_B64=$(printf '%s' "$NEW_CONTENT" | base64 -w0)

# Get SHA on telemetry branch (or empty for new file)
SHA=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}?ref=${TELEMETRY_BRANCH}" --jq '.sha' 2>/dev/null || echo "")

# PUT (create or update) on telemetry branch — NOT main
ARGS=(-X PUT "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}"
    -f message="telemetry(${STORY_KEY,,}): post-merge counter entry (PR ${PR}, outcome: ${OUTCOME})"
    -f content="$NEW_CONTENT_B64"
    -f branch="${TELEMETRY_BRANCH}")

if [[ -n "$SHA" ]]; then
    ARGS+=(-f sha="$SHA")
fi

# Pattern A retry loop — 4xx/5xx semantics per CFP-289 / domain-knowledge/jsonl-write/race-condition-handling-pattern.md
# 4xx (except 409): immediate fail, no-retry.
# 5xx / network error: exponential backoff (2s, 4s, 8s).
# 409 (SHA conflict): re-fetch SHA + jitter sleep, then retry.
# Exhausted: emit error to stderr, exit non-zero (never silent drop).
BACKOFF_DELAYS=(2 4 8)
WRITE_SUCCESS=0
for ATTEMPT in 1 2 3 4; do
    # Re-fetch SHA on each attempt (stale SHA from prior 409 would cause another conflict)
    if [[ "$ATTEMPT" -gt 1 ]]; then
        EXISTING=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}?ref=${TELEMETRY_BRANCH}" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")
        SHA=$(gh api "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}?ref=${TELEMETRY_BRANCH}" --jq '.sha' 2>/dev/null || echo "")
        # Rebuild content with refreshed EXISTING
        if [[ -n "$EXISTING" ]]; then
            NEW_CONTENT=$(printf '%s\n%s\n' "$EXISTING" "$ENTRY")
        else
            NEW_CONTENT=$(printf '%s\n' "$ENTRY")
        fi
        NEW_CONTENT_B64=$(printf '%s' "$NEW_CONTENT" | base64 -w0)
        ARGS=(-X PUT "repos/${INTERNAL_DOCS_REPO}/contents/${COUNTER_PATH}"
            -f message="telemetry(${STORY_KEY,,}): post-merge counter entry (PR ${PR}, outcome: ${OUTCOME})"
            -f content="$NEW_CONTENT_B64"
            -f branch="${TELEMETRY_BRANCH}")
        [[ -n "$SHA" ]] && ARGS+=(-f sha="$SHA")
    fi

    mkdir -p /tmp/telemetry-state
    gh api "${ARGS[@]}" -i > /tmp/telemetry-state/put-response.txt 2>/dev/null || true
    HTTP_CODE=$(head -1 /tmp/telemetry-state/put-response.txt | grep -o '[0-9]\{3\}' || echo "0")

    if echo "$HTTP_CODE" | grep -qE '^(200|201)$'; then
        echo "::notice::Telemetry JSONL write success (attempt=$ATTEMPT)"
        WRITE_SUCCESS=1
        break
    elif echo "$HTTP_CODE" | grep -q '^409$'; then
        # SHA conflict — concurrent write detected; re-fetch + jitter
        echo "::warning::SHA conflict (HTTP 409) on attempt $ATTEMPT — re-fetch SHA + jitter retry" >&2
        sleep $(( RANDOM % 5 + 1 ))
    elif echo "$HTTP_CODE" | grep -qE '^4[0-9]{2}$'; then
        # 4xx client error — no retry
        echo "::error::4xx client error (HTTP ${HTTP_CODE}) on telemetry write — no retry, aborting" >&2
        exit 1
    else
        # 5xx or network error — exponential backoff
        IDX=$(( ATTEMPT - 1 ))
        DELAY=${BACKOFF_DELAYS[$IDX]:-8}
        echo "::warning::5xx/network error (HTTP ${HTTP_CODE}) on attempt $ATTEMPT — backoff ${DELAY}s" >&2
        [[ "$ATTEMPT" -lt 4 ]] && sleep "$DELAY"
    fi
done

if [[ "$WRITE_SUCCESS" -ne 1 ]]; then
    echo "::error::Pattern A retries exhausted after 3 attempts — telemetry entry NOT written (story=${STORY_KEY}, pr=${PR})" >&2
    exit 1
fi

# Open or update single rolling PR for telemetry-counters branch (idempotent)
EXISTING_PR=$(gh pr list -R "$INTERNAL_DOCS_REPO" --state open --head "$TELEMETRY_BRANCH" --json number --jq '.[0].number' 2>/dev/null || echo "")
if [[ -z "$EXISTING_PR" ]]; then
    gh pr create -R "$INTERNAL_DOCS_REPO" \
        --base main --head "$TELEMETRY_BRANCH" \
        --title "telemetry: post-merge counters (rolling PR — ADR-026)" \
        --body "Auto-rolling telemetry counter PR (ADR-026 / CFP-74). Accumulates post-merge automation outcome events. Merge periodically (PMOAgent retro 30+ run 후)."
fi

echo "::notice::Telemetry entry appended to ${TELEMETRY_BRANCH} branch (story=$STORY_KEY, pr=$PR, outcome=$OUTCOME)"
