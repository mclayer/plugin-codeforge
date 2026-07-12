#!/usr/bin/env bash
# tests/scripts/test_check-resource-safety-claim-proof.sh
# CFP-2646 Phase 2 (구현 lane) — Discriminating self-test for
#   scripts/lib/check_resource_safety_claim_proof.py resource-safety claim ↔ proof-link presence lint.
#
# ★ hollow-gate 아님의 유일 증명 (Change Plan §8 / Story §7.4):
#   over-claim TC(TC-OC1/OC2 → MUST 검출) / honest-denial·proof-linked·ceiling TC(TC-HD1/PL1/CD1 →
#   MUST 미검출) / 정의부 EXEMPT(TC-EX1) + mutation-kill(MK-1 검출 무력화 / MK-2 denial-EXEMPT 무력화 /
#   MK-3 evidence-presence 무력화 각 load-bearing 실 RED) + 실 코퍼스 precision proof(grandfather 후 오탐 0)
#   + DoS 회귀가드(1.5MB 단일라인 bounded-time — CFP-2635 O(n²) 재발 차단) + AC-3 self-application(본 Story
#   실 산출물 lint self-PASS). presence-only 금지 — 실 exit code 로 검출/미검출 결박(ADR-119 execution-backed).
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.
#
# honesty ceiling(ADR-151 §결정7): 본 self-test 는 presence/discriminating/DoS-bounded 까지 결박 — claim 의
#   참됨(truth) 은 검증 못 함(정적 도구 상한). presence ≠ truth. bounded degradation, 임의 입력 무해 아님.

set -euo pipefail

# Windows 로컬 견고성: python helper stdout 를 utf-8 로 고정 (CI=Linux 는 utf-8 기본).
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-resource-safety-claim-proof.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_resource_safety_claim_proof.py"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# lint_case: fixture 1개를 tmpdir 코퍼스 위치에 배치 → lint scoped 실행(baseline 부재=subtract 0)
#   → exit + surface 대조. flag_substr="NOFLAG" → '::warning::' 미포함 assert (미검출 확증).
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

# mutant_case: 원본 SSOT 를 python 문자열치환으로 mutate → fixture 에 실행 → 오분류 확증(mutation-kill).
#   mutate_kind: no_detect(검출 무력화) / no_denial(denial-EXEMPT 무력화) / no_evidence(evidence-presence 무력화)
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
if kind == "no_detect":
    # claim 검출 append 무력화 → over-claim 라인 미검출(RED — TC-OC 기대검출 실패).
    s2 = s.replace(
        "claim_hits.append((lineno, tok, stripped))",
        "pass", 1)
elif kind == "no_denial":
    # denial-context EXEMPT 무력화 → 정직한 부인문(denial, ceiling 무)이 over-claim 오검출(RED).
    s2 = s.replace(
        "_is_denial_context(texts, i)",
        "False", 1)
elif kind == "no_evidence":
    # evidence-presence 무력화(항상 부재) → proof-linked/ceiling 파일이 over-claim 오검출(RED).
    s2 = s.replace(
        "file_has_evidence = _file_has_evidence(nonexempt)",
        "file_has_evidence = False", 1)
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
echo " CFP-2646: resource-safety-claim-proof-presence — discriminating self-test"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── Positive (over-claim: proof/ceiling 무 → MUST 검출, exit 1) ──"

# TC-OC1: docstring safety-claim + proof-ref 0 + ceiling 0 → flag
lint_case "TC-OC1 over-claim docstring (backtracking/DoS-guard)" 1 "::warning::" "scripts/lib/check_oc1.py" \
'#!/usr/bin/env python3
r"""
check_oc1 — 예시 게이트.
이 도구는 catastrophic backtracking 0 이며 DoS 가드 를 제공한다.
"""
X = 1'

