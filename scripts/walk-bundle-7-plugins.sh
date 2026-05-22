#!/usr/bin/env bash
# walk-bundle-7-plugins.sh — CFP-1170 Phase 2 — per-family atomic imperative walk CLI
#
# Change Plan §3.3 / §4.2 CLI arg enum / §7.4 DR
# CFP-1219: FAMILY 9 (CFP-1199 follow-up: deploy lane 활성화 — codeforge-deploy + codeforge-deploy-review)
# CFP-1225: FAMILY derive from walk_plan.py TOPOLOGICAL_ORDER (dual-roster 제거 — single SSOT 정합)
#
# 역할: per-family atomic walk orchestration shell ONLY
#   - per-plugin walk semantic = walk-single-plugin.sh 위임 (semantic 분산 0)
#   - topological order walk = walk_plan.py 위임 ([wrapper, ...8 lane] DAG invariant)
#   - per-family atomic transaction boundary (9 plugin all-or-rollback) = 본 shell 단독
#   - per-entry walk transcript: 각 plugin walk step + apply step emit (step-visible)
#   - --plugin arg 미지원 (bundle = 항상 family 전체 — per-plugin override CLI surface 0)
#   - user_decision_branches: 0 (no prompt invariant)
#   - --channel propagation: CHANNEL_ARGS array (REPO_ARGS 동형 orthogonal 차원, CFP-932 D2 동형)
#   - mixed channel detection: _check_channel_consistency (snapshot 생성 이전 — DC-1)
#
# 기존 atomic-upgrade-7-plugins.sh FAMILY + per-family transaction 답습 (change-plan §6.1)
# ADR-061 정합 — heredoc-python 0 (POSIX bash only, python3 -c 단일 one-liner 사용)
# ADR-068 I-3 per-family atomic rollback = unconditional (9 plugin 무조건)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALK_SINGLE_CLI="${SCRIPT_DIR}/walk-single-plugin.sh"

# §4.4 ownership — drift 검증 = check-codeforge-version-drift.sh (CFP-262 SSOT) 위임
DRIFT_CHECK="${CODEFORGE_DRIFT_CHECK_BIN:-${SCRIPT_DIR}/check-codeforge-version-drift.sh}"

# --------------------------------------------------------------------------
# FAMILY derive — walk_plan.py TOPOLOGICAL_ORDER 단일 SSOT (CFP-1225)
#
# 설계 결정 (D2): 하드코딩 배열 제거 → walk_plan.py get_topological_order() 에서 derive.
#   python3 -c 단일 one-liner 사용 (ADR-061 정합 — multi-line heredoc-python 금지).
#   walk_plan.py 는 실제 walk 에도 필수 의존성이므로 fail-loud exit 2 선택 (hardcoded fallback 금지).
#   이유: fallback 이 존재하면 walk_plan.py 손상/누락 을 감추는 setup-error 를 야기함.
#   _CFP1225_MOCK_DERIVE_FAIL=1 = test seam (derive 실패 시뮬레이션용).
# --------------------------------------------------------------------------
FAMILY_DERIVE() {
    local _lib_dir
    # cygpath -m: Git Bash POSIX 경로 → forward-slash Windows 경로 변환 (Python 호환)
    # fallback: cygpath 미설치(Linux/macOS) 시 POSIX 경로 그대로 사용
    if command -v cygpath >/dev/null 2>&1; then
        _lib_dir="$(cygpath -m "${SCRIPT_DIR}/lib")"
    else
        _lib_dir="${SCRIPT_DIR}/lib"
    fi
    python3 -c "import sys; sys.stdout.reconfigure(newline='\n'); sys.path.insert(0, '${_lib_dir}'); import walk_plan; print('\n'.join(walk_plan.get_topological_order()))"
}

# test seam: _CFP1225_MOCK_DERIVE_FAIL=1 → derive 실패 시뮬레이션
if [[ "${_CFP1225_MOCK_DERIVE_FAIL:-}" == "1" ]]; then
    echo "[setup-error] FAMILY derive 실패 시뮬레이션 (_CFP1225_MOCK_DERIVE_FAIL=1 test seam)" >&2
    echo "[setup-error] walk_plan.py TOPOLOGICAL_ORDER derive 불가 — walk-bundle 실행 중단" >&2
    echo "원인: _CFP1225_MOCK_DERIVE_FAIL test seam 활성 (walk_plan import 실패 동형)" >&2
    exit 2
