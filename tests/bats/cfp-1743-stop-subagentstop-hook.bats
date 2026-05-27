#!/usr/bin/env bats
#
# cfp-1743-stop-subagentstop-hook.bats
# CFP-1743 / ADR-115 §결정 2·3·5 — Stop + SubagentStop hook (record-only, block 금지)
#
# TDD RED→GREEN stash proof (CFP-1334 / ADR-082 §결정 11.A):
#   RED:   stash hooks/stop + hooks/subagent-stop + scripts/lib/append_stop_event.py
#          → TC-1~TC-5 fail (hook 부재 / ledger 미작성)
#   GREEN: restore (stash pop) → 10/10 pass
#   verified: 2026-05-27 KST (Story §0 Live Progress 참조)
#
# 10 Test cases:
#   TC-1:  stop hook exit 0 + ledger row append
#   TC-2:  subagent-stop hook exit 0 + ledger row append
#   TC-3:  ledger row JSON 유효성 (hook_source enum + hook_decision: record-only)
#   TC-4:  양 hook 순차 호출 시 2 row append 보존
#   TC-5:  block 금지 검증 — stdout JSON 안 block / permissionDecision:deny 부재
#   TC-6:  hooks.json Stop entry 안 stop command + SubagentStop entry 존재
#   TC-7:  hooks.json JSON 유효성
#   TC-8:  BYPASS_CODEFORGE_STOP=1 → stderr audit + ledger row 0건
#   TC-9:  BYPASS_CODEFORGE_SUBAGENT_STOP=1 → stderr audit + ledger row 0건
#   TC-10: ledger file 0600 mode (Unix only — Windows skip)
#

HOOK_STOP="hooks/stop"
HOOK_SUBAGENT_STOP="hooks/subagent-stop"
APPEND_SCRIPT="scripts/lib/append_stop_event.py"
HOOKS_JSON="hooks/hooks.json"

# stop hook 기본 stdin JSON (stop_hook_active 포함)
_make_stop_payload() {
  printf '{"stop_hook_active": true, "stop_reason": "idle"}'
}

# subagent-stop hook 기본 stdin JSON
_make_subagent_stop_payload() {
  printf '{"stop_hook_active": false, "subagent_completed": true}'
}

setup() {
  # 임시 ledger 디렉터리 (테스트 격리)
  export CLAUDE_PROJECT_DIR="$(mktemp -d)"
  export CLAUDE_SESSION_ID="test-session-cfp-1743"
  export CLAUDE_PLUGIN_ROOT="$(pwd)"

  # 기존 레저 초기화
  mkdir -p "${CLAUDE_PROJECT_DIR}/.claude/ledger"
  LEDGER_FILE="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"
}

teardown() {
  rm -rf "${CLAUDE_PROJECT_DIR}"
}

# ── TC-1: stop hook exit 0 + ledger row append ───────────────────────────────
@test "TC-1: stop hook exits 0 and appends ledger row" {
  # hook 파일 부재 시 FAIL (RED proof — skip 아님)
  if [ ! -f "$HOOK_STOP" ]; then
    echo "RED: hooks/stop not found — implementation required"
    return 1
  fi

  run bash -c "CLAUDE_PROJECT_DIR='${CLAUDE_PROJECT_DIR}' CLAUDE_SESSION_ID='${CLAUDE_SESSION_ID}' CLAUDE_PLUGIN_ROOT='$(pwd)' \
  bash '${HOOK_STOP}' <<< '{\"stop_hook_active\": true, \"stop_reason\": \"idle\"}'"

  [ "$status" -eq 0 ]

  LEDGER_FILE="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"
  [ -f "$LEDGER_FILE" ]

  ROW_COUNT="$(wc -l < "$LEDGER_FILE" | tr -d ' ')"
  [ "$ROW_COUNT" -ge 1 ]
}

# ── TC-2: subagent-stop hook exit 0 + ledger row append ──────────────────────
@test "TC-2: subagent-stop hook exits 0 and appends ledger row" {
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then
    echo "RED: hooks/subagent-stop not found — implementation required"
    return 1
  fi

  run bash -c "CLAUDE_PROJECT_DIR='${CLAUDE_PROJECT_DIR}' CLAUDE_SESSION_ID='${CLAUDE_SESSION_ID}' CLAUDE_PLUGIN_ROOT='$(pwd)' \
  bash '${HOOK_SUBAGENT_STOP}' <<< '{\"stop_hook_active\": false, \"subagent_completed\": true}'"

  [ "$status" -eq 0 ]

  LEDGER_FILE="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"
  [ -f "$LEDGER_FILE" ]

  ROW_COUNT="$(wc -l < "$LEDGER_FILE" | tr -d ' ')"
  [ "$ROW_COUNT" -ge 1 ]
}

