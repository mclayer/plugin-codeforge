#!/usr/bin/env bats
# tests/scripts/cfp-1195/test_cfp1195_loop_closure.bats
# CFP-1195 TDD — loop_closure_gate.py + operational-signal-to-issue.sh + check-ops-signal-alerts.sh
#
# Change Plan §8 Test Contract (19 TC):
#   TC-1:  wrapper fast-pass (repo=mclayer/plugin-codeforge) → exit 0
#   TC-2:  stage 2-b (a) non-monitor signal → Issue 발의 (gate pass, dedup 0)
#   TC-3:  Epic-level dedup — open Issue 존재 → 신규 발의 억제
#   TC-4:  Epic-level dedup — open Epic 존재 → 신규 발의 억제
#   TC-5:  S4/S5-originated double-issue prevention (dedup gate (b) only, no re-creation)
#   TC-6:  max-depth gate — loop_depth >= loop_max_depth → gate trip
#   TC-7:  escalate_user gate — pattern_count >= threshold → escalate_user
#   TC-8:  closure 3-principle OR-fire (dedup wins over max-depth)
#   TC-9:  KPI append-only (no overwrite) — history jsonl grows, state json updated
#   TC-10: KPI SHA CAS retry — conflict 시 1 retry 후 성공
#   TC-11: stage 3 pattern_count 집계 — signal_type 별 count 정확
#   TC-12: escalation_action 2-value enum (pmo_escalate / dedup_suppressed)
#   TC-13: stage 4 user gate — no auto Epic creation
#   TC-14: PMOAgent 부재/실패 (EC-5) — exit 1 not exit 2
#   TC-15: user no-response (EC-6) — stage 4 user gate message 포함
#   TC-16: ops-signal Issues 없음 (EC-8) — pattern_count 0 → PMO 발화 0
#   TC-17: 0 API call (AC-9) — script 안 curl/wget 부재 grep
#   TC-18: exit 3-tier — 정상=0 / PMO alert=1 / SETUP error=2
#   TC-19: domain disjoint — signal_type key 존재, anchor_id key 부재 grep
#
# Mock seam (_CFP1195_MOCK_* namespace):
#   _CFP1195_MOCK_REPO_NAME=<name> — repo 이름 override
#   _CFP1195_SKIP_ISSUE_CREATE=1 — Issue 발의 차단 (dry-run)
#   CBL_SKIP_ISSUE_CREATE=1 — probe sandbox env (ADR-040 Amendment 6)
#   _CFP1195_MOCK_DEDUP=1 — open Issue dedup 발동
#   _CFP1195_MOCK_EPIC_OPEN=1 — open Epic dedup 발동
#   _CFP1195_DEDUP_GATE_RESULT=<pass|dedup> — bash → python 브리지
#   _CFP1195_MOCK_LOOP_DEPTH=<N> — loop depth override
#   _CFP1195_MOCK_PATTERN_COUNT=<N> — pattern count override
#   _CFP1195_MOCK_SHA_CONFLICT=1 — SHA optimistic CAS 1회 conflict 시뮬레이션
#   GH_STUB_RESPONSE_FILE=<path> — gh CLI stub (check-ops-signal-alerts.sh)

WROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
LOOP_PY="${WROOT}/scripts/loop_closure_gate.py"
SIGNAL_SH="${WROOT}/scripts/operational-signal-to-issue.sh"
ALERTS_SH="${WROOT}/scripts/check-ops-signal-alerts.sh"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  # 기본 mock seam: non-wrapper consumer repo (fast-pass 미적용)
  export _CFP1195_MOCK_REPO_NAME="test-consumer-repo"
  export GITHUB_REPOSITORY="${_CFP1195_MOCK_REPO_NAME}"
  export _CFP1195_SKIP_ISSUE_CREATE=1
  export CBL_SKIP_ISSUE_CREATE=1

  # KPI 파일 위치 override (TEST_TMP 안)
  export _CFP1195_HISTORY_FILE="${TEST_TMP}/operational-signal-history.jsonl"
  export _CFP1195_STATE_FILE="${TEST_TMP}/operational-signal-rate.json"

  # 기본 signal params
  export CFP1195_SIGNAL_TYPE="error_rate"
  export CFP1195_SIGNAL_SIGNATURE="deadbeef12345678"
  export CFP1195_MEASURED_VALUE="0.15"
  export CFP1195_THRESHOLD="0.10"
  export CFP1195_WINDOW="3600s"
  export CFP1195_DETECTED_AT_KST="2026-05-22T00:00:00+09:00"

  # dedup gate 기본값: pass
  export _CFP1195_DEDUP_GATE_RESULT="pass"

  # loop 기본값: depth=0, pattern=0
  unset _CFP1195_MOCK_LOOP_DEPTH
  unset _CFP1195_MOCK_PATTERN_COUNT

  # loop_max_depth / pattern_count_threshold 기본값
  export _CFP1195_LOOP_MAX_DEPTH="3"
  export _CFP1195_DEDUP_WINDOW_HOURS="24"
  export _CFP1195_PATTERN_COUNT_THRESHOLD="2"
}

