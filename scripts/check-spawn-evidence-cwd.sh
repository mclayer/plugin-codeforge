#!/usr/bin/env bash
# CFP-427 actual logic (canonical)
# CFP-427 — Spawn evidence Working-dir lint (warning).
# Scan docs/stories/<KEY>.md §14 Lane Evidence rows. Each row's transcript: field
# must contain "Working dir: " followed by:
#   (a) worktree path: /c/Users/.../\.claude/worktrees/.+
#   (b) N/A bypass: "N/A — <30자 이상 사유>" (ADR-031 §결정 4 정합)
#   (c) read-only fetch suffix (deputy read-only fetch 패턴, Story 1 §14 line 1011 정착)
# enforce-from = 본 Story 2 (CFP-427) Phase 2 PR merged-at 이후 신규 Story (false-positive 회피).
#
# 환경 변수:
#   BYPASS_WORKTREE_FIRST (선택, 1 = skip)
#     ADR-040 Amendment 3 §결정 7.E — `BYPASS_WORKTREE_GC` 와 disjoint scope.
#   ENFORCE_FROM (선택, ISO8601 timestamp) — default override.
#   STORIES_DIR (선택, path) — Story file directory override.
#     기본값 = ${REPO_ROOT}/docs/stories. wrapper repo 자체는 ADR-013 dogfood-out 으로
#     docs/stories 부재 (실제 stories 는 codeforge-internal-docs/wrapper/stories/) 이므로
#     wrapper self-application 시 STORIES_DIR=<internal-docs-clone>/wrapper/stories 명시 필요.
#     CFP-427 FIX iter 1 F-002 closing — wrapper-only scope mandate 정합 (Story §5.4 cross-ref).
#     consumer / mctrader / 일반 repo 는 default 값이 정상 적용 (override 불필요).
#
# Exit code:
#   0 — always (warning tier, non-blocking)
#
# carrier: ADR-040 Amendment 3 §결정 7.A action: worktree-first-spawn-evidence-cwd (actual wire)
set -euo pipefail

if [[ "${BYPASS_WORKTREE_FIRST:-}" == "1" ]]; then
  echo "[spawn-evidence-cwd] BYPASS_WORKTREE_FIRST=1 — skip" >&2
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
# CFP-427 FIX iter 1 F-002: STORIES_DIR env override (wrapper-only scope mandate)
STORIES_DIR="${STORIES_DIR:-${REPO_ROOT}/docs/stories}"
[[ ! -d "$STORIES_DIR" ]] && { echo "[spawn-evidence-cwd] $STORIES_DIR not found — skip" >&2; exit 0; }

# enforce-from = CFP-427 Phase 2 PR merged-at (단일 기준 — FIX iter 1 F-3 정합)
# 우선순위: ENFORCE_FROM env > git inferred > hardcode default
# 안전망 = PLACEHOLDER sentinel — Phase 2 PR merge 전 = enforce 전체 skip (false-positive 회피)
# Phase 2 PR merge 직후 절차 (DeveloperPL):
#   1. gh pr view <PR> --json mergedAt 으로 timestamp fetch
#   2. ENFORCE_FROM_DEFAULT 를 PLACEHOLDER → ISO8601 timestamp 로 Edit + amend (squash 전)
ENFORCE_FROM_DEFAULT="PLACEHOLDER_REPLACE_AFTER_CFP427_MERGE"  # Phase 2 PR merge 후 mergedAt 으로 갱신
ENFORCE_FROM="${ENFORCE_FROM:-$ENFORCE_FROM_DEFAULT}"

# Safe-fallback: PLACEHOLDER sentinel 검출 시 = enforce 전체 skip (warning tier — false-positive 회피 우선)
if [[ "$ENFORCE_FROM" == PLACEHOLDER_* ]]; then
  echo "[spawn-evidence-cwd] ENFORCE_FROM still PLACEHOLDER — skip enforce (Phase 2 PR not yet merged)" >&2
  exit 0
fi

WARN_COUNT=0
for story_file in "$STORIES_DIR"/*.md; do
  [[ -f "$story_file" ]] || continue

  # enforce-from filter: file 신설 commit timestamp 확인
  ADDED_AT=$(git log --diff-filter=A --format=%cI -- "$story_file" 2>/dev/null | tail -1)
  if [[ -z "$ADDED_AT" ]]; then
    # git log 실패 = file ctime fallback 또는 skip (warning tier — false-positive 회피 우선)
    continue
  fi
  # ADDED_AT < ENFORCE_FROM = pre-existing Story → skip
  if [[ "$ADDED_AT" < "$ENFORCE_FROM" ]]; then
    continue
  fi

  # §14 Lane Evidence section 안 transcript 의 Working dir substring 추출
  STORY_KEY="$(basename "$story_file" .md)"
  while IFS= read -r line; do
    # transcript: "...Working dir: <path>" 형식 (Story 1 §14 9 row 정착 패턴)
    if [[ "$line" =~ Working\ dir:\ *([^\"\,]+) ]]; then
      WD="${BASH_REMATCH[1]}"
      # CFP-427 FIX iter 1 F-003: Working dir 빈 값 case WARN (AC-3 (d) closing)
      # trim leading/trailing whitespace
      WD="${WD#"${WD%%[![:space:]]*}"}"
      WD="${WD%"${WD##*[![:space:]]}"}"
      if [[ -z "$WD" ]]; then
        echo "[spawn-evidence-cwd] WARN: $STORY_KEY transcript Working dir 빈 값 (AC-3 (d))" >&2
        WARN_COUNT=$((WARN_COUNT + 1))
        continue
      fi
      # valid pattern 3종:
      #   (a) /c/Users/.../\.claude/worktrees/...
      #   (b) N/A — <30자 이상 사유>
      #   (c) read-only (deputy read-only fetch 패턴)
      if [[ "$WD" =~ /\.claude/worktrees/ ]]; then
        : # PASS (a)
      elif [[ "$WD" =~ ^N/A\ —\ .{30,} ]]; then
        : # PASS (b)
      elif [[ "$WD" =~ read-only ]]; then
        : # PASS (c)
      else
        echo "[spawn-evidence-cwd] WARN: $STORY_KEY transcript Working dir invalid: $WD" >&2
        WARN_COUNT=$((WARN_COUNT + 1))
      fi
    else
      # CFP-427 FIX iter 1 F-003: transcript line 안 'Working dir:' substring 자체 부재 → WARN (AC-3 (d) closing)
      echo "[spawn-evidence-cwd] WARN: $STORY_KEY transcript 'Working dir:' field 부재 (AC-3 (d))" >&2
      WARN_COUNT=$((WARN_COUNT + 1))
    fi
  done < <(awk '/^lane_evidence:/,/^```$/' "$story_file" | grep -E "^\s*transcript:")
done

if [[ "$WARN_COUNT" -gt 0 ]]; then
  echo "[spawn-evidence-cwd] WARN total: $WARN_COUNT" >&2
fi

# warning tier — exit 0 always
exit 0
