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

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2490 (Epic CFP-2481 E2) — blockable-capable tier 축 mutation-RED (workflow-mutate fixture)
#
# 방법론 SSOT = change-plan §8.1 (설계리뷰 FIX iter1): blockable-capable 이 hollow 가 아님을
#   증명하려면 *무엇을 mutate 해 무엇을 observe 하는가* 가 명시돼야 한다. tier 축은 sentinel
#   script 의 검출 *로직* 이 아니라 **workflow YAML 의 `continue-on-error` field** 다 — bash
#   harness 가 SENTINEL_TIER env 를 set 해도 GitHub Actions `continue-on-error` 평가는 Actions
#   runtime 만 수행하므로 bash 단독으론 blocking step-fail 을 observe 할 수 없다. 따라서
#   discriminating fixture 는 **workflow YAML 자체를 mutate** 하는 형태여야 한다.
#
# act 미가용 환경 fallback (change-plan §8.1 (b)) = 2-part 증명:
#   part-1 (1축 집약 structural assert): tier 축(continue-on-error ↔ SENTINEL_TIER 단일 binding)이
#     workflow YAML 안 **단일 grep-able 지점** 임을 assert. 산재하면 flip 이 다축 변경 =
#     blockable-capable 위반.
#   part-2 (tier 축이 신호의 차단 여부를 1축으로 결정): workflow 의 continue-on-error 표현식을
#     GitHub Actions expression semantics 로 직접 evaluate —
#       T-A1 (원본 warning GREEN): SENTINEL_TIER=warning → `SENTINEL_TIER != 'blocking'` = true
#                                  → continue-on-error=true → sentinel step fail 해도 job GREEN.
#       T-A2 (blocking-mutate RED): SENTINEL_TIER=blocking → 동일 표현식 = false
#                                  → continue-on-error=false → sentinel step fail 시 job RED.
#   T-A1 ∧ T-A2 가 함께여야 hollow 아님 (env 단독 아닌 YAML 의 tier 축 evaluate, AC-3).
#
# Mutation-RED kill: tier 축 binding 을 `continue-on-error: true` 하드코딩(SENTINEL_TIER 무시)
#   으로 되돌리면 — part-1 (단일 binding grep) FAIL ∧ T-A2 (blocking 에서도 true) FAIL = RED.
# ═════════════════════════════════════════════════════════════════════════════

# tier 축 = .github/ + templates/ 양쪽 byte-identical (ADR-005). 양쪽 모두 검사.
WF_GITHUB="$REPO_ROOT/.github/workflows/parallel-work-sentinel-check.yml"
WF_TEMPLATE="$REPO_ROOT/templates/github-workflows/parallel-work-sentinel-check.yml"

# GitHub Actions expression `SENTINEL_TIER != 'blocking'` 을 셸에서 동형 evaluate.
#   (Actions 의 != 는 case-insensitive string 비교 — 본 fixture 는 lowercase 고정값만 사용.)
eval_continue_on_error() {
  local tier="$1"
  if [ "$tier" != "blocking" ]; then echo "true"; else echo "false"; fi
}

set +e

# ─── part-1: tier 축 1축 집약 (single grep-able binding) structural assert ───
for WF in "$WF_GITHUB" "$WF_TEMPLATE"; do
  WF_NAME="$(basename "$(dirname "$(dirname "$WF")")")/$(basename "$WF")"

  # (1a) continue-on-error 표현식이 정확히 1개 + SENTINEL_TIER 에서 derive (하드코딩 아님).
  COE_LINES=$(grep -cE '^\s*continue-on-error:' "$WF" 2>/dev/null || echo 0)
  COE_DERIVED=$(grep -cE "continue-on-error:\s*\\\$\{\{\s*env\.SENTINEL_TIER\s*!=\s*'blocking'\s*\}\}" "$WF" 2>/dev/null || echo 0)
  # (1b) SENTINEL_TIER 의 단일 정의 지점 (workflow env: 블록) + default=warning.
  TIER_DEF=$(grep -cE "^\s*SENTINEL_TIER:\s*warning\s*$" "$WF" 2>/dev/null || echo 0)

  if [ "$COE_LINES" -eq 1 ] && [ "$COE_DERIVED" -eq 1 ] && [ "$TIER_DEF" -eq 1 ]; then
    echo "✓ PASS: T-A-tier-single-axis ($WF_NAME) — continue-on-error 1개 ∧ SENTINEL_TIER derive ∧ default=warning (1축 집약, blockable-capable)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: T-A-tier-single-axis ($WF_NAME)"
    echo "  continue-on-error 라인수=$COE_LINES (기대 1), SENTINEL_TIER-derive=$COE_DERIVED (기대 1), default-warning 정의=$TIER_DEF (기대 1)"
    echo "  → tier 축이 단일 grep-able 지점이 아니거나 continue-on-error 하드코딩 복귀 (mutation-RED kill)"
    FAIL=$((FAIL+1))
  fi
done

# ─── part-2: tier 축이 차단 여부를 1축으로 결정 (continue-on-error expr evaluate) ───
# 실 workflow 의 continue-on-error 표현식을 추출 → SENTINEL_TIER 값을 mutate 한 evaluate.
#   T-A1 (원본 warning): 평가 = true (비차단 GREEN) / T-A2 (blocking mutate): 평가 = false (차단 RED).

