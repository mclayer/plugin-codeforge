#!/usr/bin/env bash
# test-check-verification-floor.sh — discriminating test harness for check-verification-floor.sh
# (CFP-2471 / Epic CFP-2468 W3 · CFP-2597 Phase 2 축③). Change Plan §8.1 TC-1/TC-2 + §8.4 MUT-1/MUT-2
# + §8 축③ (peer-completion falsifiability) TC-4a~g + MUT-3/MUT-4/MUT-5 (mutation 생존 0).
#
# 검증 floor = ≥1 independent peer (SoD). 축①(self-audit verdict 무효) + 축②(silent degrade 차단)
# + 축③(peer-completion falsifiability — pl_recommendation: PASS 는 실재+non-empty peer_verdicts[]
# artifact 로 뒷받침돼야; 자기단언 verify_status 불신·게이트 독립 stat) 의 discriminating test.
#
#   [축①]  TC-1a (RED):  peer_count:0 + PASS  → strict 차단 (exit 1) 기대
#          TC-1c (GREEN): peer_count:0 + FIX  → self-audit PASS 발화 아님 → 통과 (차단 비대상)
#   [축②]  TC-2a (RED):  peer_count:1 + degrade_acknowledged 부재 (silent) → 차단 (exit 1) 기대
#          TC-2c (RED):  peer_count:1 + degrade_acknowledged:true 인데 degrade_reason 부재 → 차단 (사유 강제)
#   [축③]  TC-4a  (GREEN): PASS + peer_degrade{peer_count:2} + peer_verdicts[] (실 non-empty target
#                          + worker_recommendation) → 통과 (multi-peer 주장이 artifact 로 뒷받침)
#          TC-4b-i  (RED): PASS + peer_degrade{peer_count:2} + peer_verdicts[] 부재 → 차단 (축③-missing).
#                          ★구 TC-1b 재분류 — peer_count:2 위조 anti-evasion (forged multi-peer claim)
#          TC-4b-ii (RED): PASS + peer_degrade block 부재 + peer_verdicts[] 부재 → 차단 (축③-missing).
#                          ★구 TC-3 재분류 — bare no-degrade 조기종합
#          TC-4c   (RED):  PASS + peer_verdicts[] entry 의 target 미실재 → 차단 (축③-unresolved).
#                          ★load-bearing: entry 의 self-asserted verify_status:verified 를 불신하고
#                          게이트가 독립 stat 으로 RED 내는지 실증
#          TC-4d   (RED):  PASS + peer_verdicts[] target 빈 파일 (0 bytes) → 차단 (축③-empty)
#          TC-4e (GREEN):  honest single-peer degrade (peer_count:1+ack:true+degrade_reason,
#                          peer_verdicts 부재) → 축③ stand-down → 통과. ★구 TC-2b byte-identical
#                          fixture — AC-A3 무회귀 (honest-degrade 오차단 방지)
#          TC-4f (GREEN):  PASS + peer_degrade block 부재 + peer_verdicts[] (실 non-empty target
#                          + worker_recommendation) → 통과 (bare PASS 가 artifact 로 뒷받침)
#          TC-4g   (RED):  PASS + peer_verdicts[] target 실재+non-empty 이나 worker_recommendation
#                          부재 → 차단 (축③-content, advisory content-binding)
#
# MUT-1 (hollow-gate 차단): 축①의 peer_count==0 검사를 무력화 (>0 비교로 mutate) → TC-1a RED 가
#   GREEN 으로 새면 hollow. mutate copy 가 TC-1a 를 PASS 통과시키면 본 harness FAIL.
# MUT-2 (hollow-gate 차단): 축②의 degrade_acknowledged presence 검사를 항상-true 로 mutate →
#   TC-2a silent RED 가 GREEN 으로 새면 hollow.
# MUT-3 (hollow-gate 차단): 축③-unresolved 앵커 `[ ! -e "$resolved_target" ]` 를 무력화 (부정 제거) →
#   TC-4c RED 가 GREEN 으로 새면 hollow (원본 독립 stat 검사 load-bearing 입증).
# MUT-4 (hollow-gate 차단): 축③-empty 앵커 `[ ! -s "$resolved_target" ]` 만 무력화 (앞 `[ -e ]` 가드 불변) →
#   TC-4d RED 가 GREEN 으로 새면 hollow.
# MUT-5 (guard load-bearing 입증): 축③ honest-degrade stand-down 단일 조건을 무력화 → honest degrade
#   TC-4e 가 축③-missing 으로 오차단되면 원본 stand-down 가드 load-bearing (AC-A3 무회귀 보증).
#   ★MUT-1/2 와 반대 방향 assert: mutant 이 이제 TC-4e 를 차단(exit≠0)하면 kill 성공.
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

