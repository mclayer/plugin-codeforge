#!/usr/bin/env bash
# tests/scripts/test_codex-outpath-preflight.sh
# CFP-2929 §3.1 E1 / §3.2 E2 / §3.3 E3 — codex dispatch 출력 경로 방언 preflight discriminating self-test.
#
# 계약 SSOT = Change Plan cfp-2929 §3.1(L253-278) / §3.2(L280-297) / §3.3(L299-313) /
#   §8.0 AC↔mutant(L1022-1038) / §8.1 R5b·R5c fixture 구성법(L1042-1081) / §8.2 결정표 R1~R7(L1126-1142).
#
# ★★ 본 스위트의 제1 원칙 = **production 텍스트 직접 추출**.
#   preflight 루틴을 테스트 안에 재구현하지 않는다 — 재구현은 drift 표면이며 "테스트가 production 이
#   아니라 자기 사본을 검증" 하는 hollow 를 만든다. 실 `plugins/codeforge-review/agents/CodexReviewAgent.md`
#   의 dispatch 펜스에서 `codex_outpath_preflight()` 본문을 **그대로 잘라내** 평가한다.
#   mutation 도 그 추출 텍스트에 sed 를 걸어 만든다 (= 실 production 형태의 변이).
#
# ★★ cygpath ABSENT arm 구성법 (§8.1 — chief firsthand 확립, 본 스위트가 그대로 채택):
#   Git for Windows 는 `cygpath`·`uname`·`rm`·`mkdir`·`date` 가 `/usr/bin` 공존이라 PATH 에서 빼면
#   동반 소실되고 `uname -s` 가 빈 문자열이 되어 P-3 첫 conjunct 가 NO MATCH → **구조적 미발화**
#   (= "잡았다" 가 아니라 "아무것도 안 잡았다"). 해법 = **셸 함수가 PATH 조회보다 먼저 해석된다**:
#       PATH=/nonexistent-…                      # /usr/bin 제거 → cygpath ABSENT
#       uname() { printf 'MINGW64_NT-10.0\n'; }  # 함수로 MSYS 정체성만 복원
#   ★ `cygpath` 를 **함수로 shadow 하지 않는다** — `command -v` 가 함수를 찾아 ABSENT 를 못 만든다.
#     방향은 PATH 제거(cygpath) ⊕ 함수 복원(uname) 이다.
#   ★ 자기파괴성 대응 = **2 arm 분리** (§8.1 표):
#       단위 arm  — P-3 술어 평가 지점까지만 (P-0/P-1/P-2 미구동). 관측 변수 = outpath_reason 2값.
#       통합 arm  — 동 구성 + rm·mkdir·date 함수 stub → preflight 4검사 전 구간.
#     ★ stub 은 실 파일조작을 하지 않으므로 **`slot_clear_failed` 판별력은 통합 arm 에서 미검증** 이다
#       (그 축 = 아래 §C 별 fixture 소관 — 실 파일시스템 + rm no-op stub).
#   ★ `command -v "${CODEX_CYGPATH_BIN:-cygpath}"` 간접화는 **기각** (§8.1) — 프로덕션에 임의 바이너리
#     실행 env 주입면을 만든다(§7.4.5 OP-3 deny-by-default 충돌). 본 구성법은 **프로덕션 코드 무변경**.
#
# ★ 검사연극 금지 (비협상): `|| true` · `|| skip` · `continue-on-error` · `2>/dev/null; rc=0` 0건.
#   조건부 기대(`or` 묶음) 0건 — 전 행 **단일 기대**. 생존 판정 변이는 삭제하지 않고
#   **"생존 기대(이중화 확인)"** 로 정직 재라벨한다 (RED 를 만들려고 방어층을 제거하는 역행 압력 차단).
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MD_REAL="$REPO_ROOT/plugins/codeforge-review/agents/CodexReviewAgent.md"
LATE_COLLECT="$REPO_ROOT/plugins/codeforge-review/scripts/codex-late-collect.sh"

PASS=0
FAIL=0
SKIP=0

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

