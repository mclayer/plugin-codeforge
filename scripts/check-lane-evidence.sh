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
# CFP-2914 (AC-2a) review-peer co-dispatch 관측 leg 신설:
#   check_peer_codispatch() — 리뷰 4-lane (요구사항-리뷰 / 설계-리뷰 / 구현-리뷰 / 보안-테스트) 에서
#   ClaudeReviewAgent / CodexReviewAgent 2 peer 가 같은 (lane, iteration) 그룹에 60초 내로 개시
#   선언됐는지 관측. 산출 성격 = 관측 채널(로그 산출) — 산출은 로그뿐이다 (warning-tier · FAIL 미계상 ·
#   exit code 무변경 · merge 영향 0 · 전 경로 return 0).
#   ★ 설계 leg (check_parallelization) 는 무손상 존치 — 내부 분기 추가가 아니라 형제 함수 신설이다
#     (설계 leg 회귀 표면 0 · 출력 bit-identical 보존).
#   ★ 비대칭 은폐 금지 (정직 문면): 본 Story 는 peer leg 만 2축 키잉(신원·그룹화)으로 정정하고,
#     설계 leg 는 같은 그룹화 결함(서로 다른 iteration 의 row 를 한 그룹으로 합침)을 보유한 채
#     존치한다. 두 leg 의 판정 품질은 비대칭이며 이 사실을 지운 채 "관측 배선을 복원했다" 로
#     요약하면 over-claim 이다. (관찰됨 · 미조치 — 설계 leg 수정은 출력 bit-identical 보존 의무와
#     정면 충돌하고, timing 분기의 owner 는 ADR-044 §결정 5 로 본 Story scope 밖이다.)
#   RF-3: 두 leg 공유 측정 술어 _evaluate_spawn_timing() + 임계 상수 SPAWN_TIMING_THRESHOLD_S
#     단일 정의 site 추출 (임계값이 두 곳에 하드코딩되면 drift).
#
# Usage:
#   bash scripts/check-lane-evidence.sh [--story <path>] [--pr <number>] [--strict] [--quiet]
#                                        [--check-parallelization]
#                                        [--pr-labels-file <f>] [--pr-block-file <f>]  # self-test seam ∧ CI production 입력
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
# --pr-labels-file / --pr-block-file: gh fetch 대신 파일에서 PR labels/block 주입. 미설정 시 gh CLI 경로.
#   CFP-2652 gap (c) 도입 시점에는 self-test 전용 injection seam 이었다 (label↔block write-back Check 7 의
#   discriminating self-test 지원).
#   ★ CFP-2914 (AC-5) 정정 — 현재는 self-test seam 이자 **production 입력 경로**다:
#     .github/workflows/lane-evidence-check.yml 의 bash step 이 PR body·labels 를 $RUNNER_TEMP 파일로
#     떨어뜨린 뒤 이 두 인자로 주입한다 (스크립트 인자 직접 보간 0). "self-test 용" 단독 서술은 실재와
#     불일치이므로 폐기한다 (미정정 시 declared-not-bound 를 본 Story 안에서 재생산).
PR_LABELS_FILE=""
PR_BLOCK_FILE=""

while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT=1; shift ;;
        --story) STORY_PATH="$2"; shift 2 ;;
        --pr) PR_NUMBER="$2"; shift 2 ;;
        --check-parallelization) CHECK_PARALLELIZATION=1; shift ;;
        --pr-labels-file) PR_LABELS_FILE="$2"; shift 2 ;;   # self-test seam ∧ CI production 입력 (CFP-2914)
        --pr-block-file) PR_BLOCK_FILE="$2"; shift 2 ;;     # self-test seam ∧ CI production 입력 (CFP-2914)
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