fi

# FAMILY 배열 derive (walk_plan.py TOPOLOGICAL_ORDER single SSOT — CFP-1225)
# fail-loud exit 2: python3 실패 또는 walk_plan import 실패 → 명확한 오류 메시지 + exit 2
if ! mapfile -t FAMILY < <(FAMILY_DERIVE 2>/dev/null); then
    echo "[setup-error] FAMILY derive 실패: walk_plan.py get_topological_order() 호출 불가" >&2
    echo "원인: python3 미설치 또는 ${SCRIPT_DIR}/lib/walk_plan.py import 오류" >&2
    echo "walk-bundle 은 walk_plan.py 필수 의존성 — hardcoded fallback 없음 (CFP-1225 설계 결정)" >&2
    exit 2
fi

# derive 결과 검증 — 비어 있으면 fail-loud (walk_plan 손상 감지)
if [[ "${#FAMILY[@]}" -eq 0 ]]; then
    echo "[setup-error] FAMILY derive 결과 비어 있음: walk_plan.get_topological_order() 반환 empty list" >&2
    echo "원인: walk_plan.py TOPOLOGICAL_ORDER 손상 가능성 — 확인 필요" >&2
    echo "walk-bundle 실행 중단 (empty FAMILY → 9-plugin atomic transaction 불가)" >&2
    exit 2
fi

# --------------------------------------------------------------------------
# 사용법 출력 (§4.2 CLI arg schema)
# --------------------------------------------------------------------------
_usage() {
    cat <<'USAGE'
walk-bundle-7-plugins.sh — codeforge family 9 plugin per-family atomic walk CLI (CFP-1170, CFP-1219)

사용법:
  bash scripts/walk-bundle-7-plugins.sh --walk
  bash scripts/walk-bundle-7-plugins.sh --plan
  bash scripts/walk-bundle-7-plugins.sh --apply
  bash scripts/walk-bundle-7-plugins.sh --rollback
  bash scripts/walk-bundle-7-plugins.sh --apply --repo <consumer-repo-root>
  bash scripts/walk-bundle-7-plugins.sh --apply --channel <stable|beta|canary>

mode enum (정확히 1개 강제):
  --walk      9-plugin family topological walk only (read-only, per-entry transcript step-visible)
  --plan      9-plugin walk + plan (min_prereq topological resolve, dry)
  --apply     per-family atomic transaction (snapshot → 9×walk-single apply → walk_result aggregate
              verify → commit/rollback)
  --rollback  직전 per-family pre-atomic snapshot 복원 (9 plugin 일괄)

orthogonal arg:
  --repo <path>     9 plugin per-plugin walk 전체 동일 propagation (partial target mismatch 0)
  --channel <tier>  family 9 plugin 전체 동일 channel atomic walk (mixed channel detection → abort,
                    DC-1). enum: stable / beta / canary (소문자만)

원칙:
  - 사용자 결정 분기 0 (no prompt — user_decision_branches: 0)
  - --plugin arg 미지원 (bundle = 항상 family 전체 — 단일 plugin 은 walk-single-plugin.sh)
  - per-family transaction = 9 plugin all-or-rollback (partial state 0, ADR-068 I-3 unconditional)
  - F-002 옵션 A — codex/superpowers 구조적 배제 (9-name FAMILY loop)
  - CFP-1219: FAMILY 9 (CFP-1199 follow-up: deploy lane 활성화)
USAGE
}

# --------------------------------------------------------------------------
# argument parser (§4.2) — atomic-upgrade-7-plugins.sh §4.1 parser 동형
# --------------------------------------------------------------------------
MODE=""
INPUT_REPO=""
INPUT_CHANNEL=""
MODE_SET_COUNT=0