# ── TC-3: ledger row JSON 유효성 (hook_source enum + hook_decision: record-only) ──
@test "TC-3: ledger row valid JSON with hook_source enum and hook_decision record-only" {
  if [ ! -f "$HOOK_STOP" ]; then
    echo "RED: hooks/stop not found"
    return 1
  fi
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then
    echo "RED: hooks/subagent-stop not found"
    return 1
  fi

  LEDGER_FILE="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"

  # stop hook 실행
  CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_STOP" <<< '{"stop_hook_active": true, "stop_reason": "idle"}'

  # subagent-stop hook 실행
  CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_SUBAGENT_STOP" <<< '{"stop_hook_active": false}'

  # 각 row 검증
  while IFS= read -r line; do
    [ -n "$line" ] || continue

    # JSON 유효성
    echo "$line" | python3 -m json.tool > /dev/null 2>&1

    # hook_decision = record-only
    DECISION="$(echo "$line" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('hook_decision',''))" 2>/dev/null)"
    [ "$DECISION" = "record-only" ]

    # hook_source ∈ {stop, subagent-stop}
    SOURCE="$(echo "$line" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('hook_source',''))" 2>/dev/null)"
    [[ "$SOURCE" == "stop" || "$SOURCE" == "subagent-stop" ]]

  done < "$LEDGER_FILE"
}

# ── TC-4: 양 hook 순차 호출 시 2 row append 보존 ─────────────────────────────
@test "TC-4: sequential calls append 2 rows to ledger" {
  if [ ! -f "$HOOK_STOP" ]; then echo "RED: hooks/stop not found"; return 1; fi
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then echo "RED: hooks/subagent-stop not found"; return 1; fi

  LEDGER_FILE="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"

  CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_STOP" <<< '{"stop_hook_active": true}'

  CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_SUBAGENT_STOP" <<< '{"stop_hook_active": false}'

  ROW_COUNT="$(wc -l < "$LEDGER_FILE" | tr -d ' ')"
  [ "$ROW_COUNT" -eq 2 ]

  # 첫 번째 row = stop
  SOURCE_1="$(sed -n '1p' "$LEDGER_FILE" | python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('hook_source',''))" 2>/dev/null)"
  [ "$SOURCE_1" = "stop" ]

  # 두 번째 row = subagent-stop
  SOURCE_2="$(sed -n '2p' "$LEDGER_FILE" | python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('hook_source',''))" 2>/dev/null)"
  [ "$SOURCE_2" = "subagent-stop" ]
}

# ── TC-5: block 금지 검증 — stdout JSON 안 block / permissionDecision:deny 부재 ──
@test "TC-5: stop hook stdout must NOT contain block or permissionDecision:deny (P0)" {
  if [ ! -f "$HOOK_STOP" ]; then echo "RED: hooks/stop not found"; return 1; fi

  STDOUT="$(CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_STOP" <<< '{"stop_hook_active": true}' 2>/dev/null)"

  # stdout 에 "block" 키워드 부재 확인 (ADR-115 §결정 2 binding constraint)
  echo "$STDOUT" | grep -qv '"block"' || {
    echo "FAIL: stdout contains 'block' key — ADR-115 §결정 2 violation"
    return 1
  }

  # stdout 에 permissionDecision:deny 부재 확인
  echo "$STDOUT" | grep -qv 'permissionDecision.*deny' || {
    echo "FAIL: stdout contains permissionDecision:deny — ADR-115 §결정 2 violation"
    return 1
  }
}

@test "TC-5b: subagent-stop hook stdout must NOT contain block or permissionDecision:deny (P0)" {
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then echo "RED: hooks/subagent-stop not found"; return 1; fi

  STDOUT="$(CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_SUBAGENT_STOP" <<< '{"stop_hook_active": false}' 2>/dev/null)"

  echo "$STDOUT" | grep -qv '"block"' || {
    echo "FAIL: subagent-stop stdout contains 'block' key — ADR-115 §결정 2 violation"
    return 1
  }

  echo "$STDOUT" | grep -qv 'permissionDecision.*deny' || {
    echo "FAIL: subagent-stop stdout contains permissionDecision:deny"
    return 1
  }
}

# ── TC-6: hooks.json Stop + SubagentStop entry presence ──────────────────────
@test "TC-6: hooks.json has Stop entry with stop command AND SubagentStop entry" {
  [ -f "$HOOKS_JSON" ] || { echo "FAIL: hooks.json not found"; return 1; }

  # Stop 섹션 안 stop command presence
  STOP_CMD_PRESENT="$(python3 -c "
import json
with open('${HOOKS_JSON}') as f:
    data = json.load(f)
hooks = data.get('hooks', {})
stop_entries = hooks.get('Stop', [])
found = False
for entry in stop_entries:
    for h in entry.get('hooks', []):
        cmd = h.get('command', '')
        if 'run-hook.cmd' in cmd and 'stop' in cmd and 'plain-language' not in cmd:
            found = True
print('yes' if found else 'no')
" 2>/dev/null)"
  [ "$STOP_CMD_PRESENT" = "yes" ]

  # SubagentStop entry presence
  SUBAGENT_STOP_PRESENT="$(python3 -c "
import json
with open('${HOOKS_JSON}') as f:
    data = json.load(f)
hooks = data.get('hooks', {})
sub_entries = hooks.get('SubagentStop', [])
found = False
for entry in sub_entries:
    for h in entry.get('hooks', []):
        cmd = h.get('command', '')
        if 'run-hook.cmd' in cmd and 'subagent-stop' in cmd:
            found = True
print('yes' if found else 'no')
" 2>/dev/null)"
  [ "$SUBAGENT_STOP_PRESENT" = "yes" ]
}

