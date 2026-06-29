#!/usr/bin/env bash
# reapply-branch-protection.sh — CFP-2469 (Epic CFP-2468 Track W/W1) N-repo 일괄 배선 orchestration.
#
# ADR-132 §결정 7 — 독립 스크립트가 wire-branch-protection.sh 를 repo-list loop 로 반복 호출.
#   wire-* = 1-repo 원자 단위 (SRP 보존), reapply = orchestration layer 분리.
#
# 일괄 운영 리스크 3종 (ADR-132 §결정 7):
#   1. existence_check — branch 부재 repo 는 skip (graceful, abort 금지)
#   2. exponential backoff — 16-repo 일괄 = GitHub API rate-limit (secondary 포함) → backoff 재시도
#   3. partial-failure 누적보고 — 한 repo 실패가 전체 abort 안 함. 끝까지 진행 후 실패 목록 집계
#
# 권한 모델 = operator gh auth (wire-* 위임, ADR-066 무손상). idempotent 재실행 안전.
#
# Usage:
#   bash scripts/reapply-branch-protection.sh --repos owner/a,owner/b,...   [--shape solo|team]
#   bash scripts/reapply-branch-protection.sh --repos-file <path>           [--review-count N]
#   bash scripts/reapply-branch-protection.sh --repos owner/a --dry-run     [--branch main]
#
# 옵션:
#   --repos a,b,c        comma-separated repo 목록 (owner/name)
#   --repos-file <path>   repo 목록 file (non-comment non-blank line iterate)
#   --shape solo|team     모든 repo 공통 형상 (default solo) — wire-* 위임
#   --review-count N       review_count override — wire-* 위임
#   --branch <name>       대상 branch (default main)
#   --dry-run             각 repo wire-* --dry-run 위임 (PUT 0)
#
# Exit code:
#   0 = 전 repo 성공 (또는 graceful skip)
#   1 = 1+ repo 실패 (partial-failure — 누적 목록 보고 후 1 반환, 끝까지 진행)
#   2 = setup error (gh 부재 / repo 목록 0 / wire-* 부재)
#
# SSOT: ADR-132 §결정 7 + Change Plan cfp-2469-consumer-branch-protection-wire.md §3/§7.4

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIRE_SCRIPT="${SCRIPT_DIR}/wire-branch-protection.sh"

REPOS_CSV=""
REPOS_FILE=""
SHAPE="solo"
REVIEW_COUNT=""
BRANCH="main"
DRY_RUN=0

log() { printf '[reapply-branch-protection] %s\n' "$1" >&2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --repos) REPOS_CSV="${2:-}"; shift 2 ;;
    --repos-file) REPOS_FILE="${2:-}"; shift 2 ;;
    --shape) SHAPE="${2:-}"; shift 2 ;;
    --review-count) REVIEW_COUNT="${2:-}"; shift 2 ;;
    --branch) BRANCH="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      sed -n '/^# reapply-branch-protection.sh/,/^# SSOT/p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
      exit 0
      ;;
    *) log "ERROR: Unknown arg: $1"; exit 2 ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  log "ERROR: gh CLI 미설치 (operator gh auth 토큰 필요)"
  exit 2
fi
if [ ! -f "$WIRE_SCRIPT" ]; then
  log "ERROR: wire-branch-protection.sh 부재: $WIRE_SCRIPT"
  exit 2
fi

# ── repo 목록 수집 ──
REPOS=()
if [ -n "$REPOS_CSV" ]; then
  IFS=',' read -r -a _csv <<< "$REPOS_CSV"
  for r in "${_csv[@]}"; do
    r="$(printf '%s' "$r" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -n "$r" ] && REPOS+=("$r")
  done
fi
if [ -n "$REPOS_FILE" ]; then
  if [ ! -f "$REPOS_FILE" ]; then
    log "ERROR: --repos-file 부재: $REPOS_FILE"
    exit 2
  fi
  while IFS= read -r line; do
    line="${line%%$'\r'}"
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -z "$line" ] && continue
    case "$line" in \#*) continue;; esac
    REPOS+=("$line")
  done < "$REPOS_FILE"
fi

