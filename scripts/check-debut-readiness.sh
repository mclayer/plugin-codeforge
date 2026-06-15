#!/usr/bin/env bash
# check-debut-readiness.sh — single-entry consumer setup verify (CFP-125 Phase 2).
#
# 4 verification orchestration (thin wrapper):
#   1. check_bootstrap.py (8 check, ADR-027 §결정 1 SSOT)
#   2. Plugin 10종 presence (installed_plugins.json parse)
#   3. project.yaml schema validation (validate_config.py delegate)
#   4. settings.json hook 정합 (3 hook 등록 grep)
#
# Usage:
#   bash scripts/check-debut-readiness.sh                    # default (advisory, exit 0)
#   bash scripts/check-debut-readiness.sh --quiet            # PASS 시 stdout 억제
#   bash scripts/check-debut-readiness.sh --strict           # CFP-127 ADR-032 strict mode (현 release: stderr 경고 + default)
#
# Exit code:
#   Default mode: 0 (모두 PASS) / 0 (FAIL — stderr advisory 만, ADR-027 §결정 2 LLM-trust 정합)
#   Strict mode (CFP-127 후 활성): 0 (모두 PASS) / 1 (1 이상 FAIL)
#
# 본 release 시점 strict mode 미 land — --strict CLI flag 인식하나 default 동작 + stderr 경고.

set -uo pipefail

# Defaults
QUIET=0
STRICT_REQUESTED=0

# Args
while [ $# -gt 0 ]; do
    case "$1" in
        --quiet) QUIET=1; shift ;;
        --strict) STRICT_REQUESTED=1; shift ;;
        -h|--help)
            sed -n '/^# check-debut-readiness/,/^# 본 release/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ $STRICT_REQUESTED -eq 1 ]; then
    printf '[check-debut-readiness] WARN: --strict mode 는 CFP-127 (ADR-032) 후 활성. 현재 release 는 default mode (exit 0 advisory) 만 작동.\n' >&2
fi

log() { [ $QUIET -eq 0 ] && printf '%s\n' "$1"; }
log_err() { printf '%s\n' "$1" >&2; }

PASS_COUNT=0
FAIL_COUNT=0
declare -a FAIL_DETAILS=()

# Check 1 — check_bootstrap.py
check_1_bootstrap() {
    log "Check 1/4: check_bootstrap.py (8 sub-check)"
    if [ ! -f "$PLUGIN_ROOT/overlay/hooks/check_bootstrap.py" ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 1: check_bootstrap.py 부재 (plugin 미설치 또는 PLUGIN_ROOT 잘못됨)")
        return
    fi
    local out
    if ! out="$(python3 "$PLUGIN_ROOT/overlay/hooks/check_bootstrap.py" 2>&1)"; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 1: check_bootstrap.py exit non-zero")
        return
    fi
    if [ -n "$out" ]; then
        # warnings emitted but exit 0 (non-blocking)
        log "  (advisory output:)"
        printf '%s\n' "$out" | sed 's/^/    /' >&2
    fi
    PASS_COUNT=$((PASS_COUNT + 1))
}

# Check 2 — plugin presence
check_2_plugins() {
    log "Check 2/4: plugin 10종 presence"
    local plugins_json="${HOME:-$USERPROFILE}/.claude/plugins/installed_plugins.json"
    # CFP-2250 / ADR-122 — superpowers 제거 (check_bootstrap.py REQUIRED_PLUGINS 정합, 11→10).
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
    if [ ! -f "$plugins_json" ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 2: $plugins_json 부재 (Claude Code 미설치 또는 plugin 0개)")
        return
    fi
    if ! command -v python3 >/dev/null 2>&1; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 2: python3 부재 (plugin parse 불가)")
        return
    fi
    local installed
    installed="$(python3 -c "import json; print(' '.join(json.load(open('$plugins_json')).get('plugins',{}).keys()))" 2>/dev/null || true)"
    local missing=()
    for p in "${required[@]}"; do
        case " $installed " in
            *" $p "*) ;;
            *) missing+=("$p") ;;
        esac
    done
    if [ ${#missing[@]} -gt 0 ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 2: ${#missing[@]}/${#required[@]} plugin 미설치 — ${missing[*]}")
    else
        PASS_COUNT=$((PASS_COUNT + 1))
        log "  ✓ ${#required[@]}/${#required[@]} plugin 설치 확인"
    fi
}

# Check 3 — project.yaml schema
check_3_project_yaml() {
    log "Check 3/4: project.yaml schema validation"
    local yaml=".claude/_overlay/project.yaml"
    if [ ! -f "$yaml" ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 3: $yaml 부재 — 'bash scripts/bootstrap-consumer.sh' 권장")
        return
    fi
    local validator="$PLUGIN_ROOT/overlay/hooks/validate_config.py"
    if [ ! -f "$validator" ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 3: $validator 부재")
        return
    fi
    if ! python3 "$validator" "$yaml" >/dev/null 2>&1; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 3: project.yaml schema 위반 — 'python3 $validator $yaml' 직접 실행하여 상세 확인")
    else
        PASS_COUNT=$((PASS_COUNT + 1))
        log "  ✓ project.yaml schema PASS"
    fi
}

# Check 4 — settings.json hook 정합 (3 hook)
check_4_settings_hooks() {
    log "Check 4/4: settings.json 3 hook 등록 정합"
    local settings=".claude/settings.json"
    if [ ! -f "$settings" ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 4: $settings 부재")
        return
    fi
    local missing_hooks=()
    grep -q "regen-agents" "$settings" 2>/dev/null || missing_hooks+=("SessionStart:regen-agents")
    grep -q "check-bootstrap" "$settings" 2>/dev/null || missing_hooks+=("SessionStart:check-bootstrap")
    grep -q "userprompt-reminder" "$settings" 2>/dev/null || missing_hooks+=("UserPromptSubmit:userprompt-reminder")
    if [ ${#missing_hooks[@]} -gt 0 ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAIL_DETAILS+=("Check 4: ${#missing_hooks[@]}/3 hook 미등록 — ${missing_hooks[*]} (templates/settings.json.example 정합 갱신 의무)")
    else
        PASS_COUNT=$((PASS_COUNT + 1))
        log "  ✓ 3/3 hook 등록 확인 (regen-agents + check-bootstrap + userprompt-reminder)"
    fi
}

# Main
log "=== check-debut-readiness 시작 ==="
check_1_bootstrap
check_2_plugins
check_3_project_yaml
check_4_settings_hooks

log ""
log "=== Summary: $PASS_COUNT/4 PASS, $FAIL_COUNT/4 FAIL ==="
if [ $FAIL_COUNT -gt 0 ]; then
    log_err ""
    log_err "FAIL 상세:"
    for d in "${FAIL_DETAILS[@]}"; do
        log_err "  - $d"
    done
    log_err ""
    log_err "Recovery: 'bash scripts/bootstrap-consumer.sh' 또는 consumer-guide §2.1+ manual 절차 참조"
fi

# Exit policy
# Default mode: exit 0 (advisory, ADR-027 §결정 2 LLM-trust 정합)
# Strict mode (CFP-127 후 활성): exit 1 if FAIL_COUNT > 0
# 현 release: STRICT_REQUESTED 1 이어도 stderr 경고 후 default 동작
exit 0
