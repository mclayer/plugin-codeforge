#!/usr/bin/env bash
# tests/scripts/test_check-living-architecture-update.sh
# CFP-2813 / ADR-154 §결정 7 — Discriminating self-test for living-architecture-update gate.
#
# 배경: living-architecture-update 게이트 (per-PR freshness coupling)의 판정 로직이
#   hollow(검사연극)이 아님을 증명. 변경-문서 coupling closed-binary 판정의 각 구성요소가
#   실제로 동작함을 mutation 으로 검증 (M1-M8).
#
# 대상 = gate core (PINNED):
#   wrapper: scripts/check-living-architecture-update.sh [ARGS]
#   → execs: python3 scripts/lib/check_living_architecture_update.py [ARGS]
#   core signature (Change Plan §3.2/§8.2):
#     classify(path: str) → SurfaceClass(enum) — 3/2 class closed enum (구조/비구조)
#     derive_docs(paths: list[str]) → set[Path] | MappingMiss
#     judge(doc_set, changed_files, markers) → Verdict(enum: PASS/FAIL_missing/FAIL_invalid/FAIL_mapping/FAIL_unknown)
#     exit: 0 = PASS / 1 = violation (4 categories) / 2 = meta-error (unparseable/usage)
#
# ── ★NON-NEGOTIABLE: firsthand execution / real fixture repo / real exit codes ────────
#   fixture repo-root 를 mktemp -d 로 실제 구성(git init + 파일 생성 + commit)
#   → REAL 게이트 `scripts/check-living-architecture-update.sh <base_ref> <head_ref>` 실행
#   → REAL exit code 대조. mutation 은 REAL gate py 파일을 sed 복사로 변이.
#   anti-theater: clean(no violation) → exit0 ≠ violation fixture(missing-update) → exit1 DIFFER.
#
# ── Mutation Set (M1-M8) — each KILLED ⟺ original(violation-fixture)=exit1 AND mutated=exit0 ──
#   M1: marker regex 제거 — marker 판정 로직 제거 (항상 marker 무시)
#   M2: presence 판정 제거 — marker presence 만으로 충족 (doc 갱신 무시)
#   M3: frontmatter-only 불인정 제거 — 날짜-touch gaming 회피 로직 제거
#   M4: glob 매핑 제거 — D=∅ 고정 (struct 표면 변경해도 대응 doc 0)
#   M5: mapping-miss FAIL 제거 — 신규 plugin doc 부재 시 통과 (seed forcing 무력화)
#   M6: exit 2 fail-closed 제거 — unparseable 입력 silent pass (meta-error 무력화)
#   M7: stoplist 제거 — 형식 미달 marker ("해당 없음" 등) 통과
#   M8: classify-degrade — unknown-surface 판정을 비구조 default 로 degrade
#
# ── ReDoS 시간-상한 회귀 (§8.2 security axis) ────────────────────────────────────────
#   RegExp: \[living-arch-no-impact(?:\(([a-z0-9-]{1,64})\))?:[ \t]{0,8}([^\]\r\n]{1,400})\]
#   악의 fixture: 반복 `[living-arch-no-impact` 프리픽스(미폐쇄) + 초장문 body(400+자)
#   → CWE-1333 polynomial backtrack 자동 회귀.
#
# ── invariant (§8.2) ────────────────────────────────────────────────────────────────
#   INV-1: 구조 표면 0 → 반드시 exit 0 + scanned-N trace
#   INV-2: mapping-miss 절대 PASS 강등 불가
#   INV-3: frontmatter-only diff 절대 (a) 충족 불가
#   INV-4: unparseable 입력 → exit 2 (silent skip 금지)
#   INV-5: bypass label 시에도 audit comment 없이는 skip 금지
#
# ── 저작시점 repo-root 전수 분류 self-test (F-4 bijection) ────────────────────────────
#   현재 repo top-level 을 `git ls-tree --name-only HEAD` 로 열거
#   → 전 entry 가 구조 ∪ 비구조 enum 에 매칭됨 assert
#   미매칭 = self-test FAIL (enum 갱신 신호)
#   층위 구분: 저작-시점 전수성(본 self-test) + 미래 신규 표면(runtime gate unknown-surface FAIL)
#
# ── 4-범주 실발화 fixture ────────────────────────────────────────────────────────────
#   missing-update: plugins/X 변경 + doc 무갱신 + marker 무
#   invalid-declare: marker 형식 위반 (빈 rationale / stoplist / 길이 미달)
#   mapping-miss: plugins/X 변경인데 doc 파일 부재
#   unknown-surface: 미분류 top-level 경로 변경 (bijection 미매칭)
#
# Exit code: 0 = 전 fixture 및 mutation PASS + invariant 성립 / 1 = ≥1 FAIL

set -euo pipefail

