#!/usr/bin/env bash
# tests/scripts/test_check-force-push-base-advance.sh
# CFP-2490 / ADR-135 (Epic CFP-2481 E2) — Discriminating self-test for
#   scripts/lib/check_force_push_base_advance.py (force-push pre-flight base-advance L2 detect).
#
# 배경: own-branch force-push race-guard 의 L2 사후 detect 가 hollow(always-PASS) 가 아님을 보증.
#   discriminating fixture = 임시 git repo 를 만들어 base/head ancestry 를 실제로 구성하고, py SSOT
#   가 base-advance / divergence / force(non-ff) 를 *동작으로* 구분하는지 exit code 로 assert.
#
# self-contained bash (bats 미사용 — test_check-responsibility-topology.sh 답습).
#   각 케이스마다 mktemp -d 로 격리 git repo 를 만들고 --base/--head ref 로 py 를 호출한다.
#
# Discriminating 의무 (change-plan §8.1): 단순 "exit 0 = PASS" 는 non-discriminating → 금지.
#   exit code 분기(0=clean / 1=base-advance·divergence)를 케이스별로 assert.
#   ★ T-B-force (force vs non-force 판별, 설계리뷰 FIX iter1): non-ff(diverged) fixture 가 detect 되고
#     fast-forward(non-force) fixture 는 detect 안 되는 두 동작 차이가 함께여야 PASS (무차별 = hollow).
#
# Mutation-RED 입증 (change-plan §8.1 T-B4): py SSOT 의 detect 로직을 always-PASS(return EXIT_PASS)
#   로 mutate 하면 — T-B1(base-advance)/T-B3(divergence)/T-B-force 가 FAIL 해야(mutant kill).
#   (수동 mutation-RED: check_force_push_base_advance.py 의 `if violations:` 블록을 `if False:` 로
#    임시 변경 → 본 테스트 FAIL 확인 → 원복.)
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates base-advance/divergence/force detect)
#  1 = any fixture fails (detect 가 hollow 또는 회귀)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-force-push-base-advance.sh"
PY="$REPO_ROOT/scripts/lib/check_force_push_base_advance.py"

PASS=0
FAIL=0

# git author env (격리 repo commit 가능하도록 — CI 에 user.* 미설정일 수 있음).
export GIT_AUTHOR_NAME="t" GIT_AUTHOR_EMAIL="t@t" GIT_COMMITTER_NAME="t" GIT_COMMITTER_EMAIL="t@t"

# ─────────────────────────────────────────────────────────────────────────────
# mk_commit <dir> <file> <content> <msg> — dir(git repo) 에 commit 1개 추가, SHA echo.
# ─────────────────────────────────────────────────────────────────────────────
mk_commit() {
  local dir="$1" file="$2" content="$3" msg="$4"
  ( cd "$dir" && echo "$content" > "$file" && git add "$file" && git commit -q -m "$msg" )
  ( cd "$dir" && git rev-parse HEAD )
}

# ─────────────────────────────────────────────────────────────────────────────
# run_case <name> <repo_dir> <base_ref> <head_ref> <expected_exit> <description>
#   py 를 격리 repo 안에서 --base/--head 로 호출 → exit code assert.
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" repo="$2" base="$3" head="$4" expected_exit="$5" description="$6"
  local out ec=0
  out=$( cd "$repo" && python3 "$PY" --base "$base" --head "$head" 2>&1 ) || ec=$?
  if [ "$ec" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $ec) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name — expected exit $expected_exit, got $ec"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# python3 미설치 = setup-error skip (CI 는 setup-python 보장).
if ! command -v python3 >/dev/null 2>&1; then
  echo "✗ FAIL: python3 미설치 — 본 discriminating test 실행 불가 (setup-error)"
  exit 1
fi

# ═════════════════════════════════════════════════════════════════════════════
# T-B2 (clean GREEN): head == base 또는 head 가 base 의 descendant (fast-forward) → PASS (exit 0).
#   linear history: base=C1, head=C2(child of C1). head..base BEHIND=0 + base 가 head ancestor → clean.
# ═════════════════════════════════════════════════════════════════════════════
R_CLEAN=$(mktemp -d)
( cd "$R_CLEAN" && git init -q )
C1=$(mk_commit "$R_CLEAN" a.txt "1" "c1")
( cd "$R_CLEAN" && git branch base )         # base = C1
C2=$(mk_commit "$R_CLEAN" a.txt "2" "c2")     # head(HEAD) = C2 (descendant of base)
run_case "T-B2-clean" "$R_CLEAN" "base" "HEAD" 0 \
  "head 가 base 의 descendant (fast-forward) → base-advance/divergence 0 (clean GREEN)"

# ═════════════════════════════════════════════════════════════════════════════
# T-B1 (base-advance detect): base 가 head 보다 앞섬 (head..base BEHIND>0) → detect (exit 1).
#   base=C2, head=C1 (base 가 head 의 1 커밋 descendant). `--force-with-lease` 가 못 잡는 base 진행.
#   주: 이 경우 base 가 head 의 descendant 라 divergence 는 false(ancestor) → base-advance 단독 detect.
# ═════════════════════════════════════════════════════════════════════════════
run_case "T-B1-base-advance" "$R_CLEAN" "HEAD" "base" 1 \
  "base(=C2) 가 head(=base ref C1) 보다 1 커밋 앞섬 → base-advance detect (exit 1)"

