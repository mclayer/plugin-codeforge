#!/usr/bin/env bash
# scripts/check-operational-regression.sh
# CFP-1194 — regression/smoke·health monitor (thin bash orchestration)
#
# ADR-106 Amendment 2 단계 2-a: monitor-originated regression/health detection notification
#   (ops-signal label Issue 발의 — rollback 비동반, S5 ∉ rollback 영역)
# ADR-104 §결정 3: 0 API call (filesystem primary)
# ADR-104 §결정 4: wrapper-self-app N/A (Tier-1 declare-time exemption)
# ADR-061: regression %비교 + flap 카운터 = Python 위임 (본 파일 = orchestration 전용)
# ADR-064: 모달 어휘 금지 (regression 임계 = 숫자 정량 강제)
#
# 답습 source: check-rollback-signal.sh (CFP-1193 S4) — 구조 verbatim
#   호출 흐름 동형 (wrapper fast-pass → Python 위임 → signature dedup → Issue 발의)
#
# 호출 흐름:
#   regression-smoke-health-monitor.yml (24h cron)
#     └─ 본 스크립트
#          ├─ wrapper fast-pass 체크 (repo=wrapper → exit 0, §3.6 Tier-1)
#          ├─ python3 check_operational_regression.py (regression % 비교 + health FAIL + flap + signature)
#          │     ← stdout: signal_detected / signal_type / measured / baseline / threshold / window
#          │                flap_suppressed / signature
#          ├─ [signal_detected=true AND flap_suppressed=false] → signature dedup
#          │     gh issue list --search "signature: ${SIG}"
#          └─ ops-signal Issue 발의 (open Issue 부재 시) + exit 0
#
# Test override env (_CFP1194_MOCK_* namespace, S4 _CFP1193_MOCK_* 답습):
#   _CFP1194_MOCK_REPO_NAME=<str>            — repo 이름 override (wrapper fast-pass 테스트)
#   _CFP1194_MOCK_BASELINE_FILE=<path>       — baseline JSON 파일 override
#   _CFP1194_MOCK_CURRENT_METRIC_FILE=<path> — 현재 metric JSON 파일 override
#   _CFP1194_MOCK_HEALTH_FILE=<path>         — health-status JSON 파일 override
#   _CFP1194_MOCK_FLAP_STATE_FILE=<path>     — flap state JSON 파일 override
#   _CFP1194_MOCK_METRIC_UNAVAILABLE=1       — metric source 불가 시뮬레이션 (exit 2)
#   _CFP1194_MOCK_DEDUP=<0|1>               — open Issue 존재 mock (1=dedup 발동)
#   _CFP1194_MOCK_FLAP_N=<int>              — N-tick 임계 override
#   _CFP1194_MOCK_RECOVERY_MARGIN=<float>   — hysteresis recovery margin override
#   _CFP1194_SKIP_ISSUE_CREATE=<1>          — Issue 발의 차단 (dry-run)
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (정상 / 신호 감지 + Issue 발의 성공 / flap 억제 / wrapper fast-pass / dedup)
#   1 = reserved (current scope 미사용)
#   2 = SETUP error (의존성 부재 / metric source 불가 / parse 오류)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REGRESSION_PY="${WORKTREE_ROOT}/scripts/check_operational_regression.py"

# --- 인수 파싱 ---
REPO=""
METRIC_NAME="error_rate"
REGRESSION_THRESHOLD=""
SIGNAL_TYPE="auto"
FLAP_N="${_CFP1194_MOCK_FLAP_N:-2}"
RECOVERY_MARGIN="${_CFP1194_MOCK_RECOVERY_MARGIN:-0.5}"
WINDOW="86400"

# 기본 파일 경로 (consumer 환경 기본 위치)
BASELINE_FILE="${WORKTREE_ROOT}/.codeforge/operational-baseline.json"
CURRENT_METRIC_FILE="${WORKTREE_ROOT}/.codeforge/current-metric.json"
HEALTH_FILE="${WORKTREE_ROOT}/.codeforge/health-status.json"
FLAP_STATE_FILE="${WORKTREE_ROOT}/.codeforge/operational-flap-state.json"

