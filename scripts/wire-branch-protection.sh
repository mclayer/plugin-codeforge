#!/usr/bin/env bash
# wire-branch-protection.sh — CFP-2469 (Epic CFP-2468 Track W/W1) branch protection write SSOT.
#
# ADR-132 §결정 1 — branch protection write 로직 단일 SSOT (3 호출부 재사용:
#   bootstrap stage / check_bootstrap.py readiness / reapply-branch-protection.sh).
#
# 메커니즘 (ADR-132 §결정 2/3/4/5/6):
#   - GET-merge-PUT idempotent (full-replacement semantics 대비 desired-state union merge, AC-5)
#   - operator gh auth 토큰 사용 (옵션 A — codeforge PAT 미사용, ADR-066 §결정 2 6-scope 무손상, AC-7)
#   - review_count 형상 파라미터 (solo=0 / team≥1, AC-2 — solo-dev deadlock 회피)
#   - enforce_admins=true (불변, dead-gate 차단) / restrictions=null (불변, deadlock 회피) / strict=true default
#   - context↔job-name 정합 게이트 (AC-4 — 미정합 context 배선 제외 + WARN, 영구 pending 차단)
#   - 403 → WARN graceful degrade (AC-3 — hard-fail 아님, ADR-027 §결정 2 + drift-preview fallback)
#
# FORM(b) SoD (ADR-132 §결정 1): write 로직(본 스크립트) ↔ drift-preview(setup-branch-protection.sh) 분리.
# setup-branch-protection.sh 는 ZERO-write 무손상 보존.
#
# Usage:
#   bash scripts/wire-branch-protection.sh --repo <owner/name> [--shape solo|team]
#                                          [--review-count N] [--branch main]
#                                          [--dry-run] [--inspect]
#
# 옵션:
#   --repo <owner/name>   대상 repo (필수 — 미지정 시 gh repo view 자동 탐지 시도)
#   --shape solo|team     consumer 형상 (default solo) — review_count default 분기 (solo=0 / team=1)
#   --review-count N       review_count 명시 override (shape default 우선)
#   --branch <name>       대상 branch (default main)
#   --dry-run             PUT 0 — desired payload + 정합 게이트 결과만 stdout (side-effect 0)
#   --inspect             read-only GET — 현 배선 상태 보고 (readiness check 재사용 경로). exit 0=배선됨 / 3=dead-gate
#   --contexts a,b,c      등록 후보 context 명시 (default = manifest core contexts)
#
# Exit code:
#   0 = 배선 성공 (또는 --inspect: 배선 확인 / --dry-run: payload 산출 성공)
#   2 = error (gh 부재 / repo 미탐지 / manifest invalid)
#   3 = graceful degrade (403 권한 부족 → WARN — bootstrap 비-abort 신호 / --inspect: dead-gate 검출)
#
# SSOT: ADR-132 + Change Plan cfp-2469-consumer-branch-protection-wire.md §3
# 비-mirror: scripts/ (operator-run 운영 도구, consumer byte-identical 복사 대상 아님 — ADR-005 비대상)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="${PLUGIN_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"

# Core contexts (ADR-024 §결정 A 삭제 불허 invariant — append-only union 의 floor).
# NOTE: 본 set 은 manifest core-4 의 superset 후보가 아니라 "codeforge desired" set.
# 실제 등록은 context↔job-name 정합 게이트(아래)가 actual workflow job 표시명과 교집합한 결과.
DEFAULT_CONTEXTS=(
  "phase-gate-mergeable"
  "invariant-check"
  "doc frontmatter schema (CFP-28 — strict)"
  "doc section schema (CFP-28 — strict)"
)

REPO=""
SHAPE="solo"
REVIEW_COUNT=""
BRANCH="main"
DRY_RUN=0
INSPECT=0
CONTEXTS_OVERRIDE=""

log() { printf '[wire-branch-protection] %s\n' "$1" >&2; }

_usage() {
  sed -n '/^# wire-branch-protection.sh/,/^# 비-mirror/p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --shape) SHAPE="${2:-}"; shift 2 ;;
    --review-count) REVIEW_COUNT="${2:-}"; shift 2 ;;
    --branch) BRANCH="${2:-}"; shift 2 ;;
    --contexts) CONTEXTS_OVERRIDE="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --inspect) INSPECT=1; shift ;;
    -h|--help) _usage; exit 0 ;;
    *) log "ERROR: Unknown arg: $1"; _usage >&2; exit 2 ;;
  esac
done

# ── repo 탐지 ──
if [ -z "$REPO" ]; then
  if command -v gh >/dev/null 2>&1; then
    REPO="$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null || true)"
  fi
fi
if [ -z "$REPO" ]; then
  log "ERROR: --repo <owner/name> 미지정 + 자동 탐지 실패"
  exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
  log "ERROR: gh CLI 미설치 — https://cli.github.com (operator gh auth 토큰 필요, ADR-132 §결정 2)"
  exit 2
