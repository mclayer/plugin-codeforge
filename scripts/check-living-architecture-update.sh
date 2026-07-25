#!/usr/bin/env bash
# scripts/check-living-architecture-update.sh
# CFP-2813 Phase 2 — Living Architecture per-PR 최신성 게이트 thin wrapper (ADR-061)
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (변경 파일 수집은 collect_changed_files.sh 공유 헬퍼 재사용 — D8)
#
# Usage:
#   bash scripts/check-living-architecture-update.sh
#
# 변경 파일 = collect_changed_files.sh (GITHUB_BASE_REF 분기 내장) 로 수집해 python core 에 stdin 주입.
# PR body(marker 입력) = env PR_BODY / LIVING_ARCH_PR_BODY_FILE (python core 가 읽음).
#
# Exit code (python core 계약):
#   0 PASS(명시 Success·honest no-op 포함) / 1 위반(4 범주) / 2 meta-error(fail-closed)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_living_architecture_update.py"
COLLECT_LIB="${SCRIPT_DIR}/lib/collect_changed_files.sh"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-living-architecture-update] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi
if [ ! -f "${COLLECT_LIB}" ]; then
  echo "[check-living-architecture-update] ERROR: collect_changed_files.sh not found: ${COLLECT_LIB}" >&2
  exit 2
fi

SCRIPT_NAME="check-living-architecture-update"
# shellcheck source=scripts/lib/collect_changed_files.sh
. "${COLLECT_LIB}"

# 전 변경 파일 (필터 없음 — 분류는 python core 가 수행). '.' = 모든 비어있지 않은 경로.
collect_changed_files '.' | python3 "${PYTHON_SSOT}" --changed-from-stdin "$@"
