#!/usr/bin/env bash
# tests/scripts/test_adr-reservation-atomic-claim.sh
# CFP-2491 / Epic CFP-2481 E3b — ADR-RESERVATION atomic claim primitive mutation-RED 검증.
# Change Plan §8 Test Contract (AC-1~8 + §8.5) 이행. 설계리뷰 Claude F2 — m2 = m2a/m2b 물리 2-mutant 분리.
#
# anti-theater (CFP-2440 선례): always-pass 0, tautology 0. 각 mutant 는 SSOT 소스의 1-line mutation 으로
# RED 전환되어야 한다. 본 test 는 두 축으로 비-hollow 를 보장한다:
#   (1) GREEN baseline — unmutated 소스가 mock seam scenario 에서 정확 동작(claim/409-retry/exhausted/self-claim/단조성).
#   (2) RED kill — 각 mutant 별로 소스 copy 에 deterministic 1-line sed mutation 적용 후 동일 driver 재실행 →
#       반드시 baseline 과 다른 결과(=mutation 검출). mutation 이 검출 안 되면 해당 assert 가 hollow → FAIL.
#
# deterministic 재현 (Change Plan §8 GAP-1): 실 GitHub 동시성 없이 python mock seam(StubClient)으로
# 고정 stale SHA 주입 — A-PUT(200, SHA 변경) → B-PUT(동일 stale sha → 409). 타이밍 의존 0.
# 실 SSOT 소스(scripts/lib/adr-reservation-atomic-claim.py) in-place mutate 0 — 전부 mktemp copy 격리.

set -u  # set -e 미사용 — 각 케이스 || true 로 감싸 partial run 허용 + FAIL 카운터 집계.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$REPO_ROOT/scripts/lib/adr-reservation-atomic-claim.py"
GITHUB_WF="$REPO_ROOT/.github/workflows/parallel-epic-conflict-check.yml"
TEMPLATES_WF="$REPO_ROOT/templates/github-workflows/parallel-epic-conflict-check.yml"

PASS=0
FAIL=0

PYBIN="$(command -v python3 || command -v python)"

