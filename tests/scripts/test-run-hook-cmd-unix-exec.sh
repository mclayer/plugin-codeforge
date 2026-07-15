#!/usr/bin/env bash
# tests/scripts/test-run-hook-cmd-unix-exec.sh
# CFP-2702 Phase 2 (구현 lane) — AC-5 회귀 테스트
#   symbol: test_run_hook_cmd_unix_exec_dispatch
#
# 대상: hooks/run-hook.cmd 의 exec-first 폴리글롯 line 1 (양 파서 분기점, 순수 ASCII):
#   :; f="$1"; shift; exec bash "$(dirname "$0")/$f" "$@" #
#   [POSIX] : no-op → exec bash <자기dir>/$f "$@"; 후행 '#' 주석이 line1 후행 CR(\r) 흡수.
#   [cmd.exe] : 라벨 스킵 → line 2+ 배치 본문 실행.
#
# ★ discriminating (hollow-gate 아님) 증명 — 아래 3축이 함께여야 GREEN 의미가 성립:
#   (1) 정상 PASS  : exec-first 형태가 payload/args 를 충실히 전달 (happy path + CR-leak-0).
#   (2) 결함 재현 RED: CR-민감 POSIX bash 에서
#         · D1 구(舊) heredoc 폴리글롯(`: << 'CMDBLOCK'`)을 CRLF 로 만들면 여는 구분자·종료자 둘 다
#           `CMDBLOCK\r` = 대칭 → heredoc 은 정상 종료되나, 종료 직후 하단 bash 본문의 후행 CR 이
#           `$'\r': command not found`(비정상 exit) + exec 대상 경로 CR-오염 → payload 미방출 =
#           **loud 실패**. 동일 fixture 를 LF 로 두면 exit0+payload 출력(regression-guard) — CRLF 가
#           원인임을 결박. (구 주석의 "heredoc 미종료→silent no-op" 은 실측과 다름: Codex EXP-2 는
#           uniformly-CRLF 폴리글롯이 Linux 에서 loud 실패(exit 127, `$'\r': command not found`)임을 확인.)
#         · D2 현 line1 에서 후행 '#' 가드를 제거한 CRLF 변종은 마지막 인자에 \r 누출(beta\r).
#           현 '#'-가드 파일은 누출 0(위 CR-leak-0) — '#' 가드가 load-bearing 임을 대조.
#   (3) 정밀도    : 인자 정확 전달 `[alpha][beta]` (부분/오염 없이).
#
# ★★ 정직 degrade (packet §6 Fact 2): msys2/Git Bash 는 CR 을 관대 처리해 (1) heredoc 종료구분자
#   매칭에서 후행 CR 을 무시하고 (2) 스크립트 read 시 각 줄 CR 를 제거한다 → D1(loud CR-오염)·D2(인자
#   CR 누출) 결함이 마스킹되어 false-GREEN 위험. 따라서 D1/D2 는 **런타임 CR-민감성 probe**(비대칭
#   heredoc — 아래 bash_is_cr_sensitive)로 게이팅하여, CR-관대(msys) 환경에서는 SKIP(사유 stdout 명시)
#   하고 절대 PASS 로 세지 않는다. 실 kill 은 CR-민감(Linux 시스템 bash)에서 이뤄진다 — probe 가 CR-민감
#   으로 판정하면 D1/D2 가 실제 실행되어 결함을 kill 한다. Git Bash 통과를 근거로 GREEN 단정 금지.
#
# self-contained bash (tests/scripts 관례, 네트워크 0). subprocess fork 판정은 exit code 단독이
#   아니라 도메인 stdout sentinel(PAYLOAD_SENTINEL_*) 병행 assert 로 확증 (fork 진정성).
#
# Exit code: 0 = 전 케이스 PASS(SKIP 은 실패 아님), 1 = 1+ 실패.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_HOOK="$REPO_ROOT/hooks/run-hook.cmd"

PASS=0
FAIL=0
SKIP=0

WORK="$(mktemp -d)"
# shellcheck disable=SC2064
trap "rm -rf '$WORK'" EXIT

