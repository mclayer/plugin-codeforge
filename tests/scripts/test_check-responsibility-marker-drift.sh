#!/usr/bin/env bash
# tests/scripts/test_check-responsibility-marker-drift.sh
# CFP-2428 Phase 2 (Epic CFP-2418 deferred FU) — Discriminating self-test for check-responsibility-marker-drift.sh
#
# ADR-131 Amendment 1 — declared-marker layer(L1 코드→책임) drift 게이트의 discriminating fixture
# (change-plan §8.1 SSOT). 각 fixture 는 mktemp fixture-root 안에 consumer overlay project.yaml
# (repo_topology.responsibility_markers 섹션) 를 의도적으로 구성 후 wrapper 를 --root 로 가리켜 exit code
# (PASS→0 / drift→1 / setup→2) + honest-classification 마커 일치를 assert.
#
# self-contained bash (bats 미사용 — CFP-2422 test_check-responsibility-topology.sh 답습).
# run_fixture(exit-code assert) + run_fixture_marker(exit-code + stdout 마커 assert) 헬퍼.
# stale(c) fixture 는 fs-stat 대상이라 fixture-root 안에 실재 파일 생성(존재) / 미생성(부재)로 falsify.
#
# fail-open discriminating 의무 (change-plan §8.4): F-failopen 을 단순 "exit 0 = PASS" 로 검사 =
#   non-discriminating (정상 GREEN 과 fail-open 구분 불가) ⇒ 금지. honest-classification ::notice:: 마커
#   assert 의무 (exit-code-only assert 금지). F0-valid 의 PASS 마커("drift OK") ≠ fail-open notice 마커 구분.
#
# Mutation testing 1:1 주석표 (change-plan §8.2 — 서로 다른 sub-fixture set RED 의무):
#  - Mutation-unmarked  (set-diff (a) 분기 제거)             → F-unmarked PASS 면 RED
#  - Mutation-mismatch  (문자열동등 (b) 분기 제거)           → F-mismatch PASS 면 RED
#  - Mutation-stale     (fs-stat (c) 분기 제거)              → F-stale PASS 면 RED
#  - Mutation-FO        (fail-open exit0 → exit1 강제)       → F-failopen-* FAIL 면 RED (+ F0-valid GREEN 유지 = 두 set 분리)
#  - Mutation-EMPTY     (빈맵 → 스키마 무효 exit2 처리)      → F-failopen-empty exit2 나면 RED
#  - Mutation-schema    (path/responsibility 필수 제거)      → F-malformed-* exit≠2 면 RED
#  - Mutation-reverse   (역방향 notice → warning 승격)       → F-reverse-orphan-notice exit1 나면 RED (micro-decision ③ 보존)
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates lint)
#  1 = any fixture fails (lint may not be detecting mutations correctly)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-responsibility-marker-drift.sh"

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

