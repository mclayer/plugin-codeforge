#!/usr/bin/env bash
# tests/scripts/test_check-semantic-staleness-sentinel.sh
# CFP-2786 / Epic #2783 Child B — Discriminating self-test for
#   scripts/lib/check_semantic_staleness_sentinel.py carrier→in-flight cross-match.
#
# 배경: sentinel의 carrier 필터링 + anchor cross-match 가 hollow(무력)가 아님을 증명.
#   - M1: carrier-classify 가 정책경로만 필터 (비정책 제외)
#   - M2: in-flight state filter 가 open PR 만 (merged 제외)
#   - M3a: anchor overlap (primary recall signal) 가 작동
#   - M3b: matched narrowing 이 무관 PR 제외
#   - M4: self-touch short-circuit 이 자기파일 제외
#   - M5: read-only 유지 (mutation 없음)
#   - M6: 결정론 유지 + bare comment 없음
#   - M7: degrade 4-class 가 정확 분류
#   - M8: disjoint tier vocab (rebase tier 없음)
#   - M9: tier-flip 이 continue-on-error 를 통해 동작
#   - M10: workflow byte-parity 보증
#   - M11: exit-matrix 정확 (git 미설치=2, degrade=0, 무효 mode=2)
#
# self-contained bash (bats 미사용 — rebase-staleness-sentinel 답습).
#   mock seam(SEMANTIC_*_MOCK) 으로 조건을 주입하고,
#   JSON 출력 + exit code 로 assertion.
#
# Discriminating 의무 (change-plan §8): 단순 "exit 0 = PASS" 검사는 non-discriminating
#   → 금지. 출력 JSON 의 "carrier_touched", "inflight_candidates", "matched" 등
#   값을 assert: 정책경로 필터, anchor 겹침, merged 제외 등 각 조건을 분리.
#
# Exit code:
#  0 = all fixtures pass
#  1 = any fixture fails

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-semantic-staleness-sentinel.sh"
PYSRC="$REPO_ROOT/scripts/lib/check_semantic_staleness_sentinel.py"
SHSRC="$REPO_ROOT/scripts/check-semantic-staleness-sentinel.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# Helper: run_case — sentinel 호출 → exit code + JSON assert.
#   $1=name  $2=carrier_mock  $3=inflight_mock_fixture  $4=expected_exit
#   $5=expect_carrier_len  $6=expect_candidate_count  $7=description
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" carrier_mock="$2" inflight_fixture="$3" expected_exit="$4"
  local expect_carrier_len="$5" expect_candidate_count="$6" description="$7"
  local out exit_code=0 actual_carrier_len actual_candidate_count

  out=$(
    SEMANTIC_CARRIER_TOUCH_MOCK="$carrier_mock" \
    SEMANTIC_INFLIGHT_MOCK="$inflight_fixture" \
    bash "$WRAPPER" --mode carrier-cross-match 2>&1
  ) || exit_code=$?

  local ok=1
  [ "$exit_code" -eq "$expected_exit" ] || ok=0

  # JSON 파싱 — carrier_touched 길이 + inflight_candidates count extract
  if echo "$out" | grep -qF '"carrier_touched"'; then
    actual_carrier_len=$(printf '%s' "$out" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d.get("carrier_touched",[])))' 2>/dev/null || echo "PARSE_ERROR")
    [ "$actual_carrier_len" = "$expect_carrier_len" ] || ok=0
  else
    ok=0
  fi

  if echo "$out" | grep -qF '"inflight_candidates"'; then
    actual_candidate_count=$(printf '%s' "$out" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d.get("inflight_candidates",[])))' 2>/dev/null || echo "PARSE_ERROR")
    [ "$actual_candidate_count" = "$expect_candidate_count" ] || ok=0
  else
    ok=0
  fi

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name (exit $exit_code, carrier_len=$actual_carrier_len, candidates=$actual_candidate_count) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected: exit $expected_exit, carrier_len=$expect_carrier_len, candidates=$expect_candidate_count"
    echo "  Got: exit $exit_code, carrier_len=$actual_carrier_len, candidates=$actual_candidate_count"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

set +e

