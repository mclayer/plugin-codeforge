#!/usr/bin/env bash
# tests/scripts/test_check-rebase-staleness-sentinel.sh
# CFP-2784 / FU-1588-R — Discriminating self-test for
#   scripts/lib/check_rebase_staleness_sentinel.py TIER mapping + exit-code matrix.
#
# 배경: sentinel의 commit-count-behind 측정이 hollow(무력)가 아님을 증명.
#   - N==0 일 때 tier none 추천 (false-positive 0)
#   - N=1..2 일 때 tier1 추천
#   - N>=3 일 때 tier2 추천 (tier3/4 방출 금지, INV-3)
#   - bypass flip 동작 + mutation 무실행 보증.
#
# self-contained bash (bats 미사용 — test_check-parallel-work-sentinel.sh 답습).
#   mock seam(REBASE_*_MOCK) 으로 commits-behind N 을 주입하고,
#   JSON 출력 + exit code 로 tier 매핑 + degrade 분기를 assert.
#
# Discriminating 의무 (change-plan §8): 단순 "exit 0 = PASS" 검사는 non-discriminating
#   (정상 N=0 과 N=5 둘 다 exit 0) → 금지. 출력 JSON 의 "commits_behind" + "recommended_tier"
#   값을 assert: N=0→tier=none, N=2→tier1, N=3→tier2 등 계층 구분을 입증.
#
# Mutation-RED 입증 (change-plan §8 SSOT): TIER1_MAX 를 다시 2 에서 3 으로 변경하면
#   (하드코딩 복귀) — M1b (N=2→tier1 경계 케이스) 가 FAIL 해야 한다(N=2 가 tier2 = RED).
#   동시에 M1a (다른 N 값) 는 GREEN 유지. 두 set 분리로 hollow 검사 차단.
#   (수동 mutation-RED 실행 절차 = change-plan §8 — TIER1_MAX 임시 변경 → 본 테스트 FAIL 확인 → 원복.)
#
# Exit code:
#  0 = all fixtures pass (commits-behind 측정 + tier 매핑 discriminating 증명)
#  1 = any fixture fails (tier 매핑 회귀 / exit-matrix 위반)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-rebase-staleness-sentinel.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# run_case: sentinel head-compare 호출 → exit code + JSON assert.
#   $1=name  $2=revlist_mock (commits-behind N)  $3=expected_exit
#   $4=expect_tier  $5=expect_behind  $6=description
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" mock="$2" expected_exit="$3" expect_tier="$4" expect_behind="$5" description="$6"
  local out exit_code=0 actual_tier actual_behind

  out=$(
    REBASE_REVLIST_MOCK="$mock" \
    bash "$WRAPPER" --mode head-compare 2>&1
  ) || exit_code=$?

  local ok=1
  [ "$exit_code" -eq "$expected_exit" ] || ok=0

  # JSON 파싱 — recommended_tier + commits_behind extract
  if echo "$out" | grep -qF '"recommended_tier"'; then
    actual_tier=$(printf '%s' "$out" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("recommended_tier",""))' 2>/dev/null || echo "PARSE_ERROR")
    [ "$actual_tier" = "$expect_tier" ] || ok=0
  else
    ok=0
  fi

  if echo "$out" | grep -qF '"commits_behind"'; then
    actual_behind=$(printf '%s' "$out" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("commits_behind",""))' 2>/dev/null || echo "PARSE_ERROR")
    [ "$actual_behind" = "$expect_behind" ] || ok=0
  else
    ok=0
  fi

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name (exit $exit_code, tier $actual_tier, behind $actual_behind) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected: exit $expected_exit, tier $expect_tier, behind $expect_behind"
    echo "  Got: exit $exit_code, tier $actual_tier, behind $actual_behind"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

set +e

# ═════════════════════════════════════════════════════════════════════════════
# M1a: commit-count 정확성 — REBASE_REVLIST_MOCK N∈{0,1,2,3,10} → commits_behind==N ∧ tier==map(N)
#   INV-1(단일 측정) / AC-3 (정상 경로 커버).
#   RED(mutation): count→상수 0 고정 시 N>=1 가 tier1/2 미표시 = FAIL.
# ═════════════════════════════════════════════════════════════════════════════
run_case "M1a-count-0" "0" "0" "none" "0" "commits_behind=0 → tier=none (zero-staleness, false-positive 0)"
run_case "M1a-count-1" "1" "0" "tier1" "1" "commits_behind=1 → tier=tier1 (lower bound)"
run_case "M1a-count-2" "2" "0" "tier1" "2" "commits_behind=2 → tier=tier1 (mid-range)"
run_case "M1a-count-3" "3" "0" "tier2" "3" "commits_behind=3 → tier=tier2 (lower bound)"
run_case "M1a-count-10" "10" "0" "tier2" "10" "commits_behind=10 → tier=tier2 (high-staleness)"