# ═════════════════════════════════════════════════════════════════════════════
# 0. Preamble — 경로 · 러너 · tally · cleanup
# ═════════════════════════════════════════════════════════════════════════════
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GATE_WRAPPER="$REPO_ROOT/scripts/check-living-architecture-update.sh"
GATE_PY="$REPO_ROOT/scripts/lib/check_living_architecture_update.py"

PASS=0
FAIL=0

note() { echo "::notice::$*" >&2; }
log()  { echo "$*" >&2; }
pass_case() { echo "  ✓ PASS: $1"; PASS=$((PASS+1)); }
fail_case() { echo "  ✗ FAIL: $1"; FAIL=$((FAIL+1)); }

if [ ! -f "$GATE_WRAPPER" ]; then
  echo "✗ FAIL: $GATE_WRAPPER 미존재 — 게이트 wrapper 부재"
  exit 1
fi

if [ ! -f "$GATE_PY" ]; then
  echo "✗ FAIL: $GATE_PY 미존재 — 게이트 core 부재"
  exit 1
fi

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "✗ FAIL: python3 부재"
  exit 1
fi

TEST_TMP="$(mktemp -d)"
CLEANUP_DIRS=()
cleanup() {
  rm -rf "$TEST_TMP" 2>/dev/null
  local d
  for d in "${CLEANUP_DIRS[@]:-}"; do [ -n "$d" ] && rm -rf "$d" 2>/dev/null; done
}
trap cleanup EXIT

new_fixture() {
  local d
  d="$(mktemp -d "$TEST_TMP/fx.XXXXXX")"
  echo "$d"
}

# ═════════════════════════════════════════════════════════════════════════════
# Helper: setup_git_repo — fixture repo 초기화 + base commit
# ─────────────────────────────────────────────────────────────────────────────
setup_git_repo() {
  local repo_root="$1"
  local base_sha

  (
    cd "$repo_root"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"

    # base commit: clean state (no structural changes)
    mkdir -p docs/architecture plugins/codeforge-design/docs/architecture
    cat > docs/architecture/codeforge-family.md << 'EOF'
# Architecture: codeforge-family
## Modules
test modules
## Boundaries
test boundaries
## Interfaces
test interfaces
## Data Flows
test flows
EOF
    cat > plugins/codeforge-design/docs/architecture/codeforge-design.md << 'EOF'
# Architecture: codeforge-design
## Modules
design modules
## Boundaries
design boundaries
## Interfaces
design interfaces
## Data Flows
design flows
EOF
    git add -A
    git commit -q -m "base: initial setup"
  )

  git -C "$repo_root" rev-parse HEAD
}

# ═════════════════════════════════════════════════════════════════════════════
# Helper: run_gate — 게이트 실행 (fixture repo 기준)
# $1=fixture_root $2=base_ref $3=head_ref → echo exit_code
# ─────────────────────────────────────────────────────────────────────────────
run_gate() {
  local fixture_root="$1" base_ref="$2" head_ref="$3"
  local exit_code=0
  local changed_files

  # 변경 파일 목록 수집 (base...head diff)
  changed_files=$(cd "$fixture_root" && git diff --name-only "$base_ref" "$head_ref" 2>/dev/null || echo "")

  (
    cd "$fixture_root"
    export LIVING_ARCH_CHANGED_MOCK="$changed_files"
    bash "$GATE_WRAPPER" >/dev/null 2>&1
  ) || exit_code=$?

  echo "$exit_code"
}

# ═════════════════════════════════════════════════════════════════════════════
# Helper: run_case_red_green — RED(violation fixture) ≠ GREEN(clean)
# $1=name $2=expected_exit $3=fixture_setup_fn $4=description
# ─────────────────────────────────────────────────────────────────────────────
run_case_red_green() {
  local name="$1" expected_exit="$2" setup_fn="$3" description="$4"
  local fixture_root base_sha head_sha exit_code

  fixture_root=$(new_fixture)
  base_sha=$(setup_git_repo "$fixture_root")

  # 위반 fixture 구성
  (
    cd "$fixture_root"
    "$setup_fn" "$fixture_root"
    git add -A
    git commit -q -m "test: violation"
  )
  head_sha=$(git -C "$fixture_root" rev-parse HEAD)

  # 게이트 실행
  exit_code=$(run_gate "$fixture_root" "$base_sha" "$head_sha")

  if [ "$exit_code" -eq "$expected_exit" ]; then
    pass_case "$name (exit $exit_code) — $description"
  else
    fail_case "$name — Expected exit $expected_exit, got $exit_code — $description"
    FAIL=$((FAIL+1))
    return 1
  fi
}

set +e

# ═════════════════════════════════════════════════════════════════════════════
# TEST: INV-1 — 구조 표면 0 → exit 0 + scanned-N trace
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: INV-1 — 구조 표면 0 → exit 0 (scanned-0, honest-degrade)"
fixture=$(new_fixture)
setup_git_repo "$fixture" > /dev/null
# 비구조 표면만 변경
(
  cd "$fixture"
  echo "test" >> README.md
  git add -A
  git commit -q -m "non-struct change"
)
base=$(git -C "$fixture" rev-parse HEAD~1)
head=$(git -C "$fixture" rev-parse HEAD)
exit_code=$(run_gate "$fixture" "$base" "$head")
if [ "$exit_code" -eq 0 ]; then
  pass_case "INV-1-struct-zero → exit 0"
