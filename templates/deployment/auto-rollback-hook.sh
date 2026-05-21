#!/usr/bin/env bash
# templates/deployment/auto-rollback-hook.sh
# CFP-1059-S6 — green health 실패 -> blue 복귀 (swap revert, ADR-087 §결정 5)
#
# §7.4 empirical-source:
#   healthcheck window 60s: ADR-087 §결정 5 (dimension: latency + count)
#   3시간 보존 window 내 rollback 가능: Issue #1059 카테고리 3/9 (dimension: lifecycle)
#
# §11.6 idempotency: blue 이미 active -> no-op (rollback 재실행 안전)
# fail-loud: 롤백 시 사용자 알림 의무 (silent 차단)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ROLLBACK_PY="${WORKTREE_ROOT}/scripts/auto_rollback_hook.py"

REPO=""
HOST=""

usage() {
  echo "Usage: $0 --repo <repo> --host <host>"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --host) HOST="$2"; shift 2 ;;
    --help|-h) usage ;;
    *)      echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${REPO}" || -z "${HOST}" ]]; then
  echo "[ERROR] --repo, --host 필수" >&2
  exit 1
fi

MOCK_DOCKER="${_CFP1059_MOCK_DOCKER:-0}"
MOCK_SSH="${_CFP1059_MOCK_SSH:-0}"
MOCK_HEALTH="${_CFP1059_MOCK_HEALTH:-real}"
MOCK_BLUE_ACTIVE="${_CFP1059_MOCK_BLUE_ACTIVE:-0}"
MOCK_WITHIN_RETENTION="${_CFP1059_MOCK_WITHIN_RETENTION:-0}"

echo "=== auto-rollback-hook.sh ==="
echo "repo=${REPO} host=${HOST}"

if [[ -f "${ROLLBACK_PY}" ]]; then
  PYTHONUTF8=1 python3 "${ROLLBACK_PY}" \
    --repo "${REPO}" \
    --host "${HOST}" \
    --mock-docker "${MOCK_DOCKER}" \
    --mock-ssh "${MOCK_SSH}" \
    --mock-health "${MOCK_HEALTH}" \
    --mock-blue-active "${MOCK_BLUE_ACTIVE}" \
    --mock-within-retention "${MOCK_WITHIN_RETENTION}"
else
  echo "[ERROR] auto_rollback_hook.py 부재 — ADR-061 Python 로직 파일 필요" >&2
  exit 1
fi