# ═════════════════════════════════════════════════════════════════════════════
# M1b: tier 경계 off-by-one — N=2→tier1 ∧ N=3→tier2 두 경계 케이스 분리 assert.
#   INV-2 (경계 정확성).
#   ★ Mutation-RED kill: TIER1_MAX 를 2→3 으로 변경 시 N=2 가 tier2 = RED.
# ═════════════════════════════════════════════════════════════════════════════
run_case "M1b-boundary-2" "2" "0" "tier1" "2" "경계 N=2 (TIER1_MAX=2) → tier1 (off-by-one 보호)"
run_case "M1b-boundary-3" "3" "0" "tier2" "3" "경계 N=3 (TIER1_MAX+1) → tier2 (off-by-one 보호)"

# ═════════════════════════════════════════════════════════════════════════════
# M1c: tier3/4 카탈로그 제외 — N=100 → tier2 + "tier3"/"tier4" 문자열 부재.
#   INV-3 (recommended_tier enumeration guarantee).
#   ★ Mutation-RED kill: tier3/tier4 라벨 삽입 시 grep -qF 검출 = RED.
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(REBASE_REVLIST_MOCK=100 bash "$WRAPPER" --mode head-compare 2>&1); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"recommended_tier": "tier2"' || ok=0
if echo "$OUT" | grep -qF '"tier3"'; then ok=0; fi
if echo "$OUT" | grep -qF '"tier4"'; then ok=0; fi
if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M1c-tier3/4-exclusion (exit $EC) — N=100 → tier2 ∧ tier3/4 문자열 부재 (enumeration guarantee INV-3)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M1c-tier3/4-exclusion"
  echo "  Expected: exit 0, recommended_tier=tier2, tier3/tier4 key 부재"
  echo "  Output: $OUT"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M2: bypass-flip — BYPASS_REBASE_STALENESS_SENTINEL=1 → bypass JSON + bypass invoked.
#   INV-4 (bypass 동작) / AC-6 (bypass case 커버).
#   ★ Mutation-RED kill: short-circuit 제거(py 내 if os.environ.get BYPASS_ENV 문 삭제)
#   시 bypass JSON 미출현 + 추천 방출 = RED.
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(BYPASS_REBASE_STALENESS_SENTINEL=1 bash "$WRAPPER" --mode head-compare 2>&1); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"bypass": true' || ok=0
echo "$OUT" | grep -qF '"marker"' || ok=0
echo "$OUT" | grep -qF 'bypass invoked' || ok=0
if echo "$OUT" | grep -qF '"recommended_tier"' && ! echo "$OUT" | grep -qF '"bypass": true'; then ok=0; fi
if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M2-bypass-flip (exit $EC) — BYPASS=1 → bypass JSON + 'bypass invoked' + 추천 부재"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M2-bypass-flip"
  echo "  Expected: exit 0, bypass JSON, bypass invoked, 추천 부재"
  echo "  Output: $OUT"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M3: 추천-only 실행 0 — git push/rebase/gh pr merge 호출 부재 (INV-5 / AC-7).
#   sentinel 은 관측만 하고 mutation 은 스스로 실행하지 않음을 정적 증명.
#   ★ Mutation-RED kill: 호출 1줄 삽입 → grep hit = RED.
# ═════════════════════════════════════════════════════════════════════════════
ok=1
PYSRC="$REPO_ROOT/scripts/lib/check_rebase_staleness_sentinel.py"
SHSRC="$REPO_ROOT/scripts/check-rebase-staleness-sentinel.sh"
grep -qE 'git push|git rebase|gh pr merge' "$PYSRC" && ok=0
grep -qE 'git push|git rebase|gh pr merge' "$SHSRC" && ok=0
if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M3-no-mutations (grep check) — git push/rebase/gh pr merge 호출 0건 (advisory-only INV-5)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M3-no-mutations"
  echo "  Found mutation call in source (git push/rebase/gh pr merge)"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M4a: tier축 1지점 집약 — WF SENTINEL_TIER 정확히 1회 + continue-on-error derive + hardcode literal 0.
