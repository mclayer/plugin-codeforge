#!/usr/bin/env bash
# tests/scripts/test_check-hard-gate-self-verification.sh
# CFP-2684 (ADR-154) — hard-gate self-verification 메타-게이트 재귀 L3 discriminating self-test.
#
# hgsv-enroll  (self-source EXEMPT: 본 파일 path 는 'hard-gate-self-verification' 토큰을 담으므로
#              메타-게이트 자신의 subject 발견에서 자동 제외됨 — §7.7(1)/_SELF_SOURCE_TOKENS.
#              위 marker 는 selftest-execution-liveness 인벤토리 bijection 대응행일 뿐, 자기 subject 아님.)
#
# 대상 = hard-gate-self-verification META-GATE (ADR-154 §결정7 / Change Plan §8.2.1 RTM).
#   wrapper (PINNED): scripts/check-hard-gate-self-verification.sh [ARGS]
#     → execs: python3 scripts/lib/check_hard_gate_self_verification.py [ARGS]
#   CLI 계약 (PINNED — 이 test 가 소비, [reconciled: gate core docstring]):
#     --repo-root DIR  → subject=<DIR>/tests/scripts/*.sh (enroll marker 'hgsv-enroll' 보유),
#                        concept-doc=<DIR>/docs/domain-knowledge/concept/hard-gate-self-verification.md
#     EXIT: 0 = 전 fail-closed AC 통과(enrolled 0 honest-degrade 포함) / 1 = ≥1 위반 or unknown input
#           / 2 = argparse usage.
#
# ── ★NON-NEGOTIABLE: firsthand execution / real exit codes / green ≠ red ────────
#   fixture repo-root 를 mktemp -d 로 실제 build → REAL 게이트 `--repo-root <fixture>` 실행 →
#   REAL exit code(및 M4 는 REAL stdout) 대조. repo 실파일 무오염(fixture 트리만 build).
#   anti-theater: present→exit0 이 absent/mutant→exit1 과 반드시 DIFFER. 게이트 미착륙 시
#   NOT_RUN sentinel → false PASS 금지(exit1).
#
# ── RTM §8.2.1 (authoritative) — 13 AC ↔ test 함수 (present→exit0 ↔ absent→exit1) ──
#   AC-1  test_ac1_positive_control_present   positive-control anchor 보유→0 ↔ 부재→1        (M1)
#   AC-2  test_ac2_two_exit_shape             2-exit-differ shape→0 ↔ string-only/single→1   (M6 seal)
#   AC-3  test_ac3_empty_target_failclosed    enrolled0 honest-degrade→0 ↔ unreadable subj→1 (M3 stdout축=M4)
#   AC-4  test_ac4_unknown_input_failclosed   valid repo-root→0 ↔ 미존재/비-dir→1            (M3-primary 계열)
#   AC-5  test_ac5_execution_trace_emit       green verdict stdout 에 trace/count 문구 present (M4 반증)
#   AC-6  test_ac6_three_way_taxonomy_present 3-way + '결함 아님'→0 ↔ 토큰/예외 부재→1        (M2)
#   AC-7  test_ac7_self_application           TC-CLEAN-PASS + M1-M6 positive-leak + LIVE ceiling + bijection
#   AC-8  test_ac8_honest_ceiling_present     ceiling + presence≠truth + over-claim 부재→0 ↔ 부재/over-claim→1
#   AC-12 test_ac12_crossref_nodup           named≥6 + 3영역 + 재codify 부재→0 ↔ <6/재codify/영역누락→1
#   AC-13 test_ac13_identity_probe            identity_bearing:true+probe→0 ↔ +probe부재→1; 미선언=no-op(→0) (M5)
#
# ── ★M4 nuance (반드시 정확히) ──────────────────────────────────────────────────
#   M4(AC-5 trace / AC-3 honest-degrade 선언 emit)는 stdout print 이지 exit-flip 분기 아님.
#   neutralize 해도 exit 불변(0→0) → discriminating 기준 = STDOUT token 소실(exit 대조 아님).
#   M1/M2/M3/M5/M6 = exit-flip(baseline kill-fixture exit1 → mutant exit0). 이 비대칭을 정확 반영.
#
# ── §7.3-self / §8.8.2 property — PERF DoS-bound 회귀가드 (proof-ref 결속) ────────
#   gate docstring(check_hard_gate_self_verification.py:38)이 본 self-test 를 "PERF DoS 회귀가드 —
#   실측 wall-clock" proof-ref 로 단정 → test_perf_dos_bound 가 large-input(>MAX_PHYSICAL_LINE_LEN
#   단일라인 + >PER_FILE_SCAN_CAP 라인)에서 REAL 게이트 wall-clock 을 bound 이내 완료로 실측 반증
#   (islice count-cap + per-line truncate + anchored bounded regex, nested quantifier 0 → O(n²) 부재).
#   정직 천장: 총 작업량 bound 이지 임의 입력 무해 아님(bounded degradation, presence ≠ truth).
#
# ── §8.2 AC-7 sealing (born-hollow FORBIDDEN, positive-leak) ────────────────────
#   mutation M1-M6 = REAL gate copy(mktemp) 를 sed 로 fail-closed 분기 no-op 化 → kill-fixture 실행.
#   KILLED ⟺ original(kill-fixture)=exit1 AND mutated=exit0 (M4=stdout token 소실). exit≠(false,1) 오수용 금지.
#   double-guard: (a) sed 실제 치환(미치환→NOT_RUN FAIL) + (b) mutated 는 valid python(py_compile).
#   [reconciled: MUTATION-SENTINEL M1(L226)/M6(L233)/M5(L241)/M2(L303)/M3공유(L366-368)/M4(L407-409)]
#   inline hand-copy 금지(ADR-082 §11.A tautology) — 실 gate 파일 cp 대상만 mutate.
#
# Exit code: 0 = 전 assert PASS + 전 discriminating/mutation 성립, 1 = 하나라도 FAIL/non-discriminating/NOT_RUN

