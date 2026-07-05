#!/usr/bin/env bash
# tests/scripts/test_check-subagent-wait-liveness-presence.sh
# CFP-2549 Phase 2 (구현 lane) — Discriminating self-test for
#   scripts/lib/check_subagent_wait_liveness_presence.py wall-clock 가드 presence lint.
#
# 배경: 모든 background subagent 대기 dispatch(run_in_background | bg spawn) 는
#   항상 **runnable option-first** 가드 `timeout --kill-after=<K> <N>` 로 감싸야 함 (ADR-139 §결정 4 2안).
#   ★ GNU coreutils 는 duration-first `timeout <N> --kill-after=<K> cmd` 에서 `--kill-after` 를
#     실행할 명령으로 오인 → exit 127 (가드 무효). option 은 duration 앞에 와야 함.
#   [verified: coreutils 8.32 — timeout 1 --kill-after=1 sleep 5 → 127 / timeout --kill-after=1 1 sleep 5 → 124]
#
# 2-축 결박 (CFP-2545 P0 재발 방지 — presence-only 금지):
#   축 A (grep oracle) : lint 가 option-first 만 PASS · duration-first 는 RED 로 판별하는가.
#   축 B (execution)   : 실제 `timeout` 실행이 correct form → exit 124 / broken form → exit 127 인가.
#   grep oracle 을 런타임 진실에 결박 — 문자열 존재만으로는 "실행 가능"을 보증 못함.
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

