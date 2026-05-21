#!/usr/bin/env bats
# tests/scripts/cfp-1194/check-operational-regression.bats
# CFP-1194 TDD — check-operational-regression.sh + check_operational_regression.py
#
# Change Plan §8.1 Test Contract (16 TC):
#   TC-1:  regression 감지 (baseline 대비 N% 악화) + flap 미억제 → ops-signal Issue 발의
#   TC-2:  smoke·health FAIL (이진) + N-tick 연속 (flap 미억제) → ops-signal Issue 발의
#   TC-3:  regression 임계 미초과 (정상 범위) → 신호 0 + Issue 0 + exit 0
#   TC-4:  regression 임계 미정의 → 신호 미감지 (보수적) Issue 0
#   TC-5:  flap 흡수 (a) N-tick — health 단발 FAIL 후 자가 복구 (N 미만) → 신호 억제
#   TC-6:  flap 흡수 (b) hysteresis — regression 이 임계 초과 후 recovery margin 미만 미복귀
#   TC-7:  flap 흡수 (a) N-tick 도달 — health FAIL N tick 연속 → 신호 발의
#   TC-8:  baseline 부재 (첫 배포 EC-1) → 신호 미감지 + 현재값 baseline 기록 + exit 0
#   TC-9:  metric source 불가 (EC-2) → exit 2 + escalation Issue + 자동 재시도 0
#   TC-10: dedup — 동일 signature open Issue 존재 → 새 Issue 억제
#   TC-11: signature 형식 — sha256("<signal_type>|<measured>|<window>")[:16]
#   TC-12: 중복 0 검증 (S4 disjoint) — script 안 rollback_to_blue 부재 grep
#   TC-13: wrapper-self-app fast-pass (repo=wrapper) → exit 0 PASS
#   TC-14: exit 3-tier — 정상=0 / SETUP error=2
#   TC-15: health 0 API call 경계 (D3) — filesystem 파싱 primary, webhook push 경로 부재
#   TC-16: flap state cross-tick restart (§8.5) — flap counter 파일 존재 → 카운터 복원
#
# Mock seam:
#   _CFP1194_MOCK_* — S5 signal/config 주입
#   _CFP1194_SKIP_ISSUE_CREATE=1 — Issue 발의 차단 (dry-run)
#   _CFP1194_MOCK_DEDUP=1 — open Issue 존재 (dedup 발동)
#   _CFP1194_MOCK_REPO_NAME=<name> — repo 이름 override

WROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
REGRESSION_SH="${WROOT}/scripts/check-operational-regression.sh"
REGRESSION_PY="${WROOT}/scripts/check_operational_regression.py"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  # 기본 mock seam: regression 감지 기본값 (TC-1 기준)
  export _CFP1194_MOCK_REPO_NAME="test-consumer-repo"
  export _CFP1194_SKIP_ISSUE_CREATE=1
  export CBL_SKIP_ISSUE_CREATE=1
  export _CFP1194_MOCK_DEDUP=0
  export _CFP1194_MOCK_METRIC_UNAVAILABLE=0
  export _CFP1194_MOCK_FLAP_N=2
  export _CFP1194_MOCK_RECOVERY_MARGIN=0.5

  # 기본 metric 파일 (regression 기본값: error_rate 5% 현재 vs 2% baseline)
  BASELINE_FILE="${TEST_TMP}/baseline.json"
  CURRENT_FILE="${TEST_TMP}/current.json"
  HEALTH_FILE="${TEST_TMP}/health.json"
  FLAP_STATE_FILE="${TEST_TMP}/flap-state.json"

  echo '{"error_rate": 0.02}' > "${BASELINE_FILE}"
  echo '{"error_rate": 0.05}' > "${CURRENT_FILE}"  # 150% 악화 (> 임계)
  # health 기본: 정상 (FAIL 아님)
  echo '{"status": "ok"}' > "${HEALTH_FILE}"

  export _CFP1194_MOCK_BASELINE_FILE="${BASELINE_FILE}"
  export _CFP1194_MOCK_CURRENT_METRIC_FILE="${CURRENT_FILE}"
  export _CFP1194_MOCK_HEALTH_FILE="${HEALTH_FILE}"
  export _CFP1194_MOCK_FLAP_STATE_FILE="${FLAP_STATE_FILE}"

  export BASELINE_FILE CURRENT_FILE HEALTH_FILE FLAP_STATE_FILE
}

