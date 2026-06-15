#!/usr/bin/env bash
# bootstrap-consumer.sh — single-entry consumer setup (CFP-125 Phase 2).
#
# 신규 consumer project 에서 codeforge 첫 적용 시 단일 명령 setup. 8 단계 idempotent:
#   1. Pre-check (gh auth + git repo)
#   2. Plugin install reminder (stdout — 실 install 은 platform-level)
#   3. Overlay scaffold (.claude/_overlay/ + 4 file)
#   4. settings.json bootstrap (templates/settings.json.example → .claude/settings.json)
#   5. GitHub workflows + ISSUE_TEMPLATE + CODEOWNERS + PR template
#   6. Labels bootstrap (bootstrap-labels.sh delegate)
#   7. consumer-scripts.manifest copy (manifest-driven)
#   8. Summary + next step (check-debut-readiness.sh)
#
# Usage:
#   bash scripts/bootstrap-consumer.sh                    # default --resume
#   bash scripts/bootstrap-consumer.sh --org <org> --repo <repo>
#   bash scripts/bootstrap-consumer.sh --dry-run          # 실 수행 없이 stdout
#   bash scripts/bootstrap-consumer.sh --force            # marker 무시 모든 단계 재시도
#   bash scripts/bootstrap-consumer.sh --reset            # marker 삭제 + clean from scratch
#   bash scripts/bootstrap-consumer.sh --family-skip      # lane plugin 7-repo label bootstrap skip (fork)
#
# Exit code: 0 (모두 처리 또는 already-done) / 1 (fatal — gh 미인증, git repo 부재)
#
# State marker: .claude/_overlay/.bootstrap-state.json (consumer-internal, gitignored)

set -uo pipefail

# Defaults
DRY_RUN=0
FORCE=0
RESET=0
FAMILY_SKIP=0
ORG=""
REPO=""

usage() {
    sed -n '/^# bootstrap-consumer.sh/,/^# State marker/p' "$0" | sed 's/^# \?//'
    exit 0
}

# Args
while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        --force) FORCE=1; shift ;;
        --reset) RESET=1; shift ;;
        --family-skip) FAMILY_SKIP=1; shift ;;
        --org) ORG="$2"; shift 2 ;;
        --repo) REPO="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR=".claude/_overlay"
STATE_FILE="$STATE_DIR/.bootstrap-state.json"

log() { printf '[bootstrap-consumer] %s\n' "$1" >&2; }

# State marker helpers
mark_step() {
    local step="$1"
    [ $DRY_RUN -eq 1 ] && return 0
    mkdir -p "$STATE_DIR"
    local ts
    ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    if [ -f "$STATE_FILE" ]; then
        # append step (jq optional — fallback to text marker)
        if command -v jq >/dev/null 2>&1; then
            jq --arg s "$step" --arg t "$ts" \
                '.steps[$s] = $t' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
        else
            # naive append (sed-based, jq 없을 시 fallback)
            local tmp; tmp="$(mktemp)"
            python3 -c "import json,sys; d=json.load(open('$STATE_FILE')); d['steps']['$step']='$ts'; json.dump(d,open('$STATE_FILE','w'),indent=2)"
        fi
    else
        printf '{"version":"1","steps":{"%s":"%s"}}\n' "$step" "$ts" > "$STATE_FILE"
    fi
}

is_step_done() {
    local step="$1"
    [ $FORCE -eq 1 ] && return 1
    [ ! -f "$STATE_FILE" ] && return 1
    if command -v jq >/dev/null 2>&1; then
        local val
        val="$(jq -r --arg s "$step" '.steps[$s] // empty' "$STATE_FILE" 2>/dev/null || true)"
        [ -n "$val" ]
    else
        grep -q "\"$step\":" "$STATE_FILE" 2>/dev/null
    fi
}

