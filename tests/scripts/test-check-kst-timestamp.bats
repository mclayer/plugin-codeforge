#!/usr/bin/env bats
# CFP-771 / ADR-079 Amendment 1 mechanical lint — bats unit tests (15 case)
#
# Scope: Story §8 Test Contract verbatim mirror.
# Framework: bats-core (ubuntu-latest 사전 설치, Windows = npm install -g bats 또는 Git Bash)
# Local run: bats tests/scripts/test-check-kst-timestamp.bats
#
# 본 fixture file 자체는 EXEMPT_PATHS 등록 (script 가 self-scan skip).
# 테스트 fixture 안 비-KST timestamp 포함은 fixture 영역 정합.

setup() {
    REPO_ROOT="$(pwd)"
    export REPO_ROOT
    TEST_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t cfp771)"
    export TEST_DIR
    mkdir -p "$TEST_DIR/scripts/lib" \
             "$TEST_DIR/docs/adr" \
             "$TEST_DIR/docs/retros" \
             "$TEST_DIR/docs/inter-plugin-contracts" \
             "$TEST_DIR/docs/stories" \
             "$TEST_DIR/wrapper/retros" \
             "$TEST_DIR/src"
    cp "$REPO_ROOT/scripts/check-kst-timestamp.sh" "$TEST_DIR/scripts/"
    cp "$REPO_ROOT/scripts/lib/check_kst_timestamp.py" "$TEST_DIR/scripts/lib/"
    chmod +x "$TEST_DIR/scripts/check-kst-timestamp.sh"
    cd "$TEST_DIR"
}

teardown() {
    cd "$REPO_ROOT" || true
    rm -rf "$TEST_DIR"
}

# ─── Happy path (2 case) ───

@test "case 1: scope file 에 +09:00 timestamp -> exit 0 PASS" {
    cat > docs/adr/ADR-999-clean.md <<'EOF'
---
adr_number: 999
title: clean fixture
---

# clean

작업 시각: 2026-05-16T18:50:50+09:00
완료 시각: 2026-05-16T19:00:00+09:00
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-999-clean.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}

@test "case 2: timestamp 없는 scope file -> exit 0 PASS" {
    cat > docs/adr/ADR-998-no-ts.md <<'EOF'
---
adr_number: 998
title: no timestamp fixture
---

# 타임스탬프 없는 문서

본 문서에는 ISO 8601 형식 타임스탬프가 없습니다.
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-998-no-ts.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}

# ─── Violation detection (3 case) ───

@test "case 3: Z offset timestamp -> exit 1 WARN" {
    cat > docs/adr/ADR-997-utcz.md <<'EOF'
---
adr_number: 997
title: Z offset fixture
---

# Z offset

spawned at 2026-05-16T18:50:50Z and completed work.
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-997-utcz.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"violation"* ]] || [[ "$output" == *"WARN"* ]]
}

@test "case 4: +00:00 offset timestamp -> exit 1 WARN" {
    cat > docs/adr/ADR-996-utc-offset.md <<'EOF'
---
adr_number: 996
title: UTC offset fixture
---

# UTC offset

작업 시각: 2026-05-16T09:50:50+00:00 (KST 아님)
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-996-utc-offset.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"violation"* ]] || [[ "$output" == *"offset=+00:00"* ]]
}

@test "case 5: -05:00 offset timestamp -> exit 1 WARN" {
    cat > docs/adr/ADR-995-neg-offset.md <<'EOF'
---
adr_number: 995
title: negative offset fixture
---

# negative offset

timestamp: 2026-05-16T13:50:50-05:00 (EST, 위반)
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-995-neg-offset.md
    [ "$status" -eq 1 ]
}

# ─── Scope filtering (3 case) ───

@test "case 6: docs/inter-plugin-contracts/ 안 파일 -> exit 0 (EXEMPT_PREFIXES)" {
    cat > docs/inter-plugin-contracts/review-verdict-v5.md <<'EOF'
---
version: v5
---

created_at: 2026-05-16T09:00:00Z
EOF
    run bash scripts/check-kst-timestamp.sh docs/inter-plugin-contracts/review-verdict-v5.md
    [ "$status" -eq 0 ]
}