# ── CFP-2914 RF-3: 두 leg 가 공유하는 유일 임계 상수 — 단일 정의 site ────────────────
#   설계 leg (check_parallelization) 와 peer leg (check_peer_codispatch) 가 이 상수 하나만 본다.
#   리터럴 60 을 다른 곳에 다시 적으면 그 즉시 drift 표면이 생긴다 (메시지 문자열 포함 — 아래
#   설계 leg 메시지도 리터럴이 아니라 이 상수를 보간한다. 보간 결과는 byte 동일하므로 설계 leg
#   출력 bit-identical 은 무손상).
readonly SPAWN_TIMING_THRESHOLD_S=60

# CFP-2914 §3.3.4.2 규칙 1 — peer 리뷰 대상 lane closed-set. 파일 내부 1곳, 정확 일치 lookup.
#   `*리뷰*` substring 금지: 그 실패 양식이 '보안-테스트' 그룹을 통째로 누락시킨 전례를 낳았다.
PEER_REVIEW_LANES=("요구사항-리뷰" "설계-리뷰" "구현-리뷰" "보안-테스트")

# CFP-2914 §3.3.4.2 규칙 2 — peer 신원 closed-set. `agent` 선두 토큰 정확 일치 대상.
PEER_AGENT_IDS=("ClaudeReviewAgent" "CodexReviewAgent")

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

