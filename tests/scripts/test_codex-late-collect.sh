#!/usr/bin/env bash
# tests/scripts/test_codex-late-collect.sh
# CFP-2929 Phase 2(구현) — `plugins/codeforge-review/scripts/codex-late-collect.sh` discriminating 검증.
#
# 계약(SSOT) = Change Plan §3.0a(3층 + 셀매트릭스 C1~C10) / §3.4(rc stamp `_rc_stamp_ok`) / §3.5(8-step)
#              / §4.2(manifest v1) / §4.3(marker 어휘) / §8.1(단위 범위) / §8.2(BVA·enum·mutation)
#              / §8.5.1(TTL sweep 경계) / §8.5.2(restart recovery) / §8.5.3(replay) / §11.6(idempotency).
#
# ★ 최종 설계 = `round_id`(회차 유일 토큰 동등 비교). 은퇴 토큰(`not_before` 시각 하한 / NOT_BEFORE_FLOOR /
#   CLOCK_SKEW_TOL / CAPTURE_EPS / `caller-bound-inverted` / M-NB / BVA `dispatch_start − not_before` 행)은
#   본 스위트에서 **일절 사용하지 않는다**. 문서 잔존 토큰은 은퇴 기록이다.
#
# 검사연극 금지(비협상):
#   · 전 케이스 **단일 기대** — `or`(조건부 기대) 0. 플랫폼 분기(M-RCG(b) CRLF)는 `uname` 관측으로
#     환경별 **단일** 기대를 고르는 것이지 한 환경에서 두 답을 허용하는 것이 아니다.
#   · always-GREEN 금지 — `|| true` · `|| skip` · `2>/dev/null; rc=0` 로 판정을 삼키는 형태 0.
#     setup 불충족은 **skip 아니라 FAIL**(C0 블록).
#   · mutant 는 열거가 아니라 **실행** — 매 실행마다 변이본을 생성해 미변이 관측 ↔ 변이 관측이 실제로
#     갈리는지 재현한다. 변이가 텍스트에 적용되지 않으면(no-op sed) 그 자체를 FAIL 로 낸다.
#   · 생존 변이는 삭제하지 않고 **"생존 기대(이중화 확인)"** 로 정직 재라벨해 관측을 고정한다.
#
# RED 진정성: 본 스위트는 self-contained 변이 fixture 를 **매 실행 재생성**하므로, 구현이 working tree 에
#   선착한 cross-layer 상황에서도 각 층(L1/L2/L3)·각 파서 형태의 discriminating power 가 그때그때 재입증된다
#   (git stash 사후입증에 의존하지 않는 형태 — 변이 arm 이 곧 pre-GREEN 등가 관측).
#
# `set -e` 미사용: SUT 는 **정상적으로** rc=1(inconclusive)/rc=2(usage)를 반환하는 것이 계약이라
#   `-e` 는 하네스를 조기 종료시켜 관측을 소실시킨다. 유일 pass/fail 신호 = 근접 PASS/FAIL 카운터이며
#   말미에서 FAIL>0 이면 exit 1 (exit-masking 아님 — 모든 rc 는 캡처되어 assert 로 gating 된다).
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PLUGIN_ROOT="$REPO_ROOT/plugins/codeforge-review"
SUT="$PLUGIN_ROOT/scripts/codex-late-collect.sh"
HELPER_PY="$REPO_ROOT/scripts/lib/check_codex_review_output_schema.py"
HELPER_SCHEMA="$PLUGIN_ROOT/schemas/codex-review-output-schema-v1.json"

PASS=0
FAIL=0

WORK="$(mktemp -d)"
# shellcheck disable=SC2064
trap "rm -rf '$WORK'" EXIT

HOME_DIR="$WORK/home"
CR_DIR="$HOME_DIR/.claude/codeforge-scratch/codex-review"
MUT_DIR="$WORK/mut"
mkdir -p "$MUT_DIR"

# OP-1 하한 = timeout_n + kill_after_k + OP1_MARGIN_SEC(30). 본 스위트 기본 fixture = 240/30 → 300.
TN=240
KK=30
BOUND=$((TN + KK + 30))

RID0='rid-2026-0812-0001'      # 원 회차 토큰 (LEAD 발급 모사)
RID2='rid-2026-0812-0002'      # 이번 회차 토큰 (규약 준수 argv)
RIDNEW='rid-2026-0812-9999'    # collect 시점 재발급 (규약 위반)

pass() { echo "  [PASS] $1"; PASS=$((PASS + 1)); }
fail() { echo "  [FAIL] $1"; FAIL=$((FAIL + 1)); }

section() { echo; echo "── $1 ──"; }

# ════════════════════════════════════════════════════════════════════════════
#  fixture 유틸
# ════════════════════════════════════════════════════════════════════════════

fx_reset() { rm -rf "$HOME_DIR"; mkdir -p "$CR_DIR"; }

out_path() { printf '%s/codex-review-out-%s-%s.json' "$CR_DIR" "$1" "$2"; }   # <lane> <ts>

# 유효 out.json (schema v1 준수 + counts↔findings cross-field 정합 + findings 빈 배열이라 category enum 무조건 통과)
out_json_body() { printf '{"verdict":"%s","counts":{"P0":0,"P1":0,"P2":0,"P3":0},"findings":[]}\n' "$1"; }
write_out_json() { out_json_body "$2" > "$1"; }

# manifest v1 (§4.2 8행 9키 ⊕ **필수 필드** `category_enum` — helper 3번째 인자 조달 경로.
#   §4.2 승격 = DeveloperPL 판정, ArchitectPL 비준 대기. "additive 선택 필드" 아니다 — 강제점은 §H 참조)
manifest_body() {   # <lane> <dispatch_id> <round_id> <out_json> <dispatch_start> [tn] [kk] [category_enum]
  local lane="$1" did="$2" rid="$3" oj="$4" ds="$5" tn="${6:-$TN}" kk="${7:-$KK}" ce="${8:-runtime-bug}"
  printf '{"schema":"codex-dispatch-manifest-v1","lane":"%s","dispatch_id":"%s","round_id":"%s","out_json":"%s","promptfile":"%s/codex-review-%s-%s.md","category_enum":"%s","dispatch_start":%s,"timeout_n":%s,"kill_after_k":%s}\n' \
    "$lane" "$did" "$rid" "$oj" "$CR_DIR" "$lane" "$did" "$ce" "$ds" "$tn" "$kk"
}
write_manifest() { manifest_body "$@" > "$CR_DIR/dispatch-$1.json"; }

rc_stamp_path() { printf '%s/dispatch-%s.rc' "$CR_DIR" "$1"; }
# shellcheck disable=SC2059  # 형식 문자열을 인자로 받는 것은 12 바이트열 형상 fixture 의 요건
write_rc_fmt() { local lane="$1" fmt="$2"; shift 2; printf "$fmt" "$@" > "$(rc_stamp_path "$lane")"; }

set_mtime() { touch -d "@$2" "$1"; }
get_mtime() { stat -c %Y "$1" 2>/dev/null; }

# ── 결정론적 클럭 스텁 (elapsed 경계 BVA 전용) ───────────────────────────────
# ★ 왜 필요한가(firsthand): SUT 1회 호출 비용이 초 단위라 `dispatch_start` 를 `now−(BOUND−1)` 로 놓고
#   벽시계로 되재는 방식은 **경계 관측이 구조적으로 불가능**하다 — 스크립트가 `date +%s` 를 읽는 시점이
#   측정 시점보다 1초 이상 뒤라 elapsed 가 항상 하한을 넘어간다(1회차 실행에서 straddle 8/8 실측).
#   재시도로 덮으면 flaky 하거나(운) 조용히 관측을 포기하게 된다 → **클럭을 주입해 축을 결정론화**한다.
#   스텁은 `date +%s` 정확히 그 형태만 고정값으로 답하고 나머지 호출은 실 date 로 위임한다.
REAL_DATE="$(command -v date)"
mk_date_stub() {   # <fixed_epoch>
  mkdir -p "$WORK/bin"
  {
    printf '#!/usr/bin/env bash\n'
    printf 'if [ "$#" -eq 1 ] && [ "$1" = "+%%s" ]; then printf "%%s\\n" "%s"; exit 0; fi\n' "$1"
    printf 'exec "%s" "$@"\n' "$REAL_DATE"
  } > "$WORK/bin/date"
  chmod +x "$WORK/bin/date"
}

# 소비 가능한 정상 fixture 1식 (clean, 하한 충족, 신선, rc stamp 정상)
# 산출 전역: FX_TS / FX_DS / FX_OUT
mk_consumable() {   # [lane] [round_id] [dispatch_id]
  local lane="${1:-design}" rid="${2:-$RID0}"
  FX_DS=$(( $(date +%s) - 400 ))
  FX_TS="${3:-${FX_DS}-11111}"
  FX_OUT="$(out_path "$lane" "$FX_TS")"
  write_out_json "$FX_OUT" PASS
  write_manifest "$lane" "$FX_TS" "$rid" "$FX_OUT" "$FX_DS"
  write_rc_fmt "$lane" '%s 0\n' "$FX_TS"
}

# 직전 회차(#1) 잔재 삼중조 — 셋이 **서로 내부정합**인 것이 요점 (§8.5.2 residue 초기조건).
# 산출 전역: R1_TS / R1_DS / R1_OUT
mk_residue() {   # [lane]
  local lane="${1:-design}"
  R1_DS=$(( $(date +%s) - 900 ))
  R1_TS="${R1_DS}-10001"
  R1_OUT="$(out_path "$lane" "$R1_TS")"
  write_out_json "$R1_OUT" PASS                                   # valid · verdict=PASS · 미봉인
  write_manifest "$lane" "$R1_TS" "$RID0" "$R1_OUT" "$R1_DS"      # round_id = rid1(=RID0)
  write_rc_fmt "$lane" '%s 0\n' "$R1_TS"                          # "<TS1> 0"
}

# ════════════════════════════════════════════════════════════════════════════
#  SUT 실행 / assert 유틸
# ════════════════════════════════════════════════════════════════════════════

SUT_ENV=()
RC=0; OUT=''; ERR=''

run_sut() {   # <script> [argv...]
  local script="$1"; shift
  OUT="$(env HOME="$HOME_DIR" CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
           ${SUT_ENV[@]+"${SUT_ENV[@]}"} bash "$script" "$@" 2>"$WORK/stderr.txt")"
  RC=$?
  ERR="$(cat "$WORK/stderr.txt" 2>/dev/null)"
}
run_collect() { run_sut "$SUT" "$@"; }

has_out() { printf '%s' "$OUT" | grep -qF -- "$1"; }

