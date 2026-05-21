#!/usr/bin/env bash
# scripts/check-rollback-signal.sh
# CFP-1193 — rollback signal monitor (thin bash orchestration)
#
# ADR-106 Amendment 1 단계 2-a: 자동 rollback 직후 사후 알림 Issue (안전장치 3 동반)
# ADR-105 §결정 3: 안전장치 4 AND (1:숫자임계 / 2:보존기간 / 3:사후알림 / 4:kill-switch)
# ADR-104 §결정 3: 0 API call (filesystem / cron 우선)
# ADR-061: burn rate 산술 = Python 위임, dedup orchestration = bash (본 파일)
#
# 답습 source: check-channel-drift.sh (CFP-932) — signature dedup / exit 3-tier / test-override env
#
# 호출 흐름:
#   rollback-signal-monitor.yml (24h cron)
#     └─ 본 스크립트
#          ├─ wrapper fast-pass 체크 (repo=wrapper → exit 0)
#          ├─ kill-switch 체크 (filesystem flag / config flag)
#          ├─ python3 check_rollback_signal.py (임계 비교 + 안전장치 평가 + signature)
#          ├─ 안전장치 2 (보존기간) 체크 — hook 위임 (_CFP1059_MOCK_WITHIN_RETENTION)
#          ├─ [signal_detected=true + 4 AND] → 기존 hook trigger
#          │     bash templates/deployment/auto-rollback-hook.sh --repo <r> --host <h>
#          ├─ signature dedup (gh issue list --search "signature: ${SIG}")
#          └─ ops-signal Issue 발의 (open Issue 부재 시) + exit 0
#
# Test override env (_CFP1193_MOCK_* namespace, CFP-1059 _CFP1059_MOCK_* verbatim):
#   _CFP1193_MOCK_ERROR_RATE=<float>           — 에러율 override
#   _CFP1193_MOCK_ERROR_RATE_THRESHOLD=<float> — 임계 override
#   _CFP1193_MOCK_BURN_RATE=<float>            — burn rate override
#   _CFP1193_MOCK_BURN_RATE_THRESHOLD=<float>  — burn rate 임계 override
#   _CFP1193_MOCK_WINDOW=<int>                 — window (초) override
#   _CFP1193_MOCK_SIGNAL_TYPE=<str>            — signal type hint
#   _CFP1193_MOCK_KILL_SWITCH=<0|1>            — kill-switch 활성 override (1=활성)
#   _CFP1193_MOCK_KILL_SWITCH_FLAG=<path>      — kill-switch flag 경로 override
#   _CFP1193_MOCK_CONFIG_DISABLED=<0|1>        — config disabled override
#   _CFP1193_MOCK_DEDUP=<0|1>                  — open Issue 존재 mock (1=dedup 발동)
#   _CFP1193_MOCK_REPO_NAME=<str>              — repo 이름 override
#   _CFP1193_MOCK_HOOK_MISSING=<0|1>           — hook 부재 mock (1=부재, exit 2)
#   _CFP1193_SKIP_ISSUE_CREATE=<1>             — Issue 발의 차단 (dry-run)
#   _CFP1059_MOCK_WITHIN_RETENTION=<0|1>       — 보존 기간 mock (1=window 내)
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (정상 또는 임계 감지 + Issue 발의 성공)
#   1 = reserved (current scope 미사용)
#   2 = SETUP error (의존성 부재 / hook 부재 / yaml parse error)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SIGNAL_PY="${WORKTREE_ROOT}/scripts/check_rollback_signal.py"
ROLLBACK_SH="${WORKTREE_ROOT}/templates/deployment/auto-rollback-hook.sh"

# --- 인수 파싱 ---
REPO=""
HOST=""

usage() {
  cat <<'EOF'
Usage: check-rollback-signal.sh --repo <repo> --host <host>

Options:
  --repo <repo>   대상 repo (wrapper fast-pass 체크 기준)
  --host <host>   대상 host
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --host) HOST="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${REPO}" || -z "${HOST}" ]]; then
  echo "[ERROR] --repo, --host 필수" >&2
  exit 1
fi

# --- 신호 값 수집 (test override env 우선) ---
ERROR_RATE="${_CFP1193_MOCK_ERROR_RATE:-0.0}"
ERROR_RATE_THRESHOLD="${_CFP1193_MOCK_ERROR_RATE_THRESHOLD:-}"
BURN_RATE="${_CFP1193_MOCK_BURN_RATE:-0.0}"
BURN_RATE_THRESHOLD="${_CFP1193_MOCK_BURN_RATE_THRESHOLD:-}"
WINDOW="${_CFP1193_MOCK_WINDOW:-3600}"

