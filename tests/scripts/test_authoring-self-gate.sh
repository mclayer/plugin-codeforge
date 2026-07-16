#!/usr/bin/env bash
# tests/scripts/test_authoring-self-gate.sh
# CFP-2689 Phase 2 (구현 lane) / Epic #2686 Story C / ADR-158 — author-time self-gate 의 CI self-test wrapper.
#   scripts/lib/authoring_self_gate.py (저작시점 shift-left self-gate runner — 대상 기계 게이트를 리뷰 lane
#   진입 前 자기 산출물에 선실행 + 검출 결점 A ledger emit) 의 execution-backed 검증 채널.
#
# 계약 SSOT: archive/adr/ADR-158-*.md (결정 1~9) + change-plan 2026-07-16-cfp-2689 §4/§8.
#
# 검증 원칙 (execution-backed, hollow 금지 — CFP-2635/CFP-2545 선례):
#   - real invocation: runner embedded `--self-test`(독립 oracle + 대칭 fail-closed 양방향) +
#       pytest `tests/unit/test_authoring_self_gate.py`(QADev deliverable — 본 wrapper 는 호출만) 를
#       exit-code gated 로 구동.
#   - ★distinct-marker 의무 (exit-code-only 금지 — subprocess-fork 진정성): 각 fork 통과 판정을
#       exit code + **도메인 고유 stdout sentinel** 을 병행 assert. 미 fork 시 python 은 exit≠0 + 빈/
#       무관 stdout → sentinel assert 자연 실패(silent false-positive 차단). 도메인 exit(0)과 표준 exit
#       우연 일치 방어.
#
# ★exit-masking / mock-seam BAN (ADR-060 Amd22 / CFP-2635) — 본 wrapper 준수:
#   - 모든 `|| EC=$?` 는 counter-backed(직후 assert_eq 로 EC 판정) — bare `cmd || true` 무.
#   - mock-seam env(_*MOCK*=) 미사용 — 실 runner round-trip 만.
#
# ★Windows/Git-Bash (MEMORY CFP-2659): mktemp -d 사용(하드코딩 /tmp 금지). python helper 경로 = argv
#   전달(MSYS mangle 안전). 로컬 Git-Bash 에서 pytest fork 는 QADev 파일 미착지 시 RED(정상 — DevPL 이
#   QADev 합류 후 통합 검증). CI ubuntu authoritative.
# Exit 0 = 전 케이스 PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

# python3 우선(CI ubuntu authoritative), 부재 시 python fallback(로컬 Windows 견고성).
PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="$REPO_ROOT/scripts/lib/authoring_self_gate.py"
PYTEST_FILE="$REPO_ROOT/tests/unit/test_authoring_self_gate.py"

PASS=0
FAIL=0
pass() { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "✗ FAIL: $1"; echo "    $2"; FAIL=$((FAIL+1)); }

assert_eq()  { if [ "$2" = "$3" ]; then pass "$1 [$2]"; else fail "$1" "expected [$3] got [$2] — ${4:-}"; fi; }
assert_has() { case "$2" in *"$3"*) pass "$1";; *) fail "$1" "missing substring [$3] in output";; esac; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2689 Story C — author-time self-gate runner (execution-backed)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# ══ 케이스 1: runner --self-test (독립 oracle + 대칭 fail-closed) — exit 0 + distinct-marker ══
OUT1="$WORK/runner_selftest.out"; EC=0
"$PY" "$RUNNER" --self-test > "$OUT1" 2>&1 || EC=$?
assert_eq "runner --self-test: exit 0 (독립 oracle + 대칭 fail-closed 양방향 PASS)" "$EC" "0" "embedded self-test PASS 이어야"
# distinct-marker: 도메인 고유 sentinel (미 fork 시 exit≠0 + 무관 stdout → 아래 전부 RED)
assert_has "runner --self-test: distinct-marker (도메인 sentinel)" "$(cat "$OUT1")" "authoring-self-gate self-test"
assert_has "runner --self-test: distinct-marker (known-bad → FAIL 대칭)" "$(cat "$OUT1")" "SELFTEST[ac-bad-rtm-row]=FAIL"
assert_has "runner --self-test: distinct-marker (R1 path-aware N/A)" "$(cat "$OUT1")" "SELFTEST[docsec-R1-na]=N/A"
assert_has "runner --self-test: distinct-marker (측정≠emit 구분)" "$(cat "$OUT1")" "SELFTEST[e2e-stats-ran-not-emit]"
assert_has "runner --self-test: 종합 PASS sentinel" "$(cat "$OUT1")" "self-test: PASS"

# ══ 케이스 2: pytest tests/unit/test_authoring_self_gate.py (QADev deliverable — 호출만) ══
#   본 wrapper 는 QADev 작성 파일을 호출만. 파일 미착지 시 RED(정상 — DevPL 이 QADev 합류 후 통합).
OUT2="$WORK/pytest.out"; EC=0
"$PY" -m pytest "$PYTEST_FILE" -q > "$OUT2" 2>&1 || EC=$?
assert_eq "pytest test_authoring_self_gate: exit 0 (QADev AC-1~18 test 전량 PASS)" "$EC" "0" \
  "QADev 작성 tests/unit/test_authoring_self_gate.py 전량 GREEN 이어야 (파일 미착지 시 RED=born-red 통합 전)"
# distinct-marker: pytest 실 실행 sentinel (미 fork/파일부재 시 'passed' 부재 → RED)
assert_has "pytest: distinct-marker (실 실행 'passed')" "$(cat "$OUT2")" "passed"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary — authoring-self-gate (CFP-2689 Story C)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — runner --self-test(독립 oracle + 대칭 fail-closed) + pytest AC-1~18"
  echo "  (distinct-marker gated, exit-masking/mock-seam 무)."
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
