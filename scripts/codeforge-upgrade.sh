#!/usr/bin/env bash
# codeforge-upgrade.sh — CFP-743 Phase 2 — POSIX bash thin dispatcher
# Change Plan §3.1 3 책임 분리 아키텍처 / §4.1 CLI 인자 schema / §4.4 drift-check ownership
#
# 역할: CLI layer (thin dispatcher ONLY)
#   - argument enum whitelist parse (--dry-run / --apply / --rollback <version>)
#   - unknown arg = reject (no free-text injection surface, §7.1 trust boundary)
#   - Orchestrator / UpgradeAgent 위임만 (reconcile semantic 로직 0건)
#   - check-codeforge-version-drift.sh 호출 금지 (UpgradeAgent Plan stage 귀속, §4.4)
#   - user_decision_branches: 0 (no prompt invariant, reconcile-protocol-v1)
#
# §4.5 path normalization: 6 입력 형태 → canonical (scripts/lib/path_normalize.py 위임)
# abort-before-touch: path 정규화 실패 시 filesystem touch 0 보장 상태 abort

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
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
codeforge-upgrade.sh — codeforge plugin 업그레이드 CLI (CFP-743)

사용법:
  bash scripts/codeforge-upgrade.sh --dry-run
  bash scripts/codeforge-upgrade.sh --apply
  bash scripts/codeforge-upgrade.sh --rollback <version>

옵션:
  --dry-run               desired state diff preview (filesystem touch 0, network call 가능)
  --apply                 snapshot → 9 영역 reconcile → 사후 sanity check (단일 atomic unit)
  --rollback <version>    해당 version snapshot restore (예: --rollback 5.74.0)

원칙:
  - 사용자 결정 분기 0 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)
  - 실 reconcile semantic = UpgradeAgent 담당 (thin dispatcher)
  - check-codeforge-version-drift.sh 는 UpgradeAgent Plan stage 호출 (CLI 금지, §4.4)
USAGE
}

# --------------------------------------------------------------------------
# argument enum whitelist parse
# --------------------------------------------------------------------------
MODE=""
ROLLBACK_VERSION=""

if [[ $# -eq 0 ]]; then
    _usage >&2
    echo "오류: 인자가 필요합니다. --dry-run / --apply / --rollback <version> 중 하나를 지정하세요." >&2
    exit 1
fi

case "${1}" in
    --dry-run)
        MODE="dry_run"
        shift
        ;;
    --apply)
        MODE="transaction"
        shift
        ;;
    --rollback)
        MODE="snapshot_restore"
        if [[ $# -lt 2 ]]; then
            echo "오류: --rollback 에는 version 인자가 필요합니다. 예: --rollback 5.74.0" >&2
            exit 1
        fi
        ROLLBACK_VERSION="${2}"
        shift 2
        ;;
    --help|-h)
        _usage
        exit 0
        ;;
    *)
        # unknown arg = enum whitelist reject (§7.1 free-text injection surface 0)
        echo "오류: 알 수 없는 인자: '${1}'" >&2
        echo "허용 인자: --dry-run / --apply / --rollback <version>" >&2
        echo "unknown arg = enum whitelist reject (Change Plan §7.1 trust boundary)" >&2
        exit 1
        ;;
esac

# 추가 인자 거부 (free-text injection 차단)
if [[ $# -gt 0 ]]; then
    echo "오류: 예상치 못한 추가 인자: '$*'" >&2
    exit 1
fi

# --------------------------------------------------------------------------
# repo root path 정규화 (§4.5 — abort-before-touch on failure)
# --------------------------------------------------------------------------
CANONICAL_REPO_ROOT="$(_to_canonical "${REPO_ROOT}")"

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
echo "reconcile_protocol_version: 1.2"
echo "user_decision_branches: 0"
echo ""
echo "--- Orchestrator: 아래 UpgradeAgent 를 spawn 하여 처리하십시오 ---"
echo "agent_file: templates/agents/UpgradeAgent.md"
echo "input_mode: ${MODE}"
if [[ "${MODE}" == "snapshot_restore" ]]; then
    echo "input_rollback_version: ${ROLLBACK_VERSION}"
fi
echo "input_repo_root: ${CANONICAL_REPO_ROOT}"
echo ""
echo "주의: check-codeforge-version-drift.sh 는 UpgradeAgent Plan stage 에서 호출 (CLI 금지 — §4.4)"
echo "주의: 사용자 결정 분기 0 유지 (no prompt — reconcile-protocol-v1 user_decision_branches: 0)"
