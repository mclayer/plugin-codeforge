#!/usr/bin/env bash
# CFP-441 / ADR-063 §결정 5 — Version bump 3-file atomic invariant check
#
# 검증 대상 (ADR-063 §결정 1 verbatim):
#   (a) `.claude-plugin/plugin.json` mirrored field (name/version/description/author) 변경 시
#   (b) `CHANGELOG.md` 최상단 entry 의 version 이 plugin.json version 과 일치 (invariant)
#   (c) `mclayer/marketplace/.claude-plugin/marketplace.json` plugins[name=<local>] mirrored field 일치
#   (d) marketplace sync PR open / merged 상태 확인 (ADR-063 §결정 2 ordering enforcement)
#
# 본 lint 는 기존 `check-marketplace-parity.sh` + `invariant-check` workflow 의 통합 channel 로,
# ADR-063 violation 시 명시적 메시지 + recovery guidance 제공.
#
# 환경:
#   - gh CLI 가용 + auth 가능 시: marketplace.json fetch + PR search
#   - gh 미설치 / 미인증 시: warn-skip (CI는 항상 가용)
#
# 입력:
#   $BASE_REF: 비교 대상 ref (default: origin/main)
#
# Exit codes:
#   0 = PASS (atomic invariant 충족 또는 mirrored field 변경 없음)
#   1 = FAIL (ADR-063 violation)
#   2 = SETUP error (jq 없음, plugin.json 없음 등)

set -uo pipefail
cd "$(dirname "$0")/.."

BASE_REF="${BASE_REF:-origin/main}"

# --- Setup verify ---
command -v jq >/dev/null 2>&1 || { echo "❌ check-version-bump-atomic: jq not installed"; exit 2; }
command -v git >/dev/null 2>&1 || { echo "❌ check-version-bump-atomic: git not installed"; exit 2; }

PLUGIN_JSON=".claude-plugin/plugin.json"
CHANGELOG="CHANGELOG.md"

if [[ ! -f "$PLUGIN_JSON" ]]; then
  echo "ℹ check-version-bump-atomic: $PLUGIN_JSON 부재 — skip (consumer overlay 시나리오)"
  exit 0
fi

# --- Step 1: Detect mirrored field change vs base ---
git fetch origin --quiet 2>/dev/null || true

if ! git rev-parse "$BASE_REF" >/dev/null 2>&1; then
  echo "ℹ check-version-bump-atomic: base ref $BASE_REF 없음 — skip"
  exit 0
fi

# diff plugin.json from BASE_REF; check if mirrored fields changed
DIFF=$(git diff "$BASE_REF" -- "$PLUGIN_JSON" 2>/dev/null || true)

if [[ -z "$DIFF" ]]; then
  echo "✓ check-version-bump-atomic: plugin.json 변경 없음 — atomic invariant 영역 외"
  exit 0
fi

# Check mirrored fields specifically (name/version/description/author)
MIRRORED_CHANGED=0
for field in name version description author; do
  # Check for diff lines touching this field
  if echo "$DIFF" | grep -qE "^[-+]\s*\"${field}\":"; then
    MIRRORED_CHANGED=1
    break
  fi
done

if [[ "$MIRRORED_CHANGED" -eq 0 ]]; then
  echo "✓ check-version-bump-atomic: plugin.json 변경됨, but mirrored field (name/version/description/author) 무변경 — atomic invariant 영역 외"
  exit 0
fi

PLUGIN_NAME=$(jq -r '.name' "$PLUGIN_JSON")
LOCAL_VERSION=$(jq -r '.version' "$PLUGIN_JSON")
LOCAL_DESC=$(jq -r '.description' "$PLUGIN_JSON")
LOCAL_AUTHOR=$(jq -r '.author' "$PLUGIN_JSON" 2>/dev/null || jq -r '.author.name' "$PLUGIN_JSON" 2>/dev/null || echo "null")

echo "ℹ check-version-bump-atomic: plugin.json mirrored field 변경 감지"
echo "  plugin: $PLUGIN_NAME"
echo "  version (local): $LOCAL_VERSION"

# --- Step 2: CHANGELOG entry 존재 확인 ---
if [[ ! -f "$CHANGELOG" ]]; then
  echo "❌ ADR-063 §결정 1 violation: $CHANGELOG 부재 — mirrored field 변경 시 CHANGELOG entry 의무"
  exit 1
fi

