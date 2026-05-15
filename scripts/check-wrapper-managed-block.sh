#!/usr/bin/env bash
# CFP-702 / ADR-027 Amendment 3 §결정 7.D — wrapper-managed marker block lint
# Tier: blocking-on-pr (ADR-060 §결정 5 — D4 marker 위반 = customization wholesale loss 직결)
# Bypass channel: hotfix-bypass:wrapper-managed-block label (ADR-024 §결정 6.A per-entry namespace)
#
# 검증 대상:
#   1. BEGIN/END pairing: 모든 BEGIN 은 대응 END 보유 (orphan BEGIN / orphan END = malformed)
#   2. 순서 invariant: BEGIN 이 END 보다 앞 (역전 = malformed)
#   3. flat-only nesting 금지: nested BEGIN ... BEGIN ... END ... END = reject (§결정 7.D.1 Axis 2)
#
# File type별 marker syntax (§결정 7.A.1 Axis 1):
#   .yml/.yaml/.sh:  # BEGIN wrapper-managed  /  # END wrapper-managed
#   .md:             <!-- BEGIN wrapper-managed -->  /  <!-- END wrapper-managed -->
#   .json:           sidecar manifest only (marker-incapable — Wave 2 Story-5 carrier)
#
# Usage:
#   bash check-wrapper-managed-block.sh [file...]
#   bash check-wrapper-managed-block.sh  # 인수 없으면 변경된 파일 자동 감지 (git diff)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS (모든 검증 통과)
#   1 — malformed marker 감지 (orphan / 역전 / nested)
#   2 — setup error (git 미설치 등 환경 오류)
set -euo pipefail

SCRIPT_NAME="[wrapper-managed-block-lint]"

# ── 환경 변수 ────────────────────────────────────────────────────────────────
BYPASS_LABEL="${HOTFIX_BYPASS_WRAPPER_MANAGED_BLOCK:-}"
if [[ "$BYPASS_LABEL" == "1" ]]; then
  echo "$SCRIPT_NAME BYPASS=1 — skip" >&2
  exit 0
fi

# ── marker 정의 ───────────────────────────────────────────────────────────────
readonly MARKER_BEGIN_HASH="# BEGIN wrapper-managed"
readonly MARKER_END_HASH="# END wrapper-managed"
readonly MARKER_BEGIN_HTML="<!-- BEGIN wrapper-managed -->"
readonly MARKER_END_HTML="<!-- END wrapper-managed -->"

# ── 파일 타입별 marker 판별 ───────────────────────────────────────────────────
get_markers() {
  local file="$1"
  case "${file##*.}" in
    yml|yaml|sh)
      echo "$MARKER_BEGIN_HASH"
      echo "$MARKER_END_HASH"
      ;;
    md)
      echo "$MARKER_BEGIN_HTML"
      echo "$MARKER_END_HTML"
      ;;
    json)
      # JSON = marker-incapable (Wave 2 Story-5 sidecar manifest 영역)
      echo ""
      echo ""
      ;;
    *)
      # 미지원 확장자 = hash prefix marker 로 fallback (보수적)
      echo "$MARKER_BEGIN_HASH"
      echo "$MARKER_END_HASH"
      ;;
  esac
}