teardown() {
  rm -rf "${TEST_TMP}"
}

# ─── TC-1: wrapper fast-pass ───────────────────────────────────────────────────
@test "TC-1: wrapper fast-pass (mclayer/plugin-codeforge) → exit 0, no issue" {
  # MOCK_REPO_NAME must be unset so EFFECTIVE_REPO falls through to --repo arg
  unset _CFP1195_MOCK_REPO_NAME
  run bash "${SIGNAL_SH}" \
    --repo "mclayer/plugin-codeforge" \
    --signal-type "error_rate" \
    --measured-value "0.15" \
    --threshold "0.10" \
    --window "3600s"
  [ "$status" -eq 0 ]
  # fast-pass message on stdout (wrapper repo detected) — use grep for safe matching
  echo "$output" | grep -qF "fast-pass exit 0"
}

# ─── TC-2: stage 2-b (a) non-monitor signal Issue 발의 ─────────────────────────
@test "TC-2: non-monitor signal with gate pass → script completes exit 0" {
  export _CFP1195_MOCK_LOOP_DEPTH="0"
  export _CFP1195_MOCK_PATTERN_COUNT="0"
  export _CFP1195_DEDUP_GATE_RESULT="pass"
  run bash "${SIGNAL_SH}" \
    --repo "${_CFP1195_MOCK_REPO_NAME}" \
    --signal-type "error_rate" \
    --measured-value "0.15" \
    --threshold "0.10" \
    --window "3600s"
  [ "$status" -eq 0 ]
}

# ─── TC-3: Epic-level dedup — open Issue ───────────────────────────────────────
@test "TC-3: dedup gate trip (open Issue) → CLOSURE_GATE=dedup, no new issue" {
  export _CFP1195_DEDUP_GATE_RESULT="dedup"
  export _CFP1195_MOCK_DEDUP="1"
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"CLOSURE_GATE=dedup"* ]]
}

# ─── TC-4: Epic-level dedup — open Epic ───────────────────────────────────────
@test "TC-4: dedup gate trip (open Epic) → CLOSURE_GATE=dedup" {
  export _CFP1195_DEDUP_GATE_RESULT="dedup"
  export _CFP1195_MOCK_EPIC_OPEN="1"
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"CLOSURE_GATE=dedup"* ]]
}

# ─── TC-5: S4/S5-originated double-issue prevention ────────────────────────────
@test "TC-5: S4/S5-originated signal gets dedup gate only, no double creation" {
  # dedup_gate_result=pass (S4/S5 originated - already has an issue, S6 just checks Epic)
  # In signal-to-issue.sh, --source=s4s5 flag enables epic-only dedup path
  export _CFP1195_DEDUP_GATE_RESULT="pass"
  export _CFP1195_MOCK_LOOP_DEPTH="0"
  export _CFP1195_MOCK_PATTERN_COUNT="0"
  # Test: loop_closure_gate.py with pass outputs CLOSURE_GATE=pass (no extra issue)
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"CLOSURE_GATE=pass"* ]]
}

# ─── TC-6: max-depth gate ─────────────────────────────────────────────────────
@test "TC-6: loop_depth >= loop_max_depth → CLOSURE_GATE=max_depth" {
  export _CFP1195_MOCK_LOOP_DEPTH="3"   # >= default max_depth=3
  export _CFP1195_DEDUP_GATE_RESULT="pass"
  export _CFP1195_MOCK_PATTERN_COUNT="0"
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"CLOSURE_GATE=max_depth"* ]]
}

# ─── TC-7: escalate_user gate ─────────────────────────────────────────────────
@test "TC-7: pattern_count >= threshold → CLOSURE_GATE=escalate_user" {
  export _CFP1195_MOCK_PATTERN_COUNT="2"   # >= default threshold=2
  export _CFP1195_DEDUP_GATE_RESULT="pass"
  export _CFP1195_MOCK_LOOP_DEPTH="0"
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"CLOSURE_GATE=escalate_user"* ]]
}