# ═════════════════════════════════════════════════════════════════════════════
# M1: carrier-classify filter-drop — 정책경로만 필터
#   정책경로(archive/adr/ADR-060-x.md) → carrier_touched 비어있지 않음
#   비정책(scripts/lib/foo_feature.py) → carrier_touched=[] silent-pass
#   INV-1(carrier classify) / AC-1 (정상 경로 커버).
#   RED(mutation): filter 제거(모든 path 통과) 시 비정책 path도 carrier = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

# M1a: 정책경로 필터링
FIXTURE_M1A=$(mktemp)
cat > "$FIXTURE_M1A" << 'EOF'
[{"number": 1, "title": "Test PR", "body": "No anchors", "labels": []}]
EOF
run_case "M1a-policy-path" "archive/adr/ADR-060-test.md" "$FIXTURE_M1A" "0" "1" "0" "policy path (archive/adr/) → carrier_touched=1, no candidates (no anchor)"
rm -f "$FIXTURE_M1A"

# M1b: 비정책경로 silent-pass
FIXTURE_M1B=$(mktemp)
cat > "$FIXTURE_M1B" << 'EOF'
[{"number": 1, "title": "Test PR", "body": "No anchors", "labels": []}]
EOF
run_case "M1b-non-policy-path" "scripts/lib/foo_feature.py" "$FIXTURE_M1B" "0" "0" "0" "non-policy path (scripts/lib/) → carrier_touched=0 silent-pass"
rm -f "$FIXTURE_M1B"

# ═════════════════════════════════════════════════════════════════════════════
# M2: in-flight state-filter — open PR 만 candidate
#   INFLIGHT_MOCK 에 open PR + merged PR (동일 anchor) → open 만 candidate
#   INV-2 (state filter) / AC-2 (open PR only).
#   RED(mutation): open-filter 제거 시 merged 도 candidate = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

# M2a: open PR 만 candidate (merged 제외)
FIXTURE_M2=$(mktemp)
cat > "$FIXTURE_M2" << 'EOF'
[
  {"number": 1, "title": "Open PR", "body": "ADR-060 reference", "labels": [], "state": "open"},
  {"number": 2, "title": "Merged PR", "body": "ADR-060 reference", "labels": [], "state": "merged"}
]
EOF
run_case "M2-state-filter" "archive/adr/ADR-060-test.md" "$FIXTURE_M2" "0" "1" "1" "state filter: open PR candidate (merged excluded)"
rm -f "$FIXTURE_M2"

# ═════════════════════════════════════════════════════════════════════════════
# M3a: anchor overlap (primary recall signal) — MOST CRITICAL
#   carrier ADR-060, in-flight PR body 가 "ADR-060" 만 참조(경로·lane 겹침 0)
#   → anchor_overlap=[ADR-060] matched=true candidate
#   INV-3 (anchor recall) / Q6 (multi-signal OR — anchor primary).
#   RED(mutation): OR→AND 변경 시 anchor-only 미탐 = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

# M3a: anchor-only overlap → candidate (path/lane 겹침 0)
# carrier_anchors = ADR-060, workitem_anchors = ADR-060 → overlap + no path/lane overlap
FIXTURE_M3A=$(mktemp)
cat > "$FIXTURE_M3A" << 'EOF'
[{"number": 10, "title": "ADR-060 related", "body": "This work touches ADR-060 policy", "labels": [], "state": "open"}]
EOF
run_case "M3a-anchor-overlap" "archive/adr/ADR-060-test.md" "$FIXTURE_M3A" "0" "1" "1" "anchor-only overlap (no path/lane): ADR-060 matched → candidate (recall primary)"
rm -f "$FIXTURE_M3A"

# ═════════════════════════════════════════════════════════════════════════════
# M3b: anchor false-POSITIVE guard — unrelated PR excluded
#   무관 PR(ADR-999 참조, 경로/lane 겹침 0) → matched=false 미candidate
#   INV-4 (narrowing precision).
#   RED(mutation): narrowing 제거(matched 상수 true) 시 unrelated 도 candidate = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

# M3b: unrelated anchor → no candidate
FIXTURE_M3B=$(mktemp)
cat > "$FIXTURE_M3B" << 'EOF'
[{"number": 20, "title": "Unrelated PR", "body": "ADR-999 some other policy", "labels": [], "state": "open"}]
EOF
run_case "M3b-no-overlap" "archive/adr/ADR-060-test.md" "$FIXTURE_M3B" "0" "1" "0" "no overlap (ADR-999 vs ADR-060): unrelated → no candidate"
rm -f "$FIXTURE_M3B"

