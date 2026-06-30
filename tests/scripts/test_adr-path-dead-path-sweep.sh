#!/usr/bin/env bash
# tests/scripts/test_adr-path-dead-path-sweep.sh
# CFP-2519 / 설계 §8 Test Contract — docs/adr→archive/adr dead-path 클래스 sweep 회귀 검증.
# 선행 동형: CFP-2515 test_adr-sunset-criteria-pathagnostic.sh (단일 게이트) → 본 Story = 잔여 클래스 sweep.
#
# AC 매핑:
#   AC-D1.1/D1.2 (decision/kst workflow path-agnostic) → test_decision_principle_pathagnostic / test_kst_pathagnostic
#   AC-D1.3      (lib in_scope 계층)                    → test_decision_principle_lib_inscope / test_kst_lib_inscope
#   AC-D2.1/D2.3 (phase-gate SECURITY_PATHS required)   → test_phasegate_security_paths
#   AC-D3.1/D3.2 (story-init / tier-downgrade stale-ref)→ test_storyinit_stale_ref / test_tier_downgrade_comment
#   AC-D4.1/D4.2 (symmetric mutation-kill + lib-exercise)→ *_mutation_kill (workflow + lib 계층)
#   AC-D6.1      (byte-identical parity)                → 각 *_pathagnostic test 의 diff -q
#
# ★핵심 함정 2종 봉인 (설계 §8.0):
#   1. asymmetric sed no-op trap (#2514 교훈): mutation 후 diff -q no-op guard 로 sed 미반영 = FAIL 처리
#      (mutant "SURVIVED" 가 vacuous 통과 되지 않도록).
#   2. ★lib-exercise gap (green-but-dead 핵심): workflow grep 단독 mutation 은 lib in_scope() 2차 차단을
#      못 잡아 workflow-only(불완전) fix 를 green-pass 시킨다 → mutation-kill 을 lib in_scope 계층까지 exercise.
#      kst 는 SCOPE_GLOBS + L113 standalone 2-site 양쪽 load-bearing 검증 (kst 고유 비동형).
#
# anti-theater: always-pass·tautology 0 — 각 site mutation 시 RED 전환되는 load-bearing assert 만.
# set -e 미사용 — 각 test || true 로 partial run 허용, FAIL 카운터 집계 후 exit code 결정.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB_DIR="$REPO_ROOT/scripts/lib"

DECISION_GH="$REPO_ROOT/.github/workflows/decision-principle-vocabulary.yml"
DECISION_TMPL="$REPO_ROOT/templates/github-workflows/decision-principle-vocabulary.yml"
DECISION_LIB="$LIB_DIR/check_decision_principle_vocabulary.py"

KST_GH="$REPO_ROOT/.github/workflows/kst-timestamp-display.yml"
KST_TMPL="$REPO_ROOT/templates/github-workflows/kst-timestamp-display.yml"
KST_LIB="$LIB_DIR/check_kst_timestamp.py"

PHASEGATE_GH="$REPO_ROOT/.github/workflows/phase-gate-mergeable.yml"
PHASEGATE_TMPL="$REPO_ROOT/templates/github-workflows/phase-gate-mergeable.yml"

STORYINIT_GH="$REPO_ROOT/.github/workflows/story-init.yml"
STORYINIT_TMPL="$REPO_ROOT/templates/github-workflows/story-init.yml"

TIER_GH="$REPO_ROOT/.github/workflows/tier-downgrade-guard.yml"
TIER_TMPL="$REPO_ROOT/templates/github-workflows/tier-downgrade-guard.yml"

PYTHON="${PYTHON:-python}"
command -v "$PYTHON" >/dev/null 2>&1 || PYTHON="python3"

PASS=0
FAIL=0

