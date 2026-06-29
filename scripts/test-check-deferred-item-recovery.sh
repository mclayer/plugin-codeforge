#!/usr/bin/env bash
# CFP-2470 Phase 2 — check-deferred-item-recovery.sh anti-theater 변별 test (10 TC)
#
# 검증 대상 = scripts/check-deferred-item-recovery.sh → Python SSOT
#   scripts/lib/check_deferred_item_recovery.py (DevPL 산출). Change Plan §8.1 의 10 TC 전수.
#
# anti-theater 원칙 (vacuous 거짓통과 금지):
#   - 각 TC = retro fixture 작성 → 스크립트 실행 → exit code + stdout/stderr 신호 동시 assert.
#   - dual-source AND 의 각 분기 (tracked/observed) 양방향 변별 (PASS↔WARN).
#   - cross-validate seam: GH_TOKEN 설정 + DIR_GH_BIN gh stub 주입 (Issue 존재/부재 simulate) —
#     graceful skip 에 의존하지 않고 실 판정 로직을 검사한다 (hollow-gate 회피).
#   - TC-4 만 GH_TOKEN 미설정으로 graceful skip(fail-safe) 변별.
#
# 대상 스크립트 부재 시 SKIP (DevPL 산출물 미 commit) — RED 정상.
#
# gh stub 주입 = DIR_GH_BIN env (production seam). 본 test 는 "<PY_EXE> <stub.py>" 형태로
#   주입 — Windows native python 이 subprocess 로 'gh'/'bash' 호출 시 WSL relay 로 새는 문제 회피
#   (PY_EXE 절대경로). production 은 shlex.split 후 shell=False 로 호출.
#
# mutation kill mapping (본문 말미 출력):
#   - dual-source AND 의 OR→AND mutate → TC-3/TC-10 (observed) RED.
#   - _issue_exists() cross-validate 제거 mutate → TC-6 RED.
#   - tracked/observed 두 분기 collapse mutate → TC-9 또는 TC-10 RED.
#   - enum closed-set 검증 제거 → TC-8 RED.
#   - tracking-column theater 검출 제거 → TC-1 RED.
#
# Exit code: 0 (all pass) / 1 (any fail)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/scripts/check-deferred-item-recovery.sh"
PYTHON_SSOT="$REPO_ROOT/scripts/lib/check_deferred_item_recovery.py"

[ -f "$TARGET" ] && [ -f "$PYTHON_SSOT" ] || {
  echo "::warning::대상 스크립트 부재 (RED 정상 — DevPL 산출물 미 commit)."
  echo "Total: PASS=0 FAIL=0 (SKIPPED — target absent)"
  exit 0
}

PASS=0
FAIL=0

# production 이 쓰는 python 실행파일 절대경로 (cross-platform subprocess leak 회피).
PY_EXE="$(python3 -c 'import sys; print(sys.executable)' 2>/dev/null || echo python3)"

# ─── gh stub 생성 (Python — production 동일 interpreter 로 호출) ───────────────
# sys.argv = [<stub>, "issue", "view", "<N>", "--json", "number"].
# exists="yes" → exit 0 (Issue 존재) / "no" → exit 1 (Issue 부재).
make_gh_stub() {
  local stub_path="$1" exists="$2"
  cat > "$stub_path" <<STUB
import sys, json
if len(sys.argv) >= 3 and sys.argv[1] == "issue" and sys.argv[2] == "view":
    issue_num = sys.argv[3] if len(sys.argv) > 3 else "1"
    if "$exists" == "yes":
        print(json.dumps({"number": issue_num}))
        sys.exit(0)
    sys.exit(1)
sys.exit(0)
STUB
}

# ─── retro fixture 생성 (disp 공백이면 §deferred 섹션 부재 — TC-7) ─────────────
make_retro() {
  local path="$1" disp="$2" item="$3" track="$4" reason="$5" src="$6"
  cat > "$path" <<'RETRO'
# Retro 2026-06-30

## §4 다음에 할 일 (try)
- narrative 항목

RETRO
  [ -z "$disp" ] && return
  cat >> "$path" <<'RETRO'
## §deferred

| disposition | item | tracking | rationale | source |
|---|---|---|---|---|
RETRO
  printf '%s\n' "| $disp | $item | $track | $reason | $src |" >> "$path"
}

