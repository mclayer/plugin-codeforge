#!/usr/bin/env bash
# tests/scripts/test-check-fix-replay-disposition.sh
# CFP-2480 (Epic CFP-2476 E3) — Discriminating self-test for
#   scripts/lib/fix_replay_disposition.py (FIX ground-truth replay close-gate disposition SSOT).
#
# 배경: FIX ground-truth replay close gate 는 거버넌스/오케스트레이션 변경(src/** 무변경)이라
#   전통 unit test 대상이 없다. 테스트 대상 = close disposition 결정 *로직* — 게이트가
#   "close 자체"가 아니라 "원 reproducer 가 결정론적 GREEN 재현 + PL falsify 통과 시만 close
#   허용(PASS)"하고, RED 면 close 거부(falsified), 환원불가 finding 은 사유 동반 replay-impossible,
#   flaky/1회-green 은 보류(undetermined) 한다는 disposition 을 discriminating fixture 로 검증한다.
#
# self-contained bash (bats 미사용 — test-check-merge-gate-disposition.sh 답습).
#   각 TC = JSON fixture 를 stdin/파일로 SSOT 에 주입 → stdout JSON 의 dispositions[0].disposition
#   문자열을 직접 assert (exit code 모호성 회피, Story §8 권고). RED→GREEN stash proof.
#
# Discriminating 의무 (Story §8.2): 단순 "exit 0 = PASS" 검사는 non-discriminating → 금지.
#   disposition 문자열 *내용*을 assert. 핵심 discriminating 쌍:
#     - TC-1 (all-green + PL falsify → PASS) ↔ TC-2 (all-red → falsified)
#       게이트가 "close 자체"가 아니라 "Retest GREEN 만 close 허용"함을 구별.
#     - TC-3 (flaky 1회 green, 횟수 미충족 → undetermined) = false-GREEN 1회 close 차단 증명 (§1 목적 정면 훼손 차단).
#     - TC-5 (reproducible=false + reason → replay-impossible) ↔ TC-6 (reason 부재 → SETUP exit 2)
#       silent 면제 차단(INV-FR2) 구별.
#
# Mutation-kill 입증 (Story §8.2 SSOT, 본 파일 하단 문서 + 동봉 절차로 실측):
#   M1 always-close (decide_replay_disposition 항상 PASS) → TC-2/TC-3/TC-4/TC-5/TC-7/TC-8 FAIL = RED
#   M2 always-block (decide_replay_disposition 항상 falsified) → TC-1/TC-5/TC-9 FAIL = RED
#   M3 flaky-1회-close (FLAKY-1 횟수 검사 제거 → 1회 green 으로 PASS) → TC-3 FAIL = RED
#                                                       (= false-GREEN 누출, §1 목적 정면 훼손)
#   M4 silent-replay-impossible (INV-FR2 reason 검사 제거 → reason 없이 replay-impossible) → TC-6 FAIL = RED
#                                                       (= silent 면제 누출)
#
# Exit code:
#   0 = all fixtures pass (discriminating test validates disposition logic)
#   1 = any fixture fails (disposition logic regressed / mutated)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-fix-replay-disposition.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# extract_disposition: SSOT 의 stdout JSON 에서 dispositions[0].disposition 추출.
#   regex-free, jq 미의존 — python3 으로 파싱 (cross-platform, 본 repo python3 floor 가정).
# ─────────────────────────────────────────────────────────────────────────────
extract_disposition() {
  python3 -c 'import sys,json
d=json.loads(sys.stdin.read())
ds=d.get("dispositions") or []
print(ds[0]["disposition"] if ds else "<EMPTY>")'
}

# ─────────────────────────────────────────────────────────────────────────────
# has_provenance: stdout JSON 에 provenance artifact 동반 여부 (INV-FR4) 검사.
#   provenance.script == "fix_replay_disposition" 이면 1, 아니면 0 출력.
# ─────────────────────────────────────────────────────────────────────────────
has_provenance() {
  python3 -c 'import sys,json
d=json.loads(sys.stdin.read())
p=d.get("provenance") or {}
print("1" if p.get("script")=="fix_replay_disposition" else "0")'
}

# ─────────────────────────────────────────────────────────────────────────────
# run_case: fixture JSON 을 stdin 으로 SSOT 에 주입 → disposition 직접 assert.
#   $1=name  $2=fixture_json  $3=expected_disposition  $4=description
#   INV-FR4: PASS/falsified/impossible/undetermined 케이스는 provenance 동반도 함께 assert.
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" fixture="$2" expected="$3" description="$4"
  local out exit_code=0 actual prov

  out=$(printf '%s' "$fixture" | bash "$WRAPPER" 2>/dev/null) || exit_code=$?

  local ok=1
  actual=$(printf '%s' "$out" | extract_disposition 2>/dev/null) || actual="<PARSE-ERROR>"
  prov=$(printf '%s' "$out" | has_provenance 2>/dev/null) || prov="0"

  [ "$actual" = "$expected" ] || ok=0
  [ "$prov" = "1" ] || ok=0  # INV-FR4: provenance artifact 동반 필수

  # exit code 계열 cross-check (falsified 만 보류 신호 1, 그 외 0)
  case "$expected" in
    falsified) [ "$exit_code" -eq 1 ] || ok=0 ;;
    PASS|replay-impossible|undetermined) [ "$exit_code" -eq 0 ] || ok=0 ;;
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

