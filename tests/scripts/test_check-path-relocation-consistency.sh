#!/usr/bin/env bash
# tests/scripts/test_check-path-relocation-consistency.sh
# CFP-2661 Phase 2 (구현 lane) — Discriminating self-test for
#   scripts/lib/check_path_relocation_consistency.py relocation-ledger 구동 dead-path 재유입 차단 lint.
#
# ★ hollow-gate 아님의 유일 증명 (Change Plan §8 / Story §7.5) — presence-only 금지, 실 exit code 결박:
#   (a) positive anchor (shell array / python literal / yaml frontmatter sequence / D15 locked) = MUST 검출 + mutation-kill
#   (b) negative set 0-FP (union construct / doc-locations dual-variant / append-only inert)
#   (c) born-hollow guard — candidate 0 입력 → PASS 아니라 FAIL(exit 3) (AC-15, "scanned 0" ≠ "violations 0")
#   (d) construct-vs-file-level FN — file 은 dual 인데 construct 는 dead → file-level 미검출 / construct-level 검출 (AC-14)
#   (e) field-predicate discriminating — parallel_edit==locked must-flag / append-only must-NOT-flag (D15/active_when)
#   + PERF DoS fixture <5s (born-safe bound) + 실 코퍼스 precision proof (candidate ≥ floor, baseline 후 violation 0).
#   (ADR-119 / CFP-2545 execution-backed).
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-path-relocation-consistency.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_path_relocation_consistency.py"

PASS=0
FAIL=0

# post-fix census floor (CFP-2661 Phase 2 corrected repo 실측 pin — Change Plan §3.3 "pre-fix 73 pin 금지",
#   설계 estimate ≈70 supersede by construct-count 실측 39; ≥ floor 하한, ADR append-mostly 로 안정).
FLOOR=30

FIXTURE_LEDGER='relocations:
  - old: docs/adr
    new: archive/adr
    carrier: CFP-2661
    surfaces:
      - shell_array
      - python_literal
      - yaml_sequence
    active_when:
      field: parallel_edit
      equals: locked'

