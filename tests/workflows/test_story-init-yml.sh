#!/usr/bin/env bash
# test_story-init-yml.sh
# CFP-596 Phase 2 — story-init.yml workflow test suite
# Tests: T-1 ~ T-10 (Change Plan §8.5 Impl Manifest + ADR-013 Amendment 5 정합)
# Coverage: happy path (codeforge family + consumer) + fail-closed + idempotency + special chars

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || pwd)"

WORKFLOW_FILE="$REPO_ROOT/.github/workflows/story-init.yml"
TEMPLATES_WORKFLOW="$REPO_ROOT/templates/github-workflows/story-init.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_contains() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qF "$pattern" "$file"; then
        printf '%b✓%b %s\n' "$GREEN" "$NC" "$desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        printf '%b✗%b %s\n' "$RED" "$NC" "$desc"
        printf '    Pattern not found: %s\n' "$pattern"
        printf '    In file: %s\n' "$file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_not_contains() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if ! grep -qF "$pattern" "$file"; then
        printf '%b✓%b %s\n' "$GREEN" "$NC" "$desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        printf '%b✗%b %s\n' "$RED" "$NC" "$desc"
        printf '    Pattern unexpectedly found: %s\n' "$pattern"
        printf '    In file: %s\n' "$file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_regex() {
    local desc="$1"
    local file="$2"
    local pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if grep -qE "$pattern" "$file"; then
        printf '%b✓%b %s\n' "$GREEN" "$NC" "$desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        printf '%b✗%b %s\n' "$RED" "$NC" "$desc"
        printf '    Regex pattern not found: %s\n' "$pattern"
        printf '    In file: %s\n' "$file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_files_identical() {
    local desc="$1"
    local file_a="$2"
    local file_b="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    if diff -q "$file_a" "$file_b" >/dev/null 2>&1; then
        printf '%b✓%b %s\n' "$GREEN" "$NC" "$desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        printf '%b✗%b %s\n' "$RED" "$NC" "$desc"
        printf '    Files differ:\n'
        printf '    A: %s\n' "$file_a"
        printf '    B: %s\n' "$file_b"
        diff "$file_a" "$file_b" | head -20 || true
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

