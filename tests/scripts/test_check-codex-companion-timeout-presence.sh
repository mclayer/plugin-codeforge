#!/usr/bin/env bash
# tests/scripts/test_check-codex-companion-timeout-presence.sh
# CFP-2828 / ADR-081 Amendment 14 §결정 D15 — Discriminating self-test for
#   scripts/lib/check_codex_companion_timeout_presence.py wall-clock 가드 + stdin redirect presence lint.
#
# RE-TARGET (CFP-2545 → CFP-2828): 구 companion 브로커 dispatch (`node ... adversarial-review | task --write`)
#   → Codex CLI **`codex exec`** 직접 dispatch. 파일명·action 명 유지(required-context 재적립 chicken-egg
#   회피, D-5). 검사 명제 = "모든 `codex exec` dispatch 발화는 option-first `timeout --kill-after=<K> <N>`
#   가드 + stdin `- <` file-redirect 를 동반" (AC-9 wall-clock + AC-4 D8 계승).
#
# 배경: codex exec dispatch 는 항상 **runnable option-first** 가드 `timeout --kill-after=<K> <N>` 로 감싸야 함.
#   ★ GNU coreutils 는 duration-first `timeout <N> --kill-after=<K> cmd` 에서 `--kill-after` 를
#     실행할 명령으로 오인 → exit 127 (가드 무효). option 은 duration 앞에 와야 함.
#   [verified: coreutils 8.32 — timeout 1 --kill-after=1 sleep 5 → 127 / timeout --kill-after=1 1 sleep 5 → 124]
#
# 2-축 결박 (F-2 blind spot 봉인 계승):
#   축 A (grep oracle) : lint 가 §8.4 discriminating fixture (G1/G2/R1-R5/G3 + AC-4 + AC-7 E1/E2) 를
#                        정확히 판별하는가 — 각 RED 는 **의도한 축의 진단 라벨**까지 assert (귀속 단일화).
#   축 B (execution)   : 실제 `timeout` 실행이 correct form → exit 124 / broken form → exit 127 인가.
#   grep oracle 을 런타임 진실에 결박 — 문자열 존재만으로는 "실행 가능"을 보증 못함(F-2).
#
# CFP-2884 / ADR-081 Amendment 15 §결정 D16 8항 — lint 에 **3번째 disjoint 축** AC-7
#   (`export LC_ALL=<locale>.UTF-8` / `export PYTHONUTF8=1` 별도 줄 presence) 합류. 본 suite 대응:
#   ① dispatch 보유 fixture 전건에 env export 2줄 상재 (AC-7 축 GREEN 고정 → RED 귀속 단일화),
#   ② AC-7 축 자체의 load-bearing pair E1(부재) / E2(inline env-prefix) 신설.
#   ★ AC-7 GREEN 은 "인코딩 안전" 이 아님 — env export = 2급 defense-in-depth (LC_ALL/LANG 은
#     Python-on-Windows 파일 I/O 무효 실측). 1급 보증 = helper 코드계층 명시 encoding='utf-8'
#     round-trip assert (tests/scripts/test_cfp2884_promptfile_encoding_roundtrip.*).
#
# CFP-2929 §3.8 B-10 / §5.1 B-6·B-8 — lint 에 **4번째 disjoint 축** E6 (`scan_output_path_dialect`:
#   `-o` 출력 경로가 `<IDENT>=$(cygpath …)` 정규화를 거친 식별자인가) 합류 ⊕ 사정권 확대
#   (`plugins/codeforge-review` → `plugins`). 본 suite 대응:
#   ① dispatch 보유 fixture 전건에 **정규화 대입 2줄 상재**(`NORM_PREFIX`) → E6 축 GREEN 고정
#      (RED 귀속 단일화 — ENV_PREFIX 가 AC-7 축에 하는 일과 동형),
#   ② E6 축 자체의 load-bearing 짝 X1~X5 신설. 그 중 **X1 = AC-4 anti-substring** (정규화가
#      주석·산문 리터럴에만 있으면 GREEN 이 되면 안 된다 — E1 동형 강도).
#   ★ NORM_PREFIX 삽입은 **검사 우회가 아니다**: 넣는 것은 "정상 배선이면 당연히 있어야 할 정규화
#     블록" 이며, 넣은 뒤에도 X1(주석 전용)·X2(식별자 불일치)·X5(정규화 부재)가 RED 를 유지한다
#     (= 축이 약화되지 않았음의 실증. G1 ↔ X5 가 단일 변수 diff 짝).
#   ★ E6 GREEN 은 "런타임에 정규화된다" 의 보증이 아니라 **presence 신호** 다 — 별칭·간접 재대입·
#     정규화 이후 재대입은 정적 리터럴 대조가 잡지 못한다 (정직 상한, ADR-119).
#
# ★ R1 load-bearing 자기검출 (§8.4): R1 = timeout 제거 `codex exec` (column 0) → exit 1 을 요구.
#   lint 의 execution_first_tokens 가 ('timeout','node') → ('timeout','codex') 로 재타겟되지 않으면,
#   `codex exec` 첫-토큰 라인이 doc-example 로 오분류되어 스킵 → dispatch 발화 0건 → 단일 fixture no-op
#   (exit 0) ≠ 기대 exit 1 → 본 케이스가 MISMATCH 로 재타겟 회귀를 자기검출.
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-codex-companion-timeout-presence.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# 축 A: grep-oracle 케이스 (fixture text → lint → exit code assert)
#   exit code 캡처 = `|| exit_code=$?` (raw `|| true` 아님 — 근접 PASS/FAIL 카운터가 유일 pass/fail
#   신호를 gating, ADR-060 Amd22 정합).
#
# ★ 3축 합성 하 RED 귀속 단일화 (CFP-2884 / ADR-081 §결정 D16 8항):
#   lint 는 timeout 축 ∪ AC-4 redirect 축 ∪ AC-7 encoding-env 축을 `max()` 로 합성한다. 따라서
#   fixture 가 **의도한 mutation 외의 축**도 동시에 위반하면 exit 1 이 어느 축에서 왔는지 구분 불가 →
#   그 케이스는 "RED 이긴 한데 이유는 모름" = 판별력 상실 (의도 축이 회귀해도 다른 축이 exit 1 을
#   떠받쳐 MISMATCH 가 안 뜬다). 봉인 2겹:
#     (1) 모든 dispatch 보유 fixture 에 `export LC_ALL=…UTF-8` / `export PYTHONUTF8=1` 2줄 상재
#         → AC-7 축을 GREEN 으로 고정 (AC-7 을 일부러 행사하는 E1 만 예외).
#     (2) RED 케이스는 5번째 인자 `expect_label_pat` 로 **의도 축의 진단 라벨 실재**를 직접 assert
#         (exit code 스칼라만으로는 축 귀속 불가 — python self-test `_self_test_scan_axes` 의
#         must_contain/must_not_contain 설계와 동형).
# ─────────────────────────────────────────────────────────────────────────────

