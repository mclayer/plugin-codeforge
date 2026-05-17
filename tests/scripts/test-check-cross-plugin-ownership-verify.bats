#!/usr/bin/env bats
# CFP-841 / ADR-082 Amendment 1 §결정 6 scope(d) — cross-plugin-ownership-verify lint bats unit tests
#
# Scope: Change Plan §3.2 Test Contract verbatim mirror.
# Framework: bats-core (ubuntu-latest 사전 설치, Windows = npm install -g bats 또는 Git Bash)
# Local run: bats tests/scripts/test-check-cross-plugin-ownership-verify.bats
#
# 본 fixture file 자체는 self-referential exemption allowlist (script 가 self-scan skip).

setup() {
    REPO_ROOT="$(pwd)"
    export REPO_ROOT
    TEST_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t cfp841d)"
    export TEST_DIR
    mkdir -p "$TEST_DIR/scripts/lib" \
             "$TEST_DIR/docs/adr" \
             "$TEST_DIR/docs/change-plans" \
             "$TEST_DIR/docs/domain-knowledge/domain/governance-principle" \
             "$TEST_DIR/templates" \
             "$TEST_DIR/skills/lane-self-write-boundary" \
             "$TEST_DIR/src"
    cp "$REPO_ROOT/scripts/check-cross-plugin-ownership-verify.sh" "$TEST_DIR/scripts/"
    cp "$REPO_ROOT/scripts/check-cross-plugin-ownership-verify.py" "$TEST_DIR/scripts/"
    chmod +x "$TEST_DIR/scripts/check-cross-plugin-ownership-verify.sh"
    # yaml SSOT 복사 — §13.B 4-way sync 검증용
    cp "$REPO_ROOT/docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml" \
        "$TEST_DIR/docs/domain-knowledge/domain/governance-principle/"
    # SKILL.md 복사
    mkdir -p "$TEST_DIR/skills/lane-self-write-boundary"
    cp "$REPO_ROOT/skills/lane-self-write-boundary/SKILL.md" \
        "$TEST_DIR/skills/lane-self-write-boundary/" 2>/dev/null || true
    cd "$TEST_DIR"
}

teardown() {
    cd "$REPO_ROOT" || true
    rm -rf "$TEST_DIR"
}

# ─── case 1: yaml query positive — wrapper-local 단정 + annotation 부재 → fail ───

@test "case 1 (yaml-query-positive): templates/* wrapper-local 단정 + annotation 부재 -> exit 1 violation" {
    cat > docs/change-plans/2026-05-17-test.md <<'EOF'
---
change_plan: TEST-001
title: test fixture
---

# Test

templates/github-workflows/corpus-claim-verify.yml 는 wrapper-local 파일.
docs/adr/ADR-082-write-time-self-write-verification-mandate.md 는 wrapper-canonical.
EOF
    run bash scripts/check-cross-plugin-ownership-verify.sh docs/change-plans/2026-05-17-test.md
    [ "$status" -eq 1 ]
    [[ "$output" == *"OWNERSHIP_UNVERIFIED"* ]] || [[ "$output" == *"violation"* ]] || [[ "$output" == *"FAIL"* ]]
}

# ─── case 2: yaml query negative — annotation 보유 → pass ───

@test "case 2 (yaml-query-negative): wrapper-local 단정 + annotation 보유 -> exit 0 PASS" {
    cat > docs/change-plans/2026-05-17-clean.md <<'EOF'
---
change_plan: TEST-002
title: clean fixture
---

# Clean

templates/github-workflows/corpus-claim-verify.yml 는 wrapper-local 파일. [ownership-verified: cross_plugin_doc_ownership.doc_type=change_plan.owner_plugin=codeforge-design]
docs/adr/ADR-082-write-time-self-write-verification-mandate.md 는 wrapper-canonical. [ownership-verified: cross_plugin_doc_ownership.doc_type=adr.owner_plugin=codeforge-design]
EOF
    run bash scripts/check-cross-plugin-ownership-verify.sh docs/change-plans/2026-05-17-clean.md
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}

# ─── case 3: §13.B 4-way mismatch detect — yaml vs lint regex 불일치 시 flag ───

@test "case 3 (13B-sync): §13.B 4-way sync invariant check -> yaml-as-canonical SSOT invariant PASS" {
    # yaml SSOT 에 cross_plugin_doc_ownership 가 있어야 함 (Phase 2 구현 완료 후 PASS)
    run bash scripts/check-cross-plugin-ownership-verify.sh --check-4way-sync
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}

# ─── case 4: 스캔 대상 없음 → exit 0 ───

@test "case 4: 스캔 대상 파일 없음 -> exit 0 PASS" {
    run bash scripts/check-cross-plugin-ownership-verify.sh
    [ "$status" -eq 0 ]
}

# ─── case 5: comment-only FN — 실제 key 부재 + 주석만 존재 → 4WAY-SYNC-FAIL (exit 1) ───
# FIX iter1: F-CR-841-2 regex key 매칭으로 comment-only false-negative 차단
# RED-first: pre-FIX bare-substring 은 주석 line 매칭 → PASS(exit 0, FN); post-FIX regex → FAIL(exit 1)

@test "case 5 (comment-only-FN): cross_plugin_doc_ownership 주석만 존재 (실제 key 부재) -> exit 1 4WAY-SYNC-FAIL" {
    # yaml SSOT 에 실제 key 없이 주석만 포함한 fixture 생성
    mkdir -p docs/domain-knowledge/domain/governance-principle
    cat > docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml <<'EOF'
# lane-self-write-ownership-matrix.yaml — test fixture
# cross_plugin_doc_ownership sub-tree is defined here
# cross_plugin_doc_ownership: (commented out, not actual key)
lane_ownership:
  codeforge-design:
    - docs/change-plans/**
EOF

    # SKILL.md dummy 생성 (4way sync 에서 yaml 만 체크)
    mkdir -p skills/lane-self-write-boundary
    cat > skills/lane-self-write-boundary/SKILL.md <<'EOF'
# SKILL.md fixture
machine_readable_ssot: lane-self-write-ownership-matrix.yaml
EOF

    run python3 "$REPO_ROOT/scripts/check-cross-plugin-ownership-verify.py" --check-4way-sync
    [ "$status" -eq 1 ]
    [[ "$output" == *"4WAY-SYNC-FAIL"* ]] || [[ "$output" == *"FAIL"* ]]
}

# ─── case 6: actual key 보유 yaml → 4WAY-SYNC PASS (exit 0) ───
# F-CR-841-2 regex 수정 후에도 실제 key 보유 시 false-negative 없이 PASS

@test "case 6 (actual-key-positive): cross_plugin_doc_ownership 실제 key 보유 yaml -> exit 0 PASS" {
    mkdir -p docs/domain-knowledge/domain/governance-principle
    cat > docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml <<'EOF'
# lane-self-write-ownership-matrix.yaml — test fixture with actual key
# cross_plugin_doc_ownership sub-tree reference comment
cross_plugin_doc_ownership:
  doc_type: adr
  owner_plugin: codeforge-design
EOF

    mkdir -p skills/lane-self-write-boundary
    cat > skills/lane-self-write-boundary/SKILL.md <<'EOF'
# SKILL.md fixture
cross_plugin_doc_ownership: reference for sync check
machine_readable_ssot: lane-self-write-ownership-matrix.yaml
EOF

    run python3 "$REPO_ROOT/scripts/check-cross-plugin-ownership-verify.py" --check-4way-sync
    [ "$status" -eq 0 ]
    [[ "$output" == *"PASS"* ]]
}