@test "case 7: src/ 파일 -> exit 0 (scope 외)" {
    cat > src/orchestrator.py <<'EOF'
# timestamp: 2026-05-16T18:50:50Z
def run():
    pass
EOF
    run bash scripts/check-kst-timestamp.sh src/orchestrator.py
    [ "$status" -eq 0 ]
}

@test "case 8: docs/stories/ 파일 -> exit 0 (scope 외 — Story file 은 machine-layer)" {
    cat > docs/stories/CFP-999.md <<'EOF'
---
key: CFP-999
---

## §14 Lane Evidence

| lane | spawned_at | returned_at |
|---|---|---|
| 요구사항 | 2026-05-16T09:00:00Z | 2026-05-16T10:00:00Z |
EOF
    run bash scripts/check-kst-timestamp.sh docs/stories/CFP-999.md
    [ "$status" -eq 0 ]
}

# ─── Exempt 라인 처리 (4 case) ───

@test "case 9: fenced code block 안 비-KST timestamp -> exit 0 (exempt)" {
    cat > docs/adr/ADR-994-fenced.md <<'EOF'
---
adr_number: 994
title: fenced fixture
---

# fenced

다음 예시는 lint 대상 외:

```sh
echo "timestamp: 2026-05-16T18:50:50Z"
```
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-994-fenced.md
    [ "$status" -eq 0 ]
}

@test "case 10: blockquote 안 비-KST timestamp -> exit 0 (exempt)" {
    cat > docs/adr/ADR-993-blockquote.md <<'EOF'
---
adr_number: 993
title: blockquote fixture
---

# blockquote

> "2026-05-16T09:00:00Z 에 수신된 메시지" 사용자 발화 인용.
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-993-blockquote.md
    [ "$status" -eq 0 ]
}

@test "case 11: spawned_at 라인 비-KST timestamp -> exit 0 (machine-layer exempt)" {
    # spawned_at / returned_at = §14 machine-layer, KST_TS_RE 검출 대상 외
    cat > docs/adr/ADR-992-machine.md <<'EOF'
---
adr_number: 992
title: machine-layer exempt fixture
---

# machine-layer

    spawned_at: 2026-05-16T09:00:00Z
    returned_at: 2026-05-16T10:00:00Z
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-992-machine.md
    [ "$status" -eq 0 ]
}

@test "case 12: ADR frontmatter date-only line -> exit 0 (no offset, unmatched)" {
    # date: YYYY-MM-DD 형식은 KST_TS_RE 에 T 없어서 미매칭 → 자연 면제
    cat > docs/adr/ADR-991-dateonly.md <<'EOF'
---
adr_number: 991
title: date-only frontmatter fixture
date: 2026-05-16
---

# date-only

frontmatter 의 date: YYYY-MM-DD 는 offset 없음 — lint 대상 외.
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-991-dateonly.md
    [ "$status" -eq 0 ]
}

# ─── Edge case (3 case) ───

@test "case 13: 복수 timestamp 혼재 (+09:00 + Z) -> exit 1 (Z 위반 검출)" {
    cat > docs/adr/ADR-990-mixed.md <<'EOF'
---
adr_number: 990
title: mixed fixture
---

# mixed

good: 2026-05-16T18:50:50+09:00
bad: 2026-05-16T09:50:50Z
EOF
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-990-mixed.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"violation 1건"* ]]
}

@test "case 14: 빈 file -> exit 0 (no content)" {
    touch docs/adr/ADR-989-empty.md
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-989-empty.md
    [ "$status" -eq 0 ]
}

@test "case 15: file 부재 -> exit 0 + soft warn (skip)" {
    run bash scripts/check-kst-timestamp.sh docs/adr/ADR-988-missing.md
    [ "$status" -eq 0 ]
}
