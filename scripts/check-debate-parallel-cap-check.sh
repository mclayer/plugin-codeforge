#!/usr/bin/env bash
#
# check-debate-parallel-cap-check.sh — lint debate protocol parallel spawn cap declaration
# ADR-109 §결정 4 + ADR-044 Amendment 2 team-spec yaml `parallel_spawn_cap` field
# Warning tier (declaration-only Wave 1, operational phase throttle mechanism)
#
# Usage:
#   bash scripts/check-debate-parallel-cap-check.sh [--team-spec <path>]
#
# Exit codes:
#   0 — lint PASS (cap field present with valid value)
#   1 — lint FAIL (field absent or value invalid)
#   2 — schema error (yaml parse error or file read failure)

set -euo pipefail

# ===== Initialize =====
TEAM_SPECS=()

print_usage() {
  cat >&2 <<EOF
Usage: bash scripts/check-debate-parallel-cap-check.sh [--team-spec <path>]

  --team-spec <path>   Team spec yaml absolute path
                       If omitted, auto-detect 7 templates/**/team-spec-*.yaml

Exit codes:
  0 — PASS (all applicable team-spec files have valid parallel_spawn_cap)
  1 — FAIL (field absent or invalid)
  2 — schema error
EOF
}

# ===== Parse arguments =====
while [ $# -gt 0 ]; do
  case "$1" in
    --team-spec)
      if [ -z "${2:-}" ]; then
        echo "[debate-parallel-cap-check] Error: --team-spec requires argument" >&2
        exit 2
      fi
      TEAM_SPECS=("$2")
      shift 2
      ;;
    *)
      echo "Unknown flag: $1" >&2
      exit 2
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
    echo "[debate-parallel-cap-check] Error: team-spec file not found: $spec_file" >&2
    exit 2
  fi

  # Check presence first (any value type)
  cap_line=$(grep -E "^\s*parallel_spawn_cap:" "$spec_file" | head -1 || true)
  if [ -z "$cap_line" ]; then
    echo "[debate-parallel-cap-check] FAIL: $spec_file missing parallel_spawn_cap field" >&2
    failed=1
    continue
  fi

  # Extract and validate type (must be integer 1-7)
  cap_value=$(echo "$cap_line" | sed -E 's/^[^:]*:\s*([^ #]+).*/\1/')
  if ! [[ "$cap_value" =~ ^[0-9]+$ ]] || [ "$cap_value" -lt 1 ] || [ "$cap_value" -gt 7 ]; then
    echo "[debate-parallel-cap-check] FAIL: $spec_file invalid parallel_spawn_cap value=$cap_value (must be 1-7 integer)" >&2
    failed=1
  else
    echo "[debate-parallel-cap-check] PASS: $spec_file parallel_spawn_cap=$cap_value"
  fi
done

exit "$failed"
