#!/usr/bin/env bash
# CFP-2822 Phase 2 — INV-1 5종 보존 + AC-12 orphan 3축 분류 self-test (P0)
#
# 계약 SSOT: change-plan cfp-2822 §8.1 (AC-12 fixture + INV-1 5종 P0) / §8.2.3 (INV-1/2/3) /
#           §3.2③ judge / §7.3 삭제 authz / Story AC-7·AC-12 / INV-1·2·3.
# 대상 production: scripts/lib/check_orphan_worktree_classify.py (judge_orphan / orphan_state_signals /
#                 classify_orphan) + templates/scripts/check-worktree-stale.sh (locked flag).
#
# INV-1 5종 보존 fixture (각 양방향 변별 — 보존조건→KEEP+사유 ∧ 조건해제→REMOVE):
#   dirty / unpushed-N-commits / locked / pin / INCONCLUSIVE(network).
#   자동 unlock/force 금지 확인 (locked → 수동 해제만, judge 는 force-remove 안 함).
#
# AC-12 핵심: 등록·존재 여부 자체 ≠ 보존 사유 (상태 신호만 보존 트리거) + 3-case
#   (등록 worktree 위임 / 독립clone 상태검사 / 빈껍데기 안전삭제) + INCONCLUSIVE→보존.
#
# git 판정 = **실 git repo fixture** (Python subprocess 가 stub bash 스크립트를 Windows 에서
#   직접 실행 못 하는 shebang 한계 회피 — 실 git binary 로 dirty/unpushed/remote 실제 상태 생성).
# anti-theater: 각 보존 타입 = 조건 성립→KEEP(정확 사유) ∧ 조건 해제→REMOVE 양방향 (vacuous 아님).
# born-broken: fixture 경로 한글·공백 포함 / age = touch -d @epoch (TZ-독립).
#
# Exit: 0 (all pass) / 1 (any fail).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="$REPO_ROOT/scripts/lib"
STALE_SH="$REPO_ROOT/templates/scripts/check-worktree-stale.sh"
PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || PY=python

PASS=0
FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS + 1)); }
bad() { echo "FAIL: $1"; [ -n "${2:-}" ] && echo "  $2"; FAIL=$((FAIL + 1)); }

OLD_EPOCH=$(( $(date +%s) - 30 * 86400 ))   # age>7d (절대 epoch, TZ-독립)
export CFP2822_LIBDIR="$LIB_DIR"

# ── 실 git repo fixture: <dir> <dirty> <unpushed_n> <has_remote> <bare_parent> ──
# has_remote=1 → bare remote push 로 remote-tracking ref 확립(unpushed 판정 conclusive).
mk_repo() {
  local dir="$1" dirty="$2" unpushed="$3" has_remote="$4" bare="$5"
  mkdir -p "$dir"
  git init -q "$dir"
  (
    cd "$dir" || exit 1
    git config user.email t@t.local; git config user.name t; git config commit.gpgsign false
    echo base > base.txt; git add base.txt; git -c commit.gpgsign=false commit -qm init
    if [ "$has_remote" = "1" ]; then
      git init -q --bare "$bare"
      git remote add origin "$bare"
      git push -q origin HEAD:refs/heads/main 2>/dev/null
    fi
    local i=0
    while [ "$i" -lt "$unpushed" ]; do
      echo "c$i" >> base.txt; git add base.txt; git -c commit.gpgsign=false commit -qm "local$i"; i=$((i + 1))
    done
    [ "$dirty" = "1" ] && echo dirty-uncommitted >> base.txt
    exit 0
  )
}

# judge_orphan(path, 'home-direct', git_exists) → "DECISION|REASON".
judge_probe() {
  local path="$1" git_exists="$2"
  "$PY" - "$path" "$git_exists" <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_orphan_worktree_classify as m
decision, reason, age = m.judge_orphan(sys.argv[1], "home-direct", sys.argv[2] == "1")
print("%s|%s" % (decision, reason))
PY
}

if [ ! -d "$LIB_DIR" ]; then
  bad "scripts/lib 부재" "$LIB_DIR"; echo "Total: PASS=$PASS FAIL=$FAIL"; exit 1
fi
command -v git >/dev/null 2>&1 || { bad "git 부재 — 실 git fixture 불가"; echo "Total: PASS=$PASS FAIL=$FAIL"; exit 1; }

