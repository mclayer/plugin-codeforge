#!/usr/bin/env bash
# scripts/test-check-disjoint-axis-whitelist.sh
# CFP-2572 Phase 2 (원 도입 — 구 R1/R2/R3) / CFP-2869 Phase 2 (ADR-170 재제정 대응 재저작 — M1~M9)
# Discriminating test for check_disjoint_axis_whitelist.py (lint)
#
# Anti-theater test (ADR-119 검증-후-단언 / ADR-136 execution-liveness):
#   GREEN (real ADR-170 + real return-envelope-v1.md) 는 PASS,
#   surgical mutant fixture 는 각각 표적 check 만 RED 로 fire.
#   각 RED 는 required_sentinel(표적 violation) 등장 + forbidden_sentinel(off-target) 부재 검증.
#   tautology 가드: 모든 mutant 는 base GREEN(TC-M6) 과 **양방향** 대조된다 — base 가 이미
#   RED 면 TC-M6 이 먼저 FAIL 하므로 "항상 RED" 로 통과하는 위장 mutant 가 성립하지 않는다.
#
# Mutation 세트 (계약 SSOT = Story CFP-2869 §8.3):
#   M1: §결정 2 flat 표 마지막 row 뒤 out-of-band fake row `| 99 |` 주입 → declared≠actual → (C1) RED.
#   M2: 정형 선언 값 변조 ("= 7-entry" → "= 9-entry")                  → declared≠actual → (C1) RED.
#   M3: 정형 선언 라인 삭제                                             → 부재 fail-closed → (C1) RED.
#   M4: lint 대상 = Superseded 동결 구본(ADR-039)                       → 동결사체 가드   → (C0) RED.
#   M5: flat 표 row 1개 삭제                                            → declared≠actual → (C1) RED.
#   M6: negative control (무변조 정본)                                  → PASS 유지.
#   M7: LDOC "disjoint axis" 선언 제거                                  → (C2) RED.
#   M8: LDOC 긍정 copula self-claim 주입 → (C3) RED / 부정 어미 3형 negative control → PASS(오탐 0).
#   M9: §결정 2 절 **밖**(§결정 21)에 위장 row `| 8 |` 주입             → PASS 유지 (경계 밖 미계상).
#       + potency assert: 같은 row 카운터가 whole-doc scope 에서는 decoy 를 +1 로 본다
#         → 절 경계(lookahead)를 지키지 않는 구현이면 declared≠actual 로 자기 검출 (T-INV-4).
#
# fixture 앵커 규율: **구조-패턴 앵커**(§결정 N 헤딩 라인 / `| N |` row 패턴)만 사용 — 특정 문구
#   콘텐츠 sed 결박 금지 (ADR-170 §결정 2 본문 reword 에 test 가 깨지지 않도록). fake row 번호는
#   실 entry 값 공간(1~7)과 분리된 out-of-band `| 99 |`.
#
# Usage: bash scripts/test-check-disjoint-axis-whitelist.sh
# Exit: 0 = all discriminating tests pass / 1 = any fails (lint 회귀 의심) / 2 = fixture setup 실패.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

ADR_GREEN="$REPO_ROOT/archive/adr/ADR-170-orchestrator-subagent-default-inline-whitelist.md"
ADR_FROZEN="$REPO_ROOT/archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md"
LDOC_GREEN="$REPO_ROOT/docs/inter-plugin-contracts/return-envelope-v1.md"

for f in "$ADR_GREEN" "$ADR_FROZEN" "$LDOC_GREEN"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: fixture base 부재: $f"
    exit 2
  fi
done

