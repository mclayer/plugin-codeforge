#!/usr/bin/env bash
# tests/scripts/test_check-active-sessions-presence.sh
# CFP-2761 Phase 2 (구현 lane) — ADR-085 Wave2 `active-sessions-presence` self-test (Change Plan §8.3).
#
#   SSOT: scripts/lib/check_active_sessions_presence.py + wrapper scripts/check-active-sessions-presence.sh.
#   검출 신호 = STDOUT `::warning::active-sessions-presence:` 토큰 presence (warning-tier — PR-time workflow).
#   GREEN = 토큰 부재. exit: 0=clean/warn/honest-noop, 2=usage, 3=born-hollow.
#
#   presence check(firsthand): Story 파일에 frontmatter `active_sessions:` 키 OR 본문 단일라인
#     `<!-- active_sessions -->` 블록 부재 → warning. 스캔 = docs/stories/**/*.md glob(또는 --files).
#   honesty ceiling: presence ≠ truth(§7.8 상속).
#
# self-contained bash (tests/scripts 관례, bats 미사용 — ADR-060 Amд 22). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-active-sessions-presence.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_active_sessions_presence.py"
TOKEN="::warning::active-sessions-presence:"

PASS=0
FAIL=0

if [ ! -f "$WRAPPER" ] || [ ! -f "$SSOT_PY" ]; then
  echo "DEFERRED-NO-SCRIPT-UNDER-TEST: check-active-sessions-presence .sh/.py 부재 (병렬 authoring window)."
  echo "  → fixture 저작 완료·ready. 착지 후 collection-phase 실행. (honest-degrade exit 0.)"
  exit 0
fi

run_case() {
  local name="$1" exp_exit="$2" expect="$3" relpath="$4" content="$5"
  local exit_code=0 out tmpdir ok=1
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  if [ -n "$relpath" ]; then
    mkdir -p "$tmpdir/$(dirname "$relpath")"
    printf '%s\n' "$content" > "$tmpdir/$relpath"
  fi
  out=$(bash "$WRAPPER" --repo-root "$tmpdir" 2>&1) || exit_code=$?
  [ "$exit_code" -eq "$exp_exit" ] || ok=0
  case "$expect" in
    YES)     case "$out" in *"$TOKEN"*) : ;; *) ok=0;; esac ;;
    NO)      case "$out" in *"$TOKEN"*) ok=0;; esac ;;
    NOEMPTY) case "$out" in *"$TOKEN"*) ok=0;; esac; [ -n "$out" ] || ok=0 ;;
  esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $exit_code, expect=$expect)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name"; echo "  expected exit=$exp_exit expect=$expect, got exit=$exit_code"; echo "  output: $out"; FAIL=$((FAIL+1))
  fi
}

# mutant_misflag: (1) baseline — 원본으로 GREEN fixture 실행 → 토큰 ABSENT 확증(GREEN 정합, non-vacuous).
#   (2) 인식 anchor 무력화 → (3) GREEN 오분류(토큰 PRESENT) = 인식 branch load-bearing. anchor drift → HARD FAIL.
mutant_misflag() {
  local name="$1" relpath="$2" content="$3" anchor="$4" replacement="$5"
  local tmpdir mutant ok=1 apply_rc=0 base_exit=0 mut_exit=0 base_out mut_out storydir
  tmpdir=$(mktemp -d)
  mutant="$(dirname "$SSOT_PY")/._asp_mutant_$$_${RANDOM}.py"
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'; rm -f '$mutant'" RETURN
  mkdir -p "$tmpdir/$(dirname "$relpath")"
  printf '%s\n' "$content" > "$tmpdir/$relpath"

  base_out=$(bash "$WRAPPER" --repo-root "$tmpdir" 2>&1) || base_exit=$?
  case "$base_out" in *"$TOKEN"*) ok=0;; esac
  if [ "$ok" -eq 0 ]; then
    echo "X FAIL: $name — baseline GREEN 이 이미 토큰 방출(fixture 가 pre-mutation 에 오분류 = 무의미 MK)"
    echo "  baseline output: $base_out"; FAIL=$((FAIL+1)); return
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
  mut_out=$(python3 "$mutant" --repo-root "$tmpdir" 2>&1) || mut_exit=$?
  case "$mut_out" in *"$TOKEN"*) : ;; *) ok=0;; esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (baseline GREEN→no-token / mutant GREEN 오분류 방출 exit $mut_exit — 인식 anchor load-bearing, killed)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name — mutant 가 GREEN 을 여전히 정상 인식(토큰 부재) = anchor 무력화 실패"; echo "  mutant output: $mut_out"; FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2761: active-sessions-presence — self-test (§8.3)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── RED (active_sessions frontmatter/block 양쪽 부재 → 검출) ──"
run_case "RED active_sessions 전무" 0 YES "docs/stories/CFP-9999.md" \
"---
key: value
phase: 구현
---
# Story CFP-9999
active_sessions 표식이 어디에도 없음."

echo
echo "── GREEN (active_sessions presence → 미검출) ──"
run_case "GREEN frontmatter active_sessions:" 0 NO "docs/stories/CFP-9998.md" \
"---
key: value
active_sessions:
  - git_identity: alice
    worktree_path: /wt/cfp-9998
    entry_phase: 구현
---
# Story CFP-9998"
run_case "GREEN inline <!-- active_sessions --> 단일라인 블록" 0 NO "docs/stories/CFP-9997.md" \
"# Story CFP-9997
<!-- active_sessions -->
본문."

echo
echo "── 경계 (honest-degrade — silent-green 금지) ──"
run_case "TC-EMPTY story 0 파일 honest-noop" 0 NOEMPTY "" ""

echo
echo "── Mutation-kill (인식 anchor isolation 증명, baseline GREEN pre-check) ──"
mutant_misflag "MK active_sessions-anchor 무력화 → GREEN 오분류" "docs/stories/CFP-9996.md" \
"---
active_sessions:
  - git_identity: carol
    entry_phase: 구현
---
# Story CFP-9996" \
"active_sessions" "__mk_no_as__"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — presence RED/GREEN(frontmatter+단일라인 block)/honest-noop/mutation-kill(baseline) 결박"; exit 0
else
  echo "X $FAIL case(s) failed"; exit 1
fi
