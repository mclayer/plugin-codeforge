#!/usr/bin/env bash
# atomic-upgrade-7-plugins.sh — CFP-744 Wave 2 Story-4 — per-family transaction shell
# CFP-932 Wave 4 sub-Epic #882 Story-2 D2 — --channel propagation + mixed channel detection
#
# Change Plan §3.1 per-family transaction layer / §4.1 CLI arg schema /
# §4.2 per-family transaction algorithm / §4.4 ownership / §7.4.1 (a)-(i) DR
#
# 역할: per-family transaction orchestration shell ONLY (Refactor 결론)
#   - per-plugin reconcile semantic = Story-3 codeforge-upgrade.sh 위임 (semantic 분산 0, §4.4)
#   - drift 검증 = check-codeforge-version-drift.sh --plugin 7회 invocation (재구현 0, §4.4)
#   - per-family transaction boundary (7 plugin all-or-rollback) = 본 shell 단독 (§4.4)
#   - user_decision_branches: 0 (no prompt invariant — Epic §1 WHY "0 자리")
#   - --channel propagation: CHANNEL_ARGS array (REPO_ARGS 동형 orthogonal 차원) — CFP-932 D2
#
# F-002 옵션 A — 7-name FAMILY loop 가 codex/superpowers 를 구조적으로 배제
# AC-3 / ADR-037 Amendment 1 — atomic 후 0 drift invariant (drift > 0 = transaction 실패)
#
# §4.5 / §7.4.1 (i) — --repo <path> wrong-target 검증 (실재 디렉터리 AND .git 보유)
# abort-before-touch — 검증 실패 시 per-family snapshot 무생성 (filesystem touch 0)
#
# ADR-061 정합 — heredoc-python 0 (multi-line python 미사용, POSIX bash only)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --------------------------------------------------------------------------
# 사용법 출력 (§4.1 CLI 인자 schema)
# --------------------------------------------------------------------------
_usage() {
    cat <<'USAGE'
atomic-upgrade-7-plugins.sh — codeforge family 9 plugin atomic upgrade (CFP-744 A2 / CFP-932 D2)

사용법:
  bash scripts/atomic-upgrade-7-plugins.sh --dry-run
  bash scripts/atomic-upgrade-7-plugins.sh --apply
  bash scripts/atomic-upgrade-7-plugins.sh --rollback
  bash scripts/atomic-upgrade-7-plugins.sh --apply --repo <consumer-repo-root>
  bash scripts/atomic-upgrade-7-plugins.sh --apply --channel <stable|beta|canary>

옵션:
  --apply                 per-family snapshot → 9 plugin per-plugin reconcile
                          (Story-3 codeforge-upgrade.sh 위임) → 사후 9-plugin 0-drift
                          검증 → 단일 atomic unit (drift > 0 = 전체 9 plugin rollback)
  --dry-run               9 plugin desired (marketplace SSOT) vs current (installed
                          pin) drift preview, filesystem touch 0
  --rollback              직전 per-family pre-atomic snapshot 복원 (9 plugin 일괄)
  --repo <path>           reconcile 대상 consumer repo root 명시 지정 (CFP-744 AC-11,
                          mode 와 순서 무관 — orthogonal). 9 plugin per-plugin
                          reconcile 전체에 동일 --repo propagation (partial target
                          mismatch 0). 미지정 시 codeforge-upgrade.sh fallback 보존
  --channel <tier>        channel tier 명시 지정 (CFP-932 D2, mode·--repo 와 순서 무관 — orthogonal)
                          enum 허용: stable / beta / canary
                          family 9 plugin 전체 동일 channel 으로 atomic resolve
                          mixed channel detection → abort-before-touch (DC-1, INV-2)
                          per-plugin override CLI surface 구조적 부재 (단일 --channel flag)

원칙:
  - 사용자 결정 분기 0 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)
  - per-plugin reconcile semantic = Story-3 codeforge-upgrade.sh SSOT (semantic 분산 0)
  - drift 검증 = check-codeforge-version-drift.sh --plugin 9회 (재구현 0, §4.4)
  - per-family transaction = 9 plugin all-or-rollback (partial state 0, §7.4.1)
  - F-002 옵션 A — codex/superpowers 구조적 배제 (false transaction-fail 0)
