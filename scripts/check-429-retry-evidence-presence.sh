#!/usr/bin/env bash
#
# check-429-retry-evidence-presence.sh — lint 429 retry evidence marker presence
# ADR-109 §결정 8.1 + evidence-checks-registry 3 신규 entry
# Warning tier (declaration-only Wave 1, operational phase telemetry)
#
# Usage:
#   bash scripts/check-429-retry-evidence-presence.sh [--doc-file <path>]
#
# Exit codes:
#   0 — lint PASS (marker found or story file not applicable)
#   1 — lint FAIL (story §14 Lane Evidence 안 429 marker absent)
#   2 — schema error (story file 읽기 실패 또는 YAML parse error)

set -euo pipefail

DOC_FILE="${1:-}"

print_usage() {
  cat >&2 <<EOF
Usage: bash scripts/check-429-retry-evidence-presence.sh [--doc-file <path>]

  --doc-file <path>   Story file absolute path (e.g., docs/stories/CFP-1354.md)
                       If omitted, auto-detect from git changes (requires git repo)

Exit codes:
  0 — PASS
  1 — FAIL (marker absent in §14)
  2 — schema error
EOF
}

# ===== Parse arguments =====
if [ "$DOC_FILE" = "--doc-file" ] && [ -n "${2:-}" ]; then
  DOC_FILE="$2"
elif [ -z "$DOC_FILE" ]; then
  # Auto-detect from git modified files (Phase 2 PR context)
  DOC_FILE=$(git diff --name-only origin/main... 2>/dev/null | grep "^docs/stories/.*\.md$" | head -1 || echo "")
  if [ -z "$DOC_FILE" ]; then
    echo "[429-retry-evidence-presence] No story file detected (likely non-story PR). PASS."
    exit 0
  fi
fi

if [ ! -f "$DOC_FILE" ]; then
  echo "[429-retry-evidence-presence] Error: story file not found: $DOC_FILE" >&2
  exit 2
fi

# ===== Extract §14 Lane Evidence section =====
# Story file format: §14 starts with "## §14 Lane Evidence" and goes until next "##" or EOF
section_14=$(sed -n '/^## §14 Lane Evidence$/,/^##/p' "$DOC_FILE" | head -n -1)

if [ -z "$section_14" ]; then
  echo "[429-retry-evidence-presence] Warning: §14 Lane Evidence section not found in $DOC_FILE (likely early-stage story). PASS."
  exit 0
fi

# ===== Check for 429 marker pattern =====
# Pattern: [429-auto-retry: count=<digits>, final_status=success|failed]
pattern='\[429-auto-retry: count=[0-9]+, final_status=(success|failed)\]'

if echo "$section_14" | grep -qE "$pattern"; then
  echo "[429-retry-evidence-presence] PASS: 429 marker found in §14"
  exit 0
else
  # Fallback check: story has any 429 reference?
  if echo "$section_14" | grep -qi "429"; then
    echo "[429-retry-evidence-presence] FAIL: §14 mentions 429 but marker format invalid. Expected: [429-auto-retry: count=N, final_status=success|failed]" >&2
    exit 1
  fi

  # Pure absence
  echo "[429-retry-evidence-presence] FAIL: §14 Lane Evidence missing 429 marker. If story involves API rate-limit incident, add [429-auto-retry: count=N, final_status=success|failed] to transcript field." >&2
  exit 1
fi
