#!/usr/bin/env bash
# scripts/check-selftest-execution-liveness.sh — self-test execution-liveness 메타-게이트 thin bash wrapper.
#
# CFP-2622 (Epic CFP-2602 G6) / ADR-151 — wrapper-self 의 tests/scripts/*.sh self-test corpus 를
#   "선언(declared L3 fixture)"에서 "실제 CI 실행(channel alive)"으로 승격하는 정적 메타-게이트.
#   각 self-test 의 인벤토리 enroll(silent-un-run 차단) + 실행 채널 실재·alive·형식 presence 를
#   fail-closed 로 강제한다. 상세 = python core docstring(scripts/lib/check_selftest_execution_liveness.py).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 직접 실행 — NO heredoc, NO logic).
#   check-ac-traceability-matrix.sh 동형.
#
# CLI 계약 (고정 — QADev self-test + workflow 가 소비; 임의 변경 금지):
#   scripts/check-selftest-execution-liveness.sh [--repo-root DIR] [--inventory FILE]
#     --repo-root  (optional) repo 루트 (기본 = __file__ 기준 parents[2]).
#     --inventory  (optional) 인벤토리 경로 override (기본 = <repo-root>/docs/selftest-execution-liveness-inventory.yaml).
#
# Usage:
#   bash scripts/check-selftest-execution-liveness.sh
#
# Exit codes (fail-closed):
#   0 = 전 fail-closed AC(AC-1a/2/3/5/8/9 + SCHEMA) 통과 (유일 success).
#   1 = ≥1 위반 OR 판정불가(인벤토리 부재·파싱 실패·PyYAML 부재·python3 미설치).
#   2 = argparse usage/parse 오류 전용.
#
# 인자를 core 로 그대로 forward + exit code passthrough (변형 0).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# python3 우선, 부재 시 python fallback (부재 = 판정불가 = fail-closed exit 1).
if command -v python3 >/dev/null 2>&1; then
  _PY=python3
elif command -v python >/dev/null 2>&1; then
  _PY=python
else
  echo "::error::check-selftest-execution-liveness: python3/python not installed (판정불가, fail-closed exit 1)" >&2
  exit 1
fi

exec "$_PY" "${_SCRIPT_DIR}/lib/check_selftest_execution_liveness.py" "$@"
