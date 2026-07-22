#!/usr/bin/env bash
# check-wording-dictionary.sh — wording-dictionary forbid-list lint + 평문 정의 의무 advisory check
# Exit code: 0 = pass (또는 category-b advisory only), 1 = warning (PR 머지 차단 안 함, ADR-060 warning tier)
# SSOT: docs/wording-dictionary.md (CFP-610 / ADR-064 Amendment 2 + Amendment 5 — CFP-750)
#
# ─── Mode invariant SSOT (CFP-1345 / CFP-1316 retro F5 codify, super-class #1047 Wave 2) ──
# 본 lint 의 dual-mode invariant 는 ADR-064 §결정 1 wording-dictionary lint policy 가 SSOT 다.
# 두 mode 는 disjoint exit code 영역 — script body cross-contamination 금지:
#
#   카테고리 (a) STRICT mode    — 사용 금지 어휘 발견 시 EXIT_CODE=1 (warning tier, PR 머지 차단 안 함)
#                                  → emission point: scan_file_forbidden() L181 EXIT_CODE=1
#                                  → enforcement: ADR-060 warning-tier evidence-checks-registry entry
#                                                 `wording-dictionary` + bypass label `hotfix-bypass:wording-dictionary`
#
#   카테고리 (b) ADVISORY mode  — 평문 정의 누락 시 EXIT_CODE 무변경 (0 invariant) + console echo only
#                                  → emission point: scan_file_definitions() L200-206 echo only (no exit mutation)
#                                  → enforcement: 0 (advisory baseline 폭증 risk 완화 — CFP-1316 inline_orchestrator_verify 결과 검증)
#
# Mode 분리 강제: scan_file_definitions() 안 EXIT_CODE=1 mutation 금지 (cat-b advisory 영역 invariant).
# CLI flag `--strict` / `--advisory-only` 미지원 — dual-mode invariant 가 mode flag 보다 결정 명확.
#
# Exempt:
#   - blockquote 행 ("> " prefix)
#   - fenced code block (``` ... ```) 내부
#   - inline code-span (`...`) 내부 (Amendment 5 — CFP-750, 메타-언급 정밀 EXEMPT)
#   - docs/wording-dictionary.md 자체 (사전 파일 — 어휘 정의 목적)
#   - docs/adr/ADR-064-decision-principle-mandate.md (어휘 정의 ADR 본문)
#
# Lint 적용 영역 (ADR-064 Amendment 5 §Amendment 결정 2 — per-word scope decoupling):
#   박제 / 못 박기 / pin / freezing = docs/** + CLAUDE.md + templates/** (expanded scope)
#   별 (standalone) = docs/adr/** + archive/adr/** + docs/change-plans/** + CLAUDE.md + docs/orchestrator-playbook.md + templates/** (6-scope — archive/adr CFP-2661 D1 union-ADD, ADR-064 Amendment 14/CFP-1561 SSOT 정합. WORD_TARGETS L62 이 SSOT)
# 단, 인자로 파일/디렉토리를 직접 지정 시 (uniform override mode) 해당 대상에만 적용.
# CHANGELOG.md = scope 에서 제거 (CFP-2154 — main 에 CHANGELOG.md 부재 dead reference 정리.
#   정책 선언 자체는 docs/wording-dictionary.md 유지 — 파일 재생성 시 target 재추가).
#
# Self-test: `--self-test` 단일 flag = inline fixture 기반 counter-case 검증 (CFP-2154,
#   CFP-2104 D3 --self-test precedent 답습). dual-mode invariant 무관 (mode flag 아님).

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
#   박제/못 박기/pin/freezing = expanded scope (docs/** + CLAUDE.md + templates/**)
#   별 = 6-scope (5 영역 + archive/adr CFP-2661 D1 union-ADD; 확장 scope docs/inter-plugin-contracts 등은 배제 — fp carrier 분리, Amendment 4 §Amendment 결정 6 + Amendment 14/CFP-1561)
# CHANGELOG.md target 제거 (CFP-2154 — main 부재 dead reference 정리, 행동 변화 0).
# SSOT forcing function: 어휘 list ↔ scope 가 단일 map 에 통합 → drift 차단.
# 한국어 어휘 = substring match (POSIX \b ASCII boundary only — 한국어 영역 의미 부재).
# false-positive 완화 = blockquote (>) + fenced code block + inline code-span (`...`) + EXEMPT_FILES framework.
declare -A WORD_TARGETS=(
  ["박제"]="docs CLAUDE.md templates"
  ["못 박기"]="docs CLAUDE.md templates"
  ["pin"]="docs CLAUDE.md templates"
  ["freezing"]="docs CLAUDE.md templates"
  ["별"]="docs/adr archive/adr docs/change-plans CLAUDE.md docs/orchestrator-playbook.md templates"
)
# CFP-2661 D1: `별` scope union-ADD `archive/adr` (ADR 실 위치 = archive/adr, PR #1973 이동; 구경로 docs/adr
#   단독 = dead-path → scope=∅ vacuous-PASS 였음). docs/adr 는 consumer 정답 경로라 union 보존(치환 아님, I-2).
#   D1-c 원자결합: EXEMPT_FILES 도 archive/adr/ADR-064 union (분리 시 ADR-064 어휘 정의 본문 self-red).

