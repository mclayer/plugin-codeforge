#!/usr/bin/env bash
# check-workflow-permissions-presence.sh — CFP-530 / ADR-060 Amendment 8 §결정 21
# Mechanical lint: verify top-level `permissions:` block presence in workflow yml files
# Scope: .github/workflows/*.yml + templates/github-workflows/*.yml (*.yml only, exclude *.yaml fixtures)

set -euo pipefail

ROOT="${GITHUB_WORKSPACE:-.}"
WORKFLOW_DIRS=("$ROOT/.github/workflows" "$ROOT/templates/github-workflows")
MISSING=()

for dir in "${WORKFLOW_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then continue; fi
  for file in "$dir"/*.yml; do
    [ -e "$file" ] || continue
    if ! grep -q "^permissions:" "$file"; then
      MISSING+=("$file")
    fi
  done
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "::warning::workflow-permissions-block-presence FAIL — top-level permissions missing in ${#MISSING[@]} file:"
  printf '  %s\n' "${MISSING[@]}"
  exit 1
fi

echo "workflow-permissions-block-presence PASS — all workflow yml have top-level permissions"
exit 0
