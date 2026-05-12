#!/usr/bin/env bash
# test_check_impl_manifest_ac_mapping.sh
# CFP-491 — check-impl-manifest-ac-mapping.sh 단위 테스트 (3 test case)
#
# Usage:
#   bash tests/scripts/test_check_impl_manifest_ac_mapping.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../..")
HELPER="$REPO_ROOT/scripts/check-impl-manifest-ac-mapping.sh"

# Color output (TERM-aware)
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  NC='\033[0m'
else
  RED=''
  GREEN=''
  NC=''
fi

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_true() {
  local desc="$1"
  local condition="$2"

  TESTS_RUN=$((TESTS_RUN + 1))
  if eval "$condition"; then
    echo -e "${GREEN}PASS${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}FAIL${NC} $desc"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

echo "==================================================================="
echo "CFP-491 — check-impl-manifest-ac-mapping.sh 단위 테스트"
echo "Target: $HELPER"
echo "==================================================================="
echo ""

# Pre-flight — helper file 존재 확인
if [[ ! -f "$HELPER" ]]; then
  echo -e "${RED}FATAL${NC} helper script 부재: $HELPER"
  exit 2
fi

# ─── temp file 관리 ────────────────────────────────────────────────────────

TMPFILES=()
cleanup() {
  for f in "${TMPFILES[@]+"${TMPFILES[@]}"}"; do
    [[ -f "$f" ]] && rm -f "$f"
  done
}
trap cleanup EXIT

make_story_file() {
  local tmpfile
  tmpfile="$(mktemp /tmp/test_story_XXXXXX.md)"
  TMPFILES+=("$tmpfile")
  cat > "$tmpfile"
  echo "$tmpfile"
}

# ─── test case 1: drift case ───────────────────────────────────────────────
# §5.1 정의 = AC-1, AC-2 / §8.5 cite = AC-1, AC-2, AC-3
# 기본 mode 실행 → stderr 에 AC-3 포함 + exit 0

echo "[1/3] drift case — §8.5 에 미정의 AC-3 참조"
echo "-------------------------------------------------------------------"

DRIFT_STORY="$(make_story_file <<'STORYEOF'
# CFP-TEST Story

## §5 요구사항

### §5.1 AC 정의

- AC-1: 기능 A 구현
- AC-2: 기능 B 구현

## §8.5 Impl Manifest

구현 내용:
- AC-1 관련 구현
- AC-2 관련 구현
- AC-3 관련 구현
STORYEOF
)"

STDERR_DRIFT="$(bash "$HELPER" "$DRIFT_STORY" 2>&1 1>/dev/null || true)"
EXIT_DRIFT=$?

assert_true "(1a) exit 0 — 기본 mode advisory (drift 있어도 exit 0)" \
  "[ $EXIT_DRIFT -eq 0 ]"

assert_true "(1b) stderr 에 'AC-3' 포함 — drift 감지 출력" \
  "echo \"\$STDERR_DRIFT\" | grep -q 'AC-3'"

assert_true "(1c) stderr 에 'WARN' 포함" \
  "echo \"\$STDERR_DRIFT\" | grep -q 'WARN'"

echo ""

# ─── test case 2: OK case ─────────────────────────────────────────────────
# §5.1 정의 = AC-1, AC-2, AC-3 / §8.5 cite = AC-1, AC-2
# exit 0 + stdout 에 'OK §8.5 → §5.1' 포함

echo "[2/3] OK case — §8.5 cite 가 §5.1 정의 부분집합"
echo "-------------------------------------------------------------------"

OK_STORY="$(make_story_file <<'STORYEOF'
# CFP-TEST Story

## §5 요구사항

### §5.1 AC 정의

- AC-1: 기능 A 구현
- AC-2: 기능 B 구현
- AC-3: 기능 C 구현

## §8.5 Impl Manifest

구현 내용:
- AC-1 관련 구현
- AC-2 관련 구현
STORYEOF
)"

STDOUT_OK="$(bash "$HELPER" "$OK_STORY" 2>/dev/null)"
EXIT_OK=$?

assert_true "(2a) exit 0 — drift 0건 PASS" \
  "[ $EXIT_OK -eq 0 ]"

assert_true "(2b) stdout 에 'OK §8.5 → §5.1' 포함" \
  "echo \"\$STDOUT_OK\" | grep -q 'OK §8.5 → §5.1'"

echo ""

# ─── test case 3: strict mode case ────────────────────────────────────────
# drift case 동일 fixture + --strict flag → exit 1

echo "[3/3] strict mode case — --strict flag + drift 시 exit 1"
echo "-------------------------------------------------------------------"

# drift case 와 동일 Story file 재사용
EXIT_STRICT=0
bash "$HELPER" --strict "$DRIFT_STORY" >/dev/null 2>&1 || EXIT_STRICT=$?

assert_true "(3a) exit 1 — --strict mode + drift 발견" \
  "[ $EXIT_STRICT -eq 1 ]"

echo ""
echo "==================================================================="
echo "Test summary: $TESTS_PASSED / $TESTS_RUN passed, $TESTS_FAILED failed"
echo "==================================================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi

exit 0
