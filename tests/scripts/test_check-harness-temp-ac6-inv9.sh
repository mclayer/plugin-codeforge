#!/usr/bin/env bash
# CFP-2822 Phase 2 — harness Temp 관측기 INV-9 self-test (AC-6 1단계, P0)
#
# 계약 SSOT: change-plan cfp-2822 §3.2④ / §8.1 AC-6 (2단계 삭제 실행 0 assert=INV-9) /
#           §8.10 dark-path (1) / Story AC-6 / INV-9 (제3자-소유 삭제 syscall 0).
# 대상 production: scripts/lib/check_harness_temp_residue.py (observe_temp / classify_temp_entry / main).
#
# INV-9 핵심 oracle: 1단계 관측기는 Temp 하위 **삭제 syscall 0** — 실행 전/후 파일 목록 불변.
#   (2단계 삭제는 TEMP_GC_DELETE_ENABLED default-off = §8.10 dark-path status=infeasible landing.)
# git-aware: Temp 내 git worktree(dirty/unpushed) → PRESERVE("temp-git-worktree") fail-safe.
#
# anti-theater: (a) git-aware entry → PRESERVE 사유 방출 ∧ (b) 삭제 후보처럼 보이는 non-git
#   old entry 도 삭제 0 (관측만) — 실행 전/후 파일 bijection 으로 삭제 0 을 강하게 입증.
# born-broken: fixture 이름 한글·공백 / age = touch -d @epoch(TZ-독립) / --temp-root 격리(실 Temp 무접촉).
#
# Exit: 0 (all pass) / 1 (any fail).

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEMP_PY="$REPO_ROOT/scripts/lib/check_harness_temp_residue.py"
PY="${PYTHON:-python3}"; command -v "$PY" >/dev/null 2>&1 || PY=python

PASS=0; FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS + 1)); }
bad() { echo "FAIL: $1"; [ -n "${2:-}" ] && echo "  $2"; FAIL=$((FAIL + 1)); }

OLD=$(( $(date +%s) - 30 * 86400 ))
FIXROOT=$(mktemp -d)/claude
mkdir -p "$FIXROOT"

# (1) 실 git worktree fixture (remote + dirty → git-aware preserve "temp-git-worktree")
gitdir="$FIXROOT/git 세션 dir"; bare="$(dirname "$FIXROOT")/bare.git"
git init -q "$gitdir"
( cd "$gitdir"
  git config user.email t@t.local; git config user.name t; git config commit.gpgsign false
  echo a > a.txt; git add a.txt; git -c commit.gpgsign=false commit -qm init
  git init -q --bare "$bare"; git remote add origin "$bare"; git push -q origin HEAD:refs/heads/main 2>/dev/null
  echo dirty >> a.txt )       # uncommitted dirty → temp-git-worktree
touch -d "@$OLD" "$gitdir"

# (2) non-git old loose 세션 dir (삭제 후보처럼 보이나 observe-only = 삭제 0)
looses="$FIXROOT/loose 세션 dir"; mkdir -p "$looses"; echo junk > "$looses/big.bin"; touch -d "@$OLD" "$looses"

# 실행 전 파일 snapshot (삭제 0 bijection 근거)
before=$(cd "$FIXROOT" && find . | sort)
before_count=$(printf '%s\n' "$before" | grep -c . )

# main() 실행 (TEMP_GC_DELETE_ENABLED 미설정 = 2단계 off). stdout+stderr 캡처.
out=$("$PY" "$TEMP_PY" --temp-root "$FIXROOT" 2>&1)
ec=$?

after=$(cd "$FIXROOT" && find . | sort)
after_count=$(printf '%s\n' "$after" | grep -c . )

# INV-9 (1): 실행 전/후 파일 목록 완전 동일 = 삭제 syscall 0
if [ "$before" = "$after" ]; then
  ok "AC-6/INV-9: Temp 관측 전/후 파일 bijection 일치 (before=$before_count after=$after_count) — 삭제 syscall 0"
else
  bad "AC-6/INV-9: 삭제 발생 (파일 목록 변화)" "before=$before_count after=$after_count"
fi
# INV-9 (2): DONE 마커 + "delete=0" 명시 + exit 0
if [ "$ec" -eq 0 ] && printf '%s' "$out" | grep -q "delete=0"; then
  ok "AC-6/INV-9: DONE + stage1 delete=0 명시 + exit 0"
else
  bad "AC-6/INV-9: DONE delete=0 + exit0 기대" "ec=$ec out=<<$out>>"
fi
# git-aware: git 세션 → PRESERVE(temp-git-worktree)
if printf '%s' "$out" | grep -q "PRESERVE(temp-git-worktree)"; then
  ok "AC-6 git-aware: Temp git worktree(dirty)→PRESERVE(temp-git-worktree) fail-safe"
else
  bad "AC-6 git-aware PRESERVE(temp-git-worktree) 기대" "out=<<$out>>"
fi
# observe 리포트: git/loose 2 entry 관측
if printf '%s' "$out" | grep -qE "OBSERVE .* entries=2"; then
  ok "AC-6 관측 리포트: entries=2 (git + loose 관측)"
else
  bad "AC-6 관측 entries=2 기대" "out=<<$out>>"
fi
# dark-path: TEMP_GC_DELETE_ENABLED 미설정 → STAGE2-DELETE 라인 부재 (gated off, §8.10)
if ! printf '%s' "$out" | grep -q "STAGE2-DELETE"; then
  ok "AC-6 §8.10 dark-path: TEMP_GC_DELETE_ENABLED off → STAGE2-DELETE 미발화 (gated off landing)"
else
  bad "AC-6 dark-path: flag off 인데 STAGE2-DELETE 발화" "out=<<$out>>"
fi

rm -rf "$(dirname "$FIXROOT")"
echo ""
echo "============================================"
echo "AC-6 harness Temp INV-9 self-test — Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