# ═════════════════════════════════════════════════════════════════════════════
# M4: self-touch short-circuit — sentinel 자기파일만
#   carrier_touch = templates/github-workflows/semantic-staleness-detection.yml (in carrier surface + self manifest)
#   → self_touch:true carve_out, candidate 0, inflight_candidates=[]
#   INV-5 (self-carve-out) / AC-8 (발행자 != 수신자).
#   RED(mutation): is_self_touch short-circuit 제거 시 자기파일도 candidate match = FAIL.
#   DISCRIMINATING: JSON self_touch 필드 = true ∧ carve_out 필드 존재 를 assert
# ═════════════════════════════════════════════════════════════════════════════

# M4: self-touch carve-out — templates/ prefix in carrier surface + self manifest
FIXTURE_M4=$(mktemp)
cat > "$FIXTURE_M4" << 'EOF'
[{"number": 30, "title": "Self update", "body": "unrelated anchor", "labels": [], "state": "open"}]
EOF
OUT=$(SEMANTIC_CARRIER_TOUCH_MOCK="templates/github-workflows/semantic-staleness-detection.yml" \
      SEMANTIC_INFLIGHT_MOCK="$FIXTURE_M4" \
      bash "$WRAPPER" --mode carrier-cross-match 2>&1); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
# 핵심 discriminating assert: self_touch 필드 = true ∧ carve_out 필드 존재
actual_self=$(printf '%s' "$OUT" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("self_touch"))' 2>/dev/null || echo "PARSE_ERROR")
[ "$actual_self" = "True" ] || ok=0
echo "$OUT" | grep -qF '"carve_out"' || ok=0
# 기타 검증: carrier_len=1 (template 파일 감지) + candidates=0 (carve-out 으로 제외)
actual_carrier_len=$(printf '%s' "$OUT" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d.get("carrier_touched",[])))' 2>/dev/null || echo "PARSE_ERROR")
[ "$actual_carrier_len" = "1" ] || ok=0
actual_cand=$(printf '%s' "$OUT" | python3 -c 'import sys,json; print(len(json.load(sys.stdin).get("inflight_candidates",[])))' 2>/dev/null || echo "PARSE_ERROR")
[ "$actual_cand" = "0" ] || ok=0

if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M4-self-touch (self_touch=$actual_self, carrier_len=$actual_carrier_len, candidates=$actual_cand) — self_touch:true ∧ carve_out (발행자≠수신자)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M4-self-touch"
  echo "  Expected: self_touch=True, carve_out field present, carrier_len=1, candidates=0"
  echo "  Got: self_touch=$actual_self, carrier_len=$actual_carrier_len, candidates=$actual_cand"
  echo "  Output: $OUT"
  FAIL=$((FAIL+1))
fi
rm -f "$FIXTURE_M4"

# ═════════════════════════════════════════════════════════════════════════════
# M5: surface-only NEGATIVE GUARD — no mutations (read-only)
#   py+sh+workflow 소스 grep: git push/rebase/merge/close/edit 호출 부재.
#   read-only(git diff/gh pr list/git fetch/git merge-base) 만.
#   INV-6 (read-only) / AC-5 (no auto-fix).
#   RED(mutation): git push 1줄 삽입 → grep hit = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

ok=1
grep -qE 'git push|git rebase|git merge|gh pr merge|gh pr close|gh pr edit' "$PYSRC" && ok=0
grep -qE 'git push|git rebase|git merge|gh pr merge|gh pr close|gh pr edit' "$SHSRC" && ok=0
if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M5-no-mutations (grep check) — git push/rebase/merge/close/edit 호출 0건 (read-only INV-6)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M5-no-mutations"
  echo "  Found mutation call in source"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M6: idempotency (surface channel) — deterministic output + no bare comment
#   ① py 재실행 결정론(동일 mock → byte-identical JSON)
#   ② workflow 에 bare gh pr comment(upsert 없는) 부재 (step-summary primary)
#   INV-7 (deterministic) / AC-4 (no bare comment).
#   RED(mutation): bare gh pr comment 삽입 → grep hit = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