usage() {
  cat <<'EOF'
Usage: check-operational-regression.sh --repo <repo> [options]

Options:
  --repo <repo>                대상 repo (wrapper fast-pass 체크 기준)
  --metric-name <name>         regression 측정 metric 이름 (default: error_rate)
  --regression-threshold <pct> regression 임계 % (빈 문자열 = 미정의 → 신호 0)
  --signal-type <type>         신호 유형: auto|regression|smoke_health (default: auto)
  --window <sec>               측정 window 초 (default: 86400)
  --baseline-file <path>       baseline JSON 파일 경로
  --current-metric-file <path> 현재 metric JSON 파일 경로
  --health-file <path>         health-status JSON 파일 경로
  --flap-state-file <path>     flap state JSON 파일 경로
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --metric-name) METRIC_NAME="$2"; shift 2 ;;
    --regression-threshold) REGRESSION_THRESHOLD="$2"; shift 2 ;;
    --signal-type) SIGNAL_TYPE="$2"; shift 2 ;;
    --window) WINDOW="$2"; shift 2 ;;
    --baseline-file) BASELINE_FILE="$2"; shift 2 ;;
    --current-metric-file) CURRENT_METRIC_FILE="$2"; shift 2 ;;
    --health-file) HEALTH_FILE="$2"; shift 2 ;;
    --flap-state-file) FLAP_STATE_FILE="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${REPO}" ]]; then
  echo "[ERROR] --repo 필수" >&2
  exit 1
fi

# --- Step 1: wrapper-self-app fast-pass (§3.6 Tier-1 declare-time exemption) ---
# wrapper repo = declarative SSOT only. 실 monitoring = consumer 환경.
# ADR-104 §결정 4 + ADR-072 Tier-1
REPO_NAME="${_CFP1194_MOCK_REPO_NAME:-${REPO}}"
case "${REPO_NAME}" in
  plugin-codeforge|mclayer/plugin-codeforge)
    echo "[INFO] wrapper-self-app fast-pass: repo=${REPO_NAME} — N/A (ADR-104 §결정 4)"
    echo "[INFO] wrapper repo = declarative SSOT only. 실 monitoring = consumer 환경."
    exit 0
    ;;
esac

# --- Step 2: Python 스크립트 존재 확인 (SETUP guard) ---
if [[ ! -f "${REGRESSION_PY}" ]]; then
  echo "[ERROR] check_operational_regression.py 부재 — ADR-061 Python 파일 필요" >&2
  exit 2
fi

# --- Step 3: regression/health 평가 (Python 위임) ---
PYTHON_OUT=""
PYTHON_EXIT=0

# set -e 하에서 Python exit 2 정확히 포착하기 위해 subshell + || true 패턴 사용
PYTHON_OUT=$(PYTHONUTF8=1 python3 "${REGRESSION_PY}" \
    --signal-type "${SIGNAL_TYPE}" \
    --metric-name "${METRIC_NAME}" \
    --regression-threshold "${REGRESSION_THRESHOLD}" \
    --flap-n "${FLAP_N}" \
    --recovery-margin "${RECOVERY_MARGIN}" \
    --window "${WINDOW}" \
    --baseline-file "${BASELINE_FILE}" \
    --current-metric-file "${CURRENT_METRIC_FILE}" \
    --health-file "${HEALTH_FILE}" \
    --flap-state-file "${FLAP_STATE_FILE}" \
    2>&1) || PYTHON_EXIT=$?

