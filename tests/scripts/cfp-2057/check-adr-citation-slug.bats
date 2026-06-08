#!/usr/bin/env bats
# CFP-2057: D5 — ADR citation slug lint (check-adr-citation-slug.sh) 테스트
# 2-layer: L1 slug-existence + L2 deny-list (ALLOWED_HUB_REPOS/SECURITY_PATHS 맥락 ADR-057)
#
# discriminating fixture 의무 (CFP-1334):
#   D5 fixture 는 구현 전 RED → 구현 후 GREEN.
# ADR-061 준수: external .py SSOT, bats wrapper.

SCRIPT="$(dirname "$BATS_TEST_DIRNAME")/../../scripts/check-adr-citation-slug.sh"
LIB="$(dirname "$BATS_TEST_DIRNAME")/../../scripts/lib/check_adr_citation_slug.py"

setup() {
  TEST_TEMP_DIR="$(mktemp -d)"
  # ADR 디렉터리 구조 생성
  mkdir -p "${TEST_TEMP_DIR}/archive/adr"
  # ADR-026, ADR-024, ADR-116 slug 파일 생성 (L1 통과용)
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-026-post-merge-automation.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-024-branch-protection-contexts.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-116-consumer-whitelist-idempotent-injection.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-057-orchestrator-opus-mandate.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-060-evidence-checks-framework.md"
}

teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

# ─── 기본 동작 ─────────────────────────────────────────────────────────

@test "스크립트 파일 존재" {
  [ -f "$SCRIPT" ]
}

@test "Python SSOT 파일 존재 (ADR-061)" {
  [ -f "$LIB" ]
}

@test "스크립트에 실행 위임(exec python3) 패턴 존재 (ADR-061 thin wrapper)" {
  grep -q "exec python3" "$SCRIPT"
}

# ─── L2 deny-list 검사 ─────────────────────────────────────────────────

# D5-L2-a: ALLOWED_HUB_REPOS + ADR-057 조합 → exit 1 (discriminating: 구현 없으면 RED)
@test "L2: ADR-057 + ALLOWED_HUB_REPOS 맥락 → exit 1" {
  local test_file="${TEST_TEMP_DIR}/test.md"
  cat > "$test_file" << 'EOF'
# 테스트 문서

consumer overlay: ALLOWED_HUB_REPOS 확장 가능 (ADR-057 정합 — 축소 불가).
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "L2-DENY"
}

# D5-L2-b: SECURITY_PATHS + ADR-057 조합 → exit 1
@test "L2: ADR-057 + SECURITY_PATHS 맥락 → exit 1" {
  local test_file="${TEST_TEMP_DIR}/test.yml"
  cat > "$test_file" << 'EOF'
# consumer overlay 가 SECURITY_PATHS 확장 가능 (축소 불가 — ADR-057 정합)
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 1 ]
  echo "$output" | grep -q "L2-DENY"
}

# D5-L2-c: 역사 서술(오인용 정정 문맥) → 면제 (false-positive 방지)
@test "L2: 오인용 정정 문맥 → 면제 (false-positive 없음)" {
  local test_file="${TEST_TEMP_DIR}/adr-fix.md"
  cat > "$test_file" << 'EOF'
# 오인용 정정 대상

ADR-057 오인용 정정 — 실제 ADR-057 = Orchestrator Opus mandate (확장-only 와 무관).
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  # L2 violation 없어야 함 (status 0 또는 2 — L1만 있을 수 있음)
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# D5-L2-d: 정정된 string (ADR-026 Amd 4 §결정 6) → pass
@test "L2: D1 정정 후 string (ADR-026 + ADR-024 + ADR-116) → PASS" {
  local test_file="${TEST_TEMP_DIR}/corrected.yml"
  cat > "$test_file" << 'EOF'
# consumer overlay: ALLOWED_HUB_REPOS 확장 가능
# (ADR-026 Amd 4 §결정 6 (화이트리스트) + ADR-024 §결정 6 (확장-only 패턴) + ADR-116 (주입 mechanism) — 축소 불가)
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  # L2 위반 없음
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# ─── L1 slug-existence 검사 ────────────────────────────────────────────

# D5-L1-a: 존재하는 ADR 인용 → pass
@test "L1: 존재하는 ADR-026 인용 → PASS" {
  local test_file="${TEST_TEMP_DIR}/valid.md"
  cat > "$test_file" << 'EOF'
ADR-026 Amendment 4 §결정 6 화이트리스트 정책.
ADR-024 §결정 6 확장-only 패턴 선례.
ADR-116 주입 mechanism.
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 0 ]
}

# D5-L1-b: 미존재 ADR 인용 → exit 2 (non-sentinel 번호)
@test "L1: 미존재 ADR-042 인용 → exit 2" {
  local test_file="${TEST_TEMP_DIR}/missing.md"
  cat > "$test_file" << 'EOF'
참조: ADR-042 정합.
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 2 ]
  echo "$output" | grep -q "L1-SLUG"
}

