#!/usr/bin/env bash
# tests/scripts/test_check-parallel-work-sentinel.sh
# CFP-2451 (CFP-967 Phase 2 deferred wire 완성) — Discriminating self-test for
#   scripts/lib/check_parallel_work_sentinel.py STORY_KEY_PREFIX 파라미터화.
#
# 배경: sentinel 의 KEY prefix 가 "CFP" 로 하드코딩되면 consumer (prefix != "CFP",
#   예: mctrader="MCT") 에서 자기 중복작업을 못 잡는 inert(hollow) 검사가 된다.
#   CFP-2451 이 prefix 를 STORY_KEY_PREFIX env 로 파라미터화 → 본 테스트가 그 동작을 보증.
#
# self-contained bash (bats 미사용 — test_check-responsibility-marker-drift.sh 답습).
#   title-search 모드 + gh mock seam(CFP967_GH_MOCK_RESPONSE) 으로 issue list 를 주입하고,
#   STORY_KEY_PREFIX 에 따라 title filter 가 어떻게 동작하는지 exit code + matches 내용으로 assert.
#
# Discriminating 의무 (change-plan §8): 단순 "exit 0 = PASS" 검사는 non-discriminating
#   (정상 GREEN 과 hollow 구분 불가) → 금지. matches 배열의 *내용*을 assert:
#     - STORY_KEY_PREFIX=MCT 일 때 [MCT-123] title 은 matches 에 *포함*되고
#     - prefix 미스매치 title([CFP-1]) 은 matches 에서 *제외*된다.
#   이 두 조건이 함께여야 prefix 파라미터화가 hollow 가 아님을 증명.
#
# Mutation-RED 입증 (change-plan §8 SSOT): KEY_PATTERN 을 다시 re.compile(r"\bCFP-\d+\b")
#   하드코딩으로 되돌리면 — T-MCT-match (MCT-123 매칭 기대) 가 FAIL 해야 한다(MCT 가 안 잡힘).
#   동시에 T-CFP-default (기본 CFP 동작) 는 GREEN 유지. 두 set 분리로 hollow 검사 차단.
#   (수동 mutation-RED 실행 절차 = change-plan §8 — prefix 하드코딩 임시 복귀 → 본 테스트 FAIL 확인 → 원복.)
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates prefix parameterization)
#  1 = any fixture fails (prefix may not be parameterized / regressed to hardcode)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-parallel-work-sentinel.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# write_mock: gh issue list JSON fixture 작성 (title-search mock seam 입력).
#   write_mock <path> <heredoc-via-stdin>
# ─────────────────────────────────────────────────────────────────────────────
write_mock() {
  local path="$1"
  cat > "$path"
}

# ─────────────────────────────────────────────────────────────────────────────
# run_case: sentinel title-search 를 mock + env 로 호출 → exit code + grep assert.
#   $1=name  $2=story_key_prefix  $3=cfp_context  $4=mock_file
#   $5=expected_exit  $6=grep_present(있어야 함)  $7=grep_absent(없어야 함)  $8=description
#   grep_present/grep_absent 가 빈 문자열이면 해당 assert skip.
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" prefix="$2" ctx="$3" mock="$4" expected_exit="$5"
  local present="$6" absent="$7" description="$8"
  local out exit_code=0
  out=$(
    STORY_KEY_PREFIX="$prefix" \
    CFP_CONTEXT="$ctx" \
    CFP967_GH_MOCK_RESPONSE="$mock" \
    bash "$WRAPPER" --mode=title-search 2>&1
  ) || exit_code=$?

  local ok=1
  [ "$exit_code" -eq "$expected_exit" ] || ok=0
  if [ -n "$present" ]; then
    echo "$out" | grep -qF "$present" || ok=0
  fi
  if [ -n "$absent" ]; then
    if echo "$out" | grep -qF "$absent"; then ok=0; fi
  fi

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code"
    [ -n "$present" ] && echo "  Expected present: '$present'"
    [ -n "$absent" ]  && echo "  Expected absent:  '$absent'"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# fixture: 동일 mock JSON 을 두 케이스에서 공유. 두 issue title:
