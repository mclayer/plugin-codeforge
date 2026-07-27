#!/usr/bin/env bash
# templates/scripts/check-codeforge-scratch-ttl.sh
# ② codeforge-scratch TTL purge thin wrapper (CFP-2822, AC-5)
#
# ADR-061 thin wrapper: POSIX dispatch only → Python SSOT (business logic 금지).
#   대상 = ~/.claude/codeforge-scratch/ 내부 loose 파일 age>TTL 자동 삭제.
#   .git 보유 항목 = TTL 삭제 제외(AC-12 orphan 경로 회부). 상태파일 self-exemption
#   (~/.claude/worktree-gc-state/) 은 codeforge-scratch 밖이라 대상 아님.
#
# Output contract (§4.1): stdout 마지막 줄 "[scratch-ttl] DONE: purged=N kept=M", exit always 0.
# BYPASS: BYPASS_CODEFORGE_SCRATCH_TTL=1 → skip + stderr audit(UTC ISO) + exit 0
#   (check-worktree-stale.sh BYPASS_WORKTREE_GC 엔트리-레벨 skip 패턴 답습).
# fail-open: SSOT/python 부재 = exit 0 (SessionStart 경량 스캐너, 세션 개시 차단 금지).
#
# manifest: templates/consumer-scripts.manifest 등재 (consumer 배포 — per-user codeforge-scratch 공유).
set -uo pipefail

[ "${BYPASS_CODEFORGE_SCRATCH_TTL:-0}" = "1" ] && {
  >&2 printf '[scratch-ttl] BYPASS_CODEFORGE_SCRATCH_TTL=1 — scratch TTL purge suppressed at %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown)"
  exit 0
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/../../scripts/lib/check_codeforge_scratch_ttl.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[scratch-ttl] WARNING: Python SSOT not found, purge skipped (fail-open): ${PYTHON_SSOT}" >&2
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 "${PYTHON_SSOT}" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "${PYTHON_SSOT}" "$@"
fi
echo "[scratch-ttl] WARNING: python not found, purge skipped (fail-open)" >&2
exit 0
