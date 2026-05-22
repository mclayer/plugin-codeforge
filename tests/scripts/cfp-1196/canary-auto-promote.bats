#!/usr/bin/env bats
# tests/scripts/cfp-1196/canary-auto-promote.bats
# CFP-1196 TDD — canary-auto-promote.sh + canary_auto_promote.py
#
# Change Plan §8.1 Test Contract (24 TC — FIX iter1 수정):
#   TC-1:  UC-1 정상 promote — 4-tuple 전부 pass + 안전장치 4 AND 충족 → 전체 promote + Issue (완료)
#   TC-2:  pass + n_a 조합 → promote proceed + positive assertion (AC-3)
#   TC-3:  UC-2 criteria 미충족 — 1+ fail → abort + rollback + Issue (정지)
#   TC-4:  안전장치 2 미충족 — 보존 window 초과 → promote 금지 + hotfix 안내 (EC-7)
#   TC-5:  안전장치 4 — kill-switch filesystem flag 활성 → fast-skip (EC-4)
#   TC-5b: kill-switch config flag mock → fast-skip (OR disable §3.7)
#   TC-6:  UC-4 wrapper fast-pass — repo=wrapper → exit 0 PASS (AC-8)
#   TC-7:  중복 0 — atomic_swap / Traefik label flip grep 0 match (L1/L2 재구현 0, CX-1196-3)
#   TC-7b: 재사용 증명 — deploy_blue_green.py + auto-rollback-hook.sh 호출 흔적 ≥1 (positive)
#   TC-8:  dedup — 동일 signature open Issue 존재 → 새 Issue 억제 (EC-8)
#   TC-9:  D3 promote partial 실패 — 2번째 host swap fail → keep-forward + rollback + 정지 (EC-3)
#   TC-10: 안전장치 4 AND 진리표 — criteria 충족 BUT filesystem kill-switch → promote 0
#   TC-11: EC-2 canary 배포 실패 (전체 fail) — health fail → L2 rollback + 정지
#   TC-12: exit 3-tier — 정상=0 / SETUP error=2
#   TC-13: EC hook 부재 — deploy_blue_green.py 부재 → exit 2 + 자동 재시도 0 확인 (fixed: || true 제거)
#   TC-14: criteria 충족 BUT Python-derived config kill-switch (safety_4=false) → promote 0
#          (F-CR-1196-1 P1 수정 검증 — 실 project.yaml auto_promote_enabled:false 경로)
#   TC-15: 0 API call — criteria measurement path 안 network egress grep 0 match (filesystem-only)
#   TC-16: signature 형식 — sha256 기반 16-char hex
#   TC-17: canary-phase partial 실패 (F-1196-4) — subset=2, host[0] 성공 후 host[1] fail
#          → host[0] 도 rollback + 전체 정지 (host-indexed mock: _CFP1196_MOCK_CANARY_FAIL_IDX)
#   TC-18: backstop post-expiry (F-1196-2) — retention 만료 후 → promote 금지 + hotfix 안내
#   TC-19: safety_3 알림 unavailable — criteria pass + 보존 ok + kill-switch off BUT notification unavailable → promote 0

WROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
PROMOTE_SH="${WROOT}/scripts/canary-auto-promote.sh"
PROMOTE_PY="${WROOT}/scripts/canary_auto_promote.py"
DEPLOY_PY="${WROOT}/scripts/deploy_blue_green.py"
ROLLBACK_SH="${WROOT}/templates/deployment/auto-rollback-hook.sh"

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  # 기본 안전장치 4 AND 충족 상태 (promote 허용 기본값)
  export _CFP1196_MOCK_FUNCTIONAL="pass"
  export _CFP1196_MOCK_SECURITY="pass"
  export _CFP1196_MOCK_MONITORING="pass"
  export _CFP1196_MOCK_TESTING="pass"

  # 안전장치 2: 보존 window 내 (L2 hook 위임)
  export _CFP1059_MOCK_WITHIN_RETENTION=1

  # L2 deploy mock (docker/ssh/health — local 실행 허용)
  export _CFP1059_MOCK_DOCKER=1
  export _CFP1059_MOCK_SSH=1
  export _CFP1059_MOCK_HEALTH="pass"

  # 안전장치 4: kill-switch off (기본)
  export _CFP1196_MOCK_KILL_SWITCH=0
  export _CFP1196_MOCK_CONFIG_DISABLED=0

  # 안전장치 3: 알림 가용 (mock, 테스트 환경 GH_TOKEN 미설정 대응)
  export _CFP1196_MOCK_NOTIFICATION_AVAILABLE="true"

  # Issue 발의 차단 (테스트 모드)
  export _CFP1196_SKIP_ISSUE_CREATE=1
  export CBL_SKIP_ISSUE_CREATE=1

  # dedup off (기본 — open Issue 없음)
  export _CFP1196_MOCK_DEDUP=0

  # repo name (wrapper fast-pass 테스트용)
  export _CFP1196_MOCK_REPO_NAME="test-consumer-repo"

  # promote partial 실패 mock 초기화 (-1 = 없음)
  export _CFP1059_MOCK_SWAP_FAIL="-1"
}

