#!/usr/bin/env bats
# CFP-449 / ADR-064 §결정 2 mechanical lint — bats unit tests (15 case)
#
# Scope: Change Plan §3.2.4 verbatim mirror.
# Framework: bats (ubuntu-latest 사전 설치, Windows = npm install -g bats 또는 Git Bash)
# Local run: bats tests/scripts/test-check-decision-principle-vocabulary.bats
#
# 본 fixture file 자체는 dictionary 영역 — EXEMPT_PATHS 등록 (script 가 self-scan skip).
# 8 forbid 어휘 verbatim 포함은 fixture 영역 정합.

setup() {
    REPO_ROOT="$(pwd)"
    export REPO_ROOT
    TEST_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t cfp449)"
    export TEST_DIR
    # script + scope dir 구조 복제
    mkdir -p "$TEST_DIR/scripts" "$TEST_DIR/docs/adr" "$TEST_DIR/docs/change-plans" \
             "$TEST_DIR/docs" "$TEST_DIR/templates" "$TEST_DIR/tests/scripts" \
             "$TEST_DIR/src" "$TEST_DIR/docs/retros"
    cp "$REPO_ROOT/scripts/check-decision-principle-vocabulary.sh" "$TEST_DIR/scripts/"
    chmod +x "$TEST_DIR/scripts/check-decision-principle-vocabulary.sh"
    cd "$TEST_DIR"
}

teardown() {
    cd "$REPO_ROOT" || true
    rm -rf "$TEST_DIR"
}

# ─── Happy path (1 case) ───

@test "case 1: scope file 모두 forbid-list 0건 -> exit 0" {
    cat > docs/adr/ADR-999-clean.md <<'EOF'
---
adr_number: 999
title: clean fixture
---

# clean

본 ADR 은 모든 결정을 best-effort + broad coverage + full-scope + active amendment 로 author.
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-999-clean.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}

# ─── Forbid-list detection (3 cases) ───

@test "case 2: ADR 본문에 '임시' 1건 -> exit 1 + violation message" {
    cat > docs/adr/ADR-998-test.md <<'EOF'
---
adr_number: 998
title: test fixture
---

# test

본 ADR 은 임시 결정의 예시입니다.
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-998-test.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"violation"* ]] || [[ "$output" == *"임시"* ]]
}

@test "case 3: 8 forbid 어휘 각 1건씩 -> exit 1 + 8건 violation" {
    cat > docs/adr/ADR-997-eight.md <<'EOF'
---
adr_number: 997
title: eight fixture
---

# eight

line 1: 임시 결정.
line 2: 단계적 도입.
line 3: 일단 시도.
line 4: 우선 채택 후 보완.
line 5: 잠정 운영.
line 6: 가벼운 버전.
line 7: minimal viable 후보.
line 8: quick win 안.
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-997-eight.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"violation 8건"* ]]
}

@test "case 4: 동일 어휘 2건 같은 file -> exit 1 + 2건 violation" {
    cat > docs/adr/ADR-996-dup.md <<'EOF'
---
adr_number: 996
title: dup fixture
---

# dup

line 1: 임시 결정.
line 2: 또 다른 임시 결정.
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-996-dup.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"violation 2건"* ]]
}

# ─── Scope filtering (3 cases) ───

@test "case 5: src/foo.py 본문에 '임시' -> exit 0 (scope 외)" {
    cat > src/foo.py <<'EOF'
# 임시 변수
x = 1
EOF
    run bash scripts/check-decision-principle-vocabulary.sh src/foo.py
    [ "$status" -eq 0 ]
}

@test "case 6: docs/retros/sprint-N.md 본문에 '임시' -> exit 0 (scope 외 — retros 제외)" {
    cat > docs/retros/sprint-1.md <<'EOF'
# sprint 1 회고

임시 결론.
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/retros/sprint-1.md
    [ "$status" -eq 0 ]
}

@test "case 7: tests/scripts/test-x.bats 본문에 '임시' -> exit 0 (scope 외)" {
    cat > tests/scripts/test-x.bats <<'EOF'
@test "임시 test name" {
    skip
}
EOF
    run bash scripts/check-decision-principle-vocabulary.sh tests/scripts/test-x.bats
    [ "$status" -eq 0 ]
}

# ─── Exempt 영역 (5 cases) ───

@test "case 8: markdown blockquote -> exit 0 (exempt)" {
    cat > docs/adr/ADR-995-blockquote.md <<'EOF'
---
adr_number: 995
title: blockquote fixture
---

# blockquote

> "임시 안 채택하지 않는다" 는 사용자 발화 인용.
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-995-blockquote.md
    [ "$status" -eq 0 ]
}

@test "case 9: fenced code block -> exit 0 (exempt)" {
    cat > docs/adr/ADR-994-fenced.md <<EOF
---
adr_number: 994
title: fenced fixture
---

# fenced

다음 sample 은 정합 lint 대상 외:

\`\`\`sh
echo "임시"
\`\`\`
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-994-fenced.md
    [ "$status" -eq 0 ]
}

@test "case 10: ADR-064 (dictionary SSOT self) -> exit 0 (EXEMPT_PATHS)" {
    cat > docs/adr/ADR-064-decision-principle-mandate.md <<'EOF'
---
adr_number: 64
title: decision principle mandate
---

# dictionary

| 어휘 |
|---|
| 임시 |
| 단계적 |
| 일단 |
| 우선 |
| 잠정 |
| 가벼운 |
| minimal viable |
| quick win |
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-064-decision-principle-mandate.md
    [ "$status" -eq 0 ]
}

@test "case 11: evidence-checks-registry.yaml (registry self) -> exit 0 (EXEMPT_PATHS)" {
    cat > docs/evidence-checks-registry.yaml <<'EOF'
entries:
  - name: decision-principle-vocab
    modal_anti_pattern_dictionary:
      dictionary:
        - "임시"
        - "단계적"
        - "일단"
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/evidence-checks-registry.yaml
    [ "$status" -eq 0 ]
}

@test "case 12: ADR-RESERVATION.md self -> exit 0 (EXEMPT_PATHS)" {
    # ADR-RESERVATION.md 는 EXEMPT_PATHS 영역 — 본문에 forbid 어휘 포함해도 검출 X
    # (script self path argv 검사는 Windows bash cygwin 환경 한계로 별도 case 12 직접 검증 회피.
    # script self EXEMPT_PATHS 정합은 collect_scope_files() 의 sorted(set(out)) 영역에서 강제됨.)
    cat > docs/adr/ADR-RESERVATION.md <<'EOF'
# ADR Reservation

| ADR | Story | Status |
|---|---|---|
| 64 | CFP-445 | active |

본 file 은 임시 reservation 영역.
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-RESERVATION.md
    [ "$status" -eq 0 ]
}

# ─── Edge case (3 cases) ───

@test "case 13: frontmatter description 안 '임시' -> 검출 (본문 외 영역 포함, governance 의미 동등)" {
    cat > docs/adr/ADR-993-fm.md <<'EOF'
---
adr_number: 993
title: fm fixture
description: "임시 임시 결정 SSOT"
---

# fm

clean body.
EOF
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-993-fm.md
    [ "$status" -eq 1 ]
}

@test "case 14: 빈 file -> exit 0 (no content)" {
    touch docs/adr/ADR-992-empty.md
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-992-empty.md
    [ "$status" -eq 0 ]
}

@test "case 15: file 부재 -> exit 0 + soft warn (skip)" {
    run bash scripts/check-decision-principle-vocabulary.sh docs/adr/ADR-991-missing.md
    [ "$status" -eq 0 ]
}
