#!/usr/bin/env bats
# CFP-2093: D3 — ADR citation slug lint Population B 전역 확대 테스트
# 설계 §8.1 Test Contract FX-A (proximity boundary) + FX-B (EXEMPT discriminating) 이행.
#
# ADR-061 준수: external .py SSOT, bats wrapper.
# discriminating fixture 의무:
#   FX-A: .{0,40} proximity 경계 (39/40/41자 ADR-057 ↔ ratchet 키워드 간격)
#   FX-B: EXEMPT discriminating (proximity-bound + deny-priority)

LIB="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../../scripts/lib" && pwd)/check_adr_citation_slug.py"

setup() {
  TEST_TEMP_DIR="$(mktemp -d)"
  # ADR 디렉터리 구조 생성 (L1 통과용)
  mkdir -p "${TEST_TEMP_DIR}/archive/adr"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-064-decision-principle-mandate.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-058-adr-sunset-criteria-mandate.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-026-post-merge-automation.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-024-branch-protection-contexts.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-116-consumer-whitelist-idempotent-injection.md"
}

teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

# ─── FX-A: .{0,40} proximity 경계 테스트 ─────────────────────────────────

# FX-A1: ADR-057 + 39자 + 축소 불가 → DENY (RED)  [< 40 = match]
@test "FX-A1: ADR-057 ~ 39자 ~ 축소 불가 → DENY (RED)" {
  local test_file="${TEST_TEMP_DIR}/fx-a1.md"
  # ADR-057 + 정확히 39자 공백 + 축소 불가
  printf '# test\nADR-057%s축소 불가\n' "$(python3 -c "print(' '*39)")" > "$test_file"
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 1 ] || [ "$status" -eq 3 ]
  echo "$output" | grep -q "L2-DENY"
}

# FX-A2: ADR-057 + 40자 + 축소 불가 → DENY (RED)  [= 40 = 상한 매치]
@test "FX-A2: ADR-057 ~ 40자 ~ 축소 불가 → DENY (RED) (경계 매치)" {
  local test_file="${TEST_TEMP_DIR}/fx-a2.md"
  printf '# test\nADR-057%s축소 불가\n' "$(python3 -c "print(' '*40)")" > "$test_file"
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 1 ] || [ "$status" -eq 3 ]
  echo "$output" | grep -q "L2-DENY"
}

# FX-A3: ADR-057 + 41자 + 축소 불가 → PASS (비매치)  [> 40 = proximity 초과]
@test "FX-A3: ADR-057 ~ 41자 ~ 축소 불가 → PASS (proximity 초과, 비매치)" {
  local test_file="${TEST_TEMP_DIR}/fx-a3.md"
  printf '# test\nADR-057%s축소 불가\n' "$(python3 -c "print(' '*41)")" > "$test_file"
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  # L2 violation 없음
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# FX-A4: 역순 — 확장만 + 40자 + ADR-057 → DENY (RED)  [역순 패턴 cover]
@test "FX-A4: 확장만 ~ 40자 ~ ADR-057 역순 → DENY (RED)" {
  local test_file="${TEST_TEMP_DIR}/fx-a4.md"
  printf '# test\n확장만%sADR-057\n' "$(python3 -c "print(' '*40)")" > "$test_file"
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 1 ] || [ "$status" -eq 3 ]
  echo "$output" | grep -q "L2-DENY"
}

