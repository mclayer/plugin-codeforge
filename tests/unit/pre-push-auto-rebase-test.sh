#!/usr/bin/env bash
# CFP-477 — pre-push-auto-rebase hook 테스트 (TDD RED phase 선작성)
#
# Test case 5개 (AC-5 verbatim):
#   (a) BEHIND 0 + atomic OK → exit 0
#   (b) BEHIND >0 + AUTO_REBASE unset → exit 0 (advisory, CFP-447 답습)
#   (c) BEHIND >0 + AUTO_REBASE=1 → exit 1 + 4-line guidance
#   (d) atomic violation + AUTO_REBASE=1 → exit 1 + ADR-063 ref message
#   (e) detached HEAD + AUTO_REBASE=1 → exit 0 (skip, EC-1)
#
# 실행: bash tests/unit/pre-push-auto-rebase-test.sh
# 또는 bats 설치 시: bats tests/unit/pre-push-auto-rebase-test.sh

set -uo pipefail

# ---- bats 미설치 시 standalone fallback ----
if ! command -v bats &>/dev/null; then
    echo "INFO: bats 미설치 — standalone 모드로 실행" >&2
    BATS_MODE=0
else
    BATS_MODE=1
fi

HOOK="templates/.claude/hooks/pre-push-auto-rebase.sh.sample"
PASS_COUNT=0
FAIL_COUNT=0
TOTAL=5

# ---- 공통 헬퍼 ----

