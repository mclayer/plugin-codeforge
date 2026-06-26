#!/usr/bin/env bash
# scripts/check-responsibility-topology.sh — cross-repo 책임 배치 메타불변식 게이트 thin bash wrapper
#
# CFP-2422 / ADR-131 §결정 3/4 (Epic CFP-2418 Story 2) — consumer overlay project.yaml 의
#   repo_topology 섹션 메타불변식((a)고아 (b)중복소유 (c)거친파생 + layer 분리 fail-open) 검증.
# ADR-061: Python entry-point + thin bash wrapper convention (python3 직접 실행 — NO heredoc, NO logic).
#
# 입력: 인자 없음 = repo-root(스크립트 위치 기준 2-level up) 의 consumer overlay scan (CI/production).
#       --root <PATH>            = 지정 repo-root scan (self-test fixture 경로).
#       --changed-repos r1,r2,.. = actual_changed_repos sentinel 주입 (fixture — production git diff 우회).
#
# Usage:
#   bash scripts/check-responsibility-topology.sh
#   bash scripts/check-responsibility-topology.sh --root /path/to/fixture-root
#   bash scripts/check-responsibility-topology.sh --root /path/to/fixture-root --changed-repos repo-a,repo-b
#
# Exit codes (ADR-060 §결정 5 3-tier — warning tier):
#   0 = PASS (메타불변식 위반 0) OR data-absence honest no-op (fail-open)
#   1 = 메타불변식 위반 1+ (고아/중복소유/거친파생 — workflow 의 continue-on-error 로 비차단, advisory)
#   2 = SETUP error (python3 미설치 / yaml 파싱 실패 / 스키마 무효 / 인자 형식 오류) — fail-closed
#
# graceful-degradation (change-plan §3.6 / §7.5-FO): data-absence(A)=fail-open(exit 0, Python lib 내부
#   처리, path-filter skip 금지 — required check Pending trap 차단) / setup-error(B)=fail-closed(exit 2).
#
# Prior art: scripts/check-whitelist-manifest-3way.sh (CFP-2412, ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인 (부재 = setup-error B = fail-closed exit 2)
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-responsibility-topology: python3 not installed (setup-error, fail-closed exit 2)"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — python 직접 실행 + exit code passthrough (인자 그대로 forward).
python3 "${_SCRIPT_DIR}/lib/check_responsibility_topology.py" "$@"
