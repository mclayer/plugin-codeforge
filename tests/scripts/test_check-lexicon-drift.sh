#!/usr/bin/env bash
# tests/scripts/test_check-lexicon-drift.sh
# CFP-2453 Phase 2 (ADR-091 Amendment 3) — Discriminating self-test for check-lexicon-drift.sh
#
# consumer application-BC lexicon(용어 관계 사전) drift 게이트의 discriminating fixture
# (Change Plan §8.1/§8.2 SSOT). 각 fixture 는 mktemp fixture-root 안에 consumer lexicon.md
# (docs/domain-knowledge/domain/<area>/lexicon.md, frontmatter `kind: lexicon_relation`) 를
# 의도적으로 구성 후 wrapper 를 --root 로 가리켜 exit code (PASS→0 / drift→1 / setup→2) +
# honest-classification 마커 일치를 assert.
#
# archetype = tests/scripts/test_check-responsibility-marker-drift.sh (CFP-2428) 의 구조 verbatim clone.
# self-contained bash (bats 미사용). run_fixture(exit-code assert) + run_fixture_marker(exit-code +
# stdout 마커 grep -F assert) 헬퍼. fixture content 만 lexicon-specific.
#
# fail-open discriminating 의무 (Change Plan §8.4): F-failopen-absent 를 단순 "exit 0 = PASS" 로
#   검사 = non-discriminating (정상 GREEN 과 fail-open 구분 불가) ⇒ 금지. honest-classification
#   ::notice:: 마커("data-absence") assert 의무 (exit-code-only assert 금지). F0-valid 의 PASS
#   마커("lexicon drift OK") ≠ fail-open notice 마커("data-absence") 두 set 분리 = load-bearing
#   discriminating separation.
#
# Mutation testing 1:1 주석표 (Change Plan §8.2 — 서로 다른 sub-fixture set RED 의무):
#  - Mutation-collision (collision (a) 분기 제거)            → F-collision PASS 면 RED
#  - Mutation-cite      (citation-presence (b) 분기 제거)    → F-missing-cite PASS 면 RED
#  - Mutation-FO        (fail-open exit0 → exit1 강제)       → F-failopen-absent FAIL 면 RED
#                        (+ F0-valid GREEN 유지 = fail-open 마커 "data-absence" ≠ PASS 마커
#                           "lexicon drift OK", 두 set 분리)
#  - Mutation-setup     (setup exit2 → exit0)                → F-setup-* exit≠2 면 RED
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates lint)
#  1 = any fixture fails (lint may not be detecting mutations correctly)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-lexicon-drift.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# lexicon builder — consumer lexicon.md(frontmatter kind:lexicon_relation) 작성 헬퍼.
#   write_lexicon <root> <heredoc-body-via-stdin>
#   → <root>/docs/domain-knowledge/domain/vocabulary/lexicon.md 에 stdin 그대로 기록.
# ─────────────────────────────────────────────────────────────────────────────
write_lexicon() {
  local root="$1"
  mkdir -p "$root/docs/domain-knowledge/domain/vocabulary"
  cat > "$root/docs/domain-knowledge/domain/vocabulary/lexicon.md"
}

# ─────────────────────────────────────────────────────────────────────────────
# run_fixture: wrapper --root → assert exit code only
#   $1=name $2=expected_exit $3=description $4=root
# ─────────────────────────────────────────────────────────────────────────────
run_fixture() {
  local name="$1" expected_exit="$2" description="$3" root="$4"
  local out exit_code=0
  out=$( bash "$WRAPPER" --root "$root" 2>&1 ) || exit_code=$?
  if [ "$exit_code" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1)); rm -rf "$root"; return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1)); rm -rf "$root"; return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# run_fixture_marker: exit code + stdout 마커(grep -F) 동시 assert (fail-open discriminating)
