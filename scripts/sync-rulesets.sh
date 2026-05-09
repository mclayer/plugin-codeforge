#!/usr/bin/env bash
# sync-rulesets.sh — CFP-140 / ADR-048
# Sync ruleset JSON specs to GitHub (3-layer: repo/org/enterprise).
# Usage: sync-rulesets.sh [--dry-run] [--apply] [--validate] [--org ORG] [--enterprise SLUG] [--spec-dir DIR]
# Default mode: --dry-run (mutations require explicit --apply)
# Exit codes: 0=ok/no-diff, 2=dry-run would-change, 1=error
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC_DIR="${REPO_ROOT}/templates/rulesets"
MODE="dry-run"
ORG_SLUG=""
ENTERPRISE_SLUG=""
VALIDATE_ONLY=false
RULESET_WARNING_THRESHOLD=68  # 90% of 75 limit

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)    MODE="dry-run";   shift ;;
    --apply)      MODE="apply";     shift ;;
    --validate)   VALIDATE_ONLY=true; shift ;;
    --org)        ORG_SLUG="$2";    shift 2 ;;
    --enterprise) ENTERPRISE_SLUG="$2"; shift 2 ;;
    --spec-dir)   SPEC_DIR="$2";    shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "ERROR: GH_TOKEN not set." >&2
  exit 1
fi

# Strip _-prefixed meta keys (e.g. _schema_version, _description, _enterprise)
# before sending to GitHub API. Writes cleaned JSON to a temp file; caller uses that.
strip_meta_keys() {
  local src="$1"
  local tmp
  tmp=$(mktemp /tmp/ruleset-stripped.XXXXXX.json)
  jq 'with_entries(select(.key | startswith("_") | not))' "$src" > "$tmp"
  echo "$tmp"
}

