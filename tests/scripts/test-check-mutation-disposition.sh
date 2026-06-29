#!/usr/bin/env bash
# tests/scripts/test-check-mutation-disposition.sh
# CFP-2464 Phase 2 — Discriminating self-test for
#   scripts/lib/check_mutation_disposition.py
#   (mutation peer touchpoint #8 surviving-mutant disposition SSOT).
#
# 배경: mutation peer 게이트는 거버넌스/오케스트레이션 변경(src/** 무변경)이라 전통
#   unit test 대상이 없다. 테스트 대상 = surviving-mutant disposition 결정 *로직* —
#   게이트가 "surviving 자체"를 hollow-gate 로 단정하지 않고, equivalent/flaky 의심은
#   '불확정(undetermined)'으로 보류하며, killed mutant 는 reject 한다는 3-상태 결정을
#   discriminating fixture 로 검증한다.
#
# self-contained bash (bats 미사용 — test-check-merge-gate-disposition.sh 답습).
#   각 TC = JSON fixture 를 stdin 으로 SSOT 에 주입 → stdout JSON 의 mutant 별
#   "disposition" 문자열을 직접 assert (exit code 모호성 회피, Story §8 권고).
#
# Discriminating 의무 (Story §8.2): 단순 "exit 0 = OK" 검사는 non-discriminating →
#   금지. disposition 문자열 *내용*을 assert. 핵심 discriminating 삼각:
#     - TC-1 (surviving 5-AND → hollow_gate_verified) = 차단 trigger
#       ↕ TC-2/TC-3 (equivalent 동작차이 0 / flaky 비결정 → undetermined) = 보류 (차단 아님)
#       ↕ TC-4 (killed → rejected_false_positive) = 주장 자체 무효
#     세 상태가 서로 구별됨을 강제 — "surviving 만 보면 hollow" 로 변이 시 TC-2/TC-3 FAIL.
#
# Mutation-kill 입증 (Story §8.2 SSOT, 본 파일 하단 문서 + 동봉 절차로 실측):
#   M1 always-verified  (decide_one → 항상 hollow_gate_verified) → TC-2/TC-3/TC-4 FAIL = RED
#   M2 always-undetermined (decide_one → 항상 undetermined)      → TC-1/TC-4 FAIL = RED
#   M3 drop-equivalent/flaky-filter (INV-M2 의 observable_diff/deterministic 검사 제거 →
#      surviving 이면 무조건 hollow_gate_verified) → TC-2/TC-3 FAIL = RED (없는 검사연극 날조)
#   M4 drop-killed-reject (INV-M3 의 survived=false → reject 제거) → TC-4 FAIL = RED
#
# Exit code:
#   0 = all fixtures pass (discriminating test validates disposition logic)
#   1 = any fixture fails (disposition logic regressed / mutated)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-mutation-disposition.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# extract_disposition: SSOT 의 stdout JSON 에서 N번째(0-base) mutant 의 "disposition" 추출.
#   regex-free, jq 미의존 — python3 으로 파싱(cross-platform, 본 repo python3 floor 가정).
# ─────────────────────────────────────────────────────────────────────────────
extract_disposition() {
  local idx="$1"
  python3 -c "import sys,json; print(json.loads(sys.stdin.read())['dispositions'][$idx]['disposition'])"
}

# extract_severity: N번째 mutant 의 "severity" 추출 (None 은 'null' 출력).
extract_severity() {
  local idx="$1"
  python3 -c "import sys,json; print(json.dumps(json.loads(sys.stdin.read())['dispositions'][$idx]['severity']))"
}

# has_provenance: stdout JSON 에 provenance artifact 가 동반되는지 (INV-M5) 검사.
has_provenance() {
  python3 -c 'import sys,json
d=json.loads(sys.stdin.read())
p=d.get("provenance") or {}
print("1" if p.get("script")=="check_mutation_disposition" else "0")'
}

# ─────────────────────────────────────────────────────────────────────────────
# run_case: fixture JSON 을 stdin 으로 SSOT 에 주입 → 단일 mutant disposition+severity assert.
#   $1=name  $2=fixture_json  $3=expected_disposition  $4=expected_severity(json: "P0"|null)
#   $5=expected_exit  $6=description
#   INV-M5: 모든 케이스에서 provenance 동반도 함께 assert (artifact 없이 통과 0).
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" fixture="$2" expected="$3" exp_sev="$4" exp_exit="$5" description="$6"
  local out exit_code=0 actual sev prov

  out=$(printf '%s' "$fixture" | bash "$WRAPPER" 2>/dev/null) || exit_code=$?

  local ok=1
  actual=$(printf '%s' "$out" | extract_disposition 0 2>/dev/null) || actual="<PARSE-ERROR>"
  sev=$(printf '%s' "$out" | extract_severity 0 2>/dev/null) || sev="<PARSE-ERROR>"
  prov=$(printf '%s' "$out" | has_provenance 2>/dev/null) || prov="0"

  [ "$actual" = "$expected" ] || ok=0
  [ "$sev" = "$exp_sev" ] || ok=0
  [ "$prov" = "1" ] || ok=0
  [ "$exit_code" -eq "$exp_exit" ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name → $actual (sev=$sev, exit $exit_code, provenance=$prov) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected disposition: '$expected' (sev=$exp_sev, exit=$exp_exit), got: '$actual' (sev=$sev, exit=$exit_code)"
    echo "  provenance present:   '$prov' (expected '1')"
    echo "  Description:          $description"
    echo "  Raw output:           $out"
    FAIL=$((FAIL+1))
  fi
}