# TC-OC2: inline 주석 형 over-claim (CFP-2591 형) → flag
lint_case "TC-OC2 over-claim comment (nested quantifier/ReDoS-safe)" 1 "::warning::" "scripts/lib/check_oc2.py" \
'#!/usr/bin/env python3
# nested quantifier 0 (ReDoS-safe) — 안전.
X = 1'

echo
echo "── Negative (honest denial / proof-linked / ceiling / 정의부 → MUST 미검출, exit 0) ──"

# TC-HD1: honest denial + ceiling → no flag (denial 판별축)
lint_case "TC-HD1 honest denial + ceiling (NOFLAG)" 0 "NOFLAG" "scripts/lib/check_hd1.py" \
'#!/usr/bin/env python3
r"""
이 tool 은 ReDoS-safe 가 아님 — bounded degradation (임의 입력 무해 아님).
"""
X = 1'

# TC-PL1: proof-linked claim → no flag (proof-ref presence)
lint_case "TC-PL1 proof-linked claim (NOFLAG)" 0 "NOFLAG" "scripts/lib/check_pl1.py" \
'#!/usr/bin/env python3
r"""
catastrophic backtracking 0 (self-test PERF-1 회귀가드 tests/scripts/test_x.sh:120, 1MB=<1s 실측).
"""
X = 1'

# TC-CD1: honest-ceiling downgrade → no flag (ceiling presence)
lint_case "TC-CD1 honest-ceiling downgrade (NOFLAG)" 0 "NOFLAG" "scripts/lib/check_cd1.py" \
'#!/usr/bin/env python3
r"""
scan cap = 총 작업량 bound (임의 입력 무해 아님, honesty ceiling ADR-151).
"""
X = 1'

# TC-EX1: 정의부 자기열거 (closed-set 상수 정의 라인) → EXEMPT
lint_case "TC-EX1 token-definition line EXEMPT (NOFLAG)" 0 "NOFLAG" "scripts/lib/check_ex1.py" \
'#!/usr/bin/env python3
_SAFETY_CLAIM_TOKENS = ["catastrophic backtracking 0", "ReDoS-safe", "DoS 가드"]
X = 1'

# TC-HD2: denial-only (ceiling 무) → NOFLAG (denial 판별축 단독 — MK-2 fixture)
lint_case "TC-HD2 denial-only no-ceiling (NOFLAG)" 0 "NOFLAG" "scripts/lib/check_hd2.py" \
'#!/usr/bin/env python3
# 이 도구는 ReDoS-safe 가 아님 (이 위협에 취약).
X = 1'

echo
echo "── Mutation-kill (판별 로직 load-bearing 실증 — 오분류 = mutant killed) ──"

# MK-1: 검출 로직 제거 → over-claim TC-OC1 미검출(exit 0) = 검출 로직 load-bearing
mutant_case "MK-1 no_detect → TC-OC1 미검출(RED)" no_detect 0 "scripts/lib/check_oc1.py" \
'#!/usr/bin/env python3
r"""
이 도구는 catastrophic backtracking 0 이며 DoS 가드 를 제공한다.
"""
X = 1'

# MK-2: denial-EXEMPT 제거 → denial-only TC-HD2 오검출(exit 1) = 부정문 EXEMPT load-bearing
mutant_case "MK-2 no_denial → TC-HD2 오검출(RED)" no_denial 1 "scripts/lib/check_hd2.py" \
'#!/usr/bin/env python3
# 이 도구는 ReDoS-safe 가 아님 (이 위협에 취약).
X = 1'

# MK-3: evidence-presence 제거 → proof-linked TC-PL1 오검출(exit 1) = evidence presence load-bearing
mutant_case "MK-3 no_evidence → TC-PL1 오검출(RED)" no_evidence 1 "scripts/lib/check_pl1.py" \
'#!/usr/bin/env python3
r"""
catastrophic backtracking 0 (self-test PERF-1 회귀가드 tests/scripts/test_x.sh:120, 1MB=<1s 실측).
"""
X = 1'