# stale(c) fixture 용 — fixture-root 안에 실재 파일 생성 (path 존재 = stale 아님).
make_path() {
  local root="$1" rel="$2"
  mkdir -p "$root/$(dirname "$rel")"
  : > "$root/$rel"
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
# F0-valid: applicable:true + 유효 marker(topology join-key 일치, path 실재) → PASS(0) + drift OK 마커
#   정상 마커 = "drift OK" ≠ fail-open notice → non-discriminating 차단 (change-plan §8.1 F0-valid)
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
make_path "$R" "engine/src/risk/calc.py"
write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/mctrader-engine
      rationale: 도메인 귀속 — 리스크 지표 계산 엔진
      linked_artifact:
        - CFP-2418
  responsibility_markers:
    - path: engine/src/risk/calc.py
      responsibility: risk-metrics
      repo: mclayer/mctrader-engine
EOF
run_fixture_marker "F0-valid" "0" "drift OK" "applicable:true 유효 marker 정상 통과 (정상 마커 ≠ fail-open 마커)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-unmarked (a): topology 에 R 선언, manifest 에 R entry 0 → exit 1 (unmarked)
#   kill Mutation-unmarked. set-diff {topology} − {markers} ≠ ∅.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
make_path "$R" "engine/src/order/exec.py"
write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/mctrader-engine
      rationale: 미마킹될 책임
      linked_artifact:
        - CFP-2418
    - responsibility: order-execution
      owner_repo: mclayer/mctrader-engine
      rationale: 마킹된 책임
      linked_artifact:
        - CFP-2418
  responsibility_markers:
    - path: engine/src/order/exec.py
      responsibility: order-execution
EOF
run_fixture_marker "F-unmarked" "1" "(a)unmarked" "토폴로지 risk-metrics 책임이 manifest 에 미마킹 = unmarked exit1" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-mismatch (b): marker[R].repo=repo-a, topology.owner_repo[R]=repo-b → exit 1 (불일치)
#   kill Mutation-mismatch. 문자열 동등 위반.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
make_path "$R" "engine/src/risk/calc.py"
write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/repo-b
      rationale: topology 소유레포 repo-b
      linked_artifact:
        - CFP-2418
  responsibility_markers:
    - path: engine/src/risk/calc.py
      responsibility: risk-metrics
      repo: mclayer/repo-a
EOF
run_fixture_marker "F-mismatch" "1" "(b)불일치" "marker.repo=repo-a ≠ topology.owner_repo[risk-metrics]=repo-b = 불일치 exit1" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-mismatch-norepo-ok (negative): repo 미지정 entry → 불일치(b) 비대상 → exit 0
#   repo 미지정 = (b) 검사 opt-out (역방향 추론 안 함). join-key 일치 + path 실재 → PASS.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
make_path "$R" "engine/src/risk/calc.py"
write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/repo-b
      rationale: topology 소유레포
      linked_artifact:
        - CFP-2418
  responsibility_markers:
    - path: engine/src/risk/calc.py
      responsibility: risk-metrics
EOF
run_fixture "F-mismatch-norepo-ok" "0" "repo 미지정 entry = 불일치(b) 비대상 (역방향 추론 안 함) → PASS" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-stale (c): marker entry path = 부재 경로(fixture-root 안 미생성) → exit 1 (stale)
#   kill Mutation-stale. fs-stat — path 미생성이라 os.path.exists False.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)  # path 미생성 = stale
write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/mctrader-engine
      rationale: a
      linked_artifact:
        - CFP-2418
  responsibility_markers:
    - path: engine/src/moved-away/gone.py
      responsibility: risk-metrics
EOF
run_fixture_marker "F-stale" "1" "(c)stale" "marker path 부재(미생성) = stale exit1 (fs-stat)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-polyglot-glob: path glob 이 Rust+Python+TS 혼재 fixture 디렉토리 매칭 → exit 0 (언어무관 정상)
#   AC-5 — 파일별 주석 아님, glob 매칭 1+ = 존재. 언어무관 통과.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
make_path "$R" "engine/src/risk/calc.py"
make_path "$R" "engine/src/risk/lib.rs"
make_path "$R" "engine/src/risk/index.ts"
write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/mctrader-engine
      rationale: polyglot
      linked_artifact:
        - CFP-2418
  responsibility_markers:
    - path: engine/src/risk/**
      responsibility: risk-metrics
EOF
run_fixture "F-polyglot-glob" "0" "path glob engine/src/risk/** = Rust+Python+TS 혼재 매칭 1+ = 언어무관 정상 통과 (AC-5)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-reverse-orphan-notice: manifest 에만 있고 topology 에 없는 R → exit 0 + ::notice:: (warning 아님)
#   kill Mutation-reverse (역방향 notice → warning 승격 시 exit1=RED). micro-decision ③ 보존.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d)
make_path "$R" "engine/src/new/feature.py"
write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/mctrader-engine
      rationale: topology 에 있는 책임
      linked_artifact:
        - CFP-2418
  responsibility_markers:
    - path: engine/src/risk/calc.py
      responsibility: risk-metrics
    - path: engine/src/new/feature.py
      responsibility: brand-new-resp-not-in-topology
EOF
# NOTE: engine/src/risk/calc.py 도 실재해야 stale(c) 미발생 → risk-metrics entry path 도 생성.
make_path "$R" "engine/src/risk/calc.py"
run_fixture_marker "F-reverse-orphan-notice" "0" "역방향 고아" "manifest 에만 있는 R = ::notice:: 역방향 고아 (warning 아님, exit0 — micro-decision ③)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-failopen-noinject: responsibility_markers 미주입 → exit 0 + honest ::notice::
#   kill Mutation-FO (fail-open exit0 → exit1 강제 시 FAIL=RED). exit-code-only assert 금지.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibilities:
    - responsibility: risk-metrics
      owner_repo: mclayer/mctrader-engine
      rationale: a
      linked_artifact:
        - CFP-2418
EOF
run_fixture_marker "F-failopen-noinject" "0" "responsibility_markers 미주입" "markers 미주입 = fail-open exit0 + honest notice (exit-code-only 금지)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-failopen-notapplicable: applicable:false → exit 0 + honest notice
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: false
  responsibility_markers:
    - path: nonexistent/path.py
      responsibility: ignored-when-not-applicable
EOF
run_fixture_marker "F-failopen-notapplicable" "0" "applicable != true" "applicable:false = fail-open exit0 + honest notice (stale 있어도 opt-in 미활성이라 비검사)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-failopen-notopo: repo_topology 섹션 미주입 → exit 0 + honest notice
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
some_other_section:
  foo: bar
EOF
run_fixture_marker "F-failopen-notopo" "0" "repo_topology 섹션 미주입" "repo_topology 미주입 = fail-open exit0 + honest notice" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-failopen-empty: applicable:true + responsibility_markers 빈 맵 → exit 0 + honest notice
#   kill Mutation-EMPTY (빈맵 → 스키마 무효 exit2 처리 시 exit2=RED).
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibility_markers: []
EOF
run_fixture_marker "F-failopen-empty" "0" "빈 맵" "applicable:true + 빈 markers = 스키마 유효성만·정책 공백 PASS exit0 (스키마 무효 exit2 아님)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-malformed-path-absent: marker entry path 키 부재 → exit 2 (스키마 무효 SETUP)
#   kill Mutation-schema (path 필수 제거 시 exit≠2=RED).
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibility_markers:
    - responsibility: missing-path-key
EOF
run_fixture_marker "F-malformed-path-absent" "2" "setup-error" "path 키 부재 = 스키마 무효 exit2 (setup-error)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-malformed-resp-absent: marker entry responsibility 키 부재 → exit 2
#   kill Mutation-schema (responsibility 필수 제거 시 exit≠2=RED).
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibility_markers:
    - path: engine/src/risk/calc.py
EOF
run_fixture_marker "F-malformed-resp-absent" "2" "setup-error" "responsibility 키(join-key) 부재 = 스키마 무효 exit2 (setup-error)" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-malformed-yaml: 깨진 yaml → exit 2 (yaml.safe_load 파싱 실패)
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibility_markers:
    - path: bad
     responsibility: [unclosed
EOF
run_fixture_marker "F-malformed-yaml" "2" "setup-error" "malformed yaml = yaml.safe_load 파싱 실패 exit2" "$R"

# ═════════════════════════════════════════════════════════════════════════════
# F-malformed-repo-type: repo 지정되었으나 비-string(int) → exit 2 (malformed)
#   repo optional 이나 지정 시 non-empty str 의무 — int = malformed = exit2.
# ═════════════════════════════════════════════════════════════════════════════
R=$(mktemp -d); write_overlay "$R" <<'EOF'
repo_topology:
  applicable: true
  responsibility_markers:
    - path: engine/src/risk/calc.py
      responsibility: risk-metrics
      repo: 42
EOF
run_fixture_marker "F-malformed-repo-type" "2" "setup-error" "repo int 타입 = malformed 스키마 무효 exit2 (지정 시 non-empty str 의무)" "$R"

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
echo "Test Summary (CFP-2428 responsibility-marker-drift)"
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
  echo "Mutation-unmarked (set-diff (a) 분기 제거)        → F-unmarked PASS 면 RED"
  echo "Mutation-mismatch (문자열동등 (b) 분기 제거)      → F-mismatch PASS 면 RED"
  echo "Mutation-stale    (fs-stat (c) 분기 제거)         → F-stale PASS 면 RED"
  echo "Mutation-FO       (fail-open exit0 → exit1 강제)  → F-failopen-* FAIL 면 RED"
  echo "                   (+ F0-valid GREEN 유지 = fail-open 마커 ≠ 정상 마커, 두 set 분리)"
  echo "Mutation-EMPTY    (빈맵 → 스키마 무효 exit2)       → F-failopen-empty exit2 나면 RED"
  echo "Mutation-schema   (path/responsibility 필수 제거)  → F-malformed-* exit≠2 면 RED"
  echo "Mutation-reverse  (역방향 notice → warning 승격)   → F-reverse-orphan-notice exit1 나면 RED"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