# EC-2: Python exit 2 (SETUP error) → escalation Issue + exit 2
if [[ "${PYTHON_EXIT}" != "0" ]]; then
  echo "[ERROR] check_operational_regression.py SETUP error (exit 2)" >&2
  echo "${PYTHON_OUT}" >&2

  # escalation Issue 발의 (metric source 불가 알림)
  if [[ "${_CFP1194_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
    gh issue create \
      --repo "${REPO}" \
      --label "ops-signal" \
      --title "[OPS-SIGNAL] regression/health monitor SETUP error — metric source 불가" \
      --body "check-operational-regression.sh: metric source 불가 (SETUP error).

EC-2: 의존성 복구 후 재실행 필요 (ADR-057 자동 재시도 0).
metric_name: ${METRIC_NAME}
signal_type: ${SIGNAL_TYPE}
repo: ${REPO}

[CFP-1194] ops-signal label (ADR-106 Amendment 2 §결정 1 단계 2-a)" \
      2>/dev/null || true
  fi
  exit 2
fi

# Python 출력 파싱
SIGNAL_DETECTED=$(echo "${PYTHON_OUT}" | grep "^signal_detected=" | cut -d= -f2)
SIGNAL_TYPE_OUT=$(echo "${PYTHON_OUT}" | grep "^signal_type=" | cut -d= -f2)
MEASURED=$(echo "${PYTHON_OUT}" | grep "^measured=" | cut -d= -f2)
BASELINE_OUT=$(echo "${PYTHON_OUT}" | grep "^baseline=" | cut -d= -f2)
THRESHOLD=$(echo "${PYTHON_OUT}" | grep "^threshold=" | cut -d= -f2)
WINDOW_OUT=$(echo "${PYTHON_OUT}" | grep "^window=" | cut -d= -f2)
FLAP_SUPPRESSED=$(echo "${PYTHON_OUT}" | grep "^flap_suppressed=" | cut -d= -f2)
SIGNATURE=$(echo "${PYTHON_OUT}" | grep "^signature=" | cut -d= -f2)

echo "[INFO] 신호 감지: signal_detected=${SIGNAL_DETECTED} signal_type=${SIGNAL_TYPE_OUT}"
echo "[INFO] 측정값: measured=${MEASURED} baseline=${BASELINE_OUT} threshold=${THRESHOLD} window=${WINDOW_OUT}s"
echo "[INFO] flap 억제: flap_suppressed=${FLAP_SUPPRESSED}"

# 신호 미감지 (정상 범위 / 임계 미정의 / baseline bootstrap)
if [[ "${SIGNAL_DETECTED}" != "true" ]]; then
  echo "[PASS] 신호 미감지 — 정상 범위 또는 임계 미정의"
  exit 0
fi

# flap 억제 (N-tick 미달)
if [[ "${FLAP_SUPPRESSED}" == "true" ]]; then
  echo "[INFO] flap 억제 (N-tick for-clause / hysteresis) — Issue 발의 0"
  exit 0
fi

echo "[SIGNAL] regression/health 신호 감지: signal_type=${SIGNAL_TYPE_OUT} measured=${MEASURED} threshold=${THRESHOLD}"

# --- Step 4: signature dedup (Issue-level, S4 §3.8 동형 답습) ---
DEDUP_FOUND=0

if [[ "${_CFP1194_MOCK_DEDUP:-0}" == "1" ]]; then
  DEDUP_FOUND=1
elif [[ "${_CFP1194_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
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

# --- Step 5: ops-signal Issue 발의 (단계 2-a monitor-originated notification) ---
# S5 ∉ rollback — Issue 발의만 (자동 rollback trigger 0, S4와 disjoint)
ISSUE_TITLE="[OPS-SIGNAL] regression/health 감지: ${SIGNAL_TYPE_OUT} (${MEASURED} vs baseline ${BASELINE_OUT})"
ISSUE_BODY="regression/smoke·health monitor 감지 결과.

signal_type: ${SIGNAL_TYPE_OUT}
measured: ${MEASURED}
baseline: ${BASELINE_OUT}
threshold: ${THRESHOLD}
window: ${WINDOW_OUT}s
metric_name: ${METRIC_NAME}
signature: ${SIGNATURE}

[ADR-106 Amendment 2 §결정 1 단계 2-a — monitor-originated regression/health notification]
[S5 ∉ rollback — 본 Issue 는 경고 전용. 자동 rollback = S4 영역 (ADR-105 §결정 3)]
[empirical-source: Grafana/Prometheus 'for' clause + Datadog hysteresis — 산업 표준 flap 흡수]
[CFP-1194] ops-signal label (ADR-106 Amendment 2)"

if [[ "${_CFP1194_SKIP_ISSUE_CREATE:-0}" == "1" ]]; then
  echo "[INFO] Issue 발의 차단 (dry-run: _CFP1194_SKIP_ISSUE_CREATE=1)"
  echo "[INFO] Issue title preview: ${ISSUE_TITLE}"
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

echo "[INFO] regression/smoke·health monitor 완료: signal=${SIGNAL_TYPE_OUT} sig=${SIGNATURE}"
exit 0
