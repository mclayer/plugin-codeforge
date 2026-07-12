#!/usr/bin/env bash
# tests/scripts/test_check-selftest-execution-liveness.sh
# CFP-2622 (Epic CFP-2602 G6) — 메타-게이트 재귀 L3 discriminating self-test.
#
# 대상 = selftest-execution-liveness META-GATE (ADR-151 §결정9 / change-plan §8.1 RTM).
#   wrapper: scripts/check-selftest-execution-liveness.sh [ARGS]
#     → execs: python3 scripts/lib/check_selftest_execution_liveness.py [ARGS]
#   CLI 계약 (PINNED — 이 test 가 소비):
#     --repo-root PATH  → 모든 아티팩트 경로를 PATH 에서 derive
#                         (inventory=<root>/docs/selftest-execution-liveness-inventory.yaml,
#                          tests=<root>/tests/scripts/*.sh,
#                          workflows=<root>/.github/workflows + <root>/templates/github-workflows)
#     --inventory PATH  → inventory 경로만 override
#     EXIT: 0=all fail-closed AC pass, 1=≥1 violation, 2=usage error
#
# ── ★NON-NEGOTIABLE: firsthand execution / real exit codes / green ≠ red ────────
#   본 self-test 는 fixture repo-root 를 mktemp -d 로 실제 build 한 뒤 REAL 게이트를
#   `--repo-root <fixture>` 로 실행하고 REAL exit code 를 대조한다. repo 실파일 무오염
#   (fixture 트리만 mutate). anti-theater: GREEN(valid inventory)→exit 0 이 RED(변이)→exit 1
#   과 반드시 DIFFER. fixture/게이트 부재 시 NOT_RUN sentinel → 대조 skip (false PASS 금지).
#
# ── §8.1 RTM (authoritative) ──────────────────────────────────────────────────
#   AC-1a TC1 전 self-test 레코드 완비 → 0 ↔ TC2 1 레코드 삭제(파일 잔존) → 1
#   AC-2  TC3 agent_runtime + reason≥30 → 0 ↔ TC4 manual + reason<30(vague) → 1
#   AC-3  TC5 workflow:F:J 실재 job 이 test 실행 → 0 ↔ TC6 존재하지 않는 workflow → 1
#                                                    / TC6b job `if: false`(permanently_skipped) → 1
#   AC-5  TC7 parity both_copies(양 dir 참조) → 0 ↔ TC8 single(미검사 copy) → 1
#   AC-8  TC9 runtime N/A + g_boundary_check → 0 ↔ TC10 g_boundary_check empty/missing → 1
#   AC-9  TC11 메타-게이트 자기 레코드 alive → 0 ↔ TC12 자기 레코드 dead/삭제 → 1 (재귀)
#   AC-7  TC13 게이트/인벤토리/게이트-doc 정직 천장 문장 존재 + "완전 봉인" hard-claim 부재 grep
#
# ── §8.4 mutation A/B/C (게이트 로직 실효 반증 — sed-mutation of REAL gate) ─────
#   REAL check_selftest_execution_liveness.py 를 temp copy → 핵심 분기(레코드-존재 /
#   channel-alive / reason-substantive)를 각각 no-op 로 sed 무력화 → 해당 RED 가 이제
#   (잘못) 통과함을 확인 = green≠red 이 게이트 로직 온전함에 의존함을 입증. flip 안 하면
#   해당 TC 는 non-discriminating → 큰 소리로 FAIL.
#
# Exit code: 0 = 전 TC pass + 전 discriminating pair 성립, 1 = 하나라도 fail/non-discriminating

set -uo pipefail

# ═════════════════════════════════════════════════════════════════════════════
# 0. Preamble — 경로·러너·tally
# ═════════════════════════════════════════════════════════════════════════════
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GATE_WRAPPER="$REPO_ROOT/scripts/check-selftest-execution-liveness.sh"
GATE_PY="$REPO_ROOT/scripts/lib/check_selftest_execution_liveness.py"
INV_REL="docs/selftest-execution-liveness-inventory.yaml"

