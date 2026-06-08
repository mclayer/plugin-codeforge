#!/bin/bash
# inject-allowed-hub-repos.sh
# Idempotent post-reconcile injection of consumer ALLOWED_HUB_REPOS extensions
# into GitHub workflow env vars. ADR-116 consumer-applicability (idempotent reconcile-then-patch).
#
# Mechanism:
#  1. Read consumer .claude/_overlay/project.yaml phase_gate.allowed_hub_repos[]
#  2. For each .github/workflows/*.{yml,yaml} containing ALLOWED_HUB_REPOS env:
#     - Merge template default + project.yaml entries (dedup, never-reduce)
#     - Rewrite env value line (only ALLOWED_HUB_REPOS, rest untouched)
#  3. Idempotent: re-run = same result (dedup guards)
#
# Usage:
#  bash scripts/inject-allowed-hub-repos.sh [--repo <consumer-root>] [--dry-run]
#
# Exit:
#  0 = success (or no-op)
#  1 = error (YAML parse / file not writable / invalid entry format)

set -euo pipefail

REPO_ROOT="${REPO_ROOT:-.}"
DRY_RUN=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse CLI args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_ROOT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      echo "Usage: $0 [--repo <consumer-root>] [--dry-run]" >&2
      exit 1
      ;;
  esac
done

PROJECT_YAML="${REPO_ROOT}/.claude/_overlay/project.yaml"
WORKFLOWS_DIR="${REPO_ROOT}/.github/workflows"

# Validate YAML, extract phase_gate.allowed_hub_repos[]
# Exit 0 if field absent, exit 1 on parse error
extract_allowed_repos() {
  local project_yaml="$1"
  python3 "${SCRIPT_DIR}/lib/extract_allowed_hub_repos.py" "$project_yaml"
}

# Template default ALLOWED_HUB_REPOS value
TEMPLATE_DEFAULT="github.com/mclayer/codeforge-internal-docs"

# Validate repo entry format (domain/owner/repo, e.g. github.com/mclayer/mctrader-hub)
# Positive charset whitelist: only alphanumeric, dot, underscore, hyphen in each segment
validate_repo_entry() {
  local entry="$1"
  # Pattern: 3 segments separated by exactly 2 slashes
  # Each segment: [A-Za-z0-9._-]+ (alphanumeric, dot, underscore, hyphen)
  # Rejects: commas, quotes, spaces, semicolons, newlines, parens, shell metacharacters
  if [[ ! "$entry" =~ ^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$ ]]; then
    echo "WARN: Invalid repo entry format (skip): $entry" >&2
    return 1
  fi
  return 0
}