#   - [MCT-123] consumer prefix title
#   - [CFP-1]   wrapper prefix title (consumer 관점 미스매치)
MOCK=$(mktemp)
trap 'rm -f "$MOCK"' EXIT
write_mock "$MOCK" <<'EOF'
[
  {"number": 123, "title": "[MCT-123] consumer parallel-work title", "labels": [{"name": "phase:구현"}], "closedAt": null},
  {"number": 1, "title": "[CFP-1] wrapper-prefix title", "labels": [], "closedAt": null}
]
EOF

set +e

# ═════════════════════════════════════════════════════════════════════════════
# T-MCT-match: STORY_KEY_PREFIX=MCT + search_fragment 존재 → [MCT-123] 매칭(포함),
#   prefix 미스매치 [CFP-1] 은 필터링(제외). prefix 파라미터화가 동작함을 증명.
#   ★ Mutation-RED kill: KEY_PATTERN 하드코딩(CFP) 복귀 시 MCT-123 미매칭 → present assert FAIL = RED.
# ═════════════════════════════════════════════════════════════════════════════
run_case "T-MCT-match" "MCT" "MCT-123" "$MOCK" "0" \
  '"number": 123' '"number": 1,' \
  "STORY_KEY_PREFIX=MCT → [MCT-123] 매칭(포함) + 미스매치 [CFP-1] 제외 (hollow 아님 증명)"

# ═════════════════════════════════════════════════════════════════════════════
# T-CFP-default: STORY_KEY_PREFIX=CFP(기본) + search_fragment 존재 → [CFP-1] 매칭(포함),
#   prefix 미스매치 [MCT-123] 은 필터링(제외). 기본(wrapper) 동작 무변경 = 하위호환.
#   ★ 두 set 분리: 이 케이스는 Mutation-RED(prefix 하드코딩 복귀) 에서도 GREEN 유지.
# ═════════════════════════════════════════════════════════════════════════════
run_case "T-CFP-default" "CFP" "CFP-1" "$MOCK" "0" \
  '"number": 1' '"number": 123' \
  "STORY_KEY_PREFIX=CFP(기본) → [CFP-1] 매칭 + [MCT-123] 제외 (하위호환 보존)"

# ═════════════════════════════════════════════════════════════════════════════
# T-prefix-unset-defaults-CFP: STORY_KEY_PREFIX 미설정 → 기본값 "CFP" 로 degrade.
#   env 미주입(wrapper self-app / overlay 부재) 시 동작 무변경 보증.
# ═════════════════════════════════════════════════════════════════════════════
out=$(
  unset STORY_KEY_PREFIX
  CFP_CONTEXT="CFP-1" \
  CFP967_GH_MOCK_RESPONSE="$MOCK" \
  bash "$WRAPPER" --mode=title-search 2>&1
)
ec=$?
if [ "$ec" -eq 0 ] && echo "$out" | grep -qF '"number": 1' && ! echo "$out" | grep -qF '"number": 123'; then
  echo "✓ PASS: T-prefix-unset-defaults-CFP (exit $ec) — STORY_KEY_PREFIX 미설정 → 기본 CFP degrade (env 부재 무변경)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-prefix-unset-defaults-CFP"
  echo "  Expected exit 0 + [CFP-1] 포함 + [MCT-123] 제외; got exit $ec"
  echo "  Output: $out"
  FAIL=$((FAIL+1))
fi

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2451 parallel-work-sentinel prefix 파라미터화)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (change-plan §8 — hollow 검사 차단):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "Mutation-hardcode (KEY_PATTERN → re.compile(r'\\\\bCFP-\\\\d+\\\\b') 하드코딩 복귀)"
  echo "                   → T-MCT-match FAIL (MCT-123 미매칭) = RED"
  echo "                   → T-CFP-default GREEN 유지 = 두 set 분리(hollow 아님 증명)"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
