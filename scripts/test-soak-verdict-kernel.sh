#!/usr/bin/env bash
# scripts/test-soak-verdict-kernel.sh — fixture-daemon self-test (표면 B 게이트 메커니즘 dogfood)
#
# CFP-2613 (Epic CFP-2602 G2) / ADR-148 §결정3(verdict-kernel)/§결정5(생존∧sink AND)/§결정7(boot-grace)
#   + ADR-136 결정14 execution-liveness L3 (RED→GREEN + mutation-kill).
#
# wrapper runtime-0 딜레마 해소: wrapper 는 실 데몬이 없다 → 게이트 메커니즘(verdict-kernel +
#   soak-runner)을 fixture-daemon 으로 dogfood. 실 soak 아님(AC-8 declared 실행축 wrapper-side 검증채널).
#
# 9-시나리오(§8.1) 중 soak-runner 축 담당 (표면 A 축 = test-check-operational-outcome-signal.sh):
#   #1 정상 PASS · #2 크래시 FAIL · #3 1-restart FAIL(=CARRIER: crash-but-sink-advances) ·
#   #4 flat-sink FAIL · #5 역행-sink FAIL · #8 slow-boot PASS(boot-grace, grace=∞ mutation→RED)
#
# 2 축:
#   (1) kernel unit — evaluate_soak_sample 6 reason-code discriminating.
#   (2) soak-runner integration + mutation-kill — 생존축(F1)/sink축/boot-grace 가드 load-bearing 실증.
#       mutant 에서 위반 fixture 가 통과하면(생존) = hollow → self-test FAIL.
#
# Exit code: 0 (all pass) / 1 (any fail). hermetic — network 0 · real deps 0.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KERNEL="$REPO_ROOT/scripts/lib/soak-verdict-kernel.sh"
RUNNER="$REPO_ROOT/scripts/soak-runner.sh"

PASS=0
FAIL=0
ok()  { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "✗ FAIL: $1"; [ -n "${2:-}" ] && echo "    $2"; FAIL=$((FAIL+1)); }

# soak 창 파라미터 (CI 속도 vs 타이밍 견고성 균형). soak-runner grace 비교 = 정수초(date +%s)
# granularity → slow-boot(t≈0 exit) 와 death(t≈3) 를 grace=2 양쪽에 명확 분리(경계 straddle 방지).
GRACE=2; WINDOW=5; POLL=0.3

# ── 축 1: kernel unit (6 reason-code) ────────────────────────────────────────
# shellcheck source=scripts/lib/soak-verdict-kernel.sh
. "$KERNEL"
kunit() { # desc | args... | expected
  local desc="$1"; shift; local exp="${!#}"; set -- "${@:1:$(($#-1))}"
  local got; got="$(evaluate_soak_sample "$@")"
  if [ "$got" = "$exp" ]; then ok "kernel: $desc ($* -> $got)"; else bad "kernel: $desc" "expected $exp got $got ($*)"; fi
}
echo "── 축 1: verdict-kernel unit ──"
kunit "역행"          5 3 0 0  1800 0 FAIL_REGRESSION
kunit "임계 도달"      5 9 0 8  1800 0 PASS_THRESHOLD
kunit "floor freeze"   5 5 5 0  1800 1 FAIL_FREEZE
kunit "floor pass"     5 6 5 0  1800 1 PASS_FLOOR
kunit "threshold miss" 5 5 0 8  1800 1 FAIL_THRESHOLD_MISS
kunit "continue"       5 7 0 8  1800 0 CONTINUE
kunit "no-prev"       -1 0 -1 0 1800 0 CONTINUE