pass() { echo "OK PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "X FAIL: $1"; FAIL=$((FAIL+1)); }
skip() { echo "-- SKIP: $1"; SKIP=$((SKIP+1)); }

# to_crlf <src> <dst> : LF-정규화 후 각 줄에 CR 부여 → 확정 CRLF 산출(GNU sed).
to_crlf() { sed -e 's/\r$//' -e 's/$/\r/' "$1" > "$2"; }

# to_lf <src> <dst> : 확정 LF 산출(잔여 CR 제거).
to_lf() { sed -e 's/\r$//' "$1" > "$2"; }

# has_cr_bytes <file> : 파일 안 CR 바이트 존재 시 0(true).
has_cr_bytes() { case "$(od -An -c "$1" 2>/dev/null)" in *'\r'*) return 0;; *) return 1;; esac; }

# out_has_cr <string> : 문자열 안 CR 존재 시 0(true).
out_has_cr() { case "$1" in *$'\r'*) return 0;; *) return 1;; esac; }

# make_probe <dir> <name> <sentinel> : dir/name 에 LF probe hook 작성.
#   payload sentinel 출력 + printf '[%s]' 로 인자 echo (fork 진정성 + 인자 정밀도 확증용).
make_probe() {
  local dir="$1" name="$2" sentinel="$3"
  {
    printf '#!/usr/bin/env bash\n'
    printf 'printf "%s\\n"\n' "$sentinel"
    printf 'printf "[%%s]" "$@"\n'
    printf 'printf "\\n"\n'
  } > "$dir/$name"
}

# bash_is_cr_sensitive : 현 bash 가 heredoc 종료구분자 매칭에서 CR 을 엄격 구분(POSIX)하면 0(true).
#   probe = **비대칭** quoted heredoc: 여는 구분자 줄은 CR 없이(LF-only) `: <<'PTERM'`, 종료자
#   후보줄만 후행 CR(`PTERM\r`). 여는 구분자 워드 = `PTERM`(CR 없음) ≠ 파일 안 종료자 후보줄 `PTERM\r`.
#     · CR-민감 bash(Linux 시스템 bash): `PTERM\r` ≠ `PTERM` → heredoc 미종료 → 하단 `echo` 까지
#       본문 흡수 → PROBE_SENTINEL 미출력 ⇒ CR-민감.
#     · CR-관대 bash(msys/Git Bash): `PTERM\r` 를 `PTERM` 로 관대 매칭 → 종료 → PROBE_SENTINEL 출력
#       ⇒ CR-관대(마스킹).
#   ※ 대칭 CRLF(여는 구분자에도 CR)면 워드가 `PTERM\r` = 종료자 `PTERM\r` 로 **어느 bash 에서나** 종료 →
#     항상 CR-관대 오보 → D1/D2 영구 SKIP(hollow-gate). 여는 구분자 LF-only(비대칭)가 판별의 필요조건.
bash_is_cr_sensitive() {
  local d out
  d=$(mktemp -d)
  # 여는 구분자 줄 = LF-only(CR 없음), 이후 body/종료자/echo 줄만 CRLF → 비대칭 (판별 핵심).
  printf '%s' $': <<\'PTERM\'\nbody line\r\nPTERM\r\necho PROBE_SENTINEL\r\n' > "$d/probe-cr.sh"
  out=$(bash "$d/probe-cr.sh" 2>/dev/null) || true
  rm -rf "$d"
  case "$out" in
    *PROBE_SENTINEL*) return 1 ;;   # 종료구분자 관대 매칭됨 → CR-관대 (masking)
    *) return 0 ;;                  # 미종료로 본문 흡수됨 → CR-민감 (POSIX)
  esac
}