# Reset
if [ $RESET -eq 1 ]; then
    if [ -f "$STATE_FILE" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            printf '경고: --reset 가 .bootstrap-state.json 삭제 + 모든 단계 from scratch 재시도. 계속 (y/N)? '
            read -r confirm
            if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
                log "사용자 취소"
                exit 0
            fi
            rm -f "$STATE_FILE"
            log "state file 삭제됨"
        else
            log "(dry-run) state file 삭제 skip"
        fi
    fi
fi

# org/repo 자동 감지 — project.yaml 우선, git remote fallback
detect_org_repo() {
    if [ -n "$ORG" ] && [ -n "$REPO" ]; then return 0; fi
    if [ -f ".claude/_overlay/project.yaml" ]; then
        local y_org y_repo
        y_org="$(grep -E '^\s*org:' .claude/_overlay/project.yaml | head -1 | awk '{print $2}' | tr -d \"\\\"\\'\\ )"
        y_repo="$(grep -E '^\s*repo:' .claude/_overlay/project.yaml | head -1 | awk '{print $2}' | tr -d \"\\\"\\'\\ )"
        [ -z "$ORG" ] && ORG="$y_org"
        [ -z "$REPO" ] && REPO="$y_repo"
    fi
    if [ -z "$ORG" ] || [ -z "$REPO" ]; then
        # git remote fallback
        local url
        url="$(git remote get-url origin 2>/dev/null || true)"
        if [ -n "$url" ]; then
            local pair
            pair="$(printf '%s' "$url" | sed -E 's#.*github\.com[:/]([^/]+)/([^./]+)(\.git)?$#\1/\2#')"
            [ -z "$ORG" ] && ORG="$(printf '%s' "$pair" | cut -d/ -f1)"
            [ -z "$REPO" ] && REPO="$(printf '%s' "$pair" | cut -d/ -f2)"
        fi
    fi
}

run_or_dry() {
    if [ $DRY_RUN -eq 1 ]; then
        printf '[dry-run] %s\n' "$*" >&2
    else
        # CFP-2250 FIX (Codex P2): eval 제거 → argv 직접 실행 (공백 경로 안전, 재해석 0).
        # 모든 호출부 argv 형식 (run_or_dry cp "$a" "$b" 등) — redirection (2>/dev/null) 은
        # 호출부에서 outer shell 이 소비 (argv 비포함) → 동작 동등.
        "$@"
    fi
}

# Stage 1 — Pre-check
stage_1_precheck() {
    log "Stage 1: pre-check (gh + git)"
    if ! command -v gh >/dev/null 2>&1; then
        log "ERROR: gh CLI 미설치 — https://cli.github.com 에서 설치 후 'gh auth login' 실행"
        return 1
    fi
    if [ $DRY_RUN -eq 0 ] && ! gh auth status >/dev/null 2>&1; then
        log "ERROR: gh auth status 실패 — 'gh auth login' 실행"
        return 1
    fi
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log "ERROR: 현재 디렉터리가 git repo 아님"
        return 1
    fi
    detect_org_repo
    if [ -z "$ORG" ] || [ -z "$REPO" ]; then
        log "ERROR: org/repo 감지 실패 — --org <org> --repo <repo> 명시"
        return 1
    fi
    log "  org=$ORG repo=$REPO"
    # CFP-2250 결함3 preflight: manifest / project.yaml 결손 사전 안내 (story-init 발동 전 진단).
    # project.yaml 부재 = Stage 3 에서 자동 scaffold. manifest 부재 = Stage 7 skip. story-init 은 별 lane(S4).
    if [ ! -f ".claude/_overlay/project.yaml" ]; then
        log "  preflight: project.yaml 부재 — Stage 3 에서 example 로 자동 scaffold (이후 org/repo 직접 치환 의무)"
    fi
    if [ ! -f "$PLUGIN_ROOT/templates/consumer-scripts.manifest" ]; then
        log "  preflight: consumer-scripts.manifest 부재 — Stage 7 skip (wrapper plugin 설치 확인 권장)"
    fi
    mark_step "stage_1_precheck"
}

# Stage 2 — Plugin install reminder
stage_2_plugin_reminder() {
    log "Stage 2: plugin install reminder"
    local plugins_json="${HOME:-$USERPROFILE}/.claude/plugins/installed_plugins.json"
    # CFP-2250 / ADR-122 — superpowers 더 이상 codeforge 의존 아님 (check_bootstrap.py REQUIRED_PLUGINS 정합, 11→10).
    local required=(
        "codeforge@mclayer"
        "codeforge-requirements@mclayer"
        "codeforge-design@mclayer"
        "codeforge-develop@mclayer"
        "codeforge-test@mclayer"
        "codeforge-review@mclayer"
        "codeforge-pmo@mclayer"
        "github@claude-plugins-official"
        "codex@openai-codex"
        "claude-md-management@claude-plugins-official"
    )
    local missing=()
    if [ -f "$plugins_json" ] && command -v python3 >/dev/null 2>&1; then
        local installed
        installed="$(python3 -c "import json; print(' '.join(json.load(open('$plugins_json')).get('plugins',{}).keys()))")"
        for p in "${required[@]}"; do
            case " $installed " in
                *" $p "*) ;;
                *) missing+=("$p") ;;
            esac
        done
    else
        log "  (plugins JSON 부재 — Claude Code 미설치 또는 plugin 0개)"
        missing=("${required[@]}")
    fi
    if [ ${#missing[@]} -gt 0 ]; then
        log "  ${#missing[@]}/${#required[@]} plugin 미설치:"
        for p in "${missing[@]}"; do log "    /plugins install $p"; done
        log "  → Claude Code 에서 위 명령 직접 실행 의무 (platform-level)"
    else
        log "  ✓ ${#required[@]}/${#required[@]} plugin 설치 확인"
    fi
    mark_step "stage_2_plugin_reminder"
}

# Stage 3 — Overlay scaffold
stage_3_overlay_scaffold() {
    log "Stage 3: overlay scaffold"
    run_or_dry mkdir -p .claude/_overlay/agents
    local files=(
        "overlay/_overlay/README.md:.claude/_overlay/README.md"
        "overlay/_overlay/project.yaml.example:.claude/_overlay/project.yaml"
        "overlay/_overlay/run-tests.sh.example:.claude/_overlay/run-tests.sh"
        "overlay/_overlay/run-perf.sh.example:.claude/_overlay/run-perf.sh"
    )
    for entry in "${files[@]}"; do
        local src="${entry%%:*}"
        local dst="${entry##*:}"
        if [ ! -f "$dst" ]; then
            run_or_dry cp "$PLUGIN_ROOT/$src" "$dst"
            log "  cp $dst"
        else
            log "  skip $dst (already exists)"
        fi
    done
    if [ $DRY_RUN -eq 0 ]; then
        chmod +x .claude/_overlay/run-tests.sh .claude/_overlay/run-perf.sh 2>/dev/null || true
    fi
    mark_step "stage_3_overlay_scaffold"
}

# Stage 4 — settings.json bootstrap
stage_4_settings_json() {
    log "Stage 4: settings.json bootstrap"
    local target=".claude/settings.json"
    local source="$PLUGIN_ROOT/templates/settings.json.example"
    if [ -f "$target" ]; then
        local ts; ts="$(date -u +%Y%m%dT%H%M%SZ)"
        local backup="${target}.bak.${ts}"
        log "  WARN: $target 이미 존재 — 백업 후 skip ($backup)"
        if [ $DRY_RUN -eq 0 ]; then
            cp "$target" "$backup"
        fi
    else
        run_or_dry cp "$source" "$target"
        log "  cp $target"
    fi
    mark_step "stage_4_settings_json"
}

# Stage 5 — GitHub workflows + forms + CODEOWNERS + PR template
stage_5_github_setup() {
    log "Stage 5: GitHub workflows / forms / CODEOWNERS / PR template"
    run_or_dry mkdir -p .github/workflows .github/ISSUE_TEMPLATE
    # Workflows (7종 consumer-distributable)
    local workflows=(
        "phase-gate-mergeable.yml"
        "phase-label-invariant.yml"
        "story-init.yml"
        "story-section-1-immutable.yml"
        "subissue-from-impl-manifest.yml"
        "fix-ledger-sync.yml"
        "story-section-schema.yml"
    )
    for w in "${workflows[@]}"; do
        local dst=".github/workflows/$w"
        if [ ! -f "$dst" ]; then
            run_or_dry cp "$PLUGIN_ROOT/templates/github-workflows/$w" "$dst"
            log "  cp $dst"
        fi
    done
    # Forms (3종)
    local forms=("audit.yml" "bug.yml" "story.yml")
    for f in "${forms[@]}"; do
        local dst=".github/ISSUE_TEMPLATE/$f"
        if [ ! -f "$dst" ]; then
            run_or_dry cp "$PLUGIN_ROOT/templates/github-issue-forms/$f" "$dst"
            log "  cp $dst"
        fi
    done
    # config.yml (blank issue 비활성)
    if [ ! -f ".github/ISSUE_TEMPLATE/config.yml" ]; then
        if [ $DRY_RUN -eq 0 ]; then
            printf 'blank_issues_enabled: false\n' > .github/ISSUE_TEMPLATE/config.yml
        fi
        log "  cp .github/ISSUE_TEMPLATE/config.yml"
    fi
    # CODEOWNERS
    if [ ! -f ".github/CODEOWNERS" ]; then
        run_or_dry cp "$PLUGIN_ROOT/templates/CODEOWNERS.template" .github/CODEOWNERS
        log "  cp .github/CODEOWNERS (placeholder team — 직접 치환 의무)"
    fi
    # PR template
    if [ ! -f ".github/PULL_REQUEST_TEMPLATE.md" ]; then
        run_or_dry cp "$PLUGIN_ROOT/templates/github-pr-template.md" .github/PULL_REQUEST_TEMPLATE.md
        log "  cp .github/PULL_REQUEST_TEMPLATE.md"
    fi
    mark_step "stage_5_github_setup"
}

# Stage 6 — Labels bootstrap (delegate)
stage_6_labels() {
    log "Stage 6: labels bootstrap (delegate to bootstrap-labels.sh)"
    if [ $DRY_RUN -eq 1 ]; then
        log "  (dry-run) bash $PLUGIN_ROOT/scripts/bootstrap-labels.sh $ORG/$REPO"
    else
        # CFP-2250 FIX (Codex P1): silent skip 제거 — bash 종료코드 전파 (이전 `|| true` 가 실패를 삼킴).
        # ${PIPESTATUS[0]} = pipe 첫 명령(bash)의 exit code (sed 의 0 이 아닌 bash 자체 결과).
        bash "$PLUGIN_ROOT/scripts/bootstrap-labels.sh" "$ORG/$REPO" 2>&1 | sed 's/^/  /' >&2
        local labels_rc=${PIPESTATUS[0]}
        if [ "$labels_rc" -ne 0 ]; then
            log "  ERROR: label 시드 실패 (bootstrap-labels.sh exit $labels_rc)"
            return 1
        fi
    fi
    mark_step "stage_6_labels"
}

# Stage 7 — consumer-scripts.manifest copy
stage_7_consumer_scripts() {
    log "Stage 7: consumer-scripts.manifest copy"
    local manifest="$PLUGIN_ROOT/templates/consumer-scripts.manifest"
    if [ ! -f "$manifest" ]; then
        log "  WARN: manifest 부재 — skip"
        mark_step "stage_7_consumer_scripts"
        return 0
    fi
    while IFS= read -r line; do
        # trim
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"
        case "$line" in '#'*|'') continue ;; esac
        local script_path="${line%%:*}"
        case "$script_path" in
            /*|*..*|-*) log "  reject: $line"; continue ;;
        esac
        local target="$script_path"
        if [ ! -f "$target" ]; then
            run_or_dry mkdir -p "$(dirname "$target")"
            run_or_dry cp "$PLUGIN_ROOT/$script_path" "$target"
            run_or_dry chmod +x "$target" 2>/dev/null
            log "  cp $target"
        fi
    done < "$manifest"
    mark_step "stage_7_consumer_scripts"
}

# Stage 8 — Summary
stage_8_summary() {
    log ""
    log "=== bootstrap-consumer 완료 ==="
    log "  org=$ORG repo=$REPO"
    log ""
    log "Next step: bash $PLUGIN_ROOT/scripts/check-debut-readiness.sh"
    log ""
    if [ -f "$STATE_FILE" ]; then
        log "State marker: $STATE_FILE"
    fi
}

# Main
main() {
    local stages=(
        "stage_1_precheck"
        "stage_2_plugin_reminder"
        "stage_3_overlay_scaffold"
        "stage_4_settings_json"
        "stage_5_github_setup"
        "stage_6_labels"
        "stage_7_consumer_scripts"
    )
    if [ $FAMILY_SKIP -eq 1 ]; then
        log "(--family-skip set — Stage 6 labels skip)"
    fi
    local rc=0
    for stage in "${stages[@]}"; do
        if is_step_done "$stage"; then
            log "$stage: SKIP (marker exists, --force 로 재시도 가능)"
            continue
        fi
        if [ "$stage" = "stage_6_labels" ] && [ $FAMILY_SKIP -eq 1 ]; then
            log "$stage: SKIP (--family-skip)"
            continue
        fi
        if ! "$stage"; then
            log "ERROR: $stage failed"
            rc=1
            break
        fi
    done
    stage_8_summary
    return $rc
}

main "$@"
