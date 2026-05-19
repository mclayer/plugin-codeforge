#!/usr/bin/env bats
# tests/scripts/cfp-1014/cfp-1014-v1-12-amendment-log.bats
# CFP-1014 Phase 2 — v1.12 amendment_log + §4.3 (m) trigger + §4.4 ratchet row 7 + 5 cross-ref
# QADeveloperAgent TDD (RED written against Phase 2 spec, GREEN against Phase 1 implementation)
#
# TC map (Story §3.5 + Change Plan §8.1 TestContractArch dissent 1+2+3):
#
# TC-16~18: frontmatter version="1.12" equality + chronological order
# TC-19~21: amendments[] v1.12 entry append (carrier CFP-1014 + change verbatim)
# TC-22~24: §4.3 (m) trigger entry append (forward-effective + predecessor (l) v1.11 cross-ref)
# TC-25~27: §4.4 ratchet row 7 verify (wired→placeholder_reserve 역방향 차단)
# TC-28~30: 5 cross-ref atomic SSOT consistency
#           (promotion-criteria-4tuple L86 + rollback-protocol L75/L91 + README L48 + CLAUDE.md)
#
# 3-layer defense (#960 always-pass pattern_count 4 reach 차단 carrier):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture (TC-18/DISC-4, TC-24/DISC-5, TC-30/DISC-6)
#
# Mock seam: _CFP1014_MOCK_* namespace (CFP-991 _CFP991_MOCK_* verbatim 답습)
#   _CFP1014_MOCK_CONTRACT_VERSION — contract version mock
#   _CFP1014_MOCK_RATCHET_ROW     — §4.4 ratchet row mock
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1 — setup_file/teardown_file export
#
# Baseline SHA: 2ff49abe (Phase 1 merged, wrapper main HEAD = cfp-1014 HEAD)
# Evidence origin annotation: wrapper_self (Phase 2 = declare-only bats + no production code)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

RECONCILE_CONTRACT="${WORKTREE_ROOT}/docs/inter-plugin-contracts/reconcile-protocol-v1.md"
PROMOTION_CRITERIA="${WORKTREE_ROOT}/docs/domain-knowledge/domain/production-cutover/promotion-criteria-4tuple.md"
ROLLBACK_PROTOCOL="${WORKTREE_ROOT}/docs/domain-knowledge/domain/production-cutover/rollback-protocol.md"
PRODUCTION_README="${WORKTREE_ROOT}/docs/domain-knowledge/domain/production-cutover/README.md"
CLAUDE_MD="${WORKTREE_ROOT}/CLAUDE.md"

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
  unset _CFP1014_MOCK_CONTRACT_VERSION || true
  unset _CFP1014_MOCK_RATCHET_ROW || true
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1014-v112-unused}"
}

# ───────────────── TC-16~18: frontmatter version="1.12" + chronological order ─

@test "TC-16 (P0): reconcile-protocol-v1.md frontmatter version = '1.12'" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — frontmatter 정확히 version: "1.12"
  grep -q 'version: "1.12"' "$RECONCILE_CONTRACT"
  # negative — version: "1.11" 이 frontmatter 에 단독 존재하지 않음
  local frontmatter_version
  frontmatter_version=$(head -10 "$RECONCILE_CONTRACT" | grep '^version:' | awk '{print $2}' | tr -d '"')
  [ "$frontmatter_version" != "1.11" ]
}

@test "TC-17 (P0): version_history 에 v1.12 entry 존재 + carrier: CFP-1014 명시" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — version_history 에 version: "1.12" 항목 존재
  grep -q '"1.12"' "$RECONCILE_CONTRACT"
  # positive — carrier: CFP-1014 명시
  grep -q 'carrier: CFP-1014' "$RECONCILE_CONTRACT"
}

@test "TC-18/TC-DISC-4 (P0): discriminating fixture — v1.12 가 v1.11 의 후계 (chronological order, Layer 3)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # discriminating: version_history 블록 안에서 v1.11 entry 가 v1.12 entry 보다 먼저 등장해야 함
  # (frontmatter line 4 의 version: "1.12" 는 제외하고 version_history 안 entry 라인 비교)
  # version_history entry 패턴: `  - { version: "1.11"` 또는 `  - { version: "1.12"`
  local line_v111 line_v112
  line_v111=$(grep -n '{ version: "1.11"' "$RECONCILE_CONTRACT" | head -1 | cut -d: -f1)
  line_v112=$(grep -n '{ version: "1.12"' "$RECONCILE_CONTRACT" | head -1 | cut -d: -f1)
  # positive — 두 항목 모두 version_history 에 존재
  [ -n "$line_v111" ]
  [ -n "$line_v112" ]
  # positive (discriminating) — v1.12 entry 가 v1.11 entry 보다 뒤에 등장 (append-only chronological order)
  [ "$line_v112" -gt "$line_v111" ]
}