# self-record 경로 (AC-9 재귀 — 메타-게이트가 hardcode 로 확인하는 자기 self_test 경로).
SELF_TEST_PATH="tests/scripts/test_check-selftest-execution-liveness.sh"
SELF_WF="selftest-execution-liveness-test.yml"
SELF_JOB="selftest-liveness"

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
  echo "✗ FAIL: python3/python 부재 — 메타-게이트 실행 불가"
  exit 1
fi

# 임시 fixture 루트 목록 (EXIT 시 일괄 정리) + 임시 mutant py.
CLEANUP_DIRS=()
CLEANUP_FILES=()
cleanup() {
  local d f
  for d in "${CLEANUP_DIRS[@]:-}"; do [ -n "$d" ] && rm -rf "$d" 2>/dev/null; done
  for f in "${CLEANUP_FILES[@]:-}"; do [ -n "$f" ] && rm -f "$f" 2>/dev/null; done
}
trap cleanup EXIT
new_fixture_root() { local d; d="$(mktemp -d)"; CLEANUP_DIRS+=("$d"); echo "$d"; }

# ═════════════════════════════════════════════════════════════════════════════
# 1. 게이트 실행 helper — REAL exit code 를 stdout 으로 echo (로그는 stderr)
# ═════════════════════════════════════════════════════════════════════════════
# run_gate <fixture_root> [extra args...] → echoes exit code
#   PINNED entry point = wrapper .sh (contract 준수). wrapper 부재 시 python 직접 fallback.
run_gate() {
  local fix="$1"; shift
  local out ec=0
  if [ -f "$GATE_WRAPPER" ]; then
    out=$( bash "$GATE_WRAPPER" --repo-root "$fix" "$@" 2>&1 ) || ec=$?
  else
    out=$( "$PY" "$GATE_PY" --repo-root "$fix" "$@" 2>&1 ) || ec=$?
  fi
  # 게이트 stdout/stderr 는 디버깅용으로만 (판정은 exit code).
  printf '%s\n' "$out" | sed 's/^/      gate> /' >&2
  echo "$ec"
}

# run_gate_pyfile <py_path> <fixture_root> [extra args...] → echoes exit code
#   mutation A/B/C 전용 — 지정 python 파일(mutant)을 직접 실행.
#   sibling import(liveness_check_base 등) 해소 위해 PYTHONPATH 주입.
run_gate_pyfile() {
  local py="$1" fix="$2"; shift 2
  local out ec=0
  out=$( PYTHONPATH="$REPO_ROOT/scripts/lib:$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" \
         "$PY" "$py" --repo-root "$fix" "$@" 2>&1 ) || ec=$?
  printf '%s\n' "$out" | sed 's/^/      mutant> /' >&2
  echo "$ec"
}

# ═════════════════════════════════════════════════════════════════════════════
# 2. 인벤토리 스키마 emit (★RECONCILE-POINT — 실 게이트 파서에 정합)
# ═════════════════════════════════════════════════════════════════════════════
# ADR-151 §결정2 8-field 레코드. top-level 컨테이너 key = 실 게이트 확인 완료:
#   check_selftest_execution_liveness.py run() line 419: doc.get("self_tests") (list) 강제.
INV_TOP_KEY="self_tests"   # [reconciled] 실 게이트 top-level list key (verified: gate source)

# emit_record <self_test> <channel> <status> <tier> <disc> <l2> <reason> <gboundary>
emit_record() {
  local st="$1" ch="$2" cs="$3" bt="$4" df="$5" l2="$6" mr="$7" gb="$8"
  cat <<EOF
  - self_test: '$st'
    execution_channel: '$ch'
    channel_status: '$cs'
    blocking_tier: '$bt'
    discriminating_fixture: '$df'
    l2_full_scope: '$l2'
    manual_reason: '$mr'
    g_boundary_check: '$gb'
EOF
}

# emit_workflow <job_id> <test_basename> [if_false]
#   최소 workflow — 지정 job 이 run: line 으로 test 를 실행. if_false=1 이면 job-level `if: false`.
emit_workflow() {
  local job="$1" testbase="$2" iffalse="${3:-}"
  echo "name: $job"
  echo "on: [push]"
  echo "jobs:"
  echo "  $job:"
  # 게이트 _job_permanently_skipped 는 리터럴 `if: false`(YAML bool) 또는 `if: "false"` 만 검출.
  # `${{ false }}` 는 미검출 → permanently_skipped 재현 위해 반드시 리터럴 false 사용.
  [ "$iffalse" = "1" ] && echo "    if: false"
  echo "    runs-on: ubuntu-latest"
  echo "    steps:"
  echo "      - run: bash tests/scripts/$testbase"
}

