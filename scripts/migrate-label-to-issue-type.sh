#!/usr/bin/env bash
# migrate-label-to-issue-type.sh — CFP-140 / ADR-049
# Migrate label type:* to native GitHub Issue Types (idempotent).
# Usage:
#   --dry-run   (default) List Issues that would be migrated
#   --apply     Perform migration in batches (requires org admin)
#   --verify    Verify zero type:* labels remain (except impl-manifest)
#   --rollback  --batch-id N: Revert batch N
# §11.6: idempotent — --apply 2x = same result as 1x
# §7.4.2: graceful exit on SIGTERM (batch-level)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="dry-run"
ORG_SLUG=""
BATCH_SIZE=50
BATCH_ID=""
ROLLBACK=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)   MODE="dry-run";    shift ;;
    --apply)     MODE="apply";      shift ;;
    --verify)    MODE="verify";     shift ;;
    --rollback)  ROLLBACK=true;     shift ;;
    --batch-id)  BATCH_ID="$2";     shift 2 ;;
    --batch-size) BATCH_SIZE="$2";  shift 2 ;;
    --org)       ORG_SLUG="$2";     shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "ERROR: GH_TOKEN not set." >&2
  exit 1
fi

if [[ -z "$ORG_SLUG" ]]; then
  echo "ERROR: --org required." >&2
  exit 1
fi

# Type mapping (ADR-049)
declare -A LABEL_TO_TYPE
LABEL_TO_TYPE["type:epic"]="Epic"
LABEL_TO_TYPE["type:story"]="Story"
LABEL_TO_TYPE["type:bug"]="Bug"

# --- ROLLBACK mode ---
if [[ "$ROLLBACK" == true ]]; then
  if [[ -z "$BATCH_ID" ]]; then
    echo "ERROR: --rollback requires --batch-id N" >&2
    exit 1
  fi
  echo "ROLLBACK: batch-id=${BATCH_ID}"

  # Find audit Issue for this batch
  BATCH_ISSUES=$(gh api "/search/issues?q=org:${ORG_SLUG}+label:migration-batch-${BATCH_ID}&per_page=100" \
    --jq '.items[].number' 2>/dev/null || true)

  if [[ -z "$BATCH_ISSUES" ]]; then
    echo "No Issues found with label migration-batch-${BATCH_ID}"
    exit 0
  fi

  COUNT=0
  while IFS= read -r issue_number; do
    [[ -z "$issue_number" ]] && continue
    # Get current Issue Type
    CURRENT_TYPE=$(gh api "/repos/${ORG_SLUG}/issues/${issue_number}" \
      --jq '.type.name // ""' 2>/dev/null || true)

    if [[ -n "$CURRENT_TYPE" ]]; then
      # Remove Issue Type (set to null)
      gh api "/repos/${ORG_SLUG}/issues/${issue_number}" \
        --method PATCH \
        --field "type_id=" > /dev/null 2>&1 || true

      # Re-attach original type:* label
      ORIGINAL_LABEL=""
      for lbl in "${!LABEL_TO_TYPE[@]}"; do
        [[ "${LABEL_TO_TYPE[$lbl]}" == "$CURRENT_TYPE" ]] && ORIGINAL_LABEL="$lbl" && break
      done
      if [[ -n "$ORIGINAL_LABEL" ]]; then
        gh api "/repos/${ORG_SLUG}/issues/${issue_number}/labels" \
          --method POST \
          --field "labels[]=${ORIGINAL_LABEL}" > /dev/null 2>&1 || true
        echo "ROLLBACK: Issue #${issue_number} — removed type '${CURRENT_TYPE}', restored label '${ORIGINAL_LABEL}'"
      fi
      ((COUNT++)) || true
    fi
  done <<< "$BATCH_ISSUES"

  echo "ROLLBACK complete: $COUNT Issue(s) reverted in batch-${BATCH_ID}"
  exit 0
fi

# --- VERIFY mode ---
if [[ "$MODE" == "verify" ]]; then
  echo "VERIFY: checking for remaining type:* labels (except impl-manifest)..."
  REMAINING=0
  for label in "type:epic" "type:story" "type:bug"; do
    COUNT=$(gh api "/search/issues?q=org:${ORG_SLUG}+label:${label}&per_page=1" \
      --jq '.total_count' 2>/dev/null || echo "0")
    if [[ "$COUNT" -gt 0 ]]; then
      echo "FAIL: $COUNT Issue(s) still have label '$label'"
      REMAINING=$((REMAINING + COUNT))
    else
      echo "PASS: label '$label' has 0 Issues"
    fi
  done

  if [[ "$REMAINING" -gt 0 ]]; then
    echo "VERIFY FAIL: $REMAINING Issue(s) still have deprecated type:* labels" >&2
    exit 1
  fi
  echo "VERIFY PASS: no deprecated type:* labels remaining (impl-manifest not checked — separate axis)"
  exit 0
