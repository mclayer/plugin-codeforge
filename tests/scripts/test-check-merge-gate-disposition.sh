#!/usr/bin/env bash
# tests/scripts/test-check-merge-gate-disposition.sh
# CFP-2458 Phase 2 — Discriminating self-test for
#   scripts/lib/check_merge_gate_disposition.py (merge-gate 적대적 반증 disposition SSOT).
#
# 배경: merge-time 적대적 반증 게이트는 거버넌스/오케스트레이션 변경(src/** 무변경)이라
#   전통 unit test 대상이 없다. 테스트 대상 = disposition 결정 *로직* — 게이트가
#   "차단 자체"가 아니라 "verified 결함만 차단"하고, false-positive(오탐)에는 차단하지
#   않는다는 disposition 결정을 discriminating fixture 로 검증한다.
#
# self-contained bash (bats 미사용 — test_check-parallel-work-sentinel.sh 답습).
#   각 TC = JSON fixture 를 stdin/파일로 SSOT 에 주입 → stdout JSON 의 "disposition"
#   문자열을 직접 assert (exit code 모호성 회피, Story §8 권고).
#
# Discriminating 의무 (Story §8.2): 단순 "exit 0 = PASS" 검사는 non-discriminating →
#   금지. disposition 문자열 *내용*을 assert. 핵심 discriminating 쌍:
#     - TC-1/TC-2 (verified P0/P1 → BLOCKED) ↔ TC-4/TC-5 (오탐/evidence부재 → PASS)
#       게이트가 verified 결함만 차단함을 구별(차단 자체가 아님).
#     - TC-6c (한도초과 + user_notified=false → BLOCKED) = silent auto-pass 0 증명.
#
# Mutation-kill 입증 (Story §8.2 SSOT, 본 파일 하단 문서 + 동봉 절차로 실측):
#   M1 always-block (decide_disposition 항상 BLOCKED) → TC-3/TC-4/TC-5/TC-7 FAIL = RED
#   M2 always-pass  (decide_disposition 항상 PASS)    → TC-1/TC-2/TC-6c/TC-8 FAIL = RED
#   M3 silent-auto-pass (INV-G3 user_notified 검사 제거 → 한도초과 시 무조건 DEGRADED_PASS)
#                                                       → TC-6c FAIL = RED
#
# Exit code:
#   0 = all fixtures pass (discriminating test validates disposition logic)
#   1 = any fixture fails (disposition logic regressed / mutated)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-merge-gate-disposition.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# extract_disposition: SSOT 의 stdout JSON 에서 "disposition" 값을 추출.
#   regex-free, jq 미의존 — python3 으로 파싱(cross-platform, 본 repo python3 floor 가정).
# ─────────────────────────────────────────────────────────────────────────────
extract_disposition() {
  python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["disposition"])'
}

# ─────────────────────────────────────────────────────────────────────────────
# has_provenance: stdout JSON 에 provenance artifact 가 동반되는지 (INV-G4) 검사.
#   provenance.script == "check_merge_gate_disposition" 이면 1, 아니면 0 출력.
# ─────────────────────────────────────────────────────────────────────────────
has_provenance() {
  python3 -c 'import sys,json
d=json.loads(sys.stdin.read())
p=d.get("provenance") or {}
print("1" if p.get("script")=="check_merge_gate_disposition" else "0")'
}

# ─────────────────────────────────────────────────────────────────────────────
# run_case: fixture JSON 을 stdin 으로 SSOT 에 주입 → disposition 직접 assert.
#   $1=name  $2=fixture_json  $3=expected_disposition  $4=description
#   INV-G4: 모든 케이스에서 provenance 동반도 함께 assert (artifact 없이 통과 0).
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" fixture="$2" expected="$3" description="$4"
  local out exit_code=0 actual prov

  out=$(printf '%s' "$fixture" | bash "$WRAPPER" 2>/dev/null) || exit_code=$?

  local ok=1
  actual=$(printf '%s' "$out" | extract_disposition 2>/dev/null) || actual="<PARSE-ERROR>"
  prov=$(printf '%s' "$out" | has_provenance 2>/dev/null) || prov="0"

  [ "$actual" = "$expected" ] || ok=0
  # INV-G4: provenance artifact 동반 필수 (artifact 없는 disposition 반환 경로 0)
  [ "$prov" = "1" ] || ok=0

  # exit code 계열 cross-check (통과 계열 0 / 보류 계열 1)
  case "$expected" in
    PASS|DEGRADED_PASS) [ "$exit_code" -eq 0 ] || ok=0 ;;
    BLOCKED|FAIL_CLOSED) [ "$exit_code" -eq 1 ] || ok=0 ;;
  esac

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name → $actual (exit $exit_code, provenance=$prov) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected disposition: '$expected', got: '$actual'"
    echo "  provenance present:   '$prov' (expected '1')"
    echo "  exit_code:            $exit_code"
    echo "  Description:          $description"
    echo "  Raw output:           $out"
    FAIL=$((FAIL+1))
  fi
}

set +e

echo "============================================================"
echo "CFP-2458 merge-gate disposition — 10 TC discriminating fixtures"
echo "============================================================"

# ═════════════════════════════════════════════════════════════════════════════
# TC-1: verified P0 finding (evidence 일치) → BLOCKED (INV-G1)
#   ★ discriminating: M2 always-pass kill (PASS 로 변이 시 FAIL).
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-1-verified-P0" \
  '{"findings":[{"severity":"P0","evidence_present":true,"verify_result":"verified"}],"codex_available":true}' \
  "BLOCKED" \
  "verified P0(evidence 일치) → BLOCKED (INV-G1 verified 차단)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-2: verified P1 (AC 미충족, evidence 일치) → BLOCKED (INV-G1)