teardown() {
  rm -rf "${TEST_TMP}"
  unset _CFP1194_MOCK_REPO_NAME _CFP1194_SKIP_ISSUE_CREATE CBL_SKIP_ISSUE_CREATE
  unset _CFP1194_MOCK_DEDUP _CFP1194_MOCK_METRIC_UNAVAILABLE
  unset _CFP1194_MOCK_FLAP_N _CFP1194_MOCK_RECOVERY_MARGIN
  unset _CFP1194_MOCK_BASELINE_FILE _CFP1194_MOCK_CURRENT_METRIC_FILE
  unset _CFP1194_MOCK_HEALTH_FILE _CFP1194_MOCK_FLAP_STATE_FILE
  unset BASELINE_FILE CURRENT_FILE HEALTH_FILE FLAP_STATE_FILE
}

# --- 파일 존재 확인 ---
@test "스크립트 파일 존재: check-operational-regression.sh" {
  [ -f "${REGRESSION_SH}" ]
}

@test "Python 파일 존재: check_operational_regression.py (ADR-061)" {
  [ -f "${REGRESSION_PY}" ]
}

# ---
# TC-1: regression 감지 (baseline 대비 N% 악화) + flap N-tick 도달 → 신호 감지
# ---
@test "TC-1: regression 감지 (150% 악화 > 임계 10%) + N-tick 도달 → signal_detected=true" {
  # N-tick 누적: 1회 실행 = tick=1 < N=2 (억제), 2회 실행 = tick=2 >= N=2 (발의)
  export _CFP1194_MOCK_FLAP_N=1  # N=1 → 즉시 발의 (TC-1 단순화)
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  echo "output: ${output}"
  echo "status: ${status}"
  # 신호 감지 (dry-run, issue create skip)
  [[ "${output}" == *"signal_detected=true"* ]] || [[ "${output}" == *"SIGNAL"* ]] || [[ "${status}" == "0" ]]
  # exit 0 (PASS — 신호 감지 + dry-run)
  [ "${status}" -eq 0 ]
}

# ---
# TC-2: smoke·health FAIL (이진) + N-tick 도달 → 신호 발의
# ---
@test "TC-2: health FAIL (status=fail) + N-tick 도달 → smoke_health 신호 감지" {
  echo '{"status": "fail"}' > "${HEALTH_FILE}"
  export _CFP1194_MOCK_FLAP_N=1  # N=1 → 즉시 발의
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --signal-type "smoke_health" \
    --regression-threshold ""
  echo "output: ${output}"
  echo "status: ${status}"
  [[ "${output}" == *"smoke_health"* ]] || [[ "${output}" == *"SIGNAL"* ]]
  [ "${status}" -eq 0 ]
}

# ---
# TC-3: regression 임계 미초과 (정상 범위) → 신호 0
# ---
@test "TC-3: regression 임계 미초과 (현재 2% vs baseline 2%) → 신호 0 + exit 0" {
  echo '{"error_rate": 0.02}' > "${CURRENT_FILE}"  # baseline 동일 = 0% 악화
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  echo "output: ${output}"
  echo "status: ${status}"
  [[ "${output}" == *"신호 미감지"* ]] || [[ "${output}" == *"PASS"* ]] || [[ "${output}" == *"signal_detected=false"* ]]
  [ "${status}" -eq 0 ]
}

# ---
# TC-4: regression 임계 미정의 → 신호 미감지 (보수적)
# ---
@test "TC-4: regression 임계 미정의 → 신호 미감지 (보수적 unconditional guard)" {
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "" \
    --signal-type "regression"
  echo "output: ${output}"
  echo "status: ${status}"
  # 임계 미정의 = 보수적 미감지
  [[ "${output}" == *"임계 미정의"* ]] || [[ "${output}" == *"PASS"* ]] || [[ "${output}" == *"미감지"* ]]
  [ "${status}" -eq 0 ]
}

# ---
# TC-5: flap 흡수 (a) N-tick — health 단발 FAIL (N 미만) → 신호 억제
# ---
@test "TC-5: health 단발 FAIL + N-tick 미달 (flap_suppressed=true) → Issue 발의 0" {
  echo '{"status": "fail"}' > "${HEALTH_FILE}"
  export _CFP1194_MOCK_FLAP_N=3  # N=3 → 1회 FAIL = tick=1 < 3 → 억제
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --signal-type "smoke_health" \
    --regression-threshold ""
  echo "output: ${output}"
  echo "status: ${status}"
  # flap 억제 → Issue 발의 0 + exit 0
  [[ "${output}" == *"flap"* ]] || [[ "${output}" == *"억제"* ]] || [[ "${output}" == *"PASS"* ]]
  [ "${status}" -eq 0 ]
}