set -uo pipefail

# ═════════════════════════════════════════════════════════════════════════════
# 0. Preamble — 경로 · 러너 · tally · cleanup
# ═════════════════════════════════════════════════════════════════════════════
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GATE_WRAPPER="$REPO_ROOT/scripts/check-hard-gate-self-verification.sh"
GATE_PY="$REPO_ROOT/scripts/lib/check_hard_gate_self_verification.py"
CONCEPT_REL="docs/domain-knowledge/concept/hard-gate-self-verification.md"
ADR_154="$REPO_ROOT/archive/adr/ADR-154-hard-gate-self-verification-forcing-function.md"
REGISTRY="$REPO_ROOT/docs/evidence-checks-registry.yaml"

PASS=0
FAIL=0
SKIP=0
LAST_EC=""

note() { echo "::notice::$*" >&2; }
log()  { echo "$*" >&2; }
pass_case() { echo "  ✓ PASS: $1"; PASS=$((PASS+1)); }
fail_case() { echo "  ✗ FAIL: $1"; FAIL=$((FAIL+1)); }
skip_case() { echo "  ⊘ SKIP: $1"; SKIP=$((SKIP+1)); }

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "✗ FAIL: python3/python 부재 — 메타-게이트 실행 불가"
  exit 1
fi

TEST_TMP="$(mktemp -d)"
CLEANUP_DIRS=()
cleanup() {
  rm -rf "$TEST_TMP" 2>/dev/null
  local d
  for d in "${CLEANUP_DIRS[@]:-}"; do [ -n "$d" ] && rm -rf "$d" 2>/dev/null; done
}
trap cleanup EXIT
new_fixture() { local d; d="$(mktemp -d "$TEST_TMP/fx.XXXXXX")"; echo "$d"; }

# ═════════════════════════════════════════════════════════════════════════════
# 1. 게이트 실행 helper — REAL exit code(및 stdout) echo (로그는 stderr)
# ═════════════════════════════════════════════════════════════════════════════
# run_gate <repo_root> [args...] → echoes exit code. PINNED entry = wrapper .sh, 부재 시 py fallback.
run_gate() {
  local fix="$1"; shift
  local out ec=0
  if [ -f "$GATE_WRAPPER" ]; then
    out=$( bash "$GATE_WRAPPER" --repo-root "$fix" "$@" 2>&1 ) || ec=$?
  else
    out=$( "$PY" "$GATE_PY" --repo-root "$fix" "$@" 2>&1 ) || ec=$?
  fi
  printf '%s\n' "$out" | sed 's/^/      gate> /' >&2
  echo "$ec"
}

# run_pyfile <py_path> <repo_root> [args...] → echoes exit code. mutation 전용(지정 py 직접 실행).
#   게이트 core = stdlib(argparse/itertools/re/sys/pathlib)만 — sibling import 0 → PYTHONPATH 불요.
run_pyfile() {
  local py="$1" fix="$2"; shift 2
  local out ec=0
  out=$( "$PY" "$py" --repo-root "$fix" "$@" 2>&1 ) || ec=$?
  printf '%s\n' "$out" | sed 's/^/      py> /' >&2
  echo "$ec"
}

# gate_stdout <py_path> <repo_root> → echoes ONLY stdout (stderr drop) — M4/AC-5 trace 검사.
gate_stdout() {
  local py="$1" fix="$2"; shift 2
  "$PY" "$py" --repo-root "$fix" "$@" 2>/dev/null
}

# ═════════════════════════════════════════════════════════════════════════════
# 2. fixture emit — GREEN seed(전 AC 충족) + mode override 로 단일 결함 RED
# ═════════════════════════════════════════════════════════════════════════════
# emit_concept_doc <mode> — GREEN 은 AC-6/8/12 동시 충족. mode 로 단일 토큰 결함 주입.
#   [reconciled: gate _TAXONOMY_TOKENS / _HONEST_DEGRADE_EXCEPTION / _CEILING_TOKENS /
#    _PRESENCE_TRUTH_TOKENS / _NAMED_CONCEPTS(≥6) / _NEW_DEF_AREAS / _detect_recodify / _detect_overclaim]
#   토큰 격리 규칙: 각 mode 결함 토큰이 정확히 1곳에만 존재하도록 heading/area 에서 중복 토큰 배제.
emit_concept_doc() {
  local mode="${1:-green}"
  echo "# hard gate self-verification concept (fixture)"
  echo ""
  echo "## 3-way taxonomy (antonym)"
  echo "- silent-green — 게이트 green 이나 검출력 0 = 결함(위양성)"
  [ "$mode" = "no_tax" ] || echo "- silent-fallback — 검증 경로 우회/흡수 = 결함(위양성)"
  echo "- honest-degrade — 의도적 fail-open + 정직 공개 = 정상"
  # 예외 토큰 격리: '결함 아님' 만 담고 taxonomy 토큰(silent-fallback 등)은 배제 → no_tax mode 가 silent-fallback 를 정확 제거.
  [ "$mode" = "no_exc" ] || echo "  honest-degrade 는 결함 아님 (오탐 방지 codify 필수 — 무차별 검출 = 위양성)."
  echo ""
  echo "## ceiling"
  [ "$mode" = "no_ceiling" ] || echo "검출 sufficiency = undecidable — 정직 천장(honest-ceiling). L3 review-tier(AC-9)."
  # pt 라인 격리: denial marker(아님/않/없...) 배제 → over-claim RED fixture 가 ±1 denial-context 로 가려지지 않게.
  [ "$mode" = "no_pt" ] || echo "presence ≠ truth. bounded degradation."
  [ "$mode" = "overclaim" ] && echo "이 메타-게이트는 universal detection 완전 봉인 을 달성한다."
  echo ""
  echo "## named cross-ref (super-class compose, 재정의 0)"
  echo "- red-green-stash-proof — RED proof (ADR-082 §11.A)"
  echo "- vacuous-pass — 검출력 0 green 상위 class"
  echo "- execution-liveness — self-test 채널 alive L1 (ADR-151)"
  if [ "$mode" != "few_named" ]; then
    echo "- discriminating-fixture — clean↔mutant 구별 (ADR-006 §8.7)"
    echo "- discriminating-A/B — self-test / product activation (ADR-152)"
    echo "- mutation-hollow-gate — meta-hollow 차단"
    echo "- honest-degrade — 정직 공개 cross-ref"
  fi
  echo ""
  echo "## 신규 정의 3영역"
  echo "super-class 명명 + taxonomy codify"
  [ "$mode" = "no_area" ] || echo "+ internal-control identity-probe."
  [ "$mode" = "recodify" ] && echo "- execution-liveness = 재정의 대입 (cross-ref only 위반)"
}