# ─── 공통 실행 + 2-축 assert (exit code + signal) ─────────────────────────────
# run_tc <name> <disp> <item> <track> <reason> <src> <gh:yes|no|absent> <want_exit> <want_signal> <gh_token>
#   gh=absent → DIR_GH_BIN 미주입. gh_token 빈값 → GH_TOKEN 미설정 (graceful skip 변별).
#   want_signal ∈ PASS | WARN | DONE | graceful.
run_tc() {
  local name="$1" disp="$2" item="$3" track="$4" reason="$5" src="$6"
  local gh="$7" want_exit="$8" want_signal="$9" gh_token="${10:-}"

  local tmp; tmp=$(mktemp -d)
  make_retro "$tmp/retro.md" "$disp" "$item" "$track" "$reason" "$src"

  local gh_bin_cmd=""
  if [ "$gh" != "absent" ]; then
    make_gh_stub "$tmp/gh_stub.py" "$gh"
    # PY_EXE 가 Windows native python 이면 stub 도 Windows 경로여야 한다 (MSYS /tmp/... 미인식).
    # cygpath 있으면 -w 변환, 없으면(순수 POSIX) 원경로 그대로.
    local stub_path="$tmp/gh_stub.py"
    if command -v cygpath >/dev/null 2>&1; then
      stub_path="$(cygpath -w "$tmp/gh_stub.py")"
    fi
    gh_bin_cmd="$PY_EXE $stub_path"
  fi

  local out code=0
  out=$(
    GH_TOKEN="$gh_token" \
    DIR_GH_BIN="$gh_bin_cmd" \
    bash "$TARGET" "$tmp/retro.md" 2>&1
  ) || code=$?

  if [ "$code" != "$want_exit" ]; then
    echo "✗ FAIL $name: exit $code != $want_exit"
    echo "    out: $(echo "$out" | tr '\n' '|')"
    FAIL=$((FAIL+1)); rm -rf "$tmp"; return 0
  fi

  local found=0
  case "$want_signal" in
    PASS)     echo "$out" | grep -q "\[deferred-item-recovery\] PASS:" && found=1 ;;
    WARN)     echo "$out" | grep -qE "(::warning::|WARN:)" && found=1 ;;
    DONE)     echo "$out" | grep -q "\[deferred-item-recovery\] DONE:" && found=1 ;;
    graceful) echo "$out" | grep -q "graceful" && found=1 ;;
  esac

  if [ "$found" -eq 1 ]; then
    echo "✓ PASS $name (exit $code, signal=$want_signal)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL $name: signal '$want_signal' 미검출"
    echo "    out: $(echo "$out" | tr '\n' '|')"
    FAIL=$((FAIL+1))
  fi
  rm -rf "$tmp"
}

echo "=========================================="
echo "CFP-2470 Phase 2 — deferred-item-recovery 변별 test (10 TC)"
echo "=========================================="

# TC-1 (선언만/theater): tracked, tracking 공백 + rationale 공백 → WARN.
#   gh stub "yes" 주입해도 tracking 공백이라 cross-validate 도달 전 theater 검출.
run_tc "TC-1 theater(tracked,tracking공백)→WARN" \
  "tracked" "deferred-A" "" "" "decision-required" "yes" 1 "WARN" "tok"

# TC-2 (실 backing tracked): tracked + #123, Issue 실존(stub yes) → PASS.
run_tc "TC-2 tracked+실Issue→PASS" \
  "tracked" "deferred-B" "#123" "" "tracking-established" "yes" 0 "PASS" "tok"

# TC-3 (사유만 observed): observed + rationale 텍스트 → PASS.
run_tc "TC-3 observed+rationale→PASS" \
  "observed" "deferred-C" "" "carrier PR 로 해소" "obviated" "yes" 0 "PASS" "tok"

# TC-4 (PAT skip): GH_TOKEN 미설정 → graceful skip (exit 0, ::warning graceful).
run_tc "TC-4 PAT부재→graceful-skip" \
  "tracked" "deferred-D" "#123" "" "pending" "absent" 0 "graceful" ""

# TC-5 (observed 사유 누락): observed, rationale 공백 → WARN (EC-3).
run_tc "TC-5 observed,사유공백→WARN" \
  "observed" "deferred-E" "" "" "" "yes" 1 "WARN" "tok"

# TC-6 (tracked 선언 but 실 Issue 없음): tracked + #99999, stub no → WARN (EC-4 cross-validate).
run_tc "TC-6 tracked+실Issue부재→WARN" \
  "tracked" "deferred-F" "#99999" "" "pending" "no" 1 "WARN" "tok"

# TC-7 (§deferred 섹션 부재): silent skip → DONE 신호, WARN 아님.
run_tc "TC-7 섹션부재→silent-skip(DONE)" \
  "" "" "" "" "" "yes" 0 "DONE" "tok"

# TC-8 (enum 미스): disposition=MAYBE → WARN (structured 위반).
run_tc "TC-8 enum미스(MAYBE)→WARN" \
  "MAYBE" "deferred-G" "#123" "x" "tbd" "yes" 1 "WARN" "tok"

# TC-9 (정상 keep-tracking, F1): tracked + #456 실존(stub yes), 추적 유지 → PASS.
#   F1 역매핑 회귀 방지 — tracked 분기가 observed 로 collapse 되면 RED.
run_tc "TC-9 tracked추적유지+실Issue→PASS(F1)" \
  "tracked" "keep-tracking" "#456" "" "ongoing" "yes" 0 "PASS" "tok"

# TC-10 (carrier-merge obviated, F1): observed, tracking 공백, rationale=merge-link → PASS.
#   F1 역매핑 회귀 방지 — observed 분기가 tracked 로 collapse 되면 RED.
run_tc "TC-10 observed+merge-link사유→PASS(F1)" \
  "observed" "carrier-merge" "" "carrier PR #789 merge 로 해소(merge-link)" "obviated" "yes" 0 "PASS" "tok"

echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All 10 TC GREEN (deferred-item-recovery 변별 검증)"
  echo ""
  echo "[mutation kill mapping]"
  echo "  TC-1  : theater 검출 (tracking-column presence)"
  echo "  TC-2  : dual-source AND (실 Issue cross-validate, positive)"
  echo "  TC-3  : observed 분기 (rationale-required)"
  echo "  TC-4  : graceful skip (PAT 부재 fail-safe)"
  echo "  TC-5  : observed rationale 누락 검출 (EC-3)"
  echo "  TC-6  : cross-validate 부재 검출 (_issue_exists negative, EC-4)"
  echo "  TC-7  : §deferred 섹션 검출 + silent skip (EC-1)"
  echo "  TC-8  : enum closed-set {tracked,observed} 강제"
  echo "  TC-9  : tracked 분기 비-collapse (F1 역매핑 회귀)"
  echo "  TC-10 : observed 분기 비-collapse (F1 역매핑 회귀)"
  exit 0
else
  echo "✗ Some TC failed"
  exit 1
fi