# 단일 기대 assert: rc ⊕ marker. <exp_marker> = 리터럴 또는 NONE(= `[codex-` 계열 marker 미발화).
assert_result() {   # <label> <exp_rc> <exp_marker|NONE>
  local label="$1" exp_rc="$2" exp_marker="$3"
  if [ "$RC" = "$exp_rc" ]; then
    pass "$label — rc=$exp_rc"
  else
    fail "$label — rc=$RC (기대 $exp_rc) | stdout=[${OUT//$'\n'/ }] | stderr=[${ERR//$'\n'/ }]"
  fi
  if [ "$exp_marker" = NONE ]; then
    if has_out '[codex-'; then
      fail "$label — marker 미발화 기대인데 발화: [${OUT//$'\n'/ }]"
    else
      pass "$label — outcome/rejected marker 미발화"
    fi
  else
    if has_out "$exp_marker"; then
      pass "$label — marker '$exp_marker'"
    else
      fail "$label — marker '$exp_marker' 미검출 | stdout=[${OUT//$'\n'/ }]"
    fi
  fi
}

# PASS 0 (소비 0) — verdict 미발화 ∧ 봉인 미발생 ∧ 원본 좌표 잔존.
assert_pass0() {   # <label> <out_json>
  local label="$1" oj="$2"
  if has_out 'verdict='; then
    fail "$label — PASS 0 위반: verdict 발화 [${OUT//$'\n'/ }]"
  else
    pass "$label — verdict 미발화 (PASS 0)"
  fi
  if [ -e "${oj}.consumed" ]; then
    fail "$label — PASS 0 위반: .consumed 봉인 발생 (소비됨)"
  else
    pass "$label — .consumed 미생성 (소비 0)"
  fi
}

assert_consumed() {   # <label> <out_json> <verdict>
  local label="$1" oj="$2" v="$3"
  if has_out "verdict=$v"; then pass "$label — verdict=$v 발화"; else fail "$label — verdict=$v 미발화 [${OUT//$'\n'/ }]"; fi
  if [ -e "${oj}.consumed" ]; then pass "$label — .consumed 원자적 봉인"; else fail "$label — .consumed 미생성 (봉인 실패)"; fi
  if [ -e "$oj" ]; then fail "$label — 원 좌표 잔존 (rename 아님 = 재소비 가능)"; else pass "$label — 원 좌표 소멸 (at-most-once)"; fi
}

# ════════════════════════════════════════════════════════════════════════════
#  mutant 생성 (production 파일 무접촉 — $WORK 사본에만 적용)
# ════════════════════════════════════════════════════════════════════════════

cat > "$WORK/mutate.py" <<'PYEOF'
#!/usr/bin/env python3
"""CFP-2929 QADev — codex-late-collect.sh 변이 생성기.

변이가 실제로 적용되지 않으면 exit 3 (no-op 변이가 '생존' 으로 오독되는 것을 차단).
newline='' 로 write 하여 Windows CRLF 변환을 배제한다 (셸 스크립트 born-broken 회피).
"""
import sys

MODE, SRC, DST = sys.argv[1], sys.argv[2], sys.argv[3]
with open(SRC, encoding='utf-8', newline='') as fh:
    s = fh.read()
orig = s


def replace_rc_stamp_ok(text, new_fn):
    i = text.index('_rc_stamp_ok() {')
    j = text.index('\n}\n', i) + 3
    return text[:i] + new_fn + text[j:]


if MODE == 'M4b':
    # L2 제거 — rc stamp 1st 토큰 ↔ manifest dispatch_id 귀속 검사 삭제 (2nd 토큰만 채택).
    needle = '  [ "${BASH_REMATCH[1]}" = "$2" ] || return 1\n'
    if needle not in s:
        sys.exit(4)
    s = s.replace(needle, '  : # [M4b mutant] L2 프로세스 귀속 검사 삭제\n', 1)
elif MODE == 'M4c':
    # L3 제거 — step 2b 회차 귀속 동등 비교 삭제 (round_id 인자 무시).
    needle = ('if [ "$m_round_id" != "$ARGV_ROUND_ID" ]; then\n'
              '  _marker_rejected stale-manifest\n'
              '  exit 1\n'
              'fi\n')
    if needle not in s:
        sys.exit(4)
    s = s.replace(needle, ': # [M4c mutant] step 2b 회차 귀속 결박 삭제\n', 1)
elif MODE == 'RCGa':
    # 파서를 `read -r t1 t2 rest` 2-토큰 형으로 교체 (iter2 폐기형).
    s = replace_rc_stamp_ok(s, '''_rc_stamp_ok() {   # [M-RCG(a) mutant] 2-토큰 read 형
  local f="$1" t1='' t2='' rest=''
  [ -f "$f" ] || return 1
  read -r t1 t2 rest < "$f"
  [[ "$t1" =~ ^[0-9]+-[0-9]+$ ]] || return 1
  [[ "$t2" =~ ^[0-9]+$ ]] || return 1
  [ "$t1" = "$2" ] || return 1
  RC_STAMP_VALUE="$t2"; return 0
}
''')
elif MODE == 'RCGb':
    # 파서를 `content="$(cat …)"` 변형-산출 비교형으로 교체 (iter3 폐기형).
    s = replace_rc_stamp_ok(s, '''_rc_stamp_ok() {   # [M-RCG(b) mutant] 명령치환 변형-산출 비교형
  local f="$1" content=''
  [ -f "$f" ] || return 1
  content="$(cat "$f")"
  [[ "$content" =~ ^([0-9]+-[0-9]+)\\ ([0-9]+)$ ]] || return 1
  [ "${BASH_REMATCH[1]}" = "$2" ] || return 1
  RC_STAMP_VALUE="${BASH_REMATCH[2]}"; return 0
}
''')
elif MODE == 'CE':
    # step 2 `category_enum` 필수 검증 제거 (§H 은폐 회귀 재현용).
    # ★ 줄 **삭제가 아니라 중화**: 삭제하면 `m_category_enum` 이 미결박돼 `set -u` 로 죽고, 그 죽음이
    #   '관측 상이' 로 오독된다(변이본 born-broken). `_schema_reject` → `:` 치환은 대입은 남기고 처분만 없앤다.
    # 앵커 = `category_enum` ∧ `_schema_reject` 를 **함께** 갖는 줄. step 7 의 category_enum 줄은
    #   `_schema_reject` 를 갖지 않으므로 변이 표면이 step 2 로 한정된다(= step 7 잔여 검사는 그대로 살려둔 채
    #   '검증이 step 2 에 있는가' 축만 변주 — 변이 귀속이 흐려지지 않는다).
    lines = s.split('\n')
    hit = 0
    for idx, ln in enumerate(lines):
        if 'category_enum' in ln and '_schema_reject' in ln:
            lines[idx] = ln.replace('_schema_reject', ':')
            hit += 1
    if hit == 0:
        sys.exit(4)
    s = '\n'.join(lines)
else:
    sys.exit(5)

if s == orig:
    sys.exit(3)
with open(DST, 'w', encoding='utf-8', newline='') as fh:
    fh.write(s)
PYEOF

PYBIN=''
MUT_PATH=''