if [ "${#REPOS[@]}" -eq 0 ]; then
  log "ERROR: repo 목록 0 — --repos 또는 --repos-file 명시"
  exit 2
fi

# ── existence_check (ADR-132 §결정 7.1) — branch 부재 skip ──
_branch_exists() {
  local repo="$1" branch="$2"
  gh api "repos/${repo}/branches/${branch}" --jq '.name' >/dev/null 2>&1
}

# ── exp-backoff wrapper (ADR-132 §결정 7.2) — rate-limit (secondary 포함) 재시도 ──
# wire-* 호출을 backoff 로 감쌈. wire-* exit 3 (graceful degrade) 는 backoff 대상 아님 (재시도 무의미).
# rate-limit 신호(429 / secondary rate limit / exit 2 의 rate 문구)만 backoff.
_wire_with_backoff() {
  local repo="$1"
  local delays=(2 4 8)
  local attempt=0
  local out rc
  while :; do
    local wire_args=(--repo "$repo" --shape "$SHAPE" --branch "$BRANCH")
    [ -n "$REVIEW_COUNT" ] && wire_args+=(--review-count "$REVIEW_COUNT")
    [ "$DRY_RUN" -eq 1 ] && wire_args+=(--dry-run)
    out="$(bash "$WIRE_SCRIPT" "${wire_args[@]}" 2>&1)"
    rc=$?
    # rate-limit 신호 검출 → backoff 재시도 (max 3)
    if printf '%s' "$out" | grep -qiE "rate limit|429|secondary rate|abuse detection"; then
      if [ "$attempt" -lt 3 ]; then
        local d="${delays[$attempt]}"
        log "  [$repo] rate-limit 신호 — ${d}s backoff 후 재시도 (attempt $((attempt+1))/3)"
        sleep "$d"
        attempt=$((attempt + 1))
        continue
      fi
      log "  [$repo] rate-limit 3회 재시도 소진 — 실패 누적"
    fi
    # backoff 비대상 결과 (성공/graceful/error) → 그대로 반환
    printf '%s\n' "$out" >&2
    return "$rc"
  done
}

# ────────────────────────────────────────────────── main loop ──
log "일괄 배선 시작: ${#REPOS[@]} repo (shape=$SHAPE branch=$BRANCH dry-run=$DRY_RUN)"

SUCCEEDED=()
SKIPPED=()
DEGRADED=()
FAILED=()

for repo in "${REPOS[@]}"; do
  log "── $repo ──"
  if ! _branch_exists "$repo" "$BRANCH"; then
    log "  SKIP: $repo@$BRANCH branch 부재 (existence_check — abort 금지, §결정 7.1)"
    SKIPPED+=("$repo")
    continue
  fi
  _wire_with_backoff "$repo"
  wrc=$?
  case "$wrc" in
    0) SUCCEEDED+=("$repo") ;;
    3) DEGRADED+=("$repo"); log "  DEGRADED: $repo — 403 권한 부족/dead-gate (graceful, 비-abort)" ;;
    *) FAILED+=("$repo"); log "  FAIL: $repo — wire-* exit $wrc (누적, 끝까지 진행)" ;;
  esac
done

# ── 누적보고 (ADR-132 §결정 7.3) ──
log ""
log "=== 일괄 배선 집계 (${#REPOS[@]} repo) ==="
log "  성공: ${#SUCCEEDED[@]}  / skip(branch 부재): ${#SKIPPED[@]}  / degrade(403): ${#DEGRADED[@]}  / 실패: ${#FAILED[@]}"
[ "${#SUCCEEDED[@]}" -gt 0 ] && log "  성공: ${SUCCEEDED[*]}"
[ "${#SKIPPED[@]}" -gt 0 ]   && log "  skip: ${SKIPPED[*]}"
[ "${#DEGRADED[@]}" -gt 0 ]  && log "  degrade(403 WARN — operator 권한 확보 후 재실행): ${DEGRADED[*]}"
[ "${#FAILED[@]}" -gt 0 ]    && log "  실패: ${FAILED[*]}"

# exit policy: 실패 1+ → exit 1 (degrade/skip 는 graceful, exit 0 불방해)
if [ "${#FAILED[@]}" -gt 0 ]; then
  exit 1
fi
exit 0
