#!/usr/bin/env bash
# tests/scripts/test_retry_after_derivation.sh
# CFP-2984 Phase 2 (구현 lane) — AC-5a discriminating self-test.
#
# 대상 = 대기시간 산출 **순수 함수** + 헤더 픽스처 4종
#        (`Retry-After` 단독 / reset 단독 / 둘 다 / 둘 다 부재).
#
# 오라클 = 초 단위 대기는 `retry-after` 가 있을 때만 그 값에서 유도되고,
#          **reset 단독 픽스처는 헤더 유래 대기를 산출하지 않는다.**
#          reset 을 대기원으로 되돌린 변이체는 4종 중 최소 1종에서 RED.
#
# ★ 1차 출처 결속 (2차 추정 근거 불인정):
#   [source: https://platform.claude.com/docs/en/api/rate-limits]
#     - `anthropic-ratelimit-*-reset` = **RFC 3339 절대시각**
#     - `retry-after` = **초 단위 상대값**
#   [source: RFC 7231 §7.1.3] `Retry-After` = delta-seconds 또는 HTTP-date
#   ADR-109 §결정 2 (Amendment 3 정정) 가 위 두 출처를 empirical-source 로 고정한다.
#
# ★ AC-30 과 오라클 분리 (P2-3): 여기는 **계산**(함수 산출), AC-30 은 **문면**(문서가 무엇을 대기원으로
#   명명하는가). 두 검사는 서로의 정의역을 대신하지 않는다.
#
# ★ BVA (경계값): `0` / `1` / `-5` / `86400`.
#   `0` 은 "즉시 재시도"(source=retry-after, wait=0)이며 "값 부재"(source=none)와 **구분돼야** 한다 —
#   두 상태를 같은 결과로 접으면 `if not wait:` 류 구현이 조용히 부재로 오분류한다.
#
# ★ 산출물 위치: 판정 함수는 **테스트 내부 순수 함수**다 (신규 production 스크립트 신설 0 —
#   AC-12b 대상 실측이 1본으로 고정돼 있다).
#
# self-contained bash + 순수 픽스처 (INV-T3: 네트워크 0 · 실 ~/.claude 0 · 실 git 원격 0).
# Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

SUT="$WORK/wait_derivation.py"
cat > "$SUT" <<'PYSUT'
# -*- coding: utf-8 -*-
"""대기시간 산출 순수 함수 (SUT).

derive_wait(headers) -> (source, wait_seconds)
  source ∈ {"retry-after", "retry-after-invalid", "none"}
  wait_seconds = int | None   (None = 헤더 유래 대기 없음)

계약 (ADR-109 §결정 2 / Amendment 3 정정):
  - `retry-after` = 초 단위 상대값 → 그대로 대기시간으로 유도한다.
  - `anthropic-ratelimit-*-reset` = RFC 3339 절대시각 → **대기원이 아니다.**
    잔여 창 계산 정보로만 쓰며, 대기 산출 입력으로 삼지 않는다.
  - 헤더명 매칭은 **대소문자 무시**하고, 중복 헤더는 **첫 값**을 채택한다(등가 표기 정규화).
"""
import re

RE_RESET = re.compile(r"^anthropic-ratelimit-[a-z0-9_-]+-reset$")


def normalize(headers):
    """[(name, value)] → {lower_name: first_value}. 중복 헤더 = 첫 값 채택."""
    out = {}
    for name, value in headers:
        key = name.strip().lower()
        if key not in out:
            out[key] = value.strip()
    return out


def derive_wait(headers):
    h = normalize(headers)
    if "retry-after" in h:
        raw = h["retry-after"]
        if re.match(r"^\d+$", raw):
            return ("retry-after", int(raw))
        return ("retry-after-invalid", None)
    # reset 계열은 존재하더라도 헤더 유래 대기를 산출하지 않는다.
    for key in h:
        if RE_RESET.match(key):
            return ("none", None)
    return ("none", None)
PYSUT

RUNNER="$WORK/run_fixtures.py"
cat > "$RUNNER" <<'PYRUN'
# -*- coding: utf-8 -*-
"""픽스처 4종 + BVA 를 SUT 에 통과시켜 (source, wait) 를 출력한다."""
import importlib.util
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

spec = importlib.util.spec_from_file_location("sut", sys.argv[1])
sut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sut)

RESET_ABS = "2026-08-15T13:20:00Z"  # RFC 3339 절대시각 (초 단위 상대값 아님)

FIXTURES = [
    # (name, headers)
    ("F1-retry-after-only", [("Retry-After", "15")]),
    ("F2-reset-only", [("anthropic-ratelimit-requests-reset", RESET_ABS)]),
    ("F3-both", [("Retry-After", "15"), ("anthropic-ratelimit-tokens-reset", RESET_ABS)]),
    ("F4-neither", [("content-type", "application/json")]),
    # BVA
    ("B0-zero", [("Retry-After", "0")]),
    ("B1-one", [("Retry-After", "1")]),
    ("B2-negative", [("Retry-After", "-5")]),
    ("B3-large", [("Retry-After", "86400")]),
    # ③ 등가변형 (의미 보존 표기 변형): 헤더명 대소문자 + 중복 헤더
    ("E1-case-variant", [("RETRY-AFTER", "15")]),
    ("E2-duplicate", [("Retry-After", "15"), ("retry-after", "99")]),
    ("E3-reset-case-variant", [("Anthropic-RateLimit-Requests-Reset", RESET_ABS)]),
]

