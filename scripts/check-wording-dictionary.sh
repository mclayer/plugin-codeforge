#!/usr/bin/env bash
# check-wording-dictionary.sh — wording-dictionary forbid-list lint + 평문 정의 의무 advisory check
# Exit code: 0 = pass (또는 category-b advisory only), 1 = warning (PR 머지 차단 안 함, ADR-060 warning tier)
# SSOT: docs/wording-dictionary.md (CFP-610 / ADR-064 Amendment 2 + Amendment 5 — CFP-750)
#
# 카테고리 (a): 사용 금지 어휘 발견 시 exit 1 (warning)
# 카테고리 (b): 평문 정의 누락 시 exit 0 + advisory console warn (baseline 폭증 risk 완화)
#
# Exempt:
#   - blockquote 행 ("> " prefix)
#   - fenced code block (``` ... ```) 내부
#   - inline code-span (`...`) 내부 (Amendment 5 — CFP-750, 메타-언급 정밀 EXEMPT)
#   - docs/wording-dictionary.md 자체 (사전 파일 — 어휘 정의 목적)
#   - docs/adr/ADR-064-decision-principle-mandate.md (어휘 정의 ADR 본문)
#
# Lint 적용 영역 (ADR-064 Amendment 5 §Amendment 결정 2 — per-word scope decoupling):
#   박제 / 못 박기 / pin / freezing = docs/** + CLAUDE.md + CHANGELOG.md + templates/** (expanded scope)
#   별 (standalone) = docs/adr/** + docs/change-plans/** + CLAUDE.md + docs/orchestrator-playbook.md + templates/** (5-scope 유지)
# 단, 인자로 파일/디렉토리를 직접 지정 시 (uniform override mode) 해당 대상에만 적용.

set -uo pipefail

# ─── Bash 4+ guard (declare -A 의무 — codeforge precedent 4 sibling scripts) ──
# declare -A (associative array) = Bash 4+ 전용 syntax. macOS default /bin/bash =
# Bash 3.2 (Apple licensing frozen) 환경에서 즉시 실패. ADR-064 Amendment 5 §결정 2.
((BASH_VERSINFO[0] < 4)) && { echo "Bash 4+ required for declare -A (codeforge precedent — 4 sibling scripts)" >&2; exit 1; }

# ─── 카테고리 (a): 사용 금지 어휘 + per-word scope ────────────────────────────
# Mirror of docs/wording-dictionary.md 카테고리 (a) — change in lockstep (CFP-610 / CFP-672 / CFP-750 / INV-1 / ADR-068 I-1)
# 어휘 5 entry (Amendment 2: 박제 / 못 박기 / pin / freezing + Amendment 4: 별 standalone).
# Amendment 5 (CFP-750): FORBID_DICTIONARY array → per-word WORD_TARGETS associative array.
#   어휘별 scope 독립 결정 — scope 확장 시 `별` standalone false-positive collateral 차단.
#   박제/못 박기/pin/freezing = expanded scope (docs/** + CLAUDE.md + CHANGELOG.md + templates/**)
#   별 = 5-scope 유지 (별 standalone fp carrier 분리, Amendment 4 §Amendment 결정 6)
# SSOT forcing function: 어휘 list ↔ scope 가 단일 map 에 통합 → drift 차단.
# 한국어 어휘 = substring match (POSIX \b ASCII boundary only — 한국어 영역 의미 부재).
# false-positive 완화 = blockquote (>) + fenced code block + inline code-span (`...`) + EXEMPT_FILES framework.
declare -A WORD_TARGETS=(
  ["박제"]="docs CLAUDE.md CHANGELOG.md templates"
  ["못 박기"]="docs CLAUDE.md CHANGELOG.md templates"
  ["pin"]="docs CLAUDE.md CHANGELOG.md templates"
  ["freezing"]="docs CLAUDE.md CHANGELOG.md templates"
  ["별"]="docs/adr docs/change-plans CLAUDE.md docs/orchestrator-playbook.md templates"
)