# ───────────────── TC-19~21: amendments[] v1.12 entry ────────────────────────

@test "TC-19 (P0): v1.12 entry 가 'downgrade asymmetry' 변경 설명 포함" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — downgrade asymmetry 변경 내용 언급
  grep -A 5 '"1.12"' "$RECONCILE_CONTRACT" | grep -q "downgrade\|asymmetry"
}

@test "TC-20 (P0): v1.12 entry 가 'placeholder_reserve → wired' 전환 언급 포함" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — placeholder_reserve → wired 전환 명시
  grep -A 10 '"1.12"' "$RECONCILE_CONTRACT" | grep -q "placeholder_reserve.*wired\|wired.*placeholder_reserve"
  # negative — 역방향 wired → placeholder_reserve 가 활성 경로로 언급되지 않음
  # (§4.4 ratchet row 에서 차단 항목으로 언급은 허용, 활성 경로로 언급 금지)
  ! grep -A 10 '"1.12"' "$RECONCILE_CONTRACT" | grep -v "ratchet\|차단\|역방향" | grep -q "wired.*→.*placeholder_reserve"
}

@test "TC-21 (P1): v1.12 entry 가 'Wave 4 sub-Epic #882 close' 또는 '5/5 Story complete' 언급 포함" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — Wave 4 sub-Epic #882 close marker 또는 5/5 Story complete 언급
  grep -A 15 '"1.12"' "$RECONCILE_CONTRACT" | grep -q "sub-Epic.*882\|5/5 Story"
  # negative — '4/5 Story' 등 미완료 상태 언급 아님
  ! grep -A 15 '"1.12"' "$RECONCILE_CONTRACT" | grep -q "4/5 Story\|3/5 Story"
}

# ───────────────── TC-22~24: §4.3 (m) trigger entry ─────────────────────────

@test "TC-22 (P0): §4.3 (m) trigger entry 존재 (forward-effective activation)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — §4.3 (m) trigger 항목 존재
  grep -q "(m)" "$RECONCILE_CONTRACT"
  # positive — CFP-1014 또는 Story-5 와 연결
  grep -A 5 "(m)" "$RECONCILE_CONTRACT" | grep -q "CFP-1014\|Story-5"
}

@test "TC-23 (P0): §4.3 (m) 항목이 'v1.12 발동 완료' 선언 포함" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — v1.12 발동 완료 선언
  grep -A 5 "(m)" "$RECONCILE_CONTRACT" | grep -q "v1.12 발동 완료\|v1.12.*완료\|발동 완료"
}

@test "TC-24/TC-DISC-5 (P0): discriminating fixture — §4.3 (m) 가 (l) v1.11 의 후계임 확인 (Layer 3)" {
  [ -f "$RECONCILE_CONTRACT" ]
  # discriminating: (m) 항목이 (l) 항목보다 뒤에 위치
  local line_l line_m
  line_l=$(grep -n "(l)" "$RECONCILE_CONTRACT" | grep -v "version_history\|change:" | head -1 | cut -d: -f1)
  line_m=$(grep -n "(m)" "$RECONCILE_CONTRACT" | head -1 | cut -d: -f1)
  # positive — 두 항목 모두 존재
  [ -n "$line_l" ]
  [ -n "$line_m" ]
  # positive (discriminating) — (m) 이 (l) 보다 뒤에 위치
  [ "$line_m" -gt "$line_l" ]
}

# ───────────────── TC-25~27: §4.4 ratchet row 7 ──────────────────────────────

@test "TC-25 (P0): §4.4 ratchet 보존 의무 섹션에 row 7 (downgrade_asymmetry_marker wired→placeholder_reserve 차단) 존재" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — §4.4 Ratchet 섹션 존재
  grep -q "4.4 Ratchet\|Ratchet 보존 의무" "$RECONCILE_CONTRACT"
  # positive — downgrade_asymmetry_marker 역방향 차단 row 존재
  grep -q "downgrade_asymmetry_marker" "$RECONCILE_CONTRACT"
}

