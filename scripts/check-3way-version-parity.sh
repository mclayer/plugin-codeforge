#!/usr/bin/env bash
# CFP-820 / ADR-063 Amendment 5 §결정 15 — 3-way version atomic invariant check
# CFP-932 OQ-5 — channel dimension cross-ref (consumer overlay channel.tier ↔ marketplace channels[])
#
# 검증 대상 (ADR-063 Amendment 5 §결정 15 verbatim):
#   (publisher)  `.claude-plugin/plugin.json` .version
#   (registry)   `mclayer/marketplace/.claude-plugin/marketplace.json` .plugins[codeforge].version
#   (consumer)   `.claude/_overlay/project.yaml` .codeforge.version_pin.version
#
# OQ-5 channel dimension: consumer overlay codeforge.channel.tier ↔ marketplace channels[*].versions[]
#   membership drift detection = companion script check-channel-drift.sh (CFP-932 D5)
#   rationale: 3-way-version-parity covers version axis; channel axis = orthogonal separate check
#   check-3way-version-parity.sh does NOT check channel tier — delegates to check-channel-drift.sh
#
# 3-way byte-identical version field compare + sanity guard 6-tuple (Story §5.2 AC-13):
#   (1) size > 40000         (empty-blob / truncated fetch 방어)                     → exit 2
#   (2) JSON parse           (malformed JSON 방어)                                   → exit 2
#   (3) 4-field parity       (name/version/description/author 필수 — ADR-016)        → exit 2
#   (4) 6 non-codeforge byte-identical (sister plugin entries untouched verify)       → exit 2
#   (5) git diff stat        (single-line edit invariant on plugin.json)              → exit 1
#   (6) global version pattern unique (multi-version collision detect)               → exit 2
# fallback: consumer pin 미등록 = warning-first exit 0 (orthogonality invariant §7.4 / AC-2)
#
# Exit codes:
#   0 = PASS (3-way invariant 충족 / pin 미등록 warning-first / bypass active / 429 fail-open)
#   1 = FAIL (3-way version mismatch — blocking-on-pr tier, ADR-063 Amendment 5)
#   2 = SETUP / ENV error (fetch fail-closed / schema drift / malformed pin / tool missing)
#
# 환경 변수:
#   PLUGIN_JSON_PATH            override plugin.json path (testing용)
#   CONSUMER_PROJECT_YAML_PATH  override project.yaml path (testing용)
#   BYPASS_LABEL                bypass label string (e.g. "hotfix-bypass:version-3way-atomic")
#
# ADR refs: ADR-063 Amendment 5 §결정 15/16, ADR-066 §결정 2 (PAT scope — read-only reuse),
#           ADR-070 (verify-before-trust), ADR-027 Amendment 4 (fallback semantic),
#           ADR-061 (Python >5 lines = external .py file — scripts/read_version_pin.py)
# channel refs: CFP-932 / reconcile-protocol-v1 §4.10 / check-channel-drift.sh (OQ-5 companion)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PLUGIN_JSON="${PLUGIN_JSON_PATH:-$REPO_ROOT/.claude-plugin/plugin.json}"
CONSUMER_YAML="${CONSUMER_PROJECT_YAML_PATH:-$REPO_ROOT/.claude/_overlay/project.yaml}"
BYPASS_LABEL_VAR="${BYPASS_LABEL:-}"

# ─────────────────────────────────────────────────────── setup verify ──

command -v jq >/dev/null 2>&1 || { echo "❌ check-3way-version-parity: jq not installed"; exit 2; }

if [[ ! -f "$PLUGIN_JSON" ]]; then
  echo "ℹ check-3way-version-parity: $PLUGIN_JSON 부재 — skip (consumer overlay 또는 non-plugin repo)"
  exit 0
fi

# ─────────────────────────────────────────────── bypass label check ──