# run_failopen_case: codex_available=false → lane-time fail-open (빈 disposition + marker).
#   $1=name  $2=fixture_json  $3=description
run_failopen_case() {
  local name="$1" fixture="$2" description="$3"
  local out exit_code=0 ndisp foparker prov

  out=$(printf '%s' "$fixture" | bash "$WRAPPER" 2>/dev/null) || exit_code=$?

  local ok=1
  # 빈 disposition list + fail_open=true provenance + exit 0 (lane 진행)
  ndisp=$(printf '%s' "$out" | python3 -c 'import sys,json; print(len(json.loads(sys.stdin.read())["dispositions"]))' 2>/dev/null) || ndisp="-1"
  foparker=$(printf '%s' "$out" | python3 -c 'import sys,json; print("1" if json.loads(sys.stdin.read())["provenance"].get("fail_open") is True else "0")' 2>/dev/null) || foparker="0"
  prov=$(printf '%s' "$out" | has_provenance 2>/dev/null) || prov="0"

  [ "$ndisp" = "0" ] || ok=0
  [ "$foparker" = "1" ] || ok=0
  [ "$prov" = "1" ] || ok=0
  [ "$exit_code" -eq 0 ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name → fail-open (dispositions=0, fail_open=1, exit 0) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected: dispositions=0, fail_open=1, exit=0; got dispositions=$ndisp fail_open=$foparker exit=$exit_code prov=$prov"
    echo "  Description:          $description"
    echo "  Raw output:           $out"
    FAIL=$((FAIL+1))
  fi
}

set +e

echo "============================================================"
echo "CFP-2464 mutation disposition — discriminating fixtures"
echo "============================================================"

# ═════════════════════════════════════════════════════════════════════════════
# TC-1: surviving 5-AND (evidence 일치 + survived + 동작차이 + 결정론 + 재현통과) → hollow_gate_verified
#   ★ 핵심 discriminating: M2 always-undetermined kill / M3 무관(여기선 verified 정답).
#   severity P0 부여 (INV-M4) — 재현된 hollow-gate 한정.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-1-surviving-verified-P0" \
  '{"mutants":[{"id":"m1","location":"src/a.py:42","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":true,"severity":"P0"}],"codex_available":true}' \
  "hollow_gate_verified" '"P0"' 1 \
  "surviving 5-AND + 재현통과 → hollow_gate_verified (INV-M1, severity P0)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-2: equivalent 의심 (surviving 이나 관측 동작차이 0) → undetermined (severity 미부여)
#   ★ 핵심 discriminating 쌍 (TC-1 ↔ TC-2): "surviving 자체"가 아니라 동작차이 있어야 verified.
#   ★ M1 always-verified kill + M3 drop-filter kill (둘 다 이 TC FAIL).
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-2-equivalent-undetermined" \
  '{"mutants":[{"id":"m2","location":"src/a.py:50","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":false,"deterministic":true,"reproduced_pass":true,"severity":"P0"}],"codex_available":true}' \
  "undetermined" 'null' 0 \
  "surviving 이나 동작차이 0 (equivalent 의심, undecidable) → undetermined (INV-M2, severity 미부여)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-3: flaky 의심 (surviving + 동작차이 있으나 다회 실행 비결정) → undetermined
#   ★ 핵심 discriminating: M1 always-verified kill + M3 drop-filter kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-3-flaky-undetermined" \
  '{"mutants":[{"id":"m3","location":"src/a.py:60","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":true,"deterministic":false,"reproduced_pass":true,"severity":"P1"}],"codex_available":true}' \
  "undetermined" 'null' 0 \
  "surviving + 비결정 (flaky 의심) → undetermined (INV-M2, severity 미부여)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-4: killed (mutant 적용 후 suite RED = 테스트가 실제로 잡음) → rejected_false_positive
#   ★ 핵심 discriminating: M2 always-undetermined kill + M4 drop-killed-reject kill.
#   surviving-mutant/hollow-gate 주장 자체가 틀림 (테스트가 동작함).
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-4-killed-rejected" \
  '{"mutants":[{"id":"m4","location":"src/a.py:70","evidence_matches_ground_truth":true,"survived":false,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":false,"severity":"P0"}],"codex_available":true}' \
  "rejected_false_positive" 'null' 0 \
  "killed (suite RED = 테스트가 잡음) → rejected_false_positive (INV-M3, severity 미부여)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-5: evidence mismatch (Codex 발화 위치/baseline 이 실제 코드와 불일치) → rejected_false_positive