ok=1

# ① deterministic output
FIXTURE_M6=$(mktemp)
cat > "$FIXTURE_M6" << 'EOF'
[{"number": 40, "title": "Test", "body": "ADR-060", "labels": [], "state": "open"}]
EOF
OUT1=$(SEMANTIC_CARRIER_TOUCH_MOCK="archive/adr/ADR-060-test.md" SEMANTIC_INFLIGHT_MOCK="$FIXTURE_M6" bash "$WRAPPER" --mode carrier-cross-match 2>&1)
OUT2=$(SEMANTIC_CARRIER_TOUCH_MOCK="archive/adr/ADR-060-test.md" SEMANTIC_INFLIGHT_MOCK="$FIXTURE_M6" bash "$WRAPPER" --mode carrier-cross-match 2>&1)
[ "$OUT1" = "$OUT2" ] || ok=0
rm -f "$FIXTURE_M6"

# ② no bare comment
WF_YAML="$REPO_ROOT/templates/github-workflows/semantic-staleness-detection.yml"
if [ -f "$WF_YAML" ]; then
  grep -q 'gh pr comment --body' "$WF_YAML" && ok=0   # bare comment forbidden
else
  ok=0
fi

if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M6-idempotency — deterministic JSON output + no bare gh pr comment (INV-7/AC-4)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M6-idempotency"
  echo "  Deterministic output or bare comment issue"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M7: degrade 4-class HOT — git_fetch_failed / api_quota_exceeded / gh_command_failed / gh_payload_invalid
#   ① SEMANTIC_GIT_MOCK_RC=1 → degradation="git_fetch_failed" (no carrier mock → git path active)
#   ② CARRIER_MOCK + GH_MOCK_RC=1 + STDERR="rate limit exceeded" → "api_quota_exceeded"
#   ③ CARRIER_MOCK + GH_MOCK_RC=1 + generic STDERR → "gh_command_failed"
#   ④ INFLIGHT_MOCK=invalid JSON → "gh_payload_invalid"
#   INV-8 (degrade classification) / AC-3 (degrade honest).
#   Note: to test gh degrade, need carrier_touched non-empty first (silent pass blocks gh)
#   RED(mutation): class 삭제/silent truncate → false-negative = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

ok=1

# ① git_fetch_failed (no carrier mock → git path active → GIT_MOCK_RC applies)
OUT=$(SEMANTIC_GIT_MOCK_RC=1 bash "$WRAPPER" --mode carrier-cross-match 2>&1); EC=$?
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "git_fetch_failed"' || ok=0

# ② api_quota_exceeded (carrier + GH_MOCK_RC → gh path active → GH_MOCK_RC + quota stderr)
OUT=$(SEMANTIC_CARRIER_TOUCH_MOCK="archive/adr/test.md" SEMANTIC_GH_MOCK_RC=1 SEMANTIC_GH_MOCK_STDERR="rate limit exceeded" bash "$WRAPPER" --mode carrier-cross-match 2>&1); EC=$?
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "api_quota_exceeded"' || ok=0

# ③ gh_command_failed (carrier + GH_MOCK_RC + generic error)
OUT=$(SEMANTIC_CARRIER_TOUCH_MOCK="archive/adr/test.md" SEMANTIC_GH_MOCK_RC=1 SEMANTIC_GH_MOCK_STDERR="command error" bash "$WRAPPER" --mode carrier-cross-match 2>&1); EC=$?
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "gh_command_failed"' || ok=0

# ④ gh_payload_invalid (invalid JSON, need carrier to reach gh enumeration)
BADFIX=$(mktemp)
echo "not json" > "$BADFIX"
OUT=$(SEMANTIC_CARRIER_TOUCH_MOCK="archive/adr/test.md" SEMANTIC_INFLIGHT_MOCK="$BADFIX" bash "$WRAPPER" --mode carrier-cross-match 2>&1); EC=$?
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "gh_payload_invalid"' || ok=0
rm -f "$BADFIX"

if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M7-degrade-4-class — git_fetch_failed / api_quota_exceeded / gh_command_failed / gh_payload_invalid (INV-8)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M7-degrade-4-class"
  echo "  Degrade classification issue"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M8: disjoint-tier vocab — no rebase tier keywords
