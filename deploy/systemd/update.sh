#!/bin/bash
set -euo pipefail

# ── 상수 ──────────────────────────────────────────────────────────────────────
INSTALL_DIR="/opt/mctrader"
SERVICE_USER="mctrader"
SERVICE_GROUP="mctrader"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# ── root 권한 확인 ─────────────────────────────────────────────────────────────
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    echo "ERROR: 이 스크립트는 root 권한으로 실행해야 합니다." >&2
    exit 1
fi

echo "==> [1/4] git pull"
git -C "${PROJECT_ROOT}" pull
echo "    완료"

echo "==> [2/4] 프로젝트 파일 동기화: ${PROJECT_ROOT} → ${INSTALL_DIR}"
rsync -a --delete \
    --exclude='.git/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='.env' \
    --exclude='deploy/' \
    "${PROJECT_ROOT}/" "${INSTALL_DIR}/"
chown -R "${SERVICE_USER}:${SERVICE_GROUP}" "${INSTALL_DIR}"
echo "    완료"

echo "==> [3/4] pip install -e ."
"${INSTALL_DIR}/venv/bin/pip" install --quiet -e "${INSTALL_DIR}"
echo "    완료"

echo "==> [4/4] 서비스 재시작: mctrader-collector"
systemctl restart mctrader-collector
echo "    재시작 완료"

echo ""
systemctl status mctrader-collector --no-pager
