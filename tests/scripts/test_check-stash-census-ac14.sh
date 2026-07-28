#!/usr/bin/env bash
# CFP-2822 Phase 2 — multi-repo stash census self-test (AC-14)
#
# 계약 SSOT: change-plan cfp-2822 §3.5 flat sibling / §7.4.1 aging / §8.1 AC-14 / Story AC-14 /
#           §2.3 #3 (stash 자동삭제 = Non-goal 확정) / INV-3.
# 대상 production: scripts/lib/check_stash_aging_census.py (stash_census / repo_stash_census / stash_entries).
#
# AC-14: repo 별 stash 건수 = N ∧ 최고령 age 리포트 ∧ age>임계 재알림(aging) ∧ **자동 삭제 실행 0**
#   (git stash 무만료 = 의도적 사용자 데이터, Non-goal). git 판정불능 → INCONCLUSIVE(삭제 안 함).
#
# anti-theater: count = 실 git stash 개수 계측(하드코딩 아님) + 삭제 0 을 census 전/후 stash list
#   개수 불변으로 입증(가시화만) + aging BVA(old stash → AGING 태그 ∧ recent-only → 무태그).
# born-broken: age = GIT_COMMITTER_DATE 절대 epoch(TZ-독립) / repo 경로 한글·공백.
#
# Exit: 0 (all pass) / 1 (any fail).

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="$REPO_ROOT/scripts/lib"
PY="${PYTHON:-python3}"; command -v "$PY" >/dev/null 2>&1 || PY=python
export CFP2822_LIBDIR="$LIB_DIR"
command -v git >/dev/null 2>&1 || { echo "FAIL: git 부재"; exit 1; }

PASS=0; FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS + 1)); }
bad() { echo "FAIL: $1"; [ -n "${2:-}" ] && echo "  $2"; FAIL=$((FAIL + 1)); }

TMP=$(mktemp -d)
REPO="$TMP/작업 공간/stash repo"
mkdir -p "$REPO"; git init -q "$REPO"
(
  cd "$REPO"
  git config user.email t@t.local; git config user.name t; git config commit.gpgsign false
  echo a > f.txt; git add f.txt; git -c commit.gpgsign=false commit -qm init
  echo b >> f.txt; git stash push -qm s1
  echo c >> f.txt; git stash push -qm s2
  old=$(( $(date +%s) - 30 * 86400 ))     # age>7d 절대 epoch (TZ-독립)
  echo d >> f.txt; GIT_COMMITTER_DATE="@$old +0000" GIT_AUTHOR_DATE="@$old +0000" git stash push -qm sOLD
) 2>/dev/null

before=$(git -C "$REPO" stash list | grep -c . )
export CFP2822_REPO="$REPO"
export CFP2822_NONGIT="$TMP/non-git dir"; mkdir -p "$TMP/non-git dir"

out=$("$PY" - <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_stash_aging_census as s
repo = os.environ["CFP2822_REPO"]; nongit = os.environ["CFP2822_NONGIT"]
# multi-repo dedup: 같은 repo 2회 → 1회 집계.
cen = s.stash_census([repo, repo, nongit])
print("TOTAL=%d" % cen["total_stashes"])
print("REPOS=%d" % cen["repos_with_stash"])
print("AGING=%d" % len(cen["aging"]))
print("OLDEST_DAYS=%d" % ((cen["oldest_age"] or 0) // 86400))
# INCONCLUSIVE (non-git) — stash_entries None
print("NONGIT_ENTRIES=%s" % (s.stash_entries(nongit) is None))
PY
)
ec=$?
after=$(git -C "$REPO" stash list | grep -c . )

# count = N (3)
if printf '%s' "$out" | grep -q "TOTAL=3"; then ok "AC-14 stash count = 3 (실 git stash 계측)"; else bad "AC-14 TOTAL=3 기대" "out=<<$out>>"; fi
# 자동 삭제 0 — census 전/후 stash list 개수 불변
if [ "$before" = "3" ] && [ "$after" = "3" ]; then ok "AC-14 자동 삭제 0 (census 전/후 stash 개수 불변: $before→$after, Non-goal)"; else bad "AC-14 삭제 0 기대(3→3)" "before=$before after=$after"; fi
# multi-repo dedup — 같은 repo 2회 지정해도 repos_with_stash=1
if printf '%s' "$out" | grep -q "REPOS=1"; then ok "AC-14 multi-repo dedup: 같은 repo 2회 → 1회 집계"; else bad "AC-14 REPOS=1 기대" "out=<<$out>>"; fi
# aging — old stash(30d) → age>임계(7d) 재알림 대상
if printf '%s' "$out" | grep -q "AGING=1" && printf '%s' "$out" | grep -qE "OLDEST_DAYS=(2[0-9]|3[0-9])"; then
  ok "AC-14 aging: 최고령 stash age>임계(7d) → 재알림 대상(AGING=1, oldest~30d)"
else bad "AC-14 aging 검출 기대(AGING=1, oldest~30d)" "out=<<$out>>"; fi
# INCONCLUSIVE — non-git → 판정불능(삭제 안 함)
if printf '%s' "$out" | grep -q "NONGIT_ENTRIES=True"; then ok "AC-14 non-git → INCONCLUSIVE(stash_entries None, 삭제 안 함)"; else bad "AC-14 non-git INCONCLUSIVE 기대" "out=<<$out>>"; fi

rm -rf "$TMP"
echo ""
echo "============================================"
echo "AC-14 stash census self-test — Total: PASS=$PASS FAIL=$FAIL (py exit=$ec)"
echo "============================================"
[ "$FAIL" -eq 0 ] && [ "$ec" -eq 0 ] && exit 0 || exit 1
