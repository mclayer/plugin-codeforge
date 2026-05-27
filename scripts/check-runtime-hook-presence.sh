#!/usr/bin/env bash
# scripts/check-runtime-hook-presence.sh
# CFP-1745 / ADR-115 — runtime hook presence evidence gate (warning tier)
# ADR-060 §결정 5: warning tier — exit 0 always (continue-on-error: true 정합)
# ADR-061 bash convention: jq / python3 -c 5줄 이내 parse, heredoc 미사용
#
# Usage: bash scripts/check-runtime-hook-presence.sh [check_type]
#   check_type: userprompt | pretooluse-agent | stop | subagentstop | all (default)
#
# bypass: BYPASS_RUNTIME_HOOK_PRESENCE=1 env → unconditional skip

set -euo pipefail

HOOKS_JSON="${HOOKS_JSON:-hooks/hooks.json}"
CHECK_TYPE="${1:-all}"
EXIT_CODE=0

# bypass gate
if [ "${BYPASS_RUNTIME_HOOK_PRESENCE:-0}" = "1" ]; then
  echo "[runtime-hook-presence] BYPASS_RUNTIME_HOOK_PRESENCE=1 — skipping"
  exit 0
fi

# hotfix-bypass label PR skip — 호출자(workflow)가 PR label 검사 후 스킵, 스크립트는 단순 presence check
if [ ! -f "$HOOKS_JSON" ]; then
  echo "[runtime-hook-presence] WARNING: $HOOKS_JSON not found — hook presence unverifiable" >&2
  exit 0
fi

check_userprompt() {
  local count
  count=$(python3 -c "import json; d=json.load(open('$HOOKS_JSON')); print(len(d.get('hooks',{}).get('UserPromptSubmit',[])))" 2>/dev/null || echo "0")
  if [ "$count" -eq 0 ]; then
    echo "[runtime-hook-presence] WARNING: hooks.UserPromptSubmit entry 없음 (ADR-115 §결정 2)" >&2
    EXIT_CODE=1
  else
    echo "[runtime-hook-presence] OK: hooks.UserPromptSubmit presence confirmed ($count group)"
  fi
}

check_pretooluse_agent() {
  local found
  found=$(python3 -c "
import json
d=json.load(open('$HOOKS_JSON'))
items=d.get('hooks',{}).get('PreToolUse',[])
print(any(i.get('matcher','')=='Agent' for i in items))
" 2>/dev/null || echo "False")
  if [ "$found" != "True" ]; then
    echo "[runtime-hook-presence] WARNING: hooks.PreToolUse[matcher:Agent] entry 없음 (ADR-115 §결정 3)" >&2
    EXIT_CODE=1
  else
    echo "[runtime-hook-presence] OK: hooks.PreToolUse[matcher:Agent] presence confirmed"
  fi
}

check_stop() {
  local count
  count=$(python3 -c "import json; d=json.load(open('$HOOKS_JSON')); print(len(d.get('hooks',{}).get('Stop',[])))" 2>/dev/null || echo "0")
  if [ "$count" -eq 0 ]; then
    echo "[runtime-hook-presence] WARNING: hooks.Stop entry 없음 (ADR-115 §결정 5 / platform bug #10412 참조)" >&2
    EXIT_CODE=1
  else
    echo "[runtime-hook-presence] OK: hooks.Stop presence confirmed ($count group)"
  fi
}

check_subagentstop() {
  local count
  count=$(python3 -c "import json; d=json.load(open('$HOOKS_JSON')); print(len(d.get('hooks',{}).get('SubagentStop',[])))" 2>/dev/null || echo "0")
  if [ "$count" -eq 0 ]; then
    echo "[runtime-hook-presence] WARNING: hooks.SubagentStop entry 없음 (ADR-115 §결정 5 / platform bug #10412 참조)" >&2
    EXIT_CODE=1
  else
    echo "[runtime-hook-presence] OK: hooks.SubagentStop presence confirmed ($count group)"
  fi
}

case "$CHECK_TYPE" in
  userprompt)      check_userprompt ;;
  pretooluse-agent) check_pretooluse_agent ;;
  stop)            check_stop ;;
  subagentstop)    check_subagentstop ;;
  all)
    check_userprompt
    check_pretooluse_agent
    check_stop
    check_subagentstop
    ;;
  *)
    echo "[runtime-hook-presence] ERROR: unknown check_type '$CHECK_TYPE'" >&2
    exit 0
    ;;
esac

if [ "$EXIT_CODE" -ne 0 ]; then
  echo "[runtime-hook-presence] SUMMARY: hook presence check FAILED (warning tier — exit 0)" >&2
  echo "[runtime-hook-presence] bypass: add hotfix-bypass:runtime-hook-presence label to PR" >&2
fi

# warning tier: always exit 0 (ADR-060 §결정 5, continue-on-error: true 정합)
exit 0
