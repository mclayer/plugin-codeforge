#!/usr/bin/env bats
# tests/scripts/cfp-1193/check-rollback-signal.bats
# CFP-1193 TDD — check-rollback-signal.sh + check_rollback_signal.py
#
# Change Plan §8.1 Test Contract (15 TC):
#   TC-1:  error_rate 임계 초과 + 4 AND 충족 → hook trigger + Issue 발의
#   TC-2:  burn_rate 임계 초과 (window 산술) + 4 AND 충족 → trigger + Issue
#   TC-3:  임계 미초과 (정상 범위) → trigger 0 + Issue 0 + exit 0
#   TC-4:  안전장치 1 미충족 (임계 미정의) → auto 진입 0 (EC-1)
#   TC-5:  안전장치 2 미충족 (보존 기간 초과) → trigger 0 + hotfix 안내 Issue (EC-3)
#   TC-6:  안전장치 4 미충족 — kill-switch 활성 (filesystem flag) → trigger 무력화 + 감지 Issue 계속 (EC-2)
#   TC-6b: 안전장치 4 미충족 — config flag deploy.auto_rollback.enabled=false → trigger 무력화 (OR disable)
#   TC-7:  중복 0 검증 — script 안 rollback_to_blue / Traefik label flip 재정의 부재 grep (AC-3)
#   TC-8:  dedup — 동일 signature open Issue 존재 시 새 Issue 억제 (EC-5)
#   TC-9:  signature 형식 — sha256("<signal_type>|<measured>|<window>") | head -c 16
#   TC-10: kill-switch 우선 — 안전장치 1·2·3 충족 BUT kill-switch 활성 → trigger 0 (EC-2)
#   TC-11: wrapper-self-app fast-pass — repo=wrapper → exit 0 PASS (AC-7)
#   TC-12: exit 3-tier — 정상=0 / SETUP error=2
#   TC-13: EC-4 — 기존 hook 부재 → exit 2 + escalation Issue + 자동 재시도 0
#   TC-14: 안전장치 일부 충족 AND false → trigger 0 (EC-7)
#   TC-15: CFP-1243 contract-binding guard — emit signal_type ∈ operational-signal-v1 closed enum
#
# Mock seam:
#   _CFP1193_MOCK_* — 본 S4 signal/config 주입
#   _CFP1059_MOCK_* — 기존 hook 위임 (verbatim 사용)
#   _CFP1193_SKIP_ISSUE_CREATE=1 — Issue 발의 차단 (dry-run)
#   _CFP1193_MOCK_DEDUP=1 — open Issue 존재 (dedup 발동)
#   _CFP1193_MOCK_REPO_NAME=<name> — repo 이름 override

WROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
SIGNAL_SH="${WROOT}/scripts/check-rollback-signal.sh"
SIGNAL_PY="${WROOT}/scripts/check_rollback_signal.py"
ROLLBACK_SH="${WROOT}/templates/deployment/auto-rollback-hook.sh"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  # 기본 안전장치 4 AND 충족 상태 (trigger 허용 기본값)
  export _CFP1193_MOCK_ERROR_RATE="0.05"     # 5% 에러율
  export _CFP1193_MOCK_ERROR_RATE_THRESHOLD="0.02"  # 임계 2%
  export _CFP1193_MOCK_BURN_RATE="0.0"       # burn rate 정상
  export _CFP1193_MOCK_BURN_RATE_THRESHOLD="1.0"
  export _CFP1193_MOCK_WINDOW="3600"         # window 1h (초)
  export _CFP1193_MOCK_SIGNAL_TYPE="error_rate"

  # 기존 hook mock (안전장치 2 — 보존 기간 내)
  export _CFP1059_MOCK_WITHIN_RETENTION=1
  export _CFP1059_MOCK_DOCKER=1
  export _CFP1059_MOCK_SSH=1
  export _CFP1059_MOCK_HEALTH=real
  export _CFP1059_MOCK_BLUE_ACTIVE=0

  # kill-switch off (기본)
  export _CFP1193_MOCK_KILL_SWITCH=0
  export _CFP1193_MOCK_CONFIG_DISABLED=0

  # Issue 발의 차단 (테스트 모드)
  export _CFP1193_SKIP_ISSUE_CREATE=1
  export CBL_SKIP_ISSUE_CREATE=1

  # dedup off (기본 — open Issue 없음)
  export _CFP1193_MOCK_DEDUP=0

  # repo name (wrapper fast-pass 테스트용)
  export _CFP1193_MOCK_REPO_NAME="test-consumer-repo"

  export DEPLOY_REPO="test-consumer-repo"
  export DEPLOY_HOST="127.0.0.1"
}

