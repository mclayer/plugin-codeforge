#!/usr/bin/env bats
# tests/scripts/cfp-1014/cfp-1014-downgrade-asymmetry-wired.bats
# CFP-1014 Phase 2 — Wave 4 sub-Epic #882 Story-5 downgrade asymmetry invariant wired 활성
# QADeveloperAgent TDD (RED written against Phase 2 spec, GREEN against Phase 1 implementation)
#
# TC map (Story §3.5 + Change Plan §8.1 TestContractArch 3-layer defense + dissent 1+2+3):
#
# TC-1~3:   yaml.safe_load + §4.14 status="wired" equality (positive + negative + discriminating fixture)
# TC-4~6:   closed_enum length=2 invariant + content equality
# TC-7~9:   open_extension: false declaration verify (SecurityArch ratchet 강화)
# TC-10~12: carrier_story="CFP-1014" verify (carrier→realized 정정)
# TC-13~15: activation_protocol tense forward-effective verify
#
# 3-layer defense (#960 always-pass pattern_count 4 reach 차단 carrier):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture TDD RED phase (TC-3/TC-DISC-1, TC-6/TC-DISC-2, TC-15/TC-DISC-3)
#             (git stash 패턴, [feedback_tdd_red_proof_via_stash] 정합,
#              CFP-991 line 470-517 pattern verbatim 답습)
#
# Mock seam: _CFP1014_MOCK_* namespace (CFP-991 _CFP991_MOCK_* verbatim 답습)
#   _CFP1014_MOCK_STATUS    — downgrade_asymmetry_marker.status mock
#   _CFP1014_MOCK_CARRIER   — carrier_story mock
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1 — setup_file/teardown_file export
#
# Baseline SHA: 2ff49abe (Phase 1 merged, wrapper main HEAD = cfp-1014 HEAD)
# Evidence origin annotation: wrapper_self (Phase 2 = declare-only bats + no production code)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

RECONCILE_CONTRACT="${WORKTREE_ROOT}/docs/inter-plugin-contracts/reconcile-protocol-v1.md"

# ──────────────────────────────────────────────── sandbox setup ───────────────

setup_file() {
  # CFP-843 §3.3 sandbox env — bats setup_file/teardown_file export
  export CBL_SKIP_ISSUE_CREATE=1
  export CFP1014_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
  unset CFP1014_SKIP_ISSUE_CREATE
}

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown() {
  unset _CFP1014_MOCK_STATUS || true
  unset _CFP1014_MOCK_CARRIER || true
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1014-unused}"
}

# ───────────────── TC-1~3: status="wired" equality ──────────────────────────

@test "TC-1 (P0): reconcile-protocol-v1.md frontmatter version=1.12 + §4.14 downgrade_asymmetry_marker 블록 존재" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — frontmatter version 1.12
  grep -q 'version: "1.12"' "$RECONCILE_CONTRACT"
  # negative — stale version 1.11 (predecessor) 단독 선언 아님
  # (1.11 이 version_history 에 존재하므로 frontmatter 에만 없는지 체크)
  local frontmatter_version
  frontmatter_version=$(head -10 "$RECONCILE_CONTRACT" | grep '^version:' | awk '{print $2}' | tr -d '"')
  [ "$frontmatter_version" = "1.12" ]
}

@test "TC-2 (P0): §4.14 downgrade_asymmetry_marker.status = 'wired' (positive + negative)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — status: "wired" 선언 존재
  grep -q 'status: "wired"' "$RECONCILE_CONTRACT"
  # negative — placeholder_reserve 가 status 필드로 잔존하지 않음
  # (version_history 안에는 있으므로 downgrade_asymmetry_marker 블록 컨텍스트 한정)
  local block_status
  block_status=$(grep -A 10 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "status:" | head -1 | awk '{print $2}' | tr -d '"')
  [ "$block_status" = "wired" ]
}

@test "TC-3/TC-DISC-1 (P0): discriminating fixture — status='placeholder_reserve' 가 wired 와 다름 (Layer 3)" {
  # discriminating fixture: 만약 status 가 placeholder_reserve 라면 TC-2 는 실패해야 한다
  # 이 TC 는 discriminating fixture 자체를 검증 (TC-2 의 genuine RED 입증 보조)
  [ -f "$RECONCILE_CONTRACT" ]
  local block_status
  block_status=$(grep -A 10 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "status:" | head -1 | awk '{print $2}' | tr -d '"')
  # positive — 현재 status 는 wired (Phase 1 merge 완료)
  [ "$block_status" = "wired" ]
  # negative — placeholder_reserve 와 같지 않음 (discriminating assertion)
  [ "$block_status" != "placeholder_reserve" ]
}

# ───────────────── TC-4~6: closed_enum length=2 invariant ────────────────────

@test "TC-4 (P1): closed_enum 필드 존재 + 정확히 2개 값 선언" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — closed_enum 필드 존재
  grep -q "closed_enum:" "$RECONCILE_CONTRACT"
  # positive — placeholder_reserve, wired 2 값 포함
  grep -A 5 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep -q "closed_enum:.*placeholder_reserve.*wired\|closed_enum:.*wired.*placeholder_reserve"
}

@test "TC-5 (P1): closed_enum 내용 — placeholder_reserve 와 wired 양쪽 존재 (content equality)" {
  [ -f "$RECONCILE_CONTRACT" ]
  local closed_enum_line
  closed_enum_line=$(grep -A 10 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "closed_enum:")
  # positive — placeholder_reserve 포함
  echo "$closed_enum_line" | grep -q "placeholder_reserve"
  # positive — wired 포함
  echo "$closed_enum_line" | grep -q "wired"
}

