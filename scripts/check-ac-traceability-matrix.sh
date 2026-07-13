#!/usr/bin/env bash
# scripts/check-ac-traceability-matrix.sh — AC-ID zero-drop fail-closed 게이트 thin bash wrapper
#
# CFP-2603 (Epic CFP-2602 G1) / ADR-145 — 요건 traceability zero-drop 기계 게이트.
#   AC-N ↔ §8 명명 테스트 ↔ 실 테스트파일(symbol) zero-drop 을 fail-closed 로 강제한다.
#   presence/mapping 만 강제 — semantic 완전성 미강제(AC-8 CEILING). 상세 = python core docstring.
# ADR-061 §결정 1: Python entry-point + thin bash wrapper convention (python3 직접 실행 — NO heredoc,
#   NO logic). check-venue-shape-fidelity-presence.sh 동형.
#
# CLI 계약 (고정 — QADev 가 이 시그니처를 소비; 임의 변경 금지):
#   scripts/check-ac-traceability-matrix.sh --phase <1|2> --ac-source <FILE> --rtm <FILE> [--tests-root <DIR>]
#     --phase       (required) EXPLICIT phase 신호 (1=문서·명명 / 2=구현·born-missing). diff 추론 금지.
#     --ac-source   (optional) AC 목록 문서(§5 AC 표 포함) 경로. story_uri present PR 필수 —
#                   story_uri-absent 비적용 선언(--ac-applicability-none) 시 생략(ADR-145 §결정9).
#     --rtm         (required) RTM 문서(§8 Test Contract). wrapper-self=Change Plan §8 / consumer=Story §8.
#     --tests-root  (optional) born-missing 해석 루트 (phase 2 필수).
#     --ac-applicability-none (optional) story_uri-absent 비적용 선언(ac_applicability: none 마커) EXPLICIT
#                   신호 (ADR-145 §결정9). adapter-routed INPUT — verdict=core 단일소유.
#     --none-reason (optional) 비적용 선언 사유(free-text). 빈/공백 = FAIL(AC-2 auditability). injection
#                   가드: adapter 는 env-var 로만 전달(${{ }}→run: 보간 금지).
#
#   scripts/check-ac-traceability-matrix.sh --parse-pr-body <FILE>   (CFP-2659 / ADR-145 §결정11 Amd 5)
#     PR body 마커(story_uri / ac_applicability:none / rtm_uri) 추출 → JSON 1 object stdout.
#     별 leaf(lib/ac_pr_markers.py) 로 route — 게이트 판정 아님(추출 사실만, verdict=core 단일소유).
#     위 게이트 경로(2-value exit)와 disjoint — 무침범.
#
# Usage:
#   bash scripts/check-ac-traceability-matrix.sh --phase 1 --ac-source STORY.md --rtm CHANGEPLAN.md
#   bash scripts/check-ac-traceability-matrix.sh --phase 2 --ac-source STORY.md --rtm CHANGEPLAN.md --tests-root tests
#
# Exit codes (fail-closed — AC-7 no-optout):
#   0 = PASS only (유일 success — 전 hop 통과).
#   그 외 모든 non-zero exit = fail-closed FAIL (전부 차단):
#     1 = 위반(Hop1/2/3) OR 판정불가(입력 부재·파싱 실패·RTM 미해결·tests-root 부재·python3 미설치).
#     2 = argparse 인자오류(예: `--phase 3` = choices 위반) — 여전히 non-zero=차단.
#   skip-PASS / opt-out / default-green 경로 부재.
#
# 인자를 core 로 그대로 forward + exit code passthrough (변형 0).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# python3 존재 확인 (부재 = 판정불가 = fail-closed exit 1 — 2-value 계약 유지, 다른 success 경로 없음).
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-ac-traceability-matrix: python3 not installed (판정불가, fail-closed exit 1)" >&2
  exit 1
}

# --parse-pr-body (CFP-2659) — additive route: PR body 마커 파싱 pure leaf 로 forward (exec = exit passthrough).
#   첫 인자 정확 일치 시에만 분기 → 기존 게이트 경로(2-value exit 계약) 무침범. 로직 0(ADR-061 thin wrapper).
if [ "${1:-}" = "--parse-pr-body" ]; then
  exec python3 "${_SCRIPT_DIR}/lib/ac_pr_markers.py" "$@"
fi

# ADR-061 §결정 1 thin wrapper — python 직접 실행 + exit code passthrough (인자 그대로 forward).
python3 "${_SCRIPT_DIR}/lib/check_ac_traceability_matrix.py" "$@"
