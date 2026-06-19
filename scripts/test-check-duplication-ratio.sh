#!/usr/bin/env bash
# CFP-2369 — Discriminating test for check-duplication-ratio.sh
#
# RED → GREEN 변별 증명 (anti-theater, mutation-resistant):
# - dirty (ratio > threshold) → warning emit 확인 (RED)
# - clean (ratio ≤ threshold) → warning 0 확인 (GREEN)
# 둘이 갈리지 않으면 검사 무의미 (theater) → 본 테스트가 변별력을 강제.
#
# **핵심: stub detector (DUPLICATION_TOOL) 로 결정론적 검증** — jscpd/네트워크 비의존.
# stub = 인자로 dir 받아 고정 ratio 를 echo 하는 스크립트. 이렇게 스크립트 자체 로직
# (파싱 / threshold 비교 / warning emit / exit 0) 만 isolate 해 검증한다.
#
# Exit code: 0 (all tests pass) / 1 (any test fails)
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-duplication-ratio.sh"

PASS=0
FAIL=0

# 격리 작업 디렉터리
TMP=$(mktemp -d)
trap "rm -rf '$TMP'" EXIT

# target source dir (대부분 케이스 공통 — 존재만 하면 됨, 내용은 stub 가 결정)
mkdir -p "$TMP/src"
echo "placeholder" > "$TMP/src/dummy.txt"

# stub detector 생성 헬퍼 — 고정 ratio 를 echo
make_stub() {
  local path="$1"
  local ratio="$2"
  cat > "$path" <<EOF
#!/usr/bin/env bash
# stub detector — 인자(\$1 = target dir) 받아 고정 ratio echo
echo "$ratio"
EOF
  chmod +x "$path"
}

# run_test: 환경 구성 후 스크립트 실행, exit code + warning 유무 assert
#   $1 test_name / $2 expect_warn(yes|no) / $3 expect_exit / $4 (선택) "스크립트에 넘길 env+arg" 미사용
run_test() {
  local test_name="$1"
  local expect_warn="$2"   # yes | no
  local expect_exit="$3"
  shift 3
  # 나머지 인자 = 실행 시 prefix env (예: DUPLICATION_TOOL=... DUPLICATION_THRESHOLD=...)
  local env_prefix="$*"

  local output exit_code=0
  output=$( cd "$TMP" && eval "$env_prefix bash '$SCRIPT'" 2>&1 ) || exit_code=$?

  # exit code assert
  if [ "$exit_code" -ne "$expect_exit" ]; then
    echo "x FAIL: $test_name"
    echo "  Expected exit $expect_exit, got $exit_code"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
    return 1
  fi

  local has_warn=0
  echo "$output" | grep -q "::warning" && has_warn=1

  if { [ "$expect_warn" = "yes" ] && [ "$has_warn" -eq 1 ]; } || \
     { [ "$expect_warn" = "no" ]  && [ "$has_warn" -eq 0 ]; }; then
    echo "+ PASS: $test_name (warn=$has_warn, exit $exit_code)"
    PASS=$((PASS+1))
    return 0
  fi

  echo "x FAIL: $test_name"
  echo "  Expected warning: $expect_warn, Got warning: $has_warn"
  echo "  Output: $output"
  FAIL=$((FAIL+1))
  return 1
}

# ── stub 준비 ──
STUB_DIRTY="$TMP/stub-dirty.sh"      # ratio 9.0 > thr 5.0
STUB_CLEAN="$TMP/stub-clean.sh"      # ratio 1.0 ≤ thr 5.0
STUB_BOUNDARY="$TMP/stub-boundary.sh" # ratio 5.0 == thr 5.0
make_stub "$STUB_DIRTY" "9.0"
make_stub "$STUB_CLEAN" "1.0"
make_stub "$STUB_BOUNDARY" "5.0"

# T1: dirty — ratio 9.0 > threshold 5.0 → warning emit + exit 0 (RED 변별)
run_test "T1: ratio > threshold (9.0 vs 5.0) → warning" \
  "yes" 0 \
  "DUPLICATION_TOOL='bash $STUB_DIRTY' DUPLICATION_THRESHOLD=5.0"

