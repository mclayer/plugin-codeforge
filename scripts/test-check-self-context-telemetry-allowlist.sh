#!/usr/bin/env bash
# scripts/test-check-self-context-telemetry-allowlist.sh
# CFP-2572 Phase 2 — Discriminating test for check_self_context_telemetry_allowlist.py (lint)
#                    + EMISSION-LIVENESS fixture (실 emit 경로 execution-backed).
#
# Anti-theater test (ADR-119 / ADR-136 execution-liveness — presence-grep false oracle 금지):
#   Part A (문서 lint discriminating):
#     GREEN (real spawn-event-v1.md §2.1) 는 PASS,
#     surgical mutant (RC1~RC4) 는 각각 표적 check 만 RED (required/forbidden sentinel).
#       RC1: 기존 field 타입을 free-form string 으로 변경 → (S2) RED.
#       RC2: opt-in default-false 선언 제거 → (S3) RED.
#       RC3: 7번째 non-allowlist field 추가 → (S1) RED.
#       RC4: proxy != ground-truth 진술 제거 → (S6) RED.
#   Part B (EMISSION-LIVENESS — CRITICAL):
#     실 emit CLI(append_self_context_event.py) 를 구동해 tempfile 에 record 가 실제 land 하는지
#     execution-backed 로 검증 (grep 아님):
#       opt-in ON  → 정확히 1 self-context-v1 record (schema_version + 정확 6 key) land.
#       opt-in OFF → 0 row (silent always-on 금지의 역).
#
# Usage: bash scripts/test-check-self-context-telemetry-allowlist.sh
# Exit: 0 = all pass / 1 = any fail.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

CONTRACT_GREEN="$REPO_ROOT/docs/inter-plugin-contracts/spawn-event-v1.md"
EMIT_CLI="$REPO_ROOT/scripts/lib/append_self_context_event.py"

for f in "$CONTRACT_GREEN" "$EMIT_CLI"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: fixture base 부재: $f"
    exit 2
  fi
done