for name, headers in FIXTURES:
    source, wait = sut.derive_wait(headers)
    print("%s|%s|%s" % (name, source, "None" if wait is None else wait))
PYRUN

# expect: <fixture> <expected "source|wait">
expect() {
  local out="$1" name="$2" want="$3" label="$4"
  local line
  # ★ crash-as-RED / crash-as-diff 차단 — **2단 방어**이며 각 층의 담당 class 가 다르다.
  #   1차 `set -e`: 러너가 rc≠0 으로 죽으면 캡처 지점(`OUT=$(...)`)에서 스크립트가 즉시
  #      abort 하므로 이 함수는 호출조차 되지 않는다. 컴파일오류(SyntaxError /
  #      IndentationError — **Traceback 머리글이 없다**) class 가 여기서 걸린다.
  #   2차 아래 `*Traceback*` 가드: `set -e` 가 못 잡는 **rc=0 인데 stderr 로 크래시 흔적만
  #      뱉는** 잔여 class 전담. 이 층이 죽은 코드가 되지 않으려면 캡처에 `2>&1` 이 있어야
  #      한다 — 없으면 `$out` 이 stdout 전용이라 가드에 영원히 미도달한다(실측 확인함).
  #   크래시를 놓치면 grep 이 빈 줄을 내고 expect_not 이 "달라졌다" 며 통과해버린다.
  case "$out" in
    *Traceback*)
      echo "X FAIL: $label — 러너 크래시(Traceback). 산출 차이를 검출로 셀 수 없다"
      FAIL=$((FAIL + 1))
      return ;;
  esac
  line=$(printf '%s\n' "$out" | grep "^$name|" || true)
  if [ "$line" = "$name|$want" ]; then
    echo "OK PASS: $label ($line)"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $label"
    echo "  expected '$name|$want', got '$line'"
    FAIL=$((FAIL + 1))
  fi
}

# expect_not: 해당 픽스처 결과가 want 와 **달라야** 한다 (mutant kill 확인)
expect_not() {
  local out="$1" name="$2" forbidden="$3" label="$4"
  local line
  # ★ crash-as-RED / crash-as-diff 차단 — **2단 방어**이며 각 층의 담당 class 가 다르다.
  #   1차 `set -e`: 러너가 rc≠0 으로 죽으면 캡처 지점(`OUT=$(...)`)에서 스크립트가 즉시
  #      abort 하므로 이 함수는 호출조차 되지 않는다. 컴파일오류(SyntaxError /
  #      IndentationError — **Traceback 머리글이 없다**) class 가 여기서 걸린다.
  #   2차 아래 `*Traceback*` 가드: `set -e` 가 못 잡는 **rc=0 인데 stderr 로 크래시 흔적만
  #      뱉는** 잔여 class 전담. 이 층이 죽은 코드가 되지 않으려면 캡처에 `2>&1` 이 있어야
  #      한다 — 없으면 `$out` 이 stdout 전용이라 가드에 영원히 미도달한다(실측 확인함).
  #   크래시를 놓치면 grep 이 빈 줄을 내고 expect_not 이 "달라졌다" 며 통과해버린다.
  case "$out" in
    *Traceback*)
      echo "X FAIL: $label — 러너 크래시(Traceback). 산출 차이를 검출로 셀 수 없다"
      FAIL=$((FAIL + 1))
      return ;;
  esac
  line=$(printf '%s\n' "$out" | grep "^$name|" || true)
  if [ "$line" != "$name|$forbidden" ]; then
    echo "OK PASS: $label (got '$line')"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $label (mutant 가 정본과 동일 산출 — 검출력 0)"
    echo "  line: $line"
    FAIL=$((FAIL + 1))
  fi
}