# ── 단일 파일 검증 ────────────────────────────────────────────────────────────
check_file() {
  local file="$1"
  local errors=0

  # .json = sidecar manifest only (본 script 검증 범위 외)
  if [[ "${file##*.}" == "json" ]]; then
    return 0
  fi

  # file 존재 확인
  if [[ ! -f "$file" ]]; then
    echo "$SCRIPT_NAME SKIP: $file (파일 없음)" >&2
    return 0
  fi

  # marker 읽기
  local markers
  mapfile -t markers < <(get_markers "$file")
  local begin_marker="${markers[0]}"
  local end_marker="${markers[1]}"

  # marker 없는 파일 타입 = skip
  if [[ -z "$begin_marker" ]]; then
    return 0
  fi

  # ── 검증 1: BEGIN / END count ──────────────────────────────────────────────
  local begin_count end_count
  # grep -c 는 no-match 시 exit 1 + "0" 출력 (BSD/GNU 모두). || true 로 exit code 무시
  begin_count=$(grep -cF "$begin_marker" "$file" 2>/dev/null) || begin_count=0
  end_count=$(grep -cF "$end_marker" "$file" 2>/dev/null) || end_count=0
  # 빈 값 fallback
  begin_count="${begin_count:-0}"
  end_count="${end_count:-0}"

  if [[ "$begin_count" -ne "$end_count" ]]; then
    echo "$SCRIPT_NAME ERROR: $file — orphan marker (BEGIN=$begin_count, END=$end_count)" >&2
    ((errors++)) || true
  fi

  # ── 검증 2: flat-only nesting 금지 ────────────────────────────────────────
  if [[ "$begin_count" -gt 1 ]]; then
    # nested = BEGIN 2+ (flat only = max 1 pair per file)
    echo "$SCRIPT_NAME ERROR: $file — nested marker block 감지 (BEGIN count=$begin_count). ADR-027 §결정 7.D.1: flat-only — nesting 금지." >&2
    ((errors++)) || true
  fi

  # ── 검증 3: 순서 invariant (BEGIN 이 END 보다 앞) ─────────────────────────
  if [[ "$begin_count" -eq 1 ]] && [[ "$end_count" -eq 1 ]]; then
    local begin_line end_line
    begin_line=$(grep -nF "$begin_marker" "$file" | head -1 | cut -d: -f1)
    end_line=$(grep -nF "$end_marker" "$file" | head -1 | cut -d: -f1)

    if [[ -n "$begin_line" ]] && [[ -n "$end_line" ]]; then
      if [[ "$end_line" -le "$begin_line" ]]; then
        echo "$SCRIPT_NAME ERROR: $file — marker 역전 감지 (BEGIN line $begin_line, END line $end_line). END 가 BEGIN 보다 앞에 있습니다." >&2
        ((errors++)) || true
      fi
    fi
  fi

  if [[ "$errors" -eq 0 ]] && [[ "$begin_count" -gt 0 ]]; then
    echo "$SCRIPT_NAME OK: $file (BEGIN=$begin_count, END=$end_count pair 정상)" >&2
  elif [[ "$begin_count" -eq 0 ]]; then
    # marker 없는 파일 = wrapper-managed block 미사용 (합법, 에러 아님)
    : # no-op
  fi

  return $errors
}

# ── 검증 대상 파일 수집 ───────────────────────────────────────────────────────
collect_files() {
  if [[ $# -gt 0 ]]; then
    # 명시적 인수
    printf '%s\n' "$@"
  else
    # git diff 기반 자동 감지
    if ! command -v git &>/dev/null; then
      echo "$SCRIPT_NAME ERROR: git 미설치 (환경 오류)" >&2
      exit 2
    fi
    # PR 컨텍스트 (CI) vs 로컬 실행 분기
    local base_ref="${GITHUB_BASE_REF:-}"
    if [[ -n "$base_ref" ]]; then
      git diff --name-only "origin/${base_ref}...HEAD" 2>/dev/null \
        | grep -E '\.(yml|yaml|sh|md)$' || true
    else
      # 로컬: staged + unstaged
      { git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; } \
        | grep -E '\.(yml|yaml|sh|md)$' | sort -u || true
    fi
  fi
}

# ── 메인 ─────────────────────────────────────────────────────────────────────
main() {
  local total_errors=0
  local checked=0

  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    if check_file "$file"; then
      : # PASS
    else
      ((total_errors++)) || true
    fi
    ((checked++)) || true
  done < <(collect_files "$@")

  if [[ "$checked" -eq 0 ]]; then
    echo "$SCRIPT_NAME INFO: 검증 대상 파일 없음 (marker block 미사용 또는 변경 없음)" >&2
    exit 0
  fi

  if [[ "$total_errors" -gt 0 ]]; then
    echo "$SCRIPT_NAME FAIL: $total_errors 개 파일에서 malformed marker 감지" >&2
    exit 1
  fi

  echo "$SCRIPT_NAME PASS: $checked 개 파일 검증 완료"
  exit 0
}

main "$@"
