#!/usr/bin/env bash
# check-lane-evidence.sh — Lane evidence cross-validate (CFP-126 / ADR-031 Phase 2).
#
# Story §14 Lane Evidence YAML block ↔ Phase 2 PR description `## Lane evidence` 블록
# cross-validation. Lane name set + outcome 일치 + fix_iteration ↔ §10 FIX Ledger row index 정합.
#
# CFP-137 Phase 2 확장: --check-parallelization 플래그
#   TEAM-DESIGN 6 deputy row 의 spawned_at diff < 60s 검증 (ADR-044 §결정 5 Parallelization measurable).
#   대상 lane: 설계 (design). deputy role = 현 6 permanent (SecurityArchitectAgent /
#              InfraOperationalArchitectAgent / TestContractArchitectAgent / DataArchitectAgent /
#              ModuleArchitectAgent / APIContractArchitectAgent). spawned_at ISO8601 파싱 후 max-min < 60초 기준.
#
# CFP-2471 (Epic CFP-2468 W3) 축③ 확장 — lane verification floor fan-out 관측:
#   (a) stale roster 정정: 구 6 토큰 (CodebaseMapper/Refactor/OpRiskArch/DataMigrationArch 등) →
#       현 6 permanent deputy (plugins/codeforge-design/CLAUDE.md SSOT). CodebaseMapper/Refactor 는
#       deputy 아닌 4-tuple sub-tuple 이므로 roster 제외.
#   (b) <6 deputy row = silent SKIP (return 0 무로그) → honest WARN (fan-out 미spawn 의심 관측 baseline).
#       env=0 (deputy row 부재) 는 honest SKIP 사유 명시 (meta-hollow-gate 차단 — concept R-5).
#   enforcement (spawn 강제) 는 본 Story 미구현 — PR-time 관측 baseline 만 (PreToolUse Agent matcher P2
#   empirical 미확정, [empirical-source: TBD], 설계 §결정10d 보류). warning-tier 유지 (ADR-128 상속).
#
# CFP-2652 (Epic CFP-2468 W3 follow-up) 정확성 갭 3건 정정:
#   gap (a) env-absence vs evidence-absence re-key — check_parallelization 에 design-row 카운터 신설
#     (`- lane: 설계$` 행 수) 후 4-분기 re-key: (i) design_rows==0 → env-absence env=0 SKIP /
#     (ii) design_rows≥1 ∧ spawned_at_count<design_rows → evidence-absence honest WARN(★partial 포함,
#     env=0 아님) / (iii) ==design_rows ∧ <6 → 진짜 fan-out 미달 WARN / (iv) ==design_rows ∧ ≥6 →
#     기존 timing diff. 구 로직은 spawned_at '값 개수'만 카운트해 evidence-absence 를 env=0 로 오표기.
#   gap (c) Check 7 — PR label `gate:<lane>-pass` ↔ `## Lane evidence` 블록 lane PASS 행 forward 정합
#     (좁은 class, §14 면제와 독립, shape-aware). gate→lane 매핑 = 단일 SSOT
#     docs/inter-plugin-contracts/gate-lane-map-v1.yaml 소비 (병렬 table 금지 — phase-gate-mergeable.yml
#     lanePrefixForGate 와 동일 canonical datum). warning-tier (Check 1-5 패턴 fail-counted, local-only).
#
# Usage:
#   bash scripts/check-lane-evidence.sh [--story <path>] [--pr <number>] [--strict] [--quiet]
#                                        [--check-parallelization]
#                                        [--pr-labels-file <f>] [--pr-block-file <f>]  # CFP-2652 gap c self-test seam
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
# CFP-2652 gap (c): test-injection seam — gh fetch 대신 파일에서 PR labels/block 주입 (self-test 용).
#   미설정 시 gh CLI 경로(production) 사용. label↔block write-back Check 7 의 discriminating self-test 지원.
PR_LABELS_FILE=""
PR_BLOCK_FILE=""

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT=1; shift ;;
        --story) STORY_PATH="$2"; shift 2 ;;
        --pr) PR_NUMBER="$2"; shift 2 ;;
        --check-parallelization) CHECK_PARALLELIZATION=1; shift ;;
        --pr-labels-file) PR_LABELS_FILE="$2"; shift 2 ;;   # CFP-2652 gap c self-test seam
        --pr-block-file) PR_BLOCK_FILE="$2"; shift 2 ;;     # CFP-2652 gap c self-test seam
        -h|--help)
            sed -n '/^# check-lane-evidence/,/^# Effective date/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

log() { [ $QUIET -eq 0 ] && printf '%s\n' "$1"; }
log_err() { printf '%s\n' "$1" >&2; }

