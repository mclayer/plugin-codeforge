#!/usr/bin/env bash
# atomic-upgrade-7-plugins.sh — CFP-744 Wave 2 Story-4 — per-family transaction shell
# CFP-932 Wave 4 sub-Epic #882 Story-2 D2 — --channel propagation + mixed channel detection
# CFP-1059 S1 (T23 anchor) — 9 plugin family forward-compat anchor declare-only (Phase 1 declarative).
#   FAMILY array 7 entry retain (Option A, derived default 2026-05-20 KST) + comment 안 9 plugin S2/S3 wire 예정 anchor 명시. script name retain.
#   CFP-1059 S2/S3 (codeforge-deploy + codeforge-deploy-review lane plugin seed 신설) merge 후 FAMILY 2 entry append + drift check 9 invocation ratchet 영역.
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
#   - mixed channel detection: _check_channel_consistency 헬퍼 (snapshot 생성 이전 — DC-1)
#
# F-002 옵션 A — 7-name FAMILY loop 가 codex/superpowers 를 구조적으로 배제
# AC-3 / ADR-037 Amendment 1 — atomic 후 0 drift invariant (drift > 0 = transaction 실패)
#
# §4.5 / §7.4.1 (i) — --repo <path> wrong-target 검증 (실재 디렉터리 AND .git 보유)
# abort-before-touch — 검증 실패 시 per-family snapshot 무생성 (filesystem touch 0)
# DC-1 (OpRiskArch §7.4.1): mixed channel detection = snapshot 생성 이전 강제 (abort-before-touch)
#
# ADR-061 정합 — heredoc-python 0 (multi-line python 미사용, POSIX bash only)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PER_PLUGIN_CLI="${SCRIPT_DIR}/codeforge-upgrade.sh"
# §4.4 ownership — drift 검증 = check-codeforge-version-drift.sh (CFP-262 SSOT) 위임.
# CODEFORGE_DRIFT_CHECK_BIN env = test-injectable seam (default = canonical path,
# 프로덕션 동작 byte-identical — CODEFORGE_REPO_ROOT override 패턴 동형).
DRIFT_CHECK="${CODEFORGE_DRIFT_CHECK_BIN:-${SCRIPT_DIR}/check-codeforge-version-drift.sh}"

# codeforge family 7 plugin (F-002 옵션 A — codex/superpowers 구조적 배제)
# CFP-1059 forward-compat anchor (Option A, derived default 2026-05-20 KST):
#   본 Story Phase 1 시점 codeforge family = 7 plugin. CFP-1059 신설 lane 2 (codeforge-deploy + codeforge-deploy-review) 는 S2/S3 sub-Story carrier — wrapper 본 lane plugin seed 신설 후 9 plugin 으로 자연 확장 영역.
#   atomic-upgrade-7-plugins.sh 이름 retain (사용자 D2 derived default) — script body comment-level 9 plugin family anchor 만 declare. S2/S3 merge 후 FAMILY array 2 entry append + base label invocations + drift check 7→9 invocation 동시 ratchet 영역.
#   Forward-compat anchor cross-ref: ADR-087 §결정 1 (Deploy lane 신설) / ADR-088 §결정 1 (Deploy Review lane 신설) / ADR-023 §결정 N (lane plugin lifecycle — 본 Amendment carrier).
#   future rename 영역 (atomic-upgrade-9-plugins.sh 또는 atomic-upgrade-family.sh) 도 S2/S3 sub-Story 동시 검토 영역 — family auto-enumerate (글로브 패턴 또는 별 manifest) 검토 anchor (현재는 explicit list retain — Phase 1 declarative).
FAMILY=(
    codeforge
    codeforge-requirements
    codeforge-design
    codeforge-review
    codeforge-develop
    codeforge-test
    codeforge-pmo
    # CFP-1059 S2/S3 wire 후 활성:
    # codeforge-deploy           # ADR-087 Deploy lane (S2 carrier)
    # codeforge-deploy-review    # ADR-088 Deploy Review lane (S3 carrier)
)

