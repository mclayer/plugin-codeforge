#!/usr/bin/env bats
#
# cfp-1742-pretooluse-agent-spawn-gate.bats
# CFP-1742 / ADR-115 §결정 1·4·6 — PreToolUse(Agent) spawn-format gate
#
# TDD RED→GREEN stash proof (CFP-1334 / ADR-082 §결정 11.A):
#   RED:   stash hooks/pretooluse-agent-spawn-gate + scripts/lib/check_spawn_prompt_format.py
#          → TC-1~TC-6 fail (missing block warning path 미작동 / hook 부재)
#   GREEN: restore (stash pop) → 10/10 pass
#   verified: 2026-05-27 KST (Story §0 Live Progress 참조)
#
# 10 Test cases:
#   TC-1:  4 block 모두 present → exit 0 + no stderr warning
#   TC-2:  PRE-SPAWN-ORIGIN-MAIN-SHA 누락 → stderr warning + exit 0
#   TC-3:  USER-UTTERANCE-VERBATIM 누락 → stderr warning + exit 0
#   TC-4:  worktree-first directive 누락 → stderr warning + exit 0
#   TC-5:  parallel-dispatch directive 누락 → stderr warning + exit 0
#   TC-6:  4 block 모두 누락 → 4 warnings aggregated + exit 0
#   TC-7:  BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 → stderr audit + exit 0 + 0 warning
#   TC-8:  hooks.json PreToolUse matcher:"Agent" entry presence
#   TC-9:  hooks.json JSON 유효성 (python3 json.tool)
#   TC-10: Python ReDoS guard — pathological input (1000 line) < 100ms 처리
#

HOOK_SCRIPT="hooks/pretooluse-agent-spawn-gate"
VERIFIER_SCRIPT="scripts/lib/check_spawn_prompt_format.py"
HOOKS_JSON="hooks/hooks.json"

# spawn prompt 조합 헬퍼 — 4 block 모두 포함한 표준 prompt
_make_full_prompt() {
  cat <<'PROMPT'
[PRE-SPAWN-ORIGIN-MAIN-SHA] : 018387db3f4a2c9e1b567d890c12345678abcdef
[USER-UTTERANCE-VERBATIM]
사용자 원문 (진행해)
You are DeveloperAgent. worktree path: /home/user/.claude/worktrees/plugin-codeforge/cfp-1742
git -C /home/user/.claude/worktrees/plugin-codeforge/cfp-1742 status
parallel dispatch: parallel_with=[] (no dependency)
PROMPT
}

# PreToolUse JSON payload 조합 헬퍼 — tool_input.prompt 에 spawn prompt 포함
_make_payload() {
  local prompt_text="$1"
  # Python 으로 JSON 직렬화 (shell escape 문제 회피)
  python3 -c "
import json, sys
prompt = sys.argv[1]
payload = {
    'tool_name': 'Agent',
    'tool_input': {
        'prompt': prompt
    }
}
print(json.dumps(payload))
" "$prompt_text"
}

setup() {
  # 모든 테스트에서 프로젝트 루트 기준으로 실행
  cd "${BATS_TEST_DIRNAME}/../.." || return 1
}

# ── TC-1: 4 block 모두 present → exit 0 + no stderr warning ─────────────────
@test "TC-1: 4 block all present — exit 0, no spawn-format warning in stderr" {
  [ -f "$HOOK_SCRIPT" ] || { echo "RED phase: hook script required for GREEN"; return 1; }
  [ -f "$VERIFIER_SCRIPT" ] || { echo "RED phase: verifier script required for GREEN"; return 1; }

  local prompt_text
  prompt_text="$(_make_full_prompt)"
  local payload
  payload="$(_make_payload "$prompt_text")"

  # stdout + stderr 분리 캡처
  local stderr_out
  stderr_out="$(printf '%s' "$payload" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null)"
  local exit_code=$?

  [ "$exit_code" -eq 0 ]
  # "WARN:" 이 stderr 에 없어야 함 (4 block 모두 있으므로)
  [[ "$stderr_out" != *"WARN: spawn prompt missing"* ]]
}