# ─── Amendment 3 (CFP-1060) — `별 + carrier-noun` hand-off vocabulary exemption ──
# docs/wording-dictionary.md Amendment 3 §규칙 선언 regex 의 verbatim wire (Wave 2
# mechanical lint update — CFP-2154 실현). 선언문이 SSOT — noun list 임의 확장 금지.
# 선언 패턴: 별\s+(sub-CFP|carrier|session|Story|Issue|PR|lane|sub-Epic|Epic|Wave|layer|sub-axis|sub-CFP carrier|sub-Story)
# 적용 방식 = sed pre-screen: 면제 패턴 occurrence 만 제거 후 standalone `별` 검출
# (per-occurrence 정밀 — 동일 줄 안 비면제 `별` 은 계속 검출, line 단위 통째 면제 아님).
# alternation 은 longest-first 정렬 (POSIX ERE leftmost-longest 외 구현 방어).
BYEOL_CARRIER_NOUN_EXEMPT='sub-CFP carrier|sub-Story|sub-Epic|sub-axis|sub-CFP|session|carrier|Story|Issue|lane|Epic|Wave|layer|PR'

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
# CHANGELOG.md target 제거 (CFP-2154 — main 부재 dead reference 정리).
DEFINITION_REQUIRED_SCOPE="docs CLAUDE.md templates"

# ─── EXEMPT 파일 (사전 파일 자체 + 어휘 정의 ADR) ──────────────────────────────
# docs/wording-dictionary.md: 사전 파일 — 어휘 정의 목적
# docs/adr/ADR-064-*: §결정 2 forbid-list 어휘 정의 표 — 의도된 등장 (외연 허용 영역, ADR-064 §결정 2)
# Amendment 5 (CFP-750): 신규 entry 0 — 메타-언급은 inline code-span (`박제`) 정밀 EXEMPT 으로 처리
#   (file 전체 EXEMPT 차단 = sweep 대상 보존 의무, ADR-064 Amendment 5 §결정 1 처리 정책).
EXEMPT_FILES=(
  "docs/wording-dictionary.md"
  "docs/adr/ADR-064-decision-principle-mandate.md"
  "archive/adr/ADR-064-decision-principle-mandate.md"  # CFP-2661 D1-c: ADR-064 실 위치 union (archive/adr; scope union 과 원자)
  # ADR-108 append-only frozen 이력 — 과거 entry description 의 어휘는 audit trail
  # verbatim 보존 의무 (rewrite 금지) → file 단위 EXEMPT (CFP-2154).
  "docs/inter-plugin-contracts/label-registry-v2.md"
)

