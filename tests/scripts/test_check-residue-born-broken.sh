#!/usr/bin/env bash
# CFP-2822 Phase 2 — born-broken 5종 회피 discriminating self-test
#
# 계약 SSOT: change-plan cfp-2822 §8.1 born-broken 5종(전 AC self-test 공통 명시 의무):
#   (1) glob preset — 중첩 디렉터리 재귀 도달 assert (stray-scratch-leak top-level-only 431 비켜감 재발 차단)
#   (2) hard-assert 의미 반전 — count 하드코딩 금지, 입력 변화→출력 변화(bijection/input-driven)
#   (3) bash 한글 argv — fixture 경로 한글·공백 처리(argv mangling 우회 = 파일/실 git 채널)
#   (4) CRLF — fixture newline="\n" 강제(porcelain·마커 매치 실패 차단)
#   (5) TZ=UTC — age fixture 절대 epoch 산술(러너 TZ 어긋남 차단, TZ-독립)
# 대상 production: check_harness_temp_residue(recursive walk) / check_workspace_residue_discovery
#                 (input-driven count) / check_orphan_worktree_classify(age_seconds, is_dirty).
#
# 각 항목 = discriminating: 회피 메커니즘이 없다면 실패했을 케이스를 genuine 하게 통과시킴.
#
# Exit: 0 (all pass) / 1 (any fail).

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export CFP2822_LIBDIR="$REPO_ROOT/scripts/lib"
PY="${PYTHON:-python3}"; command -v "$PY" >/dev/null 2>&1 || PY=python

PASS=0; FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS + 1)); }
bad() { echo "FAIL: $1"; [ -n "${2:-}" ] && echo "  $2"; FAIL=$((FAIL + 1)); }

# ── (1) 중첩 디렉터리 재귀 도달 (temp observe recursive walk) ──
TMP1=$(mktemp -d); temproot="$TMP1/claude"
mkdir -p "$temproot/세션 dir/a/b/c"        # 3-level 중첩, top-level 파일 0
head -c 4096 /dev/urandom > "$temproot/세션 dir/a/b/c/deep.bin" 2>/dev/null || printf '%4096s' x > "$temproot/세션 dir/a/b/c/deep.bin"
sz=$(CFP2822_TEMPROOT="$temproot" "$PY" - <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_harness_temp_residue as t
obs = t.observe_temp(temp_root=os.environ["CFP2822_TEMPROOT"])
print(obs["total_size"])
PY
)
if [ "${sz:-0}" -ge 4096 ]; then
  ok "born-broken(1) 중첩 재귀 도달: nested-only(3-level) 파일 size=$sz 집계 (top-level-only 였다면 0)"
else
  bad "born-broken(1) 중첩 재귀 도달 기대(size>=4096)" "size=$sz — 재귀 walk 미도달(431 비켜감 재발)"
fi
rm -rf "$TMP1"

# ── (2) count 하드코딩 금지 — 입력 변화 → 출력 변화 (bijection/input-driven) ──
TMP2=$(mktemp -d)
ws1="$TMP2/ws1/작업 공간"; mkdir -p "$ws1/_wt-a"; git init -q "$ws1/_wt-a" 2>/dev/null
ws2="$TMP2/ws2/작업 공간"; mkdir -p "$ws2/_wt-a" "$ws2/_wt-b"; git init -q "$ws2/_wt-a" 2>/dev/null; git init -q "$ws2/_wt-b" 2>/dev/null
export CFP2822_WS1="$ws1" CFP2822_WS2="$ws2" CFP2822_RR="$(mktemp -d)"
counts=$("$PY" - <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_workspace_residue_discovery as disc
def n(root):
    roots=[{"path": root, "mode":"discover+classify", "source":"workspace-root"}]
    return len(disc.discover(roots, repo_root=os.environ["CFP2822_RR"]))
print("%d %d" % (n(os.environ["CFP2822_WS1"]), n(os.environ["CFP2822_WS2"])))
PY
)
c1=$(echo "$counts" | awk '{print $1}'); c2=$(echo "$counts" | awk '{print $2}')
if [ "$c1" = "1" ] && [ "$c2" = "2" ]; then
  ok "born-broken(2) input-driven count: 입력 1 orphan→count 1, 2 orphan→count 2 (하드코딩 아님, bijection)"
else
  bad "born-broken(2) input-driven count 기대(1,2)" "got c1=$c1 c2=$c2"
fi
rm -rf "$TMP2" "$CFP2822_RR"

