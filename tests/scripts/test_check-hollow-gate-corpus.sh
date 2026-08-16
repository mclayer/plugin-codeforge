#!/usr/bin/env bash
# tests/scripts/test_check-hollow-gate-corpus.sh
# hgsv-enroll
# CFP-2963 / ADR-175 — hollow-gate corpus 판정 하네스(scripts/check-hollow-gate-corpus.sh →
#   scripts/lib/check_hollow_gate_corpus.py) 의 discriminating self-test.
#
# ── positive-control: sanity mutant→RED (결함 앞 RED 를 상시 증명) ────────────────────
#   본 self-test 는 매 실행마다 판정 core 의 **실 파일 사본**에 결함을 주입(MUTATION-SENTINEL
#   M1~M7, M3 은 2 site 개별)하고, 무변형 baseline 과 **다른 exit** 이 나오는지 대조한다.
#   예외 = M7: 대상 불변식이 정상 corpus 에서 발화하지 않아 무변형 baseline 으로는 대조군이
#   성립하지 않으므로 **2단 mutant**(정리 무력화 baseline → 불변식 추가 제거)를 쓴다. 사유는
#   해당 블록 주석에 기재한다 — 예외를 조용히 두지 않는다.
#   mutant 가 죽지 않으면(= baseline 과 같은 exit) 본 self-test 가 FAIL 한다. inline hand-copy
#   금지(ADR-082 §11.A tautology) — 실 core 파일 `cp` 대상만 sed 로 변형한다.
#   double-guard: (a) sed 가 실제로 치환했는지 sentinel grep 으로 확인 → 미치환 = NOT_RUN FAIL
#   (false PASS 금지) / (b) 변형본이 valid python(py_compile) 인지 확인.
#
# ── identity_bearing: true ─────────────────────────────────────────────────────────
#   internal-control identity probe = **known-answer 원문대조**. 하네스가 stdout 으로 emit 하는
#   `resolved-target: unit=s01 entry=gate.py sha256=<X>` 의 <X> 는, 커밋 파일
#   tests/fixtures/hollow-gate-corpus/s01/gate.py.sample 의 sha256 과 **문면 일치**해야 한다.
#   기대값은 하네스 출력이 아니라 sha256sum 으로 **독립 계산**한 known-answer 이며, 일치는
#   "판정기가 실제로 그 커밋 artifact 를 열어 실행했다"의 내부 대조 증거다(자기 출력 순환 인용 아님).
#
# ── ★NON-NEGOTIABLE 판정 기준 3건 (틀리면 정상 corpus 를 오판한다) ──────────────────
#   ① 「균일 = 하네스 사망」의 정의는 **"전 leg 동일"** 이지 *"전부 상이가 아님"* 이 아니다.
#      day-1 실측 8 leg 은 **4 distinct** 가 정상이다 — s01 kill / (s01 clean · s02 kill ·
#      s02 clean) / (s01 empty · s02 empty) / (s01 xkill · s02 xkill). `s02 kill ≡ s02 clean` 은
#      결함이 아니라 **arm-H 의 정의**(kill 에서도 GREEN)다. "전부 상이해야 한다"를 기준으로 삼으면
#      정상 corpus 를 사망으로 오판하므로 본 self-test 는 그 기준을 쓰지 않는다.
#   ② 판별자 = **마커 문면**이지 프로세스 rc 가 아니다. fail-marker = stderr `::error::[<STAGE>]`,
#      terminal-marker = stdout `✓ <gate>: …`. rc 는 I-4(선언 exit_space 이탈)에만 쓰인다.
#      본 self-test 는 verdict 를 rc 로 역추론하지 않고 하네스가 emit 한 `verdict:` 문면을 읽는다.
#   ③ mutation KILLED ⟺ **baseline(무변형)=기대 exit AND mutant=다른 exit**. 한쪽만 보면 무효.
#      exit-flip 이 아닌 축(M4 = stdout census 토큰 소실)은 별도 함수로 kill 하되, 거기서도
#      **한쪽만 보지 않는다** — stdout 축 KILLED ⟺ baseline token ≥1 ∧ mutant token 0 ∧
#      **양 팔 exit 을 실측해 둘 다 기대치** ∧ **양 팔 stderr Traceback 0건**. 프로세스가 대상
#      분기에 **닿기 전 죽어도** 토큰은 똑같이 사라지므로, crash mutant 를 걸러내지 않으면
#      「해당 분기 중화」와 「조기 사망」이 구별되지 않는다(축 귀속 붕괴). 그러므로 crash mutant 는
#      KILL 로 계상하지 않고 **무효(FAIL)** 로 떨어뜨린다. 무효 판정은 baseline 팔에도 대칭
#      배치한다 — 대조군이 이미 crash 중이면 대조 자체가 성립하지 않는다.
#      (F-CR20-8 봉합: 종전 라벨은 "exit 은 양쪽 $expect 로 불변" 을 **관측 없이 단정**했고,
#       실측 결과 crash mutant(rc=1)·rc-flip mutant(rc=9)가 모두 그 문면으로 초록 보고됐다.)
#
# ── 검사 대상 (READ-ONLY — 본 self-test 는 repo 실파일을 일절 수정하지 않는다) ────────
#   scripts/lib/check_hollow_gate_corpus.py        (core)
#   scripts/check-hollow-gate-corpus.sh            (thin wrapper — PINNED entry)
#   docs/hollow-gate-corpus-manifest.yaml          (좌표 SSOT)
#   docs/hollow-gate-corpus-baseline.yaml          (census baseline, content_digest 결박)
#   tests/fixtures/hollow-gate-corpus/{s01,s02}/** (2-arm 표본)
#   변형은 전부 mktemp -d 안 **shadow repo-root** 와 core 사본에서만 일어난다.
#
# ── 정직 천장 (ADR-175 / ADR-151 §결정7 / INV-5 상속) ───────────────────────────────
#   본 self-test 가 보장하는 것은 **등재 표본에 대한 관측 기반 판별력**까지다. corpus 밖 게이트
#   일반으로 외삽하지 않는다 — 미등재 게이트의 hollow 여부는 본 채널의 값공간 밖(미판정)이다.
#   presence ≠ truth 를 상속한다: 본 self-test 의 GREEN 은 "하네스가 주입된 결함 앞에서 RED 를
#   냈다"이지 "hollow 게이트가 더 이상 존재하지 않는다"가 아니다. 검출 sufficiency 는 undecidable.
#   (그래서 'universal' / '완전 봉인' / 'class 봉쇄' / '근절' 류 단정은 하지 않는다.)
#
# Exit code: 0 = 전 케이스 PASS ∧ PASS > 0 / 1 = 1건이라도 FAIL 또는 NOT_RUN (vacuous green 금지)

set -uo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# 0. Preamble — 경로 / 러너 / tally / cleanup
# ═══════════════════════════════════════════════════════════════════════════════
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CORE_PY="$REPO_ROOT/scripts/lib/check_hollow_gate_corpus.py"
WRAPPER="$REPO_ROOT/scripts/check-hollow-gate-corpus.sh"
MANIFEST="$REPO_ROOT/docs/hollow-gate-corpus-manifest.yaml"
BASELINE="$REPO_ROOT/docs/hollow-gate-corpus-baseline.yaml"
CORPUS_ROOT="$REPO_ROOT/tests/fixtures/hollow-gate-corpus"
GATE_SRC="$REPO_ROOT/scripts/lib/check_hard_gate_self_verification.py"

PASS=0
FAIL=0
SKIP=0