# ─── CFP-2661 D1 grandfather baseline (AC-4 — 노출 debt 동결 + new-only subtract) ──
# D1 union(archive/adr) 이 노출한 기존 ADR 본문 위반(실측 83 파일 / 85 별 hit)을 (file|word|content) 로
# 동결 → new-only 만 flag (선례 docs/resource-safety-claim-baseline.yaml / deferred-followup-baseline.yaml).
# 기존 debt 는 warning-tier 라도 소음이므로 freeze; 신규 위반 1줄 주입 시 exit≠0 (mutation-kill AC-4).
# (플래그 파싱 前 정의 필수 — --write-baseline 이 아래 vars/함수 소비.)
WD_BASELINE_FILE="${WD_BASELINE_FILE:-docs/wording-dictionary-baseline.yaml}"
WD_WRITE_BASELINE=0
declare -A WD_BASELINE
WD_GRANDFATHERED=0
WD_NEW_VIOL=0
WD_BASELINE_TMP=""

wd_normalize_content() {
  printf '%s' "$1" | tr -s '[:space:]' ' ' | sed 's/^ *//;s/ *$//'
}

load_wd_baseline() {
  [ -f "$WD_BASELINE_FILE" ] || return 0
  local f="" w="" c
  while IFS= read -r line; do
    case "$line" in
      "- file: "*) f="${line#- file: }" ;;
      "  word: "*) w="${line#  word: }" ;;
      "  content: "*) c="${line#  content: }"; WD_BASELINE["${f}|${w}|${c}"]=1 ;;
    esac
  done < "$WD_BASELINE_FILE"
}

# ─── 인자 model (§3.2.1 — backward-compat zero migration cost) ────────────────
# 인자 없음 ($# -eq 0)  = per-word lookup mode — WORD_TARGETS map lookup 활성 (어휘별 독립 scope)
# 인자 있음 ($# -ne 0)  = uniform override mode — 지정 대상에만 모든 어휘 적용 (ad-hoc / 테스트)
# --self-test           = inline fixture counter-case 검증 (CFP-2154 / CFP-2104 D3 precedent)
SELF_TEST=0
if [ "${1:-}" = "--self-test" ]; then
  SELF_TEST=1
  shift
fi
# CFP-2661 D1: --write-baseline 모드 (현 카테고리 (a) 위반 전건 동결). single writer, 수기 편집 금지.
if [ "${1:-}" = "--write-baseline" ]; then
  WD_WRITE_BASELINE=1
  shift
  WD_BASELINE_TMP="$(mktemp)"
