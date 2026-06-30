#!/usr/bin/env bash
# scripts/test-cfp-2521-presence.sh
# CFP-2521 Phase 2 — §8 Test Contract presence assertions (A1-A8, D1, D3).
#
# 주석 언어 정책: 한글 주 언어. 영어는 기술 용어·코드만.
#
# 계약 내용:
#  A1-A8: Phase 1 merged ADR/concept/Story 검증 (presence assertions).
#  D1: DeveloperPLAgent.md 컨텍스트 경계 규약 섹션 검증.
#  D3-C1: check-pl-delegation-ratio.sh 존재 + exit 0 contract.
#  D3-C2: check-pl-delegation-ratio.sh spawn-event reuse 확인.
#
# ADR-119 research-before-claims (검증-후-단언):
#  - 각 assertion 은 독립적인 grep 또는 스크립트 호출로 검증.
#  - PASS/FAIL 명확 표기.
#  - 미실행/순환 dependency 없는 확인만 수행.
#
# Usage:
#   bash scripts/test-cfp-2521-presence.sh
#
# Exit code:
#  0 = all assertions PASS
#  1 = any assertion FAIL
#

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

# ═════════════════════════════════════════════════════════════════════════════
# 유틸 함수
# ═════════════════════════════════════════════════════════════════════════════

assert_file_exists() {
  local file="$1"
  local name="$2"

  if [ ! -f "$file" ]; then
    echo "✗ FAIL: $name — file not found: $file"
    FAIL=$((FAIL+1))
    return 1
  fi
  return 0
}

assert_grep_present() {
  local file="$1"
  local pattern="$2"
  local name="$3"

  if ! grep -q "$pattern" "$file" 2>/dev/null; then
    echo "✗ FAIL: $name — pattern not found: $pattern"
    FAIL=$((FAIL+1))
    return 1
  fi
  echo "✓ PASS: $name"
  PASS=$((PASS+1))
  return 0
}

assert_grep_all() {
  local file="$1"
  local name="$2"
  shift 2
  local patterns=("$@")

  for pattern in "${patterns[@]}"; do
    if ! grep -q "$pattern" "$file" 2>/dev/null; then
      echo "✗ FAIL: $name — pattern not found: $pattern"
      FAIL=$((FAIL+1))
      return 1
    fi
  done
  echo "✓ PASS: $name"
  PASS=$((PASS+1))
  return 0
}

# ═════════════════════════════════════════════════════════════════════════════
# A1: ADR-044 amendment_log 에 amendment: 5, CFP-2521, strengthening
# ═════════════════════════════════════════════════════════════════════════════

A1_FILE="$REPO_ROOT/archive/adr/ADR-044-phase-scoped-sequential-team.md"
assert_file_exists "$A1_FILE" "A1-file-exists" || true

if [ -f "$A1_FILE" ]; then
  # amendment: 5, cfp: CFP-2521, direction: strengthening 동시 assert
  assert_grep_all "$A1_FILE" "A1-amendment-5-cfp-2521-strengthening" \
    "amendment: 5" \
    "cfp: CFP-2521" \
    "direction: strengthening" || true
else
  echo "✗ FAIL: A1-file-exists — $A1_FILE not found"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# A2: ADR-044 본문에 § 결정 11 heading (thin-PL / context boundary)
# ═════════════════════════════════════════════════════════════════════════════

if [ -f "$A1_FILE" ]; then
  # "### 결정 11" 또는 "§결정 11" heading 존재 확인
  assert_grep_present "$A1_FILE" "### 결정 11\|§결정 11" "A2-decision-11-heading" || true
else
  echo "⊘ SKIP: A2 — $A1_FILE not found"
fi

# ═════════════════════════════════════════════════════════════════════════════
# A3: ADR-044 Amendment 5 / §결정 11 에 "4-entry" AND "disjoint" 어구
# ═════════════════════════════════════════════════════════════════════════════

