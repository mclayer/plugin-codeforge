#!/usr/bin/env bash
# tests/scripts/test_adr-amendment-threshold.sh
# CFP-2812 / ADR-167(adr-amendment-compaction-ratchet) / ADR-060 — ADR amendment 누적 임계 게이트
# discriminating self-test. Change Plan §8.1/§8.2/§8.11 Test Contract 이행 (AC-2/AC-3/AC-8).
#
# 대상 = scripts/lib/check_adr_amendment_threshold.py 순수 함수 6종 + orchestration.
#   순수 함수는 python 레벨 직접 fixture 로 찌르고(§8.1 D2), 임계 검출 로직은 게이트 전체를
#   fixture corpus 로 subprocess 구동해 mutation-kill 로 검증한다.
#
# anti-theater (ADR-119 검사연극 금지 / CFP-2440 선례): always-pass 0, tautology 0.
#   각 mutant 는 SSOT 소스의 1-line mutation 으로 검출 무력화되어야(변이본 GREEN) KILLED.
#   두 축으로 비-hollow 를 보장한다:
#     (1) 정본 GREEN/RED baseline — 미변이 소스가 fixture 에서 정확 동작(임계미달 GREEN / 초과 RED).
#     (2) mutation-kill — 각 mutant 별 mktemp copy 에 deterministic sed 적용 후 동일 fixture 재구동.
#         반드시 정본과 다른 verdict(=mutation 검출). 미검출 시 SURVIVED → FAIL.
#
# RED 진정성 (본 agent §RED 관행): 게이트 스크립트는 신규 파일(prior HEAD 버전 부재)이라 git-stash
#   pre-GREEN 노출 기법은 N/A — 대신 mutation-kill 이 discriminating proof 를 대신한다. 각 mutant 는
#   정본의 특정 검출 동작을 revert 하여 genuine 실패(변이본 GREEN)를 보이므로 vacuous-green 아님.
#
# distinct-marker (본 agent §외부 script subprocess fork 의무): 게이트를 subprocess fork 해 verdict 를
#   판정하므로 exit-code 단독 판정 금지 — 도메인 고유 stdout sentinel `census adr_candidates=`(scan 실행
#   증거) 를 병행 assert 한다. census 미관측 = fork/scan 미실행 → 즉시 FAIL(exit-code 우연일치 방어).
#
# shell 관례 (§8.11 / ADR-060 Amd22 exit-masking 금지): set -u + PASS/FAIL 카운터 + mktemp 격리 +
#   diff -q no-op guard(symmetric sed trap 차단, CFP-2491) + exit 0/1(FAIL>0 → 1). bare `|| true`
#   마스킹 없이 assertion/카운터 동반. python fixture code·grep 패턴은 ASCII 고정(한글 argv 오탐 회피).
#
# set -e 미사용 — 각 test 는 카운터로 집계하고 마지막에 exit code 결정.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$REPO_ROOT/scripts/lib/check_adr_amendment_threshold.py"

PASS=0
FAIL=0

PYBIN="$(command -v python3 || command -v python)"

# ─── fixture 생성 helper (전부 ASCII — 한글 bytes mangling 회피) ─────────────────

# n 개의 `## Amendment k` 헤딩을 본문에 담은 ADR (frontmatter 에 amendment 리스트 없음 → fm_n=0).
make_heading_adr() {
  local dir="$1" name="$2" n="$3"
  mkdir -p "$dir/archive/adr"
  {
    printf -- '---\n'
    printf 'title: fixture heading ADR\n'
    printf 'status: proposed\n'
    printf -- '---\n\n'
    local i=1
    while [ "$i" -le "$n" ]; do
      printf '## Amendment %d\n' "$i"
      i=$((i+1))
    done
    printf 'body text without further headings.\n'
  } > "$dir/archive/adr/$name"
}

# heading 0 + frontmatter dual-key (amendment_log 6 + amendments 6 = 12) ADR.
#   합산 산식이 첫-키-우선(first-key-wins) 으로 회귀하면 12 -> 6 으로 줄어 임계 검출이 누락된다.
make_dualkey_adr() {
  local dir="$1" name="$2"
  mkdir -p "$dir/archive/adr"
  {
    printf -- '---\n'
    printf 'title: fixture dual-key ADR\n'
    printf 'amendment_log:\n'
    local i
    for i in 1 2 3 4 5 6; do printf '  - amendment_id: %d\n' "$i"; done
    printf 'amendments:\n'
    for i in 7 8 9 10 11 12; do printf '  - amendment_id: %d\n' "$i"; done
    printf -- '---\n\n'
    printf 'body text without amendment headings.\n'
  } > "$dir/archive/adr/$name"
}

# frontmatter YAML 이 깨진 ADR (unterminated flow) — fail-closed(D9) RED fixture.
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