# ★ 전역 MUT_PATH 로 결과를 돌려준다 — `$(mk_mutant …)` 형이면 fail() 이 서브셸에서 실행돼
#   PASS/FAIL 카운터 증가가 유실되고 진단 문구가 caller 변수로 흡수된다(관측 소실).
mk_mutant() {   # <mode> → MUT_PATH 설정. 실패 시 FAIL 등재 후 rc=1.
  local mode="$1" dst="$MUT_DIR/codex-late-collect.$1.sh" rc=0
  MUT_PATH=''
  "$PYBIN" "$WORK/mutate.py" "$mode" "$SUT" "$dst" || rc=$?
  if [ "$rc" -ne 0 ]; then
    fail "mutant $mode 생성 실패 (mutate.py rc=$rc — 3=텍스트 무변화 / 4=앵커 미발견) : 변이 미적용은 '생존' 이 아니다"
    return 1
  fi
  if cmp -s "$SUT" "$dst"; then
    fail "mutant $mode — 변이본이 원본과 byte 동일 (no-op 변이)"
    return 1
  fi
  # 변이본 문법 정합 (born-broken 변이로 rc=2 가 나와 '관측 상이' 로 오독되는 것 차단)
  if ! bash -n "$dst" 2>"$WORK/mut_syntax.txt"; then
    fail "mutant $mode — bash -n 실패 (변이본 born-broken): $(tr '\n' ' ' < "$WORK/mut_syntax.txt")"
    return 1
  fi
  MUT_PATH="$dst"
  return 0
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2929: codex-late-collect.sh — AC-10 / AC-11 / rc stamp 12형상 / 3층 mutant"
echo "═══════════════════════════════════════════════════════════════════════════"

# ════════════════════════════════════════════════════════════════════════════
#  C0 setup guard — 불충족은 skip 이 아니라 FAIL
# ════════════════════════════════════════════════════════════════════════════
section "C0 setup guard"

if [ -f "$SUT" ]; then pass "C0a: SUT 실재 (plugins/codeforge-review/scripts/codex-late-collect.sh)"; else fail "C0a: SUT 부재 — $SUT"; fi
if [ -f "$HELPER_PY" ]; then pass "C0b: AC-6 helper 실재 (모사 helper 금지)"; else fail "C0b: AC-6 helper 부재 — $HELPER_PY"; fi
if [ -f "$HELPER_SCHEMA" ]; then pass "C0c: out.json schema 실재"; else fail "C0c: schema 부재 — $HELPER_SCHEMA"; fi

if command -v python3 >/dev/null 2>&1; then PYBIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then PYBIN="$(command -v python)"
fi
if [ -n "$PYBIN" ]; then pass "C0d: python 인터프리터 가용 ($PYBIN) — helper 실행·변이 생성 전제"; else fail "C0d: python 부재 — AC-6 helper 재검증 경로 구동 불가 (skip 아님)"; fi

# touch -d @epoch 왕복 (mtime BVA 전제)
fx_reset
: > "$WORK/mt.probe"
if set_mtime "$WORK/mt.probe" 1700000000 2>/dev/null && [ "$(get_mtime "$WORK/mt.probe")" = 1700000000 ]; then
  pass "C0e: touch -d @epoch ↔ stat 왕복 정합 (mtime fixture 구성 가능)"
else
  fail "C0e: touch -d @epoch 왕복 실패 — mtime BVA fixture 구성 불가"
fi

# §3.3 1순위 probe 오염 가드: `/c<posix>` 그림자 트리가 실재하면 absent 기대가 dialect-mangled 로 갈린다.
PROBE_SHADOW="/c${CR_DIR}"
if [ -e "$PROBE_SHADOW" ]; then
  fail "C0f: mangled probe 그림자 경로가 선재 ($PROBE_SHADOW) — absent 기대가 오염됨 (환경 정리 필요)"
else
  pass "C0f: mangled probe 그림자 경로 부재 — absent/dialect 분별 유효"
fi

# rc stamp 특수 바이트 fixture 생성능력 (NUL·CR 이 실제로 파일에 실리는가)
# 기대 바이트 = len(TS) + 4 (' ' + '0' + 개행 + 특수바이트 1). 하드코딩하지 않고 TS 길이에서 도출한다.
PROBE_TS='1786000000-1'
EXP_SPECIAL_BYTES=$(( ${#PROBE_TS} + 4 ))
write_rc_fmt design '%s 0\n\0' "$PROBE_TS"
NUL_BYTES="$(wc -c < "$(rc_stamp_path design)" | tr -d ' ')"
write_rc_fmt design '%s 0\r\n' "$PROBE_TS"
CR_BYTES="$(wc -c < "$(rc_stamp_path design)" | tr -d ' ')"
if [ "$NUL_BYTES" = "$EXP_SPECIAL_BYTES" ] && [ "$CR_BYTES" = "$EXP_SPECIAL_BYTES" ]; then
  pass "C0g: NUL·CR 바이트 fixture 생성 정합 (각 ${EXP_SPECIAL_BYTES}B — printf 가 \\0/\\r 을 실제 기록)"
else
  fail "C0g: 특수 바이트 fixture born-broken (NUL=${NUL_BYTES}B CR=${CR_BYTES}B, 각 ${EXP_SPECIAL_BYTES} 기대) — 12형상 판별 무효"
fi

# ════════════════════════════════════════════════════════════════════════════
#  AC-10 — late-collect 로 재dispatch 없이 verdict 1회 회수
# ════════════════════════════════════════════════════════════════════════════
section "AC-10 t_ac10_consumed_happy_path (정상 소비 = AC-10 teeth)"

t_ac10_consumed_happy_path() {
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID0"
  assert_result "AC-10 happy" 0 '[codex-late-collect: outcome=consumed]'
  assert_consumed "AC-10 happy" "$FX_OUT" PASS
}
t_ac10_consumed_happy_path

# ════════════════════════════════════════════════════════════════════════════
#  AC-11 — manifest-only 2-hop 경로 도출 (dispatch 셸 변수 0)
# ════════════════════════════════════════════════════════════════════════════
section "AC-11 t_ac11_manifest_only_path_derivation (셸 변수 없이 좌표 특정)"

t_ac11_manifest_only_path_derivation() {
  fx_reset
  # 추측 불가능한 dispatch_id — collector 는 lane 만 알고 고정경로 manifest 를 거쳐야만 이 좌표에 닿는다.
  local ds ts oj
  ds=$(( $(date +%s) - 400 )); ts='9999999999-98765'
  oj="$(out_path design "$ts")"
  write_out_json "$oj" ISSUES
  write_manifest design "$ts" "$RID0" "$oj" "$ds"
  write_rc_fmt design '%s 0\n' "$ts"
  # env 에 dispatch 셸 변수(OUT_JSON/TS/DISPATCH_START)를 일절 주지 않는다 — run_sut 는 HOME/PLUGIN_ROOT 만 전달.
  run_collect design "$RID0"
  assert_result "AC-11 2-hop" 0 '[codex-late-collect: outcome=consumed]'
  assert_consumed "AC-11 2-hop" "$oj" ISSUES
}
t_ac11_manifest_only_path_derivation

# ════════════════════════════════════════════════════════════════════════════
#  §8.2 collection·string size — rc stamp 전체-파일 바이트 검증 12 형상
#  정상 1형 외 전건 rc-unknown.
# ════════════════════════════════════════════════════════════════════════════
section "§8.2 t_rcstamp_12_shapes (정상 1 · 거부 11)"

t_rcstamp_12_shapes() {
  local lane=design other='1700000000-99999'
  # shape: <라벨>|<printf fmt>|<기대: CONSUMED|RCUNK>
  local shapes=(
    'S01 empty|                       |RCUNK'
    'S02 1-토큰 "0\\n"|0\n|RCUNK'
    'S03 정상 "<TS> 0\\n"|%s 0\n|CONSUMED'
    'S04 다른TS(프로세스 귀속 불일치)|OTHER|RCUNK'
    'S05 2nd 비정수 "<TS> abc\\n"|%s abc\n|RCUNK'
    'S06 3-토큰 "<TS> 0 extra\\n"|%s 0 extra\n|RCUNK'
    'S07 2행|%s 0\n%s 0\n|RCUNK'
    'S08 개행 미종료 "<TS> 0"|%s 0|RCUNK'
    'S09 선행 공백 " <TS> 0\\n"| %s 0\n|RCUNK'
    'S10 NUL 후행 "<TS> 0\\n\\0"|%s 0\n\0|RCUNK'
    'S11 NUL 선행 "<TS> 0\\0\\n"|%s 0\0\n|RCUNK'
    'S12 CRLF "<TS> 0\\r\\n"|%s 0\r\n|RCUNK'
    'S13 3-토큰(수치) "<TS> 0 7\\n" ★§8 12형상 외 보강 — ArchitectPL 회부 대상|%s 0 7\n|RCUNK'
  )
  local row label fmt want
  for row in "${shapes[@]}"; do
    label="${row%%|*}"; want="${row##*|}"; fmt="${row#*|}"; fmt="${fmt%|*}"
    fx_reset; mk_consumable "$lane" "$RID0"
    case "$label" in
      'S01 empty') : > "$(rc_stamp_path "$lane")" ;;
      'S04'*)      write_rc_fmt "$lane" '%s 0\n' "$other" ;;
      'S07 2행')   write_rc_fmt "$lane" "$fmt" "$FX_TS" "$FX_TS" ;;
      'S02'*)      write_rc_fmt "$lane" "$fmt" ;;
      *)           write_rc_fmt "$lane" "$fmt" "$FX_TS" ;;
    esac
    run_collect "$lane" "$RID0"
    if [ "$want" = CONSUMED ]; then
      assert_result "rcstamp $label" 0 '[codex-late-collect: outcome=consumed]'
      assert_consumed "rcstamp $label" "$FX_OUT" PASS
    else
      assert_result "rcstamp $label" 1 '[codex-collect-rejected: reason=rc-unknown]'
      assert_pass0 "rcstamp $label" "$FX_OUT"
    fi
  done
}
t_rcstamp_12_shapes

# ════════════════════════════════════════════════════════════════════════════
#  §8.2 BVA
# ════════════════════════════════════════════════════════════════════════════
section "§8.2 t_bva_elapsed_lower_bound (elapsed = N+K+margin ∓1)"

t_bva_elapsed_lower_bound() {
  local ds=1786000000 delta want probe
  for delta in -1 0 1; do
    fx_reset
    mk_date_stub $((ds + BOUND + delta))         # 스크립트가 볼 now = dispatch_start + BOUND + delta
    SUT_ENV=(PATH="$WORK/bin:$PATH")
    # 스텁 실효 확인 — 미실효면 경계 관측이 통째로 무의미해지므로 FAIL (skip 아님)
    probe="$(env PATH="$WORK/bin:$PATH" date +%s)"
    if [ "$probe" = "$((ds + BOUND + delta))" ]; then
      pass "BVA elapsed=BOUND$( [ "$delta" -ge 0 ] && printf '+' )$delta — 클럭 스텁 실효 확인 (now=$probe)"
    else
      fail "BVA elapsed 경계 — 클럭 스텁 미실효 (date +%s → $probe) : 경계 관측 무효"
    fi
    write_manifest design "${ds}-22222" "$RID0" "$(out_path design "${ds}-22222")" "$ds"
    write_rc_fmt design '%s 0\n' "${ds}-22222"   # out.json 은 **미생성** (step 4/5 축)
    run_collect design "$RID0"
    SUT_ENV=()
    if [ "$delta" = -1 ]; then
      want='[codex-late-collect: outcome=in-flight]'
      assert_result "BVA elapsed=BOUND-1 (하한 미충족 → in-flight, 재dispatch 금지)" 1 "$want"
    else
      want='[codex-output-absent-unclassified: stdout_bytes=-1]'
      assert_result "BVA elapsed=BOUND$( [ "$delta" = 0 ] && printf '(하한 도달)' || printf '+1' )" 1 "$want"
    fi
  done
}
t_bva_elapsed_lower_bound

section "§8.2 t_bva_mtime_freshness (mtime − dispatch_start = −1 / 0 / +1)"

t_bva_mtime_freshness() {
  local delta lbl
  for delta in -1 0 1; do
    fx_reset; mk_consumable design "$RID0"
    set_mtime "$FX_OUT" $((FX_DS + delta))
    lbl="BVA mtime−dispatch_start=$delta"
    if [ "$(get_mtime "$FX_OUT")" != "$((FX_DS + delta))" ]; then
      fail "$lbl — mtime 설정 실패 (fixture born-broken)"
      continue
    fi
    run_collect design "$RID0"
    if [ "$delta" = -1 ]; then
      assert_result "$lbl" 1 '[codex-collect-rejected: reason=stale-artifact]'
      assert_pass0 "$lbl" "$FX_OUT"
    else
      assert_result "$lbl" 0 '[codex-late-collect: outcome=consumed]'
      assert_consumed "$lbl" "$FX_OUT" PASS
    fi
  done
}
t_bva_mtime_freshness

section "§8.2 t_bva_dispatch_start_digits (10자리 / 11자리 / bignum)"

t_bva_dispatch_start_digits() {
  local ds ts
  # 10자리 = 통과 (정상 소비)
  fx_reset; mk_consumable design "$RID0"
  if [ "${#FX_DS}" = 10 ]; then pass "BVA dispatch_start 10자리 fixture 확인 (${#FX_DS})"; else fail "BVA dispatch_start fixture 자릿수 = ${#FX_DS} (10 기대)"; fi
  run_collect design "$RID0"
  assert_result "BVA dispatch_start 10자리" 0 '[codex-late-collect: outcome=consumed]'

  # 11자리 = schema 축 fail-closed (stale-manifest 와 섞지 않는다 → marker 미발화)
  for ds in 17865171770 9223372036854775808; do
    fx_reset
    ts='1786000000-55555'
    write_out_json "$(out_path design "$ts")" PASS
    write_manifest design "$ts" "$RID0" "$(out_path design "$ts")" "$ds"
    write_rc_fmt design '%s 0\n' "$ts"
    run_collect design "$RID0"
    assert_result "BVA dispatch_start=$ds (${#ds}자리) schema 축" 1 NONE
    assert_pass0 "BVA dispatch_start=$ds" "$(out_path design "$ts")"
  done
}
t_bva_dispatch_start_digits

# ════════════════════════════════════════════════════════════════════════════
#  §8.2 caller 인자 축 — round_id / lane
# ════════════════════════════════════════════════════════════════════════════
section "§8.2 t_argv_round_id_axis"

