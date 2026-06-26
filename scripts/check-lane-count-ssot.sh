#!/usr/bin/env bash
# scripts/check-lane-count-ssot.sh — lane-count SSOT consistency 게이트 thin bash wrapper
#
# CFP-2426 / ADR-060 Amendment 19 §결정 33 — canonical 작업레인 수(10, ADR-125 Amendment 1)
#   SSOT mechanical consistency enforcement. 현재-상태 lane-count 단언(N 레인 / N번째 lane /
#   레인 N개, N≠10) 가 canonical=10 과 어긋나는지 grep-기반 검출 + 5축 allowlist false-positive 차단.
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-lane-count-ssot.sh check [--repo-root <path>] [--paths <glob> ...]
#   bash scripts/check-lane-count-ssot.sh        # 인자 없으면 check default
#
# Exit codes (ADR-060 §결정 15 3-tier — warning tier):
#   0 = PASS (FLAG 0)
#   1 = FLAG 1+ (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
#   2 = SETUP error (검사 경로 부재 / python3 미설치 / 파일 read 실패)
#
# Prior art: scripts/check-deferred-followup-reconcile.sh / scripts/check-governance-drift.sh (ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-lane-count-ssot-infra-error] check-lane-count-ssot: python3 not installed"
  exit 2
}

# 인자 없으면 check 서브커맨드 default (workflow run: 본문 단순화)
if [ "$#" -eq 0 ]; then
  set -- check
fi

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_lane_count_ssot.py" "$@"
