#!/usr/bin/env bash
# CFP-2361 PS4 (신설) / CFP-2613 G2 (blocking 승격) — Operational outcome-signal + 지속-liveness
# 선언 fail-closed lint (표면 A, ADR-148 §결정4/6).
#
# ADR-014 Amendment 7 §7.4.7 + ADR-015 Amendment 1 §8.5.1 + ADR-148 (G2 표면 A):
# - operational:true Story 는 daemon_type 선언 필수 (누락=FAIL, silent default 금지, §결정6 ①).
# - daemon_type == long_running_daemon ∧ operational:true → 아래 선언 presence 를 blocking 강제:
#     ① terminal downstream sink  ② monotone progress metric  ③ 발현조건 임계 (§7.4.7 3요소)
#     ④ sink_probes[] (liveness 판정 유형 — HTTP-200 default 대체 금지, AC-3)
#     ⑤ fake-source(대상 데몬 우회) 선언 금지 (AC-5)
#     ⑥ "완전 봉인" hard-claim 금지 = 정직 천장 ack 필수 (AC-9)
# - daemon_type ∈ {request_response_service, batch_job, cli, none} → 기존 warning-tier 유지
#     (비-데몬 HTTP 서비스 mass-breakage 회피, §결정6). 신규 blocking 미적용.
# - operational:false / 미선언 → skip.
#
# **검사 방식 (literal-term presence heuristic + review anchor)**: 휴리스틱 grep — 선언 존재만
#   확인. 완전 자동분류 불가 영역 = review anchor (§결정6 ③, 정직 천장). false-positive 최소화.
#   wrapper-self: operational:true Story 0개 (§2) → 전 Story skip → graceful exit 0.
#
# **shadow-first (ADR-148 §결정10)**: 본 lint = workflow blocking-tier(exit 1) 이나
#   branch-protection required contexts 편입은 사용자 결정으로 유보 (required 미등록).
#   등록 = 후속 CFP (G1 등록순서 의존). 본 스크립트는 required 여부와 무관 — 발견 시 exit 1.
#
# Exit code: 0 (위반 없음 / 비적용) · 1 (long_running_daemon 선언 위반 = blocking FAIL)
# Output: ::error:: (blocking) / ::warning:: (non-fatal) markers to GitHub Actions.
#
# Usage:
#   bash scripts/check-operational-outcome-signal.sh [REPO_ROOT]
set -euo pipefail

REPO_ROOT="${1:-.}"
cd "$REPO_ROOT"

# Early guard: docs/stories 부재 (wrapper-self or non-consumer) → exit 0
[ -d docs/stories ] || exit 0

STORY_FILES=$(find docs/stories -name "*.md" 2>/dev/null || true)
[ -z "$STORY_FILES" ] && exit 0

WARNINGS=0
ERRORS=0

# daemon_type 값 추출 (yaml `daemon_type: X` / prose `daemon_type == X` / json `"daemon_type": "X"`).
# 값이 daemon_type 뒤 separator(: 또는 =) 바로 다음일 때만 매치 → enum 문서화 오탐 최소화.
detect_daemon_type() {
  local f="$1"
  grep -oiE 'daemon_type[[:space:]"]*[:=]+[[:space:]"]*(long_running_daemon|request_response_service|batch_job|cli|none)' "$f" 2>/dev/null \
    | grep -oiE '(long_running_daemon|request_response_service|batch_job|cli|none)' \
    | head -1 \
    | tr '[:upper:]' '[:lower:]' \
    || true
}

