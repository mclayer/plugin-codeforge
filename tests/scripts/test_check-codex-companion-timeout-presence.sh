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
#   축 A (grep oracle) : lint 가 §8.4 discriminating fixture (G1/G2/R1-R5/G3 + AC-4) 를 정확히 판별하는가.
#   축 B (execution)   : 실제 `timeout` 실행이 correct form → exit 124 / broken form → exit 127 인가.
#   grep oracle 을 런타임 진실에 결박 — 문자열 존재만으로는 "실행 가능"을 보증 못함(F-2).
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
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" fixture_text="$2" expected_exit="$3" description="$4"
  local exit_code=0 out fixture_file
  fixture_file="$(mktemp --suffix=.md)"
  # shellcheck disable=SC2064
  trap "rm -f '$fixture_file'" RETURN
  printf '%s\n' "$fixture_text" > "$fixture_file"
  out=$(bash "$WRAPPER" "$fixture_file" 2>&1) || exit_code=$?
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
  'timeout --kill-after=${CODEX_REVIEW_KILL_AFTER_SEC:-30} ${CODEX_REVIEW_TIMEOUT_SEC:-300} codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  0 "runnable option-first 가드 + stdin - < redirect → GREEN (정본 dispatch 형태)"

# G2: GREEN — option-first (리터럴) write-mode 예외 (§8.4 G2)
run_case "G2: GREEN option-first (리터럴) write-mode 예외" \
  'timeout --kill-after=30 300 codex exec -s workspace-write --output-schema s.json -o out.json - < p.md' \
  0 "write-gate 예외(-s workspace-write)도 runnable option-first 가드 + redirect 필수"

# R1: RED (load-bearing mutation) — timeout 제거, codex exec column 0 (§8.4 R1)
#   ★ execution_first_tokens 재타겟('node'→'codex') 미갱신 시 이 케이스가 MISMATCH → 회귀 자기검출.
run_case "R1: RED mutation — timeout 제거 (codex exec column0, 재타겟 자기검출)" \
  'codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "가드 load-bearing: timeout 제거 → lint RED (G1 ↔ R1 diff). execution_first_tokens=('timeout','codex') 검증"

# R2: RED — duration-first 오배열 (broken, GNU timeout exit 127) (§8.4 R2)
run_case "R2: RED duration-first 오배열 (broken)" \
  'timeout 300 --kill-after=30 codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "duration-first = GNU timeout exit 127 가드 무효 → lint RED (runnable 강제)"

# R3: RED — N=0 (option-first 형태이나 무한대기 미방지) (§8.4 R3)
run_case "R3: RED N=0 (무한대기 미방지)" \
  'timeout --kill-after=30 0 codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "N(duration)=0 → 양수 의무 위반 → lint RED"

# R4: RED — --kill-after 누락 (option 부재) (§8.4 R4)
run_case "R4: RED --kill-after 누락" \
  'timeout 300 codex exec -s read-only --output-schema s.json -o out.json - < p.md' \
  1 "--kill-after 부재 = codex 프로세스 미reap 위험 + 가드 불완전 → lint RED"

# AC-4: RED — stdin - < redirect 부재 (inline positional prompt) (§8.2 D-6 positive 구조 계약)
#   가드는 정상이나 promptfile 을 inline positional 로 전달 → redirect 축이 RED (D8 계승 위반).
run_case "AC4: RED stdin - < redirect 부재 (inline positional prompt)" \
  'timeout --kill-after=30 300 codex exec -s read-only --output-schema s.json -o out.json p.md' \
  1 "inline positional prompt (- < 부재) → AC-4 positive 구조 계약 위반 → lint RED (한글 argv mangling superset)"

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
  echo "✓ All $PASS cases pass — codex exec dispatch: option-first 가드 + stdin redirect load-bearing + 실행 축 결박 + 실 agent md grep-presence(AC-1 참조0 / I-5 -s read-only) 입증"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
