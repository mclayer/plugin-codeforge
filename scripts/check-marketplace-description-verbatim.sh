#!/usr/bin/env bash
# CFP-631 / ADR-063 Amendment 2 §결정 11 — marketplace description verbatim lint
#
# wrapper plugin.json description ↔ marketplace.json plugins[codeforge].description
# byte-identical 비교 (PR-time blocking-on-pr enforcement).
#
# 배경:
#   - ADR-016 mirrored field 4종 (name/version/description/author) 중 description 단독 enforce
#   - version = check-version-bump-atomic.sh cover
#   - name/author = check-marketplace-parity.sh warning sufficient
#   - description = 12k+ 자 장문, 편집 실수 가능성 높음 → 별도 blocking-on-pr enforce
#   - 6 sample 누적 drift evidence (CFP-387/393/423/597/612/619, CFP-619 retro §5.2 SSOT)
#
# 알고리즘 (Change Plan §3.1 / Story §3.1 verbatim):
#   1. wrapper plugin.json description 추출 (jq raw string)
#   2. marketplace.json plugins[codeforge].description 추출 (gh api fetch 또는 로컬 override)
#   3. byte-identical compare (trailing newline normalize 후 비교)
#   4. 불일치 시 diff 출력 (첫 200자 + 길이 비교)
#
# 환경 변수:
#   CFP631_MARKETPLACE_PATH  — 테스트 override: 로컬 marketplace.json 경로
#   CFP631_PLUGIN_JSON       — 테스트 override: 로컬 plugin.json 경로 (default: .claude-plugin/plugin.json)
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (byte-identical)
#   1 = DRIFT (description 불일치)
#   2 = SETUP error (파일 없음 / jq 없음 / gh 없음 / fetch 실패 등)

set -euo pipefail

PLUGIN_JSON="${CFP631_PLUGIN_JSON:-.claude-plugin/plugin.json}"
MARKETPLACE_OVERRIDE="${CFP631_MARKETPLACE_PATH:-}"

# --- 1. Setup verify ---
command -v jq >/dev/null 2>&1 || {
  echo "❌ marketplace-description-verbatim: jq not installed"
  exit 2
}

if [[ ! -f "$PLUGIN_JSON" ]]; then
  echo "❌ marketplace-description-verbatim: plugin.json not found at $PLUGIN_JSON"
  exit 2
fi

# --- 2. Extract wrapper plugin.json description ---
PLUGIN_DESC="$(jq -r '.description // empty' "$PLUGIN_JSON")"
if [[ -z "$PLUGIN_DESC" ]]; then
  echo "❌ marketplace-description-verbatim: plugin.json has no .description field"
  exit 2
fi

PLUGIN_NAME="$(jq -r '.name // empty' "$PLUGIN_JSON")"
if [[ -z "$PLUGIN_NAME" ]]; then
  echo "❌ marketplace-description-verbatim: plugin.json has no .name field"
  exit 2
fi

# --- 3. marketplace.json fetch or local override ---
MARKETPLACE_JSON=""
if [[ -n "$MARKETPLACE_OVERRIDE" ]]; then
  if [[ ! -f "$MARKETPLACE_OVERRIDE" ]]; then
    echo "❌ marketplace-description-verbatim: marketplace override path not found: $MARKETPLACE_OVERRIDE"
    exit 2
  fi
  MARKETPLACE_JSON="$(cat "$MARKETPLACE_OVERRIDE")"
else
  command -v gh >/dev/null 2>&1 || {
    echo "❌ marketplace-description-verbatim: gh CLI not installed (required for marketplace fetch)"
    exit 2
  }
  # gh api raw 우선 (base64 decode 불필요), fallback: content + base64 -d
  MARKETPLACE_JSON="$(gh api -H "Accept: application/vnd.github.raw" \
    repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json 2>/dev/null || true)"
  if [[ -z "$MARKETPLACE_JSON" ]]; then
    # fallback: base64 decode
    MARKETPLACE_JSON="$(gh api repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json \
      --jq .content 2>/dev/null | base64 -d 2>/dev/null || true)"
  fi
  if [[ -z "$MARKETPLACE_JSON" ]]; then
    echo "❌ marketplace-description-verbatim: failed to fetch marketplace.json from mclayer/marketplace"
    exit 2
  fi
