#!/usr/bin/env bash
# tests/scripts/test_check-shell-test-masking.sh
# CFP-2635 Phase 2 (구현 lane) — Discriminating self-test for
#   scripts/lib/check_shell_test_masking.py exit-masking + mock-seam-무assert 정적 lint.
#
# ★ hollow-gate 아님의 유일 증명 (Change Plan §8 / Story §7.4):
#   masking TC(TC-M1/M2 → MUST 검출) / 정당 TC(TC-L1~L6 → MUST 미검출, TC-L2 = 정밀도 keystone) /
#   mock-seam TC(TC-S1 RED / TC-S2 GREEN) + mutation-kill(제외 로직 제거 → 정당 RED /
#   검출 로직 제거 → masking RED / logical-line 재구성 제거 → TC-L2 RED) + 실 코퍼스 precision proof.
#   presence-only 금지 — 실 exit code 로 검출/미검출을 결박 (ADR-119 / CFP-2545 execution-backed).
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

# Windows 로컬 견고성: python helper stdout 를 utf-8 로 고정 (CI=Linux 는 utf-8 기본).
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-shell-test-masking.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_shell_test_masking.py"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# lint_case: fixture 파일 1개를 tmpdir 코퍼스 위치에 배치 → lint scoped 실행 → exit + surface 대조
#   인자: <name> <expected_exit> <flag_substr|""> <corpus_relpath> <fixture_content>
#   flag_substr 비어있지 않으면 → 출력에 그 substring 포함 assert (검출 확증).
#   flag_substr = "NOFLAG" → 출력에 'FLAG' 미포함 assert (미검출 확증, 정밀도 oracle).
# ─────────────────────────────────────────────────────────────────────────────
lint_case() {
  local name="$1" expected_exit="$2" flag_substr="$3" relpath="$4" content="$5"
  local exit_code=0 out tmpdir ok=1
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  mkdir -p "$tmpdir/$(dirname "$relpath")"
  printf '%s\n' "$content" > "$tmpdir/$relpath"
  out=$(bash "$WRAPPER" --repo-root "$tmpdir" 2>&1) || exit_code=$?

  [ "$exit_code" -eq "$expected_exit" ] || ok=0
  if [ "$flag_substr" = "NOFLAG" ]; then
    # 실 flag surface = '::warning::' (PASS 메시지의 'FLAG 0' 오매칭 회피).
    case "$out" in *"::warning::"*) ok=0;; esac
  elif [ -n "$flag_substr" ]; then
    case "$out" in *"$flag_substr"*) : ;; *) ok=0;; esac
  fi

  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $exit_code)"
    PASS=$((PASS+1))
  else
    echo "X FAIL: $name"
    echo "  expected exit=$expected_exit flag_substr='$flag_substr', got exit=$exit_code"
    echo "  output: $out"
    FAIL=$((FAIL+1))
  fi
}

# mutant_case: 원본 SSOT 를 python 문자열치환으로 mutate → fixture 에 실행 → 오분류 확증(mutation-kill)
#   인자: <name> <mutate_kind> <expected_exit_under_mutant> <corpus_relpath> <fixture_content>
#   mutate_kind: no_exclude(rule a 무력화) / no_detect(검출 무력화) / no_reconstruct(재구성 무력화)
# ─────────────────────────────────────────────────────────────────────────────
mutant_case() {
  local name="$1" kind="$2" expected_exit="$3" relpath="$4" content="$5"
  local exit_code=0 out tmpdir mutant ok=1
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  mkdir -p "$tmpdir/$(dirname "$relpath")"
  printf '%s\n' "$content" > "$tmpdir/$relpath"
  mutant="$tmpdir/mutant.py"

  python3 - "$SSOT_PY" "$mutant" "$kind" <<'PY'
import sys
src_path, out_path, kind = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src_path, encoding="utf-8").read()
if kind == "no_exclude":
    # rule (a) counter-backup 제외 무력화 → 정당 assert-family || true 가 masking 오검출돼야 함(RED).
    s2 = s.replace(
        "_is_counter_backup(text, defined_funcs, file_has_fail_counter)",
        "False", 1)
elif kind == "no_detect":
    # masking 검출 append 무력화 → masking 라인 미검출(RED — TC-M 기대검출 실패).
    s2 = s.replace(
        'masking.append((ll.lineno, "exit-masking", text.strip()[:140]))',
        "pass", 1)
elif kind == "no_reconstruct":
    # logical-line 재구성 무력화 → 다중행 assert continuation 의 || true 가 오검출(RED — TC-L2 keystone).
    s2 = s.replace(
        'if buf.rstrip().endswith("\\\\") and join_count < MAX_CONTINUATION_JOIN:',
        "if False:", 1)
else:
    s2 = s