# ═════════════════════════════════════════════════════════════════════════════
# Part A — 문서 lint discriminating harness
# ═════════════════════════════════════════════════════════════════════════════
run_discriminating_test() {
  local test_name="$1"
  local contract_fixture="$2"
  local expected="$3"
  local description="$4"
  local required_sentinel="${5:-}"
  local forbidden_sentinel="${6:-}"

  local lint_exit=0
  local lint_output=""
  lint_output=$(
    python3 scripts/lib/check_self_context_telemetry_allowlist.py check \
      --contract-path "$contract_fixture" \
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

# RC1: pre_tokens 타입 int → free-form string (count 6 유지, S2 격리) → (S2) RED
CONTRACT_RC1="$TMP_TEST_DIR/contract_rc1.md"
sed 's/`pre_tokens` | int/`pre_tokens` | free-form string/' "$CONTRACT_GREEN" > "$CONTRACT_RC1"

# RC2: §2.1.2 opt-in default-false 선언 제거 → (S3) RED
CONTRACT_RC2="$TMP_TEST_DIR/contract_rc2.md"
sed '/opt-in default-false/d' "$CONTRACT_GREEN" > "$CONTRACT_RC2"

# RC3: cause_category row 뒤에 7번째 non-allowlist field(numeric) 추가 (S1 격리) → (S1) RED
CONTRACT_RC3="$TMP_TEST_DIR/contract_rc3.md"
sed '/`cause_category` | enum (CLOSED) |/a | `extra_field` | int | required | injected 7th field RC3 | non-sensitive |' \
  "$CONTRACT_GREEN" > "$CONTRACT_RC3"

# RC4: §2.1.4 proxy != ground-truth verbatim 제거 (표 무손상, S6 격리) → (S6) RED
CONTRACT_RC4="$TMP_TEST_DIR/contract_rc4.md"
sed '/proxy 이지 lead-self ground-truth 가 아니다/d' "$CONTRACT_GREEN" > "$CONTRACT_RC4"

# TC-1 GREEN
run_discriminating_test \
  "TC-1-GREEN" \
  "$CONTRACT_GREEN" \
  "PASS" \
  "real spawn-event-v1.md §2.1 (6-field allow-list / numeric·enum·hash / opt-in / FORBIDDEN / 7-enum / proxy≠ground-truth)"

# TC-2 RC1 — free-form string field → (S2) only
run_discriminating_test \
  "TC-2-RC1-free-form-string" \
  "$CONTRACT_RC1" \
  "RED" \
  "RC1: pre_tokens 타입 free-form string — (S2) 표적" \
  '\(S2\)' \
  '\(S1\)|\(S3\)|\(S6\)'

# TC-3 RC2 — opt-in default-false 제거 → (S3) only
run_discriminating_test \
  "TC-3-RC2-remove-opt-in" \
  "$CONTRACT_RC2" \
  "RED" \
  "RC2: opt-in default-false 선언 제거 — (S3) 표적" \
  '\(S3\)' \
  '\(S1\)|\(S2\)|\(S6\)'

# TC-4 RC3 — 7번째 non-allowlist field → (S1) only
run_discriminating_test \
  "TC-4-RC3-seventh-field" \
  "$CONTRACT_RC3" \
  "RED" \
  "RC3: 7번째 non-allowlist field 추가 — (S1) 표적" \
  '\(S1\)' \
  '\(S2\)|\(S3\)|\(S6\)'

# TC-5 RC4 — proxy != ground-truth 제거 → (S6) only
run_discriminating_test \
  "TC-5-RC4-remove-proxy-verbatim" \
  "$CONTRACT_RC4" \
  "RED" \
  "RC4: proxy != ground-truth verbatim 제거 — (S6) 표적" \
  '\(S6\)' \
  '\(S1\)|\(S2\)|\(S3\)'

# ═════════════════════════════════════════════════════════════════════════════
# Part B — EMISSION-LIVENESS (execution-backed, presence-grep 아님)
# ═════════════════════════════════════════════════════════════════════════════

# opt-in ON — 실 emit → 정확히 1 self-context-v1 record land (schema_version + 정확 6 key)
LIVENESS_LEDGER="$TMP_TEST_DIR/liveness_on.jsonl"
emit_on_exit=0
python3 "$EMIT_CLI" \
  --telemetry-enabled --spawn-event-enabled \
  --session-id sess-liveness --turn-index 7 \
  --delegation-ratio 0.42 --pre-tokens 12345 \
  --cause-category read-heavy \
  --ledger-path "$LIVENESS_LEDGER" || emit_on_exit=$?

# 1-record land assertion (execution-backed — file 실측 후 파싱)   [EMISSION-LIVENESS ASSERT]
python3 - "$LIVENESS_LEDGER" <<'PYEOF'
import json, sys
ledger = sys.argv[1]
try:
    with open(ledger, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
except FileNotFoundError:
    print("LIVENESS-FAIL: ledger not created (opt-in ON but row 0)")
    sys.exit(1)
if len(lines) != 1:
    print("LIVENESS-FAIL: record count = %d (expected 1)" % len(lines))
    sys.exit(1)
rec = json.loads(lines[0])
if rec.get("schema_version") != "self-context-v1":
    print("LIVENESS-FAIL: schema_version = %r (expected self-context-v1)" % rec.get("schema_version"))
    sys.exit(1)
expected_keys = {"schema_version", "session_id", "turn_index",
                 "delegation_ratio", "pre_tokens", "cause_category"}
if set(rec.keys()) != expected_keys:
    print("LIVENESS-FAIL: key set = %s (expected exact 6-key)" % sorted(rec.keys()))
    sys.exit(1)
print("LIVENESS-OK: 1 self-context-v1 record land, exact 6-key")
sys.exit(0)
PYEOF
liveness_on_rc=$?
if [ "$emit_on_exit" -eq 0 ] && [ "$liveness_on_rc" -eq 0 ]; then
  echo "OK PASS: EMISSION-LIVENESS opt-in ON — 1 self-context-v1 record land (정확 6-key)"
  PASS=$((PASS+1))
else
  echo "X FAIL: EMISSION-LIVENESS opt-in ON (emit_exit=$emit_on_exit, assert_rc=$liveness_on_rc)"
  FAIL=$((FAIL+1))
fi

# opt-in OFF — flag 없음 → 0 row (file 부재 또는 empty)
LIVENESS_OFF_LEDGER="$TMP_TEST_DIR/liveness_off.jsonl"
python3 "$EMIT_CLI" \
  --session-id sess-off --turn-index 1 \
  --ledger-path "$LIVENESS_OFF_LEDGER" || true
off_rows=0
if [ -f "$LIVENESS_OFF_LEDGER" ]; then
  off_rows=$(grep -c . "$LIVENESS_OFF_LEDGER" 2>/dev/null || echo 0)
fi
if [ "$off_rows" -eq 0 ]; then
  echo "OK PASS: EMISSION-LIVENESS opt-in OFF — 0 row (silent always-on 금지의 역)"
  PASS=$((PASS+1))
else
  echo "X FAIL: EMISSION-LIVENESS opt-in OFF — $off_rows row (기대 0)"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: self-context-telemetry-allowlist lint discriminating + emission-liveness"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "OK All discriminating tests + emission-liveness passed"
  exit 0
else
  echo "X Some tests failed"
  exit 1
fi