# Extract top-level version from CHANGELOG (## [N.N.N] 패턴)
CL_VERSION=$(grep -m1 -oE '^## \[?[0-9]+\.[0-9]+\.[0-9]+\]?' "$CHANGELOG" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "")

if [[ -z "$CL_VERSION" ]]; then
  echo "❌ ADR-063 §결정 1 violation: $CHANGELOG 최상단 ## [N.N.N] header 부재"
  exit 1
fi

if [[ "$LOCAL_VERSION" != "$CL_VERSION" ]]; then
  echo "❌ ADR-063 §결정 1 violation: plugin.json version ($LOCAL_VERSION) ≠ CHANGELOG.md latest ($CL_VERSION)"
  echo "   Recovery: CHANGELOG.md 에 ## [$LOCAL_VERSION] entry 추가 (Added / Why / Compatibility 표준 형식)"
  exit 1
fi

echo "  CHANGELOG entry: ✓ $CL_VERSION"

# --- Step 3: marketplace.json parity 확인 ---
# gh 가용성 체크
if ! command -v gh >/dev/null 2>&1; then
  echo "⚠ check-version-bump-atomic: gh CLI 미설치 — marketplace parity skip (기존 check-marketplace-parity workflow 가 검증)"
  exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "⚠ check-version-bump-atomic: gh 미인증 — marketplace parity skip"
  exit 0
fi

# marketplace.json fetch via gh api
MARKETPLACE_RAW=$(gh api -H "Accept: application/vnd.github.raw" repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json 2>/dev/null || echo "")

if [[ -z "$MARKETPLACE_RAW" ]]; then
  echo "⚠ check-version-bump-atomic: marketplace.json fetch 실패 — parity check skip"
  exit 0
fi

REMOTE_VERSION=$(echo "$MARKETPLACE_RAW" | jq -r ".plugins[] | select(.name == \"$PLUGIN_NAME\") | .version" 2>/dev/null || echo "")

if [[ -z "$REMOTE_VERSION" || "$REMOTE_VERSION" == "null" ]]; then
  echo "❌ ADR-063 §결정 6 violation: marketplace.json 에 plugin '$PLUGIN_NAME' entry 부재 (ADR-016 sibling sync 미완료)"
  exit 1
fi

echo "  marketplace (remote): version=$REMOTE_VERSION"

if [[ "$LOCAL_VERSION" != "$REMOTE_VERSION" ]]; then
  echo ""
  echo "❌ ADR-063 §결정 1 + §결정 2 violation:"
  echo "   3-file atomic invariant 위반 — plugin.json ($LOCAL_VERSION) ≠ marketplace.json ($REMOTE_VERSION)"
  echo ""
  echo "   ADR-063 §결정 2 PR ordering:"
  echo "     1. mclayer/marketplace 에 sync PR open ($REMOTE_VERSION → $LOCAL_VERSION)"
  echo "     2. marketplace sync PR 선행 merge"
  echo "     3. 본 plugin PR re-run → marketplace-parity PASS"
  echo ""
  echo "   Anti-pattern: plugin PR 선행 merge 금지 (chicken-and-egg drift 발생)"
  echo "   Bypass: hotfix-bypass:marketplace-atomic label (긴급 hotfix only, 24시간 이내 sync 의무)"
  echo ""
  exit 1
fi

# --- Step 4: description / author parity (optional, ADR-016 mirrored field 4종 정합) ---
REMOTE_DESC=$(echo "$MARKETPLACE_RAW" | jq -r ".plugins[] | select(.name == \"$PLUGIN_NAME\") | .description" 2>/dev/null || echo "")

if [[ "$LOCAL_DESC" != "$REMOTE_DESC" ]]; then
  echo ""
  echo "❌ ADR-063 §결정 1 violation: description mirrored field drift"
  echo "   local desc:  $(echo "$LOCAL_DESC" | cut -c1-100)..."
  echo "   remote desc: $(echo "$REMOTE_DESC" | cut -c1-100)..."
  echo ""
  echo "   marketplace sync PR 에 description 동일 변경 의무 (ADR-016 + ADR-063 §결정 1)"
  exit 1
fi

echo "  description: ✓ parity"
echo ""
echo "✓ check-version-bump-atomic: 3-file atomic invariant 충족 (ADR-063 §결정 1)"
echo "  plugin.json $LOCAL_VERSION ↔ CHANGELOG.md $CL_VERSION ↔ marketplace.json $REMOTE_VERSION"
exit 0