# emit_subject <mode> — enrolled hard-gate self-test fixture (fake 대상 게이트의 self-test).
#   [reconciled: gate _ENROLL_MARKERS('hgsv-enroll') / _POSITIVE_CONTROL_ANCHORS / _has_two_exit_shape
#    (≥2 X=$? + -eq0 + -ne0) / _IDENTITY_BEARING_DECL / _PROBE_ANCHORS]
emit_subject() {
  local mode="${1:-good}"
  echo "#!/usr/bin/env bash"
  echo "# hgsv-enroll (hard gate self-test fixture subject)"
  [ "$mode" = "no_positive" ] || echo "# positive-control: sanity mutant→RED (결함앞 RED 상시 증명)"
  if [ "$mode" = "id_no_probe" ] || [ "$mode" = "id_probe" ]; then
    echo "# identity_bearing: true"
  fi
  [ "$mode" = "id_probe" ] && echo "# internal-control: resolved-target 원문대조 known-answer probe"
  if [ "$mode" = "no_shape" ]; then
    # string-only(exit-capture 0) — _has_two_exit_shape False → AC-2 RED (M6 seal 대상).
    echo 'echo "clean case: exit 0 expected"'
    echo 'echo "mutant case: exit 1 expected"'
  else
    # 2-exit-differ shape: ≥2 exit-capture + clean(-eq 0) + mutant(-ne 0).
    echo 'run_gate clean; rc=$?'
    echo 'run_gate mutant; mrc=$?'
    echo 'if [ "$rc" -eq 0 ]; then echo clean-ok; fi'
    echo 'if [ "$mrc" -ne 0 ]; then echo mutant-red; fi'
  fi
}

# build_fixture <F> — env: CONCEPT_MODE / SUBJECT_MODE / ENROLLED_ZERO / ADD_UNREADABLE
build_fixture() {
  local F="$1"
  mkdir -p "$F/docs/domain-knowledge/concept" "$F/tests/scripts"
  emit_concept_doc "${CONCEPT_MODE:-green}" > "$F/$CONCEPT_REL"
  if [ "${ENROLLED_ZERO:-}" != "1" ]; then
    emit_subject "${SUBJECT_MODE:-good}" > "$F/tests/scripts/test_subject_good.sh"
  fi
  # 미 enroll decoy(marker 부재) — subject 발견에서 제외되어야(무영향 실증).
  printf '#!/usr/bin/env bash\n# no enroll marker here\nexit 0\n' > "$F/tests/scripts/test_decoy_plain.sh"
  if [ "${ADD_UNREADABLE:-}" = "1" ]; then
    # 디렉터리를 *.sh 로 생성 → open() OSError → _read_lines None → AC-4 unreadable fail-closed.
    mkdir -p "$F/tests/scripts/test_unreadable.sh"
  fi
}

# 편의 빌더 (단일 결함).
build_green()             { build_fixture "$1"; }
build_enrolled_zero()     { ENROLLED_ZERO=1 build_fixture "$1"; }
build_red_ac1()           { SUBJECT_MODE=no_positive build_fixture "$1"; }
build_red_ac2()           { SUBJECT_MODE=no_shape build_fixture "$1"; }
build_red_ac13()          { SUBJECT_MODE=id_no_probe build_fixture "$1"; }
build_green_ac13probe()   { SUBJECT_MODE=id_probe build_fixture "$1"; }
build_red_unreadable()    { ADD_UNREADABLE=1 build_fixture "$1"; }
build_red_ac6_tax()       { CONCEPT_MODE=no_tax build_fixture "$1"; }
build_red_ac6_exc()       { CONCEPT_MODE=no_exc build_fixture "$1"; }
build_red_ac8_ceiling()   { CONCEPT_MODE=no_ceiling build_fixture "$1"; }
build_red_ac8_pt()        { CONCEPT_MODE=no_pt build_fixture "$1"; }
build_red_ac8_overclaim() { CONCEPT_MODE=overclaim build_fixture "$1"; }
build_red_ac12_few()      { CONCEPT_MODE=few_named build_fixture "$1"; }
build_red_ac12_area()     { CONCEPT_MODE=no_area build_fixture "$1"; }
build_red_ac12_recodify() { CONCEPT_MODE=recodify build_fixture "$1"; }