# ─────────────────────────────────────────────────────────────────────────────
# lint_case: fixture 파일 1개 + ledger 를 tmpdir 코퍼스 위치에 배치 → lint scoped 실행 → exit + surface 대조
#   인자: <name> <expected_exit> <flag_substr|NOFLAG|""> <corpus_relpath> <fixture_content>
# ─────────────────────────────────────────────────────────────────────────────
lint_case() {
  local name="$1" expected_exit="$2" flag_substr="$3" relpath="$4" content="$5"
  local exit_code=0 out tmpdir ok=1
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  mkdir -p "$tmpdir/docs"
  printf '%s\n' "$FIXTURE_LEDGER" > "$tmpdir/docs/path-relocation-ledger.yaml"
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

# mutant_case: SSOT 를 python 문자열치환으로 mutate → fixture 실행 → 오분류 확증 (mutation-kill)
mutant_case() {
  local name="$1" kind="$2" expected_exit="$3" relpath="$4" content="$5"
  local exit_code=0 out tmpdir mutant ok=1
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  mkdir -p "$tmpdir/docs"
  printf '%s\n' "$FIXTURE_LEDGER" > "$tmpdir/docs/path-relocation-ledger.yaml"
  mkdir -p "$tmpdir/$(dirname "$relpath")"
  printf '%s\n' "$content" > "$tmpdir/$relpath"
  mutant="$tmpdir/mutant.py"

  python3 - "$SSOT_PY" "$mutant" "$kind" <<'PY'
import sys
src_path, out_path, kind = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src_path, encoding="utf-8").read()
if kind == "no_cooccur":
    # co-occurrence 검출 무력화 → NEW 미동반 violation 이 안 잡힘 (RED — positive fixture 미검출).
    s2 = s.replace("if new not in c.text:", "if False:", 1)
elif kind == "no_predicate":
    # active_when predicate 무력화 (항상 active) → append-only inert 가 flag 됨 (RED — negative 오검출).
    s2 = s.replace("def _is_active(construct, active_when):",
                   "def _is_active(construct, active_when):\n    return True  # MUTANT", 1)
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
echo " CFP-2661: path-relocation-consistency — discriminating self-test"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── (a) Positive anchors (dead-path 단독 지목 → MUST 검출, exit 1) ──"

# shell array — docs/adr 단독 (union 미동반)
lint_case "TC-A1 shell array docs/adr 단독" 1 "::warning::" "scripts/fix.sh" \
'#!/usr/bin/env bash
EXEMPT_FILES=(
  "docs/adr/ADR-064-decision-principle-mandate.md"
)'

# python literal — docs/adr 단독 set
lint_case "TC-A2 python set docs/adr 단독" 1 "::warning::" "scripts/lib/fix.py" \
'EXEMPT_PATHS = {"docs/adr/ADR-RESERVATION.md"}'

# yaml frontmatter allow sequence — docs/adr 단독 (D5/D13-frontmatter construct)
lint_case "TC-A3 agent-md frontmatter allow docs/adr 단독" 1 "::warning::" "plugins/p/agents/fix.md" \
'---
name: Fix
permissions:
  allow:
    - Read
    - Edit(docs/adr/**)
    - Write(docs/adr/**)
---
body'

# D15 field-predicate locked (must-flag)
lint_case "TC-A4 section-ownership locked (D15 must-flag)" 1 "::warning::" "docs/parallel-work/fix.yaml" \
'owned_sections:
  - file: docs/adr/ADR-083-consumer-applicability-filter.md
    section: "x"
    parallel_edit: locked'

echo
echo "── (b) Negative set (union / dual-path / inert → MUST 미검출, exit 0) ──"

# union construct — docs/adr ∪ archive/adr 동반
lint_case "TC-B1 shell array union (docs∪archive)" 0 "NOFLAG" "scripts/fix.sh" \
'#!/usr/bin/env bash
EXEMPT_FILES=(
  "docs/adr/ADR-064-decision-principle-mandate.md"
  "archive/adr/ADR-064-decision-principle-mandate.md"
)'

# python union
lint_case "TC-B2 python set union" 0 "NOFLAG" "scripts/lib/fix.py" \
'EXEMPT_PATHS = {"docs/adr/ADR-RESERVATION.md", "archive/adr/ADR-RESERVATION.md"}'

# frontmatter union (allow both)
lint_case "TC-B3 agent-md frontmatter union" 0 "NOFLAG" "plugins/p/agents/fix.md" \
'---
name: Fix
permissions:
  allow:
    - Edit(docs/adr/**)
    - Edit(archive/adr/**)
    - Write(docs/adr/**)
    - Write(archive/adr/**)
---
body'

# doc-locations dual-variant (single_repo docs/adr + dogfood archive/adr = sibling keys)
lint_case "TC-B4 doc-locations dual-variant (sibling co-occur)" 0 "NOFLAG" "docs/doc-locations.yaml" \
'adr:
  variants:
    single_repo: "<owner>/docs/adr/ADR-NNN.md"
    dogfood: "archive/adr/ADR-NNN.md"'

# field-predicate append-only (inert — must-NOT-flag)
lint_case "TC-B5 section-ownership append-only (inert)" 0 "NOFLAG" "docs/parallel-work/fix.yaml" \
'owned_sections:
  - file: docs/adr/ADR-076-declarative-reconciliation-upgrade.md
    section: "x"
    parallel_edit: append-only'

echo
echo "── (c) born-hollow guard (candidate 0 → PASS 아니라 FAIL, exit 3, AC-15) ──"

# docs/adr 리터럴 0 = relocation-relevant construct 0 = born-hollow
lint_case "TC-C1 empty scope → born-hollow FAIL (exit 3)" 3 "FAIL-CLOSED" "scripts/fix.sh" \
'#!/usr/bin/env bash
echo "no relocation-relevant construct here"
X=(1 2 3)'

echo
echo "── (d) construct-vs-file-level FN (AC-14 — file dual, construct dead) ──"

# file 은 archive/adr 를 다른 construct 에 보유하나, EXEMPT_PATHS construct 는 docs/adr 단독 → construct-level 검출
lint_case "TC-D1 construct-vs-file FN (file dual, construct dead)" 1 "::warning::" "scripts/lib/fix.py" \
'ALLOWLIST_PREFIXES = ["archive/adr/ADR-099"]
EXEMPT_PATHS = {"docs/adr/ADR-RESERVATION.md"}'

echo
echo "── (e) mutation-kill (로직 load-bearing 실증) ──"

# MK-1: co-occurrence 검출 제거 → positive fixture(TC-A1) 미검출 (exit 0 = born-hollow 아님, candidate≥1 violation 0)
mutant_case "MK-1 no_cooccur → positive 미검출(RED, exit 0)" no_cooccur 0 "scripts/fix.sh" \
'#!/usr/bin/env bash
EXEMPT_FILES=(
  "docs/adr/ADR-064-decision-principle-mandate.md"
)'

# MK-2: active_when predicate 제거 → append-only inert 가 flag 됨 (exit 1 = negative 오검출)
mutant_case "MK-2 no_predicate → append-only 오검출(RED, exit 1)" no_predicate 1 "docs/parallel-work/fix.yaml" \
'owned_sections:
  - file: docs/adr/ADR-076-declarative-reconciliation-upgrade.md
    section: "x"
    parallel_edit: append-only'

echo
echo "── PERF (born-safe DoS bound — 적대적 초장문 라인 < 5s) ──"
perf_tmp=$(mktemp -d)
mkdir -p "$perf_tmp/docs" "$perf_tmp/scripts"
printf '%s\n' "$FIXTURE_LEDGER" > "$perf_tmp/docs/path-relocation-ledger.yaml"
python3 - "$perf_tmp/scripts/dos.sh" <<'PYEOF'
import sys
# 단일 물리라인 400k*4 = 1.6MB, docs/adr 리터럴 포함 (truncate 후 co-occur 판정).
open(sys.argv[1], "w", encoding="utf-8").write('ARR=("docs/adr/x" ' + '"a" '*400000 + ')\n')
PYEOF
perf=$(python3 - "$SSOT_PY" "$perf_tmp" <<'PYEOF'
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
if awk "BEGIN{exit !($perf < 5.0)}"; then
  echo "OK PASS: PERF DoS 1.6MB-line wall=${perf}s (<5s — born-safe bound 성립)"
  PASS=$((PASS+1))
else
  echo "X FAIL: PERF DoS 1.6MB-line wall=${perf}s (>=5s — bound 파손/O(n²) 회귀 의심)"
  FAIL=$((FAIL+1))
fi

echo
echo "── 실 코퍼스 precision proof (candidate ≥ floor, baseline 후 violation 0) ──"
rc_exit=0
rc_out=$(bash "$WRAPPER" --repo-root "$REPO_ROOT" 2>&1) || rc_exit=$?
# candidate ≥ floor (non-vacuity — anti born-hollow) 파싱
cand=$(printf '%s\n' "$rc_out" | grep -oE "candidates_scanned=[0-9]+" | head -1 | grep -oE "[0-9]+" || echo 0)
if [ "$rc_exit" -eq 0 ] && [ "${cand:-0}" -ge "$FLOOR" ]; then
  echo "OK PASS: RC precision proof (exit 0, candidates_scanned=$cand ≥ floor $FLOOR, baseline 후 violation 0)"
  PASS=$((PASS+1))
else
  echo "X FAIL: RC precision proof — exit=$rc_exit candidates_scanned=$cand (floor=$FLOOR)"
  echo "  output: $rc_out"
  FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — positive/negative/born-hollow/construct-FN/field-predicate/mutation-kill/PERF/precision 결박"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