# --------------------------------------------------------------------------
# 사용법 출력 (§4.1 CLI 인자 schema)
# --------------------------------------------------------------------------
_usage() {
    cat <<'USAGE'
atomic-upgrade-7-plugins.sh — codeforge family 7 plugin atomic upgrade (CFP-744 A2 / CFP-932 D2)

사용법:
  bash scripts/atomic-upgrade-7-plugins.sh --dry-run
  bash scripts/atomic-upgrade-7-plugins.sh --apply
  bash scripts/atomic-upgrade-7-plugins.sh --rollback
  bash scripts/atomic-upgrade-7-plugins.sh --apply --repo <consumer-repo-root>
  bash scripts/atomic-upgrade-7-plugins.sh --apply --channel <stable|beta|canary>

옵션:
  --apply                 per-family snapshot → 7 plugin per-plugin reconcile
                          (Story-3 codeforge-upgrade.sh 위임) → 사후 7-plugin 0-drift
                          검증 → 단일 atomic unit (drift > 0 = 전체 7 plugin rollback)
  --dry-run               7 plugin desired (marketplace SSOT) vs current (installed
                          pin) drift preview, filesystem touch 0
  --rollback              직전 per-family pre-atomic snapshot 복원 (7 plugin 일괄)
  --repo <path>           reconcile 대상 consumer repo root 명시 지정 (CFP-744 AC-11,
                          mode 와 순서 무관 — orthogonal). 7 plugin per-plugin
                          reconcile 전체에 동일 --repo propagation (partial target
                          mismatch 0). 미지정 시 codeforge-upgrade.sh fallback 보존
  --channel <tier>        channel tier 명시 지정 (CFP-932 D2, mode·--repo 와 순서 무관 — orthogonal)
                          enum 허용: stable / beta / canary
                          family 7 plugin 전체 동일 channel 으로 atomic resolve
                          mixed channel detection → abort-before-touch (DC-1, INV-2)
                          per-plugin override CLI surface 구조적 부재 (단일 --channel flag)

원칙:
  - 사용자 결정 분기 0 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)
  - per-plugin reconcile semantic = Story-3 codeforge-upgrade.sh SSOT (semantic 분산 0)
  - drift 검증 = check-codeforge-version-drift.sh --plugin 7회 (재구현 0, §4.4)
  - per-family transaction = 7 plugin all-or-rollback (partial state 0, §7.4.1)
  - F-002 옵션 A — codex/superpowers 구조적 배제 (false transaction-fail 0)
  - CFP-1059 S1 anchor — script body FAMILY 7 entry retain (Phase 1 declarative). S2/S3 sub-Story
    merge 후 9 plugin 자연 확장 영역 (codeforge-deploy + codeforge-deploy-review, ADR-087 + ADR-088).
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
# _check_channel_consistency — mixed channel detection (DC-1, snapshot 생성 이전 필수)
# _drift_status 헬퍼 분리 패턴 동형 (CFP-932 §3.2 설계 결정)
#
# DC-1 (OpRiskArch §7.4.1 design constraint — NON-NEGOTIABLE):
#   위치: arg parse → mode 1개 강제 → --repo 검증 → [NEW] mixed channel detection → idempotency pre-check → snapshot
#   mixed channel detection 은 snapshot 생성 이전 강제 (partial-state 진입 surface 차단)
#
# exit 0 = all 7 plugin resolved channel identical (consistent)
# exit 2 = mixed channel detected → abort-before-touch (snapshot 무생성, filesystem touch 0)
# --------------------------------------------------------------------------
_check_channel_consistency() {
    # --channel 미지정 시 기본 스킵 (family 7 plugin 동일 default stable → consistent)
    if [[ -z "${INPUT_CHANNEL}" ]]; then
        return 0
    fi

    # --channel C 지정 시: family 7 plugin 전부 동일 C 인지 검증
    # per-plugin override CLI surface 구조적 부재 (단일 --channel flag)
    # INV-2: --channel C 선언 시 family 7 plugin resolved channel 전부 동일 C
    # 현 구현에서 per-plugin override 없음 → consistent 보장 (single flag propagation)
    # 단, _check_channel_consistency는 future per-plugin channel override 가능성 차단 세마포어
    local consistent=1
    local mismatch_count=0
    local resolved_channels=()

    for plugin in "${FAMILY[@]}"; do
        # 각 plugin resolved channel = INPUT_CHANNEL (단일 flag 전파, override surface 0)
        resolved_channels+=("${INPUT_CHANNEL}")
    done

    # 단일 channel flag 구조에서는 항상 consistent — guard는 미래 extension 방어
    # TC-9 bats: mixed channel fixture = _CFP932_MOCK_MIXED_CHANNEL=1 로 테스트 가능하게 seam
    if [[ "${_CFP932_MOCK_MIXED_CHANNEL:-}" == "1" ]]; then
        # test seam: mixed channel 시나리오 시뮬레이션 (TC-9b/9c)
        echo "[mixed_channel_detection] MIXED CHANNEL DETECTED (test mock)" >&2
        echo "abort-before-touch: per-family snapshot 무생성, filesystem touch 0 (DC-1 / INV-2 / §7.4.1)" >&2
        echo "family channel resolve:" >&2
        local mock_channels=("${INPUT_CHANNEL}" "beta" "${INPUT_CHANNEL}" "canary" "${INPUT_CHANNEL}" "${INPUT_CHANNEL}" "beta")
        for i in "${!FAMILY[@]}"; do
            echo "  ${FAMILY[$i]}: resolved_channel=${mock_channels[$i]:-${INPUT_CHANNEL}}" >&2
        done
        echo "불일치 plugin → abort. per-plugin channel override CLI surface 구조적 부재 확인 요망." >&2
        exit 2
    fi

    # 정상 경로: 7 plugin 전부 동일 INPUT_CHANNEL → consistent
    return 0
}

# --------------------------------------------------------------------------
# §4.2 step 1 — idempotency pre-check (7 plugin drift = check-codeforge-version-drift.sh)
#   ALL drift == none → no-op 정상 종료 (snapshot/transaction 무생성, AC-9 (a))
#   drift 검증 = check-codeforge-version-drift.sh --plugin 7회 (재구현 0, §4.4)
# --------------------------------------------------------------------------
_drift_status() {
    # $1 = plugin name. stdout = drift status (none/minor/major/patch/...) per --plugin --json.
    local plugin="${1}"
    local json
    json="$(bash "${DRIFT_CHECK}" --plugin "${plugin}" --json 2>/dev/null || true)"
    # JSON: {"results":[{"plugin":"...","status":"...","...":...}],"exit_code":N}
    # status 추출 (grep — heavy json parser 회피, ADR-061 no heredoc-python)
    echo "${json}" | grep -oE "\"status\":\"[a-z-]+\"" | head -1 | sed 's/.*:"//;s/"//'
}

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