# --- kill-switch 경로 결정 ---
KILL_SWITCH_FLAG="${_CFP1193_MOCK_KILL_SWITCH_FLAG:-${WORKTREE_ROOT}/.codeforge/auto-rollback.disabled}"

# config kill-switch: test mock override OR real yaml path
# F-CR-1193-2: real consumer 환경 = project.yaml yaml.safe_load (ADR-070 grep 금지)
CONFIG_DISABLED="false"
if [[ "${_CFP1193_MOCK_CONFIG_DISABLED:-0}" == "1" ]]; then
  # test mock: --config-disabled=true 직접 전달
  CONFIG_DISABLED="true"
fi

# real config yaml path (consumer 환경 기본 위치)
# test mock 미활성 시 yaml.safe_load 경로 주입 (Python 에서 처리)
CONFIG_YAML_PATH="${_CFP1193_MOCK_CONFIG_YAML_PATH:-${WORKTREE_ROOT}/.claude/_overlay/project.yaml}"

# --- Step 1: wrapper-self-app fast-pass (ADR-104 §결정 4 / §3.6 Tier-1) ---
# wrapper repo = declare SSOT only, 실 monitoring 무의미
REPO_NAME="${_CFP1193_MOCK_REPO_NAME:-${REPO}}"
case "${REPO_NAME}" in
  plugin-codeforge|mclayer/plugin-codeforge)
    echo "[INFO] wrapper-self-app fast-pass: repo=${REPO_NAME} — N/A (ADR-104 §결정 4)"
    echo "[INFO] wrapper repo = declarative SSOT only. 실 monitoring = consumer 영역."
    exit 0
    ;;
esac

# --- Step 2: kill-switch 체크 (가장 먼저 — §3.3 kill-switch 우선, EC-2) ---
KILL_SWITCH_ACTIVE=0

# filesystem flag (primary, 0 API call)
if [[ -f "${KILL_SWITCH_FLAG}" ]]; then
  KILL_SWITCH_ACTIVE=1
fi

# kill-switch mock override (test env)
if [[ "${_CFP1193_MOCK_KILL_SWITCH:-0}" == "1" ]]; then
  KILL_SWITCH_ACTIVE=1
fi

# config flag disabled (secondary)
if [[ "${CONFIG_DISABLED}" == "true" ]]; then
  KILL_SWITCH_ACTIVE=1
fi

if [[ "${KILL_SWITCH_ACTIVE}" == "1" ]]; then
  echo "[INFO] kill-switch 활성 — rollback trigger 무력화 (§3.4 OR disable, EC-2)"
  echo "[INFO] kill_switch_active=true: 신호 감지·기록 계속 (rollback trigger 만 무력화)"
  # 신호 감지·기록은 계속 (EC-2 — 무음 비활성 차단)
  # Issue 발의는 아래에서 계속 (kill-switch 이후 신호 체크 → 감지 기록용 Issue)
fi

# --- Step 3: Python 스크립트 존재 확인 (SETUP guard) ---
if [[ ! -f "${SIGNAL_PY}" ]]; then
  echo "[ERROR] check_rollback_signal.py 부재 — ADR-061 Python 파일 필요" >&2
  exit 2
fi

# --- Step 4: 임계 감지 + 안전장치 평가 (Python 위임) ---
PYTHON_OUT=""
if ! PYTHON_OUT=$(PYTHONUTF8=1 python3 "${SIGNAL_PY}" \
    --error-rate "${ERROR_RATE}" \
    --error-rate-threshold "${ERROR_RATE_THRESHOLD}" \
    --burn-rate "${BURN_RATE}" \
    --burn-rate-threshold "${BURN_RATE_THRESHOLD}" \
    --window "${WINDOW}" \
    --kill-switch-flag "${KILL_SWITCH_FLAG}" \
    --config-disabled "${CONFIG_DISABLED}" \
    --config-yaml-path "${CONFIG_YAML_PATH}" \
    2>&1); then
  echo "[ERROR] check_rollback_signal.py 실행 실패" >&2
  echo "${PYTHON_OUT}" >&2
  exit 2
fi