fi
if [ $# -eq 0 ]; then
  OVERRIDE_TARGETS=()
else
  OVERRIDE_TARGETS=("$@")
fi

# CFP-2661 D1: baseline load (write 모드 아닐 때만 subtract 활성).
if [ "$WD_WRITE_BASELINE" -eq 0 ]; then
  load_wd_baseline
fi

EXIT_CODE=0

# ─── CFP-2661 D1: scanned-count census + 침묵-skip 봉인 (AC-1 — scanned≥156 emit / 침묵 skip 0) ──
# 게이트가 "아무것도 안 봤다"(scope=∅ vacuous-PASS)를 관측 가능하게: 실 스캔 ADR 파일 수 + 부재 scope
# skip 을 가시화한다. 부재 scope 는 조용히 continue(침묵) 하지 않고 announce 후 counter 증가.
WD_ADR_DISCOVERED=0   # adr/ADR-*.md 실 진입 수 (union archive/adr → ≥156; scope=∅ 이면 0 = vacuous 노출).
WD_FILE_SCANNED=0     # 전 .md×word 실 스캔 수.
WD_MISSING_SKIP=0     # 부재 scope path 가시화 skip 수 (침묵 아님 — announce 됨).

# 부재 scope path 가시화 helper (CFP-2661 D1 — `[ ! -e ] && continue` 침묵 skip 봉인).
announce_missing_scope() {
  echo "wording-dictionary: [skip:missing-scope] '$1' 부재 — dead-path 가시화 (침묵 skip 아님, warning tier)"
  WD_MISSING_SKIP=$((WD_MISSING_SKIP+1))
}

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
  # CFP-2661 D1 census: ADR 파일(adr/ADR-*.md) 진입 수 집계 (exempt 前 = anti-vacuity discovered floor).
  case "${file//\\//}" in *adr/ADR-*) WD_ADR_DISCOVERED=$((WD_ADR_DISCOVERED+1));; esac
  # EXEMPT 파일 건너뜀
  is_exempt_file "$file" && return
  WD_FILE_SCANNED=$((WD_FILE_SCANNED+1))

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
    # 'pin' false-positive 좁힘 (prune): 정책은 한국어 메타포 'pin' 차단 목적이나
    # GitHub Actions / git 표준 기술 compound(SHA-pin / HEAD-pin / re-pin / contract-pin / spawn pin 등)는
    # 정당 기술 용어 → 해당 compound 줄만 제외 (어휘 정책 보존, 오탐만 제거).
    if [ "$word" = "pin" ] && [ -n "$hits" ]; then
      # workspace 추가 (CFP-2154): `Cargo.lock workspace pin` 등 표준 기술 compound.
      hits="$(printf '%s\n' "$hits" | grep -viE -- '([a-z0-9]-pin|pin-[a-z0-9]|(sha|head|spawn|contract|main|action|re|git|version|baseline|frozen|prompt|workspace)[ -]?pin)' || true)"
    fi
  elif [ "$word" = "별" ]; then
    # 한국어 단일 character (CFP-672 Amendment 4) — Hangul-boundary lookahead/lookbehind
    # (?<![가-힣]) = 직전 character 가 Hangul 음절 (U+AC00-U+D7A3) 아님
    # (?![가-힣])  = 직후 character 가 Hangul 음절 아님
    # → standalone `별` (공백 / 구두점 / line edge 로 둘러싸인) 만 match.
    # Perl regex (-P) 가 PCRE 지원 = Hangul Unicode class. LC_ALL UTF-8 강제.
    # Amendment 3 (CFP-1060) exemption pre-screen (CFP-2154 wire): 선언된 `별 + carrier-noun`
    # hand-off vocabulary occurrence 를 먼저 제거 (sed 는 줄 보존 — 줄번호 불변).
    escaped_pattern="(?<![가-힣])${word}(?![가-힣])"
    hits="$(sed -E "s/별[[:space:]]+(${BYEOL_CARRIER_NOUN_EXEMPT})//g" "$sf" | LC_ALL=en_US.UTF-8 grep -nP -- "$escaped_pattern" 2>/dev/null || true)"
  else
    # 한국어 multi-character 어휘 — substring (case-insensitive 의미 없으나 -i 무해)
    hits="$(grep -ni -- "$word" "$sf" || true)"
  fi
  if [ -n "$hits" ]; then
    # CFP-2661 D1: grandfather baseline subtract (new-only) + --write-baseline collect.
    local emitted_header=0 content norm key
    while IFS= read -r hit; do
      [ -z "$hit" ] && continue
      content="${hit#*:}"                       # strip leading "<lineno>:"
      norm="$(wd_normalize_content "$content")"
      key="${file}|${word}|${norm}"
      if [ "$WD_WRITE_BASELINE" -eq 1 ]; then
        printf -- '- file: %s\n  word: %s\n  content: %s\n' "$file" "$word" "$norm" >> "$WD_BASELINE_TMP"
        continue
      fi
      if [ -n "${WD_BASELINE[$key]:-}" ]; then
        WD_GRANDFATHERED=$((WD_GRANDFATHERED+1))
        continue
      fi
      if [ "$emitted_header" -eq 0 ]; then
        echo "WARNING [wording-dictionary 카테고리 (a) forbid — NEW]: '$word' 발견 — $file"
        emitted_header=1
      fi
      echo "  $hit"
      WD_NEW_VIOL=$((WD_NEW_VIOL+1))
      # Mode invariant: STRICT mode (CFP-1345 header SSOT) — 카테고리 (a) emission point.
      # ADR-064 §결정 1 wording-dictionary lint policy + ADR-060 warning-tier framework. new-only (D1 baseline).
      EXIT_CODE=1
    done <<< "$hits"
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
        # Mode invariant: ADVISORY mode (CFP-1345 header SSOT) — 카테고리 (b) emission point.
        # EXIT_CODE 무변경 강제 (0 invariant) — strict cross-contamination 금지 (cat-a 영역과 disjoint).
        # ADR-064 §결정 1 wording-dictionary lint policy + baseline 폭증 risk 완화 mitigation.
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
    if [ ! -e "$target" ]; then announce_missing_scope "$target"; continue; fi
    if [ -f "$target" ]; then
      "$callback" "$target"
    elif [ -d "$target" ]; then
      while IFS= read -r -d '' f; do
        "$callback" "$f"
      done < <(find "$target" -name "*.md" -print0 2>/dev/null)
    fi
  done
}