t_argv_round_id_axis() {
  local rid65 i=0
  rid65=''
  while [ "$i" -lt 65 ]; do rid65="${rid65}a"; i=$((i + 1)); done

  # 미전달 (1 인자) — rc=2 usage · outcome marker 미발화
  fx_reset; mk_consumable design "$RID0"
  run_collect design
  assert_result "argv round_id 미전달" 2 NONE
  assert_pass0 "argv round_id 미전달" "$FX_OUT"

  # 형식 위반 5종 — 전건 rc=2 usage
  local bad
  for bad in '' 'abc' "$rid65" 'a b' '../etc'; do
    fx_reset; mk_consumable design "$RID0"
    run_collect design "$bad"
    assert_result "argv round_id 형식위반 '${bad:0:12}'(len=${#bad})" 2 NONE
    assert_pass0 "argv round_id 형식위반 '${bad:0:12}'" "$FX_OUT"
  done

  # 정상 형식이나 manifest 부재 → step 0 통과 증명 (no-dispatch 도달)
  fx_reset
  run_collect design "$RID0"
  assert_result "argv round_id 'rid-2026-0812-0001' 형식 통과" 1 '[codex-late-collect: outcome=no-dispatch]'

  # manifest 와 다른 값 → step 2b stale-manifest
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID2"
  assert_result "argv round_id ≠ manifest" 1 '[codex-collect-rejected: reason=stale-manifest]'
  assert_pass0 "argv round_id ≠ manifest" "$FX_OUT"

  # manifest 와 같은 값 → 정상
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID0"
  assert_result "argv round_id = manifest" 0 '[codex-late-collect: outcome=consumed]'
}
t_argv_round_id_axis

section "§8.2 t_argv_lane_enum_axis (closed enum 4종 + invalid)"

t_argv_lane_enum_axis() {
  local lane
  for lane in requirements-review design code security; do
    fx_reset
    run_collect "$lane" "$RID0"
    assert_result "lane enum '$lane' 수용" 1 '[codex-late-collect: outcome=no-dispatch]'
  done
  for lane in '../etc' '' 'Design'; do
    fx_reset
    run_collect "$lane" "$RID0"
    assert_result "lane enum 밖 '$lane' 거부 (경로 보간 전)" 2 NONE
  done
}
t_argv_lane_enum_axis

# ════════════════════════════════════════════════════════════════════════════
#  §8.5.2 restart recovery — clean 초기조건 (S-1 / S-2 / S-3)
# ════════════════════════════════════════════════════════════════════════════
section "§8.5.2 clean 초기조건 — t_s1 / t_s2 / t_s3 (구성 상태)"

t_s1_clean_out_before_rcstamp() {
  # clean ⊕ out.json write 후 · rc stamp write 전 SIGKILL → rc-unknown ∧ PASS 0 (INV-F)
  fx_reset; mk_consumable design "$RID0"
  rm -f "$(rc_stamp_path design)"
  run_collect design "$RID0"
  assert_result "S-1 clean·out후·stamp전 사망" 1 '[codex-collect-rejected: reason=rc-unknown]'
  assert_pass0 "S-1" "$FX_OUT"
}
t_s1_clean_out_before_rcstamp

t_s2_clean_after_rcstamp() {
  # clean ⊕ rc stamp write 후 SIGKILL → 정상 소비 (M9 의 kill 행 = 이 arm 이 소비 가능해야 AC-10 이 teeth)
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID0"
  assert_result "S-2 clean·stamp후 사망" 0 '[codex-late-collect: outcome=consumed]'
  assert_consumed "S-2" "$FX_OUT" PASS
}
t_s2_clean_after_rcstamp

t_s3_clean_before_manifest() {
  # clean ⊕ manifest write 전 SIGKILL → no-dispatch
  fx_reset
  run_collect design "$RID0"
  assert_result "S-3 clean·manifest전 사망" 1 '[codex-late-collect: outcome=no-dispatch]'
}
t_s3_clean_before_manifest

section "§8.5.2 t_sigkill_reachability (실 SIGKILL 로 S-1/S-2/S-3 상태 도달 가능성 입증)"

cat > "$WORK/dispatch_sim.sh" <<'SIMEOF'
#!/usr/bin/env bash
# dispatch 셸 사망 모사 — production write 순서(manifest → out.json → rc stamp)를 그대로 따르고
# 지정 stage 까지 쓴 뒤 sleep 에서 SIGKILL 을 받는다. 내용은 전부 argv 로 주입(테스트와 단일 원본).
set -u
# ★ RBODY 는 개행 **없이** 받아 여기서 `\n` 을 붙인다 — `$( )` 가 후행 개행을 제거하므로 caller 에서
#   완성 바이트열을 넘기면 rc stamp 가 '개행 미종료' 형이 되어 S-2 정상 arm 이 born-red 가 된다.
STAGE="$1"; MPATH="$2"; MBODY="$3"; OPATH="$4"; OBODY="$5"; RPATH="$6"; RBODY="$7"; READY="$8"
[ "$STAGE" -ge 1 ] && printf '%s\n' "$MBODY" > "$MPATH"
[ "$STAGE" -ge 2 ] && printf '%s\n' "$OBODY" > "$OPATH"
[ "$STAGE" -ge 3 ] && printf '%s\n' "$RBODY" > "$RPATH"
printf 'ready' > "$READY"
sleep 20
printf 'SURVIVED-SIGKILL' > "${READY}.after"
SIMEOF

sim_kill() {   # <stage> <lane> <ts> <ds> <round_id>  → SIGKILL 시점 FS 상태 구성
  local stage="$1" lane="$2" ts="$3" ds="$4" rid="$5"
  local oj ready pid i=0
  oj="$(out_path "$lane" "$ts")"
  ready="$WORK/sim.ready.$stage"
  rm -f "$ready" "${ready}.after"
  bash "$WORK/dispatch_sim.sh" "$stage" \
    "$CR_DIR/dispatch-${lane}.json" "$(manifest_body "$lane" "$ts" "$rid" "$oj" "$ds")" \
    "$oj" "$(out_json_body PASS)" \
    "$(rc_stamp_path "$lane")" "$ts 0" \
    "$ready" >"$WORK/sim.log" 2>&1 &
  pid=$!
  # ★ sim 의 stdout 을 파일로 격리하는 것이 필수다 — SIGKILL 은 sim 의 `sleep` 자식까지 죽이지 않아
  #   고아 sleep 이 하네스 stdout 파이프의 write end 를 계속 쥔다. 그러면 `test.sh | tail` 류 호출에서
  #   스위트가 끝난 뒤에도 sleep 만료까지 출력이 나오지 않는다(관측 지연 — firsthand 실측).
  while [ ! -f "$ready" ] && [ "$i" -lt 200 ]; do sleep 0.05; i=$((i + 1)); done
  if [ ! -f "$ready" ]; then
    kill -9 "$pid" 2>/dev/null
    wait "$pid" 2>/dev/null
    return 1
  fi
  kill -9 "$pid" 2>/dev/null
  wait "$pid" 2>/dev/null
  [ ! -f "${ready}.after" ]
}

t_sigkill_reachability() {
  local ds ts
  ds=$(( $(date +%s) - 400 )); ts="${ds}-77777"

  fx_reset
  if sim_kill 2 design "$ts" "$ds" "$RID0"; then
    pass "SIGKILL stage2 (out.json 후·stamp 전) 상태 도달"
    run_collect design "$RID0"
    assert_result "S-1 실 SIGKILL" 1 '[codex-collect-rejected: reason=rc-unknown]'
    assert_pass0 "S-1 실 SIGKILL" "$(out_path design "$ts")"
  else
    fail "SIGKILL stage2 — 모사 프로세스 사망 미확인 (fork-and-kill 인프라 실패)"
  fi

  fx_reset
  if sim_kill 3 design "$ts" "$ds" "$RID0"; then
    pass "SIGKILL stage3 (stamp 후) 상태 도달"
    run_collect design "$RID0"
    assert_result "S-2 실 SIGKILL" 0 '[codex-late-collect: outcome=consumed]'
    assert_consumed "S-2 실 SIGKILL" "$(out_path design "$ts")" PASS
  else
    fail "SIGKILL stage3 — 모사 프로세스 사망 미확인"
  fi

  fx_reset
  if sim_kill 0 design "$ts" "$ds" "$RID0"; then
    pass "SIGKILL stage0 (manifest 전) 상태 도달"
    run_collect design "$RID0"
    assert_result "S-3 실 SIGKILL" 1 '[codex-late-collect: outcome=no-dispatch]'
  else
    fail "SIGKILL stage0 — 모사 프로세스 사망 미확인"
  fi
}
t_sigkill_reachability

# ════════════════════════════════════════════════════════════════════════════
#  §8.5.2 residue 초기조건 — 잔재 삼중조 선재 (S-1b / S-3b / S-3b' / S-3b'' / S-3c)
#  ★ 원안 clean-start 단일은 구조적 미검출이었다. 잔재 3파일이 **서로 내부정합**인 것이 요점.
# ════════════════════════════════════════════════════════════════════════════
section "§8.5.2 residue — t_s1b / t_s3b / t_s3b_prime / t_s3b_dprime / t_s3c"

t_s1b_residue_path_a() {
  # residue ⊕ #2 가 out.json write 후 · rc stamp write 전 사망 (경로 A).
  # L1(preflight 비움)이 고정경로 3종(manifest/rc/OUT_JSON#2)을 지웠고 #2 가 manifest·out#2 를 썼다.
  # 잔재 out#1(${TS1} 좌표)은 고정경로가 아니라 L1 대상이 아니며 orphan 으로 남는다.
  fx_reset; mk_residue design
  rm -f "$CR_DIR/dispatch-design.json" "$(rc_stamp_path design)"   # L1 비움
  local ds2 ts2 oj2
  ds2=$(( $(date +%s) - 400 )); ts2="${ds2}-20002"; oj2="$(out_path design "$ts2")"
  write_out_json "$oj2" PASS
  write_manifest design "$ts2" "$RID2" "$oj2" "$ds2"
  run_collect design "$RID2"
  assert_result "S-1b residue·경로A" 1 '[codex-collect-rejected: reason=rc-unknown]'
  assert_pass0 "S-1b (out#2)" "$oj2"
  assert_pass0 "S-1b (잔재 out#1)" "$R1_OUT"
}
t_s1b_residue_path_a

t_s3b_residue_pre_preflight() {
  # residue ⊕ #2 가 preflight 이전 사망 (셀 C1) — 삼중조 온전, argv = 이번 회차 rid2.
  fx_reset; mk_residue design
  run_collect design "$RID2"
  assert_result "S-3b residue·preflight 이전 사망 (C1)" 1 '[codex-collect-rejected: reason=stale-manifest]'
  assert_pass0 "S-3b" "$R1_OUT"
}
t_s3b_residue_pre_preflight

t_s3b_prime_residue_roundid_violation() {
  # ★ 규약 위반 모사 (정상 caller 행태 아님) — LEAD 가 직전 회차 토큰 rid1 을 **byte 동일 재사용**했다.
  #   §3.5 normative 금지 3종 ①(회차 간 재사용) 을 fixture 로 의도적으로 어긴 형상이며,
  #   이 위반 전제가 있어야만 셀 C4 가 성립하고 M4(L1 제거)의 kill 이 성립한다.
  #   "정상 caller 행태" 로 읽으면 M4 의 ★필수 근거가 허위 등재가 된다.
  fx_reset; mk_residue design
  rm -f "$CR_DIR/dispatch-design.json" "$(rc_stamp_path design)"   # L1 비움 (preflight 실행)
  run_collect design "$RID0"                                        # argv = rid1 재사용 = 규약 위반
  assert_result "S-3b' residue·규약위반(rid1 재사용)·manifest write 전 사망 (C4)" 1 '[codex-late-collect: outcome=no-dispatch]'
  assert_pass0 "S-3b'" "$R1_OUT"
}
t_s3b_prime_residue_roundid_violation

