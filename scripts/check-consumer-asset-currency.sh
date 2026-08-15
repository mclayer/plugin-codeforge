#!/usr/bin/env bash
# scripts/check-consumer-asset-currency.sh
# CFP-2978 / ADR-176 — consumer 배포 자산 currency 검출 게이트 thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-consumer-asset-currency.sh
#   bash scripts/check-consumer-asset-currency.sh --pin-file <path>
#   bash scripts/check-consumer-asset-currency.sh --offline
#
# Exit (2-tier, SSOT = check_consumer_asset_currency.py):
#   0 — 판정 완료(in-sync / drifted / not-applicable) 또는 honest-degrade
#   2 — SETUP error (pin_missing / pin_schema_invalid /
#       empty_assets_without_ssot_role / not_a_git_repo / internal)
#   ★drift 는 exit 가 아니라 stdout payload 의 verdict 로 표현된다.
#
# run-marker: stdout 첫 줄 `[consumer-asset-currency] determined=<bool> verdict=<enum> assets=<int>`
#   workflow 가 별 step 에서 이 마커 부재를 FAIL 로 판정한다.
#
# BYPASS: 없음 (미도입 — Change Plan §3.4).
#
# Evidence-checks-registry entry: consumer-asset-currency-check (ADR-176 / carrier ADR-171)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_consumer_asset_currency.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-consumer-asset-currency] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