assert_file_exists() {
    local desc="$1"
    local file="$2"

    TESTS_RUN=$((TESTS_RUN + 1))
    if [[ -f "$file" ]]; then
        printf '%b✓%b %s\n' "$GREEN" "$NC" "$desc"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        printf '%b✗%b %s\n' "$RED" "$NC" "$desc"
        printf '    File not found: %s\n' "$file"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# ─── T-1: Happy path (codeforge family) — cross-repo write branch 구조 검증 ───
printf '\n%bT-1: Happy path — codeforge family cross-repo write branch%b\n' "$YELLOW" "$NC"

assert_contains "T-1.1: is_codeforge_family output 정의" \
    "$WORKFLOW_FILE" "is_codeforge_family=true"

assert_contains "T-1.2: codeforge family detection regex ^codeforge (Change Plan §3.1)" \
    "$WORKFLOW_FILE" '^codeforge'

assert_contains "T-1.3: TARGET_REPO = mclayer/codeforge-internal-docs (cross-repo write)" \
    "$WORKFLOW_FILE" "mclayer/codeforge-internal-docs"

assert_contains "T-1.4: dogfood_folder plugin folder mapping (Change Plan §3.2)" \
    "$WORKFLOW_FILE" "dogfood_folder"

assert_contains "T-1.5: CODEFORGE_CROSS_REPO_PAT mount (codeforge family branch)" \
    "$WORKFLOW_FILE" "CODEFORGE_CROSS_REPO_PAT"

assert_regex "T-1.6: cross-repo PR create with TARGET_REPO variable" \
    "$WORKFLOW_FILE" 'gh pr create.*TARGET_REPO|--repo.*TARGET_REPO'

assert_contains "T-1.7: cross-repo Issue body link update (Change Plan §4.3)" \
    "$WORKFLOW_FILE" "codeforge-internal-docs/blob/main"

assert_contains "T-1.8: Step name exists for codeforge family branch" \
    "$WORKFLOW_FILE" "Create branch + Story file (codeforge family"

assert_contains "T-1.9: Step name for family PR create" \
    "$WORKFLOW_FILE" "Create Phase 1 PR (codeforge family"

# ─── T-2: Consumer 영향 0 (AC-5) — generic consumer local write 보존 ───
printf '\n%bT-2: Consumer 영향 0 — generic consumer local write 보존 (AC-5)%b\n' "$YELLOW" "$NC"

assert_contains "T-2.1: generic consumer local write step 존재" \
    "$WORKFLOW_FILE" "Create branch + docs/stories/<KEY>.md (generic consumer"

assert_contains "T-2.2: generic consumer GITHUB_TOKEN 사용 (PAT 미노출)" \
    "$WORKFLOW_FILE" "secrets.GITHUB_TOKEN"

assert_contains "T-2.3: is_codeforge_family != 'true' 분기 존재 (consumer branch)" \
    "$WORKFLOW_FILE" "is_codeforge_family != 'true'"

assert_contains "T-2.4: local mkdir/commit/push 보존 (consumer)" \
    "$WORKFLOW_FILE" "git checkout -b"

assert_contains "T-2.5: consumer PR create step 존재" \
    "$WORKFLOW_FILE" "Create Phase 1 PR (generic consumer"

# ─── T-3: fail-closed (PAT scope 불충분) — error message 검증 ───
printf '\n%bT-3: fail-closed — PAT scope 불충분 시 error message%b\n' "$YELLOW" "$NC"

assert_contains "T-3.1: fail-closed error message (existence_check Stage 1 실패)" \
    "$WORKFLOW_FILE" "existence_check Stage 1 실패"

assert_contains "T-3.2: ADR-066 §결정 2 참조 error message" \
    "$WORKFLOW_FILE" "ADR-066 §결정 2 참조"

assert_contains "T-3.3: exit 1 (fail-closed sentinel)" \
    "$WORKFLOW_FILE" "exit 1"

assert_contains "T-3.4: PAT scope error in cross-repo write step" \
    "$WORKFLOW_FILE" "PAT repo:write scope 확인 필요"

# ─── T-4: fail-closed (PAT missing) — CODEFORGE_CROSS_REPO_PAT 미설정 ───
printf '\n%bT-4: fail-closed — PAT missing 시 HTTP 000 → exit 1%b\n' "$YELLOW" "$NC"

assert_regex "T-4.1: HTTP 000 fallback (auth/network failure sentinel)" \
    "$WORKFLOW_FILE" 'echo "000"'

assert_contains "T-4.2: fail-closed branch (4xx/5xx → exit 1)" \
    "$WORKFLOW_FILE" "PAT scope 또는"

# ─── T-5: fail-closed (internal-docs outage) — unreachable error message ───
printf '\n%bT-5: fail-closed — internal-docs outage 시 unreachable error%b\n' "$YELLOW" "$NC"

assert_contains "T-5.1: unreachable error message" \
    "$WORKFLOW_FILE" "unreachable"

assert_contains "T-5.2: Story file PUT 실패 error message" \
    "$WORKFLOW_FILE" "Story file PUT 실패"

# ─── T-6: idempotency — two-stage existence_check (Change Plan §3.5) ───
printf '\n%bT-6: idempotency — two-stage existence_check (CFP-596 §3.5)%b\n' "$YELLOW" "$NC"

assert_contains "T-6.1: Stage 1 branch existence check" \
    "$WORKFLOW_FILE" "Stage 1 — branch existence"

assert_contains "T-6.2: Stage 2 Story file existence check (codeforge family)" \
    "$WORKFLOW_FILE" "Stage 2 — Story file existence"

assert_contains "T-6.3: idempotent skip notice (both stages present)" \
    "$WORKFLOW_FILE" "idempotent skip — branch + Story file 모두 존재"

assert_contains "T-6.4: automated reconcile path notice (branch present + file absent)" \
    "$WORKFLOW_FILE" "automated reconcile path — branch 존재 + Story file 부재"

assert_contains "T-6.5: skip_branch_create flag (auto_recovered 분기 branch create skip)" \
    "$WORKFLOW_FILE" "skip_branch_create=true"

assert_contains "T-6.6: auto_recovered output 정의" \
    "$WORKFLOW_FILE" "auto_recovered=true"

assert_contains "T-6.7: PR existence check (idempotency for PR create, Change Plan §4.1)" \
    "$WORKFLOW_FILE" "PR already exists (idempotent skip)"

# ─── T-7: consumer 영향 0 재검증 — project.name field missing → exit 1 ───
printf '\n%bT-7: project.name missing → exit 1 (fail-closed, Change Plan §8.3)%b\n' "$YELLOW" "$NC"

assert_contains "T-7.1: project.name missing error message" \
    "$WORKFLOW_FILE" "project.name missing in"

assert_contains "T-7.2: project-config-schema.md §1.f 참조" \
    "$WORKFLOW_FILE" "project-config-schema.md §1.f"

# ─── T-8: commit message format invariant (Change Plan §4.1) ───
printf '\n%bT-8: commit message format invariant (§4.1 atomic invariant)%b\n' "$YELLOW" "$NC"

assert_contains "T-8.1: commit message format — §1 verbatim, §2-11 placeholder" \
    "$WORKFLOW_FILE" "feat: Story init — §1 verbatim, §2-11 placeholder"

assert_contains "T-8.2: branch namespace feat/ prefix (§4.1 atomic invariant)" \
    "$WORKFLOW_FILE" 'feat/${KEY}-${SLUG}'

# ─── T-9: byte-identical sibling sync (AC-3) ───
printf '\n%bT-9: byte-identical sibling sync — templates/ ↔ .github/workflows/ (AC-3)%b\n' "$YELLOW" "$NC"

assert_file_exists "T-9.1: .github/workflows/story-init.yml 존재" \
    "$WORKFLOW_FILE"

assert_file_exists "T-9.2: templates/github-workflows/story-init.yml 존재" \
    "$TEMPLATES_WORKFLOW"

assert_files_identical "T-9.3: byte-identical sibling sync (diff exit 0)" \
    "$WORKFLOW_FILE" \
    "$TEMPLATES_WORKFLOW"

# ─── T-10: special chars Issue title — slug normalize 기존 동작 보존 ───
printf '\n%bT-10: special chars Issue title slug normalize%b\n' "$YELLOW" "$NC"

assert_contains "T-10.1: slug normalize regex pattern [^A-Za-z0-9가-힣]+" \
    "$WORKFLOW_FILE" '[^A-Za-z0-9가-힣]+'

assert_contains "T-10.2: slug strip trailing dash + truncate 40 chars" \
    "$WORKFLOW_FILE" "[:40]"

assert_contains "T-10.3: ISSUE_TITLE → title_clean STORY prefix strip" \
    "$WORKFLOW_FILE" 'STORY'

# ─── T-11: Bug 1 fix — title regex precedence (CFP-671 / ADR-036 Amendment 1) ───
printf '\n%bT-11: Bug 1 fix — title regex precedence (CFP-671 / ADR-036 Amendment 1)%b\n' "$YELLOW" "$NC"

assert_contains "T-11.1: title regex precedence Python heredoc 존재 (re.search bracket-optional pattern)" \
    "$WORKFLOW_FILE" "re.search(r'\\[?([A-Z]+-\\d+)\\]?'"

assert_contains "T-11.2: key_from_title variable 정의 (title match 결과)" \
    "$WORKFLOW_FILE" "key_from_title"

assert_contains "T-11.3: prefix guard — startswith(prefix + \"-\") 검증" \
    "$WORKFLOW_FILE" 'key_from_title.startswith(prefix + "-")'

assert_contains "T-11.4: Issue # fallback 보존 (ADR-036 race-free)" \
    "$WORKFLOW_FILE" 'f"{prefix}-{issue_number}"'

assert_contains "T-11.5: CFP-671 / ADR-036 Amendment 1 step name 갱신" \
    "$WORKFLOW_FILE" "CFP-671 / ADR-036 Amendment 1"

# ─── T-12: Bug 1 fallback — no title pattern → Issue # fallback ───
printf '\n%bT-12: Bug 1 fallback — no title pattern (ADR-036 race-free 보존)%b\n' "$YELLOW" "$NC"

assert_contains "T-12.1: ADR-036 결정 1 race-free baseline 주석 유지" \
    "$WORKFLOW_FILE" "ADR-036 결정 1: GitHub atomic Issue numbering 위임 (race-free baseline)"

assert_contains "T-12.2: title clean (STORY prefix strip) — title 없을 때도 동작" \
    "$WORKFLOW_FILE" 're.sub(r"^\[STORY\]\s*", "", title)'

# ─── T-13: Bug 1 prefix mismatch — cross-project KEY injection 차단 ───
printf '\n%bT-13: Bug 1 prefix mismatch — cross-project KEY injection 차단 (security guard)%b\n' "$YELLOW" "$NC"

assert_contains "T-13.1: prefix guard else branch — Issue # fallback (security guard)" \
    "$WORKFLOW_FILE" "Fallback to Issue #"

assert_contains "T-13.2: cross-project KEY injection 차단 주석 또는 comment" \
    "$WORKFLOW_FILE" "cross-project KEY injection"

# ─── T-14: CFP-661 graceful degradation — PR create continue-on-error + post-fail comment ───
printf '\n%bT-14: CFP-661 graceful degradation — consumer PR create step graceful%b\n' "$YELLOW" "$NC"

assert_contains "T-14.1: pr_create_consumer step id 정의 (consumer branch — CFP-661 정합)" \
    "$WORKFLOW_FILE" "id: pr_create_consumer"

assert_contains "T-14.2: continue-on-error: true (CFP-661 graceful degradation)" \
    "$WORKFLOW_FILE" "continue-on-error: true"

assert_contains "T-14.3: Post manual PR fallback comment step (CFP-661 Wave 3)" \
    "$WORKFLOW_FILE" "Post manual PR fallback comment"

assert_contains "T-14.4: pr_create_consumer.outcome == 'failure' guard" \
    "$WORKFLOW_FILE" "steps.pr_create_consumer.outcome == 'failure'"

# ─── Summary ───
printf '\n%b─── Test Summary ──────────────────────────────────%b\n' "$YELLOW" "$NC"
printf 'Tests run:    %d\n' "$TESTS_RUN"
printf '%bTests passed: %d%b\n' "$GREEN" "$TESTS_PASSED" "$NC"

if [[ "$TESTS_FAILED" -gt 0 ]]; then
    printf '%bTests failed: %d%b\n' "$RED" "$TESTS_FAILED" "$NC"
    exit 1
else
    printf '%bAll tests passed.%b\n' "$GREEN" "$NC"
    exit 0
fi
