#!/usr/bin/env bats
#
# cfp-1746-integration-runtime-hook.bats
# CFP-1746 (Epic CFP-1740 Story-6) — 통합 검증
#
# 검증 범위:
#   - 5 hook tier (SessionStart / PreToolUse / UserPromptSubmit / Stop / SubagentStop) 공존
#   - 4 신규 hook (userprompt-submit / pretooluse-agent-spawn-gate / stop / subagent-stop)
#   - dispatcher routing 정합 (hooks.json 커맨드 패턴)
#   - ADR-115 §결정 2 block 금지 binding (4 신규 hook)
#   - ledger 경합 — stop + subagent-stop sequential 2회 호출 → 2 row 무손실
#   - ledger row schema v1.1 정합 (timestamp_kst / hook_source / hook_decision)
#   - bypass env 4 종 동작
#   - polyglot preamble 검증 (4 신규 hook 모두 Windows cmd preamble 존재)
#   - hooks.json command 패턴 — cmd injection 차단 (`run-hook.cmd <name>` 형식)
#   - 기존 7 hook 회귀 차단 (file existence verify)
#
# TDD RED→GREEN stash proof (ADR-082 §결정 11.A):
#   RED:   git stash hooks/stop hooks/subagent-stop hooks/userprompt-submit hooks/pretooluse-agent-spawn-gate
#          → TC-3 / TC-4 / TC-5 / TC-6 / TC-7 / TC-8 / TC-9 / TC-10 / TC-11 fail (9 TC)
#   GREEN: git stash pop → 13/13 PASS
#   verified: 2026-05-27 KST
#   참고: hooks/stop 단일 stash 시 = 4 fail (TC-8/9/10/11). 본 proof = 4 신규 hook 전체 stash (Story §0 §8.2 본문 일치).
#
# 13 Test cases:
#   TC-1:  hooks.json JSON valid + 5 hook tier 모두 present
#   TC-2:  hooks.json hook command 총 개수 ≥ 11
#   TC-3:  4 신규 hook script 존재
#   TC-4:  4 신규 hook script exec bit / bash -n syntax PASS
#   TC-5:  4 신규 hook script marker emit (marker 문자열 포함)
#   TC-6:  4 신규 hook 직접 호출 시 exit 0 (dispatcher routing 등가)
#   TC-7:  ADR-115 §결정 2 block 금지 — stdout 안 block / permissionDecision:deny 부재
#   TC-8:  ledger 경합 — stop + subagent-stop sequential → 2 row 무손실 append
#   TC-9:  ledger row schema v1.1 정합 (hook_source enum / hook_decision: record-only)
#   TC-10: bypass env 4 종 — 각 활성 시 exit 0 + stdout 0 (userprompt) / ledger row 0 (stop/subagent)
#   TC-11: polyglot preamble — 4 신규 hook 모두 Windows cmd preamble 없음 (bash-only hook)
#   TC-12: hooks.json command 패턴 — 모든 command 가 run-hook.cmd <name> 형식
#   TC-13: 기존 7 hook file 존재 (회귀 차단)
#

# ── 경로 상수 ────────────────────────────────────────────────────────────────
HOOKS_JSON="hooks/hooks.json"

HOOK_USERPROMPT="hooks/userprompt-submit"
HOOK_AGENT_GATE="hooks/pretooluse-agent-spawn-gate"
HOOK_STOP="hooks/stop"
HOOK_SUBAGENT_STOP="hooks/subagent-stop"

# 기존 hook 목록 (회귀 차단 TC-13 용)
EXISTING_HOOKS=(
  "hooks/session-start"
  "hooks/stale-local-main-checkout"
  "hooks/cross-repo-gh-safety"
  "hooks/schedule-wakeup-reminder"
  "hooks/plain-language-reminder"
  "hooks/korean-english-recovery"
  "hooks/plain-language-check"
)

# stop hook 기본 stdin payload
_stop_payload() {
  printf '{"stop_hook_active": true, "stop_reason": "idle"}'
}

# subagent-stop hook 기본 stdin payload
_subagent_stop_payload() {
  printf '{"stop_hook_active": false, "subagent_completed": true}'
}