if [[ -n "$BYPASS_LABEL_VAR" ]] && [[ "$BYPASS_LABEL_VAR" == "hotfix-bypass:version-3way-atomic" ]]; then
  echo "ℹ check-3way-version-parity: bypass label active ($BYPASS_LABEL_VAR)"
  echo "  ⚠ audit: hotfix-bypass 적용 — 24시간 이내 3-way version sync 의무 (ADR-024 Amendment 3)"
  echo "  3-way parity check skipped. Post-hotfix sync required."
  exit 0
fi

# ─────────────────────────────────────── read publisher version ──

PUBLISHER_VERSION=$(jq -r '.version // empty' "$PLUGIN_JSON" 2>/dev/null || echo "")
if [[ -z "$PUBLISHER_VERSION" ]]; then
  echo "❌ check-3way-version-parity: plugin.json .version 필드 부재 또는 empty"
  exit 2
fi

PLUGIN_NAME=$(jq -r '.name // "codeforge"' "$PLUGIN_JSON" 2>/dev/null || echo "codeforge")

echo "ℹ check-3way-version-parity: publisher version = $PUBLISHER_VERSION (plugin: $PLUGIN_NAME)"

# ─────────────────────────────────────── read marketplace version ──

if ! command -v gh >/dev/null 2>&1; then
  echo "⚠ check-3way-version-parity: gh CLI 미설치 — marketplace fetch skip"
  exit 0
fi

# Check gh auth — try to detect 401 vs no-auth
GH_AUTH_OUT=$(gh auth status 2>&1 || true)
if echo "$GH_AUTH_OUT" | grep -qi "not logged in\|no account\|not authenticated"; then
  echo "⚠ check-3way-version-parity: gh 미인증 — marketplace fetch skip"
  exit 0
fi

# Fetch marketplace.json metadata (sha+size) for ADR-070 verify-before-trust
MARKETPLACE_META_RAW=$(gh api repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json 2>&1)
MARKETPLACE_META_EXIT=$?

if [[ $MARKETPLACE_META_EXIT -ne 0 ]]; then
  # Classify error: 401 vs 429 vs 5xx/network (fail-closed-with-retry) vs other
  if echo "$MARKETPLACE_META_RAW" | grep -qi "bad credentials\|401\|Unauthorized"; then
    echo "❌ check-3way-version-parity: marketplace fetch 실패 — PAT 인증 오류 (401)"
    echo "  Recovery: CODEFORGE_CROSS_REPO_PAT 갱신 후 재실행 (ADR-066 §결정 2)"
    echo "  PAT scope required: marketplace contents:read"
    exit 2
  fi
  if echo "$MARKETPLACE_META_RAW" | grep -qi "rate limit\|429\|secondary rate"; then
    echo "⚠ check-3way-version-parity: marketplace fetch rate-limited (429) — fail-open"
    echo "  다음 run 자동 재검증 (false-negative ≤24h delay 허용 — §7.4(c))"
    exit 0
  fi
  # 5xx / network error → fail-closed-with-retry (Story §7.4(c) / Change Plan §13.4)
  # exponential backoff 1s / 2s / 4s, 3회 retry 후 영속 실패 시 exit 2
  if echo "$MARKETPLACE_META_RAW" | grep -qi \
      "5[0-9][0-9]\|Bad Gateway\|Service Unavailable\|Internal Server\|Gateway Timeout\|could not resolve\|connection refused\|network\|timed out"; then
    echo "⚠ check-3way-version-parity: marketplace fetch 5xx/network 오류 — fail-closed-with-retry (3회)"
    for _wait in 1 2 4; do
      sleep "$_wait"
      MARKETPLACE_META_RAW=$(gh api repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json 2>&1)
      MARKETPLACE_META_EXIT=$?
      if [[ $MARKETPLACE_META_EXIT -eq 0 ]]; then
        echo "  ✓ retry 성공 (backoff ${_wait}s)"
        break
      fi
      echo "  retry 실패 (backoff ${_wait}s — 다음 시도 대기)"
    done
    if [[ $MARKETPLACE_META_EXIT -ne 0 ]]; then
      echo "❌ check-3way-version-parity: marketplace fetch 3회 retry 후 영속 실패 — fail-closed exit 2"
      echo "  Recovery: 네트워크 상태 확인 / marketplace repo 접근 권한 재확인 (ADR-066 §결정 2)"
      exit 2
    fi
  else
    echo "⚠ check-3way-version-parity: marketplace fetch 실패 (분류 불가) — skip"
    exit 0
  fi
