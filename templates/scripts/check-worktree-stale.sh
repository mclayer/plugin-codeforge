#!/usr/bin/env bash
# CFP-136 — Stale worktree detection + auto-prune.
#
# Stale 정의 (CFP red-team 정정): worktree 는 아래 4 조건 ALL 성립 시에만 prune.
#   1. age > STALE_DAYS (기본 7일)
#   2. branch 가 MERGED (squash-merge 친화 — `gh pr list --state merged --head <branch>` 판정).
#      gh 부재/미인증/network 실패 시 → fail-safe: prune 하지 않고 보존 + 경고.
#   3a. worktree 가 CLEAN — tracked 변경 + 알려진 임시 파일 외 untracked 변경 0.
#       (`git status --porcelain` 에서 GC_TEMP_IGNORE_RE 매치 untracked 줄만 무시. tracked 는 절대 무시 안 함.)
#       남는 변경이 하나라도 있으면 절대 prune 금지 (data-loss 가드, 필수).
#   3b. merged PR 의 head commit(headRefOid) 이후로 추가된 local commit 이 0.
#       (squash merge 는 origin/main ancestry 에 브랜치 commit 을 안 올리므로 origin/main 비교는
#        항상 ahead>0 = 거짓 양성. 그래서 "병합된 PR head 이후 추가분" 으로 판정한다.)
#   4. 현재/main worktree 아님 + `locked` 아님 (git worktree list --porcelain `locked` flag 존중).
#
# 이전 결함 1: 기준이 "age>7d AND origin 브랜치 부재" 였음. 이 repo 는 SQUASH merge +
# PR 브랜치 자동 삭제 안 함 → merge 된 브랜치도 origin 에 영원히 resolve → prune 0.
# 이전 결함 2 (본 fix 대상): 결함 1 을 gh merged-PR 판정으로 고친 뒤, data-loss 가드로
# `origin/main..HEAD > 0` (unpushed) 를 추가했는데 — squash merge 상 merged 브랜치는
# 예외 없이 ahead>0 → 모든 merged worktree 가 영구 보존 → 다시 prune 0 (~90 누적).
# 또 dirty 가드가 .tmp 등 오케스트레이션 임시 파일만 있어도 발동 → merged·clean worktree 누적.
#
# 수동/스케줄 호출 권장 (always exit 0, info logging). preview 는 GC_DRY_RUN=1.
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
# DRY_RUN: GC_DRY_RUN=1 → prune 대상만 보고하고 실제 remove 안 함 (preview).
GC_DRY_RUN="${GC_DRY_RUN:-0}"
# dirty 판정에서 무시할 untracked 줄 패턴 (오케스트레이션 임시 산출물).
# git status --porcelain 의 untracked 표기 "?? <path>" 만 대상. tracked 변경은 절대 무시 안 함.
GC_TEMP_IGNORE_RE="${GC_TEMP_IGNORE_RE:-^\?\? (\.tmp|marketplace-snapshot\.json)}"
PRUNED=0
WOULD_PRUNE=0

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

# branch 의 merged PR head commit(headRefOid) 을 stdout 으로 출력하고 0 반환.
# merged PR 없음 / gh 실패(network 등) → 빈 출력 + 1 반환 → caller 가 prune 안 함 (fail-safe).
# merged PR 은 있으나 headRefOid 미상 → 빈 출력 + 0 반환 → caller 가 보수적으로 keep (head 미상 가드).
merged_pr_head() {
  local branch="$1" out
  out="$(_gh pr list --state "$GC_PR_STATE" --head "$branch" --json number,headRefOid 2>/dev/null)" || return 1
  [[ -z "$out" ]] && return 1
  # merged PR 1건 이상인지 ("number" 존재로 판정 — jq 없이 의존성 최소화).
  printf '%s' "$out" | grep -q '"number"' || return 1
  # headRefOid 값 추출 (40자 hex). 없으면 빈 출력 (caller 가 보수적 keep).
  printf '%s' "$out" | sed -nE 's/.*"headRefOid":"([0-9a-fA-F]+)".*/\1/p' | head -1
  return 0
}

# worktree 가 dirty 인지. dirty → 0, clean → 1.
# tracked 변경은 항상 dirty. untracked 줄 중 GC_TEMP_IGNORE_RE 매치(임시 산출물)는 무시.
is_worktree_dirty() {
  local wt="$1" porcelain filtered
  porcelain="$(_git -C "$wt" status --porcelain 2>/dev/null)" || return 0  # status 실패 = 보수적으로 dirty 취급
  [[ -z "$porcelain" ]] && return 1
  filtered="$(printf '%s\n' "$porcelain" | grep -vE "$GC_TEMP_IGNORE_RE")"
  [[ -n "$filtered" ]] && return 0 || return 1
}

# merged PR head commit 이후로 추가된 local commit 이 있는지. 있음 → 0, 없음 → 1.
# squash-aware: origin/main ancestry 대신 "병합된 PR 의 head 이후 추가분" 으로 판정.
#   - merged_head 미상(빈 값) → 보수적으로 0(있음) 반환 → keep.
#   - merged_head 가 local 에 없는 SHA(force-push/rebase 등) → 판정 불가 → 0 반환 → keep.
#   - rev-list --count <merged_head>..HEAD > 0 → 병합 후 추가 commit 존재 → 0(있음).
has_commits_after_merge() {
  local wt="$1" merged_head="$2" after
  [[ -z "$merged_head" ]] && return 0
  _git -C "$wt" cat-file -e "${merged_head}^{commit}" 2>/dev/null || return 0
  after="$(_git -C "$wt" rev-list --count "${merged_head}..HEAD" 2>/dev/null || echo 1)"
  [[ "${after:-1}" -gt 0 ]] && return 0 || return 1
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

  # 조건 2: merged PR 판정 + merged head commit 확보
  local merged_head
  if ! merged_head="$(merged_pr_head "$branch")"; then
    echo "[stale-check] KEEP (merged PR 없음/판정실패): $wt_path branch=$branch" >&2
    return 0
  fi

  # 조건 3b: 병합된 PR head 이후로 추가된 local commit 이 있으면 prune 금지 (squash-aware data-loss 가드)
  if has_commits_after_merge "$wt_path" "$merged_head"; then
    echo "[stale-check] KEEP (병합 후 추가 local commit — data-loss 보호): $wt_path branch=$branch" >&2
    return 0
  fi

  # 모든 조건 통과 → prune (또는 dry-run preview)
  if [[ "$GC_DRY_RUN" == "1" ]]; then
    echo "[stale-check] DRY_RUN would-prune (stale ${STALE_DAYS}d, merged, clean): $wt_path branch=$branch"
    WOULD_PRUNE=$((WOULD_PRUNE + 1))
    return 0
  fi
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

if [[ "$GC_DRY_RUN" == "1" ]]; then
  echo "[stale-check] DRY_RUN: would_prune=$WOULD_PRUNE (no removal)" >&2
fi
echo "[stale-check] DONE: pruned=$PRUNED"
