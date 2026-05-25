#!/usr/bin/env bash
# CFP-1539 / CFP-FU-A Wave 2 mechanical wire
# ADR-082 Amendment 19 §결정 1 layer 1 sub-scope (1-I)
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_pre_spawn_prompt_finalize_verify.py SSOT)
# ADR-060 §결정 5 — warning-tier (exit 0 항상 for warnings, PR merge 미차단)
#
# Pre-spawn-prompt-finalize-verify mechanical lint.
# Detection scope:
#   - Story file (docs/stories/**/*.md) 안 [USER-UTTERANCE-VERBATIM] block 내
#     `pre_spawn_prompt_finalize_verified: <true|false>` field presence 검증.
#
# Bypass channel: HOTFIX_BYPASS_PRE_SPAWN_PROMPT_FINALIZE_VERIFY=1 env
#   → 즉시 exit 0 (hotfix-bypass:pre-spawn-prompt-finalize-verify label 부착 시 workflow 에서 주입)
#
# 검증 대상 file 수집 (check-spawn-prompt-head-pin.sh collect_files 패턴 답습):
#   CI: GITHUB_BASE_REF 환경변수 기반 git diff --name-only origin/${base}...HEAD
#   로컬: staged (--cached) + unstaged (HEAD) 합산 후 sort -u
#   명시 인수: 인수 목록 그대로 사용
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier)
#   1 — malformed 감지 (genuine lint error)
#   2 — setup error (git 미설치 등)
set -euo pipefail

SCRIPT_NAME="[pre-spawn-prompt-finalize-verify-lint]"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS="${HOTFIX_BYPASS_PRE_SPAWN_PROMPT_FINALIZE_VERIFY:-}"
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
    # git diff 기반 자동 감지 (check-spawn-prompt-head-pin.sh 패턴 답습)
    if ! command -v git &>/dev/null; then
      echo "$SCRIPT_NAME ERROR: git 미설치 (환경 오류)" >&2
      exit 2
    fi
    local base_ref="${GITHUB_BASE_REF:-}"
    local git_files
    if [[ -n "$base_ref" ]]; then
      mapfile -t git_files < <(
        git diff --name-only "origin/${base_ref}...HEAD" 2>/dev/null \
          | grep -E '\.md$' || true
      )
    else
      # 로컬: staged + unstaged
      mapfile -t git_files < <(
        { git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; } \
          | grep -E '\.md$' | sort -u || true
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
  exec python3 "$SCRIPT_DIR/lib/check_pre_spawn_prompt_finalize_verify.py" "${files[@]}"
}

main "$@"