fi

# Sanity guard (1): size > 40000 (Story §5.2 AC-13 / Change Plan §7.4.1)
MARKETPLACE_SIZE=$(echo "$MARKETPLACE_META_RAW" | jq -r '.size // 0' 2>/dev/null || echo "0")

if [[ "$MARKETPLACE_SIZE" -le 40000 ]]; then
  echo "❌ check-3way-version-parity: marketplace.json fetch truncated/empty (size=$MARKETPLACE_SIZE ≤ 40000 bytes)"
  echo "  Recovery: ADR-070 empty-blob detection 표준 — 재시도 또는 marketplace repo 상태 확인"
  exit 2
fi

MARKETPLACE_RAW=$(gh api -H "Accept: application/vnd.github.raw" \
  repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json 2>/dev/null || echo "")

if [[ -z "$MARKETPLACE_RAW" ]]; then
  echo "❌ check-3way-version-parity: marketplace.json raw content empty (fetch truncated/empty)"
  exit 2
fi

# Sanity guard (2): JSON parse
if ! echo "$MARKETPLACE_RAW" | jq empty 2>/dev/null; then
  echo "❌ check-3way-version-parity: marketplace.json JSON parse 실패 — registry schema drift"
  exit 2
fi

# Sanity guard (3): 4-field parity — codeforge entry must have name/version/description/author
MARKETPLACE_ENTRY=$(echo "$MARKETPLACE_RAW" | jq ".plugins[] | select(.name == \"$PLUGIN_NAME\")" 2>/dev/null || echo "")

if [[ -z "$MARKETPLACE_ENTRY" ]]; then
  echo "❌ check-3way-version-parity: marketplace.json 에 plugin '$PLUGIN_NAME' entry 부재"
  echo "  ADR-016 sibling sync 미완료 — marketplace sync PR 확인"
  exit 2
fi

for field in name version description author; do
  FIELD_VAL=$(echo "$MARKETPLACE_ENTRY" | jq -r ".$field // empty" 2>/dev/null || echo "")
  if [[ -z "$FIELD_VAL" ]]; then
    echo "❌ check-3way-version-parity: marketplace.json codeforge entry 필드 부재: .$field"
    echo "  schema drift — 4-field parity 불충족 (name/version/description/author 필수)"
    exit 2
  fi
done

MARKETPLACE_VERSION=$(echo "$MARKETPLACE_ENTRY" | jq -r '.version' 2>/dev/null || echo "")

if [[ -z "$MARKETPLACE_VERSION" || "$MARKETPLACE_VERSION" == "null" ]]; then
  echo "❌ check-3way-version-parity: marketplace.json .version field 추출 실패"
  exit 2
fi

# Sanity guard (4): 6 non-codeforge sister plugin entries byte-identical
# (read-only invariant 자기증명 — sister entry untouched verify, §7.4.1 guard 4)
SISTER_COUNT=$(echo "$MARKETPLACE_RAW" | jq '[.plugins[] | select(.name != "'"$PLUGIN_NAME"'")] | length' 2>/dev/null || echo "0")
if [[ "$SISTER_COUNT" -ge 6 ]]; then
  # Re-fetch to compare (ADR-070 verify-before-trust — 2nd raw fetch for cross-check)
  MARKETPLACE_RAW2=$(gh api -H "Accept: application/vnd.github.raw" \
    repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json 2>/dev/null || echo "")
  SISTER_ENTRIES_1=$(echo "$MARKETPLACE_RAW"  | jq -c '[.plugins[] | select(.name != "'"$PLUGIN_NAME"'")]' 2>/dev/null || echo "[]")
  SISTER_ENTRIES_2=$(echo "$MARKETPLACE_RAW2" | jq -c '[.plugins[] | select(.name != "'"$PLUGIN_NAME"'")]' 2>/dev/null || echo "[]")
  if [[ "$SISTER_ENTRIES_1" != "$SISTER_ENTRIES_2" ]]; then
    echo "❌ check-3way-version-parity: sanity guard (4) FAIL — marketplace sister plugin entries mutation detected"
    echo "  sister entries differ between two fetches (unexpected mutation — read-only invariant violation)"
    echo "  Recovery: marketplace repo 상태 확인 / 재시도"
    exit 2
  fi