t_s3b_dprime_residue_roundid_compliant() {
  # 대조 (unique 층 아님) — S-3b' 와 동일하되 round_id 규약 **준수**(argv=rid2) = 셀 C3.
  # M4 의 **생존 조건**을 기록하는 행. 이 행이 없으면 "L1 무조건 load-bearing" 과장이 미검출된다.
  fx_reset; mk_residue design
  rm -f "$CR_DIR/dispatch-design.json" "$(rc_stamp_path design)"
  run_collect design "$RID2"
  assert_result "S-3b'' residue·규약준수(rid2) (C3)" 1 '[codex-late-collect: outcome=no-dispatch]'
  assert_pass0 "S-3b''" "$R1_OUT"
}
t_s3b_dprime_residue_roundid_compliant

t_s3c_residue_c2_closure_proof() {
  # C2 축 폐쇄 증명 — 상위 `elif` 조기 종료로 dispatch Bash 미도달(L1 미실행) ⊕ 잔재 out#1 **미봉인**
  # (`consume-seal-failed` 모사 = C2 전건 ①) ⊕ argv = rid2(규약 준수).
  # ★ round_id **이전** 형상(시각 하한 L3)에서의 기대 = **PASS 승격 관측** 이었다. 아래 m_M4c_l3_removed
  #   변이 arm 이 그 형상을 실제로 재현해(step 2b 삭제) `consumed` 를 관측하며, 그것이 본 fixture 가
  #   닫은 것이 무엇인지의 대조 증거다. 종전에는 이 셀이 서사에만 있고 관측 채널이 없었다.
  # ★ 정직: 본 fixture 는 C2 **자체**(rid1 재사용)를 닫지 못한다 — 닫히는 것은 이웃 셀 C1 이다.
  fx_reset; mk_residue design
  if [ -e "${R1_OUT}.consumed" ]; then fail "S-3c fixture — 잔재 out#1 이 이미 봉인됨 (C2 전건 ① 미모사)"; else pass "S-3c fixture — 잔재 out#1 미봉인 (C2 전건 ① 모사)"; fi
  run_collect design "$RID2"
  assert_result "S-3c residue·L1 미실행·미봉인 잔재 (C2 전건①)" 1 '[codex-collect-rejected: reason=stale-manifest]'
  assert_pass0 "S-3c" "$R1_OUT"
}
t_s3c_residue_c2_closure_proof

# ════════════════════════════════════════════════════════════════════════════
#  §8.5.3 idempotency replay — round_id 정합 (전 시나리오 argv = manifest 동일, rid0 유지)
#  ★ (i)(ii)(iii) 에도 step 4 선행 규칙 적용 → dispatch_start 를 하한 밖으로 노후화한 fixture 필수.
# ════════════════════════════════════════════════════════════════════════════
section "§8.5.3 replay — t_replay_i ~ t_replay_vi"

t_replay_i_three_consecutive() {
  fx_reset; mk_consumable design "$RID0"
  # 하한 밖 노후화 전제 확인 (없으면 2·3회차 기대가 born-red — in-flight 가 선행한다)
  if [ $(( $(date +%s) - FX_DS )) -ge "$BOUND" ]; then
    pass "replay(i) 전제 — elapsed ≥ BOUND($BOUND) 노후화 확인"
  else
    fail "replay(i) 전제 실패 — elapsed < BOUND, (i)(ii)(iii) born-red"
  fi
  local n consumed_hits=0
  for n in 1 2 3; do
    run_collect design "$RID0"
    if has_out '[codex-late-collect: outcome=consumed]'; then consumed_hits=$((consumed_hits + 1)); fi
    if [ "$n" = 1 ]; then
      assert_result "replay(i) 1회차" 0 '[codex-late-collect: outcome=consumed]'
    else
      assert_result "replay(i) ${n}회차" 1 '[codex-output-absent-unclassified: stdout_bytes=-1]'
    fi
  done
  if [ "$consumed_hits" = 1 ]; then
    pass "replay(i) — consumed 정확히 1회 (T-F3 / §11.6 at-most-once, 재발화 0)"
  else
    fail "replay(i) — consumed ${consumed_hits}회 (1 기대) = 2회 소비 성립"
  fi
}
t_replay_i_three_consecutive

t_replay_ii_after_consume() {
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID0"
  assert_result "replay(ii) 선행 소비" 0 '[codex-late-collect: outcome=consumed]'
  run_collect design "$RID0"
  assert_result "replay(ii) 소비 후 재호출" 1 '[codex-output-absent-unclassified: stdout_bytes=-1]'
  if has_out 'verdict='; then fail "replay(ii) — verdict 재발화 (§11.6 위반)"; else pass "replay(ii) — verdict 재발화 0"; fi
}
t_replay_ii_after_consume

t_replay_iii_consumed_only() {
  fx_reset; mk_consumable design "$RID0"
  mv -f "$FX_OUT" "${FX_OUT}.consumed"     # `.consumed` 만 남은 상태
  run_collect design "$RID0"
  assert_result "replay(iii) .consumed 만 잔존" 1 '[codex-output-absent-unclassified: stdout_bytes=-1]'
  if has_out 'verdict='; then fail "replay(iii) — verdict 발화"; else pass "replay(iii) — verdict 발화 0"; fi
}
t_replay_iii_consumed_only

t_replay_iv_manifest_without_out() {
  # 하한 충족 arm
  fx_reset; mk_consumable design "$RID0"
  rm -f "$FX_OUT"
  run_collect design "$RID0"
  assert_result "replay(iv) manifest 有·out.json 소실 (하한 충족)" 1 '[codex-output-absent-unclassified: stdout_bytes=-1]'
  # 하한 미충족 arm — step 4 in-flight 가 step 5 보다 선행 (결정론 클럭 스텁)
  local ds=1786000000
  fx_reset
  mk_date_stub $((ds + BOUND - 1))
  SUT_ENV=(PATH="$WORK/bin:$PATH")
  write_manifest design "${ds}-66666" "$RID0" "$(out_path design "${ds}-66666")" "$ds"
  write_rc_fmt design '%s 0\n' "${ds}-66666"
  run_collect design "$RID0"
  SUT_ENV=()
  assert_result "replay(iv) 하한 미충족 → step 4 in-flight 선행" 1 '[codex-late-collect: outcome=in-flight]'
}
t_replay_iv_manifest_without_out

t_replay_v_usage_missing_round_id() {
  fx_reset; mk_consumable design "$RID0"
  run_collect design
  assert_result "replay(v) round_id 미전달" 2 NONE
  assert_pass0 "replay(v)" "$FX_OUT"
}
t_replay_v_usage_missing_round_id

t_replay_vi_reissued_round_id() {
  # 소비돼야 하는 상태에서 collect 시점 재발급 → stale-manifest, 소비 0 (M-RID 의 kill 행)
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RIDNEW"
  assert_result "replay(vi) 회차 토큰 재발급 (rid_new ≠ rid0)" 1 '[codex-collect-rejected: reason=stale-manifest]'
  assert_pass0 "replay(vi)" "$FX_OUT"
}
t_replay_vi_reissued_round_id

# ════════════════════════════════════════════════════════════════════════════
#  §8.5.1 대체 검증 — `.consumed` retention sweep age 경계 (삭제 축 ↔ 선택 축 분리)
# ════════════════════════════════════════════════════════════════════════════
section "§8.5.1 t_ttl_sweep_age_boundary (age = TTL−1 / TTL / TTL+1 ⊕ 비-.consumed 보호)"

t_ttl_sweep_age_boundary() {
  # ★ 결정론 클럭 필수 — sweep 의 age 는 **스크립트가 읽는 now** 기준이라 벽시계로 fixture 를 놓으면
  #   SUT 호출 소요(초 단위)만큼 age 가 밀려 `age=TTL` arm 이 `TTL+δ` 로 관측된다(2회차 실행 firsthand).
  #   그 상태의 실패는 SUT 경계 결함이 아니라 fixture 결함이므로, 클럭을 고정해 축을 결정론화한다.
  local ttl=100 now=1786000000 probe
  fx_reset
  mk_date_stub "$now"
  probe="$(env PATH="$WORK/bin:$PATH" date +%s)"
  if [ "$probe" = "$now" ]; then
    pass "TTL sweep — 클럭 스텁 실효 확인 (now=$probe)"
  else
    fail "TTL sweep — 클럭 스텁 미실효 (date +%s → $probe) : age 경계 관측 무효"
  fi
  : > "$CR_DIR/a-1.json.consumed"; set_mtime "$CR_DIR/a-1.json.consumed" $((now - (ttl - 1)))
  : > "$CR_DIR/a-2.json.consumed"; set_mtime "$CR_DIR/a-2.json.consumed" $((now - ttl))
  : > "$CR_DIR/a-3.json.consumed"; set_mtime "$CR_DIR/a-3.json.consumed" $((now - ttl - 1))
  : > "$CR_DIR/keepme-out.json";   set_mtime "$CR_DIR/keepme-out.json"   $((now - ttl - 5000))
  SUT_ENV=(PATH="$WORK/bin:$PATH" CODEX_REVIEW_ARTIFACT_TTL_SEC="$ttl")
  run_collect design "$RID0"
  SUT_ENV=()
  assert_result "TTL sweep 구동 (manifest 부재 경로)" 1 '[codex-late-collect: outcome=no-dispatch]'
  if [ -e "$CR_DIR/a-1.json.consumed" ]; then pass "TTL age=TTL−1 보존"; else fail "TTL age=TTL−1 이 삭제됨 (경계 오프바이원)"; fi
  if [ -e "$CR_DIR/a-2.json.consumed" ]; then pass "TTL age=TTL 보존 (술어 = ttl < age)"; else fail "TTL age=TTL 이 삭제됨 (경계 오프바이원)"; fi
  if [ -e "$CR_DIR/a-3.json.consumed" ]; then fail "TTL age=TTL+1 미삭제 (sweep 무동작)"; else pass "TTL age=TTL+1 삭제"; fi
  if [ -e "$CR_DIR/keepme-out.json" ]; then pass "비-.consumed 파일 보존 (삭제 축이 verdict 후보에 미접촉)"; else fail "비-.consumed 파일 삭제됨 — 선택 축 오염"; fi
}
t_ttl_sweep_age_boundary

