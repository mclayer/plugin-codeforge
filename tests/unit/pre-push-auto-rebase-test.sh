#!/usr/bin/env bash
# CFP-477 — pre-push-auto-rebase hook 테스트 (TDD RED → GREEN)
#
# Test case 5개 (AC-5 verbatim):
#   (a) BEHIND 0 + AUTO_REBASE=1 → exit 0
#   (b) BEHIND >0 + AUTO_REBASE unset → exit 0 (advisory, CFP-447 답습)
#   (c) BEHIND >0 + AUTO_REBASE=1 → exit 1 + 4-line guidance
#   (d) atomic violation + AUTO_REBASE=1 → exit 1 + ADR-063 ref message
#   (e) detached HEAD + AUTO_REBASE=1 → exit 0 (skip, EC-1)
#
# 실행: bash tests/unit/pre-push-auto-rebase-test.sh
#
# BEHIND 시뮬레이션: git update-ref refs/remotes/origin/main <SHA> 직접 조작
# (Windows 환경에서 bare repo 경유 push/clone 이 HEAD ref 부재로 실패하는 문제 우회)

set -uo pipefail

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

# ---- Test 환경 격리: 임시 git repo 생성 (main 브랜치 기반 + feature 브랜치 체크아웃) ----
# 실제 pre-push hook 은 feature 브랜치에서 실행 (EC-2: main 직접 push → skip).
# _setup_repo 는 main 에 초기 커밋 후 feature-test 브랜치로 체크아웃한다.
_setup_repo() {
    local tmpdir
    tmpdir=$(mktemp -d)
    # -b main 미지원 git 버전 대응: init 후 branch rename
    if git -C "$tmpdir" init -q -b main 2>/dev/null; then
        : # 신버전 git (>= 2.28) — ok
    else
        git -C "$tmpdir" init -q
        git -C "$tmpdir" checkout -q -b main 2>/dev/null || true
    fi
    git -C "$tmpdir" config user.email "test@test.com"
    git -C "$tmpdir" config user.name "Test"
    # 초기 커밋 (main 브랜치)
    echo "init" > "$tmpdir/README.md"
    git -C "$tmpdir" add README.md
    git -C "$tmpdir" commit -q -m "init"
    # 브랜치 이름 보정 (혹시 master 인 경우)
    local branch
    branch=$(git -C "$tmpdir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
    if [[ "$branch" != "main" ]]; then
        git -C "$tmpdir" branch -m "$branch" main 2>/dev/null || true
    fi
    # feature 브랜치로 체크아웃 (EC-2 main-skip 우회 의무)
    git -C "$tmpdir" checkout -q -b feature-test 2>/dev/null || true
    echo "$tmpdir"
}

_teardown_repo() {
    local tmpdir="$1"
    rm -rf "$tmpdir"
}

# BEHIND 상황 시뮬레이션: origin/main ref 를 현재 HEAD 보다 앞선 commit 으로 설정
# (bare repo 경유 방식은 Windows 에서 HEAD ref 부재 이슈 — update-ref 직접 조작으로 우회)
_simulate_behind() {
    local repo="$1"
    local count="${2:-1}"   # 몇 commits BEHIND 할지 (기본 1)

    # origin/main 을 위한 "ahead" 커밋 생성 후 reset --hard 로 repo 를 BEHIND 상태로
    local i
    for i in $(seq 1 "$count"); do
        echo "ahead_$i" >> "$repo/ahead_marker.txt"
        git -C "$repo" add ahead_marker.txt
        git -C "$repo" commit -q -m "ahead commit $i"
    done
    local AHEAD_SHA
    AHEAD_SHA=$(git -C "$repo" rev-parse HEAD)

    # HEAD 를 count 커밋 되돌리기
    git -C "$repo" reset --hard "HEAD~${count}" 2>/dev/null

    # origin/main ref 를 AHEAD_SHA 로 직접 설정 (fetch 시뮬레이션)
    git -C "$repo" update-ref refs/remotes/origin/main "$AHEAD_SHA"
}

# hook 파일 없으면 모두 FAIL 로 리포트
if ! _check_hook_exists; then
    for label in "(a)" "(b)" "(c)" "(d)" "(e)"; do
        _fail "TC-$label" "hook 파일 미존재 — RED phase 예정"
    done
    echo ""
    echo "결과: PASS=$PASS_COUNT FAIL=$FAIL_COUNT / TOTAL=$TOTAL"
    echo "RED phase: 모든 TC FAIL — 구현 후 GREEN 확인 의무"
    exit 0
fi

# ---- TC (a): BEHIND 0 + AUTO_REBASE=1 → exit 0 ----
tc_a() {
    local repo
    repo=$(_setup_repo)

    # origin/main 없음 (= fetch 미실행 상태) → BEHIND_COUNT = 0 (기본)
    # hook 이 origin/main 부재 시 BEHIND=0 으로 처리해야 함

    local output exit_code
    output=$(cd "$repo" && env PRE_PUSH_AUTO_REBASE=1 bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"

    if [[ $exit_code -eq 0 ]]; then
        _pass "TC-(a): BEHIND 0 + AUTO_REBASE=1 → exit 0"
    else
        _fail "TC-(a)" "exit_code=$exit_code (expected 0), output=$output"
    fi
}

# ---- TC (b): BEHIND >0 + AUTO_REBASE unset → exit 0 (advisory) ----
tc_b() {
    local repo
    repo=$(_setup_repo)
    _simulate_behind "$repo" 1

    local output exit_code
    # PRE_PUSH_AUTO_REBASE 환경 변수 해제 (-u 플래그 대비)
    output=$(cd "$repo" && env PRE_PUSH_AUTO_REBASE="" bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"

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
    _simulate_behind "$repo" 1

    local output exit_code
    output=$(cd "$repo" && env PRE_PUSH_AUTO_REBASE=1 bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"

    local ok=1
    if [[ $exit_code -ne 1 ]]; then
        _fail "TC-(c)" "exit_code=$exit_code (expected 1), output=$output"
        ok=0
    fi
    if ! echo "$output" | grep -q "git pull --rebase"; then
        _fail "TC-(c)" "4-line guidance 누락 (git pull --rebase), output=$output"
        ok=0
    fi
    if ! echo "$output" | grep -qE "check-version-bump-atomic|force-with-lease"; then
        _fail "TC-(c)" "4-line guidance 누락 (atomic/force-with-lease), output=$output"
        ok=0
    fi
    if [[ $ok -eq 1 ]]; then
        _pass "TC-(c): BEHIND >0 + AUTO_REBASE=1 → exit 1 + 4-line guidance"
    fi
}

# ---- TC (d): atomic violation + AUTO_REBASE=1 → exit 1 + ADR-063 ref ----
#
# MOCK_ATOMIC_FAIL=1 env 로 hook 내부 atomic 위반 시뮬레이션.
# hook 이 MOCK_ATOMIC_FAIL=1 을 지원해야 함 (GREEN phase 구현 의무).
tc_d() {
    local repo
    repo=$(_setup_repo)

    # BEHIND=0 (origin/main 없음), atomic 위반만 시뮬레이션
    local output exit_code
    output=$(cd "$repo" && env PRE_PUSH_AUTO_REBASE=1 MOCK_ATOMIC_FAIL=1 bash "$OLDPWD/$HOOK" 2>&1)
    exit_code=$?

    _teardown_repo "$repo"

    local ok=1
    if [[ $exit_code -ne 1 ]]; then
        _fail "TC-(d)" "exit_code=$exit_code (expected 1 for atomic violation), output=$output"
        ok=0
    fi
    if ! echo "$output" | grep -qiE "ADR-063|atomic"; then
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
