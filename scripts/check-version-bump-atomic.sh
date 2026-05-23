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
# FIX-CR-1: here-string (<<<) 로 SIGPIPE 발생 path 제거 (production-scale DIFF ~100KB 시 pipefail 차단)
MIRRORED_CHANGED=0
for field in name version description author; do
  if grep -qE "^[-+]\s*\"${field}\":" <<< "$DIFF"; then
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
# FIX-CR-2: author 가 object {"name":"X"} 또는 plain string 양쪽 처리 (jq fallback 오류 패턴 제거)
LOCAL_AUTHOR=$(jq -r 'if (.author | type) == "object" then .author.name else .author end' "$PLUGIN_JSON")

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
# ADR-063 §결정 22 Amendment 9 / CFP-604 — gh-skip silent hole 차단
# 3-way 분기 (CI fail-loud + consumer self-hosted runner / non-CI graceful skip with warning):
#   (i)  CI 환경 ($CI == true AND $GITHUB_ACTIONS == true) = exit 2 fail-loud (environment error, workflow FAIL)
#   (ii) consumer self-hosted runner / non-CI 환경 ($CI 또는 $GITHUB_ACTIONS 미설정) = exit 0 graceful skip + stderr warning emit
# silent skip 금지 (ADR-063 §결정 22 (a) mandate + §2.2 "silent 0, user-visible" 도메인 불변식 정합)
_is_ci_env() {
  [[ "${CI:-}" == "true" && "${GITHUB_ACTIONS:-}" == "true" ]]
}

# gh 가용성 체크
if ! command -v gh >/dev/null 2>&1; then
  if _is_ci_env; then
    echo "❌ check-version-bump-atomic: CI 환경에서 gh CLI 미설치 — marketplace parity check 불가" >&2
    echo "   해결: GitHub Actions runner 에 gh CLI 설치 의무 (ADR-063 §결정 22)" >&2
    echo "   Bypass: hotfix-bypass:marketplace-atomic label (긴급 hotfix only)" >&2
    exit 2
  else
    echo "⚠ check-version-bump-atomic: gh CLI 미설치 — marketplace parity skip (local advisory 모드)" >&2
    echo "  CI 환경에서는 gh CLI 가 필수입니다 (ADR-063 §결정 22 (a))" >&2
    exit 0
  fi
fi

if ! gh auth status >/dev/null 2>&1; then
  if _is_ci_env; then
    echo "❌ check-version-bump-atomic: CI 환경에서 gh 미인증 — marketplace parity check 불가" >&2
    echo "   해결: GH_TOKEN 또는 GITHUB_TOKEN env 설정 의무 (ADR-063 §결정 22)" >&2
    echo "   Bypass: hotfix-bypass:marketplace-atomic label (긴급 hotfix only)" >&2
    exit 2
  else
    echo "⚠ check-version-bump-atomic: gh 미인증 — marketplace parity skip (local advisory 모드)" >&2
    echo "  CI 환경에서는 gh auth 가 필수입니다 (ADR-063 §결정 22 (a))" >&2
    exit 0
  fi
fi

# marketplace.json fetch via gh api
MARKETPLACE_RAW=$(gh api -H "Accept: application/vnd.github.raw" repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json 2>/dev/null || echo "")

if [[ -z "$MARKETPLACE_RAW" ]]; then
  if _is_ci_env; then
    echo "❌ check-version-bump-atomic: CI 환경에서 marketplace.json fetch 실패 — parity check 불가" >&2
    echo "   repos/mclayer/marketplace 접근 권한 또는 GH_TOKEN scope 확인 (ADR-066 §결정 2)" >&2
    echo "   Bypass: hotfix-bypass:marketplace-atomic label (긴급 hotfix only)" >&2
    exit 2
  else
    echo "⚠ check-version-bump-atomic: marketplace.json fetch 실패 — parity check skip (local advisory 모드)" >&2
    echo "  CI 환경에서는 marketplace.json fetch 가 필수입니다 (ADR-063 §결정 22 (a))" >&2
    exit 0
  fi
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