# T2: clean — ratio 1.0 ≤ threshold 5.0 → no warning + exit 0 (GREEN 변별)
run_test "T2: ratio <= threshold (1.0 vs 5.0) → no warning" \
  "no" 0 \
  "DUPLICATION_TOOL='bash $STUB_CLEAN' DUPLICATION_THRESHOLD=5.0"

# T3: detector 불가 — DUPLICATION_TOOL 이 존재 안 하는 command 라 빈 stdout 반환.
#     override 경로가 빈 결과 → 숫자 아님 → "unavailable" warning + exit 0.
#     (PATH 조작은 bash 자체를 깨므로 미사용 — override stub 부재로 detector-fail 모의)
run_test "T3: detector unavailable (tool produces no number) → unavailable warning" \
  "yes" 0 \
  "DUPLICATION_TOOL='$TMP/no-such-detector-xyz' DUPLICATION_THRESHOLD=5.0"

# T4: target source 부재 — DUPLICATION_TARGET 가 없는 dir → 조용히 exit 0, no warning
run_test "T4: target source absent → no warning, exit 0" \
  "no" 0 \
  "DUPLICATION_TARGET='$TMP/no-such-dir' DUPLICATION_TOOL='bash $STUB_DIRTY'"

# T5 (anti-theater missing-case): 경계값 — ratio 5.0 == threshold 5.0 → 'ratio > thr' false → no warning
#     (≤ threshold 는 clean 처리라는 경계 명확성 + threshold inclusive 하한 검증)
run_test "T5a: boundary ratio == threshold (5.0 == 5.0) → no warning (<=  is clean)" \
  "no" 0 \
  "DUPLICATION_TOOL='bash $STUB_BOUNDARY' DUPLICATION_THRESHOLD=5.0"

# T5b (anti-theater): warning 문자열에 실제 ratio 수치가 포함되는지 확인
#     (수치 없는 "공통화 필요" 메시지면 falsifiable 신호 무의미 → 수치 grounding 강제)
T5B_OUT=$( cd "$TMP" && DUPLICATION_TOOL="bash $STUB_DIRTY" DUPLICATION_THRESHOLD=5.0 bash "$SCRIPT" 2>&1 ) || true
if echo "$T5B_OUT" | grep -q "9.0%" && echo "$T5B_OUT" | grep -q "5.0%"; then
  echo "+ PASS: T5b: warning 문자열에 ratio(9.0%) + threshold(5.0%) 수치 포함"
  PASS=$((PASS+1))
else
  echo "x FAIL: T5b: warning 문자열에 ratio/threshold 수치 누락"
  echo "  Output: $T5B_OUT"
  FAIL=$((FAIL+1))
fi

# T6 (anti-theater discrimination guard): dirty 와 clean 이 실제로 갈렸는지 교차 확인
#     (둘 다 warning 이거나 둘 다 no-warning 이면 검사가 무의미 = theater → FAIL)
DIRTY_OUT=$( cd "$TMP" && DUPLICATION_TOOL="bash $STUB_DIRTY" DUPLICATION_THRESHOLD=5.0 bash "$SCRIPT" 2>&1 ) || true
CLEAN_OUT=$( cd "$TMP" && DUPLICATION_TOOL="bash $STUB_CLEAN" DUPLICATION_THRESHOLD=5.0 bash "$SCRIPT" 2>&1 ) || true
DIRTY_WARN=0; echo "$DIRTY_OUT" | grep -q "::warning" && DIRTY_WARN=1
CLEAN_WARN=0; echo "$CLEAN_OUT" | grep -q "::warning" && CLEAN_WARN=1
if [ "$DIRTY_WARN" -eq 1 ] && [ "$CLEAN_WARN" -eq 0 ]; then
  echo "+ PASS: T6: RED(dirty)=warning != GREEN(clean)=no-warning 변별 실증 (anti-theater)"
  PASS=$((PASS+1))
else
  echo "x FAIL: T6: 변별 실패 (dirty_warn=$DIRTY_WARN clean_warn=$CLEAN_WARN) — 검사 무의미(theater)"
  FAIL=$((FAIL+1))
fi

