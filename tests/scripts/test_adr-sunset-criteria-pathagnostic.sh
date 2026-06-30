#!/usr/bin/env bash
# tests/scripts/test_adr-sunset-criteria-pathagnostic.sh
# CFP-2515 / 설계 §8 Test Contract — ADR sunset-criteria workflow dead-gate 회귀 검증.
# AC 매핑: AC-4(byte-identical parity) / AC-5(RESERVATION 면제 보존) / AC-6(layer 등가) / AC-7(mutation-kill)
#
# anti-theater: always-pass·tautology 0 — mutation 시 RED 전환되는 load-bearing assert만.
# symmetric sed trap 회피 (CFP-2491 #2514 선례): diff -q no-op guard 로 sed 미반영 케이스를
# FAIL 처리 — "SURVIVED" 판정이 vacuous 통과 되지 않도록.
#
# set -e 미사용 — 각 test || true 로 partial run 허용, FAIL 카운터 집계 후 exit code 결정.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GITHUB_WF="$REPO_ROOT/.github/workflows/adr-sunset-criteria.yml"
TEMPLATES_WF="$REPO_ROOT/templates/github-workflows/adr-sunset-criteria.yml"

PASS=0
FAIL=0

# ─── AC-7 + AC-4 + AC-6: dead-gate path-agnostic 양-컨텍스트 검증 ─────────────
# §8.1 test 1: 양 copy 가 alternation regex (docs|archive) 를 detect grep 으로 보유,
# on.paths 에 archive/adr 엔트리 포함, byte-identical parity, 실 매치(wrapper+consumer) 둘 다 non-dead.
test_ac7_deadgate_pathagnostic() {
  local test_name="AC-7-deadgate-path-agnostic"

  # (1) 양 copy 의 detect grep 이 path-agnostic alternation 보유 여부
  # 파일 내 리터럴 텍스트 "^(docs|archive)/adr/ADR-" 를 고정문자열로 검색
  local gh_pa tmpl_pa
  gh_pa=$(grep -cF "^(docs|archive)/adr/ADR-" "$GITHUB_WF" 2>/dev/null) || gh_pa=0
  tmpl_pa=$(grep -cF "^(docs|archive)/adr/ADR-" "$TEMPLATES_WF" 2>/dev/null) || tmpl_pa=0

  # (2) on.paths 에 archive/adr/ADR-*.md 엔트리 보유 여부 (AC-7 트리거 경로)
  local gh_paths tmpl_paths
  gh_paths=$(grep -cF "archive/adr/ADR-*.md" "$GITHUB_WF" 2>/dev/null) || gh_paths=0
  tmpl_paths=$(grep -cF "archive/adr/ADR-*.md" "$TEMPLATES_WF" 2>/dev/null) || tmpl_paths=0

  # (3) byte-identical parity (AC-4)
  local identical=0
  diff -q "$GITHUB_WF" "$TEMPLATES_WF" >/dev/null 2>&1 && identical=1

  # (4) 실 매치 검증 — wrapper archive/adr + consumer docs/adr 양 컨텍스트 non-dead (AC-6)
  local w_match=0 c_match=0
  printf 'archive/adr/ADR-130.md\n' | grep -qE '^(docs|archive)/adr/ADR-.*\.md$' && w_match=1
  printf 'docs/adr/ADR-130.md\n'    | grep -qE '^(docs|archive)/adr/ADR-.*\.md$' && c_match=1

  if [ "$gh_pa"    -ge 1 ] && \
     [ "$tmpl_pa"  -ge 1 ] && \
     [ "$gh_paths" -ge 1 ] && \
     [ "$tmpl_paths" -ge 1 ] && \
     [ "$identical" -eq 1 ] && \
     [ "$w_match"  -eq 1 ] && \
     [ "$c_match"  -eq 1 ]; then
    echo "PASS: $test_name -- path-agnostic(docs|archive) 양 copy byte-identical + on.paths archive 엔트리 + wrapper/consumer 양 컨텍스트 매치 (dead-gate non-dead + parity)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $test_name -- gh_pa=$gh_pa tmpl_pa=$tmpl_pa gh_paths=$gh_paths tmpl_paths=$tmpl_paths identical=$identical w_match=$w_match c_match=$c_match (기대 ≥1/≥1/≥1/≥1/1/1/1)"
    FAIL=$((FAIL+1))
  fi
}