# D5-L1-c: sentinel 번호(>= 900) → L1 skip (false-positive 방지, CFP-2057 P2 fix)
@test "L1: sentinel ADR-999 인용 → PASS (sentinel skip)" {
  local test_file="${TEST_TEMP_DIR}/sentinel.md"
  cat > "$test_file" << 'EOF'
테스트 예시: ADR-999 참조 (placeholder 번호).
ADR-9995, ADR-9998 도 sentinel.
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  # sentinel 번호 → L1 위반 없음 (status 0)
  [ "$status" -eq 0 ]
}

# D5-L1-d: tests/ 경로 파일 → L1 면제 (fixture 경로, CFP-2057 P2 fix)
@test "L1: tests/ 경로 파일의 미존재 ADR 인용 → L1 면제 PASS" {
  mkdir -p "${TEST_TEMP_DIR}/tests/fixtures"
  local test_file="${TEST_TEMP_DIR}/tests/fixtures/sample-fixture.md"
  cat > "$test_file" << 'EOF'
id: ADR-042
# ADR-042: 테스트 fixture ADR sentinel (존재하지 않는 ADR 번호)
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  # tests/ 경로 면제 → L1 위반 없음 (status 0)
  [ "$status" -eq 0 ]
}

# D5-L1-e: 한 줄에 같은 ADR 번호 2회 → 위반 1건 (dedup, CFP-2057 P2 fix)
@test "L1: 한 줄에 같은 ADR-042 2회 인용 → 위반 1건 (dedup)" {
  local test_file="${TEST_TEMP_DIR}/dedup.md"
  cat > "$test_file" << 'EOF'
ADR-042 정합 (ADR-042 참조 중복).
EOF

  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 2 ]
  # 위반 1건 (L1-SLUG 1개) — dedup 결과 2건이 아님
  local count
  count=$(echo "$output" | grep -c "L1-SLUG" || true)
  [ "$count" -eq 1 ]
}

# ─── D5 자기 진원 RED 방지 확인 ───────────────────────────────────────

# D5-pass: D1 정정 완료된 파일들에 대해 D5 lint 자기 RED 없음
@test "D5: D1 정정 완료 후 phase-gate-mergeable.yml ADR-057 L2 위반 0건" {
  # D1 정정 완료 상태의 실제 파일 (ADR-057 제거됨)
  local wt_file
  wt_file="$(dirname "$BATS_TEST_DIRNAME")/../../.github/workflows/phase-gate-mergeable.yml"

  if [ ! -f "$wt_file" ]; then
    skip "worktree 파일 접근 불가"
  fi

  run python3 "$LIB" \
    --repo-root "$(dirname "$BATS_TEST_DIRNAME")/../.." \
    --l2-only \
    "$wt_file"
  # L2 위반 없음 (D1 정정 완료 확인)
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# ─── 출력 형식 확인 ────────────────────────────────────────────────────

@test "한계 명시 출력 (AC-5 의무 — L2 위반 시 NOTE 출력)" {
  local test_file="${TEST_TEMP_DIR}/violation.md"
  cat > "$test_file" << 'EOF'
ALLOWED_HUB_REPOS (ADR-057 test violation)
EOF

  # bats run captures combined stdout+stderr — capture manually for reliability
  local combined
  combined=$(python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file" 2>&1) || true
  echo "$combined" | grep -q "NOTE:"
}