#   $1=name $2=expected_exit $3=expected_marker $4=description $5=root
# ─────────────────────────────────────────────────────────────────────────────
run_fixture_marker() {
  local name="$1" expected_exit="$2" marker="$3" description="$4" root="$5"
  local out exit_code=0
  out=$( bash "$WRAPPER" --root "$root" 2>&1 ) || exit_code=$?
  local ok=1
  [ "$exit_code" -eq "$expected_exit" ] || ok=0
  echo "$out" | grep -qF "$marker" || ok=0
  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name (exit $exit_code, marker OK) — $description"
    PASS=$((PASS+1)); rm -rf "$root"; return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit (got $exit_code) AND marker '$marker'"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1)); rm -rf "$root"; return 1
  fi
}

set +e

# ═════════════════════════════════════════════════════════════════════════════
# F0-valid: collision 0 + homonym pair explicit-separate(같은 term 2-entry, 둘 다 relation:homonym +
#   상호 conflict_with) + 전수 usage_citations 보유 → PASS(0) + "lexicon drift OK" 마커
#   PASS 마커 = "lexicon drift OK" ≠ fail-open notice "data-absence" → non-discriminating 차단
#   (Change Plan §8.1 F0-valid). 정상 homonym 분리쌍은 collision 아님 + citation 보유라 (b) 미발동.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
write_lexicon "$R" <<'EOF'
---
kind: lexicon_relation
title: vocabulary lexicon
area: vocabulary
topic_slug: lexicon
status: active
updated: 2026-06-29
relations:
  - term: position
    relation: homonym
    conflict_with: position
    usage_citations:
      - "engine/src/risk/pos.py:10"
    definition: 보유 포지션(수량)
  - term: position
    relation: homonym
    conflict_with: position
    usage_citations:
      - "engine/src/ui/layout.py:42"
    definition: 화면 좌표 위치
---

# Vocabulary lexicon
EOF
run_fixture_marker "F0-valid" "0" "lexicon drift OK" "homonym explicit-separate 쌍 + 전수 citation = 정상 PASS (PASS 마커 ≠ fail-open 마커)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-collision (a): 같은 term 이 서로 다른 definition 으로 2 entry 출현하나 homonym explicit-separate
#   미선언(relation:synonym = homonym 아님) → exit 1 + "(a)collision-candidate"
#   kill Mutation-collision. collision (a) 분기 제거 시 PASS 나면 RED.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
write_lexicon "$R" <<'EOF'
---
kind: lexicon_relation
title: vocabulary lexicon
area: vocabulary
topic_slug: lexicon
status: active
updated: 2026-06-29
relations:
  - term: order
    relation: synonym
    definition: 주문(거래 지시)
  - term: order
    relation: synonym
    definition: 정렬 순서
---

# Vocabulary lexicon
EOF
run_fixture_marker "F-collision" "1" "(a)collision-candidate" "같은 표기 order 가 서로 다른 의미 2-entry, homonym explicit-separate 미선언 = collision-candidate exit1" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-missing-cite (b): relation:homonym entry 가 usage_citations 0건(키 부재) → exit 1 + "(b)citation-absent"
#   kill Mutation-cite. citation-presence (b) 분기 제거 시 PASS 나면 RED.
#   (collision (a) 미발동 보장 — homonym explicit-separate 구조라 (a) 비대상, (b) 단독 발동.)
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
write_lexicon "$R" <<'EOF'
---
kind: lexicon_relation
title: vocabulary lexicon
area: vocabulary
topic_slug: lexicon
status: active
updated: 2026-06-29
relations:
  - term: position
    relation: homonym
    conflict_with: position
    definition: 보유 포지션(수량)
  - term: position
    relation: homonym
    conflict_with: position
    usage_citations:
      - "engine/src/ui/layout.py:42"
    definition: 화면 좌표 위치
---

