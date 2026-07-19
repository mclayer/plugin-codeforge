#!/usr/bin/env bash
# tests/scripts/test_check-lane-entry-ownership.sh
# CFP-2761 Phase 2 (구현 lane) — ADR-085 Wave2 `lane-entry-ownership-verify` self-test (§8.3).
#
#   SSOT: scripts/lib/check_lane_entry_ownership.py + wrapper scripts/check-lane-entry-ownership.sh.
#   검출 신호 = STDOUT `::warning::lane-entry-ownership-verify:` 토큰 presence (warning-tier, hook-only).
#   GREEN = 토큰 부재.
#
#   detection(firsthand): entry 매칭 키 = **entry_phase**(==lane) + git_identity. 진입 (lane, git_identity)
#     의 소유 레코드(entry_phase==lane & git_identity==id) 부재 → warn / 동일 lane(entry_phase) 을 다른
#     identity 가 소유(concurrent distinct owner) → conflict warn. sessions-file = JSON/YAML.
#
# self-contained bash (tests/scripts 관례, bats 미사용 — ADR-060 Amд 22). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-lane-entry-ownership.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_lane_entry_ownership.py"
TOKEN="::warning::lane-entry-ownership-verify:"

PASS=0
FAIL=0

if [ ! -f "$WRAPPER" ] || [ ! -f "$SSOT_PY" ]; then
  echo "DEFERRED-NO-SCRIPT-UNDER-TEST: check-lane-entry-ownership .sh/.py 부재 (병렬 authoring window)."
  echo "  → fixture 저작 완료·ready. 착지 후 collection-phase 실행. (honest-degrade exit 0.)"
  exit 0
fi

run_le() {
  local name="$1" expect="$2" lane="$3" identity="$4" sessions="$5"
  local exit_code=0 out tmpdir ok=1 sf
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  sf="$tmpdir/sessions.yaml"
  printf '%s\n' "$sessions" > "$sf"
  out=$(bash "$WRAPPER" --lane "$lane" --git-identity "$identity" --sessions-file "$sf" 2>&1) || exit_code=$?
  [ "$exit_code" -eq 0 ] || ok=0
  case "$expect" in
    YES) case "$out" in *"$TOKEN"*) : ;; *) ok=0;; esac ;;
    NO)  case "$out" in *"$TOKEN"*) ok=0;; esac ;;
  esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $exit_code, expect=$expect)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name"; echo "  expect=$expect got exit=$exit_code"; echo "  output: $out"; FAIL=$((FAIL+1))
  fi
}

# mutant_misflag: (1) baseline — 원본 GREEN → 토큰 ABSENT 확증(non-vacuous). (2) owner-lookup anchor
#   `.get("git_identity")`(record-key; args.git_identity 미접촉) 무력화 → (3) GREEN 오분류(토큰 PRESENT).
mutant_misflag() {
  local name="$1" lane="$2" identity="$3" sessions="$4" anchor="$5" replacement="$6"
  local exit_code=0 base_exit=0 out base_out tmpdir mutant ok=1 apply_rc=0 sf
  tmpdir=$(mktemp -d)
  mutant="$(dirname "$SSOT_PY")/._leo_mutant_$$_${RANDOM}.py"
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'; rm -f '$mutant'" RETURN
  sf="$tmpdir/sessions.yaml"
  printf '%s\n' "$sessions" > "$sf"

  base_out=$(bash "$WRAPPER" --lane "$lane" --git-identity "$identity" --sessions-file "$sf" 2>&1) || base_exit=$?
  case "$base_out" in *"$TOKEN"*) ok=0;; esac
  if [ "$ok" -eq 0 ]; then
    echo "X FAIL: $name — baseline GREEN 이 이미 토큰 방출(무의미 MK)"; echo "  baseline: $base_out"; FAIL=$((FAIL+1)); return
  fi

  python3 - "$SSOT_PY" "$mutant" "$anchor" "$replacement" <<'PY' || apply_rc=$?
import sys
src, out, anchor, repl = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(src, encoding="utf-8").read()
if anchor not in s:
    sys.stderr.write("ANCHOR-DRIFT: %r 부재\n" % (anchor,)); sys.exit(3)
open(out, "w", encoding="utf-8").write(s.replace(anchor, repl))
PY
  if [ "$apply_rc" -ne 0 ]; then
    echo "X FAIL: $name — mutation anchor drift ('$anchor' 부재) → reconcile against real .py"; FAIL=$((FAIL+1)); return
  fi
  out=$(python3 "$mutant" --lane "$lane" --git-identity "$identity" --sessions-file "$sf" 2>&1) || exit_code=$?
  case "$out" in *"$TOKEN"*) : ;; *) ok=0;; esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (baseline GREEN→no-token / mutant GREEN 오분류 방출 exit $exit_code — owner-lookup anchor load-bearing, killed)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name — mutant 가 GREEN 을 여전히 정상 인식(토큰 부재) = anchor 무력화 실패"; echo "  mutant output: $out"; FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2761: lane-entry-ownership-verify — self-test (§8.3)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── RED (owner 레코드 부재 → 검출) ──"
run_le "RED (구현, alice) owner 레코드 부재" YES "구현" "alice" \
"active_sessions:
  - git_identity: bob
    entry_phase: 설계"

echo
echo "── RED conflict (동일 lane 다른 identity 이미 소유 → 검출) ──"
run_le "RED conflict 구현 을 bob 이 소유" YES "구현" "alice" \
"active_sessions:
  - git_identity: bob
    entry_phase: 구현"

echo
echo "── GREEN (매칭 owner 레코드 존재 → 미검출) ──"
run_le "GREEN (구현, alice) owner 레코드 존재" NO "구현" "alice" \
"active_sessions:
  - git_identity: alice
    entry_phase: 구현
  - git_identity: bob
    entry_phase: 설계"

echo
echo "── Mutation-kill (owner-lookup anchor isolation 증명, baseline GREEN pre-check) ──"
mutant_misflag "MK git_identity-record-key 무력화 → GREEN 오분류" "구현" "alice" \
"active_sessions:
  - git_identity: alice
    entry_phase: 구현" \
'.get("git_identity")' '.get("__mk_no_gitid__")'

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — owner-absent RED/conflict RED/GREEN/mutation-kill(baseline) 결박"; exit 0
else
  echo "X $FAIL case(s) failed"; exit 1
fi
