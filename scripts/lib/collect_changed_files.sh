#!/usr/bin/env bash
# 공유 helper — git diff 기반 변경 파일 수집 (CFP-2061-S6, 5 caller 중복 통합)
# ADR-061 thin-wrapper 패턴: caller 가 source 후 collect_changed_files 호출.
#
# 시그니처:
#   collect_changed_files <FILTER_REGEX> [explicit_files...]
#
# 환경 의존:
#   GITHUB_BASE_REF  — set 시 CI 분기(origin/<base>...HEAD), unset 시 로컬(HEAD + cached)
#   SCRIPT_NAME      — caller 가 정의(에러 메시지 prefix). 미정의 시 "collect_changed_files"
#   POST_FILTER_FN   — optional. set 시 각 파일에 대해 호출, exit 0 = skip(제외).
#                      미정의 시 no-op(전부 통과).
#
# FILTER_REGEX = grep -E 패턴 통째
#   suffix-anchored: '\.(md|yaml)$'
#   path-anchored:   '^docs/adr/ADR-[0-9].*\.md$'
#   모두 동일 파라미터로 수용.
#
# POST_FILTER 의미론:
#   caller 가 POST_FILTER_FN 으로 함수명 지정.
#   함수 exit 0 = 파일 제외(skip), exit non-0 = 통과.
#   stderr 메시지(예: "SKIP (self-referential): <file>")는 caller 함수 내부에서 출력.
#   (과추상화 회피 — ADR-027 §결정 7.D.2 skip-list 메시지는 caller-local 책임)

collect_changed_files() {
  local filter_regex="$1"; shift
  local raw_files=()

  if [[ $# -gt 0 ]]; then
    # 명시적 인수 모드
    raw_files=("$@")
  else
    # git diff 기반 자동 감지
    if ! command -v git &>/dev/null; then
      echo "${SCRIPT_NAME:-collect_changed_files} ERROR: git 미설치 (환경 오류)" >&2
      exit 2
    fi
    local base_ref="${GITHUB_BASE_REF:-}"
    local git_files
    if [[ -n "$base_ref" ]]; then
      mapfile -t git_files < <(git diff --name-only "origin/${base_ref}...HEAD" 2>/dev/null \
        | grep -E "$filter_regex" || true)
    else
      # 로컬: staged + unstaged
      mapfile -t git_files < <({ git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; } \
        | grep -E "$filter_regex" | sort -u || true)
    fi
    raw_files=("${git_files[@]+"${git_files[@]}"}")
  fi

  local file
  for file in "${raw_files[@]+"${raw_files[@]}"}"; do
    [[ -z "$file" ]] && continue
    # optional POST_FILTER hook (기본 no-op)
    if [[ -n "${POST_FILTER_FN:-}" ]] && "$POST_FILTER_FN" "$file"; then
      continue
    fi
    echo "$file"
  done
}