# ─────────────────── INV-1 (1) dirty — 양방향 ───────────────────
tmp=$(mktemp -d)
mk_repo "$tmp/작업 공간/clone dirty" 1 0 1 "$tmp/b1.git"; touch -d "@$OLD_EPOCH" "$tmp/작업 공간/clone dirty"
r=$(judge_probe "$tmp/작업 공간/clone dirty" 1)
[ "$r" = "KEEP|dirty" ] && ok "INV-1 dirty→KEEP(dirty): $r" || bad "INV-1 dirty→KEEP(dirty) 기대" "got=$r"
mk_repo "$tmp/작업 공간/clone clean" 0 0 1 "$tmp/b2.git"; touch -d "@$OLD_EPOCH" "$tmp/작업 공간/clone clean"
r=$(judge_probe "$tmp/작업 공간/clone clean" 1)
[ "$r" = "REMOVE|None" ] && ok "INV-1 dirty 해제(clean·age>7d)→REMOVE: $r" || bad "INV-1 clean→REMOVE 기대" "got=$r"
rm -rf "$tmp"

# ─────────────────── INV-1 (2) unpushed-N — 양방향 ───────────────────
tmp=$(mktemp -d)
mk_repo "$tmp/작업 공간/독립 clone" 0 3 1 "$tmp/b1.git"; touch -d "@$OLD_EPOCH" "$tmp/작업 공간/독립 clone"
r=$(judge_probe "$tmp/작업 공간/독립 clone" 1)
[ "$r" = "KEEP|unpushed-3" ] && ok "INV-1 unpushed-3→KEEP(unpushed-3): $r" || bad "INV-1 unpushed-3→KEEP 기대" "got=$r"
mk_repo "$tmp/작업 공간/pushed clone" 0 0 1 "$tmp/b2.git"; touch -d "@$OLD_EPOCH" "$tmp/작업 공간/pushed clone"
r=$(judge_probe "$tmp/작업 공간/pushed clone" 1)
[ "$r" = "REMOVE|None" ] && ok "INV-1 unpushed 해제(0·age>7d)→REMOVE: $r" || bad "INV-1 unpushed 0→REMOVE 기대" "got=$r"
rm -rf "$tmp"

# ─────────────────── INV-1 (3) pin — 양방향 ───────────────────
tmp=$(mktemp -d)
mk_repo "$tmp/작업 공간/pinned clone" 0 0 1 "$tmp/b1.git"; touch -d "@$OLD_EPOCH" "$tmp/작업 공간/pinned clone"
touch "$tmp/작업 공간/pinned clone/.gc-keep"    # 명시 보존 마커
r=$(judge_probe "$tmp/작업 공간/pinned clone" 1)
[ "$r" = "KEEP|pin" ] && ok "INV-1 pin(.gc-keep)→KEEP(pin, clean·age>7d 여도 마커 우선): $r" || bad "INV-1 pin→KEEP 기대" "got=$r"
rm -f "$tmp/작업 공간/pinned clone/.gc-keep"      # 마커 해제
touch -d "@$OLD_EPOCH" "$tmp/작업 공간/pinned clone"   # 마커 add/rm 로 갱신된 dir mtime 를 age>7d 로 복원
r=$(judge_probe "$tmp/작업 공간/pinned clone" 1)
[ "$r" = "REMOVE|None" ] && ok "INV-1 pin 해제→REMOVE: $r" || bad "INV-1 pin 해제→REMOVE 기대" "got=$r"
rm -rf "$tmp"

# ─────────────────── INV-1 (4) INCONCLUSIVE(network) — 양방향 ───────────────────
tmp=$(mktemp -d)
mk_repo "$tmp/작업 공간/no remote clone" 0 0 0 ""; touch -d "@$OLD_EPOCH" "$tmp/작업 공간/no remote clone"
r=$(judge_probe "$tmp/작업 공간/no remote clone" 1)
[ "$r" = "KEEP|network-inconclusive" ] && ok "INV-1 INCONCLUSIVE(no-remote)→KEEP(network-inconclusive): $r" \
  || bad "INV-1 INCONCLUSIVE→KEEP 기대" "got=$r"
mk_repo "$tmp/작업 공간/has remote clone" 0 0 1 "$tmp/b1.git"; touch -d "@$OLD_EPOCH" "$tmp/작업 공간/has remote clone"
r=$(judge_probe "$tmp/작업 공간/has remote clone" 1)
[ "$r" = "REMOVE|None" ] && ok "INV-1 INCONCLUSIVE 해제(remote·clean·age>7d)→REMOVE: $r" || bad "INV-1 INCONCLUSIVE 해제→REMOVE 기대" "got=$r"
rm -rf "$tmp"

