#!/usr/bin/env bash
# CFP-2822 Phase 2 — E10 다중-트리거 double-delete race self-test (P0)
#
# 계약 SSOT: change-plan cfp-2822 §8.5.3 (idempotency replay) / §5.2 step2 (E10 GREEN 필수) /
#           §5.3 (mkdir 원자 lock + cooldown + idempotent-remove 3중) / §8.8 concurrency /
#           Story AC-13 / INV-4 (동시 GC race 방지) / E10 엣지케이스.
# 대상 production: templates/scripts/check-worktree-stale.sh (⑤ lock/cooldown/idempotent, L61-159/285-346).
#
# 핵심 oracle: 2 GC 인스턴스 동시발화(`&` 병렬, 공유 worktree admin record + 공유 HOME/state)
#             → **double-delete = 0** (실 `worktree remove --force` syscall 정확히 1회).
# flock 부재(MINGW64 command -v flock=ABSENT) 전제 — mkdir 단일 원자 syscall 로 상호배제.
#
# anti-theater (vacuous 거짓통과 금지 — 변이 주입 없이 lock 게이트 load-bearing 입증):
#   - Case A (baseline): lock 무경쟁 → prune 1 + remove-count 1 (기저 동작 실재 확인).
#   - Case B (discriminating): lock 을 살아있는 pid 로 선점 → GC 는 SKIP + remove-count 0 +
#            DONE: pruned=0. lock 게이트를 제거/무력화하면 이 케이스가 pruned=1 로 뒤집힘
#            (lock 이 실제 판정을 바꾸는 load-bearing 축임을 입증 — genuine 실패 재현).
#   - Case C (race): 2 동시발화 → remove-count == 1 (double-delete 0) + 합계 pruned == 1.
#
# born-broken 회피: age fixture = touch -d @epoch (절대 epoch, TZ-독립) / fixture 경로 한글·공백
#   1+ 포함 / HOME override 로 실 ~/.claude 무오염 / remove-count = 실 syscall 계측(하드코딩 아님).
#
# Exit: 0 (all pass) / 1 (any fail).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STALE_SH="$REPO_ROOT/templates/scripts/check-worktree-stale.sh"

PASS=0
FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS + 1)); }
bad() { echo "FAIL: $1"; [ -n "${2:-}" ] && echo "  $2"; FAIL=$((FAIL + 1)); }

# ── 공유 stub builder — 한 HOMEDIR 안에 git/gh stub + stale worktree fixture 생성 ──
# 반환(전역): G_GIT / G_GH / G_MAIN / G_WT / G_RMLOG
build_fixture() {
  local homedir="$1"
  # fixture 경로에 한글·공백 세그먼트 1+ 포함 (born-broken #3 argv mangling 방어 실증).
  G_MAIN="$homedir/작업 공간/main"
  G_WT="$homedir/작업 공간/wt/cfp-오래된 branch"
  G_RMLOG="$homedir/remove-syscall.log"
  G_GIT="$homedir/git"
  G_GH="$homedir/gh"
  mkdir -p "$G_MAIN" "$G_WT"
  : > "$G_RMLOG"

  # age > STALE_DAYS 충족: 절대 epoch (now - 30d) 로 mtime 설정 (TZ-독립, born-broken #5).
  local old_epoch
  old_epoch=$(( $(date +%s) - 30 * 86400 ))
  touch -d "@$old_epoch" "$G_WT" 2>/dev/null || touch -t 202601010000 "$G_WT"

  # git stub — worktree remove 는 실 rm-rf + remove-count 계측(실 syscall 신호).
  cat > "$G_GIT" <<GITSTUB
#!/usr/bin/env bash
# -C <dir> prefix 흡수
if [ "\${1:-}" = "-C" ]; then shift 2; fi
case "\${1:-}" in
  rev-parse) echo "$G_MAIN"; exit 0 ;;
  worktree)
    case "\${2:-}" in
      list)
        printf 'worktree %s\n' "$G_MAIN"
        printf 'HEAD 0000000000000000000000000000000000000000\n'
        printf 'branch refs/heads/main\n\n'
        printf 'worktree %s\n' "$G_WT"
        printf 'HEAD 1111111111111111111111111111111111111111\n'
        printf 'branch refs/heads/cfp-old\n\n'
        exit 0 ;;
      remove)
        # 실 삭제 대상 = 마지막 인자. remove-count 계측 + 실제 rm-rf (idempotent 가드 트리거).
        tgt="\${!#}"
        printf 'REMOVE %s\n' "\$tgt" >> "$G_RMLOG"
        rm -rf "\$tgt" 2>/dev/null || true
        exit 0 ;;
      prune) exit 0 ;;
      *) exit 0 ;;
    esac ;;
  status) exit 0 ;;                # clean (빈 출력)
  cat-file) exit 0 ;;              # merged head 존재
  rev-list) echo 0; exit 0 ;;      # 병합 후 추가 commit 0
  branch) exit 0 ;;
  *) exit 0 ;;
esac
GITSTUB
  chmod 755 "$G_GIT"

  cat > "$G_GH" <<'GHSTUB'
#!/usr/bin/env bash
case "${1:-}" in
  auth) exit 0 ;;   # 인증됨
  pr)
    case " $* " in
      *" list "*) echo '[{"number":1,"headRefOid":"2222222222222222222222222222222222222222"}]' ;;
      *) echo '{"mergedAt":"2026-06-01T00:00:00Z"}' ;;
    esac
    exit 0 ;;
  *) exit 0 ;;
esac
GHSTUB
  chmod 755 "$G_GH"
}

