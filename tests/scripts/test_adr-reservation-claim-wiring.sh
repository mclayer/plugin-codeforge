#!/usr/bin/env bash
# tests/scripts/test_adr-reservation-claim-wiring.sh
# CFP-2563 Phase 2 (QADeveloperAgent) — claim 배선 invariant (Q4).
# Change Plan CFP-2563 §8.1 claim invariant + §8.5.2 restart recovery + §8.5.3 replay + §8.2.a AC-8.
#
# 대상: scripts/lib/adr-reservation-atomic-claim.py = **UNCHANGED primitive**(§1 no-rebuild).
#   INV-1..INV-7 (모든 write sha= / retry≤3 / exhausted=exit1 / 단조 비감소 / 동일 sha 2-client=1성공+1×409 /
#   ADR-070 append byte 보존 / 채널 경로 비대칭) 은 **기존 CFP-2491 suite 가 이미 커버** — REUSE(재구축 0):
#     → tests/scripts/test_adr-reservation-atomic-claim.sh (happy/race/exhausted/self_claim/monotonic + m1-m6 + AC-7).
#   본 file 은 wiring 이 추가하는 **신규 testable surface** 만 담당:
#     §8.5.2-P1 crash(GET 후 PUT 전) → re-run 최신 sha 재취득
#     §8.5.2-P2 crash(PUT 200 후 기록 전) → re-run self_claim idempotent skip (double-claim 0)
#     §8.5.3(a) claim replay → 새 번호 미할당 + exit0
#     AC-8 template cross-ref (wrapper=claim / consumer=Glob) — §3.1 배선(doc-reality gap #2)
#     §8.5.3(b) backfill 재실행 no-op = cross-ref tests/scripts/test_adr-reservation-backfill.sh INV-14
#
# primitive 는 무변경(present) → §8.5.2/8.5.3 scenario 는 지금 GREEN. AC-8 template 배선은 RED-until-wired.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$REPO_ROOT/scripts/lib/adr-reservation-atomic-claim.py"
ADR_TEMPLATE="$REPO_ROOT/plugins/codeforge-design/templates/adr.md"
PYBIN="$(command -v python3 || command -v python)"

PASS=0; FAIL=0; PENDING=0
pass()    { echo "  ✓ PASS: $1"; PASS=$((PASS+1)); }
fail()    { echo "  ✗ FAIL: $1"; FAIL=$((FAIL+1)); }
pending() { echo "  … RED-PENDING(배선 부재/interface): $1"; PENDING=$((PENDING+1)); }

# ─── StubClient driver (sibling test_adr-reservation-atomic-claim.sh 와 동일 seam 재사용) ──
run_driver() {
  local scenario="$1"
  "$PYBIN" - "$SRC" "$scenario" <<'PYEOF'
import sys, json, importlib.util, io, contextlib
src_py, scenario = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("acm", src_py)
acm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acm)

class StubClient:
    def __init__(self, max0=133, claims=None):
        self.state_num = max0
        self.claims = list(claims or [])
        self.version = 1
        self.attempt = 0
        self.put_calls = []          # (sent_sha, sent_max)
        self.get_calls = 0
    def get_state(self, state_path):
        self.attempt += 1; self.get_calls += 1
        body = json.dumps({"json": json.dumps({"max_adr_number": self.state_num, "claims": self.claims}),
                           "sha": f"sha-v{self.version}"})
        return acm.GhResponse(status_code=200, body=body)
    def put_state(self, state_path, content_json, blob_sha, message):
        sent = json.loads(content_json)
        self.put_calls.append((blob_sha, sent.get("max_adr_number")))
        if blob_sha != f"sha-v{self.version}":
            return acm.GhResponse(status_code=409)
        self.state_num = sent.get("max_adr_number"); self.claims = sent.get("claims", []); self.version += 1
        return acm.GhResponse(status_code=200)