for story_file in $STORY_FILES; do
  # operational:true 스코핑 — 아니면 skip.
  if ! grep -qE "operational:[[:space:]]*true" "$story_file" 2>/dev/null; then
    continue
  fi

  daemon_type="$(detect_daemon_type "$story_file")"

  # ── daemon_type presence fail-closed (§결정6 ①, silent default 금지) ──
  if [ -z "$daemon_type" ]; then
    echo "::error file=$story_file::operational:true Story 는 daemon_type 선언 필수 (enum: long_running_daemon|request_response_service|batch_job|cli|none). 미선언=FAIL (silent default 금지, ADR-148 §결정6)"
    ERRORS=$((ERRORS+1))
    continue
  fi

  if [ "$daemon_type" != "long_running_daemon" ]; then
    # 비-long_running_daemon (request_response_service/batch_job/cli/none) — 기존 warning-tier 유지.
    # 신규 blocking 미적용 (mass-breakage 회피, §결정6). 3요소 + soak 도출 = 기존 warning 동작 전면 보존.
    if ! grep -q "terminal downstream sink" "$story_file" 2>/dev/null && \
       ! grep -q "sink 경로" "$story_file" 2>/dev/null; then
      echo "::warning file=$story_file::§7.4.7 outcome-signal ① terminal downstream sink 미선언 (operational:true, daemon_type=$daemon_type — warning)"
      WARNINGS=$((WARNINGS+1))
    fi
    if ! grep -q "monotone progress metric" "$story_file" 2>/dev/null && \
       ! grep -q "단조 증가 metric" "$story_file" 2>/dev/null; then
      echo "::warning file=$story_file::§7.4.7 outcome-signal ② monotone progress metric 미선언 (operational:true, daemon_type=$daemon_type — warning)"
      WARNINGS=$((WARNINGS+1))
    fi
    if ! grep -q "발현조건 임계" "$story_file" 2>/dev/null && \
       ! grep -q "manifestation-derived" "$story_file" 2>/dev/null; then
      echo "::warning file=$story_file::§7.4.7 outcome-signal ③ 발현조건 임계 미선언 (operational:true, daemon_type=$daemon_type — warning)"
      WARNINGS=$((WARNINGS+1))
    fi
    # §8.5.1 soak 도출 (accumulation/lifetime-class 기재 시) — 비-데몬은 warning 유지 (기존 동작).
    if grep -q "accumulation" "$story_file" 2>/dev/null || \
       grep -q "lifetime-class" "$story_file" 2>/dev/null || \
       grep -q "장기-수명" "$story_file" 2>/dev/null; then
      if ! grep -q "manifestation-derived" "$story_file" 2>/dev/null && \
         ! grep -q "발현조건 기반 도출" "$story_file" 2>/dev/null && \
         ! grep -q "duration floor" "$story_file" 2>/dev/null && \
         ! grep -q "최소 지속" "$story_file" 2>/dev/null; then
        echo "::warning file=$story_file::§8.5.1 soak 구동 종점 (manifestation-derived 또는 duration floor) 도출 부재 (accumulation/lifetime-class 기재 시 — warning)"
        WARNINGS=$((WARNINGS+1))
      fi
    fi
    continue
  fi

  # ── daemon_type == long_running_daemon → blocking 선언 fail-closed (ADR-148 §결정4) ──

  # ① terminal downstream sink
  if ! grep -q "terminal downstream sink" "$story_file" 2>/dev/null && \
     ! grep -q "sink 경로" "$story_file" 2>/dev/null; then
    echo "::error file=$story_file::§7.4.7 ① terminal downstream sink 미선언 (long_running_daemon 필수, ADR-148 §결정4)"
    ERRORS=$((ERRORS+1))
  fi

  # ② monotone progress metric
  if ! grep -q "monotone progress metric" "$story_file" 2>/dev/null && \
     ! grep -q "단조 증가 metric" "$story_file" 2>/dev/null; then
    echo "::error file=$story_file::§7.4.7 ② monotone progress metric 미선언 (long_running_daemon 필수, ADR-148 §결정4)"
    ERRORS=$((ERRORS+1))
  fi

  # ③ 발현조건 임계
  if ! grep -q "발현조건 임계" "$story_file" 2>/dev/null && \
     ! grep -q "manifestation-derived" "$story_file" 2>/dev/null; then
    echo "::error file=$story_file::§7.4.7 ③ 발현조건 임계 미선언 (long_running_daemon 필수, ADR-148 §결정4)"
    ERRORS=$((ERRORS+1))
  fi

  # ④ sink_probes[] presence (liveness 판정 유형 선언 — HTTP-200 대체 금지, AC-3)
  if ! grep -q "sink_probes" "$story_file" 2>/dev/null; then
    echo "::error file=$story_file::sink_probes[] 미선언 (long_running_daemon liveness 판정 유형 — HTTP-200 default 대체 금지, ADR-148 AC-3/§결정6)"
    ERRORS=$((ERRORS+1))
  fi

  # ⑤ fake-source(대상 데몬 우회) 선언 금지 (AC-5) — 부정 문맥(금지/아님) 라인은 제외.
  fake_hit="$(grep -inE 'fake[-_]source|MCTRADER_SOURCE[[:space:]]*=[[:space:]]*fake' "$story_file" 2>/dev/null \
              | grep -viE '금지|아님|배제|없음|forbidden|prohibit|not[[:space:]]allow' || true)"
  if [ -n "$fake_hit" ]; then
    echo "::error file=$story_file::fake-source(대상 데몬 자신 우회) 선언 발견 = FAIL (실 코드경로 행사 필수, ADR-148 AC-5). 위반 라인: ${fake_hit%%$'\n'*}"
    ERRORS=$((ERRORS+1))
  fi

  # ⑥ 정직 천장 (AC-9) — "완전 봉인" hard-claim 은 정직 ack 동반 필수.
  if grep -qE '완전 봉인' "$story_file" 2>/dev/null; then
    if ! grep -qE '증명 불가|무한 미래|봉인 아님|완전 봉인 아님|완전 봉인.{0,12}금지|honest[_ ]?ceiling|honest_ceiling_ack' "$story_file" 2>/dev/null; then
      echo "::error file=$story_file::\"완전 봉인\" hard-claim 발견 (정직 천장 ack 부재) = 검사연극 = FAIL (ADR-148 AC-9/INV-D6). \"증명 불가/봉인 아님\" 정직 구분 필수"
      ERRORS=$((ERRORS+1))
    fi
  fi

  # ⑦ soak 도출 종점 (§8.5.1 accumulation/lifetime-class 기재 시) — long_running_daemon 은 error.
  if grep -q "accumulation" "$story_file" 2>/dev/null || \
     grep -q "lifetime-class" "$story_file" 2>/dev/null || \
     grep -q "장기-수명" "$story_file" 2>/dev/null; then
    if ! grep -q "manifestation-derived" "$story_file" 2>/dev/null && \
       ! grep -q "발현조건 기반 도출" "$story_file" 2>/dev/null && \
       ! grep -q "duration floor" "$story_file" 2>/dev/null && \
       ! grep -q "최소 지속" "$story_file" 2>/dev/null; then
      echo "::error file=$story_file::§8.5.1 soak 구동 종점 (manifestation-derived 또는 duration floor) 도출 부재 (long_running_daemon accumulation/lifetime-class 필수, ADR-148 §결정7)"
      ERRORS=$((ERRORS+1))
    fi
  fi
done

# blocking: long_running_daemon 선언 위반 존재 시 exit 1.
if [ "$ERRORS" -gt 0 ]; then
  echo "::error::operational outcome-signal / 지속-liveness 선언 위반 ${ERRORS}건 (long_running_daemon fail-closed, ADR-148 표면 A) — blocking FAIL"
  exit 1
fi

exit 0
