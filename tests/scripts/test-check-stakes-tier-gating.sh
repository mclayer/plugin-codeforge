#!/usr/bin/env bash
# tests/scripts/test-check-stakes-tier-gating.sh
# CFP-2432 Phase 2 — Story-shape 조건부 model tier 판정 로직 discriminating test
#
# Change Plan §8 truth-table 8행(T-G1~T-G8) + INV-1/2/3 + TB-1/2/3 변별 실증.
# env var 기반 판정이므로 fork 최소화 — wrapper 정상 호출 + env override 로 변별.
#
# red-first TDD 실증 의무:
#  1. GREEN 실행: 정상 스크립트로 모든 케이스 PASS 확인
#  2. RED 변별: mutation 사본(항상 opus echo) 으로 low-shape 케이스 FAIL 강제 → 변별성 입증
#  3. cleanup: mutation 사본 정리
#
# set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-stakes-tier-gating.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# Helper: run_test_case <name> <env-override> <expected-stdout> <description>
#   env-override = "KEY1=val1 KEY2=val2 ..." (space-separated)
#   expected-stdout = "opus" or "sonnet"
# ─────────────────────────────────────────────────────────────────────────────
run_test_case() {
  local name="$1" env_override="$2" expected="$3" description="$4"
  local out exit_code=0

  # Evaluate env override (KEY=val KEY=val ...) + run script
  # Run script with env overrides (avoid eval to prevent environment variable leakage)
  if [ -z "$env_override" ]; then
    out=$( bash "$WRAPPER" 2>/dev/null ) || exit_code=$?
  else
    out=$( (eval "export $env_override"; bash "$WRAPPER" 2>/dev/null) ) || exit_code=$?
  fi

  # Trim whitespace
  out="$(printf '%s' "$out" | tr -d '[:space:]')"
  expected="$(printf '%s' "$expected" | tr -d '[:space:]')"

  if [ "$out" = "$expected" ]; then
    echo "✓ PASS: $name — $description"
    echo "         output: '$out' (as expected)"
    PASS=$((PASS+1))
    return 0
  else
    echo "✗ FAIL: $name — $description"
    echo "         expected: '$expected', got: '$out'"
    FAIL=$((FAIL+1))
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper: run_test_case_stderr <name> <env-override> <expected-stdout>
#         <expected-stderr-marker> <description>
#   Verify both stdout exact-match AND stderr contains marker (downtier case)
# ─────────────────────────────────────────────────────────────────────────────
run_test_case_stderr() {
  local name="$1" env_override="$2" expected_stdout="$3" stderr_marker="$4" description="$5"
  local stdout stderr exit_code=0
  local output

  if [ -z "$env_override" ]; then
    output=$( bash "$WRAPPER" 2>&1 ) || exit_code=$?
  else
    output=$( (eval "export $env_override"; bash "$WRAPPER" 2>&1) ) || exit_code=$?
  fi

  # Split stdout + stderr (both captured by 2>&1)
  # Last line = stdout (tier), preceding = stderr (reason lines)
  stdout="$(printf '%s' "$output" | tail -1 | tr -d '[:space:]')"
  stderr="$(printf '%s' "$output" | head -n -1)"

  expected_stdout="$(printf '%s' "$expected_stdout" | tr -d '[:space:]')"

  local ok=1
  if [ "$stdout" != "$expected_stdout" ]; then
    ok=0
  fi
  if ! (printf '%s' "$stderr" | grep -qF "$stderr_marker"); then
    ok=0
  fi

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name — $description"
    echo "         stdout: '$stdout', stderr contains: '$stderr_marker'"
    PASS=$((PASS+1))
    return 0
  else
    echo "✗ FAIL: $name — $description"
    if [ "$stdout" != "$expected_stdout" ]; then
      echo "         stdout mismatch: expected '$expected_stdout', got '$stdout'"
    fi
    if ! (printf '%s' "$stderr" | grep -qF "$stderr_marker"); then
      echo "         stderr missing marker: '$stderr_marker'"
      echo "         actual stderr: $stderr"
    fi
    FAIL=$((FAIL+1))
    return 1
  fi
}

set +e

# ═════════════════════════════════════════════════════════════════════════════
# T-G1: 4-AND 모두 low → sonnet (wrapper_floor = sonnet)
#   INV-2 high-absorbing: 하나도 high 아니면 sonnet 정상
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "T-G1" \
  'STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no' \
  'sonnet' \
  "4-AND 모두 low → sonnet (wrapper_floor 정상 tier-flip)"

# ═════════════════════════════════════════════════════════════════════════════
# T-G2: real_funds=yes, 나머지 low → opus (high-absorbing)
#   Single high → wrapper_floor = opus
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "T-G2" \
  'STAKES_REAL_FUNDS=yes STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no' \
  'opus' \
  "real_funds=yes (single high) → opus (high-absorbing INV-2)"

# ═════════════════════════════════════════════════════════════════════════════
# T-G3: production_cutover=yes, 나머지 low → opus
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "T-G3" \
  'STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=yes STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no' \
  'opus' \
  "production_cutover=yes → opus (high-absorbing)"

# ═════════════════════════════════════════════════════════════════════════════
# T-G4: new_trust_boundary=yes, 나머지 low → opus
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "T-G4" \
  'STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=yes STAKES_LIVE_EXTERNAL_API=no' \
  'opus' \
  "new_trust_boundary=yes → opus (high-absorbing)"

# ═════════════════════════════════════════════════════════════════════════════
# T-G5: live_external_api=yes, 나머지 low → opus
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "T-G5" \
  'STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=yes' \
  'opus' \
  "live_external_api=yes → opus (high-absorbing)"

# ═════════════════════════════════════════════════════════════════════════════
# T-G6: 2+ high (mixed) → opus
#   Example: real_funds=yes + cutover=yes
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "T-G6" \
  'STAKES_REAL_FUNDS=yes STAKES_PRODUCTION_CUTOVER=yes STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no' \
  'opus' \
  "2+ high (real_funds + production_cutover) → opus (high-absorbing)"

# ═════════════════════════════════════════════════════════════════════════════
# T-G7: 4-AND low + STAKES_OVERLAY_FLOOR=opus → opus (보수 override honored, INV-3)
#   확장-only monotone: overlay honor iff overlay_rank > floor_rank (보수 방향)
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "T-G7" \
  'STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no STAKES_OVERLAY_FLOOR=opus' \
  'opus' \
  "4-AND low + overlay=opus → opus (보수 override honored, INV-3 확장-only)"

# ═════════════════════════════════════════════════════════════════════════════
# T-G8: high shape + STAKES_OVERLAY_FLOOR=sonnet → opus (down-tier 거부, AC-3)
#   overlay 가 wrapper_floor 미만 → clamp=max(wrapper_floor, overlay) 적용 + stderr 거부로그
#   INV-3 확장-only 위반 = down-tier 공격적 override 무시
# ═════════════════════════════════════════════════════════════════════════════
run_test_case_stderr "T-G8" \
  'STAKES_REAL_FUNDS=yes STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no STAKES_OVERLAY_FLOOR=sonnet' \
  'opus' \
  'overlay down-tier 거부' \
  "high shape + overlay=sonnet(down-tier) → opus (clamp=max, AC-3 거부 로그)"

# ═════════════════════════════════════════════════════════════════════════════
# INV-1 fail-safe: 모든 신호 unset → 기본값(fail-safe high) → opus
#   신호 부재/파싱불가 → high (절대 sonnet 아님)
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "INV-1-unset" \
  '' \
  'opus' \
  "모든 신호 unset → fail-safe high → opus (INV-1)"

# ═════════════════════════════════════════════════════════════════════════════
# INV-1 fail-safe: garbage 신호(예: "maybe") → fail-safe high → opus
#   normalize_signal 의 기본 분기 (case "no" → low, else → high)
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "INV-1-garbage" \
  'STAKES_REAL_FUNDS=maybe' \
  'opus' \
  "garbage 신호(maybe) → fail-safe high → opus (INV-1)"

# ═════════════════════════════════════════════════════════════════════════════
# INV-2 high-absorbing detailed: 3개 low + 1개 high → opus
#   미리 T-G2~G5 로 각 축 단일 toggle 검증함. 추가 상호작용 케이스.
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "INV-2-3low1high" \
  'STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=yes' \
  'opus' \
  "3개 low + 1개 high(live_api) → opus (high-absorbing 1개면 충분)"

# ═════════════════════════════════════════════════════════════════════════════
# INV-3 확장-only: wrapper_floor 보수 override (overlay_rank > floor_rank) honored
#   T-G7 이미 검증. 추가 케이스: wrapper_floor=opus(high) + overlay=opus → no-op
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "INV-3-nochange" \
  'STAKES_REAL_FUNDS=yes STAKES_OVERLAY_FLOOR=opus' \
  'opus' \
  "high + overlay=opus (floor=wrapper) → opus no-op (INV-3)"

# ═════════════════════════════════════════════════════════════════════════════
# TB-1: consumer-false-low (신호 모두 unset) → fail-safe opus
#   신호 자기보고 누락 시에도 opus 보수 원칙 (INV-1 재확인)
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "TB-1-consumer-false-low" \
  'STAKES_REAL_FUNDS="" STAKES_PRODUCTION_CUTOVER="" STAKES_NEW_TRUST_BOUNDARY="" STAKES_LIVE_EXTERNAL_API=""' \
  'opus' \
  "consumer 신호 누락(all empty) → fail-safe opus (TB-1)"

# ═════════════════════════════════════════════════════════════════════════════
# TB-2: parser 실패 (garbage 신호) → fail-safe opus
#   normalize_signal 이 비표준 입력을 high로 취급
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "TB-2-parser-garbage" \
  'STAKES_REAL_FUNDS=TRUE' \
  'opus' \
  "parser 실패(TRUE ≠ yes/no) → fail-safe high → opus (TB-2)"

# ═════════════════════════════════════════════════════════════════════════════
# TB-3: weaker-overlay 거부 (high shape + down-tier overlay) → opus + stderr 거부로그
#   T-G8 과 동일 의도, 명시 케이스
# ═════════════════════════════════════════════════════════════════════════════
run_test_case_stderr "TB-3-weaker-overlay" \
  'STAKES_REAL_FUNDS=yes STAKES_OVERLAY_FLOOR=haiku' \
  'opus' \
  'overlay down-tier 거부' \
  "weaker overlay(haiku) vs wrapper_floor(opus) → 거부 + opus (TB-3 INV-3)"

# ═════════════════════════════════════════════════════════════════════════════
# ANTI-THEATER DISCRIMINATING GUARD: low-shape(sonnet) ≠ high-shape(opus)
#   변별 실증: 같은 로직이라도 입력에 따라 실제로 다른 출력 → 테스트 진정성 증명
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "DISCRIMINATING-sonnet-low" \
  'STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no' \
  'sonnet' \
  "변별 가드: low-shape → sonnet (T-G1)"

run_test_case "DISCRIMINATING-opus-high" \
  'STAKES_REAL_FUNDS=yes' \
  'opus' \
  "변별 가드: high-shape → opus (T-G2), sonnet ≠ opus 실제 갈림"

# ═════════════════════════════════════════════════════════════════════════════
# 회귀 케이스: garbage overlay + low-shape → opus (INV-1 이중 안전망, F-CR-001)
# STAKES_OVERLAY_FLOOR=garbage(미지 tier) → fail-safe opus 로 clamp (known-enum guard)
# ═════════════════════════════════════════════════════════════════════════════
run_test_case "INV-1-garbage-overlay" \
  'STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no STAKES_OVERLAY_FLOOR=garbage' \
  'opus' \
  "garbage overlay(미지 tier) + low-shape → opus (fail-safe clamp, INV-1)"

run_test_case "INV-1-garbage-overlay-high" \
  'STAKES_REAL_FUNDS=yes STAKES_OVERLAY_FLOOR=megamodel' \
  'opus' \
  "garbage overlay(megamodel) + high-shape → opus (fail-safe clamp, INV-1)"

# ═════════════════════════════════════════════════════════════════════════════
# RED 변별 실증 섹션 (production sed mutation testing)
# 목적: production 파일을 sed 로 변형한 사본에서 low-shape 케이스가 RED 로 뒤집히는지 입증
#   → 정상 스크립트는 GREEN(sonnet), mutation 스크립트는 RED(opus) 다르게 출력
# ═════════════════════════════════════════════════════════════════════════════

# production wrapper_floor 계산을 항상 "opus" 로 강제하는 sed mutation 생성
# 원본은 4-AND 로직으로 low-shape → sonnet 을 결정하는데,
# sed 로 WRAPPER_FLOOR 할당 라인을 "always opus" 로 변경하면 low-shape 도 opus 가 됨
MUTATION_WRAPPER_PROD="$(mktemp)"

# sed mutation: "else" 분기(wrapper_floor=sonnet)를 "wrapper_floor=opus" 로 변경
# 이렇게 하면 4-AND=low 도 sonnet 아닌 opus 로 설정됨 → T-G1 케이스가 RED 뒤집힘
sed 's/^  WRAPPER_FLOOR="sonnet"$/  WRAPPER_FLOOR="opus"  # MUTATION: force opus/' "$WRAPPER" > "$MUTATION_WRAPPER_PROD"
chmod +x "$MUTATION_WRAPPER_PROD"

# mutation 버전에서 T-G1(low-shape) 실행 — sonnet 기대하는데 opus 나와야 RED 입증
mut_out_prod=""
exit_code=0
mut_out_prod=$( (eval "export STAKES_REAL_FUNDS=no STAKES_PRODUCTION_CUTOVER=no STAKES_NEW_TRUST_BOUNDARY=no STAKES_LIVE_EXTERNAL_API=no"; bash "$MUTATION_WRAPPER_PROD" 2>/dev/null) ) || exit_code=$?
mut_out_prod="$(printf '%s' "$mut_out_prod" | tr -d '[:space:]')"

if [ "$mut_out_prod" = "opus" ]; then
  echo "✓ RED MUTATION-CHECK: T-G1 low-shape 케이스가 production sed mutation 에서 RED 뒤집힘(opus≠sonnet 기대) — 진정성 입증"
  PASS=$((PASS+1))
else
  echo "✗ FAIL MUTATION-CHECK: sed mutation 결과 이상 (expected opus, got: $mut_out_prod)"
  FAIL=$((FAIL+1))
fi

# Cleanup production mutation
rm -f "$MUTATION_WRAPPER_PROD"

# ═════════════════════════════════════════════════════════════════════════════
# Summary
# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "═════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: $PASS PASS, $FAIL FAIL"
echo "═════════════════════════════════════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  exit 0
else
  exit 1
fi