# ════════════════════════════════════════════════════════════════════════════
#  mutation — 3층(M4/M4b/M4c) + M6 / M9 / M-M / M-RID / M-RCG(a)(b) + 생존 기록
#  ★ 각 arm 은 **미변이 관측 → 변이 관측** 을 같은 fixture 에서 연속 실행해 RED 를 실증한다.
#  ★ L1(preflight P-2 비움) · rc stamp write · manifest write · round_id 발급은 **dispatch/caller 측**
#    코드다. collector 는 그 산출 FS 상태 ⊕ argv 의 순수 함수이므로, 해당 변이는 **fixture/argv 수준**
#    으로 충실히 모사한다(스크립트 텍스트 변이가 불가능한 것이지 모사가 부정확한 것이 아니다).
#    L2·L3 · rc stamp 파서는 collector 내부이므로 **스크립트 텍스트 변이**로 적용한다.
# ════════════════════════════════════════════════════════════════════════════
section "mutation M4 (L1 제거 = P-2 고정경로 비움 삭제) — kill 셀 C4 / fixture 수준"

m_M4_l1_removed() {
  # 미변이 = S-3b'(L1 실행 → 슬롯 비움) → no-dispatch
  fx_reset; mk_residue design
  rm -f "$CR_DIR/dispatch-design.json" "$(rc_stamp_path design)"
  run_collect design "$RID0"
  assert_result "M4 미변이 (L1 실행, C4)" 1 '[codex-late-collect: outcome=no-dispatch]'
  local base_out="$OUT"
  # 변이 = L1 제거 → 잔재 삼중조 온전 ∧ argv=rid1 이 manifest#1 과 동등 → 전 층 통과 → 잔재 verdict 소비
  fx_reset; mk_residue design
  run_collect design "$RID0"
  if has_out '[codex-late-collect: outcome=consumed]' && has_out 'verdict=PASS'; then
    pass "M4 변이 (L1 제거, C4) → 잔재 verdict PASS 승격 관측 = RED (미변이 no-dispatch ↔ 변이 consumed)"
  else
    fail "M4 변이가 관측을 바꾸지 못함 (생존) — 미변이=[${base_out//$'\n'/ }] 변이=[${OUT//$'\n'/ }]"
  fi
}
m_M4_l1_removed

m_M4_under_s3b_dprime_survival() {
  # ★ 생존 기대(조건부성 기록) — 규약 준수(C3)에서는 L3 가 같은 셀을 덮어 M4 가 PASS 를 만들지 못한다.
  fx_reset; mk_residue design
  rm -f "$CR_DIR/dispatch-design.json" "$(rc_stamp_path design)"
  run_collect design "$RID2"
  assert_result "M4 미변이 (C3, 규약 준수)" 1 '[codex-late-collect: outcome=no-dispatch]'
  fx_reset; mk_residue design
  run_collect design "$RID2"
  if has_out '[codex-late-collect: outcome=consumed]'; then
    fail "M4 under C3 — PASS 승격 발생 (L3 가 C3 를 덮지 못함 = 설계 문면 반증)"
  else
    pass "M4 under C3 → PASS 0 유지 (생존 기대: L1 제거해도 처분 불변 — L3 가 덮음). 관측 marker=[${OUT//$'\n'/ }]"
  fi
  assert_pass0 "M4 under C3 (생존 arm)" "$R1_OUT"
}
m_M4_under_s3b_dprime_survival

section "mutation M4b (L2 제거 = rc stamp 귀속 검사 삭제) — kill 셀 C8 / 스크립트 변이"

m_M4b_l2_removed() {
  local mut; mk_mutant M4b || return 0; mut="$MUT_PATH"
  # C8 fixture — #2 preflight 후 #1 이 뒤늦게 자기 stamp 를 write (동일 lane 중첩 dispatch).
  #   manifest#2(dispatch_id=TS2) + out#2 신선/유효 + rc stamp 귀속 = TS1.
  local ds2 ts2 oj2 ts1
  fx_reset
  ds2=$(( $(date +%s) - 400 )); ts2="${ds2}-20002"; ts1="$(( ds2 - 500 ))-10001"
  oj2="$(out_path design "$ts2")"
  write_out_json "$oj2" PASS
  write_manifest design "$ts2" "$RID2" "$oj2" "$ds2"
  write_rc_fmt design '%s 0\n' "$ts1"           # #1 이 쓴 stamp — 형식은 완전 정상, 귀속만 다르다
  run_collect design "$RID2"
  assert_result "M4b 미변이 (C8 중첩 dispatch)" 1 '[codex-collect-rejected: reason=rc-unknown]'
  assert_pass0 "M4b 미변이 (C8)" "$oj2"
  run_sut "$mut" design "$RID2"
  if has_out '[codex-late-collect: outcome=consumed]' && has_out 'verdict=PASS'; then
    pass "M4b 변이 (L2 제거) → 타 프로세스 rc=0 채택·소비 = RED (rc-unknown ↔ consumed)"
  else
    fail "M4b 변이가 관측을 바꾸지 못함 (생존) — [${OUT//$'\n'/ }]"
  fi
}
m_M4b_l2_removed

section "mutation M4c (L3 제거 = step 2b 삭제) — kill 셀 C1 / 스크립트 변이"

m_M4c_l3_removed() {
  local mut; mk_mutant M4c || return 0; mut="$MUT_PATH"
  fx_reset; mk_residue design
  run_collect design "$RID2"
  assert_result "M4c 미변이 (S-3b / C1)" 1 '[codex-collect-rejected: reason=stale-manifest]'
  assert_pass0 "M4c 미변이 (C1)" "$R1_OUT"
  run_sut "$mut" design "$RID2"
  if has_out '[codex-late-collect: outcome=consumed]' && has_out 'verdict=PASS'; then
    pass "M4c 변이 (L3 제거) → 내부정합 잔재 삼중조 통과·소비 = RED (stale-manifest ↔ consumed)"
  else
    fail "M4c 변이가 관측을 바꾸지 못함 (생존) — [${OUT//$'\n'/ }]"
  fi
  # ★ S-3c 폐쇄 증명의 대조: 동일 변이(= round_id 이전 형상 등가)를 S-3c fixture 에 주입하면 PASS 승격.
  fx_reset; mk_residue design
  run_sut "$mut" design "$RID2"
  if has_out 'verdict=PASS'; then
    pass "S-3c 폐쇄 증명 대조 — round_id 층 부재 형상에서 잔재 PASS 승격 관측 (현 설계가 닫은 것)"
  else
    fail "S-3c 폐쇄 증명 대조 실패 — 층 부재 형상에서도 PASS 미승격 (fixture 가 C2 전건①을 모사 못함)"
  fi
}
m_M4c_l3_removed

section "mutation M4/M4b 상호 (경로 A) — ★ 생존 기대 (이중화 확인)"

m_M4_M4b_mutual_survival() {
  # L1 만 제거한 경로 A fixture: 잔재 rc#1("<TS1> 0")이 남지만 manifest#2 귀속(TS2)과 불일치 → L2 가 잡는다.
  local ds2 ts2 oj2
  fx_reset; mk_residue design
  ds2=$(( $(date +%s) - 400 )); ts2="${ds2}-20002"; oj2="$(out_path design "$ts2")"
  write_out_json "$oj2" PASS
  write_manifest design "$ts2" "$RID2" "$oj2" "$ds2"      # #2 manifest 는 덮어쓰기됨 (고정 슬롯)
  # rc stamp 는 잔재 #1 것을 그대로 둔다 (= L1 비움 미실행)
  run_collect design "$RID2"
  assert_result "M4(L1만 제거)·경로A" 1 '[codex-collect-rejected: reason=rc-unknown]'
  assert_pass0 "M4(L1만 제거)·경로A" "$oj2"
  pass "M4/M4b 상호 — 경로 A 에서 L1 제거는 rc-unknown → rc-unknown 무차이 = **생존 기대(이중화 확인)**. L1↔L2 는 이 셀에서 redundant 이며 각자의 독립 증명은 C4(M4)·C8(M4b) 에서만 나온다"
  # 이중화가 실제로 이중인지 확인: L1(fixture) ⊕ L2(스크립트) 를 동시에 제거하면 소비로 뚫린다.
  local mut; mk_mutant M4b || return 0; mut="$MUT_PATH"
  run_sut "$mut" design "$RID2"
  if has_out '[codex-late-collect: outcome=consumed]'; then
    pass "M4+M4b 동시 제거 → 경로 A 소비 관측 = 두 층의 **합**이 load-bearing 임을 실증 (집합적 증명)"
  else
    fail "M4+M4b 동시 제거인데도 소비 0 — 경로 A 방어 귀속이 설계 문면과 불일치"
  fi
}
m_M4_M4b_mutual_survival

section "mutation M6 (late-collect 루틴 자체 제거) — AC-10"

m_M6_routine_removed() {
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID0"
  assert_result "M6 미변이" 0 '[codex-late-collect: outcome=consumed]'
  # 변이 = 루틴 부재 (배포 표면에서 스크립트가 사라진 형상)
  fx_reset; mk_consumable design "$RID0"
  run_sut "$MUT_DIR/DELETED-codex-late-collect.sh" design "$RID0"
  if [ "$RC" != 0 ] && ! has_out 'verdict=' && [ ! -e "${FX_OUT}.consumed" ]; then
    pass "M6 변이 (루틴 제거) → rc=$RC · verdict 미발화 · 소비 0 = RED (consumed ↔ 회수 0, AC-10 유실)"
  else
    fail "M6 변이 — 루틴 부재인데 소비/verdict 관측 (rc=$RC, out=[${OUT//$'\n'/ }])"
  fi
}
m_M6_routine_removed

section "mutation M9 (rc stamp write 제거) — S-2 정상 arm / INV-F"

m_M9_rcstamp_write_removed() {
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID0"
  assert_result "M9 미변이 (S-2 정상 arm)" 0 '[codex-late-collect: outcome=consumed]'
  fx_reset; mk_consumable design "$RID0"
  rm -f "$(rc_stamp_path design)"          # dispatch 측 stamp write 제거 모사
  run_collect design "$RID0"
  if has_out '[codex-collect-rejected: reason=rc-unknown]' && ! has_out 'verdict='; then
    pass "M9 변이 (stamp write 제거) → rc-unknown fail-closed = RED (consumed ↔ rc-unknown)"
  else
    fail "M9 변이가 관측을 바꾸지 못함 — [${OUT//$'\n'/ }]"
  fi
}
m_M9_rcstamp_write_removed

section "mutation M-M (manifest write 제거) — AC-11"

m_MM_manifest_write_removed() {
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID0"
  assert_result "M-M 미변이 (경로 도출 성공)" 0 '[codex-late-collect: outcome=consumed]'
  fx_reset; mk_consumable design "$RID0"
  rm -f "$CR_DIR/dispatch-design.json"     # manifest write 제거 모사 (out.json·rc stamp 는 실재)
  run_collect design "$RID0"
  if has_out '[codex-late-collect: outcome=no-dispatch]' && ! has_out 'verdict='; then
    pass "M-M 변이 (manifest 제거) → no-dispatch = RED (2-hop 좌표 도출 불가, AC-11)"
  else
    fail "M-M 변이가 관측을 바꾸지 못함 — [${OUT//$'\n'/ }]"
  fi
  if [ -e "$FX_OUT" ]; then pass "M-M 변이 — out.json 실재하나 도달 불가 (glob·newest 선택 부재 확인)"; else fail "M-M 변이 — out.json 이 소비/삭제됨"; fi
}
m_MM_manifest_write_removed

