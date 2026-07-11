#!/usr/bin/env bash
# ci-runner-provisioning-check.sh — CFP-2607 (Epic W0) CI runner topology provisioning invariant lint.
#
# ADR-147 §결정 4(ii) — self-hosted 이관 private/internal repo 의 required runner 변수
#   (CI_RUNS_ON_LINUX_JSON; matrix repo 는 --require-windows 로 CI_RUNS_ON_WINDOWS_JSON 추가)
#   가 SET 되어 있는지 provisioning-time 에 fail-loud 로 검증한다.
#
# WHY NOT a GitHub Actions workflow (born-dead-gate 회피, ADR-147 §결정 4(ii)):
#   이 lint 의 감지 대상 = hosted billing 소진으로 인한 required-check hard-block
#   (2-3s FAIL → merge deadlock, AC-11). hosted-CI 워크플로로 구현하면 감지 대상 billing 에
#   co-blocked 되어 발화 불가(css-lint born-invalid / execution-liveness 재발 class).
#   따라서 실행면 = billing-독립 3택: (1) provisioning-time(operator/hub, CI 이전, primary)
#   (2) self-hosted runner(W0 후 ongoing drift) (3) org-hub 주기 스캔.
#   → gh api 메타데이터 스캔만 수행(actions run 아님). GitHub Actions 워크플로로 배선 금지.
#
# 분기 (ADR-147 §결정 2 — visibility 기반):
#   - public repo (plugin-codeforge/marketplace): hosted 유지 → 변수 UNSET 이 정상
#       (coalesce → ubuntu-latest). PASS. (변수 SET 이면 WARN — allows_public_repositories=false 로
#       GitHub 이 거부하나 delta-0 의도 위반 신호.)
#   - private/internal repo: self-hosted target → 변수 SET 필수. UNSET = fail-loud(exit 1).
#
# 변수명 SSOT (KU-2 실증 mechanism): single-leg 거버넌스(linux 단일) = CI_RUNS_ON_LINUX_JSON.
#   matrix os-leg repo = CI_RUNS_ON_LINUX_JSON ∧ CI_RUNS_ON_WINDOWS_JSON (--require-windows, ADR-147 §결정 11).
#
# Usage:
#   bash scripts/ci-runner-provisioning-check.sh --repo <owner/name> [--require-windows] [--dry-run]
#
# 옵션:
#   --repo <owner/name>   대상 repo (필수 — 미지정 시 gh repo view 자동 탐지 시도)
#   --require-windows     matrix os-leg repo — CI_RUNS_ON_WINDOWS_JSON 도 필수(ADR-147 §결정 11)
#   --dry-run             read-only 스크립트 — 검사 대상만 추가 출력(side-effect 0)
#   -h|--help             usage
#
# Exit code:
#   0 = PASS (private/internal target 변수 present, 또는 public repo 정상 unset)
#   1 = FAIL-LOUD (private/internal self-hosted target 의 required 변수 UNSET — provisioning gap, merge deadlock 위험)
#   2 = error (gh 부재 / repo 미탐지 / 예기치 못한 gh api error / 미분류 visibility)
#   3 = graceful degrade (HTTP 403 — 권한 부족으로 변수 검증 불가, WARN 비-blocking)
#
# SSOT: ADR-147 §결정 2/4/11 + Change Plan cfp-2607-ci-selfhosted-migration.md §5/§7.4/§9
# 비-mirror: scripts/ (operator/hub-run 운영 도구, consumer byte-identical 복사 대상 아님 — hosted-CI 워크플로 아님).

set -uo pipefail

LINUX_VAR="CI_RUNS_ON_LINUX_JSON"
WINDOWS_VAR="CI_RUNS_ON_WINDOWS_JSON"
SELF_HOSTED_LINUX_LABELS='["self-hosted","X64","Linux","docker"]'
SELF_HOSTED_WINDOWS_LABELS='["self-hosted","Windows","X64"]'

REPO=""
REQUIRE_WINDOWS=0
DRY_RUN=0

log() { printf '[ci-runner-provisioning-check] %s\n' "$1" >&2; }
err() { printf '[ci-runner-provisioning-check] ERROR: %s\n' "$1" >&2; }

_usage() {
  sed -n '/^# ci-runner-provisioning-check.sh/,/^# 비-mirror/p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --require-windows) REQUIRE_WINDOWS=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) _usage; exit 0 ;;
    *) err "Unknown arg: $1"; _usage >&2; exit 2 ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  err "gh CLI 부재 — provisioning 검증 불가 (billing-독립 실행면 요건). gh 설치 후 재실행."
  exit 2
fi

if [ -z "$REPO" ]; then
  REPO="$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null || true)"
fi
if [ -z "$REPO" ]; then
  err "--repo <owner/name> 미지정 + 자동 탐지 실패."
  exit 2
fi

