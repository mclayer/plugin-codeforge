#!/usr/bin/env bash
# templates/deployment/big-change-manual-trigger.sh
# CFP-1059-S6 — 큰 변경 수동 trigger (ADR-089 원칙 7, bash only)
#
# §3.1: hard limit 영역 = 자동 흐름 외, 수동 trigger + 점검 시간 알림
# hard limit 기준 (ADR-089 §결정 1 원칙 7):
#   column 100+ / row 1억+ / lock 5분+ / depth 7+
#
# 이 script = 자동 배포 흐름 skip + 수동 trigger 안내 (declare + 알림)
# 실 배포 action 0 (이 script 자체는 trigger 신호만)
set -euo pipefail

CHANGE_TYPE=""
DESCRIPTION=""

usage() {
  cat <<'EOF'
Usage: big-change-manual-trigger.sh --change-type <hard-limit|normal> [--description <desc>]

hard-limit 기준 (ADR-089 §결정 1 원칙 7):
  column 100+    : 대규모 스키마 변경
  row 1억+       : 대규모 데이터 마이그레이션
  lock 5분+      : 장시간 lock 필요 변경
  depth 7+       : 복잡한 의존 계층 변경

--change-type hard-limit : 자동 흐름 skip + 수동 trigger 안내
--change-type normal     : 일반 안내 (자동 흐름 유지)

EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --change-type)  CHANGE_TYPE="$2";  shift 2 ;;
    --description)  DESCRIPTION="$2"; shift 2 ;;
    --help|-h)      usage ;;
    *)              echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${CHANGE_TYPE}" ]]; then
  echo "[ERROR] --change-type 필수 (hard-limit | normal)" >&2
  exit 1
fi

echo "=== big-change-manual-trigger.sh ==="
echo "change-type=${CHANGE_TYPE}"
[[ -n "${DESCRIPTION}" ]] && echo "description=${DESCRIPTION}"

if [[ "${CHANGE_TYPE}" == "hard-limit" ]]; then
  echo ""
  echo "[MANUAL TRIGGER REQUIRED]"
  echo "이 변경은 hard limit 영역입니다 — 자동 배포 흐름 SKIP"
  echo ""
  echo "hard limit 기준 (ADR-089 §결정 1 원칙 7):"
  echo "  column 100+ / row 1억+ / lock 5분+ / depth 7+"
  echo ""
  echo "수동 절차:"
  echo "  1. 점검 시간 예약 (유지보수 window)"
  echo "  2. 팀 알림 (Slack / PagerDuty)"
  echo "  3. 백업 evidence 준비 (ADR-089 원칙 6)"
  echo "  4. 수동 trigger 승인 후 진행"
  echo ""
  echo "[empirical-source: ADR-089 §결정 1 원칙 7 — hard limit 명시]"
  # exit 0: 알림만 (자동 배포 action 0)
  exit 0
else
  echo "[INFO] 일반 변경 (normal) — 자동 배포 흐름 유지"
  echo "[INFO] 자동 흐름: consumer GitHub Actions 배포 파이프라인 (CFP-2782 — 배포 완전 위임)"
  echo "[INFO] hard limit 해당 시 --change-type hard-limit 사용"
  exit 0
fi