#   ★ discriminating: M2 always-pass kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-2-verified-P1" \
  '{"findings":[{"severity":"P1","evidence_present":true,"verify_result":"verified"}],"codex_available":true}' \
  "BLOCKED" \
  "verified P1(AC 미충족) → BLOCKED (INV-G1)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-3: verified P2 (cosmetic) only → PASS (비차단, 기록 후 진행)
#   ★ discriminating: M1 always-block kill (BLOCKED 로 변이 시 FAIL).
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-3-verified-P2-only" \
  '{"findings":[{"severity":"P2","evidence_present":true,"verify_result":"verified"}],"codex_available":true}' \
  "PASS" \
  "verified P2-only → PASS (P2 비차단 보조 규칙)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-4: false-positive (P0 발화, verify_result=mismatch) → PASS (차단 안 함)
#   ★ 핵심 discriminating 쌍 (TC-1 ↔ TC-4): "차단 자체"가 아니라 "verified 만 차단".
#   ★ M1 always-block kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-4-false-positive-mismatch" \
  '{"findings":[{"severity":"P0","evidence_present":true,"verify_result":"mismatch"}],"codex_available":true}' \
  "PASS" \
  "P0 발화했으나 verify_result=mismatch(오탐) → PASS (INV-G2 부당 차단 0)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-5: evidence 부재 finding (evidence_present=false) → PASS (무효 폐기)
#   ★ 핵심 discriminating 쌍 (TC-2 ↔ TC-5). M1 always-block kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-5-evidence-absent" \
  '{"findings":[{"severity":"P0","evidence_present":false,"verify_result":"absent"}],"codex_available":true}' \
  "PASS" \
  "evidence_present=false (보류 trigger 아님) → PASS (INV-G2 무효 폐기)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-6a: Codex 미가용, 한도 미초과 (retries<max AND elapsed<timeout) → BLOCKED (재시도 중)
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-6a-failmode-under-limit" \
  '{"findings":[],"codex_available":false,"degrade_state":{"retries":1,"max_retries":3,"elapsed":10,"timeout":60,"user_notified":false}}' \
  "BLOCKED" \
  "codex 미가용 + 한도 미초과(retries 1<3, elapsed 10<60) → BLOCKED (INV-G3 재시도 중)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-6b: Codex 미가용, 한도 초과 + user_notified=true → DEGRADED_PASS
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-6b-failmode-over-notified" \
  '{"findings":[],"codex_available":false,"degrade_state":{"retries":3,"max_retries":3,"elapsed":70,"timeout":60,"user_notified":true}}' \
  "DEGRADED_PASS" \
  "codex 미가용 + 한도초과 + user_notified=true → DEGRADED_PASS (INV-G3 하이브리드)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-6c: Codex 미가용, 한도 초과 + user_notified=false → BLOCKED (silent auto-pass 0)
#   ★ discriminating: M2 always-pass kill + M3 silent-auto-pass kill (둘 다 이 TC FAIL).
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-6c-failmode-over-not-notified" \
  '{"findings":[],"codex_available":false,"degrade_state":{"retries":3,"max_retries":3,"elapsed":70,"timeout":60,"user_notified":false}}' \
  "BLOCKED" \
  "codex 미가용 + 한도초과 이나 user_notified=false → BLOCKED (INV-G3 silent auto-pass 0)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-7: 정상 PASS (findings=[]) → PASS
#   ★ discriminating: M1 always-block kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-7-clean-pass" \
  '{"findings":[],"codex_available":true}' \
  "PASS" \
  "findings=[] AND codex_available=true → PASS (정상 통과)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-8: verified P0 + verified P2 혼재 → BLOCKED (P0 우선)
#   ★ discriminating: M2 always-pass kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-8-mixed-P0-P2" \
  '{"findings":[{"severity":"P2","evidence_present":true,"verify_result":"verified"},{"severity":"P0","evidence_present":true,"verify_result":"verified"}],"codex_available":true}' \
  "BLOCKED" \
  "verified P0 + verified P2 혼재 → BLOCKED (INV-G1 P0 우선)"

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2458 merge-gate disposition)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All 10 TC fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (Story §8.2 — mutation 생존 차단):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "M1 always-block (decide_disposition → 항상 (BLOCKED, prov))"
  echo "   → TC-3 / TC-4 / TC-5 / TC-7 FAIL = RED (PASS 기대인데 BLOCKED 나옴)"
  echo "M2 always-pass  (decide_disposition → 항상 (PASS, prov))"
  echo "   → TC-1 / TC-2 / TC-6c / TC-8 FAIL = RED (BLOCKED 기대인데 PASS 나옴)"
  echo "M3 silent-auto-pass (INV-G3 user_notified 검사 제거 → 한도초과 시 무조건 DEGRADED_PASS)"
  echo "   → TC-6c FAIL = RED (BLOCKED 기대인데 DEGRADED_PASS 나옴 = silent auto-pass 누출)"
  echo ""
  echo "핵심 discriminating 쌍: TC-1/TC-2(verified→BLOCKED) ↔ TC-4/TC-5(오탐·부재→PASS)"
  echo "  — 게이트가 '차단 자체'가 아니라 'verified 결함만 차단'함을 구별."
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed (disposition logic regressed / mutated)"
  exit 1
fi