# ── visibility probe (ADR-147 §결정 2 분기 입력) ──
_vis_out="$(gh api "repos/$REPO" --jq '.visibility' 2>&1)"; _vis_rc=$?
if [ $_vis_rc -ne 0 ]; then
  if printf '%s' "$_vis_out" | grep -qiE 'HTTP 403|Forbidden|must have admin'; then
    log "WARN: repos/$REPO visibility 조회 403 (권한 부족) — graceful degrade(비-blocking)."
    exit 3
  fi
  err "repos/$REPO 조회 실패: $_vis_out"
  exit 2
fi
VISIBILITY="$_vis_out"

# ── variable presence probe: echoes present|unset|forbidden|error:<msg> ──
_probe_var() {
  local name="$1" out rc
  out="$(gh api "repos/$REPO/actions/variables/$name" 2>&1)"; rc=$?
  if [ $rc -eq 0 ]; then echo "present"; return; fi
  if printf '%s' "$out" | grep -qiE 'HTTP 403|Forbidden|must have admin'; then echo "forbidden"; return; fi
  if printf '%s' "$out" | grep -qiE 'HTTP 404|Not Found'; then echo "unset"; return; fi
  echo "error:$out"
}

case "$VISIBILITY" in
  public)
    # public → hosted 유지가 정상(변수 UNSET 기대). SET 이면 delta-0 의도 위반 WARN(그러나 PASS).
    st="$(_probe_var "$LINUX_VAR")"
    case "$st" in
      unset)     log "PASS: $REPO (public) — $LINUX_VAR unset = hosted 유지(정상, coalesce → ubuntu-latest)."; exit 0 ;;
      present)   log "WARN: $REPO (public) 에 $LINUX_VAR SET — public 은 hosted 유지 대상(ADR-147 §결정 2). allows_public_repositories=false 로 GitHub 이 거부하나 delta-0 의도 위반 신호(repo-scoped 변수 제거 권고). (비-blocking, PASS)"; exit 0 ;;
      forbidden) log "WARN: $REPO (public) $LINUX_VAR 조회 403 — graceful degrade(비-blocking)."; exit 3 ;;
      *)         err "$REPO $LINUX_VAR probe 예기치 못한 응답: ${st#error:}"; exit 2 ;;
    esac
    ;;
  private|internal)
    if [ $DRY_RUN -eq 1 ]; then
      _extra=""; [ $REQUIRE_WINDOWS -eq 1 ] && _extra=" ∧ $WINDOWS_VAR"
      log "(dry-run) $REPO ($VISIBILITY) self-hosted target — 검사 대상: $LINUX_VAR$_extra"
    fi
    gap=0
    st_lin="$(_probe_var "$LINUX_VAR")"
    case "$st_lin" in
      present)   log "OK: $REPO $LINUX_VAR present." ;;
      unset)
        err "PROVISIONING GAP: $REPO ($VISIBILITY, self-hosted target) 에 $LINUX_VAR 미설정."
        err "  → hosted billing hard-block(2-3s FAIL) → required-check merge deadlock (AC-11)."
        err "  → operator 조치: gh variable set $LINUX_VAR --repo $REPO --body '$SELF_HOSTED_LINUX_LABELS'"
        gap=1 ;;
      forbidden) log "WARN: $REPO $LINUX_VAR 조회 403 — graceful degrade(비-blocking)."; exit 3 ;;
      *)         err "$REPO $LINUX_VAR probe 예기치 못한 응답: ${st_lin#error:}"; exit 2 ;;
    esac
    if [ $REQUIRE_WINDOWS -eq 1 ]; then
      st_win="$(_probe_var "$WINDOWS_VAR")"
      case "$st_win" in
        present)   log "OK: $REPO $WINDOWS_VAR present." ;;
        unset)
          err "PROVISIONING GAP: $REPO ($VISIBILITY, matrix os-leg) 에 $WINDOWS_VAR 미설정."
          err "  → windows leg 가 group5(self-hosted-private) 라우팅 상실 (ADR-147 §결정 11)."
          err "  → operator 조치: gh variable set $WINDOWS_VAR --repo $REPO --body '$SELF_HOSTED_WINDOWS_LABELS'"
          gap=1 ;;
        forbidden) log "WARN: $REPO $WINDOWS_VAR 조회 403 — graceful degrade(비-blocking)."; exit 3 ;;
        *)         err "$REPO $WINDOWS_VAR probe 예기치 못한 응답: ${st_win#error:}"; exit 2 ;;
      esac
    fi
    if [ $gap -eq 1 ]; then
      err "FAIL-LOUD: $REPO provisioning invariant 위반 — self-hosted cutover 전 required 변수 SET 필수 (ADR-147 §결정 4)."
      exit 1
    fi
    log "PASS: $REPO ($VISIBILITY) — required runner 변수 provisioning 완료."
    exit 0
    ;;
  *)
    err "$REPO visibility='$VISIBILITY' 미분류 — 수동 확인 필요."
    exit 2
    ;;
esac
