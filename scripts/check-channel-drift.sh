#!/usr/bin/env bash
# check-channel-drift.sh — CFP-932 Wave 4 sub-Epic #882 Story-2 — D5 channel drift detection
#
# ADR-063 Amendment 3 §결정 13 — channel drift scheduled detection (3-tuple)
# check-marketplace-drift.sh precedent byte-pattern 답습 (DC-2 verbatim reuse)
#
# 3-tuple drift:
#   (a) consumer .claude/_overlay/project.yaml codeforge.channel.tier
#   (b) install .claude-plugin/plugin.json .version → channels[*] tier 매핑
#   (c) registry marketplace.json plugins[name=codeforge].channels[*].versions[] membership tier
#
# Usage: bash scripts/check-channel-drift.sh
#
# Test override env (CFP932_* namespace — DC-3, CFP-843 §3.3):
#   CFP932_PLUGINS_OVERRIDE=<comma-list>    — PLUGINS array 강제
#   CFP932_MARKETPLACE_PATH=<local-path>    — marketplace.json local override
#   CFP932_PLUGIN_JSON_DIR=<dir>            — per-plugin plugin.json lookup dir
#   CFP932_API_MOCK_401=1                   — 401 fail-closed 강제
#   CFP932_API_MOCK_429=1                   — 429 fail-open 강제
#   CFP932_API_MOCK_500=1                   — 5xx retry 강제
#   CFP932_SKIP_ISSUE_CREATE=1              — Issue auto-create 차단 (dry-run / TC mode)
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (drift 없음 또는 drift 감지 + Issue auto-create 성공 — warning tier)
#   1 = (reserved, current scope 미사용)
#   2 = SETUP error (missing dependency / 401 auth / 5xx unrecoverable)
#
# Signature dedup: sha256("<plugin>|channel|<consumer-tier>|<registry-tier>") | head -c 16
# active drift Issue body 안 "signature: <sig>" substring 포함 의무.

set -euo pipefail

# --- PLUGINS 7-tuple (codeforge family) ---
if [[ -n "${CFP932_PLUGINS_OVERRIDE:-}" ]]; then
  IFS=',' read -ra PLUGINS <<< "$CFP932_PLUGINS_OVERRIDE"
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

# --- Setup verify ---
command -v jq >/dev/null 2>&1 || { echo "[codeforge-kpi-infra-error] check-channel-drift: jq not installed"; exit 2; }

# gh CLI 필요 (local override 없을 때만)
if [[ -z "${CFP932_MARKETPLACE_PATH:-}" ]] || [[ -z "${CFP932_PLUGIN_JSON_DIR:-}" ]]; then
  command -v gh >/dev/null 2>&1 || { echo "[codeforge-kpi-infra-error] check-channel-drift: gh CLI not installed"; exit 2; }
fi

# --- E-4 mock trigger (test mode) — check-marketplace-drift.sh verbatim 차용 (DC-2) ---
if [[ "${CFP932_API_MOCK_401:-}" == "1" ]]; then
  echo "[codeforge-kpi-infra-error] check-channel-drift: 401 Unauthorized (mock) — PAT 인증 실패 (ADR-066 Amendment 2 PAT scope 확인 필요)"
  if [[ "${CFP932_SKIP_ISSUE_CREATE:-}" != "1" ]]; then
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[CHANNEL-DRIFT] API auth error — 401 Unauthorized" \
      --body "check-channel-drift.sh 가 401 Unauthorized 를 수신했습니다.

CODEFORGE_CROSS_REPO_PAT 만료 또는 scope 부족 가능성.
ADR-066 Amendment 2: marketplace contents:read scope 필요.

[codeforge-kpi-infra-error] CFP-932 / ADR-063 Amendment 3 §결정 13" \
      2>/dev/null || true
  fi
  exit 2
fi

if [[ "${CFP932_API_MOCK_429:-}" == "1" ]]; then
  echo "::warning::check-channel-drift: 429 Too Many Requests (mock) — rate limit, skipping run (fail-open)"
  exit 0
fi

if [[ "${CFP932_API_MOCK_500:-}" == "1" ]]; then
  echo "[codeforge-kpi-infra-error] check-channel-drift: 5xx server error (mock) — 3회 retry 후 실패"
  if [[ "${CFP932_SKIP_ISSUE_CREATE:-}" != "1" ]]; then
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[CHANNEL-DRIFT] API server error — 5xx" \
      --body "check-channel-drift.sh 가 5xx 서버 오류를 수신했습니다. 3회 retry 후에도 실패.

[codeforge-kpi-infra-error] CFP-932 / ADR-063 Amendment 3 §결정 13" \
      2>/dev/null || true
  fi
  exit 2
fi

