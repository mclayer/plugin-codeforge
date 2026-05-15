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
# Matching policy (ADR-027 §결정 7.D.3 whole-line anchored):
#   whole-line anchored regex — leading whitespace 허용, trailing whitespace 허용.
#   substring matching 금지 (e.g. "# BEGIN wrapper-managed-evil" 는 marker 아님).
#
# Self-exclusion (ADR-027 §결정 7.D.2 self-referential skip-list):
#   SKIP_LIST 8-entry repo-relative exact path: lint 자신 + 그 lint 를 설명/테스트/구현하는
#   wrapper plugin SSOT 파일 = self-referential → skip. consumer customization 영역만 검사.
#   basename-only 매칭 금지 (consumer 동명 파일 false-skip vector 차단, SecurityArch mitigation).
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

# ── SKIP_LIST (ADR-027 §결정 7.D.2 self-referential skip-list) ────────────────
# repo-relative exact path (leading ./ normalize 후 비교)
# (1) lint 자신  (2) test fixture  (3) migration 구현 (marker 문자열 로직 보유)
# (4) lint workflow self-app  (5) lint workflow template
# (6) marker syntax 문서 SSOT  (7) marker reference  (8) ADR 자신 (marker syntax 정의)
readonly SKIP_LIST=(
  "scripts/check-wrapper-managed-block.sh"
  "scripts/test-check-wrapper-managed-block.sh"
  "scripts/migrate-existing-customization.sh"
  ".github/workflows/wrapper-managed-block.yml"
  "templates/github-workflows/wrapper-managed-block.yml"
  "docs/inter-plugin-contracts/reconcile-protocol-v1.md"
  "docs/evidence-checks-registry.yaml"
  "docs/adr/ADR-027-consumer-adoption-protocol.md"
)

# ── path canonical form 정규화 helper ────────────────────────────────────────
# 환경 간 path form 차이를 통일:
#   MSYS2/Git-Bash: /c/Users/...  → C:/Users/...
#   Windows native: C:\Users\...  → C:/Users/...
#   Unix:           /home/...     → /home/...  (변환 없음)
#   leading ./:     ./path        → path
#
# 판정 기준: /[a-zA-Z]/ 패턴 (leading slash + single letter + slash) = MSYS2 drive form
_to_canonical() {
  local p="$1"
  # backslash → forward slash (Windows native)
  p="${p//\\//}"
  # MSYS2 drive form: /c/... → C:/...
  if [[ "$p" =~ ^/([a-zA-Z])/(.*) ]]; then
    local drive="${BASH_REMATCH[1]}"
    local rest="${BASH_REMATCH[2]}"
    p="${drive^^}:/${rest}"
  fi
  echo "$p"
}

# ── repo root 해석 (absolute path → repo-relative 변환에 사용) ─────────────────
# git rev-parse 성공 시 사용, 실패 시 script 위치 기준 상위 디렉터리로 fallback
# 반환값은 항상 _to_canonical() 통과 후 저장 (C:/ form 통일)
_REPO_ROOT=""
_resolve_repo_root() {
  if [[ -n "$_REPO_ROOT" ]]; then
    return 0
  fi
  if command -v git &>/dev/null; then
    local gr
    gr="$(git rev-parse --show-toplevel 2>/dev/null)" \
      && _REPO_ROOT="$(_to_canonical "$gr")" && return 0
  fi
  # fallback: script 가 <repo>/scripts/ 에 위치 → 한 단계 위
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  _REPO_ROOT="$(_to_canonical "$(dirname "$script_dir")")"
}