# ── fixture-daemon command 빌더 (hermetic temp state) ───────────────────────
# 각 fixture: 임시 dir 의 SINK/MARKER 파일로 데몬 거동 제어. soak-runner 가 eval 하므로
# 명령 문자열에 실 경로를 리터럴 삽입 (env leak 0).
build_fixture() { # name -> echoes "DAEMON_CMD|||SINK_CMD" using $TDIR
  local name="$1" S="$TDIR/sink" M="$TDIR/marker"
  case "$name" in
    normal)     echo "while true; do n=\$(cat '$S' 2>/dev/null||echo 0); echo \$((n+1)) > '$S'; sleep 0.2; done|||cat '$S' 2>/dev/null" ;;
    crash)      echo "sleep 3; exit 1|||echo 0" ;;
    restart)    echo "if [ ! -f '$M' ]; then touch '$M'; sleep 3; exit 1; else while true; do n=\$(cat '$S' 2>/dev/null||echo 0); echo \$((n+1)) > '$S'; sleep 0.2; done; fi|||cat '$S' 2>/dev/null" ;;
    flat)       echo "while true; do echo 5 > '$S'; sleep 0.2; done|||cat '$S' 2>/dev/null" ;;
    reverse)    echo "echo 100 > '$S'; while true; do n=\$(cat '$S' 2>/dev/null||echo 100); echo \$((n-1)) > '$S'; sleep 0.3; done|||cat '$S' 2>/dev/null" ;;
    slowboot)   echo "if [ ! -f '$M' ]; then touch '$M'; exit 1; else while true; do n=\$(cat '$S' 2>/dev/null||echo 0); echo \$((n+1)) > '$S'; sleep 0.2; done; fi|||cat '$S' 2>/dev/null" ;;
  esac
}

# run_one <runner> <name> <grace> -> echoes "RESULT... <exit>" (RESULT 라인 + exit code)
run_one() {
  local runner="$1" name="$2" grace="$3"
  TDIR="$(mktemp -d)"
  local spec dcmd scmd rc out
  spec="$(build_fixture "$name")"
  dcmd="${spec%%|||*}"; scmd="${spec##*|||}"
  rc=0
  out="$(bash "$runner" "$dcmd" "$scmd" "$grace" 0 "$WINDOW" "$POLL" 2>/dev/null)" || rc=$?
  rm -rf "$TDIR"
  echo "${out}|EXIT=${rc}"
}

# assert_fixture <runner> <name> <grace> <exp_verified> <exp_exit> <label>
# 반환: 0 = 기대 일치 / 1 = 불일치.
assert_fixture() {
  local runner="$1" name="$2" grace="$3" exp_v="$4" exp_e="$5" label="$6"
  local res verified ecode
  res="$(run_one "$runner" "$name" "$grace")"
  verified="$(sed -nE 's/.*soak_verified=([a-z]+).*/\1/p' <<<"$res")"
  ecode="$(sed -nE 's/.*EXIT=([0-9]+).*/\1/p' <<<"$res")"
  if [ "$verified" = "$exp_v" ] && [ "$ecode" = "$exp_e" ]; then
    [ "$label" = "GREEN" ] && ok "soak-runner: $name -> soak_verified=$verified exit=$ecode (기대 일치)"
    return 0
  else
    [ "$label" = "GREEN" ] && bad "soak-runner: $name" "expected verified=$exp_v exit=$exp_e; got verified=$verified exit=$ecode; RESULT=[$res]"
    return 1
  fi
}

echo ""
echo "── 축 2a: soak-runner GREEN suite (fixture-daemon) ──"
# name grace exp_verified exp_exit
assert_fixture "$RUNNER" normal   "$GRACE" true  0 GREEN   # #1 정상
assert_fixture "$RUNNER" crash    "$GRACE" false 1 GREEN   # #2 크래시 (survival=false)
assert_fixture "$RUNNER" restart  "$GRACE" false 1 GREEN   # #3 1-restart = CARRIER (crash∧sink advances)
assert_fixture "$RUNNER" flat     "$GRACE" false 1 GREEN   # #4 flat-sink (FAIL_FREEZE)
assert_fixture "$RUNNER" reverse  "$GRACE" false 1 GREEN   # #5 역행 (FAIL_REGRESSION)
assert_fixture "$RUNNER" slowboot "$GRACE" true  0 GREEN   # #8 slow-boot (grace 내 exit → 미카운트 → PASS)

# CARRIER 명시 검증: restart fixture 는 sink 는 전진(sink_monotone_progressed=true)하나
# 생존축(survival=false)만으로 soak_verified=false — 사용자 원 carrier(crash-but-sink-advances) 재현.
carrier_res="$(run_one "$RUNNER" restart "$GRACE")"
carrier_surv="$(sed -nE 's/.*survival=([a-z]+).*/\1/p' <<<"$carrier_res")"
carrier_sink="$(sed -nE 's/.* sink_monotone_progressed=([a-z]+).*/\1/p' <<<"$carrier_res")"
if [ "$carrier_surv" = "false" ] && [ "$carrier_sink" = "true" ]; then
  ok "CARRIER(F1): restart fixture survival=false ∧ sink_monotone_progressed=true → 생존축 독립 FAIL (사용자 carrier 재현)"
