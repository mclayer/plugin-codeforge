#!/usr/bin/env bash
# test_phase-gate-mergeable-yml.sh
# CFP-795 Phase 2 — phase-gate-mergeable.yml 4번째 fast-pass source isPostMergeFix (3-조건 AND) 검증
# Change Plan §8.2 8-조합 truth table (T1-T8) + EC-1 + self-application 회귀 + ALLOWED_HUB_REPOS 미일치
# ADR-026 Amendment 4 §결정 6 carrier
#
# TDD RED 선행: 신규 source 미구현 상태에서 T8 관련 assertions 이 FAIL → 구현 후 PASS

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"

TEMPLATES_WORKFLOW="$REPO_ROOT/templates/github-workflows/phase-gate-mergeable.yml"
SELF_APP_WORKFLOW="$REPO_ROOT/.github/workflows/phase-gate-mergeable.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# Helper functions
# ============================================================================

assert_contains() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qF "$pattern" "$file"; then
        echo -e "${GREEN}PASS${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} $desc"
        echo "    Pattern not found: $pattern"
        echo "    In file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi
}

assert_contains_ere() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qE "$pattern" "$file"; then
        echo -e "${GREEN}PASS${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} $desc"
        echo "    ERE pattern not found: $pattern"
        echo "    In file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi
}

assert_not_contains() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if ! grep -qF "$pattern" "$file"; then
        echo -e "${GREEN}PASS${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} $desc"
        echo "    Pattern found (should not exist): $pattern"
        echo "    In file: $file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi
}

assert_files_identical() {
    local desc="$1"
    local file1="$2"
    local file2="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if diff -q "$file1" "$file2" > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC} $desc"
        echo "    Files differ: $file1 vs $file2"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    fi
}

# ============================================================================
# 0. 파일 존재 검증 (precondition)
# ============================================================================

echo ""
echo "=== 0. 파일 존재 검증 ==="

if [[ ! -f "$TEMPLATES_WORKFLOW" ]]; then
    echo -e "${RED}FAIL${NC} templates/github-workflows/phase-gate-mergeable.yml 존재"
    exit 1
fi
echo -e "${GREEN}PASS${NC} templates/github-workflows/phase-gate-mergeable.yml 존재"

if [[ ! -f "$SELF_APP_WORKFLOW" ]]; then
    echo -e "${RED}FAIL${NC} .github/workflows/phase-gate-mergeable.yml 존재"
    exit 1
fi
echo -e "${GREEN}PASS${NC} .github/workflows/phase-gate-mergeable.yml 존재"

# ============================================================================
# 1. ADR-005 byte-identical self-app mirror 검증
# ============================================================================

echo ""
echo "=== 1. ADR-005 byte-identical self-app mirror (ADR-005 §결정 2) ==="

assert_files_identical \
    "templates/ ↔ .github/ byte-identical (ADR-005)" \
    "$TEMPLATES_WORKFLOW" \
    "$SELF_APP_WORKFLOW"

# ============================================================================
# 2. 기존 3-source 무회귀 검증 (T1 기본, self-application 회귀)
# ============================================================================

echo ""
echo "=== 2. 기존 3-source 무회귀 (isEpicLabel / isSiblingPr / isDocOnly) ==="

# T1: 기존 OR-gate 3-source 존재 확인 (무변경)
assert_contains \
    "T1: isEpicLabel 기존 source 존재" \
    "$TEMPLATES_WORKFLOW" \
    "const isEpicLabel = allLabels.includes('type:epic')"

assert_contains \
    "T1: isSiblingPr 기존 source 존재" \
    "$TEMPLATES_WORKFLOW" \
    "const isSiblingPr = allLabels.includes('sibling-pr')"

assert_contains_ere \
    "T1: isDocOnly 기존 source 존재" \
    "$TEMPLATES_WORKFLOW" \
    "const isDocOnly ="

# self-application 회귀: Phase 2 PR (phase:구현) 경로가 기존 3-source 그대로 평가됨 (4번째 미발동)
# = post-merge-fix 라벨 없는 PR 은 기존 gate 경로 진입 (L183 OR-gate 통과 못하면 하위 평가)
assert_contains \
    "self-app 회귀: phase:구현 gate:design-review-pass 경로 유지" \
    "$TEMPLATES_WORKFLOW" \
    "gate: 'gate:design-review-pass'"