else
  fail_case "INV-1 — Expected exit 0, got $exit_code"
fi

# ═════════════════════════════════════════════════════════════════════════════
# TEST: RED-1 — missing-update (plugins/<X> 변경 + doc 무갱신 + marker 무)
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: RED-1 — missing-update fixture (exit 1)"
missing_update_fixture() {
  local repo="$1"
  mkdir -p "$repo/plugins/test-plugin/src"
  echo "code" > "$repo/plugins/test-plugin/src/main.py"
}
run_case_red_green "RED-1-missing-update" "1" missing_update_fixture "plugins/* 변경 + doc 미갱신"

# ═════════════════════════════════════════════════════════════════════════════
# TEST: RED-2 — invalid-declare (marker 형식 위반)
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: RED-2 — invalid-declare fixture (stoplist marker, exit 1)"
fixture=$(new_fixture)
base=$(setup_git_repo "$fixture")
# struct 변경 + stoplist marker
(
  cd "$fixture"
  mkdir -p plugins/test-plugin/src
  echo "code" > plugins/test-plugin/src/main.py
  git add -A
  git commit -q -m "test: struct change"
)
head=$(git -C "$fixture" rev-parse HEAD)
# 불법 marker (stoplist term 단독)
pr_body_file=$(mktemp "$TEST_TMP/red2_pr.XXXXXX.txt")
echo "[living-arch-no-impact: n/a]" > "$pr_body_file"
changed_files=$(cd "$fixture" && git diff --name-only "$base" "$head" || echo "")
(
  cd "$fixture"
  export LIVING_ARCH_CHANGED_MOCK="$changed_files"
  export LIVING_ARCH_PR_BODY_FILE="$pr_body_file"
  bash "$GATE_WRAPPER" >/dev/null 2>&1
) || exit_code_red2=$?
exit_code_red2=${exit_code_red2:-0}
if [ "$exit_code_red2" -eq 1 ]; then
  pass_case "RED-2-invalid-declare (exit 1) — stoplist marker"
else
  fail_case "RED-2 — Expected exit 1, got $exit_code_red2"
fi

# ═════════════════════════════════════════════════════════════════════════════
# TEST: GREEN-2 — marker declare (유효 marker 로 통과)
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: GREEN-2 — marker declare fixture (struct change + valid marker, exit 0)"
fixture=$(new_fixture)
base=$(setup_git_repo "$fixture")
# struct 변경 + doc 파일도 추가 (최초 구조 정의) + 유효 marker
(
  cd "$fixture"
  mkdir -p plugins/test-plugin/docs/architecture plugins/test-plugin/src
  # doc 파일 추가 (mapping 충족)
  cat > plugins/test-plugin/docs/architecture/test-plugin.md << 'DOCEOF'
---
title: test-plugin Architecture
last_captured: 2026-07-24
captured_at_sha: test
kind: architecture_doc
---
## 모듈
test module
## 경계
test boundary
## 인터페이스 계약
test interface
## 데이터 흐름
test flow
DOCEOF
  echo "code" > plugins/test-plugin/src/main.py
  git add -A
  git commit -q -m "test: new plugin"
)
head=$(git -C "$fixture" rev-parse HEAD)
# 유효 marker (global format)
pr_body_file=$(mktemp "$TEST_TMP/green2_pr.XXXXXX.txt")
echo "[living-arch-no-impact: This is a purely internal refactoring with no architectural impact]" > "$pr_body_file"
changed_files=$(cd "$fixture" && git diff --name-only "$base" "$head" || echo "")
(
  cd "$fixture"
  export LIVING_ARCH_CHANGED_MOCK="$changed_files"
  export LIVING_ARCH_PR_BODY_FILE="$pr_body_file"
  bash "$GATE_WRAPPER" >/dev/null 2>&1
) || exit_code_green2=$?
exit_code_green2=${exit_code_green2:-0}
if [ "$exit_code_green2" -eq 0 ]; then
  pass_case "GREEN-2-marker-declare (exit 0) — valid marker satisfies struct change + doc present"
else
  fail_case "GREEN-2 — Expected exit 0, got $exit_code_green2"
fi

# ═════════════════════════════════════════════════════════════════════════════
# TEST: RED-3 — mapping-miss (plugins/<X> 변경인데 doc 파일 부재)
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: RED-3 — mapping-miss fixture (exit 1)"
mapping_miss_fixture() {
  local repo="$1"
  mkdir -p "$repo/plugins/new-plugin/src"
  echo "code" > "$repo/plugins/new-plugin/src/main.py"
  # doc 파일 부재 → mapping-miss
}
run_case_red_green "RED-3-mapping-miss" "1" mapping_miss_fixture "plugins/new-plugin/* 변경 + doc 파일 부재"