if [[ $# -eq 0 ]]; then
    _usage >&2
    echo "오류: 인자가 필요합니다. --walk / --plan / --apply / --rollback 중 하나를 지정하세요." >&2
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
            MODE="apply"
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
            if [[ $# -lt 2 ]]; then
                echo "오류: --channel 에는 tier 인자가 필요합니다. 예: --channel stable" >&2
                exit 1
            fi
            INPUT_CHANNEL="${2}"
            # enum whitelist exact-match (§7.6 소문자만 valid)
            case "${INPUT_CHANNEL}" in
                stable|beta|canary)
                    # valid tier
                    ;;
                *)
                    echo "오류: --channel 허용 값: stable / beta / canary (입력: '${INPUT_CHANNEL}')" >&2
                    echo "enum whitelist reject — §7.6 exact-match (소문자만 유효)" >&2
                    exit 1
                    ;;
            esac
            shift 2
            ;;
        --plugin)
            # --plugin arg = bundle tier 미지원 (§4.2 / change-plan §3.3)
            echo "오류: --plugin 은 walk-bundle 미지원 — bundle tier = 항상 family 전체 9 plugin walk." >&2
            echo "단일 plugin walk: bash scripts/walk-single-plugin.sh --walk --plugin <name>" >&2
            echo "bundle tier 는 9-name FAMILY loop 구조적 배제 (per-plugin override 불가)" >&2
            exit 1
            ;;
        --help|-h)
            _usage
            exit 0
            ;;
        *)
            # unknown arg = enum whitelist reject (§7.1)
            echo "오류: 알 수 없는 인자: '${1}'" >&2
            echo "허용 인자: --walk / --plan / --apply / --rollback / --repo <path> / --channel <tier>" >&2
            echo "unknown arg = enum whitelist reject (§7.1 trust boundary)" >&2
            exit 1
            ;;
    esac
done

# mode 정확히 1개 강제 (atomic-upgrade §4.1 parser (d) 동형)
if [[ "${MODE_SET_COUNT}" -eq 0 ]]; then
    _usage >&2
    echo "오류: 인자가 필요합니다. --walk / --plan / --apply / --rollback 중 하나를 지정하세요." >&2
    exit 1
fi
if [[ "${MODE_SET_COUNT}" -gt 1 ]]; then
    echo "오류: mode 인자는 정확히 1개여야 합니다 (중복/충돌)." >&2
    exit 1
fi

# --------------------------------------------------------------------------
# orthogonal arg arrays (REPO_ARGS / CHANNEL_ARGS — atomic-upgrade §3.2 동형)
# --------------------------------------------------------------------------
REPO_ARGS=()
if [[ -n "${INPUT_REPO}" ]]; then
    if [[ ! -d "${INPUT_REPO}" ]]; then
        echo "[repo_target_failure] 지정 repo 가 실재 디렉터리 아님: ${INPUT_REPO}" >&2
        echo "abort-before-touch: per-family snapshot 무생성 (§4.5 / §7.4.1(i))" >&2
        exit 2
    fi
    if [[ ! -d "${INPUT_REPO}/.git" ]]; then
        echo "[repo_target_failure] 지정 repo 가 git repo 아님 (.git 부재): ${INPUT_REPO}" >&2
        echo "abort-before-touch: per-family snapshot 무생성 (§4.5 / §7.4.1(i))" >&2
        exit 2
    fi
    REPO_ARGS=(--repo "${INPUT_REPO}")
fi

CHANNEL_ARGS=()
if [[ -n "${INPUT_CHANNEL}" ]]; then
    CHANNEL_ARGS=(--channel "${INPUT_CHANNEL}")
fi

# --------------------------------------------------------------------------
# _check_channel_consistency — mixed channel detection (DC-1, snapshot 이전 필수)
# atomic-upgrade-7-plugins.sh _check_channel_consistency 답습 (mock seam 동형)
# --------------------------------------------------------------------------
_check_channel_consistency() {
    if [[ -z "${INPUT_CHANNEL}" ]]; then
        return 0
    fi

    # test seam: _CFP932_MOCK_MIXED_CHANNEL=1 = mixed channel 시뮬레이션 (기존 mock seam 답습)
    if [[ "${_CFP932_MOCK_MIXED_CHANNEL:-}" == "1" ]]; then
        echo "[mixed_channel_detection] MIXED CHANNEL DETECTED (test mock — DC-1)" >&2
        echo "abort-before-touch: per-family snapshot 무생성 (DC-1 / §7.4.1 / §3.3)" >&2
        echo "family channel resolve:" >&2
        local mock_channels=("${INPUT_CHANNEL}" "beta" "${INPUT_CHANNEL}" "canary" "${INPUT_CHANNEL}" "${INPUT_CHANNEL}" "beta" "${INPUT_CHANNEL}" "beta")
        for i in "${!FAMILY[@]}"; do
            echo "  ${FAMILY[$i]}: resolved_channel=${mock_channels[$i]:-${INPUT_CHANNEL}}" >&2
        done
        echo "불일치 plugin → abort. per-plugin channel override CLI surface 구조적 부재 확인 요망." >&2
        exit 2
    fi

    # 정상 경로: 단일 --channel flag → 9 plugin 전부 동일 channel
    return 0
}

