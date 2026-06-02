#!/usr/bin/env bash
# CFP-136 — Stale worktree detection + auto-prune.
#
# Stale 정의 (CFP red-team 정정): worktree 는 아래 4 조건 ALL 성립 시에만 prune.
#   1. age > STALE_DAYS (기본 7일)
#   2. branch 가 MERGED (squash-merge 친화 — `gh pr list --state merged --head <branch>` 판정).
#      gh 부재/미인증/network 실패 시 → fail-safe: prune 하지 않고 보존 + 경고.
#   3. worktree 가 CLEAN — uncommitted/untracked 변경 0 (`git status --porcelain` 빈 출력).
#      변경이 하나라도 있으면 절대 prune 금지 (data-loss 가드, 필수).
#   4. 현재/main worktree 아님 + `locked` 아님 (git worktree list --porcelain `locked` flag 존중).
#
# 이전 결함: 기준이 "age>7d AND origin 브랜치 부재" 였음. 이 repo 는 SQUASH merge +
# PR 브랜치 자동 삭제 안 함 → merge 된 브랜치도 origin 에 영원히 resolve → prune 0
# (~168 worktree 누적). 또 단일 WORKTREE_BASE prefix 필터로 다른 base 의 worktree ~30% 누락.
#
# SessionStart hook 에서 호출 권장 (always exit 0, info logging).
#
# Output contract (downstream 의존 — 변경 금지):
#   - stdout 마지막 줄: "[stale-check] DONE: pruned=N"
#   - prune 시 stdout: "[stale-check] PRUNING ..." 줄
#
# Testability: git / gh 호출은 GC_GIT_BIN / GC_GH_BIN env 로 override 가능 (test stub 주입).

set -uo pipefail

# git/gh 호출 wrapper — test 에서 stub 주입 가능.
GC_GIT_BIN="${GC_GIT_BIN:-git}"
GC_GH_BIN="${GC_GH_BIN:-gh}"
_git() { "$GC_GIT_BIN" "$@"; }
_gh()  { "$GC_GH_BIN" "$@"; }

# BYPASS: BYPASS_WORKTREE_GC=1 skips all origin contact + prune (debugging only)
if [[ "${BYPASS_WORKTREE_GC:-}" == "1" ]]; then
  echo "[stale-check] BYPASS_WORKTREE_GC=1, skipping" >&2
  exit 0
fi

REPO_ROOT="$(_git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[stale-check] NOT_A_GIT_REPO — skipping (non-blocking)" >&2
  exit 0
}

STALE_DAYS="${STALE_DAYS:-7}"
# merged 판정에 쓰는 PR state. 기본 merged. closed 도 포함하려면 GC_PR_STATE=closed.
GC_PR_STATE="${GC_PR_STATE:-merged}"
PRUNED=0

# gh 가용성 1회 평가 (인증/network 포함). 불가 시 prune 단계 진입 자체를 막아 fail-safe.
GH_OK=0
if command -v "$GC_GH_BIN" >/dev/null 2>&1; then
  if _gh auth status >/dev/null 2>&1; then
    GH_OK=1
  else
    echo "[stale-check] WARN: gh 미인증 — merged 판정 불가, 이번 pass 는 prune 하지 않음 (fail-safe)" >&2
  fi
else
  echo "[stale-check] WARN: gh 부재 — merged 판정 불가, 이번 pass 는 prune 하지 않음 (fail-safe)" >&2
fi

# branch 가 merged PR 을 가졌는지 판정. 성공 + 1건 이상 → 0(merged), 그 외 → 1.
# gh 자체 실패(network 등) 시에도 1 반환 → caller 가 prune 안 함 (fail-safe).
is_branch_merged() {
  local branch="$1" out count
  out="$(_gh pr list --state "$GC_PR_STATE" --head "$branch" --json number 2>/dev/null)" || return 1
  [[ -z "$out" ]] && return 1
  # JSON array 안 number 개수. jq 없이 "number" 등장 횟수로 세어 의존성 최소화.
  count="$(printf '%s' "$out" | grep -o '"number"' | wc -l | tr -d '[:space:]')"
  [[ "${count:-0}" -ge 1 ]] && return 0 || return 1
}

# worktree 가 dirty (uncommitted/untracked) 인지. dirty → 0, clean → 1.
is_worktree_dirty() {
  local wt="$1" porcelain
  porcelain="$(_git -C "$wt" status --porcelain 2>/dev/null)" || return 0  # status 실패 = 보수적으로 dirty 취급
  [[ -n "$porcelain" ]] && return 0 || return 1
}

# worktree 에 origin 에 push 안 된(=merged PR 에 미반영) 로컬 commit 이 있는지.
# upstream/origin/main 기준으로 ahead commit 존재 시 → 0(unpushed), 아니면 1.
has_unpushed_commits() {
  local wt="$1" branch="$2" base ahead
  # 우선 tracking upstream 과 비교, 없으면 origin/main 과 비교.
  if _git -C "$wt" rev-parse --abbrev-ref "@{upstream}" >/dev/null 2>&1; then
    ahead="$(_git -C "$wt" rev-list --count "@{upstream}..HEAD" 2>/dev/null || echo 0)"
  else
    base="origin/main"
    _git -C "$wt" rev-parse --verify "$base" >/dev/null 2>&1 || base="main"
    ahead="$(_git -C "$wt" rev-list --count "$base..HEAD" 2>/dev/null || echo 0)"
  fi
  [[ "${ahead:-0}" -gt 0 ]] && return 0 || return 1
}

