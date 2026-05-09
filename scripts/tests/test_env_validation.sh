#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(cd "$(dirname "$0")/../.." && pwd)/scripts/audit-trail-fetch.sh"

fail() { echo "FAIL: $1" >&2; exit 1; }
pass() { echo "PASS: $1"; }

# Test 1: AUDIT_PII_KEY 미설정 시 exit 1
(
  unset AUDIT_PII_KEY 2>/dev/null || true
  export GH_TOKEN="dummy-token"
  output=$("$SCRIPT" --org test-org 2>&1 || true)
  if echo "$output" | grep -q "AUDIT_PII_KEY"; then
    pass "AUDIT_PII_KEY 미설정 오류 메시지 출력"
  else
    fail "AUDIT_PII_KEY 오류 메시지 없음. 출력: $output"
  fi
)

# Test 2: GH_TOKEN 미설정 시 exit 1 (기존 동작 회귀 테스트)
(
  unset GH_TOKEN 2>/dev/null || true
  output=$("$SCRIPT" --org test-org 2>&1 || true)
  if echo "$output" | grep -q "GH_TOKEN"; then
    pass "GH_TOKEN 미설정 오류 메시지 출력"
  else
    fail "GH_TOKEN 오류 메시지 없음. 출력: $output"
  fi
)

echo "All env validation tests passed."