assert s2 != s, "mutation did not apply — anchor string drift (kind=%s)" % kind
open(out_path, "w", encoding="utf-8").write(s2)
PY

  out=$(python3 "$mutant" --repo-root "$tmpdir" 2>&1) || exit_code=$?
  [ "$exit_code" -eq "$expected_exit" ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (mutant exit $exit_code — 오분류 확증, 로직 load-bearing)"
    PASS=$((PASS+1))
  else
    echo "X FAIL: $name"
    echo "  mutant($kind) expected exit=$expected_exit, got exit=$exit_code"
    echo "  output: $out"
    FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2635: shell-test-exit-masking-detect — discriminating self-test"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── Positive (masking → MUST 검출, exit 1) ──"

# TC-M1: cmd 유일 신호, 하류 counter/assert 부재 → flag
lint_case "TC-M1 masking (some_check_cmd)" 1 "exit-masking" "scripts/test-m1.sh" \
'#!/usr/bin/env bash
# masking: exit 가 유일 신호이고 하류 카운터/assert 부재
some_check_cmd || true
echo "continue"'

# TC-M2: raw command masking (bash script invocation)
lint_case "TC-M2 masking (bash script)" 1 "exit-masking" "scripts/test-m2.sh" \
'#!/usr/bin/env bash
bash scripts/foo.sh || true
echo "continue"'

echo
echo "── Negative (정당 3종 + edge → MUST 미검출, exit 0, 정밀도 oracle) ──"

# TC-L1: counter-backup assert-family head (rule a)
lint_case "TC-L1 legit counter-backup (assert head)" 0 "NOFLAG" "scripts/test-l1.sh" \
'#!/usr/bin/env bash
FAIL=0
assert_file_exists() { [ -f "$1" ] || FAIL=$((FAIL+1)); }
assert_file_exists "$F" "name" || true
echo "trailing non-companion narration"'

# TC-L2 [정밀도 keystone]: 다중행 assert continuation → logical-line 재구성 (rule a on head)
lint_case "TC-L2 keystone (multiline assert continuation)" 0 "NOFLAG" "scripts/test-l2.sh" \
'#!/usr/bin/env bash
FAIL=0
assert_grep_all() { for p in "$@"; do grep -q "$p" x || FAIL=$((FAIL+1)); done; }
assert_grep_all "$F" "name" \
  "pattern one" \
  "direction: strengthening" || true
echo "trailing non-companion narration"'

# TC-L3: arithmetic (rule b)
lint_case "TC-L3 legit arithmetic" 0 "NOFLAG" "scripts/test-l3.sh" \
'#!/usr/bin/env bash
count=0
((count++)) || true
echo "trailing non-companion narration"'

# TC-L4: redirect-capture best-effort (rule c)
lint_case "TC-L4 legit redirect (2>/dev/null)" 0 "NOFLAG" "scripts/test-l4.sh" \
'#!/usr/bin/env bash
probe_thing foo 2>/dev/null || true
echo "trailing non-companion narration"'

# TC-L5: branch-guard (rule d)
lint_case "TC-L5 legit branch-guard" 0 "NOFLAG" "scripts/test-l5.sh" \
'#!/usr/bin/env bash
if some_probe || true; then
  echo "branch taken"
fi'

# TC-L6: heredoc + full-comment || true literal (제외)
lint_case "TC-L6 legit heredoc/comment literal" 0 "NOFLAG" "scripts/test-l6.sh" \
'#!/usr/bin/env bash
# doc: raw_cmd || true 는 안티패턴 (주석 라인 — 스캔 제외)
cat <<'"'"'EOF'"'"'
example snippet: raw_cmd || true  (heredoc 문서 텍스트, 실 명령 아님)
EOF
echo "trailing non-companion narration"'

echo
echo "── Mock-seam 축 ──"

# TC-S1 (RED): mock env export 후 block 내 동반 assertion 부재 → flag
lint_case "TC-S1 mock-seam no-assert (RED)" 1 "mock-seam-no-assert" "scripts/test-s1.sh" \
'#!/usr/bin/env bash
run_scenario() {
  export _CFP_X_MOCK=1
  do_something_with_mock
}
run_scenario
echo "no verification of mock behavior anywhere in scope"'

# TC-S2 (GREEN): mock env export 후 block 내 assert/grep 동반 → no flag
lint_case "TC-S2 mock-seam WITH assert (GREEN)" 0 "NOFLAG" "scripts/test-s2.sh" \
'#!/usr/bin/env bash
FAIL=0
run_scenario() {
  export _CFP_X_MOCK=1
  out=$(do_something_with_mock)
  echo "$out" | grep -q "expected-marker" || FAIL=$((FAIL+1))
}
run_scenario'

echo
echo "── Mutation-kill (로직 load-bearing 실증 — 오분류 = mutant killed) ──"

# MK-1: 제외 로직(rule a) 제거 → 정당 TC-L1 오검출(exit 1) = 제외 로직 load-bearing
mutant_case "MK-1 no_exclude → TC-L1 오검출(RED)" no_exclude 1 "scripts/test-l1.sh" \
'#!/usr/bin/env bash
FAIL=0
assert_file_exists() { [ -f "$1" ] || FAIL=$((FAIL+1)); }
assert_file_exists "$F" "name" || true
echo "trailing non-companion narration"'

# MK-2: 검출 로직 제거 → masking TC-M1 미검출(exit 0) = 검출 로직 load-bearing
mutant_case "MK-2 no_detect → TC-M1 미검출(RED)" no_detect 0 "scripts/test-m1.sh" \
'#!/usr/bin/env bash
some_check_cmd || true
echo "continue"'

# MK-3: logical-line 재구성 제거 → TC-L2 continuation 오검출(exit 1) = 재구성 keystone load-bearing
mutant_case "MK-3 no_reconstruct → TC-L2 오검출(RED)" no_reconstruct 1 "scripts/test-l2.sh" \
'#!/usr/bin/env bash
FAIL=0
assert_grep_all() { for p in "$@"; do grep -q "$p" x || FAIL=$((FAIL+1)); done; }
assert_grep_all "$F" "name" \
  "pattern one" \
  "direction: strengthening" || true
echo "trailing non-companion narration"'

echo
echo "── 실 코퍼스 precision proof (오탐 0) ──"

# RC: 실 70-file(=69 실 self-test, git-pathspec 33 중 1 = test-fixtures 내 비-self-test 자산 제외) 코퍼스
#     대상 실행 → 위반 0 (149행 || true 전부 정당) → exit 0.
rc_exit=0
rc_out=$(bash "$WRAPPER" --repo-root "$REPO_ROOT" 2>&1) || rc_exit=$?
if [ "$rc_exit" -eq 0 ]; then
  case "$rc_out" in
    *"FLAG 0"*|*"PASS"*)
      echo "OK PASS: RC precision proof (exit 0, 실 코퍼스 위반 0) — $rc_out"
      PASS=$((PASS+1)) ;;
    *)
      echo "X FAIL: RC precision proof — exit 0 이나 PASS surface 부재: $rc_out"
      FAIL=$((FAIL+1)) ;;
  esac
