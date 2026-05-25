#!/usr/bin/env bash
# CFP-1367 / ADR-107 Amendment 1 §결정 2 — F2 design-lane-plugin-feasibility-check
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_design_lane_plugin_feasibility.py SSOT)
# ADR-060 §결정 5 — warning-tier (exit 0 항상 for warnings, PR merge 미차단)
#
# Usage:
#   bash scripts/check-design-lane-plugin-feasibility.sh --doc-file <story-or-changeplan-path>
#
# Bypass channel: HOTFIX_BYPASS_DESIGN_LANE_PLUGIN_FEASIBILITY=1 env
#   → 즉시 exit 0 (hotfix-bypass:design-lane-plugin-feasibility label 부착 시 workflow 에서 주입)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier)
#   1 — malformed 감지 (genuine lint error)
#   2 — setup error (파일 없음 등)
set -euo pipefail

SCRIPT_NAME="[design-feasibility-lint]"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS="${HOTFIX_BYPASS_DESIGN_LANE_PLUGIN_FEASIBILITY:-}"
if [[ "$BYPASS" == "1" ]]; then
  echo "$SCRIPT_NAME BYPASS=1 — skip" >&2
  exit 0
fi

# ── Python SSOT 위임 (exit-code passthrough) ─────────────────────────────────
exec python3 "$SCRIPT_DIR/lib/check_design_lane_plugin_feasibility.py" "$@"