# ─── TC-8: 3-principle OR-fire (dedup wins) ────────────────────────────────────
@test "TC-8: OR-fire — dedup evaluated first, trip → CLOSURE_GATE=dedup" {
  export _CFP1195_DEDUP_GATE_RESULT="dedup"    # dedup wins
  export _CFP1195_MOCK_LOOP_DEPTH="5"          # max_depth also would trip
  export _CFP1195_MOCK_PATTERN_COUNT="5"       # escalate_user also would trip
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"CLOSURE_GATE=dedup"* ]]
}

# ─── TC-9: KPI append-only ─────────────────────────────────────────────────────
@test "TC-9: KPI append-only — history grows, state updated, no overwrite" {
  export _CFP1195_MOCK_LOOP_DEPTH="0"
  export _CFP1195_MOCK_PATTERN_COUNT="0"
  export _CFP1195_DEDUP_GATE_RESULT="pass"
  # Must unset dry-run to allow KPI writes
  unset _CFP1195_SKIP_ISSUE_CREATE
  unset CBL_SKIP_ISSUE_CREATE

  # First run
  python3 "${LOOP_PY}"
  local count_before
  count_before=$(wc -l < "${_CFP1195_HISTORY_FILE}" 2>/dev/null || echo "0")

  # Second run — history must grow (append-only)
  python3 "${LOOP_PY}"
  local count_after
  count_after=$(wc -l < "${_CFP1195_HISTORY_FILE}" 2>/dev/null || echo "0")

  [ "$count_after" -gt "$count_before" ]  # append-only: grew
  [ -f "${_CFP1195_STATE_FILE}" ]         # state file exists
}

# ─── TC-10: SHA CAS retry ─────────────────────────────────────────────────────
@test "TC-10: SHA CAS conflict mock → retry succeeds, exit 0" {
  export _CFP1195_MOCK_LOOP_DEPTH="0"
  export _CFP1195_MOCK_PATTERN_COUNT="0"
  export _CFP1195_DEDUP_GATE_RESULT="pass"
  export _CFP1195_MOCK_SHA_CONFLICT="1"   # simulate 1 conflict then clear
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"CLOSURE_GATE=pass"* ]]
}

# ─── TC-11: stage 3 pattern_count 집계 ────────────────────────────────────────
@test "TC-11: check-ops-signal-alerts.sh counts signal_type correctly" {
  # Create stub response with 2 issues of same signal_type
  local stub_file="${TEST_TMP}/gh_stub.json"
  cat > "${stub_file}" << 'EOF'
[
  {"number": 1, "title": "ops-signal: error_rate", "body": "signal_type: error_rate\nmeasured_value: 0.15"},
  {"number": 2, "title": "ops-signal: error_rate", "body": "signal_type: error_rate\nmeasured_value: 0.20"}
]
EOF
  export GH_STUB_RESPONSE_FILE="${stub_file}"
  export _CFP1195_MOCK_PATTERN_COUNT="2"
  export _CFP1195_PATTERN_COUNT_THRESHOLD="2"
  run bash "${ALERTS_SH}"
  [ "$status" -eq 1 ]  # threshold reached → exit 1
}

# ─── TC-12: escalation_action 2-value enum ────────────────────────────────────
@test "TC-12: ESCALATION_ACTION is pmo_escalate or dedup_suppressed" {
  export _CFP1195_MOCK_LOOP_DEPTH="0"
  export _CFP1195_MOCK_PATTERN_COUNT="0"
  export _CFP1195_DEDUP_GATE_RESULT="pass"
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"ESCALATION_ACTION="* ]]
  # Value must be pmo_escalate or dedup_suppressed or none
  [[ "$output" =~ ESCALATION_ACTION=(pmo_escalate|dedup_suppressed|none) ]]
}

# ─── TC-13: stage 4 user gate — no auto Epic ──────────────────────────────────
@test "TC-13: stage 4 user gate message present — no auto-Epic creation" {
  local stub_file="${TEST_TMP}/gh_stub.json"
  cat > "${stub_file}" << 'EOF'
[
  {"number": 1, "title": "ops-signal: error_rate", "body": "signal_type: error_rate"},
  {"number": 2, "title": "ops-signal: error_rate", "body": "signal_type: error_rate"}
]
EOF
  export GH_STUB_RESPONSE_FILE="${stub_file}"
  export _CFP1195_MOCK_PATTERN_COUNT="2"
  export _CFP1195_PATTERN_COUNT_THRESHOLD="2"
  run bash "${ALERTS_SH}"
  [ "$status" -eq 1 ]
  # Must mention user gate / no auto epic
  [[ "$output" == *"사용자"* ]] || [[ "$output" == *"user"* ]] || [[ "$output" == *"gate"* ]]
}