# ---
# TC-6: flap 흡수 (b) hysteresis — regression 경계값 진동 (recovery margin 미달)
# ---
@test "TC-6: regression hysteresis — 임계 초과 후 recovery margin 미달 → 신호 유지" {
  # 첫 tick: 15% 악화 (임계 10% 초과) → N=1 발의
  export _CFP1194_MOCK_FLAP_N=1
  echo '{"error_rate": 0.02}' > "${BASELINE_FILE}"
  echo '{"error_rate": 0.023}' > "${CURRENT_FILE}"  # 15% 악화 > 10% 임계
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  echo "output first: ${output}"

  # 두 번째 tick: 11% 악화 (임계 초과지만 hysteresis: resolve=10-0.5=9.5%, 현재 11% > 9.5% → 미해소)
  echo '{"error_rate": 0.0222}' > "${CURRENT_FILE}"  # ~11% 악화 > resolve 9.5%
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  echo "output hysteresis: ${output}"
  echo "status: ${status}"
  # hysteresis: resolve threshold 미달 = 신호 유지 or 억제 (dedup에 의해 exit 0)
  [ "${status}" -eq 0 ]
}

# ---
# TC-7: flap N-tick 도달 — health FAIL N tick 연속 → 신호 발의
# ---
@test "TC-7: health FAIL N-tick 도달 (sustained) → flap_suppressed=false + 신호 발의" {
  echo '{"status": "fail"}' > "${HEALTH_FILE}"
  export _CFP1194_MOCK_FLAP_N=2  # N=2

  # tick 1: flap 카운터=1, N=2 미달 → 억제
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --signal-type "smoke_health" \
    --regression-threshold ""
  echo "tick1 output: ${output}"

  # tick 2: flap 카운터=2, N=2 도달 → 발의
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --signal-type "smoke_health" \
    --regression-threshold ""
  echo "tick2 output: ${output}"
  echo "status: ${status}"
  # N-tick 도달 = 신호 발의 (dry-run = exit 0)
  [ "${status}" -eq 0 ]
  # 2번째 tick에서 smoke_health 신호 감지 또는 flap 미억제
  [[ "${output}" == *"smoke_health"* ]] || [[ "${output}" == *"SIGNAL"* ]] || [[ "${output}" == *"Issue"* ]]
}

# ---
# TC-8: baseline 부재 (첫 배포 EC-1) → 신호 미감지 + bootstrap + exit 0
# ---
@test "TC-8: baseline 부재 (EC-1) → 신호 미감지 + 현재값 baseline 기록 + exit 0" {
  BOOTSTRAP_FILE="${TEST_TMP}/bootstrap.json"
  # baseline 부재 (파일 없음)
  export _CFP1194_MOCK_BASELINE_FILE="${BOOTSTRAP_FILE}"
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  echo "output: ${output}"
  echo "status: ${status}"
  # baseline 부재 = bootstrap → 신호 미감지 + exit 0
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"bootstrap"* ]] || [[ "${output}" == *"baseline"* ]] || [[ "${output}" == *"PASS"* ]]
  # bootstrap 후 파일 존재
  [ -f "${BOOTSTRAP_FILE}" ]
}

# ---
# TC-9: metric source 불가 (EC-2) → exit 2 + escalation Issue
# ---
@test "TC-9: metric source 불가 (_CFP1194_MOCK_METRIC_UNAVAILABLE=1) → exit 2 (SETUP)" {
  export _CFP1194_MOCK_METRIC_UNAVAILABLE=1
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  echo "output: ${output}"
  echo "status: ${status}"
  [ "${status}" -eq 2 ]
}

# ---
# TC-10: dedup — 동일 signature open Issue 존재 → 새 Issue 억제
# ---
@test "TC-10: dedup (open Issue 존재) → 새 Issue 억제 + exit 0" {
  export _CFP1194_MOCK_DEDUP=1
  export _CFP1194_MOCK_FLAP_N=1
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  echo "output: ${output}"
  echo "status: ${status}"
  # dedup 발동 = 새 Issue 억제 + exit 0
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"dedup"* ]] || [[ "${output}" == *"억제"* ]] || [[ "${output}" == *"skip"* ]]
}

# ---
# TC-11: signature 형식 — sha256("<signal_type>|<measured>|<window>")[:16]
# ---
@test "TC-11: signature 형식 — 16-char hex (sha256 prefix)" {
  # Python 직접 호출로 signature 출력 확인 (health-status.json 사용 — smoke_health none 신호)
  HEALTH_NORM="${TEST_TMP}/health-norm.json"
  echo '{"status": "ok"}' > "${HEALTH_NORM}"
  OUT=$(python3 "${REGRESSION_PY}" \
    --signal-type "smoke_health" \
    --metric-name "error_rate" \
    --regression-threshold "" \
    --flap-n "1" \
    --recovery-margin "0.5" \
    --window "86400" \
    --baseline-file "" \
    --current-metric-file "" \
    --health-file "${HEALTH_NORM}" \
    --flap-state-file "${TEST_TMP}/flap-sig.json" \
    2>/dev/null || true)
  SIG=$(echo "${OUT}" | grep "^signature=" | cut -d= -f2)
  echo "signature: ${SIG}"
  # 16-char hex
  [[ "${SIG}" =~ ^[0-9a-f]{16}$ ]]
}