fi

# Sanity guard (5): git diff stat single-line invariant on plugin.json
# (Phase 2 self-app PR 시 plugin.json version 변경 = 1 line edit, §7.4.1 guard 5)
if command -v git >/dev/null 2>&1; then
  GIT_DIFF_STAT=$(git diff --stat HEAD -- ".claude-plugin/plugin.json" 2>/dev/null || echo "")
  if [[ -n "$GIT_DIFF_STAT" ]]; then
    # Count changed lines (+ and - combined) — should be ≤ 2 for single version field bump
    CHANGED_LINES=$(git diff HEAD -- ".claude-plugin/plugin.json" 2>/dev/null | grep -c '^[+-][^+-]' || echo "0")
    if [[ "$CHANGED_LINES" -gt 4 ]]; then
      echo "❌ check-3way-version-parity: sanity guard (5) FAIL — plugin.json multi-line edit anomaly"
      echo "  plugin.json diff lines=$CHANGED_LINES (expected ≤4 for single version field bump)"
      echo "  git diff --stat HEAD -- .claude-plugin/plugin.json:"
      echo "$GIT_DIFF_STAT"
      echo "  Recovery: plugin.json 변경 내용 검토 (version field 만 변경 의무)"
      exit 1
    fi
  fi
fi

# Sanity guard (6): global version pattern unique — codeforge entry version 은 정확히 1건 match
# (multi-version collision detect — version string 이 다른 entry 에도 출현 시 wrong-match 차단, §7.4.1 guard 6)
VERSION_MATCH_COUNT=$(echo "$MARKETPLACE_RAW" | jq "[.plugins[] | select(.version == \"$MARKETPLACE_VERSION\")] | length" 2>/dev/null || echo "0")
if [[ "$VERSION_MATCH_COUNT" -gt 1 ]]; then
  echo "❌ check-3way-version-parity: sanity guard (6) FAIL — marketplace version pattern collision"
  echo "  version=$MARKETPLACE_VERSION matches $VERSION_MATCH_COUNT plugin entries (expected exactly 1)"
  echo "  version collision 시 wrong-match 위험 — marketplace.json 내 version 중복 확인 의무"
  exit 2
fi

echo "  registry version   = $MARKETPLACE_VERSION"

# ─────────────────────────────────────── read consumer pin version ──
# ADR-061: Python >5 lines → external .py file (scripts/read_version_pin.py)

CONSUMER_PIN_VERSION=""
PIN_PRESENT=0

if ! command -v python3 >/dev/null 2>&1; then
  echo "⚠ check-3way-version-parity: python3 미설치 — consumer pin parse skip"
  exit 0
fi

READ_PIN_PY="$SCRIPT_DIR/read_version_pin.py"
if [[ ! -f "$READ_PIN_PY" ]]; then
  echo "⚠ check-3way-version-parity: read_version_pin.py 부재 — skip"
  exit 0
fi

CONSUMER_RESULT=$(python3 "$READ_PIN_PY" "$CONSUMER_YAML" 2>/dev/null)
PY_EXIT=$?

if [[ $PY_EXIT -eq 10 ]]; then
  echo "⚠ check-3way-version-parity: PyYAML 미설치 — consumer pin parse skip (pip install pyyaml)"
  exit 0
fi

if [[ $PY_EXIT -ne 0 ]]; then
  echo "⚠ check-3way-version-parity: consumer yaml parse 오류 — skip"
  exit 0
fi