USAGE
}

# --------------------------------------------------------------------------
# argument parser (§4.1) — codeforge-upgrade.sh §3.7.2-parser 8-invariant 동형
# --------------------------------------------------------------------------
MODE=""
INPUT_REPO=""
INPUT_CHANNEL=""     # CFP-932 D2 — --channel <stable|beta|canary> (REPO_ARGS 동형 orthogonal)
MODE_SET_COUNT=0

if [[ $# -eq 0 ]]; then
    _usage >&2
    echo "오류: 인자가 필요합니다. --apply / --dry-run / --rollback 중 하나를 지정하세요." >&2
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case "${1}" in
        --apply)
            MODE="apply"
            MODE_SET_COUNT=$((MODE_SET_COUNT + 1))
            shift
            ;;
        --dry-run)
            MODE="dry_run"
            MODE_SET_COUNT=$((MODE_SET_COUNT + 1))
            shift
            ;;
        --rollback)
            MODE="rollback"
            MODE_SET_COUNT=$((MODE_SET_COUNT + 1))
            shift
            ;;
        --repo)
            if [[ $# -lt 2 ]]; then
                echo "오류: --repo 에는 path 인자가 필요합니다. 예: --repo /path/to/consumer-repo" >&2
                exit 1
            fi
            INPUT_REPO="${2}"
            shift 2
            ;;
        --channel)
            # CFP-932 D2 — channel tier 명시 지정 (orthogonal, value-taking, REPO_ARGS 동형)
            if [[ $# -lt 2 ]]; then
                echo "오류: --channel 에는 tier 인자가 필요합니다. 예: --channel stable" >&2
                exit 1
            fi
            INPUT_CHANNEL="${2}"
            # enum whitelist exact-match (SecurityArch M-5 §7.6)
            case "${INPUT_CHANNEL}" in
                stable|beta|canary)
                    # valid tier
                    ;;
                *)
                    echo "오류: --channel 허용 값: stable / beta / canary (입력: '${INPUT_CHANNEL}')" >&2
                    echo "enum whitelist reject — SecurityArch M-5 §7.6 exact-match" >&2
                    exit 1
                    ;;
            esac
            shift 2
            ;;
        --help|-h)
            _usage
            exit 0
            ;;
        *)
            # unknown arg = enum whitelist reject (§7.1 free-text injection surface 0)
            echo "오류: 알 수 없는 인자: '${1}'" >&2
            echo "허용 인자: --apply / --dry-run / --rollback / --repo <path> / --channel <stable|beta|canary>" >&2
            echo "unknown arg = enum whitelist reject (Change Plan §7.1 trust boundary)" >&2
            exit 1
            ;;
    esac
done

# mode 정확히 1개 강제 (§4.1 / §3.7.2-parser (d))
if [[ "${MODE_SET_COUNT}" -eq 0 ]]; then
    _usage >&2
    echo "오류: 인자가 필요합니다. --apply / --dry-run / --rollback 중 하나를 지정하세요." >&2
    exit 1
fi
if [[ "${MODE_SET_COUNT}" -gt 1 ]]; then
    echo "오류: mode 인자는 정확히 1개여야 합니다 (--apply / --dry-run / --rollback 중복/충돌)." >&2
    exit 1
fi

