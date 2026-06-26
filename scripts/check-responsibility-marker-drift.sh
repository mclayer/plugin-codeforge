#!/usr/bin/env bash
# scripts/check-responsibility-marker-drift.sh — declared-marker layer(L1 코드→책임) drift 게이트 thin bash wrapper
#
# CFP-2428 / ADR-131 Amendment 1 (Epic CFP-2418 deferred FU) — consumer overlay project.yaml 의
#   repo_topology.responsibility_markers 섹션 drift((a)unmarked (b)불일치 (c)stale + layer 분리
#   fail-open) 검증. 기계 = 구조 대조 only (의미정합 = 리뷰어 attestation, ADR-131 §결정4 / ADR-119).
# ADR-061: Python entry-point + thin bash wrapper convention (python3 직접 실행 — NO heredoc, NO logic).
#
# 입력: 인자 없음 = repo-root(스크립트 위치 기준 2-level up) 의 consumer overlay scan (CI/production).
#       --root <PATH>            = 지정 repo-root scan (self-test fixture 경로).
#
# Usage:
#   bash scripts/check-responsibility-marker-drift.sh
#   bash scripts/check-responsibility-marker-drift.sh --root /path/to/fixture-root
#
# Exit codes (ADR-060 §결정 5 3-tier — warning tier):
#   0 = PASS (drift 0) OR data-absence honest no-op (fail-open)
#   1 = drift 위반 1+ (unmarked/불일치/stale — workflow 의 continue-on-error 로 비차단, advisory)
#   2 = SETUP error (python3 미설치 / yaml 파싱 실패 / 스키마 무효 / 인자 형식 오류) — fail-closed
#
# graceful-degradation (change-plan §3.2 / §7.1): data-absence(A)=fail-open(exit 0, Python lib 내부
#   처리, path-filter skip 금지 — required check Pending trap 차단) / setup-error(B)=fail-closed(exit 2).
#
# Prior art: scripts/check-responsibility-topology.sh (CFP-2422, ADR-061 thin wrapper — L2 게이트 sibling).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인 (부재 = setup-error B = fail-closed exit 2)
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-responsibility-marker-drift: python3 not installed (setup-error, fail-closed exit 2)"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — python 직접 실행 + exit code passthrough (인자 그대로 forward).
python3 "${_SCRIPT_DIR}/lib/check_responsibility_marker_drift.py" "$@"