# ─── 카테고리 (b): 평문 정의 동반 의무 어휘 ───────────────────────────────────
# Mirror of docs/wording-dictionary.md 카테고리 (b) — change in lockstep (CFP-610 / INV-1 / ADR-068 I-1)
DEFINITION_REQUIRED_DICTIONARY=(
  "normative"
  "sibling sync"
  "kind:contract"
  "ratchet"
  "mirrored field"
)

# 카테고리 (b) advisory scope = 카테고리 (a) 박제 expanded scope 와 동일 (default no-arg invocation).
DEFINITION_REQUIRED_SCOPE="docs CLAUDE.md CHANGELOG.md templates"

# ─── EXEMPT 파일 (사전 파일 자체 + 어휘 정의 ADR) ──────────────────────────────
# docs/wording-dictionary.md: 사전 파일 — 어휘 정의 목적
# docs/adr/ADR-064-*: §결정 2 forbid-list 어휘 정의 표 — 의도된 등장 (외연 허용 영역, ADR-064 §결정 2)
# Amendment 5 (CFP-750): 신규 entry 0 — 메타-언급은 inline code-span (`박제`) 정밀 EXEMPT 으로 처리
#   (file 전체 EXEMPT 차단 = sweep 대상 보존 의무, ADR-064 Amendment 5 §결정 1 처리 정책).
EXEMPT_FILES=(
  "docs/wording-dictionary.md"
  "docs/adr/ADR-064-decision-principle-mandate.md"
)

# ─── 인자 model (§3.2.1 — backward-compat zero migration cost) ────────────────
# 인자 없음 ($# -eq 0)  = per-word lookup mode — WORD_TARGETS map lookup 활성 (어휘별 독립 scope)
# 인자 있음 ($# -ne 0)  = uniform override mode — 지정 대상에만 모든 어휘 적용 (ad-hoc / 테스트)
if [ $# -eq 0 ]; then
  OVERRIDE_TARGETS=()
else
  OVERRIDE_TARGETS=("$@")
fi

EXIT_CODE=0

# ─── 헬퍼: EXEMPT 파일 여부 확인 ─────────────────────────────────────────────
is_exempt_file() {
  local file="$1"
  # 경로 정규화 (/ 로 통일)
  local normalized="${file//\\//}"
  for exempt in "${EXEMPT_FILES[@]}"; do
    local norm_exempt="${exempt//\\//}"
    # 파일 경로가 EXEMPT 경로로 끝나는지 확인
    if [[ "$normalized" == *"$norm_exempt" ]]; then
      return 0
    fi
  done
  return 1
}

# ─── 헬퍼: blockquote / fenced-code-block / inline-code-span 제거 후 콘텐츠 반환 ─
# R9 perf fix (CFP-750 §10 Iter 4 — Orchestrator Lead-conducted): per-line `sed` subshell
#   fork (O(lines × fork)) → 단일 awk 1-pass (O(1 fork/file)). 의미 동일 invariant 보존:
#   - fenced code block (``` ... ```) 토글 + fence marker 줄 제외
#   - blockquote ("> " prefix, 선택적 선행 공백) 줄 통째 제외 (Class-Q 사용자 verbatim 보존)
#   - 비-blockquote · 비-fence 줄만 inline code-span (`...`) gsub strip (Amendment 5 §3.3 — 메타-언급 정밀 EXEMPT)
#   precedence: fence > in_fence skip > blockquote skip > inline-code strip + print (원 per-line 분기 순서 verbatim)
strip_exempt() {
  awk '
    /^```/                { in_fence = !in_fence; next }
    in_fence              { next }
    /^[[:space:]]*>/      { next }
                          { gsub(/`[^`]*`/, ""); print }
  ' "$1"
}

