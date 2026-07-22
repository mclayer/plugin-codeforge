#!/usr/bin/env bash
# scripts/test-check-lane-count-ssot.sh
# CFP-2426 Phase 2 — Discriminating self-test for check-lane-count-ssot.sh (ADR-060 Amd19 §결정 33).
#
# anti-theater test (AC-7 / CFP-1334): lint 이 실제로 genuine STALE 를 잡고 allowlist 가
# 정탐을 면제함을 양방향 입증 + content-anchor fixture (line# 하드코딩 0 — 요구사항리뷰 R1 교훈).
#
# mutation testing (production code 깨뜨리면 RED — mutation 생존 0):
#  - Mutation-1: stale 검출 정규식(_DETECT_PATTERNS) 제거 → F-DET-1~4 RED (stale 미검출).
#  - Mutation-2: allowlist OR 결합 → false 상수화(allowlist 무력화) →
#                F-HIST-1~5 / F-NEG-1 / F-COUNTERFACTUAL / F-DUAL-1 / F-TRANS-1 RED (history/negation/counterfactual/dual 과검출).
#  - Mutation-3: amendment_log span exit 미감지(toggle exit 제거 = span 무한확장) → F-CHANNEL-1 RED
#                (multi-line amendment_log block 다음 sibling live `description:` STALE 까지 silent 면제 = false-negative).
#  - Mutation-4: 축⑤ counterfactual 정규식 over-broaden(`만약` 가정 마커 anchor 제거 → 모든 lane-count 토큰 면제)
#                → F-COUNTERFACTUAL-NEG RED (`만약` 부재 단독 `9 레인` silent 면제 = false-negative).
#  - Mutation-5: ordinal lookbehind 가드 제거(F-CR-2426-P2, `(?<![0-9])(10|[679])(?![0-9])번째 lane` → `(10|[679])(?![0-9])번째 lane`)
#                → F-GUARD-1 RED (`16번째 lane` leading-digit `6` false-FLAG = 과검출).
#
# Exit code:
#  0 = all tests pass (discriminating test validates lint)
#  1 = any test fails (lint may not be detecting mutations correctly)
#
# Prior art: scripts/test-check-deferred-followup-reconcile.sh (mktemp -d + trap + cp production + run_test 5-인자).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

# 임시 테스트 repo 생성 (production script + content fixture 격리)
TMP_REPO=$(mktemp -d)
trap "rm -rf '$TMP_REPO'" EXIT

mkdir -p "$TMP_REPO/scripts/lib"
mkdir -p "$TMP_REPO/docs"

# production script 복사 (격리 실행 — mutation 시 복사본만 변조)
cp "$REPO_ROOT/scripts/check-lane-count-ssot.sh" "$TMP_REPO/scripts/"
cp "$REPO_ROOT/scripts/lib/check_lane_count_ssot.py" "$TMP_REPO/scripts/lib/"

PROD_PY="$TMP_REPO/scripts/lib/check_lane_count_ssot.py"
PROD_PY_BAK="$TMP_REPO/scripts/lib/check_lane_count_ssot.py.bak"
cp "$PROD_PY" "$PROD_PY_BAK"

FIXTURE_REL="docs/_fixture.md"
FIXTURE_PATH="$TMP_REPO/$FIXTURE_REL"

# ─────────────────────── run_test (5-인자) ──────────────────────────────────────
# run_test <name> <fixture_content> <should_flag yes/no> <expected_exit 0/1/2> <desc>
run_test() {
  local test_name="$1"
  local fixture_content="$2"
  local should_have_flag="$3"     # "yes" or "no"
  local expected_exit_code="$4"   # "0", "1", or "2"
  local description="$5"

  printf '%s\n' "$fixture_content" > "$FIXTURE_PATH"

  local output exit_code=0
  output=$( cd "$TMP_REPO" && bash scripts/check-lane-count-ssot.sh check --repo-root . --paths "$FIXTURE_REL" 2>&1 ) || exit_code=$?

  if [ "$exit_code" -ne "$expected_exit_code" ]; then
    echo "✗ FAIL: $test_name"
    echo "  Expected exit code $expected_exit_code, got $exit_code"
    echo "  Description: $description"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
    return 0
  fi

  local has_flag=0
  if echo "$output" | grep -q "::warning::check-lane-count-ssot: FLAG"; then
    has_flag=1
  fi

  if { [ "$should_have_flag" = "yes" ] && [ "$has_flag" -eq 1 ]; } \
     || { [ "$should_have_flag" = "no" ] && [ "$has_flag" -eq 0 ]; }; then
    echo "✓ PASS: $test_name (FLAG=$has_flag, exit $exit_code)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected FLAG: $should_have_flag, Got FLAG: $has_flag"
    echo "  Description: $description"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
  fi
}

