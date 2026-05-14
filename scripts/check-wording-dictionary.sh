#!/usr/bin/env bash
# check-wording-dictionary.sh — wording-dictionary forbid-list lint + 평문 정의 의무 advisory check
# Exit code: 0 = pass (또는 category-b advisory only), 1 = warning (PR 머지 차단 안 함, ADR-060 warning tier)
# SSOT: docs/wording-dictionary.md (CFP-610 / ADR-064 Amendment 2)
#
# 카테고리 (a): 사용 금지 어휘 발견 시 exit 1 (warning)
# 카테고리 (b): 평문 정의 누락 시 exit 0 + advisory console warn (baseline 폭증 risk 완화)
#
# Exempt:
#   - blockquote 행 ("> " prefix)
#   - fenced code block (``` ... ```) 내부
#   - docs/wording-dictionary.md 자체 (사전 파일 — 어휘 정의 목적)
#
# Lint 적용 영역 (ADR-064 §결정 2 5 scope verbatim):
#   docs/adr/** / docs/change-plans/** / CLAUDE.md / docs/orchestrator-playbook.md / templates/**
# 단, 인자로 파일/디렉토리를 직접 지정 시 해당 대상에만 적용.

set -uo pipefail

# ─── 카테고리 (a): 사용 금지 어휘 ────────────────────────────────────────────
# Mirror of docs/wording-dictionary.md 카테고리 (a) — change in lockstep (CFP-610 / INV-1 / ADR-068 I-1)
FORBID_DICTIONARY=(
  "박제"
  "못 박기"
  "pin"
  "freezing"
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

# ─── EXEMPT 파일 (사전 파일 자체) ─────────────────────────────────────────────
EXEMPT_FILES=(
  "docs/wording-dictionary.md"
)

# ─── 기본 스캔 대상 (인자 없을 시) ────────────────────────────────────────────
if [ $# -eq 0 ]; then
  TARGETS=(
    "docs/adr"
    "docs/change-plans"
    "CLAUDE.md"
    "docs/orchestrator-playbook.md"
    "templates"
  )
else
  TARGETS=("$@")
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

# ─── 헬퍼: blockquote/fenced-code-block 제거 후 콘텐츠 반환 ─────────────────
strip_exempt() {
  local file="$1"
  local in_fence=0
  while IFS= read -r line; do
    # fenced code block 토글 (``` 로 시작)
    if [[ "$line" =~ ^\`\`\` ]]; then
      if [ "$in_fence" -eq 0 ]; then
        in_fence=1
      else
        in_fence=0
      fi
      # fence marker 줄 자체도 제외
      continue
    fi
    # fence 안 줄 = 제외
    [ "$in_fence" -eq 1 ] && continue
    # blockquote 줄 = 제외 ("> " 또는 ">" 로 시작, 선택적 공백 허용)
    [[ "$line" =~ ^[[:space:]]*\> ]] && continue
    echo "$line"
  done < "$file"
}

# ─── 헬퍼: 줄에 정의 패턴이 있는지 확인 (grep -P 대신 awk 사용) ──────────────
has_definition() {
  local line="$1"
  local word="$2"
  # word( 또는 word (" 패턴 — awk 로 처리 (Windows 호환)
  echo "$line" | awk -v w="$word" 'index($0, w"(") > 0 || index($0, w" (") > 0 { found=1 } END { exit !found }'
}

# ─── 파일 1개 스캔 ────────────────────────────────────────────────────────────
scan_file() {
  local file="$1"
  [ ! -f "$file" ] && return
  # .md 파일만 처리
  [[ "$file" != *.md ]] && return
  # EXEMPT 파일 건너뜀
  is_exempt_file "$file" && return

  local stripped
  stripped="$(strip_exempt "$file")"

  # 카테고리 (a): 금지 어휘
  # 영어 어휘: word-boundary regex + case-insensitive (false positive 차단 — "scoping" 안 "pin" 미검출)
  # 한국어 어휘: substring match (POSIX \b = ASCII boundary only, 한국어 영역 의미 없음)
  for word in "${FORBID_DICTIONARY[@]}"; do
    local hits
    local escaped_pattern
    if [[ "$word" =~ ^[a-zA-Z\ ]+$ ]]; then
      # 영어 어휘 — word-boundary + case-insensitive
      escaped_pattern="\\b${word}\\b"
      hits="$(echo "$stripped" | grep -niEH -- "$escaped_pattern" || true)"
    else
      # 한국어 어휘 — substring (case-insensitive 의미 없으나 -i 무해)
      hits="$(echo "$stripped" | grep -niH -- "$word" || true)"
    fi
    if [ -n "$hits" ]; then
      echo "WARNING [wording-dictionary 카테고리 (a) forbid]: '$word' 발견 — $file"
      echo "$hits" | while IFS= read -r hit; do
        echo "  $hit"
      done
      EXIT_CODE=1
    fi
  done

  # 카테고리 (b): 평문 정의 동반 의무 (exit 0 advisory only)
  for word in "${DEFINITION_REQUIRED_DICTIONARY[@]}"; do
    local hits
    hits="$(echo "$stripped" | grep -niH -- "$word" || true)"
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

# ─── 재귀 스캔 ────────────────────────────────────────────────────────────────
for target in "${TARGETS[@]}"; do
  [ ! -e "$target" ] && continue

  if [ -f "$target" ]; then
    scan_file "$target"
  elif [ -d "$target" ]; then
    while IFS= read -r -d '' f; do
      scan_file "$f"
    done < <(find "$target" -name "*.md" -print0 2>/dev/null)
  fi
done

if [ "$EXIT_CODE" -eq 0 ]; then
  echo "wording-dictionary PASS — 카테고리 (a) forbid 어휘 발견 없음"
fi

exit "$EXIT_CODE"
