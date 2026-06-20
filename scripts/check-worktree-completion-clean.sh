#!/usr/bin/env bash
# check-worktree-completion-clean.sh — phase:완료 worktree-clean self-check (완료-게이트)
#
# Carrier: CFP-2377 (ADR-128 완료 단계 정식화 — 갭 A 완료-게이트)
#          ADR-040 Amendment 9 §결정 7.K (eager 정리 검증 cleanup invariant)
#          ADR-045 Amendment 13 §D-12 (phase:완료 precondition worktree-clean self-check)
#
# 책임 경계 (검증만 — 정리 실행은 GitOpsAgent eager 가 owner, ADR-040 가정 1):
#   - "완료 처리 중인 Story 의 worktree 가 eager 정리됐는가" 를 검출하는 advisory 게이트.
#   - phase:완료 transition precondition 의 (b) 로컬 check 스크립트 (Orchestrator self-check 가 호출).
#   - backstop(check-worktree-stale.sh) 과 disjoint: backstop = age 7d+ orphan(비정상 종료),
#     본 게이트 = 0일령 완료 worktree 의 eager 누락(정상 완료 경로). 둘 다 0일령이라
#     시간 disjoint 불가 → branch 패턴 + mergedAt 으로 구분 (F2 계약, 아래).
#
# 입력:
#   STORY_KEY=cfp-NNN  (필수 — 완료 처리 중인 Story. 부재 시 advisory skip + exit 0)
#
# F2 — 완료-게이트 대상 판정 계약 (ADR-040 Amendment 9 §결정 7.K, 0-context implementer 발명 금지):
#   검출 대상 = (a) ∧ ((b) OR (c)) —
#     (a) 본 Story scope : worktree branch 가 STORY_KEY (cfp-NNN) 계열
#         (Story root `cfp-NNN[-slug]` flat 또는 sub-branch `cfp-NNN/lane/*` / `cfp-NNN/fix-iter-*`).
#         타 Story worktree 는 본 게이트 대상 아님 (backstop 영역).
#     (b) sub-worktree (즉시 검출) : branch 가 `cfp-NNN/lane/<lane>[/<sub>]` 또는
#         `cfp-NNN/fix-iter-<N>` 패턴. lane/Story 완료 시 즉시 정리 대상 → 잔존 = eager 누락 검출.
#     (c) Story root (조건부 검출) : branch 가 Story root `cfp-NNN` flat 패턴이면,
#         Phase 2 PR mergedAt non-null 일 때만 검출. open(mergedAt null) = 보존 중 → 제외
#         (orphan 오판 안 함, EC-2/EC-3 순서 invariant 정합).
#   → flatten 된 worktree path (예 cfp-NNN-lane-design) 도 branch ref 기준으로 판정한다.
#
# fail-safe 4종 상속 (check-worktree-stale.sh 동형 — data-loss 방지, ADR-040 Amendment 9 §결정 7.K):
#   (1) gh 미인증/부재 → mergedAt 판정 불가 → Story root 검출 보류(advisory) + 진행 (보존)
#   (2) dirty(tracked/임시파일 외 untracked 변경) → 검출하되 절대 prune 권고 안 함 (data-loss 가드)
#   (3) data-loss 가능 hard-block 금지 — 본 게이트는 검출(보고)만, 자동 prune 0
#   (4) always exit 0 advisory — 게이트 통과/미통과 모두 exit 0 (required CI 불가, 로컬 self-check)
#
# Output contract:
#   - 검출 시 stdout: "[completion-clean] DETECT (eager 누락): <path> branch=<branch> reason=<sub|root-merged>"
#   - 마지막 줄: "[completion-clean] DONE: detected=N story=<STORY_KEY>"
#   - detected=0 = clean (eager 정리 완료) / detected>=1 = eager 누락 advisory
#
# Testability: git / gh 호출은 GC_GIT_BIN / GC_GH_BIN env 로 override (test stub 주입).
#              preview-only = GC_DRY_RUN=1 (본 게이트는 prune 안 하므로 출력 동일, 일관성 유지).
#
# Bypass:
#   BYPASS_WORKTREE_GC=1 — origin 접촉 0 + 검출 skip (check-worktree-stale.sh 와 동일 env 존중).

set -uo pipefail