echo
echo "── 실 코퍼스 precision proof (grandfather subtract 후 new-over-claim 0) ──"

rc_exit=0
rc_out=$(bash "$WRAPPER" --repo-root "$REPO_ROOT" 2>&1) || rc_exit=$?
if [ "$rc_exit" -eq 0 ]; then
  case "$rc_out" in
    *"FLAG 0"*|*"PASS"*)
      echo "OK PASS: RC precision proof (exit 0, grandfather 후 new-over-claim 0) — $rc_out"
      PASS=$((PASS+1)) ;;
    *)
      echo "X FAIL: RC precision proof — exit 0 이나 PASS surface 부재: $rc_out"
      FAIL=$((FAIL+1)) ;;
  esac
else
  echo "X FAIL: RC precision proof — 실 코퍼스에서 new-over-claim FLAG (exit $rc_exit)"
  echo "  output: $rc_out"
  FAIL=$((FAIL+1))
fi

echo
echo "── DoS 회귀 가드 (T-3 line-length + T-4 read-path — CFP-2635 O(n²) 재발 차단, execution-backed) ──"

# PERF-1 (end-to-end): 1.5MB 단일 물리라인 코퍼스 → tool wall < 5s.
#   per-physical-line length cap(T-3) + islice(T-4) 결합 가드 — born-safe. 구판(미bound)은 동일 입력 O(n²) >60s.
perf_tmp=$(mktemp -d)
mkdir -p "$perf_tmp/scripts/lib"
python3 - "$perf_tmp/scripts/lib/check_perf.py" <<'PYEOF'
import sys
# 단일 물리라인 = 1.5MB (claim token + 대량 padding), 라인-길이 의존 경로 총 작업량 bound 검증.
open(sys.argv[1], "w", encoding="utf-8").write(
    'r"""catastrophic backtracking 0 ' + "A" * 1500000 + ' DoS 가드"""\n')
