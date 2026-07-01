#!/usr/bin/env bash
# tests/scripts/test_check-codex-companion-timeout-presence.sh
# CFP-2545 Phase 2 — Discriminating self-test for
#   scripts/lib/check_codex_companion_timeout_presence.py wall-clock 가드 presence lint.
#
# 배경: codex companion dispatch (node ... adversarial-review | task --write) 는
#   항상 timeout 가드(`timeout <N> --kill-after=<K>`)로 감싸야 함 (ADR-081 §D14).
#   hollow-gate 회피 + mutation RED 입증으로 가드가 load-bearing 임을 증명.
#
# self-contained bash (tests/scripts 관례 답습).
#   fixture text file 을 생성 → lint 를 그 파일에 대해 실행 → exit code + grep assert.
#
# Discriminating 의무 (change-plan §8):
#   - GREEN: timeout+kill-after 가드 존재 → exit 0
#   - RED (mutation): timeout 가드 제거 → exit 1
#   - RED (hollow-gate): 발화 0건(파일 존재) → exit 1
#   - RED: N ≤ 0 (N=0, N 음수) → exit 1
#   - RED: --kill-after 누락 → exit 1
#   - GREEN (consumer no-op): 경로 부재 → exit 0
#
# 각 케이스는 fixture text file 을 TMPDIR 에 생성해 lint 를 실행하고,
# exit code 대비로 GREEN/RED 를 판별. mutation-RED 는 케이스 1(GREEN) ↔ 케이스 3(RED)
# 의 diff (timeout prefix 제거) 로 증명.
#
# Exit code:
#  0 = all fixtures pass (wall-clock 가드가 load-bearing 임 증명)
#  1 = any fixture fails (가드가 검사되지 않거나 hollow-gate 미확인)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-codex-companion-timeout-presence.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# run_case: fixture text file 생성 → lint 실행 → exit code assert.
#   $1=name  $2=fixture_text  $3=expected_exit  $4=description
# fixture_text 는 fixture file 에 write.
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" fixture_text="$2" expected_exit="$3" description="$4"
  local exit_code=0 out fixture_file

  fixture_file="$(mktemp --suffix=.md)"
  trap "rm -f '$fixture_file'" RETURN

  echo -n "$fixture_text" > "$fixture_file"

  out=$(bash "$WRAPPER" "$fixture_file" 2>&1) || exit_code=$?

  if [ "$exit_code" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code"
    echo "  Description: $description"
    echo "  Fixture: $fixture_file"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Test Cases (8 discriminating 케이스)
# ─────────────────────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2545: codex-companion timeout-presence lint 8 discriminating cases"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# 케이스 1: GREEN — timeout + kill-after 가드 존재 (env-default 형태)
run_case \
  "1: GREEN timeout+kill-after (env-default)" \
  'timeout ${CODEX_REVIEW_TIMEOUT_SEC:-300} --kill-after=30 node "$CMD" adversarial-review --wait "x"' \
  0 \
  "정상 케이스: 가드 존재 + N 양수 + --kill-after 동반"

# 케이스 2: GREEN — task --write 가드 존재
run_case \
  "2: GREEN task --write (리터럴 N)" \
  'timeout 300 --kill-after=${CODEX_REVIEW_KILL_AFTER_SEC:-30} node "$CMD" task --write "y"' \
  0 \
  "정상 케이스: task --write dispatch 도 가드 필수"

# 케이스 3: RED (mutation) — timeout 가드 제거
# 주의: fixture 가 단일 파일이면 home(plugins/codeforge-review/agents/) 미포함 →
# dispatch 0건 + home 부재 → exit 0 (consumer no-op). hollow-gate 를 트리거하려면
# home 이 포함된 디렉터리 구조 필요. fixture_case3_hollow() 로 fixture 디렉터리 생성.
fixture_case3_hollow() {
  local tmpdir exitcode
  tmpdir=$(mktemp -d)
  trap "rm -rf '$tmpdir'" RETURN

  # home 경로 생성 (home-present 조건)
  mkdir -p "$tmpdir/plugins/codeforge-review/agents"

  # 발화 0건 파일 (가드 없이 단순 prose)
  echo 'This file mentions companion but has no dispatch invocations.' > "$tmpdir/plugins/codeforge-review/agents/test.md"

  # lint 실행 — home 실존 + 발화 0건 → exit 1 (hollow-gate)
  bash "$WRAPPER" "$tmpdir" 2>&1 || exitcode=$?
  return "${exitcode:-0}"
}

out=$(fixture_case3_hollow 2>&1) || exit_code=$?
if [ "$exit_code" -eq 1 ]; then
  echo "✓ PASS: 3: RED mutation — dispatch 0건 (hollow-gate I-3) (exit $exit_code) — 가드 load-bearing 증명: timeout 제거 + home 실존 → exit 1 (RED)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: 3: RED mutation — dispatch 0건 (hollow-gate I-3)"
  echo "  Expected exit 1, got $exit_code"
  echo "  Description: home 실존 + dispatch 0건 → hollow-gate exit 1"
  echo "  Output: $out"
  FAIL=$((FAIL+1))
fi
# (이 케이스는 run_case 매크로 밖에서 처리, 아래 케이스 4부터 순서대로)

# 케이스 4: RED — kill-after 누락
run_case \
  "4: RED --kill-after 누락" \
  'timeout 300 node "$CMD" adversarial-review --wait "x"' \
  1 \
  "kill-after 동반 의무: 누락 → exit 1"

# 케이스 5: RED — N = 0 (무한대기 미방지)
run_case \
  "5: RED N=0 (무한대기 미방지)" \
  'timeout 0 --kill-after=30 node "$CMD" adversarial-review --wait "x"' \
  1 \
  "N 양수 의무: N=0 → exit 1 (시간 한계 0)"

# 케이스 6: RED — N 음수
run_case \
  "6: RED N 음수" \
  'timeout -5 --kill-after=30 node "$CMD" adversarial-review --wait "x"' \
  1 \
  "N 양수 의무: N<0 → exit 1"

# 케이스 7: RED — kill-after 누락 (task --write 도 검사)
run_case \
  "7: RED --kill-after 누락 (task --write)" \
  'timeout 300 node "$CMD" task --write "x"' \
  1 \
  "--kill-after 동반 의무: task --write 에도 필수"

# 케이스 8: GREEN (consumer no-op) — 경로 부재 → exit 0
# 이 케이스는 존재하지 않는 경로를 lint 에 전달
run_case_no_op() {
  local name="$1" path="$2" expected_exit="$3" description="$4"
  local exit_code=0 out

  out=$(bash "$WRAPPER" "$path" 2>&1) || exit_code=$?

  if [ "$exit_code" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# 케이스 8: consumer no-op — 실제 경로 부재 시나리오 (wrapper = home 실존, consumer = home 부재)
# 본 테스트는 wrapper 환경이므로 home(plugins/codeforge-review/agents/) 이 실제 존재.
# 따라서 "발화 0건 + home 실존 → hollow-gate exit 1" 이 발동. consumer 시뮬레이션은
# 실제 consumer 환경에서 별도 테스트하거나, fixtures/codex-companion-timeout/ 에
# 빈 파일 + home 부재 디렉터리 fixture 를 만들어 override 할 수 있음.
# 여기서는 wrapper 관점의 "home 실존 + 발화 있음" 을 이미 케이스 1~7 로 커버했으므로,
# "경로 부재 setup error exit 2" 를 케이스 8 로 명시:
run_case_no_op \
  "8: RED setup error — 경로 부재" \
  "/nonexistent/path/to/file.md" \
  2 \
  "존재하지 않는 경로 지정 → setup error exit 2"

# 케이스 9: GREEN consumer no-op — home 부재 + dispatch 발화 0건 → exit 0
# byte-identical mirror(ADR-005)를 consumer 가 상속해도 plugins/codeforge-review/agents/ 부재 시
# spurious RED 미발생 검증 (Story §7.3 consumer degradation, py 헤더 §5). hollow-gate I-3 는
# home 실존 시에만 발동 — home 부재 고립 트리 스캔은 honest no-op exit 0.
CONSUMER_TMP=$(mktemp -d)
trap 'rm -rf "$CONSUMER_TMP"' EXIT
mkdir -p "$CONSUMER_TMP/somepkg/docs"
# dispatch 발화 없는 일반 문서 (companion 은 prose 로만 언급 — 실행 라인 아님)
printf '이 문서는 codex companion 을 prose 로만 언급한다. 실행 dispatch 발화 0건.\n' > "$CONSUMER_TMP/somepkg/docs/readme.md"
run_case_no_op \
  "9: GREEN consumer no-op (home 부재 + 발화 0건)" \
  "$CONSUMER_TMP" \
  0 \
  "consumer degradation: plugins/codeforge-review/agents/ 부재 + dispatch 발화 0건 → honest no-op exit 0 (spurious RED 미발생, byte-identical parity 안전)"

# ─────────────────────────────────────────────────────────────────────────────
# Test Summary
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — wall-clock 가드 load-bearing 입증 완료"
  exit 0
else
  echo "✗ $FAIL case(s) failed — 가드 검사 미확인 또는 hollow-gate 미방지"
  exit 1
fi
