#!/usr/bin/env bash
# tests/scripts/test_check-mid-flight-marker.sh
# CFP-2761 Phase 2 (구현 lane) — mid-flight artifact-level provenance marker stale-lint 의
#   5-유형 discriminating self-test (Change Plan §8.2 / §8.6 / §8.7, F2 mandate).
#
#   SSOT: scripts/lib/check_mid_flight_marker.py + thin wrapper scripts/check-mid-flight-marker.sh.
#   검출 신호 = STDOUT 상 `::warning::mid-flight-marker-stale:` 토큰 presence (warning-tier — exit code 아님).
#   GREEN = 토큰 부재. exit: 0=clean/warn/honest-noop, 2=parse/unknown fail-closed, 3=born-hollow.
#
#   ★ 스캔 계약(firsthand — check_mid_flight_marker.py, CFP-2761 F1+F4 narrowed scope):
#     (A) default 열거(--repo-root DIR, NO --files) = `git ls-files -- docs/stories archive/adr/ADR-RESERVATION.md`
#         (SCAN_SCOPE, tests/ defense-in-depth 배제). arbitrary root prose .md 미스캔 → F1 self-poison /
#         F4 `면제` flood 근절. (B) --files X 명시 = scope 무관 정확히 X 스캔(explicit bypass, UNCHANGED).
#     ⇒ per-유형 discriminating 케이스(run_case/mutant_case/fuzz/prop/perf)는 **--files 명시**로 tmpdir(비-git)
#       결정적 스캔(scope-invariant). FULLREPO-1/2 는 CI 기본 경로(default 열거) 회귀 가드 — tmpdir 를
#       git init + add 로 tracked 화해 docs/stories 배치 fixture 가 default 열거에 잡히게 한다.
#     타입5 예약행은 --files(또는 SCAN_SCOPE default)로 archive/adr/ADR-RESERVATION.md basename anchor 매칭.
#
# ★ F2 (generic umbrella 금지): 5유형(1 작업초안 / 2 lane N/A / 3 dispatch placeholder /
#   4 미머지 worktree[OUT-OF-SCOPE, test #3] / 5 untracked ADR reservation) 각 explicit named RED fixture +
#   유형별 mutation-kill(검출 branch isolation 증명, baseline pre-check 로 non-vacuous 강제).
#   MK-T3(placeholder-semantic)/MK-T5(reservation-anchor) = 필수.
#
# ★ honesty ceiling (§7.8 / ADR-151 §결정7): presence/discriminating/DoS-bounded 까지만 결박 —
#   marker presence ≠ 산출물 실제 확정여부 truth(E2 거짓-final 미검출, 정적 상한). presence ≠ truth.
#
# self-contained bash (tests/scripts 관례, bats 미사용 — ADR-060 Amд 22). Exit 0 = 전 케이스 PASS.
# house style = tests/scripts/test_check-resource-safety-claim-proof.sh (lint_case + mutant_case).

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-mid-flight-marker.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_mid_flight_marker.py"
TOKEN="::warning::mid-flight-marker-stale:"

PASS=0
FAIL=0

# Preflight: script-under-test 부재(병렬 authoring window) → honest-degrade DEFERRED(silent-green 아님) exit 0.
if [ ! -f "$WRAPPER" ] || [ ! -f "$SSOT_PY" ]; then
  echo "DEFERRED-NO-SCRIPT-UNDER-TEST: check-mid-flight-marker .sh/.py 부재 (병렬 authoring window)."
  echo "  → fixture cohort 저작 완료·ready. 착지 후 collection-phase 실행. (honest-degrade exit 0.)"
  exit 0
fi

kst_now()      { python3 -c 'import datetime; from datetime import timezone,timedelta; print(datetime.datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%S+09:00"))'; }
kst_days_ago() { python3 -c 'import datetime,sys; from datetime import timezone,timedelta; d=int(sys.argv[1]); print((datetime.datetime.now(timezone(timedelta(hours=9)))-timedelta(days=d)).strftime("%Y-%m-%dT%H:%M:%S+09:00"))' "$1"; }
NOW_KST="$(kst_now)"
TODAY="$(kst_days_ago 0 | cut -dT -f1)"