PYEOF
perf_e2e=$(python3 - "$SSOT_PY" "$perf_tmp" <<'PYEOF'
import subprocess, sys, time
py, root = sys.argv[1], sys.argv[2]
t0 = time.perf_counter()
try:
    subprocess.run([sys.executable, py, "--repo-root", root],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    print("%.3f" % (time.perf_counter() - t0))
except subprocess.TimeoutExpired:
    print("999.0")
PYEOF
)
rm -rf "$perf_tmp"
if awk "BEGIN{exit !($perf_e2e < 5.0)}"; then
  echo "OK PASS: PERF-1 end-to-end 1.5MB-single-line wall=${perf_e2e}s (<5s — T-3/T-4 bound, O(n²) 회귀 차단)"
  PASS=$((PASS+1))
else
  echo "X FAIL: PERF-1 end-to-end 1.5MB-single-line wall=${perf_e2e}s (>=5s — length-cap 제거/O(n²) 회귀 의심)"
  FAIL=$((FAIL+1))
fi

# PERF-2 (T-2 micro): _leading_scan_index 대량 입력 → O(n) 가드 (tokenize 복잡도 독립 검증).
perf_micro=$(python3 - "$SSOT_PY" <<'PYEOF'
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("m", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
s = "x " * 700000 + "catastrophic backtracking 0"
t0 = time.perf_counter()
hit = m._detect_claim_token(s)
el = time.perf_counter() - t0
assert hit is not None, "claim detect semantics broke: %r" % hit
print("%.3f" % el)
PYEOF
)
if awk "BEGIN{exit !($perf_micro < 2.0)}"; then
  echo "OK PASS: PERF-2 _detect_claim_token(1.4MB) wall=${perf_micro}s (<2s — substring O(n) 확증)"
  PASS=$((PASS+1))
else
  echo "X FAIL: PERF-2 _detect_claim_token wall=${perf_micro}s (>=2s — O(n²) 회귀 의심)"
  FAIL=$((FAIL+1))
fi

# PERF-3 (baseline read-path DoS): poisoned pure-whitespace baseline(256KB 단일 공백 물리라인) → load_baseline
#   bounded (timeout-guarded, fail-fast). 구판(load_baseline T-3 미적용 + _BASELINE_FILE_RE 인접 무제한 `\s*`)은
#   동일 입력 O(n²) >30s (baseline path DoS — PERF-1/2 는 scan_file path 만 커버, baseline path green-while-vuln).
#   born-safe = T-3 truncate 대칭 적용 + regex bounded-quantifier. + baseline 파싱 semantics 무회귀 assert.
perf_baseline=$(python3 - "$SSOT_PY" <<'PYEOF'
import subprocess, sys, time, tempfile, os
py = sys.argv[1]
fd, poison = tempfile.mkstemp(suffix=".yaml"); os.close(fd)
with open(poison, "w", encoding="utf-8", newline="\n") as f:
    f.write("grandfathered_claims:\n- file: scripts/foo.py\n  claim_token: ReDoS-safe\n")
    f.write(" " * 262144 + "\n")  # 256KB pure-whitespace physical line = poisoned baseline DoS payload
code = (
    "import importlib.util,sys;"
    "s=importlib.util.spec_from_file_location('m',sys.argv[1]);"
    "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
    "k=m.load_baseline(sys.argv[2]);"
    "assert ('scripts/foo.py','ReDoS-safe') in k, 'baseline parse semantics broke: %r' % sorted(k);"
    "print('OK')"
)
t0 = time.perf_counter()
try:
    r = subprocess.run([sys.executable, "-c", code, py, poison],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
    dt = time.perf_counter() - t0
    print("%.3f" % dt if r.returncode == 0 else "998.0")  # 998 = semantics broke / crash
except subprocess.TimeoutExpired:
    print("999.0")  # 999 = O(n²) 회귀 (timeout)
finally:
    os.remove(poison)
PYEOF
)
if awk "BEGIN{exit !($perf_baseline < 5.0)}"; then
  echo "OK PASS: PERF-3 load_baseline(256KB pure-ws poisoned baseline) wall=${perf_baseline}s (<5s — T-3/regex bound, baseline-path O(n²) 회귀 차단)"
  PASS=$((PASS+1))
else
  echo "X FAIL: PERF-3 load_baseline wall=${perf_baseline}s (>=5s — baseline read-path length-cap/regex bound 제거 O(n²) 회귀 의심)"
  FAIL=$((FAIL+1))
fi

echo
echo "── ★ AC-3 self-application (본 Story 실 산출물 lint self-PASS — self-referential 결함 3rd 재발 차단) ──"
# wrapper-resident 산출물 3종을 lint --files 로 통과시켜 exit 0 확인 (over-claim 방지 Story 가 자기 over-claim
#   하면 자기 게이트에 hit). change-plan + Story §7 (internal-docs repo)은 Phase 2 구현 시점 firsthand 검증(§8 기록)
#   — wrapper CI self-test 는 sibling repo 파일 미의존(deterministic).
ADR082=$(ls "$REPO_ROOT"/archive/adr/ADR-082-*.md 2>/dev/null | head -1)
ROSTER="$REPO_ROOT/plugins/codeforge-develop/agents/DeveloperAgent.md"
sa_exit=0
sa_out=$(bash "$WRAPPER" --repo-root "$REPO_ROOT" --files "$SSOT_PY" "$ADR082" "$ROSTER" 2>&1) || sa_exit=$?
if [ "$sa_exit" -eq 0 ]; then
  echo "OK PASS: AC-3 self-application — 산출물 3종(lint docstring/ADR-082 §결정16/Layer1 mandate) self-PASS (exit 0)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-3 self-application — 자기 산출물이 자기 게이트에 hit (exit $sa_exit)"
  echo "  output: $sa_out"
  FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — over-claim 검출/정직 미검출/mutation-kill/precision/DoS-bound/self-application 결박"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