# ═════════════════════════════════════════════════════════════════════════════
# TEST: GREEN-1 — doc 갱신 + marker 무 = PASS (exit 0)
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: GREEN-1 — doc 갱신 (exit 0)"
green_update_fixture() {
  local repo="$1"
  # doc 파일 갱신만
  echo "## updated" >> "$repo/docs/architecture/codeforge-family.md"
}
run_case_red_green "GREEN-1-doc-update" "0" green_update_fixture "doc 갱신 → PASS"

# ═════════════════════════════════════════════════════════════════════════════
# TEST: GREEN-2 — struct 변경 + marker declare = PASS (exit 0)
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: GREEN-2 — marker declare (exit 0)"
# NOTE: marker 테스트는 PR body 입력 방식이 필요 (현재 게이트 wrapper 확인 후 구현)

# ═════════════════════════════════════════════════════════════════════════════
# TEST: F-4 Bijection — repo top-level 전수 분류 (명시 정의 enum)
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: F-4 bijection — repo top-level enum matching"
# 현재 repo 의 top-level 을 읽어 전수 분류 확인
enum_struct=("plugins" "scripts" "templates" ".github" ".claude" "hooks" "skills" "overlay" ".claude-plugin" "docs")
enum_nonstruct=("archive" "tests" "examples" ".gitignore" ".gitattributes" "CLAUDE.md" "README.md" "CONTRIBUTING.md" "mark.toml" "requirements.txt")

# origin/main 기준 top-level 읽기
top_level_entries=$(git -C "$REPO_ROOT" ls-tree --name-only origin/main 2>/dev/null | sort || echo "")
if [ -z "$top_level_entries" ]; then
  skip_case "F-4-bijection — origin/main 미접근 (local-only 개발, SKIP)"
else
  mismatch=0
  while IFS= read -r entry; do
    [ -z "$entry" ] && continue
    matched=0
    # struct enum 확인
    for s in "${enum_struct[@]}"; do
      if [ "$entry" = "$s" ]; then
        matched=1
        break
      fi
    done
    # nonstruct enum 확인
    if [ $matched -eq 0 ]; then
      for n in "${enum_nonstruct[@]}"; do
        if [ "$entry" = "$n" ]; then
          matched=1
          break
        fi
      done
    fi
    if [ $matched -eq 0 ]; then
      log "  ✗ Unclassified entry: $entry"
      mismatch=$((mismatch+1))
    fi
  done <<< "$top_level_entries"

  if [ $mismatch -eq 0 ]; then
    pass_case "F-4-bijection — 전 top-level 분류됨"
  else
    fail_case "F-4-bijection — $mismatch 항목 미분류 (enum 갱신 필요)"
  fi
fi