# ═════════════════════════════════════════════════════════════════════════════
# Test harness — adr fixture + ldoc fixture 로 lint 실행 후 exit/sentinel 검증
# ═════════════════════════════════════════════════════════════════════════════
run_discriminating_test() {
  local test_name="$1"
  local adr_fixture="$2"          # 대상 ADR fixture path
  local ldoc_fixture="$3"         # return-envelope-v1.md fixture path
  local expected="$4"             # "PASS" or "RED"
  local description="$5"
  local required_sentinel="${6:-}"   # RED output 에 반드시 등장 (표적 violation)
  local forbidden_sentinel="${7:-}"  # RED output 에 절대 등장 금지 (off-target = 비특이)

  local lint_exit=0
  local lint_output=""
  lint_output=$(
    python3 scripts/lib/check_disjoint_axis_whitelist.py check \
      --adr-path "$adr_fixture" \
      --ldoc-path "$ldoc_fixture" \
      --repo-root "$REPO_ROOT" 2>&1
  ) || lint_exit=$?

  local lint_result="PASS"
  if [ "$lint_exit" -ne 0 ]; then
    lint_result="RED"
  fi

  if [ "$lint_result" != "$expected" ]; then
    echo "X FAIL: $test_name"
    echo "  Expected: $expected / Got: $lint_result (exit $lint_exit)"
    echo "  Desc: $description"
    echo "  Output: $lint_output"
    FAIL=$((FAIL+1))
    return 0
  fi

  if [ "$expected" = "RED" ]; then
    if [ -n "$required_sentinel" ] && ! echo "$lint_output" | grep -qE "$required_sentinel"; then
      echo "X FAIL: $test_name — RED 했으나 표적 violation 부재 (비특이 mutant)"
      echo "  required_sentinel: $required_sentinel"
      echo "  Output: $lint_output"
      FAIL=$((FAIL+1))
      return 0
    fi
    if [ -n "$forbidden_sentinel" ] && echo "$lint_output" | grep -qE "$forbidden_sentinel"; then
      echo "X FAIL: $test_name — off-target violation 검출 (mutant 비특이)"
      echo "  forbidden_sentinel: $forbidden_sentinel"
      echo "  Output: $lint_output"
      FAIL=$((FAIL+1))
      return 0
    fi
  fi

  echo "OK PASS: $test_name (lint result: $lint_result, exit $lint_exit)"
  PASS=$((PASS+1))
  return 0
}

# 정수 equality assert (potency 검증용 — mutant 잠재력 실측)
assert_eq() {
  local label="$1"
  local actual="$2"
  local expected="$3"
  if [ "$actual" = "$expected" ]; then
    echo "OK PASS: $label (= $actual)"
    PASS=$((PASS+1))
  else
    echo "X FAIL: $label — expected $expected / got $actual"
    FAIL=$((FAIL+1))
  fi
  return 0
}

# ═════════════════════════════════════════════════════════════════════════════
# fixture 생성 (구조-패턴 앵커 surgical mutant — 콘텐츠 문구 결박 0)
#   앵커 미발견 시 builder 가 exit 2 → set -e 로 즉시 중단 (silent degrade = tautology 유입 차단).
#   카운팅 유틸은 lint 본체를 import 재사용한다 (test-side 중복 계수 로직 0).
# ═════════════════════════════════════════════════════════════════════════════
TMP_TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_TEST_DIR"' EXIT

python3 - "$ADR_GREEN" "$LDOC_GREEN" "$TMP_TEST_DIR" "$REPO_ROOT" <<'PY_FIXTURE_BUILDER'
# -*- coding: utf-8 -*-
"""M1~M9 fixture builder — 구조-패턴 앵커 전용 (특정 문구 결박 0).

앵커 미발견 = FIXTURE-BUILD-ERROR exit 2 (조용한 무변조 fixture = tautology 유입이므로 금지).
"""
import os
import re
import sys

adr_green, ldoc_green, out_dir, repo_root = sys.argv[1:5]

sys.path.insert(0, os.path.join(repo_root, "scripts", "lib"))
from check_disjoint_axis_whitelist import (  # noqa: E402  (lint 본체 재사용)
    _SECTION2_START,
    _SECTION2_END,
    _DECLARED_TOTAL_RE,
    _extract_section,
    _count_base_table_entries,
)

ROW_LINE_RE = re.compile(r"^\s{0,8}\|\s{0,8}\d{1,3}\s{0,8}\|")


def die(msg):
    sys.stderr.write("FIXTURE-BUILD-ERROR: %s\n" % msg)
    sys.exit(2)


def read_text(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write_text(name, text):
    with open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="") as f:
        f.write(text)


