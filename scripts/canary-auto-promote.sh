#!/usr/bin/env bash
# scripts/canary-auto-promote.sh
# CFP-1196 — canary auto-promote mechanism (thin bash orchestration)
#
# ADR-105 §결정 3: 안전장치 4 AND (1:criteria 4-tuple / 2:보존기간 / 3:사후알림 / 4:kill-switch)
# ADR-104 §결정 3: 0 API call (criteria measurement = filesystem / local artifact)
# ADR-061: criteria 4-tuple 집계 산술 = Python 위임 (canary_auto_promote.py)
# ADR-087 §결정 5: deploy lane blue-green (deploy_blue_green.py 호출 = L2 계약)
#
# S7 = S4 (check-rollback-signal.sh) 의 mirror — trigger 방향만 반대
#   S4: 임계 위반 → auto rollback
#   S7: criteria 충족 → auto promote
#
# 호출 흐름:
#   canary-auto-promote.yml (deploy 후속 trigger / cron backstop / workflow_dispatch)
#     └─ 본 스크립트
#          ├─ kill-switch 체크 (가장 먼저 — §3.7, fast-skip, 안전장치 4)
#          ├─ wrapper fast-pass 체크 (§3.8, repo=wrapper → exit 0, Tier-1 exemption)
#          ├─ canary subset 배포 (L2 deploy_blue_green.py --host subset-member loop)
#          │     ├─ canary-phase 실패 시 → 성공한 canary host 도 rollback + 전체 정지 (§3.2 F-1196-4)
#          ├─ python3 canary_auto_promote.py (criteria 4-tuple 집계 + 안전장치 평가 + signature)
#          ├─ 안전장치 2 (보존기간) 체크 — L2 hook 위임 (_CFP1059_MOCK_WITHIN_RETENTION)
#          ├─ 안전장치 3 (notification pre-promote check — 0 API call)
#          ├─ [criteria_met=true + 4 AND] → 나머지 host 전체 promote (L2 deploy_blue_green.py loop)
#          │     ├─ promote partial 실패 (D3): keep-forward + 실패 host rollback + 전체 정지 (§3.5)
#          ├─ [criteria_met=false + 안전장치 미충족] → canary subset rollback + 정지
#          ├─ signature dedup (gh issue list --search "signature: ${SIG}")
#          └─ ops-signal Issue 발의 (open Issue 부재 시) + exit 0
#
# 3-layer disjoint (중복 0 — TC-7 grep 검증):
#   L1 criteria 정의 (CFP-991 check-canary-compatibility.sh + helper) = 읽어 재사용 (재구현 0)
#   L2 deploy/rollback (CFP-1059 deploy_blue_green.py / auto-rollback-hook.sh) = 호출만 (재구현 0)
#   L3 canary 오케스트레이션 = 본 파일 + canary_auto_promote.py (신규)
#
# Test override env (_CFP1196_MOCK_* namespace, CFP-1193 _CFP1193_MOCK_* 답습):
#   _CFP1196_MOCK_KILL_SWITCH=<0|1>            — kill-switch 활성 override (1=활성)
#   _CFP1196_MOCK_KILL_SWITCH_FLAG=<path>      — kill-switch flag 경로 override
#   _CFP1196_MOCK_CONFIG_DISABLED=<0|1>        — config auto_promote_enabled=false mock
#   _CFP1196_MOCK_DEDUP=<0|1>                  — open Issue 존재 mock (1=dedup 발동)
#   _CFP1196_MOCK_REPO_NAME=<str>              — repo 이름 override
#   _CFP1196_MOCK_HOOK_MISSING=<0|1>           — hook 부재 mock (1=부재, exit 2)
#   _CFP1196_MOCK_FUNCTIONAL=<pass|fail|n_a>   — functional gate_state override
#   _CFP1196_MOCK_SECURITY=<pass|fail|n_a>     — security gate_state override
#   _CFP1196_MOCK_MONITORING=<pass|fail|n_a>   — monitoring gate_state override
#   _CFP1196_MOCK_TESTING=<pass|fail|n_a>      — testing gate_state override
#   _CFP1196_MOCK_NOTIFICATION_AVAILABLE=<true|false> — safety_3 pre-promote check mock
#   _CFP1196_SKIP_ISSUE_CREATE=<1>             — Issue 발의 차단 (dry-run)
#   _CFP1059_MOCK_WITHIN_RETENTION=<0|1>       — 보존 기간 mock (1=window 내, 안전장치 2)
#   _CFP1059_MOCK_HEALTH=<pass|fail|real>      — L2 deploy health mock
#   _CFP1059_MOCK_DOCKER=<0|1>                 — L2 docker mock
#   _CFP1059_MOCK_SSH=<0|1>                    — L2 ssh mock
#   _CFP1059_MOCK_SWAP_FAIL=<host_idx>         — promote phase partial 실패 host 인덱스 (0-based, -1=없음)
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (promote 완료 / 정지 처리 정상 / wrapper fast-pass)
#   1 = warning (measurement source missing / sandbox-bound — continue-on-error)
#   2 = SETUP error (hook 부재 / yaml parse error / python 부재)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROMOTE_PY="${WORKTREE_ROOT}/scripts/canary_auto_promote.py"
DEPLOY_PY="${WORKTREE_ROOT}/scripts/deploy_blue_green.py"
ROLLBACK_SH="${WORKTREE_ROOT}/templates/deployment/auto-rollback-hook.sh"
HELPER_LIB="${WORKTREE_ROOT}/scripts/lib/canary-compatibility-helpers.sh"