fi

# ── shape → review_count 분기 (ADR-132 §결정 5, AC-2) ──
_resolve_review_count() {
  if [ -n "$REVIEW_COUNT" ]; then
    printf '%s' "$REVIEW_COUNT"
    return 0
  fi
  case "$SHAPE" in
    solo) printf '0' ;;
    team) printf '1' ;;
    *) log "WARN: 미지 shape '$SHAPE' — solo(0) fail-safe 처리"; printf '0' ;;
  esac
}

# ── 후보 context 목록 ──
_candidate_contexts() {
  if [ -n "$CONTEXTS_OVERRIDE" ]; then
    # comma-split
    local IFS=','
    local c
    for c in $CONTEXTS_OVERRIDE; do
      [ -n "$c" ] && printf '%s\n' "$c"
    done
  else
    local ctx
    for ctx in "${DEFAULT_CONTEXTS[@]}"; do
      printf '%s\n' "$ctx"
    done
  fi
}

# ── gh GET fail-closed helper (CFP-2493) ──
# gh HTTP-error 시 non-zero exit → stdout error JSON 미캡처(빈 출력 + return 1).
# 성공(exit 0) 시에만 stdout 통과. 404(unprotected)·transient(5xx/network) 모두 fail-closed.
# 근거: gh 는 HTTP error body 를 stdout 으로 emit + --jq 미적용 (cli/cli#5209) →
#       2>/dev/null||true 로 못 막음. exit-code 분리가 버전 무관 robust guard.
_gh_get_or_fail() {
  # args: gh api 인자 그대로 (--jq 포함). 성공 시 stdout, 실패 시 빈 출력 + return 1.
  local out
  if out="$(gh api "$@" 2>/dev/null)"; then
    printf '%s' "$out"
    return 0
  fi
  return 1
}

# ── context↔job-name 정합 게이트 (ADR-132 §결정 4, AC-4) ──
# 실제 배포된 workflow 의 check run 표시명 set 을 GET 해 후보 context 와 교집합.
# 미정합 context = 배선 제외 + WARN (영구 pending 차단). 게이트 자체는 abort 하지 않음.
# actual check name source = commits/<sha>/check-runs (가장 최근 default-branch commit).
_actual_check_names() {
  local repo="$1" branch="$2"
  local sha
  sha="$(_gh_get_or_fail "repos/${repo}/commits/${branch}" --jq '.sha')" || return 0
  [ -z "$sha" ] && return 0
  _gh_get_or_fail "repos/${repo}/commits/${sha}/check-runs" --paginate \
    --jq '.check_runs[].name' || return 0
}

# ── 현 protection state GET (idempotency GET-merge 의 GET 단계 + --inspect 재사용) ──
_current_contexts() {
  local repo="$1" branch="$2"
  _gh_get_or_fail "repos/${repo}/branches/${branch}/protection/required_status_checks" \
    --jq '.contexts[]?' || return 0
}

_protection_exists() {
  local repo="$1" branch="$2"
  gh api "repos/${repo}/branches/${branch}/protection" --jq '.url' >/dev/null 2>&1
}

# ── JSON array literal builder (context list → ["a","b"]) ──
_json_string_array() {
  # stdin = newline-separated values → JSON array (gh 의존 없는 순수 jq, 공백/em-dash 안전)
  if command -v jq >/dev/null 2>&1; then
    jq -R . | jq -s .
  else
    # jq 부재 fallback — python3
    python3 -c 'import sys,json; print(json.dumps([l.rstrip("\n") for l in sys.stdin if l.strip()!=""]))'
  fi
}

# ────────────────────────────────────────────────────────────── --inspect ──
# read-only GET — 배선 여부 보고. exit 0 = 배선됨 / 3 = dead-gate (미배선).
if [ "$INSPECT" -eq 1 ]; then
  if ! _protection_exists "$REPO" "$BRANCH"; then
    log "INSPECT: $REPO@$BRANCH — branch protection 부재 (dead gate)"
    exit 3
  fi
  cur="$(_current_contexts "$REPO" "$BRANCH")"
  cur_count=0
  [ -n "$cur" ] && cur_count="$(printf '%s\n' "$cur" | grep -c . || true)"
  ea="$(gh api "repos/${REPO}/branches/${BRANCH}/protection/enforce_admins" --jq '.enabled' 2>/dev/null || echo "unknown")"
  log "INSPECT: $REPO@$BRANCH — protection 활성, contexts=${cur_count}, enforce_admins=${ea}"
  if [ "$cur_count" -eq 0 ]; then
    log "INSPECT: required_status_checks.contexts 0개 (dead gate — workflow 돌지만 merge 차단력 0)"
    exit 3
  fi
  exit 0
fi

# ────────────────────────────────────────────────── 정합 게이트 + payload ──
rc_value="$(_resolve_review_count)"