# repo-relative path 정규화 (ADR-027 §결정 7.D.2)
# 처리 순서:
#   1. _to_canonical: MSYS2 /c/... → C:/... + backslash → / (양쪽 동일 canonical form)
#   2. absolute path 판정: Unix /... 또는 Windows C:/... → repo root prefix strip
#   3. leading ./ strip
# _resolve_repo_root() 도 _to_canonical() 통과값 저장 → input/root 양쪽 동일 form 비교
normalize_path() {
  local p="$1"

  # Step 1: canonical form (MSYS2 drive + backslash 정규화)
  p="$(_to_canonical "$p")"

  # Step 2: absolute path → repo-relative (Unix /... 또는 Windows C:/...)
  if [[ "$p" == /* ]] || [[ "$p" =~ ^[A-Za-z]:/ ]]; then
    _resolve_repo_root
    if [[ -n "$_REPO_ROOT" ]]; then
      # repo root (trailing slash normalize) + / suffix 로 prefix strip
      local repo_with_slash="${_REPO_ROOT%/}/"
      if [[ "$p" == "${repo_with_slash}"* ]]; then
        p="${p#"${repo_with_slash}"}"
      fi
    fi
  fi

  # Step 3: strip leading ./ if present
  p="${p#./}"
  echo "$p"
}

# SKIP_LIST 에 포함 여부 (repo-relative exact path 매칭 — basename-only 금지)
is_skip_listed() {
  local file
  file="$(normalize_path "$1")"
  local entry
  for entry in "${SKIP_LIST[@]}"; do
    if [[ "$file" == "$entry" ]]; then
      return 0
    fi
  done
  return 1
}

# ── marker 정의 (whole-line anchored regex, ADR-027 §결정 7.D.3) ──────────────
# 각 파일 타입별 anchored pattern: ^[[:space:]]* ... [[:space:]]*$
# grep -E 사용 (ERE anchored whole-line)
get_begin_pattern() {
  local file="$1"
  case "${file##*.}" in
    yml|yaml|sh|*)
      echo '^[[:space:]]*# BEGIN wrapper-managed[[:space:]]*$'
      ;;
    md)
      echo '^[[:space:]]*<!-- BEGIN wrapper-managed -->[[:space:]]*$'
      ;;
    json)
      echo ""
      ;;
  esac
}

get_end_pattern() {
  local file="$1"
  case "${file##*.}" in
    yml|yaml|sh|*)
      echo '^[[:space:]]*# END wrapper-managed[[:space:]]*$'
      ;;
    md)
      echo '^[[:space:]]*<!-- END wrapper-managed -->[[:space:]]*$'
      ;;
    json)
      echo ""
      ;;
  esac
}

# ── 파일 타입별 marker 판별 (표시용 — grep -n 에 사용할 pattern 반환) ─────────
get_markers() {
  local file="$1"
  case "${file##*.}" in
    yml|yaml|sh)
      echo "# BEGIN wrapper-managed"
      echo "# END wrapper-managed"
      ;;
    md)
      echo "<!-- BEGIN wrapper-managed -->"
      echo "<!-- END wrapper-managed -->"
      ;;
    json)
      # JSON = marker-incapable (Wave 2 Story-5 sidecar manifest 영역)
      echo ""
      echo ""
      ;;
    *)
      # 미지원 확장자 = hash prefix marker 로 fallback (보수적)
      echo "# BEGIN wrapper-managed"
      echo "# END wrapper-managed"
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

  # ── whole-line anchored pattern 획득 ──────────────────────────────────────
  local begin_pattern end_pattern
  begin_pattern="$(get_begin_pattern "$file")"
  end_pattern="$(get_end_pattern "$file")"

  # marker 없는 파일 타입 = skip
  if [[ -z "$begin_pattern" ]]; then
    return 0
  fi

  # ── 검증 1: BEGIN / END count (whole-line anchored, ADR-027 §결정 7.D.3) ──
  local begin_count end_count
  # grep -cE whole-line: no-match 시 exit 1 + "0" 출력. assignment-with-fallback 패턴
  begin_count=$(grep -cE "$begin_pattern" "$file" 2>/dev/null) || begin_count=0
  end_count=$(grep -cE "$end_pattern" "$file" 2>/dev/null) || end_count=0
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
    # 표시용 fixed-string (행 번호 추출용 — grep -nE anchored 도 동일하나 가독성을 위해 패턴 재사용)
    begin_line=$(grep -nE "$begin_pattern" "$file" | head -1 | cut -d: -f1)
    end_line=$(grep -nE "$end_pattern" "$file" | head -1 | cut -d: -f1)

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
  local raw_files=()
  if [[ $# -gt 0 ]]; then
    # 명시적 인수
    raw_files=("$@")
  else
    # git diff 기반 자동 감지
    if ! command -v git &>/dev/null; then
      echo "$SCRIPT_NAME ERROR: git 미설치 (환경 오류)" >&2
      exit 2
    fi
    # PR 컨텍스트 (CI) vs 로컬 실행 분기
    local base_ref="${GITHUB_BASE_REF:-}"
    local git_files
    if [[ -n "$base_ref" ]]; then
      mapfile -t git_files < <(git diff --name-only "origin/${base_ref}...HEAD" 2>/dev/null \
        | grep -E '\.(yml|yaml|sh|md)$' || true)
    else
      # 로컬: staged + unstaged
      mapfile -t git_files < <({ git diff --name-only HEAD 2>/dev/null; git diff --cached --name-only 2>/dev/null; } \
        | grep -E '\.(yml|yaml|sh|md)$' | sort -u || true)
    fi
    raw_files=("${git_files[@]+"${git_files[@]}"}")
  fi

  # SKIP_LIST 필터링 (repo-relative exact path 매칭 — ADR-027 §결정 7.D.2)
  local file
  for file in "${raw_files[@]+"${raw_files[@]}"}"; do
    [[ -z "$file" ]] && continue
    if is_skip_listed "$file"; then
      echo "$SCRIPT_NAME SKIP (self-referential): $file" >&2
      continue
    fi
    echo "$file"
  done
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
    echo "$SCRIPT_NAME INFO: 검증 대상 파일 없음 (marker block 미사용, self-referential skip, 또는 변경 없음)" >&2
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
