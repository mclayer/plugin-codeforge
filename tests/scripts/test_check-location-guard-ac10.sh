#!/usr/bin/env bash
# CFP-2822 Phase 2 — worktree 생성위치 가드 self-test (AC-10, P0)
#
# 계약 SSOT: change-plan cfp-2822 §3.2① / §8.1 AC-10 / §8.10 dark-path (3) warn→block /
#           Story AC-10 (표준 경로 통과 ∧ 표준밖 warn→block 스위치) / INV-6·7.
# 대상 production: scripts/lib/check_worktree_location_guard.py (is_nonstandard_location / main).
#
# AC-10 양방향 + 스위치:
#   · 표준 경로($HOME/.claude/worktrees/... target) → 통과(위반 아님).
#   · 표준 밖 target(raw `git worktree add` 우회 포함) → 위반 검출.
#   · warn tier → exit 0 + WARN (도입기) / block tier → exit 2 + BLOCKED (승격기) — 스위치 load-bearing.
#   · bypass env → exit 0 audit.
#
# anti-theater: 동일 nonstandard cmd 가 tier=warn→0 / tier=block→2 로 exit code 반전 →
#   tier flag 가 실제 판정을 바꾸는 load-bearing 축임을 입증(§8.10 discriminating_basis).
# born-broken: base 주입으로 결정론(bash worktree_base 포트 의존 제거) / fixture 경로 한글·공백.
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

# ── 한글·공백 cmd 는 argv/heredoc 인라인으로 넘기면 Windows byte-mangling(born-broken #3,
#    MEMORY 기지 gotcha) → bash `printf '%s' > file`(raw UTF-8 bytes) + python file-read 로
#    완전 회피. base/cwd 는 ASCII 라 argv/env 안전. (production hook 은 JSON stdin 을 읽음.) ──
CMDDIR=$(mktemp -d)

# is_nonstandard_location(cmd, base, cwd) → "True"/"False"
judge() {
  local cmd="$1" base="$2" cwd="$3"
  printf '%s' "$cmd" > "$CMDDIR/cmd.txt"
  CFP2822_CMDFILE="$CMDDIR/cmd.txt" "$PY" - "$base" "$cwd" <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_worktree_location_guard as g
cmd = open(os.environ["CFP2822_CMDFILE"], encoding="utf-8").read()
print(g.is_nonstandard_location(cmd, base=sys.argv[1], cwd=sys.argv[2]))
PY
}