# ─── --self-test: inline fixture counter-case 검증 (CFP-2154 / CFP-2104 D3 precedent) ──
# regex 정련 (Amendment 3 wire + pin workspace compound) 의 보호 강도 비축소 입증 의무:
# 정탐(true-positive) 보존 counter-case + 면제(exemption) 양방향 fixture.
# fixture = 임시 dir 안 .md (repo 스캔 대상 외) — uniform override mode 재귀 호출로 검증.
if [ "$SELF_TEST" -eq 1 ]; then
  ST_DIR="$(mktemp -d)"
  ST_FAIL=0
  st_case() {
    # $1 = case 이름 / $2 = fixture 내용 / $3 = 기대 exit code (0|1)
    local name="$1" content="$2" expected="$3" rc
    printf '%s\n' "$content" > "$ST_DIR/case.md"
    bash "$0" "$ST_DIR/case.md" > /dev/null 2>&1
    rc=$?
    if [ "$rc" -ne "$expected" ]; then
      echo "SELF-TEST FAIL: $name (expected exit $expected, got $rc)"
      ST_FAIL=1
    else
      echo "SELF-TEST PASS: $name"
    fi
  }
  # ── 정탐 보존 (counter-case — 보호 강도 비축소) ──
  st_case "박제 정탐 유지" "이 결정을 박제 한다." 1
  st_case "별 standalone 정탐 유지 (carrier-noun 외)" "별 컴퓨터 에서 실행한다." 1
  st_case "별 + 비면제 명사 정탐 유지" "동일 또는 별 Orchestrator session 에서." 1
  st_case "동일 줄 면제+정탐 혼재 — 정탐 유지" "별 carrier 분리 후 별 컴퓨터 사용." 1
  st_case "pin standalone 정탐 유지" "please pin the dependency." 1
  # ── 면제 (Amendment 3 wire + 기존 exempt invariant 보존) ──
  st_case "Amendment 3: 별 sub-CFP carrier" "Wave 2 별 sub-CFP carrier 분리." 0
  st_case "Amendment 3: 별 Story" "별 Story 로 발의한다." 0
  st_case "Amendment 3: 별 PR" "S2 는 별 PR 로 처리." 0
  st_case "Hangul-boundary: 별도/특별/구별 비검출 유지" "별도 처리. 특별 조치. 구별 기준." 0
  st_case "pin compound: workspace pin (CFP-2154 신규)" "Cargo.lock workspace pin 답습." 0
  st_case "pin compound: SHA-pin (기존 유지)" "action SHA-pin 정책 유지." 0
  st_case "blockquote exempt 유지" "> 박제 금지 인용문." 0
  # ── CFP-2661 D1 grandfather baseline (AC-4 — test_d1_grandfather_new_only: freeze → exit 0, new → exit 1) ──
  ST_BL="$ST_DIR/wd-baseline.yaml"
  printf '별 컴퓨터 에서 실행한다.\n' > "$ST_DIR/case.md"
  WD_BASELINE_FILE="$ST_BL" bash "$0" --write-baseline "$ST_DIR/case.md" > /dev/null 2>&1
  WD_BASELINE_FILE="$ST_BL" bash "$0" "$ST_DIR/case.md" > /dev/null 2>&1
  if [ $? -eq 0 ]; then echo "SELF-TEST PASS: D1 baseline grandfather (existing 위반 freeze → exit 0)"; else echo "SELF-TEST FAIL: D1 baseline grandfather"; ST_FAIL=1; fi
  printf '별 컴퓨터 에서 실행한다.\n또 별 도리 없다.\n' > "$ST_DIR/case.md"
  WD_BASELINE_FILE="$ST_BL" bash "$0" "$ST_DIR/case.md" > /dev/null 2>&1
  if [ $? -eq 1 ]; then echo "SELF-TEST PASS: D1 baseline new-only (신규 위반 주입 → exit 1, mutation-kill AC-4)"; else echo "SELF-TEST FAIL: D1 baseline new-only"; ST_FAIL=1; fi
  rm -rf "$ST_DIR"
  if [ "$ST_FAIL" -eq 1 ]; then
    echo "wording-dictionary self-test FAIL"
    exit 1
  fi
  echo "wording-dictionary self-test PASS (14 case — 12 + D1 baseline grandfather/new-only AC-4)"
  exit 0
