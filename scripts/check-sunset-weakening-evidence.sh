#!/usr/bin/env bash
# CFP-1239 / ADR-058 Amendment 1 §결정 5 — sunset-weakening-evidence mechanical lint
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_sunset_weakening_evidence.py SSOT)
# ADR-060 §결정 5 — warning-tier (exit 0 항상 for warnings, PR merge 미차단)
#
# Usage / exit code 상세: scripts/lib/check_sunset_weakening_evidence.py header 참조.
#
# Bypass channel: HOTFIX_BYPASS_SUNSET_WEAKENING_EVIDENCE=1 env
#   → 즉시 exit 0 (hotfix-bypass:sunset-weakening-evidence label 부착 시 workflow 에서 주입)
#
# 검증 대상 파일 수집 (check-amendment-number-stale.sh collect_files 패턴 답습):
#   CI: GITHUB_BASE_REF 환경변수 기반 git diff --name-only origin/${base}...HEAD
#   로컬: staged (--cached) + unstaged (HEAD) 합산 후 sort -u
#   명시 인수: 인수 목록 그대로 사용
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier)
#   1 — malformed 감지 (genuine lint error)
#   2 — setup error (git 미설치 등)
set -euo pipefail

SCRIPT_NAME="[sunset-weakening-lint]"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS="${HOTFIX_BYPASS_SUNSET_WEAKENING_EVIDENCE:-}"
if [[ "$BYPASS" == "1" ]]; then
  echo "$SCRIPT_NAME BYPASS=1 — skip" >&2
  exit 0
fi

# ── 파일 수집 ─────────────────────────────────────────────────────────────────
collect_files() {
  local raw_files=()

  if [[ $# -gt 0 ]]; then
    # 명시적 인수
    raw_files=("$@")
  else
    # git diff 기반 자동 감지 (check-amendment-number-stale.sh 패턴 답습)
    if ! command -v git &>/dev/null; then
      echo "$SCRIPT_NAME ERROR: git 미설치 (환경 오류)" >&2
      exit 2
    fi
    local base_ref="${GITHUB_BASE_REF:-}"
    local git_files
    if [[ -n "$base_ref" ]]; then
      mapfile -t git_files < <(
        git -C "$REPO_ROOT" diff --name-only "origin/${base_ref}...HEAD" 2>/dev/null \
          | grep -E '^docs/adr/ADR-[0-9].*\.md$' || true
      )
    else
      # 로컬: staged + unstaged
      mapfile -t git_files < <(
        { git -C "$REPO_ROOT" diff --name-only HEAD 2>/dev/null
          git -C "$REPO_ROOT" diff --cached --name-only 2>/dev/null; } \
          | grep -E '^docs/adr/ADR-[0-9].*\.md$' | sort -u || true
      )
    fi
    raw_files=("${git_files[@]+"${git_files[@]}"}")
  fi

  # 파일 목록 출력 (절대 경로 변환)
  local f
  for f in "${raw_files[@]+"${raw_files[@]}"}"; do
    [[ -z "$f" ]] && continue
    # 상대 경로 → 절대 경로 변환
    if [[ "$f" = /* ]]; then
      echo "$f"
    else
      echo "${REPO_ROOT}/${f}"
    fi
  done
}

# ── 메인: 파일 수집 후 Python SSOT 호출 ──────────────────────────────────────
main() {
  local files=()
  mapfile -t files < <(collect_files "$@")

  if [[ "${#files[@]}" -eq 0 ]]; then
    echo "$SCRIPT_NAME INFO: 검증 대상 ADR 파일 없음 (변경 없음 또는 ADR 외 파일만 변경)" >&2
    exit 0
  fi

  # base_ref 결정 (CI: GITHUB_BASE_REF, 로컬: 미지정 → Python 이 HEAD~1 fallback 사용)
  local base_args=()
  local base_ref="${GITHUB_BASE_REF:-}"
  if [[ -n "$base_ref" ]]; then
    base_args=("--base" "origin/${base_ref}")
  fi

  # Python SSOT 위임 (exit-code passthrough)
  exec python3 "${SCRIPT_DIR}/lib/check_sunset_weakening_evidence.py" \
    --repo "$REPO_ROOT" \
    "${base_args[@]+"${base_args[@]}"}" \
    "${files[@]}"
}

main "$@"