# Python 출력 파싱
SIGNAL_DETECTED=$(echo "${PYTHON_OUT}" | grep "^signal_detected=" | cut -d= -f2)
SIGNAL_TYPE=$(echo "${PYTHON_OUT}" | grep "^signal_type=" | cut -d= -f2)
MEASURED=$(echo "${PYTHON_OUT}" | grep "^measured=" | cut -d= -f2)
THRESHOLD=$(echo "${PYTHON_OUT}" | grep "^threshold=" | cut -d= -f2)
WINDOW_OUT=$(echo "${PYTHON_OUT}" | grep "^window=" | cut -d= -f2)
SAFETY_1=$(echo "${PYTHON_OUT}" | grep "^safety_1=" | cut -d= -f2)
SAFETY_4=$(echo "${PYTHON_OUT}" | grep "^safety_4=" | cut -d= -f2)
SIGNATURE=$(echo "${PYTHON_OUT}" | grep "^signature=" | cut -d= -f2)
PY_KILL_SWITCH=$(echo "${PYTHON_OUT}" | grep "^kill_switch_active=" | cut -d= -f2)

# Python 이 yaml.safe_load 로 config kill-switch 감지한 결과 반영 (F-CR-1193-2)
# Python 이 kill_switch_active=true 출력 시 bash KILL_SWITCH_ACTIVE 동기화
if [[ "${PY_KILL_SWITCH}" == "true" ]]; then
  KILL_SWITCH_ACTIVE=1
fi

echo "[INFO] 임계 감지: signal_detected=${SIGNAL_DETECTED} signal_type=${SIGNAL_TYPE}"
echo "[INFO] 측정값: measured=${MEASURED} threshold=${THRESHOLD} window=${WINDOW_OUT}s"
echo "[INFO] 안전장치: safety_1=${SAFETY_1} safety_4=${SAFETY_4}"

# 임계 미초과 (정상 범위)
if [[ "${SIGNAL_DETECTED}" != "true" ]]; then
  echo "[PASS] 신호 미감지 — 임계 미초과 (정상 범위)"
  exit 0
fi

# safety_1 미충족 (임계 미정의)
if [[ "${SAFETY_1}" != "true" ]]; then
  echo "[INFO] 안전장치 1 미충족 — auto 진입 0. user-decision layer 복귀 (EC-1)"
  exit 0
fi

# [SIGNAL] 감지
echo "[SIGNAL] 임계 초과 감지: signal_type=${SIGNAL_TYPE} measured=${MEASURED} threshold=${THRESHOLD}"

# --- Step 5: kill-switch 활성 시 trigger 미발동 (신호 기록용 Issue만) ---
if [[ "${KILL_SWITCH_ACTIVE}" == "1" ]]; then
  echo "[INFO] kill-switch 활성 — rollback 미발동. 감지 Issue 발의 (EC-2 감사 추적)"
  # Issue 발의로 이동 (trigger skip)
  # fall-through to Issue creation below
fi

# --- Step 6: 안전장치 2 (보존 기간) 체크 — 기존 hook 위임 ---
# hook 이 check_within_retention 평가. mock: _CFP1059_MOCK_WITHIN_RETENTION
WITHIN_RETENTION="${_CFP1059_MOCK_WITHIN_RETENTION:-0}"

if [[ "${KILL_SWITCH_ACTIVE}" != "1" ]]; then
  # kill-switch 미활성 시에만 hook trigger 시도
  if [[ "${WITHIN_RETENTION}" == "0" ]]; then
    # 보존 기간 초과 = hotfix 흐름 안내 (EC-3)
    echo "[WARN] 3시간 보존 window 만료 — 자동 rollback 영역 외 (hotfix 흐름 필요, EC-3)"
    echo "[INFO] hotfix: blue-green rollback 기간 초과. 수동 핫픽스 필요."
    echo "[empirical-source: ADR-087 §결정 5 — 3시간 보존 window, dimension: lifecycle]"
    # hotfix 안내 Issue 발의 (아래 Issue section)
    SIGNAL_TYPE="retention_expired"
    # fall-through to Issue creation
  else
    # --- Step 7: 기존 hook trigger (안전장치 4 AND 충족) ---
    # EC-4: hook 부재 체크
    if [[ "${_CFP1193_MOCK_HOOK_MISSING:-0}" == "1" ]] || [[ ! -f "${ROLLBACK_SH}" ]]; then
      echo "[ERROR] auto-rollback-hook.sh 부재 — EC-4 SETUP error (ADR-057 자동 재시도 0)" >&2
      # escalation Issue 발의 (Issue create skip 미적용)
      if [[ "${_CFP1193_SKIP_ISSUE_CREATE:-0}" != "1" ]]; then
        gh issue create \
          --repo "${REPO}" \
          --label "ops-signal" \
          --title "[OPS-SIGNAL] auto-rollback hook 부재 — EC-4 SETUP error" \
          --body "check-rollback-signal.sh: auto-rollback-hook.sh 부재.

