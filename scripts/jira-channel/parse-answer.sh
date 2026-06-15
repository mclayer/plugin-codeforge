#!/usr/bin/env bash
# CFP-2285 S2 (#2288) — Jira 결정 채널 답변 코멘트 옵션 파서
# 인용 출처: ADR-099 Amendment 1 §A1-3 (first-valid-immutable — 첫 유효 답변만 채택).
#   본 스크립트는 "단일 코멘트 1건"에서 옵션 식별자를 추출한다(결정론적 순수 텍스트).
#   first-valid 선별(여러 코멘트 중 첫 유효 1건 선택) + open-window 만료 = skill/Orchestrator 가
#   poll 단계에서 수행 — 본 스크립트는 그 1건을 받아 옵션만 뽑는다.
#
# 입력: 코멘트 본문 = stdin 또는 $1(파일 경로).
# 출력/exit:
#   추출 성공 -> exit 0 + 옵션 식별자 1개 stdout (숫자 또는 대문자 1자)
#   추출 실패 -> exit 1 + "파싱 불가" stderr
#   입력 오류 -> exit 3 (파일 미존재)
#
# 인식 형태:
#   "1) jira 로" / "B. 그게…"          (옵션 미러 — compose 옵션 줄 복사 답변, 선두 식별자)
#   "답: 2" / "답변: 2" / "선택: B"   (한글 라벨 prefix; 전각 콜론 `답：2` 도 정규화 후 인식)
#   "option B" / "옵션 3"              (옵션 키워드)
#   "2" / "B"                          (단독 토큰 — 첫 줄이 옵션 토큰일 때만)
#
# NOTE (S3 defer): FIRST_LINE 우선순위 재배치(답변이 첫 줄이 아닌 경우의 본문 전체 탐색 강화)는
#   S3 robustness 로 미룬다 — 본 FIX 비대상. v1 은 답변 상단 가정(happy-path).
#
# ADR-061 §결정 1 — bash 우선(순수 패턴 추출).
set -euo pipefail

if [ "$#" -ge 1 ]; then
  if [ ! -f "$1" ]; then
    echo "parse-answer: 입력 파일 없음: $1" >&2
    exit 3
  fi
  BODY="$(cat -- "$1")"
else
  BODY="$(cat -)"
fi

# 첫 비어있지 않은 줄을 후보로 우선 사용(답변은 보통 상단).
FIRST_LINE="$(printf '%s\n' "$BODY" | grep -m1 -vE '^[[:space:]]*$' || true)"

extract() {
  local line="$1"

  # 전각 콜론(：U+FF1A, 3-byte UTF-8)을 ASCII `:` 로 정규화한다 — bracket 식 [:：] 안
  # 멀티바이트 char 매칭이 grep 에서 불안정해 `답：2` 가 파싱 실패하던 문제 수정 (FIX P1).
  line="$(printf '%s' "$line" | sed 's/：/:/g')"

  # (0) 옵션 미러: compose 가 `1) <텍스트>` 로 제시한 옵션 줄을 사용자가 그대로 복사 답변한 경우
  #     (예: `1) jira 로 가죠`). 줄 선두 옵션 토큰(식별자 + 닫는 구두점)을 채택한다 (FIX P1).
  #     라벨 prefix(1)·option 키워드(2)보다 앞서지 않도록, 단독토큰(3)과 동급의 선두 패턴으로 둔다.
  local opt
  opt="$(printf '%s' "$line" | grep -oE '^[[:space:]]*([0-9]+|[A-Za-z])[).:]' | head -n1 || true)"
  if [ -n "$opt" ]; then
    local otok
    otok="$(printf '%s' "$opt" | grep -oE '[0-9A-Za-z]+' | head -n1 || true)"
    if printf '%s' "$otok" | grep -qE '^[0-9]+$'; then printf '%s\n' "$otok"; return 0; fi
    if printf '%s' "$otok" | grep -qiE '^[A-Za-z]$'; then printf '%s\n' "$(printf '%s' "$otok" | tr '[:lower:]' '[:upper:]')"; return 0; fi
  fi

  # (1) 라벨 prefix: 답/답변/선택/결정 : 뒤 토큰 (전각 콜론은 위에서 ASCII 로 정규화됨)
  local m
  m="$(printf '%s' "$line" \
    | grep -oiE '(답변|답|선택|결정)[[:space:]]*[:：][[:space:]]*(option|옵션)?[[:space:]]*[0-9A-Za-z]+' \
    | head -n1 || true)"
  if [ -n "$m" ]; then
    # 마지막 토큰(영숫자) 추출
    local tok
    tok="$(printf '%s' "$m" | grep -oE '[0-9A-Za-z]+$' | head -n1 || true)"
    if printf '%s' "$tok" | grep -qE '^[0-9]+$'; then printf '%s\n' "$tok"; return 0; fi
    if printf '%s' "$tok" | grep -qiE '^[A-Za-z]$'; then printf '%s\n' "$(printf '%s' "$tok" | tr '[:lower:]' '[:upper:]')"; return 0; fi
  fi

  # (2) option/옵션 키워드 뒤 토큰
  m="$(printf '%s' "$line" \
    | grep -oiE '(option|옵션)[[:space:]]*[0-9A-Za-z]+' | head -n1 || true)"
  if [ -n "$m" ]; then
    local tok
    tok="$(printf '%s' "$m" | grep -oE '[0-9A-Za-z]+$' | head -n1 || true)"
    if printf '%s' "$tok" | grep -qE '^[0-9]+$'; then printf '%s\n' "$tok"; return 0; fi
    if printf '%s' "$tok" | grep -qiE '^[A-Za-z]$'; then printf '%s\n' "$(printf '%s' "$tok" | tr '[:lower:]' '[:upper:]')"; return 0; fi
  fi

  # (3) 단독 토큰: 줄 전체가 숫자 또는 영문 1자(앞뒤 구두점 허용)
  local trimmed
  trimmed="$(printf '%s' "$line" | sed -E 's/^[[:space:]]*//; s/[[:space:].)］】]*$//; s/^[(［【]*//')"
  if printf '%s' "$trimmed" | grep -qE '^[0-9]+$'; then printf '%s\n' "$trimmed"; return 0; fi
  if printf '%s' "$trimmed" | grep -qiE '^[A-Za-z]$'; then printf '%s\n' "$(printf '%s' "$trimmed" | tr '[:lower:]' '[:upper:]')"; return 0; fi

  return 1
}

# 첫 줄 우선, 실패 시 본문 전체에서 라벨 prefix 재탐색.
if [ -n "$FIRST_LINE" ] && extract "$FIRST_LINE"; then
  exit 0
fi

# 본문 전체에서 라벨/옵션 패턴이 어디든 있으면 그 첫 매치 줄로 재시도.
LABEL_LINE="$(printf '%s\n' "$BODY" | grep -m1 -iE '(답변|답|선택|결정)[[:space:]]*[:：]|(option|옵션)[[:space:]]*[0-9A-Za-z]' || true)"
if [ -n "$LABEL_LINE" ] && extract "$LABEL_LINE"; then
  exit 0
fi

echo "parse-answer: 파싱 불가 — 옵션 식별자(숫자/영문) 미검출" >&2
exit 1
