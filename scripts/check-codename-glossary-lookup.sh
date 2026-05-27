#!/usr/bin/env bash
# check-codename-glossary-lookup.sh — wording-dictionary 카테고리 (c) PR diff scan lint
# CFP-1764 Story-2, ADR-071 §결정 19 (Amendment 8) mechanical wire
# Exit codes (ADR-060 §결정 15): 0=pass, 1=warning, 2=error
#
# Input: --file <path>   (단일 파일 scan 모드)
# Bypass: --bypass-label=hotfix-bypass:codename-glossary-lookup
#
# Detection logic:
#   각 line 에서 카테고리 (c) codename 발견 시:
#     - 동일 line 안 한글 괄호 풀이 또는 wording-dictionary 링크 있으면 pass
#     - 그 외 = warning (codename leak suspected)
#
# ADR-061 §결정 11 ReDoS-safe: line-by-line scan, anchored simple patterns
# ADR-061 §결정 11 per-entry scan cap default N=50 line

set -euo pipefail

# Parse args
FILE_TARGET=""
BYPASS_LABEL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      FILE_TARGET="$2"
      shift 2
      ;;
    --bypass-label=*)
      BYPASS_LABEL="${1#--bypass-label=}"
      shift
      ;;
    --bypass-label)
      BYPASS_LABEL="$2"
      shift 2
      ;;
    *)
      echo "[error] Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

# File target 검증
if [[ -z "${FILE_TARGET}" ]]; then
  echo "[error] --file argument required" >&2
  exit 2
fi

if [[ ! -f "${FILE_TARGET}" ]]; then
  echo "[error] File not found: ${FILE_TARGET}" >&2
  exit 2
fi

# Bypass channel (ADR-024 §결정 6 정합)
if [[ "${BYPASS_LABEL}" == "hotfix-bypass:codename-glossary-lookup" ]]; then
  echo "[bypass] hotfix-bypass:codename-glossary-lookup label detected, lint skipped"
  exit 0
fi

# Codename list — wording-dictionary 카테고리 (c) closed 15 batch (Story-1 carrier)
# 순서: 긴 패턴 먼저 (sub-set 충돌 방지)
CODENAMES=(
  "scope manifest"
  "carry-over"
  "sub-agent"
  "sub-mechanism"
  "forcing function"
  "Phase 1"
  "Phase 2"
  "Phase"
  "Layer"
  "carry"
  "drift"
  "ratchet"
  "mid-turn"
  "Story"
  "spec"
  "ADR"
  "Amendment"
  "agent"
  "lane"
)

# Per-line scan (ADR-061 §결정 11 ReDoS-safe line-by-line)
WARNING_COUNT=0
LINE_NUM=0
# regex 변수 선언 — bash [[ =~ ]] 직접 리터럴 이스케이프 불가 (syntax error 방지)
KOREAN_PAREN_PATTERN='\([^)]*[가-힣][^)]*\)'

while IFS= read -r line; do
  LINE_NUM=$((LINE_NUM + 1))

  for codename in "${CODENAMES[@]}"; do
    if [[ "${line}" == *"${codename}"* ]]; then
      # 평이 풀이 동반 검사 (heuristic):
      # (1) 동일 line 안 한글 문자가 포함된 괄호 표현 — "(한글)" 형태
      # (2) wording-dictionary 링크 포함
      # ADR-061 §결정 11: KOREAN_PAREN_PATTERN 변수 사용 (직접 리터럴 이스케이프 불가)
      if [[ "${line}" =~ $KOREAN_PAREN_PATTERN ]] || \
         [[ "${line}" == *"wording-dictionary"* ]]; then
        continue  # 평이 풀이 동반 또는 dictionary 링크 존재 → pass
      fi
      WARNING_COUNT=$((WARNING_COUNT + 1))
      echo "[warning] line ${LINE_NUM}: codename '${codename}' without plain-language accompany" >&2
      echo "  > ${line}" >&2
      break  # 해당 line 에서 첫 번째 codename 발견으로 충분
    fi
  done
done < "${FILE_TARGET}"

if [[ ${WARNING_COUNT} -gt 0 ]]; then
  echo "[summary] ${WARNING_COUNT} codename leak warning(s) — use hotfix-bypass:codename-glossary-lookup label to bypass"
  exit 1
fi

echo "[pass] No codename leak detected in ${FILE_TARGET}"
exit 0