# GC 1회 실행 (실 모드 — dry-run 아님, lock/cooldown 경로 활성).
run_gc() {
  local homedir="$1" outfile="$2"
  HOME="$homedir" \
    GC_GIT_BIN="$G_GIT" GC_GH_BIN="$G_GH" STALE_DAYS=7 \
    WORKTREE_GC_COOLDOWN_SECONDS=300 \
    bash "$STALE_SH" > "$outfile" 2>&1
  echo $?
}

remove_count() { local n=0; [ -f "$1" ] && n=$(grep -c '^REMOVE ' "$1" 2>/dev/null); echo "${n:-0}"; }

if [ ! -f "$STALE_SH" ]; then
  bad "check-worktree-stale.sh 부재" "$STALE_SH"
  echo "Total: PASS=$PASS FAIL=$FAIL"; exit 1
fi

# ─── Case A: baseline (lock 무경쟁) → prune 1 + remove-count 1 ───────────────
tmpA=$(mktemp -d)
build_fixture "$tmpA"
ecA=$(run_gc "$tmpA" "$tmpA/out.txt")
rcA=$(remove_count "$G_RMLOG")
outA=$(cat "$tmpA/out.txt")
if [ "$ecA" -eq 0 ] && printf '%s' "$outA" | grep -q "DONE: pruned=1" && [ "$rcA" -eq 1 ]; then
  ok "Case A baseline: 무경쟁 → DONE:pruned=1 + remove-syscall=1 (기저 동작 실재)"
else
  bad "Case A baseline: 무경쟁 prune 기대(pruned=1, remove=1)" \
      "exit=$ecA remove_count=$rcA out=<<$outA>>"
fi
rm -rf "$tmpA"

# ─── Case B: discriminating — lock 살아있는 pid 로 선점 → SKIP + remove 0 ─────
# lock 게이트가 load-bearing 임을 입증: 선점 시 GC 는 아무것도 안 지움(pruned=0).
# (lock 을 제거/무력화하면 Case A 처럼 pruned=1 로 뒤집힘 = genuine 판정 반전.)
tmpB=$(mktemp -d)
build_fixture "$tmpB"
lockdir="$tmpB/.claude/worktree-gc-state/.locks/worktree-gc.lock"
mkdir -p "$lockdir"
printf '%s\n' "$$" > "$lockdir/pid"            # 이 셸 = 살아있는 pid (kill -0 성공)
printf '%s\n' "$(date +%s)" > "$lockdir/epoch"  # 방금 = age<TTL (stale 아님)
ecB=$(run_gc "$tmpB" "$tmpB/out.txt")
rcB=$(remove_count "$G_RMLOG")
outB=$(cat "$tmpB/out.txt")
if [ "$ecB" -eq 0 ] && printf '%s' "$outB" | grep -q "DONE: pruned=0" \
   && printf '%s' "$outB" | grep -qi "SKIP" && [ "$rcB" -eq 0 ]; then
  ok "Case B discriminating: 살아있는 lock 선점 → SKIP + DONE:pruned=0 + remove-syscall=0 (lock load-bearing)"
else
  bad "Case B discriminating: lock 선점 시 SKIP+pruned=0+remove=0 기대" \
      "exit=$ecB remove_count=$rcB out=<<$outB>>"
fi
rm -rf "$tmpB"

# ─── Case C: race — 2 동시발화 → double-delete 0 (remove-count == 1) ──────────
tmpC=$(mktemp -d)
build_fixture "$tmpC"
run_gc "$tmpC" "$tmpC/out1.txt" > "$tmpC/ec1" 2>/dev/null &
run_gc "$tmpC" "$tmpC/out2.txt" > "$tmpC/ec2" 2>/dev/null &
wait
rcC=$(remove_count "$G_RMLOG")
ec1=$(cat "$tmpC/ec1" 2>/dev/null || echo X)
ec2=$(cat "$tmpC/ec2" 2>/dev/null || echo X)
out1=$(cat "$tmpC/out1.txt" 2>/dev/null)
out2=$(cat "$tmpC/out2.txt" 2>/dev/null)
# 합계 pruned = 두 인스턴스 pruned 합 (승자 1 + 패자 0).
pruned_sum=$(printf '%s\n%s\n' "$out1" "$out2" | grep -oE "DONE: pruned=[0-9]+" | grep -oE "[0-9]+$" | awk '{s+=$1} END{print s+0}')

# 핵심 oracle: 실 remove syscall 정확히 1회 (double-delete 0).
if [ "$rcC" -eq 1 ]; then
  ok "Case C race: 2 동시발화 → 실 worktree remove syscall == 1 (double-delete = 0)"
else
  bad "Case C race: double-delete 0 위반 — remove-syscall != 1" \
      "remove_count=$rcC (double-delete 발생!) out1=<<$out1>> out2=<<$out2>>"
fi
# 합계 pruned == 1 (승자만 1, 패자 skip 0).
if [ "$pruned_sum" -eq 1 ]; then
  ok "Case C race: 합계 pruned == 1 (승자 1 + 패자 SKIP 0)"
else
  bad "Case C race: 합계 pruned 기대 1" "pruned_sum=$pruned_sum out1=<<$out1>> out2=<<$out2>>"
fi
# INV-5: 두 인스턴스 모두 exit 0 + DONE 마커 (output contract 무손상, 어떤 입력에도 DONE).
if [ "$ec1" = "0" ] && [ "$ec2" = "0" ] \
   && printf '%s' "$out1" | grep -q "DONE:" && printf '%s' "$out2" | grep -q "DONE:"; then
  ok "Case C race: 두 인스턴스 exit 0 + DONE 마커 (INV-5 output contract 무손상)"
else
  bad "Case C race: 두 인스턴스 exit 0 + DONE 기대" "ec1=$ec1 ec2=$ec2"
fi
rm -rf "$tmpC"

echo ""
echo "============================================"
echo "E10 race self-test — Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