EC-4: SETUP error (ADR-057 자동 재시도 0 — 의존성 복구 후 재실행 필요)

repo: ${REPO}
signal_type: ${SIGNAL_TYPE}
measured: ${MEASURED}
signature: ${SIGNATURE}

[CFP-1193] ops-signal label (ADR-106 §결정 1 단계 2-a)" \
          2>/dev/null || true
      fi
      exit 2
    fi

    echo "[INFO] 기존 hook trigger: auto-rollback-hook.sh --repo ${REPO} --host ${HOST}"
    bash "${ROLLBACK_SH}" --repo "${REPO}" --host "${HOST}"
    echo "[INFO] auto-rollback 실행 완료 — 사후 알림 Issue 발의 (안전장치 3)"
  fi
fi

# --- Step 8: signature dedup (Issue-level dedup, 단계 2-a) ---
# (check-channel-drift.sh §3 signature dedup 답습)
DEDUP_FOUND=0

if [[ "${_CFP1193_MOCK_DEDUP:-0}" == "1" ]]; then
  # dedup mock: open Issue 존재
  DEDUP_FOUND=1
elif [[ "${_CFP1193_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
  # 실 환경: gh issue list --search "signature: ${SIGNATURE}"
  EXISTING=$(gh issue list \
    --repo "${REPO}" \
    --search "\"signature: ${SIGNATURE}\"" \
    --state open \
    --json number \
    --limit 5 2>/dev/null || echo "[]")
  if [[ "${EXISTING}" != "[]" && "${EXISTING}" != "" ]]; then
    DEDUP_FOUND=1
  fi
fi

if [[ "${DEDUP_FOUND}" == "1" ]]; then
  echo "[INFO] dedup: 동일 signature open Issue 존재 — 새 Issue 억제 (EC-5, skip)"
  exit 0
fi

# --- Step 9: ops-signal Issue 발의 (사후 알림, 안전장치 3 / ADR-106 §결정 1 단계 2-a) ---
KILL_SWITCH_NOTE=""
if [[ "${KILL_SWITCH_ACTIVE}" == "1" ]]; then
  KILL_SWITCH_NOTE="
** kill-switch 활성 — rollback 미발동 (감지·기록만). 수동 조치 필요."
fi

ISSUE_BODY="rollback signal monitor 감지 결과.

signal_type: ${SIGNAL_TYPE}
measured: ${MEASURED}
threshold: ${THRESHOLD}
window: ${WINDOW}s
signature: ${SIGNATURE}

안전장치 4 AND 평가:
  safety_1 (숫자 임계): ${SAFETY_1}
  safety_4 (kill-switch off): $([ "${KILL_SWITCH_ACTIVE}" == "0" ] && echo true || echo false)
${KILL_SWITCH_NOTE}

[empirical-source: ADR-087 §결정 5 — 3시간 보존 window / channel-drift-detection.yml 24h cron 답습]
[CFP-1193] ops-signal label (ADR-106 §결정 1 단계 2-a)"

ISSUE_TITLE="[OPS-SIGNAL] rollback signal 감지: ${SIGNAL_TYPE} (${MEASURED} ≥ ${THRESHOLD})"

if [[ "${_CFP1193_SKIP_ISSUE_CREATE:-0}" == "1" ]]; then
  echo "[INFO] Issue 발의 차단 (dry-run: _CFP1193_SKIP_ISSUE_CREATE=1)"
  echo "[INFO] Issue body preview: ${ISSUE_TITLE}"
else
  if command -v gh >/dev/null 2>&1; then
    gh issue create \
      --repo "${REPO}" \
      --label "ops-signal" \
      --title "${ISSUE_TITLE}" \
      --body "${ISSUE_BODY}" \
      2>/dev/null || {
        echo "[WARN] Issue 발의 실패 (gh CLI 에러 — 감지는 기록됨)" >&2
      }
  else
    echo "[WARN] gh CLI 미설치 — Issue 발의 불가 (EC-4 준용)" >&2
  fi
fi

echo "[INFO] rollback signal monitor 완료: signal=${SIGNAL_TYPE} sig=${SIGNATURE}"
exit 0
