#!/usr/bin/env bash
# CFP-2459 Phase 2 — research-request-gate skill §8 Test Contract discriminating check
# 개발자 검증 helper(§8 prose contract 분기 완결성) — CI 미배선, AC-10/OOS-6 정합(mechanical lint 신설 아님)
# 검증 대상: research-request-gate skill body 의 corroboration 분기 명세 완결성
# Story §8 TC-1~TC-7 + AC-1/AC-5/A1-2 분기별 content-anchor grep 검증
# 산출물: content-anchor 기반 검사(line# 박제 금지, negative assertion 포함)
# exit 0: 전부 PASS / exit 1: 1+ 항목 FAIL
# NOTE: CI 워크플로 미배선 — 개발자/리뷰어 수동 실행용

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_FILE="${1:-$SCRIPT_DIR/../skills/research-request-gate/SKILL.md}"

# 파일 존재 확인
if [ ! -f "$SKILL_FILE" ]; then
  echo "FAIL: skill 파일 미발견: $SKILL_FILE" >&2
  exit 1
fi

PASS_COUNT=0
FAIL_COUNT=0

# 각 검사 항목별 함수
check_tc1_corroborated() {
  # TC-1: corroborated 분기 + "일치" + "진리 증명 아님"/"반증 부재" 경고 + [verified] 무검증 승격 금지
  if grep -q "corroborated" "$SKILL_FILE" && \
     grep -q "일치" "$SKILL_FILE" && \
     (grep -q "진리 증명 아님" "$SKILL_FILE" || grep -q "반증 부재" "$SKILL_FILE") && \
     grep -q "\[verified\]" "$SKILL_FILE"; then
    echo "PASS: TC-1 corroborated 분기 완결"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: TC-1 corroborated 분기 누락 — corroborated + 일치 + 진리경고 + [verified] 미검증 승격 금지 문구 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_tc2_divergent() {
  # TC-2: divergent 분기 + "verbatim" + "임의 채택" 금지
  if grep -q "divergent" "$SKILL_FILE" && \
     grep -q "verbatim" "$SKILL_FILE" && \
     grep -q "임의 채택" "$SKILL_FILE"; then
    echo "PASS: TC-2 divergent 분기 완결"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: TC-2 divergent 분기 누락 — divergent + verbatim(분기 병기) + 임의 채택 금지 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_tc3_single_source() {
  # TC-3: single-source + graceful degradation/"실패 아님" 취지
  if grep -q "single-source" "$SKILL_FILE" && \
     (grep -q "graceful degradation" "$SKILL_FILE" || grep -q "실패 아님" "$SKILL_FILE"); then
    echo "PASS: TC-3 single-source 분기 완결"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: TC-3 single-source 분기 누락 — single-source + graceful degradation/실패아님 취지 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_tc4_recency() {
  # TC-4: "변동성"(volatility) + "WebSearch" + "Codex" 보조 위계 + "동등 교차"(시점불변)
  if grep -q "변동성" "$SKILL_FILE" && \
     grep -q "WebSearch" "$SKILL_FILE" && \
     grep -q "Codex" "$SKILL_FILE" && \
     grep -q "동등 교차" "$SKILL_FILE"; then
    echo "PASS: TC-4 시점성/변동성 분기 완결"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: TC-4 시점성/변동성 분기 누락 — 변동성 + WebSearch + Codex 위계 + 동등교차 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_tc5_divergence_unresolved() {
  # TC-5: "abstention" + "추가조사" 강제 안 함(또는 자동 재실행 금지)
  if grep -q "abstention" "$SKILL_FILE" && \
     (grep -q "추가조사" "$SKILL_FILE" || grep -q "자동 재실행 금지" "$SKILL_FILE"); then
    echo "PASS: TC-5 divergence 미결 분기 완결"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: TC-5 divergence 미결 분기 누락 — abstention + 추가조사/자동재실행금지 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_tc6_divergent_vs_abstention() {
  # TC-6: "출처 부재"(abstention) ↔ "두 단정 충돌"/"둘 다 단정" 구분
  if grep -q "출처 부재" "$SKILL_FILE" && \
     (grep -q "두 단정 충돌" "$SKILL_FILE" || grep -q "둘 다 단정" "$SKILL_FILE"); then
    echo "PASS: TC-6 divergent ≠ abstention 구분 완결"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: TC-6 divergent ≠ abstention 구분 누락 — 출처부재(abstention) ↔ 두단정충돌 구분 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_tc7_semantic_equivalent() {
  # TC-7: "의미-동등"(semantic-equivalent) + drift 시 비교 무효
  if grep -q "의미-동등" "$SKILL_FILE" && \
     grep -q "semantic-equivalent" "$SKILL_FILE" && \
     grep -q "drift" "$SKILL_FILE"; then
    echo "PASS: TC-7 의미-동등 분기 완결"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: TC-7 의미-동등 분기 누락 — 의미-동등 + semantic-equivalent + drift 무효 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_ac5_no_hardcoded_cutoff() {
  # AC-5: 특정 cutoff 날짜 패턴이 skill 본문에 부재(negative assertion — discriminating)
  # 금지 패턴: 2024-09-30, 2024-05-31, 2025-12-01, Sep 30 2024, 등
  if grep -qE '(2024-09-30|2024-05-31|2025-12-01|Sep 30, 2024|September 30, 2024)' "$SKILL_FILE"; then
    echo "FAIL: AC-5 hardcoded cutoff 날짜 검출 — 방향성만 사용, 특정 날짜 값 박제 금지" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    echo "PASS: AC-5 cutoff 날짜 하드코딩 부재(negative assertion 검증)"
    PASS_COUNT=$((PASS_COUNT + 1))
  fi
}

check_ac1_four_stages() {
  # AC-1: 추상 단계 표 골격(request/gate/theater_check/execute/inject) 유지 +
  #       corroboration 이 별도 pipeline stage 로 승격되지 않음(= execute *내부* 서술).
  # discriminating: "## 절차 추상 단계" 표 블록만 slice 해 stage row(`...`) 를 검사.
  #   - 표 안 stage 이름이 request/gate/theater_check/execute/inject 만이면 PASS.
  #   - corroborat*/secondary* 등 신규 stage row 가 표에 등재되면 5번째 단계 신설(위배).
  #   - §4.1/§5.1 산문·status 표 언급은 추상 단계 표 *밖*이라 위배 아님.
  local stage_block stage_names
  stage_block="$(awk '/^## 절차 추상 단계/{f=1} f&&/^---/{if(seen)exit} f{print; if(/^\|/)seen=1}' "$SKILL_FILE")"
  # 추상 단계 표 첫 컬럼의 백틱 stage 이름만 추출(헤더·구분선 제외)
  stage_names="$(printf '%s\n' "$stage_block" | grep -oE '^\| `[^`]+`' | sed -E 's/^\| `([^`]+)`/\1/' | sort -u | tr '\n' ' ' || true)"
  if printf '%s\n' "$stage_block" | grep -q '`request`' && \
     printf '%s\n' "$stage_block" | grep -q '`execute`' && \
     printf '%s\n' "$stage_block" | grep -q '`inject`'; then
    # 추출된 stage 이름 중 허용 집합(request/gate/theater_check/execute/inject) 밖이 있으면 위배
    if printf '%s\n' "$stage_names" | grep -qE '(corroborat|secondary|2차)'; then
      echo "FAIL: AC-1 위배 — corroboration 이 별도 pipeline stage 로 승격(execute 내부여야 함). 표 stage=[$stage_names]" >&2
      FAIL_COUNT=$((FAIL_COUNT + 1))
    else
      echo "PASS: AC-1 추상 단계 골격 완결(stage=[$stage_names], corroboration 별도 stage 미승격)"
      PASS_COUNT=$((PASS_COUNT + 1))
    fi
  else
    echo "FAIL: AC-1 추상 단계 골격 누락 — 추상 단계 표에 request/execute/inject stage row 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

check_a12_disjoint_layer() {
  # A1-2: "verify 대체 아님"/"verify 아님" + "외부 web 사실" + "file-Read-verify" 면제
  if (grep -q "verify 대체 아님" "$SKILL_FILE" || grep -q "verify 아님" "$SKILL_FILE") && \
     grep -q "외부 web 사실" "$SKILL_FILE"; then
    echo "PASS: A1-2 disjoint layer 분기 완결"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL: A1-2 disjoint layer 분기 누락 — verify 대체아님 + 외부web사실 필요" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

# 전체 검사 실행
check_tc1_corroborated
check_tc2_divergent
check_tc3_single_source
check_tc4_recency
check_tc5_divergence_unresolved
check_tc6_divergent_vs_abstention
check_tc7_semantic_equivalent
check_ac5_no_hardcoded_cutoff
check_ac1_four_stages
check_a12_disjoint_layer

# 결과 요약
echo ""
echo "=== 검사 요약 ==="
echo "PASS: $PASS_COUNT / FAIL: $FAIL_COUNT"

if [ $FAIL_COUNT -eq 0 ]; then
  echo "결론: 모든 §8 Test Contract 분기 완결 (PASS)"
  exit 0
else
  echo "결론: $FAIL_COUNT 개 항목 FAIL — 재편집 필요" >&2
  exit 1
fi