# Lane names (한국어 8종 — CFP-2326 / ADR-125: 요구사항-리뷰 9번째 lane 추가)
declare -a LANES=("요구사항" "요구사항-리뷰" "설계" "설계-리뷰" "구현" "구현-리뷰" "구현-테스트" "보안-테스트")

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
#   CFP-2652 gap (c): PR_BLOCK_FILE 주입 시 gh 대신 파일 body 사용 (self-test seam).
fetch_pr_lane_evidence() {
    local pr_num="$1"
    local body
    if [ -n "$PR_BLOCK_FILE" ]; then
        body="$(cat "$PR_BLOCK_FILE" 2>/dev/null || true)"
    else
        if [ -z "$pr_num" ]; then return 1; fi
        if ! command -v gh >/dev/null 2>&1; then
            log_err "gh CLI 미설치 — PR description fetch 불가"
            return 1
        fi
        body="$(gh pr view "$pr_num" --json body --jq '.body' 2>/dev/null || true)"
    fi
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

# CFP-2652 gap (c): PR label 목록 fetch (gate:<lane>-pass 라벨 파싱 source).
#   PR_LABELS_FILE 주입 시 gh 대신 파일(개행 구분 label 목록) 사용 (self-test seam).
fetch_pr_labels() {
    local pr_num="$1"
    if [ -n "$PR_LABELS_FILE" ]; then
        cat "$PR_LABELS_FILE" 2>/dev/null || true
        return 0
    fi
    if [ -z "$pr_num" ]; then return 0; fi
    command -v gh >/dev/null 2>&1 || return 0
    gh pr view "$pr_num" --json labels --jq '.labels[].name' 2>/dev/null || true
}

# CFP-2652 gap (c) §3.2.1: gate→lane 매핑 SSOT 소비 (단일 SSOT — 병렬 table 하드코딩 금지).
#   SSOT = docs/inter-plugin-contracts/gate-lane-map-v1.yaml, flat top-level `gate:<lane-en>-pass: <한글 lane>`.
#   nested-YAML parse 불요 — 첫 ': ' delimiter line-split robust 추출 → declare -A GATE_LANE_MAP.
#   canonical datum = plain 한글 lane (JS phase-gate-mergeable.yml lanePrefixForGate 와 동일 datum, drift 0).
# 반환: 0 = 1+ entry 로드 성공 / 1 = 파일 부재 또는 entry 0.
load_gate_lane_map() {
    local map_file="$1"
    GATE_LANE_MAP=()
    [ -f "$map_file" ] || return 1
    local line key val
    while IFS= read -r line; do
        line="${line%$'\r'}"
        # gate:<lane-en>-pass: <한글 lane> 행만 (metadata/comment 무시 — flat top-level 필터)
        case "$line" in
            gate:*-pass:\ *) : ;;
            *) continue ;;
        esac
        key="${line%%: *}"        # 첫 ': ' 앞 = gate:<lane-en>-pass
        val="${line#*: }"         # 첫 ': ' 뒤 = 한글 lane (+ trailing comment 가능)
        val="${val%%#*}"          # inline comment 제거
        val="$(printf '%s' "$val" | sed -E 's/[[:space:]]+$//')"  # trailing ws strip
        [ -n "$key" ] && [ -n "$val" ] && GATE_LANE_MAP["$key"]="$val"
    done < "$map_file"
    [ "${#GATE_LANE_MAP[@]}" -gt 0 ]
}