# run_test_setup: SETUP(exit 2) 검증 — 검사 경로 부재 케이스 (fixture 미사용)
run_test_setup() {
  local test_name="$1"
  local description="$2"
  local output exit_code=0
  # 존재하지 않는 glob 지정 → 검사 경로 0 → exit 2
  output=$( cd "$TMP_REPO" && bash scripts/check-lane-count-ssot.sh check --repo-root . --paths "docs/__nonexistent_dir__" 2>&1 ) || exit_code=$?
  if [ "$exit_code" -eq 2 ]; then
    echo "✓ PASS: $test_name (exit 2 SETUP)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $test_name (expected exit 2, got $exit_code)"
    echo "  Description: $description"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
  fi
}

echo "═══════════════ check-lane-count-ssot self-test (CFP-2426) ═══════════════"
echo ""
echo "── 기본 fixture (검출/면제 양방향) ──"

# ── F-DET (genuine STALE 검출) ──
run_test "F-DET-1 label-registry desc형" \
  '    description: "Phase: 요구사항-리뷰 (CFP-2326 / ADR-125 — 9번째 lane, Phase 1 내부 sub-gate)"' \
  yes 1 "live description: 안 9번째 lane → FLAG (AC-1)"

run_test "F-DET-2 plugin.json tagline형 (two-digit stale)" \
  '  "description": "0 core 에이전트 (wrapper-only) · 10 레인 + CI gate + role:dev"' \
  yes 1 "description tagline · 10 레인 (two-digit stale, canonical=8) → FLAG (AC-1)"

run_test "F-DET-3 section-ownership 2토큰" \
  "$(printf '    section: "레인 5개 · 단계 정의"\n    section: "레인 10개 · 단계 정의"')" \
  yes 1 "section: 값 레인 5개 + 레인 10개 → FLAG ×2 (AC-1)"

run_test "F-DET-4 base-labels 형" \
  'gate:requirements-review-pass	0e8a16	Requirements review PASS (CFP-2326 / ADR-125 — 9번째 lane, 외부사실 게이트)' \
  yes 1 "live label description 9번째 lane → FLAG (AC-1)"

echo ""
echo "── F-HIST (history 면제) ──"

# ── F-HIST-1 date행 ──
run_test "F-HIST-1 date행" \
  '    date: 2026-06-17 # 요구사항-리뷰 9번째 lane 신설 시점' \
  no 0 "date: 선두 라인 9번째 lane → no-FLAG (③-a, AC-4)"

# ── F-HIST-2 amendment_log span (multi-line block) ──
run_test "F-HIST-2 amendment_log span" \
  "$(printf 'amendment_log:\n  - amendment: 12\n    summary: lane enum 에 9번째 lane 신설 추가\n')" \
  no 0 "amendment_log block 내부 + 이벤트동사(신설/추가) 9번째 lane → no-FLAG (③-b, AC-4)"

# ── F-HIST-3 MANIFEST amendment_log형 ──
run_test "F-HIST-3 MANIFEST amendment_log" \
  "$(printf 'amendment_log:\n  - { file: review-verdict-v4.md }  # 9번째 lane 신설 3 entry 추가\n')" \
  no 0 "MANIFEST amendment_log 9번째 lane 신설 N entry → no-FLAG (③-b, AC-4)"

# ── F-HIST-4 source_section / 인용 ──
run_test "F-HIST-4 source_section 인용" \
  '    source_section: "§3.1 9번째 lane (요구사항리뷰) 신설"' \
  no 0 "source_section: 역사 인용 9번째 lane → no-FLAG (③-c, AC-4)"

# ── F-HIST-5 버전이력 표 (과거 baseline) ──
run_test "F-HIST-5 버전이력 표" \
  '| 구 버전 | 18 에이전트 · 4 레인 | 과거 baseline |' \
  no 0 "playbook 18 에이전트 · 4 레인 과거 행 → no-FLAG (③-d, AC-4)"

echo ""
echo "── F-DUAL (within-line 이중토큰 plugin-count) ──"

