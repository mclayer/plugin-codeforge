#!/usr/bin/env bash
# check-lane-evidence.sh — Lane evidence cross-validate (CFP-126 / ADR-031 Phase 2).
#
# Story §14 Lane Evidence YAML block ↔ Phase 2 PR description `## Lane evidence` 블록
# cross-validation. Lane name set + outcome 일치 + fix_iteration ↔ §10 FIX Ledger row index 정합.
#
# CFP-137 Phase 2 확장: --check-parallelization 플래그
#   TEAM-DESIGN 6 deputy row 의 spawned_at diff < 60s 검증 (ADR-044 §결정 5 Parallelization measurable).
#   대상 lane: 설계 (design). deputy role = CodebaseMapper / Refactor / SecurityArch / OpRiskArch /
#              TestContractArch / DataMigrationArch (6개). spawned_at ISO8601 파싱 후 max-min < 60초 기준.
#
# Usage:
#   bash scripts/check-lane-evidence.sh [--story <path>] [--pr <number>] [--strict] [--quiet]
#                                        [--check-parallelization]
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
CHECK_PARALLELIZATION=0
EXEMPT_SECTION_14=0   # ADR-031 Amendment 2 (CFP-2270): wrapper-self dogfood §14 면제 플래그

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT=1; shift ;;
        --story) STORY_PATH="$2"; shift 2 ;;
        --pr) PR_NUMBER="$2"; shift 2 ;;
        --check-parallelization) CHECK_PARALLELIZATION=1; shift ;;
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

# ADR-031 Amendment 2 (CFP-2270): wrapper-self dogfood (repo-kind `mixed`) §14 면제 probe.
#
# 면제 판정 (교집합, 좁게 — INV-D2-exempt-narrow):
#   detect-repo-kind 분류 == `mixed` (exit 2 AND stdout sentinel "mixed" 동시 일치)
#   AND auto-detect 후 STORY_PATH 가 비었을 때 (Story file 미발견).
# 두 조건 모두 참일 때만 §14 검사를 면제 (Check 1/2 의 FAIL → [N/A] advisory 로 대체).
#
# fail-safe (INV-D2-failsafe — 면제 억제 측): python 미탐지 / script 부재 / 예외 / 비-`mixed`
#   exit 면 면제하지 않고 기존 advisory-red 동작 보존 (보수 측 fallback). bootstrap-first-gate.py
#   `_detect_repo_kind` 의 `-1` sentinel→발화 억제 와 대칭 — 불확실 시 더 안전한 측으로 degrade.
#
# 경로해석: CLAUDE_PLUGIN_ROOT env 우선 → fallback ${BASH_SOURCE[0]} 기준 plugin root
#   (symlink 견고성 — $0 금지). bootstrap-first-gate.py `_plugin_root()` (env→__file__ parent) 정합.
detect_section_14_exemption() {
    EXEMPT_SECTION_14=0

    # auto-detect 후에도 STORY_PATH 가 실존하면 면제 불가 (over-broad 차단)
    if [ -n "$STORY_PATH" ] && [ -f "$STORY_PATH" ]; then
        return 0
    fi

    # python interpreter 탐지 (없으면 면제 억제)
    local py=""
    if command -v python3 >/dev/null 2>&1; then
        py="$(command -v python3)"
    elif command -v python >/dev/null 2>&1; then
        py="$(command -v python)"
    else
        return 0  # fail-safe: python 미탐지 → 면제 억제
    fi

    # detect-repo-kind.py 경로 해석 (env 우선 → BASH_SOURCE 기준 fallback)
    local detect_script
    if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
        detect_script="${CLAUDE_PLUGIN_ROOT}/templates/scripts/detect-repo-kind.py"
    else
        detect_script="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/templates/scripts/detect-repo-kind.py"
    fi
    if [ ! -f "$detect_script" ]; then
        return 0  # fail-safe: script 부재 → 면제 억제
    fi

    # detect 호출: stdout(kind) + exit code 둘 다 취득 (exit code 단독 의존 금지)
    local kind rc
    kind="$("$py" "$detect_script" --repo-root . 2>/dev/null)"
    rc=$?

    # mixed 확정 = exit 2 AND stdout sentinel "mixed" 동시 일치 (둘 중 하나만이면 면제 억제)
    if [ "$rc" -eq 2 ] && [ "$kind" = "mixed" ]; then
        EXEMPT_SECTION_14=1
    fi
    # 비-mixed exit / sentinel 불일치 / 예외 → EXEMPT_SECTION_14=0 유지 (fail-safe)
    return 0
}

