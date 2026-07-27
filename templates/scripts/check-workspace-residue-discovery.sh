#!/usr/bin/env bash
# templates/scripts/check-workspace-residue-discovery.sh
# ③ 잔재 발견(discovery) 스캐너 thin wrapper (CFP-2822, AC-8/8a/11/12/14/15)
#
# ADR-061 thin wrapper: POSIX dispatch only → Python SSOT (business logic 금지).
#   discover→classify→judge→execute→report 5-함수 파이프라인(orphan 3분류/scratch/stash/
#   방치 체크아웃/Temp observe-only)은 scripts/lib/check_workspace_residue_discovery.py
#   (+ flat siblings: check_orphan_worktree_classify / check_stash_aging_census /
#    check_harness_temp_residue) 가 소유. 본 wrapper 는 dispatch 만.
#
# Output contract (§4.1): stdout 마지막 줄 "[residue-scan] DONE: scanned=N flagged=M",
#   exit always 0 (advisory). 축별 라인 = "[residue-scan] KEEP (<사유>): <path>".
# 옵션: --story-key cfp-NNN (완료-게이트 재사용, Python 으로 pass-through).
# BYPASS: BYPASS_WORKSPACE_RESIDUE_SCAN=1 → skip + stderr audit(UTC ISO) + exit 0.
# fail-open: SSOT/python 부재 = exit 0 (advisory 스캐너, 트리거 차단 금지).
#
# manifest: templates/consumer-scripts.manifest 등재 (consumer 배포 — consumer 세션도 잔재 생성).
set -uo pipefail

[ "${BYPASS_WORKSPACE_RESIDUE_SCAN:-0}" = "1" ] && {
  >&2 printf '[residue-scan] BYPASS_WORKSPACE_RESIDUE_SCAN=1 — residue discovery suppressed at %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown)"
  exit 0
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/../../scripts/lib/check_workspace_residue_discovery.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[residue-scan] WARNING: Python SSOT not found, scan skipped (fail-open): ${PYTHON_SSOT}" >&2
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "${PYTHON_SSOT}" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "${PYTHON_SSOT}" "$@"
fi
echo "[residue-scan] WARNING: python not found, scan skipped (fail-open)" >&2
exit 0