run_test "F-DUAL-1 within-line 이중토큰" \
  '최상위 Claude 세션이 8 lane plugin 의 에이전트를 spawn 한다 (6 lane plugin 도 동형).' \
  no 0 "8 lane plugin / 6 lane plugin 단독 → no-FLAG (축①, AC-5)"

run_test "F-DUAL-2 dual + 별 라인 잔여 stale" \
  "$(printf '세션이 8 lane plugin 의 에이전트를 spawn.\n현재 작업레인은 9 레인 으로 구성된다.\n')" \
  yes 1 "한 라인 8 lane plugin (면제) + 별 라인 9 레인 (검출) → FLAG (잔여만, AC-5 엣지)"

echo ""
echo "── F-GUARD (leading-digit ordinal lookbehind 가드 — F-CR-2426-P2) ──"

run_test "F-GUARD-1 leading-digit ordinal" \
  '본 항목은 16번째 lane 항목이자 26번째 lane 후보 (ordinal 번호, lane count 단언 아님).' \
  no 0 "16번째 lane / 26번째 lane (leading-digit ordinal) → no-FLAG (lookbehind 가드, 가드 제거 시 RED)"

echo ""
echo "── F-NEG (negation) ──"

run_test "F-NEG-1 negation" \
  '운영 phase 는 9번째 lane 이 아니다 (ADR-104 — lane 집합 ∉).' \
  no 0 "9번째 lane 이 아니다 부정문 → no-FLAG (축②, AC-3)"

echo ""
echo "── F-COUNTERFACTUAL (가정문 축⑤ — FIX iter1 D1) ──"

run_test "F-COUNTERFACTUAL 가정문" \
  '만약 운영 phase 를 9번째 lane 으로 신설하면 ADR-023 lane count invariant 와 충돌하고 무너진다.' \
  no 0 "만약 ... 9번째 lane 으로 신설하면 ... 충돌 가정 조건절 → no-FLAG (축⑤, AC-3/AC-8)"

run_test "F-COUNTERFACTUAL-NEG over-exempt 차단" \
  '현재 작업레인은 9 레인 으로 운영 중이다 (만약 마커 부재 단독 현재-상태 단언).' \
  yes 1 "만약 마커 부재 단독 9 레인 (현재-상태 단언) → FLAG (축⑤가 일반 STALE 안 삼킴, AC-8)"

echo ""
echo "── F-TRANS (transition 화살표) ──"

run_test "F-TRANS-1 transition" \
  'lane 전이: 9→10 / 6→8 / 7→9 (정당 전이 표기)' \
  no 0 "9→10 / 6→8 / 7→9 숫자 전이 → no-FLAG (③-d, AC-7)"

run_test "F-TRANS-2 already-correct PASS" \
  "$(printf '보안-테스트 terminal 정합으로 10→8 전이 완료.\n현재 canonical = 8번째 lane (정답).\n')" \
  no 0 "8번째 lane (정답) + 10→8 전이 한 파일 → no-FLAG PASS (AC-5)"

echo ""
echo "── F-CHANNEL (★same-file channel-split — P0) ──"

# F-CHANNEL-1: multi-line amendment_log block (span 내부 entry 면제) →
#   exit(dedent, 다음 top-level key) → sibling top-level live description: STALE (검출).
run_test "F-CHANNEL-1 ★same-file split (multi-line span)" \
  "$(printf 'amendment_log:\n  - amendment: 96\n    summary: 요구사항리뷰 9번째 lane 신설 3 entry 추가\n  - name: gate:requirements-review-pass\n    description: "Requirements review PASS (CFP-2326 — 9번째 lane FIX 카운터)"\n')" \
  yes 1 "amendment_log span 내부 entry(면제) → exit → sibling description: 9번째 lane(검출) → FLAG (sibling만, AC-8, Mutation-3 kill)"

# F-CHANNEL-2: section: 값(검출) + 주석 인용(면제) 동시.
run_test "F-CHANNEL-2 section-ownership split" \
  "$(printf '    section: "레인 10개 · 단계 정의"\n    # 본 §단락 = wrapper CLAUDE.md "레인 10개 · 단계 정의" 영역 mirror\n')" \
  yes 1 "section: 값 레인 10개(검출) + 주석 따옴표 인용(면제) → FLAG (section: 값만, AC-8)"

echo ""
echo "── F-BORDER (check-lane-evidence 주석 — §7.B5) ──"

