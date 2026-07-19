#!/usr/bin/env bash
# tests/scripts/test_check-lane-entry-ownership.sh
# CFP-2761 Phase 2 (구현 lane) FIX iter1 — ADR-085 Wave2 `lane-entry-ownership-verify` self-test (§8.3).
#
#   SSOT: scripts/lib/check_lane_entry_ownership.py + wrapper scripts/check-lane-entry-ownership.sh.
#   검출 신호 = STDOUT `::warning::lane-entry-ownership-verify:` 토큰 presence (warning-tier, hook-only).
#   GREEN = 토큰 부재. exit 0 always (2 = 주어진 --sessions-file unparseable 일 때만).
#
#   ★ NEW 계약 (F2 derive-from-ambient + fixture-injection — CFP-2761 구현리뷰 FIX):
#     (A) fixture-injection: --git-identity ID + --sessions-file FILE 둘 다 명시 → **deterministic
#         ownership-presence eval** (ambient 파생 우회). ownership-presence = 진입 identity 가
#         active_sessions 소유자 목록에 존재하는가(entry_phase 무관 subset). 존재 → GREEN(토큰 부재),
#         부재 → `::warning::lane-entry-ownership-verify: ... re-adjudication candidate`, exit 0.
#     (B) honest-degrade: --git-identity/--sessions-file 미명시 + ambient(git-identity/branch→CFP)
#         파생이 실패하는 컨텍스트(비-git / 비-CFP-branch --repo-root) → 명시 "확인 불가" no-op 라인
#         (silent-green 금지) + exit 0 + `::warning::` 부재 (degrade ≠ finding).
#
#   ★ scope 정직 (honesty ceiling): 본 self-test 는 ownership-presence subset(존재/부재) + honest-degrade
#     까지만 결박 — full lane-conflict(동일 lane concurrent distinct owner) 판정은 ambient lane 의존
#     이라 fixture-injection subset 밖 (presence ≠ full ownership truth).
#
# self-contained bash (tests/scripts 관례, bats 미사용 — ADR-060 Amд 22). Exit 0 = 전 케이스 PASS.
# house style = tests/scripts/test_check-mid-flight-marker.sh (run_case + mutant_case).

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-lane-entry-ownership.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_lane_entry_ownership.py"
TOKEN="::warning::lane-entry-ownership-verify:"

PASS=0
FAIL=0

# Preflight: script-under-test 부재(병렬 authoring window) → honest-degrade DEFERRED(silent-green 아님) exit 0.
if [ ! -f "$WRAPPER" ] || [ ! -f "$SSOT_PY" ]; then
  echo "DEFERRED-NO-SCRIPT-UNDER-TEST: check-lane-entry-ownership .sh/.py 부재 (병렬 authoring window)."
  echo "  → fixture 저작 완료·ready. 착지 후 collection-phase 실행. (honest-degrade exit 0.)"
  exit 0
fi

# run_le: fixture-injection 경로 — --git-identity ID + --sessions-file <json> 로 결정적 ownership-presence
#   eval. expect: YES(토큰 present) / NO(토큰 부재). exit 0 기대.
run_le() {
  local name="$1" expect="$2" identity="$3" sessions="$4"
  local exit_code=0 out tmpdir ok=1 sf
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  sf="$tmpdir/sessions.json"
  printf '%s\n' "$sessions" > "$sf"
  out=$(bash "$WRAPPER" --git-identity "$identity" --sessions-file "$sf" 2>&1) || exit_code=$?
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

# degrade_case: ambient 파생 실패 컨텍스트(비-git tmpdir --repo-root, identity/sessions 미명시) →
#   명시 "확인 불가" no-op(비-침묵) + exit 0 + 토큰 부재(degrade ≠ finding).
degrade_case() {
  local name="$1"
  local exit_code=0 out tmpdir ok=1
  tmpdir=$(mktemp -d)  # 비-git / 비-CFP-branch — ambient(identity·branch→CFP) 파생 실패 유도.
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  out=$(bash "$WRAPPER" --repo-root "$tmpdir" 2>&1) || exit_code=$?
  [ "$exit_code" -eq 0 ] || ok=0
  case "$out" in *"확인 불가"*) : ;; *) ok=0;; esac  # visible honest line (silent-green 금지)
  [ -n "$out" ] || ok=0                              # 비-침묵 강제
  case "$out" in *"$TOKEN"*) ok=0;; esac             # degrade 는 finding 아님 — 토큰 부재
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $exit_code, '확인 불가' honest no-op, 토큰 부재)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name"; echo "  expected exit=0 + '확인 불가' stdout + no-token, got exit=$exit_code"; echo "  output: $out"; FAIL=$((FAIL+1))
  fi
}