else
  bad "CARRIER(F1) 미재현" "survival=$carrier_surv sink_monotone=$carrier_sink (RESULT=[$carrier_res])"
fi

echo ""
echo "── 축 2b: mutation-kill (가드 load-bearing 실증) ──"
# mutant 에서 특정 위반 fixture 가 통과(soak_verified=true or exit 0)하면 mutation 생존 = hollow.
# ★ mutant 은 temp dir 에 놓이므로 $SCRIPT_DIR/lib/... 상대 resolve 가 깨진다 → KERNEL_PATH 배정 라인
#   전체를 절대경로로 치환(그 위에 mutation $1 적용). `^KERNEL_PATH=.*` 로 라인 통째 치환 —
#   `\$SCRIPT_DIR/...` 매칭은 sed 가 `$` 를 anchor 로 오해 partial-match(=kernel 부재 exit2 no-op 오판).
#   미치환 시 SETUP_ERROR(exit2)=mutation no-op → positive-leak 단정이 이를 정확히 검출(F-CR-004).
mut_runner() { sed -E "s#^KERNEL_PATH=.*#KERNEL_PATH=\"$KERNEL\"#; $1" "$RUNNER" > "$2"; }
mut_kernel() { sed -E "$1" "$KERNEL" > "$2"; }

# assert_leak <runner> <name> <grace>: mutant 이 실제로 새는지 POSITIVE 단정 (verified=true ∧ exit=0).
#   반환 0 = leak 확인(mutation killed) / 1 = leak 안 함(mutation 생존 or no-op). exit=2(SETUP_ERROR) 오수용 방지.
assert_leak() {
  local res v e
  res="$(run_one "$1" "$2" "$3")"
  v="$(sed -nE 's/.*soak_verified=([a-z]+).*/\1/p' <<<"$res")"
  e="$(sed -nE 's/.*EXIT=([0-9]+).*/\1/p' <<<"$res")"
  [ "$v" = "true" ] && [ "$e" = "0" ]
}

# Mut-A: 생존축 무력화 (post-grace death_count 증가 제거) → restart(CARRIER) fixture 가
#        survival=true 로 새어 soak_verified=true → assertion(verified=false) 깨짐 → killed. (F1 핵심)
MUT="$(mktemp)"
mut_runner 's/death_count=\$\(\( death_count \+ 1 \)\)/death_count=$(( death_count + 0 ))/' "$MUT"
chmod +x "$MUT"
# F-CR-004: POSITIVE leak 단정 (verified=true ∧ exit=0) — no-op/SETUP_ERROR(exit2) 를 killed 로 오수용 금지.
if assert_leak "$MUT" restart "$GRACE"; then
  ok "mutation killed: 생존축(death_count) 무력화 — restart(CARRIER) 가 mutant 에서 verified=true∧exit=0 실제 leak (F1 생존축 load-bearing 실증)"
else
  bad "mutation NOT positively leaking: 생존축(death_count)" "restart 가 mutant 에서 verified=true∧exit=0 로 새지 않음 (no-op/미격리) — 생존축 load-bearing 미실증"
fi
rm -f "$MUT"

# Mut-B: sink 축 무력화 (kernel 이 항상 PASS_FLOOR 반환) → flat/reverse 가 sink_prog=true →
#        survival=true 와 결합해 soak_verified=true → assertion 깨짐 → killed.
MUTK="$(mktemp)"; MUTR="$(mktemp)"
mut_kernel 's/printf '"'"'%s\\n'"'"' "FAIL_FREEZE"/printf '"'"'%s\\n'"'"' "PASS_FLOOR"/; s/printf '"'"'%s\\n'"'"' "FAIL_REGRESSION"/printf '"'"'%s\\n'"'"' "PASS_FLOOR"/' "$MUTK"
# runner 가 MUTK(변이 kernel)를 source 하도록 KERNEL_PATH 라인 통째 치환 (partial-match 회피).
sed -E "s#^KERNEL_PATH=.*#KERNEL_PATH=\"$MUTK\"#" "$RUNNER" > "$MUTR"; chmod +x "$MUTR"
# F-CR-004: flat/reverse 가 변이 kernel 에서 POSITIVE leak(verified=true∧exit=0)하는지 단정.
if assert_leak "$MUTR" flat "$GRACE" && assert_leak "$MUTR" reverse "$GRACE"; then
  ok "mutation killed: sink 축(kernel FAIL_FREEZE/FAIL_REGRESSION→PASS_FLOOR) 무력화 — flat/reverse 가 verified=true∧exit=0 실제 leak (sink 축 load-bearing 실증)"
