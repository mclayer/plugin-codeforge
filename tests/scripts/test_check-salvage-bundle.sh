#!/usr/bin/env bash
# tests/scripts/test_check-salvage-bundle.sh
# CFP-2984 Phase 2 (구현 lane) — AC-1 / AC-2 / AC-4 discriminating self-test.
#
# ★ 명명 테스트 심볼 (Change Plan §8.1 RTM): test_check_salvage_bundle
#   (파일명은 하이픈, RTM 식별자는 언더스코어. Hop3 는 Python `ast` 심볼만 보므로
#    심볼 제공 pytest 모듈은 별 파일이 담당하고 본 파일은 실 self-test 본체다.)
#
# SUT = scripts/check-salvage-bundle.sh → scripts/lib/check_salvage_bundle.py
# 검사 대상 명제:
#   AC-1  빈 번들은 `empty_reason` ∧ `failed_at` **둘 다** 필수. 하나라도 제거 = RED.
#   AC-2  각 조각은 `usable`|`suspect` 중 **정확히 하나**. 미태깅·값공간 밖 = fail-closed.
#   AC-4  저장 실패 시 실패 사실 + 회수 불가 범위 기록 ∧ 종료코드 ≠ 0. exit 0/1/2 3분기.
#   INV-T5 부분 기록(truncated) 번들은 유효 번들로 판독되지 않는다.
#
# ★ hollow 아님의 근거 (§8.2-E INV-T4):
#   ① clean-input 대조군(정본 입력 → rc=0) 을 전 AC 에 배치 — "무조건 RED" 구현은 여기서 죽는다.
#   ② 각 AC 마다 ①제거 ②주입 ③등가변형 3방향 mutant 를 **실제 적용**하고, 매 mutant 마다
#      **baseline 을 그 자리에서 재실행**해 대조한다. baseline 이 이미 어긋나면 kill 주장 불성립.
#   ③ mutation 앵커가 소스에서 사라지면 ANCHOR-DRIFT 로 **크게 RED** — 조용한 skip 금지.
#
# INV-T3 순수 픽스처: 네트워크 0 · 실 `~/.claude/**` 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-salvage-bundle.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_salvage_bundle.py"
FIX="$REPO_ROOT/tests/fixtures/cfp2984/salvage"

PASS=0
FAIL=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ─────────────────────────────────────────────────────────────────────────────
# ★ crash-as-RED 차단 (CFP-2984 G7 감사 — 실사건 회귀 방지)
#   오라클·변이체가 예외로 죽어서 난 rc≠0 은 **검출이 아니다**. 크래시를 RED(=kill) 로 세면
#   mutant 원장 전체가 거짓이 된다("GREEN 아래 결함 생존" 의 거울상).
#   ★ 실사건: AC-11b 오라클에 무효 정규식이 들어가 전 케이스가 크래시했는데 mutant 7종이
#     전부 "RED"= killed 로 계상될 뻔했다.
#   ★ 본 파일의 mutant 는 **SUT 소스를 치환해 만든 변이체**다. 치환이 소스를 깨뜨리면
#     mutant 는 detection 이 아니라 SyntaxError/re.error 로 rc=1 을 낸다 — want_mutant=1 인
#     행은 그것을 그대로 "KILLED" 로 계상한다. 그래서 mutant 측 검사가 필수다.
#   ★ SyntaxError·IndentationError 는 **Traceback 머리글 없이** 출력된다(실측: 컴파일 오류
#     stderr 에 'Traceback' 부재) — Traceback 단독 grep 으로는 못 잡는다.
# ─────────────────────────────────────────────────────────────────────────────
crash_marker() { # <output> → 0 = 크래시 흔적 있음
  case "$1" in
    *Traceback*|*SyntaxError*|*IndentationError*|*TabError*) return 0 ;;
  esac
  return 1
}

# fail_crash <label> <where> <output> — 크래시를 판정으로 접지 않고 크게 실패시킨다.
fail_crash() {
  echo "X FAIL: $1 — $2 크래시(오라클 예외). rc≠0 을 검출로 셀 수 없다"
  printf '%s\n' "$3" | sed 's/^/    ! /'
  FAIL=$((FAIL + 1))
}