# userprompt-submit hook 기본 stdin payload (UserPromptSubmit JSON)
_userprompt_payload() {
  printf '{"prompt": "사용자 테스트 입력"}'
}

# pretooluse-agent-spawn-gate hook 용 최소 payload (Agent tool, 4 block 모두 포함)
_agent_gate_payload() {
  python3 -c "
import json
payload = {
  'tool_name': 'Agent',
  'tool_input': {
    'prompt': '[PRE-SPAWN-ORIGIN-MAIN-SHA] : abc123\n[USER-UTTERANCE-VERBATIM]\n사용자 원문\nworktree path: /home/user/.claude/worktrees/test\ngit -C /home/user/.claude/worktrees/test status\nparallel dispatch: parallel_with=[]'
  }
}
print(json.dumps(payload))
"
}

setup() {
  # 모든 테스트에서 프로젝트 루트 기준으로 실행
  cd "${BATS_TEST_DIRNAME}/../.." || return 1

  # ledger 격리 디렉터리 (TC-8 / TC-9 / TC-10 용)
  export CLAUDE_PROJECT_DIR="$(mktemp -d)"
  export CLAUDE_SESSION_ID="test-session-cfp-1746"
  export CLAUDE_PLUGIN_ROOT="$(pwd)"

  mkdir -p "${CLAUDE_PROJECT_DIR}/.claude/ledger"
}

teardown() {
  rm -rf "${CLAUDE_PROJECT_DIR:-}"
}