else
  echo "X FAIL: RC precision proof — 실 코퍼스에서 오탐 발생 (exit $rc_exit)"
  echo "  output: $rc_out"
  FAIL=$((FAIL+1))
fi

echo
echo "── input-driven exhaustion 회귀 가드 (CFP-2635 FIX SF-1/DR-2635-1 — execution-backed) ──"

# PERF-1 (end-to-end): 400k env-prefix 단일라인(1.5MB) 코퍼스 → tool wall < 5s.
#   per-physical-line length cap(Fix1) + read islice(Fix3) 결합 가드 — 구판(per-line 미bound) O(n²)
#   는 동일 입력에 >60s(timeout). exit 무관(truncate 후 || true 미도달) → 시간만 판정. firsthand ≈ 0.23s.
perf_tmp=$(mktemp -d)
mkdir -p "$perf_tmp/scripts"
python3 - "$perf_tmp/scripts/test-perf-dos.sh" <<'PYEOF'
import sys
# 단일 물리라인 = FAIL 카운터 헤더(file_has_fail_counter=True 유도) + 400k env-prefix + `|| true`.
open(sys.argv[1], "w", encoding="utf-8").write("FAIL=$((FAIL+1))\n" + "A=b " * 400000 + "cmd || true\n")
PYEOF
perf_e2e=$(python3 - "$SSOT_PY" "$perf_tmp" <<'PYEOF'
import subprocess, sys, time
py, root = sys.argv[1], sys.argv[2]
t0 = time.perf_counter()
try:
    subprocess.run([sys.executable, py, "--repo-root", root],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    print("%.3f" % (time.perf_counter() - t0))
except subprocess.TimeoutExpired:
    print("999.0")
PYEOF
)
rm -rf "$perf_tmp"
if awk "BEGIN{exit !($perf_e2e < 5.0)}"; then
  echo "OK PASS: PERF-1 end-to-end 400k-line wall=${perf_e2e}s (<5s — O(n²) 회귀 차단)"
  PASS=$((PASS+1))
else
  echo "X FAIL: PERF-1 end-to-end 400k-line wall=${perf_e2e}s (>=5s — length-cap 제거/O(n²) 회귀 의심)"
  FAIL=$((FAIL+1))
fi

# PERF-2 (micro): _leading_token 직접 400k env-prefix 문자열 → O(n) 가드 (truncation 우회 = Fix2 독립 검증).
#   offset-advance(index 전진) 회귀→slice-in-loop 시 1.6MB 입력 O(n²) ≈ 40s. firsthand O(n) ≈ 0.18s.
perf_micro=$(python3 - "$SSOT_PY" <<'PYEOF'
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("m", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
s = "A=b " * 400000 + "cmd"
t0 = time.perf_counter()
tok = m._leading_token(s)
el = time.perf_counter() - t0
assert tok == "cmd", "leading_token semantics broke: %r" % tok
print("%.3f" % el)
PYEOF
)
if awk "BEGIN{exit !($perf_micro < 2.0)}"; then
  echo "OK PASS: PERF-2 _leading_token(400k-prefix) wall=${perf_micro}s (<2s — offset-advance O(n) 확증)"
  PASS=$((PASS+1))
else
  echo "X FAIL: PERF-2 _leading_token wall=${perf_micro}s (>=2s — slice-in-loop O(n²) 회귀 의심)"
  FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — masking 검출/정당 미검출/mock-seam/mutation-kill/precision proof 결박"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