teardown() {
  rm -rf "${TEST_TMP}"
  unset _CFP1196_MOCK_FUNCTIONAL _CFP1196_MOCK_SECURITY
  unset _CFP1196_MOCK_MONITORING _CFP1196_MOCK_TESTING
  unset _CFP1059_MOCK_WITHIN_RETENTION
  unset _CFP1059_MOCK_DOCKER _CFP1059_MOCK_SSH _CFP1059_MOCK_HEALTH
  unset _CFP1196_MOCK_KILL_SWITCH _CFP1196_MOCK_CONFIG_DISABLED
  unset _CFP1196_MOCK_NOTIFICATION_AVAILABLE
  unset _CFP1196_SKIP_ISSUE_CREATE CBL_SKIP_ISSUE_CREATE
  unset _CFP1196_MOCK_DEDUP _CFP1196_MOCK_REPO_NAME
  unset _CFP1196_MOCK_HOOK_MISSING
  unset _CFP1059_MOCK_SWAP_FAIL
  unset _CFP1196_MOCK_KILL_SWITCH_FLAG _CFP1196_MOCK_CONFIG_YAML_PATH
  unset _CFP1196_MOCK_CANARY_FAIL_IDX
}

# --- 파일 존재 확인 ---
@test "스크립트 파일 존재: canary-auto-promote.sh" {
  [ -f "${PROMOTE_SH}" ]
  [ -x "${PROMOTE_SH}" ]
}

@test "Python 파일 존재: canary_auto_promote.py (ADR-061)" {
  [ -f "${PROMOTE_PY}" ]
}

# ---
# TC-1: UC-1 정상 promote — 4-tuple 전부 pass + 안전장치 4 AND → 전체 promote + Issue (완료)
# ---
@test "TC-1: 4-tuple 전부 pass + 안전장치 4 AND → promote 완료 + exit 0" {
  export _CFP1196_MOCK_FUNCTIONAL="pass"
  export _CFP1196_MOCK_SECURITY="pass"
  export _CFP1196_MOCK_MONITORING="pass"
  export _CFP1196_MOCK_TESTING="pass"
  export _CFP1059_MOCK_WITHIN_RETENTION=1
  export _CFP1196_MOCK_NOTIFICATION_AVAILABLE="true"
  export _CFP1196_MOCK_KILL_SWITCH=0

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2,host3" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"promote 완료"* || "$output" == *"promote 성공"* ]] || \
    [[ "$output" == *"canary auto-promote"* ]]
}

# ---
# TC-2: pass + n_a 조합 → promote proceed (AC-3)
# ---
@test "TC-2: functional=pass, security=n_a, monitoring=n_a, testing=pass → promote proceed" {
  export _CFP1196_MOCK_FUNCTIONAL="pass"
  export _CFP1196_MOCK_SECURITY="n_a"
  export _CFP1196_MOCK_MONITORING="n_a"
  export _CFP1196_MOCK_TESTING="pass"

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  # positive assertion: promote 시작 출력 확인 (criteria 미충족 아님)
  [[ "$output" != *"criteria 미충족"* ]]
  [[ "$output" == *"전체 promote 시작"* ]] || [[ "$output" == *"promote 성공"* ]] || \
    [[ "$output" == *"canary auto-promote 완료"* ]]
}

# ---
# TC-3: UC-2 criteria 미충족 — 1+ fail → abort + rollback + Issue
# ---
@test "TC-3: security=fail → promote abort + canary rollback + 정지 출력" {
  export _CFP1196_MOCK_FUNCTIONAL="pass"
  export _CFP1196_MOCK_SECURITY="fail"
  export _CFP1196_MOCK_MONITORING="pass"
  export _CFP1196_MOCK_TESTING="pass"

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"criteria 미충족"* ]] || [[ "$output" == *"criteria_met=false"* ]]
}