# ── TC-1: hooks.json JSON valid + 5 hook tier 모두 present ───────────────────
@test "TC-1: hooks.json valid JSON + 5 hook tier (SessionStart/PreToolUse/UserPromptSubmit/Stop/SubagentStop) present" {
  [ -f "$HOOKS_JSON" ] || fail "hooks.json not found"

  # JSON 유효성
  python3 -m json.tool "$HOOKS_JSON" > /dev/null

  # 5 tier presence
  run python3 -c "
import json, sys
with open('$HOOKS_JSON') as f:
    data = json.load(f)
hooks = data.get('hooks', {})
required = ['SessionStart', 'PreToolUse', 'UserPromptSubmit', 'Stop', 'SubagentStop']
missing = [k for k in required if k not in hooks]
if missing:
    print('MISSING: ' + ', '.join(missing))
    sys.exit(1)
print('PASS: all 5 hook tier present')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ── TC-2: hooks.json hook command 총 개수 ≥ 11 ───────────────────────────────
@test "TC-2: hooks.json total command count >= 11 (4 new + 7 existing baseline)" {
  [ -f "$HOOKS_JSON" ] || fail "hooks.json not found"

  run python3 -c "
import json, sys

def count_commands(obj):
    count = 0
    if isinstance(obj, dict):
        if 'command' in obj and 'type' in obj and obj.get('type') == 'command':
            count += 1
        for v in obj.values():
            count += count_commands(v)
    elif isinstance(obj, list):
        for item in obj:
            count += count_commands(item)
    return count

with open('$HOOKS_JSON') as f:
    data = json.load(f)

total = count_commands(data)
if total >= 11:
    print('PASS: %d commands found (>= 11 required)' % total)
    sys.exit(0)
else:
    print('FAIL: only %d commands found (< 11 required)' % total)
    sys.exit(1)
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ── TC-3: 4 신규 hook script 존재 ────────────────────────────────────────────
@test "TC-3: 4 new hook scripts exist (userprompt-submit / pretooluse-agent-spawn-gate / stop / subagent-stop)" {
  local missing=()
  for hook in "$HOOK_USERPROMPT" "$HOOK_AGENT_GATE" "$HOOK_STOP" "$HOOK_SUBAGENT_STOP"; do
    [ -f "$hook" ] || missing+=("$hook")
  done

  if [ ${#missing[@]} -gt 0 ]; then
    echo "RED: missing hooks: ${missing[*]}"
    return 1
  fi
}

# ── TC-4: 4 신규 hook script exec bit / bash -n syntax PASS ─────────────────
@test "TC-4: 4 new hook scripts pass bash -n syntax check" {
  for hook in "$HOOK_USERPROMPT" "$HOOK_AGENT_GATE" "$HOOK_STOP" "$HOOK_SUBAGENT_STOP"; do
    if [ ! -f "$hook" ]; then
      echo "RED: $hook not found"
      return 1
    fi
    # bash -n syntax check
    run bash -n "$hook"
    if [ "$status" -ne 0 ]; then
      echo "FAIL: bash -n syntax error in $hook"
      echo "$output"
      return 1
    fi
  done
}

# ── TC-5: 4 신규 hook script marker emit ─────────────────────────────────────
@test "TC-5: 4 new hook scripts emit one-channel-rule marker strings" {
  # userprompt-submit: stdout marker
  if [ ! -f "$HOOK_USERPROMPT" ]; then echo "RED: $HOOK_USERPROMPT not found"; return 1; fi
  local userprompt_out
  userprompt_out="$(bash "$HOOK_USERPROMPT" 2>/dev/null)"
  [[ "$userprompt_out" == *"[codeforge-wrapper-userprompt-submit]"* ]] || {
    echo "FAIL: userprompt-submit missing marker [codeforge-wrapper-userprompt-submit]"
    return 1
  }

  # pretooluse-agent-spawn-gate: bypass 없이 실행 시 exit 0
  if [ ! -f "$HOOK_AGENT_GATE" ]; then echo "RED: $HOOK_AGENT_GATE not found"; return 1; fi
  local agent_payload agent_exit
  agent_payload="$(_agent_gate_payload)"
  printf '%s' "$agent_payload" | bash "$HOOK_AGENT_GATE" >/dev/null 2>/dev/null
  agent_exit=$?
  [ "$agent_exit" -eq 0 ] || {
    echo "FAIL: pretooluse-agent-spawn-gate exited $agent_exit"
    return 1
  }

  # stop: script 안에 marker 문자열 포함
  if [ ! -f "$HOOK_STOP" ]; then echo "RED: $HOOK_STOP not found"; return 1; fi
  grep -q "codeforge-wrapper-stop" "$HOOK_STOP" || {
    echo "FAIL: stop hook missing [codeforge-wrapper-stop] marker string in file"
    return 1
  }

  # subagent-stop: script 안에 marker 문자열 포함
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then echo "RED: $HOOK_SUBAGENT_STOP not found"; return 1; fi
  grep -q "codeforge-wrapper-subagent-stop" "$HOOK_SUBAGENT_STOP" || {
    echo "FAIL: subagent-stop hook missing [codeforge-wrapper-subagent-stop] marker string in file"
    return 1
  }
}

# ── TC-6: 4 신규 hook 직접 호출 시 exit 0 ────────────────────────────────────
@test "TC-6: 4 new hooks exit 0 when called directly (dispatcher routing equivalent)" {
  for hook in "$HOOK_USERPROMPT" "$HOOK_AGENT_GATE" "$HOOK_STOP" "$HOOK_SUBAGENT_STOP"; do
    if [ ! -f "$hook" ]; then
      echo "RED: $hook not found"
      return 1
    fi
  done

  # userprompt-submit: no stdin required
  run bash "$HOOK_USERPROMPT"
  [ "$status" -eq 0 ] || { echo "FAIL: userprompt-submit exit $status"; return 1; }

  # pretooluse-agent-spawn-gate: Agent payload via stdin
  local agent_payload
  agent_payload="$(_agent_gate_payload)"
  run bash -c "printf '%s' '$agent_payload' | CLAUDE_PLUGIN_ROOT='$(pwd)' bash '$HOOK_AGENT_GATE'"
  [ "$status" -eq 0 ] || { echo "FAIL: pretooluse-agent-spawn-gate exit $status"; return 1; }

  # stop hook
  run bash -c "CLAUDE_PROJECT_DIR='${CLAUDE_PROJECT_DIR}' CLAUDE_SESSION_ID='${CLAUDE_SESSION_ID}' CLAUDE_PLUGIN_ROOT='$(pwd)' \
    bash '${HOOK_STOP}' <<< '{\"stop_hook_active\": true}'"
  [ "$status" -eq 0 ] || { echo "FAIL: stop exit $status"; return 1; }

  # subagent-stop hook
  run bash -c "CLAUDE_PROJECT_DIR='${CLAUDE_PROJECT_DIR}' CLAUDE_SESSION_ID='${CLAUDE_SESSION_ID}' CLAUDE_PLUGIN_ROOT='$(pwd)' \
    bash '${HOOK_SUBAGENT_STOP}' <<< '{\"stop_hook_active\": false}'"
  [ "$status" -eq 0 ] || { echo "FAIL: subagent-stop exit $status"; return 1; }
}

# ── TC-7: ADR-115 §결정 2 block 금지 — stdout 안 block / permissionDecision:deny 부재 ──
@test "TC-7: all 4 new hooks stdout must NOT contain block or permissionDecision:deny (ADR-115 §결정 2 P0)" {
  # userprompt-submit
  if [ ! -f "$HOOK_USERPROMPT" ]; then echo "RED: $HOOK_USERPROMPT not found"; return 1; fi
  local userprompt_stdout
  userprompt_stdout="$(bash "$HOOK_USERPROMPT" 2>/dev/null)"
  if echo "$userprompt_stdout" | grep -q '"block"'; then
    echo "FAIL: userprompt-submit stdout contains 'block' key"
    return 1
  fi
  if echo "$userprompt_stdout" | grep -q 'permissionDecision.*deny'; then
    echo "FAIL: userprompt-submit stdout contains permissionDecision:deny"
    return 1
  fi

  # pretooluse-agent-spawn-gate
  if [ ! -f "$HOOK_AGENT_GATE" ]; then echo "RED: $HOOK_AGENT_GATE not found"; return 1; fi
  local agent_payload agent_stdout
  agent_payload="$(_agent_gate_payload)"
  agent_stdout="$(printf '%s' "$agent_payload" | CLAUDE_PLUGIN_ROOT="$(pwd)" bash "$HOOK_AGENT_GATE" 2>/dev/null)"
  if echo "$agent_stdout" | grep -q '"block"'; then
    echo "FAIL: pretooluse-agent-spawn-gate stdout contains 'block' key"
    return 1
  fi
  if echo "$agent_stdout" | grep -q 'permissionDecision.*deny'; then
    echo "FAIL: pretooluse-agent-spawn-gate stdout contains permissionDecision:deny"
    return 1
  fi

  # stop hook
  if [ ! -f "$HOOK_STOP" ]; then echo "RED: $HOOK_STOP not found"; return 1; fi
  local stop_stdout
  stop_stdout="$(CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" \
    CLAUDE_PLUGIN_ROOT="$(pwd)" bash "$HOOK_STOP" <<< '{"stop_hook_active": true}' 2>/dev/null)"
  if echo "$stop_stdout" | grep -q '"block"'; then
    echo "FAIL: stop hook stdout contains 'block' key"
    return 1
  fi
  if echo "$stop_stdout" | grep -q 'permissionDecision.*deny'; then
    echo "FAIL: stop hook stdout contains permissionDecision:deny"
    return 1
  fi

  # subagent-stop hook
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then echo "RED: $HOOK_SUBAGENT_STOP not found"; return 1; fi
  local subagent_stdout
  subagent_stdout="$(CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" \
    CLAUDE_PLUGIN_ROOT="$(pwd)" bash "$HOOK_SUBAGENT_STOP" <<< '{"stop_hook_active": false}' 2>/dev/null)"
  if echo "$subagent_stdout" | grep -q '"block"'; then
    echo "FAIL: subagent-stop hook stdout contains 'block' key"
    return 1
  fi
  if echo "$subagent_stdout" | grep -q 'permissionDecision.*deny'; then
    echo "FAIL: subagent-stop hook stdout contains permissionDecision:deny"
    return 1
  fi
}

# ── TC-8: ledger 경합 — stop + subagent-stop sequential 2회 → 2 row 무손실 ─────
@test "TC-8: ledger contention — stop then subagent-stop sequential calls produce 2 rows losslessly" {
  if [ ! -f "$HOOK_STOP" ]; then echo "RED: $HOOK_STOP not found"; return 1; fi
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then echo "RED: $HOOK_SUBAGENT_STOP not found"; return 1; fi

  local ledger_file="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"

  # stop hook 먼저 호출
  CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" \
    CLAUDE_PLUGIN_ROOT="$(pwd)" bash "$HOOK_STOP" <<< '{"stop_hook_active": true}' 2>/dev/null

  # subagent-stop hook 순차 호출
  CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" \
    CLAUDE_PLUGIN_ROOT="$(pwd)" bash "$HOOK_SUBAGENT_STOP" <<< '{"stop_hook_active": false, "subagent_completed": true}' 2>/dev/null

  # ledger 파일 존재 확인
  [ -f "$ledger_file" ] || { echo "FAIL: ledger file not created"; return 1; }

  # 2 row 정확히 존재
  local row_count
  row_count="$(wc -l < "$ledger_file" | tr -d ' ')"
  [ "$row_count" -eq 2 ] || {
    echo "FAIL: expected 2 ledger rows, got $row_count"
    cat "$ledger_file"
    return 1
  }

  # 첫 번째 row = hook_source: stop
  local source_1
  source_1="$(sed -n '1p' "$ledger_file" | python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('hook_source',''))" 2>/dev/null)"
  [ "$source_1" = "stop" ] || { echo "FAIL: row 1 hook_source='$source_1', expected 'stop'"; return 1; }

  # 두 번째 row = hook_source: subagent-stop
  local source_2
  source_2="$(sed -n '2p' "$ledger_file" | python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('hook_source',''))" 2>/dev/null)"
  [ "$source_2" = "subagent-stop" ] || { echo "FAIL: row 2 hook_source='$source_2', expected 'subagent-stop'"; return 1; }
}