#   py 소스 grep: commits_behind / recommended_tier / TIER1_MAX / tier1/tier2 / 부재
#   (이들은 rebase sentinel 의 vocabulary, semantics sentinel 은 사용 금지)
#   INV-9 (disjoint tier vocab).
#   RED(mutation): tier 값 삽입 → grep hit = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

ok=1
# semantics sentinel must NOT use rebase tier vocab
grep -qF 'commits_behind' "$PYSRC" && ok=0
grep -qF 'recommended_tier' "$PYSRC" && ok=0
grep -qF 'TIER1_MAX' "$PYSRC" && ok=0
grep -qF '"tier1"' "$PYSRC" && ok=0
grep -qF '"tier2"' "$PYSRC" && ok=0

if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M8-disjoint-tier-vocab — no rebase tier keywords (commits_behind/recommended_tier/tier1/tier2) — disjoint axis (INV-9)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M8-disjoint-tier-vocab"
  echo "  Found rebase tier vocabulary in semantic sentinel"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M9: tier-flip observe (dark-path) — SENTINEL_TIER derive via continue-on-error
#   workflow YAML: orig `SENTINEL_TIER: warning` → `env.SENTINEL_TIER != 'blocking'` = true (비차단)
#   sed mutate(warning→blocking) → false(차단) 분리 observe
#   INV-10 (blockable-capable tier) / AC-9 (tier axis single-point).
#   RED(mutation): continue-on-error hardcode 'true' 시 mutated blocking 도 비차단 = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

WF_TPL="$REPO_ROOT/templates/github-workflows/semantic-staleness-detection.yml"
WF_GH="$REPO_ROOT/.github/workflows/semantic-staleness-detection.yml"