teardown() {
  rm -rf "${TEST_TMP}"
  unset _CFP1193_MOCK_ERROR_RATE _CFP1193_MOCK_ERROR_RATE_THRESHOLD
  unset _CFP1193_MOCK_BURN_RATE _CFP1193_MOCK_BURN_RATE_THRESHOLD
  unset _CFP1193_MOCK_WINDOW _CFP1193_MOCK_SIGNAL_TYPE
  unset _CFP1059_MOCK_WITHIN_RETENTION _CFP1059_MOCK_DOCKER
  unset _CFP1059_MOCK_SSH _CFP1059_MOCK_HEALTH _CFP1059_MOCK_BLUE_ACTIVE
  unset _CFP1193_MOCK_KILL_SWITCH _CFP1193_MOCK_CONFIG_DISABLED
  unset _CFP1193_SKIP_ISSUE_CREATE CBL_SKIP_ISSUE_CREATE
  unset _CFP1193_MOCK_DEDUP _CFP1193_MOCK_REPO_NAME
  unset _CFP1193_MOCK_CONFIG_YAML_PATH
  unset DEPLOY_REPO DEPLOY_HOST
}

# --- 파일 존재 확인 ---
@test "스크립트 파일 존재: check-rollback-signal.sh" {
  [ -f "${SIGNAL_SH}" ]
  [ -x "${SIGNAL_SH}" ]
}

@test "Python 파일 존재: check_rollback_signal.py (ADR-061)" {
  [ -f "${SIGNAL_PY}" ]
}

# ---
# TC-1: error_rate 임계 초과 + 안전장치 4 AND → hook trigger + Issue
# ---
@test "TC-1: error_rate 임계 초과 + 4 AND 충족 → hook trigger 호출 흔적 + 사후 알림" {
  # 에러율 5% > 임계 2% → safety_1=true + 나머지 AND 충족
  export _CFP1193_MOCK_ERROR_RATE="0.05"
  export _CFP1193_MOCK_ERROR_RATE_THRESHOLD="0.02"
  export _CFP1193_MOCK_KILL_SWITCH=0
  export _CFP1059_MOCK_WITHIN_RETENTION=1

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  # hook trigger 흔적 또는 알림 흔적 (hook mock=1 이므로 [ROLLBACK] 출력)
  [[ "${output}" == *"[SIGNAL]"* ]] || \
    [[ "${output}" == *"trigger"* ]] || \
    [[ "${output}" == *"ROLLBACK"* ]] || \
    [[ "${output}" == *"auto-rollback"* ]]
  [ "${status}" -eq 0 ]
}

# ---
# TC-2: burn_rate 임계 초과 → trigger + Issue
#   CFP-1243: 산출 signal_type = 정규명 latency_burn_rate (contract enum value)
# ---
@test "TC-2: latency burn_rate 임계 초과 + 4 AND 충족 → trigger + Issue (signal_type=latency_burn_rate)" {
  # burn rate 정량 초과 (window 산술)
  export _CFP1193_MOCK_BURN_RATE="1.5"
  export _CFP1193_MOCK_BURN_RATE_THRESHOLD="1.0"
  export _CFP1193_MOCK_ERROR_RATE="0.0"          # error_rate 는 정상
  export _CFP1193_MOCK_ERROR_RATE_THRESHOLD="0.02"
  export _CFP1193_MOCK_SIGNAL_TYPE="latency_burn_rate"
  export _CFP1059_MOCK_WITHIN_RETENTION=1

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  # CFP-1243: producer 가 정규 enum value latency_burn_rate emit (비정규 burn_rate 아님)
  [[ "${output}" == *"signal_type=latency_burn_rate"* ]]
  # 비정규 literal "signal_type=burn_rate" 절대 출현 금지 (drift guard)
  [[ "${output}" != *"signal_type=burn_rate"* ]]
  [ "${status}" -eq 0 ]
}

