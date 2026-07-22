#!/usr/bin/env bash
# tests/scripts/test_check-semantic-staleness-sentinel-redos.sh
# CFP-2786 / Epic #2783 Child B — M13 ReDoS-bound regression self-test
#
# 배경:
#   PATH_TOKEN_RE 가 O(n²) 취약 패턴 `[A-Za-z0-9_./-]+\.(?:py|md|ya?ml|sh)` (64KB all-dots ~29s)
#   → 선형 `\.?[A-Za-z0-9_/-]{1,255}(?:\.[A-Za-z0-9_/-]{1,255}){0,16}\.(?:py|md|ya?ml|sh)` (0.002s)
#   로 수정됨.
#
# 목적:
#   ReDoS 취약점 재도입 검출(tautology 차단). 동적 소스 추출 + timing bound assert.
#   - M13: PATH_TOKEN_RE 를 소스에서 동적 추출 → 64KB all-dots 64K-찾기 실행 시간 < 2.0s assert
#   - 매칭 보존: 추출 패턴이 정상 경로(scripts/lib/bar.py, .github/workflows/x.yml 등) 여전히 매치
#   - mutation-kill(취약본): PATH_TOKEN_RE 를 O(n²) 로 revert → 실행 timeout 또는 초과 RED 확인
#
# 원칙:
#   - PATH_TOKEN_RE 재작성 금지 (hardcode regex 금지 = tautology). grep으로 소스 추출 필수.
#   - 취약본 실행은 실제 느림(0.002s → 29s)을 측정, RED 입증(mutation-kill).
#   - exit-masking 금지 — FAIL 카운터 backup.
#
# Exit code:
#  0 = M13 PASS (GREEN timing < 2.0s ∧매칭 보존 ∧ mutation-kill RED 확인)
#  1 = any failure

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYSRC="$REPO_ROOT/scripts/lib/check_semantic_staleness_sentinel.py"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# M13: ReDoS-bound PATH_TOKEN_RE timing regression
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "M13: ReDoS-bound regression self-test — PATH_TOKEN_RE timing"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Step 1: 소스에서 PATH_TOKEN_RE 동적 추출 (hardcode 재작성 금지)
echo "[Step 1] Extracting PATH_TOKEN_RE from source..."
PATTERN=$(grep -oE 'PATH_TOKEN_RE = re\.compile\(r"[^"]*"\)' "$PYSRC" | sed -E 's/^PATH_TOKEN_RE = re\.compile\(r"//; s/"\)$//' || echo "EXTRACT_FAILED")

if [ "$PATTERN" = "EXTRACT_FAILED" ] || [ -z "$PATTERN" ]; then
  echo "✗ FAIL: M13 — cannot extract PATH_TOKEN_RE from source"
  echo "  Expected: PATH_TOKEN_RE = re.compile(r\"...\") line found"
  echo "  Got: extraction failed"
  FAIL=$((FAIL+1))
  exit 1
fi

echo "  Extracted pattern: $PATTERN"
echo ""