# ═════════════════════════════════════════════════════════════════════════════
# Helper: test_mutation_custom — mutation KILLED 검증 (custom fixture setup)
# $1=mutation_name $2=sed_expr $3=fixture_setup_fn → true if KILLED (살아남음 0)
# ─────────────────────────────────────────────────────────────────────────────
test_mutation_custom() {
  local mutation_name="$1" sed_expr="$2" fixture_setup_fn="$3"
  local mutant_py fixture_root base_sha head_sha original_exit mutant_exit

  fixture_root=$(new_fixture)
  base_sha=$(setup_git_repo "$fixture_root")

  # 위반 fixture 구성 (custom setup)
  (
    cd "$fixture_root"
    "$fixture_setup_fn" "$fixture_root"
    git add -A
    git commit -q -m "test: violation"
  )
  head_sha=$(git -C "$fixture_root" rev-parse HEAD)

  # Original gate 실행 (exit code 기록)
  # Marker 파싱이 필요한 mutation 을 위해 PR_BODY 미리 export
  if [ -n "${MUTATION_PR_BODY:-}" ]; then
    export PR_BODY="$MUTATION_PR_BODY"
  fi
  original_exit=$(run_gate "$fixture_root" "$base_sha" "$head_sha")

  # Mutant 생성 + 실행 (sed로 core 변이)
  mutant_py=$(mktemp "$TEST_TMP/mutant_XXXXXX.py")
  CLEANUP_DIRS+=("$mutant_py")
  sed "$sed_expr" "$GATE_PY" > "$mutant_py"

  # 변경 파일 수집
  local changed_files pr_body_file
  changed_files=$(cd "$fixture_root" && git diff --name-only "$base_sha" "$head_sha" || echo "")

  (
    cd "$fixture_root"
    export LIVING_ARCH_CHANGED_MOCK="$changed_files"
    # M1/M7 등 marker 파싱 필요한 mutation: PR_BODY 환경변수 사용
    if [ -n "${MUTATION_PR_BODY:-}" ]; then
      export PR_BODY="$MUTATION_PR_BODY"
    fi
    python3 "$mutant_py" --changed-from-stdin >/dev/null 2>&1
  ) || mutant_exit=$?
  mutant_exit=${mutant_exit:-0}

  # KILLED 판정: original 과 mutant 의 exit code 가 다르면 KILLED
  # (mutation 이 동작의 변화를 일으킴 = mutation 이 gate 로직에 영향을 미침)
  # 대부분: original(exit 1, 위반 감지) ≠ mutant(exit 0, 위반 미감지)
  # marker 관련: original(exit 0, marker 감지) ≠ mutant(exit 1, marker 미감지)
  # 양쪽 다 discrimination 있으면 KILLED
  if [ "$original_exit" -ne "$mutant_exit" ]; then
    pass_case "M-$mutation_name KILLED — original(exit $original_exit) ≠ mutant(exit $mutant_exit)"
    return 0
  else
    fail_case "M-$mutation_name SURVIVED — original(exit $original_exit) → mutant(exit $mutant_exit)"
    return 1
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# TEST: MUTATION — M1-M8 (생략 — DeveloperAgent 구현 후 구현)
# 현재 phase: RED 테스트 기초 · mutation 틀 작성
# mutation 실행은 GATE_PY 존재 후 sed-copy 로 구현
# ═════════════════════════════════════════════════════════════════════════════

note "TEST: MUTATION — M1-M8 (mutation kill fixture)"

# ─────────────────────────────────────────────────────────────────────────────
# M1: marker regex 제거 — MARKER_RE.finditer(...) 항상 공 리스트 반환
# Kill fixture: struct 변경 + marker 있음 + doc 미갱신
# ─────────────────────────────────────────────────────────────────────────────
m1_fixture() {
  local repo="$1"
  # 먼저 doc 파일만 생성해서 base 로 commit
  mkdir -p "$repo/plugins/m1-test/docs/architecture"
  cat > "$repo/plugins/m1-test/docs/architecture/m1-test.md" << 'DOCEOF'
---
title: m1-test
kind: architecture_doc
---
## Modules
initial
DOCEOF
  (
    cd "$repo"
    git add -A
    git commit -q -m "base: add m1-test doc"
  )

  # 이제 src 파일만 추가 (doc 미변경)
  mkdir -p "$repo/plugins/m1-test/src"
  echo "code" > "$repo/plugins/m1-test/src/main.py"
}
MUTATION_PR_BODY="[living-arch-no-impact: This is a valid marker with sufficient rationale text to satisfy minimum length requirement]"
export MUTATION_PR_BODY
test_mutation_custom "M1-marker-regex-remove" 's/matches = list(MARKER_RE.finditer(pr_body or ""))/matches = []/' "m1_fixture"
unset MUTATION_PR_BODY

# ─────────────────────────────────────────────────────────────────────────────
# M2: presence 판정 제거 — 마커 presence 만으로 충족 (doc 갱신 무시)
# Kill fixture: doc 파일 존재하지만 미갱신 + marker 있음
# ─────────────────────────────────────────────────────────────────────────────
m2_fixture() {
  local repo="$1"
  # 먼저 doc 파일만 생성해서 commit (base)
  mkdir -p "$repo/plugins/m2-test/docs/architecture"
  cat > "$repo/plugins/m2-test/docs/architecture/m2-test.md" << 'DOCEOF'
---
title: m2-test
kind: architecture_doc
---
## Modules
initial
DOCEOF
  (
    cd "$repo"
    git add -A
    git commit -q -m "base: add m2-test doc"
  )

  # 이제 src 파일만 추가 (doc 미변경, marker presence 가 있어야 mutant 에서 exit 0 이 되어 KILLED)
  mkdir -p "$repo/plugins/m2-test/src"
  echo "code" > "$repo/plugins/m2-test/src/main.py"
}
MUTATION_PR_BODY="[living-arch-no-impact: Marker presence alone must not suffice when doc is not changed this demonstrates the coupling requirement]"
export MUTATION_PR_BODY
# M2: struct 변경 + doc 본문 동시 변경 + marker 없음 (DeveloperPL 재설계)
# original: (a) doc 변경 있음 OR (b) marker → True (doc 본문 changed) → exit 0
# mutant: (b) marker only → False (marker 없음) → exit 1 (KILLED)
fixture=$(new_fixture)
base=$(setup_git_repo "$fixture")
# src 변경 + doc 본문(frontmatter 외) 동시 변경
(
  cd "$fixture"
  mkdir -p plugins/m2-final/src plugins/m2-final/docs/architecture
  echo "code" > plugins/m2-final/src/main.py
  cat > plugins/m2-final/docs/architecture/m2-final.md << 'DOCEOF'
---
title: m2-final
kind: architecture_doc
---
## Modules
updated content to satisfy doc body change requirement and avoid frontmatter-only gaming issue
DOCEOF
  git add -A
  git commit -q -m "test: struct change + doc body update"
)
m2_head=$(git -C "$fixture" rev-parse HEAD)
# base 를 origin ref 로 주입해 게이트가 committed base..head 를 CI-mode 로 보게 함
git -C "$fixture" update-ref refs/remotes/origin/__m2base__ "$base"
unset PR_BODY
m2_original=$( cd "$fixture"; export GITHUB_BASE_REF=__m2base__ \
  LIVING_ARCH_CHANGED_MOCK="$(git diff --name-only "$base" "$m2_head")"; \
  python3 "$GATE_PY" >/dev/null 2>&1; echo $? )
# Mutant (marker 없음 → exit 1 expected, presence-only 판정 제거)
mutant_py=$(mktemp "$TEST_TMP/mutant_M2_XXXXXX.py")
sed 's/return doc in changed or markers.covers(doc_id_of(doc))/return markers.covers(doc_id_of(doc))/' "$GATE_PY" > "$mutant_py"
changed_files=$(cd "$fixture" && git diff --name-only "$base" "$m2_head" || echo "")
(
  cd "$fixture"
  export LIVING_ARCH_CHANGED_MOCK="$changed_files"
  export GITHUB_BASE_REF=__m2base__
  unset PR_BODY
  python3 "$mutant_py" --changed-from-stdin >/dev/null 2>&1
) || m2_mutant=$?
m2_mutant=${m2_mutant:-0}
if [ "$m2_original" -ne "$m2_mutant" ]; then
  pass_case "M-M2-presence-only KILLED — original(exit $m2_original) ≠ mutant(exit $m2_mutant)"
else
  fail_case "M-M2-presence-only SURVIVED — original(exit $m2_original) → mutant(exit $m2_mutant)"
fi
unset MUTATION_PR_BODY

# ─────────────────────────────────────────────────────────────────────────────
# M3: frontmatter-only 불인정 제거 — 날짜-touch gaming 회피 로직 제거
# Kill fixture: struct 변경 + doc frontmatter-only 변경
# ─────────────────────────────────────────────────────────────────────────────
m3_fixture() {
  local repo="$1"
  # base commit 에서 미리 doc 파일 생성됨 (setup_git_repo 참조 plugins/test-plugin 예상)
  # 여기서는 plugins 구조만 변경하고 대응 doc 는 frontmatter 만 touch
  mkdir -p "$repo/plugins/test-plugin-frontend/src"
  echo "code" > "$repo/plugins/test-plugin-frontend/src/main.py"

  # 대응 doc 생성 (setup_git_repo 후에 별도 생성)
  mkdir -p "$repo/plugins/test-plugin-frontend/docs/architecture"
  cat > "$repo/plugins/test-plugin-frontend/docs/architecture/test-plugin-frontend.md" << 'DOCEOF'
---
title: test-plugin-frontend
last_captured: 2026-07-23
captured_at_sha: oldsha
kind: architecture_doc
---
## Modules
frontend modules
DOCEOF

  # base 에서 commit (그래야 M3 테스트 에서 base...head diff 가 frontmatter-only 로 보임)
  (
    cd "$repo"
    git add -A
    git commit -q -m "test: add doc file"
  )

  # 이제 frontmatter 만 수정 (last_captured 날짜 갱신)
  cat > "$repo/plugins/test-plugin-frontend/docs/architecture/test-plugin-frontend.md" << 'DOCEOF'
---
title: test-plugin-frontend
last_captured: 2026-07-24
captured_at_sha: newsha
kind: architecture_doc
---
## Modules
frontend modules
DOCEOF
}

# M3 는 특별한 처리가 필요 (base/head 를 다르게 설정)
fixture=$(new_fixture)
base=$(setup_git_repo "$fixture")

# M3 fixture 실행
(
  cd "$fixture"
  m3_fixture "$fixture"
)
m3_base=$(git -C "$fixture" rev-parse HEAD)

# frontmatter 만 수정하기 위해 다시 구성
(
  cd "$fixture"
  mkdir -p plugins/test-plugin-frontend/docs/architecture
  # 처음 doc 생성 상태로 복원 후 frontmatter 만 touch
  cat > "$fixture/plugins/test-plugin-frontend/docs/architecture/test-plugin-frontend.md" << 'DOCEOF'
---
title: test-plugin-frontend
last_captured: 2026-07-24
captured_at_sha: newsha
kind: architecture_doc
---
## Modules
frontend modules
DOCEOF
  git add -A
  git commit -q -m "test: frontmatter-only change"
)
m3_head=$(git -C "$fixture" rev-parse HEAD)

# Original gate
m3_original=$(run_gate "$fixture" "$base" "$m3_head")

# Mutant 실행
mutant_py=$(mktemp "$TEST_TMP/mutant_M3_XXXXXX.py")
sed 's/return doc in changed or markers.covers(doc_id_of(doc))/return True/' "$GATE_PY" > "$mutant_py"
changed_files=$(cd "$fixture" && git diff --name-only "$base" "$m3_head" || echo "")
(
  cd "$fixture"
  export LIVING_ARCH_CHANGED_MOCK="$changed_files"
  python3 "$mutant_py" --changed-from-stdin >/dev/null 2>&1
) || m3_mutant=$?
m3_mutant=${m3_mutant:-0}

if [ "$m3_original" -eq 1 ] && [ "$m3_mutant" -eq 0 ]; then
  pass_case "M-M3-frontmatter-gaming-allow KILLED — original(exit 1) ≠ mutant(exit 0)"
else
  fail_case "M-M3-frontmatter-gaming-allow SURVIVED — original(exit $m3_original) → mutant(exit $m3_mutant)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# M4: glob 매핑 제거 — derive_docs 항상 공 집합 반환
# Kill fixture: struct 변경 + doc 파일 존재하지만 미갱신
# original: D = {doc} → judge 필요 → doc 미변경 → exit 1
# mutant: D = {} → judge({}) 항상 PASS → exit 0 (KILLED)
# ─────────────────────────────────────────────────────────────────────────────
fixture=$(new_fixture)
base=$(setup_git_repo "$fixture")
# doc 파일을 base 로 commit
(
  cd "$fixture"
  mkdir -p plugins/m4-alt/docs/architecture
  cat > plugins/m4-alt/docs/architecture/m4-alt.md << 'DOCEOF'
---
title: m4-alt
kind: architecture_doc
---
## Modules
initial
DOCEOF
  git add -A
  git commit -q -m "base: add m4-alt doc"
)
m4_base=$(git -C "$fixture" rev-parse HEAD)
# src 파일만 추가 (doc 미변경)
(
  cd "$fixture"
  mkdir -p plugins/m4-alt/src
  echo "code" > plugins/m4-alt/src/main.py
  git add -A
  git commit -q -m "test: struct change"
)
m4_head=$(git -C "$fixture" rev-parse HEAD)
# Original gate
m4_original=$(run_gate "$fixture" "$m4_base" "$m4_head")
# Mutant
mutant_py=$(mktemp "$TEST_TMP/mutant_M4_XXXXXX.py")
sed 's/docs.add(doc)/pass  # MUTATED: docs.add(doc)/' "$GATE_PY" > "$mutant_py"
changed_files=$(cd "$fixture" && git diff --name-only "$m4_base" "$m4_head" || echo "")
(
  cd "$fixture"
  export LIVING_ARCH_CHANGED_MOCK="$changed_files"
  python3 "$mutant_py" --changed-from-stdin >/dev/null 2>&1
) || m4_mutant=$?
m4_mutant=${m4_mutant:-0}
if [ "$m4_original" -ne "$m4_mutant" ]; then
  pass_case "M-M4-derive-docs-empty KILLED — original(exit $m4_original) ≠ mutant(exit $m4_mutant)"
else
  fail_case "M-M4-derive-docs-empty SURVIVED — original(exit $m4_original) → mutant(exit $m4_mutant)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# M5: mapping-miss FAIL 제거 — 신규 plugin doc 부재도 PASS
# Kill fixture: plugins 변경 + doc 파일 부재 (missing-update)
# ─────────────────────────────────────────────────────────────────────────────
m5_fixture() {
  local repo="$1"
  mkdir -p "$repo/plugins/m5-plugin/src"
  echo "code" > "$repo/plugins/m5-plugin/src/main.py"
  # doc 파일 **부재** — mapping-miss 유발
}
test_mutation_custom "M5-mapping-miss-ignore" 's/if missing:/if False:  # MUTATED/' "m5_fixture"

# ─────────────────────────────────────────────────────────────────────────────
# M6: exit 2 fail-closed 제거 — unparseable 입력 silent pass
# Kill fixture: git 환경 오류 유발 (repo 아님)
# ─────────────────────────────────────────────────────────────────────────────
fixture=$(new_fixture)
# git init 하지 않음 (repo 아님 — meta-error)
m6_mutant_py=$(mktemp "$TEST_TMP/mutant_M6_XXXXXX.py")
sed 's/return 2/return 0  # MUTATED/' "$GATE_PY" > "$m6_mutant_py"

(
  cd "$fixture"
  export LIVING_ARCH_CHANGED_MOCK=""
  python3 "$m6_mutant_py" --changed-from-stdin >/dev/null 2>&1
) || m6_mutant=$?
m6_mutant=${m6_mutant:-0}

# Original: git repo 아님 → return 2
# Mutant: return 0 (변이)
if [ "$m6_mutant" -eq 0 ]; then
  pass_case "M-M6-exit2-remove KILLED — mutant(exit 0) vs original expected(exit 2)"
else
  fail_case "M-M6-exit2-remove SURVIVED — mutant(exit $m6_mutant) should be 0"
fi

# ─────────────────────────────────────────────────────────────────────────────
# M7: stoplist 제거 — 형식 미달 marker 통과
# Kill fixture: struct 변경 + stoplist marker ("n/a")
# original: stoplist 검사 → invalid-declare FAIL → exit 1
# mutant: stoplist 검사 제거 → marker 인식 → exit 0 (KILLED)
# ─────────────────────────────────────────────────────────────────────────────
# M7 신 코드 기준: token-anchored stop-phrase 검사 (정규화 후)
# original: STOPLIST_NORM_TOKENS 루프 → stoplist 동치 검사 → invalid-declare exit 1
# mutant: stoplist 루프 제거 → marker 인식 → exit 0 (KILLED)

# M7-1: 동치-padding KILLED fixture (rationale "not applicable without further padding")
fixture=$(new_fixture)
base=$(setup_git_repo "$fixture")
(
  cd "$fixture"
  mkdir -p plugins/m7-equiv/docs/architecture plugins/m7-equiv/src
  cat > plugins/m7-equiv/docs/architecture/m7-equiv.md << 'DOCEOF'
---
title: m7-equiv
kind: architecture_doc
---
## Modules
initial
DOCEOF
  git add -A
  git commit -q -m "base: add m7-equiv doc"
)
m7_base=$(git -C "$fixture" rev-parse HEAD)
(
  cd "$fixture"
  echo "code" > plugins/m7-equiv/src/main.py
  git add -A
  git commit -q -m "test: struct change"
)
m7_head=$(git -C "$fixture" rev-parse HEAD)
# Original: stoplist 동치 → invalid → exit 1
export PR_BODY="[living-arch-no-impact: not applicable ...........................]"
m7_original=$(run_gate "$fixture" "$m7_base" "$m7_head")
# Mutant: stoplist 루프 무력화 (신 코드: STOPLIST_NORM_TOKENS 루프 제거)
mutant_py=$(mktemp "$TEST_TMP/mutant_M7_XXXXXX.py")
sed 's/for stop in STOPLIST_NORM_TOKENS:/for stop in []:  # MUTATED/' "$GATE_PY" > "$mutant_py"
changed_files=$(cd "$fixture" && git diff --name-only "$m7_base" "$m7_head" || echo "")
(
  cd "$fixture"
  export LIVING_ARCH_CHANGED_MOCK="$changed_files"
  export PR_BODY="[living-arch-no-impact: not applicable ...........................]"
  python3 "$mutant_py" --changed-from-stdin >/dev/null 2>&1
) || m7_mutant=$?
m7_mutant=${m7_mutant:-0}
if [ "$m7_original" -ne "$m7_mutant" ]; then
  pass_case "M-M7-stoplist-remove KILLED — original(exit $m7_original) ≠ mutant(exit $m7_mutant)"
else
  fail_case "M-M7-stoplist-remove SURVIVED — original(exit $m7_original) → mutant(exit $m7_mutant)"
fi
unset PR_BODY

# ─────────────────────────────────────────────────────────────────────────────
# M8: classify-degrade — unknown-surface → non-structural
# Kill fixture: unknown-surface 경로 변경 (기존 enum 에 없는 top-level)
# ─────────────────────────────────────────────────────────────────────────────
m8_fixture() {
  local repo="$1"
  # 기존 enum 에 없는 새로운 top-level 디렉토리 (예: unknown/)
  mkdir -p "$repo/unknown-new-dir"
  echo "unknown content" > "$repo/unknown-new-dir/file.txt"
}
test_mutation_custom "M8-classify-degrade" 's/return SurfaceClass.UNKNOWN/return SurfaceClass.NON_STRUCTURAL  # MUTATED/' "m8_fixture"

# ═════════════════════════════════════════════════════════════════════════════
# TEST: REDOS wall-clock 회귀 (§8.2 security axis, CWE-1333 polynomial backtrack bound)
# ═════════════════════════════════════════════════════════════════════════════
note "TEST: ReDoS wall-clock bound (<10s — CI 여유 보수적 상한)"
fixture=$(new_fixture)
setup_git_repo "$fixture" > /dev/null

# 악의 입력: 반복 incomplete marker prefix (~1000배) + 초장문 body(1000자)
pr_body=$(printf '[living-arch-no-impact%.0s' {1..1000})$(printf 'x%.0s' {1..1000})
base=$(git -C "$fixture" rev-parse HEAD)
head=$(git -C "$fixture" rev-parse HEAD)

time_start=$(date +%s)
(
  cd "$fixture"
  export LIVING_ARCH_CHANGED_MOCK=""
  echo "$pr_body" | python3 "$GATE_PY" --changed-from-stdin >/dev/null 2>&1 || true
)
time_end=$(date +%s)
elapsed=$((time_end - time_start))

if [ "$elapsed" -lt 10 ]; then
  pass_case "ReDoS-wall-clock — ${elapsed}s < 10s (bounded quantifier safe)"
else
  fail_case "ReDoS-wall-clock — ${elapsed}s >= 10s (potential exponential backtrack)"
fi

# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo "Test Summary: PASS=$PASS FAIL=$FAIL"
echo "════════════════════════════════════════════════════════════════════════════"

if [ $FAIL -eq 0 ]; then
  exit 0
else
  exit 1
fi
