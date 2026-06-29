#!/usr/bin/env bash
# test-check-verification-floor.sh — discriminating test harness for check-verification-floor.sh
# (CFP-2471 / Epic CFP-2468 W3). Change Plan §8.1 TC-1/TC-2 + §8.4 MUT-1/MUT-2 (mutation 생존 0).
#
# 검증 floor = ≥1 independent peer (SoD). 축①(self-audit verdict 무효) + 축②(silent degrade 차단)
# 의 discriminating test:
#   TC-1a (RED):  peer_count:0 + PASS  → strict 차단 (exit 1) 기대
#   TC-1b (GREEN): peer_count:2 + PASS → 통과 (exit 0) 기대
#   TC-1c (GREEN): peer_count:0 + FIX  → self-audit PASS 발화 아님 → 통과 (차단 비대상)
#   TC-2a (RED):  peer_count:1 + degrade_acknowledged 부재 (silent) → 차단 (exit 1) 기대
#   TC-2b (GREEN): peer_count:1 + degrade_acknowledged:true + degrade_reason (honest) → 통과
#   TC-2c (RED):  peer_count:1 + degrade_acknowledged:true 인데 degrade_reason 부재 → 차단 (사유 강제)
#   TC-3  (GREEN): peer_degrade block 부재 (정상 2-peer 또는 by-design) → 통과
#
# MUT-1 (hollow-gate 차단): 축①의 peer_count==0 검사를 무력화 (>0 비교로 mutate) → TC-1a RED 가
#   GREEN 으로 새면 hollow. mutate copy 가 TC-1a 를 PASS 통과시키면 본 harness FAIL.
# MUT-2 (hollow-gate 차단): 축②의 degrade_acknowledged presence 검사를 항상-true 로 mutate →
#   TC-2a silent RED 가 GREEN 으로 새면 hollow.
#
# Usage: bash scripts/test-check-verification-floor.sh
set -uo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
SCRIPT_SRC="$REPO_ROOT/scripts/check-verification-floor.sh"

if [ ! -f "$SCRIPT_SRC" ]; then
    echo "FATAL: check-verification-floor.sh 부재: $SCRIPT_SRC" >&2
    exit 2
fi

PASS=0
FAIL=0

WORK="$(mktemp -d)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

# verdict packet fixture writer — $1=name, $2=heredoc body
write_fixture() {
    local name="$1"
    cat > "$WORK/$name.yaml"
}

# 단일 케이스: $1 name / $2 fixture file / $3 expect_exit (0|1) / $4 expect_grep (stderr/stdout 패턴, 빈=skip)
#             $5 script (검사 대상 script path, 기본 SCRIPT_SRC)
run_case() {
    local name="$1" fixture="$2" expect_exit="$3" expect_grep="$4" script="${5:-$SCRIPT_SRC}"
    local out rc
    out="$(bash "$script" --verdict "$WORK/$fixture.yaml" --strict 2>&1)"
    rc=$?
    local ok=1
    if [ "$rc" -ne "$expect_exit" ]; then
        ok=0
        echo "  exit mismatch: got $rc, expected $expect_exit"
    fi
    if [ -n "$expect_grep" ] && ! printf '%s' "$out" | grep -q "$expect_grep"; then
        ok=0
        echo "  expected pattern not found: $expect_grep"
    fi
    if [ "$ok" -eq 1 ]; then
        echo "PASS $name"
        PASS=$((PASS + 1))
    else
        echo "FAIL $name"
        printf '%s\n' "$out" | sed 's/^/    | /'
        FAIL=$((FAIL + 1))
    fi
}

# ── fixtures ──────────────────────────────────────────────────────────────
write_fixture "tc1a-selfaudit-pass" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_degrade:
    peer_count: 0
    degrade_reason: "self-audit only — 0 independent peer"
    degrade_acknowledged: false
EOF

write_fixture "tc1b-dualpeer-pass" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_degrade:
    peer_count: 2
    degrade_acknowledged: false
EOF

write_fixture "tc1c-selfaudit-fix" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: FIX
  peer_degrade:
    peer_count: 0
EOF

write_fixture "tc2a-silent-degrade" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_degrade:
    peer_count: 1
    degrade_reason: "Codex 미설치"
EOF