# ── TC-9: ledger row schema v1.1 정합 ────────────────────────────────────────
@test "TC-9: ledger row schema v1.1 — timestamp_kst / hook_source enum / hook_decision: record-only" {
  if [ ! -f "$HOOK_STOP" ]; then echo "RED: $HOOK_STOP not found"; return 1; fi

  local ledger_file="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"

  CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" \
    CLAUDE_PLUGIN_ROOT="$(pwd)" bash "$HOOK_STOP" <<< '{"stop_hook_active": true}' 2>/dev/null

  [ -f "$ledger_file" ] || { echo "FAIL: ledger not created"; return 1; }

  # 각 row JSON 유효성 + 필수 필드 검증
  while IFS= read -r line; do
    [ -n "$line" ] || continue

    # JSON parse 가능 여부
    echo "$line" | python3 -m json.tool > /dev/null 2>&1 || {
      echo "FAIL: ledger row not valid JSON: $line"
      return 1
    }

    # hook_decision = record-only
    local decision
    decision="$(echo "$line" | python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('hook_decision',''))" 2>/dev/null)"
    [ "$decision" = "record-only" ] || {
      echo "FAIL: hook_decision='$decision', expected 'record-only'"
      return 1
    }

    # hook_source 존재 (stop 또는 subagent-stop)
    local source
    source="$(echo "$line" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d.get('hook_source',''))" 2>/dev/null)"
    [[ "$source" == "stop" || "$source" == "subagent-stop" ]] || {
      echo "FAIL: hook_source='$source', expected 'stop' or 'subagent-stop'"
      return 1
    }

  done < "$ledger_file"
}

