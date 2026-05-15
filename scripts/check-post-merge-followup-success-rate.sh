#!/usr/bin/env bash
# check-post-merge-followup-success-rate.sh
# CFP-688 / ADR-026 Amendment 3 §결정 5.G.d — KPI post-detection layer
# ADR-060 §결정 15: exit code 3-tier (0 PASS / 1 breach / 2 setup error)
#
# 기능:
#   gh run list --workflow=post-merge-followup.yml で지난 14일 run 수집.
#   success rate = (success count / total count) * 100.
#   sentinel: ≥ 90% rolling 14-day window.
#
# 출력:
#   stdout: human-readable result + breach status
#   exit 0: sentinel PASS (≥ 90%)
#   exit 1: sentinel breach (< 90%)
#   exit 2: setup error (gh CLI 미설치 / API 오류 / run 0건)
#
# 의존:
#   gh (GitHub CLI) — GH_TOKEN 환경변수 또는 gh auth login 필요
#   jq — JSON 파싱
#
# ADR-026 §7.3 KPI metric SSOT:
#   gh run list --workflow=post-merge-followup.yml --created=>=YYYY-MM-DD --json conclusion

set -uo pipefail

# ── Dependency check ──────────────────────────────────────────────────────────

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found — cannot measure post-merge-followup success rate" >&2
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not found — cannot parse gh run list output" >&2
  exit 2
fi

# ── Configuration ─────────────────────────────────────────────────────────────

WORKFLOW_NAME="post-merge-followup.yml"
SENTINEL_PCT="${SENTINEL_PCT:-90}"  # sentinel threshold (default 90%)
WINDOW_DAYS="${WINDOW_DAYS:-14}"    # rolling window in days

# Compute 14-day-ago date (GNU date fallback BSD date)
SINCE_DATE=$(date -u -d "${WINDOW_DAYS} days ago" '+%Y-%m-%d' 2>/dev/null \
  || date -u -v"-${WINDOW_DAYS}d" '+%Y-%m-%d' 2>/dev/null \
  || echo "")

if [ -z "$SINCE_DATE" ]; then
  echo "ERROR: Cannot compute date offset — GNU date or BSD date required" >&2
  exit 2
fi

echo "Checking ${WORKFLOW_NAME} runs since ${SINCE_DATE} (${WINDOW_DAYS}-day rolling window)…"

# ── Collect run data ──────────────────────────────────────────────────────────

RAW_JSON=$(gh run list \
  --workflow="$WORKFLOW_NAME" \
  --created=">=${SINCE_DATE}" \
  --limit 200 \
  --json conclusion,createdAt \
  2>/dev/null) || {
  echo "ERROR: gh run list API call failed — check GH_TOKEN / repo access" >&2
  exit 2
}

# ── Compute success rate ──────────────────────────────────────────────────────

TOTAL=$(echo "$RAW_JSON" | jq 'length')
if [ "$TOTAL" -eq 0 ]; then
  echo "WARNING: No ${WORKFLOW_NAME} runs found in last ${WINDOW_DAYS} days" >&2
  echo "  Possible causes: workflow not yet deployed / no PR merges in window"
  echo "  Treating as insufficient data — sentinel status: UNKNOWN"
  exit 2
fi

SUCCESS=$(echo "$RAW_JSON" | jq '[.[] | select(.conclusion == "success")] | length')
FAILURE=$(echo "$RAW_JSON" | jq '[.[] | select(.conclusion == "failure")] | length')
OTHER=$((TOTAL - SUCCESS - FAILURE))

# Integer arithmetic (bash) — avoid floating point
# success_pct = SUCCESS * 100 / TOTAL (floor)
SUCCESS_PCT=$(( SUCCESS * 100 / TOTAL ))

echo "Runs in window:"
echo "  Total:   ${TOTAL}"
echo "  Success: ${SUCCESS}"
echo "  Failure: ${FAILURE}"
echo "  Other:   ${OTHER}"
echo "Success rate: ${SUCCESS_PCT}% (sentinel ≥ ${SENTINEL_PCT}%)"

# ── Sentinel evaluation ───────────────────────────────────────────────────────

if [ "$SUCCESS_PCT" -ge "$SENTINEL_PCT" ]; then
  echo "RESULT: PASS — post-merge-followup success rate ${SUCCESS_PCT}% ≥ ${SENTINEL_PCT}%"
  exit 0
else
  echo "RESULT: BREACH — post-merge-followup success rate ${SUCCESS_PCT}% < ${SENTINEL_PCT}%"
  echo "  Action: Investigate recent failures (gh run list --workflow=${WORKFLOW_NAME} --status=failure)"
  echo "  Bypass: hotfix-bypass:post-merge-followup-success-rate label (ADR-024 Amendment 3 §결정 6.A)"
  exit 1
fi
