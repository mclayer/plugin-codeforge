#!/usr/bin/env bash
# codeforge-upgrade.sh — CFP-743 Phase 2 — POSIX bash thin dispatcher
# CFP-932 Wave 4 sub-Epic #882 Story-2 D1 — --channel <stable|beta|canary> orthogonal arg 추가
# Change Plan §3.1 3 책임 분리 아키텍처 / §4.1 CLI 인자 schema / §4.4 drift-check ownership
#
# 역할: CLI layer (thin dispatcher ONLY)
#   - argument enum whitelist parse (--dry-run / --apply / --rollback <version>)
#   - --channel <stable|beta|canary> = 8번째 orthogonal arg (CFP-932 D1, §3.2-parser 8-invariant)
#   - unknown arg = reject (no free-text injection surface, §7.1 trust boundary)
#   - Orchestrator / UpgradeAgent 위임만 (reconcile semantic 로직 0건)
#   - check-codeforge-version-drift.sh 호출 금지 (UpgradeAgent Plan stage 귀속, §4.4)
#   - user_decision_branches: 0 (no prompt invariant, reconcile-protocol-v1)
#   - OQ-3 visible override (SecurityArch M-1a + M-1b): CLI --channel ≠ overlay 시 stdout 출력
#     + canary tier + CLI≠overlay 시 stderr [PRODUCTION-IMPACT WARNING] (no-prompt invariant 보존)
#
# §4.5 path normalization: 6 입력 형태 → canonical (scripts/lib/path_normalize.py 위임)
# abort-before-touch: path 정규화 실패 시 filesystem touch 0 보장 상태 abort

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NORMALIZE_PY="${SCRIPT_DIR}/lib/path_normalize.py"

# --------------------------------------------------------------------------
# 내부 헬퍼: path 정규화 (§4.5 abort-before-touch)
# --------------------------------------------------------------------------
_to_canonical() {
    local raw_path="${1}"
    local canonical
    canonical=$(python3 "${NORMALIZE_PY}" "${raw_path}" --repo-root "${REPO_ROOT}" 2>&1) || {
        local err_msg="${canonical}"
        echo "[path_normalization_failure] ${err_msg}" >&2
        echo "[path_normalization_failure] 원본 입력: ${raw_path}" >&2
        echo "abort-before-touch: filesystem touch 없이 종료 (Change Plan §4.5 / §7.4.1(e))" >&2
        exit 2
    }
    echo "${canonical}"
}

# --------------------------------------------------------------------------
# 사용법 출력
# --------------------------------------------------------------------------
_usage() {
    cat <<'USAGE'
codeforge-upgrade.sh — codeforge plugin 업그레이드 CLI (CFP-743 / CFP-744 AC-11 / CFP-932 D1)

사용법:
  bash scripts/codeforge-upgrade.sh --dry-run
  bash scripts/codeforge-upgrade.sh --apply
  bash scripts/codeforge-upgrade.sh --rollback <version>
  bash scripts/codeforge-upgrade.sh --apply --repo <consumer-repo-root>
  bash scripts/codeforge-upgrade.sh --apply --channel <stable|beta|canary>

옵션:
  --dry-run               desired state diff preview (filesystem touch 0, network call 가능)
  --apply                 snapshot → 9 영역 reconcile → 사후 sanity check (단일 atomic unit)
  --rollback <version>    해당 version snapshot restore (예: --rollback 5.74.0)
  --repo <path>           reconcile 대상 consumer repo root 명시 지정 (CFP-744 AC-11,
                          mode 와 순서 무관 — orthogonal). 미지정 시
                          CODEFORGE_REPO_ROOT env → 없으면 SCRIPT_DIR 부모 (현 동작 보존)
  --channel <tier>        channel tier 명시 지정 (CFP-932 D1, mode·--repo 와 순서 무관 — orthogonal)
                          enum 허용: stable (LOW risk) / beta (MEDIUM risk) / canary (HIGH risk)
                          미지정: UpgradeAgent 가 consumer overlay codeforge.channel.tier resolve
                                  → 미선언 시 derived default "stable"
                          canary 지정 시 admin 권장 (ADR-076 §결정 9.4, HIGH risk class)

원칙:
  - 사용자 결정 분기 0 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)
  - 실 reconcile semantic = UpgradeAgent 담당 (thin dispatcher)
  - check-codeforge-version-drift.sh 는 UpgradeAgent Plan stage 호출 (CLI 금지, §4.4)
  - --channel = enum parse + 위임 출력 확장만 (overlay resolve semantic = UpgradeAgent 위임)
USAGE
}

# --------------------------------------------------------------------------
# argument enum whitelist parse
# --------------------------------------------------------------------------
MODE=""
ROLLBACK_VERSION=""
INPUT_REPO=""        # CFP-744 AC-11 — --repo <path> override (미지정 = "")
INPUT_CHANNEL=""     # CFP-932 D1 — --channel <stable|beta|canary> override (미지정 = "")
MODE_SET_COUNT=0     # §3.7.2-parser (d) — mode 정확히 1개 강제