note() { echo "::notice::$*" >&2; }
log()  { echo "$*" >&2; }
pass_case() { echo "  ✓ PASS: $1"; PASS=$((PASS+1)); }
fail_case() { echo "  ✗ FAIL: $1"; FAIL=$((FAIL+1)); }
skip_case() { echo "  ⊘ SKIP: $1"; SKIP=$((SKIP+1)); }

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "✗ FAIL: python3/python 부재 — 하네스 실행 불가 (NOT_RUN, false PASS 금지)"
  exit 1
fi

TEST_TMP="$(mktemp -d)"
cleanup() { rm -rf "$TEST_TMP" 2>/dev/null; }
trap cleanup EXIT

# ── NOT_RUN 가드: 검사 대상 부재 = 무엇도 검증하지 못함 → 즉시 exit 1 (false PASS 금지) ──
missing=""
for f in "$CORE_PY" "$WRAPPER" "$MANIFEST" "$BASELINE" "$GATE_SRC"; do
  [ -f "$f" ] || missing="$missing $f"
done
[ -d "$CORPUS_ROOT/s01" ] || missing="$missing $CORPUS_ROOT/s01"
[ -d "$CORPUS_ROOT/s02" ] || missing="$missing $CORPUS_ROOT/s02"
if [ -n "$missing" ]; then
  echo "✗ FAIL: NOT_RUN — 검사 대상 부재:$missing"
  echo "        (대상 미착륙 상태에서 초록을 내지 않는다 — false PASS 금지)"
  exit 1
fi
if ! "$PY" -c "import yaml" >/dev/null 2>&1; then
  echo "✗ FAIL: NOT_RUN — pyyaml 부재. 하네스 판정 자체가 불가하므로 초록을 내지 않는다."
  exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 실행 helper — REAL exit code / REAL stdout·stderr 캡처
# ═══════════════════════════════════════════════════════════════════════════════
CORE_RC=0
CORE_OUT=""
CORE_ERR=""
RUN_SEQ=0

# run_core <py_path> <repo_root> [args...] — CORE_RC / CORE_OUT / CORE_ERR 설정.
run_core() {
  local py="$1" root="$2"; shift 2
  RUN_SEQ=$((RUN_SEQ+1))
  CORE_OUT="$TEST_TMP/run${RUN_SEQ}.out"
  CORE_ERR="$TEST_TMP/run${RUN_SEQ}.err"
  "$PY" "$py" --repo-root "$root" "$@" >"$CORE_OUT" 2>"$CORE_ERR"
  CORE_RC=$?
}

# run_wrapper <repo_root> [args...] — PINNED entry(thin bash wrapper) 경유.
run_wrapper() {
  local root="$1"; shift
  RUN_SEQ=$((RUN_SEQ+1))
  CORE_OUT="$TEST_TMP/run${RUN_SEQ}.out"
  CORE_ERR="$TEST_TMP/run${RUN_SEQ}.err"
  bash "$WRAPPER" --repo-root "$root" "$@" >"$CORE_OUT" 2>"$CORE_ERR"
  CORE_RC=$?
}

# verdict_of <unit> — 하네스가 emit 한 `verdict:` 문면에서 verdict 만 추출 (rc 역추론 금지).
verdict_of() {
  sed -n "s/^verdict: unit=$1 .*verdict=\([A-Z]*\) .*/\1/p" "$CORE_OUT" | head -1
}

# census_of <axis> — stdout `census: <axis>=<int>` 문면에서 값 추출.
census_of() {
  sed -n "s/^census: $1=\([0-9]*\)$/\1/p" "$CORE_OUT" | head -1
}

# ═══════════════════════════════════════════════════════════════════════════════
# 2. shadow repo-root 빌더 — repo 실파일 무오염 (변형은 전부 사본에서만)
# ═══════════════════════════════════════════════════════════════════════════════
# new_shadow [extra] — extra: none(기본) / s03(축 어긋난 신규 표본) / s04(오염 kill fixture)
#   corpus 하위 전 파일이 정확히 1개 samples[] 를 참조해야 하므로(bijection), shadow 에는 그
#   시나리오가 manifest 로 참조할 표본 디렉터리만 담는다.
new_shadow() {
  local extra="${1:-none}" d
  d="$(mktemp -d "$TEST_TMP/sh.XXXXXX")"
  mkdir -p "$d/docs" "$d/scripts/lib" "$d/tests/fixtures/hollow-gate-corpus"
  cp "$BASELINE" "$d/docs/hollow-gate-corpus-baseline.yaml"
  cp "$GATE_SRC" "$d/scripts/lib/"
  cp -r "$CORPUS_ROOT/s01" "$CORPUS_ROOT/s02" "$d/tests/fixtures/hollow-gate-corpus/"
  if [ "$extra" = "s03" ]; then
    cp -r "$CORPUS_ROOT/s01" "$d/tests/fixtures/hollow-gate-corpus/s03"
  fi
  if [ "$extra" = "s04" ]; then
    cp -r "$CORPUS_ROOT/s01" "$d/tests/fixtures/hollow-gate-corpus/s04"
    # 오염 = 목표 축(AC-1, kill 의 test_subject_good) + 타 축(AC-8, xkill 의 concept doc) 동시 발화.
    cp "$CORPUS_ROOT/s01/xkill/docs/domain-knowledge/concept/hard-gate-self-verification.md.sample" \
       "$d/tests/fixtures/hollow-gate-corpus/s04/kill/docs/domain-knowledge/concept/hard-gate-self-verification.md.sample"
  fi
  echo "$d"
}

# ── manifest emitter — 시나리오별 knob 은 MF_* 환경변수로 주입 (reset_mf 로 초기화) ──
MF_STAGE=""; MF_EXIT_SPACE=""; MF_EXTRA=""; MF_FLIP=""; MF_PROBE=""
MF_SAMPLES=""; MF_RECIPE_TARGET=""; MF_FORBIDDEN=""
reset_mf() {
  MF_STAGE="AC-1"; MF_EXIT_SPACE="[0, 1]"; MF_EXTRA="none"; MF_FLIP="0"; MF_PROBE="1"
  MF_SAMPLES="normal"; MF_RECIPE_TARGET="gate.py.sample"; MF_FORBIDDEN="0"
}
reset_mf