# ---
# TC-3: 임계 미초과 (정상) → trigger 0 + Issue 0 + exit 0
# ---
@test "TC-3: 임계 미초과 (정상 범위) → trigger 0 + exit 0 PASS" {
  export _CFP1193_MOCK_ERROR_RATE="0.005"         # 0.5% — 임계 2% 미달
  export _CFP1193_MOCK_ERROR_RATE_THRESHOLD="0.02"
  export _CFP1193_MOCK_BURN_RATE="0.0"
  export _CFP1193_MOCK_BURN_RATE_THRESHOLD="1.0"

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  [ "${status}" -eq 0 ]
  [[ "${output}" != *"[SIGNAL]"* ]]        # 신호 감지 없음
  [[ "${output}" != *"ROLLBACK"* ]]        # rollback hook 미호출
}

# ---
# TC-4: 안전장치 1 미충족 (임계 미정의/모달) → auto 진입 0
# ---
@test "TC-4: 안전장치 1 미충족 (임계 미정의) → trigger 0 (EC-1)" {
  # 임계값 미정의 = 빈 문자열
  export _CFP1193_MOCK_ERROR_RATE_THRESHOLD=""
  export _CFP1193_MOCK_BURN_RATE_THRESHOLD=""

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  # trigger 0 — user-decision layer (EC-1)
  [[ "${output}" != *"ROLLBACK"* ]]
  [[ "${output}" == *"safety_1=false"* ]] || \
    [[ "${output}" == *"threshold"* ]] || \
    [ "${status}" -eq 0 ]
}

# ---
# TC-5: 안전장치 2 미충족 (보존 기간 초과) → trigger 0 + hotfix 안내 (EC-3)
# ---
@test "TC-5: 안전장치 2 미충족 (보존 기간 초과) → trigger 0 + hotfix 안내 Issue" {
  # 보존 window 만료 (기존 hook check_within_retention = false)
  export _CFP1059_MOCK_WITHIN_RETENTION=0   # hook 이 만료 경로 반환
  export _CFP1193_MOCK_ERROR_RATE="0.05"    # 임계 초과 (신호 1 충족)

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  # trigger 0 + hotfix 안내
  [[ "${output}" != *"[ROLLBACK]"* ]]
  [[ "${output}" == *"hotfix"* ]] || \
    [[ "${output}" == *"retention"* ]] || \
    [[ "${output}" == *"expired"* ]] || \
    [[ "${output}" == *"만료"* ]]
}

# ---
# TC-6: kill-switch 활성 (filesystem flag) → trigger 무력화 + 신호 감지·기록 계속 (EC-2)
# ---
@test "TC-6: kill-switch 활성 (filesystem flag) → trigger 전체 무력화 + 감지 Issue 계속" {
  # filesystem flag 생성
  local flag_dir="${TEST_TMP}/.codeforge"
  mkdir -p "${flag_dir}"
  touch "${flag_dir}/auto-rollback.disabled"

  export _CFP1193_MOCK_KILL_SWITCH_FLAG="${TEST_TMP}/.codeforge/auto-rollback.disabled"
  export _CFP1193_MOCK_ERROR_RATE="0.05"   # 임계 초과 (안전장치 1 충족)

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  # rollback trigger 무력화
  [[ "${output}" != *"[ROLLBACK] green"* ]]
  # 신호 감지·기록은 계속 (EC-2)
  [[ "${output}" == *"kill-switch"* ]] || \
    [[ "${output}" == *"disabled"* ]] || \
    [[ "${output}" == *"kill_switch"* ]] || \
    [[ "${output}" == *"감지"* ]]
}

