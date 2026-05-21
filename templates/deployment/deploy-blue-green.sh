#!/usr/bin/env bash
# templates/deployment/deploy-blue-green.sh
# CFP-1059-S6 — blue-green atomic swap orchestration (ADR-087 §결정 5)
#
# §7.4 empirical-source:
#   3시간 보존: Issue #1059 카테고리 3/9 — 사용자 결정 (dimension: lifecycle)
#   healthcheck window 60s: ADR-087 §결정 5 (dimension: latency)
#   HTTP drain 30s / WebSocket 5min: ADR-087 §결정 5 (dimension: latency)
#   sequential rolling N=1 host/step: 사용자 결정 (dimension: count)
#
# §7.5 secret: DOCKER_HUB_TOKEN / SSH_KEY_PATH = env var only (no echo/log)
#
# invariant (I-1 unconditional):
#   - green health PASS = swap 전제조건 (FAIL -> auto-rollback, swap 미실행)
#   - 3시간 보존 = unconditional (green 정상이어도 blue 즉시 삭제 금지)
#   - swap = Traefik label flip (single docker API call, atomic)
#   - flip 실패 = blue 유지 (no partial state)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOY_PY="${WORKTREE_ROOT}/scripts/deploy_blue_green.py"

# ── 인수 파싱 ──────────────────────────────────────────────────────────────────
REPO=""
IMAGE=""
HOST=""
RETENTION_HOURS="${DEPLOY_RETENTION_HOURS:-3}"  # [empirical-source: Issue #1059 카테고리 3/9]

usage() {
  echo "Usage: $0 --repo <repo> --image <image> --host <host> [--retention-hours <N>]"
  echo ""
  echo "Options:"
  echo "  --repo              배포 대상 리포 이름"
  echo "  --image             Docker 이미지 (tag 포함)"
  echo "  --host              SSH 배포 호스트"
  echo "  --retention-hours   blue 보존 시간 (default: 3, empirical-source: Issue #1059)"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)         REPO="$2";             shift 2 ;;
    --image)        IMAGE="$2";            shift 2 ;;
    --host)         HOST="$2";             shift 2 ;;
    --retention-hours) RETENTION_HOURS="$2"; shift 2 ;;
    --help|-h)      usage ;;
    *)              echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${REPO}" || -z "${IMAGE}" || -z "${HOST}" ]]; then
  echo "[ERROR] --repo, --image, --host 필수" >&2
  exit 1
fi

# ── mock seam (테스트 환경) ───────────────────────────────────────────────────
MOCK_DOCKER="${_CFP1059_MOCK_DOCKER:-0}"
MOCK_SSH="${_CFP1059_MOCK_SSH:-0}"
MOCK_HEALTH="${_CFP1059_MOCK_HEALTH:-real}"     # pass | fail | real
MOCK_GREEN_RUNNING="${_CFP1059_MOCK_GREEN_RUNNING:-0}"
MOCK_SWAP_FAIL="${_CFP1059_MOCK_SWAP_FAIL:-0}"
MOCK_RESTART_BEFORE_SWAP="${_CFP1059_MOCK_RESTART_BEFORE_SWAP:-0}"

echo "=== deploy-blue-green.sh ==="
echo "repo=${REPO} image=${IMAGE} host=${HOST} retention=${RETENTION_HOURS}h"
echo "[empirical-source: Issue #1059 카테고리 3/9 — 3시간 보존, dimension: lifecycle]"

# ── idempotency: green 이미 실행 중 체크 ──────────────────────────────────────
if [[ "${MOCK_GREEN_RUNNING}" == "1" ]]; then
  echo "[INFO] green container 이미 실행 중 — skip (idempotent no-op)"
  exit 0
fi

# ── Python 로직 위임 (ADR-061: multi-line = 외부 .py) ─────────────────────────
if [[ -f "${DEPLOY_PY}" ]]; then
  PYTHONUTF8=1 python3 "${DEPLOY_PY}" \
    --repo "${REPO}" \
    --image "${IMAGE}" \
    --host "${HOST}" \
    --retention-hours "${RETENTION_HOURS}" \
    --mock-docker "${MOCK_DOCKER}" \
    --mock-ssh "${MOCK_SSH}" \
    --mock-health "${MOCK_HEALTH}" \
    --mock-swap-fail "${MOCK_SWAP_FAIL}" \
    --mock-restart-before-swap "${MOCK_RESTART_BEFORE_SWAP}"
else
  echo "[ERROR] deploy_blue_green.py 부재 — ADR-061 Python 로직 파일 필요" >&2
  exit 1
fi