# git/gh 호출 wrapper — test 에서 stub 주입 가능 (check-worktree-stale.sh 동형).
GC_GIT_BIN="${GC_GIT_BIN:-git}"
GC_GH_BIN="${GC_GH_BIN:-gh}"
_git() { "$GC_GIT_BIN" "$@"; }
_gh()  { "$GC_GH_BIN" "$@"; }

# BYPASS: BYPASS_WORKTREE_GC=1 → origin 접촉 0 + 검출 skip (debugging/offline)
if [[ "${BYPASS_WORKTREE_GC:-}" == "1" ]]; then
  echo "[completion-clean] BYPASS_WORKTREE_GC=1, skipping" >&2
  exit 0
fi

# STORY_KEY 필수 — 부재 시 advisory skip (어느 Story 완료-게이트인지 미상)
STORY_KEY="${STORY_KEY:-}"
if [[ -z "$STORY_KEY" ]]; then
  echo "[completion-clean] STORY_KEY 미지정 — skip (non-blocking advisory)" >&2
  echo "[completion-clean] DONE: detected=0 story=(none)"
  exit 0
fi
# 정규화: 소문자 + 앞뒤 공백 제거 (cfp-NNN 형태 기대)
STORY_KEY="$(printf '%s' "$STORY_KEY" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"

REPO_ROOT="$(_git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[completion-clean] NOT_A_GIT_REPO — skipping (non-blocking)" >&2
  echo "[completion-clean] DONE: detected=0 story=$STORY_KEY"
  exit 0
}

GC_TEMP_IGNORE_RE="${GC_TEMP_IGNORE_RE:-^\?\? (\.tmp|marketplace-snapshot\.json)}"
DETECTED=0

# gh 가용성 1회 평가 (mergedAt 판정용). 불가 시 Story root 검출 보류 (fail-safe 1).
GH_OK=0
if command -v "$GC_GH_BIN" >/dev/null 2>&1; then
  if _gh auth status >/dev/null 2>&1; then
    GH_OK=1
  else
    echo "[completion-clean] WARN: gh 미인증 — Story root mergedAt 판정 불가, root 검출 보류 (fail-safe)" >&2
  fi
else
  echo "[completion-clean] WARN: gh 부재 — Story root mergedAt 판정 불가, root 검출 보류 (fail-safe)" >&2
fi

# worktree 가 dirty 인지. dirty → 0, clean → 1 (check-worktree-stale.sh 동형).
#   git status 가 판정 source — status 실패(dir 부재/접근불가 등) = 보수적 dirty(0) (data-loss 가드,
#   보존 = 검출 안 함). status 가 clean(빈 출력) 이면 clean(1). 임시 파일 untracked 는 무시.
is_worktree_dirty() {
  local wt="$1" porcelain filtered
  porcelain="$(_git -C "$wt" status --porcelain 2>/dev/null)" || return 0  # status 실패 = 보수적 dirty
  [[ -z "$porcelain" ]] && return 1
  filtered="$(printf '%s\n' "$porcelain" | grep -vE "$GC_TEMP_IGNORE_RE")"
  [[ -n "$filtered" ]] && return 0 || return 1
}

# Story root branch 의 PR mergedAt 이 non-null 인지. non-null → 0, null/판정불가 → 1.
# gh pr view --json mergedAt 사용. merged PR 없음/gh 실패 → 1 (보존, fail-safe).
#   robust parsing — gh --jq 추출형(`null` / ISO timestamp) 과 raw JSON(`{"mergedAt":null}`) 양형 모두 처리.
#   "mergedAt 가 null 이거나 부재" 면 미머지(open — 보존). non-null timestamp 면 merged.
story_root_merged() {
  local branch="$1" out
  out="$(_gh pr view "$branch" --json mergedAt --jq '.mergedAt' 2>/dev/null)" || return 1
  out="$(printf '%s' "$out" | tr -d '[:space:]')"
  # 빈 출력 = PR 미상/판정 불가 → 보존 (fail-safe)
  [[ -z "$out" ]] && return 1
  # mergedAt 가 null (jq 추출형 bare `null` 또는 raw JSON `"mergedAt":null`) = open → 보존
  [[ "$out" == "null" ]] && return 1
  case "$out" in
    *'"mergedAt":null'*) return 1 ;;   # raw JSON null (stub / --jq 미적용 환경)
  esac
  # 그 외 (ISO timestamp 또는 raw JSON 안 non-null mergedAt) = merged → 검출 대상
  return 0
}