# ---
# TC-6b: config flag deploy.auto_rollback.enabled=false → trigger 무력화 (OR disable)
# ---
@test "TC-6b: config flag disabled → trigger 무력화 (OR disable §3.4)" {
  export _CFP1193_MOCK_CONFIG_DISABLED=1   # config flag disabled mock
  export _CFP1193_MOCK_ERROR_RATE="0.05"   # 임계 초과

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  [[ "${output}" != *"[ROLLBACK] green"* ]]
}

# ---
# TC-6c: config yaml real path — yaml.safe_load 경로 검증 (F-CR-1193-2)
# project.yaml 임시 파일 주입 (_CFP1193_MOCK_CONFIG_YAML_PATH) →
#   deploy.auto_rollback.enabled: false → trigger 무력화
# ---
@test "TC-6c: real config yaml path — yaml.safe_load enabled=false → trigger 무력화" {
  # 임시 project.yaml 생성 (deploy.auto_rollback.enabled: false)
  local config_yaml="${TEST_TMP}/project.yaml"
  cat > "${config_yaml}" <<'YAML'
deploy:
  auto_rollback:
    enabled: false
YAML

  # mock config yaml path 주입 (real yaml.safe_load 경로)
  export _CFP1193_MOCK_CONFIG_YAML_PATH="${config_yaml}"
  # config_disabled mock 은 OFF (real yaml.safe_load 경로를 검증)
  export _CFP1193_MOCK_CONFIG_DISABLED=0
  export _CFP1193_MOCK_ERROR_RATE="0.05"   # 임계 초과 (안전장치 1 충족)

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  # kill-switch 활성 (yaml.safe_load 로 detected) → rollback trigger 0
  [[ "${output}" != *"[ROLLBACK] green"* ]]
  # kill-switch 표시 있어야 함 (EC-2 신호 감지·기록 계속)
  [[ "${output}" == *"kill-switch"* ]] || \
    [[ "${output}" == *"kill_switch"* ]] || \
    [[ "${output}" == *"disabled"* ]]
  [ "${status}" -eq 0 ]
}

# ---
# TC-7: 중복 0 검증 — script 안 rollback_to_blue / Traefik label flip 재구현 부재 (AC-3)
# ---
@test "TC-7: 중복 0 검증 — rollback_to_blue / Traefik label flip 재정의 부재 (AC-3)" {
  # check-rollback-signal.sh 안에 rollback 실행 로직 재구현 없어야 함
  run grep -c "rollback_to_blue\|Traefik label flip\|label_flip\|blue_active.*swap\|swap.*blue" \
    "${SIGNAL_SH}"
  [ "${output}" = "0" ]

  # check_rollback_signal.py 안에도 없어야 함
  run grep -c "rollback_to_blue\|Traefik label flip\|label_flip" \
    "${SIGNAL_PY}"
  [ "${output}" = "0" ]
}

# ---
# TC-8: dedup — 동일 signature open Issue 존재 시 새 Issue 억제 (EC-5)
# ---
@test "TC-8: dedup — 동일 signature open Issue 존재 → 새 Issue 억제 (EC-5)" {
  export _CFP1193_MOCK_DEDUP=1    # open Issue 존재 mock (gh issue list mock)
  export _CFP1193_MOCK_ERROR_RATE="0.05"

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  [ "${status}" -eq 0 ]
  # 새 Issue 발의 없음 (dedup skip)
  [[ "${output}" == *"dedup"* ]] || \
    [[ "${output}" == *"skip"* ]] || \
    [[ "${output}" == *"exists"* ]] || \
    [[ "${output}" == *"중복"* ]] || \
    [[ "${output}" == *"SKIP"* ]]
}