#   ★ discriminating: D3 reject 흐름 (verify-before-trust mismatch). M2/M4 kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-5-evidence-mismatch-rejected" \
  '{"mutants":[{"id":"m5","location":"src/a.py:80","evidence_matches_ground_truth":false,"survived":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":true,"severity":"P0"}],"codex_available":true}' \
  "rejected_false_positive" 'null' 0 \
  "evidence mismatch (ground truth 불일치, D3 reject) → rejected_false_positive (INV-M3)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-6: surviving + 동작차이 + 결정론 이나 PL 재현 미통과 → undetermined (자동 reject 아님)
#   ★ discriminating: 재현 미통과 시 hollow-gate 단정 금지(보류). M1 always-verified kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-6-reproduce-fail-undetermined" \
  '{"mutants":[{"id":"m6","location":"src/a.py:90","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":false,"severity":"P0"}],"codex_available":true}' \
  "undetermined" 'null' 0 \
  "surviving 이나 PL 재현 미통과 → undetermined 보류 (INV-M1 미충족, 자동 reject 아님)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-7: surviving 5-AND + severity P2 → hollow_gate_verified 이나 P2 비차단 (INV-M4)
#   ★ discriminating: P2 = hollow_gate_verified 이되 비차단 (기록 후 진행, cry-wolf 차단).
#   exit 1 (verified count > 0) 이나 severity P2 = lane 차원 비차단 (provenance 로 식별).
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-7-verified-P2-nonblocking" \
  '{"mutants":[{"id":"m7","location":"src/a.py:100","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":true,"severity":"P2"}],"codex_available":true}' \
  "hollow_gate_verified" '"P2"' 1 \
  "surviving 5-AND + P2 → hollow_gate_verified (P2 비차단 — ADR-081 D11.b, 기록 후 진행)"

set -e

# ─────────────────────────────────────────────────────────────────────────────
# 다중 mutant 혼재 케이스 (verified + undetermined + rejected 동시) — provenance count 검증
# ─────────────────────────────────────────────────────────────────────────────
set +e
echo ""
echo "── TC-8: 다중 mutant 혼재 (verified + undetermined + rejected) ──"
MIXED='{"mutants":[
  {"id":"v","location":"x:1","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":true,"severity":"P1"},
  {"id":"u","location":"x:2","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":false,"deterministic":true,"reproduced_pass":true,"severity":"P0"},
  {"id":"r","location":"x:3","evidence_matches_ground_truth":true,"survived":false,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":false,"severity":"P0"}
],"codex_available":true}'
MIX_OUT=$(printf '%s' "$MIXED" | bash "$WRAPPER" 2>/dev/null); MIX_EXIT=$?
MIX_OK=1
V=$(printf '%s' "$MIX_OUT" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["provenance"]["verified_count"])' 2>/dev/null) || V="-1"
U=$(printf '%s' "$MIX_OUT" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["provenance"]["undetermined_count"])' 2>/dev/null) || U="-1"
R=$(printf '%s' "$MIX_OUT" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["provenance"]["rejected_count"])' 2>/dev/null) || R="-1"
[ "$V" = "1" ] || MIX_OK=0
[ "$U" = "1" ] || MIX_OK=0
[ "$R" = "1" ] || MIX_OK=0
[ "$MIX_EXIT" -eq 1 ] || MIX_OK=0   # verified_count>0 → exit 1
if [ "$MIX_OK" -eq 1 ]; then
  echo "✓ PASS: TC-8-mixed → verified=$V undetermined=$U rejected=$R (exit $MIX_EXIT) — 혼재 독립 판정 + count 정합"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: TC-8-mixed → verified=$V undetermined=$U rejected=$R exit=$MIX_EXIT (expected 1/1/1, exit 1)"
  echo "  Raw output: $MIX_OUT"
  FAIL=$((FAIL+1))
fi

# ── TC-9: lane-time fail-open (codex_available=false) → 빈 disposition + marker, lane 진행 ──
echo ""
echo "── TC-9: lane-time fail-open (codex 미가용) ──"
run_failopen_case "TC-9-failopen" \
  '{"mutants":[{"id":"x","location":"x:1","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":true,"severity":"P0"}],"codex_available":false}' \
  "codex 미가용 → fail_open_then_record_with_marker (mutation 미수행 marker 기록 후 lane 진행, ADR-070 Amd 10 D8(c) Q-B)"

