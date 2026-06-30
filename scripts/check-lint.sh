#!/usr/bin/env bash
# check-lint.sh — Consumer-side lint runner (CFP-132 / Issue #236).
#
# 매 phase production push 전 ruff + pyright 등 표준 lint 실행. CI ruff/pyright fail
# → fix → push iter 4-round 평균 ($ 비용 폭증) friction 회피.
#
# Usage:
#   bash scripts/check-lint.sh                    # 전체 lint (auto-detect tools)
#   bash scripts/check-lint.sh --fix              # ruff/eslint/stylelint auto-fix 적용
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
#   - package.json + stylelint: stylelint "**/*.css" "**/*.scss" (+ --fix if requested)  # CFP-2505 / ADR-136 D1 보조 채널
#   - 기타 (no detect): exit 0 (skip)
#
# 호출 위치:
#   - Manual: PR open 전 사용자가 직접 실행
#   - Pre-push hook: overlay/hooks/pre-push.sh.example 가 본 script 호출 (CFP-132)
#
# 외부 계약 (호출자 영향 0 — CFP-2505 / ADR-136 결정6 명시):
#   - exit code: 0=PASS/skip, 1=FAIL (불변)
#   - --fix / --quiet 플래그 동작 (불변)
#   - 언어 분기는 run_python_lint / run_node_lint / run_css_lint 3 함수로 추출 (rule-of-three).
#     함수가 전역 RAN_ANY / EXIT_CODE 를 갱신한다 (기존 인라인 패턴 유지). 호출 순서 = python → node → css.

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

# 언어 분기 = run_python_lint / run_node_lint / run_css_lint 3 함수 (rule-of-three — CFP-2505 / ADR-136 결정6).
# 각 함수는 전역 RAN_ANY / EXIT_CODE 를 갱신한다 (기존 인라인 패턴 유지). 외부 exit-code/--fix/--quiet 계약 불변.

# ----- Python (pyproject.toml) -----
run_python_lint() {
    [ -f "pyproject.toml" ] || return 0
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
}

# ----- Node (package.json) -----
run_node_lint() {
    [ -f "package.json" ] || return 0
    command -v npx >/dev/null 2>&1 || return 0
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
}

# ----- CSS (package.json + stylelint) — CFP-2505 / ADR-136 D1 보조 채널 -----
# detect = package.json 에 "stylelint" grep (eslint detect 동형). config 부재/CSS 0개 시
# stylelint 자체가 graceful (matching 0 → exit 0). stylelint 미설치 시 npx 미해결 → skip.
run_css_lint() {
    [ -f "package.json" ] || return 0
    command -v npx >/dev/null 2>&1 || return 0
    if grep -q '"stylelint"' package.json 2>/dev/null; then
        RAN_ANY=1
        log "[lint] stylelint $([ $FIX -eq 1 ] && echo "--fix") \"**/*.css\" \"**/*.scss\""
        if [ $QUIET -eq 1 ]; then
            if [ $FIX -eq 1 ]; then
                npx stylelint --fix --quiet "**/*.css" "**/*.scss" || EXIT_CODE=1
            else
                npx stylelint --quiet "**/*.css" "**/*.scss" || EXIT_CODE=1
            fi
        else
            if [ $FIX -eq 1 ]; then
                npx stylelint --fix "**/*.css" "**/*.scss" || EXIT_CODE=1
            else
                npx stylelint "**/*.css" "**/*.scss" || EXIT_CODE=1
            fi
        fi
    fi
}

# 호출 순서 = python → node → css (ADR-136 결정6).
run_python_lint
run_node_lint
run_css_lint

if [ $RAN_ANY -eq 0 ]; then
    log "[lint] no detected lint tool (pyproject.toml + ruff/pyright OR package.json + eslint/tsc/stylelint 부재) — skip"
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