# ── 축③ fixtures (execution-backed hermetic — peer_verdicts[] target 실 artifact 로 검증) ──
# TC-4a: PASS + peer_degrade{peer_count:2} + peer_verdicts[] (실 non-empty target) → GREEN
#        (claimed-multi 를 artifact 로 뒷받침 — TC-4b-i 의 cure, anti-evasion 짝)
write_fixture "tc4a-peer-backed-multi" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_degrade:
    peer_count: 2
    degrade_acknowledged: false
  peer_verdicts:
    - form: file-path-reference
      target: tc4a-peer1.txt
      verify_status: verified
      worker: claude
      worker_recommendation: PASS
EOF

# TC-4c (load-bearing): peer_verdicts[] target 미실재 → 축③-unresolved.
#   verify_status: verified 는 자기단언 — 게이트가 이를 불신하고 독립 stat 으로 RED 내야 함.
write_fixture "tc4c-peer-missing" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_verdicts:
    - form: file-path-reference
      target: tc4c-peer1.txt
      verify_status: verified
      worker: claude
      worker_recommendation: PASS
EOF

# TC-4d: peer_verdicts[] target 실재하나 빈 파일 (0 bytes) → 축③-empty.
write_fixture "tc4d-peer-empty" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_verdicts:
    - form: file-path-reference
      target: tc4d-peer1.txt
      verify_status: verified
      worker: claude
      worker_recommendation: PASS
EOF

# TC-4f: peer_degrade block 부재 + peer_verdicts[] (실 non-empty target) → GREEN
#        (bare PASS 를 artifact 로 뒷받침 — TC-4b-ii 의 cure)
write_fixture "tc4f-peer-backed-nodegrade" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_verdicts:
    - form: file-path-reference
      target: tc4f-peer1.txt
      verify_status: verified
      worker: claude
      worker_recommendation: PASS
EOF

# TC-4g (advisory): peer_verdicts[] target 실재+non-empty 이나 worker_recommendation 부재 → 축③-content.
write_fixture "tc4g-peer-nocontent" <<'EOF'
review_verdict:
  contract_version: "4.15"
  lane: code
  story_key: CFP-TEST
  pl_recommendation: PASS
  peer_verdicts:
    - form: file-path-reference
      target: tc4g-peer1.txt
      verify_status: verified
      worker: claude
EOF

# ── 축③ peer_verdict 실 artifact 생성 (target = dirname(verdict)=$WORK 기준 상대 resolve) ──
printf 'peer verdict artifact — claude review PASS\n' > "$WORK/tc4a-peer1.txt"
# tc4c-peer1.txt 는 의도적으로 미생성 (TC-4c load-bearing: 자기단언 verify_status 불신, 독립 stat 으로 RED 강제)
: > "$WORK/tc4d-peer1.txt"   # 0 bytes (빈 파일 — 축③-empty 유도)
printf 'peer verdict artifact — bare PASS backed\n' > "$WORK/tc4f-peer1.txt"
printf 'peer verdict artifact — no worker_recommendation\n' > "$WORK/tc4g-peer1.txt"

echo "=== check-verification-floor.sh discriminating test (CFP-2471 / W3 · CFP-2597 P2 축③) ==="

# ── 축① ──
run_case "TC-1a self-audit(peer_count:0)+PASS → 차단"   "tc1a-selfaudit-pass" 1 '\[FAIL 축①\]'
run_case "TC-1c self-audit(peer_count:0)+FIX → 통과"    "tc1c-selfaudit-fix"  0 '\[OK 축①\]'

# ── 축② ──
run_case "TC-2a silent degrade(ack 부재) → 차단"        "tc2a-silent-degrade" 1 '\[FAIL 축②\]'
run_case "TC-2c honest degrade(reason 부재) → 차단"     "tc2c-honest-no-reason" 1 '\[FAIL 축②\]'

# ── 축③ peer-completion falsifiability ──
run_case "TC-4a peer-backed multi(peer_count:2 + peer_verdicts 실재) → 통과"      "tc4a-peer-backed-multi"     0 '\[OK 축③\]'
run_case "TC-4b-i claimed-multi(peer_count:2, peer_verdicts 부재) → 차단"         "tc1b-dualpeer-pass"         1 '\[FAIL 축③-missing\]'
run_case "TC-4b-ii bare no-degrade(peer_verdicts 부재) → 차단"                    "tc3-no-degrade-block"       1 '\[FAIL 축③-missing\]'
run_case "TC-4c peer target 미실재(self-asserted verify_status 불신) → 차단"      "tc4c-peer-missing"          1 '\[FAIL 축③-unresolved\]'
run_case "TC-4d peer target 빈 파일(0 bytes) → 차단"                             "tc4d-peer-empty"            1 '\[FAIL 축③-empty\]'
run_case "TC-4e honest single-peer degrade stand-down → 통과(AC-A3 무회귀)"       "tc2b-honest-degrade"        0 '\[OK 축③\]'
run_case "TC-4f bare PASS + peer_verdicts 실재 → 통과"                           "tc4f-peer-backed-nodegrade" 0 '\[OK 축③\]'
run_case "TC-4g peer target 실재하나 worker_recommendation 부재 → 차단"           "tc4g-peer-nocontent"        1 '\[FAIL 축③-content\]'

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

