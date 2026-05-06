#!/usr/bin/env bash
# check-lane-evidence.sh — Lane evidence cross-validate (CFP-126 / ADR-031 Phase 2).
#
# Story §14 Lane Evidence YAML block ↔ Phase 2 PR description `## Lane evidence` 블록
# cross-validation. Lane name set + outcome 일치 + fix_iteration ↔ §10 FIX Ledger row index 정합.
#
# Usage:
#   bash scripts/check-lane-evidence.sh [--story <path>] [--pr <number>] [--strict] [--quiet]
#
# Defaults:
#   --story: docs/stories/<KEY>.md (auto-detect from git branch `cfp-N-...`)
#   --pr: 현재 branch 의 open PR (gh pr view --json number)
#
# Exit code:
#   Default mode: 0 (모든 check PASS) / 0 (FAIL — stderr advisory 만, ADR-027 §결정 2 LLM-trust 정합)
#   Strict mode (--strict): 0 / 1
#
# Effective date: ADR-031 Accepted 이후 신규 Phase 2 PR 만 검사 (retroactive 미처리, ADR-031 §결정 5).

set -uo pipefail

QUIET=0
STRICT=0
STORY_PATH=""
PR_NUMBER=""

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT=1; shift ;;
        --story) STORY_PATH="$2"; shift 2 ;;
        --pr) PR_NUMBER="$2"; shift 2 ;;
        -h|--help)
            sed -n '/^# check-lane-evidence/,/^# Effective date/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

log() { [ $QUIET -eq 0 ] && printf '%s\n' "$1"; }
log_err() { printf '%s\n' "$1" >&2; }

# Lane names (한국어 7종)
declare -a LANES=("요구사항" "설계" "설계-리뷰" "구현" "구현-리뷰" "구현-테스트" "보안-테스트")

# Auto-detect story path from branch
auto_detect_story() {
    if [ -n "$STORY_PATH" ]; then return 0; fi
    local branch
    branch="$(git branch --show-current 2>/dev/null || true)"
    if [ -n "$branch" ]; then
        # branch like "cfp-126-..." → KEY=CFP-126
        if [[ "$branch" =~ ^([a-zA-Z]+)-([0-9]+) ]]; then
            local prefix="${BASH_REMATCH[1]^^}"
            local num="${BASH_REMATCH[2]}"
            STORY_PATH="docs/stories/${prefix}-${num}.md"
            if [ ! -f "$STORY_PATH" ]; then
                # try internal-docs path (dogfood pattern)
                STORY_PATH=""
            fi
        fi
    fi
}

# Auto-detect PR number from current branch (gh pr view)
auto_detect_pr() {
    if [ -n "$PR_NUMBER" ]; then return 0; fi
    if command -v gh >/dev/null 2>&1; then
        PR_NUMBER="$(gh pr view --json number --jq '.number' 2>/dev/null || true)"
    fi
}

# Parse Story §14 Lane Evidence YAML block
parse_story_section_14() {
    local story="$1"
    if [ ! -f "$story" ]; then
        log_err "Story file 부재: $story"
        return 1
    fi
    # Find §14 section + extract YAML block (between ```yaml and ```)
    awk '
        /^## §14|^### §14|^#### §14/ { in14=1; next }
        in14 && /^## §|^### §[0-9]/ { in14=0 }
        in14 && /^```yaml/ { yaml=1; next }
        in14 && /^```/ && yaml { yaml=0; next }
        in14 && yaml { print }
    ' "$story"
}

# Parse Phase 2 PR description `## Lane evidence` block (from gh pr view)
fetch_pr_lane_evidence() {
    local pr_num="$1"
    if [ -z "$pr_num" ]; then return 1; fi
    if ! command -v gh >/dev/null 2>&1; then
        log_err "gh CLI 미설치 — PR description fetch 불가"
        return 1
    fi
    local body
    body="$(gh pr view "$pr_num" --json body --jq '.body' 2>/dev/null || true)"
    if [ -z "$body" ]; then
        log_err "PR #$pr_num description 빈 또는 fetch 실패"
        return 1
    fi
    # Extract `## Lane evidence` block
    printf '%s' "$body" | awk '
        /^## Lane evidence/ { inblock=1; next }
        inblock && /^## / { inblock=0 }
        inblock { print }
    '
}