fi

# ─── 메인 스캔 ────────────────────────────────────────────────────────────────
if [ ${#OVERRIDE_TARGETS[@]} -eq 0 ]; then
  # per-word lookup mode — 어휘별 독립 scope (WORD_TARGETS map lookup)
  for word in "${!WORD_TARGETS[@]}"; do
    # shellcheck disable=SC2206  # 공백 split = 의도 (scope path list)
    scope_paths=(${WORD_TARGETS[$word]})
    for target in "${scope_paths[@]}"; do
      if [ ! -e "$target" ]; then announce_missing_scope "$target"; continue; fi
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
      if [ ! -e "$target" ]; then announce_missing_scope "$target"; continue; fi
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

# CFP-2661 D1: --write-baseline 마무리 (수집 위반 dedup 후 baseline yaml write).
if [ "$WD_WRITE_BASELINE" -eq 1 ]; then
  {
    echo "# docs/wording-dictionary-baseline.yaml — GENERATED by scripts/check-wording-dictionary.sh --write-baseline (CFP-2661 D1)"
    echo "# DO NOT EDIT BY HAND. Regenerate: bash scripts/check-wording-dictionary.sh --write-baseline"
    echo "# grandfather = D1 union(archive/adr) 노출 시점 기존 카테고리 (a) 위반(file|word|content) 동결 → new-only subtract (ADR-060 §결정6 Clean-as-You-Code)."
    echo "schema_version: '1.0'"
    echo "generated_by: CFP-2661"
    echo "grandfathered_violations:"
    if [ -s "$WD_BASELINE_TMP" ]; then
      # 3-line record 단위 dedup (paste 로 record 합치기 → sort -u → 재분해).
      paste -d '\t' - - - < "$WD_BASELINE_TMP" | sort -u | tr '\t' '\n'
    else
      echo "# (none)"
    fi
  } > "$WD_BASELINE_FILE"
  rm -f "$WD_BASELINE_TMP"
  echo "wording-dictionary: baseline written $WD_BASELINE_FILE"
  exit 0
fi

# CFP-2661 D1 census (AC-1 — scanned-count emit / 침묵 skip 0). scope=∅ 이면 adr_files_scanned=0 노출.
echo "wording-dictionary: census adr_files_scanned=$WD_ADR_DISCOVERED total_md_word_scans=$WD_FILE_SCANNED missing_scope_skip=$WD_MISSING_SKIP grandfathered=$WD_GRANDFATHERED new_violations=$WD_NEW_VIOL (침묵 skip 0 — 부재 scope 전량 가시화)"

if [ "$EXIT_CODE" -eq 0 ]; then
  echo "wording-dictionary PASS — 카테고리 (a) forbid 신규 위반 없음 (grandfathered=$WD_GRANDFATHERED)"
fi

exit "$EXIT_CODE"
