#!/usr/bin/env bash
# CFP-2285 S3 (#2289) — Jira 결정 채널 echo-guard (self-echo 루프 차단)
# 인용 출처: ADR-099 Amendment 1 §A1-3 (first-valid-immutable / author 비신뢰).
#   PoC 실측: MCP addCommentToJiraIssue 는 사용자 본인 계정으로 write 라 코멘트 author 로
#   "orchestrator 가 쓴 코멘트" vs "사용자 답변" 을 구분할 수 없다(author 비신뢰, §A1-3).
#   따라서 echo-guard = **내용 마커**(identity 아님): orchestrator 가 쓰는 모든 코멘트
#   (결정 post / 세션답 mirror / PROCESSED 마커)에 distinctive sentinel 을 박고,
#   폴러가 그 sentinel 포함 코멘트를 답변 후보에서 제외해 자기 답 재섭취(self-echo)를 막는다.
#
#   결정론적 순수 텍스트 처리만 수행한다(MCP 호출 없음 — MCP post/poll 은 skill/Orchestrator 담당).
#
# ---- SENTINEL SSOT ----
#   본 상수가 sentinel 의 단일 원본(SSOT)이다. skills/jira-decision-channel/SKILL.md 의
#   post(§3) / mirror(§6) / PROCESSED 마커(dedup) 본문 선두에 박는 sentinel 과 **byte-동일**해야
#   한다(불일치 시 echo-guard 가 orchestrator 코멘트를 못 걸러 self-echo 루프 발생).
#   distinctive 토큰 — 사용자 평문 답변에 자연 등장하지 않는 형태를 고른다.
readonly CF_ORCH_SENTINEL='⟦cf-orch⟧'
#
# 입력: 코멘트 본문 = stdin 또는 $1(파일 경로).
# 출력/exit:
#   sentinel 이 본문 **선두**(선행 공백/개행 허용) -> exit 0  ("skip" — 답변 후보에서 제외)
#   sentinel 미포함 또는 선두 아님(본문 중간만)     -> exit 1  ("candidate" — 답변 후보로 유지)
#   입력 오류(빈 입력 / 파일 미존재)               -> exit 3
#
# NOTE: exit 0 = "이 코멘트는 건너뛰어라(skip)" 신호다. clean/pass 의미가 아님에 주의 —
#   deny-scan.sh(exit 0=clean) 와 의미축이 다르다. 폴러는 exit 1(candidate)만 답변으로 채택한다.
#
# ADR-061 §결정 1 — bash 우선(복잡 로직 아님, 순수 부분문자열 매칭).
set -euo pipefail

# ---- 입력 로드 (stdin | $1 파일) ----
if [ "$#" -ge 1 ]; then
  if [ ! -f "$1" ]; then
    echo "echo-guard: 입력 파일 없음: $1" >&2
    exit 3
  fi
  BODY="$(cat -- "$1")"
else
  BODY="$(cat -)"
fi

# 빈 입력(공백만 포함 포함) = 입력 오류. 답변 후보로도 skip 대상으로도 판정 불가.
if printf '%s' "$BODY" | grep -qE '[^[:space:]]'; then
  :
else
  echo "echo-guard: 빈 입력 — 판정 불가" >&2
  exit 3
fi

# ---- sentinel 선두 앵커 매칭 (P2-3 — doc-impl 정합) ----
# orchestrator 는 모든 코멘트(post/mirror/PROCESSED)의 본문 **선두**에 sentinel 을 박는다
# (SKILL.md 계약 — §3 post / §6 mirror / §7(e) PROCESSED 모두 "선두 sentinel"). 따라서
# 위치무관 substring(grep -qF) 이 아니라 **선두 앵커**로 매칭한다 — user 답변 본문 *중간*에
# sentinel 이 우발/인용으로 등장해도(예: "답 ⟦cf-orch⟧ 2") candidate 로 유지해 false-skip 을 막는다.
# sentinel(⟦cf-orch⟧)에 정규식 메타문자가 없어 ERE 에서 리터럴로 안전하나, 향후 sentinel 에 메타가
# 추가될 가능성에 대비해 선두 검사는 메타 비의존인 [[ == ⟦cf-orch⟧* ]] glob 으로 한다(앞 공백 trim 후).
# 선행 공백/개행 허용: BODY 앞쪽 whitespace 를 제거한 뒤 sentinel 로 시작하는지 검사한다.
LEADING_TRIMMED="${BODY#"${BODY%%[![:space:]]*}"}"   # 선두 공백류 제거 (POSIX parameter expansion)
if [[ "$LEADING_TRIMMED" == "$CF_ORCH_SENTINEL"* ]]; then
  # orchestrator 가 작성한 코멘트(post/mirror/PROCESSED) → 답변 후보에서 제외(skip).
  exit 0
fi

# sentinel 이 선두가 아님(미포함 또는 본문 중간만) → user 가 작성한 답변 후보.
exit 1