# mutant_flip: ownership-presence anchor isolation 증명 (baseline RED pre-check 로 non-vacuous 강제).
#   (1) baseline — 원본으로 ABSENT fixture(identity 부재) 실행 → 토큰 PRESENT 확증(RED non-vacuous).
#   (2) SSOT .py 사본에서 ownership-presence gate anchor 무력화(정확 1치환) → (3) mutant 실행 →
#   토큰 DISAPPEAR(=ABSENT fixture 가 GREEN 으로 flip = killed). anchor 미적용 → HARD FAIL(reconcile).
#   ABSENT fixture = active_sessions 빈 목록 + 진입 identity 부재 → re-adjudication 단일 branch 격리
#   (concurrent-owner branch 간섭 배제).
mutant_flip() {
  local name="$1" identity="$2" sessions="$3" anchor="$4" replacement="$5"
  local tmpdir mutant sf ok=1 apply_rc=0 base_exit=0 mut_exit=0 base_out mut_out
  tmpdir=$(mktemp -d)
  mutant="$(dirname "$SSOT_PY")/._leo_mutant_$$_${RANDOM}.py"
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'; rm -f '$mutant'" RETURN
  sf="$tmpdir/sessions.json"
  printf '%s\n' "$sessions" > "$sf"

  # (1) baseline RED 확증 (ABSENT → 토큰 PRESENT).
  base_out=$(bash "$WRAPPER" --git-identity "$identity" --sessions-file "$sf" 2>&1) || base_exit=$?
  case "$base_out" in *"$TOKEN"*) : ;; *) ok=0;; esac
  if [ "$ok" -eq 0 ]; then
    echo "X FAIL: $name — baseline RED 부재(ABSENT fixture 가 pre-mutation 에 미검출 = vacuous MK)"
    echo "  baseline output: $base_out"; FAIL=$((FAIL+1)); return
  fi

  # (2) mutate .py 사본.
  python3 - "$SSOT_PY" "$mutant" "$anchor" "$replacement" <<'PY' || apply_rc=$?
import sys
src, out, anchor, repl = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(src, encoding="utf-8").read()
if anchor not in s:
    sys.stderr.write("ANCHOR-DRIFT: %r 부재 in %s\n" % (anchor, src)); sys.exit(3)
open(out, "w", encoding="utf-8").write(s.replace(anchor, repl, 1))
PY
  if [ "$apply_rc" -ne 0 ]; then
    echo "X FAIL: $name — mutation anchor drift ('$anchor' 부재) → reconcile against real .py"; FAIL=$((FAIL+1)); return
  fi

  # (3) mutant 실행 → 토큰 소실(ABSENT flip to GREEN) 확증.
  mut_out=$(python3 "$mutant" --git-identity "$identity" --sessions-file "$sf" 2>&1) || mut_exit=$?
  case "$mut_out" in *"$TOKEN"*) ok=0;; esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (baseline RED→token / mutant 토큰 소실 exit $mut_exit — ownership-presence gate load-bearing, killed)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name — mutant 이 여전히 ABSENT 를 검출(토큰 잔존) = anchor 가 ownership-presence gate 를 무력화 못함"; echo "  mutant output: $mut_out"; FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2761: lane-entry-ownership-verify — self-test (§8.3, F2 derive-from-ambient)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── PRESENT (진입 identity 가 active_sessions 소유자 존재 → GREEN, 토큰 부재) ──"
run_le "PRESENT (alice 소유 존재)" NO "alice" \
'{"active_sessions":[{"git_identity":"alice","entry_phase":"구현"}]}'

echo
echo "── ABSENT (진입 identity 부재 → 검출, re-adjudication candidate) ──"
run_le "ABSENT (bob 소유 부재 — alice-only fixture)" YES "bob" \
'{"active_sessions":[{"git_identity":"alice","entry_phase":"구현"}]}'

echo
echo "── HONEST-DEGRADE (ambient 파생 실패 → '확인 불가' no-op, 토큰 부재) ──"
degrade_case "HONEST-DEGRADE 비-git repo-root, identity/sessions 미명시"

echo
echo "── Mutation-kill (ownership-presence anchor isolation — baseline RED pre-check) ──"
# ABSENT fixture(빈 active_sessions + 진입 identity 부재) → baseline 토큰 PRESENT. ownership-presence
#   gate(`if not ownership_present:` — check_lane_entry_ownership.py Step 5 firsthand-verified) 무력화 →
#   토큰 소실(GREEN flip). PRESENT fixture 는 gate 미도달이라 불변 → ABSENT 만이 anchor 검출.
mutant_flip "MK ownership-presence gate 무력화 → ABSENT flip to GREEN [필수]" "bob" \
'{"active_sessions":[]}' \
'if not ownership_present:' 'if False:  # MK-ownership-presence'

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — PRESENT/ABSENT/HONEST-DEGRADE/mutation-kill(baseline RED) 결박"; exit 0
else
  echo "X $FAIL case(s) failed"; exit 1
fi
