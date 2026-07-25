#!/usr/bin/env bash
# tests/scripts/test_check_codex_review_output_schema.sh
# CFP-2828 / ADR-081 Amendment 14 §결정 D15 — Discriminating driver for
#   scripts/lib/check_codex_review_output_schema.py (AC-6 소비 재검증 helper).
#
# 계약 (§4 소비 규칙 / §8.4 하단 negative fixture 6종):
#   helper 시그니처 = check_codex_review_output_schema.py <out_json_path> <schema_path> <category_enum>
#   exit 0 = 재검증 5단계 통과(소비 가능) / exit 1 = inconclusive(PASS 승격 금지) / exit 2 = setup error
#   재검증 5단계: ①파일존재 ②JSON parse ③schema 준수 ④counts↔findings cross-field ⑤category∈enum
#
# negative fixture 6종 (전부 → exit 1 inconclusive, PASS 승격 0):
#   ① free-form 텍스트 out.json  (#15451 documented 형상 — ②JSON parse fail)
#   ② 파일 부재                   (①존재 fail)
#   ③ partial-truncated JSON      (timeout 잔존 형상 — ②parse fail)
#   ④ verdict enum-out ("SHIP")   (③schema enum fail; verdict-missing 도 이 클래스)
#   ⑤ counts↔findings mismatch    (④cross-field fail)
#   ⑥ category∉enum               (⑤category fail)
# positive fixture 2종 (→ exit 0): valid ISSUES / valid PASS-empty.
#
# ★ distinct-marker 병행 assert (외부 script subprocess fork 진정성 — exit-code 단독 판정 금지):
#   helper 는 python3 subprocess 로 fork 됨. 도메인 exit 1(inconclusive)은 Python 의 uncaught-exception
#   기본 exit 1 과 겹치므로, exit code 단독 assert 는 fork 진정성/도메인 경로 도달을 보증 못함(silent
#   false-positive). 따라서 (exit_code, stdout sentinel) 튜플 동시 assert:
#     negative → exit 1 ∧ stdout 에 "inconclusive" 방출 (fail-closed 도메인 경로 도달 증명)
#     positive → exit 0 ∧ stdout 에 "[codex-review-output-schema] PASS" 방출
#   setup error(exit 2, "setup error:" — "inconclusive" 미방출)와 도메인 exit 1 을 구분.
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HELPER="$REPO_ROOT/scripts/lib/check_codex_review_output_schema.py"
SCHEMA="$REPO_ROOT/plugins/codeforge-review/schemas/codex-review-output-schema-v1.json"
FIX="$REPO_ROOT/tests/fixtures/codex-review-output"

PASS=0
FAIL=0

# helper 실행 → exit code + 결합 stdout/stderr 반환 (전역 LAST_EXIT / LAST_OUT).
#   exit code 캡처 = `|| LAST_EXIT=$?` (raw `|| true` 아님 — 근접 tuple assert 가 pass/fail 을 gating).
LAST_EXIT=0
LAST_OUT=""
run_helper() {
  local out_json="$1" cat_enum="$2"
  LAST_EXIT=0
  LAST_OUT="$(python3 "$HELPER" "$out_json" "$SCHEMA" "$cat_enum" 2>&1)" || LAST_EXIT=$?
}

# negative assert: exit 1 ∧ stdout "inconclusive" sentinel (distinct-marker 병행).
assert_neg() {
  local name="$1" out_json="$2" cat_enum="$3" stage="$4"
  run_helper "$out_json" "$cat_enum"
  if [ "$LAST_EXIT" -eq 1 ] && printf '%s' "$LAST_OUT" | grep -q "inconclusive"; then
    echo "✓ PASS: $name (exit 1 + inconclusive sentinel) — $stage"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit 1 ∧ 'inconclusive' sentinel; got exit $LAST_EXIT"
    echo "  Output: $LAST_OUT"
    FAIL=$((FAIL+1))
  fi
}