# ═════════════════════════════════════════════════════════════════════════════
# 3. build_fixture — GREEN seed(내부 정합) + OV_* override 로 단일 결함 RED
# ═════════════════════════════════════════════════════════════════════════════
# GREEN seed 5 레코드가 AC-1a/2/3/5/8/9 를 동시 충족.
#   1 test_wf_wired.sh          workflow:wired.yml:wired-job          (AC-3 subject)
#   2 test_agent_runtime.sh     agent_runtime + reason≥30            (AC-2 subject)
#   3 test_parity.sh            workflow:parity.yml:parity-job + both_copies (AC-5 subject)
#   4 test_runtime_na.sh        manual_registered + g_boundary_check (AC-8 subject)
#   5 test_check-selftest-execution-liveness.sh  self-record alive   (AC-9 subject)
#
# OV_* (단일 결함 주입 — 미설정 시 GREEN):
#   OV_ADD_ORPHAN=1        AC-1a: 무레코드 stub 파일 추가
#   OV_AGENT_REASON=<str>  AC-2 : agent_runtime reason 교체(vague=RED)
#   OV_WIRED_CHANNEL=<str> AC-3 : wired 레코드 channel 교체(nonexistent=RED)
#   OV_WIRED_IF=1          AC-3 : wired-job 에 if:false 주입(permanently_skipped=RED)
#   OV_PARITY_L2=<str>     AC-5 : parity 레코드 l2 교체(single=RED)
#   OV_PARITY_SINGLE=1     AC-5 : templates copy 제거(단일 copy=RED, 대체 변이)
#   OV_RUNTIME_GB=<str>    AC-8 : runtime_na g_boundary_check 교체(공백=RED, ${..-} 사용)
#   OV_SELF_STATUS=<str>   AC-9 : self-record channel_status 교체(dead=RED)
build_fixture() {
  local F="$1"

  local agent_reason="${OV_AGENT_REASON-이 self-test 는 FIX loop 와 merge-gate disposition 시점에 Orchestrator runtime 이 직접 호출한다 (CI gate 아님, agent_runtime 채널).}"
  local wired_channel="${OV_WIRED_CHANNEL-workflow:wired.yml:wired-job}"
  local parity_l2="${OV_PARITY_L2-both_copies}"
  local runtime_gb="${OV_RUNTIME_GB-soak=G2 / DAST=G5 / real-render=§8.7 runtime 축 자연 N/A — 형제 축 참조(억지 이식 아님)}"
  local self_status="${OV_SELF_STATUS-alive}"
  local wired_if="${OV_WIRED_IF-}"
  local manual_reason_na="본 레코드는 wrapper-self runtime-inert governance lint 대상으로 soak/DAST/real-render 자연 N/A 이다."

  mkdir -p "$F/docs" "$F/tests/scripts" "$F/.github/workflows" "$F/templates/github-workflows"

  # ── self-test stub 파일 (레코드와 1:1) ──
  local stub
  for stub in test_wf_wired.sh test_agent_runtime.sh test_parity.sh test_runtime_na.sh "$(basename "$SELF_TEST_PATH")"; do
    printf '#!/usr/bin/env bash\nexit 0\n' > "$F/tests/scripts/$stub"
  done
  [ "${OV_ADD_ORPHAN-}" = "1" ] && printf '#!/usr/bin/env bash\nexit 0\n' > "$F/tests/scripts/test_orphan_no_record.sh"

  # ── workflows ──
  emit_workflow "wired-job"   "test_wf_wired.sh" "$wired_if"          > "$F/.github/workflows/wired.yml"
  emit_workflow "$SELF_JOB"   "$(basename "$SELF_TEST_PATH")"         > "$F/.github/workflows/$SELF_WF"
  emit_workflow "parity-job"  "test_parity.sh"                        > "$F/.github/workflows/parity.yml"
  if [ "${OV_PARITY_SINGLE-}" != "1" ]; then
    emit_workflow "parity-job" "test_parity.sh"                       > "$F/templates/github-workflows/parity.yml"  # byte-identical
  fi

  # ── inventory ──
  {
    echo "# fixture inventory (test_check-selftest-execution-liveness.sh)"
    echo "schema_version: '1.0'"
    echo "${INV_TOP_KEY}:"
    emit_record "tests/scripts/test_wf_wired.sh"      "$wired_channel"                                  "alive" "non_required" "present"    "N/A"          ""              "workflow channel — runtime 축(soak=G2/DAST=G5) 무관, wrapper-self CI lint"
    emit_record "tests/scripts/test_agent_runtime.sh" "agent_runtime"                                   "alive" "manual"       "smoke_only" "N/A"          "$agent_reason" "agent-runtime 호출 — soak=G2/DAST=G5 runtime 축 아님, 형제 축 참조"
    emit_record "tests/scripts/test_parity.sh"        "workflow:parity.yml:parity-job"                  "alive" "non_required" "present"    "$parity_l2"   ""              "parity self-test — runtime 축(soak/DAST/real-render) 무관 governance lint"
    emit_record "tests/scripts/test_runtime_na.sh"    "manual_registered"                               "alive" "manual"       "N/A"        "N/A"          "$manual_reason_na" "$runtime_gb"
    emit_record "$SELF_TEST_PATH"                     "workflow:$SELF_WF:$SELF_JOB"                     "$self_status" "non_required" "present" "N/A"     ""              "메타-게이트 자신 — wrapper-self-only(auto parity-safe), runtime 축 soak/DAST 무관"
  } > "$F/$INV_REL"
}

