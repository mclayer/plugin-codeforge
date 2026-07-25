#!/usr/bin/env bash
# tests/scripts/test_adr-amendment-parity.sh
# CFP-2812 / ADR-167(adr-amendment-compaction-ratchet) / ADR-060 — heading<->fm parity + 재해석
# marker discriminating self-test. Change Plan §8.1/§8.2 F-1 + AC-4 이행.
#
# 대상 = scripts/lib/check_adr_amendment_threshold.py 의 check_parity / check_marker_presence 순수 함수
#   + parity 게이트 orchestration(fail-closed).
#
# forward-only 정직 천장 (D4): orchestration parity 는 merge-base delta(신규 헤딩/entry) 로만 판정한다.
#   merge-base 부재(로컬/신규) 시 delta=0 -> 소급 판정 skip 이 설계 의도다. 따라서 heading-only 검출력의
#   discriminating 검증은 순수 함수 check_parity 레벨에서 mutation-kill 로 수행하고(F-1), orchestration
#   exit-1 경로는 malformed fail-closed 로 입증한다. git 명령 미사용(제약 준수) — 실 merge-base 재현은
#   CI(merge-base fetch step) 소관. "orchestration heading-only 를 git 없이 재현" 은 주장하지 않는다.
#
# anti-theater / distinct-marker / shell 관례 = threshold self-test 와 동형(§8.11 / ADR-060 Amd22).
#   각 mutant 는 1-line mutation 으로 검출 무력화(변이본 GREEN)되어야 KILLED. 정본은 검출(RED).
#
# set -e 미사용 — 카운터 집계 후 exit code 결정.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$REPO_ROOT/scripts/lib/check_adr_amendment_threshold.py"

PASS=0
FAIL=0

PYBIN="$(command -v python3 || command -v python)"

# ─── unit: 순수 함수 python-level assertion ──────────────────────────────────────
run_py_assert() {
  local name="$1" expr="$2"
  if PYTHONUTF8=1 "$PYBIN" - "$REPO_ROOT" "$expr" <<'PYEOF' >/dev/null 2>&1
import sys
sys.path.insert(0, sys.argv[1] + "/scripts/lib")
import check_adr_amendment_threshold as m
r = eval(sys.argv[2], {"m": m})
sys.exit(0 if r else 1)
PYEOF
  then
    echo "PASS: $name"
    PASS=$((PASS+1))
  else
    echo "FAIL: $name -- expr false or error: $expr"
    FAIL=$((FAIL+1))
  fi
}

# ─── pure-function mutation-kill: 변이본 모듈을 격리 dir 로 copy+sed 후 별도 subprocess import ─
# probe expr 를 정본 dir / 변이본 dir 각각에서 eval -> EMPTY/NONEMPTY 출력.
run_probe() {
  local moddir="$1" expr="$2"
  PYTHONUTF8=1 "$PYBIN" - "$moddir" "$expr" <<'PYEOF'
import sys
sys.path.insert(0, sys.argv[1])
import check_adr_amendment_threshold as m
r = eval(sys.argv[2], {"m": m})
print("EMPTY" if r == [] else "NONEMPTY")
PYEOF
}

# 정본 probe = NONEMPTY(검출/RED), 변이본 probe = EMPTY(미검출/GREEN) 이어야 KILLED.
assert_pure_mutation_killed() {
  local name="$1" expr="$2" sed_expr="$3"
  local mdir base_out mut_out
  mdir="$(mktemp -d)"
  cp "$SRC" "$mdir/check_adr_amendment_threshold.py"
  sed -i "$sed_expr" "$mdir/check_adr_amendment_threshold.py"

  if diff -q "$SRC" "$mdir/check_adr_amendment_threshold.py" >/dev/null 2>&1; then
    echo "FAIL: $name -- sed mutation no-op (소스 무변경 — mutant 정의 오류)"
    FAIL=$((FAIL+1))
    rm -rf "$mdir"
    return
  fi

  base_out="$(run_probe "$REPO_ROOT/scripts/lib" "$expr" 2>/dev/null)"
  mut_out="$(run_probe "$mdir" "$expr" 2>/dev/null)"
  rm -rf "$mdir"

  if [ "$base_out" = "NONEMPTY" ] && [ "$mut_out" = "EMPTY" ]; then
    echo "PASS: $name -- mutant KILLED (정본 RED, 변이본 GREEN)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $name -- SURVIVED/불일치 (base=$base_out mut=$mut_out, 기대 NONEMPTY/EMPTY)"
    FAIL=$((FAIL+1))
  fi
}

# ─── orchestration fail-closed: malformed frontmatter -> parity 게이트 exit 1 (census 병행) ─
make_malformed_adr() {
  local dir="$1" name="$2"
  mkdir -p "$dir/archive/adr"
  {
    printf -- '---\n'
    printf 'title: broken\n'
    printf 'amendments: [ {amendment_id: 1\n'
    printf -- '---\n\n'
    printf 'body\n'
  } > "$dir/archive/adr/$name"
}

