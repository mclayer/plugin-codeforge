#!/usr/bin/env bats
# tests/hooks/test_schedule_wakeup_reminder.bats
# CFP-1755 / ADR-064 Amendment 12 — PreToolUse ScheduleWakeup advisory reminder hook bats fixture
#
# AC-1: hook 발화 시 valid JSON 출력 + PreToolUse hookEventName + additionalContext 4-tuple 안내
# AC-2: non-blocking (decision/permissionDecision 필드 부재)
# AC-3: BYPASS_SCHEDULE_WAKEUP_REMINDER=1 env → 발화 생략 (stdout 0 byte)
# AC-4: fail-safe (stdin 부재 / 파싱 오류 시에도 exit 0)
# AC-5: hooks/hooks.json PreToolUse array length 2 + matcher names ["Bash", "ScheduleWakeup"]
#
# CFP-1334 §8.4 5 markers:
#   pre_impl_sha:       hook script 가 단순 정적 echo 만 수행 — Phase 2 구현 영역 0 (Wave 2A advisory only),
#                       Wave 2B (signal inspection mechanism) 가 Phase 2 영역 carrier
#   git_stash_sequence: N/A (정적 hook script, RED 영역 부재 — Wave 2A scope)
#   role_vocabulary:    Orchestrator / ScheduleWakeup tool / PreToolUse hook 도메인 어휘 정합
#   red_green_anchor:   본 Wave 2A 는 advisory layer = RED 영역 부재 (Wave 2B blocking gate 시 RED→GREEN)
#   platform_verified:  Windows Git Bash + Unix bash 양 환경 hook script 정합 (CFP-1738 동등)

bats_require_minimum_version 1.5.0

BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
REPO_ROOT="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
HOOK_SCRIPT="${REPO_ROOT}/hooks/schedule-wakeup-reminder"
HOOKS_JSON="${REPO_ROOT}/hooks/hooks.json"

# On MSYS / Git Bash for Windows, paths like /c/workspace/... need conversion for Python (Windows native).
# Use cygpath when available; fall back to original path (Unix).
if command -v cygpath >/dev/null 2>&1; then
  HOOKS_JSON_PY="$(cygpath -w "${HOOKS_JSON}")"
  # forward-slash form for Python single-quoted string compatibility (cross-platform)
  HOOKS_JSON_PY="${HOOKS_JSON_PY//\\//}"
else
  HOOKS_JSON_PY="${HOOKS_JSON}"
fi

# role_vocabulary: Orchestrator + ScheduleWakeup + PreToolUse
ROLE_VOCAB="schedule-wakeup-reminder"

setup() {
  unset BYPASS_SCHEDULE_WAKEUP_REMINDER || true
}

teardown() {
  unset BYPASS_SCHEDULE_WAKEUP_REMINDER || true
}

# AC-1: hook 발화 시 valid JSON 출력 + PreToolUse hookEventName + additionalContext 4-tuple 안내
@test "TC-1: hook 발화 시 valid PreToolUse JSON + 4-tuple advisory" {
  run bash -c "echo '{\"hook_event_name\":\"PreToolUse\",\"tool_name\":\"ScheduleWakeup\"}' | bash '${HOOK_SCRIPT}'"
  [ "$status" -eq 0 ]
  [ -n "$output" ]
  # valid JSON
  echo "$output" | python -c "import sys, json; json.load(sys.stdin)"
  # hookEventName == PreToolUse
  echo "$output" | grep -q '"hookEventName":"PreToolUse"'
  # additionalContext present
  echo "$output" | grep -q '"additionalContext"'
  # 4 signal name 모두 출현
  echo "$output" | grep -q 'armed_monitor'
  echo "$output" | grep -q 'in_progress_agent'
  echo "$output" | grep -q 'open_pr_session'
  echo "$output" | grep -q 'actionable_backlog'
}

# AC-2: non-blocking (decision/permissionDecision 필드 부재)
@test "TC-2: non-blocking — decision/permissionDecision 필드 부재" {
  run bash -c "echo '{\"hook_event_name\":\"PreToolUse\",\"tool_name\":\"ScheduleWakeup\"}' | bash '${HOOK_SCRIPT}'"
  [ "$status" -eq 0 ]
  # decision 필드 부재
  run bash -c "echo '$output' | grep -c '\"decision\"' || true"
  [ "$output" = "0" ]
  # permissionDecision 필드 부재
  run bash -c "echo '$output' | grep -c '\"permissionDecision\"' || true"
  [ "$output" = "0" ]
}

# AC-3: BYPASS_SCHEDULE_WAKEUP_REMINDER=1 env → 발화 생략 (stdout 0 byte)
@test "TC-3: BYPASS_SCHEDULE_WAKEUP_REMINDER=1 → stdout 0 byte" {
  BYPASS_SCHEDULE_WAKEUP_REMINDER=1 run bash -c "echo '{\"hook_event_name\":\"PreToolUse\"}' | bash '${HOOK_SCRIPT}'"
  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

# AC-4: fail-safe (stdin 부재 / 파싱 오류 시에도 exit 0)
@test "TC-4: fail-safe — stdin empty 시 exit 0 + reminder 발화" {
  run bash -c "echo '' | bash '${HOOK_SCRIPT}'"
  [ "$status" -eq 0 ]
  # Wave 2A scope: payload 사용 0 영역 — empty stdin 도 reminder 발화 (advisory invariant)
  echo "$output" | grep -q '"hookEventName":"PreToolUse"'
}

@test "TC-4b: fail-safe — stdin parse error 시 exit 0 + reminder 발화" {
  run bash -c "echo 'xyz_not_json' | bash '${HOOK_SCRIPT}'"
  [ "$status" -eq 0 ]
  echo "$output" | grep -q '"hookEventName":"PreToolUse"'
}

# AC-5: hooks/hooks.json PreToolUse array length 2 + matcher names ["Bash", "ScheduleWakeup"]
@test "TC-5: hooks.json PreToolUse array length 2 + matcher ScheduleWakeup present" {
  # valid JSON parse + length check via bash + python pipe (single command)
  run bash -c "python -c \"import json; d = json.load(open('${HOOKS_JSON_PY}')); print(len(d['hooks']['PreToolUse']))\""
  [ "$status" -eq 0 ]
  [ "$output" = "2" ]
  # matcher names list
  run bash -c "python -c \"import json; d = json.load(open('${HOOKS_JSON_PY}')); print(','.join([e['matcher'] for e in d['hooks']['PreToolUse']]))\""
  [ "$status" -eq 0 ]
  [ "$output" = "Bash,ScheduleWakeup" ]
  # command 정확 — schedule-wakeup-reminder reference in second PreToolUse entry
  run bash -c "python -c \"import json; d = json.load(open('${HOOKS_JSON_PY}')); cmd = d['hooks']['PreToolUse'][1]['hooks'][0]['command']; print('schedule-wakeup-reminder' in cmd)\""
  [ "$status" -eq 0 ]
  [ "$output" = "True" ]
}