# ─────────────────────────────────────────────────────────────────────────────
# run_setup_error_case: SETUP error (exit 2) 전용 — disposition 산출 없이 exit 2 검증.
#   $1=name  $2=fixture_json  $3=description
# ─────────────────────────────────────────────────────────────────────────────
run_setup_error_case() {
  local name="$1" fixture="$2" description="$3"
  local exit_code=0

  printf '%s' "$fixture" | bash "$WRAPPER" >/dev/null 2>&1 || exit_code=$?

  if [ "$exit_code" -eq 2 ]; then
    echo "✓ PASS: $name → exit 2 (SETUP error) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name (expected exit 2, got $exit_code) — $description"
    FAIL=$((FAIL+1))
  fi
}

set +e

echo "============================================================"
echo "CFP-2480 fix-replay disposition — discriminating fixtures"
echo "============================================================"

# 공통 base finding 조각 (reproducible/reproducer/base_sha 정상, replay_runs 만 가변)
# ═════════════════════════════════════════════════════════════════════════════
# TC-1: all-green(3/3) + PL falsify → PASS (INV-FR1 / FLAKY-3 / INV-FR5 — close 허용)
#   ★ discriminating: M2 always-block kill (falsified 로 변이 시 FAIL).
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-1-all-green-pl-falsified" \
  '{"findings":[{"id":"F-1","reproducible":true,"reproducer_present":true,"base_sha_present":true,"replay_runs":["green","green","green"],"deterministic_runs_required":3,"pl_falsified":true}],"codex_available":true}' \
  "PASS" \
  "all-green(3/3) + PL falsify → PASS (Retest GREEN close 허용)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-2: all-red(3/3) → falsified ((A)축 fail-closed — 닫기 거부, PL falsify 무관)
#   ★ 핵심 discriminating 쌍 (TC-1 ↔ TC-2): "close 자체"가 아니라 "GREEN 만 close 허용".
#   ★ M1 always-close kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-2-all-red" \
  '{"findings":[{"id":"F-2","reproducible":true,"reproducer_present":true,"base_sha_present":true,"replay_runs":["red","red","red"],"deterministic_runs_required":3,"pl_falsified":false}],"codex_available":true}' \
  "falsified" \
  "all-red(3/3) → falsified ((A)축 fail-closed, 닫기 거부)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-3: 1회 green 만 (횟수 미충족, required=3) → undetermined (FLAKY-1 false-GREEN 차단)
#   ★ 핵심 discriminating: M3 flaky-1회-close kill (1회 green 으로 PASS 변이 시 FAIL).
#     = §1 목적("주장 아닌 실측") 정면 훼손 차단 mutation.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-3-flaky-one-green" \
  '{"findings":[{"id":"F-3","reproducible":true,"reproducer_present":true,"base_sha_present":true,"replay_runs":["green"],"deterministic_runs_required":3,"pl_falsified":true}],"codex_available":true}' \
  "undetermined" \
  "1회 green(required 3 미충족) → undetermined (FLAKY-1 false-GREEN 1회 close 금지)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-4: mixed (green+red 혼재, 충분 횟수) → undetermined (FLAKY-2 quarantine, max-FIX 보호)
#   ★ M1 always-close kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-4-mixed-flaky" \
  '{"findings":[{"id":"F-4","reproducible":true,"reproducer_present":true,"base_sha_present":true,"replay_runs":["green","red","green"],"deterministic_runs_required":3,"pl_falsified":true}],"codex_available":true}' \
  "undetermined" \
  "mixed(green+red) → undetermined (FLAKY-2 quarantine, false-RED max-FIX 부당소진 차단)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-5: reproducible=false + reason 동반 → replay-impossible (INV-FR2, silent 면제 차단)
#   ★ M1 always-close kill (PASS 로 변이 시 FAIL) / M2 always-block kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-5-replay-impossible-with-reason" \
  '{"findings":[{"id":"F-5","reproducible":false,"replay_impossible_reason":"코드 P1 naming 가독성 — 실행 가능 명령으로 환원 불가"}],"codex_available":true}' \
  "replay-impossible" \
  "reproducible=false + reason → replay-impossible (INV-FR2 사유 동반)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-6: reproducible=false + reason 부재 → SETUP error exit 2 (INV-FR2 silent 면제 차단)
