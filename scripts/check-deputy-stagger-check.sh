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

TEAM_SPEC="${1:-}"

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
if [ "$TEAM_SPEC" = "--team-spec" ] && [ -n "${2:-}" ]; then
  TEAM_SPEC="$2"
elif [ -z "$TEAM_SPEC" ]; then
  # Auto-detect from git modified files
  TEAM_SPEC=$(git diff --name-only origin/main... 2>/dev/null | grep "templates/team-spec-.*\.yaml$" | head -1 || echo "")
  if [ -z "$TEAM_SPEC" ]; then
    # Fallback: check all 7 team-spec files
    TEAM_SPECS=(templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml)
  else
    TEAM_SPECS=("$TEAM_SPEC")
  fi
fi

if [ -n "$TEAM_SPEC" ] && [ ! -f "$TEAM_SPEC" ]; then
  echo "[deputy-stagger-check] Error: team-spec file not found: $TEAM_SPEC" >&2
  exit 2
fi

# ===== Set default TEAM_SPECS if not set =====
if [ "${#TEAM_SPECS[@]:-0}" -eq 0 ]; then
  TEAM_SPECS=("$TEAM_SPEC")
fi

# ===== Check all team-spec files =====
failed=0

for spec_file in "${TEAM_SPECS[@]}"; do
  if [ ! -f "$spec_file" ]; then
    echo "[deputy-stagger-check] Warning: team-spec file not found: $spec_file (skipped)" >&2
    continue
  fi

  # Extract spawn_stagger_ms value using grep (pure bash/grep)
  stagger_value=$(grep -E "^\s*spawn_stagger_ms:\s*[0-9]+" "$spec_file" | head -1 | sed -E 's/^[^:]*:\s*([0-9]+).*/\1/' | xargs || echo "")

  if [ -z "$stagger_value" ]; then
    echo "[deputy-stagger-check] FAIL: $spec_file missing spawn_stagger_ms field" >&2
    failed=1
  elif ! [[ "$stagger_value" =~ ^[0-9]+$ ]] || [ "$stagger_value" -lt 0 ] || [ "$stagger_value" -gt 60000 ]; then
    echo "[deputy-stagger-check] FAIL: $spec_file invalid spawn_stagger_ms value=$stagger_value (must be 0-60000 ms)" >&2
    failed=1
  else
    echo "[deputy-stagger-check] PASS: $spec_file spawn_stagger_ms=$stagger_value ms"
  fi
done

exit "$failed"
