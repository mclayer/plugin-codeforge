#!/usr/bin/env bash
# walk-single-plugin.sh — CFP-1170 Phase 2 — per-plugin imperative walk CLI
#
# Change Plan §3.2 / §4.1 CLI arg enum / §7.1 trust boundary
#
# 역할: CLI layer (per-plugin walk thin dispatcher ONLY)
#   - argument enum whitelist parse (--walk / --plan / --apply / --rollback <version>)
#   - --plugin <name> = FAMILY membership check (enum exact-match)
#   - --repo <path> = wrong-target 검증 (실재 디렉터리 AND .git 보유)
#   - --channel <stable|beta|canary> = enum exact-match (§7.6 소문자만 valid)
#   - unknown arg = enum whitelist reject (no free-text injection surface — §7.1 trust boundary)
#   - walk semantic 로직 0건 — walk_plan.py + UpgradeAgent 위임만
#   - user_decision_branches: 0 (no prompt invariant)
#
# mode → UpgradeAgent input_mode mapping (§3.2):
#   --walk    → Stage 1 walk only (filesystem touch 0, read-only)
#   --plan    → Stage 1+2 (walk + plan, dry — filesystem touch 0)
#   --apply   → Stage 1+2+3 (transaction mode)
#   --rollback <version> → snapshot_restore mode
#
# 기존 codeforge-upgrade.sh 8-invariant arg parser 답습 (change-plan §6.1)
# ADR-061 정합 — heredoc-python 0 (POSIX bash only, Python = walk_plan.py SSOT)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NORMALIZE_PY="${SCRIPT_DIR}/lib/path_normalize.py"

# codeforge family 9 plugin (F-002 옵션 A — codex/superpowers 구조적 배제)
# change-plan §3.2 / §4.1 §7.1 — FAMILY membership check
# CFP-1219: deploy lane 활성화 (CFP-1059 S2/S3 resolved) — 6 lane → 8 lane
FAMILY_PLUGINS=(
    codeforge
    codeforge-requirements
    codeforge-design
    codeforge-review
    codeforge-develop
    codeforge-test
    codeforge-pmo
    codeforge-deploy          # ADR-087 Deploy lane (CFP-1219 활성)
    codeforge-deploy-review   # ADR-088 Deploy Review lane (CFP-1219 활성)
)

# --------------------------------------------------------------------------
# 내부 헬퍼: path 정규화 (§4.5 abort-before-touch)
# --------------------------------------------------------------------------
_to_canonical() {
    local raw_path="${1}"
    local canonical
    if [[ -f "${NORMALIZE_PY}" ]]; then
        canonical=$(python3 "${NORMALIZE_PY}" "${raw_path}" --repo-root "${raw_path}" 2>&1) || {
            local err_msg="${canonical}"
            echo "[path_normalization_failure] ${err_msg}" >&2
            echo "[path_normalization_failure] 원본 입력: ${raw_path}" >&2
            echo "abort-before-touch: filesystem touch 없이 종료 (Change Plan §4.5)" >&2
            exit 2
        }
    else
        # path_normalize.py 미존재 fallback = realpath (POSIX)
        canonical="$(cd "${raw_path}" 2>/dev/null && pwd)" || {
            echo "[path_normalization_failure] 경로 정규화 실패: ${raw_path}" >&2
            exit 2
        }
    fi
    echo "${canonical}"
}

# --------------------------------------------------------------------------
# 사용법 출력 (§4.1 CLI arg schema)
# --------------------------------------------------------------------------
_usage() {
    cat <<'USAGE'
walk-single-plugin.sh — per-plugin imperative walk CLI (CFP-1170)

사용법:
  bash scripts/walk-single-plugin.sh --walk --plugin <plugin-name>
  bash scripts/walk-single-plugin.sh --plan --plugin <plugin-name>
  bash scripts/walk-single-plugin.sh --apply --plugin <plugin-name>
  bash scripts/walk-single-plugin.sh --rollback <version> --plugin <plugin-name>
  bash scripts/walk-single-plugin.sh --apply --plugin <plugin-name> --repo <consumer-repo-root>
  bash scripts/walk-single-plugin.sh --apply --plugin <plugin-name> --channel <stable|beta|canary>

mode enum (정확히 1개 강제):
  --walk                Stage 1 walk only — per-plugin CHANGELOG.md (from→to) 구간 enumerate
                        (read-only, filesystem touch 0)
  --plan                Stage 1+2 — walk + plan (changelog entry + min_prereq check, dry
                        filesystem touch 0)
  --apply               Stage 1+2+3 — transaction (snapshot → apply → sanity check, per-plugin atomic)
  --rollback <version>  snapshot_restore mode (지정 version snapshot restore)

orthogonal arg (value-taking, mode 와 순서 무관):
  --plugin <name>       walk 대상 plugin (enum whitelist: codeforge + 8 lane — exact-match)
  --repo <path>         consumer repo root (미지정 = CODEFORGE_REPO_ROOT env → SCRIPT_DIR 부모)
  --channel <tier>      channel tier enum: stable / beta / canary (exact-match, 소문자만)
                        미지정 = UpgradeAgent overlay resolve or stable fallback

원칙:
  - 사용자 결정 분기 0 (no prompt — user_decision_branches: 0)
  - walk semantic 로직 0건 — UpgradeAgent spawn 위임 (thin dispatcher)
  - per-plugin FAMILY membership check (codex/superpowers 구조적 배제)
  - --channel 미지정 = UpgradeAgent overlay resolve
USAGE
}