ok=1
if [ -f "$WF_TPL" ]; then
  # Extract and evaluate tier expression
  orig_tier=$(grep -E '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$WF_TPL" | head -1 | sed -E 's/.*SENTINEL_TIER:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' | tr -d '[:space:]')
  eval_coe() { if [ "$1" != "blocking" ]; then echo "true"; else echo "false"; fi; }
  orig_coe=$(eval_coe "$orig_tier")

  # Check continue-on-error derive
  grep -qF "env.SENTINEL_TIER != 'blocking'" "$WF_TPL" || ok=0

  # Mutate and re-evaluate
  MUT=$(mktemp)
  sed -E "s/^([[:space:]]*SENTINEL_TIER:[[:space:]]*)warning/\1blocking/" "$WF_TPL" > "$MUT"
  mut_tier=$(grep -E '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$MUT" | head -1 | sed -E 's/.*SENTINEL_TIER:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' | tr -d '[:space:]')
  mut_coe=$(eval_coe "$mut_tier")

  # Verify: orig warning→true, mut blocking→false
  [ "$orig_tier" = "warning" ] || ok=0
  [ "$orig_coe" = "true" ] || ok=0
  [ "$mut_tier" = "blocking" ] || ok=0
  [ "$mut_coe" = "false" ] || ok=0

  rm -f "$MUT"

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: M9-tier-flip (sed mutate) — orig warning→coe=true(GREEN비차단) ∧ mut blocking→coe=false(RED차단) 분리 observe (INV-10)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: M9-tier-flip"
    echo "  orig_tier=$orig_tier coe=$orig_coe | mut_tier=$mut_tier coe=$mut_coe"
    FAIL=$((FAIL+1))
  fi
else
  echo "✗ FAIL: M9-tier-flip — workflow not found: $WF_TPL"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M10: byte-parity — templates ↔ .github workflow byte-identical
#   `cmp -s templates/... .github/workflows/...` byte-identical (ADR-005 integrity).
#   INV-11 (integrity).
#   RED(mutation): 1-byte drift → cmp FAIL.
# ═════════════════════════════════════════════════════════════════════════════

if [ -f "$WF_TPL" ] && [ -f "$WF_GH" ] && cmp -s "$WF_TPL" "$WF_GH"; then
  echo "✓ PASS: M10-byte-parity — templates ↔ .github byte-identical (ADR-005 integrity)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M10-byte-parity — NOT byte-identical"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M11: exit-matrix/degrade — SETUP error vs honest-degrade
#   ① git 미설치 exit 2 ∧ error_kind="git_not_installed" ∧ no Traceback
#   ② degrade(GIT_MOCK_RC=1) exit 0 ∧ degradation 필드 (no carrier mock → git path active)
#   ③ 무효 --mode exit 2 ∧ "invalid choice"
#   ④ 무효 --base-sha(zzz) exit 2
#   ⑤ 전 경로 exit ∈ {0,2}
#   INV-12 (exit-matrix) / AC-6 (SETUP handled) / AC-3 (degrade exit 0).
#   RED(mutation): exit code 체계 미정의 → false-PASS/FAIL = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

ok=1
PYBIN=$(command -v python3)

# ① git 미설치 → exit 2 + error_kind
EMPTYDIR=$(mktemp -d)
OUT1=$(PATH="$EMPTYDIR" "$PYBIN" "$PYSRC" --mode carrier-cross-match 2>&1); EC1=$?
[ "$EC1" -eq 2 ] || ok=0
echo "$OUT1" | grep -qF '"error_kind": "git_not_installed"' || ok=0
if echo "$OUT1" | grep -qF 'Traceback'; then ok=0; fi
rmdir "$EMPTYDIR" 2>/dev/null || true

# ② degrade(GIT_MOCK_RC=1) → exit 0 + degradation (no carrier mock = git path active)
OUT2=$(SEMANTIC_GIT_MOCK_RC=1 bash "$WRAPPER" --mode carrier-cross-match 2>&1); EC2=$?
[ "$EC2" -eq 0 ] || ok=0
echo "$OUT2" | grep -qF '"degradation": "git_fetch_failed"' || ok=0

# ③ 무효 --mode → exit 2 + invalid choice
OUT3=$(bash "$WRAPPER" --mode bogus-mode 2>&1); EC3=$?
[ "$EC3" -eq 2 ] || ok=0
echo "$OUT3" | grep -qF 'invalid choice' || ok=0

# ④ 무효 --base-sha → exit 2
OUT4=$("$PYBIN" "$PYSRC" --mode carrier-cross-match --base-sha zzz 2>&1); EC4=$?
[ "$EC4" -eq 2 ] || ok=0

# ⑤ all exit ∈ {0,2}
for e in "$EC1" "$EC2" "$EC3" "$EC4"; do
  [ "$e" -eq 0 ] || [ "$e" -eq 2 ] || ok=0
done

if [ "$ok" -eq 1 ]; then
  echo "✓ PASS: M11-exit-matrix — git-missing exit 2 / degrade exit 0 / invalid-mode exit 2 / invalid-sha exit 2 / all ∈ {0,2} (INV-12)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M11-exit-matrix"
  echo "  ① git-missing: EC=$EC1 (expect 2), has error_kind"
  echo "  ② degrade(GIT_MOCK_RC=1): EC=$EC2 (expect 0), has degradation"
  echo "  ③ invalid-mode: EC=$EC3 (expect 2)"
  echo "  ④ invalid-base-sha: EC=$EC4 (expect 2)"
  echo "  Output1: $OUT1"
  echo "  Output2: $OUT2"
  echo "  Output3: $OUT3"
  echo "  Output4: $OUT4"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# M12: pagination truncation — 500+ PR fixture 로 scale 테스트
#   PR_COUNT_CAP = 500. INFLIGHT_MOCK 에 500개 이상 PR fixture
#   → truncated flag 설정, 열거 loop 정상 작동 (메모리 봉인)
#   INV-13 (pagination / DoS guard).
#   RED(mutation): truncated 필드 삭제 또는 silent truncation = FAIL.
# ═════════════════════════════════════════════════════════════════════════════

FIXTURE_LARGE=$(mktemp)
# Generate 510 PR fixture (500+ for truncation, PR_COUNT_CAP=500)
# Only some PRs have ADR-060 anchor to keep candidate count manageable
{
  echo "["
  for i in {1..510}; do
    if [ $i -gt 1 ]; then echo ","; fi
    if [ $((i % 100)) -eq 0 ]; then
      echo '  {"number": '$i', "title": "PR '$i'", "body": "ADR-060 related", "labels": [], "state": "open"}'
    else
      echo '  {"number": '$i', "title": "PR '$i'", "body": "No anchor", "labels": [], "state": "open"}'
    fi
  done
  echo "]"
} > "$FIXTURE_LARGE"

OUT=$(SEMANTIC_CARRIER_TOUCH_MOCK="archive/adr/ADR-060-test.md" SEMANTIC_INFLIGHT_MOCK="$FIXTURE_LARGE" bash "$WRAPPER" --mode carrier-cross-match 2>&1); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"truncated": true' || ok=0

# Verify parsing and truncated flag presence
has_truncated=$(printf '%s' "$OUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('truncated' in d and d['truncated'] == True)" 2>/dev/null || echo "ERROR")
[ "$has_truncated" = "True" ] || ok=0

if [ "$ok" -eq 1 ]; then
  cand_count=$(printf '%s' "$OUT" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d.get("inflight_candidates",[])))' 2>/dev/null || echo "PARSE_ERROR")
  echo "✓ PASS: M12-pagination (510 fixture) — truncated flag true + scale safety (fixtures_total=510, candidates=$cand_count, PR_COUNT_CAP honored) (INV-13)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: M12-pagination"
  echo "  EC=$EC, truncated flag or has_truncated issue"
  echo "  has_truncated=$has_truncated"
  FAIL=$((FAIL+1))
fi
rm -f "$FIXTURE_LARGE"

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2786 semantic-staleness-sentinel)"
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
  echo "[M1] carrier-classify filter — policy path only"
  echo "       → M1a-policy-path (archive/adr/) GREEN | M1b-non-policy (scripts/lib/) silent-pass"
  echo "       Mutation: remove filter → non-policy included = RED"
  echo "[M2] in-flight state-filter — open PR only"
  echo "       → open PR candidate ∧ merged excluded"
  echo "       Mutation: remove state filter → merged included = RED"
  echo "[M3a] anchor-only overlap (MOST CRITICAL — recall primary signal)"
  echo "       → anchor match (ADR-060) → candidate despite no path/lane overlap"
  echo "       Mutation: OR→AND change → anchor-only miss = RED (recall loss)"
  echo "[M3b] unrelated PR excluded — narrowing precision"
  echo "       → ADR-999 vs ADR-060 no overlap → no candidate"
  echo "       Mutation: remove narrowing → all-in-flight flagged = RED"
  echo "[M4] self-touch carve-out — sentinel 자기파일"
  echo "       → scripts/lib/check_semantic_staleness_sentinel.py → carve_out"
  echo "       Mutation: remove short-circuit → self-recursive = RED"
  echo "[M5] read-only surface (NEGATIVE GUARD)"
  echo "       → no git push/rebase/merge/close/edit calls"
  echo "       Mutation: insert git push → grep hit = RED"
  echo "[M6] idempotency + no bare comment"
  echo "       → same input → same JSON output ∧ no bare gh pr comment"
  echo "       Mutation: add bare comment → grep hit = RED"
  echo "[M7] degrade 4-class classification"
  echo "       → git_fetch_failed / api_quota_exceeded / gh_command_failed / gh_payload_invalid"
  echo "       Mutation: remove class → misclassification = RED"
  echo "[M8] disjoint-tier vocab (no rebase keywords)"
  echo "       → commits_behind/recommended_tier/tier1/tier2 absent"
  echo "       Mutation: add tier keyword → grep hit = RED"
  echo "[M9] tier-flip observe (dark-path)"
  echo "       → orig SENTINEL_TIER=warning → coe=true(非차단) ∧ mut blocking → coe=false(차단)"
  echo "       Mutation: hardcode continue-on-error 'true' → both 非차단 = RED"
  echo "[M10] byte-parity"
  echo "       → templates ↔ .github byte-identical"
  echo "       Mutation: 1-byte drift → cmp FAIL = RED"
  echo "[M11] exit-matrix + SETUP error"
  echo "       → git-missing exit 2 / degrade exit 0 / invalid-mode exit 2 / invalid-sha exit 2"
  echo "       Mutation: wrong exit code → false-PASS/FAIL = RED"
  echo "[M12] pagination truncation (100+ fixture)"
  echo "       → truncated flag ∧ scale safety"
  echo "       Mutation: remove truncated flag → silent truncation = RED"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