# 편의 RED 빌더 (단일 OV_* 결함).
build_green()      { build_fixture "$1"; }
build_red_ac1a()   { OV_ADD_ORPHAN=1                                   build_fixture "$1"; }
build_red_ac2()    { OV_AGENT_REASON="짧음"                            build_fixture "$1"; }
build_red_ac3()    { OV_WIRED_CHANNEL="workflow:nonexistent.yml:ghost" build_fixture "$1"; }
build_red_ac3b()   { OV_WIRED_IF=1                                     build_fixture "$1"; }
build_red_ac5()    { OV_PARITY_L2="single"                             build_fixture "$1"; }
build_red_ac8()    { OV_RUNTIME_GB=""                                  build_fixture "$1"; }
build_red_ac9()    { OV_SELF_STATUS="dead"                             build_fixture "$1"; }

# ═════════════════════════════════════════════════════════════════════════════
# 4. discriminating pair 실행 — GREEN(0) ≠ RED(1) REAL exit code 대조
# ═════════════════════════════════════════════════════════════════════════════
GATE_PRESENT=1
if [ ! -f "$GATE_PY" ] && [ ! -f "$GATE_WRAPPER" ]; then
  GATE_PRESENT=0
  note "메타-게이트 미착륙(scripts/lib/check_selftest_execution_liveness.py 부재) — 대조 NOT_RUN."
fi

EC_GREEN="NOT_RUN"
declare -A RED_EC   # tc -> exit code

# GREEN seed 1회 실행 (모든 pair 의 positive 측).
if [ "$GATE_PRESENT" = "1" ]; then
  FG="$(new_fixture_root)"; build_green "$FG"
  log ""
  log "── GREEN seed (valid inventory, 전 AC 충족 기대 exit 0) ──"
  EC_GREEN="$(run_gate "$FG")"
fi

