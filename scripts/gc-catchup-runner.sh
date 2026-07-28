#!/usr/bin/env bash
# scripts/gc-catchup-runner.sh — SessionStart 2차 트리거(detached lazy GC)의 분리 자식 본체.
#
# Carrier: CFP-2822 ⑤ 크래시 보완 트리거 (AC-3 / AC-13)
#          ADR-169 §결정4 (SessionStart detached lazy GC 재해석 SSOT)
#
# 책임 경계:
#   - hooks/session-start-gc-catchup 가 경량 판정(임계 초과) 후 detach 로 fire-and-forget 실행하는
#     "분리 자식" 본체. 세션 개시 경로에서 분리된 백그라운드 프로세스로 돈다(부모 즉시 반환).
#   - 실 GC 로직은 check-worktree-stale.sh 가 SSOT — 본 runner 는 (cwd 이동 + 로그 header +
#     check-worktree-stale.sh 실행 + 로그 append) passthrough 뿐. 삭제/판정 로직 미소유.
#   - BYPASS_WORKTREE_GC · mkdir lock · cooldown · E10 double-delete 0 = 전부 check-worktree-stale.sh
#     가 자체 존중(§5.3 3중 방어). runner 는 그 위임 계약을 재구현하지 않는다.
#
# args: $1=run_cwd  $2=gc_script(check-worktree-stale.sh 절대경로)  $3=log_file
#
# 세션 teardown/개시 어떤 것도 block 하지 않도록 exit 0 고정(부모는 이미 반환됨 — 자식 실패는 무해).
set -uo pipefail

run_cwd="${1:-}"
gc_script="${2:-}"
log_file="${3:-}"

# GC 스크립트 부재 = graceful skip (non-blocking)
[[ -n "$gc_script" && -f "$gc_script" ]] || exit 0

# 세션 cwd(등록 worktree 가 매달린 repo)로 이동 — check-worktree-stale.sh 가 여기서
# git rev-parse --show-toplevel 로 대상 repo 를 찾는다. 실패해도 non-blocking(NOT_A_GIT_REPO skip).
if [[ -n "$run_cwd" ]]; then
  cd "$run_cwd" 2>/dev/null || true
fi

# 로그 append (SessionEnd backstop 과 동일 파일 — 감사 일원화). log_file 미지정 시 stdout.
if [[ -n "$log_file" ]]; then
  {
    printf '=== [session-start catch-up GC] %s ===\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    bash "$gc_script" 2>&1 || true
  } >> "$log_file" 2>&1
else
  printf '=== [session-start catch-up GC] %s ===\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  bash "$gc_script" 2>&1 || true
fi

exit 0
