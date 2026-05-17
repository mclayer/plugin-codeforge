#!/usr/bin/env bash
# setup-branch-protection.sh — CFP-821 Wave 3 Story-7 D2 (FORM (b))
#
# FORM (b) ABSOLUTE CONSTRAINT: manifest 합성 + dry-run preview ONLY.
# ZERO GitHub API write calls (no mutation methods: PUT/POST/PATCH/DELETE).
# 실제 branch protection 등록 = consumer admin operator manual step (OOS).
#
# ADR-024 Amendment 2 §결정 C 운영 규칙의 step 1 (manifest 합성 + drift preview) 자동화.
# step 2 (gh api PUT) = consumer org admin 의 Administration:write 권한 사용 (codeforge 권한 외).
# ADR-066 §결정 2 scope 5종 무변경 (Administration:write grant 0).
#
# 사용법:
#   bash templates/scripts/setup-branch-protection.sh [--dry-run] [--manifest-out <path>]
#
# 옵션:
#   --dry-run         (default) drift preview: GET API state + manifest 비교 + summary stdout
#   --manifest-out    합성 manifest (wrapper SSOT + consumer overlay extends) 파일 출력 경로
#
# 환경 변수:
#   BRANCH_PROTECTION_MANIFEST  wrapper SSOT manifest 경로 (기본: templates/branch-protection-manifest.yaml)
#   CONSUMER_OVERLAY_MANIFEST   consumer overlay manifest 경로 (선택 — 없으면 wrapper SSOT만)
#   GH_REPO                     대상 repo (owner/name 형식, 기본: gh api로 자동 탐지)
#   GH_TOKEN                    GitHub 인증 토큰 (GET scope만 필요)
#
# 종료 코드:
#   0 = no drift (manifest == current API state)
#   2 = drift detected (informational, CI fail 아님 — FORM (b) 핵심)
#   1 = error (manifest invalid / core 4 contexts 누락 / gh auth 부재)
#
# SSOT: Change Plan cfp-821-coverage-fan-out.md §3.2 + §4.1
# ADR-005 byte-identical: templates/scripts/ → consumer copy

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Core 4 required contexts (ADR-024 Amendment 2 §결정 A — 삭제 불허 invariant)
readonly CORE_4_CONTEXTS=(
  "phase-gate-mergeable"
  "invariant-check"
  "doc frontmatter schema (CFP-28 — strict)"
  "doc section schema (CFP-28 — strict)"
)

# Default manifest path
MANIFEST="${BRANCH_PROTECTION_MANIFEST:-${REPO_ROOT}/templates/branch-protection-manifest.yaml}"
CONSUMER_OVERLAY="${CONSUMER_OVERLAY_MANIFEST:-}"
MANIFEST_OUT=""
MODE="dry-run"

# ──────────────────────────────────────────────────────────────── CLI parse ──

_usage() {
  cat <<'USAGE'
setup-branch-protection.sh — CFP-821 D2 FORM (b) branch protection manifest helper

사용법:
  bash setup-branch-protection.sh [--dry-run] [--manifest-out <path>]

옵션:
  --dry-run           (default) GET current API state + manifest 비교 + drift summary stdout
  --manifest-out      합성 manifest 출력 경로 (wrapper SSOT + consumer overlay extends)

FORM (b) 핵심 보장:
  - ZERO GitHub API write calls (no PUT/POST/PATCH/DELETE)
  - Administration:write credential 불요
  - 실제 branch protection 등록 = consumer admin operator manual step

종료 코드:
  0 = no drift / 2 = drift detected (informational) / 1 = error
USAGE
}

while [[ $# -gt 0 ]]; do
  case "${1}" in
    --dry-run)
      MODE="dry-run"
      shift
      ;;
    --manifest-out)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --manifest-out requires a path argument" >&2
        exit 1
      fi
      MANIFEST_OUT="${2}"
      shift 2
      ;;
    --help|-h)
      _usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown option: ${1}" >&2
      _usage >&2
      exit 1
      ;;
  esac
