#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "ERROR: 이 스크립트는 macOS에서만 실행 가능합니다." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
LABEL="com.mctrader.collector"
PLIST_SRC="${SCRIPT_DIR}/${LABEL}.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/${LABEL}.plist"
LOG_DIR="${HOME}/Library/Logs/mctrader"
VENV_DIR="${PROJECT_ROOT}/venv"

echo "==> [1/5] Python venv 확인: ${VENV_DIR}"
if [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
  python3 -m venv "${VENV_DIR}"
  echo "    venv 생성 완료"
else
  echo "    venv 이미 존재, 재사용"
fi

echo "==> [2/5] pip install -e ."
"${VENV_DIR}/bin/pip" install --quiet --upgrade pip
"${VENV_DIR}/bin/pip" install --quiet -e "${PROJECT_ROOT}"
echo "    패키지 설치 완료"

echo "==> [3/5] 로그 디렉토리 생성: ${LOG_DIR}"
mkdir -p "${LOG_DIR}"
echo "    완료: ${LOG_DIR}"

echo "==> [4/5] plist 설치: ${PLIST_DST}"
mkdir -p "${HOME}/Library/LaunchAgents"
sed \
  -e "s|/Users/mctrader/mctrader|${PROJECT_ROOT}|g" \
  -e "s|/Users/mctrader/Library|${HOME}/Library|g" \
  "${PLIST_SRC}" > "${PLIST_DST}"
echo "    복사 완료: ${PLIST_DST}"

echo "==> [5/5] launchd 등록"
launchctl bootout "gui/$(id -u)" "${PLIST_DST}" 2>/dev/null || true
echo ""
echo "설치 완료."
echo "  시작:       collectorctl start"
echo "  로그 확인:  collectorctl logs"
echo "  config 경로: ${PROJECT_ROOT}/config"