# ---
# TC-9: signature 형식 — sha256("<signal_type>|<measured>|<window>") | head -c 16
# ---
@test "TC-9: signature 형식 — 16자 hex (check-channel-drift.sh 답습)" {
  # check_rollback_signal.py 가 signature 계산하는지 확인
  # Python 직접 호출하여 signature output 확인
  export _CFP1193_MOCK_ERROR_RATE="0.05"
  export _CFP1193_MOCK_ERROR_RATE_THRESHOLD="0.02"
  export _CFP1193_MOCK_BURN_RATE="0.0"
  export _CFP1193_MOCK_BURN_RATE_THRESHOLD="1.0"
  export _CFP1193_MOCK_WINDOW="3600"
  export _CFP1193_MOCK_SIGNAL_TYPE="error_rate"
  export _CFP1193_MOCK_KILL_SWITCH=0
  export _CFP1193_MOCK_CONFIG_DISABLED=0

  run python3 "${SIGNAL_PY}" \
    --error-rate "${_CFP1193_MOCK_ERROR_RATE}" \
    --error-rate-threshold "${_CFP1193_MOCK_ERROR_RATE_THRESHOLD}" \
    --burn-rate "${_CFP1193_MOCK_BURN_RATE}" \
    --burn-rate-threshold "${_CFP1193_MOCK_BURN_RATE_THRESHOLD}" \
    --window "${_CFP1193_MOCK_WINDOW}" \
    --kill-switch-flag "" \
    --config-disabled "false"

  # signature 가 16자 hex 형식
  SIG=$(echo "${output}" | grep "^signature=" | cut -d= -f2)
  [ -n "${SIG}" ]
  [[ "${SIG}" =~ ^[0-9a-f]{16}$ ]]
}

# ---
# TC-10: kill-switch 우선 — 안전장치 1·2·3 충족 BUT kill-switch 활성 → trigger 0
# ---
@test "TC-10: kill-switch 우선 — 다른 안전장치 충족 무관 trigger 0 (EC-2)" {
  # filesystem flag 생성
  local flag_dir="${TEST_TMP}/.codeforge"
  mkdir -p "${flag_dir}"
  touch "${flag_dir}/auto-rollback.disabled"

  export _CFP1193_MOCK_KILL_SWITCH_FLAG="${TEST_TMP}/.codeforge/auto-rollback.disabled"
  export _CFP1193_MOCK_ERROR_RATE="0.05"           # 안전장치 1 충족
  export _CFP1059_MOCK_WITHIN_RETENTION=1           # 안전장치 2 충족
  # 안전장치 3 = monitor 활성 = 충족

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  # trigger 0 (kill-switch 우선)
  [[ "${output}" != *"[ROLLBACK] green"* ]]
}

# ---
# TC-11: wrapper-self-app fast-pass (repo=wrapper) → exit 0 PASS 신호 측정 skip (AC-7)
# ---
@test "TC-11: wrapper-self-app fast-pass → exit 0 PASS (ADR-104 §결정 4)" {
  export _CFP1193_MOCK_REPO_NAME="plugin-codeforge"   # wrapper repo 이름

  run bash "${SIGNAL_SH}" \
    --repo "plugin-codeforge" --host "${DEPLOY_HOST}"

  [ "${status}" -eq 0 ]
  # fast-pass 표시 (신호 측정 skip)
  [[ "${output}" == *"fast-pass"* ]] || \
    [[ "${output}" == *"wrapper"* ]] || \
    [[ "${output}" == *"N/A"* ]] || \
    [[ "${output}" == *"skip"* ]]
}

# ---
# TC-12: exit 3-tier — 정상/임계감지=0 / SETUP error=2
# ---
@test "TC-12a: exit 0 — 정상 (임계 미초과)" {
  export _CFP1193_MOCK_ERROR_RATE="0.005"     # 임계 미달
  run bash "${SIGNAL_SH}" --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"
  [ "${status}" -eq 0 ]
}

@test "TC-12b: exit 0 — 임계 감지 + Issue 발의 성공 (warning tier)" {
  export _CFP1193_MOCK_ERROR_RATE="0.05"     # 임계 초과
  run bash "${SIGNAL_SH}" --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"
  [ "${status}" -eq 0 ]
}

