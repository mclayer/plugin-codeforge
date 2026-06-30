#!/usr/bin/env bash
# scripts/check-force-push-base-advance.sh — force-push base-advance 사후 detect thin bash wrapper
#
# CFP-2490 / ADR-135 (Epic CFP-2481 E2) — own-branch force-push pre-flight 가드의 L2 채널
#   (CI 사후 detect, warning tier). force-push 는 발생 후라 CI 는 차단 불가 — 사후 가시화만
#   (ADR-135 §결정 2). 진짜 pre-flight 차단은 L1 local pre-push hook (opt-in).
# ADR-061: Python entry-point + thin bash wrapper convention (exec python3 — NO heredoc, NO logic).
#
# Usage:
#   bash scripts/check-force-push-base-advance.sh --base-sha <SHA> --head-sha <SHA> [--base-ref main]
#   (또는 BASE_SHA / HEAD_SHA / BASE_REF 환경변수.)
#
# Exit codes (ADR-060 §결정 5 3-tier — warning tier):
#   0 = PASS (base-advance/divergence 0) / graceful skip (SHA 부재 / shallow checkout)
#   1 = WARN (base-advance 또는 divergence 검출 — workflow continue-on-error 로 비차단, advisory only)
#   2 = SETUP error (git 미설치 / SHA 인자 전무 / SHA 형식 무효)
#
# Prior art: scripts/check-deferred-item-recovery.sh / scripts/check-parallel-work-sentinel.sh
#   (ADR-061 thin wrapper convention).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인
command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-evidence-registry-infra-error] check-force-push-base-advance: python3 not installed"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — exec python3 (NO bash logic, NO heredoc)
exec python3 "${_SCRIPT_DIR}/lib/check_force_push_base_advance.py" "$@"
