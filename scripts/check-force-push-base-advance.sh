#!/usr/bin/env bash
# scripts/check-force-push-base-advance.sh — force-push pre-flight base-advance L2 CI 사후 detect thin bash wrapper
#
# CFP-2490 / ADR-135 (Epic CFP-2481 E2) — own-branch push-time race-guard 의 L2 사후 detect layer.
#   PR head 가 base 보다 BEHIND(base-advance) / base 와 diverged 인지를 git ancestry 로 실측해 warning emit.
#   force-push 는 CI 로 *차단* 불가 (발생 후 detect만, ADR-135 §결정 2) — warning tier 고정 (§결정 5).
#   진짜 pre-flight 차단(L1) = opt-in local pre-push hook (templates/.claude/hooks/pre-push.sh.sample).
# ADR-061: Python entry-point + thin bash wrapper convention (python3 직접 실행 — NO heredoc, NO logic).
#
# 입력 (인자 그대로 forward):
#   --base <ref>  = base ref (default: env BASE_REF/GITHUB_BASE_REF/main, origin/<base> 우선).
#   --head <ref>  = head ref (default: env HEAD_SHA/HEAD).
#
# Usage:
#   bash scripts/check-force-push-base-advance.sh
#   bash scripts/check-force-push-base-advance.sh --base main --head HEAD
#
# Exit codes (ADR-060 §결정 5 3-tier — warning tier):
#   0 = PASS (base-advance/divergence 0) OR data-absence honest no-op (fail-open)
#   1 = base-advance / divergence 검출 1+ (workflow 의 continue-on-error 로 비차단, advisory)
#   2 = SETUP error (python3/git 미설치 / repo 아님 / 인자 형식 오류) — fail-closed
#
# graceful-degradation (change-plan §7.4 rate-limit / §7.5): data-absence(A)=fail-open(exit 0, Python
#   lib 내부 처리 — base ref 미해결 = honest no-op) / setup-error(B)=fail-closed(exit 2).
#
# Prior art: scripts/check-responsibility-topology.sh (CFP-2422, ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인 (부재 = setup-error B = fail-closed exit 2)
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-force-push-base-advance: python3 not installed (setup-error, fail-closed exit 2)"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — python 직접 실행 + exit code passthrough (인자 그대로 forward).
python3 "${_SCRIPT_DIR}/lib/check_force_push_base_advance.py" "$@"
