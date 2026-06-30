#!/usr/bin/env bash
# scripts/check-venue-shape-fidelity-presence.sh — venue 형상 재현 fidelity anchor-presence lint thin bash wrapper
#
# CFP-2504 Phase 2 / ADR-006 Amendment 1 §A1-2/A1-8 — 외부 venue/시계열 데이터 형상 재현
#   fidelity 의무의 기계적 anchor-presence lint (review-독립 CI 강제). Phase 1 은 선언적 mandate
#   (TestContractArch §8 + 설계리뷰/code-review 체크리스트) — review-의존. 본 Phase 2 = CI 기계 lint.
#   project.yaml venue.applicable: true consumer 의 docs/stories/*.md §8 에 형상 재현 선언
#   (captured-golden / 실형상-justified fixture) 또는 명시적 N/A(venue 미접촉) anchor 존재 검사.
#   "합성인지 자동판정"(본질적 fuzzy)은 scope 외 — anchor-presence 만 (ADR-006 A1-8 / ADR-119).
# ADR-061: Python entry-point + thin bash wrapper convention (python3 직접 실행 — NO heredoc, NO logic).
#
# 입력 (인자 그대로 forward):
#   --config <path>       = project.yaml 경로 (default: .claude/_overlay/project.yaml).
#   --stories-dir <dir>   = story 디렉터리 (default: docs/stories).
#
# Usage:
#   bash scripts/check-venue-shape-fidelity-presence.sh
#   bash scripts/check-venue-shape-fidelity-presence.sh --config path/to/project.yaml --stories-dir path/to/stories
#
# Exit codes (ADR-060 §결정 5 3-tier — warning tier):
#   0 = PASS (전 story 형상 anchor/N/A 존재) OR data-absence honest no-op (fail-open)
#   1 = anchor 부재 story 1+ (workflow 의 continue-on-error 로 비차단, advisory)
#   2 = SETUP error (project.yaml YAML parse 실패 / python3·PyYAML 미설치) — fail-closed
#
# graceful-degradation (change-plan §7.4 / §7.5): data-absence(A)=fail-open(exit 0, Python lib
#   내부 처리 — venue.applicable false·미주입 / docs/stories 부재 / §8 본문 부재 = honest no-op) /
#   setup-error(B)=fail-closed(exit 2).
#
# Prior art: scripts/check-force-push-base-advance.sh (CFP-2490, ADR-061 thin wrapper).

set -euo pipefail

_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python 존재 확인 (부재 = setup-error B = fail-closed exit 2)
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-venue-shape-fidelity-presence: python3 not installed (setup-error, fail-closed exit 2)"
  exit 2
}

# ADR-061 §결정 1 thin wrapper — python 직접 실행 + exit code passthrough (인자 그대로 forward).
python3 "${_SCRIPT_DIR}/lib/check_venue_shape_fidelity_presence.py" "$@"
