#!/usr/bin/env bats
# CFP-841 / ADR-082 Amendment 1 §결정 6 scope(a) — corpus-claim-verify lint bats unit tests
#
# Scope: Change Plan §3.1 Test Contract verbatim mirror.
# Framework: bats-core (ubuntu-latest 사전 설치, Windows = npm install -g bats 또는 Git Bash)
# Local run: bats tests/scripts/test-check-corpus-claim-verify.bats
#
# 본 fixture file 자체는 self-referential exemption allowlist (scripts 가 self-scan skip).
# corpus enumeration token 포함은 fixture 영역 정합.

setup() {
    REPO_ROOT="$(pwd)"
    export REPO_ROOT
    TEST_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t cfp841)"
    export TEST_DIR
    mkdir -p "$TEST_DIR/scripts/lib" \
             "$TEST_DIR/docs/adr" \
             "$TEST_DIR/docs/change-plans" \
             "$TEST_DIR/docs/stories" \
             "$TEST_DIR/templates" \
             "$TEST_DIR/src"
    cp "$REPO_ROOT/scripts/check-corpus-claim-verify.sh" "$TEST_DIR/scripts/"
    cp "$REPO_ROOT/scripts/check-corpus-claim-verify.py" "$TEST_DIR/scripts/"
    chmod +x "$TEST_DIR/scripts/check-corpus-claim-verify.sh"
    cd "$TEST_DIR"
    # Effective date 고정 — forward-only guard 비활성화를 위해 과거 날짜 설정
    export CORPUS_VERIFY_EFFECTIVE_DATE="2020-01-01"
}

teardown() {
    cd "$REPO_ROOT" || true
    rm -rf "$TEST_DIR"
}

# ─── case 1: positive (annotation 부재 → fail) ───

@test "case 1: corpus enumeration token + file-path co-occurrence + annotation 부재 -> exit 1 violation" {
    cat > docs/adr/ADR-999-test.md <<'EOF'
---
adr_number: 999
title: test fixture
---

# test

전무 docs/adr/ADR-082-write-time-self-write-verification-mandate.md 의 corpus 0건 확인.
EOF
    run bash scripts/check-corpus-claim-verify.sh docs/adr/ADR-999-test.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"CORPUS_CLAIM_UNVERIFIED"* ]] || [[ "$output" == *"violation"* ]] || [[ "$output" == *"FAIL"* ]]
}

# ─── case 2: negative (annotation 보유 → pass) ───

@test "case 2: corpus enumeration token + file-path co-occurrence + annotation 보유 -> exit 0 PASS" {
    cat > docs/adr/ADR-998-clean.md <<'EOF'
---
adr_number: 998
title: clean fixture
---

# clean

전무 docs/adr/ADR-082-write-time-self-write-verification-mandate.md 의 corpus 0건 확인. [verified: git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md]
EOF
    run bash scripts/check-corpus-claim-verify.sh docs/adr/ADR-998-clean.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}

# ─── case 3: guard (1) file-path co-occurrence guard — corpus token 단독 → pass ───

@test "case 3 (guard-1): corpus token 단독 (file-path 동반 없음) -> exit 0 PASS (FP 완화)" {
    cat > docs/adr/ADR-997-guard1.md <<'EOF'
---
adr_number: 997
title: guard1 fixture
---

# guard1

해당 영역에서 관련 선례가 전무하다.
EOF
    run bash scripts/check-corpus-claim-verify.sh docs/adr/ADR-997-guard1.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}

# ─── case 4: guard (2) citation≠assertion 면제 — attribution 패턴 → pass ───

@test "case 4 (guard-2): attribution 패턴 (§N 가 ... 판정) -> exit 0 PASS (citation 면제)" {
    cat > docs/adr/ADR-996-guard2.md <<'EOF'
---
adr_number: 996
title: guard2 fixture
---

# guard2

ADR-082 §결정 4 가 docs/adr/ADR-068-boundary-completeness-invariants.md 의 prior art 재사용 판정.
EOF
    run bash scripts/check-corpus-claim-verify.sh docs/adr/ADR-996-guard2.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}

# ─── case 5: guard (4) self-referential exemption — ADR-082 본문 → pass ───

@test "case 5 (guard-4): self-referential exemption allowlist 파일 -> exit 0 PASS" {
    # allowlist: docs/adr/ADR-082-*.md 는 self-flag 면제
    mkdir -p "$TEST_DIR/docs/adr"
    cat > docs/adr/ADR-082-write-time-self-write-verification-mandate.md <<'EOF'
---
adr_number: 82
title: write-time self-write verification mandate
---

# ADR-082

예시 3건 docs/adr/ADR-082-write-time-self-write-verification-mandate.md corpus 인용 패턴.
EOF
    run bash scripts/check-corpus-claim-verify.sh \
        docs/adr/ADR-082-write-time-self-write-verification-mandate.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]] || [[ "$output" == *"exempt"* ]] || [[ "$output" == *"SKIP"* ]]
}

# ─── case 6: ±2줄 window — corpus token 2줄 위, file-path 현재줄 → flag ───