# run_case: fixture 를 tmpdir/relpath 배치 → --files 명시(relpath 비면 미명시=TC-EMPTY) → (exit, 토큰) 대조.
#   expect: YES / NO / NOEMPTY(토큰 부재 + honest 비-침묵 stdout). shift 5 후 나머지 = wrapper 추가 인자.
run_case() {
  local name="$1" exp_exit="$2" expect="$3" relpath="$4" content="$5"; shift 5
  local extra=("$@")
  local exit_code=0 out tmpdir ok=1
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  local files_arg=()
  if [ -n "$relpath" ]; then
    mkdir -p "$tmpdir/$(dirname "$relpath")"
    printf '%s\n' "$content" > "$tmpdir/$relpath"
    files_arg=(--files "$tmpdir/$relpath")
  fi
  out=$(bash "$WRAPPER" --repo-root "$tmpdir" ${files_arg[@]+"${files_arg[@]}"} ${extra[@]+"${extra[@]}"} 2>&1) || exit_code=$?
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

# mutant_case: (1) baseline — 원본으로 fixture --files 실행 → detect-signal PRESENT 확증(RED non-vacuous).
#   (2) SSOT .py 사본에서 유형-고유 real-code anchor 무력화(정확 1치환) → (3) mutant fixture --files 실행 →
#   detect-signal DISAPPEAR(=mutant killed). anchor 미적용 → HARD FAIL(reconcile). mutant = lib dir dotfile.
#   detect-signal($6, 기본 $TOKEN) = baseline present / mutant absent 대조 substring. MK-T5 는 유형5-고유
#   detail("stale reservation")로 지정 — branch-gate 무력화 시 ADR-RESERVATION 이 타입1/2/3 로 fall-through
#   하므로(§8 scan_file early-return, DevF3 firsthand) 전체 토큰이 아닌 유형5 detail 소실로 판정(robust).
mutant_case() {
  local name="$1" relpath="$2" content="$3" anchor="$4" replacement="$5" detail="${6:-$TOKEN}"
  local tmpdir mutant fixture ok=1 apply_rc=0 base_exit=0 mut_exit=0 base_out mut_out
  tmpdir=$(mktemp -d)
  mutant="$(dirname "$SSOT_PY")/._mfm_mutant_$$_${RANDOM}.py"
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'; rm -f '$mutant'" RETURN
  mkdir -p "$tmpdir/$(dirname "$relpath")"
  fixture="$tmpdir/$relpath"
  printf '%s\n' "$content" > "$fixture"

  # (1) baseline RED 확증 (detect-signal PRESENT).
  base_out=$(bash "$WRAPPER" --repo-root "$tmpdir" --files "$fixture" 2>&1) || base_exit=$?
  case "$base_out" in *"$detail"*) : ;; *) ok=0;; esac
  if [ "$ok" -eq 0 ]; then
    echo "X FAIL: $name — baseline RED 부재(detect-signal '$detail' pre-mutation 미검출 = vacuous MK)"
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

  # (3) mutant 실행 → detect-signal 소실 확증.
  mut_out=$(python3 "$mutant" --repo-root "$tmpdir" --files "$fixture" 2>&1) || mut_exit=$?
  case "$mut_out" in *"$detail"*) ok=0;; esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (baseline RED→'$detail' / mutant 소실 exit $mut_exit — detection branch load-bearing, killed)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name — mutant 여전히 검출('$detail' 잔존) = anchor 가 해당 유형 branch 를 무력화 못함"; echo "  mutant output: $mut_out"; FAIL=$((FAIL+1))
  fi
}

fuzz_case() {
  local name="$1" relpath="$2" content="$3"
  local exit_code=0 out tmpdir ok=1 fixture
  tmpdir=$(mktemp -d)
  # shellcheck disable=SC2064
  trap "rm -rf '$tmpdir'" RETURN
  mkdir -p "$tmpdir/$(dirname "$relpath")"; fixture="$tmpdir/$relpath"
  printf '%s\n' "$content" > "$fixture"
  out=$(bash "$WRAPPER" --repo-root "$tmpdir" --files "$fixture" 2>&1) || exit_code=$?
  case "$exit_code" in 0|2|3) : ;; *) ok=0;; esac
  case "$out" in *"Traceback (most recent call last)"*) ok=0;; esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (malformed 입력 graceful exit $exit_code, no crash)"; PASS=$((PASS+1))
  else
    echo "X FAIL: $name — malformed 입력에 crash/비-graceful (exit $exit_code)"; echo "  output: $out"; FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2761: mid-flight-marker-stale — 5-유형 discriminating self-test (§8.2/§8.6/§8.7)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── Positive RED (유형별 explicit named fixture → MUST 검출, 토큰 present) ──"

