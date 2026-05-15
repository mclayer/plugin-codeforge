#!/usr/bin/env bash
# CFP-673 / ADR-063 Amendment 3 §결정 13 — marketplace drift scheduled detection
# Scans all 7 codeforge family plugins for mirrored field drift vs mclayer/marketplace.
#
# Usage: bash scripts/check-marketplace-drift.sh
#
# Test override env (5종):
#   CFP673_PLUGINS_OVERRIDE=<comma-list>  — PLUGINS array 강제
#   CFP673_MARKETPLACE_PATH=<local-path>  — marketplace.json local override
#   CFP673_PLUGIN_JSON_DIR=<dir>          — per-plugin plugin.json lookup dir
#   CFP673_API_MOCK_401=1                 — 401 fail-closed 강제
#   CFP673_API_MOCK_429=1                 — 429 fail-open 강제
#   CFP673_API_MOCK_500=1                 — 5xx retry 강제
#   CFP673_SKIP_ISSUE_CREATE=1            — Issue auto-create 차단 (dry-run / TC mode)
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (drift 없음 또는 drift 감지 + Issue auto-create 성공 — warning tier)
#   1 = (reserved, current scope 미사용)
#   2 = SETUP error (missing dependency / 401 auth / 5xx unrecoverable)
#
# Signature dedup: sha256("<plugin>|<field>|<plugin-val>|<market-val>") | head -c 16
# active drift Issue body 안 "signature: <sig>" substring 포함 의무.

set -euo pipefail

# --- PLUGINS 7-tuple (codeforge family) ---
if [[ -n "${CFP673_PLUGINS_OVERRIDE:-}" ]]; then
  IFS=',' read -ra PLUGINS <<< "$CFP673_PLUGINS_OVERRIDE"
else
  PLUGINS=(
    "codeforge"
    "codeforge-requirements"
    "codeforge-design"
    "codeforge-review"
    "codeforge-develop"
    "codeforge-test"
    "codeforge-pmo"
  )
fi

MIRRORED_FIELDS=(name version description author)

# --- Setup verify ---
command -v jq >/dev/null 2>&1 || { echo "[codeforge-kpi-infra-error] check-marketplace-drift: jq not installed"; exit 2; }

# gh CLI 필요 (local override 없을 때만)
if [[ -z "${CFP673_MARKETPLACE_PATH:-}" ]] || [[ -z "${CFP673_PLUGIN_JSON_DIR:-}" ]]; then
  command -v gh >/dev/null 2>&1 || { echo "[codeforge-kpi-infra-error] check-marketplace-drift: gh CLI not installed"; exit 2; }
fi

# --- E-4 mock trigger (test mode) ---
if [[ "${CFP673_API_MOCK_401:-}" == "1" ]]; then
  echo "[codeforge-kpi-infra-error] check-marketplace-drift: 401 Unauthorized (mock) — PAT 인증 실패 (ADR-066 Amendment 2 PAT scope 확인 필요)"
  if [[ "${CFP673_SKIP_ISSUE_CREATE:-}" != "1" ]]; then
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[MARKETPLACE-DRIFT] API auth error — 401 Unauthorized" \
      --body "check-marketplace-drift.sh 가 401 Unauthorized 를 수신했습니다.

CODEFORGE_CROSS_REPO_PAT 만료 또는 scope 부족 가능성.
ADR-066 Amendment 2: marketplace contents:read scope 필요.

[codeforge-kpi-infra-error] CFP-673 / ADR-063 Amendment 3 §결정 13" \
      2>/dev/null || true
  fi
  exit 2
fi

if [[ "${CFP673_API_MOCK_429:-}" == "1" ]]; then
  echo "::warning::check-marketplace-drift: 429 Too Many Requests (mock) — rate limit, skipping run (fail-open)"
  exit 0
fi

if [[ "${CFP673_API_MOCK_500:-}" == "1" ]]; then
  echo "[codeforge-kpi-infra-error] check-marketplace-drift: 5xx server error (mock) — 3회 retry 후 실패"
  if [[ "${CFP673_SKIP_ISSUE_CREATE:-}" != "1" ]]; then
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[MARKETPLACE-DRIFT] API server error — 5xx" \
      --body "check-marketplace-drift.sh 가 5xx 서버 오류를 수신했습니다. 3회 retry 후에도 실패.

[codeforge-kpi-infra-error] CFP-673 / ADR-063 Amendment 3 §결정 13" \
      2>/dev/null || true
  fi
  exit 2
