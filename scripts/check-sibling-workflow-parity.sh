#!/usr/bin/env bash
# CFP-685 / ADR-065 §결정 1 row 3 — sibling workflow parity check
# wrapper templates/github-workflows/*.yml ↔ .github/workflows/ self-app byte-identical 검증
#
# 6 sibling plugin repo (.github/workflows/ 안 auto-phase-label.yml 기준) 는 GitHub API 를 통해
# 검증하는 Phase 2 scope (PAT scope CODEFORGE_CROSS_REPO_PAT 필요). 본 Phase 1 script 는
# wrapper repo 의 templates ↔ self-app byte-identical parity 검증 (Phase 2 precursor).
#
# Usage:
#   bash scripts/check-sibling-workflow-parity.sh
#
# Environment overrides (테스트 모드):
#   CFP685_TEMPLATES_DIR=<path>    (default: templates/github-workflows)
#   CFP685_GH_WORKFLOWS_DIR=<path> (default: .github/workflows)
#
# Exit codes (ADR-060 Amendment 2 §결정 15 3-tier):
#   0 = PASS (byte-identical or no target files)
#   1 = drift detected (SHA-256 mismatch between templates and self-app)
#   2 = SETUP error (missing directory / sha256sum+shasum both unavailable)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

TEMPLATES_DIR="${CFP685_TEMPLATES_DIR:-$REPO_ROOT/templates/github-workflows}"
GH_WORKFLOWS_DIR="${CFP685_GH_WORKFLOWS_DIR:-$REPO_ROOT/.github/workflows}"

# --- sha256sum helper (sha256sum 또는 shasum -a 256 fallback) ---
_sha256() {
  local file="$1"
  if command -v sha256sum &>/dev/null; then
    sha256sum "$file" | awk '{print $1}'
  elif command -v shasum &>/dev/null; then
    shasum -a 256 "$file" | awk '{print $1}'
  else
    echo "[check-sibling-workflow-parity] SETUP error: sha256sum / shasum 모두 미설치" >&2
    exit 2
  fi
}

# --- SETUP: templates 디렉토리 존재 확인 ---
if [[ ! -d "$TEMPLATES_DIR" ]]; then
  echo "[check-sibling-workflow-parity] SETUP error: templates directory not found: $TEMPLATES_DIR" >&2
  exit 2
fi

# --- sha256sum / shasum 가용성 사전 확인 ---
_sha256_cmd=""
if command -v sha256sum &>/dev/null; then
  # 실제 동작 확인 (stub 이 exit 127 반환하는 경우 체크)
  if echo "test" | sha256sum &>/dev/null; then
    _sha256_cmd="sha256sum"
  fi
fi
if [[ -z "$_sha256_cmd" ]] && command -v shasum &>/dev/null; then
  if echo "test" | shasum -a 256 &>/dev/null; then
    _sha256_cmd="shasum"
  fi
fi
if [[ -z "$_sha256_cmd" ]]; then
  echo "[check-sibling-workflow-parity] SETUP error: sha256sum / shasum 모두 미설치 또는 실행 불가" >&2
  exit 2
fi

# --- 대상 파일 수집 ---
TMPL_FILES=()
while IFS= read -r -d '' f; do
  TMPL_FILES+=("$(basename "$f")")
done < <(find "$TEMPLATES_DIR" -maxdepth 1 -name "*.yml" -print0 2>/dev/null | sort -z)

if [[ ${#TMPL_FILES[@]} -eq 0 ]]; then
  echo "[check-sibling-workflow-parity] PASS — templates/github-workflows: 0 files (nothing to check)"
  exit 0
fi

# --- SHA-256 비교 ---
DRIFT_COUNT=0
PASS_COUNT=0
MISSING_COUNT=0

for fname in "${TMPL_FILES[@]}"; do
  tmpl_file="$TEMPLATES_DIR/$fname"
  gh_file="$GH_WORKFLOWS_DIR/$fname"

  if [[ ! -f "$gh_file" ]]; then
    # self-app 파일 부재 = drift (template 이 배포되지 않음)
    echo "[check-sibling-workflow-parity] DRIFT (missing) — $fname: .github/workflows/$fname 부재"
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
    MISSING_COUNT=$((MISSING_COUNT + 1))
    continue
  fi

  tmpl_sha=$(_sha256 "$tmpl_file")
  gh_sha=$(_sha256 "$gh_file")

  if [[ "$tmpl_sha" == "$gh_sha" ]]; then
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "[check-sibling-workflow-parity] DRIFT — $fname: templates SHA=$tmpl_sha vs .github SHA=$gh_sha"
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
  fi
done

TOTAL=${#TMPL_FILES[@]}

if [[ "$DRIFT_COUNT" -eq 0 ]]; then
  echo "[check-sibling-workflow-parity] PASS — $TOTAL file(s) byte-identical (templates ↔ .github/workflows)"
  exit 0
else
  echo "[check-sibling-workflow-parity] drift detected: $DRIFT_COUNT drift(s), $PASS_COUNT PASS, $MISSING_COUNT missing (total $TOTAL files)"
  echo "[check-sibling-workflow-parity] Resolution: cp templates/github-workflows/<name>.yml .github/workflows/<name>.yml (ADR-065 §결정 1 row 3)"
  exit 1
fi
