#!/usr/bin/env bash
# scripts/lib/gh-api-helpers.sh — shared gh API retry helper
#
# CFP-954 (D1 consensus) — extract _gh_api_with_retry from 3-way WET:
#   - scripts/check-marketplace-drift.sh L91-125 (CFP-673)
#   - scripts/check-channel-drift.sh L99-133  (CFP-932)
#   - scripts/check-production-cutover-evidence.sh (CFP-954 신규)
#
# Single-mandate: 401/429/5xx 분기 + Issue auto-create dedup signature pattern.
# Caller 식별자 = $1 (URL) + ${_GH_HELPER_CALLER:-}{check-marketplace-drift / check-channel-drift / check-production-cutover-evidence} prefix.
#
# Test override env (CBL_* namespace, ADR-040 Amendment 6 §결정 7.D probe sandbox env scoping):
#   CBL_SKIP_ISSUE_CREATE=1   — Issue auto-create 차단 (dry-run / TC mode)
#
# Legacy override (backward-compat — existing CFP-namespaced):
#   CFP673_SKIP_ISSUE_CREATE / CFP932_SKIP_ISSUE_CREATE / CFP954_SKIP_ISSUE_CREATE
#
# Exit codes (ADR-060 §결정 15 3-tier 정합):
#   helper 자체 = source 후 _gh_api_with_retry 함수 호출 시 stdout 출력 + exit code 0/2 반환.
#   caller script 가 wrapping `|| exit $?` 로 error propagate.

# Idempotent source guard (multi-source 시 redefine 회피)
if declare -f _gh_api_with_retry >/dev/null 2>&1; then
  return 0
fi

# --- Combined SKIP_ISSUE_CREATE check (CBL primary + CFP-namespaced fallback) ---
_should_skip_issue_create() {
  if [[ -n "${CBL_SKIP_ISSUE_CREATE:-}" ]] \
     || [[ -n "${CFP673_SKIP_ISSUE_CREATE:-}" ]] \
     || [[ -n "${CFP932_SKIP_ISSUE_CREATE:-}" ]] \
     || [[ -n "${CFP954_SKIP_ISSUE_CREATE:-}" ]]; then
    return 0
  fi
  return 1
}

# --- 5xx in-run retry helper (3 attempts, 1s/2s/4s exponential) ---
# Usage: response="$(_gh_api_with_retry "<url>" "<caller-prefix>")"
#   $1 = gh api URL (예: "repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json")
#   $2 = caller prefix (echo / Issue title 식별자, 예: "check-marketplace-drift")
_gh_api_with_retry() {
  local url="$1"
  local caller="${2:-${_GH_HELPER_CALLER:-gh-api-helpers}}"
  local attempt=0
  local delays=(1 2 4)
  while [[ $attempt -lt 3 ]]; do
    local response
    response="$(gh api "$url" 2>&1)" && echo "$response" && return 0
    if echo "$response" | grep -q "429"; then
      echo "::warning::${caller}: 429 rate limit on $url — fail-open, skipping run" >&2
      exit 0
    fi
    if echo "$response" | grep -q "401"; then
      echo "[codeforge-kpi-infra-error] ${caller}: 401 Unauthorized on $url — fail-closed" >&2
      exit 2
    fi
    attempt=$((attempt + 1))
    if [[ $attempt -lt 3 ]]; then
      sleep "${delays[$((attempt-1))]}"
    fi
  done
  echo "[codeforge-kpi-infra-error] ${caller}: 5xx unrecoverable on $url after 3 retries" >&2
  if ! _should_skip_issue_create; then
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[${caller^^}] API server error — $url" \
      --body "${caller}.sh 가 '$url' 요청 실패 — 3회 retry 후에도 5xx 오류.

[codeforge-kpi-infra-error] gh-api-helpers (CFP-954 D1 consensus)" \
      2>/dev/null || true
  fi
  exit 2
}