# run_pair <tc> <ac-desc> <red_builder> <green_tc_label> <red_tc_label>
#   REAL exit code: GREEN(기대 0) vs RED(기대 1). anti-theater: green≠red 아니면 FAIL.
run_pair() {
  local ac="$1" red_builder="$2" gtc="$3" rtc="$4"
  log ""
  log "══ $ac ══"
  if [ "$GATE_PRESENT" != "1" ]; then
    skip_case "$gtc / $rtc — 게이트 미착륙 (NOT_RUN, false PASS 금지)"
    RED_EC[$rtc]="NOT_RUN"
    return
  fi

  # GREEN 측 판정 (공유 EC_GREEN).
  if [ "$EC_GREEN" = "0" ]; then
    pass_case "$gtc GREEN → exit 0 (valid inventory 통과)"
  else
    fail_case "$gtc GREEN → exit $EC_GREEN (기대 0 — valid fixture 가 통과 안 함; 스키마 정합 확인 필요)"
  fi

  # RED 측 판정.
  local FR; FR="$(new_fixture_root)"; "$red_builder" "$FR"
  local red_ec; red_ec="$(run_gate "$FR")"
  RED_EC[$rtc]="$red_ec"
  if [ "$red_ec" = "1" ]; then
    pass_case "$rtc RED → exit 1 (결함 검출)"
  else
    fail_case "$rtc RED → exit $red_ec (기대 1 — 결함 미검출; hollow/스키마 문제)"
  fi

  # anti-theater: green ≠ red.
  if [ "$EC_GREEN" = "NOT_RUN" ] || [ "$red_ec" = "NOT_RUN" ]; then
    skip_case "$ac anti-theater 대조 불가 (NOT_RUN)"
  elif [ "$EC_GREEN" = "$red_ec" ]; then
    fail_case "$ac ANTI-THEATER — GREEN(exit=$EC_GREEN) == RED(exit=$red_ec) = non-discriminating"
  else
    pass_case "$ac ANTI-THEATER discriminating — GREEN(exit=$EC_GREEN) ≠ RED(exit=$red_ec)"
  fi
}

run_pair "AC-1a (TC1/TC2 레코드 완비 ↔ 무레코드 orphan)"        build_red_ac1a "TC1"  "TC2"
run_pair "AC-2 (TC3/TC4 reason≥30 ↔ vague)"                     build_red_ac2  "TC3"  "TC4"
run_pair "AC-3 (TC5/TC6 workflow 실재 ↔ nonexistent)"           build_red_ac3  "TC5"  "TC6"
run_pair "AC-3 (TC5/TC6b workflow 실재 ↔ if:false skip)"        build_red_ac3b "TC5"  "TC6b"
run_pair "AC-5 (TC7/TC8 both_copies ↔ single)"                  build_red_ac5  "TC7"  "TC8"
run_pair "AC-8 (TC9/TC10 g_boundary_check ↔ empty)"             build_red_ac8  "TC9"  "TC10"
run_pair "AC-9 (TC11/TC12 self alive ↔ dead) [재귀]"            build_red_ac9  "TC11" "TC12"

# ═════════════════════════════════════════════════════════════════════════════
# 5. TC13 (AC-7 doc-presence) — 정직 천장 문장 존재 + hard-claim 부재 grep
# ═════════════════════════════════════════════════════════════════════════════
log ""
log "══ AC-7 (TC13 정직 천장 doc-presence) ══"
# 대상 = 메타-게이트 산출물 + 인벤토리 + carrier ADR 의 union.
TC13_TARGETS=(
  "$GATE_PY"
  "$GATE_WRAPPER"
  "$REPO_ROOT/$INV_REL"
  "$REPO_ROOT/archive/adr/ADR-151-selftest-execution-liveness-inventory.md"
)
TC13_EXISTING=()
for t in "${TC13_TARGETS[@]}"; do [ -f "$t" ] && TC13_EXISTING+=("$t"); done

if [ "${#TC13_EXISTING[@]}" -eq 0 ]; then
  skip_case "TC13 — 대상 문서 전부 미착륙 (NOT_RUN, false PASS 금지)"