# ── TC-7: hooks.json JSON 유효성 ──────────────────────────────────────────────
@test "TC-7: hooks.json is valid JSON" {
  [ -f "$HOOKS_JSON" ] || { echo "FAIL: hooks.json not found"; return 1; }
  python3 -m json.tool "$HOOKS_JSON" > /dev/null 2>&1
}

# ── TC-8: BYPASS_CODEFORGE_STOP=1 → stderr audit + ledger row 0건 ─────────────
@test "TC-8: BYPASS_CODEFORGE_STOP=1 suppresses ledger write with audit stderr" {
  if [ ! -f "$HOOK_STOP" ]; then echo "RED: hooks/stop not found"; return 1; fi

  LEDGER_FILE="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"

  STDERR_OUT="$(BYPASS_CODEFORGE_STOP=1 CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" \
    CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_STOP" <<< '{"stop_hook_active": true}' 2>&1 >/dev/null)"

  # exit 0 은 run 으로 확인 불가 (위는 subshell 분리) — 별도
  run bash -c "BYPASS_CODEFORGE_STOP=1 CLAUDE_PROJECT_DIR='${CLAUDE_PROJECT_DIR}' \
    CLAUDE_SESSION_ID='${CLAUDE_SESSION_ID}' CLAUDE_PLUGIN_ROOT='$(pwd)' \
    bash '${HOOK_STOP}' <<< '{\"stop_hook_active\": true}'"
  [ "$status" -eq 0 ]

  # ledger row 0건 (bypass 시 미작성)
  if [ -f "$LEDGER_FILE" ]; then
    ROW_COUNT="$(wc -l < "$LEDGER_FILE" | tr -d ' ')"
    [ "$ROW_COUNT" -eq 0 ]
  fi

  # audit marker 포함 여부 (stderr)
  echo "$STDERR_OUT" | grep -q "BYPASS_CODEFORGE_STOP"
}

# ── TC-9: BYPASS_CODEFORGE_SUBAGENT_STOP=1 → stderr audit + ledger row 0건 ───
@test "TC-9: BYPASS_CODEFORGE_SUBAGENT_STOP=1 suppresses ledger write with audit stderr" {
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then echo "RED: hooks/subagent-stop not found"; return 1; fi

  LEDGER_FILE="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"

  STDERR_OUT="$(BYPASS_CODEFORGE_SUBAGENT_STOP=1 CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" \
    CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_SUBAGENT_STOP" <<< '{"stop_hook_active": false}' 2>&1 >/dev/null)"

  run bash -c "BYPASS_CODEFORGE_SUBAGENT_STOP=1 CLAUDE_PROJECT_DIR='${CLAUDE_PROJECT_DIR}' \
    CLAUDE_SESSION_ID='${CLAUDE_SESSION_ID}' CLAUDE_PLUGIN_ROOT='$(pwd)' \
    bash '${HOOK_SUBAGENT_STOP}' <<< '{\"stop_hook_active\": false}'"
  [ "$status" -eq 0 ]

  if [ -f "$LEDGER_FILE" ]; then
    ROW_COUNT="$(wc -l < "$LEDGER_FILE" | tr -d ' ')"
    [ "$ROW_COUNT" -eq 0 ]
  fi

  echo "$STDERR_OUT" | grep -q "BYPASS_CODEFORGE_SUBAGENT_STOP"
}

# ── TC-10: ledger file 0600 mode (Unix only) ─────────────────────────────────
@test "TC-10: ledger file has 0600 mode (Unix only, skipped on Windows/MSYS)" {
  # Windows / MSYS / MinGW 환경 skip
  if [[ "$(uname -s 2>/dev/null)" == *MINGW* ]] || \
     [[ "$(uname -s 2>/dev/null)" == *MSYS* ]] || \
     [[ "$(uname -s 2>/dev/null)" == *CYGWIN* ]]; then
    skip "Windows/MSYS environment — file mode check skipped"
  fi

  if [ ! -f "$HOOK_STOP" ]; then echo "RED: hooks/stop not found"; return 1; fi

  LEDGER_FILE="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"

  CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_STOP" <<< '{"stop_hook_active": true}'

  [ -f "$LEDGER_FILE" ]

  # 0600 모드 확인
  FILE_MODE="$(stat -c "%a" "$LEDGER_FILE" 2>/dev/null || stat -f "%Lp" "$LEDGER_FILE" 2>/dev/null || echo "unknown")"
  [ "$FILE_MODE" = "600" ]
}