# T-A1: 원본 tier(=workflow env default warning) → continue-on-error=true → GREEN
DEFAULT_TIER=$(grep -E "^\s*SENTINEL_TIER:" "$WF_GITHUB" | head -1 | sed -E "s/.*SENTINEL_TIER:\s*//; s/\s*$//")
COE_DEFAULT=$(eval_continue_on_error "$DEFAULT_TIER")
if [ "$DEFAULT_TIER" = "warning" ] && [ "$COE_DEFAULT" = "true" ]; then
  echo "✓ PASS: T-A1 (원본 warning GREEN) — SENTINEL_TIER=$DEFAULT_TIER → continue-on-error=$COE_DEFAULT (검출돼도 비차단)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-A1 (원본 warning GREEN)"
  echo "  workflow default SENTINEL_TIER='$DEFAULT_TIER' (기대 warning), continue-on-error=$COE_DEFAULT (기대 true)"
  FAIL=$((FAIL+1))
fi

# T-A2 (workflow-mutate RED): 실 workflow YAML 의 continue-on-error 표현식을 **추출**해, 그 표현식이
#   SENTINEL_TIER=blocking 일 때 false 로 평가되는지 확인 (= blocking 으로 mutate 하면 차단 전환).
#   표현식을 workflow 에서 직접 추출하므로 continue-on-error 하드코딩(true) 복귀 시 추출 표현식이
#   SENTINEL_TIER 무관 = blocking 에서도 true → 본 assert FAIL = mutation-RED kill (workflow-mutate 민감).
COE_EXPR=$(grep -E '^\s*continue-on-error:' "$WF_GITHUB" | head -1 | sed -E 's/^\s*continue-on-error:\s*//; s/\s*$//')
# 추출 표현식이 SENTINEL_TIER 를 참조하면 (tier-derived) → blocking 일 때 false 로 평가. 그렇지 않으면
#   (하드코딩 true/false) → tier 무관 → blocking 에서도 동일 → mutation-RED 대상.
A2_EVAL="HARDCODE"
if echo "$COE_EXPR" | grep -qE "SENTINEL_TIER\s*!=\s*'blocking'"; then
  # tier-derived 표현식 — SENTINEL_TIER=blocking 대입 시 (blocking != blocking)=false
  A2_EVAL="false"
fi
if [ "$A2_EVAL" = "false" ]; then
  echo "✓ PASS: T-A2 (blocking-mutate RED, tier-축 차단전환) — workflow continue-on-error 표현식 = '$COE_EXPR' → SENTINEL_TIER=blocking 대입 시 false (sentinel step fail → job RED)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-A2 (blocking-mutate RED)"
  echo "  workflow continue-on-error 표현식 = '$COE_EXPR' (SENTINEL_TIER 미참조 = 하드코딩) → blocking mutate 시 차단 전환 안 함 = blockable-capable 위반/hollow"
  FAIL=$((FAIL+1))
fi

# T-A2-script-signal: sentinel script 가 *검출 시* non-zero exit (차단 신호) 을 내는지 확인.
#   (blocking tier 에서 continue-on-error=false 이려면 step 이 fail 가능해야 = script non-zero 가능.)
#   mock: 중복작업 후보를 강하게 주입해 sentinel 이 hit-signal exit code 를 내는 케이스 검증.
#   sentinel title-search 는 hit 시 exit 0 + matches JSON (warning advisory 설계) — 따라서
#   "차단 신호" 는 workflow 의 grep 기반 검출이 아니라 step run 의 `exit $?` 경로다.
#   본 assert 는 workflow run-step 이 sentinel 검출 결과를 exit code 로 surface 하도록 wire 됐는지
#   (즉 OUT 비-empty 시 차단 가능 경로 존재) 를 workflow 구조로 확인: blocking 시 step 이
#   continue-on-error=false 인 동일 step 이 sentinel 을 실행한다는 binding 을 grep.
SENTINEL_RUN_BOUND=$(grep -A30 "continue-on-error:.*SENTINEL_TIER" "$WF_GITHUB" | grep -cE "check-parallel-work-sentinel\.sh" 2>/dev/null || echo 0)
if [ "$SENTINEL_RUN_BOUND" -ge 1 ]; then
  echo "✓ PASS: T-A2-binding — tier 축(continue-on-error) 이 sentinel run step 과 동일 step 에 binding (차단 대상 = sentinel 검출)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-A2-binding — continue-on-error tier 축이 sentinel run step 과 분리됨 (차단해도 sentinel 무관 = hollow)"
  FAIL=$((FAIL+1))
fi

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2451 prefix 파라미터화 + CFP-2490 blockable-capable tier)"
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
  echo "[CFP-2451 prefix] Mutation-hardcode (KEY_PATTERN → re.compile(r'\\\\bCFP-\\\\d+\\\\b') 하드코딩 복귀)"
  echo "                   → T-MCT-match FAIL (MCT-123 미매칭) = RED"
  echo "                   → T-CFP-default GREEN 유지 = 두 set 분리(hollow 아님 증명)"
  echo ""
  echo "[CFP-2490 tier] Mutation-hardcode (continue-on-error: \${{ env.SENTINEL_TIER != 'blocking' }}"
  echo "                   → continue-on-error: true 하드코딩 복귀, SENTINEL_TIER 무시)"
  echo "                   → T-A-tier-single-axis FAIL (SENTINEL_TIER-derive=0) = RED"
  echo "                   → T-A2 FAIL (blocking 에서도 true = tier flip 무효) = RED"
  echo "                   → T-A1 (warning GREEN) 유지 = 두 조건 분리(hollow 아님 증명, AC-3)"
  echo "                workflow-mutate: SENTINEL_TIER: blocking → continue-on-error=false → 차단 RED 관측"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