# ─── unit: 순수 함수 python-level assertion (§8.1 D2) ────────────────────────────
# expr 를 eval 해 truthy 면 PASS. eval globals 에 module m 주입. ASCII-only.
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

# ─── AC-3 mutation-kill: 게이트 전체 subprocess fork + census distinct-marker ─────
# 정본은 fixture 에서 exit 1(RED), 변이본은 exit 0(GREEN) 이어야 KILLED.
# census(`adr_candidates=`) 를 양 실행 모두에서 관측해 실제 fork/scan 됐음을 병행 입증.
assert_threshold_mutant_killed() {
  local name="$1" fixroot="$2" sed_expr="$3"
  local mdir mutant base_out base_rc mut_out mut_rc
  mdir="$(mktemp -d)"
  mutant="$mdir/mutant.py"
  cp "$SRC" "$mutant"
  sed -i "$sed_expr" "$mutant"

  # no-op guard: sed 가 실제로 소스를 바꿨는지 (symmetric trap 차단)
  if diff -q "$SRC" "$mutant" >/dev/null 2>&1; then
    echo "FAIL: $name -- sed mutation no-op (소스 무변경 — mutant 정의 오류)"
    FAIL=$((FAIL+1))
    rm -rf "$mdir"
    return
  fi

  base_out="$(PYTHONUTF8=1 "$PYBIN" "$SRC" --mode threshold --repo-root "$fixroot" 2>&1)"
  base_rc=$?
  mut_out="$(PYTHONUTF8=1 "$PYBIN" "$mutant" --mode threshold --repo-root "$fixroot" 2>&1)"
  mut_rc=$?
  rm -rf "$mdir"

  # distinct-marker: census 관측(>=1 candidate) — exit-code 우연일치·미 fork 방어
  local base_census=0 mut_census=0
  printf '%s\n' "$base_out" | grep -q 'census adr_candidates=[1-9]' && base_census=1
  printf '%s\n' "$mut_out"  | grep -q 'census adr_candidates=[1-9]' && mut_census=1
  if [ "$base_census" -ne 1 ] || [ "$mut_census" -ne 1 ]; then
    echo "FAIL: $name -- census 미관측 (fork/scan 미실행 의심: base=$base_census mut=$mut_census)"
    FAIL=$((FAIL+1))
    return
  fi

  # KILLED = 정본 RED(exit1) AND 변이본 GREEN(exit0)
  if [ "$base_rc" -eq 1 ] && [ "$mut_rc" -eq 0 ]; then
    echo "PASS: $name -- mutant KILLED (정본 RED exit1, 변이본 GREEN exit0)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $name -- mutant SURVIVED/불일치 (base_rc=$base_rc mut_rc=$mut_rc, 기대 1/0)"
    FAIL=$((FAIL+1))
  fi
}