# Windows 로컬 견고성: python helper stdout 를 utf-8 로 고정 (CI=Linux 는 utf-8 기본).
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-subagent-wait-liveness-presence.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# 축 A: grep-oracle 케이스 (fixture text → lint → exit code assert)
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" fixture_text="$2" expected_exit="$3" description="$4"
  local exit_code=0 out fixture_file
  fixture_file="$(mktemp --suffix=.md)"
  # shellcheck disable=SC2064
  trap "rm -f '$fixture_file'" RETURN
  printf '%s\n' "$fixture_text" > "$fixture_file"
  out=$(bash "$WRAPPER" "$fixture_file" 2>&1) || exit_code=$?
  if [ "$exit_code" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# home-present 트리 케이스 (hollow-gate I-3 / consumer no-op 판별용)
run_tree_case() {
  local name="$1" expected_exit="$2" description="$3" home_present="$4" file_text="$5"
  local exit_code=0 out tmpdir
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  if [ "$home_present" = "yes" ]; then
    mkdir -p "$tmpdir/docs"
    printf '%s\n' "$file_text" > "$tmpdir/docs/orchestrator-playbook.md"
  else
    mkdir -p "$tmpdir/somepkg/docs"
    printf '%s\n' "$file_text" > "$tmpdir/somepkg/docs/readme.md"
  fi
  out=$(bash "$WRAPPER" "$tmpdir" 2>&1) || exit_code=$?
  if [ "$exit_code" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2549: subagent-wait-liveness-presence lint — 축 A (grep oracle)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# 1: GREEN — option-first (env-default) 가드 존재 (run_in_background)
run_case "A1: GREEN option-first (env-default) run_in_background" \
  'timeout --kill-after=${SUBAGENT_KILL_AFTER_SEC:-30} ${SUBAGENT_MAX_WAIT_SEC:-180} run_in_background worker --spawn "x"' \
  0 "runnable option-first: --kill-after 가 duration 앞. 가드 유효"

# 2: GREEN — option-first (리터럴) bg spawn
run_case "A2: GREEN option-first (리터럴) bg spawn" \
  'timeout --kill-after=30 180 bg spawn worker --task "y"' \
  0 "bg spawn dispatch 도 runnable option-first 가드 필수"

# 3: RED — duration-first 오배열 (broken, GNU timeout exit 127)
run_case "A3: RED duration-first 오배열 with run_in_background" \
  'timeout ${SUBAGENT_MAX_WAIT_SEC:-180} --kill-after=30 run_in_background worker --spawn "x"' \
  1 "duration-first = GNU timeout exit 127 가드 무효 → lint RED (runnable 강제)"

# 4: RED — duration-first 리터럴 (broken)
run_case "A4: RED duration-first 리터럴 with bg spawn" \
  'timeout 180 --kill-after=30 bg spawn worker --task "y"' \
  1 "duration-first 리터럴도 broken → lint RED"

# 5: RED (mutation) — timeout 가드 완전 제거
run_case "A5: RED mutation — 가드 제거 (run_in_background)" \
  'run_in_background worker --spawn "x"' \
  1 "가드 load-bearing 증명: timeout 제거 → lint RED (A1 ↔ A5 diff)"

# 6: RED — N=0 (option-first 형태이나 무한대기 미방지)
run_case "A6: RED N=0 (무한대기 미방지)" \
  'timeout --kill-after=30 0 run_in_background worker --spawn "x"' \
  1 "N(duration)=0 → 양수 의무 위반 → lint RED"

# 7: RED — --kill-after 누락 (option 부재, orphan 위험)
run_case "A7: RED --kill-after 누락" \
  'timeout 180 run_in_background worker --spawn "x"' \
  1 "--kill-after 부재 = detached subagent 좀비 위험 + 가드 불완전 → lint RED"

# 8: RED (mutation) — bg spawn 가드 제거
run_case "A8: RED mutation — 가드 제거 (bg spawn)" \
  'bg spawn worker --task "y"' \
  1 "bg spawn 가드 제거도 RED (A2 ↔ A8 diff)"

# 9: RED — hollow-gate I-3 (home 실존 + dispatch 발화 0건)
run_tree_case "A9: RED hollow-gate I-3 (home 실존 + 발화 0건)" \
  1 "home 실존하나 dispatch 발화 0건 → 발화가 스코프 이탈 가능 → exit 1 (항상 GREEN 방지)" \
  yes "이 파일에는 background-wait 규약 발화가 없다 — subagent 대기는 prose 로만 언급."

# 10: GREEN — consumer no-op (home 부재 + 발화 0건)
run_tree_case "A10: GREEN consumer no-op (home 부재)" \
  0 "consumer degradation: docs/orchestrator-playbook.md 부재 → honest no-op exit 0 (spurious RED 미발생, byte-identical parity 안전)" \
  no "이 문서는 subagent dispatch 를 prose 로만 언급. 실행 규약 발화 0건."

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " 축 B (execution-backed) — grep oracle 을 런타임 진실에 결박"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

exec_case() {
  local name="$1" expected_exit="$2" description="$3"; shift 3
  local exit_code=0
  if ! command -v timeout >/dev/null 2>&1; then
    echo "↷ SKIP: $name — timeout 미설치 (POSIX 부재 환경, CI=Linux 는 실행)"
    return
  fi
  "$@" >/dev/null 2>&1 || exit_code=$?
  if [ "$exit_code" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code — $description"
    FAIL=$((FAIL+1))
  fi
}

# B1: correct option-first form → 실제 timeout kill → exit 124
exec_case "B1: exec option-first → exit 124 (timeout kill)" \
  124 "runnable 형태가 실제로 wall-clock kill 을 수행" \
  timeout --kill-after=1 1 sleep 5

# B2: broken duration-first form → GNU timeout 이 --kill-after 를 명령으로 오인 → exit 127
exec_case "B2: exec duration-first → exit 127 (broken, 가드 무효)" \
  127 "duration-first = --kill-after 를 실행 명령으로 오인 → 가드 무효(127). lint RED 의 런타임 근거" \
  timeout 1 --kill-after=1 sleep 5

# B3: 원 reproducer (Story §6.2 원 버그 형태) → exit 127 (원 버그 재현)
exec_case "B3: exec 원 reproducer (180 --kill-after=30) → exit 127" \
  127 "원 버그 형태 재현 — dispatch 가 원래 duration-first 였으면 가드 무효였음" \
  timeout 180 --kill-after=30 sleep 1

# ─────────────────────────────────────────────────────────────────────────────
# CFP-2573 AC-3 확장: delivery-gap detection dimension (기존 timeout-guard 케이스 무손상 추가)
#   playbook §3.10.1 delivery-gap 규율 anchor(spawn-then-blind-wait 금지 + force-resume + lead-collect)
#   존재 시 GREEN / anchor 삭제 mutation → exit 1 (RED). L3 detection liveness 실증
#   (force-resume/규율 delete → presence-lint RED). base(timeout-guard) 축과 격리해 dimension 만 검증.
# distinct-marker: delivery-gap RED 는 stdout 마커 'delivery-gap' 병행 assert (dimension 발동 확증).
# ─────────────────────────────────────────────────────────────────────────────

# playbook fixture(임의 content) → wrapper dir 스캔 → exit + delivery-gap 마커 대조
run_dg_case() {  # run_dg_case <name> <expected_exit> <marker> <playbook_content>
  local name="$1" expected_exit="$2" marker="$3" content="$4"
  local exit_code=0 out tmpdir ok_mark=0
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  mkdir -p "$tmpdir/docs"
  printf '%s\n' "$content" > "$tmpdir/docs/orchestrator-playbook.md"
  out=$(bash "$WRAPPER" "$tmpdir" 2>&1) || exit_code=$?
  case "$out" in *"$marker"*) ok_mark=1;; esac
  if [ "$exit_code" -eq "$expected_exit" ] && [ "$ok_mark" -eq 1 ]; then
    echo "✓ PASS: $name (exit $exit_code + marker '$marker')"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit + marker '$marker', got exit $exit_code mark=$ok_mark"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# 실 playbook 복사본(선택 mutation) → wrapper dir 스캔 (실 content 기반 discriminating)
run_dg_realcopy() {  # run_dg_realcopy <name> <expected_exit> <marker> <strip_token|"">
  local name="$1" expected_exit="$2" marker="$3" strip_token="${4:-}"
  local exit_code=0 out tmpdir ok_mark=0
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  mkdir -p "$tmpdir/docs"
  cp "$REPO_ROOT/docs/orchestrator-playbook.md" "$tmpdir/docs/orchestrator-playbook.md"
  if [ -n "$strip_token" ]; then
    python3 - "$tmpdir/docs/orchestrator-playbook.md" "$strip_token" <<'PY'
import sys
f, tok = sys.argv[1], sys.argv[2]
t = open(f, encoding="utf-8").read()
open(f, "w", encoding="utf-8").write(t.replace(tok, ""))
PY
  fi
  out=$(bash "$WRAPPER" "$tmpdir" 2>&1) || exit_code=$?
  case "$out" in *"$marker"*) ok_mark=1;; esac
  if [ "$exit_code" -eq "$expected_exit" ] && [ "$ok_mark" -eq 1 ]; then
    echo "✓ PASS: $name (exit $exit_code + marker '$marker')"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit + marker '$marker', got exit $exit_code mark=$ok_mark"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2573 AC-3 확장: delivery-gap detection dimension (§3.10.1 규율 anchor)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# DG1: GREEN 합성 — dispatch+guard(base pass) + delivery-gap anchor 3종 존재
run_dg_case "DG1: GREEN 합성 (delivery-gap anchor 3종 존재)" 0 "PASS" \
  'timeout --kill-after=30 300 run_in_background worker  # max-wait wall-clock ceiling liveness
PL 은 spawn-then-blind-wait 금지 — 수집은 lead. stall 시 lead force-resume. named lead-collect routine.'

# DG2: RED 합성 — 동일 base(dispatch+guard, base PASS) 이나 delivery-gap anchor 0건 → exit 1 (dimension 격리)
run_dg_case "DG2: RED 합성 (anchor 삭제 mutation → delivery-gap RED)" 1 "delivery-gap" \
  'timeout --kill-after=30 300 run_in_background worker  # max-wait wall-clock ceiling liveness
이 문단엔 background-wait 규약만 있고 delivery-gap 규율 anchor 가 없다.'

# DG3: GREEN 실 playbook 복사본 (실 content — anchor 존재 + base pass)
run_dg_realcopy "DG3: GREEN 실 playbook 복사본 (anchor 존재)" 0 "PASS" ""

# DG4: RED 실 playbook 복사본에서 force-resume anchor strip → delivery-gap RED (실 content mutation)
run_dg_realcopy "DG4: RED 실 playbook — force-resume anchor strip → delivery-gap RED" 1 "delivery-gap" "force-resume"

# ─────────────────────────────────────────────────────────────────────────────
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — runnable option-first 가드 load-bearing + 실행 축 결박 입증"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