# ── CFP-2914 RF-3 — 두 leg 공유 **측정** 술어 ──────────────────────────────────────────
# _evaluate_spawn_timing <expected_min_rows> <row_count> <valid_ts_count> <ts_array_name>
#
#   측정만 수행한다. 로그 0줄 · 판정 0건 · 문면 0건 · 항상 return 0.
#   공유하는 것은 측정(state + diff + 임계 비교)이고 공유하지 않는 것은 판정과 문면이다 —
#   같은 상태라도 두 leg 에서 무게가 다르기 때문이다 (설계 leg 의 below_expected = advisory
#   WARN / peer leg 의 below_expected = group-level '판정 불가' 라는 1급 산출).
#   ★ 문면을 이 술어 안에 넣으면 설계 leg 출력에 새 문장이 섞여 '설계 leg 출력 bit-identical'
#     이 즉시 깨진다. 문면은 전적으로 caller 소유다.
#
#   ★ 입력 전제 (caller 책임 — 본 함수는 검증하지 않는다):
#     row_count / valid_ts_count / ts_array 는 caller 가 이미 필터를 통과시킨 값이다
#     (peer leg = lane 정확일치 ∧ agent 선두토큰 정확일치 ∧ 동일 iteration).
#     본 함수는 "몇 개를 셌는가" 를 묻지 않고 "센 것들이 임계 안에 있는가" 만 잰다.
#     caller 가 필터를 빠뜨려도 본 함수는 그 사실을 알 수 없다.
#
#   out-global (호출 직후 읽기). 접두 SPAWN_TIMING_ 강제 — 진단 leg 의 실효 3-상태 enum
#   (EFFECTIVE/INDETERMINATE/NON_EFFECTIVE) 과 값공간이 섞이지 않게 한다. 두 enum 은 disjoint:
#   3-상태 = "산출을 냈는가"(원장 입력) / 아래 4-상태 = "측정이 가능한가"(§14 row 입력).
#
#   SPAWN_TIMING_STATE — 4-state. 값 나열이 아니라 **의미** (ADR-068 I-1):
#     env_absent       관측 단위 자체가 0 = 환경 부재.
#                      설계 leg = `- lane: 설계` 행 0 (env=0) / peer leg = PEER-0 (peer 신원 0종).
#     evidence_absent  단위는 있으나 유효 spawned_at 이 결손 = 등식 가드 불성립
#                      (valid_ts_count != row_count). 시각 증거만 없는 상태이지 환경 부재가 아니다.
#                      ★ 이 상태가 timing 분기 도달을 막는다 — 없으면 'row 2 ∧ 유효 시각 1' 형상이
#                        min == max 로 diff = 0s 허위 통과를 낸다.
#     below_expected   등식 완비이나 기대 하한 미만. 설계 leg = 6 미달(fan-out 미달 의심) /
#                      peer leg = PEER-1 = group-level '판정 불가'.
#                      ★ 어느 leg 에서도 통과 판정으로 접히지 않는다.
#     measurable       하한 이상 ∧ 등식 완비 → diff 산출 가능. 설계 leg = 분기 (iv) / peer leg = PEER-2.
#
#   SPAWN_TIMING_DIFF      int 초 (max-min). measurable 일 때만 유의미, 그 외 -1
#   SPAWN_TIMING_WITHIN    1 = diff < SPAWN_TIMING_THRESHOLD_S / 0 = 미달. measurable 아니면 -1
#   SPAWN_TIMING_ROWS      관측 row 수 (필터 통과분). ★ 세는 대상이 leg 마다 다르다 —
#                          설계 leg = `- lane: 설계` **행 수** / peer leg = **distinct peer 신원 수**.
#                          이 키 비대칭을 지우면 "동형이니 row 수를 그대로 쓰면 된다" 는 오독이 복원된다.
#   SPAWN_TIMING_EXPECTED  기대 하한 (설계 leg 6 / peer leg 2)
#
#   구현 메모: ts_array 는 nameref (bash 4.3+) 로 받는다. 이 파일은 이미 declare -A / ${var^^}
#   로 bash 4+ 에 의존하며, local -n 사용으로 bash 4.3+ 하한을 명시한다.
_evaluate_spawn_timing() {
    local expected_min="$1" row_count="$2" valid_ts_count="$3"
    local -n _sts_ref="$4"

    SPAWN_TIMING_EXPECTED="$expected_min"
    SPAWN_TIMING_ROWS="$row_count"
    SPAWN_TIMING_DIFF=-1
    SPAWN_TIMING_WITHIN=-1

    if [ "$row_count" -eq 0 ]; then
        SPAWN_TIMING_STATE="env_absent"
        return 0
    fi
    # 등식 가드. valid_ts_count <= row_count 불변이므로 != 는 < 와 동치이며, 등식 형태로 적어
    # "완비인가" 라는 의도를 코드에 남긴다.
    if [ "$valid_ts_count" -ne "$row_count" ]; then
        SPAWN_TIMING_STATE="evidence_absent"
        return 0
    fi
    if [ "$row_count" -lt "$expected_min" ]; then
        SPAWN_TIMING_STATE="below_expected"
        return 0
    fi

    # 여기 도달 = 등식 완비 ∧ 하한 이상 → 배열 원소 1개 이상 보장 (index-0 안전).
    SPAWN_TIMING_STATE="measurable"
    local min_ts max_ts ts
    min_ts="${_sts_ref[0]}"
    max_ts="${_sts_ref[0]}"
    for ts in "${_sts_ref[@]}"; do
        [ "$ts" -lt "$min_ts" ] && min_ts="$ts"
        [ "$ts" -gt "$max_ts" ] && max_ts="$ts"
    done
    SPAWN_TIMING_DIFF=$(( max_ts - min_ts ))
    # ★ 임계 비교 단일 site (RF-3). 두 leg 의 단일 실패점이므로, 이 비교 연산자 하나를 변조하면
    #   양 leg 의 경계 케이스가 동시에 무너져야 한다 — 그것이 "단일 실패점이 실제로 단일인가" 의
    #   직접 증거다.
    if [ "$SPAWN_TIMING_DIFF" -lt "$SPAWN_TIMING_THRESHOLD_S" ]; then
        SPAWN_TIMING_WITHIN=1
    else
        SPAWN_TIMING_WITHIN=0
    fi
    return 0
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
    #   CFP-2914 RF-3: min/max 산출 · diff · 임계 비교를 공유 술어 _evaluate_spawn_timing() 단일
    #   site 로 이관. 위 (i)~(iii) 사다리의 분기 조건 · 로그 문면 · 평가 순서는 무변경이고,
    #   아래 메시지의 60 리터럴은 ${SPAWN_TIMING_THRESHOLD_S} 보간으로 대체되나 보간 결과가
    #   byte 동일하므로 설계 leg 출력 bit-identical 이 보존된다. 문면은 caller(본 함수) 소유 —
    #   술어는 문면 0건이다.
    _evaluate_spawn_timing 6 "$design_rows" "$spawned_at_count" timestamps
    local diff="$SPAWN_TIMING_DIFF"
    if [ "$SPAWN_TIMING_WITHIN" -eq 1 ]; then
        log "[PARALLELIZATION OK] TEAM-DESIGN deputy spawned_at diff = ${diff}s < ${SPAWN_TIMING_THRESHOLD_S}s (${#timestamps[@]} rows)"
    else
        log_err "[PARALLELIZATION WARN] TEAM-DESIGN deputy spawned_at diff = ${diff}s >= ${SPAWN_TIMING_THRESHOLD_S}s — Parallelization 기준 미달 (ADR-044 §결정 5). diff > ${SPAWN_TIMING_THRESHOLD_S}s = sequential spawn 의심"
        # NOTE: advisory only — not counted as fail (no agent teams enforcement in env=0 contexts)
        # If strict mode is required for parallelization, use --strict with this flag
        log_err "  (advisory: diff >= ${SPAWN_TIMING_THRESHOLD_S}s 는 FAIL 아님. Strict parallelization enforcement 는 CFP-137 후속 CFP scope)"
    fi
    return 0
}