# ── FIX 1+2: default jscpd json 파싱 경로 직접 검증 (anti-theater gap 메움) ──
# parse_jscpd_percentage 함수를 lib source 로 로드해 실 jscpd 형태 fixture 로 검증.
# (stub detector 만으로는 default 파싱 경로가 untested — P2 버그가 숨었던 이유.)
# DUPLICATION_RATIO_LIB=1 로 source = 함수만 로드, main 미실행.
# shellcheck disable=SC1090
( DUPLICATION_RATIO_LIB=1 source "$SCRIPT" ) >/dev/null 2>&1  # syntax/source 가능 sanity
DUPLICATION_RATIO_LIB=1 source "$SCRIPT" >/dev/null 2>&1

# 실 jscpd v5 형태 (statistics 복수, jscpd 5.0.10 실측 키)
echo '{"statistics":{"total":{"percentage":45.33}}}' > "$TMP/real-jscpd.json"
# 구 버전/문서 변종 (statistic 단수)
echo '{"statistic":{"total":{"percentage":12.7}}}' > "$TMP/old-jscpd.json"
# 파싱 불가 (키 둘 다 없음)
echo '{"duplicates":[]}' > "$TMP/no-pct.json"

P_REAL="$(parse_jscpd_percentage "$TMP/real-jscpd.json")"
P_OLD="$(parse_jscpd_percentage "$TMP/old-jscpd.json")"
P_NONE="$(parse_jscpd_percentage "$TMP/no-pct.json")"

if [ "$P_REAL" = "45.33" ]; then
  echo "+ PASS: T7a: parse_jscpd_percentage(statistics 복수, 실 jscpd v5) = 45.33"
  PASS=$((PASS+1))
else
  echo "x FAIL: T7a: statistics(복수) 파싱 실패 — got [$P_REAL] expected 45.33"
  FAIL=$((FAIL+1))
fi

if [ "$P_OLD" = "12.7" ]; then
  echo "+ PASS: T7b: parse_jscpd_percentage(statistic 단수, 구 변종) = 12.7 (버전 편차 흡수)"
  PASS=$((PASS+1))
else
  echo "x FAIL: T7b: statistic(단수) 변종 흡수 실패 — got [$P_OLD] expected 12.7"
  FAIL=$((FAIL+1))
fi

if [ -z "$P_NONE" ]; then
  echo "+ PASS: T7c: percentage 키 부재 json → 빈 문자열 (caller 가 unavailable 처리)"
  PASS=$((PASS+1))
else
  echo "x FAIL: T7c: percentage 부재인데 비어있지 않음 — got [$P_NONE]"
  FAIL=$((FAIL+1))
fi

# ── FIX 3: 비숫자 threshold → default 5.0 fallback + misconfig warning ──
# 비숫자 threshold(예 'abc') 면 gt 비교가 fail-silent 했던 회귀 차단.
# stub ratio 9.0 > fallback 5.0 → duplication warning 도 함께 살아있어야 함 (신호 미소실).
T8_OUT=$( cd "$TMP" && DUPLICATION_TOOL="bash $STUB_DIRTY" DUPLICATION_THRESHOLD="abc" bash "$SCRIPT" 2>&1 ) || true
T8_EXIT=0; ( cd "$TMP" && DUPLICATION_TOOL="bash $STUB_DIRTY" DUPLICATION_THRESHOLD="abc" bash "$SCRIPT" >/dev/null 2>&1 ) || T8_EXIT=$?
if echo "$T8_OUT" | grep -q "threshold misconfig" \
   && echo "$T8_OUT" | grep -q "duplication ratio 9.0%" \
   && [ "$T8_EXIT" -eq 0 ]; then
  echo "+ PASS: T8: 비숫자 threshold → misconfig warning + default 5.0 로 9.0% 초과 신호 유지 (exit 0)"
  PASS=$((PASS+1))
else
  echo "x FAIL: T8: 비숫자 threshold fallback 미작동 (fail-silent 회귀)"
  echo "  exit=$T8_EXIT Output: $T8_OUT"
  FAIL=$((FAIL+1))
fi

echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (discriminating test validates duplication-ratio check)"
  exit 0
else
  echo "Some tests failed (check may not discriminate dirty/clean correctly)"
  exit 1
fi