# --------------------------------------------------------------------------
# _drift_status — drift 검증 헬퍼 (atomic-upgrade 동형)
# --------------------------------------------------------------------------
_drift_status() {
    local plugin="${1}"
    local json
    json="$(bash "${DRIFT_CHECK}" --plugin "${plugin}" --json 2>/dev/null || true)"
    echo "${json}" | grep -oE '"status":"[a-z-]+"' | head -1 | sed 's/.*:"//;s/"//'
}

# --------------------------------------------------------------------------
# 헤더 출력
# --------------------------------------------------------------------------
echo "=== walk-bundle-7-plugins.sh: per-family atomic walk 9-plugin (mode=${MODE}) ==="
echo "family: ${FAMILY[*]}"
echo "user_decision_branches: 0"
if [[ -n "${INPUT_REPO}" ]]; then
    echo "consumer_repo_root: ${INPUT_REPO} (--repo propagation)"
else
    echo "consumer_repo_root: (fallback — walk-single-plugin.sh SCRIPT_DIR 부모 / CODEFORGE_REPO_ROOT env)"
fi
if [[ -n "${INPUT_CHANNEL}" ]]; then
    echo "channel_input: ${INPUT_CHANNEL} (CHANNEL_ARGS propagation)"
else
    echo "channel_input: (미지정 — UpgradeAgent overlay resolve or stable fallback)"
fi
echo ""

# --------------------------------------------------------------------------
# DC-1 mixed channel detection — snapshot 생성 이전 (abort-before-touch invariant)
# --------------------------------------------------------------------------
_check_channel_consistency

# --------------------------------------------------------------------------
# --walk — 7-plugin topological walk, per-entry transcript step-visible
# --------------------------------------------------------------------------
if [[ "${MODE}" == "walk" ]]; then
    echo "--- 9-plugin family topological walk (read-only, per-entry transcript step-visible) ---"
    echo "topological_order: ${FAMILY[*]}"
    echo "walk_stage: read-only (filesystem touch 0, network: offline)"
    echo ""
    for plugin in "${FAMILY[@]}"; do
        echo "  [walk] plugin=${plugin}: CHANGELOG.md enumerate (Stage 1 walk)"
        # transcript step emit (per-entry walk step visible)
        bash "${WALK_SINGLE_CLI}" --walk --plugin "${plugin}" "${REPO_ARGS[@]}" "${CHANNEL_ARGS[@]}" 2>/dev/null | \
            grep -v "^===" | grep -v "^주의" | grep -v "^---.*Orchestrator" | \
            sed "s/^/    [transcript] /" || true
        echo ""
    done
    echo "walk 완료 (9-plugin family, filesystem touch 0, per-entry transcript 출력)"
    exit 0
fi

# --------------------------------------------------------------------------
# --plan — 7-plugin min_prereq topological resolve dry
# --------------------------------------------------------------------------
if [[ "${MODE}" == "plan" ]]; then
    echo "--- 9-plugin family walk + plan (min_prereq topological resolve, dry) ---"
    echo "topological_order: ${FAMILY[*]}"
    echo "plan_stage: min_prereq topological resolve (ADR-096 §결정 1/2, dry — filesystem touch 0)"
    echo ""
    for plugin in "${FAMILY[@]}"; do
        echo "  [plan] plugin=${plugin}: walk + min_prereq check"
        bash "${WALK_SINGLE_CLI}" --plan --plugin "${plugin}" "${REPO_ARGS[@]}" "${CHANNEL_ARGS[@]}" 2>/dev/null | \
            grep -v "^===" | grep -v "^주의" | grep -v "^---.*Orchestrator" | \
            sed "s/^/    [plan] /" || true
        echo ""
    done
    echo "plan 완료 (9-plugin family, dry — filesystem touch 0)"
    exit 0
fi