# TC-T1-RED (유형1 작업초안): mid-flight 마커 status=draft + stale kst.
run_case "TC-T1-RED 작업초안 draft+stale" 0 YES "docs/stories/draft1.md" \
"# 작업 초안
<!-- mid-flight: owner=alice|worktree=/wt/cfp-x; kst=2025-01-01T00:00:00+09:00; status=draft -->
본문 초안."

# TC-T2-RED (유형2 lane N/A): N/A-token(§N ... N/A heading) + status=final 마커 부재.
run_case "TC-T2-RED lane-N/A 미확정" 0 YES "docs/stories/lane_na.md" \
"# Story
## §7 change-plan N/A 면제
(status=final 마커 동반 없음 — 미확정 N/A 선언)"

# TC-T3-RED (유형3 dispatch placeholder): placeholder-token + verdict 미기록.
run_case "TC-T3-RED dispatch placeholder" 0 YES "docs/stories/placeholder.md" \
"# Story
## §9 리뷰
verdict: pending
<!-- dispatch: CodexReviewAgent pending -->"

# TC-T4 (유형4 미머지 worktree = OUT-OF-SCOPE): 본 PR-time check 은 유형4 미claim — worktree 경로만 언급하고
#   committed 마커/N-A/placeholder/reservation 이 없는 파일은 미검출(유형4 = test_check-worktree-self-ownership.sh 소관).
run_case "TC-T4 worktree 언급-only = 본 check 미claim(out-of-scope)" 0 NO "docs/notes/wt.md" \
"# 로컬 노트
로컬 worktree cfp-2761 에서 작업 중 (committed 마커/N-A/placeholder/reservation 없음 — 유형4 는 test #3 소관)"

# TC-T5-RED (유형5 ADR-RESERVATION md-table): status=reserved + stale reserved_at → 검출.
#   F3 재작성: 구 YAML amendments_reserved[] 경로(now vacuous) → markdown 표 파싱. reserved_at
#   2025-01-01(stale-days 기본 14 대비 명백 stale — threshold-safe) → `::warning::mid-flight-marker-stale:`.
run_case "TC-T5-RED reservation md-table stale(reserved)" 0 YES "archive/adr/ADR-RESERVATION.md" \
"| adr_number | epic | status | reserved_at |
|---|---|---|---|
| 55 | CFP-367 | reserved | 2025-01-01 |"

echo
echo "── GREEN false-positive control (status=final + fresh / promoted → 토큰 부재) ──"

run_case "TC-T1-GREEN 작업초안 final+fresh" 0 NO "docs/stories/draft1.md" \
"# 작업 초안
<!-- mid-flight: owner=alice|worktree=/wt/cfp-x; kst=$NOW_KST; status=final -->
확정 본문."

run_case "TC-T2-GREEN lane-N/A 확정(final)" 0 NO "docs/stories/lane_na.md" \
"# Story
## §7 change-plan N/A 면제
<!-- mid-flight: owner=alice; kst=$NOW_KST; status=final -->"

run_case "TC-T3-GREEN verdict 승격(final)" 0 NO "docs/stories/placeholder.md" \
"# Story
## §9 리뷰
verdict: PASS
<!-- mid-flight: owner=alice; kst=$NOW_KST; status=final -->"

run_case "TC-T4-GREEN worktree-note 미검출" 0 NO "docs/notes/wt2.md" \
"# 노트
fresh 노트, 마커/reservation 없음."

# TC-T5-GREEN: 같은 md-table 이나 status=active(non-reserved) → 미검출(status 필터 격리).
run_case "TC-T5-GREEN reservation md-table active(non-reserved)" 0 NO "archive/adr/ADR-RESERVATION.md" \
"| adr_number | epic | status | reserved_at |
|---|---|---|---|
| 55 | CFP-367 | active | 2025-01-01 |"

echo
echo "── 경계 (honest-degrade / fail-closed — silent-green 금지) ──"

# TC-EMPTY: 후보 파일 0(--files 미명시 + 비-git tmpdir) → exit 0 + honest no-op(비-침묵) + 토큰 부재.
run_case "TC-EMPTY 대상 0 파일 honest-noop" 0 NOEMPTY "" ""

# TC-UNKNOWN: 마커 status 토큰이 closed-set 밖(bogus) → fail-closed exit 2.
run_case "TC-UNKNOWN status=bogus fail-closed" 2 NO "docs/stories/bogus.md" \
"# Story
<!-- mid-flight: owner=x; kst=2025-01-01T00:00:00+09:00; status=bogus -->"

echo
echo "── FULLREPO default-scan scope 회귀 (F1 self-poison / F4 면제 flood — CI 기본 경로, git-init tmpdir) ──"

# FULLREPO 케이스는 explicit --files 우회 없이 CI 실경로(--repo-root DIR, NO --files)를 그대로 구동한다.
# default 열거는 `git ls-files -- SCAN_SCOPE` 이므로 tmpdir 를 git init + add 로 tracked 화해야 fixture 가
# 잡힌다. (F5(a) — F1 self-poisoning 이 escape 했던 그 경로를 회귀 가드로 못 박음.)

# FULLREPO-1 (F1 self-poison guard): default 열거는 docs/stories/** + ADR-RESERVATION 만 스캔하고 tests/**
#   를 배제한다. tests/scripts/decoy.sh 의 status=bogus 마커(스캔되면 TC-UNKNOWN exit 2 유발 — F1 이 자기
#   오염됐던 그 신호)가 scope 배제로 미스캔 → exit 0, 동시에 docs/stories/s1.md stale draft 는 정상 검출.
#   비-vacuous: decoy 를 --files 명시 스캔하면 exit 2(poison 진정성 확증) → default 의 exit 0 이 load-bearing.
fullrepo_1() {
  local t out exit_code=0 ok=1 poison_exit=0 decoy
  t=$(mktemp -d); trap "rm -rf '$t'" RETURN
  if ! git -C "$t" init -q 2>/dev/null; then
    echo "X FAIL: FULLREPO-1 — git init 실패(환경 git 부재)"; FAIL=$((FAIL+1)); return
  fi
  mkdir -p "$t/docs/stories" "$t/tests/scripts"
  decoy="$t/tests/scripts/decoy.sh"
  printf '%s\n' "# Story s1
<!-- mid-flight: owner=alice; kst=2025-01-01T00:00:00+09:00; status=draft -->
본문 초안." > "$t/docs/stories/s1.md"
  printf '%s\n' "#!/usr/bin/env bash
# decoy fixture — status=bogus 마커: 스캔되면 TC-UNKNOWN(exit 2) 유발
# <!-- mid-flight: owner=x; kst=2025-01-01T00:00:00+09:00; status=bogus -->
echo decoy" > "$decoy"
  git -C "$t" add -A >/dev/null 2>&1 || true

  # (a) 비-vacuous 사전 확증: decoy 를 --files 명시 스캔 → poison(TC-UNKNOWN exit 2)임을 증명.
  bash "$WRAPPER" --repo-root "$t" --files "$decoy" >/dev/null 2>&1 || poison_exit=$?
  [ "$poison_exit" -eq 2 ] || ok=0
  # (b) CI 기본 경로: default 열거(NO --files) → tests/ 배제로 poison 미스캔 → exit 0 + docs/stories 검출.
  out=$(bash "$WRAPPER" --repo-root "$t" 2>&1) || exit_code=$?
  [ "$exit_code" -eq 0 ] || ok=0
  case "$out" in *"$TOKEN"*) : ;; *) ok=0;; esac
  case "$out" in *"TC-UNKNOWN"*) ok=0;; esac
  case "$out" in *"docs/stories/s1.md"*) : ;; *) ok=0;; esac

  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: FULLREPO-1 (F1 self-poison guard — decoy poison exit=$poison_exit / default 열거 tests/ 배제 exit $exit_code, docs/stories 검출, TC-UNKNOWN 부재)"; PASS=$((PASS+1))
  else
    echo "X FAIL: FULLREPO-1 — default-scan self-poison 또는 in-scope 미검출 (poison_exit=$poison_exit exit=$exit_code)"; echo "  output: $out"; FAIL=$((FAIL+1))
  fi
}
fullrepo_1