# write_old_polyglot <path> : origin/main 구(舊) heredoc 폴리글롯을 LF 로 작성.
#   Unix 측: `: << 'CMDBLOCK'` 로 배치 본문을 no-op heredoc 에 흡수 후, 하단 bash 본문이
#   자기 dir 기준으로 대상 스크립트를 exec (LF=정상 동작, regression-guard).
#   ★ CRLF 로 만들면 여는 구분자 워드도 `CMDBLOCK\r`, 종료자 줄도 `CMDBLOCK\r` = **대칭** →
#     heredoc 은 CR-민감 bash 에서도 정상 **종료된다**(미종료 아님). 대신 종료 직후 하단 bash 본문
#     각 줄의 후행 CR 이 loud 실패를 낸다: 빈 줄 `\r` → `$'\r': command not found`(비정상 exit,
#     실측 127) + `shift\r`·assignment 후행 CR 로 exec 대상 경로에 CR 혼입("No such file") →
#     payload sentinel 미방출. 즉 결함은 silent no-op 이 아니라 **loud CR-오염 실패** (실측: Codex EXP-2).
write_old_polyglot() {
  cat > "$1" <<'OLDCMD'
: << 'CMDBLOCK'
@echo off
@REM windows batch body (Unix 측에서는 heredoc 에 흡수되어야 함)
echo cmd-side body should never execute on unix
CMDBLOCK

# Unix: run the named script directly (origin/main 구조 재현)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_NAME="$1"
shift
exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"
OLDCMD
}

echo "==========================================================================="
echo " CFP-2702 AC-5: run-hook.cmd Unix exec-first dispatch — discriminating self-test"
echo "==========================================================================="

# sanity: 대상 파일 존재
if [ ! -f "$RUN_HOOK" ]; then
  fail "setup — hooks/run-hook.cmd 부재 ($RUN_HOOK)"
  echo "PASS=$PASS FAIL=$FAIL SKIP=$SKIP"; exit 1
fi

# ═════════════════════════════════════════════════════════════════════════════
# Case A (happy path, LF): 현 run-hook.cmd(LF 정규화 사본) → probe exec → payload+args+exit0.
# ═════════════════════════════════════════════════════════════════════════════
A="$WORK/case-a"; mkdir -p "$A"
to_lf "$RUN_HOOK" "$A/run-hook.cmd"
make_probe "$A" "probe-hook" "PAYLOAD_SENTINEL_A5"
ecA=0
outA=$(bash "$A/run-hook.cmd" probe-hook alpha beta 2>&1) || ecA=$?  # exit 캡처(set -e abort 방지, ecA 로 assert)
if [ "$ecA" -eq 0 ] \
   && case "$outA" in *PAYLOAD_SENTINEL_A5*) true;; *) false;; esac \
   && case "$outA" in *'[alpha][beta]'*) true;; *) false;; esac; then
  pass "Case A happy-path (LF) — payload sentinel + args '[alpha][beta]' + exit 0"
else
  fail "Case A happy-path (LF) — exit=$ecA out=[$outA]"
fi

# ═════════════════════════════════════════════════════════════════════════════
# Case B (CR-leak 0, CRLF): 현 run-hook.cmd(CRLF 사본) → 후행 '#' 가드가 line1 CR 흡수 →
#   exec 인자에 \r 미포함. payload + 정확 '[alpha][beta]' (오염 없음) + 출력 CR 부재 + exit0.
# ═════════════════════════════════════════════════════════════════════════════
B="$WORK/case-b"; mkdir -p "$B"
to_crlf "$RUN_HOOK" "$B/run-hook.cmd"
make_probe "$B" "probe-hook" "PAYLOAD_SENTINEL_B5"
# 사본이 실제 CRLF 인지(anti-vacuity) 먼저 확증 — 변환 실패 시 loud fail.
if has_cr_bytes "$B/run-hook.cmd"; then
  ecB=0
  outB=$(bash "$B/run-hook.cmd" probe-hook alpha beta 2>&1) || ecB=$?  # exit 캡처(assert 대상)
  if [ "$ecB" -eq 0 ] \
     && case "$outB" in *PAYLOAD_SENTINEL_B5*) true;; *) false;; esac \
     && case "$outB" in *'[alpha][beta]'*) true;; *) false;; esac \
     && ! out_has_cr "$outB"; then
    pass "Case B CR-leak-0 (CRLF) — '#' 가드가 line1 CR 흡수, args '[alpha][beta]' CR 미포함 + exit 0"
  else
    fail "Case B CR-leak-0 (CRLF) — exit=$ecB out=[$outB] (CR 누출 또는 인자 오염 의심)"
  fi
else
  fail "Case B setup — CRLF 변환 실패(사본에 CR 바이트 부재): GNU sed 미보유 의심"
fi