# ── MUT-3 (hollow-gate 차단): 축③-unresolved 독립 stat 존재검사 무력화 ──
# 축③-unresolved 앵커 `[ ! -e "$resolved_target" ]` → `[ -e "$resolved_target" ]` (부정 제거 →
# target 미실재 시 false 로 평가돼 unresolved 차단 실종). 이 mutant 은 TC-4c (미실재 target) 를
# 더 이상 차단하지 못함 (RED→GREEN 누출) → 원본 독립 stat 검사 load-bearing 입증.
MUT3="$WORK/mut3-check-verification-floor.sh"
sed -E 's/\[ ! -e "\$resolved_target" \]/[ -e "$resolved_target" ]/' "$SCRIPT_SRC" > "$MUT3"
chmod +x "$MUT3"
mut3_out="$(bash "$MUT3" --verdict "$WORK/tc4c-peer-missing.yaml" --strict 2>&1)"; mut3_rc=$?
if [ "$mut3_rc" -eq 0 ]; then
    echo "PASS MUT-3 mutant(축③ 존재검사 무력화)이 TC-4c 를 더 이상 차단 못 함 — 원본 stat 검사 load-bearing 입증 (mutation 생존 0)"
    PASS=$((PASS + 1))
else
    echo "FAIL MUT-3 mutant 이 여전히 TC-4c 차단 (rc=$mut3_rc) — 축③-unresolved 검사가 hollow (mutation 생존)"
    printf '%s\n' "$mut3_out" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
fi

# ── MUT-4 (hollow-gate 차단): 축③-empty non-empty 검사 무력화 (앞 -e 가드 불변) ──
# 축③-empty 앵커 `[ ! -s "$resolved_target" ]` → `[ -s "$resolved_target" ]` (부정 제거 → 빈 파일
# 시 false 로 평가돼 empty 차단 실종). ★같은 라인 앞 `[ -e "$resolved_target" ]` 가드는 불변.
# 이 mutant 은 TC-4d (빈 파일) 를 더 이상 차단하지 못함 (RED→GREEN 누출) → 검출.
MUT4="$WORK/mut4-check-verification-floor.sh"
sed -E 's/\[ ! -s "\$resolved_target" \]/[ -s "$resolved_target" ]/' "$SCRIPT_SRC" > "$MUT4"
chmod +x "$MUT4"
mut4_out="$(bash "$MUT4" --verdict "$WORK/tc4d-peer-empty.yaml" --strict 2>&1)"; mut4_rc=$?
if [ "$mut4_rc" -eq 0 ]; then
    echo "PASS MUT-4 mutant(축③ non-empty 검사 무력화)이 TC-4d 를 더 이상 차단 못 함 — 원본 -s 검사 load-bearing 입증 (mutation 생존 0)"
    PASS=$((PASS + 1))
else
    echo "FAIL MUT-4 mutant 이 여전히 TC-4d 차단 (rc=$mut4_rc) — 축③-empty 검사가 hollow (mutation 생존)"
    printf '%s\n' "$mut4_out" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
fi

# ── MUT-5 (guard load-bearing 입증): honest-degrade stand-down 단일 조건 무력화 (역방향 assert) ──
# 축③ stand-down 앵커 `if [ "$peer_count" = "1" ] && ack_is_true "$body" && [ -n ... ]; then` → `if false; then`.
# 이 mutant 은 honest single-peer degrade (TC-4e) 를 stand-down 하지 못하고 else 로 빠져 peer_verdicts[]
# 부재 → 축③-missing 으로 오차단(exit≠0). 원본 stand-down 가드가 load-bearing (AC-A3 무회귀 보증) 임을 입증.
# ★MUT-1/2 와 반대 방향: mutant 이 이제 TC-4e 를 차단(exit≠0)하면 kill 성공.
MUT5="$WORK/mut5-check-verification-floor.sh"
sed -E 's/if \[ "\$peer_count" = "1" \].*; then/if false; then/' "$SCRIPT_SRC" > "$MUT5"
chmod +x "$MUT5"
mut5_out="$(bash "$MUT5" --verdict "$WORK/tc2b-honest-degrade.yaml" --strict 2>&1)"; mut5_rc=$?
if [ "$mut5_rc" -ne 0 ]; then
    echo "PASS MUT-5 mutant(stand-down 무력화)이 honest-degrade TC-4e 를 축③-missing 으로 오차단 (rc=$mut5_rc) — 원본 stand-down 가드 load-bearing 입증 (mutation 생존 0)"
    PASS=$((PASS + 1))
else
    echo "FAIL MUT-5 mutant 이 여전히 TC-4e 통과 (rc=$mut5_rc) — stand-down 가드가 hollow (mutation 생존)"
    printf '%s\n' "$mut5_out" | sed 's/^/    | /'
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Summary: PASS=$PASS FAIL=$FAIL ==="
[ "$FAIL" -eq 0 ]