# FULLREPO-2 (F4 면제 flood guard): default 열거는 arbitrary root prose .md(notes.md)를 미스캔 → root 산문
#   `면제`(bare substring, heading/§N 컨텍스트 아님)는 flag 되지 않는다. 동시에 in-scope docs/stories/na.md
#   의 `## §7 change-plan 면제` heading(status=final 부재)은 정상 검출 → scope narrowing 이 실 검출을 안 깬다.
fullrepo_2() {
  local t out exit_code=0 ok=1
  t=$(mktemp -d); trap "rm -rf '$t'" RETURN
  if ! git -C "$t" init -q 2>/dev/null; then
    echo "X FAIL: FULLREPO-2 — git init 실패(환경 git 부재)"; FAIL=$((FAIL+1)); return
  fi
  mkdir -p "$t/docs/stories"
  printf '%s\n' "# 로컬 노트
이 조항은 면제 대상이 아니다 (산문 언급 — heading/§N 컨텍스트 아님)." > "$t/notes.md"
  printf '%s\n' "# Story na
## §7 change-plan 면제
(status=final 마커 부재 — 미확정 N/A 선언)" > "$t/docs/stories/na.md"
  git -C "$t" add -A >/dev/null 2>&1 || true

  out=$(bash "$WRAPPER" --repo-root "$t" 2>&1) || exit_code=$?
  [ "$exit_code" -eq 0 ] || ok=0
  case "$out" in *"$TOKEN"*) : ;; *) ok=0;; esac          # in-scope heading 면제 검출
  case "$out" in *"docs/stories/na.md"*) : ;; *) ok=0;; esac
  case "$out" in *"notes.md"*) ok=0;; esac                # root prose 면제 미flag(scope 배제 + non-heading)

  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: FULLREPO-2 (F4 면제 flood guard — root prose notes.md 미flag / docs/stories heading 검출 exit $exit_code)"; PASS=$((PASS+1))
  else
    echo "X FAIL: FULLREPO-2 — root prose flood 또는 in-scope 미검출 (exit $exit_code)"; echo "  output: $out"; FAIL=$((FAIL+1))
  fi
}
fullrepo_2