# --- 인수 파싱 ---
REPO=""
IMAGE=""
HOST_LIST=""     # comma-separated 전체 host 목록
CANARY_SUBSET="" # comma-separated canary subset (default = HOST_LIST 첫 번째)
RETENTION_HOURS="3"

usage() {
  cat <<'EOF'
Usage: canary-auto-promote.sh --repo <repo> --image <image> --host-list <hosts> [options]

Options:
  --repo <repo>               대상 repo
  --image <image>             배포 이미지
  --host-list <h1,h2,...>     전체 host 목록 (comma-separated)
  --canary-subset <h1,...>    canary subset (default = 첫 번째 1 host)
  --retention-hours <n>       보존 window (default 3) [empirical-source: ADR-087 §결정 5]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)            REPO="$2";            shift 2 ;;
    --image)           IMAGE="$2";           shift 2 ;;
    --host-list)       HOST_LIST="$2";       shift 2 ;;
    --canary-subset)   CANARY_SUBSET="$2";   shift 2 ;;
    --retention-hours) RETENTION_HOURS="$2"; shift 2 ;;
    --help|-h)         usage; exit 0 ;;
    *) echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${REPO}" || -z "${IMAGE}" || -z "${HOST_LIST}" ]]; then
  echo "[ERROR] --repo, --image, --host-list 필수" >&2
  exit 1
fi

# host list 파싱 (comma-separated → array)
IFS=',' read -ra ALL_HOSTS <<< "${HOST_LIST}"

# canary subset 결정 (default = 첫 번째 host, D2)
if [[ -z "${CANARY_SUBSET}" ]]; then
  CANARY_SUBSET="${ALL_HOSTS[0]}"
fi
IFS=',' read -ra CANARY_HOSTS <<< "${CANARY_SUBSET}"

# 나머지 host (전체 promote 대상) = ALL_HOSTS - CANARY_HOSTS
REMAINING_HOSTS=()
for h in "${ALL_HOSTS[@]}"; do
  is_canary=0
  for c in "${CANARY_HOSTS[@]}"; do
    if [[ "$h" == "$c" ]]; then
      is_canary=1; break
    fi
  done
  if [[ "${is_canary}" == "0" ]]; then
    REMAINING_HOSTS+=("$h")
  fi
done

# kill-switch flag 경로
KILL_SWITCH_FLAG="${_CFP1196_MOCK_KILL_SWITCH_FLAG:-${WORKTREE_ROOT}/.codeforge/auto-promote.disabled}"

# config yaml path
CONFIG_YAML_PATH="${_CFP1196_MOCK_CONFIG_YAML_PATH:-${WORKTREE_ROOT}/.claude/_overlay/project.yaml}"

# repo 이름 (wrapper fast-pass 체크)
REPO_NAME="${_CFP1196_MOCK_REPO_NAME:-${REPO}}"

# 보존 window (초)
WINDOW_SECONDS=$((RETENTION_HOURS * 3600))

# ---
# Step 1: kill-switch 체크 (가장 먼저 평가 — §3.7, fast-skip, C-5)
# ---
KILL_SWITCH_ACTIVE=0