if [[ $# -eq 0 ]]; then
    _usage >&2
    echo "오류: 인자가 필요합니다. --dry-run / --apply / --rollback <version> 중 하나를 지정하세요." >&2
    exit 1
fi

# §3.7.2-parser (CFP-744 AC-11 / CFP-932 D1) — single-positional case → while/case loop parser.
# 8-invariant byte-level 보존 (7-invariant 무변경 보존 + 8번째 --channel orthogonal):
#   (a) 기존 mode invocation 동작·exit code·error 문구 byte-identical
#   (b) --repo orthogonal (mode 와 순서 무관, loop 가 각각 독립 consume)
#   (c) --rollback value-taking 보존 (다음 토큰 consume, shift 2 semantic)
#   (d) mode 정확히 1개 강제 + 중복/충돌 reject (MODE_SET_COUNT)
#   (e) unknown arg = enum whitelist reject (loop 내 즉시 reject, §7.1)
#   (f) downstream pipeline 무변경 (REPO_ROOT resolve 후 _to_canonical 동일)
#   (g) --repo/env 미지정 fallback = $(cd "${SCRIPT_DIR}/.." && pwd) byte-identical
#   (h) --channel orthogonal value-taking (CFP-932 D1) — MODE_SET_COUNT 미영향, enum whitelist exact-match
while [[ $# -gt 0 ]]; do
    case "${1}" in
        --dry-run)
            MODE="dry_run"
            MODE_SET_COUNT=$((MODE_SET_COUNT + 1))
            shift
            ;;
        --apply)
            MODE="transaction"
            MODE_SET_COUNT=$((MODE_SET_COUNT + 1))
            shift
            ;;
        --rollback)
            MODE="snapshot_restore"
            MODE_SET_COUNT=$((MODE_SET_COUNT + 1))
            if [[ $# -lt 2 ]]; then
                echo "오류: --rollback 에는 version 인자가 필요합니다. 예: --rollback 5.74.0" >&2
                exit 1
            fi
            ROLLBACK_VERSION="${2}"
            shift 2
            ;;
        --repo)
            # CFP-744 AC-11 — consumer_repo_root 명시 지정 (orthogonal, value-taking)
            if [[ $# -lt 2 ]]; then
                echo "오류: --repo 에는 path 인자가 필요합니다. 예: --repo /path/to/consumer-repo" >&2
                exit 1
            fi
            INPUT_REPO="${2}"
            shift 2
            ;;
        --channel)
            # CFP-932 D1 — channel tier 명시 지정 (orthogonal, value-taking, 8번째 arg)
            # §3.2-parser (h) invariant: MODE_SET_COUNT 미영향
            if [[ $# -lt 2 ]]; then
                echo "오류: --channel 에는 tier 인자가 필요합니다. 예: --channel stable" >&2
                exit 1
            fi
            INPUT_CHANNEL="${2}"
            # enum whitelist exact-match (SecurityArch M-5 §7.6 — literal case, 소문자만 valid)
            case "${INPUT_CHANNEL}" in
                stable|beta|canary)
                    # valid tier — accept
                    ;;
                *)
                    echo "오류: --channel 허용 값: stable / beta / canary (입력: '${INPUT_CHANNEL}')" >&2
                    echo "enum whitelist reject — SecurityArch M-5 §7.6 exact-match (소문자만 유효)" >&2
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
            echo "허용 인자: --dry-run / --apply / --rollback <version> / --repo <path> / --channel <stable|beta|canary>" >&2
            echo "unknown arg = enum whitelist reject (Change Plan §7.1 trust boundary)" >&2
            exit 1
            ;;
    esac
done

# §3.7.2-parser (d) — mode 정확히 1개 강제 (0개 = 인자 필요 / 2개+ = mode 충돌)
if [[ "${MODE_SET_COUNT}" -eq 0 ]]; then
    _usage >&2
    echo "오류: 인자가 필요합니다. --dry-run / --apply / --rollback <version> 중 하나를 지정하세요." >&2
    exit 1
fi
if [[ "${MODE_SET_COUNT}" -gt 1 ]]; then
    echo "오류: mode 인자는 정확히 1개여야 합니다 (--dry-run / --apply / --rollback 중복/충돌)." >&2
    exit 1
fi

# --------------------------------------------------------------------------
# §3.7.2-parser (g) — consumer_repo_root resolve (CFP-744 AC-11 §4.5)
#   우선순위: --repo <path> > CODEFORGE_REPO_ROOT env > SCRIPT_DIR 부모 (현 동작 byte-identical)
# --------------------------------------------------------------------------
if [[ -n "${INPUT_REPO}" ]]; then
    REPO_ROOT="${INPUT_REPO}"
elif [[ -n "${CODEFORGE_REPO_ROOT:-}" ]]; then
    REPO_ROOT="${CODEFORGE_REPO_ROOT}"
else
    # fallback = 현 Story-3 line 17-18 그대로 (byte-identical, §3.7.2-parser (g))
    REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

# --------------------------------------------------------------------------
# §4.5 / §7.4.1 (i) — --repo wrong-target 검증 (실재 디렉터리 AND .git 보유)
#   미지정 fallback (SCRIPT_DIR 부모) 은 plugin repo = 검증 skip (현 동작 보존)
# --------------------------------------------------------------------------
if [[ -n "${INPUT_REPO}" || -n "${CODEFORGE_REPO_ROOT:-}" ]]; then
    if [[ ! -d "${REPO_ROOT}" ]]; then
        echo "[repo_target_failure] 지정 repo 가 실재 디렉터리 아님: ${REPO_ROOT}" >&2
        echo "abort-before-touch: filesystem touch 없이 종료 (Change Plan §4.5 / §7.4.1(i))" >&2
        exit 2
    fi
    if [[ ! -d "${REPO_ROOT}/.git" ]]; then
        echo "[repo_target_failure] 지정 repo 가 git repo 아님 (.git 부재): ${REPO_ROOT}" >&2
        echo "reconcile target 재확인 요망 (오타 / 다른 repo / non-git 디렉터리)" >&2
        echo "abort-before-touch: filesystem touch 없이 종료 (Change Plan §4.5 / §7.4.1(i))" >&2
        exit 2
    fi
fi

# --------------------------------------------------------------------------
# repo root path 정규화 (§4.5 — abort-before-touch on failure)
# §3.7.2-parser (f) — resolve source 만 확장, downstream pipeline byte 무변경
# --------------------------------------------------------------------------
CANONICAL_REPO_ROOT="$(_to_canonical "${REPO_ROOT}")"

# --------------------------------------------------------------------------
# OQ-3 visible override (SecurityArch M-1a + M-1b — CFP-932 §4.1)
# consumer overlay resolve는 UpgradeAgent 위임 — CLI layer에서는 override 가시화만
# --------------------------------------------------------------------------
OVERLAY_CHANNEL=""
# consumer overlay project.yaml 경로 추론 (CODEFORGE_REPO_ROOT or CANONICAL_REPO_ROOT 하위)
OVERLAY_YAML="${CANONICAL_REPO_ROOT}/.claude/_overlay/project.yaml"
if [[ -f "${OVERLAY_YAML}" ]]; then
    OVERLAY_CHANNEL="$(python3 - "${OVERLAY_YAML}" 2>/dev/null <<'PYEOF' || echo ""
import sys, yaml
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
codeforge = (data or {}).get("codeforge", {}) or {}
channel = codeforge.get("channel") or {}
tier = (channel if isinstance(channel, dict) else {}).get("tier", "")
print(tier)
PYEOF
)"
fi

# M-1a: CLI --channel 명시값 ≠ overlay 충돌 시 stdout 출력 (no-prompt invariant 보존)
if [[ -n "${INPUT_CHANNEL}" ]] && [[ -n "${OVERLAY_CHANNEL}" ]] && [[ "${INPUT_CHANNEL}" != "${OVERLAY_CHANNEL}" ]]; then
    echo "CLI override: overlay=${OVERLAY_CHANNEL} → CLI=${INPUT_CHANNEL}"
    # M-1b: canary tier + CLI≠overlay 시 stderr [PRODUCTION-IMPACT WARNING] 차등 emit
    if [[ "${INPUT_CHANNEL}" == "canary" ]]; then
        echo "[PRODUCTION-IMPACT WARNING] canary tier resolved via CLI override (overlay 의도=${OVERLAY_CHANNEL}). ADR-076 §결정 9.4 — canary = HIGH risk, admin 권장." >&2
    fi
fi

# --------------------------------------------------------------------------
# UpgradeAgent spawn 위임 출력 (Orchestrator 가 이 출력을 읽어 subagent spawn)
# reconcile semantic 로직 0건 — thin dispatcher
# --------------------------------------------------------------------------
echo "=== codeforge-upgrade.sh: UpgradeAgent spawn 위임 ==="
echo "mode: ${MODE}"
if [[ "${MODE}" == "snapshot_restore" ]]; then
    echo "rollback_version: ${ROLLBACK_VERSION}"
fi
echo "canonical_repo_root: ${CANONICAL_REPO_ROOT}"
echo "channel_input: ${INPUT_CHANNEL:-(미지정 — overlay resolve or stable fallback)}"
echo "reconcile_protocol_version: 1.8"
echo "user_decision_branches: 0"
echo ""
echo "--- Orchestrator: 아래 UpgradeAgent 를 spawn 하여 처리하십시오 ---"
echo "agent_file: templates/agents/UpgradeAgent.md"
echo "input_mode: ${MODE}"
if [[ "${MODE}" == "snapshot_restore" ]]; then
    echo "input_rollback_version: ${ROLLBACK_VERSION}"
fi
echo "input_repo_root: ${CANONICAL_REPO_ROOT}"
if [[ -n "${INPUT_CHANNEL}" ]]; then
    echo "input_channel: ${INPUT_CHANNEL}"
fi
echo ""
echo "주의: check-codeforge-version-drift.sh 는 UpgradeAgent Plan stage 에서 호출 (CLI 금지 — §4.4)"
echo "주의: 사용자 결정 분기 0 유지 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)"
echo "주의: --channel resolve semantic = UpgradeAgent 위임 (overlay codeforge.channel.tier resolve, 미선언=stable)"
