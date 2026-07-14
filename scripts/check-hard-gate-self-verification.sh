#!/usr/bin/env bash
# scripts/check-hard-gate-self-verification.sh — hard-gate self-verification 메타-게이트 thin bash wrapper.
#
# CFP-2684 / ADR-154 — 신규 hard gate 가 self-verification 번들(positive-control self-test + empty-target/
#   unknown-input fail-closed + execution-trace + internal-control identity-probe + honest-ceiling 선언 +
#   silent-green≠silent-fallback≠honest-degrade 3-way taxonomy)을 갖췄는지 presence/shape 로 fail-closed
#   검사하는 정적 메타-게이트. 검출 sufficiency=undecidable → review-tier honest-ceiling (presence ≠ truth).
#   상세 = python core docstring (scripts/lib/check_hard_gate_self_verification.py).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 직접 실행 — NO heredoc, NO logic).
#   check-selftest-execution-liveness.sh 동형.
#
# CLI 계약 (고정 — QADev self-test + workflow 가 소비; 임의 변경 금지, fixture 는 이 계약에 맞춰 build):
#   scripts/check-hard-gate-self-verification.sh [--repo-root DIR]
#     --repo-root  (optional) repo 루트 (기본 = __file__ 기준 parents[2]).
#                  subject 발견 = <DIR>/tests/scripts/*.sh (enrollment marker 보유),
#                  concept-doc = <DIR>/docs/domain-knowledge/concept/hard-gate-self-verification.md.
#
# Usage:
#   bash scripts/check-hard-gate-self-verification.sh
#
# Exit codes (fail-closed):
#   0 = 전 fail-closed AC 통과 (enrolled 0 = honest-degrade no-op 포함).
#   1 = ≥1 위반 OR unknown/unreadable input OR python3 미설치 (fail-closed).
#   2 = argparse usage/parse 오류 전용.
#
# 인자를 core 로 그대로 forward + exit code passthrough (변형 0 — exit-masking `|| true` 없음).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# python3 우선, 부재 시 python fallback (부재 = 판정불가 = fail-closed exit 1).
if command -v python3 >/dev/null 2>&1; then
  _PY=python3
elif command -v python >/dev/null 2>&1; then
  _PY=python
else
  echo "::error::check-hard-gate-self-verification: python3/python not installed (판정불가, fail-closed exit 1)" >&2
  exit 1
fi

exec "$_PY" "${_SCRIPT_DIR}/lib/check_hard_gate_self_verification.py" "$@"