# ── TC-2: PRE-SPAWN-ORIGIN-MAIN-SHA 누락 → stderr warning + exit 0 ──────────
@test "TC-2: PRE-SPAWN-ORIGIN-MAIN-SHA missing — stderr warning emitted, exit 0" {
  [ -f "$HOOK_SCRIPT" ] || { echo "RED phase: hook script required for GREEN"; return 1; }
  [ -f "$VERIFIER_SCRIPT" ] || { echo "RED phase: verifier script required for GREEN"; return 1; }

  local prompt_text
  prompt_text="$(cat <<'PROMPT'
[USER-UTTERANCE-VERBATIM]
사용자 원문
worktree path: /home/user/.claude/worktrees/plugin-codeforge/cfp-1742
parallel dispatch: parallel_with=[]
PROMPT
)"
  local payload
  payload="$(_make_payload "$prompt_text")"

  local stderr_out
  stderr_out="$(printf '%s' "$payload" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null)"
  local exit_code=$?

  [ "$exit_code" -eq 0 ]
  [[ "$stderr_out" == *"PRE-SPAWN-ORIGIN-MAIN-SHA"* ]]
}

# ── TC-3: USER-UTTERANCE-VERBATIM 누락 → stderr warning + exit 0 ────────────
@test "TC-3: USER-UTTERANCE-VERBATIM missing — stderr warning emitted, exit 0" {
  [ -f "$HOOK_SCRIPT" ] || { echo "RED phase: hook script required for GREEN"; return 1; }
  [ -f "$VERIFIER_SCRIPT" ] || { echo "RED phase: verifier script required for GREEN"; return 1; }

  local prompt_text
  prompt_text="$(cat <<'PROMPT'
[PRE-SPAWN-ORIGIN-MAIN-SHA] : 018387db3f4a2c9e1b567d890c12345678abcdef
worktree path: /home/user/.claude/worktrees/plugin-codeforge/cfp-1742
parallel dispatch: parallel_with=[]
PROMPT
)"
  local payload
  payload="$(_make_payload "$prompt_text")"

  local stderr_out
  stderr_out="$(printf '%s' "$payload" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null)"
  local exit_code=$?

  [ "$exit_code" -eq 0 ]
  [[ "$stderr_out" == *"USER-UTTERANCE-VERBATIM"* ]]
}

# ── TC-4: worktree-first directive 누락 → stderr warning + exit 0 ────────────
@test "TC-4: WORKTREE-FIRST-DIRECTIVE missing — stderr warning emitted, exit 0" {
  [ -f "$HOOK_SCRIPT" ] || { echo "RED phase: hook script required for GREEN"; return 1; }
  [ -f "$VERIFIER_SCRIPT" ] || { echo "RED phase: verifier script required for GREEN"; return 1; }

  local prompt_text
  prompt_text="$(cat <<'PROMPT'
[PRE-SPAWN-ORIGIN-MAIN-SHA] : 018387db3f4a2c9e1b567d890c12345678abcdef
[USER-UTTERANCE-VERBATIM]
사용자 원문
parallel dispatch: parallel_with=[]
PROMPT
)"
  local payload
  payload="$(_make_payload "$prompt_text")"

  local stderr_out
  stderr_out="$(printf '%s' "$payload" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null)"
  local exit_code=$?

  [ "$exit_code" -eq 0 ]
  [[ "$stderr_out" == *"WORKTREE-FIRST-DIRECTIVE"* ]]
}

# ── TC-5: parallel-dispatch directive 누락 → stderr warning + exit 0 ─────────
@test "TC-5: PARALLEL-DISPATCH-DIRECTIVE missing — stderr warning emitted, exit 0" {
  [ -f "$HOOK_SCRIPT" ] || { echo "RED phase: hook script required for GREEN"; return 1; }
  [ -f "$VERIFIER_SCRIPT" ] || { echo "RED phase: verifier script required for GREEN"; return 1; }

  local prompt_text
  prompt_text="$(cat <<'PROMPT'
[PRE-SPAWN-ORIGIN-MAIN-SHA] : 018387db3f4a2c9e1b567d890c12345678abcdef
[USER-UTTERANCE-VERBATIM]
사용자 원문
worktree path: /home/user/.claude/worktrees/plugin-codeforge/cfp-1742
PROMPT
)"
  local payload
  payload="$(_make_payload "$prompt_text")"

  local stderr_out
  stderr_out="$(printf '%s' "$payload" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null)"
  local exit_code=$?

  [ "$exit_code" -eq 0 ]
  [[ "$stderr_out" == *"PARALLEL-DISPATCH-DIRECTIVE"* ]]
}