# --- Step 4: mirrored field 4종 parity (ADR-063 §결정 22 Amendment 9 / CFP-604 — name/author 축 확장) ---
# ADR-016 mirrored field 4종 (name/version/description/author) 전체 blocking-on-pr coverage 완결
# version 은 Step 3 에서 이미 검증 완료 — Step 4 는 description/name/author 검증
FIELD_FAIL=0

REMOTE_DESC=$(echo "$MARKETPLACE_RAW" | jq -r ".plugins[] | select(.name == \"$PLUGIN_NAME\") | .description" 2>/dev/null || echo "")

if [[ "$LOCAL_DESC" != "$REMOTE_DESC" ]]; then
  echo ""
  echo "❌ ADR-063 §결정 1 violation: description mirrored field drift"
  echo "   local desc:  $(echo "$LOCAL_DESC" | cut -c1-100)..."
  echo "   remote desc: $(echo "$REMOTE_DESC" | cut -c1-100)..."
  echo "   marketplace sync PR 에 description 동일 변경 의무 (ADR-016 + ADR-063 §결정 1)"
  FIELD_FAIL=1
fi

# name 축 검증 (ADR-063 §결정 22 (b) — name/author 축 신규 blocking)
REMOTE_NAME=$(echo "$MARKETPLACE_RAW" | jq -r ".plugins[] | select(.name == \"$PLUGIN_NAME\") | .name" 2>/dev/null || echo "")
LOCAL_NAME=$(jq -r '.name' "$PLUGIN_JSON")

if [[ "$LOCAL_NAME" != "$REMOTE_NAME" ]]; then
  echo ""
  echo "❌ ADR-063 §결정 1 violation: name mirrored field drift"
  echo "   local name:  $LOCAL_NAME"
  echo "   remote name: $REMOTE_NAME"
  echo "   marketplace sync PR 에 name 동일 변경 의무 (ADR-016 + ADR-063 §결정 1 + §결정 22)"
  FIELD_FAIL=1
fi

# author 축 검증 (ADR-063 §결정 22 (b) — author 축 신규 blocking)
REMOTE_AUTHOR=$(echo "$MARKETPLACE_RAW" | jq -r ".plugins[] | select(.name == \"$PLUGIN_NAME\") | .author // .author.name // \"\"" 2>/dev/null || echo "")

# FIX-CR-4: LOCAL_AUTHOR_NORM 은 FIX-CR-2 로 LOCAL_AUTHOR 자체가 정규화됨 — alias 제거
if [[ "$LOCAL_AUTHOR" != "$REMOTE_AUTHOR" && "$LOCAL_AUTHOR" != "null" && "$REMOTE_AUTHOR" != "null" ]]; then
  echo ""
  echo "❌ ADR-063 §결정 1 violation: author mirrored field drift"
  echo "   local author:  $LOCAL_AUTHOR"
  echo "   remote author: $REMOTE_AUTHOR"
  echo "   marketplace sync PR 에 author 동일 변경 의무 (ADR-016 + ADR-063 §결정 1 + §결정 22)"
  FIELD_FAIL=1
fi

if [[ "$FIELD_FAIL" -eq 1 ]]; then
  echo ""
  echo "   ADR-063 §결정 2 PR ordering:"
  echo "     1. mclayer/marketplace 에 sync PR open (mirrored field 4종 동기화)"
  echo "     2. marketplace sync PR 선행 merge"
  echo "     3. 본 plugin PR re-run → marketplace-parity PASS"
  echo "   Anti-pattern: plugin PR 선행 merge 금지 (drift 발생)"
  echo "   Bypass: hotfix-bypass:marketplace-atomic label (긴급 hotfix only, 24시간 이내 sync 의무)"
  exit 1
fi

echo "  description: ✓ parity"
echo "  name:        ✓ parity"
echo "  author:      ✓ parity"
echo ""
echo "✓ check-version-bump-atomic: 3-file atomic invariant 충족 (ADR-063 §결정 1 + §결정 22)"
echo "  plugin.json $LOCAL_VERSION ↔ CHANGELOG.md $CL_VERSION ↔ marketplace.json $REMOTE_VERSION"
echo "  mirrored field 4종 (name/version/description/author) 전부 parity 확인 (ADR-063 §결정 22 Amendment 9)"
exit 0