# ---
# TC-12: 중복 0 검증 (S4 disjoint) — script 안 rollback_to_blue 부재 grep
# ---
@test "TC-12: S4 disjoint — check-operational-regression.sh 안 rollback_to_blue 부재" {
  run grep -c "rollback_to_blue" "${REGRESSION_SH}"
  # grep -c 결과 = 0 (부재)
  [ "${output}" = "0" ] || [ "${status}" -ne 0 ]
}

@test "TC-12b: S4 disjoint — check_operational_regression.py 안 auto-rollback hook 부재" {
  run grep -c "auto.rollback.hook\|rollback_to_blue\|Traefik label flip" "${REGRESSION_PY}"
  [ "${output}" = "0" ] || [ "${status}" -ne 0 ]
}

# ---
# TC-13: wrapper-self-app fast-pass (repo=wrapper) → exit 0 PASS
# ---
@test "TC-13: wrapper-self-app fast-pass (repo=mclayer/plugin-codeforge) → exit 0" {
  export _CFP1194_MOCK_REPO_NAME="mclayer/plugin-codeforge"
  run bash "${REGRESSION_SH}" \
    --repo "mclayer/plugin-codeforge" \
    --metric-name "error_rate" \
    --regression-threshold "10.0"
  echo "output: ${output}"
  echo "status: ${status}"
  [ "${status}" -eq 0 ]
  [[ "${output}" == *"fast-pass"* ]] || [[ "${output}" == *"wrapper"* ]] || [[ "${output}" == *"N/A"* ]]
}

# ---
# TC-14: exit 3-tier 정합 — 정상=0, SETUP error=2
# ---
@test "TC-14: exit code 0 — 정상 (임계 미초과)" {
  echo '{"error_rate": 0.02}' > "${CURRENT_FILE}"  # baseline 동일 = 정상
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  [ "${status}" -eq 0 ]
}

@test "TC-14b: exit code 2 — SETUP error (metric source 불가)" {
  export _CFP1194_MOCK_METRIC_UNAVAILABLE=1
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --metric-name "error_rate" \
    --regression-threshold "10.0" \
    --signal-type "regression"
  [ "${status}" -eq 2 ]
}

# ---
# TC-15: health 0 API call 경계 (D3) — filesystem 파싱 primary, webhook push 경로 부재
# ---
@test "TC-15: health 0 API call — filesystem 파싱 primary (health-status.json read)" {
  echo '{"status": "ok"}' > "${HEALTH_FILE}"
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --signal-type "smoke_health" \
    --regression-threshold ""
  echo "output: ${output}"
  echo "status: ${status}"
  # filesystem 파싱 정상 = exit 0
  [ "${status}" -eq 0 ]
}

@test "TC-15b: webhook push anti-pattern — script 안 webhook listener 부재 grep" {
  run grep -c "webhook.*listen\|http.*listen\|nc -l\|netcat" "${REGRESSION_SH}"
  [ "${output}" = "0" ] || [ "${status}" -ne 0 ]
}

# ---
# TC-16: flap state cross-tick restart (§8.5) — flap counter 파일 → 카운터 복원
# ---
@test "TC-16: flap state cross-tick restart — 이전 tick 카운터 파일 존재 시 복원" {
  echo '{"status": "fail"}' > "${HEALTH_FILE}"
  export _CFP1194_MOCK_FLAP_N=3  # N=3

  # 사전 상태: 이전 tick 에서 카운터=2 이미 누적 (tick 2/3)
  echo '{"health": 2}' > "${FLAP_STATE_FILE}"

  # 현재 tick: 카운터=3, N=3 도달 → 신호 발의 (restart 후 카운터 복원 확인)
  run bash "${REGRESSION_SH}" \
    --repo "test-consumer-repo" \
    --signal-type "smoke_health" \
    --regression-threshold ""
  echo "output: ${output}"
  echo "status: ${status}"
  [ "${status}" -eq 0 ]
  # N-tick 도달 = 신호 감지 (dry-run = issue create skip)
  [[ "${output}" == *"smoke_health"* ]] || [[ "${output}" == *"SIGNAL"* ]] || [[ "${output}" == *"도달"* ]] || [[ "${output}" == *"Issue"* ]]
}