run_test "F-BORDER-1 check-lane-evidence 주석" \
  '# Lane names (한국어 8종 — CFP-2326 / ADR-125: 요구사항-리뷰 9번째 lane 추가)' \
  no 0 "주석 내 9번째 lane 추가 (이벤트동사 추가) → no-FLAG (③-b 토큰-인접, §7.B5)"

echo ""
echo "── F-EXIT (exit semantics) ──"

run_test "F-EXIT-0 PASS (stale 0)" \
  '현재 canonical = 8 레인 (정답). 6 lane plugin 별 축.' \
  no 0 "canonical 8 레인 + 6 lane plugin, stale 0 파일 → exit 0 (AC-6)"

run_test "F-EXIT-1 FLAG (stale 1+, 비차단 warning)" \
  '현재 작업레인은 9 레인 이다 (stale).' \
  yes 1 "stale 1+ → exit 1 (비차단 warning, AC-6)"

run_test_setup "F-EXIT-2 SETUP (검사 경로 부재)" \
  "검사 경로 0개 → exit 2 (SETUP)"

# ─────────────────────── mutation testing (production code 변조 → fixture RED) ───
echo ""
echo "── mutation testing (production code 변조 시 RED — mutation 생존 0) ──"

# fixture 별 기대값을 단순화: mutation 후 특정 fixture 가 should_flag 반대로 뒤집히면 RED.
# mutate_and_check <mut_name> <old_str> <new_str> <fixture_content> <orig_should_flag> <desc>
#   old_str → new_str 로 PROD_PY 1회 치환 (env-var 전달 — backslash/heredoc 망가짐 회피).
#   치환이 no-op 이면 fail-loud (anchor stale 검출). orig_should_flag 와 *반대* 결과 = kill.
mutate_and_check() {
  local mut_name="$1"
  local old_str="$2"
  local new_str="$3"
  local fixture_content="$4"
  local orig_should_flag="$5"
  local desc="$6"

  cp "$PROD_PY_BAK" "$PROD_PY"

  local changed
  changed=$( MUT_OLD="$old_str" MUT_NEW="$new_str" MUT_PATH="$PROD_PY" python3 - <<'PYEOF'
import os, io
path = os.environ["MUT_PATH"]
old = os.environ["MUT_OLD"]
new = os.environ["MUT_NEW"]
src = io.open(path, encoding="utf-8").read()
if old not in src:
    print("NOOP")
else:
    src = src.replace(old, new, 1)
    io.open(path, "w", encoding="utf-8").write(src)
    print("CHANGED")
PYEOF
)

  if [ "$changed" != "CHANGED" ]; then
    echo "✗ FAIL: $mut_name — mutation anchor NOT FOUND (stale anchor, 치환 no-op)"
    echo "  old_str: $old_str"
    cp "$PROD_PY_BAK" "$PROD_PY"
    FAIL=$((FAIL+1))
    return 0
  fi

  printf '%s\n' "$fixture_content" > "$FIXTURE_PATH"
  local output exit_code=0
  output=$( cd "$TMP_REPO" && bash scripts/check-lane-count-ssot.sh check --repo-root . --paths "$FIXTURE_REL" 2>&1 ) || exit_code=$?

  local has_flag=0
  if echo "$output" | grep -q "::warning::check-lane-count-ssot: FLAG"; then
    has_flag=1
  fi

  # mutation kill = 결과가 orig 와 반대로 뒤집힘.
  local killed=0
  if [ "$orig_should_flag" = "yes" ] && [ "$has_flag" -eq 0 ]; then killed=1; fi   # 검출돼야 할 게 안 잡힘
  if [ "$orig_should_flag" = "no" ]  && [ "$has_flag" -eq 1 ]; then killed=1; fi   # 면제돼야 할 게 과검출

  cp "$PROD_PY_BAK" "$PROD_PY"

  if [ "$killed" -eq 1 ]; then
    echo "✓ PASS: $mut_name killed (mutation 생존 0)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $mut_name SURVIVED (mutation 미검출 — lint 결함 가능)"
    echo "  Description: $desc"
    echo "  has_flag=$has_flag (orig should_flag=$orig_should_flag)"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
  fi
}