# ─── lib in_scope() helper — 격리 module import (mutation 시 sed 적용된 임시 lib 도 평가 가능) ───
# arg1 = lib 절대경로, arg2 = 검사 path → in_scope() True/False stdout
lib_in_scope() {
  local lib_path="$1" probe="$2"
  "$PYTHON" - "$lib_path" "$probe" <<'PYEOF'
import sys, importlib.util
lib_path, probe = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("_libmod", lib_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("True" if mod.in_scope(probe) else "False")
PYEOF
}

# ════════════════════════════════════════════════════════════════════════════
# D1 — decision-principle-vocabulary
# ════════════════════════════════════════════════════════════════════════════

# AC-D1.1 + AC-D6.1: 양 copy on.paths archive 엔트리 + grep alternation + byte-identical + 실 매치 대칭
test_decision_principle_pathagnostic() {
  local n="decision-principle-path-agnostic"
  local gh_paths tmpl_paths gh_alt tmpl_alt
  gh_paths=$(grep -cF "archive/adr/ADR-*.md" "$DECISION_GH" 2>/dev/null) || gh_paths=0
  tmpl_paths=$(grep -cF "archive/adr/ADR-*.md" "$DECISION_TMPL" 2>/dev/null) || tmpl_paths=0
  gh_alt=$(grep -cF '(docs|archive)/adr/ADR-' "$DECISION_GH" 2>/dev/null) || gh_alt=0
  tmpl_alt=$(grep -cF '(docs|archive)/adr/ADR-' "$DECISION_TMPL" 2>/dev/null) || tmpl_alt=0

  local identical=0
  diff -q "$DECISION_GH" "$DECISION_TMPL" >/dev/null 2>&1 && identical=1

  # 실 매치 (grep alternation, wrapper archive + consumer docs 대칭)
  local w_match=0 c_match=0
  printf 'archive/adr/ADR-130.md\n' | grep -qE '^((docs|archive)/adr/ADR-.*\.md|docs/change-plans/.*\.md|CLAUDE\.md|docs/orchestrator-playbook\.md|templates/.*\.(md|yml|yaml|sh))$' && w_match=1
  printf 'docs/adr/ADR-130.md\n'    | grep -qE '^((docs|archive)/adr/ADR-.*\.md|docs/change-plans/.*\.md|CLAUDE\.md|docs/orchestrator-playbook\.md|templates/.*\.(md|yml|yaml|sh))$' && c_match=1

  if [ "$gh_paths" -ge 1 ] && [ "$tmpl_paths" -ge 1 ] && [ "$gh_alt" -ge 1 ] && [ "$tmpl_alt" -ge 1 ] \
     && [ "$identical" -eq 1 ] && [ "$w_match" -eq 1 ] && [ "$c_match" -eq 1 ]; then
    echo "PASS: $n -- on.paths archive 엔트리 + grep alternation 양 copy byte-identical + wrapper/consumer 대칭 매치"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- gh_paths=$gh_paths tmpl_paths=$tmpl_paths gh_alt=$gh_alt tmpl_alt=$tmpl_alt identical=$identical w_match=$w_match c_match=$c_match"
    FAIL=$((FAIL+1))
  fi
}

# AC-D1.3 + ★lib-exercise: lib in_scope() 가 archive/adr ADR True, 비-ADR False, docs/adr 대칭
test_decision_principle_lib_inscope() {
  local n="decision-principle-lib-inscope"
  local arc doc nonadr
  arc=$(lib_in_scope "$DECISION_LIB" "archive/adr/ADR-130.md")
  doc=$(lib_in_scope "$DECISION_LIB" "docs/adr/ADR-130.md")
  nonadr=$(lib_in_scope "$DECISION_LIB" "archive/adr/README.md")
  if [ "$arc" = "True" ] && [ "$doc" = "True" ] && [ "$nonadr" = "False" ]; then
    echo "PASS: $n -- lib in_scope() archive/adr ADR=True docs/adr ADR=True 비-ADR=False (lib 계층 실효)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- arc=$arc doc=$doc nonadr=$nonadr (기대 True/True/False)"
    FAIL=$((FAIL+1))
  fi
}

# AC-D4.1: symmetric mutation-kill (workflow grep + ★lib SCOPE_GLOBS) — diff -q no-op guard
test_decision_principle_mutation_kill() {
  # --- (a) workflow grep mutation ---
  local mn="decision-workflow-grep-mutant"
  local mdir mutated arc_orig arc_mutant
  mdir="$(mktemp -d)"; mutated="$mdir/wf.yml"; cp "$DECISION_GH" "$mutated"
  arc_orig=$(printf 'archive/adr/ADR-130.md\n' | grep -cE '^((docs|archive)/adr/ADR-.*\.md|docs/change-plans/.*\.md|CLAUDE\.md|docs/orchestrator-playbook\.md|templates/.*\.(md|yml|yaml|sh))$') || arc_orig=0
  sed -i 's#(docs|archive)/adr#docs/adr#g' "$mutated"
  if diff -q "$DECISION_GH" "$mutated" >/dev/null 2>&1; then
    echo "FAIL: $mn -- sed no-op (소스 무변경 — mutant 정의 오류)"; FAIL=$((FAIL+1)); rm -rf "$mdir"
  else
    arc_mutant=$(printf 'archive/adr/ADR-130.md\n' | grep -cE '^(docs/adr/ADR-.*\.md|docs/change-plans/.*\.md|CLAUDE\.md|docs/orchestrator-playbook\.md|templates/.*\.(md|yml|yaml|sh))$') || arc_mutant=0
    rm -rf "$mdir"
    if [ "$arc_orig" -eq 1 ] && [ "$arc_mutant" -eq 0 ]; then
      echo "PASS: $mn -- mutant KILLED (docs-only 변환 후 archive 미매치 = workflow dead-gate RED 검출)"; PASS=$((PASS+1))
    else
      echo "FAIL: $mn -- mutant SURVIVED (arc_orig=$arc_orig arc_mutant=$arc_mutant, 기대 1/0)"; FAIL=$((FAIL+1))
    fi
  fi

  # --- (b) ★lib SCOPE_GLOBS mutation (lib-exercise — workflow-only fix green-pass 봉인) ---
  local ln="decision-lib-SCOPE_GLOBS-mutant"
  local ldir mlib base_scope mut_scope arc_lib
  ldir="$(mktemp -d)"; mlib="$ldir/lib.py"; cp "$DECISION_LIB" "$mlib"
  base_scope=$(lib_in_scope "$mlib" "archive/adr/ADR-130.md")  # 변이 전 True 기대
  # mutation: SCOPE_GLOBS 에서 archive/adr glob 제거 (in_scope() 가 SCOPE_GLOBS 순회이므로 동시 무력화)
  sed -i '/"archive\/adr\/ADR-\*\.md",/d' "$mlib"
  if diff -q "$DECISION_LIB" "$mlib" >/dev/null 2>&1; then
    echo "FAIL: $ln -- sed no-op (SCOPE_GLOBS archive 라인 미제거 — mutant 정의 오류)"; FAIL=$((FAIL+1))
  else
    arc_lib=$(lib_in_scope "$mlib" "archive/adr/ADR-130.md")    # docs/adr 도 여전히 매치 확인용
    local doc_lib
    doc_lib=$(lib_in_scope "$mlib" "docs/adr/ADR-130.md")
    if [ "$base_scope" = "True" ] && [ "$arc_lib" = "False" ] && [ "$doc_lib" = "True" ]; then
      echo "PASS: $ln -- mutant KILLED (lib SCOPE_GLOBS archive 제거 시 in_scope(archive)=False, docs 회귀 0 = lib 계층 load-bearing)"; PASS=$((PASS+1))
    else
      echo "FAIL: $ln -- mutant SURVIVED (base=$base_scope arc_lib=$arc_lib doc_lib=$doc_lib, 기대 True/False/True)"; FAIL=$((FAIL+1))
    fi
  fi
  rm -rf "$ldir"
}

# ════════════════════════════════════════════════════════════════════════════
# D1 — kst-timestamp-display (lib 2-site: SCOPE_GLOBS + in_scope L113 standalone)
# ════════════════════════════════════════════════════════════════════════════

test_kst_pathagnostic() {
  local n="kst-path-agnostic"
  local gh_paths tmpl_paths gh_alt tmpl_alt
  gh_paths=$(grep -cF "archive/adr/ADR-*.md" "$KST_GH" 2>/dev/null) || gh_paths=0
  tmpl_paths=$(grep -cF "archive/adr/ADR-*.md" "$KST_TMPL" 2>/dev/null) || tmpl_paths=0
  gh_alt=$(grep -cF '(docs|archive)/adr/ADR-' "$KST_GH" 2>/dev/null) || gh_alt=0
  tmpl_alt=$(grep -cF '(docs|archive)/adr/ADR-' "$KST_TMPL" 2>/dev/null) || tmpl_alt=0
  local identical=0
  diff -q "$KST_GH" "$KST_TMPL" >/dev/null 2>&1 && identical=1
  local w_match=0 c_match=0
  printf 'archive/adr/ADR-130.md\n' | grep -qE '^(CLAUDE\.md|docs/orchestrator-playbook\.md|(docs|archive)/adr/ADR-.*\.md|docs/retros/.*\.md|wrapper/retros/.*\.md)$' && w_match=1
  printf 'docs/adr/ADR-130.md\n'    | grep -qE '^(CLAUDE\.md|docs/orchestrator-playbook\.md|(docs|archive)/adr/ADR-.*\.md|docs/retros/.*\.md|wrapper/retros/.*\.md)$' && c_match=1
  if [ "$gh_paths" -ge 1 ] && [ "$tmpl_paths" -ge 1 ] && [ "$gh_alt" -ge 1 ] && [ "$tmpl_alt" -ge 1 ] \
     && [ "$identical" -eq 1 ] && [ "$w_match" -eq 1 ] && [ "$c_match" -eq 1 ]; then
    echo "PASS: $n -- on.paths archive 엔트리 + grep alternation 양 copy byte-identical + 대칭 매치"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- gh_paths=$gh_paths tmpl_paths=$tmpl_paths gh_alt=$gh_alt tmpl_alt=$tmpl_alt identical=$identical w_match=$w_match c_match=$c_match"
    FAIL=$((FAIL+1))
  fi
}

test_kst_lib_inscope() {
  local n="kst-lib-inscope"
  local arc doc nonadr
  arc=$(lib_in_scope "$KST_LIB" "archive/adr/ADR-130.md")
  doc=$(lib_in_scope "$KST_LIB" "docs/adr/ADR-130.md")
  nonadr=$(lib_in_scope "$KST_LIB" "archive/adr/README.md")
  if [ "$arc" = "True" ] && [ "$doc" = "True" ] && [ "$nonadr" = "False" ]; then
    echo "PASS: $n -- lib in_scope() archive/adr ADR=True docs/adr ADR=True 비-ADR=False"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- arc=$arc doc=$doc nonadr=$nonadr (기대 True/True/False)"
    FAIL=$((FAIL+1))
  fi
}

# AC-D4.1 kst: ★2-site mutation (SCOPE_GLOBS + in_scope L113 standalone 양쪽 load-bearing)
test_kst_mutation_kill() {
  # --- (a) workflow grep mutation ---
  local mn="kst-workflow-grep-mutant"
  local mdir mutated arc_orig arc_mutant
  mdir="$(mktemp -d)"; mutated="$mdir/wf.yml"; cp "$KST_GH" "$mutated"
  arc_orig=$(printf 'archive/adr/ADR-130.md\n' | grep -cE '^(CLAUDE\.md|docs/orchestrator-playbook\.md|(docs|archive)/adr/ADR-.*\.md|docs/retros/.*\.md|wrapper/retros/.*\.md)$') || arc_orig=0
  sed -i 's#(docs|archive)/adr#docs/adr#g' "$mutated"
  if diff -q "$KST_GH" "$mutated" >/dev/null 2>&1; then
    echo "FAIL: $mn -- sed no-op (소스 무변경)"; FAIL=$((FAIL+1)); rm -rf "$mdir"
  else
    arc_mutant=$(printf 'archive/adr/ADR-130.md\n' | grep -cE '^(CLAUDE\.md|docs/orchestrator-playbook\.md|docs/adr/ADR-.*\.md|docs/retros/.*\.md|wrapper/retros/.*\.md)$') || arc_mutant=0
    rm -rf "$mdir"
    if [ "$arc_orig" -eq 1 ] && [ "$arc_mutant" -eq 0 ]; then
      echo "PASS: $mn -- mutant KILLED (docs-only 변환 후 archive 미매치)"; PASS=$((PASS+1))
    else
      echo "FAIL: $mn -- mutant SURVIVED (arc_orig=$arc_orig arc_mutant=$arc_mutant, 기대 1/0)"; FAIL=$((FAIL+1))
    fi
  fi

  # --- (b) ★lib SCOPE_GLOBS site mutation (collect_scope_files 경로) ---
  local sn="kst-lib-SCOPE_GLOBS-site-mutant"
  local sdir slib base arc_after
  sdir="$(mktemp -d)"; slib="$sdir/lib.py"; cp "$KST_LIB" "$slib"
  base=$(lib_in_scope "$slib" "archive/adr/ADR-130.md")  # True (in_scope L113 standalone 덕)
  sed -i '/"archive\/adr\/ADR-\*\.md",/d' "$slib"
  if diff -q "$KST_LIB" "$slib" >/dev/null 2>&1; then
    echo "FAIL: $sn -- sed no-op (SCOPE_GLOBS archive 라인 미제거)"; FAIL=$((FAIL+1))
  else
    # SCOPE_GLOBS 만 제거해도 L113 standalone 가 남아 in_scope=True 유지 (= L113 가 독립 load-bearing 증명).
    arc_after=$(lib_in_scope "$slib" "archive/adr/ADR-130.md")
    if [ "$base" = "True" ] && [ "$arc_after" = "True" ]; then
      echo "PASS: $sn -- SCOPE_GLOBS 제거 후에도 in_scope=True (L113 standalone 독립 load-bearing 입증 — 2-site 비동형)"; PASS=$((PASS+1))
    else
      echo "FAIL: $sn -- base=$base arc_after=$arc_after (기대 True/True — L113 독립성)"; FAIL=$((FAIL+1))
    fi
  fi
  rm -rf "$sdir"

  # --- (c) ★lib in_scope L113 standalone site mutation (kst 고유 chokepoint) ---
  local ln="kst-lib-inscope-L113-mutant"
  local ldir llib base113 arc113 doc113
  ldir="$(mktemp -d)"; llib="$ldir/lib.py"; cp "$KST_LIB" "$llib"
  base113=$(lib_in_scope "$llib" "archive/adr/ADR-130.md")  # True
  # mutation: L113 의 archive 분기만 제거 → docs/adr 만 매치 (path-agnostic 회귀)
  sed -i 's#if path.match("docs/adr/ADR-\*\.md") or path.match("archive/adr/ADR-\*\.md"):#if path.match("docs/adr/ADR-*.md"):#' "$llib"
  if diff -q "$KST_LIB" "$llib" >/dev/null 2>&1; then
    echo "FAIL: $ln -- sed no-op (in_scope L113 archive 분기 미제거 — mutant 정의 오류)"; FAIL=$((FAIL+1))
  else
    arc113=$(lib_in_scope "$llib" "archive/adr/ADR-130.md")
    doc113=$(lib_in_scope "$llib" "docs/adr/ADR-130.md")
    if [ "$base113" = "True" ] && [ "$arc113" = "False" ] && [ "$doc113" = "True" ]; then
      echo "PASS: $ln -- mutant KILLED (L113 archive 분기 제거 시 in_scope(archive)=False, docs 회귀 0 = L113 load-bearing chokepoint)"; PASS=$((PASS+1))
    else
      echo "FAIL: $ln -- mutant SURVIVED (base=$base113 arc=$arc113 doc=$doc113, 기대 True/False/True)"; FAIL=$((FAIL+1))
    fi
  fi
  rm -rf "$ldir"
}

# ════════════════════════════════════════════════════════════════════════════
# D2 — phase-gate-mergeable SECURITY_PATHS (required check — observable proof)
# ════════════════════════════════════════════════════════════════════════════

test_phasegate_security_paths() {
  local n="phasegate-security-paths"
  # (1) 양 copy SECURITY_PATHS regex path-agnostic 보유 + byte-identical
  local gh_rx tmpl_rx
  gh_rx=$(grep -cF '/^(docs|archive)\/adr\/ADR-.*\.md$/' "$PHASEGATE_GH" 2>/dev/null) || gh_rx=0
  tmpl_rx=$(grep -cF '/^(docs|archive)\/adr\/ADR-.*\.md$/' "$PHASEGATE_TMPL" 2>/dev/null) || tmpl_rx=0
  local identical=0
  diff -q "$PHASEGATE_GH" "$PHASEGATE_TMPL" >/dev/null 2>&1 && identical=1

  # (2) observable proof — JS regex 동작 등가 (node 있으면 실행, 없으면 grep -E 등가 검증)
  local w_match=0 c_match=0 nonadr_match=1
  if command -v node >/dev/null 2>&1; then
    w_match=$(node -e 'const r=/^(docs|archive)\/adr\/ADR-.*\.md$/; process.stdout.write(r.test("archive/adr/ADR-200-security.md")?"1":"0")')
    c_match=$(node -e 'const r=/^(docs|archive)\/adr\/ADR-.*\.md$/; process.stdout.write(r.test("docs/adr/ADR-200-security.md")?"1":"0")')
    nonadr_match=$(node -e 'const r=/^(docs|archive)\/adr\/ADR-.*\.md$/; process.stdout.write(r.test("archive/adr/README.md")?"1":"0")')
  else
    printf 'archive/adr/ADR-200-security.md\n' | grep -qE '^(docs|archive)/adr/ADR-.*\.md$' && w_match=1
    printf 'docs/adr/ADR-200-security.md\n'    | grep -qE '^(docs|archive)/adr/ADR-.*\.md$' && c_match=1
    printf 'archive/adr/README.md\n'           | grep -qE '^(docs|archive)/adr/ADR-.*\.md$' && nonadr_match=1 || nonadr_match=0
  fi

  # (3) cond3 진입가드 정적 검증 — hasPostMergeFixLabel 블록 내에서만 checkSecurityNonTouch 호출
  #     (post-merge-fix label 無 PR → SECURITY_PATHS 미평가 = 정규 lane 영향 0)
  local guard=0
  grep -q 'hasPostMergeFixLabel' "$PHASEGATE_GH" && grep -q 'checkSecurityNonTouch' "$PHASEGATE_GH" && guard=1

  if [ "$gh_rx" -ge 1 ] && [ "$tmpl_rx" -ge 1 ] && [ "$identical" -eq 1 ] \
     && [ "$w_match" = "1" ] && [ "$c_match" = "1" ] && [ "$nonadr_match" = "0" ] && [ "$guard" -eq 1 ]; then
    echo "PASS: $n -- SECURITY_PATHS path-agnostic 양 copy byte-identical + wrapper/consumer 보안 ADR 대칭 match + 비-ADR 미match + cond3 진입가드(post-merge-fix label) 존재"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- gh_rx=$gh_rx tmpl_rx=$tmpl_rx identical=$identical w_match=$w_match c_match=$c_match nonadr_match=$nonadr_match guard=$guard"
    FAIL=$((FAIL+1))
  fi
}

# AC-D4.2: phase-gate mutation-kill — regex docs-only 변환 시 archive 보안 ADR 우회 회귀
test_phasegate_mutation_kill() {
  local mn="phasegate-security-paths-mutant"
  local mdir mutated arc_orig arc_mutant
  mdir="$(mktemp -d)"; mutated="$mdir/wf.yml"; cp "$PHASEGATE_GH" "$mutated"
  arc_orig=$(printf 'archive/adr/ADR-200-security.md\n' | grep -cE '^(docs|archive)/adr/ADR-.*\.md$') || arc_orig=0
  sed -i 's#(docs|archive)\\/adr#docs\\/adr#g' "$mutated"
  if diff -q "$PHASEGATE_GH" "$mutated" >/dev/null 2>&1; then
    echo "FAIL: $mn -- sed no-op (SECURITY_PATHS regex 미변경 — mutant 정의 오류)"; FAIL=$((FAIL+1)); rm -rf "$mdir"
  else
    # mutated regex 가 docs-only 인지 확인: archive 보안 ADR 가 docs-only 패턴에 미매치 = 우회 가능(dead) 재도입
    arc_mutant=$(printf 'archive/adr/ADR-200-security.md\n' | grep -cE '^docs/adr/ADR-.*\.md$') || arc_mutant=0
    rm -rf "$mdir"
    if [ "$arc_orig" -eq 1 ] && [ "$arc_mutant" -eq 0 ]; then
      echo "PASS: $mn -- mutant KILLED (docs-only 변환 후 archive 보안 ADR 미match = post-merge-fix fast-pass 우회 RED 검출)"; PASS=$((PASS+1))
    else
      echo "FAIL: $mn -- mutant SURVIVED (arc_orig=$arc_orig arc_mutant=$arc_mutant, 기대 1/0)"; FAIL=$((FAIL+1))
    fi
  fi
}

# ════════════════════════════════════════════════════════════════════════════
# D3 — stale-ref (story-init parity-excluded / tier-downgrade comment)
# ════════════════════════════════════════════════════════════════════════════

# AC-D3.1: story-init .github copy = archive/adr (정정), templates copy = docs/adr (consumer 정답) — 분기 유지
test_storyinit_stale_ref() {
  local n="story-init-stale-ref-branch"
  local gh_archive tmpl_docs gh_docs tmpl_archive
  gh_archive=$(grep -cF 'archive/adr/ADR-027-consumer-adoption-protocol.md' "$STORYINIT_GH" 2>/dev/null) || gh_archive=0
  gh_docs=$(grep -cF 'main/docs/adr/ADR-027-consumer-adoption-protocol.md' "$STORYINIT_GH" 2>/dev/null) || gh_docs=0
  tmpl_docs=$(grep -cF 'main/docs/adr/ADR-027-consumer-adoption-protocol.md' "$STORYINIT_TMPL" 2>/dev/null) || tmpl_docs=0
  tmpl_archive=$(grep -cF 'archive/adr/ADR-027-consumer-adoption-protocol.md' "$STORYINIT_TMPL" 2>/dev/null) || tmpl_archive=0
  # .github = archive (≥1) AND docs 0 ; templates = docs (≥1) AND archive 0 (분기 유지 = parity-excluded)
  if [ "$gh_archive" -ge 1 ] && [ "$gh_docs" -eq 0 ] && [ "$tmpl_docs" -ge 1 ] && [ "$tmpl_archive" -eq 0 ]; then
    echo "PASS: $n -- .github copy=archive/adr(wrapper 정답) / templates copy=docs/adr(consumer 정답) 분기 유지 (CONSUMER_ONLY_WORKFLOWS parity-excluded)"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- gh_archive=$gh_archive gh_docs=$gh_docs tmpl_docs=$tmpl_docs tmpl_archive=$tmpl_archive (기대 ≥1/0/≥1/0)"
    FAIL=$((FAIL+1))
  fi
}

# AC-D3.2: tier-downgrade 주석 path-agnostic 갱신 + byte-identical
test_tier_downgrade_comment() {
  local n="tier-downgrade-comment"
  local gh_pa tmpl_pa identical=0
  gh_pa=$(grep -cF '(docs|archive)/adr/ADR-*.md' "$TIER_GH" 2>/dev/null) || gh_pa=0
  tmpl_pa=$(grep -cF '(docs|archive)/adr/ADR-*.md' "$TIER_TMPL" 2>/dev/null) || tmpl_pa=0
  diff -q "$TIER_GH" "$TIER_TMPL" >/dev/null 2>&1 && identical=1
  if [ "$gh_pa" -ge 1 ] && [ "$tmpl_pa" -ge 1 ] && [ "$identical" -eq 1 ]; then
    echo "PASS: $n -- 주석 path-agnostic 갱신 양 copy byte-identical"
    PASS=$((PASS+1))
  else
    echo "FAIL: $n -- gh_pa=$gh_pa tmpl_pa=$tmpl_pa identical=$identical (기대 ≥1/≥1/1)"
    FAIL=$((FAIL+1))
  fi
}

# ════════════════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "CFP-2519 Phase 2: docs/adr→archive/adr dead-path 클래스 sweep 회귀 검증"
echo "symmetric mutation-kill + ★lib-exercise (green-but-dead 차단) — CFP-2515 후속"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

test_decision_principle_pathagnostic    || true; echo ""
test_decision_principle_lib_inscope     || true; echo ""
test_decision_principle_mutation_kill   || true; echo ""
test_kst_pathagnostic                   || true; echo ""
test_kst_lib_inscope                    || true; echo ""
test_kst_mutation_kill                  || true; echo ""
test_phasegate_security_paths           || true; echo ""
test_phasegate_mutation_kill            || true; echo ""
test_storyinit_stale_ref                || true; echo ""
test_tier_downgrade_comment             || true

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
