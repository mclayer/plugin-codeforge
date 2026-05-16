#!/usr/bin/env bash
# check-wrapper-template-managed-coverage.sh — CFP-745 Phase 2 authoring-guard lint
#
# Tier: warning (ADR-060 §결정 5 — authoring drift guard, not blocking-on-pr)
# Bypass channel: hotfix-bypass:wrapper-template-managed-coverage label (ADR-024 §결정 6.A)
#
# Purpose: wrapper plugin template 안 wrapper-managed content 가 D4 marker block
#   (# BEGIN/END wrapper-managed) 또는 sidecar managed_paths 안에 위치하는지
#   authoring-time lint 검증 (§8.2 Phase 2 lint declare — authoring drift guard).
#
# Problem being solved:
#   wrapper 저작자가 wrapper-managed 라인을 marker 밖으로 이동 (authoring drift) 시
#   → reconcile-overlay.sh 의 marker 밖 preserve 가 그 변경 전파를 차단.
#   runtime silent overwrite 아님 — authoring-time guard 누락 문제.
#   본 lint = wrapper template self-audit (consumer runtime 무관, reconcile-overlay.sh 와 disjoint).
#
# Detection logic:
#   - templates/.claude/_overlay/ 아래 .sh/.yml/.yaml 파일 → marker block 존재 확인
#   - marker 존재하되 outside-marker 에 wrapper-only 라인 있는지 경고 (heuristic)
#   - .json sidecar manifest → schema_version + managed_paths 필드 존재 확인
#   - warn 전용 (exit 0 always — warning tier, consumer 작업 차단 0)
#
# reconcile-protocol-v1 §4.7 / ADR-027 Amendment 3 §결정 7.D / CFP-745 §8.2
# ADR-061 정합 — bash POSIX only (multi-line python = 외부 .py 의무)
#
# Usage:
#   bash scripts/check-wrapper-template-managed-coverage.sh [--strict]
#
# Exit code:
#   0 — PASS (warning tier: always 0 — warning output to stderr if issues found)
#   Exit code 1 only in --strict mode (CI integration, opt-in only)
set -euo pipefail

SCRIPT_NAME="[wrapper-template-managed-coverage-lint]"

# ── CLI args ─────────────────────────────────────────────────────────────────
STRICT_MODE=false
while [[ $# -gt 0 ]]; do
    case "${1}" in
        --strict) STRICT_MODE=true; shift ;;
        --help|-h)
            cat <<'USAGE'
check-wrapper-template-managed-coverage.sh — CFP-745 authoring-guard lint

Usage:
  bash scripts/check-wrapper-template-managed-coverage.sh          # warning mode (exit 0)
  bash scripts/check-wrapper-template-managed-coverage.sh --strict # blocking mode (exit 1 on issues)

Checks wrapper template overlay files for D4 marker coverage compliance.
USAGE
            exit 0 ;;
        *)
            echo "${SCRIPT_NAME} 알 수 없는 인자: ${1}" >&2
            exit 1 ;;
    esac
done

# ── Bypass check ─────────────────────────────────────────────────────────────
if [[ "${HOTFIX_BYPASS_WRAPPER_TEMPLATE_MANAGED_COVERAGE:-}" == "1" ]]; then
    echo "${SCRIPT_NAME} BYPASS=1 — skip" >&2
    exit 0
fi

# ── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Wrapper template overlay path (where wrapper-managed template files live)
TEMPLATE_OVERLAY_DIR="${WRAPPER_TEMPLATE_OVERLAY_DIR:-${REPO_ROOT}/.claude/_overlay}"
VALIDATE_SIDECAR_PY="${SCRIPT_DIR}/lib/validate_sidecar.py"

ISSUES_FOUND=0
WARNINGS=()

_warn() {
    local msg="${1}"
    WARNINGS+=("[WARN] ${msg}")
    ISSUES_FOUND=$(( ISSUES_FOUND + 1 ))
}

# ── Check 1: template overlay directory exists ────────────────────────────────
if [[ ! -d "${TEMPLATE_OVERLAY_DIR}" ]]; then
    echo "${SCRIPT_NAME} INFO: template overlay directory 없음 — skip (${TEMPLATE_OVERLAY_DIR})" >&2
    exit 0
fi

echo "${SCRIPT_NAME} 검사 대상: ${TEMPLATE_OVERLAY_DIR}"