emit_manifest() {
  local out="$1"
  cat > "$out" <<YAML
schema_version: "1.0"
gates:
  - id: check-hard-gate-self-verification
    source_path: scripts/lib/check_hard_gate_self_verification.py
    entry: gate.py
    invoke_args: ["--repo-root", "{fixture}"]
    fail_marker_stream: stderr
    terminal_marker_stream: stdout
    fail_marker_stage_id: "$MF_STAGE"
    terminal_marker_prefix: "✓ check-hard-gate-self-verification:"
    exit_space: $MF_EXIT_SPACE
YAML
  if [ "$MF_SAMPLES" = "empty" ]; then
    printf 'samples: []\n' >> "$out"
  else
    cat >> "$out" <<'YAML'
samples:
  - id: s01
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/s01
    fixtures: { kill: kill, clean: clean, empty: empty, xkill: xkill }
  - id: s02
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/s02
    fixtures: { kill: kill, clean: clean, empty: empty, xkill: xkill }
YAML
    if [ "$MF_EXTRA" = "s03" ]; then
      # ★ 축 어긋남을 fixtures 매핑으로 만든다 — kill 자리에 xkill(AC-8 위반) 을 앉히면
      #   관측 stage 는 {AC-8, SUMMARY} 인데 선언 kill_target_stage 는 AC-1 이라 짝이 어긋난다.
      cat >> "$out" <<'YAML'
  - id: s03
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/s03
    fixtures: { kill: xkill, clean: clean, empty: empty, xkill: kill }
YAML
    fi
    if [ "$MF_EXTRA" = "s04" ]; then
      cat >> "$out" <<'YAML'
  - id: s04
    gate: check-hard-gate-self-verification
    path: tests/fixtures/hollow-gate-corpus/s04
    fixtures: { kill: kill, clean: clean, empty: empty, xkill: xkill }
YAML
    fi
  fi
  cat >> "$out" <<YAML
build:
  - sample: s02
    derived_from: s01
    target: $MF_RECIPE_TARGET
    anchor_from: "    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):"
    anchor_to: "    if False:  # neutralized M1 positive-control-presence"
YAML
  if [ "$MF_PROBE" = "1" ]; then
    cat >> "$out" <<'YAML'
  - probe: p01
    derived_from: s01
    target: gate.py.sample
    anchor_from: "    if not any(a in text for a in _POSITIVE_CONTROL_ANCHORS):"
    anchor_to: "    if False:  # neutralized M1 positive-control-presence"
YAML
  fi
  printf 'classification:\n' >> "$out"
  if [ "$MF_SAMPLES" != "empty" ]; then
    if [ "$MF_FLIP" = "1" ]; then
      printf '  - sample: s01\n    declared_arm: H\n    expected_verdict: HOLLOW\n' >> "$out"
      printf '  - sample: s02\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
    else
      printf '  - sample: s01\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
      printf '  - sample: s02\n    declared_arm: H\n    expected_verdict: HOLLOW\n' >> "$out"
    fi
    [ "$MF_EXTRA" = "s03" ] && printf '  - sample: s03\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
    [ "$MF_EXTRA" = "s04" ] && printf '  - sample: s04\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
  fi
  if [ "$MF_PROBE" = "1" ]; then
    if [ "$MF_FLIP" = "1" ]; then
      printf '  - probe: p01\n    declared_arm: L\n    expected_verdict: LIVE\n' >> "$out"
    else
      printf '  - probe: p01\n    declared_arm: H\n    expected_verdict: HOLLOW\n' >> "$out"
    fi
  fi
  if [ "$MF_FORBIDDEN" = "1" ]; then
    printf '\nwaiver: "판정 회피 키공간 — denylist 명명 3종 중 1"\n' >> "$out"
  fi
  return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# 3. mutation helper — 실 core 파일 사본만 변형 (double-guard)
# ═══════════════════════════════════════════════════════════════════════════════
# mutate_core <label> <sed_expr> <sentinel> — 성공 시 변형본 경로 echo, 실패 시 빈 문자열 + rc 1.
#   파일명은 순번으로만 만든다 (label 에 공백·수식기호가 들어가므로 경로에 쓰지 않는다).
MUT_SEQ=0
MUT_PATH=""
mutate_core() {
  local label="$1" expr="$2" sentinel="$3"
  MUT_SEQ=$((MUT_SEQ+1))
  local mut="$TEST_TMP/mut_${MUT_SEQ}.py"
  cp "$CORE_PY" "$mut"
  sed -i "$expr" "$mut"
  if ! grep -qF "$sentinel" "$mut"; then
    echo ""
    return 1
  fi
  if ! "$PY" -m py_compile "$mut" >/dev/null 2>&1; then
    echo ""
    return 1
  fi
  MUT_PATH="$mut"
  echo "$mut"
  return 0
}

# mutation_kill_exit <label> <sed_expr> <sentinel> <root> <expect_base_rc> [args...]
#   KILLED ⟺ baseline(무변형)=expect_base_rc AND mutant rc != baseline rc.
mutation_kill_exit() {
  local label="$1" expr="$2" sentinel="$3" root="$4" expect="$5"; shift 5
  local mut base_rc mut_rc
  run_core "$CORE_PY" "$root" "$@"
  base_rc=$CORE_RC
  if [ "$base_rc" -ne "$expect" ]; then
    fail_case "$label: baseline 기대 exit=$expect 인데 실제 $base_rc — 대조군 성립 불가(무효 kill)"
    return 1
  fi
  # ★ mutate_core 는 명령치환(서브셸)에서 돌므로 그 안의 전역 대입은 살아남지 않는다.
  #   변형본 경로는 반드시 여기(부모 셸)에서 MUT_PATH 로 옮긴다. (최초 실행에서 실측 검출된 함정.)
  mut="$(mutate_core "$label" "$expr" "$sentinel")"
  if [ -z "$mut" ]; then
    fail_case "$label: NOT_RUN — sed 미치환 또는 변형본 syntax invalid (false PASS 금지)"
    return 1
  fi
  MUT_PATH="$mut"
  run_core "$mut" "$root" "$@"
  mut_rc=$CORE_RC
  if [ "$mut_rc" -ne "$base_rc" ]; then
    pass_case "$label: KILLED (baseline exit=$base_rc → mutant exit=$mut_rc, 판별력 load-bearing)"
    return 0
  fi
  fail_case "$label: SURVIVED (baseline exit=$base_rc == mutant exit=$mut_rc — 해당 분기가 판별에 기여하지 않음)"
  return 1
}

# mutation_kill_stdout <label> <sed_expr> <sentinel> <root> <token> <expect_rc>
#   exit-flip 이 아닌 축 전용. KILLED ⟺ **양 팔 crash 0** ∧ **양 팔 exit=expect (실측)** ∧
#   baseline stdout token ≥1 ∧ mutant stdout token 0.
#
#   ★ crash mutant 무효 (F-CR20-8 봉합). 종전 구현은 `base_hit>=1 && mut_hit==0` 두 술어만
#     보면서 라벨로는 "exit 은 양쪽 $expect 로 불변" 을 단정했다 — mutant 팔의 rc 를 **한 번도
#     읽지 않은 채** 한 단정이라 관측 없는 발화였다. 토큰이 사라지는 원인은 두 가지다:
#       (i) 대상 분기가 중화됐다      = 우리가 재려는 판별력
#      (ii) 프로세스가 그 분기에 **닿기 전 죽었다** = 아무것도 재지 못한 무효 실행
#     둘을 구별할 신호가 없으면 (ii) 가 KILL 로 계상된다(축 귀속 붕괴). 그래서
#     **stderr Traceback = crash 신호**를 양 팔 대칭으로 보고, mutant 팔 exit 을 실측해
#     기대치와 대조한다. crash 또는 exit 이탈이면 pass_case 가 아니라 fail_case 다 —
#     무효 실행을 초록으로 세지 않는다(본 Story 의 "crash mutant 무효" 규율의 집행 지점).
#     실측 근거: 이 가드 없이 census emit 자리를 `raise` 로 바꾼 mutant(실제 rc=1·Traceback 1건)와
#     `sys.exit(9)` 로 바꾼 mutant(실제 rc=9)가 **둘 다** "exit 은 양쪽 0 로 불변" KILLED 로
#     초록 보고됐다. 라벨이 주장하던 명제가 거짓인데도 통과한 것이다.
mutation_kill_stdout() {
  local label="$1" expr="$2" sentinel="$3" root="$4" token="$5" expect="$6"
  local mut base_rc mut_rc base_hit mut_hit base_tb mut_tb
  local tb_mark="Traceback (most recent call last)"

  # ── baseline 팔 (대조군) — crash 가드를 대칭 배치한다(대조군이 죽어 있으면 대조 무의미) ──
  run_core "$CORE_PY" "$root"
  base_rc=$CORE_RC
  base_tb=$(grep -cF "$tb_mark" "$CORE_ERR")
  base_hit=$(grep -cF "$token" "$CORE_OUT")
  if [ "$base_tb" -ge 1 ]; then
    fail_case "$label: 무효 — baseline(무변형) stderr 에 Traceback ${base_tb}건 (exit=$base_rc). 대조군이 이미 crash 라 어떤 관측도 해당 분기로 귀속되지 않는다"
    sed 's/^/        base-stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  if [ "$base_rc" -ne "$expect" ]; then
    fail_case "$label: baseline 기대 exit=$expect 인데 실제 $base_rc — 대조군 성립 불가"
    return 1
  fi

  # ── mutant 팔 ──
  mut="$(mutate_core "$label" "$expr" "$sentinel")"
  if [ -z "$mut" ]; then
    fail_case "$label: NOT_RUN — sed 미치환 또는 변형본 syntax invalid (false PASS 금지)"
    return 1
  fi
  MUT_PATH="$mut"
  run_core "$mut" "$root"
  mut_rc=$CORE_RC
  mut_tb=$(grep -cF "$tb_mark" "$CORE_ERR")
  mut_hit=$(grep -cF "$token" "$CORE_OUT")

  # crash mutant = 무효 kill. 토큰 소실(hit=$mut_hit)을 「분기 중화」로 귀속할 수 없다.
  if [ "$mut_tb" -ge 1 ]; then
    fail_case "$label: 무효 kill — mutant stderr 에 Traceback ${mut_tb}건 (exit=$base_rc→$mut_rc, token hit=$base_hit→$mut_hit). 프로세스가 대상 분기 도달 전 사망했을 수 있어 토큰 소실을 판별력으로 계상하지 않는다"
    sed 's/^/        mut-stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  # exit 축 실측 단언 — 라벨이 주장하는 '불변' 을 관측으로 뒷받침한다(무관측 단정 금지).
  if [ "$mut_rc" -ne "$expect" ]; then
    fail_case "$label: 무효 kill — mutant exit=$mut_rc (기대 $expect · baseline=$base_rc). exit 축이 함께 흔들리면 토큰 소실을 stdout 축 단독 판별로 귀속할 수 없다"
    return 1
  fi

  if [ "$base_hit" -ge 1 ] && [ "$mut_hit" -eq 0 ]; then
    pass_case "$label: KILLED (stdout 축 — baseline '$token' ${base_hit}건 → mutant ${mut_hit}건 / exit=$base_rc→$mut_rc 실측 불변 · Traceback base=${base_tb}건 mut=${mut_tb}건)"
    return 0
  fi
  fail_case "$label: SURVIVED (baseline hit=$base_hit / mutant hit=$mut_hit · exit=$base_rc→$mut_rc 실측 — stdout 토큰 소실 미관측)"
  return 1
}

# expect_exit <label> <expected_rc> <actual_rc> [stderr_grep_token]
expect_exit() {
  local label="$1" want="$2" got="$3" token="${4:-}"
  if [ "$got" -ne "$want" ]; then
    fail_case "$label: exit=$got (기대 $want)"
    sed 's/^/        stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  if [ -n "$token" ] && ! grep -qF "$token" "$CORE_ERR"; then
    fail_case "$label: exit=$got 은 맞으나 stderr 에 '$token' 미관측 (다른 사유로 우연히 같은 exit)"
    sed 's/^/        stderr> /' "$CORE_ERR" >&2
    return 1
  fi
  pass_case "$label: exit=$got${token:+ + stderr '$token' 관측}"
  return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# 4. T-1 양방향 — 정방향(무변형 PASS) ↔ 역방향(축 어긋난 fixture 는 여전히 RED)
#    ★ ⓐ 만으로는 "고쳐서 통과"와 "판별력을 죽여서 통과"를 구별할 수 없다. ⓑ 가 필수다.
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── T-1 양방향 (정방향 PASS ↔ 역방향 RED) ─────────────────────────────────────"

# ── T-1ⓐ 정방향: 무변형 corpus → exit 0 (PINNED entry = thin wrapper 경유) ──
bash "$WRAPPER" >"$TEST_TMP/t1a.out" 2>"$TEST_TMP/t1a.err"; clean_rc=$?
if [ "$clean_rc" -eq 0 ]; then
  pass_case "T-1ⓐ 정방향: 무변형 corpus → wrapper exit=0"
else
  fail_case "T-1ⓐ 정방향: clean corpus must PASS — wrapper exit=$clean_rc"
  sed 's/^/        stderr> /' "$TEST_TMP/t1a.err" >&2
fi

CORE_OUT="$TEST_TMP/t1a.out"
CORE_ERR="$TEST_TMP/t1a.err"
t1a_ind="$(census_of N_indeterminate)"
if [ "$t1a_ind" = "0" ]; then
  pass_case "T-1ⓐ: N_indeterminate=0 (판정불가 표본 0 — 상한 축 충족)"
else
  fail_case "T-1ⓐ: N_indeterminate='$t1a_ind' (기대 0)"
fi

# ★ 판별자 = 마커 문면 (rc 역추론 아님) — 하네스가 emit 한 verdict: 라인을 직접 읽는다.
for pair in "s01:LIVE" "s02:HOLLOW" "p01:HOLLOW"; do
  unit="${pair%%:*}"; want="${pair##*:}"
  got="$(verdict_of "$unit")"
  if [ "$got" = "$want" ]; then
    pass_case "T-1ⓐ verdict: $unit=$want (마커 문면 판정 — 프로세스 rc 역추론 아님)"
  else
    fail_case "T-1ⓐ verdict: $unit='$got' (기대 $want)"
  fi
done

# ── T-1ⓑ 역방향: 축이 어긋난(=자동 적중하는) stage 선언은 여전히 RED ──
#   SUMMARY 는 상수 footer 라 kill·xkill 양쪽 fail_stage 에 상주해 자동 적중한다 = 공허 선언.
#   ★ 이 어긋남을 잡는 **유일 검출자는 xkill 축-disjoint 검사**다 — verdict(LIVE/HOLLOW/HOLLOW)·
#   IC-1/2/5/6·census·baseline 은 전부 정상 통과한다. 그래서 M6 가 load-bearing 이다.
MUT_MANIFEST="$TEST_TMP/manifest_summary_stage.yaml"
reset_mf; MF_STAGE="SUMMARY"; emit_manifest "$MUT_MANIFEST"
bash "$WRAPPER" --manifest "$MUT_MANIFEST" >"$TEST_TMP/t1b.out" 2>"$TEST_TMP/t1b.err"; mutant_rc=$?
if [ "$mutant_rc" -ne 0 ]; then
  pass_case "T-1ⓑ 역방향: mutant corpus must FAIL — wrapper exit=$mutant_rc"
else
  fail_case "T-1ⓑ 역방향: 축 어긋난 stage 선언이 통과함 (판별력 사망 — exit=$mutant_rc)"
fi
CORE_OUT="$TEST_TMP/t1b.out"
CORE_ERR="$TEST_TMP/t1b.err"
if grep -qF "::error::[XKILL-AXIS]" "$TEST_TMP/t1b.err"; then
  pass_case "T-1ⓑ: stderr 에 ::error::[XKILL-AXIS] 관측 (자동 적중 = 공허 선언 검출)"
else
  fail_case "T-1ⓑ: exit 은 non-zero 이나 XKILL-AXIS 마커 미관측 (다른 사유로 우연히 RED)"
  sed 's/^/        stderr> /' "$TEST_TMP/t1b.err" >&2
fi
# ★ 유일 검출자 실증: T-1ⓑ 에서 verdict·census 축은 **정상 통과**한다.
if [ "$(verdict_of s01)" = "LIVE" ] && [ "$(verdict_of s02)" = "HOLLOW" ] && [ "$(census_of N_indeterminate)" = "0" ]; then
  pass_case "T-1ⓑ: verdict·N_indeterminate 축은 정상 통과 — xkill 축-disjoint 가 유일 검출자임을 실증"
else
  fail_case "T-1ⓑ: verdict/census 축 관측이 기대와 다름 (유일-검출자 실증 전제 파손)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 5. identity probe — known-answer 원문대조 (internal control)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── identity probe (known-answer 원문대조) ────────────────────────────────────"
known_sha="$("$PY" -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" \
             "$CORPUS_ROOT/s01/gate.py.sample")"
emitted_sha="$(sed -n 's/^resolved-target: unit=s01 entry=gate.py sha256=\([0-9a-f]*\)$/\1/p' "$TEST_TMP/t1a.out" | head -1)"
if [ -n "$known_sha" ] && [ "$known_sha" = "$emitted_sha" ]; then
  pass_case "identity probe: resolved-target sha256 == 커밋 s01/gate.py.sample sha256 (독립 계산 known-answer 일치)"
else
  fail_case "identity probe: known=$known_sha emitted=$emitted_sha 불일치 — 판정기가 연 artifact 가 커밋 표본이 아님"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 6. MUTATION-SENTINEL 7축 (M3 은 2 site 개별 mutant / M7 은 2단 mutant)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── MUTATION-SENTINEL 7축 (M3 = 2 site 개별 / M7 = 2단 mutant) ───────────────"

# M1 = I-8 협착 conjunct (kill.fail=1). 중화 시 arm-H(fail_stage=∅)에서 공허 참 → 정상 HOLLOW 전멸.
#   ★ 이 conjunct 는 본 Story 가 실제로 겪은 born-RED 의 봉합점이다.
mutation_kill_exit "M1 (I-8 협착 conjunct)" \
  's/    if bundle.kill.fail and kill_target_stage not in bundle.kill.fail_stages:/    if kill_target_stage not in bundle.kill.fail_stages:  # M1-neutralized/' \
  "M1-neutralized" "$REPO_ROOT" 0

# M2 = I-11 ¬LIVE ∧ ¬HOLLOW 가드. 중화 시 arm-H(kill 관측 ≡ clean 관측 = arm-H 의 정의)가 전멸.
mutation_kill_exit "M2 (I-11 ¬LIVE∧¬HOLLOW 가드)" \
  's/    if (not live) and (not hollow) and (bundle.kill.observed == bundle.clean.observed):/    if (bundle.kill.observed == bundle.clean.observed):  # M2-neutralized/' \
  "M2-neutralized" "$REPO_ROOT" 0

# M3 = exit_space 검사 — ★ 2 site. 각각 독립 mutant 로 돌려 각 site 가 load-bearing 임을 분리 확인.
#   site A = 선언검사(T-2ⓐ loud 실패, _validate_manifest) / site B = 런타임 I-4 (rc ∉ exit_space).
ES_EMPTY="$TEST_TMP/manifest_exit_space_empty.yaml"
reset_mf; MF_EXIT_SPACE="[]"; emit_manifest "$ES_EMPTY"
ES_NARROW="$TEST_TMP/manifest_exit_space_narrow.yaml"
reset_mf; MF_EXIT_SPACE="[0]"; emit_manifest "$ES_NARROW"
SH_M3="$(new_shadow none)"

mutation_kill_exit "M3-siteA (exit_space 선언검사 · T-2ⓐ loud 실패)" \
  's/        if not isinstance(es, list) or len(es) == 0:/        if False:  # M3a-neutralized/' \
  "M3a-neutralized" "$SH_M3" 3 --manifest "$ES_EMPTY"

mutation_kill_exit "M3-siteB (런타임 I-4 · rc ∉ exit_space)" \
  's/                    if rc not in gate\["exit_space"\]:/                    if False:  # M3b-neutralized/' \
  "M3b-neutralized" "$SH_M3" 1 --manifest "$ES_NARROW"

# ★ site 독립성: siteB 만 중화해도 siteA 는 살아있어야 한다 (한 번에 둘 다 지우면 분리 불가).
mut_m3b="$MUT_PATH"
if [ -n "$mut_m3b" ] && [ -f "$mut_m3b" ]; then
  run_core "$mut_m3b" "$SH_M3" --manifest "$ES_EMPTY"
  expect_exit "M3 site 독립성: siteB 중화본도 빈 exit_space 는 여전히 loud 실패" 3 "$CORE_RC" "T-2ⓐ loud 실패"
else
  fail_case "M3 site 독립성: siteB 변형본 부재 (NOT_RUN)"
fi

# M4 = census 개별 emit (7축). exit-flip 아님 → stdout 토큰 소실로 kill.
mutation_kill_stdout "M4 (census 축별 개별 emit)" \
  's/        _emit(f"census: {a}={census\[a\]}")/        pass  # M4-neutralized/' \
  "M4-neutralized" "$REPO_ROOT" "census: N_armL=" 0

# M5 = IC-4 exec-tree blinding assert. 오염 shadow(fixture 안에 stamp 잠입)로 baseline=3 을 만든 뒤 중화.
SH_M5="$(new_shadow none)"
# s01·s02 양쪽에 동일하게 주입 (한쪽에만 넣으면 provenance 검사가 트리 동일성 파손으로 먼저 발화)
echo "leaked-arm-signal" > "$SH_M5/tests/fixtures/hollow-gate-corpus/s01/kill/stamp_leak.txt"
echo "leaked-arm-signal" > "$SH_M5/tests/fixtures/hollow-gate-corpus/s02/kill/stamp_leak.txt"
MF_M5="$TEST_TMP/manifest_m5.yaml"; reset_mf; emit_manifest "$MF_M5"
mutation_kill_exit "M5 (IC-4 exec-tree blinding assert)" \
  's/                        bad = _blinding_violations(unit_dir, exec_root)/                        bad = []  # M5-neutralized/' \
  "M5-neutralized" "$SH_M5" 3 --manifest "$MF_M5"

# M6 = xkill 축-disjoint 검사. 중화 시 §4 T-1ⓑ 가 통과해버린다 = 판별력 사망.
mutation_kill_exit "M6 (xkill 축-disjoint 검사)" \
  's/                if tgt in legs\["xkill"\].fail_stages:/                if False:  # M6-neutralized/' \
  "M6-neutralized" "$REPO_ROOT" 1 --manifest "$MUT_MANIFEST"

# M7 = 형제 부재 불변식 (F-CR18-9 실행 순번 누설 채널 가드).
# ★ 2단 mutant 인 이유 (정직 기재): 이 불변식은 정상 corpus 에서 **절대 발화하지 않는다** —
#   leg 별 즉시 정리가 선행해 exec_root 직속 dir 수가 항상 1 이기 때문이다. 그래서 무변형
#   core 를 baseline 으로 잡으면 baseline exit=0 이라 대조군이 성립하지 않고(무효 kill),
#   `mutation_kill_exit` 를 그대로 쓸 수 없다. 정리를 먼저 무력화해 **불변식이 실제로
#   발화하는 상태**를 baseline 으로 만든 뒤 거기서 불변식만 더 제거한다:
#     baseline (정리만 무력화)       = 형제 누적 → 불변식 발화 → exit 3
#     mutant   (정리 + 불변식 무력화) = 무성 통과              → exit 0
#   mutant 상태가 곧 구현리뷰 iter1 P1 결함(자식이 형제 수로 실행 순번을 역산하는 채널)의
#   **원상복원**이며, 그 앞에서 RED 를 내는 것이 본 케이스의 판별력이다.
#   KILLED 판정은 exit flip 만으로 하지 않는다 — baseline stderr 에 **관측된 형제 개수 문면**이
#   있는지까지 확인해, exit 3 이 다른 substrate 사유로 난 경우를 대조군 실패로 떨어뜨린다.
SH_M7="$(new_shadow none)"
MF_M7="$TEST_TMP/manifest_m7.yaml"; reset_mf; emit_manifest "$MF_M7"
M7_SED_CLEANUP='s/^                        shutil.rmtree(unit_dir, ignore_errors=True)$/                        pass  # M7-cleanup-off/'
M7_SED_INVARIANT='s/^    if len(siblings) != 1:$/    if False:  # M7-sibling-invariant-off/'
m7_base="$(mutate_core "M7 baseline" "$M7_SED_CLEANUP" "M7-cleanup-off")"
# ★ 실측 함정 (본 케이스 작성 중 재현): mutate_core 는 명령치환(서브셸)에서 돌아 MUT_SEQ 증가가
#   부모에 남지 않는다 → 연속 2회 호출이 **같은 파일명**을 쓰고 두 번째가 첫 번째를 덮어쓴다.
#   그러면 baseline 이 mutant 와 동일해져 baseline exit=0 이 나오고 "대조군 성립 불가" 로 착지한다
#   (파일 상단이 경고한 그 함정의 2차 발현). 두 번째 호출 전에 baseline 을 별 경로로 확보한다.
if [ -n "$m7_base" ]; then cp "$m7_base" "$TEST_TMP/m7_base.py"; m7_base="$TEST_TMP/m7_base.py"; fi
m7_mut="$(mutate_core "M7 mutant" "$M7_SED_CLEANUP; $M7_SED_INVARIANT" "M7-sibling-invariant-off")"
if [ -z "$m7_base" ] || [ -z "$m7_mut" ]; then
  fail_case "M7 (형제 부재 불변식): NOT_RUN — sed 미치환 또는 변형본 syntax invalid (false PASS 금지)"
elif grep -qF "M7-sibling-invariant-off" "$m7_base"; then
  # baseline 에 mutant 처치가 섞이면 두 군의 차이가 사라져 대조 자체가 무의미해진다.
  fail_case "M7 (형제 부재 불변식): baseline 오염 — baseline 에 불변식 제거 처치가 섞였다(대조군 무효)"
else
  run_core "$m7_base" "$SH_M7" --manifest "$MF_M7"; m7_base_rc=$CORE_RC
  m7_base_hit=$(grep -cF "exec-root 직속 디렉터리 2개" "$CORE_ERR")
  run_core "$m7_mut" "$SH_M7" --manifest "$MF_M7"; m7_mut_rc=$CORE_RC
  if [ "$m7_base_rc" -ne 3 ] || [ "$m7_base_hit" -lt 1 ]; then
    fail_case "M7 (형제 부재 불변식): 대조군 성립 불가 — 정리 무력화 baseline exit=$m7_base_rc (기대 3) / '형제 2개' 문면 ${m7_base_hit}건 (기대 ≥1). 무효 kill 금지"
  elif [ "$m7_mut_rc" -eq "$m7_base_rc" ]; then
    fail_case "M7 (형제 부재 불변식): SURVIVED (baseline exit=$m7_base_rc == mutant exit=$m7_mut_rc — 불변식이 판별에 기여하지 않음 = 실행 순번 누설 채널 무방비)"
  else
    pass_case "M7 (형제 부재 불변식): KILLED (정리 무력화 baseline exit=$m7_base_rc + '형제 2개' 관측 ${m7_base_hit}건 → 불변식 제거 mutant exit=$m7_mut_rc)"
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 7. substrate-failure (exit 3) 조건
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── substrate-failure (exit 3) 조건 ──────────────────────────────────────────"

# ⓵-a 분모 0 — probe 축 제거 (N_probe=0). ★ zero-count 분기 그 자체를 친다.
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_zero_probe.yaml"
reset_mf; MF_PROBE="0"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓵-a 분모 0 (N_probe=0)" 3 "$CORE_RC" "분모 0 축"

# ⓵-b samples[] 비움 — manifest shape 층에서 loud 실패.
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_samples_empty.yaml"
reset_mf; MF_SAMPLES="empty"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓵-b samples[] 비움" 3 "$CORE_RC" "블록 'samples' 이 비어있거나"

# ⓶-a baseline 부재
SH="$(new_shadow none)"; rm -f "$SH/docs/hollow-gate-corpus-baseline.yaml"
MF="$TEST_TMP/mf_nobase.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓶-a baseline 부재" 3 "$CORE_RC" "baseline 부재"

# ⓶-b baseline digest 변조 (수기 편집 검출 — content_digest 결박)
SH="$(new_shadow none)"
sed -i 's/^  N_detected: 2$/  N_detected: 1/' "$SH/docs/hollow-gate-corpus-baseline.yaml"
MF="$TEST_TMP/mf_digest.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓶-b baseline digest 변조(수기 편집)" 3 "$CORE_RC" "content_digest 불일치"

# ⓷ stamp drift — source_sha256 변조
SH="$(new_shadow none)"
sed -i 's/^source_sha256: .*/source_sha256: "0000000000000000000000000000000000000000000000000000000000000000"/' \
  "$SH/tests/fixtures/hollow-gate-corpus/s01/stamp.yaml.sample"
MF="$TEST_TMP/mf_stamp.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓷ stamp drift (source_sha256 변조)" 3 "$CORE_RC" "source_sha256 drift"

# ⓸ bijection orphan — corpus 파일이 samples[] 참조 0
SH="$(new_shadow none)"; echo "orphan" > "$SH/tests/fixtures/hollow-gate-corpus/s01/orphan.txt"
MF="$TEST_TMP/mf_orphan.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓸ bijection orphan" 3 "$CORE_RC" "samples[] 참조 0개"

# ⓹ exec-tree blinding 파손 — fixture 안에 stamp 잠입 (IC-4)
# s01·s02 양쪽에 동일하게 주입 (한쪽에만 넣으면 provenance 검사가 트리 동일성 파손으로 먼저 발화)
SH="$(new_shadow none)"
echo "leak" > "$SH/tests/fixtures/hollow-gate-corpus/s01/clean/stamp_probe_leak.txt"
echo "leak" > "$SH/tests/fixtures/hollow-gate-corpus/s02/clean/stamp_probe_leak.txt"
MF="$TEST_TMP/mf_blind.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓹ exec-tree blinding 파손 (stamp 잠입)" 3 "$CORE_RC" "exec-tree blinding 파손"

# ⓺ recipe 대상이 samples[] 밖
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_recipe_out.yaml"
reset_mf; MF_RECIPE_TARGET="../s02/gate.py.sample"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 ⓺ recipe target 이 samples[] 밖" 3 "$CORE_RC" "samples[] 밖"

# 추가-a exit_space 빈 리스트 (T-2ⓐ — 조용한 INDETERMINATE 아니라 loud 실패)
SH="$(new_shadow none)"
run_core "$CORE_PY" "$SH" --manifest "$ES_EMPTY"
expect_exit "exit3 추가-a exit_space 빈 리스트 (T-2ⓐ loud)" 3 "$CORE_RC" "T-2ⓐ loud 실패"

# 추가-b 금지키 (denylist 명명 3종) 주입
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_forbidden.yaml"
reset_mf; MF_FORBIDDEN="1"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
expect_exit "exit3 추가-b manifest 금지키(waiver)" 3 "$CORE_RC" "금지키 사용"

# ═══════════════════════════════════════════════════════════════════════════════
# 8. T-2 exit_space 3분기
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── T-2 exit_space ───────────────────────────────────────────────────────────"
# ⓐ 빈 리스트 = exit 3 (위 추가-a 에서 확인 — 여기서는 "조용한 INDETERMINATE 아님"을 추가 확인)
#   ★ 판정 술어 주의: "I-4" 문자열 부재로 검사하면 안 된다 — SUBSTRATE 메시지 본문이 *왜* loud
#   실패시키는지 설명하며 'I-4' 를 인용하기 때문이다(설명 문면 ≠ 라벨 발동). 실제 발동 여부는
#   `::error::[INDETERMINATE]` stage 라벨의 유무로만 읽는다. (이 오판은 최초 실행에서 실측 검출됐다.)
SH="$(new_shadow none)"
run_core "$CORE_PY" "$SH" --manifest "$ES_EMPTY"
if [ "$CORE_RC" -eq 3 ] && grep -qF "::error::[SUBSTRATE]" "$CORE_ERR" \
   && ! grep -qF "::error::[INDETERMINATE]" "$CORE_ERR"; then
  pass_case "T-2ⓐ: 빈 exit_space = loud exit 3 (SUBSTRATE 라벨 · INDETERMINATE 라벨 0 — 조용한 흐름 경로 미형성)"
else
  fail_case "T-2ⓐ: exit=$CORE_RC 또는 INDETERMINATE 라벨 출현 — loud 실패 계약 파손"
  sed 's/^/        stderr> /' "$CORE_ERR" >&2
fi

# ⓑ [0,1] 정상 → exit 0 ∧ I-4 미발동
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_es_normal.yaml"; reset_mf; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
if [ "$CORE_RC" -eq 0 ] && ! grep -qF "::error::[INDETERMINATE]" "$CORE_ERR"; then
  pass_case "T-2ⓑ: exit_space [0,1] → exit 0, I-4 미발동 (day-1 실측 rc kill=1/clean=0/empty=0/xkill=1 전건 포함)"
else
  fail_case "T-2ⓑ: exit=$CORE_RC 또는 I-4 발동 — 정상 exit_space 에서 오검출"
fi

# ⓒ [0] 으로 좁힘 → kill leg rc=1 이 I-4 발동 → exit 1
SH="$(new_shadow none)"
run_core "$CORE_PY" "$SH" --manifest "$ES_NARROW"
expect_exit "T-2ⓒ: exit_space [0] 으로 좁힘 → I-4 발동" 1 "$CORE_RC" "∉ 선언 exit_space"

# ═══════════════════════════════════════════════════════════════════════════════
# 9. T-4 post-day-1 편입 시뮬레이션 — 축 짝짓기가 어긋난 신규 표본은 RED 인가
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── T-4 post-day-1 편입 (축 어긋난 신규 표본) ────────────────────────────────"
# day-1 이후 새 표본 s03 이 편입되되, kill 자리에 AC-8 축 fixture(xkill)를 앉혀 축 짝짓기를 어긋나게 한다.
# 선언 kill_target_stage 는 AC-1 인데 관측 stage 는 {AC-8, SUMMARY} 이므로 짝이 맞지 않는다.
SH="$(new_shadow s03)"; MF="$TEST_TMP/mf_t4.yaml"
reset_mf; MF_EXTRA="s03"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
if [ "$CORE_RC" -eq 1 ]; then
  pass_case "T-4: 축 어긋난 신규 표본 편입 → exit 1 (RED)"
else
  fail_case "T-4: 축 어긋난 신규 표본이 exit=$CORE_RC — 강제 게이트가 RED 를 내지 않음"
fi
t4_hits=0
grep -qF "unit=s03: I-8 성립" "$CORE_ERR" && t4_hits=$((t4_hits+1))
grep -qF "::error::[XKILL-AXIS] unit=s03" "$CORE_ERR" && t4_hits=$((t4_hits+1))
grep -qF "::error::[VERDICT] unit=s03" "$CORE_ERR" && t4_hits=$((t4_hits+1))
if [ "$t4_hits" -eq 3 ]; then
  pass_case "T-4: 3중 검출 (I-8 강등 + XKILL-AXIS 축 파손 + VERDICT reconcile 불일치)"
else
  fail_case "T-4: 검출 신호 ${t4_hits}/3 — 기대 3중 검출 미달"
  sed 's/^/        stderr> /' "$CORE_ERR" >&2
fi
# ★ 정직 천장 (실측 결과에 딸린 잔여): 위 RED 는 **선언 kill_target_stage 와 관측 stage 의 불일치**를
#   잡은 것이지 "새 표본의 kill 축이 그 게이트를 대표하는가"(축 대표성)를 잡은 것이 아니다. 축 대표성은
#   사람 판단이며 bearer 는 문서 규약뿐이다 — 기계 강제 없음. 통과를 만들려고 검사를 약화시키지 않는다.

# ═══════════════════════════════════════════════════════════════════════════════
# 10. T-6 fixture 순도 가드 — 목표 축 + 타 축 동시 발화 시 의도한 착지 확정
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── T-6 fixture 순도 (오염 fixture 의 의도한 착지) ───────────────────────────"
# 오염 fixture = s04 의 kill 이 목표 축(AC-1)과 타 축(AC-8)을 **동시** 발화 → stages={AC-1,AC-8,SUMMARY}.
#
# ★ 의도한 착지 = **LIVE 허용 (RED 아님)**. 근거를 여기에 기재한다:
#   판정식의 conjunct 는 `kill_target_stage ∈ fail_stage(kill)` 즉 **멤버십**이지 배타성이 아니다
#   (ADR-175 DR4-M1 — 한 leg 이 내는 stage id 개수는 고정이 아니며 상수 footer 와 공존한다).
#   따라서 "목표 축이 실제로 적중했다"는 요구는 그대로 살아있고, 타 축이 함께 울렸다는 사실만으로는
#   RED 로 만들지 않는다. 배타성을 요구하도록 좁히면 day-1 정상 표본(AC-1 + SUMMARY 상수 footer 공존)이
#   즉시 born-RED 가 된다 — 정상 corpus 오판.
#   ⇒ 순도(축이 하나만 울릴 것)는 **기계 강제 대상이 아니고** 표본 제작 규약이 진다. 이 잔여는
#     하네스 docstring 의 game-able residual (a) 축 대표성 = 사람 판단 과 같은 뿌리다.
SH="$(new_shadow s04)"; MF="$TEST_TMP/mf_t6.yaml"
reset_mf; MF_EXTRA="s04"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
s04_stages="$(sed -n 's/^obs-digest: unit=s04 leg=kill .*stages=\(\[[^]]*\]\).*/\1/p' "$CORE_OUT" | head -1)"
if [ "$CORE_RC" -eq 0 ] && [ "$(verdict_of s04)" = "LIVE" ]; then
  pass_case "T-6: 오염 fixture(stages=$s04_stages) → 의도한 착지 LIVE 허용 (멤버십 판정, 배타성 미요구)"
else
  fail_case "T-6: exit=$CORE_RC verdict=$(verdict_of s04) — 문서화한 의도 착지(LIVE 허용)와 불일치"
  sed 's/^/        stderr> /' "$CORE_ERR" >&2
fi
if echo "$s04_stages" | grep -qF "AC-1" && echo "$s04_stages" | grep -qF "AC-8"; then
  pass_case "T-6: 오염이 실제로 2축 동시 발화했음을 관측 (stages=$s04_stages — 무의미 fixture 아님)"
else
  fail_case "T-6: stages=$s04_stages — 2축 동시 발화 미관측 (오염 fixture 제작 실패, 검사 전제 파손)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 11. IC-4 exec-tree blinding + exec dir 재배정
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── IC-4 exec-tree blinding / exec dir 재배정 ────────────────────────────────"
# 배경: stamp.yaml.sample 의 source_sha256 == artifact_sha256 여부가 arm 과 1:1 상관이다
#   (s01 참 / s02 거짓). stamp 가 exec dir 로 새면 라벨 역산 채널이 된다 — IC-4 가 그것을 닫는다.
#   exec dir 은 실행 종료 시 삭제되므로, 여기서는 (a) 누설 시 loud 실패하는가 (b) 이름이 매 실행
#   재배정되는가 로 관측한다. exec tree 표면의 직접 assert 는 형제 pytest self-test 가
#   _materialize 를 in-process 로 불러 수행한다 (tests/scripts/test_check_hollow_gate_corpus.py).
for tok in stamp manifest baseline probe; do
  SH="$(new_shadow none)"
  # s01·s02 양쪽에 동일하게 주입 (한쪽에만 넣으면 provenance 검사가 트리 동일성 파손으로 먼저 발화)
  echo "leak" > "$SH/tests/fixtures/hollow-gate-corpus/s01/clean/${tok}_leak.txt"
  echo "leak" > "$SH/tests/fixtures/hollow-gate-corpus/s02/clean/${tok}_leak.txt"
  MF="$TEST_TMP/mf_blind_${tok}.yaml"; reset_mf; emit_manifest "$MF"
  run_core "$CORE_PY" "$SH" --manifest "$MF"
  if [ "$CORE_RC" -eq 3 ] && grep -qF "금지 토큰 '${tok}'" "$CORE_ERR"; then
    pass_case "IC-4 blinding: exec dir 에 '${tok}' 토큰 누설 → exit 3 (라벨 역산 채널 차단)"
  else
    fail_case "IC-4 blinding: '${tok}' 누설이 exit=$CORE_RC 로 통과 (역산 채널 개방)"
  fi
done

run_wrapper "$REPO_ROOT"; ex1="$(sed -n 's/^exec-root: \([^ ]*\) .*/\1/p' "$CORE_OUT" | head -1)"
run_wrapper "$REPO_ROOT"; ex2="$(sed -n 's/^exec-root: \([^ ]*\) .*/\1/p' "$CORE_OUT" | head -1)"
if [ -n "$ex1" ] && [ -n "$ex2" ] && [ "$ex1" != "$ex2" ]; then
  pass_case "IC-4 재배정: exec dir 명이 실행마다 다름 ($ex1 → $ex2)"
else
  fail_case "IC-4 재배정: exec dir 명이 고정/미관측 (ex1='$ex1' ex2='$ex2')"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 12. arm-invariance — 라벨을 뒤집어도 verdict 는 불변 (판정기가 classification 을 못 본다)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── arm-invariance (라벨 역산 판정기 falsify) ────────────────────────────────"
SH="$(new_shadow none)"; MF="$TEST_TMP/mf_armflip.yaml"
reset_mf; MF_FLIP="1"; emit_manifest "$MF"
run_core "$CORE_PY" "$SH" --manifest "$MF"
inv_ok=1
[ "$(verdict_of s01)" = "LIVE" ]   || inv_ok=0
[ "$(verdict_of s02)" = "HOLLOW" ] || inv_ok=0
[ "$(verdict_of p01)" = "HOLLOW" ] || inv_ok=0
if [ "$inv_ok" -eq 1 ]; then
  pass_case "arm-invariance: declared_arm/expected_verdict 를 뒤집어도 verdict 3건 불변 (LIVE/HOLLOW/HOLLOW)"
else
  fail_case "arm-invariance: 라벨 뒤집기가 verdict 를 바꿈 — 판정기가 classification 을 본다(역산 채널)"
fi
if [ "$CORE_RC" -eq 1 ] && [ "$(grep -cF "::error::[VERDICT]" "$CORE_ERR")" -eq 3 ]; then
  pass_case "arm-invariance: 불일치는 reconcile 단계에서만 발생 (VERDICT 3건, exit 1)"
else
  fail_case "arm-invariance: exit=$CORE_RC / VERDICT 건수=$(grep -cF "::error::[VERDICT]" "$CORE_ERR") (기대 exit 1 · 3건)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 13. 정직 천장 문면 — over-claim 어휘 부재 (INV-5)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "── 정직 천장 문면 (INV-5) ───────────────────────────────────────────────────"
overclaim_hits=0
for word in "완전 봉인" "universal detection" "class 봉쇄" "근절"; do
  if grep -qF "$word" "$TEST_TMP/t1a.out"; then
    overclaim_hits=$((overclaim_hits+1))
    log "    over-claim 어휘 '$word' 가 하네스 stdout 에 등장"
  fi
done
if [ "$overclaim_hits" -eq 0 ]; then
  pass_case "정직 천장: 하네스 stdout 에 over-claim 어휘 0건"
else
  fail_case "정직 천장: over-claim 어휘 ${overclaim_hits}건 (INV-5 위반)"
fi
if grep -qF "presence ≠ truth" "$TEST_TMP/t1a.out"; then
  pass_case "정직 천장: PASS 발화가 'presence ≠ truth' 천장을 동반"
else
  fail_case "정직 천장: PASS 발화에 천장 문면 부재"
fi

# ─ F-CR18-9 회귀 가드는 §6 M7 로 이설 (F-CR19-1/-2 정정) ───────────────────────
# 종전 이 자리에는 `rc==0` + `exec-root:` 라인 2술어만 보는 케이스가 있었고, 그 라벨이
# "즉시 정리 작동" 을 PASS 로 발화했다. 실측 결과 형제 부재 불변식과 leg 정리를 **둘 다
# 제거한 mutant 가 본 suite 전건 생존**했으므로 그 라벨은 **관측하지 않은 것을 초록으로
# 보고하는 거짓 라벨**이었다. 관측 없는 발화는 무커버리지보다 나쁘다 — 케이스를 삭제하고
# 실제 판별력을 갖는 M7(§6)로 대체했다.

# ═══════════════════════════════════════════════════════════════════════════════
# 14. 요약
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "  test_check-hollow-gate-corpus: PASS=$PASS FAIL=$FAIL SKIP=$SKIP"
echo "  천장: 등재 표본에 대한 관측 기반 판별력까지 — corpus 밖 게이트 일반으로 외삽하지 않는다."
echo "        presence ≠ truth (검출 sufficiency = undecidable)."
echo "════════════════════════════════════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ] && [ "$PASS" -gt 0 ]; then
  exit 0
else
  # PASS=0 도 실패다 — 아무 케이스도 돌지 않은 vacuous green 을 초록으로 내지 않는다.
  exit 1
fi
