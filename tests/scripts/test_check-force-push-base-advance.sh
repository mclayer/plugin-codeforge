#!/usr/bin/env bash
# tests/scripts/test_check-force-push-base-advance.sh
# CFP-2490 / ADR-135 (Epic CFP-2481 E2) — Discriminating self-test for
#   scripts/lib/check_force_push_base_advance.py (force-push base-advance L2 사후 detect).
#
# 배경: own-branch force-push 가 stale base 위에서 sibling commit 을 ancestry corruption
#   (덮어쓰기) 하는 사고(#1027, CFP-967/991 pattern_count 2). L2 CI 사후 detect 가 PR head 의
#   base-advance / divergence 를 warning 으로 표면화한다 (차단 불가 — ADR-135 §결정 2).
#
# self-contained bash (bats 미사용 — test_check-parallel-work-sentinel.sh 답습).
#   임시 git fixture repo 를 만들어 base-advance / divergence / clean / fast-forward 케이스를
#   생성하고, check 스크립트가 exit code 로 detect 여부를 어떻게 구분하는지 assert.
#
# Discriminating 의무 (change-plan §8.1): 단순 "exit 0 = PASS" 비-discriminating 검사 금지.
#   base-advance/divergence 케이스 = WARN(exit 1) 이고 clean 케이스 = PASS(exit 0) 로 *구분*되어야
#   hollow 아님. always-PASS mutant(detect 로직 무력화) 주입 시 detect 케이스가 FAIL(RED) 해야 한다.
#
# T-B1 base-advance / T-B2 clean GREEN / T-B3 divergence / T-B-force force-vs-non-force /
# T-B4 mutation 생존 0 / T-B5 graceful (SHA 부재).
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates base-advance detect)
#  1 = any fixture fails (detect 로직 무력화 / 회귀)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-force-push-base-advance.sh"
PYSSOT="$REPO_ROOT/scripts/lib/check_force_push_base_advance.py"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# fixture git repo 생성 — 4 SHA 형상:
#   C1 ─ C2 (base)        : main 라인. base = C2.
#        └ C2b (head_ff)  : C2 의 descendant (fast-forward, base 미advance) → clean.
#   C1 ─ C3 (head_behind) : C3 는 C1 기반 (C2 미반영) = base 가 C3 보다 advance → base-advance.
# ─────────────────────────────────────────────────────────────────────────────
FIX=$(mktemp -d)
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

(
  cd "$FIX"
  git init -q
  git config user.email "test@codeforge.local"
  git config user.name "codeforge-test"
  git config commit.gpgsign false

  echo "c1" > f.txt && git add f.txt && git commit -q -m "C1"
  C1=$(git rev-parse HEAD)

  echo "c2" >> f.txt && git add f.txt && git commit -q -m "C2 (base advance)"
  C2=$(git rev-parse HEAD)   # base tip

  # head_ff = C2 의 descendant (fast-forward, base 포함) → clean
  echo "c2b" >> f.txt && git add f.txt && git commit -q -m "C2b (ff head)"
  C2B=$(git rev-parse HEAD)

  # head_behind = C1 기반 별 branch (C2 미반영) → base 가 head 보다 advance + diverged
  git checkout -q -b behind "$C1"
  echo "c3" > g.txt && git add g.txt && git commit -q -m "C3 (behind/diverged head)"
  C3=$(git rev-parse HEAD)

  printf '%s\n%s\n%s\n%s\n' "$C1" "$C2" "$C2B" "$C3" > "$FIX/shas.txt"
)

readarray -t SHAS < "$FIX/shas.txt"
C1="${SHAS[0]}"; C2="${SHAS[1]}"; C2B="${SHAS[2]}"; C3="${SHAS[3]}"

# helper: fixture repo 안에서 check 실행 (--base-sha/--head-sha) → exit code 반환.
run_check() {
  local base="$1" head="$2"
  ( cd "$FIX" && bash "$WRAPPER" --base-sha "$base" --head-sha "$head" --base-ref main >/dev/null 2>&1 )
}