# ─── 헬퍼: file당 strip 1회 memoize — filesystem cache (R9 perf fix iter 2) ──────
# CFP-750 §10 Iter 4 (Orchestrator Lead-conducted). iter 1 (awk 1-pass + bash assoc-array
#   memo) 는 large-string command-substitution per (file,word) (750 fork + huge string
#   pipe transfer) 가 잔존 bottleneck (CLAUDE.md 4.2s / no-arg 120s timeout). iter 2 =
#   stripped 결과를 tmp file 로 1회 기록 + path 만 반환 → grep 이 file 직접 read
#   (대형 string 의 bash var ↔ subshell 왕복 제거). 어휘 무관 memo (filesystem 재사용).
_STRIP_CACHE_DIR="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/wdlint.$$")"
mkdir -p "$_STRIP_CACHE_DIR"
trap 'rm -rf "$_STRIP_CACHE_DIR"' EXIT
get_stripped_file() {
  local file="$1"
  local key="${file//[^A-Za-z0-9]/_}"
  local cache="$_STRIP_CACHE_DIR/$key"
  [ -f "$cache" ] || strip_exempt "$file" > "$cache"
  printf '%s' "$cache"
}

# ─── 헬퍼: 줄에 정의 패턴이 있는지 확인 (grep -P 대신 awk 사용) ──────────────
has_definition() {
  local line="$1"
  local word="$2"
  # word( 또는 word (" 패턴 — awk 로 처리 (Windows 호환)
  echo "$line" | awk -v w="$word" 'index($0, w"(") > 0 || index($0, w" (") > 0 { found=1 } END { exit !found }'
}

# ─── 단일 어휘에 대해 파일 1개 스캔 (per-word × per-file iteration) ────────────
# R9 mitigation: per-line subshell loop → file-level `grep -E ... <stripped>` 일괄.
#   strip_exempt 가 blockquote/fenced/inline-code 를 줄 단위 정확 제거 후 file-level grep 적용.
#   dispatch logic 3-way branch (영어 word-boundary / 별 Hangul-boundary / 한국어 substring) = 의미 0 line 변경.
scan_file_for_word() {
  local file="$1"
  local word="$2"
  [ ! -f "$file" ] && return
  # .md 파일만 처리 (코드 file = self-referential / test fixture 보호, §3.5)
  [[ "$file" != *.md ]] && return
  # EXEMPT 파일 건너뜀
  is_exempt_file "$file" && return

  local sf
  sf="$(get_stripped_file "$file")"

  # 카테고리 (a): 금지 어휘 — dispatch logic 3-way branch (§6.2 claim precision-tighten: 의미 0 line 변경)
  # 영어 어휘: word-boundary regex + case-insensitive (false positive 차단 — "scoping" 안 "pin" 미검출)
  # 한국어 단일 character 어휘 (별): Hangul-boundary lookahead/lookbehind regex (PCRE)
  #   — `별도` / `별개` / `특별` / `구별` 등 한자어 compound 차단 + standalone `별 도리` / `별 carrier` 만 detect
  # 한국어 multi-character 어휘 (박제, 못 박기): substring match (POSIX \b 의미 부재, false-positive risk 낮음)
  # R9 perf iter 2: grep 이 stripped tmp file 직접 read (대형 string bash var ↔ subshell 왕복 제거)
  local hits
  local escaped_pattern
  if [[ "$word" =~ ^[a-zA-Z\ ]+$ ]]; then
    # 영어 어휘 — word-boundary + case-insensitive
    escaped_pattern="\\b${word}\\b"
    hits="$(grep -niE -- "$escaped_pattern" "$sf" || true)"
  elif [ "$word" = "별" ]; then
    # 한국어 단일 character (CFP-672 Amendment 4) — Hangul-boundary lookahead/lookbehind
    # (?<![가-힣]) = 직전 character 가 Hangul 음절 (U+AC00-U+D7A3) 아님
    # (?![가-힣])  = 직후 character 가 Hangul 음절 아님
    # → standalone `별` (공백 / 구두점 / line edge 로 둘러싸인) 만 match.
    # Perl regex (-P) 가 PCRE 지원 = Hangul Unicode class. LC_ALL UTF-8 강제.
    escaped_pattern="(?<![가-힣])${word}(?![가-힣])"
    hits="$(LC_ALL=en_US.UTF-8 grep -nP -- "$escaped_pattern" "$sf" 2>/dev/null || true)"
  else
    # 한국어 multi-character 어휘 — substring (case-insensitive 의미 없으나 -i 무해)
    hits="$(grep -ni -- "$word" "$sf" || true)"
  fi
  if [ -n "$hits" ]; then
    echo "WARNING [wording-dictionary 카테고리 (a) forbid]: '$word' 발견 — $file"
    echo "$hits" | while IFS= read -r hit; do
      echo "  $hit"
    done
    EXIT_CODE=1
  fi
}