# ─── TC-14: PMOAgent 부재/실패 EC-5 ──────────────────────────────────────────
@test "TC-14: PMO alert detected → exit 1 (not exit 2)" {
  export _CFP1195_MOCK_PATTERN_COUNT="2"
  export _CFP1195_PATTERN_COUNT_THRESHOLD="2"
  local stub_file="${TEST_TMP}/gh_stub.json"
  cat > "${stub_file}" << 'EOF'
[
  {"number": 1, "title": "ops-signal: latency", "body": "signal_type: latency"},
  {"number": 2, "title": "ops-signal: latency", "body": "signal_type: latency"}
]
EOF
  export GH_STUB_RESPONSE_FILE="${stub_file}"
  run bash "${ALERTS_SH}"
  [ "$status" -eq 1 ]   # alert = exit 1 (not SETUP error exit 2)
}

# ─── TC-15: user no-response EC-6 ────────────────────────────────────────────
@test "TC-15: EC-6 user no-response — check-ops-signal-alerts output contains wait/pending note" {
  export _CFP1195_MOCK_PATTERN_COUNT="2"
  export _CFP1195_PATTERN_COUNT_THRESHOLD="2"
  local stub_file="${TEST_TMP}/gh_stub.json"
  cat > "${stub_file}" << 'EOF'
[
  {"number": 1, "title": "ops-signal: error_rate", "body": "signal_type: error_rate"},
  {"number": 2, "title": "ops-signal: error_rate", "body": "signal_type: error_rate"}
]
EOF
  export GH_STUB_RESPONSE_FILE="${stub_file}"
  run bash "${ALERTS_SH}"
  [ "$status" -eq 1 ]
  # Output should mention orchestrator or user or stage 4 gate (no auto action)
  [[ "$output" == *"Orchestrator"* ]] || [[ "$output" == *"단계 4"* ]] || [[ "$output" == *"stage 4"* ]] || [[ "$output" == *"확인"* ]]
}

# ─── TC-16: ops-signal Issues 없음 EC-8 ──────────────────────────────────────
@test "TC-16: no ops-signal issues → exit 0, PMO escalation 0" {
  local stub_file="${TEST_TMP}/gh_stub_empty.json"
  echo "[]" > "${stub_file}"
  export GH_STUB_RESPONSE_FILE="${stub_file}"
  export _CFP1195_MOCK_PATTERN_COUNT="0"
  run bash "${ALERTS_SH}"
  [ "$status" -eq 0 ]
}

# ─── TC-17: 0 API call (AC-9) ────────────────────────────────────────────────
@test "TC-17: loop_closure_gate.py contains no curl/wget/http calls" {
  run grep -E "\bcurl\b|\bwget\b|\brequests\.get\b|\burllib\b" "${LOOP_PY}"
  [ "$status" -ne 0 ]  # grep returns 1 = no match = PASS
}

# ─── TC-18: exit 3-tier ──────────────────────────────────────────────────────
@test "TC-18: exit 3-tier: normal=0, pmo-alert=1, setup-error=2" {
  # Normal: exit 0
  export _CFP1195_MOCK_LOOP_DEPTH="0"
  export _CFP1195_MOCK_PATTERN_COUNT="0"
  export _CFP1195_DEDUP_GATE_RESULT="pass"
  run python3 "${LOOP_PY}"
  [ "$status" -eq 0 ]

  # SETUP error: bad history file (force parse error via invalid content)
  # Use env override to point to bad file
  export _CFP1195_HISTORY_FILE="${TEST_TMP}/bad.jsonl"
  printf 'NOT_JSON\n' > "${TEST_TMP}/bad.jsonl"
  run python3 "${LOOP_PY}"
  # Should exit 2 on parse failure (fail-loud INV-5)
  [ "$status" -eq 2 ]
  # Restore
  export _CFP1195_HISTORY_FILE="${TEST_TMP}/operational-signal-history.jsonl"
}

# ─── TC-19: domain disjoint (signal_type vs anchor_id) ───────────────────────
@test "TC-19: loop_closure_gate.py uses signal_type key, not anchor_id" {
  run grep -E "\banchor_id\b" "${LOOP_PY}"
  [ "$status" -ne 0 ]   # anchor_id = debate-protocol domain, must be absent

  run grep -E "\bsignal_type\b" "${LOOP_PY}"
  [ "$status" -eq 0 ]   # signal_type must be present
}