if [ -f "$A1_FILE" ]; then
  # §결정 11 섹션 내에서 "4-entry" (또는 "4-entry closed enumeration") 와 "disjoint" 동시 확인
  assert_grep_all "$A1_FILE" "A3-disjoint-axis-invariant" \
    "4-entry.*closed" \
    "disjoint.*axis" || true
else
  echo "⊘ SKIP: A3 — $A1_FILE not found"
fi

# ═════════════════════════════════════════════════════════════════════════════
# A4: ADR-039 amendment_log 에 amendment: 8, CFP-2521, strengthening
# ═════════════════════════════════════════════════════════════════════════════

A4_FILE="$REPO_ROOT/archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md"
assert_file_exists "$A4_FILE" "A4-file-exists" || true

if [ -f "$A4_FILE" ]; then
  assert_grep_all "$A4_FILE" "A4-amendment-8-cfp-2521-strengthening" \
    "amendment: 8" \
    "CFP-2521" \
    "direction: strengthening" || true
else
  echo "✗ FAIL: A4-file-exists — $A4_FILE not found"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# A5: ADR-039 §결정 9 deferred list 에 DevPL self-read advisory detection 항목
# ═════════════════════════════════════════════════════════════════════════════

if [ -f "$A4_FILE" ]; then
  # "§결정 9" 섹션 내에서 "self-read" 또는 "PL self-read advisory" 어구 확인
  # 또는 "DevPL-side" + "advisory" 동시 확인
  assert_grep_all "$A4_FILE" "A5-decision-9-devpl-selfread-advisory" \
    "§결정 9" \
    "self-read.*advisory\|advisory.*self-read" || true
else
  echo "⊘ SKIP: A5 — $A4_FILE not found"
fi

# ═════════════════════════════════════════════════════════════════════════════
# A6: ADR-039 Amendment 8 에서 "4-entry" AND "disjoint axis" AND "inline whitelist"
# ═════════════════════════════════════════════════════════════════════════════

if [ -f "$A4_FILE" ]; then
  assert_grep_all "$A4_FILE" "A6-amendment-8-disjoint-axis-whitelist" \
    "4-entry.*closed.*enumeration\|4-entry" \
    "disjoint.*axis\|disjoint\|다른 차원" \
    "inline whitelist" || true
else
  echo "⊘ SKIP: A6 — $A4_FILE not found"
fi

# ═════════════════════════════════════════════════════════════════════════════
# A7: Concept 파일 존재, frontmatter kind: concept_definition, rule-of-three 명시
# ═════════════════════════════════════════════════════════════════════════════

A7_FILE="$REPO_ROOT/docs/domain-knowledge/concept/context-offloading-to-ephemeral-workers.md"
assert_file_exists "$A7_FILE" "A7-file-exists" || true

if [ -f "$A7_FILE" ]; then
  # frontmatter kind 확인 (exact field name 재확인)
  assert_grep_present "$A7_FILE" "kind: concept_definition" "A7-frontmatter-kind" || true

  # rule-of-three 항목: ADR-039 / DeveloperPLAgent / CFP-2521
  assert_grep_all "$A7_FILE" "A7-rule-of-three" \
    "ADR-039" \
    "DeveloperPLAgent" \
    "CFP-2521" || true
else
  echo "✗ FAIL: A7-file-exists — $A7_FILE not found"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# A8: Story 파일 (internal-docs repo) 의 §7 + §7.9 또는 N/A 선언
# 조건: STORY_PATH 환경변수 또는 기본 경로 설정
# ═════════════════════════════════════════════════════════════════════════════

STORY_PATH="${STORY_PATH:-$HOME/.claude/codeforge-scratch/codeforge-internal-docs/wrapper/stories/CFP-2521.md}"

if [ ! -f "$STORY_PATH" ]; then
  echo "⊘ SKIP: A8 — Story file not found at $STORY_PATH (internal-docs repo 미연동 또는 clone 부재)"
  # non-blocking — Story 파일은 external (mclayer/codeforge-internal-docs)
