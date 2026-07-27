#!/usr/bin/env bash
# CFP-2822 Phase 2 — 잔재 발견 스캐너 discovery self-test (AC-8/11/15)
#
# 계약 SSOT: change-plan cfp-2822 §3.2③ (5-함수 파이프라인) / §3.4 (aging JSONL) / §7.4.1 (backoff) /
#           §8.1 AC-8·AC-11·AC-15 / Story AC-8·AC-11·AC-15 / INV-1·2·3.
# 대상 production: scripts/lib/check_workspace_residue_discovery.py
#                 (emit_aging_realert / discover / judge / emit_metrics_summary).
#
# AC-8 (재알림 dedup/backoff, BVA): 임계+1→발화 ∧ 임계−1→무발화 ∧ 동일 항목·사유 2회→2번째 dedup
#   + 지수 backoff(7d→14d) 증가 입증.
# AC-11 (미등록 orphan count): workspace-root 미등록 git dir → 발견 count 1 / 표준(orphan 없음) → 0.
# AC-15 (용량 임계, BVA): Temp 총량 임계+1→CAPACITY-ALERT ∧ 임계−1→무발화 + 회수 강행 0(INV-1/2).
#
# ★ 실 홈 무오염: aging JSONL = ~/.claude/worktree-gc-state (expanduser) → 실 홈. in-process
#   monkeypatch(GC_STATE_DIR/AGING_STATE_FILE)로 fixture 격리. 용량 임계도 monkeypatch.
# anti-theater: BVA ±1 양방향 + dedup 2회 차이 + backoff 증가 — 하드코딩 카운트 없음, now 주입 결정론.
# born-broken: age/시간 = 절대 epoch 산술(TZ-독립) / orphan fixture 경로 한글·공백.
#
# Exit: 0 (all pass) / 1 (any fail).

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="$REPO_ROOT/scripts/lib"
PY="${PYTHON:-python3}"; command -v "$PY" >/dev/null 2>&1 || PY=python
export CFP2822_LIBDIR="$LIB_DIR"

# AC-11 fixture: workspace-root 에 미등록 git orphan (한글·공백 이름) 배치.
WSPARENT=$(mktemp -d); WSROOT="$WSPARENT/작업 공간"
mkdir -p "$WSROOT/_wt-orphan branch"
git init -q "$WSROOT/_wt-orphan branch" 2>/dev/null
export CFP2822_WSROOT="$WSROOT"
CLEANPARENT=$(mktemp -d); CLEANROOT="$CLEANPARENT/빈 작업공간"; mkdir -p "$CLEANROOT"
export CFP2822_CLEANROOT="$CLEANROOT"
# repo_root = 미등록 판정용(등록 worktree 집합 비움) 임시 비-repo 디렉터리.
export CFP2822_REPOROOT="$(mktemp -d)"

"$PY" - <<'PY'
import sys, os, io, contextlib, tempfile
sys.path.insert(0, os.environ["CFP2822_LIBDIR"])
import check_workspace_residue_discovery as disc

PASS = FAIL = 0
def ok(m):
    global PASS; PASS += 1; print("PASS: " + m)
def bad(m, d=""):
    global FAIL; FAIL += 1; print("FAIL: " + m + (("  " + d) if d else ""))

DAY = 86400

# ══════════════ AC-8 aging 재알림 dedup + BVA + backoff ══════════════
# 실 홈 무오염 — 상태 파일을 temp 로 monkeypatch.
tdir = tempfile.mkdtemp()
disc.GC_STATE_DIR = tdir
disc.AGING_STATE_FILE = os.path.join(tdir, "residue-aging.jsonl")

V = disc.Verdict(path="/w/작업 공간/보존 clone", source="home-direct", mode="discover+classify",
                 decision="KEEP", reason="dirty", age=10 * DAY)
t0 = 1_800_000_000   # 고정 절대 epoch (TZ-독립)

n1 = disc.emit_aging_realert([V], now=t0)
if n1 == 1: ok("AC-8 신규 보존 → 재알림 1회 발화")
else: bad("AC-8 신규 발화 1 기대", "got=%d" % n1)

# 동일 항목·사유 즉시 재실행 → dedup (backoff 창 내, 무발화)
n2 = disc.emit_aging_realert([V], now=t0)
if n2 == 0: ok("AC-8 동일 항목·사유 2회째 즉시 → dedup 무발화")
else: bad("AC-8 dedup 무발화(0) 기대", "got=%d" % n2)