# ─────────────────────────────────────────────────────────────────────────────
# assert_rc: SUT 를 실 실행해 종료코드를 **수치로** 대조 (문면 자칭 금지).
# ─────────────────────────────────────────────────────────────────────────────
assert_rc() {
  local name="$1" want="$2"
  shift 2
  local out rc=0
  out=$(bash "$WRAPPER" "$@" 2>&1) || rc=$?
  if crash_marker "$out"; then fail_crash "$name" "SUT" "$out"; return; fi
  if [ "$rc" -eq "$want" ]; then
    echo "OK PASS: $name (rc=$rc)"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $name — want rc=$want got rc=$rc"
    printf '%s\n' "$out" | sed 's/^/    /'
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local name="$1" needle="$2"
  shift 2
  local out rc=0
  out=$(bash "$WRAPPER" "$@" 2>&1) || rc=$?
  if crash_marker "$out"; then fail_crash "$name" "SUT" "$out"; return; fi
  case "$out" in
    *"$needle"*)
      echo "OK PASS: $name (기록 존재: $needle)"
      PASS=$((PASS + 1))
      ;;
    *)
      echo "X FAIL: $name — 출력에 '$needle' 부재 (rc=$rc)"
      printf '%s\n' "$out" | sed 's/^/    /'
      FAIL=$((FAIL + 1))
      ;;
  esac
}

# mutation 적용 — 앵커가 정확히 1회 등장할 때만 성공(0). 그 외 exit 3 = ANCHOR-DRIFT.
make_mutant() {
  python3 - "$SSOT_PY" "$1" "$2" "$3" <<'PY'
import sys
src, out, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(src, encoding="utf-8").read()
n = s.count(old)
if n != 1:
    sys.stderr.write("ANCHOR-DRIFT n=%d old=%r\n" % (n, old))
    sys.exit(3)
open(out, "w", encoding="utf-8", newline="\n").write(s.replace(old, new, 1))
PY
}

# ─────────────────────────────────────────────────────────────────────────────
# assert_kill_rc: baseline(정본) 과 mutant 를 **같은 입력**으로 각각 실행해 rc 를 대조.
#   killed ⟺ baseline rc == want_baseline ∧ mutant rc == want_mutant.
#   baseline 이 want 와 다르면 kill 주장 자체가 성립하지 않는다(INV-T4).
# ─────────────────────────────────────────────────────────────────────────────
assert_kill_rc() {
  local label="$1" old="$2" new="$3" wb="$4" wm="$5"
  shift 5
  local m="$TMP/mutant_$((RANDOM)).py" brc=0 mrc=0 bout mout
  if ! make_mutant "$m" "$old" "$new" 2>"$TMP/anchor.err"; then
    echo "X FAIL: $label — ANCHOR-DRIFT: $(cat "$TMP/anchor.err")"
    FAIL=$((FAIL + 1))
    return
  fi
  bout=$(bash "$WRAPPER" "$@" 2>&1) || brc=$?
  mout=$(python3 "$m" "$@" 2>&1) || mrc=$?
  if crash_marker "$bout"; then fail_crash "$label" "baseline(대조군 무효 — INV-T4)" "$bout"; return; fi
  if crash_marker "$mout"; then fail_crash "$label" "mutant(치환이 소스를 깨뜨림 = 거짓 kill)" "$mout"; return; fi
  if [ "$brc" -eq "$wb" ] && [ "$mrc" -eq "$wm" ]; then
    echo "OK KILLED: $label (baseline rc=$brc → mutant rc=$mrc)"
    PASS=$((PASS + 1))
  else
    echo "X SURVIVED: $label — baseline rc=$brc(want $wb) mutant rc=$mrc(want $wm)"
    echo "    ⇒ 해당 AC 는 advisory 강등 대상 (Story :649)"
    printf '%s\n' "$bout" | sed 's/^/    B| /'
    printf '%s\n' "$mout" | sed 's/^/    M| /'
    FAIL=$((FAIL + 1))
  fi
}