# CFP-2652 gap (c): `## Lane evidence` 블록에서 한글 lane 행이 PASS outcome 인지 검사.
#   행 형식 = `- <lane>: <OUTCOME>` (extract_pr_lanes 파싱 형식 정합). shape-aware — 정확 lane-name 매칭.
# 반환: 0 = 해당 lane 행 존재 ∧ outcome=PASS / 1 = 행 부재 OR non-PASS(SKIPPED 등).
block_lane_is_pass() {
    local block="$1" lane="$2"
    local row
    row="$(printf '%s\n' "$block" | grep -E "^-[[:space:]]+${lane}:" || true)"
    [ -z "$row" ] && return 1   # 행 부재 = write-back 불일치
    printf '%s' "$row" | grep -qiE ':[[:space:]]*PASS([[:space:]]|$)'
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
# Deputy roles (현 6 permanent — CFP-2471 stale roster 정정):
#   SecurityArchitectAgent / InfraOperationalArchitectAgent / TestContractArchitectAgent /
#   DataArchitectAgent / ModuleArchitectAgent / APIContractArchitectAgent
#   (구 토큰 CodebaseMapper/Refactor = 4-tuple sub-tuple, deputy 아님 → roster 제외.
#    OpRiskArch → InfraOperationalArchitectAgent, DataMigrationArch → DataArchitectAgent rename)
# Strategy: 설계 lane 의 모든 row 의 spawned_at 추출 → epoch 변환 → max-min 차이 < 60s 검증
# 조건: 6개 이상 deputy row 존재할 때만 timing 검증 (agent teams env=1 context 만 의미있음).
#   CFP-2471 (W3): env=0 (deputy row 0개) = honest SKIP 사유 명시. 1~5 row (fan-out 미달 의심) = honest WARN
#   (관측 baseline — silent SKIP 차단, meta-hollow-gate 회피). enforcement 미구현 (관측만, [empirical-source: TBD]).
check_parallelization() {
    local yaml="$1"
    if [ -z "$yaml" ]; then
        log_err "[PARALLELIZATION SKIP] §14 YAML block 없음 — skip"
        return 0
    fi

    # ── CFP-2652 gap (a): design-row 카운터 신설 (env-absence vs evidence-absence 오분류 진원 정정) ──
    # design_rows = `- lane: 설계$` 행 자체의 수 (spawned_at 유무 무관, awk unconditional).
    #   구 로직은 spawned_at '값 개수'만 카운트 → env-absence(설계 행 0)와 evidence-absence
    #   (설계 행 有 ∧ spawned_at 無/malformed)를 구조적으로 구별 불가, 무조건 "env=0" 오표기.
    #   design-row 카운터를 spawned_at 카운트와 분리해 4-분기 re-key (§3.1 H1).
    local design_rows
    design_rows="$(printf '%s' "$yaml" | awk '/- lane: 설계$/ { drows++ } END { print drows+0 }')"

    # 설계 행 한정 spawned_at '값' 목록 추출 (기존 awk 재사용 — BSD-compat sub()/substr()).
    local spawned_ts
    spawned_ts="$(printf '%s' "$yaml" | awk '
        /- lane: 설계$/ { inrow=1 }
        inrow && /spawned_at:/ {
            line=$0
            sub(/.*spawned_at:[[:space:]]*/, "", line)
            sub(/[[:space:]#].*/, "", line)
            print line
        }
        /- lane: / && !/- lane: 설계$/ { if (inrow) inrow=0 }
    ')"

    # ISO8601 → epoch (GNU date or BSD date). 파싱 성공분만 유효 timing 으로 카운트.
    #   EC-1 (malformed spawned_at): 파싱 실패 → timestamps 미포함 → spawned_at_count < design_rows
    #   → (ii) evidence-absence (env=0 절대 아님, design_rows≥1 이므로 env-absence 분기 구조적 미도달).
    local timestamps=()
    while IFS= read -r ts; do
        [ -z "$ts" ] && continue
        local epoch
        epoch="$(date -d "$ts" +%s 2>/dev/null || date -jf '%Y-%m-%dT%H:%M:%SZ' "$ts" +%s 2>/dev/null || true)"
        if [ -n "$epoch" ] && [[ "$epoch" =~ ^[0-9]+$ ]]; then
            timestamps+=("$epoch")
        fi
    done <<< "$spawned_ts"
    local spawned_at_count="${#timestamps[@]}"   # 유효 timing 개수 (spawned_at_count ≤ design_rows 불변)

    # ── 4-분기 re-key (design_rows / spawned_at_count 2-축 deterministic) ──
    #   correctness = (iii)/(iv) `spawned_at_count == design_rows` equality 가드의 상호배타성
    #   ((ii) `< design_rows` ⊥ ==) — 평가 순서와 무관. (ii)-먼저 배치 = 가독성 목적 secondary clarity.
    if [ "$design_rows" -eq 0 ]; then
        # (i) env-absence: `- lane: 설계` 행 자체 부재 = env=0 (one-shot Agent spawn, deputy row 구조적 부재).
        #   CFP-2471 (W3): silent SKIP 대신 honest SKIP 사유 명시 (meta-hollow-gate 차단 — concept R-5).
        log "[PARALLELIZATION SKIP] 설계 lane deputy row 0개 — agent teams env=0 (one-shot Agent spawn, deputy row 구조적 부재). honest SKIP 사유: env=0 fan-out 관측 불가 (ADR-039 default, ADR-044 §결정 5 N/A in env=0)"
        return 0
    elif [ "$spawned_at_count" -lt "$design_rows" ]; then
        # (ii) evidence-absence (★partial 포함): 설계 행 실재하나 유효 spawned_at 이 부족 (M<N).
        #   CFP-2652 gap (a) — 이 케이스를 env=0 로 오표기하던 결함 정정. 설계 행이 실재하므로
        #   환경 부재(env-absence) 아님 — timing evidence 만 결손. env=0/fan-out 미달 표기 금지.
        log_err "[PARALLELIZATION WARN] 설계 lane evidence-absence — 설계 행 ${design_rows}개 중 유효 spawned_at ${spawned_at_count}개 (${spawned_at_count}<${design_rows}, timing 증거 누락). 설계 행이 실재하므로 환경 부재(env-absence) 아님 — timing evidence 만 결손 (CFP-2652 gap a re-key). honest WARN — 관측 baseline (warning-tier, enforcement 미구현)"
        return 0
    elif [ "$spawned_at_count" -eq "$design_rows" ] && [ "$design_rows" -lt 6 ]; then
        # (iii) 진짜 fan-out 미달: 설계 행 各 spawned_at 완비(== design_rows)이나 6 permanent 미달.
        #   CFP-2471 (W3): silent SKIP 대신 honest WARN — fan-out 미spawn 의심 가시화 (warning-tier).
        log_err "[PARALLELIZATION WARN] 설계 lane deputy row ${design_rows}개 (${design_rows}<6 permanent) 各 spawned_at 완비 — deputy row < 6 = fan-out 미spawn 의심 (CFP-2471 / Epic CFP-2468 W3). 현 6 permanent deputy = SecurityArchitectAgent / InfraOperationalArchitectAgent / TestContractArchitectAgent / DataArchitectAgent / ModuleArchitectAgent / APIContractArchitectAgent"
        log_err "  (CONDITIONAL/N/A deputy (LiveOps/LiveOrdering/ProductionEvidence + aggregate_arch.applicable:false ModuleArch) 정당 skip 은 shape-aware 기대 roster 로 false-positive 차단 — 본 관측은 WARN 만, enforcement 미구현)"
        return 0
    fi

    # (iv) design_rows >= 6 AND spawned_at_count == design_rows → 기존 timing diff (<60s) 검사.
    #   (spawned_at_count == design_rows >= 6 보장 → timestamps 6+ 개, min/max index-0 안전)
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
    #   CFP-2652 gap (c): PR_BLOCK_FILE 주입 시 PR_NUMBER 없이도 block 소스 취득 (self-test seam).
    local pr_block=""
    if [ -n "$PR_NUMBER" ] || [ -n "$PR_BLOCK_FILE" ]; then
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

    # Check 7 (CFP-2652 gap c): PR label `gate:<lane>-pass` ↔ `## Lane evidence` 블록 lane PASS 행 정합.
    #   forward-only (label→block, 좁은 class — 전 write-back 정합 보장 아님). §14 면제와 독립 실행
    #   (label 기반이라 story_yaml gate 무관 — Check 4 와 disjoint, dogfood PR 도 검사). shape-aware
    #   (정확 lane-name — 요구사항 ≠ 요구사항-리뷰). warning-tier (Check 1-5 패턴 fail-counted, local-only).
    #   블록 전체 부재(EC-4)면 pr_block 비어 미발동 (Check 3 소관).
    if [ -n "$pr_block" ]; then
        local map_file
        if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
            map_file="${CLAUDE_PLUGIN_ROOT}/docs/inter-plugin-contracts/gate-lane-map-v1.yaml"
        else
            map_file="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/docs/inter-plugin-contracts/gate-lane-map-v1.yaml"
        fi
        declare -A GATE_LANE_MAP=()
        if ! load_gate_lane_map "$map_file"; then
            # SSOT 부재/공백 = FAIL (게이트 자기무결성 — SSOT 없이 검사 silent-skip 은 meta-hollow-gate).
            log_err "[FAIL] Check 7 gate-lane-map SSOT 로드 실패: $map_file — gap c label↔block 검사 불가"
            fail=$((fail + 1))
        else
            local pr_labels gate lane_kr wb_mismatch=0
            pr_labels="$(fetch_pr_labels "$PR_NUMBER")"
            while IFS= read -r gate; do
                [ -n "$gate" ] || continue
                lane_kr="${GATE_LANE_MAP[$gate]:-}"
                [ -z "$lane_kr" ] && continue   # 매핑 없는 gate label = 좁은 class 대상 아님 (forward-only)
                if ! block_lane_is_pass "$pr_block" "$lane_kr"; then
                    log_err "[FAIL] Check 7 write-back 불일치 — label '$gate' 존재 ∧ '## Lane evidence' 블록 '$lane_kr' PASS 행 부재/non-PASS (CFP-2652 gap c). label↔block outcome mismatch — forward write-back 결손 (특정 class, 전 write-back 정합 주장 아님)"
                    wb_mismatch=$((wb_mismatch + 1))
                fi
            done <<< "$(printf '%s\n' "$pr_labels" | grep -E '^gate:.*-pass$' || true)"
            if [ "$wb_mismatch" -gt 0 ]; then
                fail=$((fail + wb_mismatch))
            else
                log "[OK] Check 7 label↔block write-back 정합 (gate:*-pass ↔ 블록 lane PASS, shape-aware)"
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
