#!/usr/bin/env bash
# scripts/check-whitelist-manifest-3way.sh — whitelist↔manifest↔templates 3-way 일관성 게이트 thin bash wrapper
#
# CFP-2412 / ADR-130 §결정 3/5 (Epic CFP-2394 Story D) — consumer-applicability whitelist ↔
#   배포 source(templates/github-workflows/) ↔ closure manifest 의 삼각 일관성 검증.
#   방향1 whitelist→templates 실존 / 방향2 manifest dep→whitelist subset / 방향3 whitelist→manifest
#   closure-asset 등재 / depth-2 hard-exit 데이터 등재완전성.
# ADR-061: Python entry-point + thin bash wrapper convention (python3 직접 실행 — NO heredoc, NO logic).
#
# 입력: 인자 없음 = repo-root(스크립트 위치 기준 2-level up) 의 3 소스 scan (CI/production 경로).
#       --root <PATH> = 지정 repo-root scan (self-test fixture 경로).
#
# Usage:
#   bash scripts/check-whitelist-manifest-3way.sh
#   bash scripts/check-whitelist-manifest-3way.sh --root /path/to/fixture-root
#
# Exit codes (ADR-060 §결정 5 3-tier — warning tier):
#   0 = PASS (violation 0) OR data-absence honest no-op (fail-open)
#   1 = violation 1+ (warning emit — workflow 의 continue-on-error 로 비차단, advisory only)
#   2 = SETUP error (python3 미설치 / 인자 형식 오류 / read 권한 거부) — fail-closed
#
# graceful-degradation (change-plan §3.5): data-absence(A)=fail-open(exit 0, Python lib 내부 처리,
#   path-filter skip 금지 — required check Pending trap 차단) / setup-error(B)=fail-closed(exit 2).
#
# Prior art: scripts/check-spawn-prompt-fact-verify.sh (CFP-2383, ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인 (부재 = setup-error B = fail-closed exit 2)
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-whitelist-manifest-3way: python3 not installed (setup-error, fail-closed exit 2)"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — python 직접 실행 + exit code passthrough (인자 그대로 forward).
python3 "${_SCRIPT_DIR}/lib/check_whitelist_manifest_3way.py" "$@"