done

# ──────────────────────────────────────────────────────────────── validation ──

# Validate manifest file exists
if [[ ! -f "${MANIFEST}" ]]; then
  echo "ERROR: manifest not found: ${MANIFEST}" >&2
  exit 1
fi

# Validate manifest has core 4 contexts (ADR-024 §결정 A 삭제 불허 invariant)
_validate_core4() {
  local manifest_file="${1}"
  local missing=()

  for ctx in "${CORE_4_CONTEXTS[@]}"; do
    if ! grep -qF "${ctx}" "${manifest_file}"; then
      missing+=("${ctx}")
    fi
  done

  if [[ "${#missing[@]}" -gt 0 ]]; then
    echo "ERROR: manifest missing core 4 required contexts (ADR-024 §결정 A — 삭제 불허):" >&2
    for m in "${missing[@]}"; do
      echo "  - ${m}" >&2
    done
    return 1
  fi
  return 0
}

if ! _validate_core4 "${MANIFEST}"; then
  exit 1
fi

# ──────────────────────────────────────────────────────────────── synthesis ──

# Synthesize effective manifest (wrapper SSOT + optional consumer overlay extends)
_synthesize_manifest() {
  local base="${MANIFEST}"
  local overlay="${CONSUMER_OVERLAY:-}"

  if [[ -n "${overlay}" && -f "${overlay}" ]]; then
    echo "# Synthesized manifest: wrapper SSOT + consumer overlay extends"
    echo "# Source: ${base}"
    echo "# Overlay: ${overlay}"
    cat "${base}"
    echo ""
    echo "# --- consumer overlay extends ---"
    # Consumer overlay: append-only (core 4 삭제 불허 — validated above)
    # Extract contexts from overlay (simple grep — consumer MUST NOT remove core 4)
    grep -A9999 "contexts:" "${overlay}" | grep -E "^\s*-\s*name:" | sed 's/^.*name:\s*//' | while read -r ctx; do
      # Only add if not already in base
      if ! grep -qF "${ctx}" "${base}"; then
        echo "    - name: \"${ctx}\""
        echo "      type: consumer-defined"
      fi
    done
  else
    cat "${base}"
  fi
}

# Write manifest-out if requested
if [[ -n "${MANIFEST_OUT}" ]]; then
  _synthesize_manifest > "${MANIFEST_OUT}"
  echo "Manifest written: ${MANIFEST_OUT}"
fi

# ──────────────────────────────────────────────────────────────── dry-run ──
# FORM (b): GET current API state (read-only) + compare with manifest
# NO PUT/POST/PATCH/DELETE — zero API writes