# ═════════════════════════════════════════════════════════════════════════════
# Case C (fail-open 대체 = exec 성공 경로 + 대상 기대출력 assert, §8):
#   Unix 측은 line1 즉시 exec 라 bash-부재 경로가 없다 → exec 성공 시 대상 stdout 이 그대로
#   투과됨을 결정적 sentinel 로 확증(dispatcher 투명성 + fork 진정성; exit code 단독 판정 금지).
# ═════════════════════════════════════════════════════════════════════════════
C="$WORK/case-c"; mkdir -p "$C"
to_lf "$RUN_HOOK" "$C/run-hook.cmd"
# 대상이 결정적 기대출력을 방출하도록 별도 probe (인자 두 개 결합 marker).
cat > "$C/probe-hook" <<'EOF'
#!/usr/bin/env bash
printf 'FAILOPEN_TARGET_OUTPUT:%s-%s\n' "$1" "$2"
EOF
ecC=0
outC=$(bash "$C/run-hook.cmd" probe-hook one two 2>&1) || ecC=$?  # exit 캡처(assert 대상)
if [ "$ecC" -eq 0 ] && [ "$outC" = "FAILOPEN_TARGET_OUTPUT:one-two" ]; then
  pass "Case C exec-success/target-output — dispatcher 투과 'FAILOPEN_TARGET_OUTPUT:one-two' + exit 0"
else
  fail "Case C exec-success/target-output — exit=$ecC out=[$outC] (기대 'FAILOPEN_TARGET_OUTPUT:one-two')"
fi

# ═════════════════════════════════════════════════════════════════════════════
# CR-민감성 게이트 판정 (D1/D2 discriminating 분기 적용 여부).
# ═════════════════════════════════════════════════════════════════════════════
echo "── CR-민감성 probe (D1/D2 게이트) ──"
if bash_is_cr_sensitive; then
  CR_SENSITIVE=1
  echo "   → 이 bash 는 CR-민감(POSIX). D1/D2 discriminating 분기 실행(실 kill)."
else
  CR_SENSITIVE=0
  echo "   → 이 bash 는 CR-관대(msys/Git Bash). D1/D2 는 마스킹으로 vacuous → SKIP(정직 degrade)."
fi

# ═════════════════════════════════════════════════════════════════════════════
# Case D1 (결함 재현 RED — heredoc 폴리글롯 CR-민감): CR-민감 bash 에서만 유의미.
#   · LF 구-format → exit 0 + payload 출력(regression-guard: fixture 기능 정상).
#   · CRLF 구-format → **loud 실패**: 대칭 CRLF 라 heredoc 은 종료되나 하단 본문 후행 CR 이
#     `$'\r': command not found`(비정상 exit) + exec 대상 경로 CR-오염 → payload sentinel 미방출.
#     (구 주석의 "heredoc 미종료→silent no-op" 은 사실과 다름 — 실측은 loud 실패, Codex EXP-2.)
#   두 동작 차이(LF 정상 vs CRLF loud-fail)가 함께여야 CRLF 가 원인임을 결박 = discriminating.
# ═════════════════════════════════════════════════════════════════════════════
if [ "$CR_SENSITIVE" -eq 1 ]; then
  D="$WORK/case-d1"; mkdir -p "$D"
  make_probe "$D" "probe-hook" "PAYLOAD_SENTINEL_D1"
  write_old_polyglot "$D/old-lf.cmd"
  to_lf   "$D/old-lf.cmd" "$D/old.cmd";      # 확정 LF
  to_crlf "$D/old-lf.cmd" "$D/old-crlf.cmd"  # 확정 CRLF
  ec_lf=0; out_lf=$(bash "$D/old.cmd" probe-hook alpha beta 2>&1) || ec_lf=$?       # exit 캡처(regression-guard assert)
  ec_cr=0; out_cr=$(bash "$D/old-crlf.cmd" probe-hook alpha beta 2>&1) || ec_cr=$?  # exit 캡처(loud-fail assert)
  lf_has=1;  case "$out_lf" in *PAYLOAD_SENTINEL_D1*) : ;; *) lf_has=0;; esac
  cr_has=0;  case "$out_cr" in *PAYLOAD_SENTINEL_D1*) cr_has=1;; esac
  # loud 실패 시그니처: 비정상 exit(예: $'\r' → 127) 또는 stdout/stderr CR-오염 중 1+ (silent 아님 확증).
  cr_loud=0
  if [ "$ec_cr" -ne 0 ]; then cr_loud=1; fi
  if out_has_cr "$out_cr"; then cr_loud=1; fi
  if has_cr_bytes "$D/old-crlf.cmd" \
     && [ "$ec_lf" -eq 0 ] && [ "$lf_has" -eq 1 ] \
     && [ "$cr_has" -eq 0 ] && [ "$cr_loud" -eq 1 ]; then
    pass "Case D1 heredoc-CRLF 결함 재현 — LF=exit0+payload(regression-guard) ∧ CRLF=loud 실패(exit=$ec_cr · payload 부재 · CR-오염) [silent no-op 아님]"
  else
    fail "Case D1 heredoc-CRLF — ec_lf=$ec_lf(기대0) lf_has=$lf_has(기대1) cr_has=$cr_has(기대0) cr_loud=$cr_loud(기대1) ec_cr=$ec_cr crlf_bytes=$(has_cr_bytes "$D/old-crlf.cmd" && echo yes || echo no)"
  fi