# --------------------------------------------------------------------------
# §4.5 / §7.4.1 (i) — --repo wrong-target 검증 (abort-before-touch)
#   per-family snapshot 생성 전 검증 → 실패 시 filesystem touch 0
# --------------------------------------------------------------------------
REPO_ARGS=()
if [[ -n "${INPUT_REPO}" ]]; then
    if [[ ! -d "${INPUT_REPO}" ]]; then
        echo "[repo_target_failure] 지정 repo 가 실재 디렉터리 아님: ${INPUT_REPO}" >&2
        echo "abort-before-touch: per-family snapshot 무생성, filesystem touch 0 (§4.5 / §7.4.1(i))" >&2
        exit 2
    fi
    if [[ ! -d "${INPUT_REPO}/.git" ]]; then
        echo "[repo_target_failure] 지정 repo 가 git repo 아님 (.git 부재): ${INPUT_REPO}" >&2
        echo "reconcile target 재확인 요망 (오타 / 다른 repo / non-git 디렉터리)" >&2
        echo "abort-before-touch: per-family snapshot 무생성, filesystem touch 0 (§4.5 / §7.4.1(i))" >&2
        exit 2
    fi
    # per-plugin reconcile 전체에 동일 --repo propagation (partial target mismatch 0)
    REPO_ARGS=(--repo "${INPUT_REPO}")
fi

# CHANNEL_ARGS — REPO_ARGS 동형 독립 array (orthogonal 차원 — repo target ≠ channel tier)
# CFP-932 D2 §3.2 설계 결정: 두 array 독립 분리 (합치면 arg 순서 의존 발생, RefactorAgent (c)-2)
CHANNEL_ARGS=()
if [[ -n "${INPUT_CHANNEL}" ]]; then
    CHANNEL_ARGS=(--channel "${INPUT_CHANNEL}")
fi

# --------------------------------------------------------------------------
# [CFP-1170] DEPRECATION SHIM — 1 release grace (R-4 consumer breakage 차단)
#
# atomic-upgrade-7-plugins.sh 는 deprecation shim 으로 재정의됨 (change-plan §3.5 / §7.4.2).
# 실 semantic = walk-bundle-7-plugins.sh 로 이전 (imperative walk paradigm).
# 1 release grace 후 본 shim 삭제 예정 (ADR-038 Amendment 3 §결정 10 "1 release grace" 선례).
# --------------------------------------------------------------------------
echo "[DEPRECATED] atomic-upgrade-7-plugins.sh 는 CFP-1170 에서 deprecation shim 으로 재정의됩니다." >&2
echo "[DEPRECATED] 1 release grace 후 삭제 예정 (change-plan §7.4.2)." >&2
echo "[DEPRECATED] 신규 CLI: bash scripts/walk-bundle-7-plugins.sh --<mode>" >&2
echo "[DEPRECATED] 대응 redirect: atomic-upgrade-7-plugins.sh → walk-bundle-7-plugins.sh (자동 redirect 중)" >&2

# arg → walk mode 매핑
WALK_BUNDLE_CLI="${SCRIPT_DIR}/walk-bundle-7-plugins.sh"
WALK_BUNDLE_MODE=""
case "${MODE}" in
    dry_run)
        WALK_BUNDLE_MODE="--plan"
        ;;
    apply)
        WALK_BUNDLE_MODE="--apply"
        ;;
    rollback)
        WALK_BUNDLE_MODE="--rollback"
        ;;
esac

echo "=== atomic-upgrade-7-plugins.sh → walk-bundle-7-plugins.sh redirect (shim) ==="
echo "walk: deprecated redirect"

REDIRECT_BUNDLE_ARGS=("${WALK_BUNDLE_MODE}")
if [[ ${#REPO_ARGS[@]} -gt 0 ]]; then
    REDIRECT_BUNDLE_ARGS+=("${REPO_ARGS[@]}")
fi
if [[ ${#CHANNEL_ARGS[@]} -gt 0 ]]; then
    REDIRECT_BUNDLE_ARGS+=("${CHANNEL_ARGS[@]}")
fi

exec bash "${WALK_BUNDLE_CLI}" "${REDIRECT_BUNDLE_ARGS[@]}"
exit 1