else
  # 정직 천장 3 개념 (union 어딘가 존재하면 충족):
  #   ① 검출력 천장 = G3, ② 완결성 = review-tier, ③ L1 승격 = ADR-060.
  present_g3=0;   grep -qiE "G3" "${TC13_EXISTING[@]}" 2>/dev/null && present_g3=1
  present_rev=0;  grep -qiE "review|완결성" "${TC13_EXISTING[@]}" 2>/dev/null && present_rev=1
  present_060=0;  grep -qiE "ADR-060" "${TC13_EXISTING[@]}" 2>/dev/null && present_060=1
  # hard-claim 부재: "완전 봉인"/"complete seal" 이 AFFIRMATIVE 로 주장되면 위반.
  #   단, 그 표현을 FORBID/부정하는 문장(예: '"완전 봉인" hard-claim 금지', 'not a complete seal')은
  #   오히려 정직 천장 준수이므로 제외. → 부정-맥락 마커 담은 라인은 hard-claim 으로 세지 않음.
  local hard_claim_hits
  hard_claim_hits=$(grep -hiE "완전 봉인|complete seal" "${TC13_EXISTING[@]}" 2>/dev/null \
    | grep -viE "금지|아님|않|없|기각|prohibit|avoid|reject|not a|no complete|never|isn't|is not|must not" \
    || true)

  if [ "$present_g3" = "1" ] && [ "$present_rev" = "1" ] && [ "$present_060" = "1" ]; then
    pass_case "TC13 정직 천장 3개념 존재 (검출력=G3 / 완결성=review / L1=ADR-060)"
  else
    fail_case "TC13 정직 천장 문장 공백 (G3=$present_g3 review=$present_rev ADR-060=$present_060) — AC-7 obligation"
  fi
  if [ -z "$hard_claim_hits" ]; then
    pass_case "TC13 hard-claim 부재 (AFFIRMATIVE '완전 봉인'/'complete seal' 없음 — 부정-맥락 문장 제외)"
  else
    fail_case "TC13 hard-claim 존재 (AFFIRMATIVE '완전 봉인'/'complete seal' 검출) — 정직 천장 위반(ADR-151 §결정7): $hard_claim_hits"
  fi
fi

# ═════════════════════════════════════════════════════════════════════════════
# 6. §8.4 mutation A/B/C — REAL 게이트 로직 실효 반증 (sed-mutation)
# ═════════════════════════════════════════════════════════════════════════════
# 각 mutation:
#   baseline: REAL 게이트가 RED fixture 를 FAIL(exit 1) 하는지 확인 (전제).
#   mutant  : REAL 게이트 copy 에서 대상 분기를 no-op 로 무력화 → 같은 RED fixture 실행.
#   PASS 조건: baseline==1 && mutant==0 (분기 무력화로 결함 미검출 = green≠red 이 로직 의존).
#   sed 미적용(file 무변경) → NOT_RUN + FAIL (false PASS 금지).
#
# [reconciled] 실 게이트 분기를 정확 지목해 `if <cond>:` → `if False:` 로 무력화(body 사문화).
#   sed_neutralize <mutant_py> <exact-from-line> <exact-to-line> → 정확 1:1 치환. 미치환 시 exit 1.
sed_neutralize() {
  python3 - "$1" "$2" "$3" <<'PYEOF'
import sys
p, frm, to = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p, encoding="utf-8").read()
if frm not in s:
    sys.exit(1)                       # 대상 분기 부매칭 → 미적용 (recipe drift)
open(p, "w", encoding="utf-8").write(s.replace(frm, to, 1))
sys.exit(0)
PYEOF
}

# mutate_record_existence <mutant_py> — AC-1a "파일→레코드 부재" 분기(_check_corpus) 무력화.
#   실 게이트: `for f in sorted(disk): if f not in rec_paths: _error(AC-1a); violations.append(1)`.
mutate_record_existence() {
  sed_neutralize "$1" "        if f not in rec_paths:" "        if False:  # neutralized AC-1a file->record"
}

# mutate_channel_alive <mutant_py> — AC-3 alive-but-permanently_skipped 분기(_check_workflow_channel) 무력화.
#   실 게이트: `if all(_job_permanently_skipped(job_body) for _path, job_body in job_hits): _error(AC-3)`.
mutate_channel_alive() {
  sed_neutralize "$1" \
    "        if all(_job_permanently_skipped(job_body) for _path, job_body in job_hits):" \
    "        if False:  # neutralized AC-3 channel-alive"
}

# mutate_reason_substantive <mutant_py> — AC-2 manual_reason substantive 분기(_check_record) 무력화.
#   실 게이트: `if not _is_substantive(rec["manual_reason"]): _error(AC-2)`.
mutate_reason_substantive() {
  sed_neutralize "$1" \
    '        if not _is_substantive(rec["manual_reason"]):' \
    "        if False:  # neutralized AC-2 reason-substantive"
}

