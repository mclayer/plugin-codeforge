#!/bin/bash
set -euo pipefail

# ── 상수 ──────────────────────────────────────────────────────────────────────
INSTALL_DIR="/opt/mctrader"
DATA_DIR="/var/data/mctrader"
LOG_DIR="/var/log/mctrader"
SERVICE_USER="mctrader"
SERVICE_GROUP="mctrader"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ── root 권한 확인 ─────────────────────────────────────────────────────────────
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    echo "ERROR: 이 스크립트는 root 권한으로 실행해야 합니다." >&2
    exit 1
fi

echo "==> [1/8] 시스템 유저 생성: ${SERVICE_USER}"
if ! id -u "${SERVICE_USER}" &>/dev/null; then
    useradd \
        --system \
        --no-create-home \
        --shell /usr/sbin/nologin \
        --comment "mctrader service account" \
        "${SERVICE_USER}"
    echo "    유저 생성 완료: ${SERVICE_USER}"
else
    echo "    유저 이미 존재, 건너뜀: ${SERVICE_USER}"
fi

echo "==> [2/8] 설치 디렉토리 생성: ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
chown "${SERVICE_USER}:${SERVICE_GROUP}" "${INSTALL_DIR}"
chmod 755 "${INSTALL_DIR}"
echo "    완료: ${INSTALL_DIR}"

echo "==> [3/8] 데이터 및 로그 디렉토리 생성"
mkdir -p "${DATA_DIR}"
chown "${SERVICE_USER}:${SERVICE_GROUP}" "${DATA_DIR}"
chmod 750 "${DATA_DIR}"
echo "    완료: ${DATA_DIR}"

mkdir -p "${LOG_DIR}"
chown "${SERVICE_USER}:${SERVICE_GROUP}" "${LOG_DIR}"
chmod 750 "${LOG_DIR}"
echo "    완료: ${LOG_DIR}"

echo "==> [4/8] 프로젝트 파일 동기화: ${PROJECT_ROOT} → ${INSTALL_DIR}"
# .git, __pycache__, *.pyc 제외하고 복사 (idempotent)
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

echo "==> [5/8] Python venv 생성: ${INSTALL_DIR}/venv"
if [[ ! -f "${INSTALL_DIR}/venv/bin/activate" ]]; then
    python3 -m venv "${INSTALL_DIR}/venv"
    echo "    venv 생성 완료"
else
    echo "    venv 이미 존재, 재사용"
fi

echo "==> [6/8] pip install -e ."
"${INSTALL_DIR}/venv/bin/pip" install --quiet --upgrade pip
"${INSTALL_DIR}/venv/bin/pip" install --quiet -e "${INSTALL_DIR}"
echo "    패키지 설치 완료"

echo "==> [7/8] systemd 서비스 파일 설치"
cp "${SCRIPT_DIR}/mctrader-collector.service" /etc/systemd/system/mctrader-collector.service
chmod 644 /etc/systemd/system/mctrader-collector.service
echo "    복사 완료: /etc/systemd/system/mctrader-collector.service"

systemctl daemon-reload
echo "    daemon-reload 완료"

echo "==> [8/8] 서비스 활성화: mctrader-collector"
systemctl enable mctrader-collector
echo "    enable 완료"

echo ""
echo "설치 완료."
echo "  .env 파일 위치: ${INSTALL_DIR}/.env"
echo "  서비스 시작:    systemctl start mctrader-collector"
echo "  로그 확인:      journalctl -u mctrader-collector -f"