# main() tier 스위치 — cmd(파일 read) 로 payload 구성, managed_root monkeypatch(고정 base).
main_tier() {
  local cmd="$1" tier="$2" base="$3" bypass="${4:-}"
  printf '%s' "$cmd" > "$CMDDIR/cmd.txt"
  BYPASS_WORKTREE_LOCATION_GUARD="$bypass" WORKTREE_LOCATION_GUARD_TIER="$tier" \
  CFP2822_BASE="$base" CFP2822_CMDFILE="$CMDDIR/cmd.txt" "$PY" - <<'PY'
import sys, os, io, contextlib
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_worktree_location_guard as g
cmd = open(os.environ["CFP2822_CMDFILE"], encoding="utf-8").read()
g.managed_root = lambda cwd=None: os.environ["CFP2822_BASE"]   # bash 포트 의존 제거
g._read_input = lambda: {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": "/tmp"}
buf = io.StringIO(); code = 0
try:
    with contextlib.redirect_stderr(buf), contextlib.redirect_stdout(buf):
        g.main()
except SystemExit as e:
    code = e.code if isinstance(e.code, int) else 0
sys.__stdout__.write("EXIT=%d\n" % code)
sys.__stdout__.write(buf.getvalue())
PY
}

# ── 실 temp 디렉터리로 base/target 구성. fake `/home/...` 은 MSYS 마운트와 충돌하고,
#    POSIX `/tmp/...` 은 native python realpath 가 `C:\tmp` 로 오해석(argv MSYS 변환과 비대칭)
#    → born-broken. `cygpath -m` 로 Windows-mixed 형으로 통일해 target(file)·base(argv) 양쪽
#    realpath 결정론 확보 (MSYS 경로 변환 비대칭 gotcha 회피). ──
ROOT=$(cygpath -m "$(mktemp -d)" 2>/dev/null || mktemp -d)
BASE="$ROOT/.claude/worktrees"
mkdir -p "$BASE/myrepo" "$ROOT/workspace/repo"     # 실 존재 prefix
STD="git worktree add $BASE/myrepo/cfp-99-작업 br"   # 표준 base 하위 (한글 세그먼트)
BAD="git worktree add $ROOT/workspace/_wt-mtd303-inttest"  # 표준 밖 (workspace 루트)

# ── is_nonstandard_location 판정 ──
[ "$(judge "$STD" "$BASE" /tmp)" = "False" ] && ok "AC-10 표준 경로 target→통과(False)" || bad "AC-10 표준 경로 통과 기대" "got=$(judge "$STD" "$BASE" /tmp)"
[ "$(judge "$BAD" "$BASE" /tmp)" = "True" ]  && ok "AC-10 표준 밖 target(raw add 우회)→위반(True)" || bad "AC-10 표준 밖 위반 기대" "got=$(judge "$BAD" "$BASE" /tmp)"
[ "$(judge "git status" "$BASE" /tmp)" = "False" ] && ok "AC-10 worktree add 아님→가드 무관(False)" || bad "AC-10 non-add 무관 기대" "got=$(judge "git status" "$BASE" /tmp)"
# 상대경로 target (cwd 밖) 도 위반 검출: cwd=workspace/repo, ../_wt-x = workspace/_wt-x (base 밖)
[ "$(judge "git worktree add ../_wt-x" "$BASE" "$ROOT/workspace/repo")" = "True" ] && ok "AC-10 상대경로 표준밖 target→위반(True)" || bad "AC-10 상대경로 위반 기대" "got=$(judge "git worktree add ../_wt-x" "$BASE" "$ROOT/workspace/repo")"

# ── warn→block 스위치 (동일 BAD cmd 가 tier 로 exit code 반전) ──
outW=$(main_tier "$BAD" warn "$BASE"); ecW=$(printf '%s' "$outW" | grep -oE "EXIT=[0-9]+" | grep -oE "[0-9]+$")
outB=$(main_tier "$BAD" block "$BASE"); ecB=$(printf '%s' "$outB" | grep -oE "EXIT=[0-9]+" | grep -oE "[0-9]+$")
if [ "$ecW" = "0" ] && printf '%s' "$outW" | grep -q "WARN"; then
  ok "AC-10 warn tier: 표준밖 → exit 0 + WARN (도입기 통과)"
else
  bad "AC-10 warn tier: exit0 + WARN 기대" "ec=$ecW out=<<$outW>>"
fi
if [ "$ecB" = "2" ] && printf '%s' "$outB" | grep -q "BLOCKED"; then
  ok "AC-10 block tier: 표준밖 → exit 2 + BLOCKED (승격기 차단)"
else
  bad "AC-10 block tier: exit2 + BLOCKED 기대" "ec=$ecB out=<<$outB>>"
fi
# 스위치 load-bearing 입증: 동일 cmd, warn(0) ≠ block(2)
if [ "$ecW" = "0" ] && [ "$ecB" = "2" ]; then
  ok "AC-10 §8.10 스위치 discriminating: 동일 nonstandard cmd, warn=0 → block=2 반전 (tier load-bearing)"
else
  bad "AC-10 스위치 반전 기대(warn=0,block=2)" "warn=$ecW block=$ecB"
fi
# 표준 경로 → block tier 여도 통과(exit 0)
outSB=$(main_tier "$STD" block "$BASE"); ecSB=$(printf '%s' "$outSB" | grep -oE "EXIT=[0-9]+" | grep -oE "[0-9]+$")
[ "$ecSB" = "0" ] && ok "AC-10 표준 경로 → block tier 여도 통과(exit 0)" || bad "AC-10 표준+block→exit0 기대" "ec=$ecSB out=<<$outSB>>"
# bypass env → exit 0 audit (nonstandard+block 여도 무력화)
outBy=$(main_tier "$BAD" block "$BASE" 1); ecBy=$(printf '%s' "$outBy" | grep -oE "EXIT=[0-9]+" | grep -oE "[0-9]+$")
if [ "$ecBy" = "0" ] && printf '%s' "$outBy" | grep -qi "suppressed"; then
  ok "AC-10 bypass(BYPASS_WORKTREE_LOCATION_GUARD=1)→exit 0 + audit"
else
  bad "AC-10 bypass→exit0+audit 기대" "ec=$ecBy out=<<$outBy>>"
fi

rm -rf "$CMDDIR" "$ROOT"
echo ""
echo "============================================"
echo "AC-10 location guard self-test — Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