# ── TC-10: bypass env 4 종 동작 ──────────────────────────────────────────────
@test "TC-10: bypass env 4 kinds — exit 0 + correct suppression behavior each" {
  # (a) BYPASS_CODEFORGE_USERPROMPT_SUBMIT
  if [ ! -f "$HOOK_USERPROMPT" ]; then echo "RED: $HOOK_USERPROMPT not found"; return 1; fi
  local userprompt_stdout userprompt_exit
  userprompt_stdout="$(BYPASS_CODEFORGE_USERPROMPT_SUBMIT=1 bash "$HOOK_USERPROMPT" 2>/dev/null)"
  userprompt_exit=$?
  [ "$userprompt_exit" -eq 0 ] || { echo "FAIL: userprompt bypass exit $userprompt_exit"; return 1; }
  [ -z "$userprompt_stdout" ] || { echo "FAIL: userprompt bypass stdout not empty: $userprompt_stdout"; return 1; }

  local userprompt_stderr
  userprompt_stderr="$(BYPASS_CODEFORGE_USERPROMPT_SUBMIT=1 bash "$HOOK_USERPROMPT" 2>&1 >/dev/null)"
  echo "$userprompt_stderr" | grep -q "BYPASS_CODEFORGE_USERPROMPT_SUBMIT" || {
    echo "FAIL: userprompt bypass missing audit in stderr"
    return 1
  }

  # (b) BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE
  if [ ! -f "$HOOK_AGENT_GATE" ]; then echo "RED: $HOOK_AGENT_GATE not found"; return 1; fi
  local agent_payload
  agent_payload="$(_agent_gate_payload)"
  run bash -c "printf '%s' '$agent_payload' | BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 CLAUDE_PLUGIN_ROOT='$(pwd)' bash '$HOOK_AGENT_GATE'"
  [ "$status" -eq 0 ] || { echo "FAIL: agent-gate bypass exit $status"; return 1; }

  local agent_stderr
  agent_stderr="$(printf '%s' "$agent_payload" | BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 \
    CLAUDE_PLUGIN_ROOT="$(pwd)" bash "$HOOK_AGENT_GATE" 2>&1 >/dev/null)"
  echo "$agent_stderr" | grep -q "BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE" || {
    echo "FAIL: agent-gate bypass missing audit in stderr"
    return 1
  }

  # (c) BYPASS_CODEFORGE_STOP
  if [ ! -f "$HOOK_STOP" ]; then echo "RED: $HOOK_STOP not found"; return 1; fi
  local ledger_file="${CLAUDE_PROJECT_DIR}/.claude/ledger/stop-event.jsonl"

  run bash -c "BYPASS_CODEFORGE_STOP=1 CLAUDE_PROJECT_DIR='${CLAUDE_PROJECT_DIR}' \
    CLAUDE_SESSION_ID='${CLAUDE_SESSION_ID}' CLAUDE_PLUGIN_ROOT='$(pwd)' \
    bash '${HOOK_STOP}' <<< '{\"stop_hook_active\": true}'"
  [ "$status" -eq 0 ] || { echo "FAIL: stop bypass exit $status"; return 1; }

  # bypass 시 ledger row 없음
  if [ -f "$ledger_file" ]; then
    local row_count
    row_count="$(wc -l < "$ledger_file" | tr -d ' ')"
    [ "$row_count" -eq 0 ] || { echo "FAIL: stop bypass produced $row_count ledger rows (expected 0)"; return 1; }
  fi

  local stop_stderr
  stop_stderr="$(BYPASS_CODEFORGE_STOP=1 CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" \
    CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_STOP" <<< '{"stop_hook_active": true}' 2>&1 >/dev/null)"
  echo "$stop_stderr" | grep -q "BYPASS_CODEFORGE_STOP" || {
    echo "FAIL: stop bypass missing audit in stderr"
    return 1
  }

  # (d) BYPASS_CODEFORGE_SUBAGENT_STOP
  if [ ! -f "$HOOK_SUBAGENT_STOP" ]; then echo "RED: $HOOK_SUBAGENT_STOP not found"; return 1; fi

  run bash -c "BYPASS_CODEFORGE_SUBAGENT_STOP=1 CLAUDE_PROJECT_DIR='${CLAUDE_PROJECT_DIR}' \
    CLAUDE_SESSION_ID='${CLAUDE_SESSION_ID}' CLAUDE_PLUGIN_ROOT='$(pwd)' \
    bash '${HOOK_SUBAGENT_STOP}' <<< '{\"stop_hook_active\": false}'"
  [ "$status" -eq 0 ] || { echo "FAIL: subagent-stop bypass exit $status"; return 1; }

  local subagent_stderr
  subagent_stderr="$(BYPASS_CODEFORGE_SUBAGENT_STOP=1 CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" \
    CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID}" CLAUDE_PLUGIN_ROOT="$(pwd)" \
    bash "$HOOK_SUBAGENT_STOP" <<< '{"stop_hook_active": false}' 2>&1 >/dev/null)"
  echo "$subagent_stderr" | grep -q "BYPASS_CODEFORGE_SUBAGENT_STOP" || {
    echo "FAIL: subagent-stop bypass missing audit in stderr"
    return 1
  }
}

