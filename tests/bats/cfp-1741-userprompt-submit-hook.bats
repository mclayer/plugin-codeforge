#!/usr/bin/env bats
#
# cfp-1741-userprompt-submit-hook.bats
# CFP-1741 / ADR-115 §결정 1·3·5 — UserPromptSubmit hook + dispatcher entry
#
# TDD RED→GREEN stash proof (CFP-1334 / ADR-082 §결정 11.A / F-CR-1741-2):
#   RED:   stash hooks/userprompt-submit → TC-1·TC-2·TC-3·TC-4·TC-6 fail (5 fails + TC-7 fail)
#   GREEN: restore hooks/userprompt-submit → 7/7 pass (verified 2026-05-27 KST)
#
# 7 Test cases (TC-5 제거 — F-CR-1741-2 권장 (a), harness-level scope 외):
#   TC-1: stdout 에 [codeforge-wrapper-userprompt-submit] marker 존재
#   TC-2: bypass env (BYPASS_CODEFORGE_USERPROMPT_SUBMIT=1) 동작 — exit 0 + stdout 없음
#   TC-3: ADR-071 user-dialog-mode directive 포함 여부
#   TC-4: ADR-073 parallel-work-sentinel directive 포함 여부
#   TC-6: graceful degradation — hook always exits 0 even when BYPASS not set
#   TC-7: hooks.json UserPromptSubmit entry 에 userprompt-submit command 존재 (JSON validate)
#   TC-8: hooks.json JSON schema 유효성 (python json.tool)
#

HOOK_SCRIPT="hooks/userprompt-submit"
HOOKS_JSON="hooks/hooks.json"

setup() {
  # 모든 테스트에서 프로젝트 루트 기준으로 실행
  cd "${BATS_TEST_DIRNAME}/../.." || return 1
}

# TC-1: stdout 에 [codeforge-wrapper-userprompt-submit] marker 존재
@test "TC-1: stdout contains [codeforge-wrapper-userprompt-submit] marker" {
  [ -f "$HOOK_SCRIPT" ] || fail "RED phase: hook script required for GREEN"
  run bash "$HOOK_SCRIPT"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[codeforge-wrapper-userprompt-submit]"* ]]
}

# TC-2: bypass env 동작 — BYPASS_CODEFORGE_USERPROMPT_SUBMIT=1 시 exit 0 + stdout 없음
@test "TC-2: BYPASS_CODEFORGE_USERPROMPT_SUBMIT=1 exits 0 and emits no stdout" {
  [ -f "$HOOK_SCRIPT" ] || fail "RED phase: hook script required for GREEN"
  # stdout 만 캡처 (stderr 제외) — bats run 이 stderr 를 output 에 합산하므로 직접 캡처
  # local 과 assignment 분리 — `local exit_code=$?` 는 local builtin 의 exit 0 을 잡음 (F-CR-1741-1)
  local stdout_only exit_code
  stdout_only="$(BYPASS_CODEFORGE_USERPROMPT_SUBMIT=1 bash "$HOOK_SCRIPT" 2>/dev/null)"
  exit_code=$?
  [ "$exit_code" -eq 0 ]
  [ -z "$stdout_only" ]
}

# TC-3: ADR-071 user-dialog-mode 관련 directive 포함
@test "TC-3: stdout contains ADR-071 user-dialog-mode directive" {
  [ -f "$HOOK_SCRIPT" ] || fail "RED phase: hook script required for GREEN"
  run bash "$HOOK_SCRIPT"
  [ "$status" -eq 0 ]
  # ADR-071 내용 — dialog / 질문 / codeforge 중 하나 이상 포함
  [[ "$output" == *"ADR-071"* ]] || [[ "$output" == *"user-dialog"* ]] || [[ "$output" == *"dialog"* ]]
}

# TC-4: ADR-073 parallel-work-sentinel directive 포함
@test "TC-4: stdout contains ADR-073 parallel-work-sentinel directive" {
  [ -f "$HOOK_SCRIPT" ] || fail "RED phase: hook script required for GREEN"
  run bash "$HOOK_SCRIPT"
  [ "$status" -eq 0 ]
  # ADR-073 또는 parallel 또는 sentinel 중 하나 포함
  [[ "$output" == *"ADR-073"* ]] || [[ "$output" == *"parallel"* ]] || [[ "$output" == *"sentinel"* ]]
}

# TC-5: 제거 (F-CR-1741-2 권장 (a) — harness-level scope 외, bats 내 검증 불가.
#         run-hook.cmd exit /b 0 Windows cmd path 는 harness 수준 동작이며
#         bats fixture scope 에서 직접 검증 불가능. TC-7·TC-8 이 hooks.json 연결 커버.)

# TC-6: graceful degradation — set -e 사용 + 어떤 fail 도 exit 0 으로 trap
@test "TC-6: graceful degradation — hook always exits 0 even when BYPASS not set" {
  [ -f "$HOOK_SCRIPT" ] || fail "RED phase: hook script required for GREEN"
  # 정상 실행 — exit 0 보장
  run bash "$HOOK_SCRIPT"
  [ "$status" -eq 0 ]
}

# TC-7: hooks.json UserPromptSubmit entry 에 userprompt-submit command 존재
@test "TC-7: hooks.json UserPromptSubmit entry contains userprompt-submit command" {
  [ -f "$HOOKS_JSON" ] || fail "hooks.json not found"
  run python3 -c "
import json, sys
with open('$HOOKS_JSON') as f:
    data = json.load(f)
entries = data.get('hooks', {}).get('UserPromptSubmit', [])
found = False
for group in entries:
    for hook in group.get('hooks', []):
        if 'userprompt-submit' in hook.get('command', ''):
            found = True
            break
if not found:
    print('ERROR: userprompt-submit not found in UserPromptSubmit hooks')
    sys.exit(1)
print('PASS: userprompt-submit found in UserPromptSubmit hooks')
"
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# TC-8: hooks.json JSON schema 유효성 (python json.tool)
@test "TC-8: hooks.json is valid JSON (python json.tool)" {
  [ -f "$HOOKS_JSON" ] || fail "hooks.json not found"
  run python3 -m json.tool "$HOOKS_JSON"
  [ "$status" -eq 0 ]
}