# ═════════════════════════════════════════════════════════════════════════════
# 3. 공통 assert helper — REAL exit code 대조 + discriminating 판정
# ═════════════════════════════════════════════════════════════════════════════
# expect_exit <desc> <want_ec> <builder> — fixture build → run_gate → LAST_EC 대조.
expect_exit() {
  local desc="$1" want="$2" builder="$3"
  local FX; FX="$(new_fixture)"; "$builder" "$FX"
  LAST_EC="$(run_gate "$FX")"
  if [ "$LAST_EC" = "$want" ]; then
    pass_case "$desc → exit $LAST_EC"
  else
    fail_case "$desc → exit $LAST_EC (기대 $want)"
  fi
}

# discriminating <ac> <green_ec> <red_ec> — anti-theater: present ≠ absent.
discriminating() {
  local ac="$1" g="$2" r="$3"
  if [ "$g" = "NOT_RUN" ] || [ "$r" = "NOT_RUN" ]; then
    skip_case "$ac discriminating 대조 불가 (NOT_RUN)"
  elif [ "$g" != "$r" ]; then
    pass_case "$ac ANTI-THEATER discriminating — present(exit=$g) ≠ absent(exit=$r)"
  else
    fail_case "$ac ANTI-THEATER — present(exit=$g) == absent(exit=$r) = non-discriminating"
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# 4. discriminating pair tests (RTM §8.2.1)
# ═════════════════════════════════════════════════════════════════════════════
test_ac1_positive_control_present() {
  log ""; log "══ AC-1 positive-control presence (M1 대상) ══"
  expect_exit "AC-1 present (positive-control 보유 subject)" 0 build_green;  local g="$LAST_EC"
  expect_exit "AC-1 absent  (positive-control 부재 subject)" 1 build_red_ac1; local r="$LAST_EC"
  discriminating "AC-1" "$g" "$r"
}

test_ac2_two_exit_shape() {
  log ""; log "══ AC-2 2-exit-differ SHAPE (M6 seal — shape-scan≠string-scan) ══"
  expect_exit "AC-2 present (2 exit-capture + -eq0 + -ne0 shape)" 0 build_green; local g="$LAST_EC"
  expect_exit "AC-2 absent  (string-only 'exit 0/1', capture 0)"  1 build_red_ac2; local r="$LAST_EC"
  discriminating "AC-2" "$g" "$r"
}

test_ac3_empty_target_failclosed() {
  log ""; log "══ AC-3 empty-target honest-degrade(exit0) ↔ unparseable fail-closed(exit1) ══"
  expect_exit "AC-3 empty-target (enrolled 0 + valid concept) honest-degrade" 0 build_enrolled_zero; local g="$LAST_EC"
  expect_exit "AC-3 정상 subject 존재"                                          0 build_green
  expect_exit "AC-3 unparseable/unreadable enrolled subject (dir-as-.sh)"      1 build_red_unreadable; local r="$LAST_EC"
  discriminating "AC-3" "$g" "$r"
  note "AC-3 empty-target 침묵 GREEN 축 = M4 stdout(honest-degrade 선언) + M3 mutation 으로 봉인(test_ac7)"
}

test_ac4_unknown_input_failclosed() {
  log ""; log "══ AC-4 unknown-input fail-closed (default 실행 금지) ══"
  expect_exit "AC-4 present (valid repo-root)" 0 build_green; local g="$LAST_EC"
  # 미존재 repo-root
  local NX; NX="$(new_fixture)/does_not_exist_subdir"
  local rec;  rec="$(run_gate "$NX")"
  if [ "$rec" = "1" ]; then pass_case "AC-4 absent (미존재 repo-root) → exit 1"; else fail_case "AC-4 미존재 repo-root → exit $rec (기대 1)"; fi
  # 비-dir repo-root (파일)
  local FF; FF="$(new_fixture)/afile"; printf 'x\n' > "$FF"
  local rec2; rec2="$(run_gate "$FF")"
  if [ "$rec2" = "1" ]; then pass_case "AC-4 absent (비-dir repo-root=파일) → exit 1"; else fail_case "AC-4 비-dir repo-root → exit $rec2 (기대 1)"; fi
  discriminating "AC-4(미존재)" "$g" "$rec"
  discriminating "AC-4(비-dir)"  "$g" "$rec2"
}

test_ac5_execution_trace_emit() {
  log ""; log "══ AC-5 execution-trace / count emit (stdout — M4 반증축) ══"
  local FG; FG="$(new_fixture)"; build_green "$FG"
  local out ec=0
  if [ -f "$GATE_WRAPPER" ]; then
    out="$( bash "$GATE_WRAPPER" --repo-root "$FG" 2>/dev/null )"; ec=$?
  else
    out="$( gate_stdout "$GATE_PY" "$FG" )"; ec=$?
  fi
  printf '%s\n' "$out" | sed 's/^/      stdout> /' >&2
  local has=0; printf '%s' "$out" | grep -qE "enrolled=|subject scanned|honest-degrade" && has=1
  if [ "$ec" = "0" ] && [ "$has" = "1" ]; then
    pass_case "AC-5 green verdict stdout 에 execution-trace/count 문구 present (enrolled=/scanned)"
  else
    fail_case "AC-5 stdout trace 부재 — exit=$ec has_trace=$has (기대 exit0 + trace token)"
  fi
}

test_ac6_three_way_taxonomy_present() {
  log ""; log "══ AC-6 3-way taxonomy + honest-degrade 예외 (M2 대상) ══"
  expect_exit "AC-6 present (silent-green/fallback/degrade + '결함 아님')" 0 build_green;    local g="$LAST_EC"
  expect_exit "AC-6 absent  (silent-fallback 토큰 부재)"                    1 build_red_ac6_tax; local r1="$LAST_EC"
  expect_exit "AC-6 absent  (honest-degrade 예외 '결함 아님' 부재)"         1 build_red_ac6_exc; local r2="$LAST_EC"
  discriminating "AC-6(taxonomy)" "$g" "$r1"
  discriminating "AC-6(예외)"      "$g" "$r2"
}

test_ac8_honest_ceiling_present() {
  log ""; log "══ AC-8 honest-ceiling presence + over-claim 부재 ══"
  expect_exit "AC-8 present (ceiling + presence≠truth + over-claim 부재)" 0 build_green;           local g="$LAST_EC"
  expect_exit "AC-8 absent  (ceiling 문구 부재)"                          1 build_red_ac8_ceiling;   local r1="$LAST_EC"
  expect_exit "AC-8 absent  ('presence ≠ truth' 부재)"                    1 build_red_ac8_pt;        local r2="$LAST_EC"
  expect_exit "AC-8 absent  (affirmative '완전 봉인' over-claim)"         1 build_red_ac8_overclaim; local r3="$LAST_EC"
  discriminating "AC-8(ceiling)"   "$g" "$r1"
  discriminating "AC-8(presence≠truth)" "$g" "$r2"
  discriminating "AC-8(over-claim)" "$g" "$r3"
}

test_ac12_crossref_nodup() {
  log ""; log "══ AC-12 named cross-ref ≥6 + 3영역 + 재codify 부재 ══"
  expect_exit "AC-12 present (named 7 + 3영역 + 재codify 0)" 0 build_green;             local g="$LAST_EC"
  expect_exit "AC-12 absent  (named <6)"                     1 build_red_ac12_few;      local r1="$LAST_EC"
  expect_exit "AC-12 absent  (신규 정의 영역 'identity-probe' 누락)" 1 build_red_ac12_area; local r2="$LAST_EC"
  expect_exit "AC-12 absent  (기존 named 재codify: 정의-대입 shape)"  1 build_red_ac12_recodify; local r3="$LAST_EC"
  discriminating "AC-12(count)"    "$g" "$r1"
  discriminating "AC-12(area)"     "$g" "$r2"
  discriminating "AC-12(recodify)" "$g" "$r3"
}

test_ac13_identity_probe() {
  log ""; log "══ AC-13 self-declared identity_bearing → internal-control probe (M5 대상) ══"
  expect_exit "AC-13 present (identity_bearing:true + probe anchor)" 0 build_green_ac13probe; local g="$LAST_EC"
  expect_exit "AC-13 absent  (identity_bearing:true + probe 부재)"   1 build_red_ac13;        local r="$LAST_EC"
  expect_exit "AC-13 no-op   (미선언=미대상, probe 없어도 exit0)"     0 build_green
  discriminating "AC-13" "$g" "$r"
}

# ═════════════════════════════════════════════════════════════════════════════
# 5. AC-7 sealing — TC-CLEAN-PASS + M1-M6 positive-leak + LIVE ceiling + bijection
# ═════════════════════════════════════════════════════════════════════════════
# sed_neutralize <py> <frm> <to> — 실 gate copy 의 정확 분기 문자열을 1:1 no-op 치환.
#   frm 미매칭(recipe drift) → exit1 (미적용 = false PASS 금지, NOT_RUN 처리). multi-line frm safe.
sed_neutralize() {
  "$PY" - "$1" "$2" "$3" <<'PYEOF'
import sys
p, frm, to = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p, encoding="utf-8").read()
if frm not in s:
    sys.exit(1)
open(p, "w", encoding="utf-8").write(s.replace(frm, to, 1))
sys.exit(0)
PYEOF
}