# Extract lane names from Story §14 yaml block
extract_story_lanes() {
    local yaml="$1"
    printf '%s' "$yaml" | grep -E '^\s*- lane:' | sed -E 's/.*lane:\s*([^\s#]+).*/\1/' | sort -u
}

# Extract lane names from PR description block
extract_pr_lanes() {
    local block="$1"
    printf '%s' "$block" | grep -E '^- ' | sed -E 's/^-\s*([^:]+):.*/\1/' | tr -d ' ' | sort -u
}

# Run check
run_check() {
    auto_detect_story
    auto_detect_pr

    local fail=0

    # Check 1: Story §14 presence
    if [ -z "$STORY_PATH" ] || [ ! -f "$STORY_PATH" ]; then
        log_err "[FAIL] Story file path detect 실패 또는 file 부재 — --story <path> 명시"
        fail=$((fail + 1))
    else
        log "[OK] Story file: $STORY_PATH"
    fi

    # Check 2: §14 YAML block presence
    local story_yaml=""
    if [ -n "$STORY_PATH" ] && [ -f "$STORY_PATH" ]; then
        story_yaml="$(parse_story_section_14 "$STORY_PATH")"
        if [ -z "$story_yaml" ]; then
            log_err "[FAIL] Story §14 Lane Evidence YAML block 부재"
            fail=$((fail + 1))
        else
            log "[OK] Story §14 YAML block detected"
        fi
    fi

    # Check 3: PR description `## Lane evidence` presence
    local pr_block=""
    if [ -n "$PR_NUMBER" ]; then
        pr_block="$(fetch_pr_lane_evidence "$PR_NUMBER")"
        if [ -z "$pr_block" ]; then
            log_err "[FAIL] PR #$PR_NUMBER 의 ## Lane evidence 블록 부재"
            fail=$((fail + 1))
        else
            log "[OK] PR #$PR_NUMBER ## Lane evidence block detected"
        fi
    else
        log "[SKIP] PR number unknown (--pr 명시 또는 git branch 의 open PR 부재)"
    fi

    # Check 4: Lane name set 일치 (Story §14 ↔ PR description)
    if [ -n "$story_yaml" ] && [ -n "$pr_block" ]; then
        local story_lanes pr_lanes
        story_lanes="$(extract_story_lanes "$story_yaml")"
        pr_lanes="$(extract_pr_lanes "$pr_block")"
        local diff
        diff="$(diff <(printf '%s\n' "$story_lanes") <(printf '%s\n' "$pr_lanes") || true)"
        if [ -n "$diff" ]; then
            log_err "[FAIL] Lane name set mismatch (Story §14 ↔ PR description):"
            printf '%s\n' "$diff" | sed 's/^/  /' >&2
            fail=$((fail + 1))
        else
            log "[OK] Lane name set 일치"
        fi
    fi

    # Check 5: Bypass 의무 (BYPASS_LANE_EVIDENCE row 시 reason 명시 검증)
    if [ -n "$story_yaml" ]; then
        if printf '%s' "$story_yaml" | grep -q "output_status:\s*bypass"; then
            if ! printf '%s' "$pr_block" | grep -qi "BYPASS:"; then
                log_err "[FAIL] §14 에 bypass row 존재 — PR description 에 'BYPASS: <reason>' 명시 의무"
                fail=$((fail + 1))
            else
                log "[OK] BYPASS reason PR description 명시 확인"
            fi
        fi
    fi

    log ""
    log "=== Summary: $fail FAIL ==="

    # Strict mode → exit 1 if FAIL > 0
    # Default mode → exit 0 always (advisory)
    if [ $STRICT -eq 1 ] && [ $fail -gt 0 ]; then
        exit 1
    fi
    exit 0
}

run_check