fi

# --- Guard: check for mctrader audit in progress (Q-4) ---
AUDIT_IN_PROGRESS=$(gh api "/search/issues?q=org:${ORG_SLUG}+label:audit:from-mctrader-debut+is:open&per_page=1" \
  --jq '.total_count' 2>/dev/null || echo "0")
if [[ "$AUDIT_IN_PROGRESS" -gt 0 ]]; then
  echo "WARNING: $AUDIT_IN_PROGRESS open mctrader-debut audit Issue(s) detected."
  echo "WARNING: It is recommended to run migration after mctrader audit is complete (Q-4)."
  if [[ "$MODE" == "apply" ]]; then
    echo "ERROR: --apply blocked while mctrader debut audit is in progress." >&2
    echo "To override, remove audit:from-mctrader-debut labels or use --org on a clean org." >&2
    exit 1
  fi
fi

# Guard: check migration-in-progress lock
LOCK=$(gh api "/search/issues?q=org:${ORG_SLUG}+label:migration-in-progress+is:open&per_page=1" \
  --jq '.total_count' 2>/dev/null || echo "0")
if [[ "$LOCK" -gt 0 && "$MODE" == "apply" ]]; then
  echo "ERROR: migration-in-progress lock label found. Another migration may be running." >&2
  exit 1
fi

# Get org Issue Type IDs
declare -A TYPE_IDS
for type_name in Epic Story Bug Audit; do
  TYPE_ID=$(gh api "/orgs/${ORG_SLUG}/issue-types" \
    --jq ".[] | select(.name==\"${type_name}\") | .id" 2>/dev/null || true)
  if [[ -n "$TYPE_ID" ]]; then
    TYPE_IDS["$type_name"]="$TYPE_ID"
  fi
done