# ─── 단일 파일 카테고리 (b) 스캔 (어휘 무관 — 평문 정의 동반 의무) ─────────────
scan_file_definitions() {
  local file="$1"
  [ ! -f "$file" ] && return
  [[ "$file" != *.md ]] && return
  is_exempt_file "$file" && return

  local sf
  sf="$(get_stripped_file "$file")"

  for word in "${DEFINITION_REQUIRED_DICTIONARY[@]}"; do
    local hits
    hits="$(grep -ni -- "$word" "$sf" || true)"
    [ -z "$hits" ] && continue

    while IFS= read -r hit_line; do
      # 해당 줄에 "word(" 또는 "word (" 패턴이 없으면 advisory
      if ! has_definition "$hit_line" "$word"; then
        echo "ADVISORY [wording-dictionary 카테고리 (b) 평문 정의 누락]: '$word' — $file"
        echo "  $hit_line"
      fi
    done <<< "$hits"
  done
}

# ─── 헬퍼: scope path list 를 순회하며 .md 파일에 대해 콜백 적용 ──────────────
scan_scope() {
  local callback="$1"
  shift
  local scopes=("$@")
  local target
  for target in "${scopes[@]}"; do
    [ ! -e "$target" ] && continue
    if [ -f "$target" ]; then
      "$callback" "$target"
    elif [ -d "$target" ]; then
      while IFS= read -r -d '' f; do
        "$callback" "$f"
      done < <(find "$target" -name "*.md" -print0 2>/dev/null)
    fi
  done
}

# ─── 메인 스캔 ────────────────────────────────────────────────────────────────
if [ ${#OVERRIDE_TARGETS[@]} -eq 0 ]; then
  # per-word lookup mode — 어휘별 독립 scope (WORD_TARGETS map lookup)
  for word in "${!WORD_TARGETS[@]}"; do
    # shellcheck disable=SC2206  # 공백 split = 의도 (scope path list)
    scope_paths=(${WORD_TARGETS[$word]})
    for target in "${scope_paths[@]}"; do
      [ ! -e "$target" ] && continue
      if [ -f "$target" ]; then
        scan_file_for_word "$target" "$word"
      elif [ -d "$target" ]; then
        while IFS= read -r -d '' f; do
          scan_file_for_word "$f" "$word"
        done < <(find "$target" -name "*.md" -print0 2>/dev/null)
      fi
    done
  done
  # 카테고리 (b) advisory — 박제 expanded scope 와 동일 영역
  # shellcheck disable=SC2206
  defn_scope=($DEFINITION_REQUIRED_SCOPE)
  scan_scope scan_file_definitions "${defn_scope[@]}"
else
  # uniform override mode — 지정 대상에만 모든 어휘 + 카테고리 (b) 적용
  for word in "${!WORD_TARGETS[@]}"; do
    for target in "${OVERRIDE_TARGETS[@]}"; do
      [ ! -e "$target" ] && continue
      if [ -f "$target" ]; then
        scan_file_for_word "$target" "$word"
      elif [ -d "$target" ]; then
        while IFS= read -r -d '' f; do
          scan_file_for_word "$f" "$word"
        done < <(find "$target" -name "*.md" -print0 2>/dev/null)
      fi
    done
  done
  scan_scope scan_file_definitions "${OVERRIDE_TARGETS[@]}"
fi

if [ "$EXIT_CODE" -eq 0 ]; then
  echo "wording-dictionary PASS — 카테고리 (a) forbid 어휘 발견 없음"
fi

exit "$EXIT_CODE"
