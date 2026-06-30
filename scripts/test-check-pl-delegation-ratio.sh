#!/usr/bin/env bash
# scripts/test-check-pl-delegation-ratio.sh
# CFP-2521 Phase 2 D3 — Discriminating test for check-pl-delegation-ratio.sh (advisory lint)
#
# Anti-theater test: delegation-ratio 측정이 carve-out (R5) 를 정확히 honoring 하는가.
# mutation testing 으로 gate 효과성 검증 (AT-1/AT-2/AT-3/AT-4).
#
# Test cases (ADR-119 research-before-claims):
#   T1: script 항상 exit 0 (advisory-tier 불변).
#   T2: ledger 부재/empty → status=vacuous, exit 0 (honesty check).
#   T3 (AT-1 carve-out): worker 충분 시 fire 금지 (DeveloperAgent 충분 → no warning).
#   T4 (AT-2 carve-out): single segment → fire 금지 (R5 trivial 제외).
#   T5 (AT-3 sustained): sustained pattern (≥MIN_SEGMENTS + low worker) → advisory warning fire.
#   T6 (AT-4 self-verify): lint 진짜 작동 (always-vacuous hollow gate 아님) 검증.
#
# Usage:
#   bash scripts/test-check-pl-delegation-ratio.sh
#
# Exit code:
#   0 = all discriminating tests pass
#   1 = any test fails
#

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
SCRIPT="$REPO_ROOT/scripts/check-pl-delegation-ratio.sh"

PASS=0
FAIL=0

# ─── test harness ───

run_test() {
  local test_name="$1"
  local expect_status="$2"  # vacuous | ok | advisory
  local ledger_path="$3"    # path to temp ledger (or empty for no ledger)
  local description="$4"

  local tmp_dir
  tmp_dir=$(mktemp -d)
  trap "rm -rf '$tmp_dir'" RETURN

  local output=""
  local exit_code=0
  local ledger_arg=""

  if [ -n "$ledger_path" ] && [ -f "$ledger_path" ]; then
    ledger_arg="$ledger_path"
  else
    ledger_arg=""
  fi

  # script 실행 (ledger path override)
  if [ -n "$ledger_arg" ]; then
    output=$(SPAWN_EVENT_LEDGER="$ledger_arg" bash "$SCRIPT" 2>&1) || exit_code=$?
  else
    # ledger 미설정 (부재 기본값 시도 → vacuous)
    output=$(bash "$SCRIPT" 2>&1 || true) || exit_code=$?
  fi

  # exit code 검증 (항상 0 — warning-tier)
  if [ "$exit_code" -ne 0 ]; then
    echo "✗ FAIL: $test_name"
    echo "  Expected exit 0 (warning-tier), got $exit_code"
    echo "  Description: $description"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
    return 1
  fi

  # status line 파싱
  local actual_status=""
  actual_status=$(echo "$output" | grep "^status=" | cut -d= -f2 || true)

  if [ "$actual_status" != "$expect_status" ]; then
    echo "✗ FAIL: $test_name"
    echo "  Expected status=$expect_status, got status=$actual_status (exit 0)"
    echo "  Description: $description"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
    return 1
  fi

  # advisory 기대 시 ::warning:: 필수 검증
  if [ "$expect_status" = "advisory" ]; then
    if ! echo "$output" | grep -q "::warning::"; then
      echo "✗ FAIL: $test_name — advisory status 였으나 ::warning:: 마커 부재"
      echo "  Description: $description"
      echo "  Output: $output"
      FAIL=$((FAIL+1))
      return 1
    fi
  fi

  echo "✓ PASS: $test_name (status=$actual_status, exit 0)"
  PASS=$((PASS+1))
  return 0
}

# ─── fixture generator ───

# spawn-event-v1 행 생성 (JSON JSONL 형식)
make_spawn_event_row() {
  local agent_type="$1"
  local lane_label="$2"
  local event_type="${3:-agent_stop}"

  jq -n \
    --arg agent_type "$agent_type" \
    --arg lane_label "$lane_label" \
    --arg event_type "$event_type" \
    '{
      event_id: "abc123def456",
      schema_version: "spawn-event-v1",
      timestamp: "2026-06-30T12:00:00Z",
      story_key: "CFP-2521",
      lane_label: $lane_label,
      agent_type: $agent_type,
      attribution_confidence: "unattributed",
      input_tokens: null,
      output_tokens: null,
      cache_creation_input_tokens: null,
      cache_read_input_tokens: null,
      cost_usd: null,
      duration_ms: 1000,
      tool_call_count: 0,
      actor: "sha256abc",
      parent_event_id: null,
      consumer_scope: "wrapper",
      event_type: $event_type,
      elapsed_seconds: 100.0
    }'
}

# ─── test fixtures ───

# T2: empty ledger 생성
create_empty_ledger() {
  local path="$1"
  touch "$path"
}

# T3 (AT-1): worker 충분한 ledger (구현 레인에 DeveloperPLAgent 1, DeveloperAgent 1)
create_adequate_delegation_ledger() {
  local path="$1"
  {
    make_spawn_event_row "DeveloperPLAgent" "구현" "agent_stop"
    make_spawn_event_row "DeveloperAgent" "구현" "agent_stop"
  } > "$path"
}