# ═════════════════════════════════════════════════════════════════════════════
# T-B3 / T-B-force (divergence = non-fast-forward, force-push 의심): base 와 head 가 갈라짐.
#   공통 조상 C1 에서 base=C1→Bx (다른 commit), head=C1→Hx (다른 commit). base 가 head 의 ancestor
#   아님 = diverged = non-ff = force-push 시 ancestry corruption 위험 → detect (exit 1).
#   ★ T-B-force discriminating: 본 divergence(non-ff) 케이스는 detect 되고(아래), T-B2 fast-forward
#     (non-force)는 detect 안 됨(위) — 두 동작 차이가 함께여야 force/non-force 판별이 hollow 아님.
# ═════════════════════════════════════════════════════════════════════════════
R_DIV=$(mktemp -d)
( cd "$R_DIV" && git init -q )
D1=$(mk_commit "$R_DIV" a.txt "1" "d1")
( cd "$R_DIV" && git branch base )            # base 시작점 = D1
DH=$(mk_commit "$R_DIV" h.txt "head" "head-commit")   # head(HEAD) = D1→DH
( cd "$R_DIV" && git checkout -q base && echo "base" > b.txt && git add b.txt && git commit -q -m "base-commit" )  # base = D1→DB (diverged)
( cd "$R_DIV" && git checkout -q - 2>/dev/null || git checkout -q master 2>/dev/null || git checkout -q main 2>/dev/null || true )
run_case "T-B3-divergence-force" "$R_DIV" "base" "HEAD" 1 \
  "base 와 head 가 공통 조상에서 갈라짐 (non-ff/diverged = force-push 의심) → detect (exit 1)"

# ═════════════════════════════════════════════════════════════════════════════
# T-B-force-nonforce-discriminating: force(non-ff) ↔ non-force(ff) 가 다른 exit 를 내는지 직접 대조.
#   non-force(ff, T-B2 형) = exit 0, force(non-ff, T-B3 형) = exit 1. 무차별이면 hollow.
# ═════════════════════════════════════════════════════════════════════════════
ec_ff=0;  ( cd "$R_CLEAN" && python3 "$PY" --base base --head HEAD >/dev/null 2>&1 ) || ec_ff=$?
ec_nff=0; ( cd "$R_DIV"   && python3 "$PY" --base base --head HEAD >/dev/null 2>&1 ) || ec_nff=$?
if [ "$ec_ff" -eq 0 ] && [ "$ec_nff" -eq 1 ]; then
  echo "✓ PASS: T-B-force-discriminating — non-force(ff)=exit0 ∧ force(non-ff)=exit1 동작 차이 (force 판별 hollow 아님)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-B-force-discriminating — force/non-force 무차별 (ff=$ec_ff non-ff=$ec_nff, 기대 0/1) = hollow"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# T-B5 (graceful data-absence fail-open): base ref 미해결 (존재하지 않는 ref) → honest no-op (exit 0).
#   offline/shallow/single-commit 동형 — base 미해결 = 비교 비대상 fail-open (false-PASS 아닌 no-op).
# ═════════════════════════════════════════════════════════════════════════════
run_case "T-B5-graceful-absent-base" "$R_CLEAN" "no-such-ref-xyz" "HEAD" 0 \
  "base ref 미해결 → data-absence fail-open (exit 0 honest no-op, change-plan §7.4/§7.5)"

# ═════════════════════════════════════════════════════════════════════════════
# T-B6 (setup-error fail-closed): git work tree 아닌 디렉터리 → exit 2 (fail-closed).
# ═════════════════════════════════════════════════════════════════════════════
R_NOGIT=$(mktemp -d)
ec=0; ( cd "$R_NOGIT" && python3 "$PY" --base main --head HEAD >/dev/null 2>&1 ) || ec=$?
if [ "$ec" -eq 2 ]; then
  echo "✓ PASS: T-B6-setup-error (exit 2) — non-git dir → fail-closed (exit 2)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-B6-setup-error — expected exit 2 (fail-closed), got $ec"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# T-B-wrapper (thin wrapper passthrough): bash thin wrapper 가 py exit code 를 그대로 전달하는지.
# ═════════════════════════════════════════════════════════════════════════════
ec=0; ( cd "$R_DIV" && bash "$SCRIPT" --base base --head HEAD >/dev/null 2>&1 ) || ec=$?
if [ "$ec" -eq 1 ]; then
  echo "✓ PASS: T-B-wrapper (exit 1) — thin wrapper(ADR-061) exit code passthrough"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-B-wrapper — expected exit 1 passthrough, got $ec"
  FAIL=$((FAIL+1))
fi

# cleanup
rm -rf "$R_CLEAN" "$R_DIV" "$R_NOGIT"

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2490 force-push base-advance/divergence L2 detect)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (change-plan §8.1 T-B4 — hollow 검사 차단):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "Mutation (check_force_push_base_advance.py 의 'if violations:' → 'if False:' always-PASS)"
  echo "  → T-B1-base-advance FAIL (exit 0, 기대 1) = RED"
  echo "  → T-B3-divergence-force FAIL (exit 0, 기대 1) = RED"
  echo "  → T-B-force-discriminating FAIL (non-ff 도 exit 0 = 무차별) = RED"
  echo "  → T-B2-clean / T-B5-graceful GREEN 유지 = 케이스 분리 (hollow 아님 증명)"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