def find_line(lines, pattern, start=0):
    rx = re.compile(pattern)
    for i in range(start, len(lines)):
        if rx.match(lines[i]):
            return i
    return -1


adr_text = read_text(adr_green)
ldoc_text = read_text(ldoc_green)
lines = adr_text.splitlines(keepends=True)

# ── 구조 앵커 1: §결정 2 절 라인 경계 (lookahead 로 §결정 20/21 over-match 배제) ──
s2 = find_line(lines, _SECTION2_START)
if s2 < 0:
    die("§결정 2 헤딩 앵커 미발견")
s3 = find_line(lines, _SECTION2_END, s2 + 1)
if s3 < 0:
    die("§결정 3 헤딩 앵커 미발견 (절 종료 경계 소실)")

# ── 구조 앵커 2: §결정 2 절 안 numbered row 블록 ──
row_idx = [i for i in range(s2, s3) if ROW_LINE_RE.match(lines[i])]
if len(row_idx) < 2:
    die("§결정 2 flat 표 numbered row %d 개 — 구조 앵커 실패" % len(row_idx))
last_row = row_idx[-1]
nl = "\r\n" if lines[last_row].endswith("\r\n") else "\n"

# ── 구조 앵커 3: §결정 2 절 안 정형 선언 라인 ──
decl_idx = -1
for i in range(s2, s3):
    if _DECLARED_TOTAL_RE.search(lines[i]):
        decl_idx = i
        break
if decl_idx < 0:
    die("§결정 2 정형 선언 라인 앵커 미발견")

# ── M1: 마지막 numbered row 뒤 out-of-band fake row 주입 ──
m1 = list(lines)
m1.insert(last_row + 1,
          "| 99 | fake-entry | M1 주입 fake row (out-of-band) | 구조 앵커 fixture |" + nl)
write_text("adr_m1.md", "".join(m1))

# ── M2: 정형 선언 값 변조 (declared → 9) ──
m2 = list(lines)
m2[decl_idx] = _DECLARED_TOTAL_RE.sub(
    lambda m: m.group(0).replace(m.group(1) + "-entry", "9-entry", 1), m2[decl_idx], count=1)
if m2[decl_idx] == lines[decl_idx]:
    die("M2 선언 값 변조 무효과 (declared 가 이미 9 이거나 치환 실패)")
write_text("adr_m2.md", "".join(m2))

# ── M3: 정형 선언 라인 삭제 ──
m3 = list(lines)
del m3[decl_idx]
write_text("adr_m3.md", "".join(m3))

# ── M5: flat 표 row 1개 삭제 ──
m5 = list(lines)
del m5[last_row]
write_text("adr_m5.md", "".join(m5))

# ── M9: §결정 2 절 밖(§결정 21, 없으면 §결정 20) 위장 row 주입 ──
decoy_at = find_line(lines, r"### 결정 21(?![0-9])", s3)
if decoy_at < 0:
    decoy_at = find_line(lines, r"### 결정 20(?![0-9])", s3)
if decoy_at < 0:
    die("§결정 20/21 헤딩 앵커 미발견 (M9 decoy 배치 불가)")
m9 = list(lines)
m9[decoy_at + 1:decoy_at + 1] = [
    nl,
    "| 8 | decoy | M9 위장 row (§결정 2 절 밖) | 경계 lookahead fixture |" + nl,
]
m9_text = "".join(m9)
write_text("adr_m9.md", m9_text)

# ── LDOC mutants ──
ldoc_m7 = re.sub(r"disjoint\s{0,4}axis", "", ldoc_text, flags=re.IGNORECASE)
if ldoc_m7 == ldoc_text:
    die("M7 'disjoint axis' 선언 제거 무효과 (GREEN 에 선언 부재?)")
write_text("ldoc_m7.md", ldoc_m7)

write_text("ldoc_m8_positive.md",
           ldoc_text + "\n\nreturn-envelope 는 inline whitelist 의 8번째 entry 이다.\n")
write_text("ldoc_m8_neg1.md",
           ldoc_text + "\n\nreturn-envelope 는 inline whitelist 의 8번째 entry 가 아니며, 별개 축이다.\n")