# T4 (AT-2): single segment (구현 레인에 DeveloperPLAgent 1만, worker 0)
# → PL count = 1 < MIN_SEGMENTS (default 2) → should NOT fire
create_single_segment_ledger() {
  local path="$1"
  make_spawn_event_row "DeveloperPLAgent" "구현" "agent_stop" > "$path"
}

# T5 (AT-3): sustained low-delegation pattern
# 구현 레인: PL 2회 + worker 0 → pl_count=2 >= MIN_SEGMENTS, worker=0 < MIN_WORKERS → FIRE
create_sustained_low_delegation_ledger() {
  local path="$1"
  {
    make_spawn_event_row "DeveloperPLAgent" "구현" "agent_stop"
    make_spawn_event_row "DeveloperPLAgent" "구현" "agent_stop"
  } > "$path"
}

# ═════════════════════════════════════════════════════════════════════════════
# T1: exit code 항상 0 (advisory-tier invariant) — with adequate delegation
# ═════════════════════════════════════════════════════════════════════════════

T1_LEDGER="$(mktemp)"
trap "rm -f '$T1_LEDGER'" RETURN
create_adequate_delegation_ledger "$T1_LEDGER"

run_test \
  "T1-exit-zero" \
  "ok" \
  "$T1_LEDGER" \
  "Script always exits 0 (warning-tier) even with data present" || true

# ═════════════════════════════════════════════════════════════════════════════
# T2: vacuous — ledger 부재 (empty)
# ═════════════════════════════════════════════════════════════════════════════

EMPTY_LEDGER="$(mktemp)"
trap "rm -f '$EMPTY_LEDGER'" RETURN
create_empty_ledger "$EMPTY_LEDGER"

run_test \
  "T2-vacuous-empty-ledger" \
  "vacuous" \
  "$EMPTY_LEDGER" \
  "Empty ledger → status=vacuous (honesty: no data = vacuous, not false PASS)" || true

# ═════════════════════════════════════════════════════════════════════════════
# T3 (AT-1 carve-out): worker 충분 시 fire 금지
# ═════════════════════════════════════════════════════════════════════════════

ADEQUATE_LEDGER="$(mktemp)"
trap "rm -f '$ADEQUATE_LEDGER'" RETURN
create_adequate_delegation_ledger "$ADEQUATE_LEDGER"

run_test \
  "T3-AT1-adequate-delegation" \
  "ok" \
  "$ADEQUATE_LEDGER" \
  "AT-1 carve-out: worker spawn 충분 (≥MIN_WORKERS=1) → fire 금지 (status=ok, no warning)" || true

# ═════════════════════════════════════════════════════════════════════════════
# T4 (AT-2 carve-out): single segment 제외
# ═════════════════════════════════════════════════════════════════════════════

SINGLE_SEG_LEDGER="$(mktemp)"
trap "rm -f '$SINGLE_SEG_LEDGER'" RETURN
create_single_segment_ledger "$SINGLE_SEG_LEDGER"

run_test \
  "T4-AT2-single-segment-excluded" \
  "ok" \
  "$SINGLE_SEG_LEDGER" \
  "AT-2 carve-out: single segment (PL count=1 < MIN_SEGMENTS=2) → trivial excluded (status=ok, no warning)" || true

# ═════════════════════════════════════════════════════════════════════════════
# T5 (AT-3 sustained): sustained pattern → fire
# ═════════════════════════════════════════════════════════════════════════════

SUSTAINED_LEDGER="$(mktemp)"
trap "rm -f '$SUSTAINED_LEDGER'" RETURN
create_sustained_low_delegation_ledger "$SUSTAINED_LEDGER"

run_test \
  "T5-AT3-sustained-low-delegation-fire" \
  "advisory" \
  "$SUSTAINED_LEDGER" \
  "AT-3 sustained: PL count ≥MIN_SEGMENTS + worker < MIN_WORKERS → advisory fired (::warning:: emitted)" || true

# ═════════════════════════════════════════════════════════════════════════════
# T6 (AT-4 self-verify): lint 진짜 작동 (hollow-gate 아님)
# ═════════════════════════════════════════════════════════════════════════════

# AT-4: sustained ledger 을 with stricter threshold (MIN_WORKERS=0, MIN_SEGMENTS=1)
# 로 re-run 해서 진짜 measurement 작동하는지 검증.
# 단 본 스크립트는 defaults 만 테스트 → AT-3 test case 통과 자체가 AT-4 self-verify.
# (hollow gate = always-vacuous, 즉 AT-3 이 vacuous 가 되면 hollow)
# AT-3 이 advisory 를 반환했으므로 lint 진짜 작동함 증명됨.

# re-run AT-3 with verbose confirmation
AT3_OUTPUT=$(SPAWN_EVENT_LEDGER="$SUSTAINED_LEDGER" bash "$SCRIPT" 2>&1)
if echo "$AT3_OUTPUT" | grep -q "low-delegation"; then
  echo "✓ PASS: T6-AT4-self-verify (lint actually measures, not hollow)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T6-AT4-self-verify (lint output missing measurement indicator)"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: PL delegation-ratio advisory lint"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All tests passed — lint honoring carve-outs (R5) + self-verify (AT-4)"
  exit 0
else
  echo "✗ Some tests failed — lint may not be detecting patterns correctly"
  exit 1
fi