fi

# --- Retry helper (5xx in-run retry 3회, 1s/2s/4s exponential) ---
_gh_api_with_retry() {
  local url="$1"
  local attempt=0
  local delays=(1 2 4)
  while [[ $attempt -lt 3 ]]; do
    local http_code
    local response
    response="$(gh api "$url" 2>&1)" && echo "$response" && return 0
    http_code="$?"
    if echo "$response" | grep -q "429"; then
      echo "::warning::check-marketplace-drift: 429 rate limit on $url — fail-open, skipping run"
      exit 0
    fi
    if echo "$response" | grep -q "401"; then
      echo "[codeforge-kpi-infra-error] check-marketplace-drift: 401 Unauthorized on $url — fail-closed"
      exit 2
    fi
    attempt=$((attempt + 1))
    if [[ $attempt -lt 3 ]]; then
      sleep "${delays[$((attempt-1))]}"
    fi
  done
  echo "[codeforge-kpi-infra-error] check-marketplace-drift: 5xx unrecoverable on $url after 3 retries"
  if [[ "${CFP673_SKIP_ISSUE_CREATE:-}" != "1" ]]; then
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[MARKETPLACE-DRIFT] API server error — $url" \
      --body "check-marketplace-drift.sh 가 '$url' 요청 실패 — 3회 retry 후에도 5xx 오류.

[codeforge-kpi-infra-error] CFP-673 / ADR-063 Amendment 3 §결정 13" \
      2>/dev/null || true
  fi
  exit 2
}

# --- Marketplace JSON 취득 ---
MARKETPLACE_JSON=""
if [[ -n "${CFP673_MARKETPLACE_PATH:-}" ]]; then
  if [[ ! -f "${CFP673_MARKETPLACE_PATH}" ]]; then
    echo "[codeforge-kpi-infra-error] check-marketplace-drift: marketplace override path not found: ${CFP673_MARKETPLACE_PATH}"
    exit 2
  fi
  MARKETPLACE_JSON="$(cat "${CFP673_MARKETPLACE_PATH}")"
else
  MARKETPLACE_RAW="$(_gh_api_with_retry "repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json" 2>/dev/null)" || exit $?
  MARKETPLACE_JSON="$(echo "$MARKETPLACE_RAW" | jq -r '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")"
  if [[ -z "$MARKETPLACE_JSON" ]]; then
    echo "[codeforge-kpi-infra-error] check-marketplace-drift: failed to decode marketplace.json from mclayer/marketplace"
    exit 2
  fi
fi

# jq parse 검증
if ! echo "$MARKETPLACE_JSON" | jq empty 2>/dev/null; then
  echo "[codeforge-kpi-infra-error] check-marketplace-drift: marketplace.json is not valid JSON"
  exit 2
fi

# --- Signature 계산 helper ---
_compute_sig() {
  local plugin="$1" field="$2" plugin_val="$3" market_val="$4"
  printf '%s|%s|%s|%s' "$plugin" "$field" "$plugin_val" "$market_val" | sha256sum | cut -c1-16
}

# sha256sum 존재 확인
if ! command -v sha256sum >/dev/null 2>&1; then
  # macOS fallback
  if command -v shasum >/dev/null 2>&1; then
    sha256sum() { shasum -a 256 "$@"; }
  else
    echo "[codeforge-kpi-infra-error] check-marketplace-drift: sha256sum (or shasum) not found"
    exit 2
  fi
fi

# --- 메인 루프: 7 플러그인 × 4 필드 ---
TOTAL_DRIFT=0