# FX-A5: ADR-057 + 41자 + never-reduce (구두점 분리, > 40) → PASS
@test "FX-A5: ADR-057 ~ 41자 ~ never-reduce → PASS (별개 문장 오탐 차단)" {
  local test_file="${TEST_TEMP_DIR}/fx-a5.md"
  printf '# test\nADR-057%snever-reduce\n' "$(python3 -c "print(' '*41)")" > "$test_file"
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# ─── FX-B: EXEMPT discriminating 테스트 ──────────────────────────────────

# FX-B1: 자동 재시도 금지 (ADR-057) — 정당 인용 → EXEMPT (GREEN)
@test "FX-B1: 자동 재시도 금지 (ADR-057) 정당 인용 → EXEMPT (GREEN)" {
  local test_file="${TEST_TEMP_DIR}/fx-b1.md"
  cat > "$test_file" << 'EOF'
자동 재시도 금지 (ADR-057 정합 — PMOAgent 실패 시 escalate)
EOF
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# FX-B2: Sonnet→Opus fallback (ADR-057) — 정당 인용 → EXEMPT (GREEN)
@test "FX-B2: Sonnet→Opus fallback (ADR-057) 정당 인용 → EXEMPT (GREEN)" {
  local test_file="${TEST_TEMP_DIR}/fx-b2.md"
  cat > "$test_file" << 'EOF'
Sonnet→Opus fallback (ADR-057 §결정 2 — rate-limit fallback)
EOF
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# FX-B3: 확장-only ADR-057 — ratchet misquote → DENY (RED)
@test "FX-B3: 확장-only ADR-057 ratchet misquote → DENY (RED)" {
  local test_file="${TEST_TEMP_DIR}/fx-b3.md"
  cat > "$test_file" << 'EOF'
확장-only (ADR-057 정합) — overlay 축소 불가 ratchet
EOF
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 1 ] || [ "$status" -eq 3 ]
  echo "$output" | grep -q "L2-DENY"
}

# FX-B4: 혼재 라인 정정 전 (축소 불가 ADR-057 + 자동 재시도 금지 ADR-057 근접) → DENY (RED)
# 핵심: bare exempt 였다면 면제됐을 false-negative — proximity-bound + deny 우선이 차단
@test "FX-B4: 혼재 라인 정정 전 (축소불가 + 자동재시도 혼재) → DENY (RED, deny 우선)" {
  local test_file="${TEST_TEMP_DIR}/fx-b4.md"
  cat > "$test_file" << 'EOF'
축소 불가 (ADR-057) 자동 재시도 금지 (ADR-057)
EOF
  # 이 라인: "축소 불가 (ADR-057)" = ratchet misquote near ADR-057 → deny match
  # "자동 재시도 금지 (ADR-057)" = 정당 인용 → proximity-bound exempt match
  # deny 우선 → RED
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 1 ] || [ "$status" -eq 3 ]
  echo "$output" | grep -q "L2-DENY"
}

# FX-B5: 분리 정정 후 — 축소불가는 ADR-064 전용 행, ADR-057은 자동재시도 전용 행 (2행 분리)
# 설계 §7.2 #10: ADR-106 관련 ADR 링크를 2행으로 분리 (ADR-064 행 + ADR-057 자동재시도 행)
@test "FX-B5: 분리 정정 후 (2행 분리 — 축소불가=ADR-064행 / 자동재시도=ADR-057행) → PASS (GREEN)" {
  local test_file="${TEST_TEMP_DIR}/fx-b5.md"
  touch "${TEST_TEMP_DIR}/archive/adr/ADR-064-decision-principle-mandate.md"
  cat > "$test_file" << 'EOF'
- **ADR-064 §결정 7** — consumer overlay 축소 불가 (closure threshold 확장 가능 / 축소 불가)
- **ADR-057** — "자동 재시도 금지" (PMOAgent 실패 시 escalate)
EOF
  # 2행 분리 후: 각 행에서 ADR-057 근접 어휘 = "자동 재시도 금지" 뿐 (ratchet 키워드 없음)
  # ADR-064 행: "축소 불가" ↔ ADR-064 근접 (ADR-057 없음) → no deny match
  # ADR-057 행: "자동 재시도 금지" ↔ ADR-057 근접 → proximity-bound exempt → PASS
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# FX-B6: Orchestrator Opus mandate (ADR-057) — 기존 면제 retain → EXEMPT (GREEN)
@test "FX-B6: Orchestrator Opus mandate (ADR-057) 기존 면제 → EXEMPT (GREEN)" {
  local test_file="${TEST_TEMP_DIR}/fx-b6.md"
  cat > "$test_file" << 'EOF'
Orchestrator Opus mandate (ADR-057 §결정 1 — 별칭 opus 필수)
EOF
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# ─── Population B 전역 확대 동작 확인 ────────────────────────────────────

# ADR-079 정정 전 패턴 → DENY
@test "Population B: ADR-079 정정 전 패턴 (overlay 축소 불가 ADR-057) → DENY" {
  local test_file="${TEST_TEMP_DIR}/adr-079-before.md"
  cat > "$test_file" << 'EOF'
consumer overlay 는 정책을 축소할 수 없고 확장만 가능 (CLAUDE.md normative + ADR-057 정합).
EOF
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -eq 1 ] || [ "$status" -eq 3 ]
  echo "$output" | grep -q "L2-DENY"
}

# ADR-079 정정 후 패턴 → PASS
@test "Population B: ADR-079 정정 후 패턴 (ADR-064 §결정 7 정합) → PASS" {
  local test_file="${TEST_TEMP_DIR}/adr-079-after.md"
  cat > "$test_file" << 'EOF'
consumer overlay 는 정책을 축소할 수 없고 확장만 가능 (CLAUDE.md normative + consumer-guide §2556 + ADR-064 §결정 7 정합).
EOF
  run python3 "$LIB" --repo-root "$TEST_TEMP_DIR" "$test_file"
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}

# ─── D2 정정 완료 실파일 자기 RED 없음 확인 ─────────────────────────────

@test "D2 정정 완료: ADR-106 실파일 L2 위반 0건" {
  local real_file
  real_file="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)/archive/adr/ADR-106-operational-signal-pmo-input-circuit.md"

  if [ ! -f "$real_file" ]; then
    skip "실파일 접근 불가"
  fi

  run python3 "$LIB" \
    --repo-root "$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)" \
    --l2-only \
    "$real_file"
  [ "$status" -ne 1 ] && [ "$status" -ne 3 ]
}
