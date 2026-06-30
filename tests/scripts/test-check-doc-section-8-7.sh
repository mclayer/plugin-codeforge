#!/usr/bin/env bash
# tests/scripts/test-check-doc-section-8-7.sh
# CFP-2505 Phase 2 — Discriminating self-test for §8.7 doc-section lint (ADR-136 결정10).
#
# DeveloperAgent 의 scripts/lib/check_doc_section_schema.py check_section_8_7() 검증.
# 선례 = 기존 §8.5 lint(check_section_8_5) 동작 방식 (동형).
#
# check_section_8_7() 동작 (검증됨, scripts/lib/check_doc_section_schema.py):
#  - §8.7 헤딩 부재 → 무검사(return []). §8.6 gap 무관(§8.7 헤딩만 트리거).
#  - §8.7 헤딩 존재 + §8.7.0 헤딩 부재 → fail.
#  - §8.7.0 표 4 행(CSS/SCSS 파일 변경 / 컴포넌트 변경 / 스타일 토큰/테마 변경 / layout-affecting 속성 변경)
#    Y/N 미파싱 → fail.
#  - 1+ Y → §8.7.1 render-truth 본문 헤딩 필수 (부재 시 fail).
#  - 4 N → §8.7.x N/A 헤딩 + substantive reason("N/A — " + 30자 이상) 필수.
#
# ── CWD 의무 (CFP-2449 gotcha) ────────────────────────────────────────────────
#  check_doc_section_schema.py 는 CWD-상대 스캔(`Path("docs/change-plans").rglob`). argv 무시.
#  → 본 test 는 격리된 임시 dir 안에 docs/change-plans/cfp-9999-*.md fixture 를 만들고 그 dir 를
#    CWD 로 한 뒤 `python3 <worktree>/scripts/lib/check_doc_section_schema.py` 호출(깨끗한 격리).
#  cfp 번호 = 9999 (LEGACY_CHANGE_PLAN_CFPS = {1..18} 회피 — legacy skip 안 됨).
#  fixture 는 §1-§11 필수 섹션 skeleton 전부 포함 — "필수 섹션 누락" warning 이 §8.7 결과를 mask 하지
#    않도록 (격리). §8.7 외 사유 fail 0 확보.
#
# ── discriminating (anti-theater 비협상) ──────────────────────────────────────
#  - TC1(1+ Y + §8.7.1 본문) PASS exit 0 ↔ TC2(1+ Y + §8.7.1 부재) FAIL exit 1.
#  - TC3(4 N + N/A substantive 부재) FAIL exit 1.
#  - TC4(§8.6 gap allow): §8.5.4 → §8.7 gap(§8.6 부재) 인 fixture 가 §8.7 외 사유로 fail 안 함(false-pos 0).
#
# ── 사전 의존 (sibling DeveloperAgent) ────────────────────────────────────────
#  check_section_8_7() 함수 부재 시(미구현) → 명시 FAIL 로 sibling-dependency 노출(silent skip 금지).
#
# Exit code: 0 = all discriminating cases pass, 1 = any fail

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINT_PY="$REPO_ROOT/scripts/lib/check_doc_section_schema.py"

# tally 파일 — run_case 가 subshell($(...)) 안에서 호출돼 전역 변수 증가가 손실되므로 파일로 누적.
TALLY=$(mktemp)
trap 'rm -f "$TALLY"' EXIT

tally_pass() { echo "P" >> "$TALLY"; }
tally_fail() { echo "F" >> "$TALLY"; }

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "✗ FAIL: python3/python 부재 — lint 실행 불가"
  exit 1
fi

# sibling 의존 확인: check_section_8_7() 미구현이면 명시 FAIL (silent skip 금지).
if [ ! -f "$LINT_PY" ]; then
  echo "✗ FAIL: scripts/lib/check_doc_section_schema.py 부재"
  exit 1
fi
if ! grep -q 'def check_section_8_7' "$LINT_PY"; then
  echo "✗ FAIL: check_doc_section_schema.py 에 check_section_8_7() 부재 (DeveloperAgent 미구현 — sibling-dependent, 이 case 재실행 필요)"
  exit 1
fi

# ── change-plan §1-§11 필수 섹션 skeleton (§8.7 외 사유 fail 0 격리) ──
#   §8 본문은 §8.7 sub-section 으로 채운다 (per-fixture). §8.6 = 의도적 부재(gap allow 검증).
emit_skeleton_head() {
  cat <<'EOF'
### §1. 목적
fixture
### §2. 현재 구조
fixture
### §3. 도입할 설계
fixture
### §4. API 계약
fixture
### §7. 보안
fixture
### §8. Test Contract
EOF
}
emit_skeleton_tail() {
  cat <<'EOF'
### §10. FIX Ledger
fixture
### §11. 데이터 마이그레이션
fixture
EOF
}