@contextlib.contextmanager
def _silence():
    saved = sys.stdout; sys.stdout = io.StringIO()
    try: yield
    finally: sys.stdout = saved

def claim(*a, **k):
    with _silence():
        return acm.claim_adr_number(*a, **k)

def emit(t): print(t)

if scenario == "p1_crash_refetch":
    # P1: 세션 X 가 GET(max=140) 후 PUT 전 crash(=X 의 PUT 미발생). 그 사이 세션 Y 가 141 점유(state advance).
    # X re-run → claim() 이 최신 state 를 GET 재취득 → next=142 (stale 140+1=141 재사용 아님).
    c = StubClient(max0=140)
    rY = claim("r","s","b","Y:CFP-2563:run", client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    rX = claim("r","s","b","X:CFP-2563:run", client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    # 최신 sha 재취득 증명: X 의 마지막 PUT sha = Y 점유 후 server version(sha-v2), X 번호 = 142.
    last_sha = c.put_calls[-1][0] if c.put_calls else None
    if rY.adr_number == 141 and rX.adr_number == 142 and last_sha == "sha-v2":
        emit("OK:p1:Y=141:X=142:refetch-sha-v2")
    else:
        emit(f"BAD:Y={rY.adr_number}:X={rX.adr_number}:last_sha={last_sha}")

elif scenario == "p2_crash_self_claim":
    # P2: X 의 PUT 200 성공(state 에 X 의 claimed row 141 존재) 후 기록 전 crash.
    # X re-run → find_self_claim 이 X 를 감지 → self_claim 141, PUT 0회(double-claim 0).
    claims = [{"adr_number": 141, "claimant": "X:CFP-2563:run", "status": "claimed", "claimed_at": "2026-07-03T00:00:00Z"}]
    c = StubClient(max0=141, claims=claims)
    before = len(c.claims)
    r = claim("r","s","b","X:CFP-2563:run", client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    after = len(c.claims)
    if r.status == "self_claim" and r.adr_number == 141 and len(c.put_calls) == 0 and before == after:
        emit("OK:p2:self_claim=141:puts=0:no-new-append")
    else:
        emit(f"BAD:status={r.status}:num={r.adr_number}:puts={len(c.put_calls)}:before={before}:after={after}")

elif scenario == "replay_exit0":
    # §8.5.3(a): claim PUT 200 후 crash → 동일 (adr_number,claimant) 재실행 = 새 번호 미할당 + exit0.
    # exit0 = main() 이 status in (claimed, self_claim) 에 대해 return 0 (silent drop 아님).
    claims = [{"adr_number": 141, "claimant": "X:CFP-2563:run", "status": "claimed", "claimed_at": "2026-07-03T00:00:00Z"}]
    c = StubClient(max0=141, claims=claims)
    r = claim("r","s","b","X:CFP-2563:run", client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    exit_code = 0 if r.status in ("claimed", "self_claim") else 1
    if r.status == "self_claim" and r.adr_number == 141 and exit_code == 0:
        emit("OK:replay:self_claim=141:exit0:no-new-number")
    else:
        emit(f"BAD:status={r.status}:num={r.adr_number}:exit={exit_code}")

else:
    emit("BAD:unknown-scenario"); sys.exit(2)
PYEOF
}

assert_scenario() {
  local name="$1" scenario="$2" expect="$3" out
  out="$(run_driver "$scenario" 2>/dev/null)" || true
  if [[ "$out" == "$expect"* ]]; then pass "$name — $out"; else fail "$name — expected '$expect*', got '$out'"; fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo "CFP-2563 §8.5 — claim wiring invariant (Q4: restart recovery + replay + AC-8)"
echo "═══════════════════════════════════════════════════════════════════════════"

echo ""
echo "── INV-1..INV-7 = REUSE (기존 CFP-2491 suite, 재구축 0) ──"
if [ -f "$REPO_ROOT/tests/scripts/test_adr-reservation-atomic-claim.sh" ]; then
  pass "INV-1..7 커버 재사용 확인: tests/scripts/test_adr-reservation-atomic-claim.sh 존재 (happy/race/exhausted/self_claim/monotonic + m1-m6 + AC-7)"
else
  fail "기존 CFP-2491 claim suite 부재 — INV-1..7 커버 소실"
fi

echo ""
echo "── §8.5.2-P1 restart recovery (crash GET후 PUT전 → re-run 최신 sha 재취득) ──"
if [ -f "$SRC" ]; then
  assert_scenario "§8.5.2-P1 re-fetch latest sha" "p1_crash_refetch" "OK:p1:Y=141:X=142"
else
  pending "§8.5.2-P1 (primitive 부재)"
fi

echo ""
echo "── §8.5.2-P2 restart recovery (crash PUT200후 기록전 → self_claim skip, double-claim 0) ──"
if [ -f "$SRC" ]; then
  assert_scenario "§8.5.2-P2 self_claim idempotent skip" "p2_crash_self_claim" "OK:p2:self_claim=141:puts=0"
else
  pending "§8.5.2-P2 (primitive 부재)"
fi

echo ""
echo "── §8.5.3(a) idempotency replay (claim replay → 새 번호 미할당 + exit0) ──"
if [ -f "$SRC" ]; then
  assert_scenario "§8.5.3(a) replay no-new-number exit0" "replay_exit0" "OK:replay:self_claim=141:exit0"
else
  pending "§8.5.3(a) (primitive 부재)"
fi

echo ""
echo "── §8.5.3(b) backfill 재실행 no-op = cross-ref ──"
echo "  (cross-ref) tests/scripts/test_adr-reservation-backfill.sh INV-14 idempotent 가 커버 — 본 file 중복 검증 회피."

echo ""
echo "── AC-8 / INV-7 template cross-ref (wrapper=claim / consumer=Glob) — §3.1 배선 ──"
# 현 L124 = consumer default `Glob(docs/adr/ADR-*.md) max+1` 만 존재(wrapper=claim 배선 부재 = gap #2).
# 배선 GREEN 조건: consumer Glob cross-ref 존치 AND wrapper=claim 채널 참조 신설(비대칭 명시).
if [ -f "$ADR_TEMPLATE" ]; then
  consumer_ok=0; wrapper_ok=0
  grep -qE 'Glob\(.*adr/ADR-\*' "$ADR_TEMPLATE" && consumer_ok=1
  # wrapper=claim 배선 marker: primitive/state 참조(adr-reservation) 또는 (wrapper ∧ claim) 동시 언급.
  if grep -qE 'adr-reservation' "$ADR_TEMPLATE" || \
     { grep -qiE 'wrapper' "$ADR_TEMPLATE" && grep -qiE 'claim' "$ADR_TEMPLATE"; }; then
    wrapper_ok=1
  fi
  if [ "$consumer_ok" -eq 1 ] && [ "$wrapper_ok" -eq 1 ]; then
    pass "AC-8 template cross-ref (consumer Glob 존치 + wrapper=claim 배선 marker 존재)"
  else
    # wrapper=claim 배선 미착지 → interface-first RED (DeveloperAgent L124 배선 대상).
    pending "AC-8 template cross-ref (consumer_ok=$consumer_ok wrapper_claim_wire=$wrapper_ok — wrapper=claim 배선 대기)"
  fi
else
  pending "AC-8 template (plugins/codeforge-design/templates/adr.md 부재)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Results: $PASS passed, $FAIL failed, $PENDING red-pending(배선 부재/interface)"
echo "═══════════════════════════════════════════════════════════════════════════"
if [ "$FAIL" -eq 0 ] && [ "$PENDING" -eq 0 ]; then
  echo "All GREEN ✓"; exit 0
else
  echo "RED — 배선 착지 후 재실행(PL consolidated) 시 GREEN 기대."; exit 1
fi