# ─────────────────── INV-1 (5) locked — check-worktree-stale.sh 양방향 ───────────────────
locked_case() {
  local label="$1" locked="$2" expect_prune="$3"
  local h; h=$(mktemp -d)
  local main="$h/작업 공간/main"; local wt="$h/작업 공간/wt/cfp-잠긴 branch"
  mkdir -p "$main" "$wt"; touch -d "@$OLD_EPOCH" "$wt"
  local git="$h/git" gh="$h/gh"
  cat > "$git" <<GST
#!/usr/bin/env bash
if [ "\${1:-}" = "-C" ]; then shift 2; fi
case "\${1:-}" in
  rev-parse) echo "$main"; exit 0 ;;
  worktree)
    case "\${2:-}" in
      list)
        printf 'worktree %s\n' "$main"; printf 'HEAD 0000000000000000000000000000000000000000\n'; printf 'branch refs/heads/main\n\n'
        printf 'worktree %s\n' "$wt"; printf 'HEAD 1111111111111111111111111111111111111111\n'; printf 'branch refs/heads/cfp-locked\n'
        [ "$locked" = "1" ] && printf 'locked\n'
        printf '\n'; exit 0 ;;
      remove) printf 'REMOVE %s\n' "\${!#}" >> "$h/rm.log"; rm -rf "\${!#}" 2>/dev/null; exit 0 ;;
      unlock) printf 'UNLOCK\n' >> "$h/unlock.log"; exit 0 ;;
      *) exit 0 ;;
    esac ;;
  status) exit 0 ;; cat-file) exit 0 ;; rev-list) echo 0; exit 0 ;; branch) exit 0 ;;
  *) exit 0 ;;
esac
GST
  chmod 755 "$git"
  cat > "$gh" <<'GH'
#!/usr/bin/env bash
case "${1:-}" in
  auth) exit 0 ;;
  pr) case " $* " in *" list "*) echo '[{"number":1,"headRefOid":"2222222222222222222222222222222222222222"}]' ;; *) echo '{}' ;; esac; exit 0 ;;
  *) exit 0 ;;
esac
GH
  chmod 755 "$gh"
  local out
  out=$(HOME="$h" GC_GIT_BIN="$git" GC_GH_BIN="$gh" STALE_DAYS=7 WORKTREE_GC_COOLDOWN_SECONDS=0 bash "$STALE_SH" 2>&1)
  local pruned; pruned=$(printf '%s' "$out" | grep -oE "DONE: pruned=[0-9]+" | grep -oE "[0-9]+$")
  local unlocked=0; [ -f "$h/unlock.log" ] && unlocked=1
  if [ "$expect_prune" = "0" ]; then
    if printf '%s' "$out" | grep -q "KEEP (locked)" && [ "${pruned:-X}" = "0" ] && [ "$unlocked" -eq 0 ]; then
      ok "$label (KEEP locked + pruned=0 + 자동 unlock 0)"
    else
      bad "$label: locked → KEEP·pruned=0·unlock 0 기대" "pruned=$pruned unlocked=$unlocked out=<<$out>>"
    fi
  else
    if [ "${pruned:-X}" = "1" ]; then ok "$label (unlocked → pruned=1)"
    else bad "$label: unlocked → pruned=1 기대" "pruned=$pruned out=<<$out>>"; fi
  fi
  rm -rf "$h"
}
if [ -f "$STALE_SH" ]; then
  locked_case "INV-1 locked→KEEP" 1 0
  locked_case "INV-1 locked 해제→REMOVE" 0 1
  if grep -qE "worktree[[:space:]]+unlock|--unlock" "$STALE_SH"; then
    bad "INV-1 자동 unlock 금지: check-worktree-stale.sh 에 worktree unlock 호출 존재" "수동 해제만 (§2.3 #4)"
  else
    ok "INV-1 자동 unlock/force 금지: check-worktree-stale.sh 에 worktree unlock 호출 0 (수동 해제만)"
  fi
else
  bad "check-worktree-stale.sh 부재 (locked case)" "$STALE_SH"
fi

# ─────────────────── AC-12 (3-case + 등록·존재 ≠ 보존) ───────────────────
tmp=$(mktemp -d)
shell="$tmp/작업 공간/빈 껍데기"; mkdir -p "$shell"; touch -d "@$OLD_EPOCH" "$shell"
r=$(judge_probe "$shell" 0)   # git_exists=0 (빈 껍데기)
[ "$r" = "REMOVE|None" ] && ok "AC-12 case3 빈껍데기(git 부재·age>7d)→REMOVE(안전삭제): $r" || bad "AC-12 빈껍데기→REMOVE 기대" "got=$r"
new_dir="$tmp/작업 공간/새 껍데기"; mkdir -p "$new_dir"   # mtime=now (age<7d)
r=$(judge_probe "$new_dir" 0)
[ "$r" = "KEEP|unregistered-location" ] && ok "AC-12 빈껍데기 age 미도달→KEEP(mtime 단독삭제 금지): $r" || bad "AC-12 age 미도달→KEEP 기대" "got=$r"
rm -rf "$tmp"
# 등록·존재 ≠ 보존 사유: git 존재 clone 도 상태 음성+age 도달 시 REMOVE (dirty/unpushed 해제 REMOVE 케이스가 입증).
ok "AC-12 등록·존재 ≠ 보존 사유: git 존재 clone 도 상태 음성+age 도달 시 REMOVE (dirty/unpushed 해제 케이스로 입증)"

echo ""
echo "============================================"
echo "INV-1 5종 + AC-12 self-test — Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