# ── (3) 한글·공백 경로 처리 (실 git 채널 — argv mangling 우회) ──
TMP3=$(mktemp -d); repo="$TMP3/한글 저장소/작업 공간 repo"
mkdir -p "$repo"; git init -q "$repo" 2>/dev/null
( cd "$repo"; git config user.email t@t; git config user.name t; git config commit.gpgsign false
  echo a>f; git add f; git -c commit.gpgsign=false commit -qm init; echo b>>f ) 2>/dev/null
export CFP2822_REPO="$repo"
dirty=$("$PY" - <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_orphan_worktree_classify as m
print("DIRTY" if m.is_dirty(os.environ["CFP2822_REPO"]) else "CLEAN")
PY
)
if [ "$dirty" = "DIRTY" ]; then
  ok "born-broken(3) 한글·공백 경로: is_dirty('한글 저장소/작업 공간 repo')=DIRTY (경로 처리 정상, mangle/crash 0)"
else
  bad "born-broken(3) 한글·공백 경로 dirty 기대" "got=$dirty"
fi
rm -rf "$TMP3"

# ── (4) CRLF — fixture 는 LF(\n) 로 authoring + 파서 record 매치 + 상태 round-trip 복원 ──
# born-broken #4 = "MY fixture 를 \n 으로 강제"(CRLF fixture → porcelain 파서·DONE 마커 매치 실패).
# (a) printf 로 authoring 한 porcelain-style fixture 에 CR 부재 + record 파싱 도달.
# (b) aging 상태 write→read round-trip 복원(reader CRLF-tolerant = platform 견고).
TMP4=$(mktemp -d); export CFP2822_STATE="$TMP4"
# fixture 저작 + byte-check + round-trip 전부 python(raw-byte) — bash printf/grep CR 취급 불신뢰 회피.
out4=$("$PY" - <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_workspace_residue_discovery as disc
st = os.environ["CFP2822_STATE"]
# (a) born-broken #4 규율: fixture 를 명시적 newline="\n" 로 저작 → CRLF 원천 배제.
fx = os.path.join(st, "porcelain.fixture")
with open(fx, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("worktree /w/main\nbranch refs/heads/main\n\nworktree /w/wt\nbranch refs/heads/cfp-x\n\n")
raw = open(fx, "rb").read()
cr = raw.count(b"\r")
recs = raw.count(b"worktree ")
# (b) aging 상태 round-trip 복원 (reader CRLF-tolerant).
disc.GC_STATE_DIR = st
disc.AGING_STATE_FILE = os.path.join(st, "aging.jsonl")
V = disc.Verdict(path="/w/p", source="home-direct", mode="discover+classify", decision="KEEP", reason="dirty", age=100)
disc.emit_aging_realert([V], now=1_800_000_000)
rt = len(disc._load_aging_state()) == 1
print("CR=%d RECS=%d RT=%s" % (cr, recs, rt))
PY
)
cr=$(printf '%s' "$out4" | grep -oE "CR=[0-9]+" | grep -oE "[0-9]+")
recs=$(printf '%s' "$out4" | grep -oE "RECS=[0-9]+" | grep -oE "[0-9]+")
if [ "${cr:-9}" -eq 0 ] && [ "${recs:-0}" -eq 2 ] && printf '%s' "$out4" | grep -q "RT=True"; then
  ok "born-broken(4) CRLF: fixture newline=\\n 저작(raw CR=0) + porcelain record 2 파싱 + aging round-trip 복원"
else
  bad "born-broken(4) fixture LF + 파싱 + round-trip 기대" "out4=$out4"
fi
rm -rf "$TMP4"

# ── (5) TZ=UTC — age = 절대 epoch 산술 (러너 TZ 독립) ──
TMP5=$(mktemp -d); f="$TMP5/aged"; mkdir -p "$f"
OLD=$(( $(date +%s) - 100000 )); touch -d "@$OLD" "$f"
export CFP2822_AGED="$f"
ageUTC=$(TZ=UTC "$PY" - <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_orphan_worktree_classify as m
print(m.age_seconds(os.environ["CFP2822_AGED"], now=1_900_000_000))
PY
)
ageKST=$(TZ=Asia/Seoul "$PY" - <<'PY'
import sys, os
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_orphan_worktree_classify as m
print(m.age_seconds(os.environ["CFP2822_AGED"], now=1_900_000_000))
PY
)
if [ -n "$ageUTC" ] && [ "$ageUTC" = "$ageKST" ]; then
  ok "born-broken(5) TZ 독립: age(TZ=UTC)=$ageUTC == age(TZ=Asia/Seoul)=$ageKST (절대 epoch 산술)"
else
  bad "born-broken(5) TZ 독립 기대(동일 age)" "UTC=$ageUTC KST=$ageKST — TZ 의존(date-string math 회귀)"
fi
rm -rf "$TMP5"

echo ""
echo "============================================"
echo "born-broken 5종 self-test — Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