# --------------------------------------------------------------------------
# argument enum whitelist parse
# codeforge-upgrade.sh §3.7.2-parser 8-invariant 구조 답습 + walk mode 추가
# --------------------------------------------------------------------------
MODE=""
ROLLBACK_VERSION=""
INPUT_REPO=""
INPUT_CHANNEL=""
INPUT_PLUGIN=""
MODE_SET_COUNT=0

if [[ $# -eq 0 ]]; then
    _usage >&2
    echo "오류: 인자가 필요합니다. --walk / --plan / --apply / --rollback <version> 중 하나를 지정하세요." >&2
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case "${1}" in
        --walk)
            MODE="walk"
            MODE_SET_COUNT=$((MODE_SET_COUNT + 1))
            shift
            ;;
        --plan)
            MODE="plan"
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
        --plugin)
            if [[ $# -lt 2 ]]; then
                echo "오류: --plugin 에는 plugin 이름이 필요합니다. 예: --plugin codeforge" >&2
                exit 1
            fi
            INPUT_PLUGIN="${2}"
            shift 2
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
            if [[ $# -lt 2 ]]; then
                echo "오류: --channel 에는 tier 인자가 필요합니다. 예: --channel stable" >&2
                exit 1
            fi
            INPUT_CHANNEL="${2}"
            # enum whitelist exact-match (SecurityArch M-5 §7.6 — 소문자만 valid)
            case "${INPUT_CHANNEL}" in
                stable|beta|canary)
                    # valid tier — accept
                    ;;
                *)
                    echo "오류: --channel 허용 값: stable / beta / canary (입력: '${INPUT_CHANNEL}')" >&2
                    echo "enum whitelist reject — §7.6 exact-match (소문자만 유효)" >&2
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
            echo "허용 인자: --walk / --plan / --apply / --rollback <version> / --plugin <name> / --repo <path> / --channel <stable|beta|canary>" >&2
            echo "unknown arg = enum whitelist reject (Change Plan §7.1 trust boundary)" >&2
            exit 1
            ;;
    esac
done

# mode 정확히 1개 강제 (codeforge-upgrade §3.7.2-parser (d) 동형)
if [[ "${MODE_SET_COUNT}" -eq 0 ]]; then
    _usage >&2
    echo "오류: mode 인자가 필요합니다. --walk / --plan / --apply / --rollback <version> 중 하나를 지정하세요." >&2
    exit 1
fi
if [[ "${MODE_SET_COUNT}" -gt 1 ]]; then
    echo "오류: mode 인자는 정확히 1개여야 합니다 (--walk / --plan / --apply / --rollback 중복/충돌)." >&2
    exit 1
fi

# --------------------------------------------------------------------------
# --plugin FAMILY membership check (§7.1 — codex/superpowers 구조적 배제)
# --------------------------------------------------------------------------
if [[ -z "${INPUT_PLUGIN}" ]]; then
    echo "오류: --plugin 인자가 필요합니다. 예: --plugin codeforge" >&2
    echo "허용 plugin: ${FAMILY_PLUGINS[*]}" >&2
    exit 1
fi

_is_family_member() {
    local plugin="${1}"
    for member in "${FAMILY_PLUGINS[@]}"; do
        if [[ "${member}" == "${plugin}" ]]; then
            return 0
        fi
    done
    return 1
}

if ! _is_family_member "${INPUT_PLUGIN}"; then
    echo "오류: '${INPUT_PLUGIN}' 는 codeforge family 구성원이 아닙니다." >&2
    echo "허용 plugin (enum whitelist): ${FAMILY_PLUGINS[*]}" >&2
    echo "unknown plugin = enum whitelist reject (Change Plan §7.1 / §7.2 — codex/superpowers 구조적 배제)" >&2
    exit 1
fi

# --------------------------------------------------------------------------
# --repo wrong-target 검증 (§4.5 / §7.4.1 (i) — abort-before-touch)
# --------------------------------------------------------------------------
if [[ -n "${INPUT_REPO}" ]]; then
    if [[ ! -d "${INPUT_REPO}" ]]; then
        echo "[repo_target_failure] 지정 repo 가 실재 디렉터리 아님: ${INPUT_REPO}" >&2
        echo "abort-before-touch: filesystem touch 없이 종료 (§4.5 / §7.4.1(i))" >&2
        exit 2
    fi
    if [[ ! -d "${INPUT_REPO}/.git" ]]; then
        echo "[repo_target_failure] 지정 repo 가 git repo 아님 (.git 부재): ${INPUT_REPO}" >&2
        echo "reconcile target 재확인 요망 (오타 / 다른 repo / non-git 디렉터리)" >&2
        echo "abort-before-touch: filesystem touch 없이 종료 (§4.5 / §7.4.1(i))" >&2
        exit 2
    fi
fi

# --------------------------------------------------------------------------
# repo root resolve (codeforge-upgrade §3.7.2-parser (g) 동형)
#   우선순위: --repo <path> > CODEFORGE_REPO_ROOT env > SCRIPT_DIR 부모
# --------------------------------------------------------------------------
if [[ -n "${INPUT_REPO}" ]]; then
    REPO_ROOT="${INPUT_REPO}"
elif [[ -n "${CODEFORGE_REPO_ROOT:-}" ]]; then
    REPO_ROOT="${CODEFORGE_REPO_ROOT}"
else
    REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

# --------------------------------------------------------------------------
# UpgradeAgent spawn 위임 출력 (thin dispatcher — walk semantic 로직 0건)
# --------------------------------------------------------------------------
echo "=== walk-single-plugin.sh: UpgradeAgent spawn 위임 (per-plugin walk) ==="
echo "plugin: ${INPUT_PLUGIN}"
echo "mode: ${MODE}"
if [[ "${MODE}" == "snapshot_restore" ]]; then
    echo "rollback_version: ${ROLLBACK_VERSION}"
fi
echo "repo_root: ${REPO_ROOT}"
echo "channel_input: ${INPUT_CHANNEL:-(미지정 — overlay resolve or stable fallback)}"
echo "imperative_walker_protocol_version: 1.0"
echo "user_decision_branches: 0"
echo ""

# mode-specific 출력
case "${MODE}" in
    walk)
        echo "--- Stage 1 walk only (read-only, filesystem touch 0) ---"
        echo "walk_stage: read-only CHANGELOG.md enumerate (from→to, ADR-092)"
        echo "filesystem_touch: 0"
        echo "network_scope: offline (local CHANGELOG.md read only)"
        ;;
    plan)
        echo "--- Stage 1+2 walk + plan (dry, filesystem touch 0) ---"
        echo "walk_stage: CHANGELOG.md enumerate (from→to)"
        echo "plan_stage: changelog entry + min_prereq topological check (ADR-096)"
        echo "filesystem_touch: 0"
        echo "dry_run: true"
        ;;
    transaction)
        echo "--- Stage 1+2+3 transaction (per-plugin atomic apply) ---"
        echo "input_mode: transaction"
        ;;
    snapshot_restore)
        echo "--- snapshot_restore mode ---"
        echo "input_rollback_version: ${ROLLBACK_VERSION}"
        ;;
esac

echo ""
echo "--- Orchestrator: 아래 UpgradeAgent 를 spawn 하여 처리하십시오 ---"
echo "agent_file: templates/agents/UpgradeAgent.md"
echo "input_mode: ${MODE}"
if [[ "${MODE}" == "snapshot_restore" ]]; then
    echo "input_rollback_version: ${ROLLBACK_VERSION}"
fi
echo "input_plugin: ${INPUT_PLUGIN}"
echo "input_repo_root: ${REPO_ROOT}"
if [[ -n "${INPUT_CHANNEL}" ]]; then
    echo "input_channel: ${INPUT_CHANNEL}"
fi
echo ""
echo "주의: walk semantic 로직 0건 — UpgradeAgent Stage 1/2/3 위임 (thin dispatcher)"
echo "주의: 사용자 결정 분기 0 (no prompt — user_decision_branches: 0)"