echo
echo "── Mutation-kill (유형별 검출 branch isolation 증명 — baseline RED pre-check, MK-T3/MK-T5 필수) ──"

# MK-T1 (유형1): STATUS_INPROGRESS 무력화 → draft stale 미검출.
mutant_case "MK-T1 STATUS_INPROGRESS 무력화 → 유형1 미검출" "docs/stories/mk1.md" \
"# 초안
<!-- mid-flight: owner=x; kst=2025-01-01T00:00:00+09:00; status=draft -->" \
'STATUS_INPROGRESS = ("draft", "provisional")' 'STATUS_INPROGRESS = ()'

# MK-T2 (유형2): N/A-token 검출 gate 무력화 → 면제 fixture 미검출.
mutant_case "MK-T2 N/A-token gate 무력화 → 유형2 미검출" "docs/stories/mk2.md" \
"# Story
## §7 설계 면제" \
'_has_na_token(lines) and not has_final' 'False and not has_final'

# MK-T3 (★필수): placeholder-token 검출 gate 무력화 → verdict:pending fixture 미검출.
mutant_case "MK-T3 placeholder gate 무력화 → 유형3 미검출 [필수]" "docs/stories/mk3.md" \
"# Story
verdict: pending" \
'if _has_placeholder_token(lines):' 'if False:  # MK-T3'

# MK-T5 (★필수): reservation branch gate(basename anchor) 무력화 → md-table reservation stale
#   fixture 미검출. 구 YAML-path MK-T5 대체 — md-table 경로가 load-bearing(non-vacuous)임을 증명.
#   anchor = scan_file() 유형5 branch gate. F3 landing 후 anchor 정합 reconcile 대상.
mutant_case "MK-T5 reservation branch 무력화 → 유형5 md-table 미검출 [필수]" "archive/adr/ADR-RESERVATION.md" \
"| adr_number | epic | status | reserved_at |
|---|---|---|---|
| 73 | CFP-9999 | reserved | 2025-01-01 |" \
'if os.path.basename(rel) == ADR_RESERVATION_BASENAME:' 'if False:  # MK-T5' \
"stale reservation"

echo
echo "── §8.7 property / enum (status closed-set + idempotency + age monotonicity) ──"

run_case "PROP-enum provisional 수용(fresh)" 0 NO "docs/stories/prov.md" \
"# Story
<!-- mid-flight: owner=x; kst=$NOW_KST; status=provisional -->"
run_case "PROP-enum final 수용(fresh)" 0 NO "docs/stories/fin.md" \
"# Story
<!-- mid-flight: owner=x; kst=$NOW_KST; status=final -->"