# --- Retry helper (5xx in-run retry 3회, 1s/2s/4s exponential) ---
# check-marketplace-drift.sh:90-125 _gh_api_with_retry verbatim 차용 (DC-2 §7.4.4)
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
      echo "::warning::check-channel-drift: 429 rate limit on $url — fail-open, skipping run"
      exit 0
    fi
    if echo "$response" | grep -q "401"; then
      echo "[codeforge-kpi-infra-error] check-channel-drift: 401 Unauthorized on $url — fail-closed"
      exit 2
    fi
    attempt=$((attempt + 1))
    if [[ $attempt -lt 3 ]]; then
      sleep "${delays[$((attempt-1))]}"
    fi
  done
  echo "[codeforge-kpi-infra-error] check-channel-drift: 5xx unrecoverable on $url after 3 retries"
  if [[ "${CFP932_SKIP_ISSUE_CREATE:-}" != "1" ]]; then
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[CHANNEL-DRIFT] API server error — $url" \
      --body "check-channel-drift.sh 가 '$url' 요청 실패 — 3회 retry 후에도 5xx 오류.

[codeforge-kpi-infra-error] CFP-932 / ADR-063 Amendment 3 §결정 13" \
      2>/dev/null || true
  fi
  exit 2
}

# --- Marketplace JSON 취득 ---
MARKETPLACE_JSON=""
if [[ -n "${CFP932_MARKETPLACE_PATH:-}" ]]; then
  if [[ ! -f "${CFP932_MARKETPLACE_PATH}" ]]; then
    echo "[codeforge-kpi-infra-error] check-channel-drift: marketplace override path not found: ${CFP932_MARKETPLACE_PATH}"
    exit 2
  fi
  MARKETPLACE_JSON="$(cat "${CFP932_MARKETPLACE_PATH}")"
else
  MARKETPLACE_RAW="$(_gh_api_with_retry "repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json" 2>/dev/null)" || exit $?
  MARKETPLACE_JSON="$(echo "$MARKETPLACE_RAW" | jq -r '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")"
  if [[ -z "$MARKETPLACE_JSON" ]]; then
    echo "[codeforge-kpi-infra-error] check-channel-drift: failed to decode marketplace.json from mclayer/marketplace"
    exit 2
  fi
fi

# jq parse 검증
if ! echo "$MARKETPLACE_JSON" | jq empty 2>/dev/null; then
  echo "[codeforge-kpi-infra-error] check-channel-drift: marketplace.json is not valid JSON"
  exit 2
fi

# --- channels[] populate 여부 확인 (Story-4 전 = graceful unknown, OQ-1 / INV-8) ---
CHANNELS_POPULATED=0
for plugin in "${PLUGINS[@]}"; do
  COUNT="$(echo "$MARKETPLACE_JSON" | jq --arg name "$plugin" \
    '[.plugins[] | select(.name == $name)] | .[0].channels // [] | length' 2>/dev/null || echo "0")"
  if [[ "${COUNT:-0}" -gt 0 ]]; then
    CHANNELS_POPULATED=1
    break
  fi
done

if [[ "${CHANNELS_POPULATED}" -eq 0 ]]; then
  echo "::warning::check-channel-drift: marketplace.json channels[] 미populate (Story-4 전) — graceful warning exit 0 (INV-8)"
  echo "check-channel-drift: PASS (warning) — channels[] not yet populated (Story-4 carrier). consumer tier drift detection pending."
  exit 0
fi

# --- sha256sum 존재 확인 ---
if ! command -v sha256sum >/dev/null 2>&1; then
  if command -v shasum >/dev/null 2>&1; then
    sha256sum() { shasum -a 256 "$@"; }
  else
    echo "[codeforge-kpi-infra-error] check-channel-drift: sha256sum (or shasum) not found"
    exit 2
  fi
fi

# --- Signature 계산 helper ---
# signature = sha256("<plugin>|channel|<consumer-tier>|<registry-tier>") | head -c 16
_compute_sig() {
  local plugin="$1" consumer_tier="$2" registry_tier="$3"
  printf '%s|channel|%s|%s' "$plugin" "$consumer_tier" "$registry_tier" | sha256sum | cut -c1-16
}

# --- consumer project.yaml tier 취득 helper (yaml_oracle.py 미사용 — shell inline for drift script) ---
_get_consumer_tier() {
  local project_yaml="${1:-}"
  if [[ -z "${project_yaml}" ]] || [[ ! -f "${project_yaml}" ]]; then
    echo "absent"
    return 0
  fi
  # python3 yaml.safe_load inline (ADR-061 §결정 5 — 5줄 이하 허용)
  python3 - "${project_yaml}" 2>/dev/null <<'PYEOF' || echo "unknown"
import sys, yaml
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
codeforge = (data or {}).get("codeforge", {}) or {}
channel = codeforge.get("channel") or {}
tier = (channel if isinstance(channel, dict) else {}).get("tier", "stable")
print(tier)
PYEOF
}

# --- 메인 루프: PLUGINS × 3-tuple drift ---
TOTAL_DRIFT=0

