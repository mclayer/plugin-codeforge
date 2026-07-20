#!/usr/bin/env bash
# CFP-2772 Phase 2 (#) — Arc B-2: per-branch liveness heartbeat 코멘트 본문 포맷터 (write-only)
# 설계 SSOT: ADR-164 §결정 3(마이크로포맷) / §결정 5(seq·state 필드) / §결정 8(bounded 3-tuple 구성)
#   + internal-docs change-plan cfp-2772 §4.2(microformat) / §11.7(포맷 backward-compat).
#
# 역할: progress-format.sh 의 형제(sibling) — Arc B-1(MIRROR 진행미러)와 같은 control project 에
#   공존하는 Arc B-2(HEARTBEAT liveness) 코멘트 본문을 결정론적으로 포맷한다. 외부 watchdog
#   (scripts/lib/check_branch_liveness.py)가 이 본문을 파싱해 3-state(fresh/stalled/unknown)를
#   판정한다. 결정론적 순수 텍스트 조립만 수행 — MCP/Jira 호출 없음(post 는 skill/Orchestrator 담당).
#
# ---- SSOT + versioning ----
#   본 스크립트 = heartbeat comment-body 마이크로포맷의 단일 원본(SSOT). 실행가능 SSOT 이므로
#   emit(emit_branch_heartbeat.py)와 parse(check_branch_liveness.py)가 이 포맷을 유일 계약으로 삼는다.
#   **포맷 변경 = ADR-164 amendment 의무**(별도 SemVer 트랙 불요 — change-plan §11.7). split-brain 방지
#   위해 emit/parse 는 이 포맷 문자열을 복제하지 않고 본 스크립트를 호출(reuse-before-write, ADR-140).
#
# ---- SENTINEL SSOT 정합 (byte-동일 의무) ----
#   선두 sentinel 은 scripts/jira-channel/echo-guard.sh 의 CF_ORCH_SENTINEL 상수와 **byte-동일**해야
#   한다(불일치 시 Arc A echo-guard 가 heartbeat 코멘트를 "사용자 답"으로 재섭취 — self-echo,
#   그리고 watchdog 파서가 sentinel 필터를 통과 못 함). echo-guard.sh = sentinel 단일 원본.
readonly CF_ORCH_SENTINEL='⟦cf-orch⟧'
#
# ---- bounded 3-tuple construction (ADR-164 §결정 8 — construction-time 보장) ----
#   liveness heartbeat egress 의 coarse invariant 는 scan-time 희망이 아니라 construction-time 보장:
#   formatter 가 오직 (branch-slug[a-z0-9-], iso8601-ts, monotonic-int) bounded 3-tuple + 통제어휘
#   (story KEY, lane 토큰, state enum)만 수용한다 → 경로·이메일·자격증명 인코딩 STRUCTURALLY 불능.
#   free-form 은 미수용(위반 → exit 3). deny-scan.sh 는 email/RRN 미커버(§결정 8)이므로 유일 방어로
#   삼지 않으며, 본 construction-time bound 가 1차 방어(deny-scan = backstop).
#
# 입력(위치 인자):
#   $1 = branch_key   (필수)  — git ref 파생 slug, 검증 ^[a-z0-9-]+$
#   $2 = seq          (필수)  — per-branch strictly-monotonic int, 검증 ^[0-9]+$
#   $3 = story        (필수)  — Story KEY (public non-sensitive 상관 ID), 검증 ^[A-Za-z0-9._-]+$
#   $4 = lane         (필수)  — 통제 lane 토큰(한글 허용), forbidden 문자(@:=\/ 공백/제어) 미수용
#   $5 = ts           (선택)  — UTC ISO8601, 기본값 = date -u +%Y-%m-%dT%H:%M:%SZ, 검증 아래
#   $6 = state_tag    (선택)  — 기본 active, 허용 active|waiting-external|idle-yield|waiting-external:<reason>
#                               (<reason> = [a-z0-9-]+). state 필드 = §결정 5 heartbeat record 필드로
#                               watchdog D4 idle-relaxation(§결정 6)이 소비.
#
# 출력/exit:
#   성공 -> exit 0 + 단일 라인 stdout:
#     ⟦cf-orch⟧ HEARTBEAT branch=<branch> seq=<seq> story=<story> lane=<lane> ts=<ts> state=<state> — alive
#   인자/검증 오류 -> exit 3 + stderr (필수 인자 누락 / bounded 3-tuple 위반 / free-form / state enum 위반)
#
# ADR-061 §결정 1 — bash 우선(순수 텍스트 조립·검증). Windows-safety: LC_ALL=C.UTF-8, \n 개행.
set -euo pipefail
export LC_ALL="${LC_ALL:-C.UTF-8}"

BRANCH_KEY="${1:-}"
SEQ="${2:-}"
STORY="${3:-}"
LANE="${4:-}"
TS="${5:-}"
STATE="${6:-active}"