# heading 0 + fm 없음 (clean) ADR — parity GREEN baseline(비-vacuous census).
make_clean_adr() {
  local dir="$1" name="$2"
  mkdir -p "$dir/archive/adr"
  {
    printf -- '---\n'
    printf 'title: clean ADR\n'
    printf 'status: proposed\n'
    printf -- '---\n\n'
    printf 'body without amendment headings.\n'
  } > "$dir/archive/adr/$name"
}

assert_parity_gate_exit() {
  local name="$1" fixroot="$2" expected_rc="$3"
  local out rc census=0
  out="$(PYTHONUTF8=1 "$PYBIN" "$SRC" --mode parity --repo-root "$fixroot" 2>&1)"
  rc=$?
  printf '%s\n' "$out" | grep -q 'census adr_candidates=[1-9]' && census=1
  if [ "$rc" -eq "$expected_rc" ] && [ "$census" -eq 1 ]; then
    echo "PASS: $name -- exit $rc (census 관측)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $name -- exit $rc (기대 $expected_rc), census=$census"
    FAIL=$((FAIL+1))
  fi
}

echo "==============================================================================="
echo "CFP-2812 Phase 2 QADev: heading<->fm parity + 재해석 marker discriminating self-test"
echo "F-1(heading-only RED) / AC-4(marker presence/consistency) + fail-closed(D9)"
echo "==============================================================================="
echo ""

# ── unit: check_parity (heading-only drift 판정) ──
echo "-- unit: check_parity (F-1) --"
run_py_assert "parity heading-only RED (3>0)" "m.check_parity(3,0)!=[]"
run_py_assert "parity fm>=heading GREEN (0<=3)" "m.check_parity(0,3)==[]"
run_py_assert "parity 동수 GREEN (3==3)" "m.check_parity(3,3)==[]"
run_py_assert "parity heading>fm RED (4>3)" "m.check_parity(4,3)!=[]"

# ── unit: check_marker_presence (AC-4) ──
echo "-- unit: check_marker_presence (AC-4) --"
run_py_assert "marker 미기재 RED" "m.check_marker_presence({})!=[]"
run_py_assert "marker 비-boolean RED" "m.check_marker_presence({'reinterpretation':'yes'})!=[]"
run_py_assert "marker True GREEN(warning 신호일 뿐 fail 아님)" "m.check_marker_presence({'reinterpretation':True})==[]"
run_py_assert "marker False GREEN" "m.check_marker_presence({'reinterpretation':False})==[]"
echo ""

# ── mutation-kill: 순수 함수 검출력 (pure-function) ──
echo "-- mutation-kill (check_parity / check_marker_presence) --"

# MP1: parity 검사 제거 -> heading-only 미검출. `if heading_n > fm_n:` -> `if False:`.
assert_pure_mutation_killed "MP1 parity-검사-제거" \
  "m.check_parity(3,0)" \
  's/    if heading_n > fm_n:/    if False:/'

# MP2: marker 타입 검사 회귀 -> 비-boolean 미검출. `isinstance(val, bool)` -> `isinstance(val, str)`.
assert_pure_mutation_killed "MP2 marker-타입검사-회귀" \
  "m.check_marker_presence({'reinterpretation':'yes'})" \
  's/    if not isinstance(val, bool):/    if not isinstance(val, str):/'

# MP3: marker presence 검사 제거 -> 미기재 미검출.
#   presence 무력화 + KeyError 회피(get default True) 2-sub.
assert_pure_mutation_killed "MP3 marker-presence-제거" \
  "m.check_marker_presence({})" \
  's/    if "reinterpretation" not in entry:/    if False:/; s/    val = entry\["reinterpretation"\]/    val = entry.get("reinterpretation", True)/'
echo ""

# ── orchestration: fail-closed(D9) + GREEN baseline(비-vacuous) ──
echo "-- orchestration (fail-closed / GREEN baseline) --"
fr="$(mktemp -d)"; make_malformed_adr "$fr" "ADR-911-malformed.md"
assert_parity_gate_exit "parity malformed RED(D9)" "$fr" 1
rm -rf "$fr"

fr="$(mktemp -d)"; make_clean_adr "$fr" "ADR-912-clean.md"
assert_parity_gate_exit "parity clean GREEN(비-vacuous census)" "$fr" 0
rm -rf "$fr"

echo ""
echo "==============================================================================="
echo "Test Results: $PASS passed, $FAIL failed"
echo "==============================================================================="

if [ "$FAIL" -eq 0 ]; then
  echo "All tests PASSED"
  exit 0
else
  echo "Some tests FAILED"
  exit 1
fi