else
  bad "mutation NOT positively leaking: sink 축 무력화" "flat/reverse 가 변이 kernel 에서 verified=true∧exit=0 로 새지 않음 (kernel 재사용 배선/no-op 확인)"
fi
rm -f "$MUTK" "$MUTR"

# Mut-C: boot-grace 상한 가드(2*grace≥floor 차단, §결정7 ≤soak/2) 무력화 → restart(CARRIER) 를 grace=WINDOW 로.
#        restart = 생존축만 실패(sink 는 전진). grace=∞ 로 post-grace death 가 "grace 내"로 은폐 →
#        survival=true ∧ sink_prog=true → soak_verified 오PASS. mutation = 2*grace 를 0*grace 로 만들어
#        (0 ≥ floor 항상 false) 가드 무력화 (guard 표현식 정확 매치 불요 — unique substring 'BOOT_GRACE_S * 2').
#        (crash fixture 는 sink 도 frozen 이라 sink 축이 여전히 잡음 → grace 가드 격리 불가 → restart 사용.)
MUTC="$(mktemp)"
mut_runner 's/BOOT_GRACE_S \* 2/BOOT_GRACE_S \* 0/' "$MUTC"
chmod +x "$MUTC"
# F-CR-004: mutant 이 실제로 새는지 POSITIVE 단정 (verified=true ∧ exit=0). exit=2(SETUP_ERROR = mutation
#   unapplied/no-op) 를 killed 로 오수용 금지 — no-op 이면 원본 가드가 grace=WINDOW 를 cfg_error(exit2) 차단.
if assert_leak "$MUTC" restart "$WINDOW"; then
  ok "mutation killed: boot-grace 상한 가드 무력화 — restart(CARRIER) 가 grace=∞ 로 death 은폐되어 verified=true∧exit=0 실제 leak (positive 단정, F-CR-004)"
else
  bad "mutation NOT positively leaking: boot-grace 가드" "restart 가 mutant 에서 verified=true∧exit=0 로 새지 않음 (exit=2 면 mutation no-op/가드 격리 실패)"
fi
rm -f "$MUTC"

# grace 상한 가드 GREEN #1: grace=WINDOW → 2*WINDOW≥WINDOW cfg_error(exit2) 차단.
gi_res="$(run_one "$RUNNER" normal "$WINDOW")"
if grep -q "reason=SETUP_ERROR" <<<"$gi_res" && grep -q "EXIT=2" <<<"$gi_res"; then
  ok "boot-grace 상한 가드 GREEN(grace=window): 2*grace≥floor → cfg_error(exit2) fail-closed (§결정7)"
else
  bad "boot-grace 상한 가드 미작동(grace=window)" "차단되지 않음 (RESULT=[$gi_res])"
fi

# grace 상한 가드 GREEN #2 (F-CR-001 강화 load-bearing): grace=3, window=5 (floor/2 < grace < floor).
#   구 약한 가드(grace≥floor: 3≥5 false)라면 통과했을 값이나, 정본 강화 가드(2*3=6≥5 true)는 cfg_error 로 차단.
#   → 이 assertion 이 GREEN 이면 가드가 ≤soak/2 정본대로 강화됨을 실증(구 가드로 회귀 시 RED).
b_res="$(run_one "$RUNNER" normal 3)"   # grace=3, WINDOW=5
if grep -q "reason=SETUP_ERROR" <<<"$b_res" && grep -q "EXIT=2" <<<"$b_res"; then
  ok "boot-grace ≤soak/2 강화 GREEN(grace=3,window=5): 2*grace≥floor 로 차단 (구 grace≥floor 약한 가드면 통과 = 회귀 검출, F-CR-001)"
else
  bad "boot-grace 강화 가드 미작동(grace=3,window=5)" "정본 ≤soak/2(2*grace≥floor) 미적용 — 구 약한 가드 잔존 의심 (RESULT=[$b_res])"
fi

echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"
if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (kernel unit + soak-runner GREEN + 생존축/sink축/boot-grace mutation killed — 게이트 메커니즘 discriminating 실증, INV-D3 생존∧sink AND)"
  exit 0
else
  echo "Some tests failed (게이트 메커니즘 hollow 또는 분류 오류)"
  exit 1
fi
