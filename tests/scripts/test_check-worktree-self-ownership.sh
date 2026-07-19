#!/usr/bin/env bash
# tests/scripts/test_check-worktree-self-ownership.sh
# CFP-2761 Phase 2 (구현 lane) — ADR-073 Amд3/Amд21 `worktree-self-ownership-verify` self-test (§8.4).
#   유형#4(미머지 worktree) discrimination 이 여기 산다 (mid-flight-marker check 은 유형4 미claim).
#
#   SSOT: scripts/lib/check_worktree_self_ownership.py + wrapper scripts/check-worktree-self-ownership.sh.
#   검출 신호 = STDOUT `::warning::worktree-self-ownership-verify:` 토큰 presence (warning-tier, hook-only).
#   GREEN = 토큰 부재.
#
#   FIXTURE-INJECTION (live git state 미의존 — deterministic): path-based 3-tuple
#     (a) toplevel ↔ worktree-list path / (b) branch ↔ reflog membership (reflog GC 시 (a)+(c) fallback)
#     (c) branch ↔ worktree-list + reflog 2-source AND.
#
#   ★ Windows gotcha (firsthand 실측): `--toplevel /wt/...` 처럼 선두 슬래시 POSIX 경로는 Git Bash MSYS
#     경로변환으로 mangle 됨. MSYS_NO_PATHCONV 전역 export 는 SSOT_PY(`/c/Users/...`) 경로까지 깨서 역효과.
#     → fixture 경로를 **가짜 드라이브 경로 `Z:/wt/...`** 로 사용(MSYS 무변환 + check `_normalize_path` 가
#       drive lowercase/slash 정규화로 Windows·Linux 동형 처리 → 결정적).
#
# self-contained bash (tests/scripts 관례, bats 미사용 — ADR-060 Amд 22). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-worktree-self-ownership.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_worktree_self_ownership.py"
TOKEN="::warning::worktree-self-ownership-verify:"
BRANCH="cfp-2761-mid-flight-markers"
TOP="Z:/wt/cfp-2761-mid-flight-markers"

PASS=0
FAIL=0

if [ ! -f "$WRAPPER" ] || [ ! -f "$SSOT_PY" ]; then
  echo "DEFERRED-NO-SCRIPT-UNDER-TEST: check-worktree-self-ownership .sh/.py 부재 (병렬 authoring window)."
  echo "  → fixture 저작 완료·ready. 착지 후 collection-phase 실행. (honest-degrade exit 0.)"
  exit 0
fi

WL_GREEN="worktree ${TOP}
HEAD 1111111111111111111111111111111111111111
branch refs/heads/${BRANCH}

worktree Z:/wt/main
HEAD 2222222222222222222222222222222222222222
branch refs/heads/main"
RL_GREEN="1111111 HEAD@{0}: checkout: moving from main to ${BRANCH}
2222222 HEAD@{1}: commit: work on ${BRANCH}"

