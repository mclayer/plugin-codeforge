#!/usr/bin/env bash
# tests/scripts/test_check-vague-pause-taxonomy-presence.sh
# CFP-2573 Phase 2 (구현 lane) — QADev execution-backed test for
#   scripts/check-vague-pause-taxonomy-presence.sh (L1 vague-pause taxonomy presence lint).
#
# 계약 SSOT: ADR-144 §결정 2/7 + ADR-025 Amendment 3 (vague-pause 행 + decision-null discriminant + subclass).
#
# 검증 원칙 (RED→GREEN discriminating, presence-grep false oracle 금지):
#   - 실 스크립트 호출(bash wrapper → python) 후 **exit code + stdout 도메인 마커** 병행 대조.
#     distinct-marker 의무: exit 0/1/2 가 python 미 fork 시 exit 2(can't open file)와 겹칠 수 있으므로,
#     도메인 stdout 마커([...] PASS / FAIL / honest no-op)를 병행 assert (silent false-positive 차단).
#   - RED mutation = 실 ADR-025 복사본(정확 basename)에서 taxonomy 리터럴 삭제 → 실제 exit 1 관측.
#     (임시 fixture — 원본 ADR-025 미변경, git 오염 0.)
#
# self-contained pure-bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-vague-pause-taxonomy-presence.sh"
ADR025_BASENAME="ADR-025-stop-discipline-non-whitelist-as-defect.md"
REAL_ADR025="$REPO_ROOT/archive/adr/$ADR025_BASENAME"

PASS=0
FAIL=0
pass() { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "✗ FAIL: $1"; echo "    $2"; FAIL=$((FAIL+1)); }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# 실 스크립트 호출 (exit code + stdout capture)
run_lint() {  # run_lint <path...>  → sets OUT / EC
  EC=0
  OUT="$(bash "$WRAPPER" "$@" 2>&1)" || EC=$?
}

# exit code + distinct stdout 마커 병행 assert
assert_case() {  # assert_case <name> <expected_exit> <marker_substr>
  local name="$1" exp="$2" marker="$3"
  local ok_exit=0 ok_mark=0
  [ "$EC" = "$exp" ] && ok_exit=1
  case "$OUT" in *"$marker"*) ok_mark=1;; esac
  if [ "$ok_exit" = 1 ] && [ "$ok_mark" = 1 ]; then
    pass "$name (exit $EC + marker '$marker')"
  else
    fail "$name" "expected exit $exp got $EC ; marker '$marker' present=$ok_mark ; out=[${OUT:0:160}]"
  fi
}

# 실 ADR-025 → 복사본(정확 basename) + 특정 리터럴 삭제 → mutated fixture 경로 반환(stdout)
make_mutant() {  # make_mutant <subdir> <token>
  local dir="$WORK/$1"; mkdir -p "$dir"
  local dst="$dir/$ADR025_BASENAME"
  python3 - "$REAL_ADR025" "$dst" "$2" <<'PY'
import sys
src, dst, tok = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src, encoding="utf-8").read()
open(dst, "w", encoding="utf-8").write(t.replace(tok, ""))
PY
  echo "$dst"
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2573 AC-1: vague-pause taxonomy presence lint — RED→GREEN discriminating"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# ── GREEN: 현 ADR-025 상태 (3 taxonomy 리터럴 전부 존재) ──────────────────────────────
run_lint "$REAL_ADR025"
assert_case "GREEN: 실 ADR-025 (3 리터럴 전부 존재)" 0 "PASS"

# ── RED mutation: vague-pause 행 삭제 (vague-pause 리터럴 소실) → exit 1 ────────────────
M1="$(make_mutant m_vague vague-pause)"
run_lint "$M1"
assert_case "RED: vague-pause 리터럴 삭제 → 위반" 1 "FAIL"

# ── RED mutation: decision-null discriminant 삭제 → exit 1 ────────────────────────────
M2="$(make_mutant m_disc decision-null)"
run_lint "$M2"
assert_case "RED: decision-null discriminant 삭제 → 위반" 1 "FAIL"

# ── RED mutation: policy_violation_vague_pause subclass enum 삭제 → exit 1 ─────────────
M3="$(make_mutant m_subclass policy_violation_vague_pause)"
run_lint "$M3"
assert_case "RED: policy_violation_vague_pause subclass 삭제 → 위반" 1 "FAIL"

# ── consumer no-op: ADR-025 부재 경로 (wrapper 전용 taxonomy) → exit 0 honest no-op ────
NOOP_DIR="$WORK/consumer"; mkdir -p "$NOOP_DIR/archive/adr"   # ADR-025 없음 (다른 파일만)
printf 'not an ADR-025 doc\n' > "$NOOP_DIR/archive/adr/ADR-999-other.md"
run_lint "$NOOP_DIR"
assert_case "consumer no-op: ADR-025 부재 → honest no-op" 0 "honest no-op"

# ── setup error: 미존재 경로 → exit 2 (도메인 exit 2 distinct 관측) ────────────────────
run_lint "$WORK/definitely-missing-path"
assert_case "setup error: 미존재 경로 → exit 2" 2 "setup error"

# ── false-positive 방어: vague-pause 행 존치 (전부 존재)면 GREEN 유지 재확인 ────────────
# (subclass 만 있고 vague-pause/decision-null 없는 문서 = RED 이어야 함 — 부분 존재 거짓통과 차단)
PARTIAL_DIR="$WORK/partial"; mkdir -p "$PARTIAL_DIR/archive/adr"
printf '%s\n' '- policy_violation_vague_pause (subclass only, 행/discriminant 없음)' \
  > "$PARTIAL_DIR/archive/adr/$ADR025_BASENAME"
run_lint "$PARTIAL_DIR/archive/adr/$ADR025_BASENAME"
assert_case "partial: subclass 만 존재(행/discriminant 부재) → 위반" 1 "FAIL"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary — check-vague-pause-taxonomy-presence (AC-1)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — taxonomy 리터럴 3종 load-bearing (mutation→RED) + consumer no-op + setup 구분"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