# 후보 context
mapfile -t candidates < <(_candidate_contexts)

# actual check names (정합 게이트 input)
actual_raw="$(_actual_check_names "$REPO" "$BRANCH")"

# 정합: 후보 ∩ actual. actual 비어있으면(신규 repo/check run 0) gate 보수적 — 후보 전체 통과 +
# WARN (실 배포 후 재배선 권장). actual 존재 시 미정합 context 제외 + WARN.
applied_contexts=()
excluded_contexts=()
if [ -z "$actual_raw" ]; then
  log "WARN: actual check run 0개 ($REPO@$BRANCH) — 정합 검증 불가 → 후보 전체 배선 (실 배포 후 재배선 권장, AC-4)"
  applied_contexts=("${candidates[@]}")
else
  for ctx in "${candidates[@]}"; do
    if printf '%s\n' "$actual_raw" | grep -qxF "$ctx"; then
      applied_contexts+=("$ctx")
    else
      excluded_contexts+=("$ctx")
    fi
  done
  if [ "${#excluded_contexts[@]}" -gt 0 ]; then
    log "WARN: context↔job-name 미정합 ${#excluded_contexts[@]}개 배선 제외 (영구 pending 차단, AC-4):"
    for e in "${excluded_contexts[@]}"; do log "  - $e"; done
  fi
fi

# ── GET-merge: 현 contexts union (consumer 고유 설정 보존, AC-5 / ADR-132 §결정 6) ──
existing="$(_current_contexts "$REPO" "$BRANCH")"
declare -A seen=()
merged_contexts=()
# 현 contexts 먼저 (consumer 고유 보존)
if [ -n "$existing" ]; then
  while IFS= read -r ec; do
    [ -z "$ec" ] && continue
    if [ -z "${seen[$ec]:-}" ]; then seen["$ec"]=1; merged_contexts+=("$ec"); fi
  done <<< "$existing"
fi
# codeforge desired (정합 통과분) union append
for ac in "${applied_contexts[@]}"; do
  if [ -z "${seen[$ac]:-}" ]; then seen["$ac"]=1; merged_contexts+=("$ac"); fi
done

if [ "${#merged_contexts[@]}" -eq 0 ]; then
  log "WARN: 배선할 context 0개 (후보 ∩ actual = ∅ + 현 contexts 0) — 배선 skip (dead-gate 잔존)"
  log "      → workflow 배포 후 재실행 권장 (정합 게이트 산출 0)"
  exit 3
fi

contexts_json="$(printf '%s\n' "${merged_contexts[@]}" | _json_string_array)"

# ── desired PUT payload (ADR-132 §결정 5 형상 4필드) ──
# full-replacement semantics — desired-state 전체 PUT (idempotent).
read -r -d '' payload <<PAYLOAD || true
{
  "required_status_checks": { "strict": true, "contexts": ${contexts_json} },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": ${rc_value}, "require_code_owner_reviews": false },
  "restrictions": null
}
PAYLOAD

# ────────────────────────────────────────────────────────────── --dry-run ──
if [ "$DRY_RUN" -eq 1 ]; then
  log "DRY-RUN: $REPO@$BRANCH — PUT 0 (side-effect 0). desired payload:"
  printf '%s\n' "$payload"
  log "DRY-RUN: shape=$SHAPE review_count=$rc_value contexts=${#merged_contexts[@]} (정합 제외 ${#excluded_contexts[@]}개)"
  exit 0
fi

# ────────────────────────────────────────────────────────────── PUT ──
# operator gh auth 토큰 (ADR-132 §결정 2, AC-7 — codeforge PAT 미사용).
# 403 → WARN graceful degrade (ADR-132 §결정 3, AC-3).
log "PUT: $REPO@$BRANCH — shape=$SHAPE review_count=$rc_value contexts=${#merged_contexts[@]}"
put_out="$(printf '%s' "$payload" | gh api -X PUT \
  "repos/${REPO}/branches/${BRANCH}/protection" \
  --input - 2>&1)"
put_rc=$?

if [ "$put_rc" -eq 0 ]; then
  log "PUT 성공: $REPO@$BRANCH branch protection 배선 완료 (merge 차단력 충전)"
  exit 0
fi

# 403 / permission 분기 — graceful degrade
if printf '%s' "$put_out" | grep -qiE "403|Resource not accessible|Must have admin|Administration"; then
  log "WARN: $REPO@$BRANCH — 403 권한 부족 (operator 가 org-admin 아님). graceful degrade (AC-3):"
  log "      → drift preview fallback: bash templates/scripts/setup-branch-protection.sh --dry-run"
  log "      → operator org-admin 권한으로 수동 적용 또는 권한 확보 후 재실행"
  exit 3
fi

log "ERROR: $REPO@$BRANCH — PUT 실패 (403 외): ${put_out}"
exit 2
