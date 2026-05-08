#!/usr/bin/env bash
# check-lint.sh — Consumer-side lint runner (CFP-132 / Issue #236).
#
# 매 phase production push 전 ruff + pyright 등 표준 lint 실행. CI ruff/pyright fail
# → fix → push iter 4-round 평균 ($ 비용 폭증) friction 회피.
#
# Usage:
#   bash scripts/check-lint.sh                    # 전체 lint (auto-detect tools)
#   bash scripts/check-lint.sh --fix              # ruff auto-fix 적용
#   bash scripts/check-lint.sh --quiet            # 출력 최소화
#
# Exit code:
#   0: 모든 lint PASS (또는 lint tool 부재로 skip)
#   1: lint FAIL (consumer 가 fix 후 재실행 의무)
#
# Auto-detect:
#   - pyproject.toml + ruff: ruff check (+ --fix if requested) + ruff format --check
#   - pyproject.toml + pyright: pyright (또는 uv run pyright)
#   - package.json + eslint: eslint .
#   - package.json + tsc: tsc --noEmit
#   - 기타 (no detect): exit 0 (skip)
#
# 호출 위치:
#   - Manual: PR open 전 사용자가 직접 실행
#   - Pre-push hook: overlay/hooks/pre-push.sh.example 가 본 script 호출 (CFP-132)

set -u

FIX=0
QUIET=0
for arg in "$@"; do
    case "$arg" in
        --fix) FIX=1 ;;
        --quiet) QUIET=1 ;;
    esac
done

log() {
    [ $QUIET -eq 1 ] && return 0
    echo "$@"
}

err() {
    echo "$@" >&2
}

EXIT_CODE=0
RAN_ANY=0

# ----- Python (pyproject.toml) -----
if [ -f "pyproject.toml" ]; then
    # ruff
    if command -v ruff >/dev/null 2>&1 || command -v uv >/dev/null 2>&1; then
        RAN_ANY=1
        RUFF_CMD="ruff"
        command -v ruff >/dev/null 2>&1 || RUFF_CMD="uv run ruff"
        log "[lint] ruff check $([ $FIX -eq 1 ] && echo "--fix")"
        if [ $FIX -eq 1 ]; then
            $RUFF_CMD check --fix . || EXIT_CODE=1
        else
            $RUFF_CMD check . || EXIT_CODE=1
        fi
        log "[lint] ruff format --check"
        $RUFF_CMD format --check . || EXIT_CODE=1
    fi
    # pyright
    if command -v pyright >/dev/null 2>&1 || command -v uv >/dev/null 2>&1; then
        RAN_ANY=1
        PYRIGHT_CMD="pyright"
        command -v pyright >/dev/null 2>&1 || PYRIGHT_CMD="uv run pyright"
        log "[lint] pyright"
        $PYRIGHT_CMD || EXIT_CODE=1
    fi
fi

# ----- Node (package.json) -----
if [ -f "package.json" ]; then
    if command -v npx >/dev/null 2>&1; then
        if grep -q '"eslint"' package.json 2>/dev/null; then
            RAN_ANY=1
            log "[lint] eslint $([ $FIX -eq 1 ] && echo "--fix") ."
            if [ $FIX -eq 1 ]; then
                npx eslint --fix . || EXIT_CODE=1
            else
                npx eslint . || EXIT_CODE=1
            fi
        fi
        if grep -q '"typescript"' package.json 2>/dev/null; then
            RAN_ANY=1
            log "[lint] tsc --noEmit"
            npx tsc --noEmit || EXIT_CODE=1
        fi
    fi
fi

if [ $RAN_ANY -eq 0 ]; then
    log "[lint] no detected lint tool (pyproject.toml + ruff/pyright OR package.json + eslint/tsc 부재) — skip"
    exit 0
fi

if [ $EXIT_CODE -ne 0 ]; then
    err ""
    err "[lint] FAIL — fix issues then 'bash scripts/check-lint.sh' 재실행."
    err "[lint] Auto-fix 가능 항목: 'bash scripts/check-lint.sh --fix' 시도."
    exit 1
fi

log ""
log "✓ [lint] PASS — push ready."
exit 0