write_fixture "tc2b-honest-degrade" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_degrade:
    peer_count: 1
    degrade_reason: "Codex CLI 미설치 — single-peer honest degrade"
    degrade_acknowledged: true
EOF

write_fixture "tc2c-honest-no-reason" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_degrade:
    peer_count: 1
    degrade_acknowledged: true
EOF

write_fixture "tc3-no-degrade-block" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
EOF

echo "=== check-verification-floor.sh discriminating test (CFP-2471 / W3) ==="

# ── 축① ──
run_case "TC-1a self-audit(peer_count:0)+PASS → 차단"   "tc1a-selfaudit-pass" 1 '\[FAIL 축①\]'
run_case "TC-1b dual-peer(peer_count:2)+PASS → 통과"    "tc1b-dualpeer-pass"  0 '\[OK 축①\]'
run_case "TC-1c self-audit(peer_count:0)+FIX → 통과"    "tc1c-selfaudit-fix"  0 '\[OK 축①\]'

# ── 축② ──
run_case "TC-2a silent degrade(ack 부재) → 차단"        "tc2a-silent-degrade" 1 '\[FAIL 축②\]'
run_case "TC-2b honest degrade(ack:true+reason) → 통과" "tc2b-honest-degrade" 0 '\[OK 축②\]'
run_case "TC-2c honest degrade(reason 부재) → 차단"     "tc2c-honest-no-reason" 1 '\[FAIL 축②\]'

# ── 정상 경로 ──
run_case "TC-3 peer_degrade block 부재 → 통과"          "tc3-no-degrade-block" 0 ''

# ── MUT-1 (hollow-gate 차단): 축① peer_count==0 검사를 무력화 ──
# `[ "$peer_count" -eq 0 ]` → `[ "$peer_count" -lt 0 ]` (항상 false) 로 mutate.
# 이 mutant 은 TC-1a 를 더 이상 차단하지 못함 (RED→GREEN 누출) → harness 가 검출해야.
MUT1="$WORK/mut1-check-verification-floor.sh"
sed -E 's/\[ "\$peer_count" -eq 0 \]/[ "$peer_count" -lt 0 ]/' "$SCRIPT_SRC" > "$MUT1"
chmod +x "$MUT1"
mut1_out="$(bash "$MUT1" --verdict "$WORK/tc1a-selfaudit-pass.yaml" --strict 2>&1)"; mut1_rc=$?
if [ "$mut1_rc" -eq 0 ]; then
    echo "PASS MUT-1 mutant(축① 무력화)이 TC-1a 를 더 이상 차단 못 함 — 원본 검사 load-bearing 입증 (mutation 생존 0)"
    PASS=$((PASS + 1))
else
    echo "FAIL MUT-1 mutant 이 여전히 TC-1a 차단 (rc=$mut1_rc) — 축① 검사가 hollow (mutation 생존)"
    printf '%s\n' "$mut1_out" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
fi

# ── MUT-2 (hollow-gate 차단): 축② degrade_acknowledged 검사 무력화 ──
# `ack_is_true()` body 의 `[ "$val" = "true" ]` → `[ "$val" != "true" ]` 반전 시,
# silent (ack 부재 → val="") 가 true 로 평가돼 honest 경로로 빠짐 → TC-2a RED→GREEN 누출.
MUT2="$WORK/mut2-check-verification-floor.sh"
sed -E 's/\[ "\$val" = "true" \]/[ "$val" != "true" ]/' "$SCRIPT_SRC" > "$MUT2"
chmod +x "$MUT2"
mut2_out="$(bash "$MUT2" --verdict "$WORK/tc2a-silent-degrade.yaml" --strict 2>&1)"; mut2_rc=$?
if [ "$mut2_rc" -eq 0 ]; then
    echo "PASS MUT-2 mutant(축② ack 검사 반전)이 TC-2a silent 를 더 이상 차단 못 함 — 원본 검사 load-bearing 입증 (mutation 생존 0)"
    PASS=$((PASS + 1))
else
    echo "FAIL MUT-2 mutant 이 여전히 TC-2a 차단 (rc=$mut2_rc) — 축② 검사가 hollow (mutation 생존)"
    printf '%s\n' "$mut2_out" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Summary: PASS=$PASS FAIL=$FAIL ==="
[ "$FAIL" -eq 0 ]