else
  skip "Case D1 heredoc-CRLF 결함 재현 — msys CR-관대 마스킹으로 CRLF loud-fail 미발생(CR strip 후 정상 동작 → vacuous 회피). Linux 시스템 bash(CR-민감)에서 kill."
fi

# ═════════════════════════════════════════════════════════════════════════════
# Case D2 (정밀도/load-bearing — '#' 가드 discriminating, CR-민감): CR-민감 bash 에서만 유의미.
#   현 line1 에서 후행 '#' 가드를 제거한 CRLF 변종 → 마지막 인자에 \r 누출(beta\r).
#   현 '#'-가드 파일(Case B)은 누출 0 → '#' 가드가 load-bearing (vacuous 아님).
# ═════════════════════════════════════════════════════════════════════════════
if [ "$CR_SENSITIVE" -eq 1 ]; then
  E="$WORK/case-d2"; mkdir -p "$E"
  make_probe "$E" "probe-hook" "PAYLOAD_SENTINEL_D2"
  # 현 line1 의 mutation: 후행 '#' 가드 제거 (나머지 exec 의미 동일).
  printf '%s' $':; f="$1"; shift; exec bash "$(dirname "$0")/$f" "$@"\r\n' > "$E/noguard.cmd"
  outNG=$(bash "$E/noguard.cmd" probe-hook alpha beta 2>&1) || true
  # 마지막 인자 beta 에 trailing CR 누출 기대: 출력에 CR 존재 ∧ '[beta' 직후 CR.
  leak=0
  if out_has_cr "$outNG"; then
    case "$outNG" in *'[beta'$'\r'*) leak=1;; esac
  fi
  if has_cr_bytes "$E/noguard.cmd" && [ "$leak" -eq 1 ]; then
    pass "Case D2 '#'-가드 load-bearing — 가드 제거 CRLF 변종은 마지막 인자에 \\r 누출(beta\\r); 현 파일(Case B)은 누출 0 → 가드 판별력 확증"
  else
    fail "Case D2 '#'-가드 — leak=$leak(기대1) out=[$outNG] (od: $(printf '%s' "$outNG" | od -c | tr '\n' ' '))"
  fi
else
  skip "Case D2 '#'-가드 load-bearing — msys CR-관대 마스킹으로 인자 CR 누출 미발생(vacuous 회피). Linux CI 시스템 bash 에서 kill."
fi

# ═════════════════════════════════════════════════════════════════════════════
echo "==========================================================================="
echo " Test Summary (CFP-2702 AC-5 run-hook.cmd Unix exec-first dispatch)"
echo "==========================================================================="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "SKIP: $SKIP"
if [ "$SKIP" -gt 0 ]; then
  echo "NOTE: SKIP 은 CR-관대(msys) 환경의 정직 degrade — D1/D2 discriminating 은 Linux CI 시스템 bash 에서 실 kill 됨. Git Bash 통과를 GREEN 근거로 삼지 말 것."
fi
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS case(s) pass (SKIP $SKIP)"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
