#!/usr/bin/env bash
#
# check-deputy-stagger-check.sh — lint deputy fan-out stagger declaration
# ADR-109 §결정 4 + ADR-044 Amendment 2 team-spec yaml `spawn_stagger_ms` field
# Warning tier (declaration-only Wave 1, operational phase throttle mechanism)
#
# Usage:
#   bash scripts/check-deputy-stagger-check.sh [--team-spec <path>]
#
# Exit codes:
#   0 — lint PASS (stagger field present with valid value)
#   1 — lint FAIL (field absent or value invalid)
#   2 — schema error (yaml parse error or file read failure)

set -euo pipefail

# ===== Initialize =====
TEAM_SPECS=()

print_usage() {
  cat >&2 <<EOF
Usage: bash scripts/check-deputy-stagger-check.sh [--team-spec <path>]

  --team-spec <path>   Team spec yaml absolute path
                       If omitted, auto-detect 7 templates/**/team-spec-*.yaml

Exit codes:
  0 — PASS (all applicable team-spec files have valid spawn_stagger_ms)
  1 — FAIL (field absent or invalid)
  2 — schema error
EOF
}

# ===== Parse arguments =====
while [ $# -gt 0 ]; do
  case "$1" in
    --team-spec)
      if [ -z "${2:-}" ]; then
        echo "[deputy-stagger-check] Error: --team-spec requires argument" >&2
        exit 2
      fi
      TEAM_SPECS=("$2")
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# ===== Auto-detect if not specified =====
if [ "${#TEAM_SPECS[@]}" -eq 0 ]; then
  # Try git diff first
  git_modified=$(git diff --name-only origin/main... 2>/dev/null | grep "templates/team-spec-.*\.yaml$" || echo "")
  if [ -n "$git_modified" ]; then
    while IFS= read -r f; do
      TEAM_SPECS+=("$f")
    done <<< "$git_modified"
  else
    # Fallback: check all 7 templates
    TEAM_SPECS=(templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml)
  fi
fi

# ===== Check all team-spec files =====
failed=0

for spec_file in "${TEAM_SPECS[@]}"; do
  if [ ! -f "$spec_file" ]; then
    echo "[deputy-stagger-check] Error: team-spec file not found: $spec_file" >&2
    exit 2
  fi

  # Check presence first (any value type)
  stagger_line=$(grep -E "^\s*spawn_stagger_ms:" "$spec_file" | head -1 || true)
  if [ -z "$stagger_line" ]; then
    echo "[deputy-stagger-check] FAIL: $spec_file missing spawn_stagger_ms field" >&2
    failed=1
    continue
  fi

  # Extract and validate type (must be integer 0-60000)
  stagger_value=$(echo "$stagger_line" | sed -E 's/^[^:]*:\s*([^ #]+).*/\1/')
  if ! [[ "$stagger_value" =~ ^[0-9]+$ ]] || [ "$stagger_value" -lt 0 ] || [ "$stagger_value" -gt 60000 ]; then
    echo "[deputy-stagger-check] FAIL: $spec_file invalid spawn_stagger_ms value=$stagger_value (must be 0-60000 ms integer)" >&2
    failed=1
  else
    echo "[deputy-stagger-check] PASS: $spec_file spawn_stagger_ms=$stagger_value ms"
  fi
done

exit "$failed"