# branch 가 본 STORY_KEY 의 sub-worktree 패턴인지 (cfp-NNN/lane/* | cfp-NNN/fix-iter-*).
is_sub_branch() {
  local branch="$1"
  [[ "$branch" == "${STORY_KEY}/lane/"* ]] && return 0
  [[ "$branch" == "${STORY_KEY}/fix-iter-"* ]] && return 0
  return 1
}

# branch 가 본 STORY_KEY 의 Story root 패턴인지 (cfp-NNN flat 또는 cfp-NNN-<slug>).
is_root_branch() {
  local branch="$1"
  [[ "$branch" == "$STORY_KEY" ]] && return 0
  [[ "$branch" == "${STORY_KEY}-"* ]] && return 0
  return 1
}

# branch 가 본 STORY_KEY scope 인지 (a 조건). sub OR root.
in_story_scope() {
  local branch="$1"
  is_sub_branch "$branch" && return 0
  is_root_branch "$branch" && return 0
  return 1
}

evaluate_worktree() {
  local wt_path="$1" branch="$2" locked="$3" bare="$4"

  [[ -z "$wt_path" ]] && return 0
  [[ "$wt_path" == "$REPO_ROOT" ]] && return 0   # main / primary repo
  [[ "$bare" == "1" ]] && return 0               # bare worktree
  # NOTE: dir 존재 여부로 early-skip 하지 않는다 — dirty 판정은 git status 가 source
  #       (is_worktree_dirty). dir 부재/접근불가 ghost worktree 는 status 실패 → 보수적 dirty →
  #       보존(검출 안 함, data-loss 가드). 실 검출 대상 = 실재하는 clean sub/merged-root worktree.
  if [[ "$locked" == "1" ]]; then
    echo "[completion-clean] KEEP (locked): $wt_path" >&2
    return 0
  fi
  [[ -z "$branch" ]] && return 0                 # detached/no-branch = 본 게이트 대상 아님

  # (a) 본 Story scope 아니면 본 게이트 대상 아님 (backstop 영역)
  in_story_scope "$branch" || return 0

  # fail-safe (2): dirty(tracked/임시 외 untracked 변경) worktree = 보존 (data-loss 가드).
  #   uncommitted work 보유 = 정리됐어야 한다는 단언 불가 → eager 누락으로 flag 안 함 (보존).
  #   gh 미인증(fail-safe 1)과 동형 "보존 = 검출 안 함" 대칭.
  if is_worktree_dirty "$wt_path"; then
    echo "[completion-clean] KEEP (dirty — uncommitted 변경 보호, data-loss 가드): $wt_path branch=$branch" >&2
    return 0
  fi

  # (b) sub-worktree 잔존 = 즉시 검출 (eager 누락)
  if is_sub_branch "$branch"; then
    echo "[completion-clean] DETECT (eager 누락): $wt_path branch=$branch reason=sub"
    DETECTED=$((DETECTED + 1))
    return 0
  fi

  # (c) Story root = Phase 2 PR mergedAt non-null 일 때만 검출 (open=보존, 제외)
  if is_root_branch "$branch"; then
    if [[ "$GH_OK" != "1" ]]; then
      echo "[completion-clean] KEEP (Story root, gh 불가 — mergedAt 판정 보류): $wt_path branch=$branch" >&2
      return 0
    fi
    if story_root_merged "$branch"; then
      echo "[completion-clean] DETECT (eager 누락): $wt_path branch=$branch reason=root-merged"
      DETECTED=$((DETECTED + 1))
    else
      echo "[completion-clean] KEEP (Story root, Phase 2 PR open/mergedAt null — 보존 중): $wt_path branch=$branch" >&2
    fi
    return 0
  fi

  return 0
}

# git worktree list --porcelain record 단위 파싱 (check-worktree-stale.sh 동형).
WT_PATH=""
WT_BRANCH=""
WT_LOCKED=0
WT_BARE=0

flush_record() {
  evaluate_worktree "$WT_PATH" "$WT_BRANCH" "$WT_LOCKED" "$WT_BARE" || true
  WT_PATH=""
  WT_BRANCH=""
  WT_LOCKED=0
  WT_BARE=0
}

while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    "worktree "*)
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
      [[ -n "$WT_PATH" ]] && flush_record
      ;;
  esac
done < <(_git -C "$REPO_ROOT" worktree list --porcelain 2>/dev/null)
[[ -n "$WT_PATH" ]] && flush_record

echo "[completion-clean] DONE: detected=$DETECTED story=$STORY_KEY"
exit 0