write_text("ldoc_m8_neg2.md",
           ldoc_text + "\n\nreturn-envelope 는 inline whitelist 의 entry 로 추가되지 않는다.\n")
write_text("ldoc_m8_neg3.md",
           ldoc_text + "\n\nreturn-envelope 는 inline whitelist 의 entry 로 등록하지 않는다.\n")

# ── potency 실측 (M9 양방향 assert 근거) ──
#   같은 row 카운터를 (a) §결정 2 절 scope (b) whole-doc scope 로 각각 적용 —
#   decoy 는 (b) 에서만 +1 로 보인다 = 경계 미준수 구현이 RED 로 자기 검출됨의 실측 근거.
green_sec = _extract_section(adr_text, _SECTION2_START, _SECTION2_END)
m9_sec = _extract_section(m9_text, _SECTION2_START, _SECTION2_END)
if green_sec is None or m9_sec is None:
    die("potency 산출 실패 — §결정 2 절 추출 불가")
with open(os.path.join(out_dir, "potency.env"), "w", encoding="utf-8", newline="\n") as f:
    f.write("GREEN_SEC_ROWS=%d\n" % _count_base_table_entries(green_sec))
    f.write("M9_SEC_ROWS=%d\n" % _count_base_table_entries(m9_sec))
    f.write("GREEN_DOC_ROWS=%d\n" % _count_base_table_entries(adr_text))
    f.write("M9_DOC_ROWS=%d\n" % _count_base_table_entries(m9_text))
PY_FIXTURE_BUILDER

ADR_M1="$TMP_TEST_DIR/adr_m1.md"
ADR_M2="$TMP_TEST_DIR/adr_m2.md"
ADR_M3="$TMP_TEST_DIR/adr_m3.md"
ADR_M5="$TMP_TEST_DIR/adr_m5.md"
ADR_M9="$TMP_TEST_DIR/adr_m9.md"
LDOC_M7="$TMP_TEST_DIR/ldoc_m7.md"
LDOC_M8P="$TMP_TEST_DIR/ldoc_m8_positive.md"

# ═════════════════════════════════════════════════════════════════════════════
# M6 (negative control) 선행 — base GREEN 확립이 이후 전 mutant 의 tautology 가드
# ═════════════════════════════════════════════════════════════════════════════
run_discriminating_test \
  "TC-M6-negative-control-GREEN" \
  "$ADR_GREEN" \
  "$LDOC_GREEN" \
  "PASS" \
  "M6: 무변조 정본 (real ADR-170 declared==actual + real return-envelope-v1.md) — base GREEN"

# M1 — flat 표 마지막 row 뒤 out-of-band fake row `| 99 |` 주입 → (C1) only
run_discriminating_test \
  "TC-M1-fake-row-injection" \
  "$ADR_M1" \
  "$LDOC_GREEN" \
  "RED" \
  "M1: §결정 2 flat 표 마지막 row 뒤 fake row | 99 | 주입 (actual +1) — (C1) 표적" \
  '\(C1\).*declared-vs-actual 불일치' \
  '\(C0\)|\(C2\)|\(C3\)'

# M2 — 정형 선언 값 변조 → (C1) only
run_discriminating_test \
  "TC-M2-declaration-value-tamper" \
  "$ADR_M2" \
  "$LDOC_GREEN" \
  "RED" \
  "M2: 정형 선언 '= N-entry' → '= 9-entry' 값 변조 (declared 오염) — (C1) 표적" \
  '\(C1\).*declared-vs-actual 불일치' \
  '\(C0\)|\(C2\)|\(C3\)'

# M3 — 정형 선언 라인 삭제 → (C1) fail-closed only
run_discriminating_test \
  "TC-M3-declaration-line-removed" \
  "$ADR_M3" \
  "$LDOC_GREEN" \
  "RED" \
  "M3: 정형 선언 라인 삭제 (declared 소스 소실) — (C1) fail-closed 표적" \
  '\(C1\).*정형 선언 라인.*부재' \
  '\(C0\)|\(C2\)|\(C3\)'