# ---- 필수 인자 존재 검사 ----
if [ -z "$BRANCH_KEY" ]; then
  echo "heartbeat-format: branch_key 인자(\$1) 누락" >&2
  exit 3
fi
if [ -z "$SEQ" ]; then
  echo "heartbeat-format: seq 인자(\$2) 누락" >&2
  exit 3
fi
if [ -z "$STORY" ]; then
  echo "heartbeat-format: story 인자(\$3) 누락" >&2
  exit 3
fi
if [ -z "$LANE" ]; then
  echo "heartbeat-format: lane 인자(\$4) 누락" >&2
  exit 3
fi

# ---- ts 기본값 (UTC ISO8601) ----
if [ -z "$TS" ]; then
  TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi

# ---- bounded 3-tuple 검증 (branch_key / seq / ts) — 위반 시 exit 3 ----
# grep 는 LC_ALL=C 로 바이트 단위 앵커 매칭(로케일-독립, Windows Git Bash 안전).
if ! printf '%s' "$BRANCH_KEY" | LC_ALL=C grep -qE '^[a-z0-9-]+$'; then
  echo "heartbeat-format: branch_key 위반 — ^[a-z0-9-]+$ 아님: '${BRANCH_KEY}' (free-form 미수용)" >&2
  exit 3
fi
if [ "${#BRANCH_KEY}" -gt 200 ]; then
  echo "heartbeat-format: branch_key 길이 초과(>200)" >&2
  exit 3
fi
if ! printf '%s' "$SEQ" | LC_ALL=C grep -qE '^[0-9]+$'; then
  echo "heartbeat-format: seq 위반 — ^[0-9]+$ 아님: '${SEQ}'" >&2
  exit 3
fi
if [ "${#SEQ}" -gt 18 ]; then
  echo "heartbeat-format: seq 자릿수 초과(>18)" >&2
  exit 3
fi
if ! printf '%s' "$TS" | LC_ALL=C grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$'; then
  echo "heartbeat-format: ts 위반 — ISO8601 ^YYYY-MM-DDTHH:MM:SSZ$ 아님: '${TS}'" >&2
  exit 3
fi

# ---- story 검증 (KEY-like allowlist — 경로/이메일/free-form 구조적 차단) ----
if ! printf '%s' "$STORY" | LC_ALL=C grep -qE '^[A-Za-z0-9._-]+$'; then
  echo "heartbeat-format: story 위반 — ^[A-Za-z0-9._-]+$ 아님: '${STORY}' (free-form 미수용)" >&2
  exit 3
fi
if [ "${#STORY}" -gt 64 ]; then
  echo "heartbeat-format: story 길이 초과(>64)" >&2
  exit 3
fi

# ---- lane 검증 (한글 통제어휘 허용 + forbidden ASCII 문자 denylist) ----
# lane 은 한글 lane 명(구현/설계리뷰/보안테스트 …)을 허용해야 하므로 순수 allowlist 대신,
# 로케일-독립(LC_ALL=C) ASCII forbidden 문자(@:=\/ 공백/제어)만 차단한다. 한글 UTF-8 바이트(>=0x80)는
# 이 ASCII 클래스 어디에도 걸리지 않아 안전 통과, email(@)/경로(/,\,:)/필드주입(=,공백)은 구조적 차단.
if printf '%s' "$LANE" | LC_ALL=C grep -qE '[[:space:][:cntrl:]@:=\\/]'; then
  echo "heartbeat-format: lane 위반 — forbidden 문자(공백/제어/@:=\\/) 포함: '${LANE}' (free-form 미수용)" >&2
  exit 3
fi
if [ "${#LANE}" -gt 64 ]; then
  echo "heartbeat-format: lane 길이 초과(>64)" >&2
  exit 3
fi

# ---- state_tag 검증 (enum + waiting-external:<reason>) ----
if ! printf '%s' "$STATE" | LC_ALL=C grep -qE '^(active|idle-yield|waiting-external(:[a-z0-9-]+)?)$'; then
  echo "heartbeat-format: state 위반 — active|waiting-external[:<reason>]|idle-yield 아님: '${STATE}'" >&2
  exit 3
fi

# ---- 본문 조립 (sentinel 선두 + HEARTBEAT 토큰 — echo-guard 정합 + MIRROR 분별) ----
# 형식: ⟦cf-orch⟧ HEARTBEAT branch=<branch> seq=<seq> story=<story> lane=<lane> ts=<ts> state=<state> — alive
#   HEARTBEAT 토큰 = Arc B-1(MIRROR)와 분별(watchdog 파서가 HEARTBEAT 만 골라냄).
#   '— alive' = em-dash(U+2014) — progress-format.sh 형제 스타일 정합.
printf '%s HEARTBEAT branch=%s seq=%s story=%s lane=%s ts=%s state=%s — alive\n' \
  "$CF_ORCH_SENTINEL" "$BRANCH_KEY" "$SEQ" "$STORY" "$LANE" "$TS" "$STATE"

exit 0