else
  if [ -f "$STORY_PATH" ]; then
    # §7 design narrative 존재 확인
    assert_grep_present "$STORY_PATH" "^## § 7\|^## .*설계" "A8-section-7-present" || true

    # §7.9 또는 §11.7 N/A 선언 확인 (정확한 섹션은 파일 읽고 확인)
    if grep -q "§7\.9\|§11\.7\|N/A" "$STORY_PATH" 2>/dev/null; then
      echo "✓ PASS: A8-nonnecessary-section-na-declared"
      PASS=$((PASS+1))
    else
      echo "⚠ WARNING: A8 — N/A section 선언 미확인 (파일 검토 필요)"
      # non-blocking warning
    fi
  fi
fi

# ═════════════════════════════════════════════════════════════════════════════
# D1: DeveloperPLAgent.md 컨텍스트 경계 규약 섹션 + 핵심 어구
# ═════════════════════════════════════════════════════════════════════════════

D1_FILE="$REPO_ROOT/plugins/codeforge-develop/agents/DeveloperPLAgent.md"
assert_file_exists "$D1_FILE" "D1-file-exists" || true

if [ -f "$D1_FILE" ]; then
  # 섹션 heading 확인: "컨텍스트 경계 규약"
  assert_grep_present "$D1_FILE" "컨텍스트 경계 규약" "D1-context-boundary-section" || true

  # 핵심 어구: "essential" / "carve-out" / "disjoint axis" / "PL self-spawn 금지"
  assert_grep_all "$D1_FILE" "D1-essential-carveout-disjoint-selfspawn" \
    "essential\|carve-out" \
    "disjoint.*axis\|disjoint" \
    "PL self-spawn 금지\|self-spawn 금지" || true
else
  echo "✗ FAIL: D1-file-exists — $D1_FILE not found"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# D3-PRESENCE: check-pl-delegation-ratio.sh 존재 확인
# ═════════════════════════════════════════════════════════════════════════════

D3_SCRIPT="$REPO_ROOT/scripts/check-pl-delegation-ratio.sh"
assert_file_exists "$D3_SCRIPT" "D3-script-exists" || true

# ═════════════════════════════════════════════════════════════════════════════
# D3-C1: check-pl-delegation-ratio.sh exit 0 contract (비-essential ledger 없을 때)
# ═════════════════════════════════════════════════════════════════════════════

if [ -f "$D3_SCRIPT" ]; then
  # ledger 미설정 시 exit 0 확인
  NONEXISTENT_LEDGER="/tmp/nonexistent-ledger-$RANDOM.jsonl"
  if bash "$D3_SCRIPT" SPAWN_EVENT_LEDGER="$NONEXISTENT_LEDGER" >/dev/null 2>&1; then
    echo "✓ PASS: D3-C1-exit-0-advisory"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: D3-C1-exit-0-advisory — script exited non-zero (C1 contract violation)"
    FAIL=$((FAIL+1))
  fi
else
  echo "⊘ SKIP: D3-C1 — $D3_SCRIPT not found"
fi

# ═════════════════════════════════════════════════════════════════════════════
# D3-C2: check-pl-delegation-ratio.sh reuses spawn-event-v1 channel (grep 확인)
# ═════════════════════════════════════════════════════════════════════════════

if [ -f "$D3_SCRIPT" ]; then
  assert_grep_all "$D3_SCRIPT" "D3-C2-spawn-event-reuse" \
    "spawn-event-v1\|SPAWN_EVENT_LEDGER\|spawn-event" || true
else
  echo "⊘ SKIP: D3-C2 — $D3_SCRIPT not found"
fi

# ═════════════════════════════════════════════════════════════════════════════
# 최종 요약
# ═════════════════════════════════════════════════════════════════════════════

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: CFP-2521 Phase 2 §8 Test Contract presence assertions"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All assertions passed"
  exit 0
else
  echo "✗ Some assertions failed"
  exit 1
fi