# ── CFP-2914 (AC-2a) — review-peer co-dispatch 관측 leg (형제 함수) ──────────────────────
# 리뷰 4-lane 에서 ClaudeReviewAgent / CodexReviewAgent 2 peer 가 같은 (lane, iteration) 그룹에
# 60초 내로 개시 선언됐는지 관측한다. 산출 = 관측 채널(로그 산출) — 산출은 로그뿐이다.
#
# 2축 키잉 규약 1~7 — 규약을 어기면 판정 자체가 무의미해진다:
#   1 lane 축     PEER_REVIEW_LANES 정확 일치 (substring 금지).
#   2 그룹 키     (lane 정확일치, iteration). 서로 다른 iteration 의 row 를 co-dispatch 비교
#                 대상으로 묶지 않는다 — §14 iteration 의 계약 의미가 dispatch round 식별자다.
#   3 신원 계수   agent 값 좌측 trim 후 첫 [공백 또는 '('] 직전까지의 **선두 토큰** 이
#                 PEER_AGENT_IDS 에 정확 일치할 때만 peer 1 로 계수.
#                 substring 금지 · 토큰경계 regex 금지 — 둘 다 실측 FP 가 동일하다. 함정은
#                 경계가 아니라 **한 row 의 agent 가 여러 신원을 서술**하는 것이다:
#                 `agent: DesignReviewPLAgent (codeforge-review@mclayer) + ClaudeReviewAgent +
#                 CodexReviewAgent` → 이 row 는 PL row 로 분류하고 peer 계수 0 이 정답.
#   4 collapse    같은 (lane, iteration) 그룹 안에서 동일 peer 신원이 2행 이상이면 spawned_at
#                 **최소값을 대표**로 collapse. 파일 출현 순서 의존 금지 — 순서에 의존하면 문서
#                 편집만으로 판정이 바뀌어 재현성이 붕괴한다.
#                 ★ 정직 라벨: 동일 peer 신원이 같은 (lane, iteration) 에 2행인 형상은 **실 코퍼스
#                   0건**이다. 즉 규칙 4 는 관측된 결함의 수리가 아니라 순서 의존을 사전 차단하는
#                   **합성 전용 방어 규칙**이며 그 fixture 도 합성이다. "실물에서 관측됐다" 로
#                   쓰면 거짓이다.
#   5 정규화      spawned_at 값에서 주변 따옴표 strip + 후행 주석(# 이후) strip + **CR strip**
#                 후 date -d 파싱. CR strip 은 같은 파일 내 방어 비대칭의 정산이다 —
#                 load_gate_lane_map() 은 line="${line%$'\r'}" 로 CR 을 벗기는데
#                 check_parallelization() 의 awk 는 CR 처리가 0건이다. 신규 leg 는 명시한다.
#   6 TZ-less     offset(±HH:MM / ±HHMM) 도 Z 도 보유하지 않은 값은 파싱 성공으로 계상하지
#                 않는다 → evidence_absent 낙하. 근거 = GNU date -d "2026-05-12T16:05:30" 은
#                 파싱에 성공하되 러너의 로컬 TZ 로 해석하며, KST↔UTC 차 32,400초는 60초 임계의
#                 540배라 한 그룹에 혼재하면 판정이 무의미해진다.
#                 ★ 정직 라벨: 현 코퍼스에 TZ-less 값은 **0건**이다 — 관측된 결함의 수리가 아니라
#                   **미발생 결함의 사전 봉쇄**이며, 이 성격을 숨기지 않는다.
#   7 iteration   결측 = 판정 **비대상** 낙하 (위반 계상 금지). 결측 row 를 한 그룹으로 병합하지
#                 않는다. iteration 이 정수 아닌 자유 서술이면 그 문자열 자체가 그룹 키가 되어
#                 결과적으로 판정 불가 방향으로만 degrade 한다 (canonical 정규화 미채택 —
#                 free-text → key 승격 표면을 하나 더 만들지 않기 위함).
#
# ★ 등식 가드: peer_rows >= 2 ∧ peer_ts_count == peer_rows 둘 다 충족할 때만 timing 분기에
#   도달한다 (술어의 evidence_absent 가 집행). 미승계 시 'PL 1행이 두 peer 명을 서술' 하는 실물
#   형상이 peer_rows 2 ∧ 유효 시각 1 → min == max → diff = 0s 허위 통과를 낸다.
#
# lane closed-set 을 gate-lane-map-v1.yaml 외부 SSOT 로 승격하지 않는 근거 = **의미 disjoint**.
#   그 registry 가 담는 것은 'gate 라벨 → lane 매핑' 이고 본 leg 가 필요한 것은 'peer 리뷰 대상
#   lane 집합' 이다. 값이 일부 겹친다는 이유로 서로 다른 관심사를 한 SSOT 에 묶으면 의미 결합이
#   생긴다. 승격 trigger = **peer 대상 lane 집합을 소비하는 2번째 지점이 생길 때**.
check_peer_codispatch() {
    local yaml="$1"
    if [ -z "$yaml" ]; then
        log_err "[PEER CO-DISPATCH N/A] §14 YAML block 없음 — skip"
        return 0
    fi

    # §14 row 평탄화: 레코드 1행 = lane <US> iteration <US> agent <US> spawned_at.
    #   따옴표/주석/CR strip 은 규칙 5. agent 는 선두 토큰 추출을 위해 원문(trim 만) 유지.
    #   ★ 구분자가 US(0x1f)인 이유: TAB 은 IFS whitespace 라서 `IFS=$'\t' read` 가 연속 구분자를
    #     하나로 접어 **빈 필드를 소멸**시킨다 (iteration 결측 row 에서 agent 값이 iteration 칸으로
    #     밀려 들어가 규칙 7 이 무력화된다 — 실측 확인). US 는 IFS whitespace 가 아니므로 빈 필드가
    #     보존되고, 값 안의 공백도 그대로 남는다 (lane `설계 리뷰` 같은 비정합 표기 보존).
    local records
    records="$(printf '%s' "$yaml" | awk '
        function trim(s) { sub(/^[[:space:]]+/, "", s); sub(/[[:space:]]+$/, "", s); return s }
        function kv(line,   v) { v = line; sub(/^[^:]*:[[:space:]]*/, "", v); return trim(v) }
        function clean(v,   f, l) {
            sub(/[[:space:]]*#.*$/, "", v)
            v = trim(v)
            if (length(v) >= 2) {
                f = substr(v, 1, 1); l = substr(v, length(v), 1)
                if (f == l && (f == "\"" || f == "\047")) v = substr(v, 2, length(v) - 2)
            }
            return trim(v)
        }
        BEGIN { OFS = "\037"; have = 0 }
        { sub(/\r$/, "") }
        /^[[:space:]]*-[[:space:]]+lane:/ {
            if (have) print lane, iter, agent, sat
            have = 1; lane = clean(kv($0)); iter = ""; agent = ""; sat = ""
            next
        }
        have && /^[[:space:]]*iteration:/  { if (iter  == "") iter  = clean(kv($0)); next }
        have && /^[[:space:]]*agent:/      { if (agent == "") agent = kv($0);        next }
        have && /^[[:space:]]*spawned_at:/ { if (sat   == "") sat   = clean(kv($0)); next }
        END { if (have) print lane, iter, agent, sat }
    ')"

    local -a group_keys=()
    declare -A group_seen=() peer_seen=() peer_min=() lane_group_count=() lane_peer=()
    local nonconformant=0 missing_iteration=0
    local lane iter agent sat ident key mkey prev epoch x in_lane is_peer

    while IFS=$'\037' read -r lane iter agent sat; do
        [ -n "$lane" ] || continue

        # 규칙 1 — lane 축 정확 일치.
        in_lane=0
        for x in "${PEER_REVIEW_LANES[@]}"; do
            if [ "$lane" = "$x" ]; then in_lane=1; break; fi
        done
        if [ "$in_lane" -eq 0 ]; then
            # 리뷰-유사 표기인데 closed-set 미매칭이면 별도 계상 (판정 모집단 미진입).
            #   이 heuristic 매칭은 **카운터 전용**이며 어떤 판정에도 입력되지 않는다.
            if printf '%s' "$lane" | grep -qiE '리뷰|review|보안|security'; then
                nonconformant=$((nonconformant + 1))
            fi
            continue
        fi

        # 규칙 7 — iteration 결측은 판정 비대상.
        if [ -z "$iter" ]; then
            missing_iteration=$((missing_iteration + 1))
            continue
        fi

        # 규칙 2 — 그룹 키 = (lane 정확일치, iteration). 합성 키 구분자도 US(0x1f) — 값에 등장할 수
        #   없는 제어문자라 키 충돌이 구조적으로 불가능하다.
        key="${lane}"$'\037'"${iter}"
        if [ -z "${group_seen[$key]:-}" ]; then
            group_seen["$key"]=1
            group_keys+=("$key")
            lane_group_count["$lane"]=$(( ${lane_group_count[$lane]:-0} + 1 ))
        fi

        # 규칙 3 — 신원 축: 선두 토큰 정확 일치 (substring 금지).
        ident="${agent%%[[:space:](]*}"
        is_peer=0
        for x in "${PEER_AGENT_IDS[@]}"; do
            if [ "$ident" = "$x" ]; then is_peer=1; break; fi
        done
        [ "$is_peer" -eq 1 ] || continue

        mkey="${key}"$'\037'"${ident}"
        peer_seen["$mkey"]=1
        lane_peer["${lane}"$'\037'"${ident}"]=1

        # 규칙 5·6 — 정규화된 spawned_at → epoch. TZ 미보유 값은 파싱 시도조차 하지 않는다.
        epoch=""
        if [[ "$sat" =~ ([Zz]|[+-][0-9]{2}:?[0-9]{2})$ ]]; then
            epoch="$(date -d "$sat" +%s 2>/dev/null || date -jf '%Y-%m-%dT%H:%M:%SZ' "$sat" +%s 2>/dev/null || true)"
            [[ "$epoch" =~ ^[0-9]+$ ]] || epoch=""
        fi
        if [ -n "$epoch" ]; then
            # 규칙 4 — 동일 신원 다중 행은 최소값 대표 (순서 무관 = 재현 가능).
            prev="${peer_min[$mkey]:-}"
            if [ -z "$prev" ] || [ "$epoch" -lt "$prev" ]; then
                peer_min["$mkey"]="$epoch"
            fi
        fi
    done <<< "$records"

    # ── 산출 ① 범위 선언 (보장 / 미보장 대구) ────────────────────────────────────────
    log "[PEER CO-DISPATCH SCOPE] 관측 채널(로그 산출) — 산출은 로그뿐이다 (warning-tier · FAIL 미계상 · exit code 무변경 · merge 영향 0)"
    log "  보장: (lane 정확일치 ∧ agent 선두토큰 정확일치 ∧ 동일 iteration) 으로 묶인 그룹 안에서 '선언된' spawned_at 값들의 diff 가 ${SPAWN_TIMING_THRESHOLD_S}초 내인가."
    log "  미보장: 실제 spawn 동시성 · peer 가 실제로 산출을 냈는지(실효 판정은 원장 입력 진단 leg 소관) · §14 에 기록되지 않은 peer · 자기단언 값 자체의 진위."

    # ── 산출 ② 그룹별 co-dispatch 판정 (PEER-N (co-dispatch scope) = timing 판정의 유일 입력) ──
    local total_groups="${#group_keys[@]}"
    local g_lane g_iter peer_rows peer_ts_count id
    local -a peer_epochs=()
    if [ "$total_groups" -eq 0 ]; then
        log "[PEER CO-DISPATCH N/A] 판정 대상 그룹 0개 — (리뷰 4-lane 정확일치 ∧ iteration 보유) 조건을 만족하는 §14 row 부재. 판정 대상 부재이지 'peer 부재' 아님"
    else
        for key in "${group_keys[@]}"; do
            g_lane="${key%%$'\037'*}"
            g_iter="${key##*$'\037'}"
            peer_rows=0
            peer_ts_count=0
            peer_epochs=()
            # 신원 순회는 closed-set 선언 순서 고정 — 문서 출현 순서와 무관하게 재현된다.
            for id in "${PEER_AGENT_IDS[@]}"; do
                [ -n "${peer_seen[${key}$'\037'${id}]:-}" ] || continue
                peer_rows=$((peer_rows + 1))
                prev="${peer_min[${key}$'\037'${id}]:-}"
                if [ -n "$prev" ]; then
                    peer_ts_count=$((peer_ts_count + 1))
                    peer_epochs+=("$prev")
                fi
            done

            _evaluate_spawn_timing 2 "$peer_rows" "$peer_ts_count" peer_epochs
            case "$SPAWN_TIMING_STATE" in
                env_absent)
                    log "[PEER CO-DISPATCH N/A] ${g_lane} / iteration ${g_iter} — PEER-0 (co-dispatch scope) 판정 불가: 행-단위 peer 증거 부재 (선두토큰 정확일치 peer 신원 0종). ★ '행-단위 peer 증거 부재' 이지 'peer 부재' 가 아니다 — ①진짜 미스폰 과 ②띄웠으나 §14 에 기록하지 않음 은 이 채널로 원리적 구별 불가이며, PL 1행이 dual-peer 를 서술한 실물 형상도 여기로 낙하한다"
                    ;;
                evidence_absent)
                    log "[PEER CO-DISPATCH N/A] ${g_lane} / iteration ${g_iter} — PEER-${peer_rows} (co-dispatch scope) 판정 불가: 등식 가드 불성립 (peer 신원 ${peer_rows}종 중 유효 spawned_at ${peer_ts_count}종 — peer_ts_count != peer_rows). 시각 증거 결손이므로 timing 분기에 도달하지 않는다 (TZ-less · malformed · 미기입 포함)"
                    ;;
                below_expected)
                    log "[PEER CO-DISPATCH N/A] ${g_lane} / iteration ${g_iter} — PEER-${peer_rows} (co-dispatch scope) 판정 불가: distinct peer 신원 ${peer_rows}종 < ${SPAWN_TIMING_EXPECTED}종 이라 co-dispatch 비교 대상이 성립하지 않는다. ★ 판정 불가는 어떤 경로로도 통과 판정으로 접히지 않는다 — group-level '판정 불가' 자체가 1급 산출이다"
                    ;;
                measurable)
                    if [ "$SPAWN_TIMING_WITHIN" -eq 1 ]; then
                        log "[PEER CO-DISPATCH PASS] ${g_lane} / iteration ${g_iter} — PEER-${peer_rows} (co-dispatch scope) peer 신원 ${peer_rows}종 spawned_at diff = ${SPAWN_TIMING_DIFF}s < ${SPAWN_TIMING_THRESHOLD_S}s"
                        log "  (ceiling — 자기단언 채널: 이 판정이 말하는 것은 '선언된 spawned_at 값이 ${SPAWN_TIMING_THRESHOLD_S}초 내' 이지 '실제로 ${SPAWN_TIMING_THRESHOLD_S}초 내에 spawn 됐다' 가 아니다. §14 는 저작자 자기단언 채널이며 그 진위는 어떤 keying 규약으로도 교정되지 않는다 — 실측 반례: 8행 전건 동일 시각 자기단언이 diff = 0s 통과를 냈고, 그 8행 중 6행의 agent 값이 '— PL 단독 통합' 으로 미스폰을 자인했다)"
                    else
                        log_err "[PEER CO-DISPATCH WARN] ${g_lane} / iteration ${g_iter} — PEER-${peer_rows} (co-dispatch scope) peer 신원 ${peer_rows}종 spawned_at diff = ${SPAWN_TIMING_DIFF}s >= ${SPAWN_TIMING_THRESHOLD_S}s — 선언 시각 기준 co-dispatch 미달 (순차 개시 의심). 관측 채널 — FAIL 아님, enforcement 미구현"
                    fi
                    ;;
            esac
        done
    fi

    # ── 산출 ③ lane 누적 커버리지 (whether 물음 전용 — co-dispatch 판정 입력 아님) ──────────
    local cov_ids cov_n cov_printed=0
    for x in "${PEER_REVIEW_LANES[@]}"; do
        [ -n "${lane_group_count[$x]:-}" ] || continue
        cov_ids=""
        cov_n=0
        for id in "${PEER_AGENT_IDS[@]}"; do
            if [ -n "${lane_peer[${x}$'\037'${id}]:-}" ]; then
                cov_n=$((cov_n + 1))
                cov_ids="${cov_ids:+$cov_ids }${id}"
            fi
        done
        log "[PEER COVERAGE] ${x} — PEER coverage (lane 누적) = ${cov_n}종${cov_ids:+ (${cov_ids})} / 관측 그룹 ${lane_group_count[$x]}개"
        cov_printed=1
    done
    if [ "$cov_printed" -eq 1 ]; then
        log "  (PEER coverage (lane 누적) 은 whether(커버리지) 물음 전용이다 — lane 전체 iteration 의 합집합이라 '라운드 1 에 Claude, 라운드 3 에 Codex' 도 2종으로 세어진다. 따라서 이 수치는 co-dispatch(when) 판정에 입력되지 않으며 위 co-dispatch 판정 줄에도 등장하지 않는다)"
    fi

    # ── 산출 ④ lane 표기 비정합 · iteration 결측 카운터 ─────────────────────────────────
    log "[PEER LANE-LABEL] lane_label_nonconformant: ${nonconformant} (리뷰-유사 표기인데 closed-set 미매칭 → 판정 모집단 미진입) / iteration 결측 판정 비대상 row: ${missing_iteration}"
    log "  (분리 ≠ 해소: 표기 비정합을 진짜 PEER-0(미기록)과 다른 카운터로 분리했을 뿐 비정합 자체가 해소된 것은 아니다. canonical 정규화는 채택하지 않았다 — free-text → key 승격 표면을 하나 더 만들지 않기 위함이며, §14 lane 의 진짜 처방은 schema 층 enum 집행으로 본 Story scope 밖이다)"

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
        # Check 6b (CFP-2914 AC-2a): review-peer co-dispatch 관측 leg.
        #   설계 leg 와 나란히 호출하는 형제 함수다 — check_parallelization() 내부에 분기를 더하지
        #   않으므로 설계 leg 의 회귀 표면이 0 이다. 반환값은 설계 leg 와 동일하게 버려진다
        #   (전 경로 return 0, FAIL count 미증가 — warning tier).
        check_peer_codispatch "$story_yaml"
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