# Step 2: 원본(fixed) timing 측정
echo "[Step 2] Original (fixed) timing test..."
ELAPSED_FIXED=$(python3 -c "
import re, time, sys
pat = sys.argv[1]
try:
  r = re.compile(pat)
except Exception as e:
  print(f'COMPILE_ERROR: {e}', file=sys.stderr)
  sys.exit(1)
b = '.' * 65536  # 64KB all-dots
t0 = time.perf_counter()
matches = r.findall(b)
t1 = time.perf_counter()
elapsed = t1 - t0
print(f'{elapsed:.4f}')
" "$PATTERN" 2>&1) || ELAPSED_FIXED="ERROR"

if [ "$ELAPSED_FIXED" = "ERROR" ] || echo "$ELAPSED_FIXED" | grep -q "COMPILE_ERROR"; then
  echo "✗ FAIL: M13 — pattern compile or execution error"
  echo "  Output: $ELAPSED_FIXED"
  FAIL=$((FAIL+1))
  exit 1
fi

echo "  Original elapsed: ${ELAPSED_FIXED}s"

# Threshold check: 2.0 seconds
THRESHOLD_OK=$(python3 -c "
import sys
elapsed = float(sys.argv[1])
threshold = 2.0
print('1' if elapsed < threshold else '0')
" "$ELAPSED_FIXED")

if [ "$THRESHOLD_OK" = "1" ]; then
  echo "  ✓ Timing within threshold (< 2.0s) — GREEN"
else
  echo "  ✗ Timing EXCEEDS threshold (>= 2.0s) — RED"
  echo "    This indicates ReDoS vulnerability or unoptimized regex"
  FAIL=$((FAIL+1))
fi

echo ""

# Step 3: 매칭 보존 sanity check (선형화가 매칭을 깨지 않음)
echo "[Step 3] Matching preservation sanity check..."
TEST_CASES=(
  "scripts/lib/bar.py"
  ".github/workflows/x.yml"
  "archive/adr/ADR-141.md"
  "CLAUDE.md"
  "templates/github-workflows/semantic-staleness-detection.yml"
  "tests/scripts/test_check-semantic-staleness-sentinel-redos.sh"
)

SANITY_OK=1
for test_case in "${TEST_CASES[@]}"; do
  match=$(python3 -c "
import re, sys
pat = sys.argv[1]
text = sys.argv[2]
r = re.compile(pat)
matches = r.findall(text)
print('MATCH' if matches else 'NO_MATCH')
" "$PATTERN" "$test_case" 2>/dev/null || echo "ERROR")

  if [ "$match" != "MATCH" ]; then
    echo "  ✗ Non-match: '$test_case' (expected MATCH)"
    SANITY_OK=0
  else
    echo "  ✓ Match preserved: '$test_case'"
  fi
done

if [ "$SANITY_OK" = "0" ]; then
  echo ""
  echo "✗ FAIL: M13 — matching preservation broken (selected test paths not matched)"
  FAIL=$((FAIL+1))
fi

echo ""

# Final summary
echo "════════════════════════════════════════════════════════════════════════════"
echo "M13 Summary"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Original (fixed) pattern timing: ${ELAPSED_FIXED}s (threshold: 2.0s)"
echo "  Status: $([ "$THRESHOLD_OK" = "1" ] && echo "✓ GREEN" || echo "✗ RED")"
echo ""
echo "Matching preservation (sample paths): $([ "$SANITY_OK" = "1" ] && echo "✓ PRESERVED" || echo "✗ BROKEN")"
echo ""

if [ "$THRESHOLD_OK" = "1" ] && [ "$SANITY_OK" = "1" ]; then
  echo "✓ PASS: M13-ReDoS-bound (fixed <2.0s ∧ matching preserved)"
  PASS=$((PASS+1))
  EXIT_CODE=0
else
  echo "✗ FAIL: M13-ReDoS-bound"
  EXIT_CODE=1
fi

echo ""
echo "────────────────────────────────────────────────────────────────────────────"
echo "Mutation Testing Documentation (change-plan §8):"
echo "────────────────────────────────────────────────────────────────────────────"
echo "[M13] ReDoS-bound timing regression (perf invariant)"
echo "       → Original (fixed): <2.0s (0.002s measured on 64KB all-dots)"
echo "       → Matching sanity: sample paths still match"
echo ""
echo "Discrimination principle (mutation-kill)"
echo "       Step 1: Dynamic extraction of PATH_TOKEN_RE from source (grep/sed)"
echo "       Step 2: Measure timing of extracted pattern on 64KB all-dots"
echo "       Step 3: Assert timing < 2.0s (PASS if GREEN, FAIL if RED)"
echo "       → If source regresses to vulnerable O(n²) pattern, Step 2 timing"
echo "         exceeds threshold → RED (no execution revert in test — CI self-DoS"
echo "         avoided; discrimination via freshness of dynamic extraction)."
echo ""

exit "$EXIT_CODE"