mutate_sut() {
  local dest="$1" kind="$2"
  "$PY" - "$SUT" "$dest" "$kind" <<'PYMUT'
import io
import sys
src, dest, kind = sys.argv[1], sys.argv[2], sys.argv[3]
s = io.open(src, encoding="utf-8").read()
if kind == "no_derivation":
    # ① 제거: 대기 산출식 자체를 지운다 → retry-after 가 있어도 대기를 못 낸다.
    old = '            return ("retry-after", int(raw))'
    new = '            return ("none", None)'
elif kind == "reset_as_wait":
    # ② 주입: reset(절대시각)을 대기원으로 되돌린다 → reset 단독 픽스처가 대기를 산출.
    old = '        if RE_RESET.match(key):\n            return ("none", None)'
    new = '        if RE_RESET.match(key):\n            return ("retry-after", 3600)'
elif kind == "no_case_norm":
    # ③ 등가변형 저항 제거: 헤더명 정규화(대소문자)를 없앤다.
    old = '        key = name.strip().lower()'
    new = '        key = name.strip()'
elif kind == "zero_is_absent":
    # 경계 붕괴: `0` 을 "값 부재" 로 접는다 (`if not wait:` 류 구현).
    old = '        if re.match(r"^\\d+$", raw):\n            return ("retry-after", int(raw))'
    new = '        if re.match(r"^\\d+$", raw) and int(raw) > 0:\n            return ("retry-after", int(raw))\n        if raw == "0":\n            return ("none", None)'
else:
    raise SystemExit("unknown mutant kind %r" % kind)
assert s.count(old) == 1, ("mutant anchor count != 1", s.count(old), kind)
io.open(dest, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
PYMUT
}

echo "── AC-5a: Retry-After 대기 유도 (순수 함수 + 헤더 픽스처 4종 + BVA)"

# ── baseline (clean-input 대조군) ───────────────────────────────────────────
BASE_OUT=$("$PY" "$RUNNER" "$SUT" 2>&1)
expect "$BASE_OUT" "F1-retry-after-only" "retry-after|15" "TC-C1 F1 retry-after 단독 → 그 값에서 유도"
expect "$BASE_OUT" "F2-reset-only"       "none|None"      "TC-C2 F2 reset 단독 → 헤더 유래 대기 미산출 (★ keystone)"
expect "$BASE_OUT" "F3-both"             "retry-after|15" "TC-C3 F3 둘 다 → retry-after 가 대기원"
expect "$BASE_OUT" "F4-neither"          "none|None"      "TC-C4 F4 둘 다 부재 → 헤더 유래 대기 미산출"
expect "$BASE_OUT" "B0-zero"             "retry-after|0"  "TC-B0 BVA 0 = 즉시 재시도 (부재와 구분)"
expect "$BASE_OUT" "B1-one"              "retry-after|1"  "TC-B1 BVA 1"
expect "$BASE_OUT" "B2-negative"         "retry-after-invalid|None" "TC-B2 BVA -5 = 무효 (조용한 0 낙하 금지)"
expect "$BASE_OUT" "B3-large"            "retry-after|86400" "TC-B3 BVA 86400"
expect "$BASE_OUT" "E1-case-variant"     "retry-after|15" "TC-E1 ③등가변형 헤더명 대소문자 → 정규화 후 동일 산출"
expect "$BASE_OUT" "E2-duplicate"        "retry-after|15" "TC-E2 ③등가변형 중복 헤더 → 첫 값 채택"
expect "$BASE_OUT" "E3-reset-case-variant" "none|None"    "TC-E3 ③등가변형 reset 대소문자 → 여전히 대기원 아님"

# ── ① 제거 mutant ──────────────────────────────────────────────────────────
M1="$WORK/m1.py"; mutate_sut "$M1" "no_derivation"
M1_OUT=$("$PY" "$RUNNER" "$M1" 2>&1)
expect_not "$M1_OUT" "F1-retry-after-only" "retry-after|15" "TC-M1 ①제거 대기 산출식 삭제 → F1 RED"

# ── ② 주입 mutant (reset 을 대기원으로 되돌림) ─────────────────────────────
M2="$WORK/m2.py"; mutate_sut "$M2" "reset_as_wait"
M2_OUT=$("$PY" "$RUNNER" "$M2" 2>&1)
expect_not "$M2_OUT" "F2-reset-only" "none|None" "TC-M2 ②주입 reset 을 대기원으로 → F2 RED (4종 중 최소 1종)"
expect_not "$M2_OUT" "E3-reset-case-variant" "none|None" "TC-M2b ②주입 + 표기 변형 reset → E3 도 RED"
# 형제 회귀: 같은 mutant 아래에서도 F1/F3 은 여전히 정본과 동일 → 검출이 F2 축에서만 발생함을 확인
expect "$M2_OUT" "F1-retry-after-only" "retry-after|15" "TC-M2c 형제 회귀 — reset mutant 는 F1 산출을 바꾸지 않는다"

# ── ③ 등가변형 저항 제거 mutant ────────────────────────────────────────────
M3="$WORK/m3.py"; mutate_sut "$M3" "no_case_norm"
M3_OUT=$("$PY" "$RUNNER" "$M3" 2>&1)
expect_not "$M3_OUT" "E1-case-variant" "retry-after|15" "TC-M3 ③등가변형 헤더 정규화 제거 → E1 RED"

# ── 경계 붕괴 mutant (0 을 부재로 접음) ────────────────────────────────────
M4="$WORK/m4.py"; mutate_sut "$M4" "zero_is_absent"
M4_OUT=$("$PY" "$RUNNER" "$M4" 2>&1)
expect_not "$M4_OUT" "B0-zero" "retry-after|0" "TC-M4 경계 붕괴 0→부재 → B0 RED"
expect "$M4_OUT" "F1-retry-after-only" "retry-after|15" "TC-M4b 형제 회귀 — 경계 mutant 는 F1 산출을 바꾸지 않는다"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