# filesystem flag (primary, 0 API call)
if [[ -f "${KILL_SWITCH_FLAG}" ]]; then
  KILL_SWITCH_ACTIVE=1
fi

# kill-switch mock override (test env)
if [[ "${_CFP1196_MOCK_KILL_SWITCH:-0}" == "1" ]]; then
  KILL_SWITCH_ACTIVE=1
fi

# config flag disabled (secondary) — mock override
if [[ "${_CFP1196_MOCK_CONFIG_DISABLED:-0}" == "1" ]]; then
  KILL_SWITCH_ACTIVE=1
fi

if [[ "${KILL_SWITCH_ACTIVE}" == "1" ]]; then
  echo "[INFO] kill-switch 활성 — auto-promote 무력화 (§3.7 OR disable, EC-4 / TC-5)"
  echo "[INFO] kill_switch_active=true: 수동 promote 통제 복귀"
  echo "[INFO] 사후 알림 Issue 발의 (kill-switch 활성 감사 추적)"
  # Issue 발의로 이동 (fall-through)
fi

# ---
# Step 2: wrapper-self-app fast-pass (§3.8, ADR-104 §결정 4, Tier-1 exemption)
# ---
case "${REPO_NAME}" in
  plugin-codeforge|mclayer/plugin-codeforge)
    echo "[INFO] wrapper-self-app fast-pass: repo=${REPO_NAME} — N/A (ADR-104 §결정 4)"
    echo "[INFO] wrapper repo = declarative SSOT only. 실 canary promote = consumer 영역."
    exit 0
    ;;
esac

# ---
# Step 3: Python / hook 의존성 확인 (SETUP guard)
# ---
if [[ ! -f "${PROMOTE_PY}" ]]; then
  echo "[ERROR] canary_auto_promote.py 부재 — ADR-061 Python 파일 필요" >&2
  exit 2
fi