# Mutation-1: stale 검출 정규식 제거 → F-DET RED (stale 미검출).
mutate_and_check "Mutation-1 (detect 정규식 제거)" \
  '_DETECT_PATTERNS = [_RE_HANGUL_LANE, _RE_HANGUL_LANE_GAE, _RE_ENG_ORDINAL_LANE]' \
  '_DETECT_PATTERNS = []' \
  '    description: "Phase: 요구사항-리뷰 (CFP-2326 — 9번째 lane, Phase 1 sub-gate)"' \
  yes "detect 정규식 제거 시 genuine STALE(F-DET-1) 미검출 = RED"

# Mutation-2: allowlist 무력화 (allowlist_match 항상 None 반환) → F-HIST/NEG/CF/DUAL 과검출.
mutate_and_check "Mutation-2 (allowlist 무력화)" \
  'def allowlist_match(line, in_amendment_span, stale_match=None):' \
  'def allowlist_match(line, in_amendment_span, stale_match=None):
    return None  # MUTATION-2' \
  '운영 phase 는 9번째 lane 이 아니다 (ADR-104 부정문).' \
  no "allowlist 무력화 시 negation(F-NEG-1) 과검출 = RED"

# Mutation-3: amendment_log span exit 미감지 (toggle exit 제거 = 무한확장) → F-CHANNEL-1 RED.
#   update_amendment_span 의 exit 검사 직전에 무조건 return True 삽입 — enter 후 영영 span 유지.
mutate_and_check "Mutation-3 (span exit 미감지 = 무한확장)" \
  '    # in_span == True — exit 조건 검사 (빈 줄은 span 유지)' \
  '    return True, span_enter_indent  # MUTATION-3 (exit 미감지)
    # in_span == True — exit 조건 검사 (빈 줄은 span 유지)' \
  "$(printf 'amendment_log:\n  - amendment: 96\n    summary: 요구사항리뷰 9번째 lane 신설 3 entry 추가\n  - name: gate:requirements-review-pass\n    description: "Requirements review PASS (CFP-2326 — 9번째 lane FIX 카운터)"\n')" \
  yes "span exit 미감지 시 sibling live description: STALE 까지 silent 면제 = false-negative RED (F-CHANNEL-1)"

# Mutation-4: 축⑤ counterfactual over-broaden (만약 가정 마커 anchor 제거 → 모든 lane-count 토큰 면제) → F-CF-NEG RED.
#   over-broad 형태 = 가정 마커·귀결동사 anchor 제거하고 일반 lane-count 토큰을 통째 면제.
mutate_and_check "Mutation-4 (counterfactual over-broaden)" \
  'r"만약.*(?:10|[679])번째\s{0,3}lane.*(?:신설|충돌|된다|무너)"' \
  'r"([6-9])\s{0,3}레인|([6-9])번째\s{0,3}lane"' \
  '현재 작업레인은 9 레인 으로 운영 중이다 (만약 마커 부재 단독 현재-상태 단언).' \
  yes "counterfactual 정규식 over-broaden(가정 마커 제거 → 일반 lane-count 면제) 시 단독 9 레인(F-COUNTERFACTUAL-NEG) silent 면제 = false-negative RED"

# Mutation-5: ordinal lookbehind 가드 제거 (F-CR-2426-P2) → F-GUARD-1 false-FLAG RED.
#   `(?<![0-9])([6-9])번째 lane` → `([6-9])번째 lane` 으로 가드 제거 시 `16번째 lane` 의 leading-digit
#   `6` 이 false-FLAG → F-GUARD-1(no-FLAG 기대)이 과검출 RED.
mutate_and_check "Mutation-5 (ordinal 가드 제거)" \
  'r"(?<![0-9])(10|[679])(?![0-9])번째\s{0,3}lane"' \
  'r"(10|[679])(?![0-9])번째\s{0,3}lane"' \
  '본 항목은 16번째 lane 항목이자 26번째 lane 후보 (ordinal 번호, lane count 단언 아님).' \
  no "ordinal lookbehind 가드 제거 시 16번째 lane leading-digit false-FLAG(F-GUARD-1 과검출) = RED"

# ─────────────────────── 종합 ───────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  PASS: $PASS / FAIL: $FAIL"
echo "═══════════════════════════════════════════════════════════════"

if [ "$FAIL" -gt 0 ]; then
  echo "✗ self-test FAILED (lint 결함 또는 mutation 생존 — 회귀 차단)"
  exit 1
fi
echo "✓ self-test PASSED (전 fixture + 5 mutation kill — discriminating power 입증)"
exit 0
