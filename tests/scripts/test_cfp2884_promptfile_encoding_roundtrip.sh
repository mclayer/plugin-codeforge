#!/usr/bin/env bash
# tests/scripts/test_cfp2884_promptfile_encoding_roundtrip.sh
# CFP-2884 Phase 2 (r9/r10) — Codex promptfile UTF-8 round-trip self-test wrapper.
#   Change Plan §5 row 14 (Codex promptfile 언어 구획 규약 Phase 2 — wrapper fixture) +
#   ADR-151 corpus 편입 (AC-1a bijection metadata gate).
#
# 계약 SSOT: wrapper/change-plans/cfp-2884-codex-promptfile-utf8-language-partition.md §5 row 14.
#
# 실행 진정성 계약 (r10 — R7-1, distinct-marker 의무 · exit-code-only 금지):
#   pytest fork 판정 = exit code ∧ stdout 'passed' 토큰 병행 assert
#   (전량 skip 출력 'N skipped' 에는 'passed' 토큰 부재 — 판별력 실측)
#   - 선례: tests/scripts/test_authoring-self-gate.sh L13-16 (★distinct-marker) + L72 (pytest 'passed' assert)
#   - CFP-2635 / ADR-060 Amendment 22: exit-code masking 금지, subprocess-fork 진정성
#
# Windows/Git-Bash 견고성 (CFP-2659): mktemp -d 안전 (python helper 경로 = argv 전달).
# Exit 0 = pytest suite PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

# python3 우선(CI ubuntu authoritative), 부재 시 python fallback(로컬 Windows 견고성).
PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTEST_FILE="$REPO_ROOT/tests/scripts/test_cfp2884_promptfile_encoding_roundtrip.py"

PASS=0
FAIL=0
pass() { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "✗ FAIL: $1"; echo "    $2"; FAIL=$((FAIL+1)); }

assert_eq()  { if [ "$2" = "$3" ]; then pass "$1 [$2]"; else fail "$1" "expected [$3] got [$2] — ${4:-}"; fi; }
assert_has() { case "$2" in *"$3"*) pass "$1";; *) fail "$1" "missing substring [$3] in output";; esac; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2884 Phase 2 — Codex promptfile UTF-8 round-trip test wrapper"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# ══ pytest suite 실행 (행 5 계약: python3 -m pytest ... -q + exit-code 전파) ══
OUT="$WORK/pytest.out"; EC=0
"$PY" -m pytest "$PYTEST_FILE" -q > "$OUT" 2>&1 || EC=$?

# ★distinct-marker 의무: exit code ∧ stdout sentinel 병행 assert (exit-code-only 금지)
assert_eq "pytest suite: exit 0 (fixture AC-1~6/AC-9 PASS)" "$EC" "0" \
  "tests/scripts/test_cfp2884_promptfile_encoding_roundtrip.py 전량 GREEN"

# Distinct-marker: pytest 실 실행 sentinel 'passed' (전량 skip = 'N skipped' 출력이라 sentinel 부재 판별)
assert_has "pytest: distinct-marker (실 실행 'passed')" "$(cat "$OUT")" "passed"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary — CFP-2884 promptfile UTF-8 round-trip"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — pytest AC-1~6/AC-9 (distinct-marker gated, exit-code-only 무)."
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