# run_case <fixture-md-body-builder-fn> <expected_exit> <name> <desc>
#   격리 임시 dir + cd + python3 lint. 결과 exit code assert.
#   ★ 로그(PASS/FAIL)는 stderr 로(라이브 가시), exit code 만 stdout 으로 echo → caller 가
#     $(run_case ...) 로 ec 캡처(로그는 화면에 그대로 흐름). PASS/FAIL 카운트는 파일 tally 로 누적
#     (subshell 변수 격리 회피 — caller 가 $(...) 로 호출하면 함수가 subshell 이라 전역 PASS/FAIL 손실).
run_case() {
  local body_fn="$1" expected="$2" name="$3" desc="$4"
  local T; T=$(mktemp -d)
  mkdir -p "$T/docs/change-plans"
  "$body_fn" > "$T/docs/change-plans/cfp-9999-fixture.md"
  local out ec=0
  out=$( cd "$T" && "$PY" "$LINT_PY" 2>&1 ) || ec=$?
  if [ "$ec" = "$expected" ]; then
    echo "✓ PASS: $name (exit $ec) — $desc" >&2
    echo "P" >> "$TALLY"
  else
    {
      echo "✗ FAIL: $name"
      echo "  Expected exit $expected, got $ec"
      echo "  Description: $desc"
      echo "  Lint output: $out"
    } >&2
    echo "F" >> "$TALLY"
  fi
  rm -rf "$T"
  echo "$ec"  # stdout = exit code only (caller 캡처용)
}