# Parse Story §14 Lane Evidence YAML block
parse_story_section_14() {
    local story="$1"
    if [ ! -f "$story" ]; then
        log_err "Story file 부재: $story"
        return 1
    fi
    # Find §14 section + extract YAML block (between ```yaml and ```)
    # CFP-2293 sibling: heading § 선택적. story-init renderer 는 `## N.`(§ 없음) 헤딩을
    #   생성하고 실 story 는 `## 14.` / `## §14.` 양쪽이 혼재(34건 no-§ 실측) → 양쪽 수용.
    #   `(§)?` 그룹 = multibyte-safe (§ = 2바이트 C2A7; awk byte-mode/mawk 에서 `§?` 는
    #   2번째 바이트만 optional → no-§ 미스. 그룹으로 전체 § 를 optional 처리).
    #   section-end terminator 도 (§)? + 숫자 anchor 로 일반화(`## 15.`/`## §15.` 모두 종료).
    awk '
        /^## (§)?14|^### (§)?14|^#### (§)?14/ { in14=1; next }
        in14 && /^## (§)?[0-9]|^### (§)?[0-9]/ { in14=0 }
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
    printf '%s' "$yaml" | grep -E '^[[:space:]]*- lane:' | sed -E 's/.*lane:[[:space:]]*([^[:space:]#]+).*/\1/' | sort -u
}

# Extract lane names from PR description block
extract_pr_lanes() {
    local block="$1"
    printf '%s' "$block" | grep -E '^- ' | sed -E 's/^-[[:space:]]*([^:]+):.*/\1/' | tr -d ' ' | sort -u
}