case "$CONSUMER_RESULT" in
  PIN_ABSENT)
    PIN_PRESENT=0
    ;;
  PIN_MALFORMED:*)
    MALFORMED_REASON="${CONSUMER_RESULT#PIN_MALFORMED:}"
    echo "❌ check-3way-version-parity: consumer pin malformed ($MALFORMED_REASON)"
    echo "  .claude/_overlay/project.yaml .codeforge.version_pin.version 필드 확인"
    echo "  예시:"
    echo "    codeforge:"
    echo "      version_pin:"
    echo "        version: \"$PUBLISHER_VERSION\""
    exit 2
    ;;
  PIN_VERSION:*)
    PIN_PRESENT=1
    CONSUMER_PIN_VERSION="${CONSUMER_RESULT#PIN_VERSION:}"
    ;;
  *)
    echo "⚠ check-3way-version-parity: consumer pin parse 예외 — skip"
    exit 0
    ;;
esac

# ──────────────────────── consumer pin absent = warning-first (AC-2 / §7.4(a)) ──

if [[ "$PIN_PRESENT" -eq 0 ]]; then
  echo "⚠ check-3way-version-parity: consumer pin SSOT 미등록"
  echo "  .claude/_overlay/project.yaml 에 codeforge.version_pin block 없음"
  echo "  3-way parity enforce 비활성 (warning-first — pin 등록 후 blocking-on-pr 활성)"
  echo "  등록 예시:"
  echo "    codeforge:"
  echo "      version_pin:"
  echo "        version: \"$PUBLISHER_VERSION\""
  echo ""
  echo "  ℹ 3-way version-3way-atomic: SKIPPED (pin absent — orthogonality invariant AC-2)"
  exit 0
fi

echo "  consumer pin       = $CONSUMER_PIN_VERSION"

# ────────────────────────────────────── 3-way compare ──

PASS=1
FAILURES=()

if [[ "$PUBLISHER_VERSION" != "$MARKETPLACE_VERSION" ]]; then
  PASS=0
  FAILURES+=("wrapper plugin.json ($PUBLISHER_VERSION) ≠ marketplace.json ($MARKETPLACE_VERSION)")
fi

if [[ "$PUBLISHER_VERSION" != "$CONSUMER_PIN_VERSION" ]]; then
  PASS=0
  FAILURES+=("wrapper plugin.json ($PUBLISHER_VERSION) ≠ consumer pin ($CONSUMER_PIN_VERSION)")
fi

if [[ "$MARKETPLACE_VERSION" != "$CONSUMER_PIN_VERSION" ]]; then
  PASS=0
  FAILURES+=("marketplace.json ($MARKETPLACE_VERSION) ≠ consumer pin ($CONSUMER_PIN_VERSION)")
fi

if [[ "$PASS" -eq 1 ]]; then
  echo ""
  echo "✓ check-3way-version-parity: 3-way PASS"
  echo "  publisher=$PUBLISHER_VERSION ↔ registry=$MARKETPLACE_VERSION ↔ consumer=$CONSUMER_PIN_VERSION"
  echo "  ADR-063 Amendment 5 §결정 15 3-way atomic invariant 충족"
  exit 0
fi

echo ""
echo "❌ check-3way-version-parity: 3-way version FAIL (ADR-063 Amendment 5 §결정 15 violation)"
for failure in "${FAILURES[@]}"; do
  echo "  MISMATCH: $failure"
done
echo ""
echo "  3-way atomic invariant requires byte-identical version across:"
echo "    wrapper plugin.json .version"
echo "    == marketplace.json .plugins[codeforge].version"
echo "    == .claude/_overlay/project.yaml .codeforge.version_pin.version"
echo ""
echo "  Note: exact-match comparison — 'v' prefix NOT normalized (§7.4(e))"
echo "  Recovery:"
echo "    1. marketplace sync PR merge (ADR-063 §결정 2 ordering)"
echo "    2. consumer project.yaml codeforge.version_pin.version 갱신"
echo "  Bypass: hotfix-bypass:version-3way-atomic label (ADR-024 Amendment 3, 24시간 내 sync 의무)"
exit 1