# ═════════════════════════════════════════════════════════════════════════════
# TC1 — frontend-bearing Y + §8.7.1 본문 있음 → PASS (exit 0)
#   §8.7.0 표 1+ Y (CSS/SCSS 파일 변경 = Y) + §8.7.1 render-truth 본문 → lint exit 0.
# ═════════════════════════════════════════════════════════════════════════════
tc1_body() {
  emit_skeleton_head
  cat <<'EOF'
#### §8.7 UI 실렌더 검증 (CONDITIONAL — CFP-2505 / ADR-136)
##### §8.7.0 Applicability decision (필수)
| 적용 조건 | Y/N | 근거 |
|---|:-:|---|
| CSS/SCSS 파일 변경 (순수 stylesheet) | Y | styles.css 의 모달 position 규칙을 직접 수정해 레이아웃 영향 발생 |
| 컴포넌트 변경 (JSX/TSX/Vue/template 렌더 구조) | N | 컴포넌트 렌더 구조 무변경 — CSS 규칙만 수정해 DOM 트리 형상 동일 유지 |
| 스타일 토큰/테마 변경 (design token / theme variable) | N | design token / theme variable 무변경 — 토큰 정의 파일 미접촉 상태 유지 |
| layout-affecting 속성 변경 (position/display/z-index 등) | Y | position:fixed 규칙을 portal 전역 selector 로 이동해 좌표 결과 변경 |
##### §8.7.1 render-truth 도구 독립성 (적용 시)
- 실 layout 엔진(Playwright)으로 모달 position 좌표를 검증 — jsdom 부적격(layout 미계산).
##### §8.7.2 min bar (적용 시)
- toHaveCSS('position','fixed') + boundingBox().y 좌표 단언.
EOF
  emit_skeleton_tail
}
EC_TC1=$(run_case tc1_body 0 "TC1-Y-with-871-PASS" "1+ Y + §8.7.1 render-truth 본문 → lint exit 0 (PASS)" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# TC2 — frontend-bearing Y + §8.7.1 본문 부재 → FAIL (exit 1)
#   1+ Y 인데 §8.7.1 render-truth 본문 헤딩 없음 → lint exit 1. TC1 ↔ TC2 discriminating.
# ═════════════════════════════════════════════════════════════════════════════
tc2_body() {
  emit_skeleton_head
  cat <<'EOF'
#### §8.7 UI 실렌더 검증 (CONDITIONAL — CFP-2505 / ADR-136)
##### §8.7.0 Applicability decision (필수)
| 적용 조건 | Y/N | 근거 |
|---|:-:|---|
| CSS/SCSS 파일 변경 (순수 stylesheet) | Y | styles.css 의 모달 position 규칙을 직접 수정해 레이아웃 영향 발생 |
| 컴포넌트 변경 (JSX/TSX/Vue/template 렌더 구조) | N | 컴포넌트 렌더 구조 무변경 — CSS 규칙만 수정해 DOM 트리 형상 동일 유지 |
| 스타일 토큰/테마 변경 (design token / theme variable) | N | design token / theme variable 무변경 — 토큰 정의 파일 미접촉 상태 유지 |
| layout-affecting 속성 변경 (position/display/z-index 등) | Y | position:fixed 규칙을 portal 전역 selector 로 이동해 좌표 결과 변경 |
EOF
  # ★ §8.7.1 본문 의도적 부재 (1+ Y 인데 render-truth 본문 없음 → FAIL 기대)
  emit_skeleton_tail
}
EC_TC2=$(run_case tc2_body 1 "TC2-Y-without-871-FAIL" "1+ Y + §8.7.1 본문 부재 → lint exit 1 (FAIL)" | tail -1)

# ── anti-theater discriminating: TC1(PASS) ↔ TC2(FAIL) ──
if [ "$EC_TC1" = "$EC_TC2" ]; then
  echo "✗ FAIL: ANTI-THEATER — TC1(exit=$EC_TC1) == TC2(exit=$EC_TC2) = non-discriminating hollow lint"
  tally_fail
else
  echo "✓ PASS: ANTI-THEATER discriminating — TC1(Y+§8.7.1 exit=$EC_TC1) ≠ TC2(Y+no§8.7.1 exit=$EC_TC2)"
  tally_pass
fi

# ═════════════════════════════════════════════════════════════════════════════
# TC3 — 4 N + N/A substantive 부재 → FAIL (exit 1)
#   4 행 모두 N 인데 §8.7.x N/A reason 이 30자 미만(vague) → exit 1.
# ═════════════════════════════════════════════════════════════════════════════
tc3_body() {
  emit_skeleton_head
  cat <<'EOF'
#### §8.7 UI 실렌더 검증 (CONDITIONAL — CFP-2505 / ADR-136)
##### §8.7.0 Applicability decision (필수)
| 적용 조건 | Y/N | 근거 |
|---|:-:|---|
| CSS/SCSS 파일 변경 (순수 stylesheet) | N | backend 서비스 코드만 수정 — stylesheet 파일 미접촉 상태로 렌더 산출물 부재 |
| 컴포넌트 변경 (JSX/TSX/Vue/template 렌더 구조) | N | 컴포넌트 렌더 구조 무변경 — 실행 가능 frontend 코드 0줄로 DOM 형상 무관 |
| 스타일 토큰/테마 변경 (design token / theme variable) | N | design token / theme variable 무변경 — 토큰 정의 파일 미접촉 상태 유지 |
| layout-affecting 속성 변경 (position/display/z-index 등) | N | layout 속성 무변경 — 좌표 영향 규칙 미접촉으로 렌더 좌표 동일 유지 |
##### §8.7.x N/A 명시 (4 적용 조건 모두 No)
N/A — 짧음
EOF
  emit_skeleton_tail
}
EC_TC3=$(run_case tc3_body 1 "TC3-4N-vague-NA-FAIL" "4 N + N/A reason 30자 미만(vague) → lint exit 1 (FAIL)" | tail -1)

# ── TC3-ok (대조 GREEN): 4 N + N/A substantive 30자+ → PASS (over-strict mutation 검출) ──
tc3ok_body() {
  emit_skeleton_head
  cat <<'EOF'
#### §8.7 UI 실렌더 검증 (CONDITIONAL — CFP-2505 / ADR-136)
##### §8.7.0 Applicability decision (필수)
| 적용 조건 | Y/N | 근거 |
|---|:-:|---|
| CSS/SCSS 파일 변경 (순수 stylesheet) | N | backend 서비스 코드만 수정 — stylesheet 파일 미접촉 상태로 렌더 산출물 부재 |
| 컴포넌트 변경 (JSX/TSX/Vue/template 렌더 구조) | N | 컴포넌트 렌더 구조 무변경 — 실행 가능 frontend 코드 0줄로 DOM 형상 무관 |
| 스타일 토큰/테마 변경 (design token / theme variable) | N | design token / theme variable 무변경 — 토큰 정의 파일 미접촉 상태 유지 |
| layout-affecting 속성 변경 (position/display/z-index 등) | N | layout 속성 무변경 — 좌표 영향 규칙 미접촉으로 렌더 좌표 동일 유지 |
##### §8.7.x N/A 명시 (4 적용 조건 모두 No)
N/A — 본 Story 는 backend 서비스 코드만 수정해 UI/CSS/컴포넌트/스타일 토큰 변경 0개, 렌더 산출물 부재. 검증 채널: 통합 테스트. 면제 분류: runtime-inert
EOF
  emit_skeleton_tail
}
EC_TC3OK=$(run_case tc3ok_body 0 "TC3ok-4N-substantive-NA-PASS" "4 N + N/A substantive 30자+ → lint exit 0 (PASS, over-strict 검출)" | tail -1)

if [ "$EC_TC3" = "$EC_TC3OK" ]; then
  echo "✗ FAIL: ANTI-THEATER — TC3(vague exit=$EC_TC3) == TC3ok(substantive exit=$EC_TC3OK) = N/A 길이 검증 non-discriminating"
  tally_fail
else
  echo "✓ PASS: ANTI-THEATER discriminating — TC3(vague N/A exit=$EC_TC3) ≠ TC3ok(substantive N/A exit=$EC_TC3OK)"
  tally_pass
fi

# ═════════════════════════════════════════════════════════════════════════════
# TC4 — §8.6 gap allow (false-positive 0)
#   change-plan 에 §8.5(+§8.5.4) 존재 → §8.6 의도적 부재 → §8.7 로 점프(gap). §8.7 lint 가
#   §8.6 부재를 사유로 fail 시키지 않음 — §8.7 본문 자체는 valid(4 N + substantive N/A) → exit 0.
#   §8.5.4 → §8.7 gap 인 fixture 가 §8.7 외 사유로 fail 안 함 assert.
# ═════════════════════════════════════════════════════════════════════════════
tc4_body() {
  emit_skeleton_head
  cat <<'EOF'
#### §8.5 Stateful / restart invariant tests (CONDITIONAL)
##### §8.5.0 Applicability decision (필수)
| 적용 조건 | Y/N | 근거 |
|---|:-:|---|
| Long-running connection | N | 본 Story 는 declarative 산출물만 — 런타임 connection 0건으로 long-running 형상 부재함 |
| Stateful in-memory cache | N | in-memory cache 미사용 — stateless 산출물이라 cache 상태 누적 형상 자체 부재함 |
| Background worker | N | background worker 미도입 — 동기 처리만이라 worker lifecycle 형상 부재 상태 유지함 |
| Process restart-aware system | N | restart-aware system 부재 — 영속 상태 0건이라 restart recovery 형상 무관 상태 유지함 |
##### §8.5.4 N/A 명시 (4 적용 조건 모두 No 시)
N/A — 본 Story 는 declarative 산출물만 수정해 stateful 4 조건 모두 부재. 검증 채널: 단위 테스트. 면제 분류: runtime-inert
#### §8.7 UI 실렌더 검증 (CONDITIONAL — CFP-2505 / ADR-136)
##### §8.7.0 Applicability decision (필수)
| 적용 조건 | Y/N | 근거 |
|---|:-:|---|
| CSS/SCSS 파일 변경 (순수 stylesheet) | N | backend 서비스 코드만 수정 — stylesheet 파일 미접촉 상태로 렌더 산출물 부재 |
| 컴포넌트 변경 (JSX/TSX/Vue/template 렌더 구조) | N | 컴포넌트 렌더 구조 무변경 — 실행 가능 frontend 코드 0줄로 DOM 형상 무관 |
| 스타일 토큰/테마 변경 (design token / theme variable) | N | design token / theme variable 무변경 — 토큰 정의 파일 미접촉 상태 유지 |
| layout-affecting 속성 변경 (position/display/z-index 등) | N | layout 속성 무변경 — 좌표 영향 규칙 미접촉으로 렌더 좌표 동일 유지 |
##### §8.7.x N/A 명시 (4 적용 조건 모두 No)
N/A — 본 Story 는 backend 서비스 코드만 수정해 UI/CSS 변경 0개, 렌더 산출물 부재. 검증 채널: 통합 테스트. 면제 분류: runtime-inert
EOF
  emit_skeleton_tail
}
EC_TC4=$(run_case tc4_body 0 "TC4-86-gap-allow" "§8.5.4 → §8.7 gap(§8.6 부재) → §8.7 외 사유 fail 0 → exit 0 (false-positive 0)" | tail -1)

# ─────────────────────────────────────────────────────────────────────────────
# Summary (tally 파일에서 집계)
# ─────────────────────────────────────────────────────────────────────────────
# 안전 카운트: grep -F line 출력을 wc -l (0 매칭이어도 exit code 무관, 단일 정수).
PASS=$(grep -cF "P" "$TALLY" 2>/dev/null | head -1); PASS=$(( PASS + 0 ))
FAIL=$(grep -cF "F" "$TALLY" 2>/dev/null | head -1); FAIL=$(( FAIL + 0 ))

echo ""
echo "============================================================"
echo "Test Summary (CFP-2505 §8.7 doc-section lint)"
echo "============================================================"
echo "PASS: $PASS / FAIL: $FAIL / TOTAL: $((PASS+FAIL))"
echo "Discriminating: TC1(Y+§8.7.1)=$EC_TC1 ≠ TC2(Y+no§8.7.1)=$EC_TC2 ; TC3(vague)=$EC_TC3 ≠ TC3ok(subst)=$EC_TC3OK"
echo "§8.6 gap allow: TC4 exit=$EC_TC4 (0=false-positive 0)"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