# py_valid <py> — mutated py 가 valid python 인지 (py_compile double-guard (b)).
py_valid() {
  "$PY" - "$1" <<'PYEOF'
import sys, py_compile
try:
    py_compile.compile(sys.argv[1], doraise=True)
except Exception as e:
    print("PYCOMPILE-FAIL:", e, file=sys.stderr)
    sys.exit(1)
sys.exit(0)
PYEOF
}

# ── [reconciled] mutation 대상 분기 문자열 (real gate 에서 firsthand 확인) ──
# exit-flip (M1/M2/M5/M6): single-line `if <cond>:` → `if False:`
FROM_M1='    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):'
TO_M1='    if False:  # neutralized M1 positive-control-presence'
FROM_M6='    if not _has_two_exit_shape(lines):'
TO_M6='    if False:  # neutralized M6 two-exit-shape'
FROM_M5='        if not any(a in text for a in _PROBE_ANCHORS):'
TO_M5='        if False:  # neutralized M5 identity-probe'
FROM_M2='    if not any(e in text for e in _HONEST_DEGRADE_EXCEPTION):'
TO_M2='    if False:  # neutralized M2 honest-degrade-exception'

# M3 (공유 unreadable-subject fail-closed): _error+append 만 제거, `continue` 보존(crash 회피 → silent skip).
#   ★ M3-primary(repo-root 존재 검사)는 bad-root 가 concept-doc 부재→AC-6 로 cascade 하여 exit0 flip 불가 →
#     구조상 non-discriminating. 따라서 M3 = 공유 discover-subjects unreadable 분기(clean flip)로 봉인.
FROM_M3="$(cat <<'EOF'
            # MUTATION-SENTINEL M3(공유): unknown/unreadable input → fail-closed (default 실행/skip 금지).
            _error("AC-4", f"{rel}: 파일 읽기 불가(unreadable/unparseable) — fail-closed exit1 (silent skip 금지).")
            violations.append(1)
EOF
)"
TO_M3='            pass  # neutralized M3-shared unreadable fail-closed (silent skip = fail-open)'

