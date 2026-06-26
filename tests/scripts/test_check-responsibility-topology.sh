#!/usr/bin/env bash
# tests/scripts/test_check-responsibility-topology.sh
# CFP-2422 Phase 2 (Epic CFP-2418 Story 2) — Discriminating self-test for check-responsibility-topology.sh
#
# ADR-131 §결정 3/4 — cross-repo 책임 배치 메타불변식 게이트의 discriminating fixture (change-plan
# §8.1 SSOT). 각 fixture 는 mktemp fixture-root 안에 consumer overlay project.yaml(repo_topology
# 섹션) 를 의도적으로 구성 후 wrapper 를 --root(+ --changed-repos sentinel)로 가리켜 exit code
# (PASS→0 / 위반→1 / setup→2) + honest-classification 마커 일치를 assert.
#
# self-contained bash (bats 미사용 — CFP-2412 test-check-whitelist-manifest-3way.sh 답습).
# run_fixture(exit-code assert) + run_fixture_marker(exit-code + stdout 마커 assert) 헬퍼.
#
# fail-open discriminating 의무 (change-plan §8.2 AC-10): F-failopen 을 단순 "exit 0 = PASS" 로 검사 =
#   non-discriminating (정상 GREEN 과 fail-open 구분 불가) ⇒ 금지. honest-classification ::notice:: 마커
#   assert 의무 (exit-code-only assert 금지). F0-valid 의 PASS 마커 ≠ fail-open notice 마커 구분.
#
# Mutation testing 1:1 주석표 (change-plan §8.2 — 서로 다른 sub-fixture set RED 의무):
#  - Mutation-orphan   ((a)고아 빈리스트 exit1 분기 제거)          → F-orphan-empty PASS 면 RED
#  - Mutation-dup      ((b)중복소유 N≥2 분기 제거)                 → F-dup PASS 면 RED
#  - Mutation-dup-norm (정규화(set dedup) 제거 = 동일레포 2회→중복) → F-dup-same-owner-ok FAIL 면 RED
#  - Mutation-drift-1  (거친파생 declared\actual 단방향만)         → F-drift-declared PASS 면 RED
#  - Mutation-drift-2  (거친파생 actual\declared 단방향만)         → F-drift-actual PASS 면 RED
#  - Mutation-FO       (fail-open exit0 → exit1 강제)              → F-failopen-a/b/c FAIL 면 RED (layer 분리 falsify)
#                       + F0-valid 는 GREEN 유지 (fail-open 마커 ≠ 정상 마커 = Mutation-FO 무영향, 두 set 분리)
#  - Mutation-EMPTY    (빈맵 → 스키마 무효 exit2 처리)             → F-failopen-c exit2 나면 RED
#  - Mutation-SS1      (SS-1 경계 mutate: 키부재 exit2 → exit1)    → SS-1a exit1 나면 RED (키부재≠빈리스트)
#  - Mutation-schema   (linked_artifact ≥1 / rationale 필수 제거)  → SS-2/SS-3 exit≠2 면 RED
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates lint)
#  1 = any fixture fails (lint may not be detecting mutations correctly)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-responsibility-topology.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# overlay builder — consumer overlay project.yaml(repo_topology 섹션) 작성 헬퍼.
#   write_overlay <root> <heredoc-body-via-stdin>
# ─────────────────────────────────────────────────────────────────────────────
write_overlay() {
  local root="$1"
  mkdir -p "$root/.claude/_overlay"
  cat > "$root/.claude/_overlay/project.yaml"
}