for plugin in "${PLUGINS[@]}"; do
  # plugin.json 취득
  PLUGIN_JSON_CONTENT=""
  if [[ -n "${CFP673_PLUGIN_JSON_DIR:-}" ]]; then
    PLUGIN_JSON_PATH="${CFP673_PLUGIN_JSON_DIR}/${plugin}.json"
    if [[ ! -f "$PLUGIN_JSON_PATH" ]]; then
      echo "::warning::check-marketplace-drift: plugin.json not found at $PLUGIN_JSON_PATH — skipping $plugin"
      continue
    fi
    PLUGIN_JSON_CONTENT="$(cat "$PLUGIN_JSON_PATH")"
  else
    PLUGIN_RAW="$(_gh_api_with_retry "repos/mclayer/plugin-${plugin}/contents/.claude-plugin/plugin.json" 2>/dev/null)" || exit $?
    PLUGIN_JSON_CONTENT="$(echo "$PLUGIN_RAW" | jq -r '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")"
    if [[ -z "$PLUGIN_JSON_CONTENT" ]]; then
      echo "::warning::check-marketplace-drift: failed to decode plugin.json for $plugin — skipping"
      continue
    fi
  fi

  # jq parse 검증
  if ! echo "$PLUGIN_JSON_CONTENT" | jq empty 2>/dev/null; then
    echo "::warning::check-marketplace-drift: plugin.json for $plugin is not valid JSON — skipping"
    continue
  fi

  # marketplace entry 확인
  MARKET_ENTRY="$(echo "$MARKETPLACE_JSON" | jq --arg name "$plugin" '.plugins[] | select(.name == $name)' 2>/dev/null || echo "")"
  if [[ -z "$MARKET_ENTRY" ]]; then
    echo "::warning::check-marketplace-drift: plugin '$plugin' not registered in marketplace.json — skipping"
    continue
  fi

  # 4 mirrored field 비교
  for field in "${MIRRORED_FIELDS[@]}"; do
    PLUGIN_VAL="$(echo "$PLUGIN_JSON_CONTENT" | jq -r ".$field // empty" 2>/dev/null || echo "")"
    MARKET_VAL="$(echo "$MARKET_ENTRY" | jq -r ".$field // empty" 2>/dev/null || echo "")"

    if [[ "$PLUGIN_VAL" != "$MARKET_VAL" ]]; then
      TOTAL_DRIFT=$((TOTAL_DRIFT + 1))
      SIG="$(_compute_sig "$plugin" "$field" "$PLUGIN_VAL" "$MARKET_VAL")"

      echo "::warning::check-marketplace-drift: DRIFT detected — plugin=$plugin field=$field signature=$SIG"
      echo "  plugin.json value:      $(echo "$PLUGIN_JSON_CONTENT" | jq ".$field")"
      echo "  marketplace.json value: $(echo "$MARKET_ENTRY" | jq ".$field")"

      # Signature dedup — active open Issue 확인
      if [[ "${CFP673_SKIP_ISSUE_CREATE:-}" != "1" ]]; then
        ACTIVE_ISSUE="$(gh issue list \
          --repo mclayer/plugin-codeforge \
          --label "drift-detection" \
          --state open \
          --search "\"signature: ${SIG}\"" \
          --limit 1 \
          --json number,title \
          --jq '.[0].number // empty' 2>/dev/null || echo "")"

        if [[ -n "$ACTIVE_ISSUE" ]]; then
          echo "  -> dedup: active Issue #${ACTIVE_ISSUE} already exists for signature ${SIG} — skipping create"
        else
          gh issue create \
            --repo mclayer/plugin-codeforge \
            --label "drift-detection" \
            --title "[MARKETPLACE-DRIFT] plugin=${plugin} field=${field}" \
            --body "## Marketplace drift detected

**Plugin**: \`${plugin}\`
**Field**: \`${field}\`
**Detected**: $(date -u '+%Y-%m-%dT%H:%M:%SZ')

### Values

| Source | Value |
|---|---|
| \`plugin.json\` | $(echo "$PLUGIN_JSON_CONTENT" | jq ".$field") |
| \`marketplace.json\` | $(echo "$MARKET_ENTRY" | jq ".$field") |

### Resolution

ADR-063 Amendment 3 §결정 13 — marketplace sync PR open + merge 의무.
sibling sync window: 24h.

signature: ${SIG}

---
Source: \`scripts/check-marketplace-drift.sh\` (CFP-673 / ADR-063 Amendment 3 §결정 13)" \
            2>/dev/null || echo "  -> Issue create failed (non-fatal, will retry on next run)"
        fi
      fi
    fi
  done
done

# --- 결과 요약 ---
if [[ "$TOTAL_DRIFT" -eq 0 ]]; then
  echo "check-marketplace-drift: PASS — 0 drift across ${#PLUGINS[@]} plugins (${#MIRRORED_FIELDS[@]} fields each)"
else
  echo "check-marketplace-drift: WARNING — ${TOTAL_DRIFT} drift(s) detected across ${#PLUGINS[@]} plugins. Issues auto-created (warning tier, ADR-063 Amendment 3 §결정 13)."
fi

# warning tier — drift 감지 시에도 exit 0 (Issue auto-create 가 통보 channel)
exit 0
