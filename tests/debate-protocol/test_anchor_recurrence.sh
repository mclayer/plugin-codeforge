#!/usr/bin/env bash
# CFP-391 / Plan T16 — debate-protocol-v1 anchor recurrence escalation simulation test
#
# Tests the algorithm described in CFP-391 Story §2.5 + ADR-059 §결정 4:
#   count(Story §9 의 "### Debate transcript: <anchor_id>" sub-section) >= 2 → immediate user escalation
#
# Input: fixtures/story-{with,without}-recurrence.md
# Output: exit 0 if all assertions pass, 1 otherwise

set -euo pipefail
cd "$(dirname "$0")"

FAIL=0
PASS=0

# count_recurrence <story-file> <anchor_id> → integer count
count_recurrence() {
  local story="$1"
  local anchor="$2"
  grep -cE "^### Debate transcript: ${anchor}\s*$" "$story" || true
}

echo "=== Test 1: with-recurrence fixture (anchor docs/foo.md:42 appears 2 times) ==="
COUNT=$(count_recurrence fixtures/story-with-recurrence.md "docs/foo.md:42")
echo "count = $COUNT"

# Assertion 1: count == 2 → escalation 발동
if [[ "$COUNT" == "2" ]]; then
  echo "PASS: count = 2 (escalation triggered)"
  PASS=$((PASS+1))
else
  echo "FAIL: expected count = 2, got $COUNT"
  FAIL=$((FAIL+1))
fi

# Assertion 2: escalation decision = >= 2 threshold
if [[ "$COUNT" -ge 2 ]]; then
  echo "PASS: count >= 2 → AskUserQuestion escalation (ADR-059 §결정 4)"
  PASS=$((PASS+1))
else
  echo "FAIL: count < 2 → no escalation (logic bug)"
  FAIL=$((FAIL+1))
fi

echo ""
echo "=== Test 2: without-recurrence fixture (anchor docs/foo.md:42 appears 1 time) ==="
COUNT=$(count_recurrence fixtures/story-without-recurrence.md "docs/foo.md:42")
echo "count = $COUNT"

# Assertion 3: count == 1 → no escalation
if [[ "$COUNT" == "1" ]]; then
  echo "PASS: count = 1 (no escalation)"
  PASS=$((PASS+1))
else
  echo "FAIL: expected count = 1, got $COUNT"
  FAIL=$((FAIL+1))
fi

# Assertion 4: count < 2 → 정상 debate flow 진행
if [[ "$COUNT" -lt 2 ]]; then
  echo "PASS: count < 2 → debate Round dispatch 정상 진입"
  PASS=$((PASS+1))
else
  echo "FAIL: count >= 2 → unexpected escalation"
  FAIL=$((FAIL+1))
fi

echo ""
echo "=== Test 3: different anchor (docs/bar.md:10) on with-recurrence fixture ==="
COUNT=$(count_recurrence fixtures/story-with-recurrence.md "docs/bar.md:10")
echo "count = $COUNT"

# Assertion 5: 0 occurrence (anchor not present)
if [[ "$COUNT" == "0" ]]; then
  echo "PASS: count = 0 for non-existent anchor"
  PASS=$((PASS+1))
else
  echo "FAIL: expected count = 0, got $COUNT"
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