# M4 (execution-trace emit): else-branch enrolled≥1 trace print → token 소실. exit 불변(0→0).
FROM_M4="$(cat <<'EOF'
        print(f"✓ check-hard-gate-self-verification: enrolled={enrolled} subject scanned "
              f"(AC-1/2/13 presence/shape) + concept-doc AC-6/8/12 통과. "
              f"presence/shape 천장 — 검출 sufficiency=undecidable (review-tier, AC-9). presence ≠ truth.")
EOF
)"
TO_M4='        print("neutralized-m4-trace")'

# run_mutation_exit <label> <builder> <frm> <to> — baseline(kill-fixture)=exit1 → mutant=exit0 (positive-leak).
run_mutation_exit() {
  local label="$1" builder="$2" frm="$3" to="$4"
  log "── MUTATION $label (exit-flip) ──"
  local FR; FR="$(new_fixture)"; "$builder" "$FR"
  local base_ec; base_ec="$(run_pyfile "$GATE_PY" "$FR")"
  if [ "$base_ec" != "1" ]; then
    fail_case "MUTATION $label baseline(kill-fixture) → exit $base_ec (기대 1). 대조 무의미 — fixture 부정확."
    return
  fi
  local MD mut; MD="$(mktemp -d)"; CLEANUP_DIRS+=("$MD"); mut="$MD/mutant.py"
  cp "$GATE_PY" "$mut"
  if ! sed_neutralize "$mut" "$frm" "$to"; then
    fail_case "MUTATION $label — sed 미치환(branch 문자열 drift). NOT_RUN, false PASS 금지."
    return
  fi
  if ! py_valid "$mut"; then
    fail_case "MUTATION $label — mutated py invalid(py_compile 실패). NOT_RUN(double-guard b)."
    return
  fi
  local mut_ec; mut_ec="$(run_pyfile "$mut" "$FR")"
  if [ "$base_ec" = "1" ] && [ "$mut_ec" = "0" ]; then
    pass_case "MUTATION $label KILLED — baseline(kill-fixture)=exit1 → mutant=exit0 (분기 load-bearing)"
  else
    fail_case "MUTATION $label NOT KILLED — baseline=$base_ec mutant=$mut_ec (기대 1→0). non-discriminating/부정확."
  fi
}

# run_mutation_stdout <label> <green_builder> <frm> <to> <token> — M4: exit 불변, stdout token 소실로 KILL.
run_mutation_stdout() {
  local label="$1" builder="$2" frm="$3" to="$4" token="$5"
  log "── MUTATION $label (stdout nuance — trace-emit 축, exit-flip 아님) ──"
  local FG; FG="$(new_fixture)"; "$builder" "$FG"
  local base_out base_ec
  base_out="$( gate_stdout "$GATE_PY" "$FG" )"; base_ec=$?
  local base_has=0; printf '%s' "$base_out" | grep -qF "$token" && base_has=1
  if [ "$base_ec" != "0" ] || [ "$base_has" != "1" ]; then
    fail_case "MUTATION $label baseline — exit=$base_ec token('$token')present=$base_has (기대 exit0 + token). 대조 무의미."
    return
  fi
  local MD mut; MD="$(mktemp -d)"; CLEANUP_DIRS+=("$MD"); mut="$MD/mutant.py"
  cp "$GATE_PY" "$mut"
  if ! sed_neutralize "$mut" "$frm" "$to"; then
    fail_case "MUTATION $label — sed 미치환(branch drift). NOT_RUN."
    return
  fi
  if ! py_valid "$mut"; then
    fail_case "MUTATION $label — mutated py invalid. NOT_RUN(double-guard b)."
    return
  fi
  local mut_out mut_ec
  mut_out="$( gate_stdout "$mut" "$FG" )"; mut_ec=$?
  local mut_has=0; printf '%s' "$mut_out" | grep -qF "$token" && mut_has=1
  if [ "$mut_ec" = "0" ] && [ "$mut_has" = "0" ]; then
    pass_case "MUTATION $label KILLED(stdout) — baseline stdout has '$token' → mutant 소실 (exit 불변 0→0 = M4 trace 축)"
  else
    fail_case "MUTATION $label NOT KILLED — mutant exit=$mut_ec token_present=$mut_has (기대 exit0 + token 소실)."
  fi
}