# git worktree list --porcelain 을 record 단위로 파싱.
# 각 record: "worktree <path>" / "HEAD <sha>" / "branch refs/heads/<name>" / "locked [reason]" / "bare" / 빈줄
WT_PATH=""
WT_BRANCH=""
WT_LOCKED=0
WT_BARE=0

evaluate_worktree() {
  # 한 worktree record 평가. 모든 위험 연산은 || 로 감싸 한 worktree 실패가 pass 를 abort 못 하게.
  local wt_path="$1" branch="$2" locked="$3" bare="$4"

  [[ -z "$wt_path" ]] && return 0

  # main / primary repo worktree 는 건너뜀
  if [[ "$wt_path" == "$REPO_ROOT" ]]; then
    return 0
  fi
  # bare worktree 건너뜀
  if [[ "$bare" == "1" ]]; then
    return 0
  fi
  # locked worktree 절대 prune 금지
  if [[ "$locked" == "1" ]]; then
    echo "[stale-check] KEEP (locked): $wt_path" >&2
    return 0
  fi
  # 경로 부재 (이미 사라짐) → prune 대상 아님, git prune 이 정리
  if [[ ! -d "$wt_path" ]]; then
    return 0
  fi

  # 조건 1: age > STALE_DAYS
  if [[ -z "$(find "$wt_path" -maxdepth 0 -mtime "+$STALE_DAYS" 2>/dev/null)" ]]; then
    return 0  # 충분히 오래되지 않음
  fi

  if [[ -z "$branch" ]]; then
    echo "[stale-check] KEEP (detached/no-branch): $wt_path" >&2
    return 0
  fi

  # 조건 3a: dirty 면 절대 prune 금지 (data-loss 가드)
  if is_worktree_dirty "$wt_path"; then
    echo "[stale-check] KEEP (dirty — uncommitted/untracked 변경 보호): $wt_path branch=$branch" >&2
    return 0
  fi

  # gh 불가 시 prune 단계 진입 금지 (fail-safe). 이미 위에서 WARN 출력함.
  if [[ "$GH_OK" != "1" ]]; then
    echo "[stale-check] KEEP (gh 불가 — merged 판정 못 함): $wt_path branch=$branch" >&2
    return 0
  fi

  # 조건 2: merged PR 판정
  if ! is_branch_merged "$branch"; then
    echo "[stale-check] KEEP (merged PR 없음/판정실패): $wt_path branch=$branch" >&2
    return 0
  fi

  # 조건 3b: merged 라도 PR 에 미반영된 로컬 commit 이 있으면 prune 금지
  if has_unpushed_commits "$wt_path" "$branch"; then
    echo "[stale-check] KEEP (unpushed local commits — data-loss 보호): $wt_path branch=$branch" >&2
    return 0
  fi

  # 모든 조건 통과 → prune
  echo "[stale-check] PRUNING (stale ${STALE_DAYS}d, merged, clean): $wt_path branch=$branch"
  if _git -C "$REPO_ROOT" worktree remove --force "$wt_path" 2>/dev/null; then
    _git -C "$REPO_ROOT" branch -D "$branch" >/dev/null 2>&1 || true
    PRUNED=$((PRUNED + 1))
  else
    echo "[stale-check] WARN: worktree remove 실패 (skip): $wt_path" >&2
  fi
  return 0
}

flush_record() {
  # 누적된 record 를 평가 후 reset. 실패해도 pass 계속.
  evaluate_worktree "$WT_PATH" "$WT_BRANCH" "$WT_LOCKED" "$WT_BARE" || true
  WT_PATH=""
  WT_BRANCH=""
  WT_LOCKED=0
  WT_BARE=0
}

# porcelain 출력을 record 단위로 읽음. 빈 줄 = record 경계.
while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    "worktree "*)
      # 새 record 시작 — 이전 record flush
      [[ -n "$WT_PATH" ]] && flush_record
      WT_PATH="${line#worktree }"
      ;;
    "branch refs/heads/"*)
      WT_BRANCH="${line#branch refs/heads/}"
      ;;
    "branch "*)
      WT_BRANCH="${line#branch }"
      ;;
    "locked"*)
      WT_LOCKED=1
      ;;
    "bare")
      WT_BARE=1
      ;;
    "")
      # record 경계
      [[ -n "$WT_PATH" ]] && flush_record
      ;;
  esac
done < <(_git -C "$REPO_ROOT" worktree list --porcelain 2>/dev/null)
# 마지막 record flush (trailing 빈 줄 없을 수 있음)
[[ -n "$WT_PATH" ]] && flush_record

echo "[stale-check] DONE: pruned=$PRUNED"