assert_contains \
    "self-app 회귀: phase:구현 구분 블록 유지" \
    "$TEMPLATES_WORKFLOW" \
    "phase:구현"

# ============================================================================
# 3. T2-T7 BLOCK 보장: 3-조건 AND partial 충족 시 fast-pass 미발동 검증
#    (structural: 3-조건 모두 AND 결합이어야 fast-pass)
# ============================================================================

echo ""
echo "=== 3. T2-T7 BLOCK 보장 — 3-조건 AND 구조 검증 ==="

# T2: post-merge-fix label 단독 → BLOCK (3-조건 AND 구조로 cond2/cond3 미충족 시 isPostMergeFix=false)
# T6: label + cond3, cond2 FAIL (orphan hotfix) → BLOCK
# 공통 anchor: isPostMergeFix 가 3-조건 AND (cond1 ∧ cond2 ∧ cond3 = cond2 ∧ cond3) 인지 확인
assert_contains \
    "T2/T6: isPostMergeFix = cond2 && cond3 AND 구조 (label 단독 BLOCK 보장)" \
    "$TEMPLATES_WORKFLOW" \
    "isPostMergeFix = cond2 && cond3"

# T5: label + cond2, cond3 FAIL (보안 touch) → BLOCK
# 조건 3 양면 구조 확인: (3a) 원 PR ∧ (3b) hotfix PR 자체 SECURITY_PATHS non-match
assert_contains_ere \
    "T5: 조건 3 양면 구조 (cond3a && cond3b) 존재 — 보안 touch 시 BLOCK" \
    "$TEMPLATES_WORKFLOW" \
    "cond3a.*&&.*cond3b|cond3b.*&&.*cond3a|const cond3 ="

# T7: cond2 + cond3, label 없음 → BLOCK
# short-circuit: hasPostMergeFixLabel false → cond2/cond3 skip → isPostMergeFix=false
assert_contains \
    "T7: hasPostMergeFixLabel short-circuit (label 없으면 cond2/cond3 skip)" \
    "$TEMPLATES_WORKFLOW" \
    "const hasPostMergeFixLabel = allLabels.includes('post-merge-fix')"

assert_contains_ere \
    "T7: short-circuit if(hasPostMergeFixLabel) 블록 존재" \
    "$TEMPLATES_WORKFLOW" \
    "if \(hasPostMergeFixLabel\)"

# ============================================================================
# 4. T8: 3-조건 모두 충족 → fast-pass success 경로 검증
# ============================================================================

echo ""
echo "=== 4. T8: 3-조건 모두 충족 → isPostMergeFix fast-pass ==="

# T8: 4번째 source OR-gate 에 포함
assert_contains \
    "T8: OR-gate 4-way 확장 (isPostMergeFix 포함)" \
    "$TEMPLATES_WORKFLOW" \
    "isEpicLabel || isSiblingPr || isDocOnly || isPostMergeFix"

# T8: fast-pass reason 4-way ternary (post-merge-fix branch 포함)
assert_contains \
    "T8: fast-pass reason ternary — post-merge-fix branch 존재" \
    "$TEMPLATES_WORKFLOW" \
    "post-merge-fix"

# T8: checkHubStorySection10Binding helper 함수 존재
assert_contains \
    "T8: checkHubStorySection10Binding helper 함수 존재 (조건 2)" \
    "$TEMPLATES_WORKFLOW" \
    "async function checkHubStorySection10Binding"

# T8: checkSecurityNonTouch helper 함수 존재
assert_contains \
    "T8: checkSecurityNonTouch helper 함수 존재 (조건 3 양면)" \
    "$TEMPLATES_WORKFLOW" \
    "async function checkSecurityNonTouch"

# ============================================================================
# 5. ALLOWED_HUB_REPOS 화이트리스트 검증 (Codex TP#2 P1 inline FIX — §3.2 step 2.5)
# ============================================================================

echo ""
echo "=== 5. ALLOWED_HUB_REPOS 화이트리스트 (zero-trust anchor, story_uri spoofing 차단) ==="

