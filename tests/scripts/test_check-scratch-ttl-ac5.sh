#!/usr/bin/env bash
# CFP-2822 Phase 2 — codeforge-scratch TTL purge self-test (AC-5, P0)
#
# 계약 SSOT: change-plan cfp-2822 §3.2② / §8.1 AC-5 / Story AC-5 / INV-1 (class 5 이식).
# 대상 production: scripts/lib/check_codeforge_scratch_ttl.py (run / _safe_to_purge).
#
# AC-5 양방향 변별:
#   · `.git` 보유 디렉터리 → TTL 삭제 **제외** + orphan 회부(REFER-ORPHAN, 삭제 0).
#   · age>TTL 순수 loose 파일 → PURGED(실 삭제).
#   · age<TTL loose 파일 → KEEP (TTL 미도달).
#   · worktree-stale-gc.log(session-end 영속 로그) → 명시 제외(하위호환).
#   · GC_DRY_RUN=1 → would-purge (실 삭제 0).
#
# ★ 실 홈 무오염 격리(중대): check_codeforge_scratch_ttl.py 는 expanduser("~")(Windows=USERPROFILE,
#   HOME override 무시)로 실 codeforge-scratch 를 스캔·삭제한다 → 테스트가 실 홈을 파괴하면 안 됨.
#   → `_scratch_root` 를 in-process monkeypatch 해 fixture 루트로 고정(실 홈 절대 미접근).
# anti-theater: 삭제 O(loose old) ∧ 삭제 X(.git/log/young) 양방향 — 판정이 한쪽만 맞으면 FAIL.
# born-broken: age = os.utime 절대 epoch(TZ-독립) / fixture 이름 한글·공백 포함.
#
# Exit: 0 (all pass) / 1 (any fail).

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="$REPO_ROOT/scripts/lib"
PY="${PYTHON:-python3}"; command -v "$PY" >/dev/null 2>&1 || PY=python
export CFP2822_LIBDIR="$LIB_DIR"

PASS=0; FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS + 1)); }
bad() { echo "FAIL: $1"; [ -n "${2:-}" ] && echo "  $2"; FAIL=$((FAIL + 1)); }

# fixture 루트 준비 (in-process python 이 monkeypatch 로 _scratch_root 를 이 루트로 고정).
FIX=$(mktemp -d)/codeforge-scratch
mkdir -p "$FIX"
OLD=$(( $(date +%s) - 30 * 86400 ))
YOUNG=$(( $(date +%s) - 1 * 3600 ))

# fixtures
printf 'old loose\n' > "$FIX/오래된 산출물.txt";       touch -d "@$OLD"   "$FIX/오래된 산출물.txt"
printf 'young\n'     > "$FIX/최근 산출물.txt";         touch -d "@$YOUNG" "$FIX/최근 산출물.txt"
printf 'log\n'       > "$FIX/worktree-stale-gc.log";  touch -d "@$OLD"   "$FIX/worktree-stale-gc.log"
mkdir -p "$FIX/독립 clone/.git";                        touch -d "@$OLD"   "$FIX/독립 clone"
mkdir -p "$FIX/일반 디렉터리";                            touch -d "@$OLD"   "$FIX/일반 디렉터리"

# in-process 실행 (monkeypatch _scratch_root → FIX). GC_DRY_RUN env 로 실/dry 분기.
run_ttl() {
  local dry="$1" fix="$2"
  GC_DRY_RUN="$dry" CFP2822_FIX="$fix" "$PY" - <<'PY'
import sys, os, io, contextlib
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_codeforge_scratch_ttl as m
fix = os.environ["CFP2822_FIX"]
m._scratch_root = lambda: fix          # 실 홈 절대 미접근 — fixture 고정
buf = io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
    m.run()                            # PURGED/DONE(stdout) + REFER-ORPHAN(stderr) 전부 캡처
sys.__stdout__.write(buf.getvalue())   # 병합 출력 → 실제 stdout
PY
}

# ── DRY_RUN: would-purge, 실 삭제 0 ──
out=$(run_ttl 1 "$FIX" 2>/dev/null)
if printf '%s' "$out" | grep -q "would-purge" && [ -f "$FIX/오래된 산출물.txt" ]; then
  ok "AC-5 DRY_RUN: old loose → would-purge + 파일 존치(실 삭제 0)"
else
  bad "AC-5 DRY_RUN: would-purge + 파일 존치 기대" "out=<<$out>> exists=$([ -f "$FIX/오래된 산출물.txt" ] && echo y || echo n)"
fi

# ── 실 purge ──
out=$(run_ttl "" "$FIX" 2>/dev/null)
# (a) old loose → PURGED + 실제 삭제됨
if printf '%s' "$out" | grep -q "PURGED" && [ ! -f "$FIX/오래된 산출물.txt" ]; then
  ok "AC-5 loose(age>TTL)→PURGED + 실 삭제됨"
else
  bad "AC-5 loose(age>TTL)→PURGED 기대" "out=<<$out>> exists=$([ -f "$FIX/오래된 산출물.txt" ] && echo y || echo n)"
fi
# (b) .git 보유 dir → REFER-ORPHAN + 존치 (삭제 X, orphan 회부)
if printf '%s' "$out" | grep -q "REFER-ORPHAN" && [ -d "$FIX/독립 clone/.git" ]; then
  ok "AC-5 .git 보유 dir→REFER-ORPHAN + 존치(TTL 삭제 제외, AC-12 회부)"
else
  bad "AC-5 .git 보유 dir→REFER-ORPHAN + 존치 기대" "out=<<$out>> exists=$([ -d "$FIX/독립 clone/.git" ] && echo y || echo n)"
fi
# (c) young loose → 존치
if [ -f "$FIX/최근 산출물.txt" ]; then
  ok "AC-5 young loose(age<TTL)→존치(TTL 미도달)"
else
  bad "AC-5 young loose 존치 기대" "삭제됨"
fi
# (d) 영속 로그 → 명시 제외 존치
if [ -f "$FIX/worktree-stale-gc.log" ]; then
  ok "AC-5 worktree-stale-gc.log→명시 제외 존치(하위호환)"
else
  bad "AC-5 stale-gc.log 존치 기대" "삭제됨"
fi
# (e) DONE 마커 + output contract
if printf '%s' "$out" | grep -qE "\[scratch-ttl\] DONE: purged=[0-9]+ kept=[0-9]+"; then
  ok "AC-5 output contract: [scratch-ttl] DONE: purged=N kept=M (INV-5)"
else
  bad "AC-5 DONE 마커 기대" "out=<<$out>>"
fi

rm -rf "$(dirname "$FIX")"
echo ""
echo "============================================"
echo "AC-5 scratch TTL self-test — Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