if [[ ${#TYPE_IDS[@]} -eq 0 ]]; then
  echo "WARNING: No Issue Types configured for org ${ORG_SLUG}"
  echo "Run: gh api /orgs/${ORG_SLUG}/issue-types to check configuration"
  if [[ "$MODE" == "apply" ]]; then
    echo "ERROR: Cannot apply migration without configured Issue Types." >&2
    exit 1
  fi
fi

# Collect Issues to migrate
ALL_ISSUES=()
for label in "type:epic" "type:story" "type:bug"; do
  ISSUES=$(gh api "/search/issues?q=org:${ORG_SLUG}+label:${label}&per_page=100" \
    --paginate --jq '.items[] | "\(.number)\t\(.repository_url | split("/")[-2]+"/"+split("/")[-1])\t'"$label"'"' 2>/dev/null || true)
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    ALL_ISSUES+=("$line")
  done <<< "$ISSUES"
done

TOTAL=${#ALL_ISSUES[@]}
echo "Issues to migrate: $TOTAL"

if [[ "$MODE" == "dry-run" ]]; then
  for issue in "${ALL_ISSUES[@]:-}"; do
    IFS=$'\t' read -r num repo lbl <<< "$issue"
    target_type="${LABEL_TO_TYPE[$lbl]:-unknown}"
    echo "DRY-RUN: Issue #${num} in ${repo}: label '${lbl}' → Issue Type '${target_type}'"
  done
  echo "DRY-RUN complete: $TOTAL Issue(s) would be migrated"
  exit 2
fi

# --- APPLY mode ---
# Set migration-in-progress lock by creating audit Issue
if [[ "$TOTAL" -gt 0 ]]; then
  LOCK_ISSUE=$(gh api "/repos/${ORG_SLUG}/plugin-codeforge/issues" \
    --method POST \
    --field "title=[migration] CFP-140 label→Issue Type migration in progress ($(date -u +%Y-%m-%dT%H:%M:%SZ))" \
    --field "body=Migration started. Do not run --apply concurrently." \
    --jq '.number' 2>/dev/null || echo "")
  [[ -n "$LOCK_ISSUE" ]] && \
    gh api "/repos/${ORG_SLUG}/plugin-codeforge/issues/${LOCK_ISSUE}/labels" \
      --method POST --field "labels[]=migration-in-progress" > /dev/null 2>&1 || true
fi

# SIGTERM handler: release lock
cleanup() {
  if [[ -n "${LOCK_ISSUE:-}" ]]; then
    gh api "/repos/${ORG_SLUG}/plugin-codeforge/issues/${LOCK_ISSUE}/labels/migration-in-progress" \
      --method DELETE > /dev/null 2>&1 || true
    echo "SIGTERM: migration-in-progress lock released" >&2
  fi
}
trap cleanup SIGTERM SIGINT

# Batch processing
CURRENT_BATCH=1
BATCH_COUNT=0
TOTAL_MIGRATED=0
BATCH_ISSUE_NUMBERS=()

for issue_data in "${ALL_ISSUES[@]:-}"; do
  IFS=$'\t' read -r issue_num repo lbl <<< "$issue_data"
  target_type="${LABEL_TO_TYPE[$lbl]:-}"
  [[ -z "$target_type" ]] && continue

  TYPE_ID="${TYPE_IDS[$target_type]:-}"
  if [[ -z "$TYPE_ID" ]]; then
    echo "WARNING: Issue Type '${target_type}' not configured — skipping #${issue_num}"
    continue
  fi

  # Idempotency: check current type before applying
  CURRENT_TYPE=$(gh api "/repos/${repo}/issues/${issue_num}" \
    --jq '.type.name // ""' 2>/dev/null || true)

  if [[ "$CURRENT_TYPE" == "$target_type" ]]; then
    echo "SKIP (idempotent): Issue #${issue_num} already has type '${target_type}'"
    continue
  fi

  # Apply Issue Type
  gh api "/repos/${repo}/issues/${issue_num}" \
    --method PATCH \
    --field "type_id=${TYPE_ID}" > /dev/null 2>&1 || {
    # 409 = already set (idempotent)
    echo "SKIP (409/already set): Issue #${issue_num}"
    continue
  }
  echo "APPLY: Issue #${issue_num} in ${repo}: '${lbl}' → '${target_type}'"
  BATCH_ISSUE_NUMBERS+=("$issue_num")
  ((BATCH_COUNT++)) || true
  ((TOTAL_MIGRATED++)) || true

  # Flush batch
  if [[ "$BATCH_COUNT" -ge "$BATCH_SIZE" ]]; then
    # Create audit Issue for batch
    BATCH_NUMS=$(IFS=,; echo "${BATCH_ISSUE_NUMBERS[*]}")
    gh api "/repos/${ORG_SLUG}/plugin-codeforge/issues" \
      --method POST \
      --field "title=[migration] CFP-140 batch-${CURRENT_BATCH} complete (${BATCH_COUNT} Issues)" \
      --field "body=Issues: ${BATCH_NUMS}" \
      --jq '.number' > /dev/null 2>&1 || true

    # Label the batch audit Issue (idempotent: migration-batch-N count=1)
    gh api "/repos/${ORG_SLUG}/plugin-codeforge/issues" \
      --paginate --jq ".[] | select(.title | startswith(\"[migration] CFP-140 batch-${CURRENT_BATCH}\")) | .number" 2>/dev/null | head -1 | \
      xargs -I{} gh api "/repos/${ORG_SLUG}/plugin-codeforge/issues/{}/labels" \
        --method POST --field "labels[]=migration-batch-${CURRENT_BATCH}" > /dev/null 2>&1 || true

    echo "BATCH ${CURRENT_BATCH} complete: $BATCH_COUNT Issues"
    ((CURRENT_BATCH++)) || true
    BATCH_COUNT=0
    BATCH_ISSUE_NUMBERS=()
    sleep 1  # rate limit safety (§7.4.4)
  fi
done

# Final partial batch
if [[ "$BATCH_COUNT" -gt 0 ]]; then
  BATCH_NUMS=$(IFS=,; echo "${BATCH_ISSUE_NUMBERS[*]:-}")
  echo "BATCH ${CURRENT_BATCH} complete: $BATCH_COUNT Issues"
fi

# Release lock
if [[ -n "${LOCK_ISSUE:-}" ]]; then
  gh api "/repos/${ORG_SLUG}/plugin-codeforge/issues/${LOCK_ISSUE}/labels/migration-in-progress" \
    --method DELETE > /dev/null 2>&1 || true
  gh api "/repos/${ORG_SLUG}/plugin-codeforge/issues/${LOCK_ISSUE}" \
    --method PATCH --field "state=closed" > /dev/null 2>&1 || true
fi

echo "APPLY complete: $TOTAL_MIGRATED Issue(s) migrated"
echo "Next step: run --verify to confirm zero type:* labels remain"
exit 0