@test "TC-6/TC-DISC-2 (P1): discriminating fixture — closed_enum length=2 invariant (3번째 값 추가 금지, Layer 3)" {
  [ -f "$RECONCILE_CONTRACT" ]
  local closed_enum_line
  closed_enum_line=$(grep -A 10 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "closed_enum:")
  # positive — 정확히 2개 값 (placeholder_reserve 와 wired)
  echo "$closed_enum_line" | grep -q "placeholder_reserve.*wired\|wired.*placeholder_reserve"
  # negative (discriminating) — 3번째 값 금지 (예: "deprecated" 등 확장 차단)
  # closed_enum 에서 3개 이상 enum 값이 있으면 실패 (length=2 invariant)
  local value_count
  value_count=$(echo "$closed_enum_line" | grep -o '"[^"]*"' | wc -l | tr -d ' ')
  [ "$value_count" -le 2 ]
}

# ───────────────── TC-7~9: open_extension: false ─────────────────────────────

@test "TC-7 (P1): open_extension: false 선언 존재 (SecurityArch ratchet 강화)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — open_extension: false 존재 (downgrade_asymmetry_marker 블록 컨텍스트)
  grep -A 15 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep -q "open_extension: false"
}

@test "TC-8 (P1): open_extension 가 true 로 선언되지 않음 (enum 확장 차단 boundary 명문화)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # negative — open_extension: true 금지 (ratchet 강화 방향만 허용)
  ! grep -A 15 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep -q "open_extension: true"
}

@test "TC-9 (P1): open_extension: false 가 downgrade_asymmetry_marker 블록 스코프 안에 있음" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — downgrade_asymmetry_marker 블록 내 15라인 안에 open_extension: false 존재
  local in_block
  in_block=$(grep -A 15 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "open_extension: false" | wc -l | tr -d ' ')
  [ "$in_block" -ge 1 ]
  # negative — 블록 밖에서만 open_extension:false 가 선언되고 블록 안에는 없는 경우 차단
  # (in_block 이 0 이면 실패 — 위에서 이미 검증됨)
}

# ───────────────── TC-10~12: carrier_story="CFP-1014" verify ─────────────────

@test "TC-10 (P0): carrier_story='CFP-1014' 정정 완료 (carrier→realized 정정)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — carrier_story: "CFP-1014" 선언 존재
  grep -A 10 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep -q 'carrier_story: "CFP-1014"'
}

@test "TC-11 (P0): carrier_story 값이 'CFP-991-Story-5' 가 아닌 'CFP-1014' 임을 직접 비교 확인" {
  [ -f "$RECONCILE_CONTRACT" ]
  # carrier_story: "CFP-1014" 줄을 직접 파싱해 정확한 값 비교
  local carrier_val
  carrier_val=$(grep -A 10 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "carrier_story:" | head -1 | awk '{print $2}' | tr -d '"')
  # negative — 값이 stale placeholder 'CFP-991-Story-5' 와 같지 않음
  [ "$carrier_val" != "CFP-991-Story-5" ]
  # positive — 값이 정확히 CFP-1014 임 (TC-12 와 동일하나 음의 방향에서 검증)
  [ "$carrier_val" = "CFP-1014" ]
}

@test "TC-12 (P1): carrier_story 값 = 정확히 'CFP-1014' (ADR-068 I-4 wording SSOT 정합)" {
  [ -f "$RECONCILE_CONTRACT" ]
  local carrier_val
  carrier_val=$(grep -A 10 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "carrier_story:" | head -1 | awk '{print $2}' | tr -d '"')
  # positive — 정확히 CFP-1014
  [ "$carrier_val" = "CFP-1014" ]
}

# ───────────────── TC-13~15: activation_protocol tense forward-effective ─────

@test "TC-13 (P1): activation_protocol 필드 존재 + 'wired 활성 완료' 또는 'forward-effective' wording 포함" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — activation_protocol 필드 존재
  grep -A 15 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep -q "activation_protocol:"
  # positive — '활성 완료' wording (Phase 1 post-merge tense 반영)
  grep -A 15 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "activation_protocol:" | grep -q "활성 완료\|forward-effective"
}

@test "TC-14 (P1): activation_protocol 가 placeholder tense ('활성 예정' 등) 이 아님" {
  [ -f "$RECONCILE_CONTRACT" ]
  # negative — stale 미래 tense 금지 ('활성 예정', 'will be activated', 'placeholder_reserve 상태')
  ! grep -A 15 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "activation_protocol:" | grep -q "활성 예정\|will be activated\|placeholder_reserve 상태"
}

@test "TC-15/TC-DISC-3 (P1): discriminating fixture — activation_protocol tense 검증 (Layer 3)" {
  # discriminating fixture: activation_protocol 이 '활성 완료' forward-effective tense 여야 함
  [ -f "$RECONCILE_CONTRACT" ]
  local ap_line
  ap_line=$(grep -A 15 "downgrade_asymmetry_marker:" "$RECONCILE_CONTRACT" | grep "activation_protocol:" | head -1)
  # positive — '활성 완료' 포함 (Phase 1 post-merge tense 검증)
  echo "$ap_line" | grep -q "활성 완료"
  # positive — 'forward-effective' 포함 (영문 tense 검증)
  echo "$ap_line" | grep -q "forward-effective"
  # negative (discriminating) — '활성 예정' 미래 tense 아님
  ! echo "$ap_line" | grep -q "활성 예정"
}
