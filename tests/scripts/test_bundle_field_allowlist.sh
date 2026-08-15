#!/usr/bin/env bash
# tests/scripts/test_bundle_field_allowlist.sh
# CFP-2984 Phase 2 (구현 lane) — AC-31 discriminating self-test.
#
# ★ 명명 테스트 심볼 (Change Plan §8.1 RTM): test_bundle_field_allowlist
#
# SUT = scripts/check-salvage-bundle.sh --validate
# 정본 앵커: **allowlist = `ADR-179 §결정 2-U` 닫힌 10 필드** / 값 형태 술어 = Story §7.12-G S-10.
#
# 2중 대조:
#   (a) 필드 집합 차집합 — `bundle_fields − allowlist` 가 공집합.
#   (b) 값 형태 분류 — 참조형 = **4 조건 AND** (①개행 0 ②길이 ≤512 ③공백 ≤1
#       ④닫힌 형태집합 완전일치: path[:line[-line]] / branch@<7~40hex> /
#       blob:sha256:<64hex> / <40hex> / #<digits>). 하나라도 불충족 = 원문형 = 위반.
#
# ★★ ③ `wip_summary` 는 술어 적용 **제외** (원문형 유일 예외).
#    근거 = ADR-179 §결정 2-U 닫힘 규칙 3 — "③ 에 대한 AC-31 의 기계 보장 = 0,
#    ③ 내용 통제는 AC-32 단독 위임". 이 예외를 반영하지 않으면 **거짓 RED** 다.
#    → 아래 "대조군: wip_summary 원문형" 케이스가 그 예외의 회귀 앵커다.
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
  if [ "$brc" -eq "$wb" ] && [ "$mrc" -eq "$wm" ]; then
    echo "OK KILLED: $label (baseline rc=$brc → mutant rc=$mrc)"
    PASS=$((PASS + 1))
  else
    echo "X SURVIVED: $label — baseline rc=$brc(want $wb) mutant rc=$mrc(want $wm)"
    echo "    ⇒ AC-31 advisory 강등 대상 (Story :649)"
    printf '%s\n' "$bout" | sed 's/^/    B| /'
    printf '%s\n' "$mout" | sed 's/^/    M| /'
    FAIL=$((FAIL + 1))
  fi
}

# allowlist 정본 앵커 무결성 — 10 필드(⑧ 은 2 키) = 11 키. 정본이 흔들리면 크게 RED.
echo "══ 0. allowlist 정본 앵커 (ADR-179 §결정 2-U) ══"
# ★ MSYS 경로 함정: `python3 -c "<code>"` 문자열 **안**의 경로는 MSYS→Windows 변환을 받지
#   않는다(`/c/...` 그대로 전달돼 import 실패). cd 후 상대 import 로 회피한다.
ALLOW_N=$(cd "$REPO_ROOT/scripts/lib" && python3 -c "import check_salvage_bundle as m; print(len(m.ALLOWLIST_FIELDS))")
if [ "$ALLOW_N" -eq 11 ]; then
  echo "OK PASS: allowlist 키 수 = 11 (닫힌 10 필드, ⑧ = empty_reason + failed_at 2 키)"
  PASS=$((PASS + 1))
else
  echo "X FAIL: allowlist 키 수 = $ALLOW_N — ADR-179 §결정 2-U 와 불일치 (확장 = amendment 의무)"
  FAIL=$((FAIL + 1))
fi

echo "══ 1. clean-input 대조군 ══"
assert_rc "대조군 정본 번들 (전건 참조형)"      0 --validate --bundle "$FIX/bundle-valid.json"
assert_rc "★대조군 wip_summary 원문형 → GREEN" 0 --validate --bundle "$FIX/bundle-wip-prose.json"
assert_rc "대조군 SHA 대문자 hex 등가변형"      0 --validate --bundle "$FIX/bundle-uppercase-sha.json"
assert_rc "대조군 blob 참조 대문자 hex 등가변형" 0 --validate --bundle "$FIX/bundle-uppercase-blobref.json"