# ALLOWED_HUB_REPOS 상수/env 참조 존재
assert_contains \
    "ALLOWED_HUB_REPOS env 주입 존재" \
    "$TEMPLATES_WORKFLOW" \
    "ALLOWED_HUB_REPOS"

# 화이트리스트 미일치 시 cond2=false (fail-closed) 구조
assert_contains_ere \
    "ALLOWED_HUB_REPOS 미일치 → cond2=false (fail-closed)" \
    "$TEMPLATES_WORKFLOW" \
    "ALLOWED_HUB_REPOS|allowedHubRepos"

# dogfood default: github.com/mclayer/codeforge-internal-docs
assert_contains \
    "dogfood default hub: github.com/mclayer/codeforge-internal-docs" \
    "$TEMPLATES_WORKFLOW" \
    "mclayer/codeforge-internal-docs"

# ============================================================================
# 6. SECURITY_PATHS 정의 검증 (조건 3 — §3.3 verbatim)
# ============================================================================

echo ""
echo "=== 6. SECURITY_PATHS 정의 (조건 3 양면 — §3.3) ==="

# SECURITY_PATHS const 존재
assert_contains \
    "SECURITY_PATHS const 정의 존재" \
    "$TEMPLATES_WORKFLOW" \
    "SECURITY_PATHS"

# docs/adr/ ADR 보안 패턴
assert_contains_ere \
    "SECURITY_PATHS: docs/adr/ADR-.* 패턴 존재" \
    "$TEMPLATES_WORKFLOW" \
    "docs.adr.ADR"

# docs/security/ 경로 패턴
assert_contains \
    "SECURITY_PATHS: docs/security/ 패턴 존재" \
    "$TEMPLATES_WORKFLOW" \
    "docs/security/"

# ============================================================================
# 7. corrects_pr marker 파싱 검증 (조건 3 원 MERGED PR 역참조)
# ============================================================================

echo ""
echo "=== 7. corrects_pr marker 파싱 (조건 3 §3.3 — 원 MERGED PR 역참조) ==="

assert_contains \
    "corrects_pr marker 파싱 존재" \
    "$TEMPLATES_WORKFLOW" \
    "corrects_pr"

# ============================================================================
# 8. fail-closed 검증 (marker 부재, fetch 실패 시 BLOCK)
# ============================================================================

echo ""
echo "=== 8. fail-closed 구조 검증 ==="

# cond2 = false default (fail-closed)
assert_contains \
    "cond2 fail-closed default (false 초기화)" \
    "$TEMPLATES_WORKFLOW" \
    "let isPostMergeFix = false"

# story_uri: marker 부재 시 cond2=false
assert_contains \
    "story_uri: marker 파싱 재사용 (기존 L34 패턴)" \
    "$TEMPLATES_WORKFLOW" \
    "story_uri:"

# ============================================================================
# 9. EC-1: 재귀 hotfix depth > 2 → escalate 검증
# ============================================================================

echo ""
echo "=== 9. EC-1: 재귀 hotfix depth > 2 → escalate ==="

assert_contains_ere \
    "EC-1: depth > 2 또는 depth check 로직 존재" \
    "$TEMPLATES_WORKFLOW" \
    "depth|recurs"

# ============================================================================
# 10. 워크플로우 문법 기초 검증 (YAML 기본 구조)
# ============================================================================

echo ""
echo "=== 10. workflow 기본 구조 ==="

assert_contains \
    "workflow name 존재" \
    "$TEMPLATES_WORKFLOW" \
    "name: Phase Gate Mergeable"

assert_contains \
    "permissions block 존재 (checks: write)" \
    "$TEMPLATES_WORKFLOW" \
    "checks: write"

assert_contains \
    "CROSS_REPO_TOKEN env 존재" \
    "$TEMPLATES_WORKFLOW" \
    "CROSS_REPO_TOKEN:"

# ALLOWED_HUB_REPOS workflow env block 주입
assert_contains \
    "ALLOWED_HUB_REPOS workflow env: block 주입" \
    "$TEMPLATES_WORKFLOW" \
    "ALLOWED_HUB_REPOS:"