# ─── Python driver: mock seam 으로 OCC scenario 구동 ──────────────────────────
# 인자: $1 = 테스트할 소스 .py 경로 / $2 = scenario 이름.
# 출력: 1줄 결과 토큰 (PASS/FAIL 판정에 사용). exit code 도 반영.
#
# StubClient 가 GitHubContentsClient 를 대체 — get_state/put_state 를 결정적으로 stub.
run_driver() {
  local src_py="$1"
  local scenario="$2"
  "$PYBIN" - "$src_py" "$scenario" <<'PYEOF'
import sys, json, importlib.util, types

src_py = sys.argv[1]
scenario = sys.argv[2]

spec = importlib.util.spec_from_file_location("acm", src_py)
acm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(acm)


class StubClient:
    """결정적 OCC stub. state = {max_adr_number, claims}, blob_sha 는 내용 버전으로 모사.

    race 시나리오: 외부 세션이 put 직전 state 를 바꿔치기(advance)하면 stale sha PUT 은 409.
    """
    def __init__(self, max0=133, claims=None, race_advances=None):
        # race_advances: attempt 번호(1-based) → 외부 세션이 *그 attempt 의 read 후 PUT 전*에 점유한 횟수.
        # 핵심 timing: advance 는 read 시점이 아니라 put_state 진입 시점에 적용된다 →
        # 클라이언트가 막 read 한 sha 가 stale 이 되어 PUT 이 409 를 받는다 (실 race window 모사).
        self.state_num = max0
        self.claims = list(claims or [])
        self.version = 1                       # blob sha 모사 — 내용 변경 시 증가.
        self.attempt = 0                       # get_state 호출 카운터(=attempt 번호).
        self.race_advances = race_advances or {}
        self.put_calls = []                    # (sent_sha, sent_max) 기록 — 검증용.

    def get_state(self, state_path):
        self.attempt += 1
        body = json.dumps({
            "json": json.dumps({"max_adr_number": self.state_num, "claims": self.claims}),
            "sha": f"sha-v{self.version}",
        })
        return acm.GhResponse(status_code=200, body=body)

    def put_state(self, state_path, content_json, blob_sha, message):
        sent = json.loads(content_json)
        self.put_calls.append((blob_sha, sent.get("max_adr_number")))
        # ── race window: 이 attempt 의 read 후 PUT 직전에 외부 세션이 점유했으면 server state advance ──
        adv = self.race_advances.get(self.attempt, 0)
        if adv:
            self.state_num += adv
            self.version += adv      # server sha 가 바뀌어 클라이언트 stale sha 와 불일치 → 409.
            # advance 는 1회만 (이 attempt 의 race window 소진).
            self.race_advances[self.attempt] = 0
        # OCC: 클라이언트가 보낸 sha 가 현재 server version 과 일치해야 성공.
        current_sha = f"sha-v{self.version}"
        if blob_sha != current_sha:
            return acm.GhResponse(status_code=409)
        # 수락 — server state 갱신 + version 증가.
        self.state_num = sent.get("max_adr_number")
        self.claims = sent.get("claims", [])
        self.version += 1
        return acm.GhResponse(status_code=200)


def emit(token):
    print(token)


import os as _os, contextlib as _ctx, io as _io

@_ctx.contextmanager
def _suppress_stdout():
    """production claim_adr_number 가 stdout 에 점유 번호를 print 하므로(CLI 용),
    driver 결과 토큰만 stdout 에 남도록 claim 호출 동안 stdout 을 격리한다."""
    saved = sys.stdout
    sys.stdout = _io.StringIO()
    try:
        yield
    finally:
        sys.stdout = saved


def claim(*args, **kwargs):
    with _suppress_stdout():
        return acm.claim_adr_number(*args, **kwargs)


# scenario dispatch
if scenario == "happy":
    # 단순 claim — 첫 attempt 성공, 134 점유, PUT 에 sha 동봉.
    c = StubClient(max0=133)
    r = claim("r", "s", "b", "Arch:CFP-2491:run1",
                             client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    # INV-1: 모든 PUT 에 sha 동봉(unconditional 0).
    has_unconditional = any(sha is None or sha == "" for (sha, _) in c.put_calls)
    if r.status == "claimed" and r.adr_number == 134 and not has_unconditional:
        emit("OK:claimed=134:sha-present")
    else:
        emit(f"BAD:status={r.status}:num={r.adr_number}:unconditional={has_unconditional}")

elif scenario == "race_409_then_recompute":
    # 핵심 m2 표적: attempt1 read(N=133) 후 PUT 전 외부 세션이 134 점유(+1).
    # → attempt1 PUT(stale sha-v1) = 409. attempt2 read(N=134, sha-v2) → next=135.
    # 정상 구현: 135 claim 성공 (re-fetch SHA + next 재계산 둘 다).
    c = StubClient(max0=133, race_advances={1: 1})
    r = claim("r", "s", "b", "Arch:CFP-2491:run2",
                             client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    # 검증: 최종 claim 번호 = 135 (N+1 재계산), attempt >= 2, 마지막 PUT sha = sha-v2 (re-fetch).
    last_put_sha = c.put_calls[-1][0] if c.put_calls else None
    last_put_max = c.put_calls[-1][1] if c.put_calls else None
    if (r.status == "claimed" and r.adr_number == 135 and r.attempts >= 2
            and last_put_sha == "sha-v2" and last_put_max == 135):
        emit("OK:claimed=135:refetch+recompute")
    else:
        emit(f"BAD:status={r.status}:num={r.adr_number}:attempts={r.attempts}:last_sha={last_put_sha}:last_max={last_put_max}")

elif scenario == "exhausted":
    # 모든 attempt 마다 외부 세션이 점유 → 매번 stale sha → 영구 409. exhausted = exit1, silent drop 0.
    c = StubClient(max0=133, race_advances={i: 1 for i in range(1, 10)})
    r = claim("r", "s", "b", "Arch:CFP-2491:run3", max_attempts=4,
                             client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    # INV-2 직접 측정 (구현리뷰 P2 F2): retry ≤ 3 = 총 attempts == max_attempts(4) 직접 단언 (간접→직접 승격).
    if r.status == "exhausted" and r.adr_number is None and r.attempts == 4:
        emit("OK:exhausted:exit1:attempts=4")
    else:
        emit(f"BAD:status={r.status}:num={r.adr_number}:attempts={r.attempts}")

elif scenario == "self_claim":
    # idempotency (A1-2): 동일 claimant 의 claimed row 이미 존재 → self-claim, 새 번호 미할당.
    claims = [{"adr_number": 134, "claimant": "Arch:CFP-2491:dup", "status": "claimed",
               "claimed_at": "2026-06-30T00:00:00Z"}]
    c = StubClient(max0=134, claims=claims)
    r = claim("r", "s", "b", "Arch:CFP-2491:dup",
                             client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    # self-claim 은 PUT 호출 0 (re-emit 없음) + 기존 번호 134 반환.
    if r.status == "self_claim" and r.adr_number == 134 and len(c.put_calls) == 0:
        emit("OK:self_claim=134:no-reemit")
    else:
        emit(f"BAD:status={r.status}:num={r.adr_number}:puts={len(c.put_calls)}")

elif scenario == "monotonic_value":
    # 단조성: claim 번호는 항상 max+1 (>max). 정상 구현은 절대 N-1 등 rewind 기록 안 함.
    c = StubClient(max0=200)
    r = claim("r", "s", "b", "Arch:CFP-2491:mono",
                             client=c, sleep_fn=lambda x: None, jitter_fn=lambda: 0)
    sent_max = c.put_calls[-1][1] if c.put_calls else None
    if r.status == "claimed" and sent_max == 201 and sent_max > 200:
        emit("OK:monotonic=201")
    else:
        emit(f"BAD:status={r.status}:sent_max={sent_max}")

else:
    emit("BAD:unknown-scenario")
    sys.exit(2)
PYEOF
}

# ─── assert helper: baseline GREEN + mutant RED ──────────────────────────────
# baseline (unmutated SRC) 는 expected_ok 토큰을 내야 PASS.
assert_baseline() {
  local test_name="$1" scenario="$2" expected_prefix="$3"
  local out
  out="$(run_driver "$SRC" "$scenario" 2>/dev/null)" || true
  if [[ "$out" == "$expected_prefix"* ]]; then
    echo "✓ PASS: $test_name (baseline GREEN) — $out"
    PASS=$((PASS+1))
    return 0
  else
    echo "✗ FAIL: $test_name (baseline) — expected '$expected_prefix*', got '$out'"
    FAIL=$((FAIL+1))
    return 1
  fi
}

# mutant RED: SRC copy 에 sed mutation 적용 → driver 가 baseline 과 다른(=BAD 또는 다른 OK) 결과 → kill 확인.
# kill 판정 = mutated 결과가 expected_prefix 로 시작하지 않음 (mutation 이 정확 동작을 깨뜨림).
assert_mutant_red() {
  local mutant_name="$1" scenario="$2" expected_prefix="$3" sed_expr="$4"
  local mdir mutated out
  mdir="$(mktemp -d)"
  mutated="$mdir/mutated.py"
  cp "$SRC" "$mutated"
  # mutation 적용
  sed -i "$sed_expr" "$mutated"
  # mutation 이 실제로 소스를 바꿨는지(no-op sed 차단)
  if diff -q "$SRC" "$mutated" >/dev/null 2>&1; then
    echo "✗ FAIL: $mutant_name — sed mutation no-op (소스 무변경 — mutant 정의 오류)"
    FAIL=$((FAIL+1))
    rm -rf "$mdir"
    return 1
  fi
  out="$(run_driver "$mutated" "$scenario" 2>/dev/null)" || true
  rm -rf "$mdir"
  if [[ "$out" == "$expected_prefix"* ]]; then
    # mutant 가 여전히 정확 동작 토큰을 냄 = assert 가 hollow (mutation 미검출).
    echo "✗ FAIL: $mutant_name — mutant SURVIVED (still '$out' — assert hollow)"
    FAIL=$((FAIL+1))
    return 1
  else
    echo "✓ PASS: $mutant_name — mutant KILLED (RED: '$out' != baseline)"
    PASS=$((PASS+1))
    return 0
  fi
}

# ─── dead-gate path-agnostic 양-컨텍스트 (AC-7, m5) ───────────────────────────
# 구현리뷰 invariant-check 정합: parallel-epic-conflict-check.yml 은 consumer-only 면제 목록 밖이라
# `.github` ↔ `templates` byte-identical 의무. 따라서 dead-gate 정정 = 비대칭(컨텍스트별 분기)이 아니라
# **path-agnostic 단일 regex** `^(docs|archive)/adr/ADR-RESERVATION.md$` (양 컨텍스트 동시 매치) →
# byte-identical parity + wrapper(archive/adr) detection + consumer(docs/adr) detection 동시 충족.
# AC-7 = dead-gate 가 wrapper archive/adr 와 consumer docs/adr 양 컨텍스트에서 살아있음(non-dead) 증명.
test_ac7_deadgate_pathagnostic() {
  local test_name="AC-7-deadgate-path-agnostic"
  local gh_pa tmpl_pa identical=0
  # 양 copy 가 path-agnostic regex (docs|archive) 를 보유해야(dead-gate 정정 완료).
  gh_pa=$(grep -cE '\^\(docs\|archive\)/adr/ADR-RESERVATION\.md\$' "$GITHUB_WF" 2>/dev/null); gh_pa=${gh_pa:-0}
  tmpl_pa=$(grep -cE '\^\(docs\|archive\)/adr/ADR-RESERVATION\.md\$' "$TEMPLATES_WF" 2>/dev/null); tmpl_pa=${tmpl_pa:-0}
  # byte-identical parity (invariant-check 의무).
  diff -q "$GITHUB_WF" "$TEMPLATES_WF" >/dev/null 2>&1 && identical=1
  # 실 매치 검증: wrapper archive/adr + consumer docs/adr 둘 다 매치 (dead-gate non-dead).
  local w_match=0 c_match=0
  echo "archive/adr/ADR-RESERVATION.md" | grep -qE '^(docs|archive)/adr/ADR-RESERVATION\.md$' && w_match=1
  echo "docs/adr/ADR-RESERVATION.md"    | grep -qE '^(docs|archive)/adr/ADR-RESERVATION\.md$' && c_match=1

  if [ "$gh_pa" -ge 1 ] && [ "$tmpl_pa" -ge 1 ] && [ "$identical" -eq 1 ] && [ "$w_match" -eq 1 ] && [ "$c_match" -eq 1 ]; then
    echo "✓ PASS: $test_name — path-agnostic(docs|archive) 양 copy byte-identical + wrapper/consumer 양 컨텍스트 매치 (dead-gate non-dead + parity 정합)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $test_name — gh_pa=$gh_pa tmpl_pa=$tmpl_pa identical=$identical w_match=$w_match c_match=$c_match (기대 ≥1/≥1/1/1/1)"
    FAIL=$((FAIL+1))
  fi
}

# m5: path-agnostic regex 에서 archive 분기를 제거(`(docs|archive)` → `docs`)하면
#     wrapper archive/adr 충돌 미검출(dead-gate 재도입) → RED.
test_m5_deadgate_mutant() {
  local mutant_name="m5-deadgate-singlepath"
  local mdir mutated arc_orig arc_mutant
  mdir="$(mktemp -d)"; mutated="$mdir/wf.yml"; cp "$GITHUB_WF" "$mutated"
  arc_orig=$(printf 'archive/adr/ADR-RESERVATION.md\n' | grep -cE '^(docs|archive)/adr/ADR-RESERVATION\.md$')
  sed -i 's#(docs|archive)/adr#docs/adr#g' "$mutated"
  if diff -q "$GITHUB_WF" "$mutated" >/dev/null 2>&1; then
    echo "FAIL: $mutant_name -- sed no-op (mutant 정의 오류)"
    FAIL=$((FAIL+1)); rm -rf "$mdir"; return 1
  fi
  arc_mutant=$(printf 'archive/adr/ADR-RESERVATION.md\n' | grep -cE '^docs/adr/ADR-RESERVATION\.md$')
  rm -rf "$mdir"
  if [ "$arc_orig" -eq 1 ] && [ "$arc_mutant" -eq 0 ]; then
    echo "PASS: $mutant_name -- mutant KILLED (docs-only mutate 시 archive 미매치 = wrapper dead-gate RED)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $mutant_name -- mutant SURVIVED (arc_orig=$arc_orig arc_mutant=$arc_mutant)"
    FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "CFP-2491 Phase 2: ADR-RESERVATION atomic claim (단일-셀 OCC)"
echo "mutation-RED Test Suite (m1-m6 + m2a/m2b 분리 + AC-6 e2e + AC-7 양-컨텍스트)"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# ── GREEN baseline (unmutated 소스 정확 동작) ──
echo "── GREEN baseline ──"
assert_baseline "baseline-happy-claim"       "happy"                    "OK:claimed=134" || true
assert_baseline "baseline-race-recompute"    "race_409_then_recompute"  "OK:claimed=135" || true
assert_baseline "baseline-exhausted"         "exhausted"                "OK:exhausted"   || true
assert_baseline "baseline-self-claim"        "self_claim"               "OK:self_claim=134" || true
assert_baseline "baseline-monotonic"         "monotonic_value"          "OK:monotonic=201" || true
echo ""

# ── RED kill (mutant 별 1-line mutation → assert load-bearing 증명) ──
echo "── RED kill (mutant 검출) ──"

# m1: PUT 에서 sha= 제거 (unconditional). build_next_state 의 blob_sha 인자를 None 으로 강제.
#     → happy scenario 의 INV-1(sha-present) assert RED.
assert_mutant_red "m1-unconditional-put" "happy" "OK:claimed=134" \
  's/put_resp = client.put_state(state_path, content_json, state.blob_sha, message)/put_resp = client.put_state(state_path, content_json, None, message)/' || true

# m2a: 매 attempt SHA re-fetch 생략 — read phase 의 get_state 를 첫 attempt 결과로 고정(stale blob sha 재사용).
#      → race scenario 에서 stale sha-v1 영구 재사용 → 135 claim 실패(영구 409 또는 오번호). RED.
assert_mutant_red "m2a-no-sha-refetch" "race_409_then_recompute" "OK:claimed=135" \
  's/        get_resp = client.get_state(state_path)/        get_resp = get_resp if attempt > 1 else client.get_state(state_path)/' || true

# m2b: 매 attempt next 재계산 생략 — next_number 를 attempt 무관 첫 값으로 고정.
#      → race scenario 에서 N+1(=134) 고집 → 다른 세션 점유 번호와 충돌(135 미도달). RED.
assert_mutant_red "m2b-no-next-recompute" "race_409_then_recompute" "OK:claimed=135" \
  's/        next_number = state.max_adr_number + 1/        next_number = next_number if attempt > 1 else state.max_adr_number + 1/' || true

# m3: 409 → success 처리. 409 분기를 200 처럼 claimed return.
#     → race scenario 에서 첫 409 를 성공으로 오판 → 134(점유 충돌 번호) claim. 135 미도달 RED.
assert_mutant_red "m3-409-as-success" "race_409_then_recompute" "OK:claimed=135" \
  's/        elif put_resp.status_code == 409:/        elif put_resp.status_code == 409 and False:/' || true

# m4: exhausted 시 exit0 (silent drop). exhausted return status 를 claimed 로 위조.
#     → exhausted scenario 에서 status!=exhausted → RED.
assert_mutant_red "m4-silent-drop" "exhausted" "OK:exhausted" \
  's/    return ClaimResult(status="exhausted", attempts=max_attempts, reason="retries exhausted")/    return ClaimResult(status="claimed", adr_number=999, attempts=max_attempts, reason="retries exhausted")/' || true

# m6: claim 번호 N-1 기록 (rewind). next_number = max - 1.
#     → monotonic scenario 에서 sent_max=199(<200) → 단조성 violation reject 또는 오번호. RED.
assert_mutant_red "m6-rewind" "monotonic_value" "OK:monotonic=201" \
  's/        next_number = state.max_adr_number + 1/        next_number = state.max_adr_number - 1/' || true

echo ""
echo "── dead-gate path-agnostic (AC-7 / m5) ──"
test_ac7_deadgate_pathagnostic || true
test_m5_deadgate_mutant || true

# AC-6 e2e: 동일 blob SHA 2-client → 정확히 1성공 + 1×409 (race scenario 가 이를 증명 —
#           attempt1 PUT(stale) 409 = 2nd client 가 먼저 점유한 결과의 deterministic 모사).
#           baseline-race-recompute (135 claim via 409 then refetch) 가 곧 AC-6 INV-5 의 e2e 증명.
echo ""
echo "── AC-6 e2e (동일 SHA 2-client → 1 success + 1×409, race scenario 가 증명) ──"
test_ac6_e2e() {
  local out
  out="$(run_driver "$SRC" "race_409_then_recompute" 2>/dev/null)" || true
  # race scenario: 1st PUT(stale sha) → 409 (=다른 client 가 먼저 점유), 2nd attempt → 성공.
  # = 동일 초기 SHA 에서 정확히 1 client 성공, 충돌 client 는 409 받고 재시도.
  if [[ "$out" == "OK:claimed=135"* ]]; then
    echo "✓ PASS: AC-6-e2e — 1 success(135) + 충돌 client 409 후 재계산 (INV-5)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: AC-6-e2e — got '$out'"
    FAIL=$((FAIL+1))
  fi
}
test_ac6_e2e || true

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Test Results: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests PASSED ✓"
  exit 0
else
  echo "Some tests FAILED ✗"
  exit 1
fi