echo "══ 2. (a) 필드 집합 차집합 ══"
assert_rc "allowlist 밖 필드 1건 추가"          1 --validate --bundle "$FIX/bundle-extra-field.json"
assert_rc "allowlist 안 필드를 동의 키명 개명"  1 --validate --bundle "$FIX/bundle-renamed-key.json"

echo "══ 3. (b) 값 형태 분류 — 4 조건 개별 반증 ══"
assert_rc "① 개행 삽입 (unfinished 원소)"       1 --validate --bundle "$FIX/bundle-newline-in-unfinished.json"
assert_rc "①+③ 참조형 필드 값에 diff 원문 투입" 1 --validate --bundle "$FIX/bundle-raw-in-ref.json"
assert_rc "② 길이 초과 (>512)"                  1 --validate --bundle "$FIX/bundle-overlong-ref.json"
assert_rc "④ 닫힌 형태집합 밖 (구문상 비참조)"  1 --validate --bundle "$FIX/bundle-prose-in-ref.json"

echo "══ 4. 3방향 mutant — AC-31 ══"
assert_kill_rc "AC-31 ①제거 (allowlist 차집합 대조 삭제)" \
  'unknown = sorted(set(bundle) - set(ALLOWLIST_FIELDS))' \
  'unknown = []' \
  1 0 --validate --bundle "$FIX/bundle-extra-field.json"
assert_kill_rc "AC-31 ②주입·구조→산문 (값 형태 분류기 삭제 → 값에 원문 은닉)" \
  'if not is_reference_form(obj[key]):' \
  'if False:' \
  1 0 --validate --bundle "$FIX/bundle-raw-in-ref.json"
# ★ 실측 발견 (숨기지 않는다 — 오라클 자문의 정직 기록):
#   `<40hex>` 형태에 대한 대소문자 mutant 는 **SURVIVED** 했다. 근인 = S-10 ④ 형태집합의
#   `path[:line[-line]]` 형태(`[^\s:]+`)가 **콜론 없는 bare 토큰 전부를 포섭**하므로
#   `<40hex>`·`branch@<hex>`·`#<digits>` 는 실질적으로 잉여 항이다. 즉 bare 토큰에 대해
#   실 검출력을 내는 것은 ①개행·②길이·③공백 3 조건이고 ④ 는 **콜론을 포함한 값**에서만 문다.
#   → 비-discriminating mutant 를 kill 로 계상하지 않고, ④ 가 실제로 무는 축
#     (`blob:sha256:` 형태)으로 대체한다. 위 subsumption 사실은 보고에 declare 한다.
assert_kill_rc "AC-31 ③등가변형·대소문자 (blob 참조 hex 대문자 수용 제거)" \
  're.compile(r"blob:sha256:[0-9a-fA-F]{64}"),' \
  're.compile(r"blob:sha256:[0-9a-f]{64}"),' \
  0 1 --validate --bundle "$FIX/bundle-uppercase-blobref.json"
assert_kill_rc "AC-31 ④추가 (④ 닫힌 형태집합 조건 무력화 → 산문 통과)" \
  'for rx in _REF_FORMS:' \
  'for rx in (re.compile(r"[^\n\r]*"),):' \
  1 0 --validate --bundle "$FIX/bundle-prose-in-ref.json"
# ★ ③ 예외의 회귀 앵커 — 술어를 wip_summary 에 무차별 적용하면 정본 번들이 거짓 RED 가 된다.
assert_kill_rc "AC-31 ⑤추가 (③ 예외 제거 → wip_summary 에 술어 무차별 적용 = 거짓 RED)" \
  'out.append("wip_summary: 비어있지 않은 문자열이어야 한다")' \
  'out.append("wip_summary: 비어있지 않은 문자열이어야 한다")
    if "wip_summary" in bundle and not is_reference_form(bundle.get("wip_summary")):
        out.append("wip_summary: 참조형 술어 위반")' \
  0 1 --validate --bundle "$FIX/bundle-wip-prose.json"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