_pass() { echo "PASS: $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
_fail() { echo "FAIL: $1 — $2"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# hook 파일 존재 여부 사전 확인
_check_hook_exists() {
    if [[ ! -f "$HOOK" ]]; then
        echo "ERROR: hook 파일 미발견: $HOOK" >&2
        echo "  → GREEN phase 구현 전 RED phase: 모든 TC 는 SKIP/FAIL 예정" >&2
        return 1
    fi
    return 0
}

# ---- Test 환경 격리: 임시 git repo 생성 ----
_setup_repo() {
    local tmpdir
    tmpdir=$(mktemp -d)
    git -C "$tmpdir" init -q
    git -C "$tmpdir" config user.email "test@test.com"
    git -C "$tmpdir" config user.name "Test"
    # 초기 커밋
    echo "init" > "$tmpdir/README.md"
    git -C "$tmpdir" add README.md
    git -C "$tmpdir" commit -q -m "init"
    echo "$tmpdir"
}

_teardown_repo() {
    local tmpdir="$1"
    rm -rf "$tmpdir"
}

# ---- 원본 hook 을 복사해 테스트 repo 에서 실행 ----
_run_hook() {
    local repo="$1"
    shift
    # 환경 변수 통째로 받아 실행
    env "$@" bash "$OLDPWD/$HOOK" 2>&1
    return $?
}

# hook 파일 없으면 모두 FAIL 로 리포트
if ! _check_hook_exists; then
    for i in a b c d e; do
        _fail "TC-($i)" "hook 파일 미존재 — RED phase 예정"
    done
    echo ""
    echo "결과: PASS=$PASS_COUNT FAIL=$FAIL_COUNT / TOTAL=$TOTAL"
    echo "RED phase: 모든 TC FAIL — 구현 후 GREEN 확인 의무"
    exit 0
fi

# ---- TC (a): BEHIND 0 + atomic OK → exit 0 ----
tc_a() {
    local repo
    repo=$(_setup_repo)

    # origin 흉내: 동일 커밋 → BEHIND=0
    local origin
    origin=$(mktemp -d)
    git -C "$origin" init -q --bare
    git -C "$repo" remote add origin "$origin"
    git -C "$repo" push -q origin HEAD:main 2>/dev/null || true
    git -C "$repo" fetch origin -q 2>/dev/null || true

    # check-version-bump-atomic.sh 가 없으면 skip (exit 0 기대 유지)
    # hook 을 repo 디렉터리에서 실행 (CWD = repo)
    local output exit_code
    output=$(cd "$repo" && env PRE_PUSH_AUTO_REBASE=1 bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"
    rm -rf "$origin"

    if [[ $exit_code -eq 0 ]]; then
        _pass "TC-(a): BEHIND 0 + AUTO_REBASE=1 → exit 0"
    else
        _fail "TC-(a)" "exit_code=$exit_code, output=$output"
    fi
}

# ---- TC (b): BEHIND >0 + AUTO_REBASE unset → exit 0 (advisory) ----
tc_b() {
    local repo
    repo=$(_setup_repo)

    # origin 에 추가 커밋 (BEHIND 발생)
    local origin
    origin=$(mktemp -d)
    git -C "$origin" init -q --bare
    git -C "$repo" remote add origin "$origin"
    git -C "$repo" push -q origin HEAD:main 2>/dev/null || true

    # origin 에 새 커밋 추가 (repo 는 BEHIND)
    local tmp_clone
    tmp_clone=$(mktemp -d)
    git clone -q "$origin" "$tmp_clone" 2>/dev/null
    echo "extra" >> "$tmp_clone/README.md"
    git -C "$tmp_clone" add README.md
    git -C "$tmp_clone" commit -q -m "extra commit"
    git -C "$tmp_clone" push -q origin main 2>/dev/null || true
    git -C "$repo" fetch origin -q 2>/dev/null || true

    local output exit_code
    output=$(cd "$repo" && env -u PRE_PUSH_AUTO_REBASE bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"
    _teardown_repo "$tmp_clone"
    rm -rf "$origin"

    if [[ $exit_code -eq 0 ]]; then
        _pass "TC-(b): BEHIND >0 + AUTO_REBASE unset → exit 0 (advisory)"
    else
        _fail "TC-(b)" "exit_code=$exit_code (expected 0), output=$output"
    fi
}

# ---- TC (c): BEHIND >0 + AUTO_REBASE=1 → exit 1 + 4-line guidance ----
tc_c() {
    local repo
    repo=$(_setup_repo)

    local origin
    origin=$(mktemp -d)
    git -C "$origin" init -q --bare
    git -C "$repo" remote add origin "$origin"
    git -C "$repo" push -q origin HEAD:main 2>/dev/null || true

    local tmp_clone
    tmp_clone=$(mktemp -d)
    git clone -q "$origin" "$tmp_clone" 2>/dev/null
    echo "extra" >> "$tmp_clone/README.md"
    git -C "$tmp_clone" add README.md
    git -C "$tmp_clone" commit -q -m "extra commit"
    git -C "$tmp_clone" push -q origin main 2>/dev/null || true
    git -C "$repo" fetch origin -q 2>/dev/null || true

    local output exit_code
    output=$(cd "$repo" && env PRE_PUSH_AUTO_REBASE=1 bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"
    _teardown_repo "$tmp_clone"
    rm -rf "$origin"

    # exit 1 + 4-line guidance 포함 확인
    local ok=1
    if [[ $exit_code -ne 1 ]]; then
        _fail "TC-(c)" "exit_code=$exit_code (expected 1), output=$output"
        ok=0
    fi
    if ! echo "$output" | grep -q "git pull --rebase"; then
        _fail "TC-(c)" "4-line guidance 누락 (git pull --rebase), output=$output"
        ok=0
    fi
    if ! echo "$output" | grep -q "check-version-bump-atomic\|force-with-lease"; then
        _fail "TC-(c)" "4-line guidance 누락 (atomic/force-with-lease), output=$output"
        ok=0
    fi
    if [[ $ok -eq 1 ]]; then
        _pass "TC-(c): BEHIND >0 + AUTO_REBASE=1 → exit 1 + 4-line guidance"
    fi
}

# ---- TC (d): atomic violation + AUTO_REBASE=1 → exit 1 + ADR-063 ref ----
tc_d() {
    local repo
    repo=$(_setup_repo)

    # BEHIND=0 (same commit origin)
    local origin
    origin=$(mktemp -d)
    git -C "$origin" init -q --bare
    git -C "$repo" remote add origin "$origin"
    git -C "$repo" push -q origin HEAD:main 2>/dev/null || true
    git -C "$repo" fetch origin -q 2>/dev/null || true

    # plugin.json 과 CHANGELOG.md 모두 변경 (mirrored field bump)
    # check-version-bump-atomic.sh 가 없으면 hook 이 스킵 → 이 TC 는 mock 방식 필요
    # mock: MOCK_ATOMIC_FAIL=1 env 로 hook 내부에서 분기 (hook 이 지원해야 함)
    local output exit_code
    output=$(cd "$repo" && env PRE_PUSH_AUTO_REBASE=1 MOCK_ATOMIC_FAIL=1 bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"
    rm -rf "$origin"

    local ok=1
    if [[ $exit_code -ne 1 ]]; then
        _fail "TC-(d)" "exit_code=$exit_code (expected 1 for atomic violation), output=$output"
        ok=0
    fi
    if ! echo "$output" | grep -qi "ADR-063\|atomic"; then
        _fail "TC-(d)" "ADR-063 ref 메시지 누락, output=$output"
        ok=0
    fi
    if [[ $ok -eq 1 ]]; then
        _pass "TC-(d): atomic violation + AUTO_REBASE=1 → exit 1 + ADR-063 ref"
    fi
}

# ---- TC (e): detached HEAD + AUTO_REBASE=1 → exit 0 (skip, EC-1) ----
tc_e() {
    local repo
    repo=$(_setup_repo)

    # detached HEAD 상태로 전환
    local HEAD_SHA
    HEAD_SHA=$(git -C "$repo" rev-parse HEAD)
    git -C "$repo" checkout -q --detach "$HEAD_SHA" 2>/dev/null || true

    local output exit_code
    output=$(cd "$repo" && env PRE_PUSH_AUTO_REBASE=1 bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"

    if [[ $exit_code -eq 0 ]]; then
        _pass "TC-(e): detached HEAD + AUTO_REBASE=1 → exit 0 (skip)"
    else
        _fail "TC-(e)" "exit_code=$exit_code (expected 0 for detached HEAD), output=$output"
    fi
}

# ---- 실행 ----

echo "=== CFP-477 pre-push-auto-rebase hook 테스트 ==="
echo ""

# 각 TC 는 독립 격리 실행
tc_a
tc_b
tc_c
tc_d
tc_e

echo ""
echo "=== 결과: PASS=$PASS_COUNT FAIL=$FAIL_COUNT / TOTAL=$TOTAL ==="

if [[ $FAIL_COUNT -eq 0 ]]; then
    echo "GREEN phase: 모든 TC PASS"
    exit 0
else
    echo "FAIL 있음: 구현 확인 필요"
    exit 1
fi