# ─── 정본 게이트 exit code assertion (malformed / AC-2 / AC-8) ───────────────────
assert_gate_exit() {
  local name="$1" fixroot="$2" expected_rc="$3"; shift 3
  local out rc census=0
  out="$(PYTHONUTF8=1 "$PYBIN" "$SRC" --mode threshold --repo-root "$fixroot" "$@" 2>&1)"
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
echo "CFP-2812 Phase 2 QADev: ADR amendment 누적 임계 게이트 discriminating self-test"
echo "AC-2(산식<->baseline 동일성) / AC-3(mutation-kill) / AC-8(사이클) + fail-closed(D9)"
echo "==============================================================================="
echo ""

# ── unit: count_frontmatter_entries dual-key 합산 (§8.2 collection size) ──
echo "-- unit: 순수 함수 (dual-key 합산 / effective=max / BVA / marker) --"
run_py_assert "count_fm dual-key 합산 25" \
  "m.count_frontmatter_entries({'amendment_log':[0]*10,'amendments':[0]*15})==25"
run_py_assert "count_fm 비-list 키 무시" \
  "m.count_frontmatter_entries({'amendment_log':None,'amendments':[0]*3})==3"
run_py_assert "count_heading 2매치" \
  "m.count_heading_amendments('## Amendment 1\n### Amendment 2\n')==2"
run_py_assert "count_heading 단일#/비헤딩 0매치" \
  "m.count_heading_amendments('# Amendment X\nAmendment Y\n')==0"

# ── unit: effective_count = max (역방향 drift 포함) ──
run_py_assert "effective max(0,16)==16" "m.effective_count(0,16)==16"
run_py_assert "effective max(59,21)==59" "m.effective_count(59,21)==59"

# ── unit: check_threshold 4분기 BVA (N=10, `>=`) ──
run_py_assert "BVA 9 미달 GREEN" "m.check_threshold(9,'ADR-999',{},10)==[]"
run_py_assert "BVA 10 미등재 RED" "m.check_threshold(10,'ADR-999',{},10)!=[]"
run_py_assert "BVA 11 미등재 RED" "m.check_threshold(11,'ADR-999',{},10)!=[]"
run_py_assert "grandfather == GREEN" "m.check_threshold(10,'ADR-082',{'ADR-082':10},10)==[]"
run_py_assert "grandfather 초과 RED" "m.check_threshold(11,'ADR-082',{'ADR-082':10},10)!=[]"
# shrink 분기(iv)는 effective>=N 이면서 <grandfathered_at 일 때만 도달 (effective<N 은 분기0에서 GREEN 단락)
run_py_assert "grandfather shrink RED" "m.check_threshold(10,'ADR-082',{'ADR-082':12},10)!=[]"

# ── unit: check_marker_presence (미기재/비-boolean RED, boolean GREEN) ──
run_py_assert "marker 미기재 RED" "m.check_marker_presence({})!=[]"
run_py_assert "marker 비-boolean RED" "m.check_marker_presence({'reinterpretation':'yes'})!=[]"
run_py_assert "marker True GREEN" "m.check_marker_presence({'reinterpretation':True})==[]"
run_py_assert "marker False GREEN(false != fail)" "m.check_marker_presence({'reinterpretation':False})==[]"
echo ""

# ── AC-3 mutation-kill (4 취약 revert) ──
echo "-- AC-3 mutation-kill (임계검사/경계/baseline/dual-key 합산) --"

# mutant#1 임계 검사 제거: effective<N 분기를 항상 True 로 -> 항상 GREEN.
#   fixture = 미등재 effective 11 -> 정본 RED, 변이본 항상 GREEN.
fr="$(mktemp -d)"; make_heading_adr "$fr" "ADR-901-a.md" 11
assert_threshold_mutant_killed "mutant#1 임계검사-제거" "$fr" \
  's/    if effective < threshold_n:/    if effective < threshold_n or True:/'
rm -rf "$fr"

# mutant#2 `>=`->`>` off-by-one: `<` -> `<=` 로 경계값 N=10 을 미검출.
#   fixture = 미등재 effective 정확히 10 (경계) -> 정본 RED, 변이본 GREEN.
fr="$(mktemp -d)"; make_heading_adr "$fr" "ADR-902-b.md" 10
assert_threshold_mutant_killed "mutant#2 경계-off-by-one(10)" "$fr" \
  's/    if effective < threshold_n:/    if effective <= threshold_n:/'
rm -rf "$fr"

# mutant#3 baseline 미등재 세탁: 미등재 검사를 무력화하고 미등재 ADR 을 현재 count 로 자동 grandfather.
#   (단순 무력화는 grandfathered_at 역참조 KeyError 로 crash -> 2-sub 로 안전 우회 후 GREEN 유도)
#   fixture = 미등재 effective 11 -> 정본 RED(미등재), 변이본 GREEN(자동 grandfather).
fr="$(mktemp -d)"; make_heading_adr "$fr" "ADR-903-c.md" 11
assert_threshold_mutant_killed "mutant#3 baseline-미등재-세탁" "$fr" \
  's/    if adr_id not in baseline:/    if False:/; s/    grandfathered_at = baseline\[adr_id\]/    grandfathered_at = baseline.get(adr_id, effective)/'
rm -rf "$fr"

# mutant#4 first-key-wins 회귀: dual-key 합산을 첫 list 키만 세도록 -> 12 -> 6 으로 임계 미달.
#   fixture = heading 0 + amendment_log 6 + amendments 6 (합 12) -> 정본 RED, 변이본 GREEN.
fr="$(mktemp -d)"; make_dualkey_adr "$fr" "ADR-904-d.md"
assert_threshold_mutant_killed "mutant#4 first-key-wins-회귀" "$fr" \
  's/            total += len(val)/            return len(val)/'
rm -rf "$fr"
echo ""

# ── fail-closed(D9): malformed frontmatter -> 침묵 GREEN 아닌 명시 exit 1 ──
echo "-- fail-closed(D9) / AC-2 / AC-8 (정본 게이트) --"
fr="$(mktemp -d)"; make_malformed_adr "$fr" "ADR-905-malformed.md"
assert_gate_exit "malformed-YAML RED(D9)" "$fr" 1
rm -rf "$fr"

# ── AC-2: 도입 corpus --write-baseline 생성물로 무인자 threshold -> 소급 fail 0 (exit 0) ──
fr="$(mktemp -d)"
make_heading_adr "$fr" "ADR-801-over1.md" 11
make_heading_adr "$fr" "ADR-802-over2.md" 12
make_heading_adr "$fr" "ADR-803-clean.md" 0
PYTHONUTF8=1 "$PYBIN" "$SRC" --mode threshold --write-baseline --repo-root "$fr" >/dev/null 2>&1
wb_rc=$?
if [ "$wb_rc" -eq 0 ] && [ -f "$fr/docs/adr-amendment-threshold-baseline.yaml" ]; then
  echo "PASS: AC-2 --write-baseline 생성 (exit 0 + baseline 파일 존재)"
  PASS=$((PASS+1))
else
  echo "FAIL: AC-2 --write-baseline 실패 (rc=$wb_rc, baseline 파일=$([ -f "$fr/docs/adr-amendment-threshold-baseline.yaml" ] && echo yes || echo no))"
  FAIL=$((FAIL+1))
fi
assert_gate_exit "AC-2 산식<->baseline 동일성 (소급 fail 0)" "$fr" 0
rm -rf "$fr"

# ── AC-8: 재제정 신규 ADR count 0 -> baseline 비대상 GREEN ──
fr="$(mktemp -d)"; make_heading_adr "$fr" "ADR-806-fresh.md" 0
assert_gate_exit "AC-8 count0 재제정 ADR GREEN" "$fr" 0
rm -rf "$fr"

# ── AC-8: 퇴역 ADR baseline 항목 미제거(dangling) -> B-2 검출 RED ──
fr="$(mktemp -d)"
make_heading_adr "$fr" "ADR-807-clean.md" 0
mkdir -p "$fr/docs"
printf 'entries:\n- adr: ADR-999\n  grandfathered_at: 10\n' > "$fr/docs/adr-amendment-threshold-baseline.yaml"
assert_gate_exit "AC-8 dangling baseline entry RED(B-2)" "$fr" 1
rm -rf "$fr"

# ── F-SEC-01(c) ReDoS teeth: FRONTMATTER_RE blank-line payload sub-초 파싱 (discriminating) ──
# born-safe bound 검출력 — 정본([ \t]*) sub-초 완료 / 취약 revert(\s*, 개행 소비 복원) 이차 backtracking
#   → timeout 초과 = KILLED. 단순 존재 아닌 검출력(mutation-kill) 실증. mktemp 격리 + diff -q no-op guard.
echo "-- F-SEC-01(c) ReDoS teeth (FRONTMATTER_RE blank-line, discriminating) --"
if ! command -v timeout >/dev/null 2>&1; then
  echo "SKIP: ReDoS teeth — 'timeout' 미가용 (CI Linux 채널 adr-amendment-threshold-test.yml 에서 실행)"
else
  redos_root="$(mktemp -d)"
  mkdir -p "$redos_root/archive/adr"
  # blank-line payload (~60KB, 미완결 frontmatter) — 전 body backtrack 유도
  { printf -- '---\n'; head -c 61440 /dev/zero | tr '\0' '\n'; printf 'x\n'; } > "$redos_root/archive/adr/ADR-909-redos.md"
  printf 'schema_version: "1.0"\nentries: []\n' > "$redos_root/empty-baseline.yaml"
  timeout 6 env PYTHONUTF8=1 "$PYBIN" "$SRC" --mode threshold --repo-root "$redos_root" \
    --baseline "$redos_root/empty-baseline.yaml" "$redos_root/archive/adr/ADR-909-redos.md" >/dev/null 2>&1
  canon_rc=$?
  if [ "$canon_rc" -eq 124 ]; then
    echo "FAIL: ReDoS teeth — 정본이 timeout(124) — FRONTMATTER_RE ReDoS 미수정 의심"
    FAIL=$((FAIL+1))
  else
    rmut="$(mktemp -d)"; rmutant="$rmut/mutant.py"; cp "$SRC" "$rmutant"
    sed -i 's/\[ \\t\]\*/\\s*/g' "$rmutant"   # FRONTMATTER_RE [ \t]* → \s* (취약 복원)
    if diff -q "$SRC" "$rmutant" >/dev/null 2>&1; then
      echo "FAIL: ReDoS teeth — sed mutation no-op ([ \\t]* 미치환, 정본에 born-safe bound 부재 의심)"
      FAIL=$((FAIL+1))
    else
      timeout 6 env PYTHONUTF8=1 "$PYBIN" "$rmutant" --mode threshold --repo-root "$redos_root" \
        --baseline "$redos_root/empty-baseline.yaml" "$redos_root/archive/adr/ADR-909-redos.md" >/dev/null 2>&1
      mut_rc=$?
      if [ "$mut_rc" -eq 124 ]; then
        echo "PASS: ReDoS teeth — 정본 sub-초(rc=$canon_rc) / 취약 revert timeout(124) KILLED (FRONTMATTER_RE 이차 backtracking 검출력)"
        PASS=$((PASS+1))
      else
        echo "FAIL: ReDoS teeth — 취약 revert 가 timeout 안 남(rc=$mut_rc) — discriminating 미작동"
        FAIL=$((FAIL+1))
      fi
    fi
    rm -rf "$rmut"
  fi
  rm -rf "$redos_root"
fi

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