# positive assert: exit 0 ∧ stdout PASS sentinel (distinct-marker 병행).
assert_pos() {
  local name="$1" out_json="$2" cat_enum="$3" note="$4"
  run_helper "$out_json" "$cat_enum"
  if [ "$LAST_EXIT" -eq 0 ] && printf '%s' "$LAST_OUT" | grep -q "\[codex-review-output-schema\] PASS"; then
    echo "✓ PASS: $name (exit 0 + PASS sentinel) — $note"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit 0 ∧ '[codex-review-output-schema] PASS' sentinel; got exit $LAST_EXIT"
    echo "  Output: $LAST_OUT"
    FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2828: codex-review out.json 소비 재검증 helper — negative fixture 6종"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# ① free-form 텍스트 (모델이 schema 대신 산문 방출, #15451) → ② JSON parse fail
assert_neg "N1: free-form 텍스트 out.json (#15451)" \
  "$FIX/neg1_freeform.json" "runtime-bug,layer-violation" "② JSON parse fail-closed"

# ② 파일 부재 (존재하지 않는 경로) → ① 파일 존재 fail
assert_neg "N2: 파일 부재 (nonexistent path)" \
  "$FIX/__nonexistent_out__.json" "runtime-bug,layer-violation" "① 파일 부재 fail-closed"

# ③ partial-truncated JSON (timeout 잔존 형상) → ② JSON parse fail
assert_neg "N3: partial-truncated JSON (timeout 잔존)" \
  "$FIX/neg3_truncated.json" "runtime-bug,layer-violation" "② truncated parse fail-closed"

# ④ verdict enum-out ("SHIP") → ③ schema enum fail
assert_neg "N4: verdict enum-out (\"SHIP\")" \
  "$FIX/neg4_verdict_enum_out.json" "runtime-bug,layer-violation" "③ schema verdict enum fail"

# ⑤ counts↔findings mismatch (counts.P0=1 ∧ findings P0 0건) → ④ cross-field fail
assert_neg "N5: counts↔findings mismatch (cross-field)" \
  "$FIX/neg5_counts_findings_mismatch.json" "runtime-bug,layer-violation" "④ cross-field fail"

# ⑥ category∉enum (schema-valid string 이나 packet enum 밖) → ⑤ category fail
assert_neg "N6: category∉enum (schema-valid string)" \
  "$FIX/neg6_category_out_of_enum.json" "runtime-bug,layer-violation" "⑤ category∉enum fail"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " positive fixture (재검증 5단계 전부 통과 → exit 0)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# positive 1: schema-valid ∧ cross-field 정합 ∧ category∈enum
assert_pos "P1: valid ISSUES (cross-field 정합 ∧ category∈enum)" \
  "$FIX/pos1_valid_issues.json" "runtime-bug,layer-violation" "5단계 전부 통과"

# positive 2: findings empty ∧ verdict=PASS ∧ counts 전0 (§8.2 정상 PASS)
assert_pos "P2: valid PASS-empty (findings empty ∧ counts 전0)" \
  "$FIX/pos2_valid_pass_empty.json" "runtime-bug,layer-violation" "PASS-only-if-explicit 정상 경로"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " 취약 revert 재현 (discriminating 입증 — born-broken/vacuous-green 방지)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
# positive fixture 를 일부러 깨서(counts.P1 1→2, cross-field 위반) helper 가 exit 1 로 검출하는지 →
# 원 fixture 로 exit 0 회복하는지 확인. helper 가 실제로 정합/위반을 discriminate 함을 입증.
revert_tmp="$(mktemp --suffix=.json)"
# shellcheck disable=SC2064
trap "rm -f '$revert_tmp'" EXIT
python3 - "$FIX/pos1_valid_issues.json" "$revert_tmp" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding='utf-8'))
data['counts']['P1'] = 2   # cross-field 파손: findings P1 1건 ↔ counts.P1=2
json.dump(data, open(sys.argv[2], 'w', encoding='utf-8'))
PY
# broken → exit 1 (helper 가 cross-field 위반 검출)
run_helper "$revert_tmp" "runtime-bug,layer-violation"
if [ "$LAST_EXIT" -eq 1 ] && printf '%s' "$LAST_OUT" | grep -q "cross-field"; then
  echo "✓ PASS: REVERT-1 broken pos1(counts.P1 1→2) → exit 1 (cross-field 검출) — discriminating 입증"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: REVERT-1 broken fixture 가 exit 1 로 검출되지 않음 (vacuous-green 위험)"
  echo "  got exit $LAST_EXIT | Output: $LAST_OUT"
  FAIL=$((FAIL+1))
fi
# restore semantics: 원 fixture 는 여전히 exit 0
run_helper "$FIX/pos1_valid_issues.json" "runtime-bug,layer-violation"
if [ "$LAST_EXIT" -eq 0 ]; then
  echo "✓ PASS: REVERT-2 원 pos1 fixture → exit 0 (정합 회복) — 위 broken 이 진짜 discriminate 였음"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: REVERT-2 원 fixture 가 exit 0 아님 (got $LAST_EXIT)"
  FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — negative 6종 inconclusive + positive 2종 통과 + discriminating 입증"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