# LIVE ceiling-honesty — 실 산출물(gate .py/.sh + concept doc + registry + ADR-154) grep.
#   ceiling 문구 존재 + affirmative over-claim(완전 봉인/universal detection) 부재(±1 denial-context 제외).
#   fixture-fallback 금지 — 실 파일 대상. ±1 window = gate _is_denial_context 의미 mirror(오탐 회피).
live_ceiling_honesty() {
  log "── LIVE ceiling-honesty (실 산출물 grep, fixture-fallback 금지) ──"
  local targets=( "$GATE_PY" "$GATE_WRAPPER" "$REPO_ROOT/$CONCEPT_REL" "$REGISTRY" "$ADR_154" )
  local existing=() t
  for t in "${targets[@]}"; do [ -f "$t" ] && existing+=("$t"); done
  if [ "${#existing[@]}" -eq 0 ]; then
    skip_case "LIVE ceiling — 실 산출물 대상 전부 부재 (NOT_RUN, false PASS 금지)"
    return
  fi
  local rc=0
  "$PY" - "${existing[@]}" <<'PYEOF' >&2 || rc=$?
import sys
files = sys.argv[1:]
OVERCLAIM = ("완전 봉인", "universal detection")
DENIAL = ("아님","아니다","않","없","금지","못","불가","부재","미주장","기각"," not ","never","reject","avoid","prohibit","no ")
CEILING = ("undecidable","정직 천장","honest-ceiling","honest ceiling","presence ≠ truth")
def denial_ctx(lines, i):
    for j in (i-1, i, i+1):
        if 0 <= j < len(lines) and any(m in lines[j] for m in DENIAL):
            return True
    return False
ceiling_present = False
hardclaims = []
for f in files:
    try:
        lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
    except OSError as e:
        print("READ-FAIL", f, e); sys.exit(2)
    text = "\n".join(lines)
    if any(c in text for c in CEILING):
        ceiling_present = True
    for i, ln in enumerate(lines):
        for oc in OVERCLAIM:
            if oc in ln and not denial_ctx(lines, i):
                hardclaims.append((f, i + 1, oc, ln.strip()[:90]))
if not ceiling_present:
    print("CEILING-ABSENT — 실 산출물 union 에 ceiling 문구 부재")
    sys.exit(1)
if hardclaims:
    for h in hardclaims:
        print("HARDCLAIM", h[0], "line", h[1], repr(h[2]), "::", h[3])
    sys.exit(1)
print("LIVE-CEILING-OK ceiling_present=1 affirmative_overclaim=0 (denial-context excluded)")
sys.exit(0)
PYEOF
  if [ "$rc" = "0" ]; then
    pass_case "LIVE ceiling-honesty — ceiling 문구 존재 + affirmative over-claim 부재 (부정-맥락 ±1 제외)"
  else
    fail_case "LIVE ceiling-honesty FAIL(rc=$rc) — ceiling 부재 또는 affirmative over-claim 검출 (위 HARDCLAIM 로그)"
  fi
}

# bijection cross-seal — 본 self-test 착륙으로 selftest-execution-liveness record↔file 짝 성립.
bijection_cross_seal() {
  log "── bijection cross-seal (selftest-execution-liveness 실 repo 통과) ──"
  local L_PY="$REPO_ROOT/scripts/lib/check_selftest_execution_liveness.py"
  local L_SH="$REPO_ROOT/scripts/check-selftest-execution-liveness.sh"
  if [ ! -f "$L_PY" ] && [ ! -f "$L_SH" ]; then
    skip_case "bijection cross-seal — selftest-execution-liveness 게이트 부재 (NOT_RUN)"
    return
  fi
  local out ec=0
  if [ -f "$L_SH" ]; then
    out="$( bash "$L_SH" --repo-root "$REPO_ROOT" 2>&1 )" || ec=$?
  else
    out="$( "$PY" "$L_PY" --repo-root "$REPO_ROOT" 2>&1 )" || ec=$?
  fi
  printf '%s\n' "$out" | sed 's/^/      liveness> /' >&2
  if [ "$ec" = "0" ]; then
    pass_case "bijection cross-seal — record↔file 짝 성립, selftest-execution-liveness exit0 (two-meta-gate mutual cross-seal)"
  else
    fail_case "bijection cross-seal — selftest-execution-liveness exit $ec (record↔file bijection 미해소 또는 타 결함; 로그 확인)"
  fi
}

test_ac7_self_application() {
  log ""; log "══ AC-7 self-application (born-hollow FORBIDDEN — TC-CLEAN-PASS + M1-M6 + LIVE + bijection) ══"
  # TC-CLEAN-PASS — valid 번들 + shallow observation → exit0 (L3 ceiling 미강제 실증).
  expect_exit "AC-7 TC-CLEAN-PASS (valid 번들 → exit0, L3 sufficiency 미강제)" 0 build_green
  # mutation M1-M6 positive-leak (M4 = stdout).
  run_mutation_exit   "M1 positive-control-presence" build_red_ac1        "$FROM_M1" "$TO_M1"
  run_mutation_exit   "M6 two-exit-shape"            build_red_ac2        "$FROM_M6" "$TO_M6"
  run_mutation_exit   "M5 identity-probe"            build_red_ac13       "$FROM_M5" "$TO_M5"
  run_mutation_exit   "M2 honest-degrade-exception"  build_red_ac6_exc    "$FROM_M2" "$TO_M2"
  run_mutation_exit   "M3 unknown-input(unreadable)" build_red_unreadable "$FROM_M3" "$TO_M3"
  run_mutation_stdout "M4 execution-trace(stdout)"   build_green          "$FROM_M4" "$TO_M4" "subject scanned"
  # LIVE ceiling-honesty + bijection cross-seal.
  live_ceiling_honesty
  bijection_cross_seal
}

# ═════════════════════════════════════════════════════════════════════════════
# 5b. PERF DoS-bound 회귀가드 (§7.3-self / §8.8.2 property — gate docstring proof-ref 결속)
# ═════════════════════════════════════════════════════════════════════════════
# build_perf_fixture <F> — valid GREEN 번들 + large-input 부하 subject:
#   (a) 단일 물리라인 > MAX_PHYSICAL_LINE_LEN(8192): 1.5MB 단일 라인(per-line truncate 부하)
#   (b) 총 라인 수 > PER_FILE_SCAN_CAP(5000): 20000 라인(islice count-cap 부하)
#   subject 는 valid(hgsv-enroll + positive-control + 2-exit shape) → 게이트 exit0(완료시간 측정 대상).
build_perf_fixture() {
  local F="$1"
  mkdir -p "$F/docs/domain-knowledge/concept" "$F/tests/scripts"
  emit_concept_doc green > "$F/$CONCEPT_REL"
  local subj="$F/tests/scripts/test_perf_subject.sh"
  {
    echo "#!/usr/bin/env bash"
    echo "# hgsv-enroll positive-control sanity mutant→RED (large-input DoS-bound fixture)"
    echo 'rc=$?'
    echo 'mrc=$?'
    echo 'if [ "$rc" -eq 0 ]; then echo clean-ok; fi'
    echo 'if [ "$mrc" -ne 0 ]; then echo mutant-red; fi'
  } > "$subj"
  # (a) 1.5MB 단일 물리라인(scan cap 내 위치 → truncate-scan 경로 부하). (b) 20000 filler 라인.
  "$PY" - "$subj" <<'PYEOF'
import sys
p = sys.argv[1]
with open(p, "a", encoding="utf-8") as f:
    f.write("# " + ("A" * 1500000) + "\n")                       # (a) >MAX_PHYSICAL_LINE_LEN
    f.write("\n".join("# filler scan line %d" % i for i in range(20000)) + "\n")  # (b) >PER_FILE_SCAN_CAP
PYEOF
}