# M4 — lint 대상을 Superseded 동결 구본으로 지정 → (C0) only
run_discriminating_test \
  "TC-M4-frozen-superseded-target" \
  "$ADR_FROZEN" \
  "$LDOC_GREEN" \
  "RED" \
  "M4: lint 대상 = Superseded 동결 구본 ADR-039 (영구-PASS hollow-gate) — (C0) 표적" \
  '\(C0\).*Superseded' \
  '\(C1\)|\(C2\)|\(C3\)'

# M5 — flat 표 row 1개 삭제 → (C1) only
run_discriminating_test \
  "TC-M5-table-row-removed" \
  "$ADR_M5" \
  "$LDOC_GREEN" \
  "RED" \
  "M5: §결정 2 flat 표 row 1개 삭제 (actual -1) — (C1) 표적" \
  '\(C1\).*declared-vs-actual 불일치' \
  '\(C0\)|\(C2\)|\(C3\)'

# M7 — LDOC disjoint-axis 선언 제거 → (C2) only
run_discriminating_test \
  "TC-M7-ldoc-disjoint-axis-removed" \
  "$ADR_GREEN" \
  "$LDOC_M7" \
  "RED" \
  "M7: return-envelope-v1.md 'disjoint axis' 선언 제거 — (C2) 표적" \
  '\(C2\)' \
  '\(C0\)|\(C1\)|\(C3\)'

# M8 양성 — 긍정 copula self-claim → (C3) only
run_discriminating_test \
  "TC-M8-positive-self-claim" \
  "$ADR_GREEN" \
  "$LDOC_M8P" \
  "RED" \
  "M8 양성: LDOC 이 '8번째 entry 이다' 긍정 copula 로 self-claim — (C3) 표적" \
  '\(C3\)' \
  '\(C0\)|\(C1\)|\(C2\)'

# M8 negative control 3종 — 부정 어미 자연 문구는 오탐 0 (PASS 유지)
run_discriminating_test \
  "TC-M8-neg1-entry-ga-anim" \
  "$ADR_GREEN" \
  "$TMP_TEST_DIR/ldoc_m8_neg1.md" \
  "PASS" \
  "M8 negative-1: '...8번째 entry 가 아니며' 부정 어미 — (C3) 오탐 0"

run_discriminating_test \
  "TC-M8-neg2-chuga-doeji-anneunda" \
  "$ADR_GREEN" \
  "$TMP_TEST_DIR/ldoc_m8_neg2.md" \
  "PASS" \
  "M8 negative-2: '...entry 로 추가되지 않는다' 부정 어미 — (C3) 오탐 0"

run_discriminating_test \
  "TC-M8-neg3-deungrok-haji-anneunda" \
  "$ADR_GREEN" \
  "$TMP_TEST_DIR/ldoc_m8_neg3.md" \
  "PASS" \
  "M8 negative-3: '...entry 로 등록하지 않는다' 부정 어미 — (C3) 오탐 0"

# M9 — §결정 2 절 밖 decoy row → PASS 유지 (경계 밖 미계상)
run_discriminating_test \
  "TC-M9-out-of-section-decoy" \
  "$ADR_M9" \
  "$LDOC_GREEN" \
  "PASS" \
  "M9: §결정 21 절 안 위장 row | 8 | 주입 — 절 경계 lookahead 준수 시 미계상 (PASS 유지)"

# M9 potency — 같은 카운터가 whole-doc scope 에서는 decoy 를 +1 로 본다
#   (= 경계 미준수 구현이면 declared≠actual 로 RED. mutant 무력 fixture 가 아님을 실측)
# shellcheck disable=SC1091
. "$TMP_TEST_DIR/potency.env"
assert_eq "TC-M9-potency: §결정 2 절 scope row count 불변 (decoy 미계상)" \
  "$M9_SEC_ROWS" "$GREEN_SEC_ROWS"
assert_eq "TC-M9-potency: whole-doc scope row count +1 (decoy 실재 — over-match 시 RED 근거)" \
  "$M9_DOC_ROWS" "$((GREEN_DOC_ROWS + 1))"

# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: disjoint-axis-whitelist lint discriminating test (M1~M9)"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "OK All discriminating tests passed — lint is detecting mutations correctly"
  exit 0
else
  echo "X Some tests failed — lint may not be detecting mutations correctly"
  exit 1
fi