# 전 fixture 공통 인코딩 env 서두 (AC-7 축 GREEN 고정 — 별도 줄 export 2종)
ENV_PREFIX='export LC_ALL=C.UTF-8
export PYTHONUTF8=1'

# 전 fixture 공통 출력 경로 정규화 서두 (CFP-2929 E6 축 GREEN 고정 — 실 P-0 형태와 동형 2-hop).
# ★ 이 2줄이 없으면 `-o` 를 가진 dispatch fixture 는 E6 축에서 RED 가 되어 다른 축의 RED 귀속이
#   흐려진다 (봉인 (1) 과 동일 취지). 아래 X5 가 "이 2줄이 실제로 load-bearing" 임을 짝으로 실증.
NORM_PREFIX='_n="$(cygpath -m "$OUT_JSON" 2>/dev/null)"
OUT_JSON="$_n"'

# 3축 GREEN 고정 서두 (timeout 축은 각 fixture 의 dispatch 라인 형태가 결정).
FIXTURE_PREFIX="$ENV_PREFIX
$NORM_PREFIX"

run_case() {
  local name="$1" fixture_text="$2" expected_exit="$3" description="$4" expect_label_pat="${5:-}"
  local exit_code=0 out fixture_file
  fixture_file="$(mktemp --suffix=.md)"
  # shellcheck disable=SC2064
  trap "rm -f '$fixture_file'" RETURN
  printf '%s\n' "$fixture_text" > "$fixture_file"
  out=$(bash "$WRAPPER" "$fixture_file" 2>&1) || exit_code=$?
  local problem=""
  if [ "$exit_code" -ne "$expected_exit" ]; then
    problem="Expected exit $expected_exit, got $exit_code"
  elif [ -n "$expect_label_pat" ] && ! printf '%s' "$out" | grep -qE -- "$expect_label_pat"; then
    # 축 귀속 assert: exit 1 이 **의도한 축**에서 왔음을 진단 라벨 실재로 입증 (합성 max() 하 필수)
    problem="exit $exit_code 은 맞으나 의도 축 진단 라벨 부재 (pat: $expect_label_pat) — RED 귀속 불명"
  fi
  if [ -z "$problem" ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  $problem"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# 축별 진단 라벨 (scripts/lib/check_codex_companion_timeout_presence.py 발화 리터럴과 결속)
LBL_TIMEOUT='FAIL — wall-clock 가드 누락'
LBL_REDIRECT='FAIL \(AC-4 — stdin `- <` redirect 부재\)'
LBL_ENCODING='FAIL \(AC-7 — UTF-8 인코딩 env export 부재\)'
LBL_DIALECT='FAIL \(E6 — 출력 경로 방언 정규화 부재/불일치\)'

# home-present 트리 케이스 (hollow-gate I-3 / consumer no-op 판별용)
run_tree_case() {
  local name="$1" expected_exit="$2" description="$3" home_present="$4" file_text="$5"
  local exit_code=0 out tmpdir
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  if [ "$home_present" = "yes" ]; then
    mkdir -p "$tmpdir/plugins/codeforge-review/agents"
    printf '%s\n' "$file_text" > "$tmpdir/plugins/codeforge-review/agents/CodexReviewAgent.md"
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
echo " CFP-2828: codex exec dispatch timeout+redirect presence lint — 축 A (grep oracle)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# G1: GREEN — option-first (env-default) read-only dispatch 가드 존재 (§8.4 G1)
run_case "G1: GREEN option-first (env-default) read-only" \
  "$FIXTURE_PREFIX"'
timeout --kill-after=${CODEX_REVIEW_KILL_AFTER_SEC:-30} ${CODEX_REVIEW_TIMEOUT_SEC:-300} codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  0 "runnable option-first 가드 + stdin - < redirect + 인코딩 env export 2종 → 3축 전부 GREEN (정본 dispatch 형태)"

# G2: GREEN — option-first (리터럴) write-mode 예외 (§8.4 G2)
run_case "G2: GREEN option-first (리터럴) write-mode 예외" \
  "$FIXTURE_PREFIX"'
timeout --kill-after=30 300 codex exec -s workspace-write --output-schema s.json -o out.json - < p.md' \
  0 "write-gate 예외(-s workspace-write)도 runnable option-first 가드 + redirect + 인코딩 env export 필수"

# R1: RED (load-bearing mutation) — timeout 제거, codex exec column 0 (§8.4 R1)
#   ★ execution_first_tokens 재타겟('node'→'codex') 미갱신 시: dispatch 발화 0건 → timeout 축 no-op
#     ∧ AC-7 축 vacuous → exit 0 ≠ 기대 1 → MISMATCH 로 회귀 자기검출 (env export 상재 상태에서도 보존).
run_case "R1: RED mutation — timeout 제거 (codex exec column0, 재타겟 자기검출)" \
  "$FIXTURE_PREFIX"'
codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "가드 load-bearing: timeout 제거 → timeout 축 단독 RED (G1 ↔ R1 diff). execution_first_tokens=('timeout','codex') 검증" \
  "$LBL_TIMEOUT"

# R2: RED — duration-first 오배열 (broken, GNU timeout exit 127) (§8.4 R2)
run_case "R2: RED duration-first 오배열 (broken)" \
  "$FIXTURE_PREFIX"'
timeout 300 --kill-after=30 codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "duration-first = GNU timeout exit 127 가드 무효 → timeout 축 단독 RED (runnable 강제)" \
  "$LBL_TIMEOUT"

# R3: RED — N=0 (option-first 형태이나 무한대기 미방지) (§8.4 R3)
run_case "R3: RED N=0 (무한대기 미방지)" \
  "$FIXTURE_PREFIX"'
timeout --kill-after=30 0 codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "N(duration)=0 → 양수 의무 위반 → timeout 축 단독 RED" \
  "$LBL_TIMEOUT"

# R4: RED — --kill-after 누락 (option 부재) (§8.4 R4)
run_case "R4: RED --kill-after 누락" \
  "$FIXTURE_PREFIX"'
timeout 300 codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "--kill-after 부재 = codex 프로세스 미reap 위험 + 가드 불완전 → timeout 축 단독 RED" \
  "$LBL_TIMEOUT"

# AC-4: RED — stdin - < redirect 부재 (inline positional prompt) (§8.2 D-6 positive 구조 계약)
#   가드는 정상이나 promptfile 을 inline positional 로 전달 → redirect 축이 RED (D8 계승 위반).
run_case "AC4: RED stdin - < redirect 부재 (inline positional prompt)" \
  "$FIXTURE_PREFIX"'
timeout --kill-after=30 300 codex exec -s read-only --output-schema s.json -o out.json p.md' \
  1 "inline positional prompt (- < 부재) → AC-4 positive 구조 계약 위반 → redirect 축 단독 RED (한글 실값 argv 노출 회피 superset)" \
  "$LBL_REDIRECT"

# AC-7 (E1): RED — 인코딩 env export 부재 (CFP-2884 3번째 disjoint 축, ADR-081 §결정 D16 8항)
#   G1 과 dispatch 라인 byte-동일, 차이는 env export 2줄 유무뿐 → G1 ↔ E1 이 AC-7 축의 load-bearing pair.
run_case "E1: RED AC-7 인코딩 env export 부재 (G1 ↔ E1 단일 변수 diff)" \
  "$NORM_PREFIX"'
timeout --kill-after=${CODEX_REVIEW_KILL_AFTER_SEC:-30} ${CODEX_REVIEW_TIMEOUT_SEC:-300} codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "가드·redirect 정상이나 export LC_ALL/PYTHONUTF8 별도 줄 부재 → AC-7 축 단독 RED (2급 defense-in-depth presence). ★ E6 축은 NORM_PREFIX 로 GREEN 고정 — RED 귀속 단일" \
  "$LBL_ENCODING"

# ★ inline env-prefix mutant (`LC_ALL=… PYTHONUTF8=1 timeout … codex exec …`) 은 본 suite 에 두지
#   않는다 — scripts/lib/check_codex_companion_timeout_presence.py `_self_test_scan_axes` E4 가
#   이미 소유 (중복 fixture 유입 금지, ADR-140 재사용 우선). 여기 두려면 "inline 라인 + 정상 가드 라인"
#   2줄 shape 가 필요한데, 그 shape 자체가 E4 와 byte 수준으로 같은 케이스다.
#
# ★ 정직 ceiling (declared FN — 본 PR 유발 아님, first-token 휴리스틱의 기존 성질):
#   파일의 **유일한** dispatch 라인이 inline env-prefix 형태이면 first-token 이 'timeout'/'codex' 가
#   아니라 doc-example 로 분류 → 발화 0건 → 3축 전부 vacuous → exit 0. 즉 그 형태는 timeout 축까지
#   포함해 통째로 미검출이다 (AC-7 도입 전부터 동일). presence lint 의 declared 천장 —
#   '완전 봉인' 아님 (ADR-151 §결정 7).

# ═══════════════════════════════════════════════════════════════════════════
#  CFP-2929 E6 — 4번째 disjoint 축 (출력 경로 방언 정규화) load-bearing 짝 X1~X5
# ═══════════════════════════════════════════════════════════════════════════
# 전 케이스 `$ENV_PREFIX` 상재 → AC-7 축 GREEN 고정. timeout·redirect 축도 정상 형태로 고정.
#   ⇒ 아래 RED 는 **E6 축 단독** 이며 `$LBL_DIALECT` 로 귀속을 직접 assert 한다.

# X1: ★★ RED — AC-4 anti-substring. 정규화가 **주석·산문 리터럴에만** 존재.
#   이 케이스가 GREEN 이 되면 E6 축은 hollow 다 (문면만 갖추면 통과 = 검사 우회 자유).
#   기존 `E4 RED: inline env-prefix…`(python self-test) 및 E1 과 **동형 강도**의 결박.
run_case "X1: RED E6 anti-substring (정규화가 주석·산문에만 존재)" \
  "$ENV_PREFIX"'
# _n="$(cygpath -m "$OUT_JSON" 2>/dev/null)"   <- 주석: 실행되지 않는다
#   OUT_JSON="$_n"
산문 언급: 출력 경로는 cygpath -m 으로 drive-form 정규화한다고 문서에 적어만 둔다.
timeout --kill-after=30 300 codex exec -s read-only --output-schema s.json -o "$OUT_JSON" - < p.md' \
  1 "주석·산문 리터럴은 런타임에 대입을 수행하지 않는다 → E6 축 단독 RED (substring hollow 차단)" \
  "$LBL_DIALECT"

# X2: RED — 정규화는 실재하나 `-o "$VAR"` 의 VAR 가 **정규화 도달 식별자 집합 밖**.
#   E-2 가 보여준 실패 형태("2개 중 1개만 고침")의 정적 대응물 — 정규화 산출을 argv 로 안 넘기면
#   정규화가 무의미하다.
run_case "X2: RED E6 식별자 불일치 (정규화 산출을 -o 로 안 넘김)" \
  "$ENV_PREFIX"'
NORMALIZED="$(cygpath -m "$SOMETHING_ELSE")"
timeout --kill-after=30 300 codex exec -s read-only --output-schema s.json -o "$OUT_JSON" - < p.md' \
  1 "정규화 대입은 있으나 -o 의 식별자가 그 폐포에 없음 → E6 축 단독 RED (presence 만으로 통과 불가)" \
  "$LBL_DIALECT"

# X3: GREEN — 2-hop 복사 대입 (실 P-0 형태 `_n=$(cygpath …)` → `OUT_JSON="$_n"` → `-o "$OUT_JSON"`).
#   ★ born-red 방지 결박: 실 production 형태가 RED 가 되면 축 자체가 배포 불가다.
run_case "X3: GREEN E6 2-hop 복사 대입 (실 P-0 형태)" \
  "$ENV_PREFIX"'
_n="$(cygpath -m "$OUT_JSON" 2>/dev/null)"
OUT_JSON="$_n"
timeout --kill-after=30 300 codex exec -s read-only --output-schema s.json -o "$OUT_JSON" - < p.md' \
  0 "정규화 산출이 1-hop 복사를 거쳐 argv 변수에 도달 — 위치 비의존(B-10) 변수 흐름 판정이 실 형태를 통과시킨다"

# X4: GREEN — `-o` 부재 dispatch = 본 축 vacuous (출력 경로 argv 자체가 없다).
#   ★ 축의 정의역을 못 박는다 — 무관한 dispatch 를 무차별 RED 로 만들면 상시-RED 가 된다.
run_case "X4: GREEN E6 vacuous (-o 부재 dispatch)" \
  "$ENV_PREFIX"'
timeout --kill-after=30 300 codex exec -s read-only --output-schema s.json - < p.md' \
  0 "출력 경로 argv 부재 = E6 정의역 밖 → vacuous GREEN (정의역 초과 적용 0)"

# X5: ★ RED — G1 ↔ X5 **단일 변수 diff** (NORM_PREFIX 2줄 유무뿐). 리터럴 `-o out.json` 형.
#   G1 이 GREEN 인 이유가 "NORM_PREFIX 상재" 임을 짝으로 실증한다 = NORM_PREFIX 삽입이 검사
#   우회가 아니라 **load-bearing 배선**이라는 증거.
run_case "X5: RED E6 정규화 부재 (G1 ↔ X5 단일 변수 diff)" \
  "$ENV_PREFIX"'
timeout --kill-after=${CODEX_REVIEW_KILL_AFTER_SEC:-30} ${CODEX_REVIEW_TIMEOUT_SEC:-300} codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "가드·redirect·인코딩 정상이나 정규화 대입 전무 → E6 축 단독 RED. G1 과의 차이는 NORM_PREFIX 2줄뿐" \
  "$LBL_DIALECT"

# R5: RED — hollow-gate I-3 (home 실존 + dispatch 발화 0건) (§8.4 R5)
run_tree_case "R5: RED hollow-gate I-3 (home 실존 + 발화 0건)" \
  1 "home 실존하나 codex exec dispatch 발화 0건 → 발화 스코프 이탈 가능 → exit 1 (항상 GREEN 방지, born-broken 재현)" \
  yes "이 파일에는 codex exec 실행 dispatch 발화가 없다 — prose 로만 언급."

# G3: GREEN — consumer no-op (home 부재 + dispatch 발화 0건) (§8.4 G3)
run_tree_case "G3: GREEN consumer no-op (home 부재)" \
  0 "consumer degradation: plugins/codeforge-review/agents/ 부재 → honest no-op exit 0 (spurious RED 미발생, byte-identical parity 안전)" \
  no "이 문서는 codex exec 를 prose 로만 언급. 실행 dispatch 발화 0건."

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " 축 B (execution-backed) — grep oracle 을 런타임 진실에 결박 (F-2 봉인)"
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

# B1: correct option-first form → 실제 timeout kill → exit 124 (§8.4 B1)
exec_case "B1: exec option-first → exit 124 (timeout kill)" \
  124 "runnable 형태가 실제로 wall-clock kill 을 수행" \
  timeout --kill-after=1 1 sleep 5

# B2: broken duration-first form → GNU timeout 이 --kill-after 를 명령으로 오인 → exit 127 (§8.4 B2)
exec_case "B2: exec duration-first → exit 127 (broken, 가드 무효)" \
  127 "duration-first = --kill-after 를 실행 명령으로 오인 → 가드 무효(127). lint RED 의 런타임 근거" \
  timeout 1 --kill-after=1 sleep 5

# B3: 원 reproducer (Story 원 버그 형태) → exit 127 (원 버그 재현)
exec_case "B3: exec 원 reproducer (300 --kill-after=30) → exit 127" \
  127 "원 버그 형태 재현 — dispatch 가 원래 duration-first 였으면 가드 무효였음" \
  timeout 300 --kill-after=30 sleep 1

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " 축 C (grep-presence) — 실 CodexReviewAgent.md 대상 §8.1 grep 계약 (AC-1 / I-5)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
# §8.1 = "CodexReviewAgent.md dispatch 문자열 | grep 계약: AC-1(companion 참조 0) / AC-4 / AC-9 /
#   -s read-only presence(I-5)". AC-4/AC-9 = 축 A(lint). AC-1/I-5 = 실 agent md 대상 grep-presence(본 축 C).
MD_REAL="$REPO_ROOT/plugins/codeforge-review/agents/CodexReviewAgent.md"

# AC-1 companion **dispatch invocation** 형태 (dispatch 발화 한정 — prose "companion 브로커 우회" 서술
#   언급은 대상 아님, DevPL 지시). 3 리터럴: node ... codex-companion.mjs | node ... adversarial-review |
#   node ... task --write. `node` + 뒤이어 dispatch 리터럴 동반 라인만 매칭 → prose `node` 오탐 0.
AC1_PAT='node[[:space:]].*(codex-companion\.mjs|adversarial-review|task[[:space:]]+--write)'
# I-5 `-s read-only` presence — codex exec dispatch 실행 라인 한정 ([^`] 로 backtick inline prose 회피).
I5_PAT='codex[[:space:]]+exec[^`]*-s[[:space:]]+read-only'

# 안전 count. ★ exit-masking 아님(ADR-060 Amd22): grep -c 는 0 매칭 시 exit 1(정상 = "0건"),
#   즉 grep exit 는 pass/fail 신호가 **아니라** count 표현 수단 → `|| n=0` 은 "0건" 정규화이고,
#   실제 pass/fail 은 반환 count 를 근접 assert(assert_count_eq/ge)가 gating. file 부재 위장은 아래
#   MD_REAL 존재 guard 가 별도 차단(부재 시 grep count 0 의 false-PASS 방지).
grep_count() { local n; n=$(grep -cE "$1" "$2" 2>/dev/null) || n=0; printf '%s' "$n"; }

assert_count_eq() {
  local name="$1" file="$2" pat="$3" expected="$4" desc="$5" cnt
  cnt="$(grep_count "$pat" "$file")"
  if [ "$cnt" -eq "$expected" ]; then
    echo "✓ PASS: $name (count $cnt == $expected) — $desc"; PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name (expected count $expected, got $cnt) — $desc"; FAIL=$((FAIL+1))
  fi
}
assert_count_ge() {
  local name="$1" file="$2" pat="$3" min="$4" desc="$5" cnt
  cnt="$(grep_count "$pat" "$file")"
  if [ "$cnt" -ge "$min" ]; then
    echo "✓ PASS: $name (count $cnt >= $min) — $desc"; PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name (expected count >= $min, got $cnt) — $desc"; FAIL=$((FAIL+1))
  fi
}

# setup guard: 실 agent md 존재 (부재 시 grep count 0 이 AC-1 을 false-PASS 위장하는 born-broken 차단)
if [ -f "$MD_REAL" ]; then
  echo "✓ PASS: C0 setup — 실 CodexReviewAgent.md 존재 (grep-presence 대상 확정)"
  PASS=$((PASS+1))

  # C1 (AC-1): companion dispatch invocation 참조 0 (실 agent md firsthand)
  assert_count_eq "C1: AC-1 companion dispatch 참조 0 (실 agent md)" \
    "$MD_REAL" "$AC1_PAT" 0 \
    "companion dispatch 발화(node ... adversarial-review|task --write|codex-companion.mjs) = 0"

  # C2 (I-5): -s read-only presence >=1 (실 agent md dispatch 실행 라인 firsthand)
  assert_count_ge "C2: I-5 -s read-only presence >=1 (실 agent md)" \
    "$MD_REAL" "$I5_PAT" 1 \
    "codex exec dispatch 실행 라인에 -s read-only 리터럴 고정 (network-off 기본 축)"

  # C1-disc: AC-1 grep 탐지력 결박 — companion dispatch 라인 주입 → grep 검출(>=1) (never-match 패턴 아님)
  MD_INJ="$(mktemp --suffix=.md)"
  cp "$MD_REAL" "$MD_INJ"
  printf '%s\n' 'timeout --kill-after=30 300 node "$CMD" adversarial-review --wait "x"' >> "$MD_INJ"
  assert_count_ge "C1-disc: AC-1 grep 탐지력 (companion 라인 주입 → 검출)" \
    "$MD_INJ" "$AC1_PAT" 1 \
    "주입 companion dispatch 를 grep 이 검출 = C1 이 vacuous(never-match) 아님 입증"
  rm -f "$MD_INJ"

  # C2-disc: I-5 discriminating — -s read-only 제거 사본 → grep RED(0) (presence assert 결박, born-broken 방지)
  MD_STRIP="$(mktemp --suffix=.md)"
  sed 's/-s read-only//g' "$MD_REAL" > "$MD_STRIP"
  assert_count_eq "C2-disc: I-5 discriminating (-s read-only 제거 → RED)" \
    "$MD_STRIP" "$I5_PAT" 0 \
    "presence 제거 시 count 0 = C2 가 실제 presence 를 결박 입증"
  rm -f "$MD_STRIP"
else
  echo "✗ FAIL: C0 setup — 실 CodexReviewAgent.md 부재 ($MD_REAL) — grep-presence setup 실패 (born-broken 위장 차단)"
  FAIL=$((FAIL+1))
fi

# ─────────────────────────────────────────────────────────────────────────────
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — codex exec dispatch: option-first 가드 + stdin redirect + AC-7 인코딩 env export + E6 출력경로 방언 정규화 **4축** load-bearing(RED 축 귀속 라벨 assert 포함, X1 = AC-4 anti-substring) + 실행 축 결박 + 실 agent md grep-presence(AC-1 참조0 / I-5 -s read-only) 입증"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