# test_perf_dos_bound — large-input 에서 REAL 게이트 wall-clock 을 bound 이내 완료로 실측 반증.
#   islice count-cap + per-line truncate + anchored bounded regex(nested quantifier 0) → O(n²) 부재.
#   catastrophic backtracking 회귀 시(bound 제거) 이 test 가 timeout/초과로 RED (CFP-2635 1.5MB>60s 교훈).
test_perf_dos_bound() {
  log ""; log "══ PERF DoS-bound 회귀가드 (born-safe bound 실측 wall-clock) ══"
  local FP; FP="$(new_fixture)"; build_perf_fixture "$FP"
  local BOUND_S=5
  # REAL 게이트 core(py SSOT) 를 sys.executable 로 직접 측정 — PERF 축 = core 알고리즘 bound
  #   (islice/truncate/regex). thin wrapper(bash)는 wall-clock 복잡도 무기여 + Windows python subprocess
  #   가 'bash' PATH 해소 불가(FileNotFoundError) → py-path 로 측정 정합. python time.time precise 측정.
  local res
  res="$( "$PY" - "$GATE_PY" "$FP" <<'PYEOF'
import subprocess, sys, time
gate_py, fix = sys.argv[1], sys.argv[2]
cmd = [sys.executable, gate_py, "--repo-root", fix]
t = time.time()
try:
    # stdout/stderr = DEVNULL: 게이트 한글 UTF-8 출력을 non-UTF8 locale(Windows cp949)에서 decode 안 함
    # (text=True → UnicodeDecodeError). 측정 대상 = wall-clock + returncode 만.
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("%.3f %d" % (time.time() - t, r.returncode))
except Exception as e:
    print("ERR-%s -1" % type(e).__name__)   # 실패 시 rc=-1 → 아래 assert 가 FAIL(silent false-pass 금지)
PYEOF
)"
  local elapsed rc
  elapsed="${res%% *}"; rc="${res##* }"
  # bound assert: elapsed < BOUND_S (awk float 비교 — branch-guard capture, exit-masking 아님).
  local within=0
  awk -v e="$elapsed" -v b="$BOUND_S" 'BEGIN{exit !(e+0 < b+0)}' && within=1
  log "      PERF 측정: wall-clock=${elapsed}s / gate exit=${rc} / bound<${BOUND_S}s / within=${within}"
  if [ "$rc" = "0" ] && [ "$within" = "1" ]; then
    pass_case "PERF DoS-bound — large-input(1.5MB 단일라인 + 20000 라인) 게이트 ${elapsed}s < ${BOUND_S}s 완료 (islice count-cap + per-line truncate + anchored bounded regex, O(n²) catastrophic 부재 실측)"
  else
    fail_case "PERF DoS-bound — wall-clock=${elapsed}s exit=${rc} within=${within} (기대 exit0 + <${BOUND_S}s). catastrophic backtracking/미bound 회귀 의심."
  fi
  note "정직 천장: 본 완화는 총 작업량 bound(PER_FILE_SCAN_CAP × MAX_PHYSICAL_LINE_LEN)이지 임의 입력 무해 아님(bounded degradation, presence ≠ truth)."
}

# ═════════════════════════════════════════════════════════════════════════════
# 6. 실행 — NOT_RUN 가드 → 전 test → Summary
# ═════════════════════════════════════════════════════════════════════════════
if [ ! -f "$GATE_PY" ] && [ ! -f "$GATE_WRAPPER" ]; then
  echo "⊘ 메타-게이트 미착륙(check_hard_gate_self_verification.py/.sh 부재) — NOT_RUN, false PASS 금지."
  echo "  (게이트 없이 exit 0 반환 안 함.)"
  exit 1
fi

test_ac1_positive_control_present
test_ac2_two_exit_shape
test_ac3_empty_target_failclosed
test_ac4_unknown_input_failclosed
test_ac5_execution_trace_emit
test_ac6_three_way_taxonomy_present
test_ac8_honest_ceiling_present
test_ac12_crossref_nodup
test_ac13_identity_probe
test_ac7_self_application
test_perf_dos_bound

echo ""
echo "============================================================"
echo "Test Summary — CFP-2684 (ADR-154) hard-gate self-verification 메타-게이트 재귀 self-test"
echo "============================================================"
echo "PASS: $PASS / FAIL: $FAIL / SKIP: $SKIP / TOTAL ASSERT: $((PASS+FAIL))"
echo "천장(honest-ceiling): presence/shape/format/fail-closed 까지만 — 검출 sufficiency=undecidable(review-tier). presence ≠ truth."
echo ""
if [ "$FAIL" -eq 0 ] && [ "$PASS" -gt 0 ]; then
  echo "✓ 전 assert PASS + 전 discriminating pair(present≠absent) + M1-M6 positive-leak(M4=stdout) 성립"
  exit 0
else
  echo "✗ 하나 이상 FAIL/non-discriminating/NOT_RUN (FAIL=$FAIL, PASS=$PASS)"
  exit 1
fi