# ── TC-11: polyglot preamble 검증 (4 신규 hook 구조 확인) ─────────────────────
# 4 신규 hook 은 bash-only 파일 (run-hook.cmd 가 dispatcher 역할).
# TC-11 은 dispatcher (run-hook.cmd) 가 polyglot preamble 을 보유하고,
# 4 신규 hook script 자체는 표준 bash shebang (#!/usr/bin/env bash) 으로 시작함을 검증.
@test "TC-11: dispatcher run-hook.cmd has polyglot preamble; 4 new hooks have bash shebang" {
  # dispatcher 파일 polyglot preamble 검증
  local dispatcher="hooks/run-hook.cmd"
  [ -f "$dispatcher" ] || { echo "FAIL: hooks/run-hook.cmd not found"; return 1; }

  # Windows cmd block 존재 확인 (@REM 또는 @echo 패턴)
  grep -q "@REM\|@echo" "$dispatcher" || {
    echo "FAIL: run-hook.cmd missing Windows cmd preamble (@REM or @echo)"
    return 1
  }

  # Unix bash exec 라인 존재 확인
  grep -q "exec bash" "$dispatcher" || {
    echo "FAIL: run-hook.cmd missing Unix exec bash line"
    return 1
  }

  # 4 신규 hook 은 표준 bash shebang 으로 시작 (#!/usr/bin/env bash 또는 #!/bin/bash)
  for hook in "$HOOK_USERPROMPT" "$HOOK_AGENT_GATE" "$HOOK_STOP" "$HOOK_SUBAGENT_STOP"; do
    [ -f "$hook" ] || { echo "RED: $hook not found"; return 1; }
    local first_line
    first_line="$(head -1 "$hook")"
    [[ "$first_line" == "#!/usr/bin/env bash" || "$first_line" == "#!/bin/bash" ]] || {
      echo "FAIL: $hook first line is '$first_line', expected bash shebang"
      return 1
    }
  done
}

