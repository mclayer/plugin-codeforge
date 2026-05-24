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

TEAM_SPEC="${1:-}"

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
if [ "$TEAM_SPEC" = "--team-spec" ] && [ -n "${2:-}" ]; then
  TEAM_SPEC="$2"
elif [ -z "$TEAM_SPEC" ]; then
  # Auto-detect from git modified files
  TEAM_SPEC=$(git diff --name-only origin/main... 2>/dev/null | grep "templates/team-spec-.*\.yaml$" | head -1 || echo "")
  if [ -z "$TEAM_SPEC" ]; then
    # Fallback: check all 7 team-spec files (Phase 2 likely modifies all)
    TEAM_SPECS=(templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml)
  else
    TEAM_SPECS=("$TEAM_SPEC")
  fi
fi

if [ -n "$TEAM_SPEC" ] && [ ! -f "$TEAM_SPEC" ]; then
  echo "[debate-parallel-cap-check] Error: team-spec file not found: $TEAM_SPEC" >&2
  exit 2
fi

# ===== Set default TEAM_SPECS if not set =====
if [ -z "${TEAM_SPECS[@]:-}" ]; then
  TEAM_SPECS=("$TEAM_SPEC")
fi

# ===== Check all team-spec files =====
failed=0

for spec_file in "${TEAM_SPECS[@]}"; do
  if [ ! -f "$spec_file" ]; then
    echo "[debate-parallel-cap-check] Warning: team-spec file not found: $spec_file (skipped)" >&2
    continue
  fi

  # Extract parallel_spawn_cap value using grep (no jq/yq dependency — pure bash/grep)
  cap_value=$(grep -E "^\s*parallel_spawn_cap:\s*[0-9]+" "$spec_file" | head -1 | awk -F: '{print $2}' | xargs || echo "")

  if [ -z "$cap_value" ]; then
    echo "[debate-parallel-cap-check] FAIL: $spec_file missing parallel_spawn_cap field" >&2
    failed=1
  elif ! [[ "$cap_value" =~ ^[0-9]+$ ]] || [ "$cap_value" -lt 1 ] || [ "$cap_value" -gt 7 ]; then
    echo "[debate-parallel-cap-check] FAIL: $spec_file invalid parallel_spawn_cap value=$cap_value (must be 1-7)" >&2
    failed=1
  else
    echo "[debate-parallel-cap-check] PASS: $spec_file parallel_spawn_cap=$cap_value"
  fi
done

exit "$failed"
