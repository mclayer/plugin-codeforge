#!/usr/bin/env bash
# scripts/test-check-return-envelope-schema.sh
# CFP-2572 Phase 2 — Discriminating test for check_return_envelope_schema.py (lint)
#
# Anti-theater test (ADR-119 / ADR-136 execution-liveness):
#   GREEN (real return-envelope-v1.md + real MANIFEST.yaml) 는 PASS,
#   surgical mutant (RB1/RB2/RB3) 는 각각 표적 check 만 RED 로 fire (required/forbidden sentinel).
#
# Mutation targeting (single-purpose surgical each):
#   RB1: fixture 에서 §2 envelope.meta cap 절(size_bytes/cap_bytes/over_cap) 제거 → (M1) RED.
#   RB2: fixture 에서 §3 raw-exclusion 표 row 제거 → (M2) RED.
#   RB3: MANIFEST fixture 에서 return_envelope entry 제거 → (M3) RED.
#
# Usage: bash scripts/test-check-return-envelope-schema.sh
# Exit: 0 = all pass / 1 = any fail.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

LDOC_GREEN="$REPO_ROOT/docs/inter-plugin-contracts/return-envelope-v1.md"
MANIFEST_GREEN="$REPO_ROOT/docs/inter-plugin-contracts/MANIFEST.yaml"

for f in "$LDOC_GREEN" "$MANIFEST_GREEN"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: fixture base 부재: $f"
    exit 2
  fi
done

run_discriminating_test() {
  local test_name="$1"
  local ldoc_fixture="$2"
  local manifest_fixture="$3"
  local expected="$4"
  local description="$5"
  local required_sentinel="${6:-}"
  local forbidden_sentinel="${7:-}"

  local lint_exit=0
  local lint_output=""
  lint_output=$(
    python3 scripts/lib/check_return_envelope_schema.py check \
      --ldoc-path "$ldoc_fixture" \
      --manifest-path "$manifest_fixture" \
      --repo-root "$REPO_ROOT" 2>&1
  ) || lint_exit=$?

  local lint_result="PASS"
  if [ "$lint_exit" -ne 0 ]; then
    lint_result="RED"
  fi

  if [ "$lint_result" != "$expected" ]; then
    echo "X FAIL: $test_name"
    echo "  Expected: $expected / Got: $lint_result (exit $lint_exit)"
    echo "  Desc: $description"
    echo "  Output: $lint_output"
    FAIL=$((FAIL+1))
    return 0
  fi

  if [ "$expected" = "RED" ]; then
    if [ -n "$required_sentinel" ] && ! echo "$lint_output" | grep -qE "$required_sentinel"; then
      echo "X FAIL: $test_name — RED 했으나 표적 violation 부재 (비특이 mutant)"
      echo "  required_sentinel: $required_sentinel / Output: $lint_output"
      FAIL=$((FAIL+1))
      return 0
    fi
    if [ -n "$forbidden_sentinel" ] && echo "$lint_output" | grep -qE "$forbidden_sentinel"; then
      echo "X FAIL: $test_name — off-target violation 검출 (mutant 비특이)"
      echo "  forbidden_sentinel: $forbidden_sentinel / Output: $lint_output"
      FAIL=$((FAIL+1))
      return 0
    fi
  fi

  echo "OK PASS: $test_name (lint result: $lint_result, exit $lint_exit)"
  PASS=$((PASS+1))
  return 0
}

TMP_TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_TEST_DIR"' EXIT

# RB1: §2 envelope.meta 의 cap yaml 필드 라인(6-space 들여쓰기) 3개 제거 → (M1) RED
LDOC_RB1="$TMP_TEST_DIR/ldoc_rb1.md"
sed -e '/^      size_bytes:/d' -e '/^      cap_bytes:/d' -e '/^      over_cap:/d' \
  "$LDOC_GREEN" > "$LDOC_RB1"

# RB2: §3 raw-exclusion 표 row 제거 → (M2) RED
LDOC_RB2="$TMP_TEST_DIR/ldoc_rb2.md"
sed '/| raw-exclusion |/d' "$LDOC_GREEN" > "$LDOC_RB2"

# RB3: MANIFEST 에서 return_envelope contract block(name~파일명) 제거 → (M3) RED
MANIFEST_RB3="$TMP_TEST_DIR/manifest_rb3.yaml"
sed '/- name: return_envelope/,/return-envelope-v1.md/d' "$MANIFEST_GREEN" > "$MANIFEST_RB3"

# TC-1 GREEN
run_discriminating_test \
  "TC-1-GREEN" \
  "$LDOC_GREEN" \
  "$MANIFEST_GREEN" \
  "PASS" \
  "real return-envelope-v1.md (cap field + raw-exclusion) + real MANIFEST (return_envelope 등록)"

# TC-2 RB1 — cap 절 제거 → (M1) only
run_discriminating_test \
  "TC-2-RB1-remove-cap" \
  "$LDOC_RB1" \
  "$MANIFEST_GREEN" \
  "RED" \
  "RB1: §2 envelope.meta cap 절 제거 — (M1) 표적" \
  '\(M1\)' \
  '\(M2\)|\(M3\)'

# TC-3 RB2 — raw-exclusion 절 제거 → (M2) only
run_discriminating_test \
  "TC-3-RB2-remove-raw-exclusion" \
  "$LDOC_RB2" \
  "$MANIFEST_GREEN" \
  "RED" \
  "RB2: §3 raw-exclusion 절 제거 — (M2) 표적" \
  '\(M2\)' \
  '\(M1\)|\(M3\)'

# TC-4 RB3 — MANIFEST return_envelope entry 제거 → (M3) only
run_discriminating_test \
  "TC-4-RB3-manifest-unregistered" \
  "$LDOC_GREEN" \
  "$MANIFEST_RB3" \
  "RED" \
  "RB3: MANIFEST return_envelope entry 제거 — (M3) 표적" \
  '\(M3\)' \
  '\(M1\)|\(M2\)'

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: return-envelope-schema lint discriminating test"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "OK All discriminating tests passed — lint is detecting mutations correctly"
  exit 0
else
  echo "X Some tests failed — lint may not be detecting mutations correctly"
  exit 1
fi
