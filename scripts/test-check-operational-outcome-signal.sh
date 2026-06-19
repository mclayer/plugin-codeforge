#!/usr/bin/env bash
# CFP-2361 PS4 — Discriminating test for check-operational-outcome-signal.sh
#
# RED → GREEN 변별 증명 (mutation testing pattern):
# - Dirty fixture: §7.4.7 outcome-signal 미완 / §8.5.1 soak 도출 미완 → lint 경고 emit 확인
# - Clean fixture: 3요소 + soak 도출 완비 → lint 경고 0 확인
#
# Exit code: 0 (all tests pass) / 1 (any test fails)
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

# Create temporary test directory
TMP_REPO=$(mktemp -d)
trap "rm -rf '$TMP_REPO'" EXIT

# Copy necessary files
mkdir -p "$TMP_REPO/docs/stories" "$TMP_REPO/scripts"
cp "$REPO_ROOT/scripts/check-operational-outcome-signal.sh" "$TMP_REPO/scripts/"

run_test() {
  local test_name="$1"
  local story_content="$2"
  local should_warn="$3"  # "yes" or "no"
  local should_exit_code="${4:-0}"  # expected exit code (default 0)

  local story_file="$TMP_REPO/docs/stories/TEST-001.md"
  [ -z "$story_content" ] || echo "$story_content" > "$story_file"

  local output
  local exit_code=0
  output=$( cd "$TMP_REPO" && bash scripts/check-operational-outcome-signal.sh 2>&1 ) || exit_code=$?

  if [ "$exit_code" -ne "$should_exit_code" ]; then
    echo "✗ FAIL: $test_name"
    echo "  Expected exit code $should_exit_code, got $exit_code"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
    return 1
  fi

  local has_warning=0
  if echo "$output" | grep -q "::warning"; then
    has_warning=1
  fi

  if [ "$should_warn" = "yes" ] && [ "$has_warning" -eq 1 ]; then
    echo "✓ PASS: $test_name (warning correctly emitted, exit $exit_code)"
    PASS=$((PASS+1))
    return 0
  elif [ "$should_warn" = "no" ] && [ "$has_warning" -eq 0 ]; then
    echo "✓ PASS: $test_name (no warning, exit $exit_code)"
    PASS=$((PASS+1))
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected warning: $should_warn, Got warning: $has_warning"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
    return 1
  fi
}

# Test 1: Dirty fixture — operational:true 이지만 outcome-signal 3요소 미완
run_test "T1: outcome-signal ① terminal sink 미선언" \
'---
title: Test operational story
operational: true
---

# 테스트 스토리

## §7.4 운영 리스크

### §7.4.7 Operational throughput/scale

monotone progress metric: written rows count

발현조건 임계: >= 100 rows
' \
"yes"

# Test 2: Dirty fixture — §8.5 accumulation 기재 но soak 도출 미완
run_test "T2: soak 도출 (manifestation/duration) 미완" \
'---
title: Test operational story with accumulation
operational: true
---

# 테스트 스토리

## §8.5 Stateful/restart invariant tests

### §8.5.1 Long-running invariant tests

테스트 대상 invariant: cache eviction rate bound

부하 시나리오: 6시간 sustained load

**accumulation/lifetime-class 리스크**: in-memory cache 가 lifetime 동안 미회수 누적
' \
"yes"

# Test 3: Clean fixture — outcome-signal 3요소 완비
run_test "T3: outcome-signal 완비 (no warning)" \
'---
title: Test operational story complete
operational: true
---

# 테스트 스토리

## §7.4 운영 리스크

### §7.4.7 Operational throughput/scale

**① terminal downstream sink**: object-store parts path

**② monotone progress metric**: written parts count (단조 증가)

**③ 발현조건 임계**: >= 8 MiB/shard flush 누적

## §8.5 Stateful/restart invariant tests

### §8.5.1 Long-running invariant tests

**accumulation/lifetime-class 리스크**: 미회수 buffer 누적

**soak 구동 종점 (manifestation-derived)**: 발현조건 임계 >= 8 MiB/shard 도달까지 구동
' \
"no"

# Test 4: Clean fixture — duration floor fallback
run_test "T4: duration floor fallback (no warning)" \
'---
title: Test operational story with duration floor
operational: true
---

# 테스트 스토리

## §7.4 운영 리스크

### §7.4.7 Operational throughput/scale

**① terminal downstream sink**: message broker offset

**② monotone progress metric**: consumer-committed offset (단조 증가)

**③ 발현조건 임계**: >= 1000 messages/minute sustained

## §8.5 Stateful/restart invariant tests

### §8.5.1 Long-running invariant tests

**accumulation/lifetime-class 리스크**: redelivery queue overflow (발현 미정량)

**soak 최소 지속 (duration floor)**: >= 30분 고정 지속 + "발현조건 미상" 리스크 명시
' \
"no"

# Test 5: Non-operational story (no operational:true) → skip gracefully
run_test "T5: non-operational story skip" \
'---
title: Non-operational story
---

# 단순 스토리

일반 기능 추가로 operational 요구사항 없음
' \
"no"

# Test 6: Missing docs/stories directory → F1 guard detection (exit 0, no warning)
TMP_NO_STORIES=$(mktemp -d)
trap "rm -rf '$TMP_REPO' '$TMP_NO_STORIES'" EXIT
mkdir -p "$TMP_NO_STORIES/scripts"
cp "$REPO_ROOT/scripts/check-operational-outcome-signal.sh" "$TMP_NO_STORIES/scripts/"
# docs/stories 디렉터리 생성 안 함 (wrapper-self 상황 모의)

output=$( cd "$TMP_NO_STORIES" && bash scripts/check-operational-outcome-signal.sh 2>&1 ) || exit_code=$?
if [ "${exit_code:-0}" -eq 0 ] && ! echo "$output" | grep -q "::warning"; then
  echo "✓ PASS: T6: missing docs/stories (exit 0, no warning — F1 guard works)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T6: missing docs/stories (F1 guard not working)"
  echo "  Exit code: ${exit_code:-0}, Output: $output"
  FAIL=$((FAIL+1))
fi

# Summary
echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (discriminating test validates lint)"
  exit 0
else
  echo "Some tests failed (lint may not be detecting mutations correctly)"
  exit 1
fi