# PROP-idempotency: 동일 fixture 2회 실행 stdout 동일(정적 파싱 결정성).
prop_idem() {
  local t out1 out2 f
  t=$(mktemp -d); trap "rm -rf '$t'" RETURN
  mkdir -p "$t/docs/stories"; f="$t/docs/stories/idem.md"
  printf '%s\n' "# S
<!-- mid-flight: owner=x; kst=2025-01-01T00:00:00+09:00; status=draft -->" > "$f"
  out1=$(bash "$WRAPPER" --repo-root "$t" --files "$f" 2>&1 || true)
  out2=$(bash "$WRAPPER" --repo-root "$t" --files "$f" 2>&1 || true)
  if [ "$out1" = "$out2" ]; then
    echo "OK PASS: PROP-idempotency (2회 실행 stdout 동일 — 결정적 파싱)"; PASS=$((PASS+1))
  else
    echo "X FAIL: PROP-idempotency — 2회 실행 stdout 상이"; FAIL=$((FAIL+1))
  fi
}
prop_idem

# PROP-age BVA + monotonic: --stale-days 30 경계. within(29d)<30 미검출 / beyond(31d,60d)>30 검출(older ⇒ stale).
run_case "PROP-age BVA within(now-29d, <30d) 미검출" 0 NO "docs/stories/age_in.md" \
"# S
<!-- mid-flight: owner=x; kst=$(kst_days_ago 29); status=draft -->" --stale-days 30
run_case "PROP-age BVA beyond(now-31d, >30d) 검출" 0 YES "docs/stories/age_out.md" \
"# S
<!-- mid-flight: owner=x; kst=$(kst_days_ago 31); status=draft -->" --stale-days 30
run_case "PROP-age monotonic older(now-60d, >30d) 검출" 0 YES "docs/stories/age_old.md" \
"# S
<!-- mid-flight: owner=x; kst=$(kst_days_ago 60); status=draft -->" --stale-days 30

echo
echo "── §8.7 fuzz (malformed 마커 → crash 금지, graceful exit) ──"

fuzz_case "FUZZ-brokenkst 깨진 kst" "docs/stories/fz1.md" \
"# S
<!-- mid-flight: owner=x; kst=not-a-date; status=draft -->"
fuzz_case "FUZZ-truncated 잘린 comment" "docs/stories/fz2.md" \
"# S
<!-- mid-flight: owner=x; kst="
fuzz_case "FUZZ-random 무작위 라인" "docs/stories/fz3.md" \
"zzz \$\$\$ <!-- mid --> ;;; kst=== owner status=?? |||"

echo
echo "── §8.6 DoS 회귀 가드 (≈1.5MB corpus bounded-time — anchored regex/per-line cap) ──"

perf_tmp=$(mktemp -d)
mkdir -p "$perf_tmp/docs/stories"
python3 - "$perf_tmp/docs/stories/big.md" <<'PYEOF'
import sys
with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
    f.write("# big corpus\n")
    f.write(("padding line filler 0123456789 abcdef " * 40 + "\n") * 20000)  # ≈1.5MB
    f.write("<!-- mid-flight: owner=x; kst=2025-01-01T00:00:00+09:00; status=draft -->\n")
PYEOF
perf_wall=$(python3 - "$SSOT_PY" "$perf_tmp/docs/stories/big.md" "$perf_tmp" <<'PYEOF'
import subprocess, sys, time
py, bigfile, root = sys.argv[1], sys.argv[2], sys.argv[3]
t0 = time.perf_counter()
try:
    subprocess.run([sys.executable, py, "--repo-root", root, "--files", bigfile],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    print("%.3f" % (time.perf_counter() - t0))
except subprocess.TimeoutExpired:
    print("999.0")
PYEOF
)
rm -rf "$perf_tmp"
if awk "BEGIN{exit !($perf_wall < 10.0)}"; then
  echo "OK PASS: PERF-1.5MB corpus wall=${perf_wall}s (<10s — bounded regex/per-line cap, O(n²) 회귀 차단)"; PASS=$((PASS+1))
else
  echo "X FAIL: PERF-1.5MB corpus wall=${perf_wall}s (>=10s — length-cap 제거/O(n²) DoS 회귀 의심)"; FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — 5유형 discriminating/GREEN control/mutation-kill(baseline RED, T3·T5 필수)/property/fuzz/DoS-bound 결박"; exit 0
else
  echo "X $FAIL case(s) failed"; exit 1
fi