for plugin in "${PLUGINS[@]}"; do
  # (a) consumer tier
  CONSUMER_TIER="stable"  # derived default (missing overlay = stable, INV-8)
  # Note: consumer project.yaml path lookup is environment-dependent
  # In CI context, CODEFORGE_CONSUMER_YAML_PATH env for override
  if [[ -n "${CODEFORGE_CONSUMER_YAML_PATH:-}" ]]; then
    CONSUMER_TIER="$(_get_consumer_tier "${CODEFORGE_CONSUMER_YAML_PATH}")"
  fi

  # (b) install plugin.json .version → tier 매핑
  INSTALL_VERSION=""
  if [[ -n "${CFP932_PLUGIN_JSON_DIR:-}" ]]; then
    PLUGIN_JSON_PATH="${CFP932_PLUGIN_JSON_DIR}/${plugin}.json"
    if [[ -f "$PLUGIN_JSON_PATH" ]]; then
      INSTALL_VERSION="$(jq -r '.version // empty' "$PLUGIN_JSON_PATH" 2>/dev/null || echo "")"
    fi
  else
    PLUGIN_RAW="$(_gh_api_with_retry "repos/mclayer/plugin-${plugin}/contents/.claude-plugin/plugin.json" 2>/dev/null)" || continue
    INSTALL_JSON="$(echo "$PLUGIN_RAW" | jq -r '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")"
    if [[ -n "${INSTALL_JSON}" ]]; then
      INSTALL_VERSION="$(echo "$INSTALL_JSON" | jq -r '.version // empty' 2>/dev/null || echo "")"
    fi
  fi

  # (c) registry marketplace.json channels[*].versions[] membership
  REGISTRY_TIER="unknown"
  if [[ -n "${INSTALL_VERSION}" ]]; then
    for tier in stable beta canary; do
      MATCHED="$(echo "$MARKETPLACE_JSON" | jq --arg name "$plugin" --arg tier "$tier" --arg ver "$INSTALL_VERSION" \
        '[.plugins[] | select(.name == $name)] | .[0].channels // [] | .[] | select(.tier == $tier) | .versions // [] | .[] | select(. == $ver)' \
        2>/dev/null || echo "")"
      if [[ -n "${MATCHED}" ]]; then
        REGISTRY_TIER="${tier}"
        break
      fi
    done
  fi

  # drift check: consumer vs registry
  if [[ "${CONSUMER_TIER}" != "${REGISTRY_TIER}" ]] && [[ "${REGISTRY_TIER}" != "unknown" ]]; then
    TOTAL_DRIFT=$((TOTAL_DRIFT + 1))
    SIG="$(_compute_sig "$plugin" "$CONSUMER_TIER" "$REGISTRY_TIER")"

    echo "::warning::check-channel-drift: DRIFT detected — plugin=$plugin consumer_tier=$CONSUMER_TIER registry_tier=$REGISTRY_TIER signature=$SIG"

    # Signature dedup — active open Issue 확인
    if [[ "${CFP932_SKIP_ISSUE_CREATE:-}" != "1" ]]; then
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
          --title "[CHANNEL-DRIFT] plugin=${plugin} consumer_tier=${CONSUMER_TIER} registry_tier=${REGISTRY_TIER}" \
          --body "## Channel drift detected

**Plugin**: \`${plugin}\`
**Consumer tier**: \`${CONSUMER_TIER}\`
**Registry tier**: \`${REGISTRY_TIER}\`
**Install version**: \`${INSTALL_VERSION:-unknown}\`
**Detected**: $(date -u '+%Y-%m-%dT%H:%M:%SZ')

### 3-tuple drift

| leg | value |
|---|---|
| (a) consumer overlay | \`${CONSUMER_TIER}\` |
| (b) install version tier | \`${INSTALL_VERSION:-unknown}\` → \`${REGISTRY_TIER}\` |
| (c) registry membership | \`${REGISTRY_TIER}\` |

### Resolution

ADR-076 §결정 9 — channel pin invariant: consumer overlay ↔ registry tier alignment 의무.
Story-4 전: registry channels[] 미populate = transitional valid (graceful unknown, INV-8).

signature: ${SIG}

---
Source: \`scripts/check-channel-drift.sh\` (CFP-932 / ADR-063 Amendment 3 §결정 13)" \
          2>/dev/null || echo "  -> Issue create failed (non-fatal, will retry on next run)"
      fi
    fi
  fi
done

# --- 결과 요약 ---
if [[ "$TOTAL_DRIFT" -eq 0 ]]; then
  echo "check-channel-drift: PASS — 0 drift across ${#PLUGINS[@]} plugins"
else
  echo "check-channel-drift: WARNING — ${TOTAL_DRIFT} drift(s) detected across ${#PLUGINS[@]} plugins. Issues auto-created (warning tier, ADR-063 Amendment 3 §결정 13)."
fi

# warning tier — drift 감지 시에도 exit 0 (Issue auto-create 가 통보 channel)
exit 0