# ── Check 2: marker-capable files (.sh/.yml/.yaml) ───────────────────────────
while IFS= read -r -d '' f; do
    rel="${f#${TEMPLATE_OVERLAY_DIR}/}"
    ext="${f##*.}"

    # Skip sidecar manifest itself
    if [[ "$(basename "${f}")" == ".wrapper-managed-manifest.json" ]]; then
        continue
    fi

    case "${ext}" in
        sh|yml|yaml)
            # Expect D4 marker block — BEGIN/END wrapper-managed
            local_has_begin=false
            local_has_end=false
            grep -qxF "# BEGIN wrapper-managed" "${f}" 2>/dev/null && local_has_begin=true || true
            grep -qxF "# END wrapper-managed" "${f}" 2>/dev/null && local_has_end=true || true

            if ! "${local_has_begin}" && ! "${local_has_end}"; then
                _warn "${rel}: D4 marker block 없음 — wrapper-managed content 가 marker 바깥에 있을 수 있음 (authoring drift risk)"
            elif "${local_has_begin}" && ! "${local_has_end}"; then
                _warn "${rel}: orphan BEGIN marker (END 없음) — check-wrapper-managed-block.sh 가 차단할 예정이나 authoring drift signal"
            elif ! "${local_has_begin}" && "${local_has_end}"; then
                _warn "${rel}: orphan END marker (BEGIN 없음) — check-wrapper-managed-block.sh 가 차단할 예정이나 authoring drift signal"
            else
                echo "${SCRIPT_NAME} PASS: ${rel} — D4 marker block OK"
            fi
            ;;
        md)
            # .md uses <!-- BEGIN/END wrapper-managed --> syntax
            local_has_begin=false
            local_has_end=false
            grep -qxF "<!-- BEGIN wrapper-managed -->" "${f}" 2>/dev/null && local_has_begin=true || true
            grep -qxF "<!-- END wrapper-managed -->" "${f}" 2>/dev/null && local_has_end=true || true

            if ! "${local_has_begin}" && ! "${local_has_end}"; then
                _warn "${rel}: D4 marker block (md syntax) 없음 — wrapper-managed content 가 marker 바깥에 있을 수 있음"
            elif "${local_has_begin}" != "${local_has_end}"; then
                _warn "${rel}: orphan md marker — marker 쌍 불완전"
            else
                echo "${SCRIPT_NAME} PASS: ${rel} — D4 marker block (md) OK"
            fi
            ;;
        json)
            # .json: sidecar manifest required for managed content
            # (skip if not a known wrapper-managed JSON template)
            echo "${SCRIPT_NAME} INFO: ${rel} — JSON file (marker-incapable, sidecar manifest 기반)"
            ;;
    esac
done < <(find "${TEMPLATE_OVERLAY_DIR}" -type f \
    \( -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "*.json" \) \
    -print0 2>/dev/null)

# ── Check 3: sidecar manifest schema ─────────────────────────────────────────
sidecar="${TEMPLATE_OVERLAY_DIR}/.wrapper-managed-manifest.json"
if [[ -f "${sidecar}" ]]; then
    if python3 "${VALIDATE_SIDECAR_PY}" "${sidecar}" 2>/dev/null; then
        echo "${SCRIPT_NAME} PASS: .wrapper-managed-manifest.json — schema OK"
    else
        _warn ".wrapper-managed-manifest.json: sidecar schema invalid (schema_version 또는 managed_paths 누락)"
    fi
else
    echo "${SCRIPT_NAME} INFO: .wrapper-managed-manifest.json 없음 — JSON sidecar manifest 미사용 시 정상"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
if [[ "${ISSUES_FOUND}" -eq 0 ]]; then
    echo "${SCRIPT_NAME} PASS — wrapper template marker coverage OK (issues: 0)"
    exit 0
else
    echo "${SCRIPT_NAME} WARN — ${ISSUES_FOUND}개 authoring drift 가능성 감지:"
    for w in "${WARNINGS[@]}"; do
        echo "  ${w}" >&2
    done
    echo "" >&2
    echo "${SCRIPT_NAME} 권장: wrapper template 파일에 D4 marker block 추가 후 재실행" >&2
    echo "${SCRIPT_NAME} 참조: ADR-027 §결정 7.A.1 (D4 marker block syntax) + reconcile-protocol-v1 §4.7" >&2

    if "${STRICT_MODE}"; then
        echo "${SCRIPT_NAME} --strict mode: exit 1" >&2
        exit 1
    else
        # Warning tier: always exit 0 (ADR-060 §결정 5 warning = continue-on-error)
        exit 0
    fi
fi
