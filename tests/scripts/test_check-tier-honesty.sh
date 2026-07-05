#!/usr/bin/env bash
# tests/scripts/test_check-tier-honesty.sh
# CFP-2573 Phase 2 (구현 lane) — QADev execution-backed test for
#   scripts/check-tier-honesty.py (AC-6 tier 정직 meta-gate — measurement/advisory lever self-honesty).
#
# 계약 SSOT: ADR-144 §결정 7 (measurement/advisory lever 는 자기 tier 만 주장, 긍정 enforcement 언어 0).
#
# 검증 원칙 (mutation oracle, presence-grep false oracle 금지):
#   - check-tier-honesty.py 는 CWD-상대 5 lever artifact 를 스캔 → **격리 sandbox 미러**(실 artifact 복사)에서
#     `cd sandbox && python3 <real script>` 실행. mutation 은 sandbox 복사본에만 적용 → 원본/ git 오염 0.
#   - 실 스크립트 호출 후 **exit code + stdout 도메인 마커** 병행 대조 (distinct-marker — exit 2 collision 방어).
#   - RED = measurement lever 에 '물리강제' 긍정주입 / advisory lever 에 'blocking-on-pr' 긍정주입 / tier 라벨 strip.
#   - ★false-positive 방어 GREEN = 'block 금지'류 정직 부정 서술은 GREEN 유지 (closed-set 토큰만 매칭 실증).
#
# self-contained pure-bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-tier-honesty.py"
REAL_ADR025="$REPO_ROOT/archive/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md"

PASS=0
FAIL=0
pass() { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "✗ FAIL: $1"; echo "    $2"; FAIL=$((FAIL+1)); }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# 5 lever artifact 미러 sandbox 구축 (실 artifact 복사 — check-tier-honesty 는 text 스캔만, import 없음)
build_sandbox() {  # build_sandbox <dir>
  local d="$1"
  mkdir -p "$d/archive/adr" "$d/hooks" "$d/scripts/lib"
  cp "$REAL_ADR025" "$d/archive/adr/"
  cp "$REPO_ROOT/hooks/story-transition-autonomy-reminder.py"          "$d/hooks/"
  cp "$REPO_ROOT/scripts/lib/aggregate_stop_event.py"                  "$d/scripts/lib/"
  cp "$REPO_ROOT/scripts/lib/check_subagent_wait_liveness_presence.py" "$d/scripts/lib/"
  cp "$REPO_ROOT/scripts/check-tier-honesty.py"                        "$d/scripts/"
}

# 첫 매칭 라인 뒤에 텍스트 주입 (경로 = argv → MSYS mangle 안전)
inject_on_line() {  # inject_on_line <file> <line_substr> <inject_text>
  python3 - "$1" "$2" "$3" <<'PY'
import sys
f, sub, ins = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(f, encoding="utf-8").read().splitlines()
for i, l in enumerate(lines):
    if sub in l:
        lines[i] = l + " " + ins
        break
open(f, "w", encoding="utf-8").write("\n".join(lines) + "\n")
PY
}
strip_line() {  # strip_line <file> <line_substr>
  python3 - "$1" "$2" <<'PY'
import sys
f, sub = sys.argv[1], sys.argv[2]
lines = [l for l in open(f, encoding="utf-8").read().splitlines() if sub not in l]
open(f, "w", encoding="utf-8").write("\n".join(lines) + "\n")
PY
}

run_lint() {  # run_lint <sandbox_dir>  → sets OUT / EC
  EC=0
  OUT="$(cd "$1" && python3 "$SCRIPT" 2>&1)" || EC=$?
}
assert_case() {  # assert_case <name> <expected_exit> <marker_substr>
  local name="$1" exp="$2" marker="$3"
  local ok_exit=0 ok_mark=0
  [ "$EC" = "$exp" ] && ok_exit=1
  case "$OUT" in *"$marker"*) ok_mark=1;; esac
  if [ "$ok_exit" = 1 ] && [ "$ok_mark" = 1 ]; then
    pass "$name (exit $EC + marker '$marker')"
  else
    fail "$name" "expected exit $exp got $EC ; marker '$marker' present=$ok_mark ; out=[${OUT:0:200}]"
  fi
}

MEAS_LINE="tier: [measurement]"
ADVP_LINE="tier: [advisory / priming]"

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2573 AC-6: tier 정직 meta-gate — mutation oracle (execution-backed)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# ── GREEN: 현 lever set (5 lever 전부 자기 tier + 긍정 enforcement 0) ──────────────────
SB="$WORK/green"; build_sandbox "$SB"
run_lint "$SB"
assert_case "GREEN: 현 lever set 정직" 0 "PASS"

# ── RED: measurement lever(aggregate) tier-선언 라인에 '물리강제' 긍정주입 → exit 1 ────────
SB="$WORK/red_meas"; build_sandbox "$SB"
inject_on_line "$SB/scripts/lib/aggregate_stop_event.py" "$MEAS_LINE" "물리강제"
run_lint "$SB"
assert_case "RED: measurement lever '물리강제' 긍정주입 → 위반" 1 "FAIL"

# ── RED: advisory lever(reminder) tier-선언 라인에 'blocking-on-pr' 긍정주입 → exit 1 ──────
SB="$WORK/red_advp"; build_sandbox "$SB"
inject_on_line "$SB/hooks/story-transition-autonomy-reminder.py" "$ADVP_LINE" "blocking-on-pr"
run_lint "$SB"
assert_case "RED: advisory lever 'blocking-on-pr' 긍정주입 → 위반" 1 "FAIL"

# ── RED: measurement lever tier 라벨 strip (Axis1 위반) → exit 1 ──────────────────────
SB="$WORK/red_strip"; build_sandbox "$SB"
strip_line "$SB/scripts/lib/aggregate_stop_event.py" "$MEAS_LINE"
run_lint "$SB"
assert_case "RED: measurement lever tier 라벨 strip → 위반" 1 "FAIL"

# ── ★GREEN false-positive 방어: 'block 금지'류 정직 부정 서술은 GREEN 유지 ────────────────
# tier-선언 라인에 "NEVER block — deny/block 안 함" 주입 (closed-set enforcement 토큰 미포함) → 여전히 exit 0.
SB="$WORK/green_negation"; build_sandbox "$SB"
inject_on_line "$SB/scripts/lib/aggregate_stop_event.py" "$MEAS_LINE" "(NEVER block — deny/block 안 함)"
run_lint "$SB"
assert_case "GREEN: 정직 부정 서술('block 금지'류)은 GREEN 유지 (false-positive 방어)" 0 "PASS"

# ── consumer no-op: 5 lever 전부 부재 → honest no-op exit 0 ────────────────────────────
SB="$WORK/consumer"; mkdir -p "$SB"
run_lint "$SB"
assert_case "consumer no-op: 5 lever 부재 → honest no-op" 0 "no-op"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary — check-tier-honesty (AC-6)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — tier 정직 mutation oracle (물리강제/blocking-on-pr/strip → RED) + 부정서술 GREEN 유지"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