# assert_kill_absent: baseline 출력에는 needle 이 있고 mutant 출력에는 없어야 killed.
assert_kill_absent() {
  local label="$1" old="$2" new="$3" needle="$4"
  shift 4
  local m="$TMP/mutant_$((RANDOM)).py" bout mout bhit=0 mhit=0
  if ! make_mutant "$m" "$old" "$new" 2>"$TMP/anchor.err"; then
    echo "X FAIL: $label — ANCHOR-DRIFT: $(cat "$TMP/anchor.err")"
    FAIL=$((FAIL + 1))
    return
  fi
  bout=$(bash "$WRAPPER" "$@" 2>&1) || true
  mout=$(python3 "$m" "$@" 2>&1) || true
  if crash_marker "$bout"; then fail_crash "$label" "baseline(대조군 무효 — INV-T4)" "$bout"; return; fi
  # ★ 크래시한 mutant 는 needle 을 못 내므로 '기록 無' = killed 로 오독된다. 여기서 끊는다.
  if crash_marker "$mout"; then fail_crash "$label" "mutant(치환이 소스를 깨뜨림 = 거짓 kill)" "$mout"; return; fi
  case "$bout" in *"$needle"*) bhit=1 ;; esac
  case "$mout" in *"$needle"*) mhit=1 ;; esac
  if [ "$bhit" -eq 1 ] && [ "$mhit" -eq 0 ]; then
    echo "OK KILLED: $label (baseline 기록 有 → mutant 기록 無: $needle)"
    PASS=$((PASS + 1))
  else
    echo "X SURVIVED: $label — baseline hit=$bhit(want 1) mutant hit=$mhit(want 0) needle=$needle"
    echo "    ⇒ 해당 AC 는 advisory 강등 대상 (Story :649)"
    FAIL=$((FAIL + 1))
  fi
}

echo "══ 1. clean-input 대조군 (정본 입력 → 0-finding ∧ 정상 완료) ══"
assert_rc "대조군 정본 번들(조각 2)"            0 --validate --bundle "$FIX/bundle-valid.json"
assert_rc "대조군 조각 1건 (collection size)"    0 --validate --bundle "$FIX/bundle-one-fragment.json"
assert_rc "대조군 조각 N=5 (collection size)"    0 --validate --bundle "$FIX/bundle-many-fragments.json"
assert_rc "대조군 빈 번들(조각 0) + 2필드 보유"  0 --validate --bundle "$FIX/bundle-empty-valid.json"
assert_rc "대조군 태그 대소문자·공백 등가변형"   0 --validate --bundle "$FIX/bundle-tag-case-variant.json"
assert_rc "대조군 시각 소수초 등가변형"          0 --validate --bundle "$FIX/bundle-fractional-ts.json"

echo "══ 2. AC-1 — 빈 번들 2필드 조건부 required ══"
assert_rc "AC-1 빈 번들 empty_reason 결손"       1 --validate --bundle "$FIX/bundle-empty-missing-reason.json"
assert_rc "AC-1 빈 번들 failed_at 결손"          1 --validate --bundle "$FIX/bundle-empty-missing-failed-at.json"
assert_rc "AC-1 3요소 중 재개점 결손"            1 --validate --bundle "$FIX/bundle-missing-resume-point.json"
assert_rc "AC-1 재개점 동의 키명 개명"           1 --validate --bundle "$FIX/bundle-renamed-key.json"

echo "══ 3. AC-2 — 조각 태깅 fail-closed ══"
assert_rc "AC-2 미태깅 조각 1건 혼입"            1 --validate --bundle "$FIX/bundle-untagged-fragment.json"
assert_rc "AC-2 태그 빈 문자열"                  1 --validate --bundle "$FIX/bundle-tag-empty.json"
assert_rc "AC-2 태그 unknown(값공간 밖)"         1 --validate --bundle "$FIX/bundle-tag-unknown.json"

echo "══ 4. INV-T5 — 부분 기록 번들 ══"
assert_rc "INV-T5 truncated 번들"                1 --validate --bundle "$FIX/bundle-truncated.json"
assert_rc "입력 부재 = fail-closed"              1 --validate --bundle "$FIX/__absent__.json"

