#!/usr/bin/env bash
# CFP-1489 / Wave 2-A of CFP-1389 (Sub-CFP A CFP-1437 mechanical wire)
# ADR-073 Amendment 11 §결정 1-A + ADR-082 Amendment 15 §결정 1 layer 1 sub-scope (1-E)
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_spawn_prompt_head_pin.py SSOT)
# ADR-060 §결정 5 — warning-tier (exit 0 항상 for warnings, PR merge 미차단)
#
# Pre-spawn HEAD-pin protocol mechanical lint.
# Detection scope:
#   - 변경된 파일 중 spawn-prompt candidate file 안에서
#     `[PRE-SPAWN-ORIGIN-MAIN-SHA: <40-char-hex>]` block presence + format 검증.
#
# Bypass channel: HOTFIX_BYPASS_SPAWN_PROMPT_HEAD_PIN=1 env
#   → 즉시 exit 0 (hotfix-bypass:spawn-prompt-head-pin label 부착 시 workflow 에서 주입)
#
# 검증 대상 file 수집 (check-amendment-number-stale.sh collect_files 패턴 답습):
#   CI: GITHUB_BASE_REF 환경변수 기반 git diff --name-only origin/${base}...HEAD
#   로컬: staged (--cached) + unstaged (HEAD) 합산 후 sort -u
#   명시 인수: 인수 목록 그대로 사용
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier)
#   1 — malformed 감지 (genuine lint error)
#   2 — setup error (git 미설치 등)
set -euo pipefail

SCRIPT_NAME="[spawn-prompt-head-pin-lint]"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS="${HOTFIX_BYPASS_SPAWN_PROMPT_HEAD_PIN:-}"
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
        git diff --name-only "origin/${base_ref}...HEAD" 2>/dev/null \
          | grep -E '\.(md|yaml|yml|txt|log)$' || true
      )
    else
      # 로컬: staged + unstaged
      mapfile -t git_files < <(
        { git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; } \
          | grep -E '\.(md|yaml|yml|txt|log)$' | sort -u || true
      )
    fi
    raw_files=("${git_files[@]+"${git_files[@]}"}")
  fi

  # 파일 목록 출력
  local f
  for f in "${raw_files[@]+"${raw_files[@]}"}"; do
    [[ -z "$f" ]] && continue
    echo "$f"
  done
}

# ── 메인: 파일 수집 후 Python SSOT 호출 ──────────────────────────────────────
main() {
  local files=()
  mapfile -t files < <(collect_files "$@")

  if [[ "${#files[@]}" -eq 0 ]]; then
    echo "$SCRIPT_NAME INFO: 검증 대상 파일 없음 (변경 없음 또는 해당 확장자 미포함)" >&2
    exit 0
  fi

  # Python SSOT 위임 (exit-code passthrough)
  exec python3 "$SCRIPT_DIR/lib/check_spawn_prompt_head_pin.py" "${files[@]}"
}

main "$@"