# Merge template default + project.yaml entries, dedup, output comma-separated
merge_allowed_repos() {
  local project_yaml="$1"
  # Use associative array (bash 4+) to track uniqueness
  declare -A seen
  local -a result

  # Template default first
  result+=("$TEMPLATE_DEFAULT")
  seen["$TEMPLATE_DEFAULT"]=1

  # Project.yaml entries (from extract_allowed_repos)
  if [[ -f "$project_yaml" ]]; then
    while IFS= read -r repo_entry; do
      [[ -z "$repo_entry" ]] && continue
      # Trim leading/trailing whitespace using bash parameter expansion (no xargs)
      repo_entry="${repo_entry#"${repo_entry%%[![:space:]]*}"}"
      repo_entry="${repo_entry%"${repo_entry##*[![:space:]]}"}"
      [[ -z "$repo_entry" ]] && continue
      if validate_repo_entry "$repo_entry"; then
        # Dedup: skip if already seen
        if [[ "${seen[$repo_entry]:-}" != "1" ]]; then
          result+=("$repo_entry")
          seen["$repo_entry"]=1
        fi
      fi
    done < <(extract_allowed_repos "$project_yaml")
  fi

  # Output comma-separated, quoted for YAML env value
  local merged=""
  for repo in "${result[@]}"; do
    if [[ -z "$merged" ]]; then
      merged="$repo"
    else
      merged="${merged},${repo}"
    fi
  done

  echo "$merged"
}

# Inject merged value into workflow env line
# Input: workflow file path, merged value
# Output: rewritten file (or stdout in dry-run)
inject_workflow_env() {
  local workflow_file="$1"
  local merged_value="$2"

  # Find ALLOWED_HUB_REPOS env line, rewrite value only
  # Pattern: ALLOWED_HUB_REPOS: "..." (double-quoted only)
  # Detect quote style mismatch and warn

  if [[ "$DRY_RUN" == 1 ]]; then
    echo "=== DRY-RUN: Would inject into $workflow_file ==="
    sed -n '/^[[:space:]]*ALLOWED_HUB_REPOS:/p' "$workflow_file" || true
    echo "New value: ALLOWED_HUB_REPOS: \"$merged_value\""
    echo ""
  else
    # Check if line exists with double-quotes (expected format)
    if ! grep -q '^[[:space:]]*ALLOWED_HUB_REPOS:[[:space:]]*".*"[[:space:]]*$' "$workflow_file"; then
      # Line with different quote style found, warn but skip rewrite
      if grep -q '^[[:space:]]*ALLOWED_HUB_REPOS:' "$workflow_file"; then
        echo "WARN: ALLOWED_HUB_REPOS line found but value not rewritten (quote style mismatch): $workflow_file" >&2
        return 1
      fi
      return 0
    fi

    # In-place rewrite using AWK
    # Match: ALLOWED_HUB_REPOS: "<anything>" → ALLOWED_HUB_REPOS: "<merged_value>"
    # Use temporary file to avoid sed portability issues
    local tmp_file="${workflow_file}.tmp.$$"

    # AWK to rewrite ALLOWED_HUB_REPOS line only (idempotent safe)
    # Count rewrites by writing count marker to stderr
    awk -v merged="$merged_value" '
      /^[[:space:]]*ALLOWED_HUB_REPOS:[[:space:]]*".*"[[:space:]]*$/ {
        # Preserve indentation
        match($0, /^[[:space:]]*/);
        indent = substr($0, RSTART, RLENGTH);
        printf "%sALLOWED_HUB_REPOS: \"%s\"\n", indent, merged;
        print "REWRITTEN" > "/tmp/rewrite_marker.tmp";
        next;
      }
      { print; }
    ' "$workflow_file" > "$tmp_file"

    # Check if rewrite actually happened
    if [[ ! -f "/tmp/rewrite_marker.tmp" ]]; then
      rm "$tmp_file"
      echo "WARN: ALLOWED_HUB_REPOS line found but value not rewritten (quote style mismatch): $workflow_file" >&2
      return 1
    fi
    rm -f "/tmp/rewrite_marker.tmp"

    mv "$tmp_file" "$workflow_file"
    echo "Injected: $workflow_file"
  fi
}

# Main
main() {
  # No-op if project.yaml absent (consumer not using phase_gate.allowed_hub_repos)
  if [[ ! -f "$PROJECT_YAML" ]]; then
    echo "No $PROJECT_YAML — no-op" >&2
    return 0
  fi

  # Compute merged value
  merged=$(merge_allowed_repos "$PROJECT_YAML")
  if [[ -z "$merged" ]]; then
    echo "No phase_gate.allowed_hub_repos entries — no-op" >&2
    return 0
  fi

  # Find all .github/workflows/*.{yml,yaml} with ALLOWED_HUB_REPOS env
  if [[ ! -d "$WORKFLOWS_DIR" ]]; then
    echo "Workflows directory not found: $WORKFLOWS_DIR — no-op" >&2
    return 0
  fi

  found_any=0
  skipped_count=0
  while IFS= read -r workflow_file; do
    if grep -q '^[[:space:]]*ALLOWED_HUB_REPOS:' "$workflow_file"; then
      if ! inject_workflow_env "$workflow_file" "$merged"; then
        skipped_count=$((skipped_count + 1))
        continue
      fi
      found_any=1
    fi
  done < <(find "$WORKFLOWS_DIR" -maxdepth 1 \( -name "*.yml" -o -name "*.yaml" \))

  if [[ $found_any -eq 0 ]]; then
    echo "No workflows with ALLOWED_HUB_REPOS env found — no-op" >&2
  fi

  return 0
}

main