# ─────────────────────────────────────────────────────────────────────────────
# run_fixture: wrapper --root [--changed-repos ...] → assert exit code only
#   $1=name $2=expected_exit $3=description $4=root $5=changed-repos(optional)
# ─────────────────────────────────────────────────────────────────────────────
run_fixture() {
  local name="$1" expected_exit="$2" description="$3" root="$4" changed="${5:-}"
  local out exit_code=0
  if [ -n "$changed" ]; then
    out=$( bash "$WRAPPER" --root "$root" --changed-repos "$changed" 2>&1 ) || exit_code=$?
  else
    out=$( bash "$WRAPPER" --root "$root" 2>&1 ) || exit_code=$?
  fi
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
#   $1=name $2=expected_exit $3=expected_marker $4=description $5=root $6=changed-repos(optional)
# ─────────────────────────────────────────────────────────────────────────────
run_fixture_marker() {
  local name="$1" expected_exit="$2" marker="$3" description="$4" root="$5" changed="${6:-}"
  local out exit_code=0
  if [ -n "$changed" ]; then
    out=$( bash "$WRAPPER" --root "$root" --changed-repos "$changed" 2>&1 ) || exit_code=$?
  else
    out=$( bash "$WRAPPER" --root "$root" 2>&1 ) || exit_code=$?
  fi
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
# F0-valid: applicable:true + 유효·위반0 맵 → PASS(0) + 정상 통과 마커 (대조 GREEN baseline)
#   정상 마커 = "메타불변식 OK" ≠ fail-open notice → non-discriminating 차단 (change-plan §8.1 F0-valid)
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/mctrader-engine
      rationale: 도메인 귀속 — 리스크 지표 계산 엔진
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "F0-valid" "0" "메타불변식 OK" "applicable:true 유효 맵 정상 통과 (정상 마커 ≠ fail-open 마커)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-orphan-empty (SS-1b 경계): owner_repo 키 well-formed + 빈 리스트(0 entry) → exit 1 (고아)
#   kill Mutation-orphan. exit2(키부재=SS-1a) 아님 — disjoint falsify.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: orphan-resp
      owner_repo: []
      rationale: 주인없는 책임 — 빈 리스트
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "F-orphan-empty" "1" "(a)고아" "owner_repo 빈 리스트 = 고아 exit1 (SS-1b — 키부재 exit2 와 disjoint)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-dup: 동일 responsibility 가 N≥2 owner_repo → exit 1 (중복소유)
#   kill Mutation-dup.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: dual-owned
      owner_repo:
        - mclayer/repo-a
        - mclayer/repo-b
      rationale: 중복소유 — 두 레포
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "F-dup" "1" "(b)중복소유" "동일 책임 N=2 owner_repo = 중복소유 exit1 (책임명+충돌레포 출력)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-dup-same-owner-ok (negative): 동일 책임·동일 레포 2회 선언 → exit 0 (정규화 후 단일소유 PASS)
#   kill Mutation-dup-norm (정규화 제거 시 동일레포 2회 → 중복소유 오판 FAIL=RED).
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: same-owner-twice
      owner_repo:
        - mclayer/repo-a
        - mclayer/repo-a
      rationale: 동일레포 2회 선언 = 중복선언 ≠ 중복소유
      linked_artifact:
        - CFP-2418
EOF
run_fixture "F-dup-same-owner-ok" "0" "동일레포 2회 선언 = 정규화 후 단일소유 PASS (중복선언 ≠ 중복소유)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-drift-declared: declared 에만 있고 actual 에 없는 레포 → exit 1 (거친파생 declared\actual)
#   kill Mutation-drift-1 (declared\actual 단방향 검사 제거 시 PASS=RED).
#   declared = {repo-a, repo-b} / actual = {repo-a} → declared\actual = {repo-b} 비어있지 않음.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: resp-a
      owner_repo: mclayer/repo-a
      rationale: a
      linked_artifact:
        - CFP-2418
    - responsibility: resp-b
      owner_repo: mclayer/repo-b
      rationale: b
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "F-drift-declared" "1" "(c)거친파생" "declared {repo-a,repo-b} ≠ actual {repo-a} = declared\\actual 비어있지않음 (양방향 차집합 declared-side)" "$R" "mclayer/repo-a"

# ═════════════════════════════════════════════════════════════════════════════
# F-drift-actual: actual 에만 있고 declared 에 없는 레포 → exit 1 (거친파생 actual\declared)
#   kill Mutation-drift-2 (actual\declared 단방향 검사 제거 시 PASS=RED).
#   declared = {repo-a} / actual = {repo-a, repo-c} → actual\declared = {repo-c} 비어있지 않음.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: resp-a
      owner_repo: mclayer/repo-a
      rationale: a
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "F-drift-actual" "1" "(c)거친파생" "declared {repo-a} ≠ actual {repo-a,repo-c} = actual\\declared 비어있지않음 (양방향 차집합 actual-side)" "$R" "mclayer/repo-a,mclayer/repo-c"

# ═════════════════════════════════════════════════════════════════════════════
# F-drift-match-ok (negative): declared == actual → exit 0 (집합 일치 PASS)
#   거친파생 검사가 일치 시 false-FAIL 안 하는지 (over-strict mutation 검출).
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: resp-a
      owner_repo: mclayer/repo-a
      rationale: a
      linked_artifact:
        - CFP-2418
    - responsibility: resp-b
      owner_repo: mclayer/repo-b
      rationale: b
      linked_artifact:
        - CFP-2418
EOF
run_fixture "F-drift-match-ok" "0" "declared {repo-a,repo-b} == actual {repo-a,repo-b} 집합 일치 PASS" "$R" "mclayer/repo-a,mclayer/repo-b"

# ═════════════════════════════════════════════════════════════════════════════
# F-failopen-a: repo_topology 섹션 미주입 → exit 0 + honest-classification ::notice:: 마커
#   kill Mutation-FO (fail-open exit0 → exit1 강제 시 FAIL=RED). exit-code-only assert 금지 (AC-10).
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
some_other_section:
  foo: bar
EOF
run_fixture_marker "F-failopen-a" "0" "repo_topology 섹션 미주입" "repo_topology 미주입 = fail-open exit0 + honest notice (exit-code-only 금지)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-failopen-b: applicable:false → exit 0 + honest notice
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: false
  responsibilities:
    - responsibility: ignored-when-not-applicable
      owner_repo: []
      rationale: applicable:false 면 검사 비대상
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "F-failopen-b" "0" "applicable != true" "applicable:false = fail-open exit0 + honest notice (빈 owner 있어도 opt-in 미활성이라 비검사)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-failopen-c: applicable:true + responsibilities 빈 맵 → exit 0 + honest notice
#   kill Mutation-EMPTY (빈맵 → 스키마 무효 exit2 처리 시 exit2=RED).
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities: []
EOF
run_fixture_marker "F-failopen-c" "0" "responsibilities 빈 맵" "applicable:true + 빈 맵 = 스키마 유효성만·정책 공백 PASS exit0 (스키마 무효 exit2 아님)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# SS-1a (키 부재): owner_repo 키 부재 → exit 2 (스키마 무효 SETUP)
#   kill Mutation-SS1 (SS-1 경계 mutate: 키부재를 exit1 처리 시 RED). SS-1b(빈리스트=exit1)와 disjoint.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: missing-owner-key
      rationale: owner_repo 키 자체 부재 = 스키마 무효
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "SS-1a-key-absent" "2" "SS-1a" "owner_repo 키 부재 = 스키마 무효 exit2 (키존재+빈리스트=SS-1b exit1 와 disjoint)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# SS-2 (linked_artifact 0개): → exit 2 (≥1 필수 위반 = 스키마 무효)
#   kill Mutation-schema (linked_artifact ≥1 검사 제거 시 exit≠2=RED).
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: no-linked-artifact
      owner_repo: mclayer/repo-a
      rationale: linked_artifact 0개
      linked_artifact: []
EOF
run_fixture_marker "SS-2-linked-artifact-empty" "2" "SS-2" "linked_artifact 0개 = ≥1 필수 위반 스키마 무효 exit2" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# SS-3 (rationale 결손): → exit 2 (필수필드 결손)
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: no-rationale
      owner_repo: mclayer/repo-a
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "SS-3-rationale-absent" "2" "SS-3" "rationale 키 부재 = 필수필드 결손 스키마 무효 exit2" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# SS-4 (malformed yaml): yaml.safe_load 파싱 실패 → exit 2
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: bad
     owner_repo: [unclosed
EOF
run_fixture_marker "SS-4-malformed-yaml" "2" "SS-4" "malformed yaml = yaml.safe_load 파싱 실패 exit2" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# SS-1a-malformed-type (owner_repo 비-string·비-list 타입): → exit 2
#   owner_repo: 42 (int) = malformed = SS-1a exit2 (키존재+빈리스트 SS-1b exit1 과 disjoint)
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: malformed-owner-type
      owner_repo: 42
      rationale: owner_repo 가 int = malformed
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "SS-1a-malformed-type" "2" "SS-1a" "owner_repo int 타입 = malformed 스키마 무효 exit2" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-data-absence-overlay: consumer overlay 파일 자체 부재 → exit 0 + honest notice
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)  # overlay 미작성
run_fixture_marker "F-data-absence-overlay" "0" "consumer overlay project.yaml 부재" "overlay 파일 부재 = data-absence fail-open exit0 + honest notice" "$R"

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2422 responsibility-topology)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (change-plan §8.2 — 서로 다른 sub-fixture set RED 의무):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "Mutation-orphan   ((a)고아 빈리스트 exit1 제거)          → F-orphan-empty PASS 면 RED"
  echo "Mutation-dup      ((b)중복소유 N≥2 제거)                 → F-dup PASS 면 RED"
  echo "Mutation-dup-norm (정규화 set dedup 제거)                → F-dup-same-owner-ok FAIL 면 RED"
  echo "Mutation-drift-1  (거친파생 declared\\actual 단방향 제거) → F-drift-declared PASS 면 RED"
  echo "Mutation-drift-2  (거친파생 actual\\declared 단방향 제거) → F-drift-actual PASS 면 RED"
  echo "Mutation-FO       (fail-open exit0 → exit1 강제)         → F-failopen-a/b/c FAIL 면 RED"
  echo "                   (+ F0-valid GREEN 유지 = fail-open 마커 ≠ 정상 마커, 두 set 분리)"
  echo "Mutation-EMPTY    (빈맵 → 스키마 무효 exit2 처리)        → F-failopen-c exit2 나면 RED"
  echo "Mutation-SS1      (SS-1 경계 키부재 exit2 → exit1)       → SS-1a exit1 나면 RED"
  echo "Mutation-schema   (linked_artifact ≥1 / rationale 필수 제거) → SS-2/SS-3 exit≠2 면 RED"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