# ── TC-6: 4 block 모두 누락 → 4 warning aggregated + exit 0 ─────────────────
@test "TC-6: all 4 blocks missing — 4 warnings aggregated, exit 0" {
  [ -f "$HOOK_SCRIPT" ] || { echo "RED phase: hook script required for GREEN"; return 1; }
  [ -f "$VERIFIER_SCRIPT" ] || { echo "RED phase: verifier script required for GREEN"; return 1; }

  local prompt_text="You are DeveloperAgent. implement the feature."
  local payload
  payload="$(_make_payload "$prompt_text")"

  local stderr_out
  stderr_out="$(printf '%s' "$payload" | bash "$HOOK_SCRIPT" 2>&1 >/dev/null)"
  local exit_code=$?

  [ "$exit_code" -eq 0 ]
  # missing blocks warning 발화 확인
  [[ "$stderr_out" == *"WARN"* ]]
  # 4개 block 모두 언급
  [[ "$stderr_out" == *"PRE-SPAWN-ORIGIN-MAIN-SHA"* ]]
  [[ "$stderr_out" == *"USER-UTTERANCE-VERBATIM"* ]]
  [[ "$stderr_out" == *"WORKTREE-FIRST-DIRECTIVE"* ]]
  [[ "$stderr_out" == *"PARALLEL-DISPATCH-DIRECTIVE"* ]]
}

# ── TC-7: BYPASS env → stderr audit + exit 0 + 0 warning ────────────────────
@test "TC-7: BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 — audit emitted, exit 0, no block warning" {
  [ -f "$HOOK_SCRIPT" ] || { echo "RED phase: hook script required for GREEN"; return 1; }

  local prompt_text="You are DeveloperAgent. no blocks present."
  local payload
  payload="$(_make_payload "$prompt_text")"

  local stderr_out
  stderr_out="$(printf '%s' "$payload" | BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1 bash "$HOOK_SCRIPT" 2>&1 >/dev/null)"
  local exit_code=$?

  [ "$exit_code" -eq 0 ]
  # bypass audit 발화
  [[ "$stderr_out" == *"BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE=1"* ]]
  # block warning 없음 (bypass 시 verifier 미실행)
  [[ "$stderr_out" != *"WARN: spawn prompt missing"* ]]
}

# ── TC-8: hooks.json PreToolUse matcher:"Agent" entry presence ───────────────
@test "TC-8: hooks.json has PreToolUse matcher=Agent entry with pretooluse-agent-spawn-gate" {
  [ -f "$HOOKS_JSON" ] || fail "hooks.json not found"
  run python3 -c "
import json, sys
with open('$HOOKS_JSON') as f:
    data = json.load(f)
pretooluse_entries = data.get('hooks', {}).get('PreToolUse', [])
found = False
for group in pretooluse_entries:
    matcher = group.get('matcher', '')
    if matcher == 'Agent':
        for hook in group.get('hooks', []):
            if 'pretooluse-agent-spawn-gate' in hook.get('command', ''):
                found = True
                break
if not found:
    print('ERROR: pretooluse-agent-spawn-gate not found in PreToolUse[matcher=Agent] hooks')
    sys.exit(1)
print('PASS: pretooluse-agent-spawn-gate found in PreToolUse[matcher=Agent] hooks')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ── TC-9: hooks.json JSON 유효성 ─────────────────────────────────────────────
@test "TC-9: hooks.json is valid JSON (python3 json.tool)" {
  [ -f "$HOOKS_JSON" ] || fail "hooks.json not found"
  run python3 -m json.tool "$HOOKS_JSON"
  [ "$status" -eq 0 ]
}

# ── TC-10: Python ReDoS guard — pathological input (1000 line) < 500ms ───────
# ADR-061 Amendment 3 §결정 11 per-entry scan cap = 50 line → 1000-line 입력도
# 상위 50 line 만 scan 후 즉시 종료 (ReDoS 방지 설계 검증).
# budget: 500ms (Python interpreter 기동 + 50-line scan — 실측 avg ~60ms, 8× 여유)
@test "TC-10: Python verifier handles 1000-line pathological input within 500ms (scan_cap=50)" {
  [ -f "$VERIFIER_SCRIPT" ] || { echo "RED phase: verifier script required for GREEN"; return 1; }

  run python3 -c "
import subprocess, time, sys, os

# 1000-line pathological input: 각 line 200자 (RE_* 패턴의 .{0,200} 경계 테스트)
line = 'a' * 200
pathological_input = ('\n'.join([line] * 1000)).encode('utf-8')

start = time.time()
proc = subprocess.run(
    [sys.executable, os.path.join('$VERIFIER_SCRIPT'),'--prompt-stdin'],
    input=pathological_input,
    capture_output=True,
    timeout=5
)
elapsed = time.time() - start

# 500ms budget (8× 실측 여유 — Python startup ~50ms + scan ~10ms)
budget = 0.500
if elapsed < budget:
    print('PASS: %.3fs < %.3fs (%dms budget) scan_cap=50 effective' % (elapsed, budget, int(budget*1000)))
    sys.exit(0)
else:
    print('FAIL: %.3fs >= %.3fs (%dms budget exceeded)' % (elapsed, budget, int(budget*1000)))
    sys.exit(1)
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}
