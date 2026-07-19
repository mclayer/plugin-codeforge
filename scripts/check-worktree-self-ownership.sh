#!/usr/bin/env bash
# scripts/check-worktree-self-ownership.sh — worktree self-ownership 3-tuple verify thin wrapper
#
# CFP-2761 §5.2 / ADR-073 Amendment 3 §결정1-D/1-E — path-based 3-tuple 소유 검증 (HOOK-ONLY,
#   workflow:null). (a) toplevel↔worktree-list path MATCH / (b) branch↔reflog lineage /
#   (c) worktree-list∧reflog 2-source AND (reflog GC 시 (a)+(c) fallback). LIVE + FIXTURE mode.
#   subagent parallel_session_conflict verdict → re-verify warning. warning tier (advisory).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_worktree_self_ownership.py header.
#   bash scripts/check-worktree-self-ownership.sh [--repo-root DIR] \
#       [--toplevel PATH --worktree-list-file FILE --reflog-file FILE --branch NAME] \
#       [--subagent-verdict VERDICT]
#     0 = clean / mismatch warning (advisory)
#     2 = usage error OR 불완전 fixture (bad args)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-worktree-self-ownership-infra-error] check-worktree-self-ownership: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_worktree_self_ownership.py" "$@"