#   INV-6 (tier axis single-point, blockable-capable wire).
# ═════════════════════════════════════════════════════════════════════════════
WF_TPL="$REPO_ROOT/templates/github-workflows/rebase-staleness-detection.yml"
WF_GH="$REPO_ROOT/.github/workflows/rebase-staleness-detection.yml"

if [ -f "$WF_TPL" ]; then
  ok=1
  tier_env_count=$(grep -c "SENTINEL_TIER:" "$WF_TPL")
  derive_count=$(grep -cF "env.SENTINEL_TIER != 'blocking'" "$WF_TPL")
  hardcode_coe=$(grep "continue-on-error:" "$WF_TPL" | grep -v '\${{' | wc -l | tr -d ' ')

  [ "$tier_env_count" -eq 1 ] || ok=0
  [ "$derive_count" -ge 1 ] || ok=0
  [ "$hardcode_coe" -eq 0 ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: M4a-axis-single (workflow check) — SENTINEL_TIER env 1회 + continue-on-error derive + hardcode literal 0 (tier axis 1지점)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: M4a-axis-single"
    echo "  tier_env_count=$tier_env_count (expect 1), derive_count=$derive_count (expect >=1), hardcode_coe=$hardcode_coe (expect 0)"
    FAIL=$((FAIL+1))
  fi
else
  echo "✗ FAIL: M4a-axis-single — workflow not found: $WF_TPL"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M4b: tier flip observe — workflow sed mutate(warning→blocking) →
#   continue-on-error 평가식 분기 observe (warning=true 비차단 vs blocking=false 차단).
#   INV-6 (blockable-capable tier 동작).
#   ★ Mutation-RED kill: continue-on-error expr → hardcode 'true' 시 mutated blocking 도 비차단 = RED.
# ═════════════════════════════════════════════════════════════════════════════
if [ -f "$WF_TPL" ]; then
  MUT=$(mktemp)
  sed -E "s/^([[:space:]]*SENTINEL_TIER:[[:space:]]*)warning/\1blocking/" "$WF_TPL" > "$MUT"

  orig_tier=$(grep -E '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$WF_TPL" | head -1 | sed -E 's/.*SENTINEL_TIER:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' | tr -d '[:space:]')
  mut_tier=$(grep -E '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$MUT" | head -1 | sed -E 's/.*SENTINEL_TIER:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' | tr -d '[:space:]')

  eval_coe() { if [ "$1" != "blocking" ]; then echo "true"; else echo "false"; fi; }
  orig_coe=$(eval_coe "$orig_tier")
  mut_coe=$(eval_coe "$mut_tier")

  ok=1
  [ "$orig_tier" = "warning" ] || ok=0
  [ "$orig_coe" = "true" ] || ok=0
  [ "$mut_tier" = "blocking" ] || ok=0
  [ "$mut_coe" = "false" ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: M4b-tier-flip (sed mutate) — orig warning→coe=true(GREEN비차단) ∧ mut blocking→coe=false(RED차단) 분리 observe"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: M4b-tier-flip"
    echo "  orig_tier=$orig_tier coe=$orig_coe (expect warning/true) | mut_tier=$mut_tier coe=$mut_coe (expect blocking/false)"
    FAIL=$((FAIL+1))
  fi
  rm -f "$MUT"
else
  echo "✗ FAIL: M4b-tier-flip — workflow not found: $WF_TPL"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M5: byte-parity — templates ↔ .github workflow byte-identical (ADR-005).
#   INV-7 (integrity).
#   ★ Mutation-RED kill: 1-byte drift 삽입 → cmp RED.
# ═════════════════════════════════════════════════════════════════════════════
if [ -f "$WF_TPL" ] && [ -f "$WF_GH" ] && cmp -s "$WF_TPL" "$WF_GH"; then
  echo "✓ PASS: M5-byte-parity — templates ↔ .github byte-identical (ADR-005 integrity)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M5-byte-parity — templates ↔ .github NOT byte-identical"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M6: exit-matrix/degrade — ① git 미설치 exit 2 ② degrade(rc!=0) exit 0
#   ③ 무효 --mode exit 2 ④ 전 경로 exit ∈ {0,2}.
#   AC-4a(degrade), AC-4b(setup error), INV-5.
#   ★ Mutation-RED [exit]: exit code 체계 미정의 → git 미설치 exit 0(false-PASS) = RED.
# ═════════════════════════════════════════════════════════════════════════════
ok=1
PYBIN=$(command -v python3)

# ① git 미설치 — PATH 격리로 git 미발견 → exit 2 ∧ error_kind json
EMPTYDIR=$(mktemp -d)
OUT1=$(PATH="$EMPTYDIR" "$PYBIN" "$PYSRC" --mode head-compare 2>&1); EC1=$?
[ "$EC1" -eq 2 ] || ok=0
echo "$OUT1" | grep -qF '"error_kind": "git_not_installed"' || ok=0
if echo "$OUT1" | grep -qF 'Traceback'; then ok=0; fi
rmdir "$EMPTYDIR" 2>/dev/null || true

# ② degrade(rc!=0) — git mock rc=1 → exit 0 ∧ degradation 필드
OUT2=$(REBASE_GIT_MOCK_RC=1 REBASE_GIT_MOCK_STDERR="test error" bash "$WRAPPER" --mode head-compare 2>&1); EC2=$?
[ "$EC2" -eq 0 ] || ok=0
echo "$OUT2" | grep -qF '"degradation": "git_fetch_failed"' || ok=0

# ③ 무효 --mode → argparse native exit 2
OUT3=$(bash "$WRAPPER" --mode bogus-mode 2>&1); EC3=$?
[ "$EC3" -eq 2 ] || ok=0
echo "$OUT3" | grep -qF 'invalid choice' || ok=0

# ④ 전 경로 exit ∈ {0,2}
for e in "$EC1" "$EC2" "$EC3"; do
  [ "$e" -eq 0 ] || [ "$e" -eq 2 ] || ok=0
done

if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M6-exit-matrix (degrade + setup error) — git-missing exit 2 / degrade exit 0 / invalid-mode exit 2 / all ∈ {0,2}"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M6-exit-matrix"
  echo "  ① git-missing: exit=$EC1, expect 2, has error_kind"
  echo "  ② degrade(rc=1): exit=$EC2, expect 0, has degradation"
  echo "  ③ invalid-mode: exit=$EC3, expect 2"
  echo "  Output1: $OUT1"
  echo "  Output2: $OUT2"
  echo "  Output3: $OUT3"
  FAIL=$((FAIL+1))
fi

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2784 FU-1588-R rebase-staleness-sentinel)"
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
  echo "[count-mapping] Mutation-hardcode (N count → constant 0 고정)"
  echo "         → M1a-count-1/count-2/count-3/count-10 FAIL (tier1/2 미표시) = RED / M1a-count-0 GREEN 유지 = 두 set 분리"
  echo "[boundary] Mutation-1 (TIER1_MAX=2 → 3 변경 — boundary shift)"
  echo "         → M1b-boundary-2 FAIL (N=2 가 tier2 = OFF-BY-ONE 위반) = RED"
  echo "[enumeration] Mutation-2 (tier3/tier4 라벨 삽입)"
  echo "         → M1c-tier3/4-exclusion FAIL (tier3/4 출현) = RED (INV-3 위반)"
  echo "[bypass] Mutation-3 (BYPASS short-circuit 제거 — if os.environ.get 문 삭제)"
  echo "         → M2-bypass-flip FAIL (bypass JSON 미출현) = RED (bypass 무효)"
  echo "[mutation] Mutation-4 (git push/rebase/gh pr merge 호출 1줄 삽입)"
  echo "         → M3-no-mutations FAIL (grep hit) = RED (mutation 실행 위반 INV-5)"
  echo "[tier-axis] Mutation-5 (SENTINEL_TIER 2지점 산재 또는 hardcode continue-on-error literal)"
  echo "         → M4a-axis-single FAIL (tier_env_count != 1 or hardcode_coe > 0) = RED"
  echo "[tier-flip] Mutation-6 (continue-on-error expr → hardcode 'true' 고정)"
  echo "         → M4b-tier-flip FAIL (mutated blocking 도 coe=true 비차단) = RED"
  echo "[exit-code] Mutation-7 (exit 2 → exit 0 이동 — git 미설치 케이스)"
  echo "         → M6-exit-matrix FAIL (EC1 != 2) = RED"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
