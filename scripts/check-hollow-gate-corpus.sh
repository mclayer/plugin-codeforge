#!/usr/bin/env bash
# scripts/check-hollow-gate-corpus.sh — hollow-gate corpus 판정 하네스 thin bash wrapper.
#
# CFP-2963 / ADR-175 — 커밋된 2-arm corpus(게이트 artifact + kill/clean/empty/xkill fixture leg)를
#   **실행**해 표본이 LIVE(결함 앞 RED) 인지 HOLLOW(결함 앞에서도 GREEN) 인지 arm-invariant 로 분류하는
#   동적 메타-게이트. 판정 입력 = leg 실행 관측 마커뿐이며 선언 arm(L/H)은 판정 함수에 도달하지 않는다.
#   천장: 등재 표본의 관측 기반 verdict 까지만 — corpus 밖 게이트 일반으로 외삽하지 않는다.
#   presence != truth. 상세 = python core docstring (scripts/lib/check_hollow_gate_corpus.py).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 직접 실행 — NO heredoc, NO logic).
#   check-hard-gate-self-verification.sh 동형.
#
# CLI 계약 (고정 — self-test + workflow 가 소비; 임의 변경 금지):
#   scripts/check-hollow-gate-corpus.sh [--repo-root DIR] [--manifest FILE] [--baseline FILE]
#                                       [--init-baseline] [--allow-baseline-shrink] [--reason TEXT]
#     --repo-root               (optional) repo 루트 (기본 = __file__ 기준 parents[2]).
#     --manifest                (optional) sidecar manifest (기본 = <DIR>/docs/hollow-gate-corpus-manifest.yaml).
#     --baseline                (optional) census baseline (기본 = <DIR>/docs/hollow-gate-corpus-baseline.yaml).
#     --init-baseline --reason  baseline **부재 시에만** 최초 각인. 이미 있으면 거부(exit 3).
#     --allow-baseline-shrink --reason  기존 baseline 재기록(사유 각인). 플래그·사유 없이는 거부.
#   `--write-baseline` 형 자기 하향 재생성 경로는 부재 (ADR-175 명시 금지).
#
# Usage:
#   bash scripts/check-hollow-gate-corpus.sh
#
# Exit codes (fail-closed):
#   0 = PASS (arm-L 전건 LIVE + arm-H 전건 HOLLOW + 축별 baseline 하한 충족 + INDETERMINATE 0).
#   1 = FAIL (N_indeterminate >= 1 / verdict 불충족 / baseline 하한 미달 /
#             kill_target_stage in fail_stage(xkill) / IC assert 미성립 / pyyaml 부재 = 판정불가).
#   2 = argparse usage/parse 오류 전용.
#   3 = substrate-failure (분모 0 / baseline 부재·digest 불일치 / stamp drift / bijection 파손 /
#             exec-tree blinding 파손 / recipe 대상이 samples[] 밖 / exit_space 미선언 / 금지키).
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
  echo "::error::check-hollow-gate-corpus: python3/python not installed (판정불가, fail-closed exit 1)" >&2
  exit 1
fi

exec "$_PY" "${_SCRIPT_DIR}/lib/check_hollow_gate_corpus.py" "$@"