# ---
# TC-13: EC-4 — 기존 hook 부재 → exit 2 + escalation + 자동 재시도 0 (ADR-057)
# ---
@test "TC-13: EC-4 — hook 부재 → exit 2 + 자동 재시도 0 (ADR-057)" {
  export _CFP1193_MOCK_ERROR_RATE="0.05"   # 임계 초과 (trigger 시도)
  export _CFP1193_MOCK_HOOK_MISSING=1      # hook 부재 mock

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  # SETUP error = exit 2
  [ "${status}" -eq 2 ]
  # 에러 메시지
  [[ "${output}" == *"hook"* ]] || \
    [[ "${output}" == *"missing"* ]] || \
    [[ "${output}" == *"부재"* ]] || \
    [[ "${output}" == *"ERROR"* ]]
}

# ---
# TC-14: 안전장치 일부만 충족 → AND false → trigger 0 (EC-7)
# ---
@test "TC-14: 안전장치 AND 일부만 충족 → trigger 0 (EC-7)" {
  # 안전장치 1 false (임계 미초과) — AND 단락 평가 → trigger 0
  export _CFP1193_MOCK_ERROR_RATE="0.005"          # 임계 미달 (safety_1=false)
  export _CFP1193_MOCK_ERROR_RATE_THRESHOLD="0.02"
  export _CFP1059_MOCK_WITHIN_RETENTION=1           # 안전장치 2 충족
  # 안전장치 3 = monitor 활성 (충족)
  export _CFP1193_MOCK_KILL_SWITCH=0                # 안전장치 4 충족

  run bash "${SIGNAL_SH}" \
    --repo "${DEPLOY_REPO}" --host "${DEPLOY_HOST}"

  [ "${status}" -eq 0 ]
  [[ "${output}" != *"[ROLLBACK]"* ]]
}

# ---
# TC-15: CFP-1243 contract-binding guard —
#   producer 가 emit 하는 non-none signal_type 값이 operational-signal-v1 의
#   closed enum {error_rate, latency_burn_rate, regression, smoke_health} 의
#   MEMBER 임을 보증. 비정규 alias (burn_rate 등) 출현 시 FAIL.
#   ADR-106 §결정 3 / operational-signal-v1 §3.1 signal_type enum 정합.
#   check_rollback_signal.py 의 reachable non-none 값 = {error_rate, latency_burn_rate}.
# ---
@test "TC-15: contract-binding — emit signal_type ∈ operational-signal-v1 closed enum (CFP-1243)" {
  # operational-signal-v1 §3.1 closed enum (open_extension: false)
  local CONTRACT_ENUM="error_rate latency_burn_rate regression smoke_health"

  # --- case A: burn-rate 임계 초과 → 정확히 latency_burn_rate emit ---
  run python3 "${SIGNAL_PY}" \
    --error-rate "0.0" \
    --error-rate-threshold "0.02" \
    --burn-rate "1.5" \
    --burn-rate-threshold "1.0" \
    --window "3600" \
    --kill-switch-flag "" \
    --config-disabled "false"
  [ "${status}" -eq 0 ]
  local SIG_TYPE_A
  SIG_TYPE_A=$(echo "${output}" | grep "^signal_type=" | cut -d= -f2)
  # 정확히 latency_burn_rate (비정규 burn_rate 절대 아님)
  [ "${SIG_TYPE_A}" = "latency_burn_rate" ]
  # closed enum membership 확인
  [[ " ${CONTRACT_ENUM} " == *" ${SIG_TYPE_A} "* ]]

  # --- case B: error-rate 임계 초과 → error_rate emit (enum member) ---
  run python3 "${SIGNAL_PY}" \
    --error-rate "0.05" \
    --error-rate-threshold "0.02" \
    --burn-rate "0.0" \
    --burn-rate-threshold "1.0" \
    --window "3600" \
    --kill-switch-flag "" \
    --config-disabled "false"
  [ "${status}" -eq 0 ]
  local SIG_TYPE_B
  SIG_TYPE_B=$(echo "${output}" | grep "^signal_type=" | cut -d= -f2)
  [ "${SIG_TYPE_B}" = "error_rate" ]
  [[ " ${CONTRACT_ENUM} " == *" ${SIG_TYPE_B} "* ]]
}
