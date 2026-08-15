#!/usr/bin/env bash
# tests/scripts/test_salvage_side_effect_dedup.sh
# CFP-2984 Phase 2 (구현 lane) — AC-3 discriminating self-test (idempotency replay §8.5.3).
#
# ★ 명명 테스트 심볼 (Change Plan §8.1 RTM): test_salvage_side_effect_dedup
#
# SUT = scripts/check-salvage-bundle.sh --dedup (scripts/lib/check_salvage_bundle.py)
# 정본: ADR-179 §결정 4 (dedup 술어) / Change Plan §11.6 (intent_key) / §8.5.3 (K1~K5 · S1~S5)
#
# 검사 대상 명제 (AC-3):
#   중복 intent **만** 억제되고 **신규 intent 는 억제되지 않는다**.
#   중복 판정을 제거한 변이체와 **무조건 억제로 바꾼 변이체 둘 다** RED.
#
# ★★ S4 대조군이 비협상인 이유 (§8.5.3 — 본 Story 가 정확히 이 실패를 겨냥한다):
#   dedup 술어를 **무조건 true** 로 바꾼 mutant 는 ①제거만 RED 이고 ②주입·③등가변형은
#   전부 GREEN 으로 **생존**한다(억제가 기대값이므로). S4(서로 다른 intent 2건 → 둘 다 실행)
#   가 없으면 그 mutant 를 어떤 방향으로도 잡을 수 없다.
#
# K1 (verb,target,payload) / K2 canonical(사전순 JSON·NFC·후행공백 제거) /
# K3 휘발 필드 **명시 열거** 제외 / K4 sha256(canonical) / K5 **정확 일치만**.
#
# INV-T3 순수 픽스처: 네트워크 0 · 실 GitHub API 0 · 실 `~/.claude/**` 0 · 실 git 원격 0.
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

LEDGER="$FIX/ledger-applied.json"

# assert_summary: dedup 판정 요약(suppressed/executed 수치)을 **계산 결과로** 대조.
assert_summary() {
  local name="$1" intents="$2" want="$3"
  local out rc=0
  out=$(bash "$WRAPPER" --dedup --ledger "$LEDGER" --intents "$FIX/$intents" 2>&1) || rc=$?
  case "$out" in
    *"$want"*)
      echo "OK PASS: $name ($want)"
      PASS=$((PASS + 1))
      ;;
    *)
      echo "X FAIL: $name — want '$want' (rc=$rc)"
      printf '%s\n' "$out" | sed 's/^/    /'
      FAIL=$((FAIL + 1))
      ;;
  esac
}

assert_rc() {
  local name="$1" want="$2"
  shift 2
  local out rc=0
  out=$(bash "$WRAPPER" "$@" 2>&1) || rc=$?
  if [ "$rc" -eq "$want" ]; then
    echo "OK PASS: $name (rc=$rc)"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $name — want rc=$want got rc=$rc"
    printf '%s\n' "$out" | sed 's/^/    /'
    FAIL=$((FAIL + 1))
  fi
}

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

# assert_kill_summary: baseline 요약과 mutant 요약을 **같은 입력**으로 각각 실행해 대조.
#   killed ⟺ baseline 이 want_baseline 을 내고 mutant 는 내지 못한다(INV-T4 — baseline 필수).
assert_kill_summary() {
  local label="$1" old="$2" new="$3" intents="$4" want_baseline="$5"
  local m="$TMP/mutant_$((RANDOM)).py" bout mout bhit=0 mhit=0
  if ! make_mutant "$m" "$old" "$new" 2>"$TMP/anchor.err"; then
    echo "X FAIL: $label — ANCHOR-DRIFT: $(cat "$TMP/anchor.err")"
    FAIL=$((FAIL + 1))
    return
  fi
  bout=$(bash "$WRAPPER" --dedup --ledger "$LEDGER" --intents "$FIX/$intents" 2>&1) || true
  mout=$(python3 "$m" --dedup --ledger "$LEDGER" --intents "$FIX/$intents" 2>&1) || true
  case "$bout" in *"$want_baseline"*) bhit=1 ;; esac
  case "$mout" in *"$want_baseline"*) mhit=1 ;; esac
  if [ "$bhit" -eq 1 ] && [ "$mhit" -eq 0 ]; then
    echo "OK KILLED: $label (baseline '$want_baseline' → mutant 미산출)"
    PASS=$((PASS + 1))
  else
    echo "X SURVIVED: $label — baseline hit=$bhit(want 1) mutant hit=$mhit(want 0)"
    echo "    ⇒ AC-3 advisory 강등 대상 (Story :649)"
    printf '%s\n' "$bout" | sed 's/^/    B| /'
    printf '%s\n' "$mout" | sed 's/^/    M| /'
    FAIL=$((FAIL + 1))
  fi
}

