#!/usr/bin/env bash
# check-capture-gate-completion.sh — phase:완료 capture self-check (지식캡처 완료-게이트)
#
# Carrier: CFP-2392 (ADR-129 §결정 1 — OMC-adopt 지식캡처 완료시점 게이트)
#          ADR-045 Amendment 14 §D-13 (phase:완료 capture admission self-check)
#
# 책임 경계 (검증만 — capture admission 판단은 Orchestrator self-eval 가 owner):
#   - "완료 처리 시점에 재사용지식 외부화(capture) 검토 흔적이 존재하는가" 를 검출하는 advisory 게이트.
#   - 3문 admission(구글5분/코드베이스특정/실제노력) 자체 = semantic(behavioral, Orchestrator self-eval).
#     본 lint 은 "흔적 존재" presence 검사만 (honest decline — admission 판단은 lint 범위 밖).
#   - warning-tier 로컬 self-check (required CI 불가 — phase:완료 transition = Orchestrator self-write
#     + 완료 marker working-tree, ADR-099/ADR-122/ADR-128 worktree-clean 선례 동형).
#
# 입력:
#   STORY_KEY=cfp-NNN  (필수 — 완료 처리 중인 Story. 부재 시 advisory skip + exit 0 no-op)
#
# 검증 명제 (ADR-129 §결정 1 — forced-no-silent-skip):
#   완료 처리 시점에 capture admission 결과 흔적이 존재하는가 —
#     (A) capture artifact 1+ 신규 : skills/<slug>/SKILL.md 또는 docs/domain-knowledge/**/*.md 신규 파일
#         (base...HEAD diff OR staged/working-tree 신규).
#     (B) 명시적 no-capture note : "캡처 대상 검토 완료" 또는 "외부화 불요" 패턴 흔적 (commit message
#         HEAD OR working-tree 텍스트, 1줄).
#   둘 다 부재 = WARN emit (완료 전 재사용지식 외부화 검토 필요).
#   artifact 1+ OR note 1+ = PASS (no warn).
#
# fail-safe (ADR-129 §결정 1(5)) — data-loss/hard-block 금지:
#   (1) git 미인증/부재 → 검출 불가 → exit 0 보존 (hard-block 금지)
#   (2) STORY_KEY 부재 → exit 0 no-op (진행 중/미해당)
#   (3) base 비교 ref 부재(origin/main 없음) → fallback ref 시도, 모두 실패 → working-tree 신규만 검사
#   (4) always exit 0 advisory — PASS/WARN 모두 exit 0 (required CI 불가, 로컬 self-check)
#
# Output contract (QADev test 가 assert):
#   - WARN 시 stdout: "[capture-gate] WARN: capture artifact 0 + no-capture note 0 — 완료 전 재사용지식 외부화 검토 필요"
#       (sentinel = 정규식 \[capture-gate\] WARN)
#   - PASS 시 stdout: "[capture-gate] PASS: ..." (sentinel = \[capture-gate\] PASS)
#   - 마지막 줄: "[capture-gate] DONE: warn=<0|N> story=<STORY_KEY>"
#
# Testability: git 호출은 GC_GIT_BIN env 로 override (test stub 주입, worktree-clean 동형).
#
# Bypass:
#   BYPASS_CAPTURE_GATE=1 — skip + exit 0 (worktree-clean BYPASS_WORKTREE_GC 동형).

set -uo pipefail

# git 호출 wrapper — test 에서 stub 주입 가능 (check-worktree-completion-clean.sh 동형).
GC_GIT_BIN="${GC_GIT_BIN:-git}"
_git() { "$GC_GIT_BIN" "$@"; }

# BYPASS: BYPASS_CAPTURE_GATE=1 → 검출 skip (debugging/offline)
if [[ "${BYPASS_CAPTURE_GATE:-}" == "1" ]]; then
  echo "[capture-gate] BYPASS_CAPTURE_GATE=1, skipping" >&2
  exit 0
fi

# STORY_KEY 필수 — 부재 시 advisory skip (완료 처리 중 아님 / 미해당)
STORY_KEY="${STORY_KEY:-}"
if [[ -z "$STORY_KEY" ]]; then
  echo "[capture-gate] STORY_KEY 미지정 — skip (non-blocking advisory, 완료 처리 중 아님)" >&2
  echo "[capture-gate] DONE: warn=0 story=(none)"
  exit 0
fi
# 정규화: 소문자 + 앞뒤 공백 제거 (cfp-NNN 형태 기대)
STORY_KEY="$(printf '%s' "$STORY_KEY" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"

# worktree root — git repo 아니면 fail-safe exit 0 (검출 불가, 보존)
REPO_ROOT="$(_git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "[capture-gate] NOT_A_GIT_REPO — skipping (non-blocking, fail-safe)" >&2
  echo "[capture-gate] DONE: warn=0 story=$STORY_KEY"
  exit 0
}

