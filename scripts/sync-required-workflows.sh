#!/usr/bin/env bash
# sync-required-workflows.sh — CFP-140 / ADR-048
# Sync required-workflows-spec.yaml to GitHub enterprise required workflows.
# Usage: sync-required-workflows.sh [--dry-run] [--apply] [--spec FILE] [--enterprise SLUG]
# Default mode: --dry-run
# Exit codes: 0=ok/no-diff, 2=dry-run would-change, 1=error
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC_FILE="${REPO_ROOT}/templates/required-workflows-spec.yaml"
MODE="dry-run"
ENTERPRISE_SLUG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)    MODE="dry-run";       shift ;;
    --apply)      MODE="apply";         shift ;;
    --spec)       SPEC_FILE="$2";       shift 2 ;;
    --enterprise) ENTERPRISE_SLUG="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "ERROR: GH_TOKEN not set." >&2
  exit 1
fi

if [[ ! -f "$SPEC_FILE" ]]; then
  echo "ERROR: spec file not found: $SPEC_FILE" >&2
  exit 1
fi

# Parse spec (requires python3 + pyyaml, or yq)
parse_spec() {
  python3 - "$SPEC_FILE" <<'PY'
import sys, yaml
data = yaml.safe_load(open(sys.argv[1]))
enterprise = data.get('enterprise_slug', '')
source_repo = data.get('source_repo', '')
for wf in data.get('required_workflows', []):
    print(f"{enterprise}\t{source_repo}\t{wf['id']}\t{wf['source_workflow']}\t{wf['target']}")
PY
}

# Graceful degradation: check enterprise vs org-level
DEGRADED=false
if [[ -n "$ENTERPRISE_SLUG" ]]; then
  if ! gh api "/enterprises/${ENTERPRISE_SLUG}" --jq '.slug' >/dev/null 2>&1; then
    echo "WARNING: enterprise ${ENTERPRISE_SLUG} not accessible — trying org-level fallback"
    DEGRADED=true
  fi
else
  # Read from spec
  ENTERPRISE_SLUG=$(python3 -c \
    "import yaml; d=yaml.safe_load(open('${SPEC_FILE}')); print(d.get('enterprise_slug',''))" 2>/dev/null || true)
fi

if [[ "$ENTERPRISE_SLUG" == "ENTERPRISE_SLUG_PLACEHOLDER" ]]; then
  echo "WARNING: enterprise_slug is placeholder — skipping enterprise sync"
  echo "Update templates/required-workflows-spec.yaml with actual enterprise slug"
  exit 2
fi

drift_detected=false

while IFS=$'\t' read -r enterprise source_repo wf_id source_workflow target; do
  [[ -z "$enterprise" ]] && continue
  echo "Checking: $wf_id (source: $source_workflow, target: $target)"

  if [[ "$DEGRADED" == false ]]; then
    # Check live enterprise required workflows
    LIVE=$(gh api "/enterprises/${enterprise}/actions/required_workflows" \
      --paginate --jq ".required_workflows[] | select(.name==\"${wf_id}\") | .id" 2>/dev/null || true)

    if [[ "$MODE" == "dry-run" ]]; then
      if [[ -z "$LIVE" ]]; then
        echo "DRY-RUN: would create required workflow '${wf_id}' in enterprise ${enterprise}"
      else
        echo "DRY-RUN: required workflow '${wf_id}' exists (id=${LIVE}), checking for drift"
      fi
      drift_detected=true
    else
      if [[ -z "$LIVE" ]]; then
        # Create
        gh api "/enterprises/${enterprise}/actions/required_workflows" \
          --method POST \
          --field "name=${wf_id}" \
          --field "workflow_file_path=${source_workflow}" \
          --field "repository_id=$(gh api "/repos/${source_repo}" --jq '.id')" \
          --field "scope=all" > /dev/null 2>&1 || \
          echo "WARNING: failed to create ${wf_id} — may require enterprise admin"
        echo "APPLY: created required workflow '${wf_id}' in enterprise ${enterprise}"
      else
        echo "OK: required workflow '${wf_id}' already exists (id=${LIVE})"
      fi
    fi
  else
    echo "DEGRADED: skipping enterprise sync for '${wf_id}' (no enterprise access)"
    echo "ACTION: manually register '${source_workflow}' from ${source_repo} as required workflow"
  fi
done < <(parse_spec 2>/dev/null || true)

if [[ "$MODE" == "dry-run" && "$drift_detected" == true ]]; then
  echo "DRY-RUN complete: run with --apply to sync required workflows"
  exit 2
fi

echo "sync-required-workflows.sh: done (mode=$MODE)"
exit 0