# run_mutation <label> <recipe_fn> <red_builder>
run_mutation() {
  local label="$1" recipe="$2" red_builder="$3"
  log ""
  log "── MUTATION $label ──"
  if [ "$GATE_PRESENT" != "1" ] || [ ! -f "$GATE_PY" ]; then
    skip_case "MUTATION $label — 게이트 py 미착륙 (NOT_RUN)"
    return
  fi

  local FR; FR="$(new_fixture_root)"; "$red_builder" "$FR"

  # baseline: REAL 게이트가 RED 를 FAIL 해야 함.
  local base_ec; base_ec="$(run_gate_pyfile "$GATE_PY" "$FR")"
  if [ "$base_ec" != "1" ]; then
    fail_case "MUTATION $label baseline — REAL 게이트가 RED fixture 를 FAIL 안 함 (exit=$base_ec, 기대 1). 대조 무의미."
    return
  fi

  # mutant 생성 — temp dir(scripts/lib read-only 경계 존중; 게이트는 sibling import 0, stdlib+yaml 만).
  local MD; MD="$(mktemp -d)"; CLEANUP_DIRS+=("$MD")
  local mut="$MD/mutant.py"
  cp "$GATE_PY" "$mut"

  if ! "$recipe" "$mut"; then
    fail_case "MUTATION $label — recipe 가 mutant 를 변경 못 함 (branch 패턴 drift). false PASS 금지, NOT_RUN."
    rm -rf "$MD"
    return
  fi

  local mut_ec; mut_ec="$(run_gate_pyfile "$mut" "$FR")"
  rm -rf "$MD"

  if [ "$base_ec" = "1" ] && [ "$mut_ec" = "0" ]; then
    pass_case "MUTATION $label — 분기 무력화로 RED flip (baseline exit=1 → mutant exit=0) = 게이트 로직 live·discriminating"
  else
    fail_case "MUTATION $label — flip 실패 (baseline=$base_ec, mutant=$mut_ec). 기대 1→0. non-discriminating 또는 recipe 부정확."
  fi
}

# Mutation B 는 channel-alive(AC-3 permanently_skipped) 분기를 무력화하므로, 그 분기가 유일 위반인
#   RED = build_red_ac3b(if:false → permanently_skipped, channel_status alive) 를 사용.
#   (build_red_ac3 = nonexistent workflow 는 AC-2 file-absent 분기 소관이라 mutation B 무관.)
run_mutation "A record-existence (AC-1a)"   mutate_record_existence   build_red_ac1a
run_mutation "B channel-alive (AC-3)"       mutate_channel_alive      build_red_ac3b
run_mutation "C reason-substantive (AC-2)"  mutate_reason_substantive build_red_ac2

# ═════════════════════════════════════════════════════════════════════════════
# 7. Summary
# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "Test Summary — CFP-2622 G6 메타-게이트 재귀 L3 self-test"
echo "============================================================"
echo "PASS: $PASS / FAIL: $FAIL / SKIP: $SKIP / TOTAL ASSERT: $((PASS+FAIL))"
echo "GREEN seed exit: $EC_GREEN (기대 0)"
echo "RED exit codes:"
for tc in TC2 TC4 TC6 TC6b TC8 TC10 TC12; do
  echo "  $tc → ${RED_EC[$tc]:-N/A} (기대 1)"
done
echo ""
if [ "$GATE_PRESENT" != "1" ]; then
  echo "⊘ 메타-게이트 미착륙 — 전 discriminating 대조 NOT_RUN. 게이트 착륙 후 재실행 필요."
  echo "  (false PASS 금지: 게이트 없이 exit 0 반환 안 함.)"
  exit 1
fi
if [ "$FAIL" -eq 0 ] && [ "$PASS" -gt 0 ]; then
  echo "✓ 전 TC pass + 전 discriminating pair 성립 (green≠red) + mutation A/B/C flip 확인"
  exit 0
else
  echo "✗ 하나 이상 실패/비-discriminating (FAIL=$FAIL, PASS=$PASS)"
  exit 1
fi