# ============================================================================
# 11. CodeReview iter 1 verified-true P1 regression (F-002 / F-003)
# ============================================================================

echo ""
echo "=== 11. CodeReview iter 1 F-002/F-003 regression ==="

# F-002: PR identifier substring boundary 강제 (sub-prefix collision 차단)
#   PR #80 vs §10 row #800 collision 회귀 — regex word-boundary 패턴이 코드에 포함되었는지 정적 검증
assert_contains \
    "F-002: prIdEscaped (regex meta escape) 정의 존재" \
    "$TEMPLATES_WORKFLOW" \
    "const prIdEscaped"

assert_contains \
    "F-002: prIdRegex (boundary-aware) 정의 존재" \
    "$TEMPLATES_WORKFLOW" \
    "const prIdRegex = new RegExp"

assert_contains_ere \
    "F-002: 비-숫자 boundary 패턴 [^0-9] 사용" \
    "$TEMPLATES_WORKFLOW" \
    '\[\^0-9\]'

# F-002 런타임 회귀: PR #80 + §10 row #800 → boundary regex 가 mismatch 해야 함
test_F002_pr_id_substring_boundary() {
    local desc="F-002 런타임: PR #80 boundary regex 가 §10 row #800 부적합치 reject"
    TESTS_RUN=$((TESTS_RUN + 1))
    local pattern='(^|[^0-9])mclayer/plugin-codeforge#80([^0-9]|$)'
    local section10_row='| F-001 | P0 | mclayer/plugin-codeforge#800 | ... |'
    if echo "$section10_row" | grep -qE "$pattern"; then
        echo -e "${RED}FAIL${NC} $desc"
        echo "    PR #80 boundary regex 가 §10 row #800 wrongly matched (sub-prefix collision)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    else
        echo -e "${GREEN}PASS${NC} $desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    fi
}
test_F002_pr_id_substring_boundary || true

# F-003: depth count semantic — row-split per-line match (keyword grep 아님)
assert_contains \
    "F-003: depth count row-split semantic (split(/\\n/).filter(...))" \
    "$TEMPLATES_WORKFLOW" \
    "section10.split(/\\n/).filter"

assert_contains_ere \
    "F-003: depthRows 변수가 split + filter 패턴 사용" \
    "$TEMPLATES_WORKFLOW" \
    'depthRows = section10\.split'

# F-003 런타임 회귀: keyword prose 3+ hit 가 1줄 안에 있으면 row count=1 (BLOCK 회귀 차단)
test_F003_depth_row_count_semantic() {
    local desc="F-003 런타임: keyword prose 3+ hit 단일 line → row count = 1 (depth ≤ 2 → 통과)"
    TESTS_RUN=$((TESTS_RUN + 1))
    local prose='본 §10 정책은 post-merge-fix label + corrects_pr marker 를 사용한다. post-merge-fix 는 cross-repo.'
    # row split + per-line match — prose 가 단일 line 이므로 row_count = 1
    local row_count
    row_count=$(echo "$prose" | grep -cE '(\bcorrects_pr\b|\bpost-merge-fix\b)' || echo 0)
    if [ "$row_count" -gt 2 ]; then
        echo -e "${RED}FAIL${NC} $desc"
        echo "    depth count 가 row 단위가 아닌 keyword count 로 동작 (row_count=$row_count)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1 || true
    else
        echo -e "${GREEN}PASS${NC} $desc (row_count=$row_count)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    fi
}
test_F003_depth_row_count_semantic || true

# ============================================================================
# 결과 요약
# ============================================================================

echo ""
echo "============================================"
echo "CFP-795 phase-gate-mergeable.yml 테스트 결과"
echo "============================================"
echo "총 테스트: $TESTS_RUN"
echo -e "PASS: ${GREEN}$TESTS_PASSED${NC}"
echo -e "FAIL: ${RED}$TESTS_FAILED${NC}"
echo ""

if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}TDD RED: ${TESTS_FAILED}개 assertion FAIL — 신규 source 구현 후 GREEN 전환 예상${NC}"
    exit 1
else
    echo -e "${GREEN}GREEN: 모든 assertion PASS${NC}"
    exit 0
fi