# Vocabulary lexicon
EOF
run_fixture_marker "F-missing-cite" "1" "(b)citation-absent" "homonym entry(position) usage_citations 키 부재 = citation-absent exit1 (presence-check only)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-failopen-absent: lexicon.md 1개도 부재(root 하위 미생성) → exit 0 + "data-absence" honest ::notice::
#   kill Mutation-FO (fail-open exit0 → exit1 강제 시 FAIL=RED). exit-code-only assert 금지 —
#   "data-absence" 마커로 assert(§8.4 load-bearing discriminating: fail-open ≠ valid-PASS).
#   F0-valid PASS 마커 "lexicon drift OK" ≠ 본 fail-open 마커 "data-absence" 두 set 분리.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)  # lexicon.md 미작성 = data-absence
run_fixture_marker "F-failopen-absent" "0" "data-absence" "lexicon.md 부재 = fail-open exit0 + honest ::notice:: data-absence (exit-code-only 금지, PASS 마커와 구분)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-setup-malformed: 깨진 yaml frontmatter(unclosed bracket) → exit 2 + "setup-error" (fail-closed)
#   kill Mutation-setup (setup exit2 → exit0 시 exit≠2=RED). yaml.safe_load 파싱 실패.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
write_lexicon "$R" <<'EOF'
---
kind: lexicon_relation
title: vocabulary lexicon
area: vocabulary
topic_slug: lexicon
status: active
updated: 2026-06-29
relations:
  - term: order
    relation: [unclosed
    definition: 주문
---

# Vocabulary lexicon
EOF
run_fixture_marker "F-setup-malformed" "2" "setup-error" "unclosed bracket = yaml.safe_load 파싱 실패 setup-error exit2 (fail-closed)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-setup-schema-enum: relations entry relation enum 위반(relation: foobar) → exit 2 + "setup-error"
#   kill Mutation-setup (setup exit2 → exit0 시 exit≠2=RED). 스키마 무효 fail-closed.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
write_lexicon "$R" <<'EOF'
---
kind: lexicon_relation
title: vocabulary lexicon
area: vocabulary
topic_slug: lexicon
status: active
updated: 2026-06-29
relations:
  - term: order
    relation: foobar
    definition: 주문
---

# Vocabulary lexicon
EOF
run_fixture_marker "F-setup-schema-enum" "2" "setup-error" "relation: foobar = enum 위반 스키마 무효 setup-error exit2 (허용: homonym/synonym/antonym)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-setup-schema-noterm: relations entry 필수 term 키 부재 → exit 2 + "setup-error"
#   kill Mutation-setup (setup exit2 → exit0 시 exit≠2=RED). 필수필드 부재 스키마 무효.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
write_lexicon "$R" <<'EOF'
---
kind: lexicon_relation
title: vocabulary lexicon
area: vocabulary
topic_slug: lexicon
status: active
updated: 2026-06-29
relations:
  - relation: synonym
    definition: term 키 없는 entry
---

# Vocabulary lexicon
EOF
run_fixture_marker "F-setup-schema-noterm" "2" "setup-error" "relations entry term 키 부재 = 필수필드 부재 스키마 무효 setup-error exit2" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-setup-schema-norelation: relations entry 필수 relation 키 부재 → exit 2 + "setup-error"
#   kill Mutation-setup (setup exit2 → exit0 시 exit≠2=RED). 필수필드 부재 스키마 무효.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
write_lexicon "$R" <<'EOF'
---
kind: lexicon_relation
title: vocabulary lexicon
area: vocabulary
topic_slug: lexicon
status: active
updated: 2026-06-29
relations:
  - term: order
    definition: relation 키 없는 entry
---

# Vocabulary lexicon
EOF
run_fixture_marker "F-setup-schema-norelation" "2" "setup-error" "relations entry relation 키 부재 = 필수필드 부재 스키마 무효 setup-error exit2" "$R"

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2453 lexicon-drift)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (Change Plan §8.2 — 서로 다른 sub-fixture set RED 의무):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "Mutation-collision (collision (a) 분기 제거)          → F-collision PASS 면 RED"
  echo "Mutation-cite      (citation-presence (b) 분기 제거)  → F-missing-cite PASS 면 RED"
  echo "Mutation-FO        (fail-open exit0 → exit1 강제)     → F-failopen-absent FAIL 면 RED"
  echo "                    (+ F0-valid GREEN 유지 = fail-open 마커 'data-absence' ≠ PASS 마커"
  echo "                       'lexicon drift OK', 두 set 분리 — §8.4 discriminating separation)"
  echo "Mutation-setup     (setup exit2 → exit0)              → F-setup-* exit≠2 면 RED"
  echo "                    (F-setup-malformed / F-setup-schema-enum / -noterm / -norelation)"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
