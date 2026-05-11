#!/usr/bin/env bash
# CFP-391 / Plan T16 — debate-protocol-v1 divergence detection simulation test
#
# Tests the algorithm described in CFP-391 Story §2.3 (Trigger 정의 — DesignReview scope):
#   for anchor_id in union(claude_findings.anchor_id, codex_findings.anchor_id):
#     - one-sided emission → divergence_type = recommendation
#     - both severity mismatch → divergence_type = severity
#     - both recommendation mismatch → divergence_type = recommendation
#     - both aligned → no divergence
#
# Input: fixtures/findings-{divergent,aligned}.json
# Output: exit 0 if all assertions pass, 1 otherwise

set -euo pipefail
cd "$(dirname "$0")"

if ! command -v jq >/dev/null 2>&1; then
  echo "::error::jq 미설치 — test skip" >&2
  exit 2
fi

FAIL=0
PASS=0

detect_divergences() {
  local fixture="$1"
  jq -r '
    . as $root |
    (([.claude_findings[].anchor_id] + [.codex_findings[].anchor_id]) | unique) as $anchors |
    $anchors[] as $a |
    {
      anchor_id: $a,
      claude: ($root.claude_findings | map(select(.anchor_id == $a)) | first),
      codex:  ($root.codex_findings  | map(select(.anchor_id == $a)) | first)
    } |
    if (.claude == null) or (.codex == null) then
      "\(.anchor_id)\trecommendation\tone_sided"
    elif .claude.severity != .codex.severity then
      "\(.anchor_id)\tseverity\tboth_emit_diff_severity"
    elif .claude.recommendation != .codex.recommendation then
      "\(.anchor_id)\trecommendation\tboth_emit_diff_recommendation"
    else
      "\(.anchor_id)\tnone\taligned"
    end
  ' "$fixture"
}

echo "=== Test 1: divergent fixture (2 anchors, both divergent) ==="
RESULT=$(detect_divergences fixtures/findings-divergent.json)
echo "$RESULT"

# Assertion 1: 2 anchors should produce 2 divergences (severity OR recommendation)
DIVERGENCE_COUNT=$(echo "$RESULT" | grep -cE "severity|recommendation" || true)
if [[ "$DIVERGENCE_COUNT" == "2" ]]; then
  echo "PASS: 2 divergences detected (expected 2)"
  PASS=$((PASS+1))
else
  echo "FAIL: expected 2 divergences, got $DIVERGENCE_COUNT"
  FAIL=$((FAIL+1))
fi

# Assertion 2: review-verdict-v4.md anchor should be severity mismatch (P1 vs P0)
ANCHOR1_TYPE=$(echo "$RESULT" | grep "review-verdict-v4.md:52" | awk -F'\t' '{print $2}')
if [[ "$ANCHOR1_TYPE" == "severity" ]]; then
  echo "PASS: review-verdict-v4.md:52 = severity mismatch"
  PASS=$((PASS+1))
else
  echo "FAIL: expected severity, got '$ANCHOR1_TYPE'"
  FAIL=$((FAIL+1))
fi

# Assertion 3: team-spec yaml anchor should be severity mismatch (P2 vs P1)
ANCHOR2_TYPE=$(echo "$RESULT" | grep "team-spec-design-review.yaml:33" | awk -F'\t' '{print $2}')
if [[ "$ANCHOR2_TYPE" == "severity" ]]; then
  echo "PASS: team-spec-design-review.yaml:33 = severity mismatch"
  PASS=$((PASS+1))
else
  echo "FAIL: expected severity, got '$ANCHOR2_TYPE'"
  FAIL=$((FAIL+1))
fi

echo ""
echo "=== Test 2: aligned fixture (2 anchors, both aligned) ==="
RESULT=$(detect_divergences fixtures/findings-aligned.json)
echo "$RESULT"

# Assertion 4: 0 divergences (both anchors aligned)
DIVERGENCE_COUNT=$(echo "$RESULT" | grep -cE "severity|recommendation" || true)
if [[ "$DIVERGENCE_COUNT" == "0" ]]; then
  echo "PASS: 0 divergences detected (expected 0)"
  PASS=$((PASS+1))
else
  echo "FAIL: expected 0 divergences, got $DIVERGENCE_COUNT"
  FAIL=$((FAIL+1))
fi

# Assertion 5: all anchors marked 'none'
NONE_COUNT=$(echo "$RESULT" | grep -c "none" || true)
if [[ "$NONE_COUNT" == "2" ]]; then
  echo "PASS: 2 anchors marked 'none' (aligned)"
  PASS=$((PASS+1))
else
  echo "FAIL: expected 2 'none', got $NONE_COUNT"
  FAIL=$((FAIL+1))
fi

echo ""
echo "=== Summary ==="
echo "PASS: $PASS / $((PASS+FAIL))"
echo "FAIL: $FAIL"

if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