# ---
# TC-4: 안전장치 2 미충족 — 보존 window 초과 → promote 금지 + hotfix 안내 (EC-7)
# ---
@test "TC-4: 보존 window 만료 → promote 금지 + hotfix 안내" {
  export _CFP1059_MOCK_WITHIN_RETENTION=0

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"보존 window 만료"* ]] || [[ "$output" == *"retention"* ]]
}

# ---
# TC-5: 안전장치 4 — kill-switch filesystem flag 활성 → fast-skip (EC-4)
# ---
@test "TC-5: kill-switch filesystem flag 활성 → fast-skip (수동 통제 복귀)" {
  export _CFP1196_MOCK_KILL_SWITCH=1

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"kill-switch"* ]]
}

# ---
# TC-5b: kill-switch config flag → fast-skip (OR disable §3.7)
# ---
@test "TC-5b: kill-switch config flag → fast-skip (OR disable)" {
  export _CFP1196_MOCK_KILL_SWITCH=0
  export _CFP1196_MOCK_CONFIG_DISABLED=1

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"kill-switch"* ]]
}

# ---
# TC-6: UC-4 wrapper fast-pass — repo=wrapper → exit 0 PASS (AC-8)
# ---
@test "TC-6: wrapper repo → Tier-1 fast-pass exit 0 (§3.8)" {
  export _CFP1196_MOCK_REPO_NAME="plugin-codeforge"

  run bash "${PROMOTE_SH}" \
    --repo "mclayer/plugin-codeforge" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"wrapper-self-app fast-pass"* ]] || \
    [[ "$output" == *"N/A"* ]]
}

# ---
# TC-7: 중복 0 (negative) — atomic_swap / Traefik label flip 재구현 grep 0 match (CX-1196-3)
# ---
@test "TC-7: L1/L2 재구현 0 — atomic_swap / Traefik grep 0 match (AC-6)" {
  # canary-auto-promote.sh 안에 L2 swap 로직 재정의 없음 확인
  run grep -n "atomic_swap\|traefik.*label.*flip\|docker.*label.*traefik" \
    "${WROOT}/scripts/canary-auto-promote.sh"
  [ "$status" -ne 0 ]  # grep 0 match = exit 1

  # canary_auto_promote.py 안 동일 확인
  run grep -n "atomic_swap\|traefik.*label.*flip" \
    "${WROOT}/scripts/canary_auto_promote.py"
  [ "$status" -ne 0 ]
}

# ---
# TC-7b: 재사용 증명 (positive) — L2 hook + L1 helper 호출 흔적 ≥1 (AC-6)
# ---
@test "TC-7b: 재사용 증명 — deploy_blue_green.py + auto-rollback-hook.sh 호출 흔적 존재 (positive)" {
  # canary-auto-promote.sh 가 L2 deploy_blue_green.py 호출
  run grep -n "deploy_blue_green.py" "${WROOT}/scripts/canary-auto-promote.sh"
  [ "$status" -eq 0 ]
  [ "${#lines[@]}" -ge 1 ]

  # canary-auto-promote.sh 가 L2 auto-rollback-hook.sh 호출
  run grep -n "auto-rollback-hook.sh" "${WROOT}/scripts/canary-auto-promote.sh"
  [ "$status" -eq 0 ]
  [ "${#lines[@]}" -ge 1 ]
}

# ---
# TC-8: dedup — 동일 signature open Issue 존재 → 새 Issue 억제 (EC-8)
# ---
@test "TC-8: dedup — open Issue 존재 시 새 Issue 억제 출력" {
  export _CFP1196_MOCK_DEDUP=1

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"dedup"* ]]
}

# ---
# TC-9: D3 promote partial 실패 — 2번째 host swap fail → keep-forward + rollback + 정지 (EC-3)
# ---
@test "TC-9: promote partial 실패 D3 — 1번째 host keep-forward, 2번째 rollback + 정지" {
  # promote 시 0번째(index 0) = 첫 번째 나머지 host 성공, 1번째(index 1) = 실패
  export _CFP1059_MOCK_SWAP_FAIL="1"

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2,host3" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  # D3 정책 메시지 확인
  [[ "$output" == *"keep-forward"* ]] || \
    [[ "$output" == *"partial"* ]] || \
    [[ "$output" == *"promote 실패"* ]]
}