# BVA 임계−1: count=1 → interval 7d. (7d - 1) 경과 → 무발화
n3 = disc.emit_aging_realert([V], now=t0 + 7 * DAY - 1)
if n3 == 0: ok("AC-8 BVA 임계−1(7d-1s) → 무발화")
else: bad("AC-8 임계−1 무발화 기대", "got=%d" % n3)

# BVA 임계+1: (7d + 1) 경과 → 발화 (count → 2)
n4 = disc.emit_aging_realert([V], now=t0 + 7 * DAY + 1)
if n4 == 1: ok("AC-8 BVA 임계+1(7d+1s) → 재알림 발화 (backoff 창 경과)")
else: bad("AC-8 임계+1 발화 기대", "got=%d" % n4)

# backoff 증가: count=2 → interval 14d. 직전 알림(t0+7d+1)로부터 14d-1 → 무발화 (7d 로는 부족 = 증가 입증)
last = t0 + 7 * DAY + 1
n5 = disc.emit_aging_realert([V], now=last + 14 * DAY - 1)
if n5 == 0: ok("AC-8 backoff 증가: count=2 → interval 14d, 14d-1 무발화 (7d→14d 지수 증가)")
else: bad("AC-8 backoff 14d-1 무발화 기대", "got=%d" % n5)
n6 = disc.emit_aging_realert([V], now=last + 14 * DAY + 1)
if n6 == 1: ok("AC-8 backoff 증가: 14d+1 → 발화 (지수 backoff 확증)")
else: bad("AC-8 backoff 14d+1 발화 기대", "got=%d" % n6)

# INV-3: 사유 없는 KEEP 은 aging 대상 아님 (reason=None → 미발화)
Vn = disc.Verdict(path="/w/nogit", source="temp", mode="observe-only", decision="KEEP", reason=None, age=DAY)
n7 = disc.emit_aging_realert([Vn], now=t0)
if n7 == 0: ok("AC-8/INV-3 사유 없는 보존(reason=None) → aging 대상 아님 (무발화)")
else: bad("AC-8 reason=None 무발화 기대", "got=%d" % n7)

# ══════════════ AC-11 미등록 orphan count ══════════════
def orphan_count(root):
    roots = [{"path": root, "mode": "discover+classify", "source": "workspace-root"}]
    cands = disc.discover(roots, repo_root=os.environ["CFP2822_REPOROOT"])
    return sum(1 for c in cands if c.source == "workspace-root")

c_orphan = orphan_count(os.environ["CFP2822_WSROOT"])
if c_orphan == 1: ok("AC-11 workspace-root 미등록 git orphan → 발견 count=1")
else: bad("AC-11 orphan count=1 기대", "got=%d" % c_orphan)

c_clean = orphan_count(os.environ["CFP2822_CLEANROOT"])
if c_clean == 0: ok("AC-11 orphan 없는 workspace-root → count=0 (변별)")
else: bad("AC-11 clean count=0 기대", "got=%d" % c_clean)

# ══════════════ AC-15 용량 임계 BVA + 회수 강행 0 ══════════════
disc.CAPACITY_ALERT_BYTES = 1000   # monkeypatch 임계
def capacity_alert(total):
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        disc.emit_metrics_summary([], [], {"total_size": total}, None)
    return buf.getvalue()

out_over = capacity_alert(1001)   # 임계+1
if "CAPACITY-ALERT" in out_over: ok("AC-15 BVA 임계+1(1001>1000) → CAPACITY-ALERT 발화")
else: bad("AC-15 임계+1 CAPACITY-ALERT 기대", "out=%r" % out_over)
# 회수 강행 0 — 경고 문구에 '회수 강행 0' 명시 (삭제 아님)
if "회수 강행 0" in out_over: ok("AC-15 CAPACITY-ALERT = 회수 강행 0 (INV-1/2 가시화만)")
else: bad("AC-15 회수 강행 0 명시 기대", "out=%r" % out_over)

out_under = capacity_alert(999)   # 임계−1
if "CAPACITY-ALERT" not in out_under: ok("AC-15 BVA 임계−1(999) → 무발화 (변별)")
else: bad("AC-15 임계−1 무발화 기대", "out=%r" % out_under)

print("")
print("HARNESS-SUMMARY PASS=%d FAIL=%d" % (PASS, FAIL))
sys.exit(0 if FAIL == 0 else 1)
PY
ec=$?

rm -rf "$WSPARENT" "$CLEANPARENT" "$CFP2822_REPOROOT" 2>/dev/null || true
echo "============================================"
echo "AC-8/11/15 discovery self-test — exit=$ec"
echo "============================================"
exit $ec