section "mutation M-RID (round_id collect 시점 재발급) — §8.5.3 (vi)"

m_MRID_roundid_reissued() {
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RID0"
  assert_result "M-RID 미변이 (verbatim 전송)" 0 '[codex-late-collect: outcome=consumed]'
  fx_reset; mk_consumable design "$RID0"
  run_collect design "$RIDNEW"             # collect 시점 재발급 = 두 소비처 값 불일치
  if has_out '[codex-collect-rejected: reason=stale-manifest]' && ! has_out 'verdict=' && [ ! -e "${FX_OUT}.consumed" ]; then
    pass "M-RID 변이 (재발급) → stale-manifest · 소비 0 = RED (consumed ↔ 전건 거부, AC-10 100% 무효 경로 포착)"
  else
    fail "M-RID 변이가 관측을 바꾸지 못함 — [${OUT//$'\n'/ }]"
  fi
}
m_MRID_roundid_reissued

section "mutation M-RCG(a) — rc stamp 파서를 2-토큰 read 형으로 교체"

m_MRCGa_two_token_parser() {
  local mut; mk_mutant RCGa || return 0; mut="$MUT_PATH"
  local case_fmt label
  # (a) 의 kill 케이스 = 3-토큰 ∧ 2행
  for label in '3-토큰' '2행'; do
    fx_reset; mk_consumable design "$RID0"
    if [ "$label" = '3-토큰' ]; then
      write_rc_fmt design '%s 0 extra\n' "$FX_TS"
    else
      write_rc_fmt design '%s 0\n%s 0\n' "$FX_TS" "$FX_TS"
    fi
    run_collect design "$RID0"
    assert_result "M-RCG(a) 미변이 [$label]" 1 '[codex-collect-rejected: reason=rc-unknown]'
    run_sut "$mut" design "$RID0"
    if has_out '[codex-late-collect: outcome=consumed]'; then
      pass "M-RCG(a) 변이 [$label] → ACCEPT·소비 = RED (rc-unknown ↔ consumed)"
    else
      fail "M-RCG(a) 변이 [$label] 가 관측을 바꾸지 못함 (생존) — [${OUT//$'\n'/ }]"
    fi
  done
}
m_MRCGa_two_token_parser

section "mutation M-RCG(b) — rc stamp 파서를 \$(cat) 변형-산출 비교형으로 교체"

m_MRCGb_cat_variant_parser() {
  local mut; mk_mutant RCGb || return 0; mut="$MUT_PATH"
  local is_msys=0
  case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) is_msys=1 ;; esac

  local label
  for label in 'NUL 후행' 'NUL 선행' 'CRLF'; do
    fx_reset; mk_consumable design "$RID0"
    case "$label" in
      'NUL 후행') write_rc_fmt design '%s 0\n\0' "$FX_TS" ;;
      'NUL 선행') write_rc_fmt design '%s 0\0\n' "$FX_TS" ;;
      'CRLF')     write_rc_fmt design '%s 0\r\n' "$FX_TS" ;;
    esac
    run_collect design "$RID0"
    assert_result "M-RCG(b) 미변이 [$label]" 1 '[codex-collect-rejected: reason=rc-unknown]'
    run_sut "$mut" design "$RID0"
    if [ "$label" = CRLF ] && [ "$is_msys" = 0 ]; then
      # 비-MSYS: 명령치환이 CR 을 흡수하지 않으므로 구 파서도 CRLF 를 거부한다 = 이 셀에서 생존.
      # (설계 firsthand: (b) 의 CRLF ACCEPT 는 MSYS CR 흡수 기인 = 플랫폼 의존 판정)
      if has_out '[codex-collect-rejected: reason=rc-unknown]'; then
        pass "M-RCG(b) 변이 [CRLF · 비-MSYS] → 거부 유지 = **생존 기대(플랫폼 의존)**. (b) 의 kill 은 NUL 2형이 담당"
      else
        fail "M-RCG(b) 변이 [CRLF · 비-MSYS] → 예상 밖 관측 [${OUT//$'\n'/ }]"
      fi
    else
      if has_out '[codex-late-collect: outcome=consumed]'; then
        pass "M-RCG(b) 변이 [$label] → ACCEPT·소비 = RED (rc-unknown ↔ consumed)"
      else
        fail "M-RCG(b) 변이 [$label] 가 관측을 바꾸지 못함 (생존) — [${OUT//$'\n'/ }]"
      fi
    fi
  done
}
m_MRCGb_cat_variant_parser

# ════════════════════════════════════════════════════════════════════════════
#  §H category_enum 필수 승격 (schema 축)
#
#  계약: `category_enum` 은 **manifest 필수 필드**이며 그 부재·빈값은 **step 2 schema 불일치 축**에서
#        거부된다 (DeveloperPL 판정 — §4.2 표 반영은 ArchitectPL 비준 대기).
#
#  ★ 왜 신설하는가 (커버리지 공백 firsthand): 기존 `manifest_body()` 는 이 키를 **항상** emit 하고
#    `ce="${8:-runtime-bug}"` 라 **빈 문자열조차 default 로 접힌다** → 부재/빈값 arm 이 스위트에 0 건이었다.
#    즉 규약이 문면·코드에만 있고 fixture 가 늘 올바른 값을 쓰면 GREEN 인 채 배포되는 형상(M-RID 와 동형).
#
#  ★ 은폐 실증 (막아야 할 회귀): 승격 전에는 `category_enum` 부재 ∧ out.json 부재 ∧ elapsed 하한 미충족이면
#    step 4 에서 `[codex-late-collect: outcome=in-flight]` 로 빠져나가 producer 계약 결함이 **전혀 발화하지
#    않았다**. H1 이 그 가드이고, M-CE 변이 arm 이 그 은폐를 **매 실행 재현**한다.
#
#  관측 서명 계약 (step 2 거부): stdout marker **0** (`_schema_reject` 는 stdout 을 내지 않는다)
#    ⊕ stderr `schema 불일치 축 fail-closed` ⊕ 소비 0.
#
#  ★ fork 진정성 (exit code·마커 부재 단독 판정 금지): 본 arm 들의 1차 기대는 "마커 **미**발화" 라
#    SUT 를 fork 하지 못해도 공허 통과할 수 있다. 그 공백은 (a) rc 단일 기대(미 fork = 127 ≠ 1)와
#    (b) **도메인 고유 stderr sentinel** `schema 불일치 축 fail-closed`(도메인 코드 경로에서만 방출)의
#    **병행 assert** 가 막는다. firsthand 실증: 미 fork 조건(드라이버 REPO_ROOT 오유도 → SUT 경로 부재)을
#    강제했더니 마커-부재 assert 4건은 전부 통과한 반면 rc assert 와 sentinel assert 는 genuine 실패했다
#    (`rc=127` · `stderr=[bash: …: No such file or directory]`). = sentinel 이 vacuous 아님을 입증.
# ════════════════════════════════════════════════════════════════════════════

# stderr 관측 (stdout 전용 `has_out` 의 짝 — step 2 거부는 stdout 이 비어 stdout 만으로는 분별 불가).
has_err() { printf '%s' "$ERR" | grep -qF -- "$1"; }

H_SCHEMA_SIG='schema 불일치 축 fail-closed'   # `_schema_reject` 진단 서명 (step 2 축)
H_STEP7_SIG='소비 조건 미충족'                 # step 7 말미 처분 서명 (도달 여부 관측용)

assert_schema_axis() {   # <label> — step 2 schema 축 거부의 stderr 서명
  if has_err "$H_SCHEMA_SIG"; then
    pass "$1 — step 2 schema 축 거부 서명 (stderr '$H_SCHEMA_SIG')"
  else
    fail "$1 — step 2 schema 축 서명 미검출 | stderr=[${ERR//$'\n'/ }]"
  fi
}

# ── §H 전용 fixture 경로: `category_enum` 축 **하나만** 변주한다 ──────────────────────
# ★ 기존 `manifest_body`/`write_manifest` 의 시그니처·호출부 **무접촉** (286 PASS 무회귀).
#   부재/빈값은 `manifest_body` 로 만들 수 없으므로(위 사유) 그 **산출물 후처리**로만 만들고,
#   후처리가 no-op 이면 arm 이 성립하지 않은 것이므로 **그 자체를 FAIL** 로 낸다 (검사연극 금지).
h_write_manifest_catenum() {   # <keep|nokey|empty> <lane> <dispatch_id> <round_id> <out_json> <dispatch_start>
  local mode="$1"; shift
  local lane="$1" body out
  body="$(manifest_body "$@")"
  case "$mode" in
    keep)
      out="$body"
      ;;
    nokey)
      out="$(printf '%s' "$body" | sed -E 's/"category_enum":"[^"]*",//')"
      if printf '%s' "$out" | grep -qF 'category_enum'; then
        fail "§H fixture 결함 — category_enum 키 제거가 no-op (manifest 형상 변경 의심). arm 무효"
        return 1
      fi
      ;;
    empty)
      out="$(printf '%s' "$body" | sed -E 's/"category_enum":"[^"]*"/"category_enum":""/')"
      if ! printf '%s' "$out" | grep -qF '"category_enum":""'; then
        fail "§H fixture 결함 — category_enum 빈값 치환이 no-op. arm 무효"
        return 1
      fi
      ;;
    *)
      fail "§H fixture 결함 — 알 수 없는 mode=$mode"
      return 1
      ;;
  esac
  printf '%s\n' "$out" > "$CR_DIR/dispatch-${lane}.json"
  return 0
}

# 산출 전역: H_TS / H_DS / H_OUT.  elapsed=under → OP-1 하한(300) **미만**(은폐 arm 성립 조건).
h_fixture() {   # <keep|nokey|empty> <present|absent> <ok|missing> <under|over>
  local ce="$1" oj_mode="$2" stamp_mode="$3" el="$4" lane=design
  fx_reset
  if [ "$el" = under ]; then H_DS="$(date +%s)"; else H_DS=$(( $(date +%s) - 400 )); fi
  H_TS="${H_DS}-31337"
  H_OUT="$(out_path "$lane" "$H_TS")"
  if [ "$oj_mode" = present ]; then write_out_json "$H_OUT" PASS; fi
  h_write_manifest_catenum "$ce" "$lane" "$H_TS" "$RID2" "$H_OUT" "$H_DS" || return 1
  if [ "$stamp_mode" = ok ]; then write_rc_fmt "$lane" '%s 0\n' "$H_TS"; fi
  return 0
}

section "§H t_h1_catenum_absent_hides_as_inflight (★ 은폐 회귀 가드)"