# ---
# TC-10: 안전장치 4 AND 진리표 — criteria 충족 BUT kill-switch 활성 → promote 0
# ---
@test "TC-10: criteria 충족 + kill-switch 활성 → AND false → promote 0 (kill-switch 우선)" {
  export _CFP1196_MOCK_FUNCTIONAL="pass"
  export _CFP1196_MOCK_SECURITY="pass"
  export _CFP1196_MOCK_MONITORING="pass"
  export _CFP1196_MOCK_TESTING="pass"
  export _CFP1196_MOCK_KILL_SWITCH=1  # kill-switch 활성

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"kill-switch"* ]]
  # 전체 promote 없음 확인
  [[ "$output" != *"전체 promote 시작"* ]]
}

# ---
# TC-11: EC-2 canary 배포 실패 (F-1196-4) — health fail → rollback + promote 미진입
# ---
@test "TC-11: canary 배포 health fail → L2 rollback + promote 미진입 + 정지 출력" {
  export _CFP1059_MOCK_HEALTH="fail"

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  [[ "$output" == *"canary 배포 실패"* ]] || \
    [[ "$output" == *"canary-phase"* ]] || \
    [[ "$output" == *"promote 미진입"* ]]
}

# ---
# TC-12: exit 3-tier — 정상=0 / SETUP error=2
# ---
@test "TC-12: 정상 종료 = exit 0" {
  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
}

@test "TC-12b: SETUP error (hook 부재) = exit 2" {
  export _CFP1196_MOCK_HOOK_MISSING=1

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 2 ]
}

# ---
# TC-13: EC hook 부재 — exit 2 + 자동 재시도 0
# ---
@test "TC-13: deploy_blue_green.py 부재 → exit 2 + 자동 재시도 0 (ADR-057)" {
  export _CFP1196_MOCK_HOOK_MISSING=1

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 2 ]
  [[ "$output" == *"부재"* ]] || [[ "$output" == *"SETUP error"* ]]
  # 자동 재시도 흔적 없음 (ADR-057)
  [[ "$output" != *"retry"* ]]
  [[ "$output" != *"재시도"* ]]
}

# ---
# TC-14: criteria 충족 BUT Python-derived config kill-switch (safety_4=false) → promote 0
#        (F-CR-1196-1 P1 수정 검증 — 실 project.yaml auto_promote_enabled:false 경로)
# ---
@test "TC-14: criteria 충족 BUT config kill-switch(Python-derived safety_4=false) → promote 0" {
  # 실 disabled yaml 파일 생성 (--config-yaml-path 경유 Python 평가)
  DISABLED_YAML="${TEST_TMP}/project_disabled.yaml"
  cat > "${DISABLED_YAML}" <<'YAML'
deploy:
  canary:
    auto_promote_enabled: false
YAML

  export _CFP1196_MOCK_FUNCTIONAL="pass"
  export _CFP1196_MOCK_SECURITY="pass"
  export _CFP1196_MOCK_MONITORING="pass"
  export _CFP1196_MOCK_TESTING="pass"
  export _CFP1196_MOCK_KILL_SWITCH=0      # filesystem flag OFF
  export _CFP1196_MOCK_CONFIG_DISABLED=0  # bash mock OFF — Python 실 평가 경로
  export _CFP1196_MOCK_CONFIG_YAML_PATH="${DISABLED_YAML}"

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  # Python-derived safety_4=false → Step 9b 게이트 발동
  [[ "$output" == *"config kill-switch"* ]] || \
    [[ "$output" == *"safety_4"* ]] || \
    [[ "$output" == *"auto_promote_enabled"* ]]
  # promote 미진입 확인
  [[ "$output" != *"전체 promote 시작"* ]]
}

# ---
# TC-15: 0 API call — criteria measurement code path 안 network egress grep 0 match
# ---
@test "TC-15: 0 API call — canary_auto_promote.py measurement path 안 network call grep 0 match" {
  # Python measurement 함수 안 network egress 없음 (filesystem-only, ADR-104 §결정 3, CX-1196-4)
  # grep 대상: canary_auto_promote.py 의 check_safety_1/check_safety_3/check_safety_4 함수
  # action-layer 분리: gh issue 발의(사후 알림) = measurement path 외 (promote 결정 후)
  run grep -n "requests\.\|urllib\.request\|httpx\.\|prometheus_api_client\|socket\.connect\|http\.client" \
    "${WROOT}/scripts/canary_auto_promote.py"
  [ "$status" -ne 0 ]  # grep 0 match = network 호출 없음

  # bash measurement path (canary-auto-promote.sh criteria 집계 경로)도 동일 확인
  run grep -n "curl.*criteria\|wget.*criteria\|gh api.*criteria" \
    "${WROOT}/scripts/canary-auto-promote.sh"
  [ "$status" -ne 0 ]
}