# ── TC-10: SETUP error (hollow_gate_verified 인데 severity 누락) → exit 2 ──
echo ""
echo "── TC-10: SETUP error (verified severity 누락) ──"
BAD='{"mutants":[{"id":"b","location":"x:1","evidence_matches_ground_truth":true,"survived":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":true,"severity":null}],"codex_available":true}'
printf '%s' "$BAD" | bash "$WRAPPER" >/dev/null 2>&1; BAD_EXIT=$?
if [ "$BAD_EXIT" -eq 2 ]; then
  echo "✓ PASS: TC-10-setup-error → exit 2 (verified mutant severity 누락 = malformed)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: TC-10-setup-error → exit $BAD_EXIT (expected 2)"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# TC-11/TC-12: null-policy 대칭 회귀 (CFP-2464 FIX P1 — _decide_one null 가드 5-AND 정렬)
#   배경: 이전 구현은 evidence_ok/survived 를 `is False` 로만 가드 → 누락(None)이면
#     reject 를 건너뛰고 이후 positive 단언 없이 false hollow_gate_verified 산출
#     (5-AND 위반, 부당 차단/cry-wolf). 나머지 3 필드는 `is not True` 라 안전.
#   FIX: 5 필드 전부 is-not-True 로 정렬 → 누락/None 은 undetermined 안전 강등.
#   ★ discriminating: 누락 필드(None)가 더 이상 hollow_gate_verified 안 냄을 변별.
#     (회귀 시 = 이전 비대칭 복구 = hollow_gate_verified/exit 1 → FAIL)
# ═════════════════════════════════════════════════════════════════════════════
set +e
echo ""
echo "── TC-11/TC-12: null-policy 대칭 회귀 (FIX P1 — 누락 필드 5-AND 미충족) ──"

# TC-11: survived 누락 + 나머지 4 true + P0 → undetermined (이전엔 false hollow_gate_verified)
run_case "TC-11-survived-missing-undetermined" \
  '{"mutants":[{"id":"m11","location":"src/a.py:110","evidence_matches_ground_truth":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":true,"severity":"P0"}],"codex_available":true}' \
  "undetermined" 'null' 0 \
  "survived 누락 (None) → 5-AND 미충족 → undetermined (FIX P1 — false hollow_gate_verified 차단)"

# TC-12: evidence_matches_ground_truth 누락 + 나머지 4 true + P0 → undetermined
run_case "TC-12-evidence-missing-undetermined" \
  '{"mutants":[{"id":"m12","location":"src/a.py:120","survived":true,"observable_behavior_diff":true,"deterministic":true,"reproduced_pass":true,"severity":"P0"}],"codex_available":true}' \
  "undetermined" 'null' 0 \
  "evidence_matches_ground_truth 누락 (None) → 5-AND 미충족 → undetermined (FIX P1 — false hollow_gate_verified 차단)"

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2464 mutation disposition)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (Story §8.2 — mutation 생존 차단):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "M1 always-verified (_decide_one → 항상 hollow_gate_verified)"
  echo "   → TC-2 / TC-3 / TC-4 / TC-5 / TC-6 FAIL = RED (undetermined/reject 기대인데 verified)"
  echo "M2 always-undetermined (_decide_one → 항상 undetermined)"
  echo "   → TC-1 / TC-4 / TC-5 / TC-7 / TC-8 FAIL = RED (verified/reject 기대인데 undetermined)"
  echo "M3 drop-equivalent/flaky-filter (INV-M2 observable_diff/deterministic 검사 제거)"
  echo "   → TC-2 / TC-3 FAIL = RED (surviving 이면 무조건 verified = 없는 검사연극 날조)"
  echo "M4 drop-killed-reject (INV-M3 survived=false → reject 제거)"
  echo "   → TC-4 FAIL = RED (killed 인데 reject 안 됨)"
  echo "M5 null-asymmetric (evidence_ok/survived 를 is-not-True 대신 is-False 로만 가드 —"
  echo "   FIX P1 이전 회귀: 누락(None) → reject 건너뛰고 false hollow_gate_verified)"
  echo "   → TC-11 / TC-12 FAIL = RED (누락 필드인데 hollow_gate_verified, exit 1)"
  echo ""
  echo "핵심 discriminating 삼각: TC-1(surviving→verified) ↔ TC-2/TC-3(equivalent/flaky→undetermined)"
  echo "  ↔ TC-4/TC-5(killed/mismatch→rejected) — 세 상태가 서로 구별됨을 강제."
  echo "  surviving≠hollow-gate 양면(concept M-1/M-3) 보존 = cry-wolf 차단."
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed (disposition logic regressed / mutated)"
  exit 1
fi