@test "case 6: corpus token 2-line 위 + file-path 현재줄 (window co-occurrence) + annotation 부재 -> exit 1" {
    cat > docs/adr/ADR-995-window.md <<'EOF'
---
adr_number: 995
title: window fixture
---

# window

현재 등록된 검사 항목이 다수 존재한다.

해당 파일은 docs/evidence-checks-registry.yaml 에 등록.
EOF
    run bash scripts/check-corpus-claim-verify.sh docs/adr/ADR-995-window.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"CORPUS_CLAIM_UNVERIFIED"* ]] || [[ "$output" == *"violation"* ]] || [[ "$output" == *"FAIL"* ]]
}

# ─── case 7: 파일 없음 → exit 0 (스캔 대상 없음) ───

@test "case 7: 스캔 대상 파일 없음 -> exit 0 PASS" {
    run bash scripts/check-corpus-claim-verify.sh
    [ "$status" -eq 0 ]
}

# ─── case 8: guard-3 forward-only — effective-date 이전 commit line → 면제 (exit 0) ───
# FIX iter1: F-CR-841-1 --line-porcelain 수정으로 guard-3 정상 동작 검증
# RED-first: pre-FIX (--porcelain, guard-3 inert) 시 flag→exit 1 (FAIL), post-FIX 시 exit 0 (GREEN)

@test "case 8 (guard-3 legacy-exempt): effective-date 이전 commit line -> exit 0 PASS (legacy 면제)" {
    # temp git repo 초기화
    git init -q "$TEST_DIR/gitrepo"
    cd "$TEST_DIR/gitrepo"
    git config user.email "test@test.com"
    git config user.name "Test"
    mkdir -p docs/adr

    # corpus-claim line 포함 파일 작성
    cat > docs/adr/ADR-legacy.md <<'EOF'
---
adr_number: 994
title: legacy fixture
---

# legacy

전무 docs/adr/ADR-082-write-time-self-write-verification-mandate.md 관련 corpus 0건.
EOF

    # effective-date(2026-05-17) 이전 날짜로 commit
    GIT_AUTHOR_DATE="2026-01-01T00:00:00+00:00" \
    GIT_COMMITTER_DATE="2026-01-01T00:00:00+00:00" \
    git add docs/adr/ADR-legacy.md
    GIT_AUTHOR_DATE="2026-01-01T00:00:00+00:00" \
    GIT_COMMITTER_DATE="2026-01-01T00:00:00+00:00" \
    git commit -q -m "legacy commit"

    cp "$REPO_ROOT/scripts/check-corpus-claim-verify.py" scripts/ 2>/dev/null || \
        cp "$REPO_ROOT/scripts/check-corpus-claim-verify.py" .

    # CORPUS_VERIFY_EFFECTIVE_DATE = 2026-05-17 (이전 commit = 면제 대상)
    CORPUS_VERIFY_EFFECTIVE_DATE="2026-05-17" \
        run python3 "$REPO_ROOT/scripts/check-corpus-claim-verify.py" docs/adr/ADR-legacy.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]] || [[ "$output" == *"0 violation"* ]]

    cd "$TEST_DIR"
}

# ─── case 9: guard-3 forward-only — effective-date 이후 commit + annotation 부재 → flag (exit 1) ───
# FIX iter1: F-CR-841-1 --line-porcelain 수정으로 guard-3 비면제 정상 동작 검증
# post-FIX: annotation 부재 new-commit line → exit 1 (정상 비면제)

@test "case 9 (guard-3 new-commit-flag): effective-date 이후 commit + annotation 부재 -> exit 1 FAIL" {
    # temp git repo 초기화
    git init -q "$TEST_DIR/gitrepo2"
    cd "$TEST_DIR/gitrepo2"
    git config user.email "test@test.com"
    git config user.name "Test"
    mkdir -p docs/adr

    # corpus-claim line 포함 파일 작성
    cat > docs/adr/ADR-new.md <<'EOF'
---
adr_number: 993
title: new fixture
---

# new

전무 docs/adr/ADR-082-write-time-self-write-verification-mandate.md 관련 corpus 0건.
EOF

    # effective-date(2026-05-17) 이후 날짜로 commit (annotation 부재)
    GIT_AUTHOR_DATE="2026-05-18T00:00:00+00:00" \
    GIT_COMMITTER_DATE="2026-05-18T00:00:00+00:00" \
    git add docs/adr/ADR-new.md
    GIT_AUTHOR_DATE="2026-05-18T00:00:00+00:00" \
    GIT_COMMITTER_DATE="2026-05-18T00:00:00+00:00" \
    git commit -q -m "new commit"

    # CORPUS_VERIFY_EFFECTIVE_DATE = 2026-05-17 (이후 commit = 비면제 → annotation 부재면 flag)
    CORPUS_VERIFY_EFFECTIVE_DATE="2026-05-17" \
        run python3 "$REPO_ROOT/scripts/check-corpus-claim-verify.py" docs/adr/ADR-new.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"FAIL"* ]] || [[ "$output" == *"violation"* ]] || [[ "$output" == *"CORPUS_CLAIM_UNVERIFIED"* ]]

    cd "$TEST_DIR"
}