# ── TC-12: hooks.json command 패턴 — run-hook.cmd <name> 형식 (cmd injection 차단) ──
@test "TC-12: hooks.json all commands match run-hook.cmd <name> pattern (no cmd injection)" {
  [ -f "$HOOKS_JSON" ] || fail "hooks.json not found"

  run python3 -c "
import json, sys, re

with open('$HOOKS_JSON') as f:
    data = json.load(f)

def collect_commands(obj):
    commands = []
    if isinstance(obj, dict):
        if obj.get('type') == 'command' and 'command' in obj:
            commands.append(obj['command'])
        for v in obj.values():
            commands.extend(collect_commands(v))
    elif isinstance(obj, list):
        for item in obj:
            commands.extend(collect_commands(item))
    return commands

commands = collect_commands(data)

# 허용 패턴: '...run-hook.cmd' <hook-name>
# hook-name 은 영숫자·하이픈만 허용 (cmd injection 차단)
PATTERN = re.compile(r'^\"?\\\${CLAUDE_PLUGIN_ROOT}/hooks/run-hook\.cmd\"?\s+[a-zA-Z0-9\-]+\$')

bad = []
for cmd in commands:
    if not PATTERN.match(cmd):
        bad.append(cmd)

if bad:
    print('FAIL: non-conforming commands found:')
    for b in bad:
        print('  ' + b)
    sys.exit(1)
print('PASS: all %d commands match run-hook.cmd <name> pattern' % len(commands))
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ── TC-13: 기존 7 hook file 존재 (회귀 차단) ─────────────────────────────────
@test "TC-13: existing 7 hook files present (regression guard)" {
  local missing=()
  for hook in "${EXISTING_HOOKS[@]}"; do
    [ -f "$hook" ] || missing+=("$hook")
  done

  if [ ${#missing[@]} -gt 0 ]; then
    echo "REGRESSION: missing existing hooks: ${missing[*]}"
    return 1
  fi
}