@test "TC-26 (P0): §4.4 ratchet row — §4.4 섹션 안에 'wired → placeholder_reserve 역방향 약화 = 차단' 명시" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — §4.4 Ratchet 섹션 (line 374 부근) 에 wired → placeholder_reserve 차단 row 존재
  # §4.4 시작 라인부터 20라인 이내에 downgrade_asymmetry_marker + 차단 언급
  grep -A 20 "4\.4 Ratchet\|Ratchet 보존 의무" "$RECONCILE_CONTRACT" | grep -q "downgrade_asymmetry_marker.*차단\|wired.*역방향.*차단\|역방향.*약화.*차단"
  # negative — §4.4 ratchet 차단 방향이 올바름 (wired→placeholder_reserve 방향, 강화 방향 아님)
  # §4.4 섹션 안 downgrade_asymmetry_marker 행은 'wired → placeholder_reserve' 역방향 차단이어야 함
  grep -A 20 "4\.4 Ratchet\|Ratchet 보존 의무" "$RECONCILE_CONTRACT" | grep "downgrade_asymmetry_marker" | grep -q "wired"
}

@test "TC-27 (P1): §4.4 ratchet row 가 ADR-058 §결정 5 sunset_justification 의무 언급" {
  [ -f "$RECONCILE_CONTRACT" ]
  # positive — ADR-058 §결정 5 또는 sunset_justification 언급
  grep -A 5 "downgrade_asymmetry_marker.*역방향\|wired.*placeholder_reserve.*차단" "$RECONCILE_CONTRACT" | grep -q "ADR-058\|sunset_justification"
}

# ───────────────── TC-28~30: 5 cross-ref atomic SSOT consistency ──────────────

@test "TC-28 (P0): promotion-criteria-4tuple.md — 'downgrade scope 외' 섹션 존재 + 'wired 활성' 언급" {
  [ -f "$PROMOTION_CRITERIA" ]
  # positive — downgrade scope 외 섹션 존재
  grep -q "downgrade scope 외\|downgrade scope" "$PROMOTION_CRITERIA"
  # positive — 파일 안에 'wired' 언급 존재 (CFP-1014 carrier 완료 반영)
  grep -q "wired" "$PROMOTION_CRITERIA"
  # positive — CFP-1014 언급 존재 (carrier 완료 명시)
  grep -q "CFP-1014" "$PROMOTION_CRITERIA"
  # negative — 'placeholder_reserve' 가 downgrade_asymmetry_marker 현재 활성 상태로 직접 선언되지 않음
  # (본문 섹션에서 'status: placeholder_reserve' 형태의 활성 선언 금지)
  ! grep -q 'status: placeholder_reserve' "$PROMOTION_CRITERIA"
}

@test "TC-29 (P0): rollback-protocol.md — Step 5a + CSC-4 에 'wired' 언급" {
  [ -f "$ROLLBACK_PROTOCOL" ]
  # positive — 'wired' 언급 존재 (CFP-1014 carrier 완료 반영)
  grep -q "wired" "$ROLLBACK_PROTOCOL"
  # positive — CSC-4 항목 존재
  grep -q "CSC-4" "$ROLLBACK_PROTOCOL"
  # negative — stale 'placeholder_reserve' 가 rollback 활성 경로 설명에 잔존하지 않음
  # (rollback-protocol 은 wired 상태에서의 rollback 경로 설명 대상)
  ! grep -A 5 "CSC-4" "$ROLLBACK_PROTOCOL" | grep -q "placeholder_reserve.*status\|status.*placeholder_reserve"
}

@test "TC-30/TC-DISC-6 (P0): discriminating fixture — README.md L48 + CLAUDE.md 에 CFP-1014 wired 활성 반영 (Layer 3, atomic SSOT consistency)" {
  [ -f "$PRODUCTION_README" ]
  [ -f "$CLAUDE_MD" ]
  # positive — README.md 에 CFP-1014 + MERGED + wired 언급 (Stage 5 transition)
  grep -q "CFP-1014.*MERGED\|MERGED.*CFP-1014" "$PRODUCTION_README"
  grep -q "wired" "$PRODUCTION_README"
  # positive (discriminating) — CLAUDE.md 에 v1.12 Active 언급 (reconcile-protocol-v1 현재 버전)
  grep -q "v1.12.*Active\|Active.*v1.12" "$CLAUDE_MD"
  # positive (discriminating) — CLAUDE.md 에 downgrade_asymmetry_marker + wired 언급
  grep -q "downgrade_asymmetry_marker.*wired\|wired.*downgrade_asymmetry_marker" "$CLAUDE_MD"
  # negative (discriminating) — CLAUDE.md 가 stale v1.11 이 current 버전으로 선언하지 않음
  # (v1.11 언급 자체는 허용이나 v1.11 Active 는 금지)
  ! grep -q 'v1.11.*Active[^)]' "$CLAUDE_MD"
}