# CFP-137 Phase 2: Parallelization check
# TEAM-DESIGN 6 deputy spawned_at diff < 60s (ADR-044 §결정 5)
# Deputy roles (any of): CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch
# Strategy: 설계 lane 의 모든 row 의 spawned_at 추출 → epoch 변환 → max-min 차이 < 60s 검증
# 조건: 6개 이상 deputy row 존재할 때만 (agent teams env=1 context 만 의미있음 — env=0 시 deputy row 부재)
check_parallelization() {
    local yaml="$1"
    if [ -z "$yaml" ]; then
        log_err "[PARALLELIZATION SKIP] §14 YAML block 없음 — skip"
        return 0
    fi

    # Extract 설계 lane rows block
    # strategy: parse all rows where lane: 설계 and extract spawned_at timestamps
    local design_rows
    # BSD-compat awk: use sub() + substr()/split() instead of 3-arg match (gawk-only)
    design_rows="$(printf '%s' "$yaml" | awk '
        /- lane: 설계$/ { inrow=1; ts="" }
        inrow && /spawned_at:/ {
            line=$0
            sub(/.*spawned_at:[[:space:]]*/, "", line)
            sub(/[[:space:]#].*/, "", line)
            ts=line
            print ts
        }
        /- lane: / && !/- lane: 설계$/ { if (inrow) inrow=0 }
    ')"

    local row_count
    row_count=$(printf '%s\n' "$design_rows" | grep -c '[0-9]' || true)

    if [ "$row_count" -lt 6 ]; then
        log "[PARALLELIZATION SKIP] 설계 lane deputy rows < 6 ($row_count 개) — agent teams env=0 or deputy rows absent. skip (ADR-044 §결정 5 N/A in env=0)"
        return 0
    fi

    # Parse ISO8601 → epoch seconds via date (GNU date or BSD date)
    local timestamps=()
    while IFS= read -r ts; do
        [ -z "$ts" ] && continue
        local epoch
        # GNU date
        epoch="$(date -d "$ts" +%s 2>/dev/null || date -jf '%Y-%m-%dT%H:%M:%SZ' "$ts" +%s 2>/dev/null || true)"
        if [ -n "$epoch" ] && [[ "$epoch" =~ ^[0-9]+$ ]]; then
            timestamps+=("$epoch")
        fi
    done <<< "$design_rows"

    if [ "${#timestamps[@]}" -lt 6 ]; then
        log "[PARALLELIZATION SKIP] spawned_at epoch 파싱 성공 row < 6 (${#timestamps[@]} 개, date 미지원 또는 null ts) — skip"
        return 0
    fi

    # Find min and max
    local min_ts max_ts
    min_ts="${timestamps[0]}"
    max_ts="${timestamps[0]}"
    for ts in "${timestamps[@]}"; do
        [ "$ts" -lt "$min_ts" ] && min_ts="$ts"
        [ "$ts" -gt "$max_ts" ] && max_ts="$ts"
    done

    local diff=$(( max_ts - min_ts ))
    if [ "$diff" -lt 60 ]; then
        log "[PARALLELIZATION OK] TEAM-DESIGN deputy spawned_at diff = ${diff}s < 60s (${#timestamps[@]} rows)"
    else
        log_err "[PARALLELIZATION WARN] TEAM-DESIGN deputy spawned_at diff = ${diff}s >= 60s — Parallelization 기준 미달 (ADR-044 §결정 5). diff > 60s = sequential spawn 의심"
        # NOTE: advisory only — not counted as fail (no agent teams enforcement in env=0 contexts)
        # If strict mode is required for parallelization, use --strict with this flag
        log_err "  (advisory: diff >= 60s 는 FAIL 아님. Strict parallelization enforcement 는 CFP-137 후속 CFP scope)"
    fi
    return 0
}

# Run check
run_check() {
    auto_detect_story
    auto_detect_pr
    detect_section_14_exemption

    local fail=0

    # Check 1: Story §14 presence
    if [ -z "$STORY_PATH" ] || [ ! -f "$STORY_PATH" ]; then
        if [ "${EXEMPT_SECTION_14:-0}" -eq 1 ]; then
            # ADR-031 Amendment 2: wrapper-self dogfood (mixed repo-kind) — Story file 부재는
            # ADR-013 dogfood-out 정상. FAIL count 미증가.
            log "[N/A] wrapper-self dogfood Story (repo-kind mixed) — §14 면제 (ADR-031 Amendment 2)"
        else
            log_err "[FAIL] Story file path detect 실패 또는 file 부재 — --story <path> 명시"
            fail=$((fail + 1))
        fi
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
    elif [ "${EXEMPT_SECTION_14:-0}" -eq 1 ]; then
        # ADR-031 Amendment 2: Story file 부재 dogfood → §14 YAML block 검사도 면제.
        log "[N/A] §14 YAML block — wrapper-self dogfood 면제 (ADR-031 Amendment 2)"
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
        if printf '%s' "$story_yaml" | grep -q "output_status:[[:space:]]*bypass"; then
            if ! printf '%s' "$pr_block" | grep -qi "BYPASS:"; then
                log_err "[FAIL] §14 에 bypass row 존재 — PR description 에 'BYPASS: <reason>' 명시 의무"
                fail=$((fail + 1))
            else
                log "[OK] BYPASS reason PR description 명시 확인"
            fi
        fi
    fi

    # Check 6 (optional): Parallelization — TEAM-DESIGN 6 deputy spawned_at diff < 60s
    # CFP-137 Phase 2 / ADR-044 §결정 5 Parallelization measurable verification
    if [ $CHECK_PARALLELIZATION -eq 1 ]; then
        check_parallelization "$story_yaml"
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