echo "══ 1. replay 시나리오 S1~S5 (§8.5.3) ══"
assert_summary "S1 동일 intent 재요청 → 억제"          intents-s1-duplicate.json    "suppressed=1 executed=0"
assert_summary "S2 키 순서만 다른 등가 payload → 억제" intents-s2-key-order.json    "suppressed=1 executed=0"
assert_summary "S3 휘발 필드만 다름 → 억제"            intents-s3-volatile.json     "suppressed=1 executed=0"
assert_summary "S4 대조군: verb 동일·target 상이 2건 → 둘 다 실행" \
                                                       intents-s4-control.json      "suppressed=0 executed=2"
assert_rc "S5 원장 손상 → fail-closed" 1 --dedup --ledger "$FIX/ledger-corrupt.json" \
  --intents "$FIX/intents-s1-duplicate.json"
assert_rc "S5 원장 부재 → fail-closed" 1 --dedup --ledger "$FIX/__absent__.json" \
  --intents "$FIX/intents-s1-duplicate.json"
assert_rc "S5 원장 row 에 자유 텍스트 유입 → fail-closed" 1 \
  --dedup --ledger "$FIX/ledger-bad-row.json" --intents "$FIX/intents-s1-duplicate.json"

echo "══ 2. clean-input 대조군 + 경계 ══"
assert_summary "대조군 신규 intent 1건 → 실행"         intents-clean-new.json       "suppressed=0 executed=1"
assert_summary "status=intended 는 억제 대상 아님"     intents-intended-not-applied.json "suppressed=0 executed=1"
assert_rc "K3 휘발 열거 밖 미지 필드 → fail-closed" 1 \
  --dedup --ledger "$LEDGER" --intents "$FIX/intents-unknown-field.json"

echo "══ 3. 3방향 mutant — AC-3 ══"
assert_kill_summary "AC-3 ①제거 (dedup 술어 삭제)" \
  '        if key in applied:' \
  '        if False:' \
  intents-s1-duplicate.json "suppressed=1 executed=0"
# ★★ 이 mutant 는 S4 대조군에서만 죽는다. S1~S3 로는 어느 방향으로도 잡히지 않는다.
assert_kill_summary "AC-3 ②주입·의미변경 경계 (dedup 술어를 무조건 true 로 치환)" \
  '        if key in applied:' \
  '        if True:' \
  intents-s4-control.json "suppressed=0 executed=2"
assert_kill_summary "AC-3 ③등가변형·순서 재배열 (canonical sort_keys 제거)" \
  'return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)' \
  'return json.dumps(obj, sort_keys=False, separators=(",", ":"), ensure_ascii=False)' \
  intents-s2-key-order.json "suppressed=1 executed=0"
assert_kill_summary "AC-3 ④추가 (K3 휘발 필드 명시 열거 제외 무력화)" \
  'if k not in VOLATILE_KEYS}' \
  'if True}' \
  intents-s3-volatile.json "suppressed=1 executed=0"

# ★ K5(정확 일치만) 의 **부분 완화** mutant 는 기계 falsify 불가 — declare (숨기지 않는다).
#   `key[:8]` prefix 완화 mutant 를 실제 적용해봤으나 S1~S4 어느 픽스처도 RED 로 전환되지
#   않는다(SURVIVED 실측). 근인 = 그 mutant 를 발화시키려면 sha256 **선두 8 hex 가 일치하는
#   서로 다른 intent** 픽스처가 필요한데, 그것은 2^32 급 탐색이라 픽스처로 구성 불가하다.
#   ⇒ K5 에 대해 본 오라클이 실제로 강제하는 것은 "서로 다른 intent 는 억제되지 않는다"(S4)
#      까지이며, "prefix/유사도 완화가 도입되어도 잡는다" 는 **강제되지 않는다**.
#   전면 완화(무조건 억제)는 위 ②주입 mutant 가 S4 로 잡는다.

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
