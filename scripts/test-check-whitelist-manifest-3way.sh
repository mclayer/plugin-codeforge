#!/usr/bin/env bash
# scripts/test-check-whitelist-manifest-3way.sh
# CFP-2412 Phase 2 (Epic CFP-2394 Story D) — Discriminating self-test for check-whitelist-manifest-3way.sh
#
# ADR-130 §결정 3/5 — whitelist↔manifest↔templates/github-workflows 3-way 일관성 게이트의
# 13 discriminating fixture (change-plan §6.1 SSOT). 각 fixture 는 mktemp fixture-root 안에 3 소스
# (whitelist txt / manifest / templates/github-workflows dir) 를 의도적으로 구성 후 wrapper 를
# --root 로 가리켜 exit code (valid→0 / fail→1 / setup→2) 일치를 assert.
#
# self-contained bash (bats 미사용 — CFP-2383 답습). run_fixture 헬퍼 + per-fixture mktemp build.
#
# Mutation testing 1:1 주석표 (change-plan §6.1 — mutation 생존 0):
#  - Mutation-1 (방향1 전수검증 제거)            → F1 PASS 면 RED (phantom-whitelist 미검출)
#  - Mutation-2 (방향2 부분집합 제거)            → F2 PASS 면 RED (manifest-dep-miss 미검출)
#  - Mutation-3 (depth-2 walker 제거)            → F3 PASS 면 RED (depth2-unregistered 미검출)
#  - Mutation-4 (template-only 분류 제거)        → F4 FAIL 면 RED (template-only 정상분기 오판)
#  - Mutation-5 (방향2 bijection 역강제 mutate)  → F5 phantom-FAIL 면 RED (script-only 오판)
#  - Mutation-6 (glob `.yml` 단독 축소)          → F6 phantom-dead 면 RED (.yaml ext 미인식)
#  - Mutation-7 (주석/빈줄 skip 제거)            → F7 주석 phantom entry FAIL 면 RED
#  - Mutation-8 (exit 2 분기를 1 로 mutate)      → F8 exit 1 이면 RED (SETUP vs finding 혼동)
#  - Mutation-9 (case-exact 매칭 제거)           → F9 PASS 면 RED (case-mismatch 미검출)
#  - Mutation-10 (방향3 whitelist→manifest coverage 제거) → F10 PASS 면 RED (closure-asset 미검출)
#  - Mutation-11a/b/c (data-absence→silent FAIL exit 1/2 mutate) → F11a/b/c FAIL 면 RED (fail-open 退化)
#  - [CFP-2751 D2] M-D2a (scripts/lib/*.py shape 제거) / M-D2b (char-class underscore 탈락) → CFP2751-C1 exit 1→0 면 RED
#  - [CFP-2751 D2] M-D2c (주석 strip 제거) → CFP2751-C2/C5 exit 0→1 / M-D2d (whitelist scoping 제거) → CFP2751-C3 exit 0→1 면 RED
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates lint)
#  1 = any fixture fails (lint may not be detecting mutations correctly)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-whitelist-manifest-3way.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# Fixture-root builder — baseline-valid 3 소스 (3-way 정합, exit 0)
#   whitelist: wf-a.yml, wf-b.yaml (dual-ext)
#   templates: wf-a.yml (run: scripts/check-a.sh), wf-b.yaml (run: scripts/check-b.sh),
#              bootstrap-labels.yml (run: scripts/bootstrap-labels.sh), plugin-only.yml
#   manifest: scripts/check-a.sh, scripts/check-b.sh, scripts/bootstrap-labels.sh,
#             templates/labels/base-labels.tsv, plugin-only.yml dep entry
# ─────────────────────────────────────────────────────────────────────────────
build_baseline() {
  local root="$1"
  mkdir -p "$root/templates/scripts"
  mkdir -p "$root/templates/github-workflows"
  mkdir -p "$root/templates/labels"
  mkdir -p "$root/scripts"

  # whitelist (28 의 미니 모델 — dual-ext + depth-2 chain workflow 포함)
  cat > "$root/templates/scripts/consumer_applicable_workflows.txt" <<'EOF'
# baseline whitelist fixture
wf-a.yml
wf-b.yaml
bootstrap-labels.yml
EOF

  # templates/github-workflows (배포 source 채널)
  cat > "$root/templates/github-workflows/wf-a.yml" <<'EOF'
name: wf-a
on:
  pull_request:
    paths:
      - 'scripts/check-phantom-paths-only.sh'
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: bash scripts/check-a.sh
EOF

  cat > "$root/templates/github-workflows/wf-b.yaml" <<'EOF'
name: wf-b
on:
  pull_request:
    types: [opened]
jobs:
  b:
    runs-on: ubuntu-latest
    steps:
      - run: bash scripts/check-b.sh
EOF

  cat > "$root/templates/github-workflows/bootstrap-labels.yml" <<'EOF'
name: bootstrap-labels
on:
  pull_request:
    types: [opened]
jobs:
  bl:
    runs-on: ubuntu-latest
    steps:
      - run: bash scripts/bootstrap-labels.sh
EOF

  # plugin-only workflow (whitelist 비등재 — 방향2 plugin-only 분류 대상)
  cat > "$root/templates/github-workflows/plugin-only.yml" <<'EOF'
name: plugin-only
on:
  pull_request:
    types: [opened]
jobs:
  po:
    runs-on: ubuntu-latest
    steps:
      - run: echo plugin-only
EOF

  # manifest (closure — 방향3 / depth-2 등재)
  cat > "$root/templates/consumer-scripts.manifest" <<'EOF'
# baseline manifest fixture
scripts/check-a.sh:templates/github-workflows/wf-a.yml
scripts/check-b.sh:templates/github-workflows/wf-b.yaml
scripts/bootstrap-labels.sh:templates/github-workflows/bootstrap-labels.yml
templates/labels/base-labels.tsv
scripts/check-plugin-only.sh:templates/github-workflows/plugin-only.yml
EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# run_fixture: build → mutate(callback already applied) → wrapper --root → assert exit
# ─────────────────────────────────────────────────────────────────────────────
run_fixture() {
  local name="$1"
  local expected_exit="$2"
  local description="$3"
  local root="$4"

  local out exit_code=0
  out=$( bash "$WRAPPER" --root "$root" 2>&1 ) || exit_code=$?

  if [ "$exit_code" -eq "$expected_exit" ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
    rm -rf "$root"
    return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
    rm -rf "$root"
    return 1
  fi
}

set +e

# ─────────────────────────────────────────────────────────────────────────────
# F0 baseline-valid: 3-way 정합 → PASS(0) (RED→GREEN 기준선)
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
run_fixture "F0-baseline-valid" "0" "정합 3-way 기준선 (GREEN baseline)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F1 phantom-whitelist: whitelist 에 __nonexistent__ 추가, templates 부재 → FAIL(1)
#   kill Mutation-1 (방향1 전수검증 제거)
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
echo "__nonexistent__.yml" >> "$R/templates/scripts/consumer_applicable_workflows.txt"
run_fixture "F1-phantom-whitelist" "1" "whitelist phantom → templates 부재 (방향1 real-dead)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F2 manifest-dep-miss: manifest :dep_workflow 가 가리키는 template 실파일 부재 → FAIL(1)
#   kill Mutation-2 (방향2 부분집합 제거). dep_workflow 가 whitelist 도 아니고 template 도 없음.
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
echo "scripts/check-ghost.sh:templates/github-workflows/ghost-wf.yml" >> "$R/templates/consumer-scripts.manifest"
run_fixture "F2-manifest-dep-miss" "1" "manifest dep_workflow → whitelist·template 둘 다 부재 (방향2 phantom dep)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F3 depth2-unregistered: hard-exit chain(bootstrap yml→sh→누락 tsv) 의 tsv manifest 미등재 → FAIL(1)
#   kill Mutation-3 (depth-2 walker 제거). bootstrap-labels.yml whitelist 등재 + tsv manifest 제거.
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
grep -v 'base-labels.tsv' "$R/templates/consumer-scripts.manifest" > "$R/m.tmp" && mv "$R/m.tmp" "$R/templates/consumer-scripts.manifest"
run_fixture "F3-depth2-unregistered" "1" "hard-exit 데이터 base-labels.tsv manifest 미등재 (depth-2)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F4 template-only-falsepos: templates 존재 + .github 부재 → PASS(0)
#   kill Mutation-4 (template-only 분류 제거 → 전부 dead 오판). baseline 자체가 .github 무관 = 정상 PASS.
#   (lib 은 .github 채널 미참조 — templates 존재만으로 방향1 PASS → consumer-only 정상.)
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
# .github/workflows 부재 명시 (생성 안 함) — templates 만으로 PASS 여야 함
run_fixture "F4-template-only-falsepos" "0" "templates 존재 + .github 부재 = consumer-only 정상 PASS" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F5 scriptonly-noflag: manifest dep_workflow 미부착 entry(script-only) → PASS(0)
#   kill Mutation-5 (방향2 bijection 역강제 → script-only 가 phantom-FAIL 나면 RED).
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
echo "scripts/check-shared-helper.sh" >> "$R/templates/consumer-scripts.manifest"   # dep_workflow 미부착
run_fixture "F5-scriptonly-noflag" "0" "manifest script-only(dep 미부착) entry = 방향2 비대상 PASS" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F6 yaml-ext: whitelist <name> ↔ .yaml 확장자 template → PASS(0)
#   kill Mutation-6 (glob `.yml` 단독 축소 → .yaml template 미인식 phantom-dead 면 RED).
#   baseline 의 wf-b.yaml 이 이미 .yaml ext — 별 whitelist 항목 추가 없이 baseline 이 covers.
#   명시적 강화: 확장자 없는 whitelist 명도 .yaml 매칭 확인.
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
# whitelist 에 wf-c (확장자 생략) 추가 + .yaml template 만 생성
echo "wf-c.yaml" >> "$R/templates/scripts/consumer_applicable_workflows.txt"
cat > "$R/templates/github-workflows/wf-c.yaml" <<'EOF'
name: wf-c
on:
  pull_request:
    types: [opened]
jobs:
  c:
    runs-on: ubuntu-latest
    steps:
      - run: echo no-closure-dep
EOF
run_fixture "F6-yaml-ext" "0" "whitelist → .yaml 확장자 template 매칭 (dual-ext glob)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F7 comment-skip: whitelist # 주석줄 + 빈줄 → PASS(0)
#   kill Mutation-7 (주석/빈줄 skip 제거 → 주석 phantom entry FAIL 면 RED).
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
printf '\n# this-is-a-comment.yml\n\n   # indented comment\n\n' >> "$R/templates/scripts/consumer_applicable_workflows.txt"
run_fixture "F7-comment-skip" "0" "whitelist 주석·빈줄 skip (phantom entry 0)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F8 setup-error: --root 가 존재하지 않는 dir → exit 2 (fail-closed)
#   kill Mutation-8 (exit 2 분기를 1 로 mutate → SETUP vs finding 혼동 검출).
# ─────────────────────────────────────────────────────────────────────────────
setup_exit=0
bash "$WRAPPER" --root "/nonexistent/fixture/root/xyz" >/dev/null 2>&1 || setup_exit=$?
if [ "$setup_exit" -eq 2 ]; then
  echo "✓ PASS: F8-setup-error (exit 2 for nonexistent root)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: F8-setup-error"
  echo "  Expected exit 2, got $setup_exit"
  FAIL=$((FAIL+1))
fi

# ─────────────────────────────────────────────────────────────────────────────
# F9 case-mismatch: whitelist `Wf-Case` ↔ template `wf-case.yml` (Linux CI case-sensitive) → FAIL(1)
#   kill Mutation-9 (case-exact 매칭 제거 → F9 PASS 면 RED).
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
echo "Wf-Case.yml" >> "$R/templates/scripts/consumer_applicable_workflows.txt"
cat > "$R/templates/github-workflows/wf-case.yml" <<'EOF'
name: wf-case
on:
  pull_request:
    types: [opened]
jobs:
  wc:
    runs-on: ubuntu-latest
    steps:
      - run: echo case
EOF
run_fixture "F9-case-mismatch" "1" "whitelist 'Wf-Case' ↔ template 'wf-case' case-mismatch (방향1 case-exact)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F10 whitelist-closure-asset-unregistered ★: whitelist workflow 의 run: 블록 1-hop closure 자산이
#   manifest 미등재 → FAIL(1). kill Mutation-10 (방향3 whitelist→manifest coverage 제거).
#   wf-a.yml 의 check-a.sh 를 manifest 에서 제거 (run: 블록 dep 미등재).
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
grep -v 'scripts/check-a.sh' "$R/templates/consumer-scripts.manifest" > "$R/m.tmp" && mv "$R/m.tmp" "$R/templates/consumer-scripts.manifest"
run_fixture "F10-whitelist-closure-asset-unregistered" "1" "whitelist wf-a 의 closure 자산 check-a.sh manifest 미등재 (방향3)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F10b on.paths-false-positive guard: on.paths 필터 안 dep 토큰은 closure 아님 → PASS(0)
#   (방향3 가 run:-block-aware AM-3 추출 — naive grep 이면 check-phantom-paths-only.sh false-FAIL).
#   wf-a.yml on.paths 안 'scripts/check-phantom-paths-only.sh' 는 manifest 미등재지만 closure 아님 → PASS.
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
# baseline 그대로 — wf-a.yml on.paths 에 check-phantom-paths-only.sh 있고 manifest 미등재.
# run:-block-aware 추출이면 closure 아님 → PASS. naive grep 이면 false-FAIL → mutation 검출.
run_fixture "F10b-onpaths-falsepos-guard" "0" "on.paths 안 dep 토큰은 closure 아님 (run:-block-aware AM-3)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F12 env-sibling-not-extracted ★ [구현리뷰 FIX iter 2 P1]: whitelist workflow 의 list-item `- run:` 의
#   sibling `env:` 키(run: 와 동일 컬럼) 안 script 토큰은 closure 아님 → manifest 미등재여도 PASS(0).
#   kill: run_indent=len(prefix) 정정 revert(=버그 복원) 시 env: 값(미등재 script) 오추출 → F12 FAIL=RED.
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
# wf-a.yml 을 list-item `- run:` + sibling env: (미등재 script 토큰 포함) 으로 재작성.
# check-a.sh = 실 run: dep(manifest 등재) / check-env-phantom.sh = env: 값(closure 아님, 미등재).
cat > "$R/templates/github-workflows/wf-a.yml" <<'EOF'
name: wf-a
on:
  pull_request:
    types: [opened]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: bash scripts/check-a.sh
        env:
          SCRIPT_REF: bash scripts/check-env-phantom.sh
EOF
run_fixture "F12-env-sibling-not-extracted" "0" "list-item run: 의 env: sibling script 토큰 = closure 아님 (오추출 0)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F13 with-sibling-not-extracted ★ [구현리뷰 FIX iter 2 P1]: 동형 — sibling `with:` 키 안 script 토큰은
#   closure 아님 → PASS(0). kill: run_indent 버그 복원 시 with: args: 값 오추출 → F13 FAIL=RED.
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
cat > "$R/templates/github-workflows/wf-a.yml" <<'EOF'
name: wf-a
on:
  pull_request:
    types: [opened]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: bash scripts/check-a.sh
        with:
          args: bash scripts/check-with-phantom.sh
EOF
run_fixture "F13-with-sibling-not-extracted" "0" "list-item run: 의 with: sibling script 토큰 = closure 아님 (오추출 0)" "$R"

# =============================================================================
# CFP-2751 D2 — scripts/lib/*.py 1-hop 직접호출 shape-coverage (change-plan §8 5-case RTM)
#   _DEP_PATTERNS append: re.compile(r"\bscripts/lib/[a-z0-9_-]+\.py\b") (underscore load-bearing).
#   방향3 이 "yml→scripts/lib/*.py(1-hop 직접)" 미모델링 shape 를 검출하게 됐음을 discriminate.
#   fixture 파일명 underscore 강제 = M-D2b(char-class 에서 `_` 탈락 시 미매칭) discriminate.
#   Case4(d1-repos-executable / AC-1) = check-consumer-scripts-manifest.sh Check4 harness 소유
#     (CFP-2408 축) → 본 3way self-test 에 중복 fixture 금지(change-plan §8.1). live CI 검증.
# =============================================================================

# -----------------------------------------------------------------------------
# CFP2751-C1 libpy-runblock-unregistered ★ [AC-3]: whitelist wf run:블록이 미등재
#   scripts/lib/d2_phantom_dep.py(underscore名) 직접호출 → FAIL(1). 등재 scripts/check-a.sh 공존.
#   kill M-D2a(_DEP_PATTERNS scripts/lib shape 제거) / M-D2b(char-class underscore 탈락).
#   ★ 정규식 load-bearing 반증: check_whitelist_manifest_3way.py 의 scripts/lib 정규식 제거 시
#     이 케이스 exit 1→0 flip = self-test FAIL (정규식이 검출을 실제로 수행함을 반증적 증명).
# -----------------------------------------------------------------------------
R=$(mktemp -d); build_baseline "$R"
echo "d2-libpy.yml" >> "$R/templates/scripts/consumer_applicable_workflows.txt"
cat > "$R/templates/github-workflows/d2-libpy.yml" <<'EOF'
name: d2-libpy
on:
  pull_request:
    types: [opened]
jobs:
  d:
    runs-on: ubuntu-latest
    steps:
      - run: |
          bash scripts/check-a.sh
          python3 scripts/lib/d2_phantom_dep.py
EOF
run_fixture "CFP2751-C1-libpy-runblock-unregistered" "1" "whitelist wf run:블록 미등재 scripts/lib/d2_phantom_dep.py(underscore) 직접호출 검출 (방향3 shape-coverage, AC-3)" "$R"

# -----------------------------------------------------------------------------
# CFP2751-C2 libpy-comment-only-pass ★ [AC-4]: run:블록 안 `#` 주석줄에서만 언급한
#   scripts/lib/d2_comment_only.py(미등재) → 무검출 PASS(0). 등재 scripts/check-a.sh 실호출.
#   kill M-D2c(_YAML_COMMENT_LINE strip 제거 → 주석 phantom 추출 → exit 0→1 flip = RED).
# -----------------------------------------------------------------------------
R=$(mktemp -d); build_baseline "$R"
echo "d2-comment.yml" >> "$R/templates/scripts/consumer_applicable_workflows.txt"
cat > "$R/templates/github-workflows/d2-comment.yml" <<'EOF'
name: d2-comment
on:
  pull_request:
    types: [opened]
jobs:
  c:
    runs-on: ubuntu-latest
    steps:
      - run: |
          bash scripts/check-a.sh
          # helper ref only (not invoked): scripts/lib/d2_comment_only.py
EOF
run_fixture "CFP2751-C2-libpy-comment-only-pass" "0" "run:블록 주석줄 scripts/lib/d2_comment_only.py 언급 = closure 아님 (주석 strip, AC-4)" "$R"

# -----------------------------------------------------------------------------
# CFP2751-C3 libpy-plugin-only-pass ★ [AC-5]: 비-whitelist(plugin-only) wf 가 미등재
#   scripts/lib/d2_plugin_scoped.py 직접호출 → 무검출 PASS(0) (whitelist scoping auto-exclude).
#   kill M-D2d(whitelist scoping 제거 → 전 template scan → plugin-only helper 검출 → exit 0→1 = RED).
# -----------------------------------------------------------------------------
R=$(mktemp -d); build_baseline "$R"
# d2-plugin.yml = whitelist 미등재(plugin-only). manifest 도 미참조 = 순수 orphan template.
cat > "$R/templates/github-workflows/d2-plugin.yml" <<'EOF'
name: d2-plugin
on:
  pull_request:
    types: [opened]
jobs:
  p:
    runs-on: ubuntu-latest
    steps:
      - run: python3 scripts/lib/d2_plugin_scoped.py
EOF
run_fixture "CFP2751-C3-libpy-plugin-only-pass" "0" "비-whitelist plugin-only wf 의 미등재 scripts/lib/d2_plugin_scoped.py = whitelist scoping auto-exclude (AC-5)" "$R"

# -----------------------------------------------------------------------------
# CFP2751-C5 born-green-corpus-shape ★ [AC-6]: whitelist wf run:블록이 scripts/lib/*.py
#   6개(underscore, 전부 등재) 직접호출 → 위반 0 PASS(0). 별 whitelist wf 는 comment-only
#   미등재 helper → 여전히 무검출(vacuity 반증: 게이트가 실제로 보되 등재라 통과).
#   kill: comment-strip 제거 시 comment-only wf 의 미등재 helper 검출 → exit 0→1 flip = RED
#         (born-green 이 "아무것도 안 봐서 pass" 가 아님을 반증).
# -----------------------------------------------------------------------------
R=$(mktemp -d); build_baseline "$R"
{
  echo "d2-corpus.yml"
  echo "d2-corpus-comment.yml"
} >> "$R/templates/scripts/consumer_applicable_workflows.txt"
# 6종 lib py 를 manifest 에 등재 (script-only, dep_workflow 미부착 = 방향2 비대상)
{
  echo "scripts/lib/d2_corpus_1.py"
  echo "scripts/lib/d2_corpus_2.py"
  echo "scripts/lib/d2_corpus_3.py"
  echo "scripts/lib/d2_corpus_4.py"
  echo "scripts/lib/d2_corpus_5.py"
  echo "scripts/lib/d2_corpus_6.py"
} >> "$R/templates/consumer-scripts.manifest"
cat > "$R/templates/github-workflows/d2-corpus.yml" <<'EOF'
name: d2-corpus
on:
  pull_request:
    types: [opened]
jobs:
  cc:
    runs-on: ubuntu-latest
    steps:
      - run: |
          python3 scripts/lib/d2_corpus_1.py
          python3 scripts/lib/d2_corpus_2.py
          python3 scripts/lib/d2_corpus_3.py
          python3 scripts/lib/d2_corpus_4.py
          python3 scripts/lib/d2_corpus_5.py
          python3 scripts/lib/d2_corpus_6.py
EOF
cat > "$R/templates/github-workflows/d2-corpus-comment.yml" <<'EOF'
name: d2-corpus-comment
on:
  pull_request:
    types: [opened]
jobs:
  cm:
    runs-on: ubuntu-latest
    steps:
      - run: |
          bash scripts/check-a.sh
          # doc ref (not invoked): scripts/lib/d2_corpus_unregistered.py
EOF
run_fixture "CFP2751-C5-born-green-corpus-shape" "0" "whitelist wf run:블록 scripts/lib/*.py 6종(전부 등재) + comment-only 미등재 helper = 위반 0 born-green non-vacuous (AC-6)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F11a data-absence-whitelist ★: whitelist txt 파일 자체 부재 → PASS(exit 0, honest no-op)
#   kill Mutation-11a (data-absence→silent FAIL exit 1/2 mutate → fail-open 退化 시 RED).
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
rm -f "$R/templates/scripts/consumer_applicable_workflows.txt"
run_fixture "F11a-data-absence-whitelist" "0" "whitelist 파일 부재 = 검증 비대상 honest no-op (fail-open)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F11b data-absence-manifest ★: manifest 파일 자체 부재 → PASS(exit 0, honest no-op)
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
rm -f "$R/templates/consumer-scripts.manifest"
run_fixture "F11b-data-absence-manifest" "0" "manifest 파일 부재 = 검증 비대상 honest no-op (fail-open)" "$R"

# ─────────────────────────────────────────────────────────────────────────────
# F11c data-absence-templates-dir ★: templates/github-workflows/ dir 자체 부재 → PASS(exit 0, no-op)
# ─────────────────────────────────────────────────────────────────────────────
R=$(mktemp -d); build_baseline "$R"
rm -rf "$R/templates/github-workflows"
run_fixture "F11c-data-absence-templates-dir" "0" "templates dir 부재 = 검증 비대상 honest no-op (fail-open)" "$R"

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2412 whitelist-manifest-3way)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (change-plan §6.1 — mutation 생존 0):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "Mutation-1  (방향1 전수검증 제거)                 → F1 PASS 면 RED"
  echo "Mutation-2  (방향2 부분집합 제거)                 → F2 PASS 면 RED"
  echo "Mutation-3  (depth-2 walker 제거)                 → F3 PASS 면 RED"
  echo "Mutation-4  (template-only 분류 제거)             → F4 FAIL 면 RED"
  echo "Mutation-5  (방향2 bijection 역강제 mutate)       → F5 phantom-FAIL 면 RED"
  echo "Mutation-6  (glob .yml 단독 축소)                 → F6 phantom-dead 면 RED"
  echo "Mutation-7  (주석/빈줄 skip 제거)                 → F7 phantom entry FAIL 면 RED"
  echo "Mutation-8  (exit 2 분기를 1 로 mutate)           → F8 exit 1 이면 RED"
  echo "Mutation-9  (case-exact 매칭 제거)                → F9 PASS 면 RED"
  echo "Mutation-10 (방향3 whitelist→manifest coverage 제거) → F10 PASS 면 RED"
  echo "            (run:-block-aware AM-3 추출 → naive grep 이면 F10b false-FAIL)"
  echo "Mutation-11a/b/c (data-absence→silent FAIL exit 1/2) → F11a/b/c FAIL 면 RED (fail-open 退化)"
  echo "Mutation-12/13 (run_indent=len(prefix) → len(whitespace-only) 버그 복원) → F12/F13 FAIL 면 RED"
  echo "            (list-item run: 의 env:/with: sibling 컬럼 오판 → script 토큰 오추출)"
  echo "[CFP-2751 D2] M-D2a (_DEP_PATTERNS scripts/lib/*.py shape 제거)   → CFP2751-C1 exit 1→0 면 RED"
  echo "[CFP-2751 D2] M-D2b (char-class [a-z0-9_-] underscore 탈락)       → CFP2751-C1 exit 1→0 면 RED (underscore名 미매칭)"
  echo "[CFP-2751 D2] M-D2c (_YAML_COMMENT_LINE 주석 strip 제거)          → CFP2751-C2/C5 exit 0→1 면 RED"
  echo "[CFP-2751 D2] M-D2d (whitelist scoping 제거 → 전 template scan)   → CFP2751-C3 exit 0→1 면 RED"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