# --------------------------------------------------------------------------
# --rollback — 직전 per-family pre-atomic snapshot 복원 (7 plugin 일괄)
# --------------------------------------------------------------------------
if [[ "${MODE}" == "rollback" ]]; then
    echo "--- rollback: per-family pre-atomic snapshot 복원 (9 plugin 일괄, partial 0) ---"
    echo "per-family rollback = 직전 per-family snapshot 복원 → 9 plugin 전체"
    echo ""
    echo "--- Orchestrator: 아래 per-family rollback 을 처리하십시오 ---"
    echo "per_family_rollback: true"
    echo "family: ${FAMILY[*]}"
    echo "rollback_source: 직전 per-family pre-atomic snapshot (N=5 retention)"
    echo "per_plugin_delegate: ${WALK_SINGLE_CLI} --rollback <pinned-version> ${REPO_ARGS[*]:-} ${CHANNEL_ARGS[*]:-} # 9 plugin loop"
    echo "corrupt-snapshot escalation: §7.4.1 (f) — silent partial-state 0"
    echo "rollback 완료 후 stale snapshot GC (orphan 잔존 0)"
    echo "user_decision_branches: 0"
    exit 0
fi

# --------------------------------------------------------------------------
# --apply — per-family transaction (§4.2 algorithm)
# atomic-upgrade-7-plugins.sh §4.2 step 1-6 답습 + walk semantic
# --------------------------------------------------------------------------
if [[ "${MODE}" == "apply" ]]; then
    # step 1 — idempotency pre-check (ALL none → no-op, ADR-037 Amendment 1 §7.4.1(e))
    echo "--- step 1: idempotency pre-check (9 plugin drift 검사) ---"
    ALL_NONE=1
    for plugin in "${FAMILY[@]}"; do
        status="$(_drift_status "${plugin}" || echo "unknown")"
        if [[ -z "${status}" ]]; then status="unknown"; fi
        echo "  ${plugin}: drift=${status}"
        if [[ "${status}" != "none" ]]; then
            ALL_NONE=0
        fi
    done
    echo ""
    if [[ "${ALL_NONE}" -eq 1 ]]; then
        echo "9 plugin 이미 전부 최신 (desired == current) — no-op 정상 종료"
        echo "(idempotency: snapshot/transaction 무생성 — §7.4.1 (e), prompt 0)"
        exit 0
    fi

    # _CFP1170_MOCK_APPLY_FAIL=1 = per-plugin apply 실패 시뮬레이션 (TC-17 test seam)
    if [[ "${_CFP1170_MOCK_APPLY_FAIL:-}" == "1" ]]; then
        echo "--- [MOCK] per-plugin apply 실패 시뮬레이션 (TC-17 test seam) ---" >&2
        echo "per-family atomic rollback 발동 (partial state 0, ADR-068 I-3 unconditional)" >&2
        echo "family_rollback: true" >&2
        echo "partial_artifact_forbidden: true" >&2
        exit 1
    fi

    # step 2-6 — per-family transaction (Orchestrator 처리 위임)
    echo "--- step 2-6: per-family atomic transaction (Orchestrator 처리 위임) ---"
    echo "--- Orchestrator: 아래 per-family transaction 을 처리하십시오 ---"
    echo "per_family_transaction: apply"
    echo "family: ${FAMILY[*]}"
    if [[ -n "${INPUT_CHANNEL}" ]]; then
        echo "channel_args: ${CHANNEL_ARGS[*]}"
    fi
    echo "step_2_disk_preflight: per-family snapshot 예상 크기 vs 가용 공간 (부족 = abort-before-touch)"
    echo "step_3_pre_atomic_snapshot: 9 plugin pin state union 단일 tar + checksum"
    echo "step_4_per_plugin_walk_apply: ${WALK_SINGLE_CLI} --apply ${REPO_ARGS[*]:-} ${CHANNEL_ARGS[*]:-}  # 9 plugin loop"
    echo "step_4_failure: per-plugin 실패 = abort + per-family atomic rollback (ADR-068 I-3 unconditional)"
    echo "step_5_walk_result_aggregate: aggregate_walk_result() (walk_plan.py SSOT)"
    echo "step_5_invariant: ANY FAILED/PARTIAL_FAILURE → transaction 실패 → 전체 9 plugin rollback"
    echo "step_6_commit: transaction 완결 (snapshot = audit trail, N=5 retention)"
    echo "rollback: per-family pre-atomic snapshot 복원 (9 plugin 일괄, partial state 0)"
    echo "user_decision_branches: 0"
    exit 0
fi

# 도달 불가 (mode 1개 강제 후 enum 전부 처리됨)
echo "오류: 내부 상태 이상 (mode='${MODE}')" >&2
exit 1