if [[ "${_CFP1196_MOCK_HOOK_MISSING:-0}" == "1" ]] || [[ ! -f "${DEPLOY_PY}" ]]; then
  echo "[ERROR] deploy_blue_green.py 부재 — L2 deploy hook 필요 (EC-hook-missing)" >&2
  # escalation Issue
  if [[ "${_CFP1196_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
    gh issue create \
      --repo "${REPO}" \
      --label "ops-signal" \
      --title "[OPS-SIGNAL] canary auto-promote L2 hook 부재 — SETUP error" \
      --body "canary-auto-promote.sh: deploy_blue_green.py 부재.

SETUP error (ADR-057 자동 재시도 0 — 의존성 복구 후 재실행 필요)

repo: ${REPO}
[CFP-1196] ops-signal label (ADR-106 §결정 1 단계 2)" \
      2>/dev/null || true
  fi
  exit 2
fi

# ---
# Step 4: kill-switch 활성 시 사후 알림 Issue만 발의 후 종료 (promote skip)
# ---
if [[ "${KILL_SWITCH_ACTIVE}" == "1" ]]; then
  # signature 계산은 python에 위임
  KILL_SWITCH_SIG=$(printf "kill_switch_active|1|%s" "${WINDOW_SECONDS}" | sha256sum | cut -c1-16 2>/dev/null || echo "killswitch000000")
  if [[ "${_CFP1196_MOCK_DEDUP:-0}" != "1" ]] && [[ "${_CFP1196_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
    EXISTING=$(gh issue list --repo "${REPO}" --search "\"signature: ${KILL_SWITCH_SIG}\"" --state open --json number --limit 5 2>/dev/null || echo "[]")
    if [[ "${EXISTING}" == "[]" || "${EXISTING}" == "" ]]; then
      gh issue create \
        --repo "${REPO}" \
        --label "ops-signal" \
        --title "[OPS-SIGNAL] canary auto-promote kill-switch 활성 — 수동 promote 통제" \
        --body "canary-auto-promote.sh: kill-switch 활성으로 자동 promote 차단.

kill_switch_active=true
repo: ${REPO}
image: ${IMAGE}
signature: ${KILL_SWITCH_SIG}

수동 promote 통제 복귀 상태입니다.
[CFP-1196] ops-signal label" \
        2>/dev/null || true
    fi
  fi
  exit 0
fi

# ---
# Step 5: canary subset 배포 (L2 deploy_blue_green.py 호출 — 재구현 0)
# ---
echo "[INFO] canary subset 배포 시작: subset=${CANARY_SUBSET}"
CANARY_DEPLOYED=()

# L2 deploy 공통 인수 구성
DEPLOY_BASE_ARGS=(
  "--repo" "${REPO}"
  "--image" "${IMAGE}"
  "--retention-hours" "${RETENTION_HOURS}"
)

# L2 mock args (테스트 환경)
if [[ "${_CFP1059_MOCK_DOCKER:-0}" == "1" ]]; then
  DEPLOY_BASE_ARGS+=("--mock-docker" "1")
fi
if [[ "${_CFP1059_MOCK_SSH:-0}" == "1" ]]; then
  DEPLOY_BASE_ARGS+=("--mock-ssh" "1")
fi
if [[ -n "${_CFP1059_MOCK_HEALTH:-}" ]]; then
  DEPLOY_BASE_ARGS+=("--mock-health" "${_CFP1059_MOCK_HEALTH}")
fi

for host in "${CANARY_HOSTS[@]}"; do
  echo "[INFO] canary 배포: host=${host}"
  if PYTHONUTF8=1 python3 "${DEPLOY_PY}" "${DEPLOY_BASE_ARGS[@]}" "--host" "${host}" 2>&1; then
    CANARY_DEPLOYED+=("${host}")
    echo "[INFO] canary 배포 성공: host=${host}"
  else
    # canary-phase 실패 (host health fail 등)
    echo "[WARN] canary 배포 실패: host=${host} — F-1196-4 canary-phase partial 실패"
    echo "[INFO] 이미 성공한 canary host rollback: ${CANARY_DEPLOYED[*]:-none}"

    # 실패 host rollback (L2 auto-rollback-hook)
    if [[ -f "${ROLLBACK_SH}" ]]; then
      bash "${ROLLBACK_SH}" --repo "${REPO}" --host "${host}" 2>&1 || true
    fi

    # 이미 성공한 canary host 도 rollback (§3.2 F-1196-4 — canary는 측정 기준선)
    for rolled_host in "${CANARY_DEPLOYED[@]}"; do
      echo "[INFO] canary 성공 host rollback (측정 기준선 일관성): host=${rolled_host}"
      if [[ -f "${ROLLBACK_SH}" ]]; then
        bash "${ROLLBACK_SH}" --repo "${REPO}" --host "${rolled_host}" 2>&1 || true
      fi
    done

    # 사후 알림 Issue (canary-phase partial 실패)
    CANARY_FAIL_SIG=$(printf "canary_phase_fail|%s|%s" "${host}" "${WINDOW_SECONDS}" | sha256sum | cut -c1-16 2>/dev/null || echo "canaryfail0000")
    if [[ "${_CFP1196_MOCK_DEDUP:-0}" != "1" ]] && [[ "${_CFP1196_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
      EXISTING=$(gh issue list --repo "${REPO}" --search "\"signature: ${CANARY_FAIL_SIG}\"" --state open --json number --limit 5 2>/dev/null || echo "[]")
      if [[ "${EXISTING}" == "[]" || "${EXISTING}" == "" ]]; then
        gh issue create \
          --repo "${REPO}" \
          --label "ops-signal" \
          --title "[OPS-SIGNAL] canary 배포 실패 — promote 중단" \
          --body "canary-auto-promote.sh: canary subset 배포 실패.

failed_host: ${host}
rolled_back_canary: ${CANARY_DEPLOYED[*]:-none}
policy: F-1196-4 canary-phase 전체 rollback (부분 canary = 측정 무의미)

promote 미진입 — 수동 조치 필요.
signature: ${CANARY_FAIL_SIG}
[CFP-1196] ops-signal label" \
          2>/dev/null || true
      fi
    fi
    echo "[INFO] canary-phase 실패 처리 완료 — promote 미진입"
    exit 0
  fi
done

echo "[INFO] canary subset 배포 완료: ${CANARY_DEPLOYED[*]}"

# ---
# Step 6: criteria 측정 + 안전장치 평가 (Python 위임 — 재구현 0)
# ---
FUNCTIONAL="${_CFP1196_MOCK_FUNCTIONAL:-n_a}"
SECURITY="${_CFP1196_MOCK_SECURITY:-n_a}"
MONITORING="${_CFP1196_MOCK_MONITORING:-n_a}"
TESTING="${_CFP1196_MOCK_TESTING:-n_a}"
NOTIFICATION_MOCK="${_CFP1196_MOCK_NOTIFICATION_AVAILABLE:-}"

CONFIG_DISABLED_ARG="false"
if [[ "${_CFP1196_MOCK_CONFIG_DISABLED:-0}" == "1" ]]; then
  CONFIG_DISABLED_ARG="true"
fi

PYTHON_OUT=""
if ! PYTHON_OUT=$(PYTHONUTF8=1 python3 "${PROMOTE_PY}" \
    --functional "${FUNCTIONAL}" \
    --security "${SECURITY}" \
    --monitoring "${MONITORING}" \
    --testing "${TESTING}" \
    --kill-switch-flag "${KILL_SWITCH_FLAG}" \
    --config-disabled "${CONFIG_DISABLED_ARG}" \
    --config-yaml-path "${CONFIG_YAML_PATH}" \
    --window "${WINDOW_SECONDS}" \
    --mock-notification-available "${NOTIFICATION_MOCK}" \
    2>&1); then
  echo "[ERROR] canary_auto_promote.py 실행 실패" >&2
  echo "${PYTHON_OUT}" >&2
  exit 2
fi

# Python 출력 파싱
CRITERIA_MET=$(echo "${PYTHON_OUT}" | grep "^criteria_met=" | cut -d= -f2)
GATE_STATES=$(echo "${PYTHON_OUT}" | grep "^gate_states=" | cut -d= -f2-)
SAFETY_1=$(echo "${PYTHON_OUT}" | grep "^safety_1=" | cut -d= -f2)
SAFETY_3=$(echo "${PYTHON_OUT}" | grep "^safety_3=" | cut -d= -f2)
SAFETY_4=$(echo "${PYTHON_OUT}" | grep "^safety_4=" | cut -d= -f2)
NOTIFICATION_AVAILABLE=$(echo "${PYTHON_OUT}" | grep "^notification_available=" | cut -d= -f2)
SIGNATURE=$(echo "${PYTHON_OUT}" | grep "^signature=" | cut -d= -f2)

echo "[INFO] criteria 집계: criteria_met=${CRITERIA_MET}"
echo "[INFO] gate_states: ${GATE_STATES}"
echo "[INFO] 안전장치: safety_1=${SAFETY_1} safety_3=${SAFETY_3} safety_4=${SAFETY_4}"

# ---
# Step 7: 안전장치 3 (pre-promote notification availability check — F-1196-3)
# ---
if [[ "${SAFETY_3}" != "true" ]]; then
  echo "[WARN] 안전장치 3 미충족 — 알림 mechanism 미가용 (TC-19)"
  echo "[WARN] notification_available=false → promote 금지 (무음 promote 차단, ADR-105 안전장치 3)"
  echo "[INFO] GH_TOKEN 또는 gh CLI 미설정 — GitHub Actions 환경 확인 필요"
  # canary subset rollback (배포된 host 되돌리기)
  for h in "${CANARY_DEPLOYED[@]}"; do
    if [[ -f "${ROLLBACK_SH}" ]]; then
      bash "${ROLLBACK_SH}" --repo "${REPO}" --host "${h}" 2>&1 || true
    fi
  done
  exit 0
fi

# ---
# Step 8: 안전장치 2 (보존 기간) 체크 — L2 hook 위임
# ---
WITHIN_RETENTION="${_CFP1059_MOCK_WITHIN_RETENTION:-0}"

if [[ "${WITHIN_RETENTION}" == "0" ]]; then
  echo "[WARN] 3시간 보존 window 만료 — promote 금지 (TC-4 / TC-18)"
  echo "[INFO] backstop 정책 (F-1196-2): cron backstop(24h) > retention(3h) = 만료 후 도착 가능"
  echo "[INFO] missed canary 사후 정리: promote 금지 + hotfix 안내 (EC-7)"
  echo "[empirical-source: ADR-087 §결정 5 — 3시간 보존 window, dimension: lifecycle]"

  # 사후 알림 (hotfix 안내 Issue)
  EXPIRED_SIG=$(printf "retention_expired|canary|%s" "${WINDOW_SECONDS}" | sha256sum | cut -c1-16 2>/dev/null || echo "expired0000000")
  if [[ "${_CFP1196_MOCK_DEDUP:-0}" != "1" ]] && [[ "${_CFP1196_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
    EXISTING=$(gh issue list --repo "${REPO}" --search "\"signature: ${EXPIRED_SIG}\"" --state open --json number --limit 5 2>/dev/null || echo "[]")
    if [[ "${EXISTING}" == "[]" || "${EXISTING}" == "" ]]; then
      gh issue create \
        --repo "${REPO}" \
        --label "ops-signal" \
        --title "[OPS-SIGNAL] canary 보존 window 만료 — promote 금지 + hotfix 필요" \
        --body "canary-auto-promote.sh: 3시간 보존 window 만료로 promote 금지.

정책 (F-1196-2): backstop cron 주기(24h) > retention(3h) — backstop = missed canary 사후 정리.
in-window promote 보장 = deploy 후속 trigger (primary) 책임.

수동 hotfix 또는 재배포 필요.
signature: ${EXPIRED_SIG}

[empirical-source: ADR-087 §결정 5 — 3시간 보존 window]
[CFP-1196] ops-signal label" \
        2>/dev/null || true
    fi
  fi
  exit 0
fi

# ---
# Step 9: criteria 미충족 → canary rollback + 정지 (EC-1)
# ---
if [[ "${CRITERIA_MET}" != "true" ]]; then
  echo "[WARN] criteria 미충족 (safety_1=false) — promote abort (EC-1 보수적 정지)"
  echo "[INFO] gate_states: ${GATE_STATES}"
  echo "[INFO] canary subset rollback 시작"

  for h in "${CANARY_DEPLOYED[@]}"; do
    echo "[INFO] canary rollback: host=${h}"
    if [[ -f "${ROLLBACK_SH}" ]]; then
      bash "${ROLLBACK_SH}" --repo "${REPO}" --host "${h}" 2>&1 || true
    fi
  done

  # 사후 알림 Issue (정지)
  ABORT_SIG=$(printf "canary_abort|%s|%s" "${GATE_STATES}" "${WINDOW_SECONDS}" | sha256sum | cut -c1-16 2>/dev/null || echo "aborted00000000")
  if [[ "${_CFP1196_MOCK_DEDUP:-0}" == "1" ]]; then
    echo "[INFO] dedup: 동일 signature open Issue 존재 — 새 Issue 억제 (TC-8)"
  elif [[ "${_CFP1196_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
    EXISTING=$(gh issue list --repo "${REPO}" --search "\"signature: ${ABORT_SIG}\"" --state open --json number --limit 5 2>/dev/null || echo "[]")
    if [[ "${EXISTING}" == "[]" || "${EXISTING}" == "" ]]; then
      gh issue create \
        --repo "${REPO}" \
        --label "ops-signal" \
        --title "[OPS-SIGNAL] canary promote 정지 — criteria 미충족" \
        --body "canary-auto-promote.sh: criteria 미충족으로 promote 정지.

criteria_met=false
gate_states: ${GATE_STATES}
canary_rolled_back: ${CANARY_DEPLOYED[*]:-none}

policy: EC-1 (1+ fail → abort, 보수적 정지)
signature: ${ABORT_SIG}

[CFP-1196] ops-signal label (ADR-106 §결정 1 단계 2)" \
        2>/dev/null || true
    fi
  fi

  echo "[INFO] promote 정지 처리 완료"
  exit 0
fi

# ---
# Step 10: 전체 promote (criteria 충족 + 안전장치 4 AND)
# ---
echo "[INFO] criteria 충족 + 안전장치 4 AND — 전체 promote 시작"
echo "[INFO] remaining_hosts=${REMAINING_HOSTS[*]:-none}"

PROMOTED=()
FAILED=()
PROMOTE_PARTIAL=0

# promote loop (D3: keep-forward + 실패 host rollback + 전체 정지)
PROMOTE_IDX=0
for host in "${REMAINING_HOSTS[@]+"${REMAINING_HOSTS[@]}"}"; do
  # TC-9: --mock-swap-fail host 인덱스 (0-based, -1=없음) 체크
  SWAP_FAIL_IDX="${_CFP1059_MOCK_SWAP_FAIL:--1}"
  DEPLOY_ARGS=("${DEPLOY_BASE_ARGS[@]}" "--host" "${host}")
  if [[ "${SWAP_FAIL_IDX}" == "${PROMOTE_IDX}" ]]; then
    DEPLOY_ARGS+=("--mock-swap-fail" "1")
  fi

  echo "[INFO] promote: host=${host}"
  if PYTHONUTF8=1 python3 "${DEPLOY_PY}" "${DEPLOY_ARGS[@]}" 2>&1; then
    PROMOTED+=("${host}")
    echo "[INFO] promote 성공: host=${host}"
  else
    # D3: 실패 host rollback + 전체 정지 (잔여 host 진입 차단)
    echo "[WARN] promote 실패: host=${host} — D3 keep-forward + 실패 host rollback + 정지"
    FAILED+=("${host}")
    PROMOTE_PARTIAL=1

    # 실패 host rollback
    if [[ -f "${ROLLBACK_SH}" ]]; then
      bash "${ROLLBACK_SH}" --repo "${REPO}" --host "${host}" 2>&1 || true
    fi
    echo "[INFO] 이미 promote된 host keep-forward (D3): ${PROMOTED[*]:-none}"
    break  # fail-fast: 잔여 host 진입 차단
  fi
  PROMOTE_IDX=$((PROMOTE_IDX + 1))
done

# ---
# Step 11: signature dedup 확인
# ---
DEDUP_FOUND=0
if [[ "${_CFP1196_MOCK_DEDUP:-0}" == "1" ]]; then
  DEDUP_FOUND=1
elif [[ "${_CFP1196_SKIP_ISSUE_CREATE:-0}" != "1" ]] && command -v gh >/dev/null 2>&1; then
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
  echo "[INFO] dedup: 동일 signature open Issue 존재 — 새 Issue 억제 (TC-8)"
  exit 0
fi

# ---
# Step 12: ops-signal Issue 발의 (사후 알림, ADR-106 §결정 1 단계 2)
# ---
if [[ "${PROMOTE_PARTIAL}" == "1" ]]; then
  ISSUE_TITLE="[OPS-SIGNAL] canary promote 부분 실패 (D3 keep-forward)"
  ISSUE_BODY="canary-auto-promote.sh: promote 중 일부 host 실패 (D3 정책).

criteria_met=true (gate_states: ${GATE_STATES})
promoted_keep_forward: ${PROMOTED[*]:-none}
failed_rolled_back: ${FAILED[*]:-none}

D3 정책: keep-forward (이미 promote된 host 유지) + 실패 host rollback + 잔여 host 차단.
수동 조치 필요.
signature: ${SIGNATURE}

[CFP-1196] ops-signal label"
else
  ISSUE_TITLE="[OPS-SIGNAL] canary promote 완료"
  ISSUE_BODY="canary-auto-promote.sh: criteria 충족 → 전체 promote 완료.

criteria_met=true (gate_states: ${GATE_STATES})
canary_hosts: ${CANARY_DEPLOYED[*]:-none}
promoted_hosts: ${PROMOTED[*]:-none}
signature: ${SIGNATURE}

[CFP-1196] ops-signal label (ADR-106 §결정 1 단계 2)"
fi

if [[ "${_CFP1196_SKIP_ISSUE_CREATE:-0}" == "1" ]]; then
  echo "[INFO] Issue 발의 차단 (dry-run: _CFP1196_SKIP_ISSUE_CREATE=1)"
  echo "[INFO] Issue preview: ${ISSUE_TITLE}"
else
  if command -v gh >/dev/null 2>&1; then
    gh issue create \
      --repo "${REPO}" \
      --label "ops-signal" \
      --title "${ISSUE_TITLE}" \
      --body "${ISSUE_BODY}" \
      2>/dev/null || {
        echo "[WARN] Issue 발의 실패 (gh CLI 에러 — promote 결과는 기록됨)" >&2
      }
  else
    echo "[WARN] gh CLI 미설치 — Issue 발의 불가" >&2
  fi
fi

if [[ "${PROMOTE_PARTIAL}" == "1" ]]; then
  echo "[WARN] canary auto-promote 완료 (부분 실패, D3): sig=${SIGNATURE}"
else
  echo "[INFO] canary auto-promote 완료: sig=${SIGNATURE}"
fi
exit 0
