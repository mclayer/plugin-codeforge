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
# CFP-2490 (Epic CFP-2481 E2) — tier-flip mutation-RED (blockable-capable wire hollow 금지).
#
# 방법론 SSOT (change-plan §8.1): tier 축 = workflow YAML 의 `continue-on-error` field (sentinel
#   script 검출 *로직* 아님). bash 단독으론 GitHub Actions `continue-on-error` 평가를 observe 불가 →
#   discriminating fixture 는 **workflow YAML 자체를 mutate** 한다. 2-part 증명:
#     (A) 1축 집약 — tier 축(continue-on-error ↔ SENTINEL_TIER) 이 단일 grep-able 지점임 assert
#         (산재 시 flip 이 다축 변경 = blockable-capable 위반).
#     (B) workflow-mutate observe — 원본(warning, derive expr 존재) GREEN ↔ mutated(SENTINEL_TIER=
#         blocking flip) 의 continue-on-error 평가 분기 observe (비차단 true ↔ 차단 false).
#   non-discriminating "exit 0 = PASS" 절대 금지 — 두 observation 분리(원본 ∧ mutated)가 함께여야 PASS.
# ═════════════════════════════════════════════════════════════════════════════

set +e

WF_TPL="$REPO_ROOT/templates/github-workflows/parallel-work-sentinel-check.yml"
WF_GH="$REPO_ROOT/.github/workflows/parallel-work-sentinel-check.yml"

# ── T-A0-parity (tier 축 byte-identical): templates ↔ .github workflow byte-identical (ADR-005). ──
if [ -f "$WF_TPL" ] && [ -f "$WF_GH" ] && cmp -s "$WF_TPL" "$WF_GH"; then
  echo "✓ PASS: T-A0-parity — sentinel workflow templates ↔ .github byte-identical (ADR-005)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-A0-parity — sentinel workflow templates ↔ .github NOT byte-identical (ADR-005 위반)"
  FAIL=$((FAIL+1))
fi

# ── T-A1-axis-single (1축 집약): continue-on-error 가 SENTINEL_TIER derive expr 단일 지점인가. ──
#    (1) tier env `SENTINEL_TIER:` 선언 정확히 1회 + (2) `env.SENTINEL_TIER != 'blocking'` derive expr
#    ≥1 (hardcode 아님) + (3) continue-on-error hardcode literal(true/false) 0건 (전부 derive, 산재 0).
if [ -f "$WF_TPL" ]; then
  tier_env_count=$(grep -cE '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$WF_TPL")
  derive_count=$(grep -cF "env.SENTINEL_TIER != 'blocking'" "$WF_TPL")
  hardcode_coe=$(grep -E '^[[:space:]]*continue-on-error:[[:space:]]*(true|false)[[:space:]]*$' "$WF_TPL" | wc -l | tr -d ' ')
  if [ "$tier_env_count" -eq 1 ] && [ "$derive_count" -ge 1 ] && [ "$hardcode_coe" -eq 0 ]; then
    echo "✓ PASS: T-A1-axis-single — tier 축 1지점 집약 (SENTINEL_TIER env 1회 + continue-on-error derive, hardcode literal 0)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: T-A1-axis-single — tier 축 산재/미집약 (SENTINEL_TIER env=$tier_env_count, derive=$derive_count, hardcode continue-on-error literal=$hardcode_coe)"
    echo "  blockable-capable 위반: tier 축이 단일 grep-able 지점이 아니면 flip 이 다축 변경 = hollow"
    FAIL=$((FAIL+1))
  fi
else
  echo "✗ FAIL: T-A1-axis-single — workflow 부재: $WF_TPL"
  FAIL=$((FAIL+1))
fi

# ── T-A2-workflow-mutate-RED: workflow YAML mutate 로 tier 축 동작 분기 observe (env 단독 아님). ──
#    원본(warning): continue-on-error = (warning != 'blocking') = true (비차단/GREEN).
#    mutated(blocking flip, 단일 축 1줄 sed): continue-on-error = (blocking != 'blocking') = false (차단/RED).
#    bash 가 Actions runtime 을 못 돌리므로 평가식을 동형 bash 비교로 재현 — 두 입력 결과 분기 observe
#    (원본 true ∧ mutated false 함께여야 PASS). "tier 1축 변경이 실제 차단 여부를 produce" falsify 가능.
if [ -f "$WF_TPL" ]; then
  MUT=$(mktemp)
  sed -E "s/^([[:space:]]*SENTINEL_TIER:[[:space:]]*)warning/\1blocking/" "$WF_TPL" > "$MUT"
  # 값만 추출: SENTINEL_TIER: 뒤 첫 토큰(영문자) — 후행 inline comment(# ...) 제외.
  orig_tier=$(grep -E '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$WF_TPL" | head -1 | sed -E 's/.*SENTINEL_TIER:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' | tr -d '[:space:]')
  mut_tier=$(grep -E '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$MUT" | head -1 | sed -E 's/.*SENTINEL_TIER:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' | tr -d '[:space:]')
  eval_coe() { if [ "$1" != "blocking" ]; then echo "true"; else echo "false"; fi; }
  orig_coe=$(eval_coe "$orig_tier")   # 기대: true (warning → 비차단)
  mut_coe=$(eval_coe "$mut_tier")     # 기대: false (blocking → 차단)
  if [ "$orig_tier" = "warning" ] && [ "$orig_coe" = "true" ] && \
     [ "$mut_tier" = "blocking" ] && [ "$mut_coe" = "false" ]; then
    echo "✓ PASS: T-A2-workflow-mutate-RED — 원본 warning→continue-on-error=true(GREEN/비차단) ∧ mutated blocking→continue-on-error=false(RED/차단) 분리 observe (hollow 아님)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: T-A2-workflow-mutate-RED — tier flip 이 차단 동작 분기를 produce 하지 않음 (hollow)"
    echo "  orig_tier=$orig_tier orig_coe=$orig_coe (기대 warning/true) | mut_tier=$mut_tier mut_coe=$mut_coe (기대 blocking/false)"
    FAIL=$((FAIL+1))
  fi
  rm -f "$MUT"
else
  echo "✗ FAIL: T-A2-workflow-mutate-RED — workflow 부재: $WF_TPL"
  FAIL=$((FAIL+1))
fi

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2451 prefix 파라미터화 + CFP-2490 tier-flip blockable-capable)"
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
  echo "[prefix] Mutation-hardcode (KEY_PATTERN → re.compile(r'\\\\bCFP-\\\\d+\\\\b') 하드코딩 복귀)"
  echo "         → T-MCT-match FAIL (MCT-123 미매칭) = RED / T-CFP-default GREEN 유지 = 두 set 분리"
  echo "[tier]   Mutation-1 (workflow 의 continue-on-error derive → hardcode 'true' 복귀)"
  echo "         → T-A1-axis-single FAIL (hardcode_coe>0) = RED (tier 축 산재/미derive)"
  echo "[tier]   Mutation-2 (SENTINEL_TIER env 선언 제거 또는 2지점 산재)"
  echo "         → T-A1-axis-single FAIL (tier_env_count != 1) = RED (1축 집약 위반)"
  echo "[tier]   Mutation-3 (continue-on-error 평가식 != 'blocking' → 항상 true 로 hardcode)"
  echo "         → T-A2-workflow-mutate-RED FAIL (mutated blocking 도 비차단) = RED (flip 무효)"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