#   ★ 핵심 discriminating: M4 silent-replay-impossible kill (reason 없이 면제 변이 시 exit 0 = FAIL).
# ═════════════════════════════════════════════════════════════════════════════
run_setup_error_case "TC-6-replay-impossible-no-reason" \
  '{"findings":[{"id":"F-6","reproducible":false,"replay_impossible_reason":null}],"codex_available":true}' \
  "reproducible=false + reason 부재 → exit 2 SETUP (INV-FR2 silent 면제 차단)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-7: reproducer_present=false (reproduce-before-fix 위반) → undetermined (INV-FR3 자동 close 금지)
#   ★ M1 always-close kill.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-7-no-reproducer" \
  '{"findings":[{"id":"F-7","reproducible":true,"reproducer_present":false,"base_sha_present":true,"replay_runs":["green","green","green"],"deterministic_runs_required":3,"pl_falsified":true}],"codex_available":true}' \
  "undetermined" \
  "reproducer_present=false → undetermined (INV-FR3 reproduce-before-fix 위반, close 불가)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-8: all-green 이나 PL falsify 부재 → undetermined (INV-FR5 실행자≠판정자)
#   ★ M1 always-close kill — Codex replay 보고만으로 close 금지.
# ═════════════════════════════════════════════════════════════════════════════
run_case "TC-8-no-pl-falsify" \
  '{"findings":[{"id":"F-8","reproducible":true,"reproducer_present":true,"base_sha_present":true,"replay_runs":["green","green","green"],"deterministic_runs_required":3,"pl_falsified":false}],"codex_available":true}' \
  "undetermined" \
  "all-green 이나 pl_falsified=false → undetermined (INV-FR5 실행자≠판정자)"

# ═════════════════════════════════════════════════════════════════════════════
# TC-9: Codex 미가용 (fail-mode (B)축) → fail-open (빈 dispositions, lane 진행 exit 0)
#   ★ discriminating: (A)축 falsified[닫기 거부]와 disjoint 증명. M2 always-block kill (falsified 양산 시 FAIL).
# ═════════════════════════════════════════════════════════════════════════════
run_setup_error_or_failopen_TC9() {
  local out exit_code=0 empty prov
  out=$(printf '%s' '{"findings":[{"id":"F-9","reproducible":true,"reproducer_present":true,"base_sha_present":true,"replay_runs":["red","red"],"deterministic_runs_required":2,"pl_falsified":false}],"codex_available":false}' | bash "$WRAPPER" 2>/dev/null) || exit_code=$?
  empty=$(printf '%s' "$out" | python3 -c 'import sys,json; d=json.loads(sys.stdin.read()); print("1" if (d.get("dispositions")==[] and d.get("provenance",{}).get("fail_open") is True) else "0")' 2>/dev/null) || empty="0"
  prov=$(printf '%s' "$out" | has_provenance 2>/dev/null) || prov="0"
  if [ "$empty" = "1" ] && [ "$prov" = "1" ] && [ "$exit_code" -eq 0 ]; then
    echo "✓ PASS: TC-9-codex-unavailable-fail-open → fail-open (empty dispositions, exit 0) — (B)축 lane-time fail-open, (A)축과 disjoint"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: TC-9-codex-unavailable-fail-open (empty=$empty prov=$prov exit=$exit_code) — raw: $out"
    FAIL=$((FAIL+1))
  fi
}
run_setup_error_or_failopen_TC9

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2480 fix-replay disposition)"
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
  echo "M1 always-close (decide_replay_disposition → 항상 PASS)"
  echo "   → TC-2/TC-3/TC-4/TC-5/TC-7/TC-8 FAIL = RED (close 거부/보류/면제 기대인데 PASS)"
  echo "M2 always-block (decide_replay_disposition → 항상 falsified)"
  echo "   → TC-1/TC-5/TC-9 FAIL = RED (PASS/impossible/fail-open 기대인데 falsified)"
  echo "M3 flaky-1회-close (FLAKY-1 횟수 검사 제거 → 1회 green 으로 PASS)"
  echo "   → TC-3 FAIL = RED (undetermined 기대인데 PASS = false-GREEN 누출, §1 목적 정면 훼손)"
  echo "M4 silent-replay-impossible (INV-FR2 reason 검사 제거 → reason 없이 replay-impossible)"
  echo "   → TC-6 FAIL = RED (exit 2 기대인데 exit 0 replay-impossible = silent 면제 누출)"
  echo ""
  echo "핵심 discriminating 쌍: TC-1(all-green+falsify→PASS) ↔ TC-2(all-red→falsified)"
  echo "  — 게이트가 'close 자체'가 아니라 'Retest GREEN 만 close 허용'함을 구별."
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed (disposition logic regressed / mutated)"
  exit 1
fi
