#!/usr/bin/env bash
# templates/deployment/expand-migration-apply.sh
# CFP-1059-S6 — 마이그레이션 step 2: expand apply (source-first, ADR-089 원칙 2)
#
# §11.1 단계 2: 확장 마이그레이션 apply (green start 직전)
#   RDB = Alembic upgrade head (revision-based, idempotent)
#   빅데이터 = custom expand (rekey-migration oneshot, idempotent marker check)
#
# §11.6 idempotency:
#   Alembic = already at head -> no-op
#   빅데이터 = marker check 후 skip
#   partial apply 검출 -> fail-loud (exit 비0)
#
# §7.4 empirical-source:
#   expand timeout = Alembic transaction-per-revision (no fixed timeout)
#   batch size = consumer 데이터 volume 의존 (design-time 미고정)
#   [empirical-source: TBD — consumer 데이터 volume 실측 후 lock-in, dimension: volume]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
EXPAND_PY="${WORKTREE_ROOT}/scripts/expand_migration_apply.py"

MIGRATION_TYPE=""
TARGET=""

usage() {
  echo "Usage: $0 --type <alembic|bigdata> --target <head|rekey-migration>"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)   MIGRATION_TYPE="$2"; shift 2 ;;
    --target) TARGET="$2";         shift 2 ;;
    --help|-h) usage ;;
    *)        echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${MIGRATION_TYPE}" || -z "${TARGET}" ]]; then
  echo "[ERROR] --type, --target 필수" >&2
  exit 1
fi

MOCK_ALEMBIC="${_CFP1059_MOCK_ALEMBIC:-0}"
MOCK_ALEMBIC_AT_HEAD="${_CFP1059_MOCK_ALEMBIC_AT_HEAD:-0}"
MOCK_BIGDATA_EXPAND="${_CFP1059_MOCK_BIGDATA_EXPAND:-0}"
MOCK_BIGDATA_ALREADY_DONE="${_CFP1059_MOCK_BIGDATA_ALREADY_DONE:-0}"
MOCK_PARTIAL_APPLY="${_CFP1059_MOCK_PARTIAL_APPLY:-0}"

echo "=== expand-migration-apply.sh ==="
echo "type=${MIGRATION_TYPE} target=${TARGET}"
echo "[empirical-source: TBD — batch size consumer 데이터 volume 실측 후 lock-in, dimension: volume]"

if [[ -f "${EXPAND_PY}" ]]; then
  PYTHONUTF8=1 python3 "${EXPAND_PY}" \
    --type "${MIGRATION_TYPE}" \
    --target "${TARGET}" \
    --mock-alembic "${MOCK_ALEMBIC}" \
    --mock-alembic-at-head "${MOCK_ALEMBIC_AT_HEAD}" \
    --mock-bigdata-expand "${MOCK_BIGDATA_EXPAND}" \
    --mock-bigdata-already-done "${MOCK_BIGDATA_ALREADY_DONE}" \
    --mock-partial-apply "${MOCK_PARTIAL_APPLY}"
else
  echo "[ERROR] expand_migration_apply.py 부재 — ADR-061 Python 로직 파일 필요" >&2
  exit 1
fi
