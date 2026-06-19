#!/usr/bin/env bash
# CFP-2369 — Reusability duplication-ratio 측정 (warning-tier, non-blocking).
#
# CFP-2364 Amendment 13 (ADR-042) 의 (d) Reusability 축 측정 연동 Phase-2 mechanical wire.
# CFP-2364 = Phase-1 declarative (RefactorAgent 가 before 신호 emit 하나 자동 측정 deferred).
# 본 스크립트 = 그 후속 carrier — duplication ratio 를 mechanical 산출해 warning emit.
# ADR 근거: ADR-042 Amendment 14 (CFP-2364 측정 연동 deferred → mechanical wire) + ADR-060
# (evidence-checks-registry framework, warning tier).
#
# **warning-tier 불변**: 항상 exit 0 (비차단). 측정 결과는 GitHub Actions warning 마커로만 노출.
# blocking 승격은 evidence 누적 후 별 CFP — 현 단계는 신호 제공까지 (advisory).
# repo-level 분해 mechanical gate 는 out-of-scope (advisory 유지 — Amendment 14 §결정).
#
# detector 계약:
#   - 환경변수 DUPLICATION_TOOL = "target dir 를 $1 로 받아 중복 백분율(float, 예 4.2)을
#     stdout 1줄로 출력하는 command". 설정 시 그대로 호출.
#   - 미설정 시 default = 내장 jscpd 호출 (npx --yes jscpd ... --reporters json) 후 json 의
#     statistics.total.percentage 추출 (jq → python → grep fallback).
#
# 환경변수:
#   DUPLICATION_TOOL       — detector command override (위 계약)
#   DUPLICATION_THRESHOLD  — 경고 임계 백분율 (default 5.0)
#   DUPLICATION_TARGET     — 측정 target dir (인자 $1 > env > default src|. 순)
#
# graceful degradation (전부 exit 0):
#   ① target source 부재         → 출력 없이 exit 0
#   ② detector 도구 불가          → ::warning::detector unavailable, skipped + exit 0
#   ③ ratio ≤ threshold          → 출력 없이 exit 0
#   ④ ratio > threshold          → ::warning::... + exit 0
#
# wrapper-self: src 부재 (declarative-only) → ① graceful exit 0 (CI 통과).
#
# Usage:
#   bash scripts/check-duplication-ratio.sh [target_dir]
#   DUPLICATION_THRESHOLD=3.0 bash scripts/check-duplication-ratio.sh src
#   DUPLICATION_TOOL='my-detector' bash scripts/check-duplication-ratio.sh .
#
# Exit code: 0 (always — warning-tier, non-blocking)
#
set -euo pipefail

THRESHOLD="${DUPLICATION_THRESHOLD:-5.0}"

# target dir 결정: 인자 $1 > env DUPLICATION_TARGET > default.
# default = src 있으면 src. src 부재 + 명시 target 0 = "측정할 source 없음" → graceful exit 0.
# (wrapper-self = declarative-only repo 라 src 부재 → 암묵 whole-repo(.) scan 안 함, 조용히 통과.)
# explicit target("." 포함) 은 그대로 존중.
TARGET="${1:-${DUPLICATION_TARGET:-}}"
if [ -z "$TARGET" ]; then
  if [ -d src ]; then
    TARGET="src"
  else
    # ① target source 부재 (default 해소 실패) → 조용히 exit 0
    exit 0
  fi
fi

# ① 명시 target 이 dir 아님 → 조용히 exit 0
if [ ! -d "$TARGET" ]; then
  exit 0
fi

# float 비교 헬퍼 (awk — bash 산술은 정수 only). a > b 면 0 반환.
gt() {
  awk -v a="$1" -v b="$2" 'BEGIN { exit !(a > b) }'
}

# detector 실행 → ratio (float, stdout 1줄) 반환. 불가 시 비어 있는 문자열 반환.
measure_ratio() {
  local target="$1"

  # detector override 가 있으면 그대로 호출
  if [ -n "${DUPLICATION_TOOL:-}" ]; then
    # shellcheck disable=SC2086
    $DUPLICATION_TOOL "$target" 2>/dev/null || true
    return 0
  fi

  # default detector = jscpd (node/npx 필요)
  if ! command -v npx >/dev/null 2>&1; then
    return 0  # node/npx 부재 → 빈 문자열 (caller 가 ② unavailable 처리)
  fi

  local tmp
  tmp="$(mktemp -d 2>/dev/null || echo "")"
  [ -z "$tmp" ] && return 0

  # jscpd json reporter — output dir 에 jscpd-report.json 생성
  if ! npx --yes jscpd "$target" --reporters json --silent --output "$tmp" >/dev/null 2>&1; then
    rm -rf "$tmp" 2>/dev/null || true
    return 0  # jscpd 실행 실패 (네트워크 / 미설치) → 빈 문자열 → ② unavailable
  fi

  local report="$tmp/jscpd-report.json"
  if [ ! -f "$report" ]; then
    rm -rf "$tmp" 2>/dev/null || true
    return 0
  fi

  # statistics.total.percentage 추출 — jq → python → grep fallback
  local pct=""
  if command -v jq >/dev/null 2>&1; then
    pct="$(jq -r '.statistics.total.percentage // empty' "$report" 2>/dev/null || true)"
  fi
  if [ -z "$pct" ] && command -v python3 >/dev/null 2>&1; then
    pct="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["statistics"]["total"]["percentage"])' "$report" 2>/dev/null || true)"
  fi
  if [ -z "$pct" ] && command -v python >/dev/null 2>&1; then
    pct="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["statistics"]["total"]["percentage"])' "$report" 2>/dev/null || true)"
  fi
  if [ -z "$pct" ]; then
    # grep fallback — "percentage": 4.2 형태 첫 매치
    pct="$(grep -o '"percentage"[[:space:]]*:[[:space:]]*[0-9.]*' "$report" 2>/dev/null | head -1 | grep -o '[0-9.]*$' || true)"
  fi

  rm -rf "$tmp" 2>/dev/null || true
  printf '%s' "$pct"
}

RATIO="$(measure_ratio "$TARGET" | head -1 | tr -d '[:space:]')"

# ② detector 불가 (빈 결과 또는 숫자 아님) → unavailable warning + exit 0
if [ -z "$RATIO" ] || ! printf '%s' "$RATIO" | grep -Eq '^[0-9]+(\.[0-9]+)?$'; then
  echo "::warning::duplication detector unavailable, skipped (재사용성: DUPLICATION_TOOL 미설정 + jscpd 구동 불가 — RefactorAgent (d) before 신호 수동 대조 유지)"
  exit 0
fi

# ③/④ threshold 비교 — ratio > threshold 면 warning, 이하면 무출력 (경계값 == 은 ≤ 처리 = no warning)
if gt "$RATIO" "$THRESHOLD"; then
  echo "::warning::duplication ratio ${RATIO}% > threshold ${THRESHOLD}% (재사용성: 공통 추출 검토 — RefactorAgent (d))"
fi

# warning-tier — 항상 exit 0
exit 0