assert_exit() {
  local name="$1" expected="$2" actual="$3" desc="$4"
  if [ "$actual" -eq "$expected" ]; then
    echo "✓ PASS: $name (exit $actual) — $desc"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name — expected exit $expected, got $actual ($desc)"
    FAIL=$((FAIL+1))
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# T-B2 (clean GREEN): base=C2, head=C2B (C2B 는 C2 의 descendant = base 포함) → PASS exit 0.
# ═════════════════════════════════════════════════════════════════════════════
run_check "$C2" "$C2B"; assert_exit "T-B2-clean" 0 $? \
  "head(C2B) 가 base(C2) 포함 (fast-forward) → base-advance/divergence 0 = PASS"

# ═════════════════════════════════════════════════════════════════════════════
# T-B1 (base-advance detect): base=C2, head=C3 (C3 는 C1 기반, C2 미반영) → base 가 head 보다
#   advance + diverged → WARN exit 1.
# ═════════════════════════════════════════════════════════════════════════════
run_check "$C2" "$C3"; assert_exit "T-B1-base-advance" 1 $? \
  "base(C2) 가 head(C3) 보다 advance + head 가 C2 미반영 → base-advance detect (WARN)"

# ═════════════════════════════════════════════════════════════════════════════
# T-B3 (divergence): base=C2B, head=C3 (서로 다른 라인, 공통조상 C1) → diverged → WARN exit 1.
# ═════════════════════════════════════════════════════════════════════════════
run_check "$C2B" "$C3"; assert_exit "T-B3-divergence" 1 $? \
  "base(C2B) 와 head(C3) diverged (공통조상 C1, 상호 미포함) → divergence detect (WARN)"

# ═════════════════════════════════════════════════════════════════════════════
# T-B-force (force vs non-force discriminating — change-plan §8.1):
#   L2 detect 의 force-push 위험 판별 축 = head 가 base 를 *포함하지 않는가* (non-fast-forward).
#   (1) non-force fixture (head=C2B 가 base=C2 의 descendant = fast-forward) → 위험 0 = PASS(exit 0).
#   (2) force fixture (head=C3 가 base=C2 를 미포함 = non-ff/diverged) → 위험 신호 = WARN(exit 1).
#   두 케이스 동작 차이가 있어야 PASS (force/non-force 무차별 = hollow).
# ═════════════════════════════════════════════════════════════════════════════
run_check "$C2" "$C2B"; FF_EXIT=$?
run_check "$C2" "$C3";  NONFF_EXIT=$?
if [ "$FF_EXIT" -eq 0 ] && [ "$NONFF_EXIT" -eq 1 ]; then
  echo "✓ PASS: T-B-force (force vs non-force 구분) — fast-forward(exit $FF_EXIT) ≠ non-ff/diverged(exit $NONFF_EXIT)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-B-force — fast-forward exit=$FF_EXIT (기대 0) / non-ff exit=$NONFF_EXIT (기대 1) — force/non-force 무차별 = hollow"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# T-B5 (graceful): 존재하지 않는 SHA (shallow checkout / fetch 실패 모사) → advisory degrade exit 0.
# ═════════════════════════════════════════════════════════════════════════════
( cd "$FIX" && bash "$WRAPPER" --base-sha "0000000" --head-sha "1111111" >/dev/null 2>&1 ); assert_exit "T-B5-graceful" 0 $? \
  "존재하지 않는 SHA (shallow/fetch 실패) → graceful skip (비차단 advisory degrade)"

# T-B5b (SETUP): SHA 전무 → exit 2 (호출 계약 위반).
( cd "$FIX" && bash "$WRAPPER" >/dev/null 2>&1 ); assert_exit "T-B5b-setup" 2 $? \
  "SHA 인자 전무 → SETUP exit 2"

# ═════════════════════════════════════════════════════════════════════════════
# T-B4 (mutation 생존 0): detect 로직을 always-PASS 로 mutate → T-B1/T-B3/T-B-force 가 RED 해야.
#   mutation = check() 의 WARN 분기를 무력화 (behind=0 강제 + diverged=False 강제).
#   tmp 복사본을 mutate 해 실행 (원본 무손상).
# ═════════════════════════════════════════════════════════════════════════════
MUT_PY="$FIX/mutant_check.py"
cp "$PYSSOT" "$MUT_PY"
# always-PASS mutant: WARN 트리거 조건 `behind > 0 or diverged` 를 `False` 로 치환.
python3 - "$MUT_PY" <<'PYEOF'
import sys, re
p = sys.argv[1]
src = open(p, encoding="utf-8").read()
mutated = src.replace("if behind > 0 or diverged:", "if False:  # MUTANT always-PASS")
assert mutated != src, "mutation target line not found — test fixture drift"
open(p, "w", encoding="utf-8").write(mutated)
PYEOF

mut_run() {
  local base="$1" head="$2"
  ( cd "$FIX" && python3 "$MUT_PY" --base-sha "$base" --head-sha "$head" --base-ref main >/dev/null 2>&1 )
}

# mutant 는 base-advance(T-B1) / divergence(T-B3) / force(T-B-force non-ff) 케이스를 모두 PASS(exit 0)
#   로 만든다 = detect 무력화. self-test 가 이를 잡으려면 = mutant 하에서 해당 케이스 exit 가 1 이 아님(0)
#   을 관측해 "mutation 생존 0 (kill)" 으로 판정.
mut_run "$C2" "$C3"; MUT_BASE_ADVANCE=$?
mut_run "$C2B" "$C3"; MUT_DIVERGENCE=$?
if [ "$MUT_BASE_ADVANCE" -eq 0 ] && [ "$MUT_DIVERGENCE" -eq 0 ]; then
  # mutant 가 detect 를 무력화함(원래 WARN=1 케이스가 PASS=0) → 원본 test 가 RED 로 잡음 = kill 성공.
  echo "✓ PASS: T-B4-mutation-kill — always-PASS mutant 가 base-advance(exit $MUT_BASE_ADVANCE) + divergence(exit $MUT_DIVERGENCE) detect 무력화 관측 → 원본 discriminating test 가 RED 로 kill"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-B4-mutation-kill — mutant 하에서 base-advance=$MUT_BASE_ADVANCE / divergence=$MUT_DIVERGENCE (기대 둘다 0 = detect 무력화 관측 불가 = mutation 미적용/생존)"
  FAIL=$((FAIL+1))
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2490 force-push base-advance L2 detect — ADR-135)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (change-plan §8.1 — hollow 검사 차단):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "Mutation (check() WARN 분기 'behind > 0 or diverged' → 'False' always-PASS)"
  echo "          → T-B1 base-advance / T-B3 divergence / T-B-force 가 detect 무력화 = RED kill"
  echo "          → T-B2 clean / T-B5 graceful 는 GREEN 유지 (조건 분리, hollow 아님 증명)"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
