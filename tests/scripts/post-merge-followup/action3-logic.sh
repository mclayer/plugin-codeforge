#!/usr/bin/env bash
# action3-logic.sh
# CFP-476 Phase 2 — workflow Action 3 (Carrier Issue close) isolated extraction
# For bash mock simulation in test harness
# ADR-026 Amendment 1 §결정 5.A-5.D algorithm

set -euo pipefail

# Input variables (injected from fixture mock or workflow env)
# - PR_BODY: PR body content (from fixture)
# - PR_NUM: PR number
# - THIS_REPO: repository slug (e.g., mclayer/plugin-codeforge)
# - ISSUE_NUM: pre-resolved carrier Issue number
# - TERMINAL_PHASE: terminal phase determined by consumer config
# - ISSUE_LANE: current Issue label phase
# - EXISTING_AUDIT: existing audit comment (for idempotency probe)

# Output: writes to $GITHUB_OUTPUT mock (or stdout)
OUTPUT_FILE="${GITHUB_OUTPUT:-.github-output}"

outcome_exit() {
    local outcome="$1"
    echo "outcome=$outcome" >> "$OUTPUT_FILE"
    exit 0
}

# ── Step 1: Basic issue resolution check ──────────────────────────────────
if [ -z "$ISSUE_NUM" ]; then
    echo "No Issue found" >&2
    outcome_exit "skip_no_issue"
fi

# ── Step 2: Terminal-phase gate ──────────────────────────────────────────
# In actual workflow, this is enforced in steps 3-5. In mock, we check fixture configuration
# to determine if this should be mid-phase skip or allowed to proceed.
# Special handling: fixtures can set ISSUE_LANE_SKIP_REASON to override
if [ -n "${ISSUE_LANE_SKIP_REASON:-}" ]; then
    echo "Mid-phase block by fixture: $ISSUE_LANE_SKIP_REASON" >&2
    outcome_exit "skip_phase1"
fi

# ── Step 3: Idempotency probe (AC-17) ─────────────────────────────────────
if [ -n "$EXISTING_AUDIT" ]; then
    echo "Audit comment already exists" >&2
    outcome_exit "skip_already_audited"
fi

# ── Step 4: Source A regex extraction (POSIX ERE — ADR-026 §결정 5.A SSOT) ──
# Regex: GitHub native 9 variant close keyword + bare/qualified #N reference.
MATCHES=$(printf '%s' "$PR_BODY" \
    | grep -oiE '(close[sd]?|fix(es|ed)?|resolve[sd]?)[[:space:]]*:?[[:space:]]*(([[:alnum:]_-]+/[[:alnum:]_.-]+)?#[0-9]+)' \
    || echo "")

if [ -z "$MATCHES" ]; then
    echo "No close keyword in PR body" >&2
    outcome_exit "skip_no_close_keyword"
fi

# ── Step 5: Parse and classify issue references ───────────────────────────
# Extract same-repo vs cross-repo references
SET_X=""
CROSS_REPO_HIT_SET=""
while IFS= read -r match_line; do
    [ -z "$match_line" ] && continue
    REF=$(echo "$match_line" | grep -oE '([[:alnum:]_-]+/[[:alnum:]_.-]+)?#[0-9]+$' | head -1 || echo "")
    [ -z "$REF" ] && continue

    if echo "$REF" | grep -qE '^[[:alnum:]_-]+/[[:alnum:]_.-]+#[0-9]+$'; then
        # Qualified owner/repo#N
        REF_REPO=$(echo "$REF" | sed 's/#[0-9]*$//')
        REF_NUM=$(echo "$REF" | grep -oE '[0-9]+$')
        if [ "$REF_REPO" = "$THIS_REPO" ]; then
            # Same-repo qualified → treat as bare
            SET_X=$(printf '%s\n%s' "$SET_X" "$REF_NUM" | sed '/^$/d')
        else
            CROSS_REPO_HIT_SET=$(printf '%s\n%s' "$CROSS_REPO_HIT_SET" "$REF" | sed '/^$/d')
        fi
    else
        # Bare #N
        REF_NUM=$(echo "$REF" | grep -oE '[0-9]+$')
        SET_X=$(printf '%s\n%s' "$SET_X" "$REF_NUM" | sed '/^$/d')
    fi
done <<EOF
$MATCHES
EOF
SET_X=$(echo "$SET_X" | sort -u | sed '/^$/d')

# ── Step 6: Cross-repo check ──────────────────────────────────────────────
if [ -n "$CROSS_REPO_HIT_SET" ]; then
    CROSS_REF=$(echo "$CROSS_REPO_HIT_SET" | head -1)
    echo "Cross-repo reference: $CROSS_REF" >&2
    outcome_exit "skip_cross_repo_unsupported"
fi

if [ -z "$SET_X" ]; then
    echo "No same-repo references" >&2
    outcome_exit "skip_no_match"
fi

# ── Step 7: Multi-match audit ─────────────────────────────────────────────
MATCH_COUNT=$(echo "$SET_X" | wc -l | tr -d ' ')
if [ "$MATCH_COUNT" -gt 1 ]; then
    echo "Multi-issue detected: $SET_X" >&2
    outcome_exit "skip_multi_issue"
fi

# ── Step 8: Single-issue dual-source AND (§5.A) ────────────────────────────
# This is the critical logic: Source A (keyword) ∩ Source B (GitHub API)
TARGET_N=$(echo "$SET_X" | head -1)

# In mock simulation, SOURCE_B is injected from fixture
# In real workflow, it's queried via `gh issue view ... closedByPullRequestsReferences`
# For fixture compatibility, SOURCE_B_LIST is a comma-separated string of PR numbers
SOURCE_B_LIST="${SOURCE_B_LIST:-}"

if [ -z "$SOURCE_B_LIST" ]; then
    echo "Source B empty (dual-source mismatch)" >&2
    outcome_exit "skip_dual_source_mismatch"
fi

# Check if PR_NUM is in Source B list
if ! echo "$SOURCE_B_LIST" | tr ',' '\n' | grep -qxF "$PR_NUM"; then
    echo "PR #$PR_NUM not in Source B" >&2
    outcome_exit "skip_dual_source_mismatch"
fi

# ── Step 9: Success ────────────────────────────────────────────────────────
echo "Issue close success" >&2
outcome_exit "success"