# --- Validation ---
validate_specs() {
  local errors=0
  local names=()

  for spec_file in "${SPEC_DIR}"/*.json; do
    [[ -f "$spec_file" ]] || continue
    # Skip schema comments (_* fields) — basic JSON validity check
    if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$spec_file" 2>/dev/null; then
      echo "VALIDATE ERROR: invalid JSON: $spec_file" >&2
      ((errors++)) || true
      continue
    fi

    name=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('name',''))" "$spec_file" 2>/dev/null || true)
    if [[ -z "$name" ]]; then
      echo "VALIDATE ERROR: missing 'name' field in $spec_file" >&2
      ((errors++)) || true
      continue
    fi

    # Check duplicate names
    for existing in "${names[@]:-}"; do
      if [[ "$existing" == "$name" ]]; then
        echo "VALIDATE ERROR: duplicate ruleset name '$name' (§5.3 edge case 1)" >&2
        ((errors++)) || true
      fi
    done
    names+=("$name")
  done

  if [[ $errors -gt 0 ]]; then
    echo "Validation failed: $errors error(s)" >&2
    exit 1
  fi
  echo "Validation passed (${#names[@]} ruleset spec(s), no duplicates)"
}

validate_specs

[[ "$VALIDATE_ONLY" == true ]] && exit 0

# --- Drift check ---
check_ruleset_count_warning() {
  local layer="$1"
  local count="$2"
  if [[ "$count" -ge "$RULESET_WARNING_THRESHOLD" ]]; then
    echo "WARNING: $layer ruleset count ($count) >= ${RULESET_WARNING_THRESHOLD} (90% of 75 limit)"
  fi
}

drift_detected=false

# Repo-level (requires --org)
if [[ -f "${SPEC_DIR}/repo-default.json" && -n "$ORG_SLUG" ]]; then
  echo "--- Repo-level rulesets ---"
  LIVE_COUNT=$(gh api "/orgs/${ORG_SLUG}/rulesets" --paginate --jq 'length' 2>/dev/null || echo "0")
  check_ruleset_count_warning "org" "$LIVE_COUNT"

  if [[ "$MODE" == "dry-run" ]]; then
    echo "DRY-RUN: would sync ${SPEC_DIR}/repo-default.json to org ${ORG_SLUG} rulesets"
    drift_detected=true
  else
    # Apply via PUT (create or update by name)
    RULESET_NAME=$(python3 -c "import json; print(json.load(open('${SPEC_DIR}/repo-default.json'))['name'])")
    EXISTING_ID=$(gh api "/orgs/${ORG_SLUG}/rulesets" --paginate \
      --jq ".[] | select(.name==\"${RULESET_NAME}\") | .id" 2>/dev/null || true)

    if [[ -n "$EXISTING_ID" ]]; then
      _stripped=$(strip_meta_keys "${SPEC_DIR}/repo-default.json")
      gh api "/orgs/${ORG_SLUG}/rulesets/${EXISTING_ID}" \
        --method PUT \
        --input "$_stripped" > /dev/null
      rm -f "$_stripped"
      echo "APPLY: updated repo-default ruleset (id=${EXISTING_ID}) in ${ORG_SLUG}"
    else
      _stripped=$(strip_meta_keys "${SPEC_DIR}/repo-default.json")
      gh api "/orgs/${ORG_SLUG}/rulesets" \
        --method POST \
        --input "$_stripped" > /dev/null
      rm -f "$_stripped"
      echo "APPLY: created repo-default ruleset in ${ORG_SLUG}"
    fi
  fi
fi

# Org-level (requires --org)
if [[ -f "${SPEC_DIR}/org-default.json" && -n "$ORG_SLUG" ]]; then
  echo "--- Org-level rulesets ---"
  if [[ "$MODE" == "dry-run" ]]; then
    echo "DRY-RUN: would sync ${SPEC_DIR}/org-default.json to org ${ORG_SLUG}"
    drift_detected=true
  else
    RULESET_NAME=$(python3 -c "import json; print(json.load(open('${SPEC_DIR}/org-default.json'))['name'])")
    EXISTING_ID=$(gh api "/orgs/${ORG_SLUG}/rulesets" --paginate \
      --jq ".[] | select(.name==\"${RULESET_NAME}\") | .id" 2>/dev/null || true)

    if [[ -n "$EXISTING_ID" ]]; then
      _stripped=$(strip_meta_keys "${SPEC_DIR}/org-default.json")
      gh api "/orgs/${ORG_SLUG}/rulesets/${EXISTING_ID}" \
        --method PUT \
        --input "$_stripped" > /dev/null
      rm -f "$_stripped"
      echo "APPLY: updated org-default ruleset (id=${EXISTING_ID}) in ${ORG_SLUG}"
    else
      _stripped=$(strip_meta_keys "${SPEC_DIR}/org-default.json")
      gh api "/orgs/${ORG_SLUG}/rulesets" \
        --method POST \
        --input "$_stripped" > /dev/null
      rm -f "$_stripped"
      echo "APPLY: created org-default ruleset in ${ORG_SLUG}"
    fi
  fi
fi

# Enterprise-level (requires --enterprise)
if [[ -f "${SPEC_DIR}/enterprise-default.json" && -n "$ENTERPRISE_SLUG" ]]; then
  echo "--- Enterprise-level rulesets ---"
  LIVE_COUNT=$(gh api "/enterprises/${ENTERPRISE_SLUG}/rulesets" --paginate --jq 'length' 2>/dev/null || echo "0")
  check_ruleset_count_warning "enterprise" "$LIVE_COUNT"

  if [[ "$MODE" == "dry-run" ]]; then
    echo "DRY-RUN: would sync ${SPEC_DIR}/enterprise-default.json to enterprise ${ENTERPRISE_SLUG}"
    drift_detected=true
  else
    RULESET_NAME=$(python3 -c "import json; print(json.load(open('${SPEC_DIR}/enterprise-default.json'))['name'])")
    EXISTING_ID=$(gh api "/enterprises/${ENTERPRISE_SLUG}/rulesets" --paginate \
      --jq ".[] | select(.name==\"${RULESET_NAME}\") | .id" 2>/dev/null || true)

    if [[ -n "$EXISTING_ID" ]]; then
      _stripped=$(strip_meta_keys "${SPEC_DIR}/enterprise-default.json")
      gh api "/enterprises/${ENTERPRISE_SLUG}/rulesets/${EXISTING_ID}" \
        --method PUT \
        --input "$_stripped" > /dev/null
      rm -f "$_stripped"
      echo "APPLY: updated enterprise-default ruleset (id=${EXISTING_ID}) in ${ENTERPRISE_SLUG}"
    else
      _stripped=$(strip_meta_keys "${SPEC_DIR}/enterprise-default.json")
      gh api "/enterprises/${ENTERPRISE_SLUG}/rulesets" \
        --method POST \
        --input "$_stripped" > /dev/null
      rm -f "$_stripped"
      echo "APPLY: created enterprise-default ruleset in ${ENTERPRISE_SLUG}"
    fi
  fi
fi

if [[ "$MODE" == "dry-run" && "$drift_detected" == true ]]; then
  echo "DRY-RUN complete: drift would be applied. Run with --apply to sync."
  exit 2
fi

echo "sync-rulesets.sh: done (mode=$MODE)"
exit 0