# ---
# TC-16: signature 형식 — sha256 기반 16-char hex
# ---
@test "TC-16: canary_auto_promote.py signature 출력 = 16-char hex" {
  run python3 "${PROMOTE_PY}" \
    --functional "pass" \
    --security "pass" \
    --monitoring "n_a" \
    --testing "pass" \
    --window "10800" \
    --mock-notification-available "true"

  [ "$status" -eq 0 ]

  # signature= 라인 추출
  SIG=$(echo "$output" | grep "^signature=" | cut -d= -f2)
  [ -n "${SIG}" ]
  # 16-char hex 검증
  [[ "${#SIG}" -eq 16 ]]
  [[ "${SIG}" =~ ^[0-9a-f]{16}$ ]]
}

# ---
# TC-17: canary-phase partial 실패 (F-1196-4) — subset=2, host[0]=pass, host[1]=fail → host[0] 도 rollback
# ---
@test "TC-17: canary subset=2, host[0] 성공 후 host[1] health fail → host[0] 도 rollback + 전체 정지" {
  # host-indexed: index 0(host1) = 전역 pass, index 1(host2) = force fail (_CFP1196_MOCK_CANARY_FAIL_IDX)
  export _CFP1059_MOCK_HEALTH="pass"          # 전역 기본 = pass
  export _CFP1196_MOCK_CANARY_FAIL_IDX="1"    # canary index 1 = host2 force fail (host[0] 먼저 성공)

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2,host3" \
    --canary-subset "host1,host2"

  [ "$status" -eq 0 ]
  # host1 배포 성공 후 host2 실패 → F-1196-4 전체 rollback (host1 포함)
  [[ "$output" == *"canary 배포 실패"* ]] || [[ "$output" == *"canary-phase"* ]]
  # host1 도 rollback (측정 기준선 일관성)
  [[ "$output" == *"canary 성공 host rollback"* ]] || [[ "$output" == *"rolled_back_canary"* ]] || \
    [[ "$output" == *"canary-phase 실패 처리 완료"* ]]
  # promote 미진입
  [[ "$output" != *"전체 promote 시작"* ]]
}

# ---
# TC-18: backstop post-expiry (F-1196-2) — retention 만료 후 도착 → promote 금지 + hotfix 안내
# ---
@test "TC-18: backstop cron이 retention 만료 후 도착 → promote 금지 + hotfix 안내 (EC-7)" {
  export _CFP1059_MOCK_WITHIN_RETENTION=0  # retention 만료

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  # backstop 정책 메시지 확인
  [[ "$output" == *"보존 window 만료"* ]] || [[ "$output" == *"retention"* ]]
  # in-window promote 미보장 정정 메시지
  [[ "$output" == *"backstop"* ]] || [[ "$output" == *"hotfix"* ]] || \
    [[ "$output" == *"만료"* ]]
}

# ---
# TC-19: safety_3 알림 unavailable — criteria pass + 보존 ok + kill-switch off BUT notification unavailable → promote 0
# ---
@test "TC-19: notification unavailable → promote 금지 (무음 promote 차단, F-1196-3)" {
  export _CFP1196_MOCK_FUNCTIONAL="pass"
  export _CFP1196_MOCK_SECURITY="pass"
  export _CFP1196_MOCK_MONITORING="pass"
  export _CFP1196_MOCK_TESTING="pass"
  export _CFP1059_MOCK_WITHIN_RETENTION=1
  export _CFP1196_MOCK_KILL_SWITCH=0
  export _CFP1196_MOCK_NOTIFICATION_AVAILABLE="false"  # 알림 불가

  run bash "${PROMOTE_SH}" \
    --repo "test-consumer-repo" \
    --image "myapp:v2" \
    --host-list "host1,host2" \
    --canary-subset "host1"

  [ "$status" -eq 0 ]
  # 알림 unavailable → promote 금지 출력
  [[ "$output" == *"알림 mechanism 미가용"* ]] || \
    [[ "$output" == *"safety_3"* ]] || \
    [[ "$output" == *"무음 promote 차단"* ]] || \
    [[ "$output" == *"notification"* ]]
  # 전체 promote 없음 확인
  [[ "$output" != *"전체 promote 시작"* ]]
}