ok()   { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
bad()  { echo "✗ FAIL: $1"; shift; for l in "$@"; do echo "    $l"; done; FAIL=$((FAIL+1)); }
skip() { echo "↷ SKIP: $1 — $2"; SKIP=$((SKIP+1)); }

# 관측 문자열 동등 assert (단일 기대 — `or` 묶음 금지)
assert_eq() {
  local name="$1" actual="$2" expected="$3" desc="$4"
  if [ "$actual" = "$expected" ]; then
    ok "$name — $desc [관측: $actual]"
  else
    bad "$name" "기대: $expected" "실제: $actual" "설명: $desc"
  fi
}

# mutant 판별력 assert: 미변이 관측 ≠ 변이 관측 이어야 KILL. 두 관측값 모두 기대치와 일치도 함께 요구
# (관측이 "갈리기만" 하면 되는 게 아니라 **무엇으로** 갈리는지가 계약이다 — 판별력 오귀속 차단).
assert_kill() {
  local name="$1" base_obs="$2" base_exp="$3" mut_obs="$4" mut_exp="$5" desc="$6"
  local prob=""
  if [ "$base_obs" != "$base_exp" ]; then
    prob="미변이 관측 불일치 (기대 $base_exp, 실제 $base_obs)"
  elif [ "$mut_obs" != "$mut_exp" ]; then
    prob="변이 관측 불일치 (기대 $mut_exp, 실제 $mut_obs)"
  elif [ "$base_obs" = "$mut_obs" ]; then
    prob="미변이 == 변이 (무차이) — 변이 생존, 판별력 0"
  fi
  if [ -z "$prob" ]; then
    ok "$name [KILL] $base_obs → $mut_obs — $desc"
  else
    bad "$name [KILL 실패]" "$prob" "설명: $desc"
  fi
}

# 생존 기대 assert (§8.2 등재 규율 — 삭제 대신 정직 재라벨). 이중화가 실재함을 **적극 관측**한다.
assert_survive() {
  local name="$1" base_obs="$2" mut_obs="$3" expected="$4" desc="$5"
  if [ "$base_obs" = "$mut_obs" ] && [ "$base_obs" = "$expected" ]; then
    ok "$name [생존 기대 = 이중화 확인] 미변이 == 변이 == $base_obs — $desc"
  else
    bad "$name [생존 기대 위반]" "미변이: $base_obs / 변이: $mut_obs / 기대(양쪽): $expected" "설명: $desc"
  fi
}

# ═══════════════════════════════════════════════════════════════════════════
# §S0 setup guard — 추출이 성립하는가 (부재 시 전 케이스가 vacuous PASS 로 위장되는 것 차단)
# ═══════════════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §S0 setup guard — 실 production 텍스트 추출 성립 확인"
echo "═══════════════════════════════════════════════════════════════════════════"

if [ ! -f "$MD_REAL" ]; then
  bad "S0-1 실 CodexReviewAgent.md 존재" "부재: $MD_REAL" "추출 불가 — 이하 전 케이스 vacuous, 즉시 종료"
  echo "PASS: $PASS / FAIL: $FAIL / SKIP: $SKIP"; exit 1
fi
ok "S0-1 실 CodexReviewAgent.md 존재 ($MD_REAL)"

# 첫 ```bash 펜스 → 다음 ``` 까지 (행번호 비의존 — D17 층 삽입으로 행이 밀려도 무영향)
extract_fence() { awk '/^```bash$/{f=1;next} f&&/^```$/{exit} f{print}' "$1"; }
FENCE="$WORK/fence.sh"
extract_fence "$MD_REAL" > "$FENCE"
if [ "$(wc -l < "$FENCE")" -lt 40 ]; then
  bad "S0-2 dispatch 펜스 추출" "추출 행수 $(wc -l < "$FENCE") < 40 — 펜스 구조 변경 의심"
  echo "PASS: $PASS / FAIL: $FAIL / SKIP: $SKIP"; exit 1
fi
ok "S0-2 dispatch 펜스 추출 ($(wc -l < "$FENCE") 행)"

PREFLIGHT="$WORK/preflight.sh"
sed -n '/^codex_outpath_preflight() {/,/^}$/p' "$FENCE" > "$PREFLIGHT"
if [ "$(wc -l < "$PREFLIGHT")" -lt 10 ]; then
  bad "S0-3 codex_outpath_preflight() 추출" \
      "추출 행수 $(wc -l < "$PREFLIGHT") < 10 — 함수 부재 또는 시그니처 변경" \
      "★ 이 실패는 '테스트 결함' 이 아니라 'preflight 미배선' 신호일 수 있다 (pre-GREEN 형상)"
  echo "PASS: $PASS / FAIL: $FAIL / SKIP: $SKIP"; exit 1
fi
ok "S0-3 codex_outpath_preflight() 추출 ($(wc -l < "$PREFLIGHT") 행)"

# 4 검사 전부 실재 — 부분 배선을 전체 배선으로 오인하지 않는다
S0_MISSING=""
grep -q 'command -v cygpath'            "$PREFLIGHT" || S0_MISSING="$S0_MISSING P-0(cygpath 가드)"
grep -q 'dir_create_failed'             "$PREFLIGHT" || S0_MISSING="$S0_MISSING P-1(dir_create_failed)"
grep -q 'slot_clear_failed'             "$PREFLIGHT" || S0_MISSING="$S0_MISSING P-2(slot_clear_failed)"
grep -q 'MSYS_NO_PATHCONV'              "$PREFLIGHT" || S0_MISSING="$S0_MISSING P-3(방언 술어)"
grep -q 'cygpath_failed'                "$PREFLIGHT" || S0_MISSING="$S0_MISSING P-0(cygpath_failed enum)"
if [ -z "$S0_MISSING" ]; then
  ok "S0-4 preflight 4검사 리터럴 전건 실재 (P-0/P-1/P-2/P-3)"
else
  bad "S0-4 preflight 4검사 리터럴" "누락:$S0_MISSING"
fi

# P-3 술어 블록 (단위 arm 용) — `uname -s` if → 첫 `^  fi$`
P3="$WORK/p3.sh"
sed -n '/^  if \[\[ "\$(uname -s)"/,/^  fi$/p' "$PREFLIGHT" > "$P3"
if grep -q 'uname -s' "$P3" && grep -q 'MSYS_NO_PATHCONV' "$P3" && grep -q 'dialect_reject' "$P3"; then
  ok "S0-5 P-3 술어 블록 추출 (단위 arm 무대)"
else
  bad "S0-5 P-3 술어 블록 추출" "uname -s / MSYS_NO_PATHCONV / dialect_reject 중 일부 부재"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 공통 harness — stub 구성 ⊗ mutation sed ⊗ 관측
# ═══════════════════════════════════════════════════════════════════════════
# 관측 = "reason|rc|out_json" 3-튜플 (runner 는 항상 exit 0 — 관측은 stdout 이지 exit code 가 아니다).

# 최소 충실 cygpath -m stub: `/x/…` (단일문자 드라이브 세그먼트) → `X:/…`, 그 외 = fixpoint.
# [근거: chief firsthand — cygpath -m "/c/Users/…/x.json" → C:/Users/…/x.json ·
#        cygpath -m "C:/Users/mccho/x.json" → C:/Users/mccho/x.json (fixpoint)]
# ★ stub 충실도 자체는 §R-real 케이스가 실 cygpath 와 대조해 결박한다 (MSYS 한정).
CYG_OK='cygpath() { local p="" a; for a in "$@"; do case "$a" in -*) ;; *) p="$a";; esac; done
  case "$p" in /?/*) local d="${p:1:1}"; printf "%s:/%s\n" "${d^^}" "${p:3}" ;; *) printf "%s\n" "$p" ;; esac; }'
CYG_FAIL='cygpath() { return 1; }'                       # 존재하나 rc≠0
CYG_EMPTY='cygpath() { printf ""; return 0; }'           # 존재하나 빈 출력
WIN='uname() { printf "MINGW64_NT-10.0\n"; }'
LNX='uname() { printf "Linux\n"; }'
NOCYG='PATH=/nonexistent-cfp2929-cygpath-absent'         # /usr/bin 제거 → cygpath ABSENT
STUBS='mkdir() { return 0; }
rm() { return 0; }
date() { printf "1770000000\n"; }'                       # ABSENT arm 동반 소실분 복원 (통합 arm)

# $1=mode(unit|full) $2=setup $3=mutation-sed('' = 미변이) $4=OUT_JSON → stdout "reason|rc|out"
obs_pf() {
  local mode="$1" setup="$2" mutsed="$3" outjson="$4" body script tmpd
  tmpd="$(mktemp -d -p "$WORK")"
  if [ "$mode" = unit ]; then
    body="$( { echo '_pf() {'; echo '  outpath_reason=""'; cat "$P3"; echo '  return 0'; echo '}'; } )"
  else
    body="$(sed -e 's/^codex_outpath_preflight() {.*$/_pf() {/' "$PREFLIGHT")"
  fi
  if [ -n "$mutsed" ]; then
    body="$(printf '%s\n' "$body" | sed "$mutsed")"
  fi
  script="$tmpd/run.sh"
  {
    printf '%s\n' "$setup"
    printf 'CR_DIR=%q\n' "$tmpd/cr"
    printf 'OUT_JSON=%q\n' "$outjson"
    printf 'MANIFEST="$CR_DIR/dispatch-design.json"\n'
    printf 'RC_STAMP="$CR_DIR/dispatch-design.rc"\n'
    printf '%s\n' "$body"
    printf 'outpath_reason=""; _pf; _rc=$?\n'
    printf 'printf "%%s|%%s|%%s\\n" "${outpath_reason:-PROCEED}" "$_rc" "${OUT_JSON:-<empty>}"\n'
    printf 'exit 0\n'
  } > "$script"
  bash "$script" 2>/dev/null | tail -1
}

# 관측 3-튜플에서 reason 만 (대다수 행의 판정 축)
reason_of() { printf '%s' "${1%%|*}"; }

# ── mutation sed 프로그램 (전부 **실 production 텍스트** 에 대한 변이) ────────────────
# M5  : P-3 env 술어 set-ness → 값 비교 (`MSYS_NO_PATHCONV=0` 도 변환 해제라는 사실을 무시하는 변이)
MUT_M5='s/\[ -n "\${MSYS_NO_PATHCONV+x}" \]/[ "${MSYS_NO_PATHCONV:-}" = "1" ]/'
# M3  : P-0 `command -v cygpath` 가드 제거 (무조건 실행)
MUT_M3='s/if command -v cygpath >\/dev\/null 2>&1; then/if true; then/'
# M-P0: P-0 의 rc·빈문자열 검사 제거 = **원안 형태 복원** (`OUT_JSON=""` 로 P-3 조용히 우회)
MUT_MP0='/\[ -n "\$_n" \]/d
s/2>\/dev\/null)" || { outpath_reason=cygpath_failed; return 1; }/2>\/dev\/null)"/'
# M-a : (a) 정규화(P-0 블록) 전체 제거 — (b) export 삭제는 유지
MUT_MA='/if command -v cygpath/,/^  fi$/d'
# M-L : P-2 부재 재확인에서 `|| [ -L "$_f" ]` 제거 (dangling symlink 를 `-e` 단독이 놓치는 형태)
#       ★ §8.2 명명 mutant 아님 — §3.2 P-2 가 명시 요구한 `-e ∥ -L` conjunct 의 load-bearing 실증용
#         로컬 변이 (설계리뷰 P2 지적 항목). 매핑표에 그 귀속으로 기재.
MUT_ML='s/if \[ -e "\$_f" \] || \[ -L "\$_f" \]; then/if [ -e "$_f" ]; then/'

POSIX_OUT='/c/tmp/cfp2929/o.json'
DRIVE_OUT='C:/tmp/cfp2929/o.json'

# ═══════════════════════════════════════════════════════════════════════════
# §A 결정표 R1~R7 (§8.2 tier B) — 미변이 관측
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §A 결정표 R1~R7 — 미변이 관측 (통합 arm)"
echo "═══════════════════════════════════════════════════════════════════════════"

R1_OBS="$(obs_pf full "$WIN
$CYG_OK
unset MSYS_NO_PATHCONV" '' "$POSIX_OUT")"
assert_eq "R1 Windows ∧ unset ∧ POSIX ∧ cygpath 있음" "$R1_OBS" "PROCEED|0|$DRIVE_OUT" \
  "P-0 정규화 → drive-form argv → write OK"

R2_OBS="$(obs_pf full "$WIN
$CYG_OK
unset MSYS_NO_PATHCONV" '' "$DRIVE_OUT")"
assert_eq "R2 Windows ∧ unset ∧ drive-form ∧ cygpath 있음" "$R2_OBS" "PROCEED|0|$DRIVE_OUT" \
  "cygpath -m fixpoint (E-5) → write OK"

R3_OBS="$(obs_pf full "$WIN
$CYG_OK
export MSYS_NO_PATHCONV=1" '' "$POSIX_OUT")"
assert_eq "R3 Windows ∧ set(=1 ambient) ∧ POSIX ∧ cygpath 있음" "$R3_OBS" "PROCEED|0|$DRIVE_OUT" \
  "(a) 2급 방어 발동 → 정규화 → write OK. ★ (a) 의 독립 정당화 행 (M-a kill 행)"

# ★★ R4 정직 주석 (§8.2 원안 오등재 정정) — R4 는 **M5 를 잡지 못한다**.
#    cygpath 가 있으면 P-0 정규화가 무조건 선행해 OUT_JSON 이 drive-form 이 되므로 P-3 3번째
#    conjunct(`case "$OUT_JSON" in /*`)가 애초에 미매치한다 → env 술어가 set-ness 든 값비교든
#    **관측이 동일**하다. M5 의 실 kill 행 = R5b (아래 §B). 여기서는 미변이 관측만 기록한다.
R4_OBS="$(obs_pf full "$WIN
$CYG_OK
export MSYS_NO_PATHCONV=0" '' "$POSIX_OUT")"
assert_eq "R4 Windows ∧ set(=0) ∧ POSIX ∧ cygpath 있음 [M5 비-kill 행 — 정직 주석 참조]" \
  "$R4_OBS" "PROCEED|0|$DRIVE_OUT" \
  "정규화 선행 → /* 미매치 → P-3 미발화 → write OK. ★ 이 행은 M5 를 못 잡는다(원안 오등재 정정)"

R5_OBS="$(obs_pf full "$NOCYG
$WIN
$STUBS
export MSYS_NO_PATHCONV=1" '' "$POSIX_OUT")"
assert_eq "R5 Windows ∧ set(=1) ∧ POSIX ∧ cygpath 없음" "$R5_OBS" "dialect_reject|1|$POSIX_OUT" \
  "(a) 불가 → P-3 발화 → dialect_reject → codex 미호출 (전용 marker + inconclusive)"

R5B_OBS="$(obs_pf full "$NOCYG
$WIN
$STUBS
export MSYS_NO_PATHCONV=0" '' "$POSIX_OUT")"
assert_eq "R5b Windows ∧ set(=0) ∧ POSIX ∧ cygpath 없음" "$R5B_OBS" "dialect_reject|1|$POSIX_OUT" \
  "★ set-ness 판정으로 P-3 발화 (=0 도 변환 해제) — M5 의 실 kill 행"

R5C_OBS="$(obs_pf full "$NOCYG
$WIN
$STUBS
unset MSYS_NO_PATHCONV" '' "$POSIX_OUT")"
assert_eq "R5c Windows ∧ unset ∧ POSIX ∧ cygpath 없음" "$R5C_OBS" "PROCEED|0|$POSIX_OUT" \
  "★ (a) no-op · P-3 미발화 → MSYS 자연 변환에 위임 → write OK. (b) export 삭제의 독립 정당화 행"

R6_OBS="$(obs_pf full "$NOCYG
$LNX
$STUBS
unset MSYS_NO_PATHCONV" '' "$POSIX_OUT")"
assert_eq "R6 비-Windows ∧ POSIX ∧ cygpath 없음 [AC-2]" "$R6_OBS" "PROCEED|0|$POSIX_OUT" \
  "전면 no-op — 경로 byte 동일 (INV-H 비-Windows 무변형)"

R7A_OBS="$(obs_pf full "$WIN
$CYG_FAIL
unset MSYS_NO_PATHCONV" '' "$POSIX_OUT")"
assert_eq "R7a Windows ∧ cygpath 존재하나 rc≠0" "$(reason_of "$R7A_OBS")" "cygpath_failed" \
  "P-0 fail-closed → codex 미호출 + inconclusive"

R7B_OBS="$(obs_pf full "$WIN
$CYG_EMPTY
unset MSYS_NO_PATHCONV" '' "$POSIX_OUT")"
assert_eq "R7b Windows ∧ cygpath 존재하나 빈 출력" "$(reason_of "$R7B_OBS")" "cygpath_failed" \
  "빈 출력도 fail-closed — OUT_JSON=\"\" 로 P-3 우회 차단 (부재 no-op ↔ 실패 거부 두 상태 분리)"

# 단위 arm 재확인 (P-0/P-1/P-2 미구동 — P-3 술어 단독 판정, 관측 개입 0)
R5B_U="$(obs_pf unit "$NOCYG
$WIN
export MSYS_NO_PATHCONV=0" '' "$POSIX_OUT")"
assert_eq "R5b 단위 arm (P-3 술어 단독)" "$(reason_of "$R5B_U")" "dialect_reject" \
  "P-1/P-2 를 애초에 평가하지 않으므로 그들의 통과·실패가 관측에 개입할 수 없다"
R5C_U="$(obs_pf unit "$NOCYG
$WIN
unset MSYS_NO_PATHCONV" '' "$POSIX_OUT")"
assert_eq "R5c 단위 arm (P-3 술어 단독)" "$(reason_of "$R5C_U")" "PROCEED" \
  "동상 — 관측 변수 = outpath_reason ∈ {dialect_reject, PROCEED} 2값"

# ABSENT arm 구성이 실제로 성립하는가 (구조적 미발화 = "아무거나 잡았다" 차단, §8.1 필수 사전조건)
ABSENT_PROBE="$(bash -c "$NOCYG
$WIN
command -v cygpath >/dev/null 2>&1 && echo PRESENT || echo ABSENT
printf '%s\n' \"\$(uname -s)\"" 2>/dev/null)"
assert_eq "A-pre cygpath ABSENT arm 성립 확인" "$(printf '%s' "$ABSENT_PROBE" | tr '\n' ',')" \
  "ABSENT,MINGW64_NT-10.0" \
  "cygpath = ABSENT ∧ uname -s = MSYS 정체성 유지 → P-3 첫 conjunct MATCH 가능 (구조적 미발화 아님)"

# stub 충실도 결박 — 실 cygpath 와 대조 (MSYS 한정. 부재 플랫폼은 명시 SKIP)
if command -v cygpath >/dev/null 2>&1; then
  REAL_POSIX="$(cygpath -m "$POSIX_OUT")"
  REAL_FIX="$(cygpath -m "$DRIVE_OUT")"
  STUB_POSIX="$(bash -c "$CYG_OK
cygpath -m $POSIX_OUT")"
  STUB_FIX="$(bash -c "$CYG_OK
cygpath -m $DRIVE_OUT")"
  assert_eq "A-fid cygpath stub 충실도 (POSIX → drive-form)" "$STUB_POSIX" "$REAL_POSIX" \
    "stub 산출 == 실 cygpath -m 산출 (stub 이 R1~R4 관측을 왜곡하지 않음을 결박)"
  assert_eq "A-fid cygpath stub 충실도 (drive-form fixpoint)" "$STUB_FIX" "$REAL_FIX" \
    "동상 — fixpoint 축"
else
  skip "A-fid cygpath stub 충실도 대조" \
       "실 cygpath 부재 플랫폼(비-MSYS) — 대조 불가. ★ 이 SKIP 은 R1~R7 본 행 판정에 영향 0 (stub 은 그대로 구동)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# §B mutation — 미변이 관측 ↔ 변이 관측 (§8.2 mutation 세트)
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §B mutation kill/생존 — 실 production 텍스트 변이"
echo "═══════════════════════════════════════════════════════════════════════════"

# ── M-P0 : P-0 rc·빈문자열 검사 제거 → R7 에서 kill ────────────────────────────────
MP0_A="$(obs_pf full "$WIN
$CYG_FAIL
unset MSYS_NO_PATHCONV" "$MUT_MP0" "$POSIX_OUT")"
assert_kill "M-P0 @ R7a (cygpath rc≠0)" \
  "$R7A_OBS" "cygpath_failed|1|$POSIX_OUT" "$MP0_A" "PROCEED|0|<empty>" \
  "AC-1 음면 — 검사 제거 시 OUT_JSON=\"\" 로 P-3 우회 → \`-o \"\"\` dispatch"
MP0_B="$(obs_pf full "$WIN
$CYG_EMPTY
unset MSYS_NO_PATHCONV" "$MUT_MP0" "$POSIX_OUT")"
assert_kill "M-P0 @ R7b (cygpath 빈 출력)" \
  "$R7B_OBS" "cygpath_failed|1|$POSIX_OUT" "$MP0_B" "PROCEED|0|<empty>" \
  "동상 — 빈 출력 축"

# ── M5 : env 술어 set-ness → 값비교. kill 행 = R5b / 생존 행 = R4 ─────────────────
M5_R5B="$(obs_pf full "$NOCYG
$WIN
$STUBS
export MSYS_NO_PATHCONV=0" "$MUT_M5" "$POSIX_OUT")"
assert_kill "M5 @ R5b (cygpath 없음 ∧ env=0)" \
  "$(reason_of "$R5B_OBS")" "dialect_reject" "$(reason_of "$M5_R5B")" "PROCEED" \
  "값비교 변이는 =0 을 통과시켜 조용한 write 실패로 간다 — set-ness 술어가 load-bearing"
M5_R4="$(obs_pf full "$WIN
$CYG_OK
export MSYS_NO_PATHCONV=0" "$MUT_M5" "$POSIX_OUT")"
assert_survive "M5 @ R4 (cygpath 있음 ∧ env=0)" \
  "$(reason_of "$R4_OBS")" "$(reason_of "$M5_R4")" "PROCEED" \
  "정규화가 /* 를 없애 P-3 3번째 conjunct 미매치 → env 술어 형태가 관측을 바꾸지 않는다 (원안 R4 오등재 정정)"

# ── M1 : `export MSYS_NO_PATHCONV=1` 복원(= (b) 되돌림). kill 행 = R5c / 생존 = TREAT ──
#   ★ 변이 모사 방식: production 이 export 를 되살리면 preflight 진입 시점 env 가 set 이 된다.
#     따라서 동일 행 구성에서 env 를 set 으로 두는 것이 그 변이의 **정확한 관측면**이다.
M1_R5C="$(obs_pf full "$NOCYG
$WIN
$STUBS
export MSYS_NO_PATHCONV=1" '' "$POSIX_OUT")"
assert_kill "M1 @ R5c (cygpath 없음 ∧ 원래 unset)" \
  "$(reason_of "$R5C_OBS")" "PROCEED" "$(reason_of "$M1_R5C")" "dialect_reject" \
  "export 가 남아 있었다면 P-3 이 발화해 codex 미호출 — (b) export 삭제의 독립 정당화"
M1_TREAT="$(obs_pf full "$WIN
$CYG_OK
export MSYS_NO_PATHCONV=1" '' "$POSIX_OUT")"
assert_survive "M1 @ TREAT arm (cygpath 있음)" \
  "$(reason_of "$R1_OBS")" "$(reason_of "$M1_TREAT")" "PROCEED" \
  "(a) 가 무조건 선행해 drive-form 을 만들므로 export 유무 무관 — 원안의 'TREAT arm RED' 는 오등재였다"

# ── M3 : `command -v cygpath` 가드 제거 → R6(비-Windows) 에서 kill ────────────────
M3_R6="$(obs_pf full "$NOCYG
$LNX
$STUBS
unset MSYS_NO_PATHCONV" "$MUT_M3" "$POSIX_OUT")"
assert_kill "M3 @ R6 (비-Windows)" \
  "$(reason_of "$R6_OBS")" "PROCEED" "$(reason_of "$M3_R6")" "cygpath_failed" \
  "AC-2 — 가드 제거 시 부재 cygpath 실행(rc=127) → fail-closed. 비-Windows byte 무변형 파괴"

# ── M-a : (a) 정규화 제거 → R3(ambient export) 에서 kill ─────────────────────────
MA_R3="$(obs_pf full "$WIN
$CYG_OK
export MSYS_NO_PATHCONV=1" "$MUT_MA" "$POSIX_OUT")"
assert_kill "M-a @ R3 (ambient export ∧ cygpath 있음)" \
  "$(reason_of "$R3_OBS")" "PROCEED" "$(reason_of "$MA_R3")" "dialect_reject" \
  "(b) 는 남의 셸 프로파일을 통제하지 못한다 — ambient export 환경에서 (a) 만이 방어"

# ═══════════════════════════════════════════════════════════════════════════
# §C P-1 / P-2 / 순서 고정 (§3.2 4검사 · 순서 고정)
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §C P-1 dir_create_failed / P-2 slot_clear_failed / 검사 순서 고정"
echo "═══════════════════════════════════════════════════════════════════════════"

C_P1="$(obs_pf full "$LNX
$CYG_OK
mkdir() { return 1; }
unset MSYS_NO_PATHCONV" '' "$WORK/p1/o.json")"
assert_eq "C1 P-1 아티팩트 디렉터리 생성 실패" "$(reason_of "$C_P1")" "dir_create_failed" \
  "mkdir -p 실패 → 명명된 fail-closed (E-4: 디렉터리 부재는 exit 0 + out.json 부재로 조용히 수렴)"

# P-2 = **실 파일시스템** + rm no-op stub (통합 arm 의 stub 이 못 무는 축 — §8.1 정직 declare 대응)
mkdir -p "$WORK/p2"; : > "$WORK/p2/o.json"
C_P2="$(obs_pf full "$LNX
$CYG_OK
rm() { return 0; }
unset MSYS_NO_PATHCONV" '' "$WORK/p2/o.json")"
assert_eq "C2 P-2 비움 실패 (rm no-op ∧ 선재 파일)" "$(reason_of "$C_P2")" "slot_clear_failed" \
  "비움 실패 = '이번 회차 슬롯을 우리가 소유한다고 단언 불가' → 경고가 아니라 차단"

mkdir -p "$WORK/p2b"; : > "$WORK/p2b/o.json"
C_P2B="$(obs_pf full "$LNX
$CYG_OK
unset MSYS_NO_PATHCONV" '' "$WORK/p2b/o.json")"
assert_eq "C2-ctrl P-2 대조 (rm 정상 ∧ 선재 파일)" "$(reason_of "$C_P2B")" "PROCEED" \
  "비움이 실제로 되면 통과 — C2 가 '선재 파일이면 무조건 RED' 인 상시-RED 가 아님을 결박"

# P-2 `-e ∥ -L` dangling symlink conjunct (§3.2 설계리뷰 P2 지적 — Linux 단위 arm 귀속)
#   ★ Windows 는 심볼릭 링크 생성이 개발자 모드/권한 요건에 걸려 러너 구성이 불안정 → 설계가 명시적으로
#     `windows-latest` 비대상 선언. **정직 잔여**: "Windows ∧ dangling symlink" 조합은 본 Story 미검증.
if ln -s "$WORK/definitely-nonexistent-target" "$WORK/dangling" 2>/dev/null \
   && [ -L "$WORK/dangling" ] && [ ! -e "$WORK/dangling" ]; then
  mkdir -p "$WORK/p2c"
  ln -s "$WORK/definitely-nonexistent-target" "$WORK/p2c/o.json"
  C_P2C="$(obs_pf full "$LNX
$CYG_OK
rm() { return 0; }
unset MSYS_NO_PATHCONV" '' "$WORK/p2c/o.json")"
  C_P2C_ML="$(obs_pf full "$LNX
$CYG_OK
rm() { return 0; }
unset MSYS_NO_PATHCONV" "$MUT_ML" "$WORK/p2c/o.json")"
  assert_kill "C3 P-2 dangling symlink (-e ∥ -L conjunct)" \
    "$(reason_of "$C_P2C")" "slot_clear_failed" "$(reason_of "$C_P2C_ML")" "PROCEED" \
    "\`-e\` 단독은 dangling symlink 에 false → 비움 무력화를 놓친다. \`-L\` 동반이 load-bearing"
else
  skip "C3 P-2 dangling symlink (-e ∥ -L conjunct)" \
       "이 플랫폼에서 dangling symlink 생성 불가 (Windows 권한/개발자 모드) — §8.1 이 windows-latest 비대상으로 명시 선언한 축. Linux 러너에서 구동됨. ★ 정직 잔여: 'Windows ∧ dangling symlink' 조합 미검증"
fi

# 순서 고정 P-0 → P-1 : 두 실패가 동시 가능할 때 P-0 이 먼저 판정을 내야 한다
C_ORD="$(obs_pf full "$WIN
$CYG_FAIL
mkdir() { return 1; }
unset MSYS_NO_PATHCONV" '' "$POSIX_OUT")"
assert_eq "C4 검사 순서 P-0 ≺ P-1" "$(reason_of "$C_ORD")" "cygpath_failed" \
  "cygpath 실패 ∧ mkdir 실패 동시 → P-0 reason 이 나와야 한다 (순서 고정)"
C_ORD_CTRL="$(obs_pf full "$WIN
$CYG_OK
mkdir() { return 1; }
unset MSYS_NO_PATHCONV" '' "$POSIX_OUT")"
assert_eq "C4-ctrl 순서 대조 (P-0 통과 시 P-1 이 판정)" "$(reason_of "$C_ORD_CTRL")" "dir_create_failed" \
  "C4 가 'cygpath_failed 상시 반환' 이 아님을 결박 (단일 변수 diff = cygpath 성공 여부)"

# ═══════════════════════════════════════════════════════════════════════════
# §D (b) 1급 — `export MSYS_NO_PATHCONV=1` 삭제 presence (§3.1 (b))
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §D (b) 1급 — export 삭제 presence (실 agent md firsthand)"
echo "═══════════════════════════════════════════════════════════════════════════"
# 안전 count (ADR-060 Amd22 정합 — grep exit 는 pass/fail 신호가 아니라 count 표현 수단이며,
#   실 pass/fail 은 아래 assert_eq 가 gating. 파일 부재 위장은 S0-1 guard 가 별도 차단).
gcount() { local n; n=$(grep -cE "$1" "$2" 2>/dev/null) || n=0; printf '%s' "$n"; }
D_EXPORT="$(gcount '^[[:space:]]*export[[:space:]]+MSYS_NO_PATHCONV' "$MD_REAL")"
assert_eq "D1 실 agent md 의 \`export MSYS_NO_PATHCONV\` 발화 0건" "$D_EXPORT" "0" \
  "(b) 1급 = 한 줄 삭제로 argv 소비 site 2개 동시 교정. 잔존 시 R5c 가 dialect_reject 로 뒤집힌다"
# 탐지력 결박 — 주입 사본에서 검출돼야 한다 (never-match 패턴이 아님을 입증)
cp "$MD_REAL" "$WORK/md_inj.md"
printf '%s\n' '  export MSYS_NO_PATHCONV=1   # 주입 mutant' >> "$WORK/md_inj.md"
D_INJ="$(gcount '^[[:space:]]*export[[:space:]]+MSYS_NO_PATHCONV' "$WORK/md_inj.md")"
assert_eq "D1-disc 탐지력 (export 주입 → 검출)" "$D_INJ" "1" \
  "D1 이 vacuous(never-match) 아님 입증"

# ═══════════════════════════════════════════════════════════════════════════
# §E AC-3a — post-dispatch discriminator 2 라벨 분별 (D-1 / D-2, M10)
# ═══════════════════════════════════════════════════════════════════════════
# ★ 배치 근거: 본 파일이 이미 '실 production 텍스트 추출' 기계를 소유하므로 재사용(ADR-140 재사용 우선).
#   `tests/scripts/test_codex-late-collect.sh` 는 8-step 흐름·rc stamp 파서·잔재 시나리오 소관이며
#   본 절은 그와 disjoint 한 **라벨 분별 축** 만 문다 (중복 fixture 유입 0).
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §E AC-3a — discriminator 라벨 분별 (D-1 / D-2 관측표 · M10)"
echo "═══════════════════════════════════════════════════════════════════════════"

if [ ! -f "$LATE_COLLECT" ]; then
  bad "E0 setup — codex-late-collect.sh 존재" "부재: $LATE_COLLECT" \
      "★ AC-3a/AC-3b 절 vacuous 위장 차단 — discriminator 미배선 신호"
else
  ok "E0 setup — codex-late-collect.sh 존재"
  DISC_HELPERS="$WORK/disc_helpers.sh"
  # ★ 추출 앵커는 **정의 줄 말미 주석을 허용**해야 한다 (`_basename() {   # …` 실형태).
  #   `{$` 로 못 박으면 조용히 0행 추출 → 함수 미정의 → 라벨 payload 가 빈 문자열이 되어
  #   "라벨은 나왔는데 내용이 없다" 는 형태로 **검사가 hollow 화** 한다. 아래 E0-3 이 그 class 를 문다.
  {
    sed -n '/^_marker_dialect()/p' "$LATE_COLLECT"
    sed -n '/^_marker_absent()/p' "$LATE_COLLECT"
    sed -n '/^_basename() {/,/^}$/p' "$LATE_COLLECT"
    sed -n '/^_mangled_probe_path() {/,/^}$/p' "$LATE_COLLECT"
  } > "$DISC_HELPERS"
  DISC_STEP5="$WORK/disc_step5.sh"
  sed -n '/^  probe="\$(_mangled_probe_path/,/^  exit 1$/p' "$LATE_COLLECT" > "$DISC_STEP5"

  if grep -q '_marker_dialect' "$DISC_STEP5" && grep -q '_marker_absent' "$DISC_STEP5" \
     && grep -q '_mangled_probe_path' "$DISC_HELPERS"; then
    ok "E0-2 discriminator step5 블록 + 보조 함수 추출"
  else
    bad "E0-2 discriminator 추출" "step5 블록 또는 _mangled_probe_path 부재 — 형태 변경 의심"
  fi

  # E0-3 추출 무결성 guard — 4 보조 함수가 **실제로 정의**되는가 (0행 추출 = silent hollow 차단)
  E0_DEFS="$(bash -c ". '$DISC_HELPERS'; for fn in _marker_dialect _marker_absent _basename _mangled_probe_path; do
      [ \"\$(type -t \$fn)\" = function ] || printf '%s ' \"\$fn\"; done" 2>/dev/null)"
  if [ -z "$E0_DEFS" ]; then
    ok "E0-3 보조 함수 4종 정의 확인 (_marker_dialect/_marker_absent/_basename/_mangled_probe_path)"
  else
    bad "E0-3 보조 함수 정의" "미정의: $E0_DEFS" "추출 앵커가 실 정의 줄 형태와 어긋남 — 라벨 payload 가 빈 문자열이 된다"
  fi

  # ── L1: 파생 경로 순수 함수 (파일시스템 무관 — 전 플랫폼 결정론) ────────────────
  probe_of() { bash -c ". '$DISC_HELPERS'; _mangled_probe_path \"\$1\" || echo '<rc1>'" _ "$1"; }
  assert_eq "E1 파생 (drive-form 입력)" "$(probe_of 'C:/Users/x/o.json')" "/c/c/Users/x/o.json" \
    "MSYS_NO_PATHCONV 하에서 Windows 프로그램이 실제로 쓰는 그림자 좌표 (E-6)"
  assert_eq "E2 파생 (POSIX 입력)" "$(probe_of '/c/Users/x/o.json')" "/c/c/Users/x/o.json" \
    "이미 POSIX 형 — 드라이브 관례상 c 가정 (best-effort 프로브)"
  assert_eq "E3 파생 (상대 경로 = 후보 도출 불가)" "$(probe_of 'relative/o.json')" "<rc1>" \
    "절대 경로가 아니면 프로브 후보 없음 → rc=1 (허구 좌표 생성 0)"

  # ── L2: 라벨 선택 (arm S = 파생 stub, 전 플랫폼 구동) ────────────────────────────
  #   ★ 정직 seam: arm S 는 **파생 결과** 를 test double 로 주입한다. 파생 정확성은 L1(E1~E3) 이,
  #     실 파생 end-to-end 는 아래 arm R(MSYS) 과 §8.1 T-A Windows oracle 이 각각 결박한다.
  #     L2 가 무는 것은 "**프로브 실재 ↔ 부재가 서로 다른 라벨을 산출하는가**" 단일 속성이다.
  label_of() {   # $1=probe 경로(존재/부재로 D-1/D-2 결정) $2=out_json $3=mutation-sed → "라벨|exit"
    local probe="$1" outjson="$2" mutsed="$3" step5 s rc=0 out
    step5="$(cat "$DISC_STEP5")"
    [ -n "$mutsed" ] && step5="$(printf '%s\n' "$step5" | sed "$mutsed")"
    s="$(mktemp -p "$WORK")"
    {
      printf '. %q\n' "$DISC_HELPERS"
      printf '_mangled_probe_path() { printf %%s %q; }\n' "$probe"
      printf 'm_out_json=%q\n' "$outjson"
      printf '%s\n' "$step5"
    } > "$s"
    out="$(bash "$s" 2>/dev/null)" || rc=$?
    printf '%s|%s' "$out" "$rc"
  }

  mkdir -p "$WORK/mangled"; : > "$WORK/mangled/codex-review-out-design-1-2.json"
  D1_S="$(label_of "$WORK/mangled/codex-review-out-design-1-2.json" \
          'C:/real/codex-review-out-design-1-2.json' '')"
  D2_S="$(label_of "$WORK/absent/codex-review-out-design-1-2.json" \
          'C:/real/codex-review-out-design-1-2.json' '')"
  assert_eq "E4 D-1 (mangled 부모 사전 생성 ⊕ 미교정)" "$D1_S" \
    "[codex-outpath-dialect-mangled: basename=codex-review-out-design-1-2.json]|1" \
    "1순위 probe 로만 도달 — stderr 축은 0줄이라 무산출 (E-6: 조용한 오위치 기록)"
  assert_eq "E5 D-2 (mangled 부모 부재 ⊕ 진짜 산출 0)" "$D2_S" \
    "[codex-output-absent-unclassified: stdout_bytes=-1]|1" \
    "원인 미상 — 단정 금지. stdout 미관측 sentinel -1 (실측 0 과 구별)"
  if [ "${D1_S%|*}" != "${D2_S%|*}" ]; then
    ok "E6 AC-3a 분별 요구 — D-1 라벨 ≠ D-2 라벨 (exit 0 + 부재 한 칸이 2 라벨로 분화)"
  else
    bad "E6 AC-3a 분별 요구" "D-1 == D-2 == ${D1_S%|*} — 분별 0, AC-3a 미충족"
  fi

  # M10 — 1순위(mangled probe) 제거 → 양쪽 다 output-absent-unclassified (분별 0)
  MUT_M10='s/^  if \[ -n "\$probe" \] \&\& \[ -e "\$probe" \]; then$/  if false; then/'
  D1_M10="$(label_of "$WORK/mangled/codex-review-out-design-1-2.json" \
            'C:/real/codex-review-out-design-1-2.json' "$MUT_M10")"
  assert_kill "M10 @ D-1 (1순위 probe 제거)" \
    "${D1_S%|*}" "[codex-outpath-dialect-mangled: basename=codex-review-out-design-1-2.json]" \
    "${D1_M10%|*}" "[codex-output-absent-unclassified: stdout_bytes=-1]" \
    "AC-3a — probe 제거 시 D-1 이 D-2 와 같은 라벨로 붕괴 = 분별 0"
  if [ "${D1_M10%|*}" = "${D2_S%|*}" ]; then
    ok "M10 분별 붕괴 확증 — 변이 하에서 D-1 라벨 == D-2 라벨"
  else
    bad "M10 분별 붕괴 확증" "변이 D-1(${D1_M10%|*}) != D-2(${D2_S%|*}) — 붕괴가 아닌 제3 상태"
  fi

  # ── arm R: 실 파생 end-to-end (MSYS 한정 — 임시 디렉터리가 `/c/…` 하위일 때만 성립) ──
  #   `_mangled_probe_path("/Users/…/tmp.X/o.json")` = `/c` + 입력 = 실 임시 파일 경로.
  #   → **stub 없이** 실 파생으로 D-1/D-2 를 구성한다. `C:\c\` 그림자 트리 실write 0 (호스트 무오염).
  case "$WORK" in
    /c/*)
      R_IN="${WORK#/c}/armR/o.json"
      mkdir -p "$WORK/armR"; : > "$WORK/armR/o.json"
      s="$(mktemp -p "$WORK")"
      { printf '. %q\n' "$DISC_HELPERS"; printf 'm_out_json=%q\n' "$R_IN"; cat "$DISC_STEP5"; } > "$s"
      rc=0; D1_R="$(bash "$s" 2>/dev/null)" || rc=$?
      assert_eq "E7 arm R — 실 파생 D-1 (stub 0)" "$D1_R" \
        "[codex-outpath-dialect-mangled: basename=o.json]" \
        "실 _mangled_probe_path 산출이 실재 파일을 가리켜 1순위 발화 — arm S 의 stub seam 을 결박"
      rm -f "$WORK/armR/o.json"
      rc=0; D2_R="$(bash "$s" 2>/dev/null)" || rc=$?
      assert_eq "E8 arm R — 실 파생 D-2 (동일 입력, 파일만 제거)" "$D2_R" \
        "[codex-output-absent-unclassified: stdout_bytes=-1]" \
        "단일 변수 diff(프로브 대상 파일 유무) 로 라벨이 갈림"
      ;;
    *)
      skip "E7/E8 arm R — 실 파생 end-to-end" \
           "임시 디렉터리가 /c/… 하위가 아님(비-MSYS) — 실 파생 좌표 \`/c/<입력>\` 를 쓰기 가능한 위치로 만들 수 없다. ★ arm S(E4~E6·M10)는 그대로 구동되어 AC-3a 본 판정에 공백 0. 실 방언 end-to-end 는 §8.1 T-A Windows oracle 소관"
      ;;
  esac
fi

# ═══════════════════════════════════════════════════════════════════════════
# §F AC-3b — 처분 단조성 (M11 · verdict 유일 생산처 INV-A)
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §F AC-3b — 처분 단조성 (PASS 승격 0)"
echo "═══════════════════════════════════════════════════════════════════════════"

if [ -f "$LATE_COLLECT" ]; then
  # M11 — dialect-mangled 라벨의 처분을 inconclusive → PASS 로 승격
  #   처분 관측면 = collector exit code (0 = consumed/획득 · ≠0 = 미획득 inconclusive, 스크립트 헤더 계약).
  MUT_M11='s|^    _marker_dialect "\$(_basename "\$m_out_json")"$|&; exit 0|'
  D1_M11="$(label_of "$WORK/mangled/codex-review-out-design-1-2.json" \
            'C:/real/codex-review-out-design-1-2.json' "$MUT_M11")"
  assert_kill "M11 @ D-1 (dialect-mangled 처분 승격)" \
    "${D1_S##*|}" "1" "${D1_M11##*|}" "0" \
    "AC-3b 단일 속성 — 라벨 축(M10)과 번들 금지. 신규 신호가 PASS 를 생산하면 B-b 위반"
  assert_eq "F1 D-2 처분 불변 (M11 스코프 밖)" "${D2_S##*|}" "1" \
    "M11 은 dialect 분기 한정 — D-2 처분이 함께 움직이면 변이 스코프 오귀속"
else
  bad "F0 setup — codex-late-collect.sh 부재" "M11 미실행"
fi

# INV-A / P4 — verdict 유일 생산처 = out.json `verdict` 필드. 그 외 리터럴 PASS 대입 0건.
# ★ vacuity guard 선행: verdict= 대입이 애초에 0건이면 "위반 0건" 은 아무것도 말하지 않는다.
VERDICT_TOTAL="$(gcount '(^|[[:space:];])verdict=' "$FENCE")"
if [ "$VERDICT_TOTAL" -ge 4 ]; then
  ok "F2-pre vacuity guard — 템플릿 verdict= 대입 $VERDICT_TOTAL 건 (≥4) 실재"
else
  bad "F2-pre vacuity guard" "verdict= 대입 $VERDICT_TOTAL 건 < 4 — 아래 INV-A 검사가 vacuous"
fi
VERDICT_BAD="$(grep -oE '(^|[[:space:];])verdict=[^ ;#]*' "$FENCE" 2>/dev/null \
               | sed 's/.*verdict=//' | grep -cvE '^(inconclusive|<out\.json)$')" || VERDICT_BAD=0
assert_eq "F2 INV-A verdict 유일 생산처 (리터럴 승격 대입 0건)" "$VERDICT_BAD" "0" \
  "dispatch 템플릿의 verdict= 대입 RHS ∈ {inconclusive, out.json 필드 read} — 그 외 = PASS 신규 생산처"
cp "$FENCE" "$WORK/fence_inj.sh"
printf '%s\n' 'verdict=PASS' >> "$WORK/fence_inj.sh"
VERDICT_INJ="$(grep -oE '(^|[[:space:];])verdict=[^ ;#]*' "$WORK/fence_inj.sh" 2>/dev/null \
               | sed 's/.*verdict=//' | grep -cvE '^(inconclusive|<out\.json)$')" || VERDICT_INJ=0
assert_eq "F2-disc 탐지력 (verdict=PASS 주입 → 검출)" "$VERDICT_INJ" "1" \
  "F2 가 vacuous 아님 입증"

# T-F4 — preflight 실패 분기가 codex 호출과 제어흐름상 단절돼 있는가 (at-most-once, INV-G)
F3_ELIF="$(gcount '^elif ! codex_outpath_preflight; then$' "$FENCE")"
assert_eq "F3 T-F4 preflight fail-closed 분기 실재 (elif 제어흐름 단절)" "$F3_ELIF" "1" \
  "codex 호출은 else 절 안 — preflight 실패 시 구조적으로 도달 불가 (at-most-once 안전)"
F4_MARKER="$(gcount 'codex-outpath-precheck-failed: reason=' "$FENCE")"
assert_eq "F4 전용 marker 실재 (stall/encoding marker 재사용 0)" "$F4_MARKER" "1" \
  "원인 분별 요구 — 전용 marker 가 아니면 stall 통계까지 오염된다"

# ═══════════════════════════════════════════════════════════════════════════
# §G AC-5 named test — t_dispatch_shell_syntax_bash_n
# ═══════════════════════════════════════════════════════════════════════════
# ★★ 설계 문면 정정 반영 (QADev 판정, DevPL 인계): §8.1 은 "실 CodexReviewAgent.md dispatch 블록 전체
#    `bash -n` **rc=0**" 으로 적었으나 **그 요구는 달성 불가**다 — 펜스 안 `<조립 원본 emit> | …` 줄이
#    placeholder 라 미치환 상태에서 `bash -n` 이 rc=2(`syntax error near unexpected token '|'`)를 낸다.
#    그 줄은 **B-7 byte-frozen 구간(D17 층)** 안이라 수정 = B-7 위반이며, **편집 이전(브랜치 base)부터
#    rc=2** 였다 (본 스위트가 아래 G1-pre 로 그 사실을 실측 기록한다).
#    → 정정된 test 정의 = **placeholder 정규화 후 rc=0** ⊕ **편집 전 ↔ 편집 후 대조로 "신규 문법 오류 0"**.
#    근거 = 설계 §13 자신이 "신규 오류 0" 기준을 쓴다.
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §G AC-5 — t_dispatch_shell_syntax_bash_n (dispatch 블록 문법 무회귀)"
echo "═══════════════════════════════════════════════════════════════════════════"

# 치환 규칙 (test 안 명시 — 설계 문면 요구). 전부 **열거된 리터럴 치환**이며 generic `<…>` 일괄 치환은
#   금지한다: 펜스 안 `- < "$PROMPTFILE"` · `> "$MANIFEST.tmp"` 등 실 리다이렉트를 파괴한다.
#   1) `<…emit>`(줄 선두)            → `printf '%s' ASSEMBLED`
#   2) `verdict=<out.json …read>`    → `verdict=PASS`
#   3) `<packet category_enum, …>`   → `cat-a,cat-b`
#   4) `<packet round_id>`           → `rid-2026-0812-0001`
#   5) `<scratch>`                   → `/tmp/cfp2929-scratch`
#   6) `<lane>`                      → `design`
#   7) `<EFFORT>`                    → `medium`
normalize_placeholders() {
  sed -e 's|^<[^>]*emit>|printf '"'"'%s'"'"' ASSEMBLED|' \
      -e 's/verdict=<out\.json[^>]*>/verdict=PASS/' \
      -e 's/<packet category_enum[^>]*>/cat-a,cat-b/g' \
      -e 's/<packet round_id>/rid-2026-0812-0001/g' \
      -e 's|<scratch>|/tmp/cfp2929-scratch|g' \
      -e 's/<lane>/design/g' \
      -e 's/<EFFORT>/medium/g'
}
# 주석 제거(보수적: 줄 선두 `#` 또는 공백 뒤 `#`) 후 남은 `<…>` = **미등록 신규 placeholder** 신호.
strip_comments() { sed -e 's/[[:space:]]#.*$//' -e 's/^[[:space:]]*#.*$//'; }

NORM_WORK="$WORK/norm_work.sh"
normalize_placeholders < "$FENCE" > "$NORM_WORK"
G_RESID="$(strip_comments < "$NORM_WORK" | grep -cE '<[^<>]*>')" || G_RESID=0
assert_eq "G0 치환 완전성 — 실행 줄 잔여 placeholder 0" "$G_RESID" "0" \
  "미등록 placeholder 가 남으면 bash -n 이 '우연히 유효한 리다이렉트'로 통과해 검사가 hollow 가 된다"
G_RESID_RAW="$(strip_comments < "$FENCE" | grep -cE '<[^<>]*>')" || G_RESID_RAW=0
if [ "$G_RESID_RAW" -ge 1 ]; then
  ok "G0-disc 잔여 guard 판별력 — 미정규화 원본에서 $G_RESID_RAW 건 검출 (never-match 아님)"
else
  bad "G0-disc 잔여 guard 판별력" "미정규화 원본에서도 0건 — guard 가 아무것도 못 잡는다"
fi

G_RC=0; G_OUT="$(bash -n "$NORM_WORK" 2>&1)" || G_RC=$?
if [ "$G_RC" -eq 0 ]; then
  ok "G1 t_dispatch_shell_syntax_bash_n — 정규화 후 dispatch 블록 bash -n rc=0 (편집 후)"
else
  bad "G1 t_dispatch_shell_syntax_bash_n (편집 후)" "rc=$G_RC" "$G_OUT"
fi

# 편집 전 대조 — "신규 문법 오류 0". **기준선 = 브랜치 base 고정** (`git merge-base HEAD origin/main`).
#   ★ `origin/main` 을 기준선으로 직접 쓰면 **움직이는 ref** 다 — 이 repo 는 병렬 세션이 상시라, 남이
#     main 에서 그 파일을 건드리는 순간 "신규 문법 오류 0" 의 기준면이 이동해 대조가 **우리 변경분이
#     아닌 남의 변경분**을 재게 된다. 본 Story 가 관통 진단한 "기준면이 잘못된 측정" class 와 동형.
#   ★ merge-base 는 브랜치 base 를 **동적 도출**하므로 rebase 를 따라간다 — 하드코딩 SHA 는 born-stale
#     이라 금지(B-8 정신). ★ 이 대조 arm 은 기준선에 실측 민감하다: 동일 파일의 과거 리비전 중
#     `154b6e692`·`4361a5de3` 은 raw rc=0 이라 아래 G1-pre(기대 2)가 **뒤집힌다** — 기준선 선택이
#     판정을 바꾼다는 뜻이며, 따라서 기준선 고정은 vacuous 가 아니다.
#   ★ 실패 처리 3단 — ① merge-base 산출 실패 → origin/main fallback 하되 **"기준선 열화" 명시 발화**
#     (조용히 다른 기준으로 재는 것이 가장 나쁘다) ② ref/blob 자체 부재 → 기존 명시 SKIP.
BASE_REF=""
BASE_MB=""
BASE_DESC=""
BASE_DEGRADED=0
if git -C "$REPO_ROOT" rev-parse --verify -q origin/main >/dev/null; then
  if BASE_MB="$(git -C "$REPO_ROOT" merge-base HEAD origin/main 2>/dev/null)" && [ -n "$BASE_MB" ]; then
    BASE_REF="$BASE_MB"
    BASE_DESC="브랜치 base ${BASE_MB:0:9}"
  else
    BASE_REF="origin/main"
    BASE_DESC="origin/main (★기준선 열화)"
    BASE_DEGRADED=1
  fi
fi

if [ -n "$BASE_REF" ] \
   && git -C "$REPO_ROOT" cat-file -e "$BASE_REF:plugins/codeforge-review/agents/CodexReviewAgent.md" 2>/dev/null; then
  if [ "$BASE_DEGRADED" -eq 1 ]; then
    echo "⚠ 기준선 열화: merge-base(HEAD, origin/main) 산출 실패 → 움직이는 ref(origin/main)로 대조한다."
    echo "    병렬 세션이 main 에서 대상 파일을 건드리면 '신규 오류 0' 의 기준면이 이동해 우리 변경분이"
    echo "    아닌 남의 변경분을 재게 된다. FAIL 은 아니지만 **판정 신뢰도 저하**를 조용히 넘기지 않는다."
  fi
  # 기준선 provenance 실측 기록 — 움직이는 ref 와 지금 일치하는지까지 출력에 남긴다(감사 가능).
  echo "  [기준선] $BASE_DESC / origin/main=$(git -C "$REPO_ROOT" rev-parse --short=9 origin/main)"
  git -C "$REPO_ROOT" show "$BASE_REF:plugins/codeforge-review/agents/CodexReviewAgent.md" \
    > "$WORK/md_pre.md"
  extract_fence "$WORK/md_pre.md" > "$WORK/fence_pre.sh"
  normalize_placeholders < "$WORK/fence_pre.sh" > "$WORK/norm_pre.sh"
  P_RC=0; bash -n "$WORK/norm_pre.sh" >/dev/null 2>&1 || P_RC=$?
  assert_eq "G2 편집 전($BASE_DESC) 정규화 후 bash -n rc" "$P_RC" "0" \
    "대조 기준선 — 편집 전이 rc≠0 이면 '신규 오류 0' 판정이 성립하지 않는다"
  assert_eq "G3 신규 문법 오류 0 (편집 전 rc == 편집 후 rc)" "$G_RC" "$P_RC" \
    "AC-5 — B-7 byte-frozen 구간 무접촉 + 삽입분이 문법 회귀를 만들지 않았음"
  # 미정규화 상태 기록 (설계 문면 '원문 rc=0' 요구가 왜 달성 불가인가의 실측 근거)
  R_PRE=0; bash -n "$WORK/fence_pre.sh" >/dev/null 2>&1 || R_PRE=$?
  R_NOW=0; bash -n "$FENCE" >/dev/null 2>&1 || R_NOW=$?
  assert_eq "G1-pre 미정규화 원문은 편집 전부터 rc≠0 (설계 문면 정정 근거)" "$R_PRE" "2" \
    "placeholder \`<…emit> | …\` 가 B-7 byte-frozen 구간 안 — 편집 이전부터 bash -n rc=2"
  assert_eq "G1-now 미정규화 원문 rc 무변 (편집 후에도 동일)" "$R_NOW" "$R_PRE" \
    "미정규화 축에서도 회귀 0 — 정정된 정의가 원 의도(무회귀)를 보존"
else
  skip "G2/G3 편집 전 대조" \
       "기준선 ref(브랜치 base ← merge-base HEAD origin/main, fallback origin/main) 또는 대상 blob 미존재 (shallow clone 등) — G1(편집 후 rc=0) 은 그대로 구동되어 문법 회귀는 여전히 차단"
fi

# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "SKIP: $SKIP"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — R1~R7 결정표 · M-P0/M5/M1/M3/M-a/M-L kill · M5@R4·M1@TREAT 생존(이중화) ·"
  echo "  P-1/P-2/순서 · (b) export 삭제 presence · AC-3a 2라벨 분별(M10) · AC-3b 단조성(M11/INV-A) ·"
  echo "  AC-5 dispatch 블록 문법 무회귀 — 전부 **실 production 텍스트 추출** 기반"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