echo "══ 5. AC-4 — 종료 코드 0/1/2 3분기 + 저장 실패 경로 ══"
mkdir -p "$TMP/blocked-as-dir"
assert_rc "AC-4 usage: mode 인자 결손"           2 --validate
assert_rc "AC-4 usage: mode 미지정"              2 --bundle "$FIX/bundle-valid.json"
assert_rc "AC-4 저장 성공 → 0"                   0 --store --bundle "$FIX/bundle-valid.json" --out "$TMP/ok.json"
assert_rc "AC-4 저장 실패 → 성공 미보고(≠0)"     1 --store --bundle "$FIX/bundle-valid.json" --out "$TMP/blocked-as-dir"
assert_contains "AC-4 실패 사실 기록" "::salvage-incident::" \
  --store --bundle "$FIX/bundle-valid.json" --out "$TMP/blocked-as-dir"
assert_contains "AC-4 회수 불가 범위 기록" "unrecoverable_scope" \
  --store --bundle "$FIX/bundle-valid.json" --out "$TMP/blocked-as-dir"
if [ -s "$TMP/ok.json" ]; then
  echo "OK PASS: AC-4 저장 성공 시 산출 파일 실재"
  PASS=$((PASS + 1))
else
  echo "X FAIL: AC-4 저장 성공을 보고했는데 산출 파일이 없다"
  FAIL=$((FAIL + 1))
fi

echo "══ 6. 3방향 mutant — AC-1 ══"
assert_kill_rc "AC-1 ①제거 (빈 번들 required 열거 삭제)" \
  'REQUIRED_EMPTY = ("empty_reason", "failed_at")' \
  'REQUIRED_EMPTY = ()' \
  1 0 --validate --bundle "$FIX/bundle-empty-missing-reason.json"
assert_kill_rc "AC-1 ②주입 (3요소 required 검사 무력화)" \
  'for key in REQUIRED_NONEMPTY:' \
  'for key in ():' \
  1 0 --validate --bundle "$FIX/bundle-missing-resume-point.json"
assert_kill_rc "AC-1 ③등가변형·값 표현 (시각 소수초 표기 비정규화)" \
  '(?:\.\d{1,6})?' \
  '' \
  0 1 --validate --bundle "$FIX/bundle-fractional-ts.json"

echo "══ 7. 3방향 mutant — AC-2 ══"
assert_kill_rc "AC-2 ①제거 (미태깅 fail-closed 분기 삭제)" \
  'out.append("integrity_tag[%d]: 미태깅 조각 — fail-closed(suspect 취급)" % idx)' \
  'pass' \
  1 0 --validate --bundle "$FIX/bundle-untagged-fragment.json"
assert_kill_rc "AC-2 ②주입 (태그 값공간에 unknown 유입)" \
  'TAG_ENUM = ("usable", "suspect")' \
  'TAG_ENUM = ("usable", "suspect", "unknown", "")' \
  1 0 --validate --bundle "$FIX/bundle-tag-unknown.json"
assert_kill_rc "AC-2 ③등가변형·대소문자 공백 (enum 정규화 제거)" \
  'return value.strip().lower()' \
  'return value' \
  0 1 --validate --bundle "$FIX/bundle-tag-case-variant.json"

echo "══ 8. 3방향 mutant — AC-4 ══"
assert_kill_rc "AC-4 ①제거 (저장 실패가 성공을 보고)" \
  'STORE_FAILURE_EXIT = EXIT_VIOLATION' \
  'STORE_FAILURE_EXIT = EXIT_PASS' \
  1 0 --store --bundle "$FIX/bundle-valid.json" --out "$TMP/blocked-as-dir"
assert_kill_absent "AC-4 ②주입 (회수 불가 범위 기록 누락)" \
  '"unrecoverable_scope": {' \
  '"_dropped_scope": {' \
  'unrecoverable_scope' \
  --store --bundle "$FIX/bundle-valid.json" --out "$TMP/blocked-as-dir"
assert_kill_rc "AC-4 ③등가변형·값 표현 (usage 코드 2→1 접기)" \
  'EXIT_USAGE = 2' \
  'EXIT_USAGE = 1' \
  2 1 --validate

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