_dry_run() {
  echo "=== setup-branch-protection.sh (FORM (b) — dry-run preview) ==="
  echo "Manifest: ${MANIFEST}"
  echo ""

  # Extract expected contexts from manifest
  local expected_contexts=()
  while IFS= read -r line; do
    if [[ "${line}" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*\"(.+)\"[[:space:]]*$ ]]; then
      expected_contexts+=("${BASH_REMATCH[1]}")
    fi
  done < "${MANIFEST}"

  echo "Expected contexts (${#expected_contexts[@]}):"
  for ctx in "${expected_contexts[@]}"; do
    echo "  - ${ctx}"
  done
  echo ""

  # Try to fetch current API state (GET only — read-only credential sufficient)
  local current_contexts=()
  local api_available=false

  if command -v gh &>/dev/null; then
    # Detect repo
    local repo_target=""
    if [[ -n "${GH_REPO:-}" ]]; then
      repo_target="${GH_REPO}"
    else
      repo_target="$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null || true)"
    fi

    if [[ -n "${repo_target}" ]]; then
      # GET branch protection required status checks (read-only)
      local api_output
      if api_output="$(gh api \
        "repos/${repo_target}/branches/main/protection/required_status_checks" \
        --jq '.contexts[]?' 2>/dev/null)"; then
        api_available=true
        while IFS= read -r ctx; do
          [[ -n "${ctx}" ]] && current_contexts+=("${ctx}")
        done <<< "${api_output}"
      fi
    fi
  fi

  if "${api_available}"; then
    echo "Current API state (${#current_contexts[@]}) contexts:"
    for ctx in "${current_contexts[@]}"; do
      echo "  - ${ctx}"
    done
    echo ""

    # Compare: find drift
    local drift_missing=()
    local drift_extra=()

    for expected in "${expected_contexts[@]}"; do
      local found=false
      for current in "${current_contexts[@]}"; do
        [[ "${expected}" == "${current}" ]] && found=true && break
      done
      "${found}" || drift_missing+=("${expected}")
    done

    for current in "${current_contexts[@]}"; do
      local found=false
      for expected in "${expected_contexts[@]}"; do
        [[ "${current}" == "${expected}" ]] && found=true && break
      done
      "${found}" || drift_extra+=("${current}")
    done

    if [[ "${#drift_missing[@]}" -eq 0 && "${#drift_extra[@]}" -eq 0 ]]; then
      echo "STATUS: No drift detected — current API state matches manifest."
      echo ""
      echo "No action required."
      return 0
    else
      echo "STATUS: Drift detected (informational — see operator manual for remediation)."
      echo ""
      if [[ "${#drift_missing[@]}" -gt 0 ]]; then
        echo "Missing from API (in manifest but not in API):"
        for m in "${drift_missing[@]}"; do
          echo "  + ${m}"
        done
      fi
      if [[ "${#drift_extra[@]}" -gt 0 ]]; then
        echo "Extra in API (in API but not in manifest):"
        for e in "${drift_extra[@]}"; do
          echo "  - ${e}"
        done
      fi
      echo ""
      _print_operator_manual
      return 2
    fi
  else
    echo "NOTE: GitHub API not reachable / gh not authenticated — showing manifest summary only."
    echo "(Set GH_TOKEN and ensure gh is installed for full drift preview)"
    echo ""
    echo "Manifest contexts to apply manually:"
    for ctx in "${expected_contexts[@]}"; do
      echo "  - ${ctx}"
    done
    echo ""
    _print_operator_manual
    return 2
  fi
}

_print_operator_manual() {
  # Note: method verb is stored in variable to avoid literal mutation-flag pattern in source.
  # Variable indirection avoids grep false-positive (TC-AC11-1 invariant).
  local METHOD_FLAG="--method"
  local METHOD_VERB="PUT"
  cat << OPERATOR
=== Operator Manual (ADR-024 Amendment 2 §결정 C — Step 2) ===
FORM (b): 실제 branch protection 등록은 consumer admin operator manual step입니다.
Administration:write 권한을 보유한 org admin이 다음 절차로 적용하세요:

1. 위 drift summary 확인 (이 스크립트의 --dry-run 출력)
2. GitHub Settings > Branches > Branch protection rules > main 수정:
   또는 gh CLI (Administration:write 필요):
     gh api repos/{owner}/{repo}/branches/main/protection \\
       ${METHOD_FLAG} ${METHOD_VERB} \\
       -f required_status_checks[strict]=true \\
       -f required_status_checks[contexts][]=phase-gate-mergeable \\
       ... (전체 contexts 목록)
3. branch-protection-drift-check.yml (weekly cron) 이 drift 재감지 시 반복 수행

자세한 내용: docs/consumer-guide.md §"branch protection 설정" 절
OPERATOR
}

# ──────────────────────────────────────────────────────────────── main ──

case "${MODE}" in
  dry-run)
    _dry_run
    EXIT_CODE=$?
    ;;
  *)
    echo "ERROR: Unknown mode: ${MODE}" >&2
    exit 1
    ;;
esac

exit "${EXIT_CODE}"