t_h1_catenum_absent_hides_as_inflight() {
  # 부재 ∧ out.json 부재 ∧ elapsed 하한 미만 = 승격 전 은폐가 정확히 성립하던 좌표.
  h_fixture nokey absent missing under || return 0
  run_collect design "$RID2"
  assert_result "H1 (부재·out 부재·하한 미만)" 1 NONE
  assert_schema_axis "H1"
  if has_out '[codex-late-collect: outcome=in-flight]'; then
    fail "H1 — ★은폐 회귀: producer 필수 필드 누락이 in-flight 로 흡수됨 (승격 전 형상 복귀)"
  else
    pass "H1 — outcome=in-flight 미발화 (은폐 회귀 가드)"
  fi
  if has_out '[codex-late-collect: outcome=consumed]'; then
    fail "H1 — consumed 발화 (소비 0 위반)"
  else
    pass "H1 — outcome=consumed 0"
  fi
}
t_h1_catenum_absent_hides_as_inflight

section "§H t_h2_catenum_absent_rejects_before_helper (step 7 → step 2 이동)"

t_h2_catenum_absent_rejects_before_helper() {
  # out.json 실재 + 정상 rc stamp = 승격 전이라면 step 7 까지 내려가 helper_rc=2 로 처분되던 좌표.
  # ★ 이 arm 이 실제로 사는 값(M-CE firsthand): 승격과 함께 step 7 의 중복 부재검사가 제거돼 **step 2 가
  #   유일 강제점**이 됐다. 그래서 step 2 검증을 중화하면 collector 가 **빈 enum 을 들고 그대로 진행**하고,
  #   `findings: []` 인 PASS out.json 에서는 검사 ⑤ 가 **순회 대상 0 이라 통과**하므로 `verdict=PASS` 로
  #   **거짓 소비가 완주**한다(변이 실측: rc=0 · consumed · .consumed 봉인). 무력화되는 것은 *enum 대조
  #   자체* 가 아니라 ***그 대조가 걸릴 지점의 부재*** 이며, 하필 그것이 PASS verdict 의 통상 형상이다.
  #   ★ 반증된 오귀속 기록: "빈 enum 이 검사 ⑤ 를 공허 참으로 통과시킨다"는 **거짓**이다 — 빈 enum 은
  #     오히려 **더 엄격**하다(빈 집합 ∌ 임의 category). 4-arm 실측 rc: (`findings: []`, 빈)=0 /
  #     (`findings: []`, 정상)=0 / (finding 1개, 빈)=1 / (finding 1개, 정상)=1 → 빈 enum 축은 두 arm 을
  #     가르지 않는다. [verified: DeveloperPL firsthand — helper 4-arm 직접 실행 / QADev 재현 + `_check_category_enum`
  #     본문 판독(`for … in data['findings']` 순회형)]
  #   즉 이 arm 이 막는 것은 사유 오라벨이 아니라 **거짓 PASS 승격(fail-open)** 이다.
  h_fixture nokey present ok over || return 0
  run_collect design "$RID2"
  assert_result "H2 (부재·out 실재·stamp 정상)" 1 NONE
  assert_schema_axis "H2"
  # step 7 미도달 = 검증이 앞당겨졌다는 직접 증거.
  # ★ 정직 상한: 이 부재-assert 는 **어휘 의존**이라 문구가 바뀌면 공허 통과할 수 있다.
  #   어휘 비의존 증거는 H2b(마커 축) 와 M-CE(변이 축) 가 담당한다.
  if has_err "$H_STEP7_SIG"; then
    fail "H2 — step 7 처분 서명 '$H_STEP7_SIG' 관측 = 검증이 여전히 step 7 (앞당겨지지 않음)"
  else
    pass "H2 — step 7 미도달 (step 2 에서 종결)"
  fi
  if [ -e "${H_OUT}.consumed" ]; then
    fail "H2 — .consumed rename 발생 (소비 0 위반)"
  else
    pass "H2 — .consumed rename 미발생"
  fi
  assert_pass0 "H2" "$H_OUT"
  if [ -f "$H_OUT" ]; then pass "H2 — 원 좌표 잔존 (미소비)"; else fail "H2 — 원 좌표 소멸 = 소비됨"; fi
}
t_h2_catenum_absent_rejects_before_helper

section "§H t_h2b_catenum_absent_precedes_rc_axis (★ 어휘 비의존 순서 증거 — 추가 arm)"

t_h2b_catenum_absent_precedes_rc_axis() {
  # ★ 지시 표 밖 **추가** arm. H2 의 '앞당겨짐' 을 stderr 문구가 아니라 **stdout 마커 축**으로 증명한다:
  #   부재 ∧ rc stamp **부재** 좌표는 검증이 step 7 에 있으면 `reason=rc-unknown` 이 발화하고,
  #   step 2 에 있으면 그 전에 종결돼 **마커가 없다**. 문구 변경에 면역인 순서 증거.
  h_fixture nokey present missing over || return 0
  run_collect design "$RID2"
  assert_result "H2b (부재·stamp 부재)" 1 NONE
  assert_schema_axis "H2b"
  if has_out '[codex-collect-rejected: reason=rc-unknown]'; then
    fail "H2b — rc-unknown 발화 = 필수 필드 검증이 rc 축(step 7) 뒤에 있음 (순서 계약 위반)"
  else
    pass "H2b — rc-unknown 미발화 = 필수 필드 검증이 rc 축보다 **앞**에서 종결 (어휘 비의존 증거)"
  fi
}
t_h2b_catenum_absent_precedes_rc_axis

section "§H t_h3_catenum_empty_equals_absent (빈 문자열 = 부재 등가)"

t_h3_catenum_empty_equals_absent() {
  # `_json_str_field` 는 `""` 에 대해 **rc=0 · 빈 값**을 돌려준다 → rc 만 보는 구현은 이 arm 을 통과시킨다.
  # 즉 `-n` 검사가 load-bearing 인지 여기서만 갈린다.
  h_fixture empty present ok over || return 0
  run_collect design "$RID2"
  assert_result "H3 (빈 문자열)" 1 NONE
  assert_schema_axis "H3"
  assert_pass0 "H3" "$H_OUT"
}
t_h3_catenum_empty_equals_absent

section "§H t_h4_catenum_valid_consumes (★ 대조 arm — 거부의 category_enum 축 귀속 확정)"

t_h4_catenum_valid_consumes() {
  # H2 와 **완전히 동일한 fixture 구성 경로**에서 `category_enum` 만 정상값으로 되돌린다.
  # 이 arm 이 없으면 H1~H3 의 거부가 다른 이유(경로·형상·환경) 때문일 가능성을 배제하지 못한다.
  h_fixture keep present ok over || return 0
  run_collect design "$RID2"
  assert_result "H4 대조 (정상 category_enum)" 0 '[codex-late-collect: outcome=consumed]'
  assert_consumed "H4 대조" "$H_OUT" PASS
  if has_err "$H_SCHEMA_SIG"; then
    fail "H4 대조 — 정상값인데 schema 축 거부 서명 관측 = H1~H3 의 거부가 category_enum 축 귀속이 아님"
  else
    pass "H4 대조 — schema 축 거부 미발생 = H1~H3 거부의 **유일 변인이 category_enum** 임을 확정"
  fi
}
t_h4_catenum_valid_consumes

section "§H t_h5_axis_disjoint_no_reason_collapse (§4.3 축 비혼동)"

t_h5_axis_disjoint_no_reason_collapse() {
  # producer 필수 필드 누락이 **잔재 축**(stale-manifest)·**rc 축**(rc-unknown) 카운터로 접히면
  # 사유가 합쳐져 진단이 불가능해진다 — 이 Story 가 관통 진단한 실패 양식.
  h_fixture nokey present ok over || return 0
  run_collect design "$RID2"
  if has_out '[codex-collect-rejected: reason=stale-manifest]'; then
    fail "H5 — 필수 필드 누락이 stale-manifest(잔재·귀속 축)로 접힘 = 축 혼동"
  else
    pass "H5 — reason=stale-manifest 미발화 (귀속 축과 disjoint)"
  fi
  if has_out '[codex-collect-rejected: reason=rc-unknown]'; then
    fail "H5 — 필수 필드 누락이 rc-unknown(rc 판독 축)으로 접힘 = 축 혼동"
  else
    pass "H5 — reason=rc-unknown 미발화 (rc 축과 disjoint)"
  fi
}
t_h5_axis_disjoint_no_reason_collapse

section "§H mutation M-CE (step 2 category_enum 검증 중화) — 은폐 재현 / kill 셀 H1·H2b"

m_MCE_step2_catenum_check_removed() {
  local mut; mk_mutant CE || return 0; mut="$MUT_PATH"
  # (a) H1 좌표 — ★ 은폐 재현. 변이본에서는 producer 계약 결함이 `outcome=in-flight` 로 조용히 빠져나간다.
  h_fixture nokey absent missing under || return 0
  run_sut "$mut" design "$RID2"
  if has_out '[codex-late-collect: outcome=in-flight]'; then
    pass "M-CE 변이 (step 2 검증 중화) → H1 좌표가 outcome=in-flight 로 은폐 = RED 재현 (schema 거부 ↔ in-flight)"
  else
    fail "M-CE 변이 (a) 가 관측을 바꾸지 못함 (생존) — rc=$RC / [${OUT//$'\n'/ }]"
  fi
  # (b) H2b 좌표 — 어휘 비의존 kill. 변이본은 rc 축(step 7)까지 내려가 `rc-unknown` 을 발화한다.
  h_fixture nokey present missing over || return 0
  run_sut "$mut" design "$RID2"
  if has_out '[codex-collect-rejected: reason=rc-unknown]'; then
    pass "M-CE 변이 → H2b 좌표가 rc 축까지 내려가 rc-unknown 발화 = 검증 위치(step 2)가 load-bearing 임의 어휘 비의존 증거"
  else
    fail "M-CE 변이 (b) 가 관측을 바꾸지 못함 (생존) — rc=$RC / [${OUT//$'\n'/ }]"
  fi
  # (c) H4 좌표 — 변이본에서도 정상값은 소비된다 = 변이가 category_enum 축**만** 건드렸음(부작용 0).
  h_fixture keep present ok over || return 0
  run_sut "$mut" design "$RID2"
  if has_out '[codex-late-collect: outcome=consumed]'; then
    pass "M-CE 변이 대조 → 정상값 소비 유지 = 변이 표면이 category_enum 축에 한정 (부작용 0)"
  else
    fail "M-CE 변이 대조 실패 — 정상값도 소비 안 됨: 변이가 다른 축을 깨뜨림 (kill 귀속 무효) — rc=$RC / [${OUT//$'\n'/ }]"
  fi
}
m_MCE_step2_catenum_check_removed

# ════════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " 결과: PASS=$PASS  FAIL=$FAIL"
echo "═══════════════════════════════════════════════════════════════════════════"
if [ "$FAIL" -gt 0 ]; then exit 1; fi
exit 0