# ─── AC-7 mutation-kill: docs-only 변환 시 archive 미검출 RED ────────────────
# §8.1 test 2: .github workflow copy 를 mktemp 로 격리 후 (docs|archive) → docs 로 변환.
# diff -q no-op guard (symmetric trap 회피 — CFP-2491 #2514 선례)
# archive 경로가 변환 후 grep 에서 0 이면 mutant KILLED.
test_m5_deadgate_mutant() {
  local mutant_name="m5-deadgate-singlepath"
  local mdir mutated arc_orig arc_mutant
  mdir="$(mktemp -d)"
  mutated="$mdir/wf.yml"
  cp "$GITHUB_WF" "$mutated"

  # baseline: archive 경로가 현재 regex 에 매치 (1 기대)
  arc_orig=$(printf 'archive/adr/ADR-130.md\n' | grep -cE '^(docs|archive)/adr/ADR-.*\.md$') || arc_orig=0

  # mutation: (docs|archive)/adr → docs/adr (archive 분기 제거)
  sed -i 's#(docs|archive)/adr#docs/adr#g' "$mutated"

  # no-op guard: sed 가 실제로 소스를 바꿨는지 확인 (symmetric trap 차단)
  if diff -q "$GITHUB_WF" "$mutated" >/dev/null 2>&1; then
    echo "FAIL: $mutant_name -- sed no-op (소스 무변경 — mutant 정의 오류, diff 동일)"
    FAIL=$((FAIL+1))
    rm -rf "$mdir"
    return 1
  fi

  # mutant 적용 후: archive 경로가 docs-only regex 에 미매치 (0 기대)
  arc_mutant=$(printf 'archive/adr/ADR-130.md\n' | grep -cE '^docs/adr/ADR-.*\.md$') || arc_mutant=0

  rm -rf "$mdir"

  if [ "$arc_orig" -eq 1 ] && [ "$arc_mutant" -eq 0 ]; then
    echo "PASS: $mutant_name -- mutant KILLED (docs-only 변환 후 archive 미매치 = wrapper dead-gate RED 재도입 검출)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $mutant_name -- mutant SURVIVED (arc_orig=$arc_orig arc_mutant=$arc_mutant, 기대 1/0)"
    FAIL=$((FAIL+1))
  fi
}

# ─── AC-5 회귀: ADR-RESERVATION 면제 grep -v 보존 확인 ──────────────────────
# §8.1 test 3: 양 copy 가 L43 의 substring grep -v 'ADR-RESERVATION.md' 를 여전히 보유,
# 양 path(archive/ + docs/) 에서 면제(빈 출력) 동작.
test_ac5_reservation_exempt() {
  local test_name="AC-5-reservation-exempt"

  # (1) 양 copy 가 grep -v 'ADR-RESERVATION.md' substring 보유 여부
  local gh_exemption tmpl_exemption
  gh_exemption=$(grep -cF "grep -v 'ADR-RESERVATION.md'" "$GITHUB_WF" 2>/dev/null) || gh_exemption=0
  tmpl_exemption=$(grep -cF "grep -v 'ADR-RESERVATION.md'" "$TEMPLATES_WF" 2>/dev/null) || tmpl_exemption=0

  # (2) 실 동작: archive + docs 양 path 가 grep -v 로 필터링돼 빈 출력
  local arc_out doc_out
  arc_out=$(printf 'archive/adr/ADR-RESERVATION.md\n' | grep -v 'ADR-RESERVATION.md') || true
  doc_out=$(printf 'docs/adr/ADR-RESERVATION.md\n'    | grep -v 'ADR-RESERVATION.md') || true

  # 빈 출력 = 면제 성공
  local arc_exempt=0 doc_exempt=0
  [ -z "$arc_out" ] && arc_exempt=1
  [ -z "$doc_out" ] && doc_exempt=1

  if [ "$gh_exemption"   -ge 1 ] && \
     [ "$tmpl_exemption" -ge 1 ] && \
     [ "$arc_exempt"     -eq 1 ] && \
     [ "$doc_exempt"     -eq 1 ]; then
    echo "PASS: $test_name -- 양 copy grep -v 면제 보존 + archive/docs 양 path 면제 동작"
    PASS=$((PASS+1))
  else
    echo "FAIL: $test_name -- gh_exemption=$gh_exemption tmpl_exemption=$tmpl_exemption arc_exempt=$arc_exempt doc_exempt=$doc_exempt (기대 ≥1/≥1/1/1)"
    FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "CFP-2515 Phase 2 QADev: ADR sunset-criteria dead-gate path-agnostic 회귀 검증"
echo "AC-4(parity) / AC-5(RESERVATION 면제) / AC-6(layer 등가) / AC-7(mutation-kill)"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

test_ac7_deadgate_pathagnostic || true
echo ""
test_m5_deadgate_mutant || true
echo ""
test_ac5_reservation_exempt || true

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Test Results: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests PASSED"
  exit 0
else
  echo "Some tests FAILED"
  exit 1
fi
