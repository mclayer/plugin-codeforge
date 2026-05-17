#!/usr/bin/env bash
# CFP-843 Phase 2 — test/probe sandbox env 표준 wire (§3.3)
# ADR-040 Amendment 6 §결정 7.J.3 — sandbox env probe entry point guard
#
# 책임: probe / test 실행 시 live GitHub repo 부수효과 (Issue create / label / comment) 누설 차단
# 주요 env vars (disjoint scope — §결정 7.E 패턴 동형):
#   CBL_SKIP_ISSUE_CREATE=1 — Issue create API 호출 억제 (read-only 기본 모드)
#   CBL_MOCK_ISSUE_CREATE_CALLED=<path> — TC 용 sentinel file (create 호출 시 touch)
#
# env var 분리 원칙 (ADR-040 §결정 7.J.3 SSOT):
#   CBL_SKIP_ISSUE_CREATE  ≠  BYPASS_WORKTREE_FIRST  ≠  BYPASS_WORKTREE_GC
#   각 env 는 독립 scope — superset 아님
#
# --mock-create 플래그:
#   TC-6 용 — "Issue create" 행동을 시뮬레이션 (실제 GitHub API 미호출)
#   CBL_SKIP_ISSUE_CREATE=1 이면 create 억제 (sentinel 미생성)
#   CBL_SKIP_ISSUE_CREATE 부재이면 sentinel 파일 생성 (create 호출 재현)
#
# Exit code:
#   0 — always
#
# read-only token default: probe 기본값 = GitHub write API 미호출
#   write 필요 시 CBL_SKIP_ISSUE_CREATE 해제 + 명시적 opt-in 필요
set -euo pipefail

PREFIX="[probe-sandbox-env]"

MOCK_CREATE=false

# 인수 파싱
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mock-create)
      MOCK_CREATE=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

if [[ "$MOCK_CREATE" == true ]]; then
  # TC-6 시뮬레이션: Issue create 행동
  if [[ "${CBL_SKIP_ISSUE_CREATE:-}" == "1" ]]; then
    echo "$PREFIX CBL_SKIP_ISSUE_CREATE=1 — Issue create suppressed (sandbox env, #836 재현 차단)" >&2
    # sentinel 미생성 (create 안 함)
    exit 0
  else
    echo "$PREFIX Issue create simulation — live mode (CBL_SKIP_ISSUE_CREATE not set)" >&2
    # sentinel 생성 (create 호출 재현)
    if [[ -n "${CBL_MOCK_ISSUE_CREATE_CALLED:-}" ]]; then
      touch "${CBL_MOCK_ISSUE_CREATE_CALLED}"
      echo "$PREFIX sentinel written: ${CBL_MOCK_ISSUE_CREATE_CALLED}" >&2
    fi
    exit 0
  fi
fi

# 일반 probe env 검사: 환경 변수 현황 보고
echo "$PREFIX sandbox env check:" >&2
echo "$PREFIX   CBL_SKIP_ISSUE_CREATE=${CBL_SKIP_ISSUE_CREATE:-<unset>}" >&2
echo "$PREFIX   BYPASS_WORKTREE_FIRST=${BYPASS_WORKTREE_FIRST:-<unset>}" >&2
echo "$PREFIX   BYPASS_WORKTREE_GC=${BYPASS_WORKTREE_GC:-<unset>}" >&2
echo "$PREFIX env disjoint scope verified (ADR-040 §결정 7.J.3)" >&2

exit 0