run_wt() {
  local name="$1" expect="$2" toplevel="$3" branch="$4" wl="$5" rl="$6" verdict="${7:-}"
  local exit_code=0 out tmpdir ok=1 wlf rlf
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  wlf="$tmpdir/wl.txt"; rlf="$tmpdir/rl.txt"
  printf '%s\n' "$wl" > "$wlf"
  printf '%s' "$rl" > "$rlf"   # 빈 문자열 → 빈 파일(reflog GC), trailing newline 없이
  local args=(--toplevel "$toplevel" --worktree-list-file "$wlf" --reflog-file "$rlf" --branch "$branch")
  [ -n "$verdict" ] && args+=(--subagent-verdict "$verdict")
  out=$(bash "$WRAPPER" "${args[@]}" 2>&1) || exit_code=$?
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

# mutant_misflag: (1) baseline — 원본 GREEN 3-tuple → 토큰 ABSENT 확증(GREEN verified, non-vacuous).
#   (2) invert-predicate anchor 무력화(substring-fallback 무관) → (3) GREEN 오분류(토큰 PRESENT) = tuple 판정 load-bearing.
mutant_misflag() {
  local name="$1" anchor="$2" replacement="$3"
  local exit_code=0 base_exit=0 out base_out tmpdir mutant ok=1 apply_rc=0 wlf rlf
  tmpdir=$(mktemp -d)
  mutant="$(dirname "$SSOT_PY")/._wso_mutant_$$_${RANDOM}.py"
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'; rm -f '$mutant'" RETURN
  wlf="$tmpdir/wl.txt"; rlf="$tmpdir/rl.txt"
  printf '%s\n' "$WL_GREEN" > "$wlf"
  printf '%s' "$RL_GREEN" > "$rlf"

  base_out=$(bash "$WRAPPER" --toplevel "$TOP" --worktree-list-file "$wlf" --reflog-file "$rlf" --branch "$BRANCH" 2>&1) || base_exit=$?
  case "$base_out" in *"$TOKEN"*) ok=0;; esac
  if [ "$ok" -eq 0 ]; then
    echo "X FAIL: $name — baseline GREEN 이 이미 토큰 방출(무의미 MK / 경로 정규화 의심)"; echo "  baseline: $base_out"; FAIL=$((FAIL+1)); return
  fi

  python3 - "$SSOT_PY" "$mutant" "$anchor" "$replacement" <<'PY' || apply_rc=$?
import sys
src, out, anchor, repl = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(src, encoding="utf-8").read()
if anchor not in s:
    sys.stderr.write("ANCHOR-DRIFT: %r 부재\n" % (anchor,)); sys.exit(3)
open(out, "w", encoding="utf-8").write(s.replace(anchor, repl, 1))
PY
  if [ "$apply_rc" -ne 0 ]; then
    echo "X FAIL: $name — mutation anchor drift ('$anchor' 부재) → reconcile against real .py"; FAIL=$((FAIL+1)); return
  fi
  out=$(python3 "$mutant" --toplevel "$TOP" --worktree-list-file "$wlf" --reflog-file "$rlf" --branch "$BRANCH" 2>&1) || exit_code=$?
  case "$out" in *"$TOKEN"*) : ;; *) ok=0;; esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (baseline GREEN→no-token / mutant GREEN 오분류 방출 exit $exit_code — tuple 판정 load-bearing, killed)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name — mutant 가 GREEN 을 여전히 verified 처리(토큰 부재) = anchor 무력화 실패"; echo "  mutant output: $out"; FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2761: worktree-self-ownership-verify — 3-tuple self-test (§8.4, 유형#4)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── RED (tuple mismatch → 검출) ──"
run_wt "RED (a) toplevel↔worktree-list path mismatch" YES "Z:/wt/UNLISTED-path" "$BRANCH" "$WL_GREEN" "$RL_GREEN"
run_wt "RED (b) branch↔reflog membership mismatch" YES "$TOP" "$BRANCH" "$WL_GREEN" \
"9999999 HEAD@{0}: checkout: moving from main to some-other-branch"
# (c) clean isolation: branch 'orphan-feature'(경로 substring 아님) 이 worktree-list 부재하나 reflog 존재
#   → wl_has_branch False, reflog_has_branch True → tuple(c) 단독 mismatch (tuple b 미발동).
run_wt "RED (c) branch↔worktree-list mismatch (clean)" YES "$TOP" "orphan-feature" "$WL_GREEN" \
"abc1234 HEAD@{0}: checkout: moving from main to orphan-feature"

echo
echo "── GREEN (verified / GC fallback / benign verdict → 미검출) ──"
run_wt "GREEN 3-tuple verified" NO "$TOP" "$BRANCH" "$WL_GREEN" "$RL_GREEN"
run_wt "GREEN reflog-GC fallback (empty reflog + a+c)" NO "$TOP" "$BRANCH" "$WL_GREEN" ""
run_wt "GREEN benign subagent-verdict" NO "$TOP" "$BRANCH" "$WL_GREEN" "$RL_GREEN" "ok"

echo
echo "── subagent re-verify (§결정1-E parallel_session_conflict 오판 → 재verify 노트) ──"
run_wt "RE-VERIFY subagent parallel_session_conflict" YES "$TOP" "$BRANCH" "$WL_GREEN" "$RL_GREEN" "parallel_session_conflict"

echo
echo "── Mutation-kill (tuple 판정 branch isolation 증명, baseline GREEN pre-check) ──"
# MK-1: tuple(a) path-match invert → GREEN 경로가 '불일치' 처리되어 오분류.
mutant_misflag "MK-1 tuple(a) path-match invert → GREEN 오분류" \
"norm_top in wt_paths" "norm_top not in wt_paths"
# MK-2: tuple(b) reflog-lineage invert → GREEN reflog membership 이 '부재' 처리되어 오분류.
mutant_misflag "MK-2 tuple(b) reflog-lineage invert → GREEN 오분류" \
"branch in reflog_content" "branch not in reflog_content"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — 3-tuple(a/b/c) RED/GREEN/GC-fallback/re-verify/mutation-kill(baseline) 결박"; exit 0
else
  echo "X $FAIL case(s) failed"; exit 1
fi