fi

# --- 4. Find plugin entry in marketplace ---
MARKETPLACE_ENTRY="$(echo "$MARKETPLACE_JSON" | jq --arg name "$PLUGIN_NAME" \
  '.plugins[] | select(.name == $name)' 2>/dev/null || true)"
if [[ -z "$MARKETPLACE_ENTRY" ]]; then
  echo "❌ marketplace-description-verbatim: FAIL — plugin '$PLUGIN_NAME' not registered in marketplace.json"
  echo "   Expected: marketplace.json plugins[] entry with name == '$PLUGIN_NAME'"
  exit 1
fi

# --- 5. Extract marketplace description ---
MARKET_DESC="$(echo "$MARKETPLACE_ENTRY" | jq -r '.description // empty')"
if [[ -z "$MARKET_DESC" ]]; then
  echo "❌ marketplace-description-verbatim: marketplace.json entry for '$PLUGIN_NAME' has no .description field"
  exit 2
fi

# --- 6. Byte-identical compare (trailing newline normalize) ---
# printf を使い trailing newline を正規化して比較
PLUGIN_DESC_NORM="$(printf '%s' "$PLUGIN_DESC")"
MARKET_DESC_NORM="$(printf '%s' "$MARKET_DESC")"

if [[ "$PLUGIN_DESC_NORM" == "$MARKET_DESC_NORM" ]]; then
  echo "✅ marketplace-description-verbatim: PASS"
  echo "   plugin '$PLUGIN_NAME' description byte-identical (${#PLUGIN_DESC_NORM} chars)"
  exit 0
fi

# --- 7. DRIFT report ---
echo "❌ marketplace-description-verbatim: DRIFT — description not byte-identical"
echo ""
echo "   plugin.json length:      ${#PLUGIN_DESC_NORM} chars"
echo "   marketplace.json length: ${#MARKET_DESC_NORM} chars"
echo ""

# 최초 불일치 위치 찾기 (최대 500자 스캔)
FIRST_DIFF_POS=""
SCAN_LEN=${#PLUGIN_DESC_NORM}
if [[ ${#MARKET_DESC_NORM} -lt "$SCAN_LEN" ]]; then
  SCAN_LEN=${#MARKET_DESC_NORM}
fi
MAX_SCAN=500
if [[ "$SCAN_LEN" -gt "$MAX_SCAN" ]]; then
  SCAN_LEN="$MAX_SCAN"
fi
for ((i=0; i<SCAN_LEN; i++)); do
  if [[ "${PLUGIN_DESC_NORM:$i:1}" != "${MARKET_DESC_NORM:$i:1}" ]]; then
    FIRST_DIFF_POS="$i"
    break
  fi
done

if [[ -n "$FIRST_DIFF_POS" ]]; then
  echo "   First difference at char position: $FIRST_DIFF_POS"
  START=$(( FIRST_DIFF_POS > 20 ? FIRST_DIFF_POS - 20 : 0 ))
  echo "   plugin.json   context: ...$(echo "${PLUGIN_DESC_NORM:$START:60}" | cat -A)..."
  echo "   marketplace   context: ...$(echo "${MARKET_DESC_NORM:$START:60}" | cat -A)..."
  echo ""
fi

echo "   plugin.json description (first 200 chars):"
echo "   $(echo "$PLUGIN_DESC_NORM" | cut -c1-200)"
echo ""
echo "   marketplace.json description (first 200 chars):"
echo "   $(echo "$MARKET_DESC_NORM" | cut -c1-200)"
echo ""
echo "   Recovery: 두 파일의 description 을 byte-identical 로 동기화하세요."
echo "   참조: ADR-063 Amendment 2 §결정 11 / ADR-016 mirrored field 4종"
echo "   bypass: hotfix-bypass:marketplace-description-verbatim label (ADR-024 Amendment 3)"
exit 1