ARTIFACT_COUNT=0
NOTE_COUNT=0

# base 비교 ref 해석 — origin/main 우선, 없으면 fallback. 모두 실패 = "" (working-tree 신규만 검사).
resolve_base_ref() {
  local ref
  for ref in "origin/main" "origin/master" "main" "master"; do
    if _git rev-parse --verify --quiet "$ref" >/dev/null 2>&1; then
      printf '%s' "$ref"
      return 0
    fi
  done
  printf ''
  return 0
}

# capture artifact 신규 검출 = skills/<slug>/SKILL.md 또는 docs/domain-knowledge/**/*.md 패턴.
#   소스 = (1) base...HEAD diff (base ref 존재 시) (2) staged + working-tree(untracked 포함) 신규.
#   패턴 매치 1+ = ARTIFACT_COUNT 증가. git 호출 실패 = 0 (fail-safe, 보존).
is_capture_path() {
  local p="$1"
  case "$p" in
    skills/*/SKILL.md)              return 0 ;;
    docs/domain-knowledge/*.md)     return 0 ;;
    docs/domain-knowledge/*/*.md)   return 0 ;;
    docs/domain-knowledge/*/*/*.md) return 0 ;;
  esac
  return 1
}

count_capture_artifacts() {
  local base files line
  base="$(resolve_base_ref)"

  # (1) base...HEAD diff (base ref 존재 시 only — A/M 신규·수정 모두 흔적으로 인정)
  if [[ -n "$base" ]]; then
    files="$(_git -C "$REPO_ROOT" diff --name-only "${base}...HEAD" 2>/dev/null)" || files=""
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      if is_capture_path "$line"; then
        ARTIFACT_COUNT=$((ARTIFACT_COUNT + 1))
      fi
    done < <(printf '%s\n' "$files")
  fi

  # (2) staged + working-tree(untracked 포함) 변경 — base 무관 신규 capture 흔적 보강.
  files="$(_git -C "$REPO_ROOT" status --porcelain --untracked-files=all 2>/dev/null)" || files=""
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    # porcelain 형식: 'XY <path>' (rename 은 'R  old -> new'). path 부분만 추출.
    local path="${line:3}"
    case "$path" in
      *' -> '*) path="${path##* -> }" ;;
    esac
    if is_capture_path "$path"; then
      ARTIFACT_COUNT=$((ARTIFACT_COUNT + 1))
    fi
  done < <(printf '%s\n' "$files")
}

# no-capture note 검출 = "캡처 대상 검토 완료" 또는 "외부화 불요" 패턴.
#   소스 = (1) 최근 commit message (HEAD) (2) working-tree 변경 파일 텍스트(staged+untracked 신규).
#   단순·robust — 패턴 1+ 매치 = NOTE_COUNT 증가. git 호출 실패 = 0 (fail-safe).
NO_CAPTURE_RE='캡처 대상 검토 완료|외부화 불요'

count_no_capture_notes() {
  local msg line path

  # (1) HEAD commit message 흔적
  msg="$(_git -C "$REPO_ROOT" log -1 --format='%B' 2>/dev/null)" || msg=""
  if [[ -n "$msg" ]] && printf '%s' "$msg" | grep -qE "$NO_CAPTURE_RE" 2>/dev/null; then
    NOTE_COUNT=$((NOTE_COUNT + 1))
  fi

  # (2) working-tree 변경 파일(staged + untracked 신규) 안 패턴 흔적
  local status_out
  status_out="$(_git -C "$REPO_ROOT" status --porcelain --untracked-files=all 2>/dev/null)" || status_out=""
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    path="${line:3}"
    case "$path" in
      *' -> '*) path="${path##* -> }" ;;
    esac
    [[ -z "$path" ]] && continue
    # 파일 존재 + 텍스트 grep (바이너리/부재 안전)
    if [[ -f "$REPO_ROOT/$path" ]]; then
      if grep -qE "$NO_CAPTURE_RE" "$REPO_ROOT/$path" 2>/dev/null; then
        NOTE_COUNT=$((NOTE_COUNT + 1))
      fi
    fi
  done < <(printf '%s\n' "$status_out")
}

count_capture_artifacts
count_no_capture_notes

WARN=0
if [[ "$ARTIFACT_COUNT" -ge 1 || "$NOTE_COUNT" -ge 1 ]]; then
  echo "[capture-gate] PASS: capture artifact=$ARTIFACT_COUNT no-capture note=$NOTE_COUNT (재사용지식 외부화 검토 흔적 존재)"
else
  echo "[capture-gate] WARN: capture artifact 0 + no-capture note 0 — 완료 전 재사용지식 외부화 검토 필요"
  WARN=1
fi

echo "[capture-gate] DONE: warn=$WARN story=$STORY_KEY"
exit 0
